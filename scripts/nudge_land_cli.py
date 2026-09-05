"""Deterministic JSON-over-stdin operation dispatcher for NudgeWhen nudge-land.

The CLI dispatcher accepts exactly one of the four operations
``stage``, ``commit``, ``push``, ``verify_ci`` as its first argument.
Every operation reads exactly one JSON object from standard input and
writes exactly one structured JSON receipt to standard output. Any
diagnostic text is written to standard error only.

The worktree is always resolved from ``os.getcwd()``; the dispatcher
does not accept an external worktree path from model input.

The operations and their state-machine transitions:

* ``stage``:
  - validates the full authorization object including digest;
  - verifies the canonical repository identity from the configured
    remote;
  - verifies the exact branch and exact base HEAD;
  - verifies the exact pre-state (every authorized path is present
    with its expected worktree status and SHA-256 fingerprint);
  - establishes the ledger atomically BEFORE first mutation;
  - persists the mutation intent while retaining
    ``S1_LEDGER_ACTIVE`` as the verified state;
  - executes exactly ``git add -- <authorized paths>`` through an
    argument-vector subprocess;
  - verifies the cached path set, cached whitespace verdict, and raw
    cached bytes against the authorized fingerprints;
  - advances the ledger to ``S4_STAGED`` only after every cached
    proof succeeds.

* ``commit``:
  - input carries only ``authorization_id`` and ``authorization_digest``;
  - scans the ledger directory for the unique matching id+digest;
  - acquires the per-authorization transaction lock;
  - re-verifies cached path set, cached whitespace verdict, and raw
    cached bytes against the authorized fingerprints;
  - persists ``MUTATION_IN_PROGRESS:COMMIT`` while retaining
    ``S4_STAGED`` as the durable ``verified_state``;
  - executes exactly one commit with the authorized subject (no
    ``--amend``, no ``-a``, no retry);
  - verifies HEAD parent, HEAD subject, HEAD-vs-parent changed paths,
    and HEAD raw blob bytes;
  - verifies the post-commit working tree is clean;
  - advances to ``S6_COMMITTED`` and persists the landing SHA.

* ``push``:
  - input carries only ``authorization_id`` and ``authorization_digest``;
  - scans the ledger directory for the unique matching id+digest;
  - acquires the per-authorization transaction lock;
  - re-verifies the local remote push destination identity;
  - requires the current local HEAD to match the persisted
    ``landing_commit_sha``;
  - independently establishes the expected remote branch base SHA and
    compares it to ``expected_remote_base_sha``;
  - persists ``MUTATION_IN_PROGRESS:PUSH`` while retaining
    ``S6_COMMITTED`` as the durable ``verified_state``;
  - executes exactly one ordinary non-force push:
    ``git push <remote> <push_branch>``;
  - no force, no force-with-lease, no retry;
  - independently establishes the post-push branch SHA and requires
    equality with the persisted ``landing_commit_sha``;
  - advances to ``S8_PUSHED``.

* ``verify_ci``:
  - input carries only ``authorization_id`` and ``authorization_digest``;
  - scans the ledger directory for the unique matching id+digest;
  - acquires the per-authorization transaction lock;
  - persists ``MUTATION_IN_PROGRESS:VERIFY_CI`` while retaining
    ``S8_PUSHED`` as the durable ``verified_state``;
  - uses the persisted ``landing_commit_sha`` as the immutable
    expected CI head;
  - bounded internal polling only;
  - accepts only an exact authorized workflow + head + branch + event
    + success response;
  - failure / cancellation / timeout / mismatch consumes the
    authorization;
  - success marks ``LANDED / S10_LANDED``.

Any hard stop records the actual last verified state, the mutation
attempted/result, and never retries, never infers rollback.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
from typing import Any, Callable, Mapping, Sequence

from scripts import nudge_land_ledger as ledger_mod
from scripts import nudge_land_runtime as runtime


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


OPERATION_STAGE = "stage"
OPERATION_COMMIT = "commit"
OPERATION_PUSH = "push"
OPERATION_VERIFY_CI = "verify_ci"

SUPPORTED_OPERATIONS: tuple[str, ...] = (
    OPERATION_STAGE,
    OPERATION_COMMIT,
    OPERATION_PUSH,
    OPERATION_VERIFY_CI,
)

# Default poll configuration for verify_ci. C2B tests use mocked
# process responses and never exercise real polling against GitHub.
DEFAULT_VERIFY_CI_TIMEOUT_SECONDS = 60.0
DEFAULT_VERIFY_CI_INTERVAL_SECONDS = 1.0


# ---------------------------------------------------------------------------
# Hard-stop reasons — surfaced in the receipt
# ---------------------------------------------------------------------------


HARD_STOP_UNKNOWN_OPERATION = "HARD_STOP_UNKNOWN_OPERATION"
HARD_STOP_MALFORMED_JSON = "HARD_STOP_MALFORMED_JSON"
HARD_STOP_MISSING_FIELDS = "HARD_STOP_MISSING_FIELDS"
HARD_STOP_BAD_DIGEST = "HARD_STOP_BAD_DIGEST"
HARD_STOP_UNSUPPORTED_STATUS = "HARD_STOP_UNSUPPORTED_STATUS"
HARD_STOP_BAD_REMOTE = "HARD_STOP_BAD_REMOTE"
HARD_STOP_REMOTE_SHA_MISMATCH = "HARD_STOP_REMOTE_SHA_MISMATCH"
HARD_STOP_UNEXPECTED_DIRTY_PATH = "HARD_STOP_UNEXPECTED_DIRTY_PATH"
HARD_STOP_PATH_NOT_FOUND = "HARD_STOP_PATH_NOT_FOUND"
HARD_STOP_FINGERPRINT_MISMATCH = "HARD_STOP_FINGERPRINT_MISMATCH"
HARD_STOP_CACHED_PATH_SET_MISMATCH = "HARD_STOP_CACHED_PATH_SET_MISMATCH"
HARD_STOP_CACHED_STATUS_SET_MISMATCH = "HARD_STOP_CACHED_STATUS_SET_MISMATCH"
HARD_STOP_CACHED_WHITESPACE = "HARD_STOP_CACHED_WHITESPACE"
HARD_STOP_CACHED_BLOB_MISMATCH = "HARD_STOP_CACHED_BLOB_MISMATCH"
HARD_STOP_LEDGER_ERROR = "HARD_STOP_LEDGER_ERROR"
HARD_STOP_LEDGER_LOCKED = "HARD_STOP_LEDGER_LOCKED"
HARD_STOP_LEDGER_TERMINAL = "HARD_STOP_LEDGER_TERMINAL"
HARD_STOP_LEDGER_STALE_MUTATION = "HARD_STOP_LEDGER_STALE_MUTATION"
HARD_STOP_LEDGER_MISSING = "HARD_STOP_LEDGER_MISSING"
HARD_STOP_LEDGER_AMBIGUOUS = "HARD_STOP_LEDGER_AMBIGUOUS"
HARD_STOP_LEDGER_CORRUPT = "HARD_STOP_LEDGER_CORRUPT"
HARD_STOP_BRANCH_MISMATCH = "HARD_STOP_BRANCH_MISMATCH"
HARD_STOP_BASE_HEAD_MISMATCH = "HARD_STOP_BASE_HEAD_MISMATCH"
HARD_STOP_NO_AUTHORIZATION = "HARD_STOP_NO_AUTHORIZATION"
HARD_STOP_REVVERIF_CACHED_FAILED = "HARD_STOP_REVVERIF_CACHED_FAILED"
HARD_STOP_COMMIT_SUBJECT_MISMATCH = "HARD_STOP_COMMIT_SUBJECT_MISMATCH"
HARD_STOP_COMMIT_CHANGED_PATHS_MISMATCH = "HARD_STOP_COMMIT_CHANGED_PATHS_MISMATCH"
HARD_STOP_COMMIT_BLOB_MISMATCH = "HARD_STOP_COMMIT_BLOB_MISMATCH"
HARD_STOP_POST_COMMIT_DIRTY = "HARD_STOP_POST_COMMIT_DIRTY"
HARD_STOP_REMOTE_DESTINATION_MISMATCH = "HARD_STOP_REMOTE_DESTINATION_MISMATCH"
HARD_STOP_PUSH_SHA_MISMATCH = "HARD_STOP_PUSH_SHA_MISMATCH"
HARD_STOP_STAGE_FAILED = "HARD_STOP_STAGE_FAILED"
HARD_STOP_COMMIT_FAILED = "HARD_STOP_COMMIT_FAILED"
HARD_STOP_PUSH_FAILED = "HARD_STOP_PUSH_FAILED"
HARD_STOP_LOCAL_HEAD_DRIFT = "HARD_STOP_LOCAL_HEAD_DRIFT"
HARD_STOP_CI_REJECTED = "HARD_STOP_CI_REJECTED"
HARD_STOP_CI_TIMEOUT = "HARD_STOP_CI_TIMEOUT"
HARD_STOP_CONSUMED_PERSISTENCE_FAILED = "HARD_STOP_CONSUMED_PERSISTENCE_FAILED"
HARD_STOP_DURABILITY_NOT_ESTABLISHED = "HARD_STOP_DURABILITY_NOT_ESTABLISHED"


# ---------------------------------------------------------------------------
# Input / output plumbing
# ---------------------------------------------------------------------------


def read_stdin_payload() -> dict[str, Any]:
    """Read and decode exactly one JSON object from stdin."""
    raw = sys.stdin.buffer.read()
    if not raw.strip():
        raise ValueError("stdin was empty; expected a JSON object")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed JSON on stdin: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("stdin JSON must be a top-level object")
    return payload


def resolve_worktree_path() -> str:
    """Resolve the worktree path from the current process cwd."""
    return str(pathlib.Path(os.getcwd()).resolve())


# ---------------------------------------------------------------------------
# Argument-vector runners
# ---------------------------------------------------------------------------


GitRunner = Callable[[Sequence[str], str], runtime.ProcessResult]


def git_add_paths(
    worktree: str,
    paths: Sequence[str],
    *,
    runner: GitRunner | None = None,
) -> runtime.ProcessResult:
    """Run ``git add -- <paths>`` as an argument vector."""
    argv: list[str] = ["git", "add", "--"]
    argv.extend(paths)
    if runner is None:
        return runtime.run_process(argv, cwd=worktree)
    return runner(argv, worktree)


def git_commit(
    worktree: str,
    subject: str,
    *,
    runner: GitRunner | None = None,
) -> runtime.ProcessResult:
    """Run ``git commit -m <subject>`` as an argument vector."""
    argv = ["git", "commit", "-m", subject]
    if runner is None:
        return runtime.run_process(argv, cwd=worktree)
    return runner(argv, worktree)


def git_push(
    worktree: str,
    remote: str,
    branch: str,
    *,
    runner: GitRunner | None = None,
) -> runtime.ProcessResult:
    """Run ``git push <remote> <branch>`` as an argument vector."""
    argv = ["git", "push", remote, branch]
    if runner is None:
        return runtime.run_process(argv, cwd=worktree)
    return runner(argv, worktree)


# ---------------------------------------------------------------------------
# Authorization parsing helpers
# ---------------------------------------------------------------------------


def _parse_authorization(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Parse and validate the full stage authorization payload."""
    runtime.validate_authorization_shape(payload)
    runtime.verify_authorization_digest(payload)
    return dict(payload)


