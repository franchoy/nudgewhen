"""Unit tests for the persistent outside-worktree transaction ledger.

The tests cover the per-authorization lookup design, atomic write
semantics, per-authorization lock fail-closed semantics, and the
corrupt / terminal / stale error surfaces. Every test uses
``tempfile.TemporaryDirectory`` so the persistent state root is fully
isolated and never touches the NudgeWhen worktree or the host default
state root.
"""

from __future__ import annotations

import datetime as _datetime
import fcntl
import hashlib
import json
import os
import pathlib
import shutil
import tempfile
import threading
import time
import unittest

from scripts import nudge_land_ledger as ledger_mod
from scripts.nudge_land_ledger import (
    LEDGER_FILE_SUFFIX,
    LEDGER_STATE_ACTIVE,
    LEDGER_STATE_CONSUMED,
    LEDGER_STATE_LANDED,
    LEDGER_STATE_MUTATION_IN_PROGRESS,
    LedgerAmbiguousError,
    LedgerAuthorizationTerminalError,
    LedgerCorruptError,
    LedgerDurabilityError,
    LedgerEntry,
    LedgerError,
    LedgerLockedError,
    LedgerMissingError,
    LedgerStaleMutationError,
    LedgerStateError,
    LedgerStore,
    STEP_S1_LEDGER_ACTIVE,
    STEP_S4_STAGED,
    STEP_S6_COMMITTED,
    STEP_S8_PUSHED,
    STEP_S10_LANDED,
    TERMINAL_STATES,
    _safe_component,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

REPO_IDENTITY = "github:octocat/hello"
OTHER_IDENTITY = "github:octocat/world"
AUTH_ID = "auth-001"
AUTH_DIGEST = "a" * 64


def _now_iso() -> str:
    return (
        _datetime.datetime.now(tz=_datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )


def _base_entry(
    *,
    identity: str = REPO_IDENTITY,
    auth_id: str = AUTH_ID,
    auth_digest: str = AUTH_DIGEST,
    state: str = LEDGER_STATE_ACTIVE,
    verified_state: str = STEP_S1_LEDGER_ACTIVE,
    landing_commit_sha: str | None = None,
    mutation_intent: str | None = None,
    mutation_in_progress_substate: str | None = None,
) -> LedgerEntry:
    """Build a structurally valid ``LedgerEntry`` with deterministic defaults."""
    now = _now_iso()
    return LedgerEntry(
        authorization_id=auth_id,
        authorization_digest=auth_digest,
        repository_identity=identity,
        authorized_branch="release/v0.1.3",
        authorized_base_head="1" * 40,
        authorized_push_branch="release/v0.1.3",
        authorized_remote="origin",
        authorized_remote_repository=identity,
        authorized_commit_subject="feat: stage nudge-land runtime",
        expected_remote_base_sha="2" * 40,
        authorized_ci_workflow_or_check="CI",
        expected_ci_event="push",
        authorized_paths=["scripts/nudge_land_runtime.py"],
        authorized_file_fingerprints={
            "scripts/nudge_land_runtime.py": "a" * 64,
        },
        expected_initial_status=[
            {
                "status": "WORKTREE_MODIFIED",
                "path": "scripts/nudge_land_runtime.py",
            }
        ],
        state=state,
        mutation_intent=mutation_intent,
        mutation_in_progress_substate=mutation_in_progress_substate,
        verified_state=verified_state,
        landing_commit_sha=landing_commit_sha,
        created_at=now,
        updated_at=now,
        history=[
            {
                "step": verified_state,
                "timestamp": now,
                "notes": "ledger created",
            }
        ],
    )


def _write_entry(state_root: pathlib.Path, entry: LedgerEntry) -> pathlib.Path:
    """Atomically write ``entry`` under ``state_root`` bypassing the store API."""
    identity_dir = (
        state_root / "ledgers" / _safe_component(entry.repository_identity)
    )
    identity_dir.mkdir(parents=True, exist_ok=True)
    path = identity_dir / f"{_safe_component(entry.authorization_id)}{LEDGER_FILE_SUFFIX}"
    serialized = json.dumps(
        entry.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    path.write_text(serialized, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# M1, M2: id+digest-only deterministic lookup
# ---------------------------------------------------------------------------


class TestFindByIdDigest(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-ledger-m1-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_m1_lookup_success(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        store.create(
            repository_identity=REPO_IDENTITY,
            authorization_id=AUTH_ID,
            authorization_digest=AUTH_DIGEST,
            authorized_branch="release/v0.1.3",
            authorized_base_head="1" * 40,
            authorized_push_branch="release/v0.1.3",
            authorized_remote="origin",
            authorized_remote_repository="github:octocat/hello",
            authorized_commit_subject="feat: stage nudge-land runtime",
            expected_remote_base_sha="2" * 40,
            authorized_ci_workflow_or_check="CI",
            expected_ci_event="push",
            authorized_paths=["scripts/nudge_land_runtime.py"],
            authorized_file_fingerprints={
                "scripts/nudge_land_runtime.py": "a" * 64,
            },
            expected_initial_status=[
                {
                    "status": "WORKTREE_MODIFIED",
                    "path": "scripts/nudge_land_runtime.py",
                }
            ],
        )
        entry = store.find_by_id_digest(AUTH_ID, AUTH_DIGEST)
        self.assertEqual(entry.authorization_id, AUTH_ID)
        self.assertEqual(entry.authorization_digest, AUTH_DIGEST)
        self.assertEqual(entry.repository_identity, REPO_IDENTITY)

    def test_m1_create_rejects_remote_repository_identity_mismatch(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        with self.assertRaises(LedgerStateError):
            store.create(
                repository_identity=REPO_IDENTITY,
                authorization_id=AUTH_ID,
                authorization_digest=AUTH_DIGEST,
                authorized_branch="release/v0.1.3",
                authorized_base_head="1" * 40,
                authorized_push_branch="release/v0.1.3",
                authorized_remote="origin",
                authorized_remote_repository=OTHER_IDENTITY,
                authorized_commit_subject="feat: stage nudge-land runtime",
                expected_remote_base_sha="2" * 40,
                authorized_ci_workflow_or_check="CI",
                expected_ci_event="push",
                authorized_paths=["scripts/nudge_land_runtime.py"],
                authorized_file_fingerprints={
                    "scripts/nudge_land_runtime.py": "a" * 64,
                },
                expected_initial_status=[
                    {
                        "status": "WORKTREE_MODIFIED",
                        "path": "scripts/nudge_land_runtime.py",
                    }
                ],
            )
        # No ledger entry must have been persisted for this authorization.
        with self.assertRaises(LedgerMissingError):
            store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        with self.assertRaises(LedgerMissingError):
            store.find_by_id_digest(AUTH_ID, AUTH_DIGEST)

    def test_m2_missing_rejected(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        with self.assertRaises(LedgerMissingError):
            store.find_by_id_digest(AUTH_ID, AUTH_DIGEST)

    def test_m4_digest_binding_rejected(self) -> None:
        # Wrong digest must NOT match the persisted entry.
        store = LedgerStore(state_root=self.tmp)
        store.create(
            repository_identity=REPO_IDENTITY,
            authorization_id=AUTH_ID,
            authorization_digest=AUTH_DIGEST,
            authorized_branch="release/v0.1.3",
            authorized_base_head="1" * 40,
            authorized_push_branch="release/v0.1.3",
            authorized_remote="origin",
            authorized_remote_repository="github:octocat/hello",
            authorized_commit_subject="feat: stage nudge-land runtime",
            expected_remote_base_sha="2" * 40,
            authorized_ci_workflow_or_check="CI",
            expected_ci_event="push",
            authorized_paths=["scripts/nudge_land_runtime.py"],
            authorized_file_fingerprints={
                "scripts/nudge_land_runtime.py": "a" * 64,
            },
            expected_initial_status=[
                {
                    "status": "WORKTREE_MODIFIED",
                    "path": "scripts/nudge_land_runtime.py",
                }
            ],
        )
        with self.assertRaises(LedgerMissingError):
            store.find_by_id_digest(AUTH_ID, "b" * 64)


# ---------------------------------------------------------------------------
# M3: ambiguous/duplicate rejection
# ---------------------------------------------------------------------------


class TestAmbiguousLookup(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-ledger-m3-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_m3_ambiguous_rejected(self) -> None:
        # Two ledger entries sharing authorization_id+digest under
        # two distinct repository identities must surface as an
        # ambiguous error.
        entry_a = _base_entry(identity=REPO_IDENTITY)
        entry_b = _base_entry(identity=OTHER_IDENTITY)
        _write_entry(self.tmp, entry_a)
        _write_entry(self.tmp, entry_b)
        store = LedgerStore(state_root=self.tmp)
        with self.assertRaises(LedgerAmbiguousError) as ctx:
            store.find_by_id_digest(AUTH_ID, AUTH_DIGEST)
        self.assertGreaterEqual(len(ctx.exception.identities), 2)


# ---------------------------------------------------------------------------
# M5, M6: per-authorization concurrent lock fails closed
# ---------------------------------------------------------------------------


class TestConcurrentLock(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-ledger-m5-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_m5_concurrent_lock_fails_closed(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        store.create(
            repository_identity=REPO_IDENTITY,
            authorization_id=AUTH_ID,
            authorization_digest=AUTH_DIGEST,
            authorized_branch="release/v0.1.3",
            authorized_base_head="1" * 40,
            authorized_push_branch="release/v0.1.3",
            authorized_remote="origin",
            authorized_remote_repository="github:octocat/hello",
            authorized_commit_subject="feat: stage nudge-land runtime",
            expected_remote_base_sha="2" * 40,
            authorized_ci_workflow_or_check="CI",
            expected_ci_event="push",
            authorized_paths=["scripts/nudge_land_runtime.py"],
            authorized_file_fingerprints={
                "scripts/nudge_land_runtime.py": "a" * 64,
            },
            expected_initial_status=[
                {
                    "status": "WORKTREE_MODIFIED",
                    "path": "scripts/nudge_land_runtime.py",
                }
            ],
        )
        results: list[str] = []
        barrier = threading.Event()

        def attempt() -> None:
            try:
                with store.transaction(REPO_IDENTITY, AUTH_ID):
                    barrier.wait(timeout=0.5)
                    results.append("acquired")
            except LedgerLockedError:
                results.append("rejected")

        threads = [threading.Thread(target=attempt) for _ in range(2)]
        for t in threads:
            t.start()
        # Give the first thread time to acquire the lock.
        time.sleep(0.1)
        barrier.set()
        for t in threads:
            t.join(timeout=5.0)
        self.assertEqual(results.count("acquired"), 1)
        self.assertEqual(results.count("rejected"), 1)

    def test_m6_second_transaction_interleaved_rejected(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        store.create(
            repository_identity=REPO_IDENTITY,
            authorization_id=AUTH_ID,
            authorization_digest=AUTH_DIGEST,
            authorized_branch="release/v0.1.3",
            authorized_base_head="1" * 40,
            authorized_push_branch="release/v0.1.3",
            authorized_remote="origin",
            authorized_remote_repository="github:octocat/hello",
            authorized_commit_subject="feat: stage nudge-land runtime",
            expected_remote_base_sha="2" * 40,
            authorized_ci_workflow_or_check="CI",
            expected_ci_event="push",
            authorized_paths=["scripts/nudge_land_runtime.py"],
            authorized_file_fingerprints={
                "scripts/nudge_land_runtime.py": "a" * 64,
            },
            expected_initial_status=[
                {
                    "status": "WORKTREE_MODIFIED",
                    "path": "scripts/nudge_land_runtime.py",
                }
            ],
        )
        with store.transaction(REPO_IDENTITY, AUTH_ID):
            # Nested same-authorization transaction must fail closed.
            with self.assertRaises(LedgerLockedError):
                with store.transaction(REPO_IDENTITY, AUTH_ID):
                    pass

    def test_m15_transaction_create_rejects_remote_repository_identity_mismatch(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        with store.transaction(REPO_IDENTITY, AUTH_ID) as tx:
            with self.assertRaises(LedgerStateError):
                tx.create(
                    authorization_digest=AUTH_DIGEST,
                    authorized_branch="release/v0.1.3",
                    authorized_base_head="1" * 40,
                    authorized_push_branch="release/v0.1.3",
                    authorized_remote="origin",
                    authorized_remote_repository=OTHER_IDENTITY,
                    authorized_commit_subject="feat: stage nudge-land runtime",
                    expected_remote_base_sha="2" * 40,
                    authorized_ci_workflow_or_check="CI",
                    expected_ci_event="push",
                    authorized_paths=["scripts/nudge_land_runtime.py"],
                    authorized_file_fingerprints={
                        "scripts/nudge_land_runtime.py": "a" * 64,
                    },
                    expected_initial_status=[
                        {
                            "status": "WORKTREE_MODIFIED",
                            "path": "scripts/nudge_land_runtime.py",
                        }
                    ],
                )
        # No ledger entry must have been durably created after transaction exit.
        with self.assertRaises(LedgerMissingError):
            store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        with self.assertRaises(LedgerMissingError):
            store.find_by_id_digest(AUTH_ID, AUTH_DIGEST)


# ---------------------------------------------------------------------------
# M7: verified_state semantics during mutation-in-progress
# ---------------------------------------------------------------------------


class TestVerifiedStateDuringMutation(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-ledger-m7-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _create(self) -> LedgerStore:
        store = LedgerStore(state_root=self.tmp)
        store.create(
            repository_identity=REPO_IDENTITY,
            authorization_id=AUTH_ID,
            authorization_digest=AUTH_DIGEST,
            authorized_branch="release/v0.1.3",
            authorized_base_head="1" * 40,
            authorized_push_branch="release/v0.1.3",
            authorized_remote="origin",
            authorized_remote_repository="github:octocat/hello",
            authorized_commit_subject="feat: stage nudge-land runtime",
            expected_remote_base_sha="2" * 40,
            authorized_ci_workflow_or_check="CI",
            expected_ci_event="push",
            authorized_paths=["scripts/nudge_land_runtime.py"],
            authorized_file_fingerprints={
                "scripts/nudge_land_runtime.py": "a" * 64,
            },
            expected_initial_status=[
                {
                    "status": "WORKTREE_MODIFIED",
                    "path": "scripts/nudge_land_runtime.py",
                }
            ],
        )
        return store

    def test_m7_stage_intent_keeps_s1(self) -> None:
        store = self._create()
        entry = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        advanced = store.advance(
            entry,
            new_state=LEDGER_STATE_MUTATION_IN_PROGRESS,
            new_verified_state=STEP_S1_LEDGER_ACTIVE,
            mutation_intent="STAGE",
            mutation_in_progress_substate="STAGE",
            notes="stage intent",
        )
        self.assertEqual(advanced.state, LEDGER_STATE_MUTATION_IN_PROGRESS)
        self.assertEqual(advanced.verified_state, STEP_S1_LEDGER_ACTIVE)

    def test_m7_unequal_mutation_pair_rejected_before_persistence(self) -> None:
        store = self._create()
        entry = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        with self.assertRaises(LedgerStateError):
            store.advance(
                entry,
                new_state=LEDGER_STATE_MUTATION_IN_PROGRESS,
                new_verified_state=STEP_S1_LEDGER_ACTIVE,
                mutation_intent="STAGE",
                mutation_in_progress_substate="COMMIT",
                notes="stage intent unequal",
            )
        # In-memory entry must remain at its original durable state.
        self.assertEqual(entry.state, LEDGER_STATE_ACTIVE)
        self.assertEqual(entry.verified_state, STEP_S1_LEDGER_ACTIVE)
        self.assertIsNone(entry.mutation_intent)
        self.assertIsNone(entry.mutation_in_progress_substate)
        # Reload the durable entry and prove it was not mutated.
        reloaded = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        self.assertEqual(reloaded.state, LEDGER_STATE_ACTIVE)
        self.assertEqual(reloaded.verified_state, STEP_S1_LEDGER_ACTIVE)
        self.assertIsNone(reloaded.mutation_intent)
        self.assertIsNone(reloaded.mutation_in_progress_substate)

    def test_m7_commit_intent_keeps_s4(self) -> None:
        store = self._create()
        entry = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        advanced = store.advance(
            entry,
            new_state=LEDGER_STATE_MUTATION_IN_PROGRESS,
            new_verified_state=STEP_S4_STAGED,
            mutation_intent="COMMIT",
            mutation_in_progress_substate="COMMIT",
            notes="commit intent",
        )
        self.assertEqual(advanced.verified_state, STEP_S4_STAGED)

    def test_m7_push_intent_keeps_s6(self) -> None:
        store = self._create()
        entry = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        advanced = store.advance(
            entry,
            new_state=LEDGER_STATE_MUTATION_IN_PROGRESS,
            new_verified_state=STEP_S6_COMMITTED,
            mutation_intent="PUSH",
            mutation_in_progress_substate="PUSH",
            notes="push intent",
        )
        self.assertEqual(advanced.verified_state, STEP_S6_COMMITTED)

    def test_m7_verify_ci_intent_keeps_s8(self) -> None:
        store = self._create()
        entry = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        advanced = store.advance(
            entry,
            new_state=LEDGER_STATE_MUTATION_IN_PROGRESS,
            new_verified_state=STEP_S8_PUSHED,
            mutation_intent="VERIFY_CI",
            mutation_in_progress_substate="VERIFY_CI",
            notes="verify_ci intent",
        )
        self.assertEqual(advanced.verified_state, STEP_S8_PUSHED)


# ---------------------------------------------------------------------------
# M8: landing_commit_sha round-trips
# ---------------------------------------------------------------------------


class TestLandingShaRoundTrip(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-ledger-m8-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_m8_landing_sha_persists_and_round_trips(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        store.create(
            repository_identity=REPO_IDENTITY,
            authorization_id=AUTH_ID,
            authorization_digest=AUTH_DIGEST,
            authorized_branch="release/v0.1.3",
            authorized_base_head="1" * 40,
            authorized_push_branch="release/v0.1.3",
            authorized_remote="origin",
            authorized_remote_repository="github:octocat/hello",
            authorized_commit_subject="feat: stage nudge-land runtime",
            expected_remote_base_sha="2" * 40,
            authorized_ci_workflow_or_check="CI",
            expected_ci_event="push",
            authorized_paths=["scripts/nudge_land_runtime.py"],
            authorized_file_fingerprints={
                "scripts/nudge_land_runtime.py": "a" * 64,
            },
            expected_initial_status=[
                {
                    "status": "WORKTREE_MODIFIED",
                    "path": "scripts/nudge_land_runtime.py",
                }
            ],
        )
        entry = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        landed = "abcdef0123456789abcdef0123456789abcdef01"
        store.advance(
            entry,
            new_state=LEDGER_STATE_MUTATION_IN_PROGRESS,
            new_verified_state=STEP_S4_STAGED,
            mutation_intent="COMMIT",
            mutation_in_progress_substate="COMMIT",
            notes="commit intent",
        )
        advanced = store.advance(
            entry,
            new_state=LEDGER_STATE_ACTIVE,
            new_verified_state=STEP_S6_COMMITTED,
            mutation_intent=None,
            mutation_in_progress_substate=None,
            notes="commit complete",
            landing_commit_sha=landed,
        )
        self.assertEqual(advanced.landing_commit_sha, landed)
        reloaded = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        self.assertEqual(reloaded.landing_commit_sha, landed)
        # Also confirm via the public id+digest lookup.
        via_lookup = store.find_by_id_digest(AUTH_ID, AUTH_DIGEST)
        self.assertEqual(via_lookup.landing_commit_sha, landed)


# ---------------------------------------------------------------------------
# M9, M10: fsync failure fail-closed
# ---------------------------------------------------------------------------


class TestFsyncFailure(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-ledger-m9-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)
        # Restore default os.fsync in case a test patched it.
        if hasattr(os, "fsync"):
            pass  # The patcher is restored in each test.

    def test_m9_file_fsync_failure_fails_closed(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        original_fsync = os.fsync

        def raising_fsync(fd: int) -> None:
            raise OSError(5, "simulated fsync failure")

        os.fsync = raising_fsync  # type: ignore[assignment]
        try:
            with self.assertRaises(LedgerDurabilityError):
                store.create(
                    repository_identity=REPO_IDENTITY,
                    authorization_id=AUTH_ID,
                    authorization_digest=AUTH_DIGEST,
                    authorized_branch="release/v0.1.3",
                    authorized_base_head="1" * 40,
                    authorized_push_branch="release/v0.1.3",
                    authorized_remote="origin",
                    authorized_remote_repository="github:octocat/hello",
                    authorized_commit_subject="feat: stage nudge-land runtime",
                    expected_remote_base_sha="2" * 40,
                    authorized_ci_workflow_or_check="CI",
                    expected_ci_event="push",
                    authorized_paths=["scripts/nudge_land_runtime.py"],
                    authorized_file_fingerprints={
                        "scripts/nudge_land_runtime.py": "a" * 64,
                    },
                    expected_initial_status=[
                        {
                            "status": "WORKTREE_MODIFIED",
                            "path": "scripts/nudge_land_runtime.py",
                        }
                    ],
                )
        finally:
            os.fsync = original_fsync  # type: ignore[assignment]

    def test_m10_directory_fsync_failure_fails_closed(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        # First create succeeds without fsync patch.
        store.create(
            repository_identity=REPO_IDENTITY,
            authorization_id=AUTH_ID,
            authorization_digest=AUTH_DIGEST,
            authorized_branch="release/v0.1.3",
            authorized_base_head="1" * 40,
            authorized_push_branch="release/v0.1.3",
            authorized_remote="origin",
            authorized_remote_repository="github:octocat/hello",
            authorized_commit_subject="feat: stage nudge-land runtime",
            expected_remote_base_sha="2" * 40,
            authorized_ci_workflow_or_check="CI",
            expected_ci_event="push",
            authorized_paths=["scripts/nudge_land_runtime.py"],
            authorized_file_fingerprints={
                "scripts/nudge_land_runtime.py": "a" * 64,
            },
            expected_initial_status=[
                {
                    "status": "WORKTREE_MODIFIED",
                    "path": "scripts/nudge_land_runtime.py",
                }
            ],
        )
        # Now patch fsync to fail only on the directory fd, not on
        # the file fd. The directory fsync is the second call inside
        # ``_atomic_write``.
        entry = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        store.advance(
            entry,
            new_state=LEDGER_STATE_MUTATION_IN_PROGRESS,
            new_verified_state=STEP_S1_LEDGER_ACTIVE,
            mutation_intent="STAGE",
            mutation_in_progress_substate="STAGE",
            notes="stage intent",
        )
        original_fsync = os.fsync

        def selective_fsync(fd: int) -> None:
            # The directory fd is obtained via ``os.open(O_DIRECTORY)``
            # and ``fstat`` reports ``S_ISDIR``. Use that to fail only
            # the directory fsync.
            try:
                import stat as _stat
                st = os.fstat(fd)
                if _stat.S_ISDIR(st.st_mode):
                    raise OSError(5, "simulated dir fsync failure")
            except OSError:
                # If fstat itself raises, fall back to raising.
                raise

        os.fsync = selective_fsync  # type: ignore[assignment]
        try:
            with self.assertRaises(LedgerDurabilityError):
                store.advance(
                    entry,
                    new_state=LEDGER_STATE_ACTIVE,
                    new_verified_state=STEP_S4_STAGED,
                    mutation_intent=None,
                    mutation_in_progress_substate=None,
                    notes="stage complete",
                )
        finally:
            os.fsync = original_fsync  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# M11: failed persistence does not falsely advance in-memory state
# ---------------------------------------------------------------------------


class TestFailedPersistenceDoesNotMutate(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-ledger-m11-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_m11_failed_persistence_leaves_in_memory_unchanged(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        store.create(
            repository_identity=REPO_IDENTITY,
            authorization_id=AUTH_ID,
            authorization_digest=AUTH_DIGEST,
            authorized_branch="release/v0.1.3",
            authorized_base_head="1" * 40,
            authorized_push_branch="release/v0.1.3",
            authorized_remote="origin",
            authorized_remote_repository="github:octocat/hello",
            authorized_commit_subject="feat: stage nudge-land runtime",
            expected_remote_base_sha="2" * 40,
            authorized_ci_workflow_or_check="CI",
            expected_ci_event="push",
            authorized_paths=["scripts/nudge_land_runtime.py"],
            authorized_file_fingerprints={
                "scripts/nudge_land_runtime.py": "a" * 64,
            },
            expected_initial_status=[
                {
                    "status": "WORKTREE_MODIFIED",
                    "path": "scripts/nudge_land_runtime.py",
                }
            ],
        )
        entry = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        store.advance(
            entry,
            new_state=LEDGER_STATE_MUTATION_IN_PROGRESS,
            new_verified_state=STEP_S4_STAGED,
            mutation_intent="COMMIT",
            mutation_in_progress_substate="COMMIT",
            notes="commit intent",
        )
        baseline_state = entry.state
        baseline_verified = entry.verified_state
        baseline_landing = entry.landing_commit_sha
        self.assertEqual(baseline_state, LEDGER_STATE_MUTATION_IN_PROGRESS)
        self.assertEqual(baseline_verified, STEP_S4_STAGED)
        self.assertIsNone(baseline_landing)
        # Patch fsync to fail.
        original_fsync = os.fsync

        def raising_fsync(fd: int) -> None:
            raise OSError(5, "simulated fsync failure")

        os.fsync = raising_fsync  # type: ignore[assignment]
        try:
            with self.assertRaises(LedgerDurabilityError):
                store.advance(
                    entry,
                    new_state=LEDGER_STATE_ACTIVE,
                    new_verified_state=STEP_S6_COMMITTED,
                    mutation_intent=None,
                    mutation_in_progress_substate=None,
                    notes="commit complete",
                    landing_commit_sha="abcdef0123456789abcdef0123456789abcdef01",
                )
        finally:
            os.fsync = original_fsync  # type: ignore[assignment]
        # The in-memory copy must still be at the captured baseline state.
        self.assertEqual(entry.state, baseline_state)
        self.assertEqual(entry.verified_state, baseline_verified)
        self.assertEqual(entry.landing_commit_sha, baseline_landing)


# ---------------------------------------------------------------------------
# M12: terminal LANDED/CONSUMED reuse fails closed
# ---------------------------------------------------------------------------


class TestTerminalReuse(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-ledger-m12-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_m12_landed_reuse_rejected(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        store.create(
            repository_identity=REPO_IDENTITY,
            authorization_id=AUTH_ID,
            authorization_digest=AUTH_DIGEST,
            authorized_branch="release/v0.1.3",
            authorized_base_head="1" * 40,
            authorized_push_branch="release/v0.1.3",
            authorized_remote="origin",
            authorized_remote_repository="github:octocat/hello",
            authorized_commit_subject="feat: stage nudge-land runtime",
            expected_remote_base_sha="2" * 40,
            authorized_ci_workflow_or_check="CI",
            expected_ci_event="push",
            authorized_paths=["scripts/nudge_land_runtime.py"],
            authorized_file_fingerprints={
                "scripts/nudge_land_runtime.py": "a" * 64,
            },
            expected_initial_status=[
                {
                    "status": "WORKTREE_MODIFIED",
                    "path": "scripts/nudge_land_runtime.py",
                }
            ],
        )
        entry = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        store.advance(
            entry,
            new_state=LEDGER_STATE_LANDED,
            new_verified_state=STEP_S10_LANDED,
            mutation_intent=None,
            mutation_in_progress_substate=None,
            landing_commit_sha="abcdef0123456789abcdef0123456789abcdef01",
            notes="landed",
        )
        # Reload should fail closed because terminal.
        with self.assertRaises(LedgerAuthorizationTerminalError):
            store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)

    def test_m12_consumed_reuse_rejected(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        store.create(
            repository_identity=REPO_IDENTITY,
            authorization_id=AUTH_ID,
            authorization_digest=AUTH_DIGEST,
            authorized_branch="release/v0.1.3",
            authorized_base_head="1" * 40,
            authorized_push_branch="release/v0.1.3",
            authorized_remote="origin",
            authorized_remote_repository="github:octocat/hello",
            authorized_commit_subject="feat: stage nudge-land runtime",
            expected_remote_base_sha="2" * 40,
            authorized_ci_workflow_or_check="CI",
            expected_ci_event="push",
            authorized_paths=["scripts/nudge_land_runtime.py"],
            authorized_file_fingerprints={
                "scripts/nudge_land_runtime.py": "a" * 64,
            },
            expected_initial_status=[
                {
                    "status": "WORKTREE_MODIFIED",
                    "path": "scripts/nudge_land_runtime.py",
                }
            ],
        )
        entry = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        store.advance(
            entry,
            new_state=LEDGER_STATE_CONSUMED,
            new_verified_state=STEP_S1_LEDGER_ACTIVE,
            mutation_intent=None,
            mutation_in_progress_substate=None,
            notes="consumed",
        )
        with self.assertRaises(LedgerAuthorizationTerminalError):
            store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)

    def test_m12_landed_without_sha_rejected_before_persistence(self) -> None:
        store = LedgerStore(state_root=self.tmp)
        store.create(
            repository_identity=REPO_IDENTITY,
            authorization_id=AUTH_ID,
            authorization_digest=AUTH_DIGEST,
            authorized_branch="release/v0.1.3",
            authorized_base_head="1" * 40,
            authorized_push_branch="release/v0.1.3",
            authorized_remote="origin",
            authorized_remote_repository="github:octocat/hello",
            authorized_commit_subject="feat: stage nudge-land runtime",
            expected_remote_base_sha="2" * 40,
            authorized_ci_workflow_or_check="CI",
            expected_ci_event="push",
            authorized_paths=["scripts/nudge_land_runtime.py"],
            authorized_file_fingerprints={
                "scripts/nudge_land_runtime.py": "a" * 64,
            },
            expected_initial_status=[
                {
                    "status": "WORKTREE_MODIFIED",
                    "path": "scripts/nudge_land_runtime.py",
                }
            ],
        )
        entry = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        with self.assertRaises(LedgerStateError):
            store.advance(
                entry,
                new_state=LEDGER_STATE_LANDED,
                new_verified_state=STEP_S10_LANDED,
                mutation_intent=None,
                mutation_in_progress_substate=None,
                notes="landed without sha",
            )
        self.assertEqual(entry.state, LEDGER_STATE_ACTIVE)
        self.assertEqual(entry.verified_state, STEP_S1_LEDGER_ACTIVE)
        self.assertIsNone(entry.landing_commit_sha)
        reloaded = store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        self.assertEqual(reloaded.state, LEDGER_STATE_ACTIVE)
        self.assertEqual(reloaded.verified_state, STEP_S1_LEDGER_ACTIVE)
        self.assertIsNone(reloaded.landing_commit_sha)


# ---------------------------------------------------------------------------
# M13: stale MUTATION_IN_PROGRESS fails closed
# ---------------------------------------------------------------------------


class TestStaleMutation(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-ledger-m13-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_m13_stale_mutation_in_progress_rejected(self) -> None:
        entry = _base_entry(
            state=LEDGER_STATE_MUTATION_IN_PROGRESS,
            verified_state=STEP_S1_LEDGER_ACTIVE,
            mutation_intent="STAGE",
            mutation_in_progress_substate="STAGE",
        )
        _write_entry(self.tmp, entry)
        store = LedgerStore(state_root=self.tmp)
        with self.assertRaises(LedgerStaleMutationError):
            store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        with self.assertRaises(LedgerStaleMutationError):
            store.find_by_id_digest(AUTH_ID, AUTH_DIGEST)


# ---------------------------------------------------------------------------
# M14: corrupt ledger JSON fails closed
# ---------------------------------------------------------------------------


class TestCorruptLedger(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-ledger-m14-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_m14_corrupt_ledger_fails_closed(self) -> None:
        identity_dir = (
            self.tmp / "ledgers" / _safe_component(REPO_IDENTITY)
        )
        identity_dir.mkdir(parents=True, exist_ok=True)
        path = identity_dir / f"{_safe_component(AUTH_ID)}{LEDGER_FILE_SUFFIX}"
        path.write_text("{ this is not valid JSON", encoding="utf-8")
        store = LedgerStore(state_root=self.tmp)
        with self.assertRaises(LedgerCorruptError):
            store.load(REPO_IDENTITY, AUTH_ID, AUTH_DIGEST)
        with self.assertRaises(LedgerCorruptError):
            store.find_by_id_digest(AUTH_ID, AUTH_DIGEST)


if __name__ == "__main__":
    unittest.main()