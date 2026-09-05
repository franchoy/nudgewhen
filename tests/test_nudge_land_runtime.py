"""Unit tests for the deterministic Python landing runtime primitives.

The tests cover:

* canonical authorization serialization stability and digest mismatch
  detection;
* path normalization safety including traversal, absolute paths,
  duplicates, symlinks, parent-directory symlinks, and missing files;
* argument-vector subprocess runner semantics without shell, shell
  command strings, pipelines, or redirections;
* porcelain v2 status parsing for the supported subset and rejection
  of pre-staged, deleted, renamed, conflicted, mode-only, file-type,
  submodule, and intent-to-add entries;
* index / commit / HEAD proof primitives;
* GitHub HTTPS / SSH remote normalization;
* CI query parsing and timeout semantics.

The tests use ``tempfile.TemporaryDirectory`` for any disposable Git
repositories; the project worktree is never touched.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts import nudge_land_runtime as runtime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _hex(value: str, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(c in "0123456789abcdefABCDEF" for c in value)
    )


def _git(cwd: str, *args: str) -> subprocess.CompletedProcess:
    """Run a literal git command in ``cwd`` for fixture setup only."""
    return subprocess.run(
        ["git", "-C", cwd, *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=False,
    )


def _setup_empty_repo(cwd: str) -> None:
    """Initialize a fresh empty repository at ``cwd`` with deterministic identity."""
    _git(cwd, "init", "--initial-branch=main")
    _git(cwd, "config", "user.name", "Nudge Land Test")
    _git(cwd, "config", "user.email", "nudge-land@example.invalid")
    _git(cwd, "config", "commit.gpgsign", "false")
    _git(cwd, "config", "tag.gpgsign", "false")


def _commit(cwd: str, subject: str, files: dict[str, str]) -> str:
    """Commit ``files`` in ``cwd`` and return the new HEAD SHA."""
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


def _build_bare_remote(tmp_dir: str) -> str:
    """Create a local bare remote in ``tmp_dir`` and return its path."""
    bare_dir = pathlib.Path(tmp_dir) / "remote.git"
    bare_dir.mkdir(parents=True, exist_ok=True)
    _git(str(bare_dir.parent), "init", "--bare", str(bare_dir))
    return str(bare_dir)


# ---------------------------------------------------------------------------
# Authorization serialization
# ---------------------------------------------------------------------------


class TestCanonicalAuthorizationSerialization(unittest.TestCase):
    """The canonical serializer and digest are deterministic and self-consistent."""

    def _auth(self) -> dict[str, object]:
        return {
            "authorization_version": "1",
            "authorization_id": "auth-001",
            "authorization_digest": "0" * 64,
            "authorized_branch": "release/v0.1.3",
            "authorized_base_head": "1" * 40,
            "authorized_paths": ["scripts/nudge_land_runtime.py"],
            "expected_initial_status": [
                {
                    "status": "WORKTREE_MODIFIED",
                    "path": "scripts/nudge_land_runtime.py",
                }
            ],
            "authorized_file_fingerprints": {
                "scripts/nudge_land_runtime.py": "a" * 64,
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

    def test_canonical_serialization_stable(self) -> None:
        auth = self._auth()
        first = runtime.canonical_authorization_bytes(auth)
        second = runtime.canonical_authorization_bytes(auth)
        self.assertEqual(first, second)
        self.assertIsInstance(first, bytes)

    def test_digest_stable(self) -> None:
        auth = self._auth()
        first = runtime.compute_authorization_digest(auth)
        second = runtime.compute_authorization_digest(auth)
        self.assertEqual(first, second)
        self.assertTrue(_hex(first, 64))

    def test_digest_changes_when_payload_changes(self) -> None:
        auth_a = self._auth()
        auth_b = self._auth()
        auth_b["authorized_commit_subject"] = "feat: different subject"
        self.assertNotEqual(
            runtime.compute_authorization_digest(auth_a),
            runtime.compute_authorization_digest(auth_b),
        )

    def test_digest_excludes_authorization_digest_field(self) -> None:
        auth = self._auth()
        auth_a = dict(auth)
        auth_b = dict(auth)
        auth_b["authorization_digest"] = "f" * 64
        self.assertEqual(
            runtime.compute_authorization_digest(auth_a),
            runtime.compute_authorization_digest(auth_b),
        )

    def test_digest_mismatch_detected(self) -> None:
        auth = self._auth()
        auth["authorization_digest"] = "f" * 64
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.verify_authorization_digest(auth)

    def test_verify_authorization_digest_success(self) -> None:
        auth = self._auth()
        auth["authorization_digest"] = runtime.compute_authorization_digest(auth)
        runtime.verify_authorization_digest(auth)  # must not raise

    def test_canonical_bytes_use_utf8(self) -> None:
        auth = self._auth()
        auth["authorized_commit_subject"] = "feat: çhâine utf-8 ✨"
        payload = runtime.canonical_authorization_bytes(auth)
        self.assertIn("çhâine", payload.decode("utf-8"))

    def test_shape_validation_accepts_valid_authorization(self) -> None:
        auth = self._auth()
        auth["authorization_digest"] = runtime.compute_authorization_digest(auth)
        runtime.validate_authorization_shape(auth)  # must not raise

    def test_shape_validation_rejects_missing_field(self) -> None:
        auth = self._auth()
        del auth["authorized_commit_subject"]
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.validate_authorization_shape(auth)

    def test_shape_validation_rejects_absolute_path(self) -> None:
        auth = self._auth()
        auth["authorized_paths"] = ["/etc/passwd"]
        auth["authorized_file_fingerprints"] = {"/etc/passwd": "a" * 64}
        auth["expected_initial_status"] = [
            {"status": "WORKTREE_MODIFIED", "path": "/etc/passwd"}
        ]
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.validate_authorization_shape(auth)

    def test_shape_validation_rejects_traversal_path(self) -> None:
        auth = self._auth()
        auth["authorized_paths"] = ["scripts/../etc/passwd"]
        auth["authorized_file_fingerprints"] = {
            "scripts/../etc/passwd": "a" * 64
        }
        auth["expected_initial_status"] = [
            {"status": "WORKTREE_MODIFIED", "path": "scripts/../etc/passwd"}
        ]
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.validate_authorization_shape(auth)

    def test_shape_validation_rejects_non_canonical_path(self) -> None:
        auth = self._auth()
        auth["authorized_paths"] = ["a/./b"]
        auth["authorized_file_fingerprints"] = {"a/./b": "a" * 64}
        auth["expected_initial_status"] = [
            {"status": "WORKTREE_MODIFIED", "path": "a/./b"}
        ]
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.validate_authorization_shape(auth)

    def test_shape_validation_rejects_double_slash(self) -> None:
        auth = self._auth()
        auth["authorized_paths"] = ["a//b"]
        auth["authorized_file_fingerprints"] = {"a//b": "a" * 64}
        auth["expected_initial_status"] = [
            {"status": "WORKTREE_MODIFIED", "path": "a//b"}
        ]
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.validate_authorization_shape(auth)

    def test_shape_validation_rejects_backslash_path(self) -> None:
        auth = self._auth()
        auth["authorized_paths"] = ["a\\b"]
        auth["authorized_file_fingerprints"] = {"a\\b": "a" * 64}
        auth["expected_initial_status"] = [
            {"status": "WORKTREE_MODIFIED", "path": "a\\b"}
        ]
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.validate_authorization_shape(auth)

    def test_shape_validation_rejects_empty_paths(self) -> None:
        auth = self._auth()
        auth["authorized_paths"] = []
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.validate_authorization_shape(auth)

    def test_shape_validation_rejects_fingerprint_mismatch(self) -> None:
        auth = self._auth()
        auth["authorized_file_fingerprints"] = {"other.py": "a" * 64}
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.validate_authorization_shape(auth)

    def test_shape_validation_rejects_non_hex_fingerprint(self) -> None:
        auth = self._auth()
        auth["authorized_file_fingerprints"] = {
            "scripts/nudge_land_runtime.py": "not-hex"
        }
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.validate_authorization_shape(auth)

    def test_shape_validation_rejects_unsupported_status(self) -> None:
        auth = self._auth()
        auth["expected_initial_status"] = [
            {"status": "DELETED", "path": "scripts/nudge_land_runtime.py"}
        ]
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.validate_authorization_shape(auth)

    def test_shape_validation_rejects_single_use_false(self) -> None:
        auth = self._auth()
        auth["single_use"] = False
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.validate_authorization_shape(auth)

    def test_shape_validation_rejects_branch_push_branch_mismatch(self) -> None:
        auth = self._auth()
        auth["authorized_push_branch"] = "main"
        with self.assertRaises(runtime.NudgeLandAuthorizationError):
            runtime.validate_authorization_shape(auth)


# ---------------------------------------------------------------------------
# Path normalization and file fingerprint
# ---------------------------------------------------------------------------


class TestPathNormalization(unittest.TestCase):
    """Path normalization rejects every unsafe form."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="nudge-land-runtime-path-")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _worktree(self) -> str:
        return self.tmp

    def test_empty_path_rejected(self) -> None:
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.normalize_relative_path("", self._worktree(), must_exist=False)

    def test_absolute_posix_path_rejected(self) -> None:
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.normalize_relative_path("/etc/passwd", self._worktree(), must_exist=False)

    def test_absolute_windows_path_rejected(self) -> None:
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.normalize_relative_path(
                "C:\\Users\\test", self._worktree(), must_exist=False
            )

    def test_traversal_rejected(self) -> None:
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.normalize_relative_path(
                "../escape.txt", self._worktree(), must_exist=False
            )

    def test_nul_rejected(self) -> None:
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.normalize_relative_path(
                "ok\x00.txt", self._worktree(), must_exist=False
            )

    def test_duplicate_normalized_path_rejected(self) -> None:
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.assert_no_duplicate_normalized_paths(["a.txt", "a.txt"])

    def test_canonical_dot_segment_rejected(self) -> None:
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.canonical_path_string("a/./b")

    def test_canonical_double_slash_rejected(self) -> None:
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.canonical_path_string("a//b")

    def test_canonical_trailing_dot_rejected(self) -> None:
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.canonical_path_string("a/")

    def test_canonical_empty_segment_rejected(self) -> None:
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.canonical_path_string("a//b")

    def test_regular_file_accepted(self) -> None:
        path = pathlib.Path(self.tmp) / "file.txt"
        path.write_text("hello", encoding="utf-8")
        normalized = runtime.normalize_relative_path(
            "file.txt", self._worktree(), must_exist=True
        )
        self.assertEqual(normalized, "file.txt")

    def test_symlink_rejected(self) -> None:
        target = pathlib.Path(self.tmp) / "target.txt"
        target.write_text("hi", encoding="utf-8")
        link = pathlib.Path(self.tmp) / "link.txt"
        os.symlink(str(target), str(link))
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.normalize_relative_path(
                "link.txt", self._worktree(), must_exist=True
            )

    def test_symlink_traversal_rejected(self) -> None:
        outside = tempfile.mkdtemp(prefix="nudge-land-outside-")
        try:
            outside_file = pathlib.Path(outside) / "secret.txt"
            outside_file.write_text("secret", encoding="utf-8")
            link = pathlib.Path(self.tmp) / "escape.txt"
            os.symlink(str(outside_file), str(link))
            with self.assertRaises(runtime.NudgeLandPathError):
                runtime.normalize_relative_path(
                    "escape.txt", self._worktree(), must_exist=True
                )
        finally:
            shutil.rmtree(outside, ignore_errors=True)

    def test_parent_directory_symlink_rejected(self) -> None:
        outside = tempfile.mkdtemp(prefix="nudge-land-parent-symlink-")
        try:
            outside_file = pathlib.Path(outside) / "target.txt"
            outside_file.write_text("secret", encoding="utf-8")
            parent_link = pathlib.Path(self.tmp) / "parent"
            os.symlink(str(outside), str(parent_link))
            target = pathlib.Path(self.tmp) / "parent" / "target.txt"
            with self.assertRaises(runtime.NudgeLandPathError):
                runtime.normalize_relative_path(
                    "parent/target.txt", self._worktree(), must_exist=False
                )
        finally:
            shutil.rmtree(outside, ignore_errors=True)

    def test_directory_rejected(self) -> None:
        os.mkdir(pathlib.Path(self.tmp) / "subdir")
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.normalize_relative_path(
                "subdir", self._worktree(), must_exist=True
            )

    def test_missing_path_rejected_when_required(self) -> None:
        with self.assertRaises(runtime.NudgeLandPathError):
            runtime.normalize_relative_path(
                "missing.txt", self._worktree(), must_exist=True
            )

    def test_worktree_sha256_exact(self) -> None:
        content = "the quick brown fox"
        (pathlib.Path(self.tmp) / "data.txt").write_text(content, encoding="utf-8")
        sha = runtime.compute_file_sha256("data.txt", self._worktree())
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        self.assertEqual(sha, expected)

    def test_pathname_with_space_normalized(self) -> None:
        path = pathlib.Path(self.tmp) / "name with space.txt"
        path.write_text("hi", encoding="utf-8")
        normalized = runtime.normalize_relative_path(
            "name with space.txt", self._worktree(), must_exist=True
        )
        self.assertEqual(normalized, "name with space.txt")

    def test_pathname_with_tab_normalized(self) -> None:
        path = pathlib.Path(self.tmp) / "name\twith\ttab.txt"
        path.write_text("hi", encoding="utf-8")
        normalized = runtime.normalize_relative_path(
            "name\twith\ttab.txt", self._worktree(), must_exist=True
        )
        self.assertEqual(normalized, "name\twith\ttab.txt")

    def test_pathname_with_newline_normalized(self) -> None:
        path = pathlib.Path(self.tmp) / "name\nwith\nnewline.txt"
        path.write_text("hi", encoding="utf-8")
        normalized = runtime.normalize_relative_path(
            "name\nwith\nnewline.txt", self._worktree(), must_exist=True
        )
        self.assertEqual(normalized, "name\nwith\nnewline.txt")