def _parse_id_digest(
    payload: Mapping[str, Any],
    *,
    authorized_keys: frozenset[str],
    operation: str,
) -> tuple[str, str]:
    """Parse ``authorization_id`` + ``authorization_digest`` and reject extras."""
    extras = set(payload.keys()) - authorized_keys
    if extras:
        raise ValueError(
            f"{operation} input must contain exactly authorization_id "
            f"and authorization_digest; extras={sorted(extras)}"
        )
    if "authorization_id" not in payload or "authorization_digest" not in payload:
        raise ValueError(
            f"{operation} input must contain authorization_id and authorization_digest"
        )
    auth_id = payload.get("authorization_id")
    auth_digest = payload.get("authorization_digest")
    if not isinstance(auth_id, str) or not auth_id:
        raise ValueError("authorization_id missing")
    if (
        not isinstance(auth_digest, str)
        or len(auth_digest) != 64
        or not all(c in "0123456789abcdefABCDEF" for c in auth_digest)
    ):
        raise ValueError("authorization_digest missing or not a SHA-256 hex")
    return auth_id, auth_digest


def _canonical_repository_identity(
    authorization: Mapping[str, Any],
    worktree: str,
    *,
    git_runner: GitRunner | None = None,
) -> str:
    """Derive the canonical repository identity from the configured remote."""
    remote = str(authorization["authorized_remote"])
    expected = str(authorization["authorized_remote_repository"])
    identity = runtime.verify_remote_push_destination(
        worktree, remote, expected, runner=git_runner
    )
    return identity.as_string()


# ---------------------------------------------------------------------------
# Operation: stage
# ---------------------------------------------------------------------------


def stage_op(
    worktree: str,
    payload: Mapping[str, Any],
    *,
    store: ledger_mod.LedgerStore,
    git_runner: GitRunner | None = None,
) -> tuple[runtime.Receipt, int]:
    """Execute the ``stage`` operation end-to-end.

    The stage operation requires the complete authorization object. The
    full transaction boundary is:

    1. Validate the authorization shape + digest (PURE).
    2. PURELY parse the EXPECTED canonical repository identity from
       ``authorized_remote_repository`` (no Git observation).
    3. Acquire the authorization-level id+digest lock.
    4. Establish no existing valid same-id+digest ledger already exists.
    5. Acquire the per-repository transaction lock.
    6. Verify Git remote push destination against the expected identity.
    7. Verify current branch and HEAD.
    8. Capture worktree status and verify pre-state.
    9. Create the S1 ledger.
    10. Persist MUTATION_IN_PROGRESS with intent STAGE.
    11. ``git add -- <authorized paths>``.
    12. Verify cached path / status / whitespace / blob.
    13. Persist S4_STAGED.
    14. Release both locks.

    No Git observation may occur before BOTH locks are held.
    """
    try:
        authorization = _parse_authorization(payload)
    except (runtime.NudgeLandAuthorizationError, ValueError) as exc:
        receipt = _hard_stop_receipt(
            payload,
            operation=OPERATION_STAGE,
            entry_state=runtime.STEP_S0_NOT_STARTED,
            attempted_transition=f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}",
            reason=HARD_STOP_BAD_DIGEST,
            notes=str(exc),
        )
        return receipt, 2

    auth_id = authorization["authorization_id"]
    auth_digest = authorization["authorization_digest"]

    # PURE parse of expected canonical identity. No Git observation.
    try:
        expected_identity = runtime.canonical_identity_for_remote_repository(
            authorization["authorized_remote_repository"]
        )
    except runtime.NudgeLandRemoteError as exc:
        receipt = _hard_stop_receipt(
            authorization,
            operation=OPERATION_STAGE,
            entry_state=runtime.STEP_S0_NOT_STARTED,
            attempted_transition=f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}",
            reason=HARD_STOP_BAD_REMOTE,
            notes=str(exc),
        )
        return receipt, 3

    canonical_identity = expected_identity.as_string()

    # Acquire the authorization-level lock. No Git observation until
    # both required safety boundaries have been acquired.
    auth_lock_stack = contextlib.ExitStack()
    try:
        auth_lock_stack.enter_context(
            store._acquire_auth_lock(auth_id, auth_digest)
        )
    except ledger_mod.LedgerLockedError as exc:
        receipt = _hard_stop_receipt(
            authorization,
            operation=OPERATION_STAGE,
            entry_state=runtime.STEP_S0_NOT_STARTED,
            attempted_transition=f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}",
            reason=HARD_STOP_LEDGER_LOCKED,
            notes=str(exc),
            repository_identity=canonical_identity,
        )
        return receipt, 20

    with auth_lock_stack:
        # Establish that no existing valid same-id+digest authorization
        # already exists. While the authorization-level lock is held,
        # the scan observes a stable state.
        try:
            store.find_by_id_digest(auth_id, auth_digest)
        except ledger_mod.LedgerMissingError:
            # No existing valid ledger — proceed.
            pass
        except ledger_mod.LedgerError as exc:
            receipt = _hard_stop_receipt(
                authorization,
                operation=OPERATION_STAGE,
                entry_state=runtime.STEP_S0_NOT_STARTED,
                attempted_transition=f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}",
                reason=_ledger_reason(exc),
                notes=str(exc),
                repository_identity=canonical_identity,
            )
            return receipt, 21
        else:
            receipt = _hard_stop_receipt(
                authorization,
                operation=OPERATION_STAGE,
                entry_state=runtime.STEP_S0_NOT_STARTED,
                attempted_transition=f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}",
                reason=HARD_STOP_LEDGER_ERROR,
                notes=(
                    f"existing same-id+digest ledger already exists "
                    f"for {auth_id!r}"
                ),
                repository_identity=canonical_identity,
            )
            return receipt, 21

        # Acquire the per-repository transaction lock while the
        # authorization-level lock remains held.
        try:
            with store.transaction(canonical_identity, auth_id) as tx:
                # Now Git observation may begin.

                try:
                    runtime.verify_remote_push_destination(
                        worktree,
                        authorization["authorized_remote"],
                        authorization["authorized_remote_repository"],
                        runner=git_runner,
                    )
                except (
                    runtime.NudgeLandRemoteError,
                    runtime.NudgeLandSubprocessError,
                ) as exc:
                    receipt = _hard_stop_receipt(
                        authorization,
                        operation=OPERATION_STAGE,
                        entry_state=runtime.STEP_S0_NOT_STARTED,
                        attempted_transition=(
                            f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                        ),
                        reason=HARD_STOP_BAD_REMOTE,
                        notes=str(exc),
                        repository_identity=canonical_identity,
                    )
                    return receipt, 3

                try:
                    current_head = runtime.capture_head_sha(
                        worktree, runner=git_runner
                    )
                    current_branch = _current_branch(
                        worktree, runner=git_runner
                    )
                except runtime.NudgeLandSubprocessError as exc:
                    receipt = _hard_stop_receipt(
                        authorization,
                        operation=OPERATION_STAGE,
                        entry_state=runtime.STEP_S0_NOT_STARTED,
                        attempted_transition=(
                            f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                        ),
                        reason=HARD_STOP_BRANCH_MISMATCH,
                        notes=str(exc),
                        repository_identity=canonical_identity,
                    )
                    return receipt, 4

                if current_branch != authorization["authorized_branch"]:
                    receipt = _hard_stop_receipt(
                        authorization,
                        operation=OPERATION_STAGE,
                        entry_state=runtime.STEP_S0_NOT_STARTED,
                        attempted_transition=(
                            f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                        ),
                        reason=HARD_STOP_BRANCH_MISMATCH,
                        notes=(
                            f"branch mismatch: got {current_branch!r} "
                            f"expected {authorization['authorized_branch']!r}"
                        ),
                        repository_identity=canonical_identity,
                    )
                    return receipt, 5
                if current_head != authorization["authorized_base_head"]:
                    receipt = _hard_stop_receipt(
                        authorization,
                        operation=OPERATION_STAGE,
                        entry_state=runtime.STEP_S0_NOT_STARTED,
                        attempted_transition=(
                            f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                        ),
                        reason=HARD_STOP_BASE_HEAD_MISMATCH,
                        notes=(
                            f"base HEAD mismatch: got {current_head!r} "
                            f"expected {authorization['authorized_base_head']!r}"
                        ),
                        repository_identity=canonical_identity,
                    )
                    return receipt, 6

                try:
                    worktree_entries = runtime.capture_worktree_status(
                        worktree, runner=git_runner
                    )
                except runtime.NudgeLandStatusError as exc:
                    receipt = _hard_stop_receipt(
                        authorization,
                        operation=OPERATION_STAGE,
                        entry_state=runtime.STEP_S0_NOT_STARTED,
                        attempted_transition=(
                            f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                        ),
                        reason=HARD_STOP_UNSUPPORTED_STATUS,
                        notes=str(exc),
                        repository_identity=canonical_identity,
                    )
                    return receipt, 7
                except runtime.NudgeLandSubprocessError as exc:
                    receipt = _hard_stop_receipt(
                        authorization,
                        operation=OPERATION_STAGE,
                        entry_state=runtime.STEP_S0_NOT_STARTED,
                        attempted_transition=(
                            f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                        ),
                        reason=HARD_STOP_UNEXPECTED_DIRTY_PATH,
                        notes=str(exc),
                        repository_identity=canonical_identity,
                    )
                    return receipt, 7

                try:
                    _verify_pre_state(
                        authorization, worktree_entries, worktree, git_runner
                    )
                except _HardStop as stop:
                    return stop.receipt, stop.exit_code

                try:
                    entry = tx.create(
                        authorization_digest=auth_digest,
                        authorized_branch=authorization["authorized_branch"],
                        authorized_base_head=authorization["authorized_base_head"],
                        authorized_push_branch=authorization["authorized_push_branch"],
                        authorized_remote=authorization["authorized_remote"],
                        authorized_remote_repository=authorization[
                            "authorized_remote_repository"
                        ],
                        authorized_commit_subject=authorization[
                            "authorized_commit_subject"
                        ],
                        expected_remote_base_sha=authorization[
                            "expected_remote_base_sha"
                        ],
                        authorized_ci_workflow_or_check=authorization[
                            "authorized_ci_workflow_or_check"
                        ],
                        expected_ci_event=authorization["expected_ci_event"],
                        authorized_paths=list(authorization["authorized_paths"]),
                        authorized_file_fingerprints=dict(
                            authorization["authorized_file_fingerprints"]
                        ),
                        expected_initial_status=list(
                            authorization["expected_initial_status"]
                        ),
                    )
                except ledger_mod.LedgerError as exc:
                    receipt = _hard_stop_receipt(
                        authorization,
                        operation=OPERATION_STAGE,
                        entry_state=runtime.STEP_S0_NOT_STARTED,
                        attempted_transition=(
                            f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                        ),
                        reason=_ledger_reason(exc),
                        notes=str(exc),
                        repository_identity=canonical_identity,
                    )
                    return receipt, 8

                try:
                    tx.advance(
                        entry,
                        new_state=ledger_mod.LEDGER_STATE_MUTATION_IN_PROGRESS,
                        new_verified_state=runtime.STEP_S1_LEDGER_ACTIVE,
                        mutation_intent=ledger_mod.MUTATION_INTENT_STAGE,
                        mutation_in_progress_substate=(
                            runtime.MUTATION_IN_PROGRESS_SUBSTATE_STAGE
                        ),
                        notes="stage: persisting intent while verified_state remains S1",
                    )
                except ledger_mod.LedgerError as exc:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        exc,
                        OPERATION_STAGE,
                        canonical_identity,
                    )
                    return receipt, 9 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

                result = git_add_paths(
                    worktree,
                    list(authorization["authorized_paths"]),
                    runner=git_runner,
                )
                if result.returncode != 0:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        runtime.NudgeLandSubprocessError(
                            f"git add failed rc={result.returncode}: "
                            f"{result.stderr!r}"
                        ),
                        OPERATION_STAGE,
                        canonical_identity,
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_ATTEMPTED_COMPLETION_UNKNOWN
                        ),
                    )
                    return receipt, 10 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

                try:
                    cached_status_set = runtime.capture_index_status_set(
                        worktree, runner=git_runner
                    )
                except runtime.NudgeLandSubprocessError as exc:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        exc,
                        OPERATION_STAGE,
                        canonical_identity,
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                        ),
                    )
                    return receipt, 11 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
                except runtime.NudgeLandStatusError as exc:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        exc,
                        OPERATION_STAGE,
                        canonical_identity,
                        reason_override=HARD_STOP_CACHED_STATUS_SET_MISMATCH,
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                        ),
                    )
                    return receipt, 12 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

                expected_paths = tuple(sorted(authorization["authorized_paths"]))
                try:
                    cached_paths = runtime.capture_index_path_set(
                        worktree,
                        runner=git_runner,
                    )
                except (
                    runtime.NudgeLandSubprocessError,
                    runtime.NudgeLandStatusError,
                ) as exc:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        exc,
                        OPERATION_STAGE,
                        canonical_identity,
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                        ),
                    )
                    return receipt, 11 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
                if cached_paths != expected_paths:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        _stop_with_reason(
                            HARD_STOP_CACHED_PATH_SET_MISMATCH,
                            f"cached path set drift: got {cached_paths!r}",
                        ),
                        OPERATION_STAGE,
                        canonical_identity,
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                        ),
                    )
                    return receipt, 13 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
                expected_status_set = tuple(
                    sorted(
                        [
                            runtime.CachedIndexEntry(
                                runtime.STATUS_CODE_WORKTREE_MODIFIED
                                if record["status"] == runtime.STATUS_WORKTREE_MODIFIED
                                else runtime.STATUS_CODE_UNTRACKED_NEW,
                                runtime.canonical_path_string(record["path"]),
                            )
                            for record in authorization["expected_initial_status"]
                        ],
                        key=lambda entry: entry.path,
                    )
                )
                if cached_status_set != expected_status_set:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        _stop_with_reason(
                            HARD_STOP_CACHED_STATUS_SET_MISMATCH,
                            f"cached status set drift: got {cached_status_set!r}",
                        ),
                        OPERATION_STAGE,
                        canonical_identity,
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                        ),
                    )
                    return receipt, 13 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

                try:
                    ws_verdict = runtime.capture_index_whitespace_verdict(
                        worktree, runner=git_runner
                    )
                except runtime.NudgeLandSubprocessError as exc:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        exc,
                        OPERATION_STAGE,
                        canonical_identity,
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                        ),
                    )
                    return receipt, 14 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
                if ws_verdict.state == runtime.WHITESPACE_GIT_COMMAND_FAILURE:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        runtime.NudgeLandSubprocessError(
                            f"git diff --check failed rc={ws_verdict.returncode}: "
                            f"{ws_verdict.stderr!r}"
                        ),
                        OPERATION_STAGE,
                        canonical_identity,
                        reason_override=HARD_STOP_CACHED_WHITESPACE,
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                        ),
                    )
                    return receipt, 15 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
                if ws_verdict.state == runtime.WHITESPACE_FINDING:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        _stop_with_reason(
                            HARD_STOP_CACHED_WHITESPACE,
                            "cached whitespace finding",
                        ),
                        OPERATION_STAGE,
                        canonical_identity,
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                        ),
                    )
                    return receipt, 16 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

                for rel in expected_paths:
                    try:
                        sha = runtime.capture_index_blob_sha256(
                            worktree, rel, runner=git_runner
                        )
                    except (
                        runtime.NudgeLandSubprocessError,
                        runtime.NudgeLandStatusError,
                    ) as exc:
                        receipt, persisted = _consume_and_return(
                            tx,
                            entry,
                            exc,
                            OPERATION_STAGE,
                            canonical_identity,
                            reason_override=HARD_STOP_CACHED_BLOB_MISMATCH,
                            mutation_attempted=True,
                            mutation_result=(
                                runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                            ),
                        )
                        return receipt, 17 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
                    expected_sha = authorization["authorized_file_fingerprints"][rel]
                    if sha != expected_sha:
                        receipt, persisted = _consume_and_return(
                            tx,
                            entry,
                            _stop_with_reason(
                                HARD_STOP_CACHED_BLOB_MISMATCH,
                                f"cached blob mismatch for {rel!r}",
                            ),
                            OPERATION_STAGE,
                            canonical_identity,
                            mutation_attempted=True,
                            mutation_result=(
                                runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                            ),
                        )
                        return receipt, 17 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

                try:
                    tx.advance(
                        entry,
                        new_state=ledger_mod.LEDGER_STATE_ACTIVE,
                        new_verified_state=runtime.STEP_S4_STAGED,
                        mutation_intent=None,
                        mutation_in_progress_substate=None,
                        notes="stage complete: cached bytes match authorized fingerprints",
                    )
                except ledger_mod.LedgerError as exc:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        exc,
                        OPERATION_STAGE,
                        canonical_identity,
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                        ),
                    )
                    return receipt, 18 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
        except ledger_mod.LedgerLockedError as exc:
            receipt = _hard_stop_receipt(
                authorization,
                operation=OPERATION_STAGE,
                entry_state=runtime.STEP_S0_NOT_STARTED,
                attempted_transition=(
                    f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                ),
                reason=HARD_STOP_LEDGER_LOCKED,
                notes=str(exc),
                repository_identity=canonical_identity,
            )
            return receipt, 19

    receipt = runtime.build_receipt(
        authorization_id=auth_id,
        authorization_digest=auth_digest,
        repository_identity=canonical_identity,
        operation=OPERATION_STAGE,
        entry_state=runtime.STEP_S0_NOT_STARTED,
        attempted_transition=f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}",
        mutation_attempted=True,
        mutation_result=runtime.MUTATION_EXECUTED,
        last_verified_state=runtime.STEP_S4_STAGED,
        result_state=runtime.STEP_S4_STAGED,
        authorization_state=ledger_mod.LEDGER_STATE_ACTIVE,
        direct_observations=(
            "current_branch_match",
            "current_head_match",
            "worktree_status_match",
            "fingerprint_match",
            "cached_path_set_match",
            "cached_status_set_match",
            "cached_whitespace_ok",
            "cached_blob_match",
        ),
    )
    return receipt, 0


