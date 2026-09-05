"""Persistent outside-worktree transaction ledger for NudgeWhen nudge-land.

The ledger binds a canonical repository identity, an authorization id,
and the authorization digest to a small state machine. The state
machine moves through these high-level states:

* ``ACTIVE`` — ledger created, no mutation intent persisted.
* ``MUTATION_IN_PROGRESS`` — a mutation intent has been recorded and
  the corresponding Git action is being attempted; the
  ``mutation_in_progress_substate`` field carries the specific
  mutation.
* ``LANDED`` — terminal success; the verify_ci operation accepted
  exact-head CI success.
* ``CONSUMED`` — terminal failure; the authorization has been
  consumed by a hard-stop and can never be reused.

The verified step field tracks the discrete checkpoints:

* ``S1_LEDGER_ACTIVE``
* ``S4_STAGED``
* ``S6_COMMITTED``
* ``S8_PUSHED``
* ``S10_LANDED``

The intermediate ``S5_COMMITTING``, ``S7_PUSHING``, and
``S9_VERIFYING_CI`` are descriptive MUTATION_IN_PROGRESS substates
rather than verified steps. They MUST NOT appear as the durable
``verified_state`` of any ledger entry.

The landing SHA is an explicit durable ledger field and is persisted
together with the verified ``S6_COMMITTED`` state.

Atomic write semantics:

1. write temporary file in the same ledger directory,
2. ``flush``,
3. ``fsync`` the file descriptor (FAIL CLOSED on OSError),
4. ``os.replace`` atomically swaps the temporary file into place,
5. ``fsync`` the directory file descriptor (FAIL CLOSED on OSError).

Concurrency:

The ledger uses ``fcntl.flock`` on a sibling ``.lock`` file with
``LOCK_EX | LOCK_NB``. A concurrent invocation of the same
authorization therefore fails closed. Nested store primitives never
release the lock between persistence, mutation, and proof stages.

Closed-on-error semantics:

* malformed JSON → ``LedgerCorruptError``
* missing expected ledger after a prior state →
  ``LedgerMissingError``
* stale ``MUTATION_IN_PROGRESS`` after a process restart →
  ``LedgerStaleMutationError``
* reuse of a ``LANDED`` or ``CONSUMED`` authorization →
  ``LedgerAuthorizationTerminalError``
* duplicate matching id+digest ledgers →
  ``LedgerAmbiguousError``

The module never repairs, deletes, or rewrites a ledger entry on its
own; recovery requires a separate explicit maintainer authorization.

The in-memory ``LedgerEntry`` is only mutated AFTER its new durable
representation has been written to disk. If persistence fails, the
caller-visible in-memory state remains at its previous durable value.
"""

from __future__ import annotations

import datetime as _datetime
import enum
import fcntl
import hashlib
import json
import os
import pathlib
import tempfile
from typing import Any, Callable, Mapping

from scripts import nudge_land_runtime as runtime


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


# High-level ledger states.
LEDGER_STATE_ACTIVE = "ACTIVE"
LEDGER_STATE_MUTATION_IN_PROGRESS = "MUTATION_IN_PROGRESS"
LEDGER_STATE_LANDED = "LANDED"
LEDGER_STATE_CONSUMED = "CONSUMED"
# Caller-visible uncertainty state when an advance succeeded at
# ``os.replace`` time but the directory fsync afterwards failed.
LEDGER_STATE_DURABILITY_NOT_ESTABLISHED = "DURABILITY_NOT_ESTABLISHED"

# Verified step labels. The CLI dispatcher reads these verbatim.
STEP_S1_LEDGER_ACTIVE = "S1_LEDGER_ACTIVE"
STEP_S4_STAGED = "S4_STAGED"
STEP_S6_COMMITTED = "S6_COMMITTED"
STEP_S8_PUSHED = "S8_PUSHED"
STEP_S10_LANDED = "S10_LANDED"

# Mutation-intent labels accepted by ``mark_mutation_intent``.
MUTATION_INTENT_STAGE = "STAGE"
MUTATION_INTENT_COMMIT = "COMMIT"
MUTATION_INTENT_PUSH = "PUSH"
MUTATION_INTENT_VERIFY_CI = "VERIFY_CI"

# MUTATION_IN_PROGRESS substates. The authoritative durable substate
# vocabulary is STAGE / COMMIT / PUSH / VERIFY_CI and must agree across
# the runtime / ledger / CLI modules. These labels are also reused as
# the ``mutation_intent`` value so a single vocabulary covers both
# purposes.
SUBSTATE_STAGE = "STAGE"
SUBSTATE_COMMIT = "COMMIT"
SUBSTATE_PUSH = "PUSH"
SUBSTATE_VERIFY_CI = "VERIFY_CI"

# Default persistent state root under ``$XDG_STATE_HOME`` or
# ``~/.local/state``. The CLI dispatcher and tests can override the
# state root.
DEFAULT_STATE_NAMESPACE = "nudge-land"
DEFAULT_STATE_LEDGER_DIR = "ledgers"
DEFAULT_STATE_LOCK_DIR = "locks"
DEFAULT_STATE_AUTH_LOCK_DIR = "auth_locks"

# File extensions for ledger artifacts.
LEDGER_FILE_SUFFIX = ".json"
LOCK_FILE_SUFFIX = ".lock"

# Active states (verified) that allow further transitions.
TERMINAL_STATES = frozenset({LEDGER_STATE_LANDED, LEDGER_STATE_CONSUMED})

# Durability-error kinds. The ``kind`` attribute on
# :class:`LedgerDurabilityError` distinguishes a failure that occurred
# before ``os.replace`` (so the previous durable state is intact) from
# one that occurred after ``os.replace`` but before the directory
# fsync (so direct durability of the new state is not established).
LEDGER_DURABILITY_PRE_REPLACE = "PRE_REPLACE_DURABILITY_FAILURE"
LEDGER_DURABILITY_POST_REPLACE = "POST_REPLACE_DURABILITY_NOT_ESTABLISHED"


# ---------------------------------------------------------------------------
# Exception types
# ---------------------------------------------------------------------------


class LedgerError(Exception):
    """Base class for every ledger error."""


class LedgerCorruptError(LedgerError):
    """The ledger JSON could not be parsed or is structurally malformed."""


class LedgerMissingError(LedgerError):
    """An expected ledger entry was not present."""


class LedgerStaleMutationError(LedgerError):
    """A ledger was found in ``MUTATION_IN_PROGRESS`` after a restart."""


class LedgerAuthorizationTerminalError(LedgerError):
    """The authorization is already ``LANDED`` or ``CONSUMED``."""


class LedgerLockedError(LedgerError):
    """Another process currently holds the ledger lock."""


class LedgerStateError(LedgerError):
    """An illegal state transition was attempted."""


class LedgerAmbiguousError(LedgerError):
    """More than one ledger entry matches the supplied id+digest."""

    def __init__(self, identities: list[str]) -> None:
        super().__init__(
            f"ambiguous ledger match: {len(identities)} entries share id+digest"
        )
        self.identities = list(identities)


class LedgerDurabilityError(LedgerError):
    """An fsync (file or directory) reported failure.

    The ``kind`` attribute distinguishes two phases:

    * ``PRE_REPLACE_DURABILITY_FAILURE`` — the failure occurred before
      ``os.replace``. The previously durable ledger state is intact.
    * ``POST_REPLACE_DURABILITY_NOT_ESTABLISHED`` — the failure
      occurred after ``os.replace`` but before the directory fsync.
      Direct durability of the new state is not established; the
      previous and the new state are both possible on next read.
    """

    def __init__(
        self,
        message: str,
        *,
        kind: str = LEDGER_DURABILITY_PRE_REPLACE,
    ) -> None:
        super().__init__(message)
        if kind not in (
            LEDGER_DURABILITY_PRE_REPLACE,
            LEDGER_DURABILITY_POST_REPLACE,
        ):
            raise ValueError(f"unknown LedgerDurabilityError kind: {kind!r}")
        self.kind = kind


# ---------------------------------------------------------------------------
# State-root resolution
# ---------------------------------------------------------------------------