# ---------------------------------------------------------------------------
# Process runner
# ---------------------------------------------------------------------------


class TestProcessRunner(unittest.TestCase):
    """The process runner is argument-vector safe and captures return code."""

    def test_runner_rejects_string_argv(self) -> None:
        with self.assertRaises(TypeError):
            runtime.run_process("echo hi", cwd=".")

    def test_runner_independent_stdout_stderr_capture(self) -> None:
        # ``sys.executable -c`` is a non-shell argv-form Python helper.
        # It writes distinct lines to stdout and stderr independently.
        code = (
            "import sys;"
            "sys.stdout.write('OUT');"
            "sys.stdout.flush();"
            "sys.stderr.write('ERR');"
            "sys.stderr.flush()"
        )
        result = runtime.run_process(
            [sys.executable, "-c", code],
            cwd=".",
        )
        self.assertEqual(result.stdout, b"OUT")
        self.assertEqual(result.stderr, b"ERR")
        self.assertEqual(result.returncode, 0)

    def test_runner_no_shell_metacharacter_interpretation(self) -> None:
        # If shell=True were ever used the chained ``;false`` would run.
        # The argv form passes the literal string verbatim to ``true``.
        result = runtime.run_process(["true", ";false"], cwd=".")
        self.assertEqual(result.returncode, 0)

    def test_runner_retains_numeric_return_code(self) -> None:
        result = runtime.run_process([sys.executable, "-c", "raise SystemExit(7)"], cwd=".")
        self.assertEqual(result.returncode, 7)

    def test_runner_argv_contract(self) -> None:
        result = runtime.run_process(["true"], cwd=".")
        self.assertEqual(result.argv, ("true",))