_CONSUMED_PERSISTENCE_FAILED_EXIT = 80


def _verify_pre_state(
    authorization: Mapping[str, Any],
    worktree_entries: Sequence[runtime.WorktreeStatusEntry],
    worktree: str,
    git_runner: GitRunner | None,
) -> None:
    """Verify the pre-state matches ``expected_initial_status`` and fingerprints."""
    expected_by_path: dict[str, str] = {}
    try:
        for record in authorization["expected_initial_status"]:
            canonical = runtime.canonical_path_string(record["path"])
            expected_by_path[canonical] = record["status"]
    except runtime.NudgeLandPathError as exc:
        raise _HardStop(
            HARD_STOP_PATH_NOT_FOUND,
            str(exc),
            _hard_stop_receipt(
                authorization,
                operation=OPERATION_STAGE,
                entry_state=runtime.STEP_S0_NOT_STARTED,
                attempted_transition=(
                    f"{runtime.STEP_S0_NOT_STARTED} -> "
                    f"{runtime.STEP_S4_STAGED}"
                ),
                reason=HARD_STOP_PATH_NOT_FOUND,
                notes=str(exc),
            ),
            19,
        ) from exc
    seen_paths: set[str] = set()
    for entry in worktree_entries:
        try:
            canonical = runtime.canonical_path_string(entry.path)
        except runtime.NudgeLandPathError as exc:
            raise _HardStop(
                HARD_STOP_PATH_NOT_FOUND,
                str(exc),
                _hard_stop_receipt(
                    authorization,
                    operation=OPERATION_STAGE,
                    entry_state=runtime.STEP_S0_NOT_STARTED,
                    attempted_transition=(
                        f"{runtime.STEP_S0_NOT_STARTED} -> "
                        f"{runtime.STEP_S4_STAGED}"
                    ),
                    reason=HARD_STOP_PATH_NOT_FOUND,
                    notes=str(exc),
                ),
                19,
            ) from exc
        if canonical in seen_paths:
            raise _HardStop(
                HARD_STOP_UNEXPECTED_DIRTY_PATH,
                f"duplicate worktree path: {entry.path!r}",
                _hard_stop_receipt(
                    authorization,
                    operation=OPERATION_STAGE,
                    entry_state=runtime.STEP_S0_NOT_STARTED,
                    attempted_transition=(
                        f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                    ),
                    reason=HARD_STOP_UNEXPECTED_DIRTY_PATH,
                    notes=f"duplicate worktree path: {entry.path!r}",
                ),
                16,
            )
        seen_paths.add(canonical)
        if canonical not in expected_by_path:
            raise _HardStop(
                HARD_STOP_UNEXPECTED_DIRTY_PATH,
                f"unexpected dirty path: {entry.path!r}",
                _hard_stop_receipt(
                    authorization,
                    operation=OPERATION_STAGE,
                    entry_state=runtime.STEP_S0_NOT_STARTED,
                    attempted_transition=(
                        f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                    ),
                    reason=HARD_STOP_UNEXPECTED_DIRTY_PATH,
                    notes=f"unexpected dirty path: {entry.path!r}",
                ),
                17,
            )
        if entry.status != expected_by_path[canonical]:
            raise _HardStop(
                HARD_STOP_UNSUPPORTED_STATUS,
                f"status mismatch for {entry.path!r}: got {entry.status!r}",
                _hard_stop_receipt(
                    authorization,
                    operation=OPERATION_STAGE,
                    entry_state=runtime.STEP_S0_NOT_STARTED,
                    attempted_transition=(
                        f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                    ),
                    reason=HARD_STOP_UNSUPPORTED_STATUS,
                    notes=(
                        f"status mismatch for {entry.path!r}: got {entry.status!r}"
                    ),
                ),
                18,
            )
        expected_sha = authorization["authorized_file_fingerprints"][canonical]
        try:
            actual_sha = runtime.compute_file_sha256(
                canonical, worktree, runner=None
            )
        except runtime.NudgeLandPathError as exc:
            raise _HardStop(
                HARD_STOP_PATH_NOT_FOUND,
                str(exc),
                _hard_stop_receipt(
                    authorization,
                    operation=OPERATION_STAGE,
                    entry_state=runtime.STEP_S0_NOT_STARTED,
                    attempted_transition=(
                        f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                    ),
                    reason=HARD_STOP_PATH_NOT_FOUND,
                    notes=str(exc),
                ),
                19,
            ) from exc
        if actual_sha != expected_sha:
            raise _HardStop(
                HARD_STOP_FINGERPRINT_MISMATCH,
                f"fingerprint mismatch for {entry.path!r}",
                _hard_stop_receipt(
                    authorization,
                    operation=OPERATION_STAGE,
                    entry_state=runtime.STEP_S0_NOT_STARTED,
                    attempted_transition=(
                        f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                    ),
                    reason=HARD_STOP_FINGERPRINT_MISMATCH,
                    notes=f"fingerprint mismatch for {entry.path!r}",
                ),
                20,
            )
    try:
        missing = (
            {
                runtime.canonical_path_string(p)
                for p in authorization["authorized_paths"]
            }
            - seen_paths
        )
    except runtime.NudgeLandPathError as exc:
        raise _HardStop(
            HARD_STOP_PATH_NOT_FOUND,
            str(exc),
            _hard_stop_receipt(
                authorization,
                operation=OPERATION_STAGE,
                entry_state=runtime.STEP_S0_NOT_STARTED,
                attempted_transition=(
                    f"{runtime.STEP_S0_NOT_STARTED} -> "
                    f"{runtime.STEP_S4_STAGED}"
                ),
                reason=HARD_STOP_PATH_NOT_FOUND,
                notes=str(exc),
            ),
            19,
        ) from exc
    if missing:
        missing_list = sorted(missing)
        raise _HardStop(
            HARD_STOP_PATH_NOT_FOUND,
            f"missing authorized paths: {missing_list}",
            _hard_stop_receipt(
                authorization,
                operation=OPERATION_STAGE,
                entry_state=runtime.STEP_S0_NOT_STARTED,
                attempted_transition=(
                    f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
                ),
                reason=HARD_STOP_PATH_NOT_FOUND,
                notes=f"missing authorized paths: {missing_list}",
            ),
            21,
        )


