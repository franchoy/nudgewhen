"""Unit tests for the deterministic JSON-over-stdin operation dispatcher.

The tests cover the full stage / commit / push / verify_ci operation
flow with structured receipts, the hard-stop taxonomy, the
authorization-key contract, the local-HEAD and remote-SHA comparison
proof, the CI polling semantics, and the production module entrypoint.
Every test uses ``tempfile.TemporaryDirectory`` and either real
disposable Git repositories or injected ``ProcessResult`` runners so
no live network, no live ``gh``, no shell, and no worktree mutation
of the NudgeWhen project occurs.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from typing import Any

from scripts import nudge_land_cli as cli_mod
from scripts import nudge_land_ledger as ledger_mod
from scripts import nudge_land_runtime as runtime
from scripts.nudge_land_cli import (
    HARD_STOP_BAD_DIGEST,
    HARD_STOP_BASE_HEAD_MISMATCH,
    HARD_STOP_BRANCH_MISMATCH,
    HARD_STOP_CACHED_WHITESPACE,
    HARD_STOP_FINGERPRINT_MISMATCH,
    HARD_STOP_LEDGER_MISSING,
    HARD_STOP_MISSING_FIELDS,
    HARD_STOP_UNKNOWN_OPERATION,
    HARD_STOP_UNEXPECTED_DIRTY_PATH,
    OPERATION_COMMIT,
    OPERATION_PUSH,
    OPERATION_VERIFY_CI,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

REPO_IDENTITY = "github:octocat/hello"
REMOTE_URL = "https://github.com/octocat/hello.git"


def _git(cwd: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", cwd, *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=False,
    )


def _setup_empty_repo(cwd: str) -> None:
    _git(cwd, "init", "--initial-branch=main")
    _git(cwd, "config", "user.name", "Nudge Land Test")
    _git(cwd, "config", "user.email", "nudge-land@example.invalid")
    _git(cwd, "config", "commit.gpgsign", "false")
    _git(cwd, "config", "tag.gpgsign", "false")


def _commit(cwd: str, subject: str, files: dict[str, str]) -> str:
    for rel, content in files.items():
        path = pathlib.Path(cwd) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _git(cwd, "add", "--", *files.keys())
    res = _git(cwd, "commit", "-m", subject)
    if res.returncode != 0:
        raise RuntimeError(f"git commit failed: {res.stderr!r}")
    sha_res = _git(cwd, "rev-parse", "HEAD")
    return sha_res.stdout.decode("ascii").strip()


def _auth(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a deterministic authorization object."""
    auth: dict[str, Any] = {
        "authorization_version": "1",
        "authorization_id": "auth-001",
        "authorization_digest": "0" * 64,
        "authorized_branch": "release/v0.1.3",
        "authorized_base_head": "1" * 40,
        "authorized_paths": ["worktree_file.txt"],
        "expected_initial_status": [
            {"status": "WORKTREE_MODIFIED", "path": "worktree_file.txt"}
        ],
        "authorized_file_fingerprints": {
            "worktree_file.txt": "a" * 64,
        },
        "authorized_commit_subject": "feat: stage nudge-land runtime",
        "authorized_remote": "origin",
        "authorized_remote_repository": "github:octocat/hello",
        "authorized_push_branch": "release/v0.1.3",
        "expected_remote_base_sha": "2" * 40,
        "authorized_ci_workflow_or_check": "CI",
        "expected_ci_event": "push",
        "single_use": True,
    }
    if overrides:
        auth.update(overrides)
    auth["authorization_digest"] = runtime.compute_authorization_digest(auth)
    return auth


# ---------------------------------------------------------------------------
# N1-N7: stage operation
# ---------------------------------------------------------------------------