# ---------------------------------------------------------------------------
# Worktree status parsing
# ---------------------------------------------------------------------------


class TestWorktreeStatusParsing(unittest.TestCase):
    """Porcelain v2 parsing for the supported subset using real disposable repos."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="nudge-land-status-")
        _setup_empty_repo(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _commit(self, subject: str, files: dict[str, str]) -> str:
        return _commit(self.tmp, subject, files)

    def test_real_modified_tracked_parsed(self) -> None:
        self._commit("initial", {"a.txt": "a\n"})
        (pathlib.Path(self.tmp) / "a.txt").write_text("a2\n", encoding="utf-8")
        entries = runtime.capture_worktree_status(self.tmp)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].status, runtime.STATUS_WORKTREE_MODIFIED)
        self.assertEqual(entries[0].path, "a.txt")

    def test_real_untracked_new_parsed(self) -> None:
        self._commit("initial", {"a.txt": "a\n"})
        (pathlib.Path(self.tmp) / "new.txt").write_text("new\n", encoding="utf-8")
        entries = runtime.capture_worktree_status(self.tmp)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].status, runtime.STATUS_UNTRACKED_NEW)
        self.assertEqual(entries[0].path, "new.txt")

    def _record(self, xy: str, sub: str, path: str) -> bytes:
        # ``1 <XY> <sub> <mH> <mI> <mW> <hH> <hI> <path>\0``
        hH = b"0" * 40
        return (
            b"1 "
            + xy.encode("ascii")
            + b" "
            + sub.encode("ascii")
            + b" 100644 100644 100644 "
            + hH
            + b" "
            + hH
            + b" "
            + path.encode("utf-8")
            + b"\x00"
        )

    def test_synthetic_modified_tracked_parsed(self) -> None:
        payload = self._record(" M", "N...", "foo.txt")
        entries = runtime.parse_porcelain_v2_status(payload)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].status, runtime.STATUS_WORKTREE_MODIFIED)
        self.assertEqual(entries[0].path, "foo.txt")

    def test_synthetic_prestaged_rejected(self) -> None:
        payload = self._record("M.", "N...", "foo.txt")
        with self.assertRaises(runtime.NudgeLandStatusError):
            runtime.parse_porcelain_v2_status(payload)

    def test_synthetic_intent_to_add_rejected(self) -> None:
        # ``A.`` — added in the index, intent-to-add.
        payload = self._record("A.", "N...", "foo.txt")
        with self.assertRaises(runtime.NudgeLandStatusError):
            runtime.parse_porcelain_v2_status(payload)

    def test_deleted_rejected(self) -> None:
        payload = self._record(" D", "N...", "foo.txt")
        with self.assertRaises(runtime.NudgeLandStatusError):
            runtime.parse_porcelain_v2_status(payload)

    def test_index_delete_rejected(self) -> None:
        payload = self._record("D.", "N...", "foo.txt")
        with self.assertRaises(runtime.NudgeLandStatusError):
            runtime.parse_porcelain_v2_status(payload)

    def test_rename_rejected(self) -> None:
        payload = b"2 R. N 100 100\x00foo.txt\x00bar.txt\x00"
        with self.assertRaises(runtime.NudgeLandStatusError):
            runtime.parse_porcelain_v2_status(payload)

    def test_copy_rejected(self) -> None:
        payload = b"2 C. N 100 100\x00foo.txt\x00bar.txt\x00"
        with self.assertRaises(runtime.NudgeLandStatusError):
            runtime.parse_porcelain_v2_status(payload)

    def test_conflict_rejected(self) -> None:
        payload = b"u UU N 100 100 100 100 100 100 100 0\x00foo.txt\x00"
        with self.assertRaises(runtime.NudgeLandStatusError):
            runtime.parse_porcelain_v2_status(payload)

    def test_submodule_rejected(self) -> None:
        # Frozen porcelain-v2 submodule sub field is ``S<c><m><u>``;
        # we use ``S...`` to confirm the rejection explicitly.
        payload = self._record(" M", "S...", "sub")
        with self.assertRaises(runtime.NudgeLandStatusError):
            runtime.parse_porcelain_v2_status(payload)

    def test_file_type_change_rejected(self) -> None:
        payload = self._record(" T", "N...", "foo.txt")
        with self.assertRaises(runtime.NudgeLandStatusError):
            runtime.parse_porcelain_v2_status(payload)

    def test_mode_only_change_rejected(self) -> None:
        # Mode-only / unsupported Y column is rejected.
        payload = self._record(" A", "N...", "foo.txt")
        with self.assertRaises(runtime.NudgeLandStatusError):
            runtime.parse_porcelain_v2_status(payload)

    def test_unsupported_worktree_status_rejected(self) -> None:
        # ``.A`` would be an "added in worktree" which we don't accept.
        payload = self._record(" A", "N...", "foo.txt")
        with self.assertRaises(runtime.NudgeLandStatusError):
            runtime.parse_porcelain_v2_status(payload)


# ---------------------------------------------------------------------------
# Live disposable repository exercises
# ---------------------------------------------------------------------------


class TestDisposableRepoPrimitives(unittest.TestCase):
    """End-to-end primitives against a disposable Git repository."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="nudge-land-runtime-repo-")
        self.cwd = self.tmp
        _setup_empty_repo(self.cwd)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_capture_worktree_status_modified(self) -> None:
        head = _commit(self.cwd, "initial", {"README.md": "hi\n"})
        self.assertTrue(_hex(head, 40))
        (pathlib.Path(self.cwd) / "README.md").write_text("bye\n", encoding="utf-8")
        entries = runtime.capture_worktree_status(self.cwd)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].status, runtime.STATUS_WORKTREE_MODIFIED)
        self.assertEqual(entries[0].path, "README.md")

    def test_capture_worktree_status_untracked(self) -> None:
        _commit(self.cwd, "initial", {"README.md": "hi\n"})
        (pathlib.Path(self.cwd) / "new.txt").write_text("new\n", encoding="utf-8")
        entries = runtime.capture_worktree_status(self.cwd)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].status, runtime.STATUS_UNTRACKED_NEW)
        self.assertEqual(entries[0].path, "new.txt")

    def test_index_path_set_proof(self) -> None:
        _commit(self.cwd, "initial", {"a.txt": "a\n"})
        _commit(self.cwd, "second", {"b.txt": "b\n"})
        (pathlib.Path(self.cwd) / "a.txt").write_text("a2\n", encoding="utf-8")
        _git(self.cwd, "add", "--", "a.txt")
        cached = runtime.capture_index_path_set(self.cwd)
        self.assertEqual(cached, ("a.txt",))

    def test_index_status_set_proof(self) -> None:
        _commit(self.cwd, "initial", {"a.txt": "a\n"})
        _commit(self.cwd, "second", {"b.txt": "b\n"})
        (pathlib.Path(self.cwd) / "a.txt").write_text("a2\n", encoding="utf-8")
        _git(self.cwd, "add", "--", "a.txt")
        cached = runtime.capture_index_status_set(self.cwd)
        self.assertEqual(
            cached,
            (runtime.CachedIndexEntry(
                runtime.STATUS_CODE_WORKTREE_MODIFIED, "a.txt"
            ),),
        )

    def test_index_whitespace_finding_detected(self) -> None:
        _commit(self.cwd, "initial", {"a.txt": "ok\n"})
        (pathlib.Path(self.cwd) / "a.txt").write_text("ok    \n", encoding="utf-8")
        _git(self.cwd, "add", "--", "a.txt")
        verdict = runtime.capture_index_whitespace_verdict(self.cwd)
        self.assertEqual(verdict.state, runtime.WHITESPACE_FINDING)
        self.assertNotEqual(verdict.returncode, 0)
        self.assertTrue(verdict.stdout)
        self.assertEqual(verdict.stderr, b"")

    def test_index_whitespace_nonzero_finding_mapping(self) -> None:
        expected_cwd = self.cwd
        expected_argv = [
            "git",
            "-C",
            expected_cwd,
            "diff",
            "--cached",
            "--check",
        ]
        injected_stdout = b"a.txt:1: trailing whitespace.\n+ok    \n"
        injected_stderr = b""

        def _runner(argv_, cwd, stdin=None):
            self.assertEqual(argv_, expected_argv)
            self.assertEqual(cwd, expected_cwd)
            self.assertIsNone(stdin)
            return runtime.ProcessResult(
                argv=tuple(argv_),
                cwd=cwd,
                stdout=injected_stdout,
                stderr=injected_stderr,
                returncode=2,
            )

        verdict = runtime.capture_index_whitespace_verdict(
            expected_cwd,
            runner=_runner,
        )
        self.assertEqual(verdict.state, runtime.WHITESPACE_FINDING)
        self.assertEqual(verdict.returncode, 2)
        self.assertEqual(verdict.stdout, injected_stdout)
        self.assertEqual(verdict.stderr, b"")

    def test_index_whitespace_command_failure_mapping(self) -> None:
        expected_cwd = self.cwd
        expected_argv = [
            "git",
            "-C",
            expected_cwd,
            "diff",
            "--cached",
            "--check",
        ]
        injected_stdout = b""
        injected_stderr = b"fatal: .git/index: index file smaller than expected\n"

        def _runner(argv_, cwd, stdin=None):
            self.assertEqual(argv_, expected_argv)
            self.assertEqual(cwd, expected_cwd)
            self.assertIsNone(stdin)
            return runtime.ProcessResult(
                argv=tuple(argv_),
                cwd=cwd,
                stdout=injected_stdout,
                stderr=injected_stderr,
                returncode=128,
            )

        verdict = runtime.capture_index_whitespace_verdict(
            expected_cwd,
            runner=_runner,
        )
        self.assertEqual(verdict.state, runtime.WHITESPACE_GIT_COMMAND_FAILURE)
        self.assertEqual(verdict.returncode, 128)
        self.assertEqual(verdict.stdout, b"")
        self.assertEqual(verdict.stderr, injected_stderr)

    def test_index_whitespace_clean_detected(self) -> None:
        _commit(self.cwd, "initial", {"a.txt": "ok\n"})
        (pathlib.Path(self.cwd) / "a.txt").write_text("ok\n", encoding="utf-8")
        _git(self.cwd, "add", "--", "a.txt")
        verdict = runtime.capture_index_whitespace_verdict(self.cwd)
        self.assertEqual(verdict.state, runtime.WHITESPACE_CLEAN)
        self.assertEqual(verdict.returncode, 0)

    def test_index_raw_blob_fingerprint_exact(self) -> None:
        content = "the exact bytes\n"
        _commit(self.cwd, "initial", {"a.txt": content})
        (pathlib.Path(self.cwd) / "a.txt").write_text(content, encoding="utf-8")
        _git(self.cwd, "add", "--", "a.txt")
        sha = runtime.capture_index_blob_sha256(self.cwd, "a.txt")
        self.assertEqual(sha, hashlib.sha256(content.encode("utf-8")).hexdigest())

    def test_head_subject_proof_root_commit(self) -> None:
        _commit(self.cwd, "first commit", {"a.txt": "a\n"})
        head_sha = runtime.capture_head_sha(self.cwd)
        subject = runtime.capture_head_subject(self.cwd)
        self.assertTrue(_hex(head_sha, 40))
        self.assertEqual(subject, "first commit")

    def test_head_parent_subject_proof_with_two_commits(self) -> None:
        # HEAD must have a parent. Create a second commit so HEAD has
        # a verifiable parent.
        first = _commit(self.cwd, "first commit", {"a.txt": "a\n"})
        second = _commit(self.cwd, "second commit", {"b.txt": "b\n"})
        self.assertNotEqual(first, second)
        head_sha = runtime.capture_head_sha(self.cwd)
        parent_sha = runtime.capture_head_parent(self.cwd)
        subject = runtime.capture_head_subject(self.cwd)
        self.assertEqual(parent_sha, first)
        self.assertEqual(head_sha, second)
        self.assertEqual(subject, "second commit")

    def test_head_vs_parent_changed_paths_proof(self) -> None:
        _commit(self.cwd, "first commit", {"a.txt": "a\n"})
        _commit(self.cwd, "second commit", {"b.txt": "b\n"})
        changed = runtime.capture_head_changed_paths(self.cwd)
        self.assertEqual(
            changed,
            ((runtime.STATUS_CODE_UNTRACKED_NEW, "b.txt"),),
        )

    def test_head_raw_blob_fingerprint_exact(self) -> None:
        content = "head content\n"
        _commit(self.cwd, "first commit", {"a.txt": content})
        sha = runtime.capture_head_blob_sha256(self.cwd, "a.txt")
        self.assertEqual(sha, hashlib.sha256(content.encode("utf-8")).hexdigest())

    def test_post_commit_clean_proof(self) -> None:
        _commit(self.cwd, "first commit", {"a.txt": "a\n"})
        _commit(self.cwd, "second commit", {"b.txt": "b\n"})
        self.assertTrue(runtime.capture_worktree_is_clean(self.cwd))

    def test_post_commit_clean_false_when_dirty(self) -> None:
        _commit(self.cwd, "first commit", {"a.txt": "a\n"})
        (pathlib.Path(self.cwd) / "dirty.txt").write_text("d\n", encoding="utf-8")
        self.assertFalse(runtime.capture_worktree_is_clean(self.cwd))