# ---------------------------------------------------------------------------
# Operation: commit
# ---------------------------------------------------------------------------


def commit_op(
    worktree: str,
    payload: Mapping[str, Any],
    *,
    store: ledger_mod.LedgerStore,
    git_runner: GitRunner | None = None,
) -> tuple[runtime.Receipt, int]:
    """Execute the ``commit`` operation end-to-end."""
    try:
        auth_id, auth_digest = _parse_id_digest(
            payload,
            authorized_keys=runtime.COMMIT_AUTHORIZED_KEYS,
            operation=OPERATION_COMMIT,
        )
    except ValueError as exc:
        receipt = _hard_stop_receipt(
            payload,
            operation=OPERATION_COMMIT,
            entry_state=runtime.STEP_S4_STAGED,
            attempted_transition=f"{runtime.STEP_S4_STAGED} -> {runtime.STEP_S6_COMMITTED}",
            reason=HARD_STOP_MISSING_FIELDS,
            notes=str(exc),
        )
        return receipt, 22

    identity = ""
    auth_lock_stack = contextlib.ExitStack()

    try:
        auth_lock_stack.enter_context(
            store._acquire_auth_lock(auth_id, auth_digest)
        )

        try:
            entry = _load_ledger(
                store,
                auth_id,
                auth_digest,
                OPERATION_COMMIT,
            )
        except _HardStop as stop:
            return stop.receipt, stop.exit_code

        identity = entry.repository_identity

        with store.transaction(identity, auth_id) as tx:
            try:
                entry = tx.load(auth_digest)
            except ledger_mod.LedgerError as exc:
                receipt = _hard_stop_receipt(
                    payload,
                    operation=OPERATION_COMMIT,
                    entry_state=runtime.STEP_S4_STAGED,
                    attempted_transition=(
                        f"{runtime.STEP_S4_STAGED} -> "
                        f"{runtime.STEP_S6_COMMITTED}"
                    ),
                    reason=_ledger_reason(exc),
                    notes=str(exc),
                    repository_identity=identity,
                )
                return receipt, 23

            canonical_identity = entry.repository_identity

            if entry.verified_state != runtime.STEP_S4_STAGED:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_REVVERIF_CACHED_FAILED,
                        f"unexpected verified state {entry.verified_state!r}",
                    ),
                    OPERATION_COMMIT,
                    canonical_identity,
                )
                return receipt, 24 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                cached_paths = runtime.capture_index_path_set(
                    worktree, runner=git_runner
                )
            except (
                runtime.NudgeLandSubprocessError,
                runtime.NudgeLandStatusError,
            ) as exc:
                receipt, persisted = _consume_and_return(
                    tx, entry, exc, OPERATION_COMMIT, canonical_identity
                )
                return receipt, 25 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
            expected_paths = tuple(sorted(entry.authorized_paths))
            if cached_paths != expected_paths:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_CACHED_PATH_SET_MISMATCH,
                        f"cached path set drift: got {cached_paths!r}",
                    ),
                    OPERATION_COMMIT,
                    canonical_identity,
                )
                return receipt, 26 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                cached_status_set = runtime.capture_index_status_set(
                    worktree, runner=git_runner
                )
            except (runtime.NudgeLandSubprocessError, runtime.NudgeLandStatusError) as exc:
                receipt, persisted = _consume_and_return(
                    tx, entry, exc, OPERATION_COMMIT, canonical_identity
                )
                return receipt, 27 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
            # G1/G2/G3: build the expected cached status set using the
            # canonical ``runtime.CachedIndexEntry`` so the comparison
            # is consistent with the observed
            # ``tuple[CachedIndexEntry, ...]`` returned by
            # ``capture_index_status_set``.
            expected_status_set = tuple(
                sorted(
                    [
                        runtime.CachedIndexEntry(
                            runtime.STATUS_CODE_WORKTREE_MODIFIED
                            if record["status"] == runtime.STATUS_WORKTREE_MODIFIED
                            else runtime.STATUS_CODE_UNTRACKED_NEW,
                            runtime.canonical_path_string(record["path"]),
                        )
                        for record in entry.expected_initial_status
                    ],
                    key=lambda entry_obj: entry_obj.path,
                )
            )
            if cached_status_set != expected_status_set:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_CACHED_STATUS_SET_MISMATCH,
                        f"cached status set drift: got {cached_status_set!r}",
                    ),
                    OPERATION_COMMIT,
                    canonical_identity,
                )
                return receipt, 28 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                ws_verdict = runtime.capture_index_whitespace_verdict(
                    worktree, runner=git_runner
                )
            except runtime.NudgeLandSubprocessError as exc:
                receipt, persisted = _consume_and_return(
                    tx, entry, exc, OPERATION_COMMIT, canonical_identity
                )
                return receipt, 29 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
            if ws_verdict.state != runtime.WHITESPACE_CLEAN:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_CACHED_WHITESPACE,
                        f"cached whitespace drift: {ws_verdict.state}",
                    ),
                    OPERATION_COMMIT,
                    canonical_identity,
                )
                return receipt, 30 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            for rel in expected_paths:
                try:
                    sha = runtime.capture_index_blob_sha256(
                        worktree, rel, runner=git_runner
                    )
                except runtime.NudgeLandSubprocessError as exc:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        exc,
                        OPERATION_COMMIT,
                        canonical_identity,
                    )
                    return receipt, 31 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
                expected_sha = entry.authorized_file_fingerprints[rel]
                if sha != expected_sha:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        _stop_with_reason(
                            HARD_STOP_CACHED_BLOB_MISMATCH,
                            f"cached blob drift for {rel!r}",
                        ),
                        OPERATION_COMMIT,
                        canonical_identity,
                    )
                    return receipt, 31 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            # Re-verify local HEAD has not drifted.
            try:
                current_head = runtime.capture_head_sha(
                    worktree, runner=git_runner
                )
            except runtime.NudgeLandSubprocessError as exc:
                receipt, persisted = _consume_and_return(
                    tx, entry, exc, OPERATION_COMMIT, canonical_identity
                )
                return receipt, 32 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
            if current_head != entry.authorized_base_head:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_BASE_HEAD_MISMATCH,
                        f"HEAD drift: got {current_head!r}",
                    ),
                    OPERATION_COMMIT,
                    canonical_identity,
                )
                return receipt, 33 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
            # H1: branch recheck is mandatory and must occur before the
            # commit intent is persisted. A branch drift between the
            # authorized state and the current worktree is a hard-stop.
            try:
                current_branch = _current_branch(worktree, runner=git_runner)
            except runtime.NudgeLandSubprocessError as exc:
                receipt, persisted = _consume_and_return(
                    tx, entry, exc, OPERATION_COMMIT, canonical_identity
                )
                return receipt, 34 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
            if current_branch != entry.authorized_branch:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_BRANCH_MISMATCH,
                        f"branch drift: got {current_branch!r}",
                    ),
                    OPERATION_COMMIT,
                    canonical_identity,
                )
                return receipt, 35 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                tx.advance(
                    entry,
                    new_state=ledger_mod.LEDGER_STATE_MUTATION_IN_PROGRESS,
                    new_verified_state=runtime.STEP_S4_STAGED,
                    mutation_intent=ledger_mod.MUTATION_INTENT_COMMIT,
                    mutation_in_progress_substate=runtime.MUTATION_IN_PROGRESS_SUBSTATE_COMMIT,
                    notes="commit: persisting intent while verified_state remains S4",
                )
            except ledger_mod.LedgerError as exc:
                receipt, persisted = _consume_and_return(
                    tx, entry, exc, OPERATION_COMMIT, canonical_identity
                )
                return receipt, 34 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            commit_result = git_commit(
                worktree, entry.authorized_commit_subject, runner=git_runner
            )
            if commit_result.returncode != 0:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    runtime.NudgeLandSubprocessError(
                        f"git commit failed rc={commit_result.returncode}: "
                        f"{commit_result.stderr!r}"
                    ),
                    OPERATION_COMMIT,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=runtime.MUTATION_ATTEMPTED_COMPLETION_UNKNOWN,
                )
                return receipt, 35 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                new_head = runtime.capture_head_sha(worktree, runner=git_runner)
                new_parent = runtime.capture_head_parent(
                    worktree, runner=git_runner
                )
                new_subject = runtime.capture_head_subject(
                    worktree, runner=git_runner
                )
                new_changed = runtime.capture_head_changed_paths(
                    worktree, runner=git_runner
                )
            except (
                runtime.NudgeLandSubprocessError,
                runtime.NudgeLandStatusError,
            ) as exc:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    exc,
                    OPERATION_COMMIT,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED,
                )
                return receipt, 36 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            if new_head == entry.authorized_base_head:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_BASE_HEAD_MISMATCH,
                        f"commit did not advance HEAD: got {new_head!r}",
                    ),
                    OPERATION_COMMIT,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=(
                        runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                    ),
                )
                return receipt, 37 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
            if new_parent != entry.authorized_base_head:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_BASE_HEAD_MISMATCH,
                        f"commit parent mismatch: got {new_parent!r} "
                        f"expected {entry.authorized_base_head!r}",
                    ),
                    OPERATION_COMMIT,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=(
                        runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                    ),
                )
                return receipt, 37 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
            if new_subject != entry.authorized_commit_subject:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_COMMIT_SUBJECT_MISMATCH,
                        f"commit subject drift: got {new_subject!r}",
                    ),
                    OPERATION_COMMIT,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED,
                )
                return receipt, 37 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                expected_changed = tuple(
                    (
                        runtime.STATUS_CODE_WORKTREE_MODIFIED
                        if record["status"] == runtime.STATUS_WORKTREE_MODIFIED
                        else runtime.STATUS_CODE_UNTRACKED_NEW,
                        runtime.canonical_path_string(record["path"]),
                    )
                    for record in sorted(
                        entry.expected_initial_status,
                        key=lambda r: runtime.canonical_path_string(r["path"]),
                    )
                )
            except runtime.NudgeLandPathError as exc:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    exc,
                    OPERATION_COMMIT,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=(
                        runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                    ),
                )
                return receipt, 38 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
            if new_changed != expected_changed:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_COMMIT_CHANGED_PATHS_MISMATCH,
                        f"commit changed paths drift: got {new_changed!r}",
                    ),
                    OPERATION_COMMIT,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED,
                )
                return receipt, 38 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            for rel in expected_paths:
                try:
                    sha = runtime.capture_head_blob_sha256(
                        worktree, rel, runner=git_runner
                    )
                except runtime.NudgeLandSubprocessError as exc:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        exc,
                        OPERATION_COMMIT,
                        canonical_identity,
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                        ),
                    )
                    return receipt, 39 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
                expected_sha = entry.authorized_file_fingerprints[rel]
                if sha != expected_sha:
                    receipt, persisted = _consume_and_return(
                        tx,
                        entry,
                        _stop_with_reason(
                            HARD_STOP_COMMIT_BLOB_MISMATCH,
                            f"commit blob drift for {rel!r}",
                        ),
                        OPERATION_COMMIT,
                        canonical_identity,
                        mutation_attempted=True,
                        mutation_result=runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED,
                    )
                    return receipt, 39 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                post_commit_clean = runtime.capture_worktree_is_clean(
                    worktree, runner=git_runner
                )
            except runtime.NudgeLandSubprocessError as exc:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    exc,
                    OPERATION_COMMIT,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=(
                        runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                    ),
                )
                return receipt, 40 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            if not post_commit_clean:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_POST_COMMIT_DIRTY,
                        "post-commit worktree is dirty",
                    ),
                    OPERATION_COMMIT,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED,
                )
                return receipt, 40 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                tx.advance(
                    entry,
                    new_state=ledger_mod.LEDGER_STATE_ACTIVE,
                    new_verified_state=runtime.STEP_S6_COMMITTED,
                    mutation_intent=None,
                    mutation_in_progress_substate=None,
                    notes="commit complete",
                    landing_commit_sha=new_head,
                )
            except ledger_mod.LedgerError as exc:
                if isinstance(
                    exc, ledger_mod.LedgerDurabilityError
                ) and getattr(exc, "kind", None) == (
                    ledger_mod.LEDGER_DURABILITY_POST_REPLACE
                ):
                    receipt = _hard_stop_receipt(
                        payload,
                        operation=OPERATION_COMMIT,
                        entry_state=runtime.STEP_S4_STAGED,
                        attempted_transition=(
                            f"{runtime.STEP_S4_STAGED} -> "
                            f"{runtime.STEP_S6_COMMITTED}"
                        ),
                        reason=HARD_STOP_DURABILITY_NOT_ESTABLISHED,
                        notes=str(exc),
                        repository_identity=canonical_identity,
                        authorization_state=(
                            ledger_mod.LEDGER_STATE_DURABILITY_NOT_ESTABLISHED
                        ),
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                        ),
                        last_verified_state=runtime.STEP_S6_COMMITTED,
                        result_state=runtime.STEP_S6_COMMITTED,
                    )
                    return receipt, 41
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    exc,
                    OPERATION_COMMIT,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=(
                        runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                    ),
                )
                return receipt, 41 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
    except ledger_mod.LedgerLockedError as exc:
        receipt = _hard_stop_receipt(
            {"authorization_id": auth_id, "authorization_digest": auth_digest},
            operation=OPERATION_COMMIT,
            entry_state=runtime.STEP_S4_STAGED,
            attempted_transition=f"{runtime.STEP_S4_STAGED} -> {runtime.STEP_S6_COMMITTED}",
            reason=HARD_STOP_LEDGER_LOCKED,
            notes=str(exc),
            repository_identity=identity,
        )
        return receipt, 42
    finally:
        auth_lock_stack.close()

    receipt = runtime.build_receipt(
        authorization_id=auth_id,
        authorization_digest=auth_digest,
        repository_identity=identity,
        operation=OPERATION_COMMIT,
        entry_state=runtime.STEP_S4_STAGED,
        attempted_transition=f"{runtime.STEP_S4_STAGED} -> {runtime.STEP_S6_COMMITTED}",
        mutation_attempted=True,
        mutation_result=runtime.MUTATION_EXECUTED,
        last_verified_state=runtime.STEP_S6_COMMITTED,
        result_state=runtime.STEP_S6_COMMITTED,
        authorization_state=ledger_mod.LEDGER_STATE_ACTIVE,
        direct_observations=(
            "ledger_state_S4",
            "cached_path_set_match",
            "cached_status_set_match",
            "cached_whitespace_ok",
            "cached_blob_match",
            "commit_subject_match",
            "commit_changed_paths_match",
            "commit_blob_match",
            "post_commit_clean",
            f"head_sha={new_head}",
            f"parent_sha={new_parent}",
        ),
    )
    return receipt, 0