def resolve_default_state_root() -> pathlib.Path:
    """Return the default persistent state root for the ledger."""
    xdg = os.environ.get("XDG_STATE_HOME", "").strip()
    if xdg:
        return pathlib.Path(xdg).expanduser().resolve()
    home = os.environ.get("HOME", "").strip()
    if home:
        return pathlib.Path(home).expanduser().resolve() / ".local" / "state"
    return pathlib.Path("~/.local/state").expanduser().resolve()


# ---------------------------------------------------------------------------
# Ledger entry
# ---------------------------------------------------------------------------


class LedgerEntry:
    """In-memory representation of one ledger JSON document."""

    __slots__ = (
        "authorization_id",
        "authorization_digest",
        "repository_identity",
        "authorized_branch",
        "authorized_base_head",
        "authorized_push_branch",
        "authorized_remote",
        "authorized_remote_repository",
        "authorized_commit_subject",
        "expected_remote_base_sha",
        "authorized_ci_workflow_or_check",
        "expected_ci_event",
        "authorized_paths",
        "authorized_file_fingerprints",
        "expected_initial_status",
        "state",
        "mutation_intent",
        "mutation_in_progress_substate",
        "verified_state",
        "landing_commit_sha",
        "created_at",
        "updated_at",
        "history",
    )

    def __init__(
        self,
        *,
        authorization_id: str,
        authorization_digest: str,
        repository_identity: str,
        authorized_branch: str,
        authorized_base_head: str,
        authorized_push_branch: str,
        authorized_remote: str,
        authorized_remote_repository: str,
        authorized_commit_subject: str,
        expected_remote_base_sha: str,
        authorized_ci_workflow_or_check: str,
        expected_ci_event: str,
        authorized_paths: list[str],
        authorized_file_fingerprints: dict[str, str],
        expected_initial_status: list[dict[str, str]],
        state: str,
        mutation_intent: str | None,
        mutation_in_progress_substate: str | None,
        verified_state: str,
        landing_commit_sha: str | None,
        created_at: str,
        updated_at: str,
        history: list[dict[str, str]],
    ) -> None:
        self.authorization_id = authorization_id
        self.authorization_digest = authorization_digest
        self.repository_identity = repository_identity
        self.authorized_branch = authorized_branch
        self.authorized_base_head = authorized_base_head
        self.authorized_push_branch = authorized_push_branch
        self.authorized_remote = authorized_remote
        self.authorized_remote_repository = authorized_remote_repository
        self.authorized_commit_subject = authorized_commit_subject
        self.expected_remote_base_sha = expected_remote_base_sha
        self.authorized_ci_workflow_or_check = authorized_ci_workflow_or_check
        self.expected_ci_event = expected_ci_event
        self.authorized_paths = list(authorized_paths)
        self.authorized_file_fingerprints = dict(authorized_file_fingerprints)
        self.expected_initial_status = list(expected_initial_status)
        self.state = state
        self.mutation_intent = mutation_intent
        self.mutation_in_progress_substate = mutation_in_progress_substate
        self.verified_state = verified_state
        self.landing_commit_sha = landing_commit_sha
        self.created_at = created_at
        self.updated_at = updated_at
        self.history = list(history)

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "authorization_digest": self.authorization_digest,
            "repository_identity": self.repository_identity,
            "authorized_branch": self.authorized_branch,
            "authorized_base_head": self.authorized_base_head,
            "authorized_push_branch": self.authorized_push_branch,
            "authorized_remote": self.authorized_remote,
            "authorized_remote_repository": self.authorized_remote_repository,
            "authorized_commit_subject": self.authorized_commit_subject,
            "expected_remote_base_sha": self.expected_remote_base_sha,
            "authorized_ci_workflow_or_check": self.authorized_ci_workflow_or_check,
            "expected_ci_event": self.expected_ci_event,
            "authorized_paths": list(self.authorized_paths),
            "authorized_file_fingerprints": dict(self.authorized_file_fingerprints),
            "expected_initial_status": list(self.expected_initial_status),
            "state": self.state,
            "mutation_intent": self.mutation_intent,
            "mutation_in_progress_substate": self.mutation_in_progress_substate,
            "verified_state": self.verified_state,
            "landing_commit_sha": self.landing_commit_sha,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "history": list(self.history),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LedgerEntry":
        required = (
            "authorization_id",
            "authorization_digest",
            "repository_identity",
            "authorized_branch",
            "authorized_base_head",
            "authorized_push_branch",
            "authorized_remote",
            "authorized_remote_repository",
            "authorized_commit_subject",
            "expected_remote_base_sha",
            "authorized_ci_workflow_or_check",
            "expected_ci_event",
            "authorized_paths",
            "authorized_file_fingerprints",
            "expected_initial_status",
            "state",
            "mutation_intent",
            "mutation_in_progress_substate",
            "verified_state",
            "landing_commit_sha",
            "created_at",
            "updated_at",
            "history",
        )
        if not isinstance(data, Mapping):
            raise LedgerCorruptError("ledger entry must be a JSON object")
        for field in required:
            if field not in data:
                raise LedgerCorruptError(
                    f"ledger entry missing required field: {field}"
                )

        # Strict raw-JSON type validation: reject fabrication via
        # str()/list()/dict() coercion of malformed shapes. Each
        # binding-critical field is type-checked before being trusted.

        def _require_str(name: str) -> str:
            value = data[name]
            if not isinstance(value, str) or not value:
                raise LedgerCorruptError(
                    f"ledger entry has invalid {name}: {value!r}"
                )
            return value

        def _require_hex(name: str, length: int) -> str:
            value = data[name]
            if (
                not isinstance(value, str)
                or len(value) != length
                or not all(c in "0123456789abcdefABCDEF" for c in value)
            ):
                raise LedgerCorruptError(
                    f"ledger entry has invalid {name}: {value!r}"
                )
            return value

        authorization_id = _require_str("authorization_id")
        authorization_digest = _require_hex("authorization_digest", 64)

        repository_identity = _require_str("repository_identity")
        if not _is_canonical_repo_identity(repository_identity):
            raise LedgerCorruptError(
                f"ledger entry has invalid repository_identity: "
                f"{repository_identity!r}"
            )

        authorized_branch = _require_str("authorized_branch")
        authorized_base_head = _require_hex("authorized_base_head", 40)
        authorized_push_branch = _require_str("authorized_push_branch")
        authorized_remote = _require_str("authorized_remote")
        authorized_remote_repository = _require_str("authorized_remote_repository")
        authorized_commit_subject = _require_str("authorized_commit_subject")
        expected_remote_base_sha = _require_hex("expected_remote_base_sha", 40)
        authorized_ci_workflow_or_check = _require_str(
            "authorized_ci_workflow_or_check"
        )
        expected_ci_event = _require_str("expected_ci_event")

        authorized_paths_raw = data["authorized_paths"]
        if not isinstance(authorized_paths_raw, list) or not authorized_paths_raw:
            raise LedgerCorruptError(
                "ledger entry authorized_paths must be a non-empty list"
            )
        canonical_authorized_paths: list[str] = []
        for path in authorized_paths_raw:
            if not isinstance(path, str) or not path:
                raise LedgerCorruptError(
                    f"ledger entry authorized_paths entry invalid: {path!r}"
                )
            try:
                canonical_authorized_paths.append(
                    runtime.canonical_path_string(path)
                )
            except runtime.NudgeLandPathError as exc:
                raise LedgerCorruptError(
                    f"ledger entry authorized_paths entry invalid: {path!r}"
                ) from exc
        try:
            runtime.assert_no_duplicate_normalized_paths(
                canonical_authorized_paths
            )
        except runtime.NudgeLandPathError as exc:
            raise LedgerCorruptError(
                "ledger entry authorized_paths has duplicate canonical entry"
            ) from exc
        authorized_paths = canonical_authorized_paths

        authorized_file_fingerprints_raw = data["authorized_file_fingerprints"]
        if not isinstance(authorized_file_fingerprints_raw, Mapping):
            raise LedgerCorruptError(
                "ledger entry authorized_file_fingerprints must be a JSON object"
            )
        canonical_fingerprint_keys: list[str] = []
        authorized_file_fingerprints: dict[str, str] = {}
        for fpath, fsha in authorized_file_fingerprints_raw.items():
            if not isinstance(fpath, str) or not fpath:
                raise LedgerCorruptError(
                    "ledger entry authorized_file_fingerprints key invalid"
                )
            try:
                canonical_fpath = runtime.canonical_path_string(fpath)
            except runtime.NudgeLandPathError as exc:
                raise LedgerCorruptError(
                    "ledger entry authorized_file_fingerprints key invalid"
                ) from exc
            if canonical_fpath in authorized_file_fingerprints:
                raise LedgerCorruptError(
                    "ledger entry authorized_file_fingerprints has duplicate "
                    f"canonical key: {canonical_fpath!r}"
                )
            canonical_fingerprint_keys.append(canonical_fpath)
            authorized_file_fingerprints[canonical_fpath] = _require_hex_of(
                "authorized_file_fingerprints", fsha, 64
            )
        if set(canonical_fingerprint_keys) != set(canonical_authorized_paths):
            raise LedgerCorruptError(
                "ledger entry authorized_file_fingerprints path-set does not "
                "match authorized_paths"
            )

        expected_initial_status_raw = data["expected_initial_status"]
        if not isinstance(expected_initial_status_raw, list) or not expected_initial_status_raw:
            raise LedgerCorruptError(
                "ledger entry expected_initial_status must be a non-empty list"
            )
        allowed_status_labels = {
            runtime.STATUS_WORKTREE_MODIFIED,
            runtime.STATUS_UNTRACKED_NEW,
        }
        canonical_status_paths: list[str] = []
        expected_initial_status: list[dict[str, str]] = []
        for record in expected_initial_status_raw:
            if not isinstance(record, Mapping):
                raise LedgerCorruptError(
                    "ledger entry expected_initial_status entry must be object"
                )
            if set(record.keys()) != {"status", "path"}:
                raise LedgerCorruptError(
                    "ledger entry expected_initial_status entry must have "
                    "exactly status and path keys"
                )
            status = record["status"]
            rpath = record["path"]
            if not isinstance(status, str) or status not in allowed_status_labels:
                raise LedgerCorruptError(
                    f"ledger entry expected_initial_status status invalid: "
                    f"{status!r}"
                )
            if not isinstance(rpath, str) or not rpath:
                raise LedgerCorruptError(
                    f"ledger entry expected_initial_status path invalid: "
                    f"{rpath!r}"
                )
            try:
                canonical_rpath = runtime.canonical_path_string(rpath)
            except runtime.NudgeLandPathError as exc:
                raise LedgerCorruptError(
                    f"ledger entry expected_initial_status path invalid: "
                    f"{rpath!r}"
                ) from exc
            if canonical_rpath in canonical_status_paths:
                raise LedgerCorruptError(
                    "ledger entry expected_initial_status has duplicate "
                    f"canonical path: {canonical_rpath!r}"
                )
            canonical_status_paths.append(canonical_rpath)
            expected_initial_status.append(
                {"status": status, "path": canonical_rpath}
            )
        if set(canonical_status_paths) != set(canonical_authorized_paths):
            raise LedgerCorruptError(
                "ledger entry expected_initial_status path-set does not "
                "match authorized_paths"
            )

        state = data["state"]
        if not isinstance(state, str) or state not in (
            LEDGER_STATE_ACTIVE,
            LEDGER_STATE_MUTATION_IN_PROGRESS,
            LEDGER_STATE_LANDED,
            LEDGER_STATE_CONSUMED,
        ):
            raise LedgerCorruptError(
                f"ledger entry has unknown state: {state!r}"
            )

        verified = data["verified_state"]
        if not isinstance(verified, str) or verified not in (
            STEP_S1_LEDGER_ACTIVE,
            STEP_S4_STAGED,
            STEP_S6_COMMITTED,
            STEP_S8_PUSHED,
            STEP_S10_LANDED,
        ):
            raise LedgerCorruptError(
                f"ledger entry has unknown verified_state: {verified!r}"
            )

        mutation_intent = data["mutation_intent"]
        if mutation_intent is not None and (
            not isinstance(mutation_intent, str)
            or mutation_intent
            not in (
                MUTATION_INTENT_STAGE,
                MUTATION_INTENT_COMMIT,
                MUTATION_INTENT_PUSH,
                MUTATION_INTENT_VERIFY_CI,
            )
        ):
            raise LedgerCorruptError(
                f"ledger entry has invalid mutation_intent: {mutation_intent!r}"
            )

        mutation_in_progress_substate = data["mutation_in_progress_substate"]
        if mutation_in_progress_substate is not None and (
            not isinstance(mutation_in_progress_substate, str)
            or mutation_in_progress_substate
            not in (
                SUBSTATE_STAGE,
                SUBSTATE_COMMIT,
                SUBSTATE_PUSH,
                SUBSTATE_VERIFY_CI,
            )
        ):
            raise LedgerCorruptError(
                "ledger entry has invalid mutation_in_progress_substate: "
                f"{mutation_in_progress_substate!r}"
            )

        landing_raw = data["landing_commit_sha"]
        if landing_raw is None:
            landing_sha: str | None = None
        else:
            landing_sha = _require_hex_of(
                "landing_commit_sha", landing_raw, 40
            )

        created_at = _require_str("created_at")
        updated_at = _require_str("updated_at")

        history_raw = data["history"]
        if not isinstance(history_raw, list):
            raise LedgerCorruptError(
                "ledger entry history must be a list"
            )
        history: list[dict[str, str]] = []
        for record in history_raw:
            if not isinstance(record, Mapping):
                raise LedgerCorruptError(
                    "ledger entry history entry must be an object"
                )
            step = record.get("step")
            ts = record.get("timestamp")
            notes = record.get("notes")
            if not isinstance(step, str) or not step:
                raise LedgerCorruptError(
                    f"ledger entry history step invalid: {step!r}"
                )
            if not isinstance(ts, str) or not ts:
                raise LedgerCorruptError(
                    f"ledger entry history timestamp invalid: {ts!r}"
                )
            if not isinstance(notes, str):
                raise LedgerCorruptError(
                    f"ledger entry history notes invalid: {notes!r}"
                )
            history.append({"step": step, "timestamp": ts, "notes": notes})

        # F22 cross-field binding.
        if authorized_push_branch != authorized_branch:
            raise LedgerCorruptError(
                "ledger entry authorized_push_branch does not match "
                f"authorized_branch: push={authorized_push_branch!r} "
                f"branch={authorized_branch!r}"
            )
        try:
            canonical_remote_identity = (
                runtime.canonical_identity_for_remote_repository(
                    authorized_remote_repository
                ).as_string()
            )
        except runtime.NudgeLandRemoteError as exc:
            raise LedgerCorruptError(
                "ledger entry authorized_remote_repository is malformed: "
                f"{authorized_remote_repository!r}"
            ) from exc
        if canonical_remote_identity != repository_identity:
            raise LedgerCorruptError(
                "ledger entry authorized_remote_repository does not match "
                f"repository_identity: remote={canonical_remote_identity!r} "
                f"identity={repository_identity!r}"
            )

        # F17 state / mutation / verified / landing-sha coherence.
        def _verify_no_sha(label: str) -> None:
            if landing_sha is not None:
                raise LedgerCorruptError(
                    f"ledger entry has invalid landing_commit_sha for "
                    f"{label}: {landing_sha!r}"
                )

        def _verify_sha_required(label: str) -> None:
            if landing_sha is None:
                raise LedgerCorruptError(
                    f"ledger entry missing landing_commit_sha for {label}"
                )

        if state == LEDGER_STATE_ACTIVE:
            if (
                mutation_intent is not None
                or mutation_in_progress_substate is not None
            ):
                raise LedgerCorruptError(
                    "ledger entry ACTIVE state requires null mutation_intent "
                    "and mutation_in_progress_substate"
                )
            if verified not in (
                STEP_S1_LEDGER_ACTIVE,
                STEP_S4_STAGED,
                STEP_S6_COMMITTED,
                STEP_S8_PUSHED,
            ):
                raise LedgerCorruptError(
                    f"ledger entry ACTIVE state has invalid verified_state: "
                    f"{verified!r}"
                )
            if verified in (STEP_S6_COMMITTED, STEP_S8_PUSHED):
                _verify_sha_required(f"ACTIVE/{verified}")
            else:
                _verify_no_sha(f"ACTIVE/{verified}")
        elif state == LEDGER_STATE_MUTATION_IN_PROGRESS:
            if mutation_intent is None:
                raise LedgerCorruptError(
                    "ledger entry MUTATION_IN_PROGRESS state requires a "
                    "non-null mutation_intent"
                )
            if mutation_intent != mutation_in_progress_substate:
                raise LedgerCorruptError(
                    "ledger entry MUTATION_IN_PROGRESS state requires "
                    "matching mutation_intent and mutation_in_progress_substate"
                )
            if mutation_intent == MUTATION_INTENT_STAGE:
                if verified != STEP_S1_LEDGER_ACTIVE:
                    raise LedgerCorruptError(
                        "ledger entry MUTATION_IN_PROGRESS/STAGE has invalid "
                        f"verified_state: {verified!r}"
                    )
                _verify_no_sha("MUTATION_IN_PROGRESS/STAGE")
            elif mutation_intent == MUTATION_INTENT_COMMIT:
                if verified != STEP_S4_STAGED:
                    raise LedgerCorruptError(
                        "ledger entry MUTATION_IN_PROGRESS/COMMIT has invalid "
                        f"verified_state: {verified!r}"
                    )
                _verify_no_sha("MUTATION_IN_PROGRESS/COMMIT")
            elif mutation_intent == MUTATION_INTENT_PUSH:
                if verified != STEP_S6_COMMITTED:
                    raise LedgerCorruptError(
                        "ledger entry MUTATION_IN_PROGRESS/PUSH has invalid "
                        f"verified_state: {verified!r}"
                    )
                _verify_sha_required("MUTATION_IN_PROGRESS/PUSH")
            elif mutation_intent == MUTATION_INTENT_VERIFY_CI:
                if verified != STEP_S8_PUSHED:
                    raise LedgerCorruptError(
                        "ledger entry MUTATION_IN_PROGRESS/VERIFY_CI has "
                        f"invalid verified_state: {verified!r}"
                    )
                _verify_sha_required("MUTATION_IN_PROGRESS/VERIFY_CI")
            else:
                raise LedgerCorruptError(
                    "ledger entry MUTATION_IN_PROGRESS state has invalid "
                    f"mutation_intent: {mutation_intent!r}"
                )
        elif state == LEDGER_STATE_LANDED:
            if (
                mutation_intent is not None
                or mutation_in_progress_substate is not None
            ):
                raise LedgerCorruptError(
                    "ledger entry LANDED state requires null mutation_intent "
                    "and mutation_in_progress_substate"
                )
            if verified != STEP_S10_LANDED:
                raise LedgerCorruptError(
                    f"ledger entry LANDED state has invalid verified_state: "
                    f"{verified!r}"
                )
            _verify_sha_required("LANDED")
        elif state == LEDGER_STATE_CONSUMED:
            if (
                mutation_intent is not None
                or mutation_in_progress_substate is not None
            ):
                raise LedgerCorruptError(
                    "ledger entry CONSUMED state requires null mutation_intent "
                    "and mutation_in_progress_substate"
                )
            if verified not in (
                STEP_S1_LEDGER_ACTIVE,
                STEP_S4_STAGED,
                STEP_S6_COMMITTED,
                STEP_S8_PUSHED,
            ):
                raise LedgerCorruptError(
                    f"ledger entry CONSUMED state has invalid verified_state: "
                    f"{verified!r}"
                )
            if verified in (STEP_S6_COMMITTED, STEP_S8_PUSHED):
                _verify_sha_required(f"CONSUMED/{verified}")
            else:
                _verify_no_sha(f"CONSUMED/{verified}")
        else:
            raise LedgerCorruptError(
                f"ledger entry has unknown state: {state!r}"
            )

        return cls(
            authorization_id=authorization_id,
            authorization_digest=authorization_digest,
            repository_identity=repository_identity,
            authorized_branch=authorized_branch,
            authorized_base_head=authorized_base_head,
            authorized_push_branch=authorized_push_branch,
            authorized_remote=authorized_remote,
            authorized_remote_repository=canonical_remote_identity,
            authorized_commit_subject=authorized_commit_subject,
            expected_remote_base_sha=expected_remote_base_sha,
            authorized_ci_workflow_or_check=authorized_ci_workflow_or_check,
            expected_ci_event=expected_ci_event,
            authorized_paths=authorized_paths,
            authorized_file_fingerprints=authorized_file_fingerprints,
            expected_initial_status=expected_initial_status,
            state=state,
            mutation_intent=mutation_intent,
            mutation_in_progress_substate=mutation_in_progress_substate,
            verified_state=verified,
            landing_commit_sha=landing_sha,
            created_at=created_at,
            updated_at=updated_at,
            history=history,
        )