# ---------------------------------------------------------------------------
# Remote destination normalization
# ---------------------------------------------------------------------------


class TestRemoteNormalization(unittest.TestCase):

    def test_https_https_with_git(self) -> None:
        identity = runtime.normalize_github_remote(
            "https://github.com/octocat/hello.git"
        )
        self.assertEqual(identity.as_string(), "github:octocat/hello")

    def test_https_without_git(self) -> None:
        identity = runtime.normalize_github_remote(
            "https://github.com/octocat/hello"
        )
        self.assertEqual(identity.as_string(), "github:octocat/hello")

    def test_ssh_with_git(self) -> None:
        identity = runtime.normalize_github_remote(
            "git@github.com:octocat/hello.git"
        )
        self.assertEqual(identity.as_string(), "github:octocat/hello")

    def test_ssh_without_git(self) -> None:
        identity = runtime.normalize_github_remote(
            "git@github.com:octocat/hello"
        )
        self.assertEqual(identity.as_string(), "github:octocat/hello")

    def test_wrong_host_rejected(self) -> None:
        with self.assertRaises(runtime.NudgeLandRemoteError):
            runtime.normalize_github_remote("https://gitlab.com/octocat/hello.git")

    def test_wrong_scheme_rejected(self) -> None:
        with self.assertRaises(runtime.NudgeLandRemoteError):
            runtime.normalize_github_remote("ssh://git@github.com/octocat/hello.git")

    def test_wrong_repository_distinguishable(self) -> None:
        a = runtime.normalize_github_remote(
            "https://github.com/octocat/hello.git"
        )
        b = runtime.normalize_github_remote(
            "https://github.com/octocat/world.git"
        )
        self.assertNotEqual(a.as_string(), b.as_string())

    def test_parse_canonical_repo(self) -> None:
        identity = runtime.parse_canonical_repo("github:octocat/hello")
        self.assertEqual(identity.owner, "octocat")
        self.assertEqual(identity.repo, "hello")
        self.assertEqual(identity.as_string(), "github:octocat/hello")

    def test_canonical_identity_for_remote_repository(self) -> None:
        identity = runtime.canonical_identity_for_remote_repository("octocat/hello")
        self.assertEqual(identity.as_string(), "github:octocat/hello")

    def test_canonical_identity_for_remote_repository_canonical(self) -> None:
        identity = runtime.canonical_identity_for_remote_repository(
            "github:octocat/hello"
        )
        self.assertEqual(identity.as_string(), "github:octocat/hello")