# ---------------------------------------------------------------------------
# Operation: push
# ---------------------------------------------------------------------------


def push_op(
    worktree: str,
    payload: Mapping[str, Any],
    *,
    store: ledger_mod.LedgerStore,
    git_runner: GitRunner | None = None,
    ls_remote_runner: Callable[
        [Sequence[str], str], runtime.ProcessResult
    ] | None = None,
) -> tuple[runtime.Receipt, int]:
    """Execute the ``push`` operation end-to-end."""
    try:
        auth_id, auth_digest = _parse_id_digest(
            payload,
            authorized_keys=runtime.PUSH_AUTHORIZED_KEYS,
            operation=OPERATION_PUSH,
        )
    except ValueError as exc:
        receipt = _hard_stop_receipt(
            payload,
            operation=OPERATION_PUSH,
            entry_state=runtime.STEP_S6_COMMITTED,
            attempted_transition=f"{runtime.STEP_S6_COMMITTED} -> {runtime.STEP_S8_PUSHED}",
            reason=HARD_STOP_MISSING_FIELDS,
            notes=str(exc),
        )
        return receipt, 43

    identity = ""
    auth_lock_stack = contextlib.ExitStack()

    try:
        auth_lock_stack.enter_context(
            store._acquire_auth_lock(auth_id, auth_digest)
        )

        try:
            entry = _load_ledger(
                store,
                auth_id,
                auth_digest,
                OPERATION_PUSH,
            )
        except _HardStop as stop:
            return stop.receipt, stop.exit_code

        identity = entry.repository_identity

        with store.transaction(identity, auth_id) as tx:
            try:
                entry = tx.load(auth_digest)
            except ledger_mod.LedgerError as exc:
                receipt = _hard_stop_receipt(
                    payload,
                    operation=OPERATION_PUSH,
                    entry_state=runtime.STEP_S6_COMMITTED,
                    attempted_transition=(
                        f"{runtime.STEP_S6_COMMITTED} -> "
                        f"{runtime.STEP_S8_PUSHED}"
                    ),
                    reason=_ledger_reason(exc),
                    notes=str(exc),
                    repository_identity=identity,
                )
                return receipt, 44

            canonical_identity = entry.repository_identity

            if entry.verified_state != runtime.STEP_S6_COMMITTED:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_REVVERIF_CACHED_FAILED,
                        f"unexpected verified state {entry.verified_state!r}",
                    ),
                    OPERATION_PUSH,
                    canonical_identity,
                )
                return receipt, 45 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            if entry.landing_commit_sha is None:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_LOCAL_HEAD_DRIFT,
                        "missing persisted landing_commit_sha",
                    ),
                    OPERATION_PUSH,
                    canonical_identity,
                )
                return receipt, 46 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                runtime.verify_remote_push_destination(
                    worktree,
                    entry.authorized_remote,
                    entry.authorized_remote_repository,
                    runner=git_runner,
                )
            except (runtime.NudgeLandRemoteError, runtime.NudgeLandSubprocessError) as exc:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_REMOTE_DESTINATION_MISMATCH, str(exc)
                    ),
                    OPERATION_PUSH,
                    canonical_identity,
                )
                return receipt, 47 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                local_head = runtime.capture_head_sha(
                    worktree, runner=git_runner
                )
            except runtime.NudgeLandSubprocessError as exc:
                receipt, persisted = _consume_and_return(
                    tx, entry, exc, OPERATION_PUSH, canonical_identity
                )
                return receipt, 48 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
            if local_head != entry.landing_commit_sha:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_LOCAL_HEAD_DRIFT,
                        f"local HEAD drift: got {local_head!r}",
                    ),
                    OPERATION_PUSH,
                    canonical_identity,
                )
                return receipt, 49 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            runner = ls_remote_runner or (
                lambda argv, cwd: runtime.run_process(argv, cwd=cwd)
            )
            try:
                remote_sha = runtime.capture_remote_branch_sha_via_runner(
                    lambda: runtime.build_ls_remote_branch_argv(
                        entry.authorized_remote, entry.authorized_push_branch
                    ),
                    cwd=worktree,
                    runner=runner,
                    expected_branch=entry.authorized_push_branch,
                )
            except (runtime.NudgeLandSubprocessError, runtime.NudgeLandError) as exc:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(HARD_STOP_REMOTE_SHA_MISMATCH, str(exc)),
                    OPERATION_PUSH,
                    canonical_identity,
                )
                return receipt, 50 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            if remote_sha != entry.expected_remote_base_sha:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_REMOTE_SHA_MISMATCH,
                        f"remote SHA mismatch: got {remote_sha!r} "
                        f"expected {entry.expected_remote_base_sha!r}",
                    ),
                    OPERATION_PUSH,
                    canonical_identity,
                )
                return receipt, 51 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                tx.advance(
                    entry,
                    new_state=ledger_mod.LEDGER_STATE_MUTATION_IN_PROGRESS,
                    new_verified_state=runtime.STEP_S6_COMMITTED,
                    mutation_intent=ledger_mod.MUTATION_INTENT_PUSH,
                    mutation_in_progress_substate=runtime.MUTATION_IN_PROGRESS_SUBSTATE_PUSH,
                    notes="push: persisting intent while verified_state remains S6",
                )
            except ledger_mod.LedgerError as exc:
                receipt, persisted = _consume_and_return(
                    tx, entry, exc, OPERATION_PUSH, canonical_identity
                )
                return receipt, 52 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            push_result = git_push(
                worktree,
                entry.authorized_remote,
                entry.authorized_push_branch,
                runner=git_runner,
            )
            if push_result.returncode != 0:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    runtime.NudgeLandSubprocessError(
                        f"git push failed rc={push_result.returncode}: "
                        f"{push_result.stderr!r}"
                    ),
                    OPERATION_PUSH,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=runtime.MUTATION_ATTEMPTED_COMPLETION_UNKNOWN,
                )
                return receipt, 53 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                post_push_sha = runtime.capture_remote_branch_sha_via_runner(
                    lambda: runtime.build_ls_remote_branch_argv(
                        entry.authorized_remote, entry.authorized_push_branch
                    ),
                    cwd=worktree,
                    runner=runner,
                    expected_branch=entry.authorized_push_branch,
                )
            except (runtime.NudgeLandSubprocessError, runtime.NudgeLandError) as exc:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(HARD_STOP_PUSH_SHA_MISMATCH, str(exc)),
                    OPERATION_PUSH,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED,
                )
                return receipt, 54 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            if post_push_sha != entry.landing_commit_sha:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_PUSH_SHA_MISMATCH,
                        f"post-push SHA mismatch: got {post_push_sha!r} "
                        f"expected {entry.landing_commit_sha!r}",
                    ),
                    OPERATION_PUSH,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED,
                )
                return receipt, 55 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                tx.advance(
                    entry,
                    new_state=ledger_mod.LEDGER_STATE_ACTIVE,
                    new_verified_state=runtime.STEP_S8_PUSHED,
                    mutation_intent=None,
                    mutation_in_progress_substate=None,
                    notes="push complete",
                )
            except ledger_mod.LedgerError as exc:
                if isinstance(
                    exc, ledger_mod.LedgerDurabilityError
                ) and getattr(exc, "kind", None) == (
                    ledger_mod.LEDGER_DURABILITY_POST_REPLACE
                ):
                    receipt = _hard_stop_receipt(
                        payload,
                        operation=OPERATION_PUSH,
                        entry_state=runtime.STEP_S6_COMMITTED,
                        attempted_transition=(
                            f"{runtime.STEP_S6_COMMITTED} -> "
                            f"{runtime.STEP_S8_PUSHED}"
                        ),
                        reason=HARD_STOP_DURABILITY_NOT_ESTABLISHED,
                        notes=str(exc),
                        repository_identity=canonical_identity,
                        authorization_state=(
                            ledger_mod.LEDGER_STATE_DURABILITY_NOT_ESTABLISHED
                        ),
                        mutation_attempted=True,
                        mutation_result=(
                            runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                        ),
                        last_verified_state=runtime.STEP_S8_PUSHED,
                        result_state=runtime.STEP_S8_PUSHED,
                    )
                    return receipt, 56
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    exc,
                    OPERATION_PUSH,
                    canonical_identity,
                    mutation_attempted=True,
                    mutation_result=(
                        runtime.MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED
                    ),
                )
                return receipt, 56 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
    except ledger_mod.LedgerLockedError as exc:
        receipt = _hard_stop_receipt(
            {"authorization_id": auth_id, "authorization_digest": auth_digest},
            operation=OPERATION_PUSH,
            entry_state=runtime.STEP_S6_COMMITTED,
            attempted_transition=f"{runtime.STEP_S6_COMMITTED} -> {runtime.STEP_S8_PUSHED}",
            reason=HARD_STOP_LEDGER_LOCKED,
            notes=str(exc),
            repository_identity=identity,
        )
        return receipt, 57
    finally:
        auth_lock_stack.close()

    receipt = runtime.build_receipt(
        authorization_id=auth_id,
        authorization_digest=auth_digest,
        repository_identity=identity,
        operation=OPERATION_PUSH,
        entry_state=runtime.STEP_S6_COMMITTED,
        attempted_transition=f"{runtime.STEP_S6_COMMITTED} -> {runtime.STEP_S8_PUSHED}",
        mutation_attempted=True,
        mutation_result=runtime.MUTATION_EXECUTED,
        last_verified_state=runtime.STEP_S8_PUSHED,
        result_state=runtime.STEP_S8_PUSHED,
        authorization_state=ledger_mod.LEDGER_STATE_ACTIVE,
        direct_observations=(
            "ledger_state_S6",
            "remote_destination_match",
            "expected_remote_base_sha_match",
            "local_head_matches_landing_sha",
            "push_command_executed",
            f"local_head_sha={local_head}",
            f"post_push_sha={post_push_sha}",
        ),
    )
    return receipt, 0