class TestStage(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-cli-n1-"))
        self.worktree = self.tmp / "work"
        self.worktree.mkdir()
        _setup_empty_repo(str(self.worktree))
        _git(str(self.worktree), "branch", "-m", "main", "release/v0.1.3")
        _git(str(self.worktree), "remote", "add", "origin", REMOTE_URL)
        _commit(str(self.worktree), "initial", {"worktree_file.txt": "a\n"})
        _commit(str(self.worktree), "second", {"other.txt": "o\n"})
        (self.worktree / "worktree_file.txt").write_text("b\n", encoding="utf-8")
        new_digest = hashlib.sha256(b"b\n").hexdigest()
        self.auth = _auth(
            overrides={
                "authorized_file_fingerprints": {"worktree_file.txt": new_digest},
                "authorized_base_head": _git(
                    str(self.worktree), "rev-parse", "HEAD"
                ).stdout.decode("ascii").strip(),
            }
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _store(self) -> ledger_mod.LedgerStore:
        return ledger_mod.LedgerStore(state_root=self.tmp / "state")

    def test_n1_stage_creates_s1_to_s4(self) -> None:
        store = self._store()
        receipt, exit_code = cli_mod.stage_op(
            str(self.worktree),
            self.auth,
            store=store,
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(receipt.last_verified_state, runtime.STEP_S4_STAGED)
        entry = store.find_by_id_digest(
            self.auth["authorization_id"],
            self.auth["authorization_digest"],
        )
        self.assertEqual(entry.verified_state, runtime.STEP_S4_STAGED)

    def test_n2_stage_rejects_unexpected_dirty_path(self) -> None:
        (self.worktree / "untracked_extra.txt").write_text(
            "x\n", encoding="utf-8"
        )
        store = self._store()
        receipt, _ = cli_mod.stage_op(
            str(self.worktree),
            self.auth,
            store=store,
        )
        self.assertEqual(receipt.hard_stop_reason, HARD_STOP_UNEXPECTED_DIRTY_PATH)

    def test_n3_stage_rejects_wrong_branch(self) -> None:
        # Detach HEAD so symbolic-ref fails.
        _git(str(self.worktree), "checkout", "--detach")
        store = self._store()
        receipt, _ = cli_mod.stage_op(
            str(self.worktree),
            self.auth,
            store=store,
        )
        self.assertEqual(receipt.hard_stop_reason, HARD_STOP_BRANCH_MISMATCH)

    def test_n4_stage_rejects_wrong_base_head(self) -> None:
        wrong_auth = _auth(
            overrides={
                "authorized_base_head": "f" * 40,
                "authorized_file_fingerprints": {
                    "worktree_file.txt": hashlib.sha256(b"b\n").hexdigest()
                },
            }
        )
        store = self._store()
        receipt, _ = cli_mod.stage_op(
            str(self.worktree),
            wrong_auth,
            store=store,
        )
        self.assertEqual(receipt.hard_stop_reason, HARD_STOP_BASE_HEAD_MISMATCH)

    def test_n5_stage_rejects_fingerprint_mismatch(self) -> None:
        wrong_auth = _auth(
            overrides={
                "authorized_base_head": _git(
                    str(self.worktree), "rev-parse", "HEAD"
                ).stdout.decode("ascii").strip(),
                "authorized_file_fingerprints": {
                    "worktree_file.txt": "f" * 64,
                },
            }
        )
        store = self._store()
        receipt, _ = cli_mod.stage_op(
            str(self.worktree),
            wrong_auth,
            store=store,
        )
        self.assertEqual(receipt.hard_stop_reason, HARD_STOP_FINGERPRINT_MISMATCH)

    def test_n7_stage_whitespace_finding(self) -> None:
        (self.worktree / "worktree_file.txt").write_text(
            "b    \n", encoding="utf-8"
        )
        new_digest = hashlib.sha256(b"b    \n").hexdigest()
        ws_auth = _auth(
            overrides={
                "authorized_base_head": _git(
                    str(self.worktree), "rev-parse", "HEAD"
                ).stdout.decode("ascii").strip(),
                "authorized_file_fingerprints": {"worktree_file.txt": new_digest},
            }
        )
        store = self._store()
        receipt, _ = cli_mod.stage_op(
            str(self.worktree),
            ws_auth,
            store=store,
        )
        self.assertEqual(receipt.hard_stop_reason, HARD_STOP_CACHED_WHITESPACE)


# ---------------------------------------------------------------------------
# N8, N9: commit input contract
# ---------------------------------------------------------------------------


class TestCommitInputContract(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-cli-n8-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _store(self) -> ledger_mod.LedgerStore:
        return ledger_mod.LedgerStore(state_root=self.tmp / "state")

    def test_n8_commit_rejects_extra_fields(self) -> None:
        store = self._store()
        receipt, _ = cli_mod.commit_op(
            "/tmp",
            {
                "authorization_id": "auth-001",
                "authorization_digest": "a" * 64,
                "authorized_branch": "release/v0.1.3",
            },
            store=store,
        )
        self.assertEqual(receipt.hard_stop_reason, HARD_STOP_MISSING_FIELDS)

    def test_n9_commit_loads_by_id_digest_only(self) -> None:
        store = self._store()
        receipt, _ = cli_mod.commit_op(
            "/tmp",
            {
                "authorization_id": "auth-001",
                "authorization_digest": "a" * 64,
            },
            store=store,
        )
        self.assertEqual(receipt.hard_stop_reason, HARD_STOP_LEDGER_MISSING)
        self.assertEqual(receipt.operation, OPERATION_COMMIT)


# ---------------------------------------------------------------------------
# N15: push input contract
# ---------------------------------------------------------------------------


class TestPushInputContract(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-cli-n15-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _store(self) -> ledger_mod.LedgerStore:
        return ledger_mod.LedgerStore(state_root=self.tmp / "state")

    def test_n15_push_rejects_extra_fields(self) -> None:
        store = self._store()
        receipt, _ = cli_mod.push_op(
            "/tmp",
            {
                "authorization_id": "auth-001",
                "authorization_digest": "a" * 64,
                "authorized_branch": "release/v0.1.3",
            },
            store=store,
        )
        self.assertEqual(receipt.hard_stop_reason, HARD_STOP_MISSING_FIELDS)

    def test_n15_push_loads_by_id_digest_only(self) -> None:
        store = self._store()
        receipt, _ = cli_mod.push_op(
            "/tmp",
            {
                "authorization_id": "auth-001",
                "authorization_digest": "a" * 64,
            },
            store=store,
        )
        self.assertEqual(receipt.hard_stop_reason, HARD_STOP_LEDGER_MISSING)
        self.assertEqual(receipt.operation, OPERATION_PUSH)


# ---------------------------------------------------------------------------
# N19-N22: verify_ci input contract
# ---------------------------------------------------------------------------


class TestVerifyCiInputContract(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-cli-n19-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _store(self) -> ledger_mod.LedgerStore:
        return ledger_mod.LedgerStore(state_root=self.tmp / "state")

    def test_n19_verify_ci_rejects_extra_fields(self) -> None:
        store = self._store()
        receipt, _ = cli_mod.verify_ci_op(
            "/tmp",
            {
                "authorization_id": "auth-001",
                "authorization_digest": "a" * 64,
                "authorized_branch": "release/v0.1.3",
            },
            store=store,
        )
        self.assertEqual(receipt.hard_stop_reason, HARD_STOP_MISSING_FIELDS)

    def test_n19_verify_ci_loads_by_id_digest_only(self) -> None:
        store = self._store()
        receipt, _ = cli_mod.verify_ci_op(
            "/tmp",
            {
                "authorization_id": "auth-001",
                "authorization_digest": "a" * 64,
            },
            store=store,
        )
        self.assertEqual(receipt.hard_stop_reason, HARD_STOP_LEDGER_MISSING)
        self.assertEqual(receipt.operation, OPERATION_VERIFY_CI)


# ---------------------------------------------------------------------------
# VerifyCI success integration: proves the LANDED/S10 entry persists with
# the landing_commit_sha already retained through the legal S6/PUSH/S8 path.
# ---------------------------------------------------------------------------


class TestVerifyCiSuccessIntegration(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(
            tempfile.mkdtemp(prefix="nudge-land-cli-verify-ci-success-")
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_verify_ci_success_persists_landed_with_retained_sha(self) -> None:
        store = ledger_mod.LedgerStore(state_root=self.tmp / "state")
        auth = _auth()
        auth_id = auth["authorization_id"]
        auth_digest = auth["authorization_digest"]
        landing_sha = "0123456789abcdef0123456789abcdef01234567"

        # Create the real S1 ledger entry with the full authorization context
        # supplied by _auth().
        store.create(
            repository_identity=REPO_IDENTITY,
            authorization_id=auth_id,
            authorization_digest=auth_digest,
            authorized_branch=auth["authorized_branch"],
            authorized_base_head=auth["authorized_base_head"],
            authorized_push_branch=auth["authorized_push_branch"],
            authorized_remote=auth["authorized_remote"],
            authorized_remote_repository=auth["authorized_remote_repository"],
            authorized_commit_subject=auth["authorized_commit_subject"],
            expected_remote_base_sha=auth["expected_remote_base_sha"],
            authorized_ci_workflow_or_check=auth[
                "authorized_ci_workflow_or_check"
            ],
            expected_ci_event=auth["expected_ci_event"],
            authorized_paths=list(auth["authorized_paths"]),
            authorized_file_fingerprints=dict(
                auth["authorized_file_fingerprints"]
            ),
            expected_initial_status=list(
                auth["expected_initial_status"]
            ),
        )

        # Establish ACTIVE / S8_PUSHED with the deterministic landing_commit_sha
        # retained through legal transitions:
        #   S1 -> MIP/STAGE -> S4 -> MIP/COMMIT -> S6 -> MIP/PUSH -> S8.
        with store.transaction(REPO_IDENTITY, auth_id) as tx:
            entry = tx.load(auth_digest)
            tx.advance(
                entry,
                new_state=ledger_mod.LEDGER_STATE_MUTATION_IN_PROGRESS,
                new_verified_state=runtime.STEP_S1_LEDGER_ACTIVE,
                mutation_intent=ledger_mod.MUTATION_INTENT_STAGE,
                mutation_in_progress_substate=(
                    runtime.MUTATION_IN_PROGRESS_SUBSTATE_STAGE
                ),
                notes="test: enter stage",
            )
            tx.advance(
                entry,
                new_state=ledger_mod.LEDGER_STATE_ACTIVE,
                new_verified_state=runtime.STEP_S4_STAGED,
                mutation_intent=None,
                mutation_in_progress_substate=None,
                notes="test: stage complete",
            )
            tx.advance(
                entry,
                new_state=ledger_mod.LEDGER_STATE_MUTATION_IN_PROGRESS,
                new_verified_state=runtime.STEP_S4_STAGED,
                mutation_intent=ledger_mod.MUTATION_INTENT_COMMIT,
                mutation_in_progress_substate=(
                    runtime.MUTATION_IN_PROGRESS_SUBSTATE_COMMIT
                ),
                notes="test: enter commit",
            )
            tx.advance(
                entry,
                new_state=ledger_mod.LEDGER_STATE_ACTIVE,
                new_verified_state=runtime.STEP_S6_COMMITTED,
                mutation_intent=None,
                mutation_in_progress_substate=None,
                landing_commit_sha=landing_sha,
                notes="test: commit complete",
            )
            tx.advance(
                entry,
                new_state=ledger_mod.LEDGER_STATE_MUTATION_IN_PROGRESS,
                new_verified_state=runtime.STEP_S6_COMMITTED,
                mutation_intent=ledger_mod.MUTATION_INTENT_PUSH,
                mutation_in_progress_substate=(
                    runtime.MUTATION_IN_PROGRESS_SUBSTATE_PUSH
                ),
                notes="test: enter push",
            )
            tx.advance(
                entry,
                new_state=ledger_mod.LEDGER_STATE_ACTIVE,
                new_verified_state=runtime.STEP_S8_PUSHED,
                mutation_intent=None,
                mutation_in_progress_substate=None,
                notes="test: push complete",
            )

        # Inject one successful authorized CI response matching the persisted
        # authority and the retained landing SHA. The injected response is a
        # GitHub-style JSON payload dictionary, not a CIResponse object.
        responses = [
            {
                "workflow_runs": [
                    {
                        "name": auth["authorized_ci_workflow_or_check"],
                        "head_sha": landing_sha,
                        "head_branch": auth["authorized_branch"],
                        "event": auth["expected_ci_event"],
                        "status": "completed",
                        "conclusion": "success",
                    }
                ]
            }
        ]

        receipt, exit_code = cli_mod.verify_ci_op(
            "/tmp",
            {
                "authorization_id": auth_id,
                "authorization_digest": auth_digest,
            },
            store=store,
            responses=responses,
            interval_seconds=0.0,
            sleep_fn=lambda _: None,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(receipt.last_verified_state, runtime.STEP_S10_LANDED)
        self.assertEqual(receipt.result_state, runtime.STEP_S10_LANDED)
        self.assertEqual(
            receipt.authorization_state, ledger_mod.LEDGER_STATE_LANDED
        )

        # Inspect durable terminal bytes directly (public load() must remain
        # fail-closed for terminal LANDED entries).
        ledger_path = store._ledger_path(REPO_IDENTITY, auth_id)
        payload = json.loads(ledger_path.read_text(encoding="utf-8"))
        durable_entry = ledger_mod.LedgerEntry.from_dict(payload)
        self.assertEqual(durable_entry.state, ledger_mod.LEDGER_STATE_LANDED)
        self.assertEqual(
            durable_entry.verified_state, runtime.STEP_S10_LANDED
        )
        self.assertEqual(durable_entry.landing_commit_sha, landing_sha)
        self.assertIsNone(durable_entry.mutation_intent)
        self.assertIsNone(durable_entry.mutation_in_progress_substate)

        # Public terminal-load semantics remain fail-closed.
        with self.assertRaises(ledger_mod.LedgerAuthorizationTerminalError):
            store.load(REPO_IDENTITY, auth_id, auth_digest)


# ---------------------------------------------------------------------------
# N25: unknown operation emits structured JSON
# ---------------------------------------------------------------------------


class TestUnknownOperation(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-cli-n25-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_n25_unknown_operation_returns_structured_receipt(self) -> None:
        store = ledger_mod.LedgerStore(state_root=self.tmp / "state")
        receipt, exit_code = cli_mod.run_dispatch(
            argv=["bogus_operation"],
            stdin_payload={"some": "data"},
            store=store,
        )
        self.assertEqual(exit_code, 65)
        self.assertEqual(receipt.hard_stop_reason, HARD_STOP_UNKNOWN_OPERATION)


# ---------------------------------------------------------------------------
# N26: production module entrypoint invokes main() and emits one JSON receipt
# ---------------------------------------------------------------------------


class TestModuleEntrypoint(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="nudge-land-cli-n26-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_n26_main_writes_one_json_receipt(self) -> None:
        state_root = self.tmp / "state"
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "scripts.nudge_land_cli",
                "--state-root",
                str(state_root),
                "bogus",
            ],
            cwd=str(REPO_ROOT),
            check=False,
            capture_output=True,
            input=b'{}',
        )
        out = result.stdout.decode("utf-8").strip()
        self.assertTrue(out.startswith("{"))
        receipt = json.loads(out)
        self.assertEqual(receipt["hard_stop_reason"], HARD_STOP_UNKNOWN_OPERATION)

    def test_n26_main_actually_invokable(self) -> None:
        # Direct invocation: call main() with an unknown operation.
        state_root = self.tmp / "state"
        # Patch stdin via input=b'{}' through subprocess so main()
        # receives valid JSON on stdin.
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                (
                    "import sys, io;"
                    "sys.stdin = io.TextIOWrapper(io.BytesIO(b'{}'));"
                    "from scripts.nudge_land_cli import main;"
                    "sys.exit(main(['--state-root', sys.argv[1], 'bogus']))"
                ),
                str(state_root),
            ],
            cwd=str(REPO_ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
        out = result.stdout.strip()
        self.assertTrue(out.startswith("{"))
        receipt = json.loads(out)
        self.assertEqual(receipt["hard_stop_reason"], HARD_STOP_UNKNOWN_OPERATION)


# ---------------------------------------------------------------------------
# N27: No prohibited patterns in CLI source
# ---------------------------------------------------------------------------


class TestNoProhibitedPatterns(unittest.TestCase):

    def test_n27_no_bash_sh_shell_true_in_cli(self) -> None:
        cli_path = REPO_ROOT / "scripts" / "nudge_land_cli.py"
        text = cli_path.read_text(encoding="utf-8")
        # Forbidden tokens.
        forbidden_substrings = [
            "shell=True",
            '"bash"',
            "'bash'",
            '"sh"',
            "'sh'",
        ]
        for token in forbidden_substrings:
            self.assertNotIn(
                token,
                text,
                f"CLI source contains forbidden token: {token!r}",
            )


if __name__ == "__main__":
    unittest.main()