# ---------------------------------------------------------------------------
# Push-URL proof
# ---------------------------------------------------------------------------


class TestPushURLProof(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="nudge-land-pushurl-")
        self.cwd = self.tmp
        _setup_empty_repo(self.cwd)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_explicit_pushurl_returns_fetch_url(self) -> None:
        _git(self.cwd, "remote", "add", "origin", "https://github.com/octocat/hello.git")
        urls = runtime.capture_push_urls(self.cwd, "origin")
        self.assertEqual(urls, ["https://github.com/octocat/hello.git"])

    def test_one_explicit_pushurl_returns_only_that_url(self) -> None:
        _git(
            self.cwd,
            "remote",
            "add",
            "origin",
            "https://github.com/octocat/hello.git",
        )
        _git(
            self.cwd,
            "config",
            "--add",
            "remote.origin.pushurl",
            "https://github.com/octocat/pushonly.git",
        )
        urls = runtime.capture_push_urls(self.cwd, "origin")
        self.assertEqual(urls, ["https://github.com/octocat/pushonly.git"])

    def test_two_explicit_pushurls_returns_both(self) -> None:
        _git(self.cwd, "remote", "add", "origin", "https://github.com/octocat/hello.git")
        _git(
            self.cwd,
            "config",
            "--add",
            "remote.origin.pushurl",
            "https://github.com/octocat/world.git",
        )
        _git(
            self.cwd,
            "config",
            "--add",
            "remote.origin.pushurl",
            "https://github.com/octocat/zoo.git",
        )
        urls = runtime.capture_push_urls(self.cwd, "origin")
        self.assertEqual(
            urls,
            [
                "https://github.com/octocat/world.git",
                "https://github.com/octocat/zoo.git",
            ],
        )

    def test_multiple_distinct_push_destinations_rejected(self) -> None:
        _git(self.cwd, "remote", "add", "origin", "https://github.com/octocat/hello.git")
        _git(
            self.cwd,
            "config",
            "--add",
            "remote.origin.pushurl",
            "https://github.com/octocat/world.git",
        )
        with self.assertRaises(runtime.NudgeLandRemoteError):
            runtime.verify_remote_push_destination(
                self.cwd, "origin", "github:octocat/hello"
            )