# ---------------------------------------------------------------------------
# Operation: verify_ci
# ---------------------------------------------------------------------------


def verify_ci_op(
    worktree: str,
    payload: Mapping[str, Any],
    *,
    store: ledger_mod.LedgerStore,
    timeout_seconds: float = DEFAULT_VERIFY_CI_TIMEOUT_SECONDS,
    interval_seconds: float = DEFAULT_VERIFY_CI_INTERVAL_SECONDS,
    responses: Sequence[dict[str, Any]] | None = None,
    response_queue: runtime._MockResponseQueue | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    clock_fn: Callable[[], float] = time.monotonic,
) -> tuple[runtime.Receipt, int]:
    """Execute the ``verify_ci`` operation end-to-end."""
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if interval_seconds < 0:
        raise ValueError("interval_seconds must be non-negative")

    try:
        auth_id, auth_digest = _parse_id_digest(
            payload,
            authorized_keys=runtime.VERIFY_CI_AUTHORIZED_KEYS,
            operation=OPERATION_VERIFY_CI,
        )
    except ValueError as exc:
        receipt = _hard_stop_receipt(
            payload,
            operation=OPERATION_VERIFY_CI,
            entry_state=runtime.STEP_S8_PUSHED,
            attempted_transition=f"{runtime.STEP_S8_PUSHED} -> {runtime.STEP_S10_LANDED}",
            reason=HARD_STOP_MISSING_FIELDS,
            notes=str(exc),
        )
        return receipt, 58

    identity = ""
    auth_lock_stack = contextlib.ExitStack()

    try:
        auth_lock_stack.enter_context(
            store._acquire_auth_lock(auth_id, auth_digest)
        )

        try:
            entry = _load_ledger(
                store,
                auth_id,
                auth_digest,
                OPERATION_VERIFY_CI,
            )
        except _HardStop as stop:
            return stop.receipt, stop.exit_code

        identity = entry.repository_identity

        with store.transaction(identity, auth_id) as tx:
            try:
                entry = tx.load(auth_digest)
            except ledger_mod.LedgerError as exc:
                receipt = _hard_stop_receipt(
                    payload,
                    operation=OPERATION_VERIFY_CI,
                    entry_state=runtime.STEP_S8_PUSHED,
                    attempted_transition=(
                        f"{runtime.STEP_S8_PUSHED} -> "
                        f"{runtime.STEP_S10_LANDED}"
                    ),
                    reason=_ledger_reason(exc),
                    notes=str(exc),
                    repository_identity=identity,
                )
                return receipt, 59

            canonical_identity = entry.repository_identity

            if entry.verified_state != runtime.STEP_S8_PUSHED:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_REVVERIF_CACHED_FAILED,
                        f"unexpected verified state {entry.verified_state!r}",
                    ),
                    OPERATION_VERIFY_CI,
                    canonical_identity,
                )
                return receipt, 60 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            if entry.landing_commit_sha is None:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(
                        HARD_STOP_LOCAL_HEAD_DRIFT,
                        "missing persisted landing_commit_sha",
                    ),
                    OPERATION_VERIFY_CI,
                    canonical_identity,
                )
                return receipt, 61 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            try:
                tx.advance(
                    entry,
                    new_state=ledger_mod.LEDGER_STATE_MUTATION_IN_PROGRESS,
                    new_verified_state=runtime.STEP_S8_PUSHED,
                    mutation_intent=ledger_mod.MUTATION_INTENT_VERIFY_CI,
                    mutation_in_progress_substate=runtime.MUTATION_IN_PROGRESS_SUBSTATE_VERIFY_CI,
                    notes="verify_ci: persisting intent while verified_state remains S8",
                )
            except ledger_mod.LedgerError as exc:
                receipt, persisted = _consume_and_return(
                    tx, entry, exc, OPERATION_VERIFY_CI, canonical_identity
                )
                return receipt, 62 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            expected = runtime.CIQueryRequest(
                workflow=entry.authorized_ci_workflow_or_check,
                head_sha=entry.landing_commit_sha,
                branch=entry.authorized_branch,
                event=entry.expected_ci_event,
            )

            verdict = runtime.poll_ci(
                remote_repo=canonical_identity,
                head_sha=entry.landing_commit_sha,
                expected=expected,
                timeout_seconds=timeout_seconds,
                interval_seconds=interval_seconds,
                responses=responses,
                response_queue=response_queue,
                sleep_fn=sleep_fn,
                clock_fn=clock_fn,
            )

            if isinstance(verdict, runtime.CIResponse):
                try:
                    tx.advance(
                        entry,
                        new_state=ledger_mod.LEDGER_STATE_LANDED,
                        new_verified_state=runtime.STEP_S10_LANDED,
                        mutation_intent=None,
                        mutation_in_progress_substate=None,
                        notes="CI success; landed",
                        landing_commit_sha=entry.landing_commit_sha,
                    )
                except ledger_mod.LedgerError as exc:
                    if isinstance(
                        exc, ledger_mod.LedgerDurabilityError
                    ) and getattr(exc, "kind", None) == (
                        ledger_mod.LEDGER_DURABILITY_POST_REPLACE
                    ):
                        receipt = _hard_stop_receipt(
                            payload,
                            operation=OPERATION_VERIFY_CI,
                            entry_state=runtime.STEP_S8_PUSHED,
                            attempted_transition=(
                                f"{runtime.STEP_S8_PUSHED} -> "
                                f"{runtime.STEP_S10_LANDED}"
                            ),
                            reason=HARD_STOP_DURABILITY_NOT_ESTABLISHED,
                            notes=str(exc),
                            repository_identity=canonical_identity,
                            authorization_state=(
                                ledger_mod.LEDGER_STATE_DURABILITY_NOT_ESTABLISHED
                            ),
                            mutation_attempted=False,
                            mutation_result=runtime.MUTATION_NOT_ATTEMPTED,
                            last_verified_state=runtime.STEP_S10_LANDED,
                            result_state=runtime.STEP_S10_LANDED,
                        )
                        return receipt, 63
                    receipt, persisted = _consume_and_return(
                        tx, entry, exc, OPERATION_VERIFY_CI, canonical_identity
                    )
                    return receipt, 63 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
                receipt = runtime.build_receipt(
                    authorization_id=auth_id,
                    authorization_digest=auth_digest,
                    repository_identity=canonical_identity,
                    operation=OPERATION_VERIFY_CI,
                    entry_state=runtime.STEP_S8_PUSHED,
                    attempted_transition=(
                        f"{runtime.STEP_S8_PUSHED} -> {runtime.STEP_S10_LANDED}"
                    ),
                    mutation_attempted=False,
                    mutation_result=runtime.MUTATION_NOT_ATTEMPTED,
                    last_verified_state=runtime.STEP_S10_LANDED,
                    result_state=runtime.STEP_S10_LANDED,
                    authorization_state=ledger_mod.LEDGER_STATE_LANDED,
                    direct_observations=(
                        "ledger_state_S8",
                        "ci_workflow_match",
                        "ci_head_sha_match",
                        "ci_branch_match",
                        "ci_event_match",
                        "ci_conclusion_success",
                    ),
                )
                return receipt, 0

            if verdict == runtime.CI_RESULT_NOT_ESTABLISHED_WITHIN_AUTHORIZED_TIMEOUT:
                receipt, persisted = _consume_and_return(
                    tx,
                    entry,
                    _stop_with_reason(HARD_STOP_CI_TIMEOUT, "ci poll timed out"),
                    OPERATION_VERIFY_CI,
                    canonical_identity,
                )
                return receipt, 64 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT

            receipt, persisted = _consume_and_return(
                tx,
                entry,
                _stop_with_reason(
                    HARD_STOP_CI_REJECTED, f"CI rejected: {verdict}"
                ),
                OPERATION_VERIFY_CI,
                canonical_identity,
            )
            return receipt, 65 if persisted else _CONSUMED_PERSISTENCE_FAILED_EXIT
    except ledger_mod.LedgerLockedError as exc:
        receipt = _hard_stop_receipt(
            {"authorization_id": auth_id, "authorization_digest": auth_digest},
            operation=OPERATION_VERIFY_CI,
            entry_state=runtime.STEP_S8_PUSHED,
            attempted_transition=f"{runtime.STEP_S8_PUSHED} -> {runtime.STEP_S10_LANDED}",
            reason=HARD_STOP_LEDGER_LOCKED,
            notes=str(exc),
            repository_identity=identity,
        )
        return receipt, 66
    finally:
        auth_lock_stack.close()