def _utc_now_iso() -> str:
    """Return the current UTC time in a deterministic ISO-8601 string."""
    return (
        _datetime.datetime.now(tz=_datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )


# ---------------------------------------------------------------------------
# Ledger store
# ---------------------------------------------------------------------------


class LedgerStore:
    """Persistent outside-worktree transaction ledger."""

    def __init__(self, state_root: str | os.PathLike[str] | None = None) -> None:
        if state_root is None:
            self._state_root = resolve_default_state_root() / DEFAULT_STATE_NAMESPACE
        else:
            self._state_root = pathlib.Path(os.fspath(state_root)).resolve()
        self._ledger_dir = self._state_root / DEFAULT_STATE_LEDGER_DIR
        self._lock_dir = self._state_root / DEFAULT_STATE_LOCK_DIR
        self._auth_lock_dir = self._state_root / DEFAULT_STATE_AUTH_LOCK_DIR

    @property
    def state_root(self) -> pathlib.Path:
        return self._state_root

    @property
    def ledger_dir(self) -> pathlib.Path:
        return self._ledger_dir

    @property
    def lock_dir(self) -> pathlib.Path:
        return self._lock_dir

    # ---- path helpers ----------------------------------------------------

    def _ledger_path(
        self,
        repository_identity: str,
        authorization_id: str,
    ) -> pathlib.Path:
        identity_dir = self._ledger_dir / _safe_component(repository_identity)
        return identity_dir / f"{_safe_component(authorization_id)}{LEDGER_FILE_SUFFIX}"

    def _lock_path(
        self,
        repository_identity: str,
        authorization_id: str,
    ) -> pathlib.Path:
        identity_dir = self._lock_dir / _safe_component(repository_identity)
        return identity_dir / f"{_safe_component(authorization_id)}{LOCK_FILE_SUFFIX}"

    def _auth_lock_path(
        self,
        authorization_id: str,
        authorization_digest: str,
    ) -> pathlib.Path:
        """Path for the authorization-level uniqueness lock file.

        The lock is keyed by the pair
        ``(authorization_id, authorization_digest)`` so the dispatcher
        can serialize same-id+digest transaction discovery before any
        repository observation occurs.
        """
        safe_id = _safe_component(authorization_id)
        safe_digest = _safe_component(authorization_digest)
        return (
            self._auth_lock_dir
            / f"{safe_id}-{safe_digest}{LOCK_FILE_SUFFIX}"
        )

    # ---- existence / loading ---------------------------------------------

    def exists(self, repository_identity: str, authorization_id: str) -> bool:
        return self._ledger_path(repository_identity, authorization_id).exists()

    def load(
        self,
        repository_identity: str,
        authorization_id: str,
        authorization_digest: str,
    ) -> LedgerEntry:
        """Load and validate the ledger entry.

        An existing ledger path that cannot be read is a corruption/trust
        failure — it is never silently converted to a missing entry.
        """
        path = self._ledger_path(repository_identity, authorization_id)
        if not path.exists():
            raise LedgerMissingError(
                f"missing ledger entry for {authorization_id!r}"
            )
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise LedgerCorruptError(
                f"unreadable ledger at {path}: {exc}"
            ) from exc
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LedgerCorruptError(
                f"malformed ledger JSON for {authorization_id!r}: {exc}"
            ) from exc
        entry = LedgerEntry.from_dict(payload)
        _verify_binding(entry, repository_identity, authorization_id, authorization_digest)
        if entry.state in TERMINAL_STATES:
            raise LedgerAuthorizationTerminalError(
                f"authorization {authorization_id!r} is in terminal state "
                f"{entry.state!r}"
            )
        if entry.state == LEDGER_STATE_MUTATION_IN_PROGRESS:
            raise LedgerStaleMutationError(
                f"authorization {authorization_id!r} is in stale "
                f"MUTATION_IN_PROGRESS substate {entry.mutation_in_progress_substate!r}"
            )
        return entry

    def find_by_id_digest(
        self,
        authorization_id: str,
        authorization_digest: str,
    ) -> LedgerEntry:
        """Find a ledger entry using only id+digest.

        Delegates to :meth:`_scan_for_id_digest`, which uses the
        deterministic auth-id-derived ledger filename to identify a
        candidate ledger before trusting its JSON body and which
        distinguishes MISSING / AMBIGUOUS / CORRUPT / FOUND outcomes.

        The caller is responsible for holding the authorization-level
        lock so the scan observes a stable state. A matching candidate
        is also verified against ``MUTATION_IN_PROGRESS`` and
        terminal-state guards.
        """
        if not isinstance(authorization_id, str) or not authorization_id:
            raise LedgerMissingError("authorization_id missing")
        if not isinstance(authorization_digest, str) or not authorization_digest:
            raise LedgerMissingError("authorization_digest missing")

        outcome, payload = self._scan_for_id_digest(
            authorization_id, authorization_digest
        )
        if outcome == "MISSING":
            raise LedgerMissingError(
                f"missing ledger entry for {authorization_id!r}"
            )
        if outcome == "CORRUPT":
            path, reason = payload
            raise LedgerCorruptError(
                f"corrupt ledger at {path}: {reason}"
            )
        if outcome == "AMBIGUOUS":
            raise LedgerAmbiguousError(list(payload))
        # outcome == "FOUND"
        entry = payload
        if entry.state in TERMINAL_STATES:
            raise LedgerAuthorizationTerminalError(
                f"authorization {authorization_id!r} is in terminal state "
                f"{entry.state!r}"
            )
        if entry.state == LEDGER_STATE_MUTATION_IN_PROGRESS:
            raise LedgerStaleMutationError(
                f"authorization {authorization_id!r} is in stale "
                f"MUTATION_IN_PROGRESS substate {entry.mutation_in_progress_substate!r}"
            )
        return entry

    # ---- atomic creation / update ----------------------------------------

    def create(
        self,
        *,
        repository_identity: str,
        authorization_id: str,
        authorization_digest: str,
        authorized_branch: str,
        authorized_base_head: str,
        authorized_push_branch: str,
        authorized_remote: str,
        authorized_remote_repository: str,
        authorized_commit_subject: str,
        expected_remote_base_sha: str,
        authorized_ci_workflow_or_check: str,
        expected_ci_event: str,
        authorized_paths: list[str],
        authorized_file_fingerprints: dict[str, str],
        expected_initial_status: list[dict[str, str]],
    ) -> LedgerEntry:
        """Atomically create a new ``ACTIVE`` ledger entry."""
        with self._acquire_lock(repository_identity, authorization_id):
            return self._create_inner(
                repository_identity=repository_identity,
                authorization_id=authorization_id,
                authorization_digest=authorization_digest,
                authorized_branch=authorized_branch,
                authorized_base_head=authorized_base_head,
                authorized_push_branch=authorized_push_branch,
                authorized_remote=authorized_remote,
                authorized_remote_repository=authorized_remote_repository,
                authorized_commit_subject=authorized_commit_subject,
                expected_remote_base_sha=expected_remote_base_sha,
                authorized_ci_workflow_or_check=authorized_ci_workflow_or_check,
                expected_ci_event=expected_ci_event,
                authorized_paths=authorized_paths,
                authorized_file_fingerprints=authorized_file_fingerprints,
                expected_initial_status=expected_initial_status,
            )

    def _create_inner(
        self,
        *,
        repository_identity: str,
        authorization_id: str,
        authorization_digest: str,
        authorized_branch: str,
        authorized_base_head: str,
        authorized_push_branch: str,
        authorized_remote: str,
        authorized_remote_repository: str,
        authorized_commit_subject: str,
        expected_remote_base_sha: str,
        authorized_ci_workflow_or_check: str,
        expected_ci_event: str,
        authorized_paths: list[str],
        authorized_file_fingerprints: dict[str, str],
        expected_initial_status: list[dict[str, str]],
    ) -> LedgerEntry:
        """Internal: create without acquiring the lock."""
        try:
            canonical_remote_identity = (
                runtime.canonical_identity_for_remote_repository(
                    authorized_remote_repository
                ).as_string()
            )
        except runtime.NudgeLandRemoteError as exc:
            raise LedgerStateError(
                f"invalid authorized_remote_repository at create: {exc}"
            )
        if canonical_remote_identity != repository_identity:
            raise LedgerStateError(
                "authorized_remote_repository canonical identity "
                f"{canonical_remote_identity!r} does not match "
                f"repository_identity {repository_identity!r}"
            )
        path = self._ledger_path(repository_identity, authorization_id)
        if path.exists():
            raise LedgerStateError(
                f"ledger entry already exists for {authorization_id!r}"
            )
        now = _utc_now_iso()
        entry = LedgerEntry(
            authorization_id=authorization_id,
            authorization_digest=authorization_digest,
            repository_identity=repository_identity,
            authorized_branch=authorized_branch,
            authorized_base_head=authorized_base_head,
            authorized_push_branch=authorized_push_branch,
            authorized_remote=authorized_remote,
            authorized_remote_repository=canonical_remote_identity,
            authorized_commit_subject=authorized_commit_subject,
            expected_remote_base_sha=expected_remote_base_sha,
            authorized_ci_workflow_or_check=authorized_ci_workflow_or_check,
            expected_ci_event=expected_ci_event,
            authorized_paths=list(authorized_paths),
            authorized_file_fingerprints=dict(authorized_file_fingerprints),
            expected_initial_status=list(expected_initial_status),
            state=LEDGER_STATE_ACTIVE,
            mutation_intent=None,
            mutation_in_progress_substate=None,
            verified_state=STEP_S1_LEDGER_ACTIVE,
            landing_commit_sha=None,
            created_at=now,
            updated_at=now,
            history=[
                {
                    "step": STEP_S1_LEDGER_ACTIVE,
                    "timestamp": now,
                    "notes": "ledger created",
                }
            ],
        )
        new_payload = entry.to_dict()
        self._atomic_write(path, new_payload)
        return entry

    def advance(
        self,
        entry: LedgerEntry,
        *,
        new_state: str,
        new_verified_state: str,
        mutation_intent: str | None,
        mutation_in_progress_substate: str | None,
        notes: str,
        landing_commit_sha: str | None = None,
    ) -> LedgerEntry:
        """Atomically update the ledger entry to a new state.

        The caller-visible ``entry`` is mutated ONLY after the new
        durable representation has been fsync'd. If persistence fails
        the in-memory entry remains at its previous durable state.
        """
        with self._acquire_lock(entry.repository_identity, entry.authorization_id):
            return self._advance_inner(
                entry,
                new_state=new_state,
                new_verified_state=new_verified_state,
                mutation_intent=mutation_intent,
                mutation_in_progress_substate=mutation_in_progress_substate,
                notes=notes,
                landing_commit_sha=landing_commit_sha,
            )

    def _advance_inner(
        self,
        entry: LedgerEntry,
        *,
        new_state: str,
        new_verified_state: str,
        mutation_intent: str | None,
        mutation_in_progress_substate: str | None,
        notes: str,
        landing_commit_sha: str | None = None,
    ) -> LedgerEntry:
        """Internal: advance without acquiring the lock."""
        if entry.state in TERMINAL_STATES:
            raise LedgerAuthorizationTerminalError(
                f"authorization {entry.authorization_id!r} is in terminal state "
                f"{entry.state!r}"
            )
        _verify_state_transition(entry.state, new_state)
        _verify_verified_state(new_verified_state)
        if new_state == LEDGER_STATE_MUTATION_IN_PROGRESS:
            if (
                mutation_intent is None
                or mutation_in_progress_substate is None
                or mutation_intent != mutation_in_progress_substate
            ):
                raise LedgerStateError(
                    "mutation_intent and mutation_in_progress_substate "
                    "must both be non-null and equal when advancing to "
                    f"{LEDGER_STATE_MUTATION_IN_PROGRESS!r}; got "
                    f"mutation_intent={mutation_intent!r} "
                    f"mutation_in_progress_substate="
                    f"{mutation_in_progress_substate!r}"
                )
        elif new_state == LEDGER_STATE_LANDED:
            if (
                new_verified_state != STEP_S10_LANDED
                or mutation_intent is not None
                or mutation_in_progress_substate is not None
                or landing_commit_sha is None
            ):
                raise LedgerStateError(
                    "LANDED advance requires verified_state="
                    f"{STEP_S10_LANDED!r}, null mutation_intent, null "
                    "mutation_in_progress_substate, and a non-null "
                    f"landing_commit_sha; got new_verified_state="
                    f"{new_verified_state!r} mutation_intent="
                    f"{mutation_intent!r} mutation_in_progress_substate="
                    f"{mutation_in_progress_substate!r} landing_commit_sha="
                    f"{landing_commit_sha!r}"
                )
        now = _utc_now_iso()
        new_payload = entry.to_dict()
        new_payload["state"] = new_state
        new_payload["mutation_intent"] = mutation_intent
        new_payload["mutation_in_progress_substate"] = mutation_in_progress_substate
        new_payload["verified_state"] = new_verified_state
        new_payload["updated_at"] = now
        history = list(new_payload.get("history", []))
        history.append(
            {
                "step": new_verified_state,
                "timestamp": now,
                "notes": notes,
            }
        )
        new_payload["history"] = history
        if landing_commit_sha is not None:
            _verify_hex(landing_commit_sha, 40, "landing_commit_sha")
            new_payload["landing_commit_sha"] = landing_commit_sha
        path = self._ledger_path(
            entry.repository_identity, entry.authorization_id
        )
        self._atomic_write(path, new_payload)
        entry.state = new_state
        entry.mutation_intent = mutation_intent
        entry.mutation_in_progress_substate = mutation_in_progress_substate
        entry.verified_state = new_verified_state
        entry.updated_at = now
        entry.history = history
        if landing_commit_sha is not None:
            entry.landing_commit_sha = landing_commit_sha
        return entry

    def append_history(
        self,
        entry: LedgerEntry,
        *,
        step: str,
        notes: str,
        new_state: str | None = None,
        new_verified_state: str | None = None,
    ) -> LedgerEntry:
        """Append a history record without advancing the verified step."""
        with self._acquire_lock(entry.repository_identity, entry.authorization_id):
            return self._append_history_inner(
                entry,
                step=step,
                notes=notes,
                new_state=new_state,
                new_verified_state=new_verified_state,
            )

    def _append_history_inner(
        self,
        entry: LedgerEntry,
        *,
        step: str,
        notes: str,
        new_state: str | None = None,
        new_verified_state: str | None = None,
    ) -> LedgerEntry:
        """Internal: append history without acquiring the lock."""
        if entry.state in TERMINAL_STATES:
            raise LedgerAuthorizationTerminalError(
                f"authorization {entry.authorization_id!r} is in terminal state "
                f"{entry.state!r}"
            )
        now = _utc_now_iso()
        new_payload = entry.to_dict()
        history = list(new_payload.get("history", []))
        history.append(
            {
                "step": step,
                "timestamp": now,
                "notes": notes,
            }
        )
        new_payload["history"] = history
        new_payload["updated_at"] = now
        if new_state is not None:
            _verify_state_transition(entry.state, new_state)
            new_payload["state"] = new_state
        if new_verified_state is not None:
            _verify_verified_state(new_verified_state)
            new_payload["verified_state"] = new_verified_state
        path = self._ledger_path(
            entry.repository_identity, entry.authorization_id
        )
        self._atomic_write(path, new_payload)
        entry.history = history
        entry.updated_at = now
        if new_state is not None:
            entry.state = new_state
        if new_verified_state is not None:
            entry.verified_state = new_verified_state
        return entry

    # ---- atomic write primitive ------------------------------------------

    def _atomic_write(self, path: pathlib.Path, payload: dict[str, Any]) -> None:
        """Write ``payload`` atomically into ``path`` with fail-closed fsync.

        Durability phases:

        1. write the serialized payload to a temporary file in the same
           directory,
        2. ``flush``,
        3. ``fsync`` the temporary file descriptor. Failure here raises
           :class:`LedgerDurabilityError` with
           :data:`LEDGER_DURABILITY_PRE_REPLACE`; the previously durable
           ledger state is intact.
        4. ``os.replace`` atomically swaps the temporary file into place.
        5. ``fsync`` the directory file descriptor. Failure here raises
           :class:`LedgerDurabilityError` with
           :data:`LEDGER_DURABILITY_POST_REPLACE`; direct durability of
           the new state is NOT ESTABLISHED — the previous and the new
           state are both possible on next read.
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise LedgerDurabilityError(
                f"parent-directory mkdir failed for {path.parent}: {exc}",
                kind=LEDGER_DURABILITY_PRE_REPLACE,
            ) from exc
        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        try:
            fd, tmp_path = tempfile.mkstemp(
                prefix=path.name + ".",
                suffix=".tmp",
                dir=str(path.parent),
            )
        except OSError as exc:
            raise LedgerDurabilityError(
                f"tempfile.mkstemp failed for {path}: {exc}",
                kind=LEDGER_DURABILITY_PRE_REPLACE,
            ) from exc
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                try:
                    fh.write(serialized)
                except OSError as exc:
                    raise LedgerDurabilityError(
                        f"temporary-file write failed for {path}: {exc}",
                        kind=LEDGER_DURABILITY_PRE_REPLACE,
                    ) from exc
                try:
                    fh.flush()
                except OSError as exc:
                    raise LedgerDurabilityError(
                        f"temporary-file flush failed for {path}: {exc}",
                        kind=LEDGER_DURABILITY_PRE_REPLACE,
                    ) from exc
                try:
                    os.fsync(fh.fileno())
                except OSError as exc:
                    raise LedgerDurabilityError(
                        f"file fsync failed for {path}: {exc}",
                        kind=LEDGER_DURABILITY_PRE_REPLACE,
                    ) from exc
            try:
                os.replace(tmp_path, str(path))
            except OSError as exc:
                raise LedgerDurabilityError(
                    f"os.replace failed for {path}: {exc}",
                    kind=LEDGER_DURABILITY_PRE_REPLACE,
                ) from exc
            try:
                dir_fd = os.open(str(path.parent), os.O_DIRECTORY)
            except OSError as exc:
                raise LedgerDurabilityError(
                    f"directory os.open failed for {path.parent}: {exc}",
                    kind=LEDGER_DURABILITY_POST_REPLACE,
                ) from exc
            try:
                os.fsync(dir_fd)
            except OSError as exc:
                raise LedgerDurabilityError(
                    f"directory fsync failed for {path.parent}: {exc}",
                    kind=LEDGER_DURABILITY_POST_REPLACE,
                ) from exc
            finally:
                os.close(dir_fd)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    # ---- lock primitive ---------------------------------------------------

    def _acquire_lock(
        self,
        repository_identity: str,
        authorization_id: str,
    ):
        """Return a context manager that acquires the per-authorization lock."""
        return _LockContext(self._lock_path(repository_identity, authorization_id))

    def _acquire_auth_lock(
        self,
        authorization_id: str,
        authorization_digest: str,
    ):
        """Return a context manager that acquires the authorization lock.

        The lock is keyed by ``(authorization_id, authorization_digest)``
        so the dispatcher can serialize same-id+digest transaction
        discovery before any per-repository observation occurs.
        """
        return _LockContext(
            self._auth_lock_path(authorization_id, authorization_digest)
        )

    def transaction(
        self,
        repository_identity: str,
        authorization_id: str,
    ) -> "_Transaction":
        """Return a context manager that holds the per-authorization lock.

        The yielded transaction object exposes the unlocked variants of
        ``create``, ``advance``, ``append_history`` and ``load`` so the
        dispatcher can hold one lock across every persistence, mutation,
        and proof stage of the operation.
        """
        return _Transaction(self, repository_identity, authorization_id)

    # ---- id+digest scan ---------------------------------------------------

    def _scan_for_id_digest(
        self,
        authorization_id: str,
        authorization_digest: str,
    ) -> tuple[str, Any]:
        """Scan the ledger directory for a candidate under the auth lock.

        Returns a structured tuple that distinguishes every terminal
        outcome of the lookup. The caller is expected to hold the
        authorization-level lock so the scan observes a stable state.

        Possible outcomes:

        * ``("MISSING", None)`` — no candidate file matches.
        * ``("AMBIGUOUS", sorted_identities)`` — more than one
          candidate file matches across identity directories.
        * ``("CORRUPT", (path, reason))`` — a candidate file exists at
          the expected auth-id-derived ledger path but cannot be read,
          contains malformed JSON, has an invalid production schema,
          claims a different authorization id, or has an invalid
          repository binding. Corrupt candidates are NEVER silently
          skipped: a single corrupt candidate means the lookup fails
          closed with corruption rather than reporting a fabricated
          zero match.
        * ``("FOUND", entry)`` — exactly one valid candidate matched
          both the auth-id-derived ledger path AND the supplied
          ``authorization_digest``.

        A different ``authorization_digest`` for the same id is treated
        as a binding mismatch (no valid match) — the file is internally
        valid but does not manufacture authority for the requested
        operation.
        """
        expected_filename = (
            f"{_safe_component(authorization_id)}{LEDGER_FILE_SUFFIX}"
        )
        if not self._ledger_dir.exists():
            return ("MISSING", None)
        matches: list[LedgerEntry] = []
        first_corrupt: tuple[pathlib.Path, str] | None = None
        for identity_dir in self._ledger_dir.iterdir():
            if not identity_dir.is_dir():
                continue
            candidate_path = identity_dir / expected_filename
            if not candidate_path.exists():
                continue
            # The auth-id-derived ledger path is deterministic. Any
            # rejection here is a corruption signal, never a silent
            # skip: A5 mandates that a ledger at the expected path
            # which cannot be read, cannot be parsed, has an invalid
            # schema, claims a different id, or has a binding mismatch
            # against the directory identity is reported as CORRUPT.
            try:
                raw = candidate_path.read_bytes()
            except OSError as exc:
                if first_corrupt is None:
                    first_corrupt = (candidate_path, f"unreadable: {exc}")
                continue
            try:
                raw_text = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                if first_corrupt is None:
                    first_corrupt = (candidate_path, f"invalid UTF-8: {exc}")
                continue
            try:
                payload = json.loads(raw_text)
            except json.JSONDecodeError as exc:
                if first_corrupt is None:
                    first_corrupt = (candidate_path, f"malformed JSON: {exc}")
                continue
            if not isinstance(payload, Mapping):
                if first_corrupt is None:
                    first_corrupt = (candidate_path, "non-object payload")
                continue
            try:
                entry = LedgerEntry.from_dict(payload)
            except LedgerCorruptError as exc:
                if first_corrupt is None:
                    first_corrupt = (candidate_path, f"invalid schema: {exc}")
                continue
            if entry.authorization_id != authorization_id:
                # Path encoded our auth_id but the file's body claims a
                # different one. This is path/content mismatch and is a
                # corruption signal, not a silent skip.
                if first_corrupt is None:
                    first_corrupt = (
                        candidate_path,
                        f"authorization_id mismatch: {entry.authorization_id!r}",
                    )
                continue
            if entry.authorization_digest != authorization_digest:
                # Different digest for the same id: no valid match. Do
                # NOT manufacture authority; do NOT report corruption.
                # Continue scanning for a matching candidate.
                continue
            # Validate that the entry's repository_identity is
            # consistent with the directory it lives in.
            expected_dir_name = _safe_component(entry.repository_identity)
            if expected_dir_name != identity_dir.name:
                if first_corrupt is None:
                    first_corrupt = (
                        candidate_path,
                        "repository binding mismatch",
                    )
                continue
            matches.append(entry)
        if first_corrupt is not None:
            return ("CORRUPT", first_corrupt)
        if not matches:
            return ("MISSING", None)
        if len(matches) > 1:
            identities = sorted(entry.repository_identity for entry in matches)
            return ("AMBIGUOUS", identities)
        return ("FOUND", matches[0])


# ---------------------------------------------------------------------------
# Lock context manager
# ---------------------------------------------------------------------------


class _LockContext:
    """Context manager that holds ``fcntl.flock(LOCK_EX | LOCK_NB)``."""

    def __init__(self, lock_path: pathlib.Path) -> None:
        self._lock_path = lock_path
        self._fd: int | None = None

    def __enter__(self) -> "_LockContext":
        try:
            self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise LedgerLockedError(
                f"failed to acquire ledger lock {self._lock_path}"
            ) from exc
        try:
            fd = os.open(
                str(self._lock_path),
                os.O_CREAT | os.O_RDWR,
                0o600,
            )
        except OSError as exc:
            raise LedgerLockedError(
                f"failed to acquire ledger lock {self._lock_path}"
            ) from exc
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            try:
                os.close(fd)
            finally:
                raise LedgerLockedError(
                    f"failed to acquire ledger lock {self._lock_path}"
                ) from exc
        self._fd = fd
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._fd is not None:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_UN)
            finally:
                os.close(self._fd)
                self._fd = None


# ---------------------------------------------------------------------------
# Transaction context manager
# ---------------------------------------------------------------------------


class _Transaction:
    """Hold the per-authorization lock for the duration of one operation.

    Each operation (stage / commit / push / verify_ci) acquires the
    transaction at entry and releases it at exit. The nested unlocked
    variants ensure no second same-authorization transaction can
    interleave between the persistence, mutation, and proof stages of
    the same operation.
    """

    def __init__(
        self,
        store: "LedgerStore",
        repository_identity: str,
        authorization_id: str,
    ) -> None:
        self._store = store
        self._repository_identity = repository_identity
        self._authorization_id = authorization_id
        self._fd: int | None = None

    @property
    def repository_identity(self) -> str:
        return self._repository_identity

    @property
    def authorization_id(self) -> str:
        return self._authorization_id

    def __enter__(self) -> "_Transaction":
        lock_path = self._store._lock_path(
            self._repository_identity, self._authorization_id
        )
        try:
            lock_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise LedgerLockedError(
                f"failed to acquire ledger lock {lock_path}"
            ) from exc
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o600)
        except OSError as exc:
            raise LedgerLockedError(
                f"failed to acquire ledger lock {lock_path}"
            ) from exc
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            try:
                os.close(fd)
            finally:
                raise LedgerLockedError(
                    f"failed to acquire ledger lock {lock_path}"
                ) from exc
        self._fd = fd
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._fd is not None:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_UN)
            finally:
                os.close(self._fd)
                self._fd = None

    # ---- unlocked primitives --------------------------------------------

    def create(
        self,
        *,
        authorization_digest: str,
        authorized_branch: str,
        authorized_base_head: str,
        authorized_push_branch: str,
        authorized_remote: str,
        authorized_remote_repository: str,
        authorized_commit_subject: str,
        expected_remote_base_sha: str,
        authorized_ci_workflow_or_check: str,
        expected_ci_event: str,
        authorized_paths: list[str],
        authorized_file_fingerprints: dict[str, str],
        expected_initial_status: list[dict[str, str]],
    ) -> LedgerEntry:
        return self._store._create_inner(
            repository_identity=self._repository_identity,
            authorization_id=self._authorization_id,
            authorization_digest=authorization_digest,
            authorized_branch=authorized_branch,
            authorized_base_head=authorized_base_head,
            authorized_push_branch=authorized_push_branch,
            authorized_remote=authorized_remote,
            authorized_remote_repository=authorized_remote_repository,
            authorized_commit_subject=authorized_commit_subject,
            expected_remote_base_sha=expected_remote_base_sha,
            authorized_ci_workflow_or_check=authorized_ci_workflow_or_check,
            expected_ci_event=expected_ci_event,
            authorized_paths=authorized_paths,
            authorized_file_fingerprints=authorized_file_fingerprints,
            expected_initial_status=expected_initial_status,
        )

    def load(self, authorization_digest: str) -> LedgerEntry:
        """Load and validate the ledger entry under the held transaction lock.

        An existing ledger path that cannot be read is a corruption/trust
        failure — it is never silently converted to a missing entry.
        """
        path = self._store._ledger_path(
            self._repository_identity, self._authorization_id
        )
        if not path.exists():
            raise LedgerMissingError(
                f"missing ledger entry for {self._authorization_id!r}"
            )
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise LedgerCorruptError(
                f"unreadable ledger at {path}: {exc}"
            ) from exc
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LedgerCorruptError(
                f"malformed ledger JSON for {self._authorization_id!r}: {exc}"
            ) from exc
        entry = LedgerEntry.from_dict(payload)
        _verify_binding(
            entry,
            self._repository_identity,
            self._authorization_id,
            authorization_digest,
        )
        if entry.state in TERMINAL_STATES:
            raise LedgerAuthorizationTerminalError(
                f"authorization {self._authorization_id!r} is in terminal state "
                f"{entry.state!r}"
            )
        if entry.state == LEDGER_STATE_MUTATION_IN_PROGRESS:
            raise LedgerStaleMutationError(
                f"authorization {self._authorization_id!r} is in stale "
                f"MUTATION_IN_PROGRESS substate {entry.mutation_in_progress_substate!r}"
            )
        return entry

    def advance(
        self,
        entry: LedgerEntry,
        *,
        new_state: str,
        new_verified_state: str,
        mutation_intent: str | None,
        mutation_in_progress_substate: str | None,
        notes: str,
        landing_commit_sha: str | None = None,
    ) -> LedgerEntry:
        return self._store._advance_inner(
            entry,
            new_state=new_state,
            new_verified_state=new_verified_state,
            mutation_intent=mutation_intent,
            mutation_in_progress_substate=mutation_in_progress_substate,
            notes=notes,
            landing_commit_sha=landing_commit_sha,
        )

    def append_history(
        self,
        entry: LedgerEntry,
        *,
        step: str,
        notes: str,
        new_state: str | None = None,
        new_verified_state: str | None = None,
    ) -> LedgerEntry:
        return self._store._append_history_inner(
            entry,
            step=step,
            notes=notes,
            new_state=new_state,
            new_verified_state=new_verified_state,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _safe_component(value: str) -> str:
    """Return a filesystem-safe component derived from ``value``."""
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"sha256-{digest}"


def _verify_binding(
    entry: LedgerEntry,
    repository_identity: str,
    authorization_id: str,
    authorization_digest: str,
) -> None:
    """Verify the ledger entry binds to the supplied identifiers."""
    if entry.authorization_id != authorization_id:
        raise LedgerCorruptError(
            "authorization id mismatch: ledger="
            f"{entry.authorization_id!r} caller={authorization_id!r}"
        )
    if entry.authorization_digest != authorization_digest:
        raise LedgerCorruptError(
            "authorization digest mismatch in ledger"
        )
    if entry.repository_identity != repository_identity:
        raise LedgerCorruptError(
            "repository identity mismatch in ledger"
        )


def _verify_state_transition(current: str, new: str) -> None:
    """Validate a forward-progress state transition."""
    if current == new:
        raise LedgerStateError(
            f"state transition must change the state: {current!r}"
        )
    allowed: dict[str, tuple[str, ...]] = {
        LEDGER_STATE_ACTIVE: (
            LEDGER_STATE_MUTATION_IN_PROGRESS,
            LEDGER_STATE_LANDED,
            LEDGER_STATE_CONSUMED,
        ),
        LEDGER_STATE_MUTATION_IN_PROGRESS: (
            LEDGER_STATE_ACTIVE,
            LEDGER_STATE_LANDED,
            LEDGER_STATE_CONSUMED,
        ),
        LEDGER_STATE_LANDED: (),
        LEDGER_STATE_CONSUMED: (),
    }
    if new not in allowed.get(current, ()):
        raise LedgerStateError(
            f"illegal state transition {current!r} -> {new!r}"
        )


def _verify_verified_state(state: str) -> None:
    if state not in (
        STEP_S1_LEDGER_ACTIVE,
        STEP_S4_STAGED,
        STEP_S6_COMMITTED,
        STEP_S8_PUSHED,
        STEP_S10_LANDED,
    ):
        raise LedgerStateError(
            f"illegal verified_state: {state!r}"
        )


def _verify_hex(value: str, length: int, field: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != length
        or not all(c in "0123456789abcdefABCDEF" for c in value)
    ):
        raise LedgerStateError(
            f"{field} must be a {length}-char hex str"
        )


def _require_hex_of(field_name: str, value: Any, length: int) -> str:
    """Strict hex validation helper that raises ``LedgerCorruptError``."""
    if (
        not isinstance(value, str)
        or len(value) != length
        or not all(c in "0123456789abcdefABCDEF" for c in value)
    ):
        raise LedgerCorruptError(
            f"ledger entry has invalid {field_name}: {value!r}"
        )
    return value


def _is_canonical_repo_identity(identity: str) -> bool:
    """Return True iff ``identity`` parses as a canonical repository identity.

    Delegates canonical validity to
    :func:`nudge_land_runtime.parse_canonical_repo` so the ledger does not
    maintain its own repository grammar.
    """
    try:
        runtime.parse_canonical_repo(identity)
    except runtime.NudgeLandRemoteError:
        return False
    return True


__all__ = [
    "DEFAULT_STATE_AUTH_LOCK_DIR",
    "LEDGER_DURABILITY_PRE_REPLACE",
    "LEDGER_DURABILITY_POST_REPLACE",
    "LEDGER_FILE_SUFFIX",
    "LEDGER_STATE_ACTIVE",
    "LEDGER_STATE_CONSUMED",
    "LEDGER_STATE_DURABILITY_NOT_ESTABLISHED",
    "LEDGER_STATE_LANDED",
    "LEDGER_STATE_MUTATION_IN_PROGRESS",
    "LOCK_FILE_SUFFIX",
    "MUTATION_INTENT_COMMIT",
    "MUTATION_INTENT_PUSH",
    "MUTATION_INTENT_STAGE",
    "MUTATION_INTENT_VERIFY_CI",
    "STEP_S1_LEDGER_ACTIVE",
    "STEP_S4_STAGED",
    "STEP_S6_COMMITTED",
    "STEP_S8_PUSHED",
    "STEP_S10_LANDED",
    "SUBSTATE_COMMIT",
    "SUBSTATE_PUSH",
    "SUBSTATE_STAGE",
    "SUBSTATE_VERIFY_CI",
    "LedgerAmbiguousError",
    "LedgerAuthorizationTerminalError",
    "LedgerCorruptError",
    "LedgerDurabilityError",
    "LedgerEntry",
    "LedgerError",
    "LedgerLockedError",
    "LedgerMissingError",
    "LedgerStaleMutationError",
    "LedgerStateError",
    "LedgerStore",
    "TERMINAL_STATES",
    "resolve_default_state_root",
]