# ---------------------------------------------------------------------------
# Remote branch SHA parsing
# ---------------------------------------------------------------------------


class TestRemoteBranchQuery(unittest.TestCase):

    def test_payload_parsing(self) -> None:
        payload = (
            b"abcdef0123456789abcdef0123456789abcdef01\trefs/heads/main\n"
        )
        sha = runtime.parse_ls_remote_branch_payload(payload, "main")
        self.assertEqual(sha, "abcdef0123456789abcdef0123456789abcdef01")

    def test_payload_parsing_wrong_branch_rejected(self) -> None:
        payload = b"abcdef0123456789abcdef0123456789abcdef01\trefs/heads/release/v0.1.3\n"
        with self.assertRaises(runtime.NudgeLandSubprocessError):
            runtime.parse_ls_remote_branch_payload(payload, "main")

    def test_argv_construction(self) -> None:
        argv = runtime.build_ls_remote_branch_argv("origin", "main")
        self.assertEqual(
            argv,
            ["git", "ls-remote", "origin", "refs/heads/main"],
        )


# ---------------------------------------------------------------------------
# CI query parsing
# ---------------------------------------------------------------------------


def _run_payload(name: str, *, head_sha: str, head_branch: str, event: str,
                 status: str, conclusion: str | None) -> dict:
    return {
        "name": name,
        "head_sha": head_sha,
        "head_branch": head_branch,
        "event": event,
        "status": status,
        "conclusion": conclusion,
    }