# ---------------------------------------------------------------------------
# Dispatcher helpers
# ---------------------------------------------------------------------------


def _load_ledger(
    store: ledger_mod.LedgerStore,
    auth_id: str,
    auth_digest: str,
    operation: str,
) -> ledger_mod.LedgerEntry:
    """Load the unique ledger entry using only authorization_id + authorization_digest.

    The caller/model supplies ONLY those two keys. The repository
    identity comes exclusively from the persisted trusted transaction
    state. A deterministic fail-closed lookup produces one of:

    * zero matching transactions → ``_HardStop`` (HARD_STOP_LEDGER_MISSING);
    * more than one matching transaction → ``_HardStop``
      (HARD_STOP_LEDGER_AMBIGUOUS);
    * terminal ``LANDED``/``CONSUMED`` → ``_HardStop``
      (HARD_STOP_LEDGER_TERMINAL);
    * stale ``MUTATION_IN_PROGRESS`` → ``_HardStop``
      (HARD_STOP_LEDGER_STALE_MUTATION);
    * one match → returned after binding verification.
    """
    try:
        return store.find_by_id_digest(auth_id, auth_digest)
    except ledger_mod.LedgerError as exc:
        raise _ledger_lookup_hard_stop(exc, auth_id, auth_digest, operation) from exc


def _ledger_lookup_hard_stop(
    exc: ledger_mod.LedgerError,
    auth_id: str,
    auth_digest: str,
    operation: str,
) -> _HardStop:
    """Convert a ledger lookup error into a structured ``_HardStop``."""
    entry_state = _entry_state_for_operation(operation)
    reason = _ledger_reason(exc)
    if isinstance(exc, ledger_mod.LedgerMissingError):
        exit_code = 101
    elif isinstance(exc, ledger_mod.LedgerAmbiguousError):
        exit_code = 102
    elif isinstance(exc, ledger_mod.LedgerStaleMutationError):
        exit_code = 104
    elif isinstance(exc, ledger_mod.LedgerAuthorizationTerminalError):
        exit_code = 105
    else:
        exit_code = 103
    return _HardStop(
        reason,
        str(exc),
        _hard_stop_receipt(
            {
                "authorization_id": auth_id,
                "authorization_digest": auth_digest,
            },
            operation=operation,
            entry_state=entry_state,
            attempted_transition=_attempted_transition(operation, entry_state),
            reason=reason,
            notes=str(exc),
        ),
        exit_code,
    )


def _entry_state_for_operation(operation: str) -> str:
    """Return the entry step for ``operation``."""
    if operation == OPERATION_STAGE:
        return runtime.STEP_S0_NOT_STARTED
    if operation == OPERATION_COMMIT:
        return runtime.STEP_S4_STAGED
    if operation == OPERATION_PUSH:
        return runtime.STEP_S6_COMMITTED
    if operation == OPERATION_VERIFY_CI:
        return runtime.STEP_S8_PUSHED
    return runtime.STEP_S0_NOT_STARTED


def _current_branch(
    worktree: str,
    *,
    runner: GitRunner | None = None,
) -> str:
    """Return the current branch name from ``git symbolic-ref``."""
    argv = ["git", "symbolic-ref", "--short", "HEAD"]
    if runner is None:
        result = runtime.run_process(argv, cwd=worktree)
    else:
        result = runner(argv, worktree)
    if result.returncode != 0:
        raise runtime.NudgeLandSubprocessError(
            f"git symbolic-ref failed rc={result.returncode}: {result.stderr!r}"
        )
    return result.stdout.decode("utf-8").strip()


def _consume_and_return(
    tx: ledger_mod._Transaction,
    entry: ledger_mod.LedgerEntry,
    exc: BaseException,
    operation: str,
    repository_identity: str,
    *,
    reason_override: str | None = None,
    mutation_attempted: bool = False,
    mutation_result: str = runtime.MUTATION_NOT_ATTEMPTED,
) -> tuple[runtime.Receipt, bool]:
    """Consume the authorization and return a hard-stop receipt.

    Returns ``(receipt, persisted)``. ``persisted`` is ``False`` iff the
    attempt to persist ``CONSUMED`` failed.

    The defaults are the safest hard-stop defaults: a helper that has
    not yet observed a mutation must report ``MUTATION_NOT_ATTEMPTED``.
    Post-mutation callers must opt into a stronger provenance label
    explicitly.

    K5: when the persist attempt fails after ``os.replace`` but before
    the directory fsync (a POST_REPLACE durability failure), the
    receipt uses ``LEDGER_STATE_DURABILITY_NOT_ESTABLISHED`` and the
    ``HARD_STOP_DURABILITY_NOT_ESTABLISHED`` reason — it does NOT
    falsely report ACTIVE or CONSUMED as definitely durable. A
    PRE_REPLACE durability failure preserves the previous durable
    state and is reported as ``HARD_STOP_CONSUMED_PERSISTENCE_FAILED``.
    """
    notes = getattr(exc, "notes", None) or str(exc)
    reason = reason_override or getattr(exc, "reason", None) or _exception_reason(exc, operation)
    receipt_mutation_attempted = mutation_attempted
    receipt_mutation_result = mutation_result
    try:
        tx.advance(
            entry,
            new_state=ledger_mod.LEDGER_STATE_CONSUMED,
            new_verified_state=entry.verified_state,
            mutation_intent=None,
            mutation_in_progress_substate=None,
            notes=f"consumed by {operation} hard-stop: {notes}",
        )
        persisted = True
        authorization_state = ledger_mod.LEDGER_STATE_CONSUMED
        hard_stop_reason = reason
    except ledger_mod.LedgerDurabilityError as persist_exc:
        # Distinguish pre-replace vs post-replace durability failures.
        # K5: when the consume advance fails AFTER os.replace but
        # BEFORE the directory fsync, direct durability of the new
        # state is not established. The receipt MUST NOT falsely
        # report ACTIVE or CONSUMED as definitely durable.
        if getattr(persist_exc, "kind", None) == (
            ledger_mod.LEDGER_DURABILITY_POST_REPLACE
        ):
            persisted = False
            authorization_state = (
                ledger_mod.LEDGER_STATE_DURABILITY_NOT_ESTABLISHED
            )
            hard_stop_reason = HARD_STOP_DURABILITY_NOT_ESTABLISHED
            notes = (
                f"consumed-durability-uncertain: {persist_exc}; "
                f"original reason: {reason}; original notes: {notes}"
            )
        else:
            persisted = False
            authorization_state = entry.state
            hard_stop_reason = HARD_STOP_CONSUMED_PERSISTENCE_FAILED
            notes = (
                f"consumed-persistence failed: {persist_exc}; "
                f"original reason: {reason}; original notes: {notes}"
            )
    except ledger_mod.LedgerError as persist_exc:
        persisted = False
        authorization_state = entry.state
        hard_stop_reason = HARD_STOP_CONSUMED_PERSISTENCE_FAILED
        notes = (
            f"consumed-persistence failed: {persist_exc}; "
            f"original reason: {reason}; original notes: {notes}"
        )
    return (
        _hard_stop_receipt(
            {
                "authorization_id": entry.authorization_id,
                "authorization_digest": entry.authorization_digest,
            },
            operation=operation,
            entry_state=entry.verified_state,
            attempted_transition=_attempted_transition(
                operation, entry.verified_state
            ),
            reason=hard_stop_reason,
            notes=notes,
            repository_identity=repository_identity,
            authorization_state=authorization_state,
            mutation_attempted=receipt_mutation_attempted,
            mutation_result=receipt_mutation_result,
        ),
        persisted,
    )


def _attempted_transition(operation: str, current_step: str) -> str:
    if operation == OPERATION_STAGE:
        return f"{runtime.STEP_S0_NOT_STARTED} -> {runtime.STEP_S4_STAGED}"
    if operation == OPERATION_COMMIT:
        return f"{runtime.STEP_S4_STAGED} -> {runtime.STEP_S6_COMMITTED}"
    if operation == OPERATION_PUSH:
        return f"{runtime.STEP_S6_COMMITTED} -> {runtime.STEP_S8_PUSHED}"
    if operation == OPERATION_VERIFY_CI:
        return f"{runtime.STEP_S8_PUSHED} -> {runtime.STEP_S10_LANDED}"
    return f"{current_step} -> unknown"


def _ledger_reason(exc: BaseException) -> str:
    if isinstance(exc, ledger_mod.LedgerAuthorizationTerminalError):
        return HARD_STOP_LEDGER_TERMINAL
    if isinstance(exc, ledger_mod.LedgerStaleMutationError):
        return HARD_STOP_LEDGER_STALE_MUTATION
    if isinstance(exc, ledger_mod.LedgerMissingError):
        return HARD_STOP_LEDGER_MISSING
    if isinstance(exc, ledger_mod.LedgerAmbiguousError):
        return HARD_STOP_LEDGER_AMBIGUOUS
    if isinstance(exc, ledger_mod.LedgerLockedError):
        return HARD_STOP_LEDGER_LOCKED
    if isinstance(exc, ledger_mod.LedgerCorruptError):
        return HARD_STOP_LEDGER_CORRUPT
    return HARD_STOP_LEDGER_ERROR


def _exception_reason(
    exc: BaseException,
    operation: str | None = None,
) -> str:
    if isinstance(exc, ledger_mod.LedgerError):
        return _ledger_reason(exc)
    if isinstance(exc, runtime.NudgeLandSubprocessError):
        if operation == OPERATION_STAGE:
            return HARD_STOP_STAGE_FAILED
        if operation == OPERATION_COMMIT:
            return HARD_STOP_COMMIT_FAILED
        return HARD_STOP_PUSH_FAILED
    if isinstance(exc, runtime.NudgeLandPathError):
        return HARD_STOP_PATH_NOT_FOUND
    if isinstance(exc, runtime.NudgeLandRemoteError):
        return HARD_STOP_BAD_REMOTE
    if isinstance(exc, runtime.NudgeLandAuthorizationError):
        return HARD_STOP_BAD_DIGEST
    if isinstance(exc, runtime.NudgeLandStatusError):
        return HARD_STOP_UNSUPPORTED_STATUS
    return HARD_STOP_NO_AUTHORIZATION


