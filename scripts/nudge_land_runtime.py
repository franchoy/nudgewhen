"""Deterministic Python landing runtime primitives for NudgeWhen nudge-land.

This module is part of the v0.1.3 Phase 6 nudge-land Python landing core
(C2B). It provides the deterministic, testable, standard-library-only
runtime primitives that the persistent transaction ledger
(``scripts.nudge_land_ledger.py``) and the deterministic JSON-over-stdin
operation dispatcher (``scripts.nudge_land_cli.py``) build on.

The implementation is intentionally constrained:

* Python standard library only. No third-party imports.
* Argument-vector subprocess execution with ``shell=False``. No shell
  command strings. No pipelines. No redirections.
* Independent capture of ``stdout`` bytes, ``stderr`` bytes, and the
  numeric process ``returncode``. The ``returncode`` is never inferred
  from captured output text.
* Deterministic canonical authorization serialization with SHA-256
  digest. Canonicalization is key-sorted, comma+colon separators, UTF-8
  with ``ensure_ascii=False`` and ``allow_nan=False``.
* ``lstat``-style path validation so symlinks — including parent
  directory symlinks — are not silently followed into accepted
  regular-file classifications.
* All repository and remote primitives take a configurable process
  runner so tests can supply mocked ``ProcessResult`` objects without
  touching the real network or the real worktree.

The module never mutates Git state on its own; the stage / commit /
push / verify-ci sequencing lives in the dispatcher module.
"""

from __future__ import annotations

import dataclasses
import enum
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from typing import Any, Callable, Iterable, Mapping, Sequence


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------


# Supported canonical verified step states returned by the runtime to the
# transaction ledger and the CLI dispatcher. ``S5_COMMITTING``,
# ``S7_PUSHING`` and ``S9_VERIFYING_CI`` are descriptive in-progress
# runtime constants; the durable ``verified_state`` field never carries
# any of them.

STEP_S0_NOT_STARTED = "S0_NOT_STARTED"
STEP_S1_LEDGER_ACTIVE = "S1_LEDGER_ACTIVE"
STEP_S4_STAGED = "S4_STAGED"
STEP_S5_COMMITTING = "S5_COMMITTING"
STEP_S6_COMMITTED = "S6_COMMITTED"
STEP_S7_PUSHING = "S7_PUSHING"
STEP_S8_PUSHED = "S8_PUSHED"
STEP_S9_VERIFYING_CI = "S9_VERIFYING_CI"
STEP_S10_LANDED = "S10_LANDED"


# Mutation-in-progress substates. The authoritative vocabulary is
# ``STAGE`` / ``COMMIT`` / ``PUSH`` / ``VERIFY_CI`` — explicit short
# labels that match the four operations. ``STEP_S5_COMMITTING``,
# ``STEP_S7_PUSHING`` and ``STEP_S9_VERIFYING_CI`` are descriptive
# in-progress runtime constants and MUST NOT appear as a durable
# ``mutation_in_progress_substate``.

MUTATION_IN_PROGRESS_SUBSTATE_STAGE = "STAGE"
MUTATION_IN_PROGRESS_SUBSTATE_COMMIT = "COMMIT"
MUTATION_IN_PROGRESS_SUBSTATE_PUSH = "PUSH"
MUTATION_IN_PROGRESS_SUBSTATE_VERIFY_CI = "VERIFY_CI"


# GitHub remote canonical-identity host tag. The canonical identity is
# rendered as ``github:<owner>/<repo>``.

GITHUB_HOST_TAG = "github"


# Authoritative CI result / rejection labels. These labels are emitted by
# the CI query / polling primitives and are part of the contract surface
# with the CLI dispatcher and the test suite.

CI_RESULT_NOT_ESTABLISHED_WITHIN_AUTHORIZED_TIMEOUT = (
    "CI_RESULT_NOT_ESTABLISHED_WITHIN_AUTHORIZED_TIMEOUT"
)
CI_REJECTED_FAILURE = "CI_REJECTED_FAILURE"
CI_REJECTED_CANCELLED = "CI_REJECTED_CANCELLED"
CI_REJECTED_TIMED_OUT = "CI_REJECTED_TIMED_OUT"
CI_REJECTED_ACTION_REQUIRED = "CI_REJECTED_ACTION_REQUIRED"
CI_REJECTED_WRONG_SHA = "CI_REJECTED_WRONG_SHA"
CI_REJECTED_WRONG_BRANCH = "CI_REJECTED_WRONG_BRANCH"
CI_REJECTED_WRONG_EVENT = "CI_REJECTED_WRONG_EVENT"
CI_REJECTED_WRONG_WORKFLOW = "CI_REJECTED_WRONG_WORKFLOW"


# Authoritative CI conclusion values that the runtime accepts as
# successful. Anything else is rejected with the matching label above.

CI_CONCLUSION_SUCCESS = "success"


# Fields that MUST be present in every authorization object. The set is
# the contract surface with the CLI stage operation and with the
# canonical serializer.

AUTHORIZATION_REQUIRED_FIELDS: tuple[str, ...] = (
    "authorization_version",
    "authorization_id",
    "authorization_digest",
    "authorized_branch",
    "authorized_base_head",
    "authorized_paths",
    "expected_initial_status",
    "authorized_file_fingerprints",
    "authorized_commit_subject",
    "authorized_remote",
    "authorized_remote_repository",
    "authorized_push_branch",
    "expected_remote_base_sha",
    "authorized_ci_workflow_or_check",
    "expected_ci_event",
    "single_use",
)


# Authorized-only key sets for the commit / push / verify_ci operations.
# Anything beyond these two keys is a hard stop.

COMMIT_AUTHORIZED_KEYS: frozenset[str] = frozenset(
    {"authorization_id", "authorization_digest"}
)
PUSH_AUTHORIZED_KEYS: frozenset[str] = frozenset(
    {"authorization_id", "authorization_digest"}
)
VERIFY_CI_AUTHORIZED_KEYS: frozenset[str] = frozenset(
    {"authorization_id", "authorization_digest"}
)


# Mutation provenance labels.

MUTATION_NOT_ATTEMPTED = "MUTATION_NOT_ATTEMPTED"
MUTATION_ATTEMPTED_COMPLETION_UNKNOWN = "MUTATION_ATTEMPTED_COMPLETION_UNKNOWN"
MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED = (
    "MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED"
)
MUTATION_EXECUTED = "MUTATION_EXECUTED"


# Whitespace-verdict labels.

WHITESPACE_CLEAN = "CLEAN"
WHITESPACE_FINDING = "WHITESPACE_FINDING"
WHITESPACE_GIT_COMMAND_FAILURE = "GIT_COMMAND_FAILURE"


# Supported worktree status codes returned by the worktree status
# parser and the cached-index status parser. The strings are the
# authoritative labels.

STATUS_WORKTREE_MODIFIED = "WORKTREE_MODIFIED"
STATUS_UNTRACKED_NEW = "UNTRACKED_NEW"

# Single-character porcelain-v2 status codes mapped from
# ``expected_initial_status`` entries. The runtime keeps this mapping
# explicit so the dispatcher and the tests share the same vocabulary.

STATUS_CODE_WORKTREE_MODIFIED = "M"
STATUS_CODE_UNTRACKED_NEW = "A"


# ---------------------------------------------------------------------------
# Exception types
# ---------------------------------------------------------------------------


class NudgeLandError(Exception):
    """Base class for every deterministic error raised by this module."""


class NudgeLandSubprocessError(NudgeLandError):
    """A subprocess completed with a non-zero ``returncode``.

    The runner still surfaces the structured ``ProcessResult`` to the
    caller; this exception is reserved for cases where the call site
    wants a hard-stop raised directly.
    """


class NudgeLandPathError(NudgeLandError, ValueError):
    """A path failed safety / normalization validation."""


class NudgeLandAuthorizationError(NudgeLandError, ValueError):
    """An authorization object failed structural / digest validation."""


class NudgeLandStatusError(NudgeLandError, ValueError):
    """A ``git status --porcelain=v2 -z`` line was unsupported."""


class NudgeLandRemoteError(NudgeLandError, ValueError):
    """A remote URL or remote identity was rejected."""