class TestCIQuery(unittest.TestCase):

    def _expected(self) -> runtime.CIQueryRequest:
        return runtime.CIQueryRequest(
            workflow="CI",
            head_sha="a" * 40,
            branch="release/v0.1.3",
            event="push",
        )

    def _payload(
        self,
        *,
        name: str = "CI",
        head_sha: str | None = None,
        head_branch: str | None = None,
        event: str | None = None,
        status: str = "completed",
        conclusion: str | None = "success",
    ) -> dict:
        return {
            "workflow_runs": [
                _run_payload(
                    name=name,
                    head_sha=head_sha or "a" * 40,
                    head_branch=head_branch or "release/v0.1.3",
                    event=event or "push",
                    status=status,
                    conclusion=conclusion,
                )
            ]
        }

    def test_success_accepted(self) -> None:
        verdict = runtime.evaluate_ci_response(self._payload(), self._expected())
        self.assertIsInstance(verdict, runtime.CIResponse)
        self.assertEqual(verdict.conclusion, "success")

    def test_wrong_sha_rejected(self) -> None:
        verdict = runtime.evaluate_ci_response(
            self._payload(head_sha="b" * 40), self._expected()
        )
        self.assertEqual(verdict, runtime.CI_REJECTED_WRONG_SHA)

    def test_wrong_branch_rejected(self) -> None:
        verdict = runtime.evaluate_ci_response(
            self._payload(head_branch="main"), self._expected()
        )
        self.assertEqual(verdict, runtime.CI_REJECTED_WRONG_BRANCH)

    def test_wrong_event_rejected(self) -> None:
        verdict = runtime.evaluate_ci_response(
            self._payload(event="pull_request"), self._expected()
        )
        self.assertEqual(verdict, runtime.CI_REJECTED_WRONG_EVENT)

    def test_failure_rejected(self) -> None:
        verdict = runtime.evaluate_ci_response(
            self._payload(conclusion="failure"), self._expected()
        )
        self.assertEqual(verdict, runtime.CI_REJECTED_FAILURE)

    def test_cancelled_rejected(self) -> None:
        verdict = runtime.evaluate_ci_response(
            self._payload(conclusion="cancelled"), self._expected()
        )
        self.assertEqual(verdict, runtime.CI_REJECTED_CANCELLED)

    def test_timed_out_rejected(self) -> None:
        verdict = runtime.evaluate_ci_response(
            self._payload(conclusion="timed_out"), self._expected()
        )
        self.assertEqual(verdict, runtime.CI_REJECTED_TIMED_OUT)

    def test_action_required_rejected(self) -> None:
        verdict = runtime.evaluate_ci_response(
            self._payload(conclusion="action_required"), self._expected()
        )
        self.assertEqual(verdict, runtime.CI_REJECTED_ACTION_REQUIRED)

    def test_in_progress_returns_in_progress(self) -> None:
        verdict = runtime.evaluate_ci_response(
            self._payload(status="in_progress", conclusion=None),
            self._expected(),
        )
        self.assertEqual(verdict, "in_progress")

    def test_poll_succeeds_after_queued_in_progress(self) -> None:
        responses = [
            self._payload(status="queued", conclusion=None),
            self._payload(status="in_progress", conclusion=None),
            self._payload(status="completed", conclusion="success"),
        ]
        verdict = runtime.poll_ci(
            remote_repo="github:octocat/hello",
            head_sha="a" * 40,
            expected=self._expected(),
            timeout_seconds=5.0,
            interval_seconds=0.0,
            responses=responses,
            sleep_fn=lambda _: None,
        )
        self.assertIsInstance(verdict, runtime.CIResponse)
        self.assertEqual(verdict.conclusion, "success")

    def test_poll_failure_rejected(self) -> None:
        responses = [self._payload(conclusion="failure")]
        verdict = runtime.poll_ci(
            remote_repo="github:octocat/hello",
            head_sha="a" * 40,
            expected=self._expected(),
            timeout_seconds=5.0,
            interval_seconds=0.0,
            responses=responses,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(verdict, runtime.CI_REJECTED_FAILURE)

    def test_poll_cancelled_rejected(self) -> None:
        responses = [self._payload(conclusion="cancelled")]
        verdict = runtime.poll_ci(
            remote_repo="github:octocat/hello",
            head_sha="a" * 40,
            expected=self._expected(),
            timeout_seconds=5.0,
            interval_seconds=0.0,
            responses=responses,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(verdict, runtime.CI_REJECTED_CANCELLED)

    def test_poll_timeout_deterministic(self) -> None:
        # timeout_seconds must satisfy the positive API precondition.
        # Advance an injected deterministic clock through fake sleep so
        # timeout behavior is tested without wall-clock sleeping.
        clock = [0.0]

        def advance_clock(seconds: float) -> None:
            clock[0] += seconds

        responses = [self._payload(status="queued", conclusion=None)]
        verdict = runtime.poll_ci(
            remote_repo="github:octocat/hello",
            head_sha="a" * 40,
            expected=self._expected(),
            timeout_seconds=0.001,
            interval_seconds=0.001,
            responses=responses,
            sleep_fn=advance_clock,
            clock_fn=lambda: clock[0],
        )
        self.assertEqual(
            verdict,
            runtime.CI_RESULT_NOT_ESTABLISHED_WITHIN_AUTHORIZED_TIMEOUT,
        )

    def test_poll_clock_advances_to_success(self) -> None:
        responses = [
            self._payload(status="queued", conclusion=None),
            self._payload(status="in_progress", conclusion=None),
            self._payload(status="completed", conclusion="success"),
        ]
        clock = [0.0]

        def tick(_seconds: float) -> None:
            clock[0] += 0.1

        verdict = runtime.poll_ci(
            remote_repo="github:octocat/hello",
            head_sha="a" * 40,
            expected=self._expected(),
            timeout_seconds=10.0,
            interval_seconds=0.05,
            responses=responses,
            sleep_fn=tick,
            clock_fn=lambda: clock[0],
        )
        self.assertIsInstance(verdict, runtime.CIResponse)


if __name__ == "__main__":
    unittest.main()