class _HardStop(Exception):
    """Internal exception carrying a hard-stop receipt."""

    def __init__(
        self,
        reason: str,
        notes: str,
        receipt: runtime.Receipt,
        exit_code: int,
    ) -> None:
        super().__init__(notes)
        self.reason = reason
        self.notes = notes
        self.receipt = receipt
        self.exit_code = exit_code


def _stop(reason: str) -> _HardStop:
    return _HardStop(reason, reason, _placeholder_receipt(reason), 1)


def _stop_with_reason(reason: str, notes: str) -> _HardStop:
    return _HardStop(reason, notes, _placeholder_receipt(reason), 1)


def _placeholder_receipt(reason: str) -> runtime.Receipt:
    return runtime.build_receipt(
        authorization_id="",
        authorization_digest="",
        repository_identity="",
        operation="",
        entry_state=runtime.STEP_S0_NOT_STARTED,
        attempted_transition="",
        mutation_attempted=False,
        mutation_result=runtime.MUTATION_NOT_ATTEMPTED,
        last_verified_state=runtime.STEP_S0_NOT_STARTED,
        result_state=runtime.STEP_S0_NOT_STARTED,
        authorization_state="REJECTED",
        hard_stop_reason=reason,
    )


def _hard_stop_receipt(
    payload: Mapping[str, Any],
    *,
    operation: str,
    entry_state: str,
    attempted_transition: str,
    reason: str,
    notes: str,
    repository_identity: str = "",
    authorization_state: str = "REJECTED",
    mutation_attempted: bool = False,
    mutation_result: str = runtime.MUTATION_NOT_ATTEMPTED,
    last_verified_state: str | None = None,
    result_state: str | None = None,
) -> runtime.Receipt:
    """Build a hard-stop receipt with the directly retained verified state.

    J5: ``last_verified_state`` and ``result_state`` must reflect the
    directly retained verified state. Do NOT default ``result_state`` to
    ``S0_NOT_STARTED`` when ``S4_STAGED`` / ``S6_COMMITTED`` /
    ``S8_PUSHED`` is the retained directly verified state. When the
    caller does not supply ``result_state`` explicitly, fall through to
    ``last_verified_state`` then ``entry_state`` so a commit / push /
    verify_ci hard-stop carries the actual retained state rather than
    a fabricated S0.
    """
    resolved_last_verified = last_verified_state or entry_state
    return runtime.build_receipt(
        authorization_id=str(payload.get("authorization_id", "")),
        authorization_digest=str(payload.get("authorization_digest", "")),
        repository_identity=repository_identity,
        operation=operation,
        entry_state=entry_state,
        attempted_transition=attempted_transition,
        mutation_attempted=mutation_attempted,
        mutation_result=mutation_result,
        last_verified_state=resolved_last_verified,
        result_state=result_state or resolved_last_verified,
        authorization_state=authorization_state,
        hard_stop_reason=reason,
        direct_observations=(),
        unavailable_evidence=(),
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run_dispatch(
    *,
    argv: Sequence[str],
    stdin_payload: dict[str, Any] | None,
    store: ledger_mod.LedgerStore,
    git_runner: GitRunner | None = None,
    ls_remote_runner: Callable[
        [Sequence[str], str], runtime.ProcessResult
    ] | None = None,
    verify_ci_responses: Sequence[dict[str, Any]] | None = None,
    verify_ci_response_queue: runtime._MockResponseQueue | None = None,
    timeout_seconds: float = DEFAULT_VERIFY_CI_TIMEOUT_SECONDS,
    interval_seconds: float = DEFAULT_VERIFY_CI_INTERVAL_SECONDS,
    sleep_fn: Callable[[float], None] = time.sleep,
    clock_fn: Callable[[], float] = time.monotonic,
) -> tuple[runtime.Receipt, int]:
    """Dispatch to one operation and return ``(receipt, exit_code)``."""
    if not argv:
        receipt = _hard_stop_receipt(
            {},
            operation="unknown",
            entry_state=runtime.STEP_S0_NOT_STARTED,
            attempted_transition="unknown",
            reason=HARD_STOP_UNKNOWN_OPERATION,
            notes="no operation supplied",
        )
        return receipt, 64
    operation = str(argv[0])
    if operation not in SUPPORTED_OPERATIONS:
        receipt = _hard_stop_receipt(
            {},
            operation=operation,
            entry_state=runtime.STEP_S0_NOT_STARTED,
            attempted_transition="unknown",
            reason=HARD_STOP_UNKNOWN_OPERATION,
            notes=f"unknown operation: {operation!r}",
        )
        return receipt, 65

    if stdin_payload is None:
        receipt = _hard_stop_receipt(
            {},
            operation=operation,
            entry_state=runtime.STEP_S0_NOT_STARTED,
            attempted_transition="unknown",
            reason=HARD_STOP_MALFORMED_JSON,
            notes="stdin payload missing",
        )
        return receipt, 66

    worktree = resolve_worktree_path()

    if operation == OPERATION_STAGE:
        return stage_op(worktree, stdin_payload, store=store, git_runner=git_runner)
    if operation == OPERATION_COMMIT:
        return commit_op(
            worktree,
            stdin_payload,
            store=store,
            git_runner=git_runner,
        )
    if operation == OPERATION_PUSH:
        return push_op(
            worktree,
            stdin_payload,
            store=store,
            git_runner=git_runner,
            ls_remote_runner=ls_remote_runner,
        )
    if operation == OPERATION_VERIFY_CI:
        return verify_ci_op(
            worktree,
            stdin_payload,
            store=store,
            timeout_seconds=timeout_seconds,
            interval_seconds=interval_seconds,
            responses=verify_ci_responses,
            response_queue=verify_ci_response_queue,
            sleep_fn=sleep_fn,
            clock_fn=clock_fn,
        )

    receipt = _hard_stop_receipt(
        {},
        operation=operation,
        entry_state=runtime.STEP_S0_NOT_STARTED,
        attempted_transition="unknown",
        reason=HARD_STOP_UNKNOWN_OPERATION,
        notes=f"unhandled operation: {operation!r}",
    )
    return receipt, 67


def main(argv: Sequence[str] | None = None) -> int:
    """Process entry point. Reads JSON from stdin and dispatches one operation.

    The CLI is invokable both as the ``__main__`` of
    ``scripts.nudge_land_cli`` and as the module entrypoint
    ``python3 -B -m scripts.nudge_land_cli``. The ``operation`` is
    accepted positionally but is intentionally NOT validated against
    ``SUPPORTED_OPERATIONS`` by argparse so that unknown operations
    reach the dispatcher and produce a structured JSON receipt.
    """
    argv_list = list(argv) if argv is not None else None
    parser = argparse.ArgumentParser(
        prog="nudge_land_cli",
        description="NudgeWhen nudge-land operation dispatcher.",
        add_help=True,
    )
    parser.add_argument(
        "operation",
        nargs="?",
        default="",
        help="One of stage, commit, push, or verify_ci.",
    )
    parser.add_argument(
        "--state-root",
        default=None,
        help="Override the persistent ledger state root.",
    )
    parser.add_argument(
        "--verify-ci-timeout",
        type=float,
        default=DEFAULT_VERIFY_CI_TIMEOUT_SECONDS,
    )
    parser.add_argument(
        "--verify-ci-interval",
        type=float,
        default=DEFAULT_VERIFY_CI_INTERVAL_SECONDS,
    )
    args = parser.parse_args(argv_list)

    try:
        stdin_payload = read_stdin_payload()
    except ValueError as exc:
        receipt = _hard_stop_receipt(
            {},
            operation=str(args.operation or "unknown"),
            entry_state=runtime.STEP_S0_NOT_STARTED,
            attempted_transition="unknown",
            reason=HARD_STOP_MALFORMED_JSON,
            notes=str(exc),
        )
        sys.stdout.write(json.dumps(receipt.to_dict(), sort_keys=True))
        sys.stdout.write("\n")
        sys.stdout.flush()
        return 70

    store = ledger_mod.LedgerStore(state_root=args.state_root)
    receipt, exit_code = run_dispatch(
        argv=[args.operation] if args.operation else [],
        stdin_payload=stdin_payload,
        store=store,
        timeout_seconds=args.verify_ci_timeout,
        interval_seconds=args.verify_ci_interval,
    )
    sys.stdout.write(json.dumps(receipt.to_dict(), sort_keys=True))
    sys.stdout.write("\n")
    sys.stdout.flush()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "DEFAULT_VERIFY_CI_INTERVAL_SECONDS",
    "DEFAULT_VERIFY_CI_TIMEOUT_SECONDS",
    "HARD_STOP_BAD_DIGEST",
    "HARD_STOP_BAD_REMOTE",
    "HARD_STOP_BASE_HEAD_MISMATCH",
    "HARD_STOP_BRANCH_MISMATCH",
    "HARD_STOP_CACHED_BLOB_MISMATCH",
    "HARD_STOP_CACHED_PATH_SET_MISMATCH",
    "HARD_STOP_CACHED_STATUS_SET_MISMATCH",
    "HARD_STOP_CACHED_WHITESPACE",
    "HARD_STOP_CI_REJECTED",
    "HARD_STOP_CI_TIMEOUT",
    "HARD_STOP_COMMIT_BLOB_MISMATCH",
    "HARD_STOP_COMMIT_CHANGED_PATHS_MISMATCH",
    "HARD_STOP_COMMIT_SUBJECT_MISMATCH",
    "HARD_STOP_CONSUMED_PERSISTENCE_FAILED",
    "HARD_STOP_DURABILITY_NOT_ESTABLISHED",
    "HARD_STOP_FINGERPRINT_MISMATCH",
    "HARD_STOP_LEDGER_AMBIGUOUS",
    "HARD_STOP_LEDGER_CORRUPT",
    "HARD_STOP_LEDGER_ERROR",
    "HARD_STOP_LEDGER_LOCKED",
    "HARD_STOP_LEDGER_MISSING",
    "HARD_STOP_LEDGER_STALE_MUTATION",
    "HARD_STOP_LEDGER_TERMINAL",
    "HARD_STOP_LOCAL_HEAD_DRIFT",
    "HARD_STOP_MALFORMED_JSON",
    "HARD_STOP_MISSING_FIELDS",
    "HARD_STOP_NO_AUTHORIZATION",
    "HARD_STOP_PATH_NOT_FOUND",
    "HARD_STOP_POST_COMMIT_DIRTY",
    "HARD_STOP_PUSH_FAILED",
    "HARD_STOP_PUSH_SHA_MISMATCH",
    "HARD_STOP_REMOTE_DESTINATION_MISMATCH",
    "HARD_STOP_REMOTE_SHA_MISMATCH",
    "HARD_STOP_REVVERIF_CACHED_FAILED",
    "HARD_STOP_UNEXPECTED_DIRTY_PATH",
    "HARD_STOP_UNKNOWN_OPERATION",
    "HARD_STOP_UNSUPPORTED_STATUS",
    "OPERATION_COMMIT",
    "OPERATION_PUSH",
    "OPERATION_STAGE",
    "OPERATION_VERIFY_CI",
    "SUPPORTED_OPERATIONS",
    "commit_op",
    "git_add_paths",
    "git_commit",
    "git_push",
    "main",
    "push_op",
    "read_stdin_payload",
    "resolve_worktree_path",
    "run_dispatch",
    "stage_op",
    "verify_ci_op",
]