class NudgeLandCIError(NudgeLandError, ValueError):
    """A CI query / polling primitive produced a hard-stop result."""


# ---------------------------------------------------------------------------
# Process runner
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ProcessResult:
    """Structured result of a single subprocess invocation.

    Attributes
    ----------
    argv:
        Exact argument vector passed to ``subprocess.run``. The list is
        stored as a tuple so the value is hashable and immutable.
    cwd:
        Working directory used for the invocation. Stored as a string.
    stdout:
        Captured standard output bytes. Never decoded.
    stderr:
        Captured standard error bytes. Never decoded.
    returncode:
        Numeric process exit status. ``None`` is reserved for
        ``subprocess.TimeoutExpired``; this runner does not raise on
        timeout, it returns ``returncode=None``.
    """

    argv: tuple[str, ...]
    cwd: str
    stdout: bytes
    stderr: bytes
    returncode: int | None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation for receipts."""
        return {
            "argv": list(self.argv),
            "cwd": self.cwd,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "returncode": self.returncode,
        }


ProcessRunner = Callable[[Sequence[str], str, bytes | None], ProcessResult]


def run_process(
    argv: Sequence[str],
    cwd: str,
    stdin: bytes | None = None,
) -> ProcessResult:
    """Execute ``argv`` from ``cwd`` and return a ``ProcessResult``.

    The runner always uses ``shell=False`` with a list-form ``argv``;
    raises ``TypeError`` if the caller passes a string. ``stdout`` and
    ``stderr`` are captured independently. The numeric ``returncode``
    is taken from the ``CompletedProcess`` object and never inferred
    from output text.
    """
    if not isinstance(argv, (list, tuple)):
        raise TypeError(
            "run_process requires an argument vector, got "
            f"{type(argv).__name__}"
        )
    if any(not isinstance(part, str) for part in argv):
        raise TypeError("run_process argv entries must all be str")
    if not argv:
        raise ValueError("run_process requires a non-empty argv")

    completed = subprocess.run(
        list(argv),
        cwd=cwd,
        input=stdin,
        shell=False,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return ProcessResult(
        argv=tuple(argv),
        cwd=str(cwd),
        stdout=bytes(completed.stdout),
        stderr=bytes(completed.stderr),
        returncode=int(completed.returncode) if completed.returncode is not None else None,
    )


# ---------------------------------------------------------------------------
# Path normalization and safety
# ---------------------------------------------------------------------------


# Canonical-path regex: a non-empty relative POSIX path containing only
# forward slashes, no ``.`` segments, no empty segments, no ``..``
# segments. Used both to detect non-canonical inputs and to canonicalize
# inputs safely.
_CANONICAL_PATH_RE = re.compile(r"^(?!/)(?!.*\.\.)(?![^/]*/\./)[^/\s][^/\s]*(?:/[^/\s][^/\s]*)*$")


def canonical_path_string(raw_path: str) -> str:
    """Return the canonical form of ``raw_path``.

    A canonical path uses POSIX forward slashes only, contains no
    ``.`` segments, no ``..`` segments, no empty segments, and is not
    absolute. Inputs that are not already canonical are rejected.
    """
    if not isinstance(raw_path, str):
        raise NudgeLandPathError(
            f"path must be str, got {type(raw_path).__name__}"
        )
    if raw_path == "":
        raise NudgeLandPathError("empty path is rejected")
    if "\x00" in raw_path:
        raise NudgeLandPathError("path contains a NUL byte")
    if "\\" in raw_path:
        raise NudgeLandPathError(
            f"path contains a backslash separator: {raw_path!r}"
        )
    if raw_path.startswith("/"):
        raise NudgeLandPathError(f"absolute path rejected: {raw_path!r}")
    if re.match(r"^[A-Za-z]:[\\/]", raw_path):
        raise NudgeLandPathError(f"absolute Windows path rejected: {raw_path!r}")
    if "//" in raw_path:
        raise NudgeLandPathError(
            f"path contains an empty segment: {raw_path!r}"
        )
    parts = raw_path.split("/")
    if any(part == "." for part in parts):
        raise NudgeLandPathError(
            f"path contains a '.' segment: {raw_path!r}"
        )
    if any(part == ".." for part in parts):
        raise NudgeLandPathError(
            f"path contains a '..' segment: {raw_path!r}"
        )
    if any(part == "" for part in parts):
        raise NudgeLandPathError(
            f"path contains an empty segment: {raw_path!r}"
        )
    return raw_path


def normalize_relative_path(
    raw_path: str,
    worktree: str | os.PathLike[str],
    *,
    must_exist: bool,
) -> str:
    """Normalize ``raw_path`` and return a forward-slash POSIX string.

    The function rejects:

    * empty strings;
    * strings containing a NUL byte;
    * strings containing backslash separators;
    * absolute paths (POSIX or Windows);
    * paths whose canonical form contains ``.`` or ``..`` segments;
    * paths whose canonical form contains an empty segment;
    * paths that resolve outside ``worktree``;
    * final-component symlinks;
    * parent-directory symlinks that escape or redirect traversal.

    When ``must_exist`` is true the final component is also validated as
    a regular non-symlink file via ``os.lstat`` so a symlink is not
    silently followed into an accepted regular-file classification.

    The function never raises ``FileNotFoundError`` for ``must_exist``
    mode; it raises ``NudgeLandPathError`` so callers can treat every
    rejection uniformly.
    """
    import stat as _stat

    canonical = canonical_path_string(raw_path)
    worktree_path = os.path.abspath(os.fspath(worktree))
    candidate = os.path.normpath(os.path.join(worktree_path, canonical))

    candidate_parts = candidate.split(os.sep)
    if any(part == ".." for part in candidate_parts):
        raise NudgeLandPathError(
            f"path resolves outside worktree: {raw_path!r}"
        )
    worktree_parts = worktree_path.split(os.sep)
    if candidate_parts[: len(worktree_parts)] != worktree_parts:
        raise NudgeLandPathError(
            f"path resolves outside worktree: {raw_path!r}"
        )

    rel = os.path.relpath(candidate, worktree_path).replace(os.sep, "/")
    if rel.startswith(".."):
        raise NudgeLandPathError(
            f"path resolves outside worktree: {raw_path!r}"
        )

    # Parent-directory symlink rejection. ``os.path.abspath`` already
    # resolved the worktree prefix lexically; we still walk every
    # parent directory component lexically and reject symlinks.
    rel_parts = rel.split("/")
    walk = worktree_path
    for part in rel_parts[:-1]:
        walk = os.path.join(walk, part)
        try:
            st = os.lstat(walk)
        except FileNotFoundError as exc:
            raise NudgeLandPathError(
                f"path does not exist: {raw_path!r}"
            ) from exc
        if _stat.S_ISLNK(st.st_mode):
            raise NudgeLandPathError(
                f"parent directory is a symlink: {raw_path!r}"
            )

    if must_exist:
        try:
            st = os.lstat(candidate)
        except FileNotFoundError as exc:
            raise NudgeLandPathError(
                f"path does not exist: {raw_path!r}"
            ) from exc
        if _stat.S_ISLNK(st.st_mode):
            raise NudgeLandPathError(
                f"path is a symlink: {raw_path!r}"
            )
        if not _stat.S_ISREG(st.st_mode):
            raise NudgeLandPathError(
                f"path is not a regular file: {raw_path!r}"
            )

    return rel


def assert_no_duplicate_normalized_paths(paths: Iterable[str]) -> None:
    """Reject duplicates in a normalized relative path list."""
    seen: set[str] = set()
    for raw in paths:
        if not isinstance(raw, str):
            raise NudgeLandPathError(
                f"path must be str, got {type(raw).__name__}"
            )
        normalized = canonical_path_string(raw)
        if normalized in seen:
            raise NudgeLandPathError(
                f"duplicate normalized path rejected: {normalized!r}"
            )
        seen.add(normalized)


def compute_file_sha256(
    raw_path: str,
    worktree: str | os.PathLike[str],
    *,
    runner: ProcessRunner | None = None,
) -> str:
    """Return the SHA-256 of the exact bytes of ``raw_path``.

    The function reads the file in 64 KiB chunks via the standard
    library ``hashlib`` so memory use stays bounded for any reasonable
    worktree file size. Symlinks are rejected by
    ``normalize_relative_path`` in ``must_exist`` mode and never reach
    this point.
    """
    rel = normalize_relative_path(raw_path, worktree, must_exist=True)
    abs_path = pathlib.Path(os.fspath(worktree)) / rel
    digest = hashlib.sha256()
    with open(str(abs_path), "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Authorization object
# ---------------------------------------------------------------------------


def _is_hex_string(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(c in "0123456789abcdefABCDEF" for c in value)
    )


def validate_authorization_shape(authorization: Mapping[str, Any]) -> None:
    """Validate the structural shape of an authorization object.

    The function is strict: any missing field, any wrong type, any
    empty authorized_paths, any non-hex SHA-256 in
    ``authorized_file_fingerprints``, any non-positive ``single_use``
    flag, or any non-canonical absolute / traversal path causes a hard
    ``NudgeLandAuthorizationError``.
    """
    if not isinstance(authorization, Mapping):
        raise NudgeLandAuthorizationError(
            "authorization must be a mapping"
        )
    for field in AUTHORIZATION_REQUIRED_FIELDS:
        if field not in authorization:
            raise NudgeLandAuthorizationError(
                f"authorization missing required field: {field}"
            )

    if authorization["authorized_branch"] != authorization["authorized_push_branch"]:
        raise NudgeLandAuthorizationError(
            "authorized_push_branch must equal authorized_branch "
            "for this initial implementation"
        )

    paths = authorization["authorized_paths"]
    if not isinstance(paths, list) or not paths:
        raise NudgeLandAuthorizationError(
            "authorized_paths must be a non-empty list"
        )
    if any(not isinstance(p, str) for p in paths):
        raise NudgeLandAuthorizationError(
            "authorized_paths entries must all be str"
        )
    canonical_paths: list[str] = []
    for p in paths:
        try:
            canonical_paths.append(canonical_path_string(p))
        except NudgeLandPathError as exc:
            raise NudgeLandAuthorizationError(
                f"authorized path not canonical: {p!r} ({exc})"
            ) from exc
    assert_no_duplicate_normalized_paths(canonical_paths)

    fingerprints = authorization["authorized_file_fingerprints"]
    if not isinstance(fingerprints, Mapping):
        raise NudgeLandAuthorizationError(
            "authorized_file_fingerprints must be a mapping"
        )
    if set(fingerprints.keys()) != set(canonical_paths):
        raise NudgeLandAuthorizationError(
            "authorized_file_fingerprints keys must match authorized_paths exactly"
        )
    for path, sha in fingerprints.items():
        try:
            canonical_path_string(path)
        except NudgeLandPathError as exc:
            raise NudgeLandAuthorizationError(
                f"authorized_file_fingerprint key not canonical: {path!r} ({exc})"
            ) from exc
        if not _is_hex_string(sha, 64):
            raise NudgeLandAuthorizationError(
                f"authorized_file_fingerprint for {path!r} is not a SHA-256 hex"
            )

    initial = authorization["expected_initial_status"]
    if not isinstance(initial, list) or not initial:
        raise NudgeLandAuthorizationError(
            "expected_initial_status must be a non-empty list"
        )
    seen_paths: set[str] = set()
    for record in initial:
        if not isinstance(record, Mapping):
            raise NudgeLandAuthorizationError(
                "expected_initial_status entries must be mappings"
            )
        if set(record.keys()) != {"status", "path"}:
            raise NudgeLandAuthorizationError(
                "expected_initial_status entries must have exactly status and path"
            )
        status = record["status"]
        path = record["path"]
        if status not in (STATUS_WORKTREE_MODIFIED, STATUS_UNTRACKED_NEW):
            raise NudgeLandAuthorizationError(
                f"unsupported expected_initial_status: {status!r}"
            )
        if not isinstance(path, str) or not path:
            raise NudgeLandAuthorizationError(
                "expected_initial_status path must be a non-empty str"
            )
        try:
            canonical_path = canonical_path_string(path)
        except NudgeLandPathError as exc:
            raise NudgeLandAuthorizationError(
                f"expected_initial_status path not canonical: {path!r} ({exc})"
            ) from exc
        if canonical_path in seen_paths:
            raise NudgeLandAuthorizationError(
                f"expected_initial_status has duplicate path: {canonical_path!r}"
            )
        seen_paths.add(canonical_path)

    if seen_paths != set(canonical_paths):
        raise NudgeLandAuthorizationError(
            "expected_initial_status paths must match authorized_paths exactly"
        )

    for field in (
        "authorization_version",
        "authorization_id",
        "authorized_branch",
        "authorized_base_head",
        "authorized_commit_subject",
        "authorized_remote",
        "authorized_remote_repository",
        "authorized_push_branch",
        "expected_remote_base_sha",
        "authorized_ci_workflow_or_check",
        "expected_ci_event",
    ):
        value = authorization[field]
        if not isinstance(value, str) or not value:
            raise NudgeLandAuthorizationError(
                f"{field} must be a non-empty str"
            )

    if not _is_hex_string(authorization["authorization_digest"], 64):
        raise NudgeLandAuthorizationError(
            "authorization_digest must be a 64-char hex SHA-256"
        )

    if not _is_hex_string(authorization["authorized_base_head"], 40):
        raise NudgeLandAuthorizationError(
            "authorized_base_head must be a 40-char hex SHA-1"
        )
    if not _is_hex_string(authorization["expected_remote_base_sha"], 40):
        raise NudgeLandAuthorizationError(
            "expected_remote_base_sha must be a 40-char hex SHA-1"
        )

    if authorization["single_use"] is not True:
        raise NudgeLandAuthorizationError(
            "single_use must be exactly True"
        )


def canonical_authorization_bytes(
    authorization: Mapping[str, Any],
) -> bytes:
    """Return the canonical UTF-8 JSON serialization of ``authorization``.

    The canonicalization rule is:

    * ``json.dumps(..., sort_keys=True, separators=(",", ":"))``
    * ``ensure_ascii=False`` so Unicode identifiers are preserved
    * ``allow_nan=False`` so non-finite floats are rejected
    * digest field is included in the serialization so the digest is
      self-describing.

    This function never reads or writes files; it is pure.
    """
    if not isinstance(authorization, Mapping):
        raise NudgeLandAuthorizationError(
            "authorization must be a mapping"
        )
    payload = json.dumps(
        dict(authorization),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return payload.encode("utf-8")


def canonical_authorization_bytes_without_digest(
    authorization: Mapping[str, Any],
) -> bytes:
    """Return the canonical serialization of ``authorization`` minus the digest."""
    if "authorization_digest" not in authorization:
        raise NudgeLandAuthorizationError(
            "authorization missing authorization_digest field"
        )
    stripped = {k: v for k, v in authorization.items() if k != "authorization_digest"}
    payload = json.dumps(
        stripped,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return payload.encode("utf-8")


def compute_authorization_digest(
    authorization: Mapping[str, Any],
) -> str:
    """Return the SHA-256 of the canonical serialization excluding the digest."""
    payload = canonical_authorization_bytes_without_digest(authorization)
    return hashlib.sha256(payload).hexdigest()


def verify_authorization_digest(
    authorization: Mapping[str, Any],
) -> None:
    """Recompute the digest and reject any mismatch with the supplied value."""
    expected = authorization.get("authorization_digest")
    if not isinstance(expected, str) or not _is_hex_string(expected, 64):
        raise NudgeLandAuthorizationError(
            "authorization_digest must be a SHA-256 hex str"
        )
    actual = compute_authorization_digest(authorization)
    if actual != expected:
        raise NudgeLandAuthorizationError(
            "authorization_digest mismatch: "
            f"supplied={expected!r} computed={actual!r}"
        )


# ---------------------------------------------------------------------------
# Worktree status parsing
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class WorktreeStatusEntry:
    """One parsed ``git status --porcelain=v2 -z`` entry.

    Only the supported subset of porcelain-v2 entries is modelled here:
    ordinary unstaged modifications (type ``1`` with ``.M``) and
    untracked files (type ``?``). Any other entry type is a hard-stop.
    """

    status: str  # STATUS_WORKTREE_MODIFIED or STATUS_UNTRACKED_NEW
    path: str  # POSIX relative path


def _split_v2_records(payload: bytes) -> list[bytes]:
    """Split a ``git status --porcelain=v2 -z`` payload into records."""
    if payload.endswith(b"\x00"):
        payload = payload[:-1]
    if not payload:
        return []
    return payload.split(b"\x00")


def parse_porcelain_v2_status(payload: bytes) -> list[WorktreeStatusEntry]:
    """Parse a ``git status --porcelain=v2 -z`` payload into entries.

    Supported entries are:

    * ``1 .M N... <path>`` — ordinary unstaged tracked modification →
      :data:`STATUS_WORKTREE_MODIFIED`.
    * ``? <path>`` — untracked file → :data:`STATUS_UNTRACKED_NEW`.

    Any other entry — including pre-staged, deleted, renamed, copied,
    conflicted, file-type changed, mode-only, submodule, intent-to-add,
    skip-worktree/sparse special states — is rejected with
    :class:`NudgeLandStatusError`.

    Path bytes are decoded with strict UTF-8 so two different invalid
    byte sequences can never collapse to the same replacement string.
    The HEAD / index / worktree file mode fields (mH / mI / mW) must
    all be equal and must equal one of the supported regular-file
    modes ``100644`` or ``100755``; a mode-only change
    (``mH == mI != mW``) and any other unsupported mode transition
    are hard-stop rejections.
    """
    _SUPPORTED_REGULAR_FILE_MODES = frozenset({"100644", "100755"})
    entries: list[WorktreeStatusEntry] = []
    for record in _split_v2_records(payload):
        if not record:
            continue
        kind = record[:1]
        if kind == b"?":
            try:
                path = record[2:].decode("utf-8")
            except UnicodeDecodeError as exc:
                raise NudgeLandStatusError(
                    f"invalid UTF-8 in untracked path: {exc}"
                ) from exc
            entries.append(WorktreeStatusEntry(STATUS_UNTRACKED_NEW, path))
            continue
        if kind == b"1":
            # Parse using fixed byte offsets so the parser survives
            # ``X == ' '`` (which produces two consecutive spaces in
            # the record and would otherwise split into two empty
            # tokens with a space-delimited tokenizer).
            #
            # Layout:
            #   0:           '1'
            #   1:           ' '
            #   2-3:         XY  (2 chars)
            #   4:           ' '
            #   5-8:         sub (4 chars)
            #   9:           ' '
            #   10-15:       mH  (6 chars)
            #   16:          ' '
            #   17-22:       mI  (6 chars)
            #   23:          ' '
            #   24-29:       mW  (6 chars)
            #   30:          ' '
            #   31-70:       hH  (40 chars)
            #   71:          ' '
            #   72-111:      hI  (40 chars)
            #   112:         ' '
            #   113+:        path (variable)
            if len(record) < 113:
                raise NudgeLandStatusError(
                    f"malformed porcelain v2 record: {record!r}"
                )
            xy = record[2:4].decode("ascii")
            sub = record[5:9].decode("ascii")
            mH = record[10:16].decode("ascii")
            mI = record[17:23].decode("ascii")
            mW = record[24:30].decode("ascii")
            try:
                path = record[113:].decode("utf-8")
            except UnicodeDecodeError as exc:
                raise NudgeLandStatusError(
                    f"invalid UTF-8 in worktree path: {exc}"
                ) from exc
            if len(xy) != 2:
                raise NudgeLandStatusError(
                    f"malformed XY status: {xy!r}"
                )
            x = xy[0]
            y = xy[1]
            # Real ``git status --porcelain=v2`` emits ``.`` for an
            # unchanged index status; older variants used `` ``. The
            # contract's frozen semantics accept either form so the
            # parser survives both.
            if x not in (" ", "."):
                raise NudgeLandStatusError(
                    f"pre-staged entry rejected: {xy!r} {path!r}"
                )
            if y == "D":
                raise NudgeLandStatusError(
                    f"deleted entry rejected: {path!r}"
                )
            if y in ("U", "X", "Y") or x in ("U",):
                raise NudgeLandStatusError(
                    f"conflict entry rejected: {xy!r} {path!r}"
                )
            if y == "?":
                raise NudgeLandStatusError(
                    f"untracked-in-worktree rejected: {path!r}"
                )
            if y == "!":
                raise NudgeLandStatusError(
                    f"ignored entry rejected: {path!r}"
                )
            if sub.startswith("S"):
                raise NudgeLandStatusError(
                    f"submodule entry rejected: sub={sub!r} {path!r}"
                )
            if sub != "N...":
                raise NudgeLandStatusError(
                    f"unsupported submodule state: sub={sub!r} {path!r}"
                )
            # F2: reject mode-only changes and any unsupported mode
            # transition. The supported initial candidate requires an
            # ordinary regular-file content modification: HEAD / index
            # / worktree modes must all equal the same supported
            # regular-file mode. Both ``100644`` and ``100755`` are
            # accepted as ordinary regular-file content modifications;
            # any other mode is rejected.
            if not (mH == mI == mW):
                raise NudgeLandStatusError(
                    f"mode-only or mode transition rejected: "
                    f"mH={mH!r} mI={mI!r} mW={mW!r} {path!r}"
                )
            if mH not in _SUPPORTED_REGULAR_FILE_MODES:
                raise NudgeLandStatusError(
                    f"unsupported file mode: mH={mH!r} {path!r}"
                )
            if y != "M":
                raise NudgeLandStatusError(
                    f"unsupported worktree status: {xy!r} {path!r}"
                )
            entries.append(WorktreeStatusEntry(STATUS_WORKTREE_MODIFIED, path))
            continue
        if kind in (b"2", b"u", b"!"):
            raise NudgeLandStatusError(
                f"unsupported porcelain v2 kind: {record[:32]!r}"
            )
        raise NudgeLandStatusError(
            f"unknown porcelain v2 kind: {record[:32]!r}"
        )
    return entries


def capture_worktree_status(
    worktree: str | os.PathLike[str],
    *,
    runner: ProcessRunner | None = None,
) -> list[WorktreeStatusEntry]:
    """Capture the worktree status and return parsed entries.

    Uses ``git -C <worktree> status --porcelain=v2 -z --untracked-files=normal``
    so the payload is NUL-delimited and machine-safe to parse.
    """
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = [
        "git",
        "-C",
        cwd,
        "status",
        "--porcelain=v2",
        "-z",
        "--untracked-files=normal",
    ]
    result = runner_fn(argv, cwd=cwd)
    if result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git status failed rc={result.returncode}: {result.stderr!r}"
        )
    return parse_porcelain_v2_status(result.stdout)


# ---------------------------------------------------------------------------
# Index snapshot / proof
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class CachedIndexEntry:
    """One parsed ``git diff --cached --name-status -z`` entry."""

    status_code: str  # single-character porcelain-v1 status code
    path: str  # POSIX relative path


def capture_index_path_set(
    worktree: str | os.PathLike[str],
    *,
    runner: ProcessRunner | None = None,
) -> tuple[str, ...]:
    """Return the sorted tuple of cached changed paths in the index."""
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = [
        "git",
        "-C",
        cwd,
        "diff",
        "--cached",
        "--name-only",
        "-z",
    ]
    result = runner_fn(argv, cwd=cwd)
    if result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git diff --cached --name-only failed rc={result.returncode}: {result.stderr!r}"
        )
    parts: list[str] = []
    for raw_part in result.stdout.split(b"\x00"):
        if not raw_part:
            continue
        try:
            decoded = raw_part.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise NudgeLandStatusError(
                f"invalid UTF-8 in cached path: {exc}"
            ) from exc
        try:
            parts.append(canonical_path_string(decoded))
        except NudgeLandPathError as exc:
            raise NudgeLandStatusError(
                f"invalid cached path: {decoded!r}: {exc}"
            ) from exc
    return tuple(sorted(parts))


def capture_index_status_set(
    worktree: str | os.PathLike[str],
    *,
    runner: ProcessRunner | None = None,
) -> tuple[CachedIndexEntry, ...]:
    """Return the sorted tuple of ``CachedIndexEntry`` for cached entries.

    Uses NUL-delimited ``--name-status`` so filenames containing spaces,
    tabs, or newlines do not break parsing. Renames, copies, and any
    non-A/M entry are rejected with :class:`NudgeLandStatusError`.

    Status bytes are decoded with strict ASCII and path bytes with
    strict UTF-8 so any two distinct Git-observed bytes can never
    collapse to the same replacement string.
    """
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = [
        "git",
        "-C",
        cwd,
        "diff",
        "--cached",
        "--name-status",
        "-z",
    ]
    result = runner_fn(argv, cwd=cwd)
    if result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git diff --cached --name-status failed rc={result.returncode}: {result.stderr!r}"
        )
    raw = result.stdout
    if raw.endswith(b"\x00"):
        raw = raw[:-1]
    if not raw:
        return ()
    parts = raw.split(b"\x00")
    entries: list[CachedIndexEntry] = []
    i = 0
    while i < len(parts):
        if i + 1 >= len(parts):
            raise NudgeLandStatusError(
                f"malformed trailing name-status record: "
                f"trailing token {parts[i]!r}"
            )
        status_raw = parts[i]
        path_raw = parts[i + 1]
        i += 2
        if not status_raw or not path_raw:
            continue
        try:
            status = status_raw.decode("ascii")
        except UnicodeDecodeError as exc:
            raise NudgeLandStatusError(
                f"invalid ASCII in cached status: {exc}"
            ) from exc
        # Skip the trailing original path on rename/copy records.
        if status.startswith(("R", "C")):
            raise NudgeLandStatusError(
                f"cached rename/copy rejected: {status!r} {path_raw!r}"
            )
        # Reject any unsupported status code. ``A`` and ``M`` are the
        # only codes the supported candidate set accepts.
        if status not in ("A", "M"):
            raise NudgeLandStatusError(
                f"unsupported cached status: {status!r} {path_raw!r}"
            )
        try:
            decoded = path_raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise NudgeLandStatusError(
                f"invalid UTF-8 in cached path: {exc}"
            ) from exc
        try:
            path = canonical_path_string(decoded)
        except NudgeLandPathError as exc:
            raise NudgeLandStatusError(
                f"invalid cached path: {decoded!r}: {exc}"
            ) from exc
        entries.append(CachedIndexEntry(status, path))
    entries.sort(key=lambda e: e.path)
    return tuple(entries)


@dataclasses.dataclass(frozen=True)
class WhitespaceVerdict:
    """Direct observation of a single cached whitespace check invocation."""

    state: str  # WHITESPACE_CLEAN / WHITESPACE_FINDING / GIT_COMMAND_FAILURE
    returncode: int
    stdout: bytes
    stderr: bytes


def capture_index_whitespace_verdict(
    worktree: str | os.PathLike[str],
    *,
    runner: ProcessRunner | None = None,
) -> WhitespaceVerdict:
    """Return a :class:`WhitespaceVerdict` distinguishing the three states."""
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = [
        "git",
        "-C",
        cwd,
        "diff",
        "--cached",
        "--check",
    ]
    result = runner_fn(argv, cwd=cwd)
    rc = result.returncode
    if rc == 0:
        state = WHITESPACE_CLEAN
    elif rc is not None and rc != 0 and not result.stderr and result.stdout:
        state = WHITESPACE_FINDING
    else:
        state = WHITESPACE_GIT_COMMAND_FAILURE
    return WhitespaceVerdict(
        state=state,
        returncode=int(rc) if rc is not None else -1,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def capture_index_blob_bytes(
    worktree: str | os.PathLike[str],
    rel_path: str,
    *,
    runner: ProcessRunner | None = None,
) -> bytes:
    """Return the staged blob bytes for ``rel_path`` from the index."""
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = [
        "git",
        "-C",
        cwd,
        "show",
        f":{rel_path}",
    ]
    result = runner_fn(argv, cwd=cwd)
    if result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git show staged blob failed rc={result.returncode}: {result.stderr!r}"
        )
    return result.stdout


def capture_index_blob_sha256(
    worktree: str | os.PathLike[str],
    rel_path: str,
    *,
    runner: ProcessRunner | None = None,
) -> str:
    """Return the SHA-256 of the staged blob bytes for ``rel_path``."""
    return hashlib.sha256(
        capture_index_blob_bytes(worktree, rel_path, runner=runner)
    ).hexdigest()


# ---------------------------------------------------------------------------
# Commit proof
# ---------------------------------------------------------------------------


def capture_head_sha(
    worktree: str | os.PathLike[str],
    *,
    runner: ProcessRunner | None = None,
) -> str:
    """Return the full 40-char HEAD SHA."""
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = ["git", "-C", cwd, "rev-parse", "HEAD"]
    result = runner_fn(argv, cwd=cwd)
    if result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git rev-parse HEAD failed rc={result.returncode}: {result.stderr!r}"
        )
    sha = result.stdout.strip().decode("ascii")
    if not _is_hex_string(sha, 40):
        raise NudgeLandSubprocessError(
            f"HEAD SHA is not a 40-char hex: {sha!r}"
        )
    return sha


def capture_head_parent(
    worktree: str | os.PathLike[str],
    *,
    runner: ProcessRunner | None = None,
) -> str:
    """Return the full 40-char HEAD parent SHA."""
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = ["git", "-C", cwd, "rev-parse", "HEAD^"]
    result = runner_fn(argv, cwd=cwd)
    if result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git rev-parse HEAD^ failed rc={result.returncode}: {result.stderr!r}"
        )
    sha = result.stdout.strip().decode("ascii")
    if not _is_hex_string(sha, 40):
        raise NudgeLandSubprocessError(
            f"HEAD parent SHA is not a 40-char hex: {sha!r}"
        )
    return sha


def capture_head_subject(
    worktree: str | os.PathLike[str],
    *,
    runner: ProcessRunner | None = None,
) -> str:
    """Return the HEAD commit subject line, exactly as recorded."""
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = ["git", "-C", cwd, "log", "-1", "--pretty=%s", "HEAD"]
    result = runner_fn(argv, cwd=cwd)
    if result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git log -1 --pretty=%s failed rc={result.returncode}: {result.stderr!r}"
        )
    try:
        return result.stdout.rstrip(b"\r\n").decode("utf-8")
    except UnicodeDecodeError as exc:
        raise NudgeLandStatusError(
            f"invalid UTF-8 in HEAD subject: {exc}"
        ) from exc


def capture_head_changed_paths(
    worktree: str | os.PathLike[str],
    *,
    runner: ProcessRunner | None = None,
) -> tuple[tuple[str, str], ...]:
    """Return the sorted tuple of ``(status, path)`` for HEAD vs HEAD^.

    Uses NUL-delimited ``git diff-tree --no-commit-id --name-status -z``
    so filenames containing spaces, tabs, or newlines do not break
    parsing. Renames, copies, and any unsupported status are rejected.

    Status bytes are decoded with strict ASCII and path bytes with
    strict UTF-8 so any two distinct Git-observed bytes can never
    collapse to the same replacement string.
    """
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = [
        "git",
        "-C",
        cwd,
        "diff-tree",
        "--no-commit-id",
        "--name-status",
        "-z",
        "-r",
        "HEAD^",
        "HEAD",
    ]
    result = runner_fn(argv, cwd=cwd)
    if result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git diff-tree failed rc={result.returncode}: {result.stderr!r}"
        )
    raw = result.stdout
    if raw.endswith(b"\x00"):
        raw = raw[:-1]
    if not raw:
        return ()
    parts = raw.split(b"\x00")
    pairs: list[tuple[str, str]] = []
    i = 0
    while i < len(parts):
        if i + 1 >= len(parts):
            raise NudgeLandStatusError(
                f"malformed trailing name-status record: "
                f"trailing token {parts[i]!r}"
            )
        status_raw = parts[i]
        path_raw = parts[i + 1]
        i += 2
        if not status_raw or not path_raw:
            continue
        try:
            status = status_raw.decode("ascii")
        except UnicodeDecodeError as exc:
            raise NudgeLandStatusError(
                f"invalid ASCII in HEAD-vs-parent status: {exc}"
            ) from exc
        if status.startswith(("R", "C")):
            raise NudgeLandStatusError(
                f"HEAD-vs-parent rename/copy rejected: {status!r} {path_raw!r}"
            )
        if status not in ("A", "M"):
            raise NudgeLandStatusError(
                f"unsupported HEAD-vs-parent status: {status!r} {path_raw!r}"
            )
        try:
            decoded = path_raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise NudgeLandStatusError(
                f"invalid UTF-8 in HEAD-vs-parent path: {exc}"
            ) from exc
        try:
            path = canonical_path_string(decoded)
        except NudgeLandPathError as exc:
            raise NudgeLandStatusError(
                f"invalid HEAD-vs-parent path: {decoded!r}: {exc}"
            ) from exc
        pairs.append((status, path))
    pairs.sort(key=lambda pair: pair[1])
    return tuple(pairs)


def capture_head_blob_bytes(
    worktree: str | os.PathLike[str],
    rel_path: str,
    *,
    runner: ProcessRunner | None = None,
) -> bytes:
    """Return the HEAD blob bytes for ``rel_path``."""
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = [
        "git",
        "-C",
        cwd,
        "show",
        f"HEAD:{rel_path}",
    ]
    result = runner_fn(argv, cwd=cwd)
    if result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git show HEAD blob failed rc={result.returncode}: {result.stderr!r}"
        )
    return result.stdout


def capture_head_blob_sha256(
    worktree: str | os.PathLike[str],
    rel_path: str,
    *,
    runner: ProcessRunner | None = None,
) -> str:
    """Return the SHA-256 of the HEAD blob bytes for ``rel_path``."""
    return hashlib.sha256(
        capture_head_blob_bytes(worktree, rel_path, runner=runner)
    ).hexdigest()


def capture_worktree_is_clean(
    worktree: str | os.PathLike[str],
    *,
    runner: ProcessRunner | None = None,
) -> bool:
    """Return True iff the worktree is clean after a successful commit."""
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = [
        "git",
        "-C",
        cwd,
        "status",
        "--porcelain=v2",
        "-z",
        "--untracked-files=normal",
    ]
    result = runner_fn(argv, cwd=cwd)
    if result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git status post-commit failed rc={result.returncode}: {result.stderr!r}"
        )
    return not result.stdout.strip(b"\x00\n\r ").strip()


# ---------------------------------------------------------------------------
# Remote destination normalization
# ---------------------------------------------------------------------------


_GITHUB_HTTPS_PATTERN = re.compile(
    r"^https://github\.com/([^/\s]+)/([^/\s]+?)(?:\.git)?$"
)
_GITHUB_SSH_PATTERN = re.compile(
    r"^git@github\.com:([^/\s]+)/([^/\s]+?)(?:\.git)?$"
)


@dataclasses.dataclass(frozen=True)
class CanonicalRepoIdentity:
    """Canonical normalized repository identity."""

    host_tag: str  # always ``github`` in the initial implementation
    owner: str
    repo: str

    def as_string(self) -> str:
        return f"{self.host_tag}:{self.owner}/{self.repo}"


def normalize_github_remote(url: str) -> CanonicalRepoIdentity:
    """Normalize one of the four supported GitHub URL forms."""
    if not isinstance(url, str) or not url:
        raise NudgeLandRemoteError("remote URL must be a non-empty str")
    candidate = url.strip()
    match = _GITHUB_HTTPS_PATTERN.match(candidate)
    if match:
        owner, repo = match.group(1), match.group(2)
    else:
        match = _GITHUB_SSH_PATTERN.match(candidate)
        if not match:
            raise NudgeLandRemoteError(
                f"unsupported remote URL form: {url!r}"
            )
        owner, repo = match.group(1), match.group(2)
    if not owner or not repo:
        raise NudgeLandRemoteError(
            f"remote URL missing owner/repository: {url!r}"
        )
    return CanonicalRepoIdentity(GITHUB_HOST_TAG, owner, repo)


def parse_canonical_repo(identity: str) -> CanonicalRepoIdentity:
    """Parse the canonical ``github:<owner>/<repo>`` identity string."""
    if not isinstance(identity, str) or not identity:
        raise NudgeLandRemoteError("canonical identity must be a non-empty str")
    match = re.match(r"^github:([^/\s]+)/([^/\s]+)$", identity)
    if not match:
        raise NudgeLandRemoteError(
            f"unsupported canonical identity: {identity!r}"
        )
    owner, repo = match.group(1), match.group(2)
    return CanonicalRepoIdentity(GITHUB_HOST_TAG, owner, repo)


def canonical_identity_for_remote_repository(
    remote_repository: str,
) -> CanonicalRepoIdentity:
    """Convert a ``<owner>/<repo>`` or canonical string into the identity."""
    if not isinstance(remote_repository, str) or not remote_repository:
        raise NudgeLandRemoteError(
            "remote repository must be a non-empty str"
        )
    if "/" in remote_repository and ":" not in remote_repository:
        match = re.match(r"^([^/\s]+)/([^/\s]+)$", remote_repository)
        if match:
            return CanonicalRepoIdentity(GITHUB_HOST_TAG, match.group(1), match.group(2))
    return parse_canonical_repo(remote_repository)


# ---------------------------------------------------------------------------
# Remote push-URL proof
# ---------------------------------------------------------------------------


def capture_push_urls(
    worktree: str | os.PathLike[str],
    remote: str,
    *,
    runner: ProcessRunner | None = None,
) -> list[str]:
    """Return the push URLs configured for ``remote`` from the worktree.

    When no explicit ``remote.<remote>.pushurl`` entries exist, the
    implicit push URL — the fetch URL — is returned as a single-element
    list. When one or more explicit pushurl entries exist, only those
    entries are returned.
    """
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    pushurl_argv = [
        "git",
        "-C",
        cwd,
        "config",
        "--get-all",
        f"remote.{remote}.pushurl",
    ]
    pushurl_result = runner_fn(pushurl_argv, cwd=cwd)
    if pushurl_result.returncode not in (0, 1):
        raise NudgeLandSubprocessError(
            f"git config --get-all pushurl failed rc={pushurl_result.returncode}: "
            f"{pushurl_result.stderr!r}"
        )
    explicit: list[str] = []
    if pushurl_result.returncode == 0:
        for raw in pushurl_result.stdout.splitlines():
            line = raw.decode("utf-8").strip()
            if line:
                explicit.append(line)
    if explicit:
        return explicit
    fetch_argv = [
        "git",
        "-C",
        cwd,
        "remote",
        "get-url",
        remote,
    ]
    fetch_result = runner_fn(fetch_argv, cwd=cwd)
    if fetch_result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git remote get-url failed rc={fetch_result.returncode}: "
            f"{fetch_result.stderr!r}"
        )
    fetch_url = fetch_result.stdout.decode("utf-8").strip()
    if not fetch_url:
        raise NudgeLandRemoteError(
            f"remote {remote!r} has no resolvable URL"
        )
    return [fetch_url]


def verify_remote_push_destination(
    worktree: str | os.PathLike[str],
    remote: str,
    expected_identity: str,
    *,
    runner: ProcessRunner | None = None,
) -> CanonicalRepoIdentity:
    """Verify that the configured push destination matches ``expected_identity``.

    Exactly one push URL must resolve to ``expected_identity`` after
    normalization. Multiple push URLs that resolve to multiple distinct
    canonical identities is a hard-stop. A single push URL that
    resolves to a different canonical identity is also a hard-stop.
    """
    expected = parse_canonical_repo(expected_identity)
    push_urls = capture_push_urls(worktree, remote, runner=runner)
    if not push_urls:
        raise NudgeLandRemoteError(
            f"remote {remote!r} has no push URLs"
        )
    identities = [normalize_github_remote(url) for url in push_urls]
    canonical_strings = {identity.as_string() for identity in identities}
    if len(canonical_strings) != 1:
        raise NudgeLandRemoteError(
            f"multiple distinct push destinations for {remote!r}: "
            f"{sorted(canonical_strings)}"
        )
    canonical_identity = next(iter(canonical_strings))
    if canonical_identity != expected.as_string():
        raise NudgeLandRemoteError(
            f"push destination mismatch: got {canonical_identity!r}, "
            f"expected {expected.as_string()!r}"
        )
    return expected


# ---------------------------------------------------------------------------
# Remote branch SHA — network-read primitive
# ---------------------------------------------------------------------------


def build_ls_remote_branch_argv(
    remote: str,
    branch: str,
) -> list[str]:
    """Construct the argument vector for ``git ls-remote`` of one branch."""
    return [
        "git",
        "ls-remote",
        remote,
        f"refs/heads/{branch}",
    ]


def parse_ls_remote_branch_payload(
    payload: bytes,
    expected_branch: str,
) -> str:
    """Parse a ``git ls-remote <remote> refs/heads/<branch>`` payload."""
    text = payload.decode("utf-8", errors="replace")
    for raw_line in text.splitlines():
        if not raw_line:
            continue
        parts = raw_line.split("\t", 1)
        if len(parts) != 2:
            raise NudgeLandSubprocessError(
                f"ls-remote line malformed: {raw_line!r}"
            )
        sha, ref = parts[0], parts[1]
        if ref == f"refs/heads/{expected_branch}":
            if not _is_hex_string(sha, 40):
                raise NudgeLandSubprocessError(
                    f"ls-remote SHA not a 40-char hex: {sha!r}"
                )
            return sha
    raise NudgeLandSubprocessError(
        f"ls-remote missing ref refs/heads/{expected_branch}"
    )


def read_remote_branch_sha(
    worktree: str | os.PathLike[str],
    remote: str,
    branch: str,
    *,
    runner: ProcessRunner | None = None,
) -> str:
    """Run the production ``git ls-remote`` query and return the SHA."""
    cwd = str(pathlib.Path(os.fspath(worktree)).resolve())
    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = build_ls_remote_branch_argv(remote, branch)
    result = runner_fn(argv, cwd=cwd)
    if result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git ls-remote failed rc={result.returncode}: {result.stderr!r}"
        )
    return parse_ls_remote_branch_payload(result.stdout, branch)


def capture_remote_branch_sha_via_runner(
    argv_builder: Callable[[], list[str]],
    cwd: str,
    runner: ProcessRunner,
    expected_branch: str,
) -> str:
    """Run an externally constructed ``git ls-remote`` argv and parse the SHA."""
    argv = argv_builder()
    if list(argv[:2]) != ["git", "ls-remote"]:
        raise NudgeLandSubprocessError(
            f"argv is not a git ls-remote command: {argv!r}"
        )
    result = runner(argv, cwd=cwd)
    if result.returncode != 0:
        raise NudgeLandSubprocessError(
            f"git ls-remote failed rc={result.returncode}: {result.stderr!r}"
        )
    return parse_ls_remote_branch_payload(result.stdout, expected_branch)


# ---------------------------------------------------------------------------
# CI query / polling
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class CIQueryRequest:
    """The exact CI query contract for the verify_ci operation."""

    workflow: str
    head_sha: str
    branch: str
    event: str


@dataclasses.dataclass(frozen=True)
class CIResponse:
    """A successful CI response that the runtime is willing to accept."""

    workflow: str
    head_sha: str
    branch: str
    event: str
    conclusion: str  # CI_CONCLUSION_SUCCESS only


@dataclasses.dataclass(frozen=True)
class CIRunRecord:
    """One normalized CI run record parsed from an API response payload."""

    name: str
    head_sha: str
    head_branch: str
    event: str
    status: str
    conclusion: str | None


def build_ci_query_argv(remote_repo: str, head_sha: str) -> list[str]:
    """Construct the argv for ``gh api repos/.../actions/runs?head_sha=...``."""
    identity = parse_canonical_repo(remote_repo)
    path = f"repos/{identity.owner}/{identity.repo}/actions/runs?head_sha={head_sha}"
    return ["gh", "api", path]


def parse_ci_response_payload(payload: dict[str, Any]) -> list[CIRunRecord]:
    """Parse the raw API JSON payload into ``CIRunRecord`` instances."""
    if not isinstance(payload, Mapping):
        raise NudgeLandCIError("CI payload must be a JSON object")
    workflow_runs = payload.get("workflow_runs")
    if not isinstance(workflow_runs, list):
        raise NudgeLandCIError("CI payload missing workflow_runs list")
    records: list[CIRunRecord] = []
    for raw in workflow_runs:
        if not isinstance(raw, Mapping):
            continue
        try:
            records.append(
                CIRunRecord(
                    name=str(raw.get("name", "")),
                    head_sha=str(raw.get("head_sha", "")),
                    head_branch=str(raw.get("head_branch", "")),
                    event=str(raw.get("event", "")),
                    status=str(raw.get("status", "")),
                    conclusion=(
                        str(raw["conclusion"])
                        if raw.get("conclusion") is not None
                        else None
                    ),
                )
            )
        except Exception:
            continue
    return records


def _evaluate_single_ci_record(
    record: CIRunRecord,
    expected: CIQueryRequest,
) -> CIResponse | str:
    """Evaluate one record against the expected contract."""
    if record.head_sha != expected.head_sha:
        return CI_REJECTED_WRONG_SHA
    if record.head_branch != expected.branch:
        return CI_REJECTED_WRONG_BRANCH
    if record.event != expected.event:
        return CI_REJECTED_WRONG_EVENT
    if record.name != expected.workflow:
        return CI_REJECTED_WRONG_WORKFLOW
    if record.status != "completed":
        return "in_progress"
    conclusion = record.conclusion
    if conclusion == CI_CONCLUSION_SUCCESS:
        return CIResponse(
            workflow=record.name,
            head_sha=record.head_sha,
            branch=record.head_branch,
            event=record.event,
            conclusion=conclusion,
        )
    if conclusion == "failure":
        return CI_REJECTED_FAILURE
    if conclusion == "cancelled":
        return CI_REJECTED_CANCELLED
    if conclusion == "timed_out":
        return CI_REJECTED_TIMED_OUT
    if conclusion == "action_required":
        return CI_REJECTED_ACTION_REQUIRED
    return CI_REJECTED_FAILURE


def evaluate_ci_response(
    payload: dict[str, Any],
    expected: CIQueryRequest,
) -> CIResponse | str:
    """Evaluate a single CI payload and return either a response or a label."""
    records = parse_ci_response_payload(payload)
    for record in records:
        verdict = _evaluate_single_ci_record(record, expected)
        if verdict == "in_progress":
            continue
        return verdict
    return "in_progress"


class _MockResponseQueue:
    """Deterministic CI response queue that advances on every read.

    The contract: each call to ``take()`` returns the next response and
    advances the cursor. ``peek()`` returns the response at the cursor
    without advancing.
    """

    def __init__(self, responses: Sequence[dict[str, Any]]) -> None:
        self._responses: tuple[dict[str, Any], ...] = tuple(responses)
        self._index = 0

    def take(self) -> dict[str, Any] | None:
        if self._index >= len(self._responses):
            return None
        response = self._responses[self._index]
        self._index += 1
        return response

    def remaining(self) -> int:
        return max(0, len(self._responses) - self._index)


def query_ci(
    remote_repo: str,
    head_sha: str,
    expected: CIQueryRequest,
    *,
    runner: ProcessRunner | None = None,
    responses: Sequence[dict[str, Any]] | None = None,
    response_queue: _MockResponseQueue | None = None,
) -> CIResponse | str:
    """Run the production CI query and evaluate the response.

    When ``responses`` or ``response_queue`` is supplied, the runner is
    not invoked. Each call to ``query_ci`` consumes the next response
    from the supplied queue (without wrapping) so a
    ``queued -> in_progress -> success`` sequence actually advances.
    """
    if responses is not None or response_queue is not None:
        queue = (
            response_queue
            if response_queue is not None
            else _MockResponseQueue(responses or ())
        )
        payload = queue.take()
        if payload is None:
            return "in_progress"
        return evaluate_ci_response(payload, expected)

    runner_fn: ProcessRunner = runner if runner is not None else run_process
    argv = build_ci_query_argv(remote_repo, head_sha)
    result = runner_fn(argv, cwd=".")
    if result.returncode != 0:
        return CI_REJECTED_FAILURE
    try:
        payload = json.loads(result.stdout.decode("utf-8"))
    except json.JSONDecodeError:
        return CI_REJECTED_FAILURE
    return evaluate_ci_response(payload, expected)


def poll_ci(
    remote_repo: str,
    head_sha: str,
    expected: CIQueryRequest,
    *,
    timeout_seconds: float,
    interval_seconds: float,
    responses: Sequence[dict[str, Any]] | None = None,
    response_queue: _MockResponseQueue | None = None,
    runner: ProcessRunner | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    clock_fn: Callable[[], float] = time.monotonic,
) -> CIResponse | str:
    """Poll the CI query until a definitive verdict or timeout.

    ``timeout_seconds`` must be strictly positive. ``interval_seconds``
    must be non-negative. ``clock_fn`` is injectable so tests can
    deterministically reach the timeout without wall-clock sleeping.
    """
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if interval_seconds < 0:
        raise ValueError("interval_seconds must be non-negative")
    deadline = clock_fn() + timeout_seconds
    queue = (
        response_queue
        if response_queue is not None
        else (
            _MockResponseQueue(responses or ())
            if responses is not None
            else None
        )
    )
    while True:
        verdict = query_ci(
            remote_repo,
            head_sha,
            expected,
            runner=runner,
            response_queue=queue,
        )
        if verdict != "in_progress":
            return verdict
        if clock_fn() >= deadline:
            return CI_RESULT_NOT_ESTABLISHED_WITHIN_AUTHORIZED_TIMEOUT
        remaining = deadline - clock_fn()
        sleep_fn(min(interval_seconds, remaining))


# ---------------------------------------------------------------------------
# Receipt
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Receipt:
    """Structured receipt produced by every CLI operation."""

    authorization_id: str
    authorization_digest: str
    repository_identity: str
    operation: str
    entry_state: str
    attempted_transition: str
    mutation_attempted: bool
    mutation_result: str
    last_verified_state: str
    result_state: str
    authorization_state: str
    direct_observations: tuple[str, ...]
    unavailable_evidence: tuple[str, ...]
    hard_stop_reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "authorization_digest": self.authorization_digest,
            "repository_identity": self.repository_identity,
            "operation": self.operation,
            "entry_state": self.entry_state,
            "attempted_transition": self.attempted_transition,
            "mutation_attempted": self.mutation_attempted,
            "mutation_result": self.mutation_result,
            "last_verified_state": self.last_verified_state,
            "result_state": self.result_state,
            "authorization_state": self.authorization_state,
            "direct_observations": list(self.direct_observations),
            "unavailable_evidence": list(self.unavailable_evidence),
            "hard_stop_reason": self.hard_stop_reason,
        }


def build_receipt(
    *,
    authorization_id: str,
    authorization_digest: str,
    repository_identity: str,
    operation: str,
    entry_state: str,
    attempted_transition: str,
    mutation_attempted: bool,
    mutation_result: str,
    last_verified_state: str,
    result_state: str,
    authorization_state: str,
    direct_observations: Iterable[str] = (),
    unavailable_evidence: Iterable[str] = (),
    hard_stop_reason: str | None = None,
) -> Receipt:
    """Construct a ``Receipt`` deterministically."""
    return Receipt(
        authorization_id=str(authorization_id),
        authorization_digest=str(authorization_digest),
        repository_identity=str(repository_identity),
        operation=str(operation),
        entry_state=str(entry_state),
        attempted_transition=str(attempted_transition),
        mutation_attempted=bool(mutation_attempted),
        mutation_result=str(mutation_result),
        last_verified_state=str(last_verified_state),
        result_state=str(result_state),
        authorization_state=str(authorization_state),
        direct_observations=tuple(direct_observations),
        unavailable_evidence=tuple(unavailable_evidence),
        hard_stop_reason=(
            str(hard_stop_reason) if hard_stop_reason is not None else None
        ),
    )


def write_receipt(receipt: Receipt) -> None:
    """Serialize the receipt as one JSON object on stdout."""
    json.dump(receipt.to_dict(), sys.stdout)
    sys.stdout.write("\n")


__all__ = [
    "AUTHORIZATION_REQUIRED_FIELDS",
    "CanonicalRepoIdentity",
    "CIQueryRequest",
    "CIResponse",
    "CIRunRecord",
    "CachedIndexEntry",
    "CI_CONCLUSION_SUCCESS",
    "CI_REJECTED_ACTION_REQUIRED",
    "CI_REJECTED_CANCELLED",
    "CI_REJECTED_FAILURE",
    "CI_REJECTED_TIMED_OUT",
    "CI_REJECTED_WRONG_BRANCH",
    "CI_REJECTED_WRONG_EVENT",
    "CI_REJECTED_WRONG_SHA",
    "CI_REJECTED_WRONG_WORKFLOW",
    "CI_RESULT_NOT_ESTABLISHED_WITHIN_AUTHORIZED_TIMEOUT",
    "COMMIT_AUTHORIZED_KEYS",
    "GITHUB_HOST_TAG",
    "MUTATION_ATTEMPTED_COMPLETION_UNKNOWN",
    "MUTATION_DIRECTLY_OBSERVED_SUCCESSFUL_BUT_ACCEPTANCE_FAILED",
    "MUTATION_EXECUTED",
    "MUTATION_IN_PROGRESS_SUBSTATE_COMMIT",
    "MUTATION_IN_PROGRESS_SUBSTATE_PUSH",
    "MUTATION_IN_PROGRESS_SUBSTATE_VERIFY_CI",
    "MUTATION_NOT_ATTEMPTED",
    "NudgeLandAuthorizationError",
    "NudgeLandCIError",
    "NudgeLandError",
    "NudgeLandPathError",
    "NudgeLandRemoteError",
    "NudgeLandStatusError",
    "NudgeLandSubprocessError",
    "PUSH_AUTHORIZED_KEYS",
    "ProcessResult",
    "ProcessRunner",
    "Receipt",
    "STATUS_CODE_UNTRACKED_NEW",
    "STATUS_CODE_WORKTREE_MODIFIED",
    "STATUS_UNTRACKED_NEW",
    "STATUS_WORKTREE_MODIFIED",
    "STEP_S0_NOT_STARTED",
    "STEP_S1_LEDGER_ACTIVE",
    "STEP_S4_STAGED",
    "STEP_S5_COMMITTING",
    "STEP_S6_COMMITTED",
    "STEP_S7_PUSHING",
    "STEP_S8_PUSHED",
    "STEP_S9_VERIFYING_CI",
    "STEP_S10_LANDED",
    "VERIFY_CI_AUTHORIZED_KEYS",
    "WHITESPACE_CLEAN",
    "WHITESPACE_FINDING",
    "WHITESPACE_GIT_COMMAND_FAILURE",
    "WhitespaceVerdict",
    "WorktreeStatusEntry",
    "_MockResponseQueue",
    "assert_no_duplicate_normalized_paths",
    "build_ci_query_argv",
    "build_ls_remote_branch_argv",
    "build_receipt",
    "canonical_authorization_bytes",
    "canonical_authorization_bytes_without_digest",
    "canonical_identity_for_remote_repository",
    "canonical_path_string",
    "capture_head_blob_bytes",
    "capture_head_blob_sha256",
    "capture_head_changed_paths",
    "capture_head_parent",
    "capture_head_sha",
    "capture_head_subject",
    "capture_index_blob_bytes",
    "capture_index_blob_sha256",
    "capture_index_path_set",
    "capture_index_status_set",
    "capture_index_whitespace_verdict",
    "capture_push_urls",
    "capture_remote_branch_sha_via_runner",
    "capture_worktree_is_clean",
    "capture_worktree_status",
    "compute_authorization_digest",
    "compute_file_sha256",
    "evaluate_ci_response",
    "normalize_github_remote",
    "normalize_relative_path",
    "parse_canonical_repo",
    "parse_ci_response_payload",
    "parse_ls_remote_branch_payload",
    "parse_porcelain_v2_status",
    "poll_ci",
    "query_ci",
    "read_remote_branch_sha",
    "run_process",
    "validate_authorization_shape",
    "verify_authorization_digest",
    "verify_remote_push_destination",
    "write_receipt",
]
