"""Core regression tests for ``scripts.validate_local``.

Exercises the real validator functions in isolation. No validator
business logic is reimplemented. Python standard library only.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import tempfile
import unittest

from pathlib import Path

from scripts import validate_local
from tests import _helpers


_GROUPS: tuple[str, ...] = ("required", "docs", "android")
_ALL_ALIAS: str = "all"


def _make_args(**overrides: object) -> argparse.Namespace:
    """Build a synthetic ``argparse.Namespace`` compatible with the validator."""
    base: dict[str, object] = {
        "group": None,
        "skip_android": False,
        "offline": False,
        "fail_fast": False,
        "require_clean": False,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


class ImportAndAPITests(unittest.TestCase):
    """The real validator must expose the callable symbols these tests use."""

    def test_parse_args_is_callable(self) -> None:
        self.assertTrue(callable(validate_local.parse_args))

    def test_resolve_groups_is_callable(self) -> None:
        self.assertTrue(callable(validate_local.resolve_groups))

    def test_print_summary_and_gate_is_callable(self) -> None:
        self.assertTrue(callable(validate_local.print_summary_and_gate))

    def test_main_is_callable(self) -> None:
        self.assertTrue(callable(validate_local.main))


class ArgumentParsingTests(unittest.TestCase):
    """``parse_args`` must honour every supported flag in the contract."""

    def test_default_invocation(self) -> None:
        args = validate_local.parse_args([], _GROUPS, _ALL_ALIAS)
        self.assertIsNone(args.group)
        self.assertFalse(args.skip_android)
        self.assertFalse(args.offline)
        self.assertFalse(args.fail_fast)
        self.assertFalse(args.require_clean)

    def test_repeated_group(self) -> None:
        args = validate_local.parse_args(
            ["--group", "required", "--group", "docs"], _GROUPS, _ALL_ALIAS
        )
        self.assertEqual(args.group, ["required", "docs"])

    def test_skip_android_flag(self) -> None:
        args = validate_local.parse_args(["--skip-android"], _GROUPS, _ALL_ALIAS)
        self.assertTrue(args.skip_android)

    def test_offline_flag(self) -> None:
        args = validate_local.parse_args(["--offline"], _GROUPS, _ALL_ALIAS)
        self.assertTrue(args.offline)

    def test_fail_fast_flag(self) -> None:
        args = validate_local.parse_args(["--fail-fast"], _GROUPS, _ALL_ALIAS)
        self.assertTrue(args.fail_fast)

    def test_require_clean_flag(self) -> None:
        args = validate_local.parse_args(["--require-clean"], _GROUPS, _ALL_ALIAS)
        self.assertTrue(args.require_clean)

    def test_unknown_group_choice_raises_systemexit_two(self) -> None:
        """``parse_args`` must raise ``SystemExit(2)`` and emit
        ``invalid choice`` to stderr when given an unknown ``--group``
        value. This is argparse invocation behaviour, not a validator
        ``main()`` return code."""
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as cm:
                validate_local.parse_args(
                    ["--group", "unknown"], _GROUPS, _ALL_ALIAS
                )
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("invalid choice", err.getvalue())


class GroupResolutionTests(unittest.TestCase):
    """``resolve_groups`` must produce the correct selection tuple."""

    def test_default_group_order(self) -> None:
        args = _make_args()
        self.assertEqual(
            validate_local.resolve_groups(args, _GROUPS, _ALL_ALIAS),
            _GROUPS,
        )

    def test_all_alias_expansion(self) -> None:
        args = _make_args(group=[_ALL_ALIAS])
        self.assertEqual(
            validate_local.resolve_groups(args, _GROUPS, _ALL_ALIAS),
            _GROUPS,
        )

    def test_first_seen_dedup(self) -> None:
        args = _make_args(group=["required", "docs", "required"])
        self.assertEqual(
            validate_local.resolve_groups(args, _GROUPS, _ALL_ALIAS),
            ("required", "docs"),
        )

    def test_explicit_and_all_overlap(self) -> None:
        args = _make_args(group=["required", _ALL_ALIAS])
        self.assertEqual(
            validate_local.resolve_groups(args, _GROUPS, _ALL_ALIAS),
            _GROUPS,
        )

    def test_default_with_skip_android(self) -> None:
        args = _make_args(skip_android=True)
        self.assertEqual(
            validate_local.resolve_groups(args, _GROUPS, _ALL_ALIAS),
            ("required", "docs"),
        )

    def test_all_with_skip_android(self) -> None:
        args = _make_args(group=[_ALL_ALIAS], skip_android=True)
        self.assertEqual(
            validate_local.resolve_groups(args, _GROUPS, _ALL_ALIAS),
            ("required", "docs"),
        )

    def test_explicit_android_with_skip_android_conflict(self) -> None:
        args = _make_args(group=["android"], skip_android=True)
        with _helpers.capture_stdout_stderr() as (_, err):
            result = validate_local.resolve_groups(args, _GROUPS, _ALL_ALIAS)
        self.assertEqual(result, 2)
        self.assertIn(
            "FAIL invocation \u2014 --skip-android combined with explicit --group android",
            err.getvalue(),
        )


class ReleaseGateCalculationTests(unittest.TestCase):
    """``print_summary_and_gate`` must produce the contract's gate literal."""

    def setUp(self) -> None:
        self._saved = _helpers.save_validator_state()
        _helpers.reset_validator_state()

    def tearDown(self) -> None:
        _helpers.restore_validator_state(self._saved)

    def test_full_selection_no_failures_android_present_satisfied(self) -> None:
        validate_local.emit("PASS", "required", "files", "ok")
        validate_local.emit("PASS", "docs", "files", "ok")
        validate_local.emit("PASS", "android", "files", "ok")
        args = _make_args()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            validate_local.print_summary_and_gate(
                args,
                _GROUPS,
                ("required", "docs", "android"),
                True,
            )
        rendered = out.getvalue()
        self.assertIn("SUMMARY pass=3 fail=0 skip=0", rendered)
        self.assertIn("release_gate=SATISFIED", rendered)

    def test_partial_selection_with_no_failures_not_satisfied(self) -> None:
        validate_local.emit("PASS", "required", "files", "ok")
        args = _make_args()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            validate_local.print_summary_and_gate(
                args,
                ("required",),
                ("required", "docs", "android"),
                True,
            )
        rendered = out.getvalue()
        self.assertIn("SUMMARY pass=1 fail=0 skip=0", rendered)
        self.assertIn("release_gate=NOT_SATISFIED", rendered)

    def test_full_selection_with_one_failure_not_satisfied(self) -> None:
        validate_local.emit("PASS", "required", "files", "ok")
        validate_local.emit("FAIL", "docs", "x", "broken")
        validate_local.emit("PASS", "android", "y", "ok")
        args = _make_args()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            validate_local.print_summary_and_gate(
                args,
                _GROUPS,
                ("required", "docs", "android"),
                True,
            )
        rendered = out.getvalue()
        self.assertIn("SUMMARY pass=2 fail=1 skip=0", rendered)
        self.assertIn("release_gate=NOT_SATISFIED", rendered)

    def test_android_required_but_skipped_not_satisfied(self) -> None:
        validate_local.emit("PASS", "required", "files", "ok")
        validate_local.emit("PASS", "docs", "files", "ok")
        args = _make_args(skip_android=True)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            validate_local.print_summary_and_gate(
                args,
                ("required", "docs"),
                ("required", "docs", "android"),
                True,
            )
        rendered = out.getvalue()
        self.assertIn("release_gate=NOT_SATISFIED", rendered)


class MainExitSemanticsTests(unittest.TestCase):
    """Exercise the real ``main()`` with controlled dependencies.

    Every test in this class patches the validator's ``get_release_contract``,
    ``check_git_prerequisite``, ``check_git_worktree_prerequisite`` and
    controlled entries of the ``VALIDATION_HANDLERS`` registry as the
    specific scenario under test requires. The originals are restored in
    ``tearDown`` even when an assertion fails. The validator business
    logic is never reimplemented.
    """

    def setUp(self) -> None:
        self._saved_state = _helpers.save_validator_state()
        self._saved_handlers = _helpers.save_validation_handlers()
        _helpers.reset_validator_state()
        _helpers.reset_validation_handlers_to_real()

    def tearDown(self) -> None:
        _helpers.restore_validation_handlers(self._saved_handlers)
        _helpers.restore_validator_state(self._saved_state)

    def test_main_returns_zero_on_synthetic_required_pass(self) -> None:
        """All required dependencies pass; ``main`` must return 0 and the
        summary must record zero failures, with the release gate still
        ``NOT_SATISFIED`` because only the required group was selected."""
        contract = _helpers.build_minimal_validation_contract()
        original_required_handler = validate_local.VALIDATION_HANDLERS["required"]

        def controlled_pass_handler(args: argparse.Namespace) -> bool:
            validate_local.emit("PASS", "required", "synthetic", "controlled pass")
            return True

        validate_local.VALIDATION_HANDLERS["required"] = controlled_pass_handler
        try:
            with _helpers.patched_module_attribute(
                "get_release_contract", lambda: contract
            ), _helpers.patched_module_attribute(
                "check_git_prerequisite", lambda: True
            ), _helpers.patched_module_attribute(
                "check_git_worktree_prerequisite", lambda: True
            ), _helpers.capture_stdout_stderr() as (out, _):
                rc = validate_local.main(["--group", "required"])
        finally:
            validate_local.VALIDATION_HANDLERS["required"] = original_required_handler

        rendered = out.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("SUMMARY pass=1 fail=0 skip=0", rendered)
        self.assertIn("release_gate=NOT_SATISFIED", rendered)

    def test_main_returns_one_on_synthetic_required_fail(self) -> None:
        """A controlled required handler that fails must propagate as a
        return value of 1, with ``fail=1`` in the summary and the release
        gate remaining ``NOT_SATISFIED``."""
        contract = _helpers.build_minimal_validation_contract()
        original_required_handler = validate_local.VALIDATION_HANDLERS["required"]

        def controlled_fail_handler(args: argparse.Namespace) -> bool:
            validate_local.emit("FAIL", "required", "synthetic", "controlled fail")
            return False

        validate_local.VALIDATION_HANDLERS["required"] = controlled_fail_handler
        try:
            with _helpers.patched_module_attribute(
                "get_release_contract", lambda: contract
            ), _helpers.patched_module_attribute(
                "check_git_prerequisite", lambda: True
            ), _helpers.patched_module_attribute(
                "check_git_worktree_prerequisite", lambda: True
            ), _helpers.capture_stdout_stderr() as (out, _):
                rc = validate_local.main(["--group", "required"])
        finally:
            validate_local.VALIDATION_HANDLERS["required"] = original_required_handler

        rendered = out.getvalue()
        self.assertEqual(rc, 1)
        self.assertIn("SUMMARY pass=0 fail=1 skip=0", rendered)
        self.assertIn("release_gate=NOT_SATISFIED", rendered)

    def test_main_invocation_conflict_returns_two(self) -> None:
        """The real ``parse_args`` and ``resolve_groups`` must execute and
        ``main`` must return 2 with the exact conflict line on stderr when
        ``--group android`` is combined with ``--skip-android``. The Git
        prerequisite and the Android validation handler must never be
        reached; if the Android handler is invoked the test fails
        immediately."""
        contract = _helpers.build_minimal_validation_contract()
        prereq_called = {"git": 0, "worktree": 0}

        def failing_git_prereq() -> bool:
            prereq_called["git"] += 1
            return True

        def failing_worktree_prereq() -> bool:
            prereq_called["worktree"] += 1
            return True

        def fail_if_called_android_handler(args: argparse.Namespace) -> bool:
            self.fail(
                "Android validation handler must not be invoked when "
                "--skip-android is combined with --group android"
            )
            return False  # pragma: no cover - unreachable

        original_android_handler = validate_local.VALIDATION_HANDLERS["android"]
        validate_local.VALIDATION_HANDLERS["android"] = fail_if_called_android_handler
        try:
            with _helpers.patched_module_attribute(
                "get_release_contract", lambda: contract
            ), _helpers.patched_module_attribute(
                "check_git_prerequisite", failing_git_prereq
            ), _helpers.patched_module_attribute(
                "check_git_worktree_prerequisite", failing_worktree_prereq
            ), _helpers.capture_stdout_stderr() as (_, err):
                rc = validate_local.main(["--group", "android", "--skip-android"])
        finally:
            validate_local.VALIDATION_HANDLERS["android"] = original_android_handler

        self.assertEqual(rc, 2)
        self.assertIn(
            "FAIL invocation \u2014 --skip-android combined with explicit --group android",
            err.getvalue(),
        )
        self.assertEqual(prereq_called["git"], 0)
        self.assertEqual(prereq_called["worktree"], 0)

    def test_main_require_clean_dirty_pre_state_returns_one(self) -> None:
        """With a non-empty pre-state and ``--require-clean`` set, ``main``
        must return 1 and emit the pre-state FAIL line. The required
        validation handler must never be invoked."""
        contract = _helpers.build_minimal_validation_contract()
        required_called = {"n": 0}

        def fail_if_called_required_handler(args: argparse.Namespace) -> bool:
            required_called["n"] += 1
            self.fail(
                "Required validation handler must not be invoked when "
                "--require-clean is set and the pre-state is dirty"
            )
            return False  # pragma: no cover - unreachable

        original_required_handler = validate_local.VALIDATION_HANDLERS["required"]
        validate_local.VALIDATION_HANDLERS["required"] = fail_if_called_required_handler
        try:
            with _helpers.patched_module_attribute(
                "get_release_contract", lambda: contract
            ), _helpers.patched_module_attribute(
                "check_git_prerequisite", lambda: True
            ), _helpers.patched_module_attribute(
                "check_git_worktree_prerequisite", lambda: True
            ), _helpers.patched_module_attribute(
                "git_status_short",
                lambda: " M scripts/validate_local.py\n",
            ), _helpers.capture_stdout_stderr() as (out, _):
                rc = validate_local.main(
                    ["--group", "required", "--require-clean"]
                )
        finally:
            validate_local.VALIDATION_HANDLERS[
                "required"
            ] = original_required_handler

        rendered = out.getvalue()
        self.assertEqual(rc, 1)
        self.assertIn(
            "FAIL required/clean-state \u2014 non-ignored uncommitted changes present",
            rendered,
        )
        self.assertIn("SUMMARY pass=0 fail=1 skip=0", rendered)
        self.assertIn("release_gate=NOT_SATISFIED", rendered)
        self.assertEqual(required_called["n"], 0)

    def test_main_require_clean_post_validation_residue_returns_one(self) -> None:
        """When the pre-state is clean but the post-validation state is
        dirty, ``main`` must return 1 with both the pre-state PASS line
        and the post-validation FAIL line on stdout. The required handler
        must be invoked exactly once and ``git_status_short`` must be
        called exactly twice."""
        contract = _helpers.build_minimal_validation_contract()
        required_called = {"n": 0}
        status_calls = {"n": 0}

        def status_short_side_effect() -> str:
            status_calls["n"] += 1
            if status_calls["n"] == 1:
                return ""
            return " M scripts/validate_local.py\n"

        def controlled_required_handler(args: argparse.Namespace) -> bool:
            required_called["n"] += 1
            validate_local.emit(
                "PASS", "required", "synthetic", "controlled pass"
            )
            return True

        original_required_handler = validate_local.VALIDATION_HANDLERS["required"]
        validate_local.VALIDATION_HANDLERS["required"] = controlled_required_handler
        try:
            with _helpers.patched_module_attribute(
                "get_release_contract", lambda: contract
            ), _helpers.patched_module_attribute(
                "check_git_prerequisite", lambda: True
            ), _helpers.patched_module_attribute(
                "check_git_worktree_prerequisite", lambda: True
            ), _helpers.patched_module_attribute(
                "git_status_short", status_short_side_effect
            ), _helpers.capture_stdout_stderr() as (out, _):
                rc = validate_local.main(
                    ["--group", "required", "--require-clean"]
                )
        finally:
            validate_local.VALIDATION_HANDLERS[
                "required"
            ] = original_required_handler

        rendered = out.getvalue()
        self.assertEqual(rc, 1)
        self.assertEqual(required_called["n"], 1)
        self.assertEqual(status_calls["n"], 2)
        self.assertIn(
            "PASS required/clean-state \u2014 non-ignored state clean before validation",
            rendered,
        )
        self.assertIn(
            "FAIL required/clean-state \u2014 validation produced non-ignored changes",
            rendered,
        )
        self.assertIn("release_gate=NOT_SATISFIED", rendered)


class TrackedBytecodeRejectionTests(unittest.TestCase):
    """``check_required`` must reject tracked Python bytecode/cache-output
    paths through the real ``required/no-bytecode`` branch. A tracked path
    is treated as bytecode/cache output when its basename ends in
    ``.pyc``, ``.pyo``, or ``.pyd`` or when one of its Git path
    components is exactly ``__pycache__``. Because ``fail_fast`` is true,
    the real checker must stop immediately after this rejection and the
    wrapper, ``.gitignore``, and ``.gitattributes`` fixtures must never
    be reached. The validator's own ``REQUIRED_FILES``, ``git_ls_files``
    and ``check_release_contract`` are temporarily patched, and every
    patched object is restored even when an assertion fails. The four
    tests collectively cover the four bytecode/cache-output
    classifications, including the ``pkg/__pycache__/marker.txt`` case
    in which the basename has no bytecode extension but the path
    contains a ``__pycache__`` path component."""

    def test_tracked_pyc_is_rejected_with_required_no_bytecode_line(self) -> None:
        with _helpers.patched_module_attribute(
            "REQUIRED_FILES", ()
        ), _helpers.patched_module_attribute(
            "git_ls_files", lambda: ["bad.pyc"]
        ), _helpers.patched_module_attribute(
            "check_release_contract", lambda *a, **k: True
        ):
            args = _make_args(fail_fast=True, require_clean=False)
            with _helpers.capture_stdout_stderr() as (out, _):
                result = validate_local.check_required(args, True)
        self.assertFalse(result)
        self.assertIn(
            "FAIL required/no-bytecode \u2014 tracked bytecode: bad.pyc",
            out.getvalue(),
        )

    def test_tracked_pyo_is_rejected_with_required_no_bytecode_line(self) -> None:
        with _helpers.patched_module_attribute(
            "REQUIRED_FILES", ()
        ), _helpers.patched_module_attribute(
            "git_ls_files", lambda: ["bad.pyo"]
        ), _helpers.patched_module_attribute(
            "check_release_contract", lambda *a, **k: True
        ):
            args = _make_args(fail_fast=True, require_clean=False)
            with _helpers.capture_stdout_stderr() as (out, _):
                result = validate_local.check_required(args, True)
        self.assertFalse(result)
        self.assertIn(
            "FAIL required/no-bytecode \u2014 tracked bytecode: bad.pyo",
            out.getvalue(),
        )

    def test_tracked_pyd_is_rejected_with_required_no_bytecode_line(self) -> None:
        with _helpers.patched_module_attribute(
            "REQUIRED_FILES", ()
        ), _helpers.patched_module_attribute(
            "git_ls_files", lambda: ["bad.pyd"]
        ), _helpers.patched_module_attribute(
            "check_release_contract", lambda *a, **k: True
        ):
            args = _make_args(fail_fast=True, require_clean=False)
            with _helpers.capture_stdout_stderr() as (out, _):
                result = validate_local.check_required(args, True)
        self.assertFalse(result)
        self.assertIn(
            "FAIL required/no-bytecode \u2014 tracked bytecode: bad.pyd",
            out.getvalue(),
        )

    def test_tracked_pycache_component_is_rejected_with_required_no_bytecode_line(
        self,
    ) -> None:
        with _helpers.patched_module_attribute(
            "REQUIRED_FILES", ()
        ), _helpers.patched_module_attribute(
            "git_ls_files", lambda: ["pkg/__pycache__/marker.txt"]
        ), _helpers.patched_module_attribute(
            "check_release_contract", lambda *a, **k: True
        ):
            args = _make_args(fail_fast=True, require_clean=False)
            with _helpers.capture_stdout_stderr() as (out, _):
                result = validate_local.check_required(args, True)
        self.assertFalse(result)
        self.assertIn(
            "FAIL required/no-bytecode \u2014 tracked bytecode: pkg/__pycache__/marker.txt",
            out.getvalue(),
        )


class GitignorePythonRulesTests(unittest.TestCase):
    """``check_required`` must verify the ``GITIGNORE_PYTHON_REQUIRED``
    rules through the real ``required/gitignore-python`` branch.

    Test 1 creates a controlled temporary directory containing a
    ``.gitignore`` that includes every ``GITIGNORE_REQUIRED`` rule plus
    the two ``GITIGNORE_PYTHON_REQUIRED`` rules. Patching ``REPO``,
    ``REQUIRED_FILES``, ``git_ls_files`` and ``check_release_contract``
    through ``_helpers.patched_module_attribute`` confines the test to
    the bounded invariant, the originals are restored even when an
    assertion fails, and the real validator must emit the exact
    ``PASS required/gitignore-python \u2014 Python bytecode ignore rules
    present`` line.

    Test 2 creates a controlled temporary directory containing a
    ``.gitignore`` that includes every ``GITIGNORE_REQUIRED`` rule plus
    only one of the two ``GITIGNORE_PYTHON_REQUIRED`` rules. The real
    validator must emit the exact
    ``FAIL required/gitignore-python \u2014 missing rules: *.py[cod]``
    line, naming exactly the missing rule."""

    def test_both_required_python_ignore_rules_emit_pass_required_gitignore_python(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            gi_path = tmp_root / ".gitignore"
            gi_path.write_text(
                "build/\n"
                "local.properties\n"
                "*.apk\n"
                "*.aab\n"
                "*.jks\n"
                "*.keystore\n"
                "session-ses_*.md\n"
                "__pycache__/\n"
                "*.py[cod]\n",
                encoding="utf-8",
            )
            with _helpers.patched_module_attribute(
                "REPO", tmp_root
            ), _helpers.patched_module_attribute(
                "REQUIRED_FILES", ()
            ), _helpers.patched_module_attribute(
                "git_ls_files", lambda: []
            ), _helpers.patched_module_attribute(
                "check_release_contract", lambda *a, **k: True
            ):
                args = _make_args(fail_fast=False, require_clean=False)
                with _helpers.capture_stdout_stderr() as (out, _):
                    validate_local.check_required(args, False)
        self.assertIn(
            "PASS required/gitignore-python \u2014 Python bytecode ignore rules present",
            out.getvalue(),
        )

    def test_missing_one_required_python_ignore_rule_emits_fail_required_gitignore_python(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            gi_path = tmp_root / ".gitignore"
            gi_path.write_text(
                "build/\n"
                "local.properties\n"
                "*.apk\n"
                "*.aab\n"
                "*.jks\n"
                "*.keystore\n"
                "session-ses_*.md\n"
                "__pycache__/\n",
                encoding="utf-8",
            )
            with _helpers.patched_module_attribute(
                "REPO", tmp_root
            ), _helpers.patched_module_attribute(
                "REQUIRED_FILES", ()
            ), _helpers.patched_module_attribute(
                "git_ls_files", lambda: []
            ), _helpers.patched_module_attribute(
                "check_release_contract", lambda *a, **k: True
            ):
                args = _make_args(fail_fast=False, require_clean=False)
                with _helpers.capture_stdout_stderr() as (out, _):
                    result = validate_local.check_required(args, False)
        self.assertFalse(result)
        self.assertIn(
            "FAIL required/gitignore-python \u2014 missing rules: *.py[cod]",
            out.getvalue(),
        )


class TrackedProhibitedBuildOutputRejectionTests(unittest.TestCase):
    """``check_required`` must reject tracked paths under the real
    ``PROHIBITED_TRACKED_PREFIXES`` through the real
    ``required/no-build-output`` branch. Because ``fail_fast`` is true,
    the real checker must stop immediately after this rejection and the
    wrapper, ``.gitignore``, and ``.gitattributes`` fixtures must never
    be reached. The validator's own ``REQUIRED_FILES``, ``git_ls_files``
    and ``check_release_contract`` are temporarily patched, and every
    patched object is restored even when an assertion fails."""

    def test_tracked_build_output_is_rejected_with_required_no_build_output_line(
        self,
    ) -> None:
        with _helpers.patched_module_attribute(
            "REQUIRED_FILES", ()
        ), _helpers.patched_module_attribute(
            "git_ls_files", lambda: ["app/build/generated.txt"]
        ), _helpers.patched_module_attribute(
            "check_release_contract", lambda *a, **k: True
        ):
            args = _make_args(fail_fast=True, require_clean=False)
            with _helpers.capture_stdout_stderr() as (out, _):
                result = validate_local.check_required(args, True)
        self.assertFalse(result)
        self.assertIn(
            "FAIL required/no-build-output \u2014 tracked build output: app/build/generated.txt",
            out.getvalue(),
        )


class Phase4TestSuitePresenceTests(unittest.TestCase):
    """Characterize the explicit Phase 4 test-suite presence contract.

    The production ``REQUIRED_FILES`` tuple must list the four Phase 4
    regression-test paths as exact, fixed entries. No ``tests/``
    wildcard may be used as a substitute.
    """

    def test_phase4_test_suite_paths_are_required(self) -> None:
        expected = {
            "tests/__init__.py",
            "tests/_helpers.py",
            "tests/test_validator_core.py",
            "tests/test_validator_repository.py",
        }
        required = set(validate_local.REQUIRED_FILES)
        for path in expected:
            self.assertIn(path, required)
        # No wildcard or directory-style entries
        self.assertNotIn("tests/", required)
        self.assertNotIn("tests/*", required)
        self.assertNotIn("tests/**", required)


class CandidateUntrackedTestVisibilityTests(unittest.TestCase):
    """``candidate_inventory`` must include allowlisted untracked test
    paths only in non-clean/candidate mode.

    Uses ``tempfile.TemporaryDirectory`` to create an isolated REPO with
    one allowlisted untracked test path and one arbitrary untracked
    sibling. ``git_ls_files`` is patched to return no tracked files.
    The production ``CANDIDATE_UNTRACKED_ALLOWLIST`` is never patched
    and drives the result.
    """

    def test_candidate_inventory_includes_allowlisted_untracked_test_only_in_candidate_mode(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            tests_dir = tmp_root / "tests"
            tests_dir.mkdir()
            allowlisted = tests_dir / "test_validator_core.py"
            allowlisted.write_text(
                "# isolated regression test fixture\n", encoding="utf-8"
            )
            not_allowlisted = tests_dir / "not_allowlisted.py"
            not_allowlisted.write_text(
                "# arbitrary untracked file\n", encoding="utf-8"
            )
            allowlisted_posix = allowlisted.as_posix()
            not_allowlisted_posix = not_allowlisted.as_posix()

            with _helpers.patched_module_attribute(
                "REPO", tmp_root
            ), _helpers.patched_module_attribute(
                "git_ls_files", lambda: []
            ):
                candidate_args = _make_args(require_clean=False)
                candidate_result = validate_local.candidate_inventory(
                    candidate_args
                )
                candidate_posix = [p.as_posix() for p in candidate_result]
                self.assertEqual(
                    candidate_posix.count(allowlisted_posix), 1
                )
                self.assertNotIn(not_allowlisted_posix, candidate_posix)

                clean_args = _make_args(require_clean=True)
                clean_result = validate_local.candidate_inventory(clean_args)
                clean_posix = [p.as_posix() for p in clean_result]
                self.assertNotIn(allowlisted_posix, clean_posix)
                self.assertNotIn(not_allowlisted_posix, clean_posix)


class BrokenRelativeMarkdownLinkTests(unittest.TestCase):
    """``check_docs`` must fail a repository-local relative Markdown link
    whose target does not exist through the real ``docs/md-links`` branch.

    Because ``fail_fast`` is true, the real checker must stop immediately
    after the broken-link failure and the later contract/governance
    checks must never be reached. The validator's own ``REPO``,
    ``candidate_inventory`` and ``GRADLEW_BAT_EXPECTED_SHA`` are
    temporarily patched to an isolated ``TemporaryDirectory`` containing
    a synthetic ``gradlew.bat`` and exactly one candidate Markdown file
    with one relative filesystem link whose target is intentionally
    absent. The ``resolve_md_link``, ``check_docs``, ``emit``,
    ``Path.exists`` and ``Path.resolve`` functions are never patched, and
    every patched object is restored even when an assertion fails.
    """

    def test_broken_relative_markdown_link_fails_docs_md_links(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            docs_dir = repo / "docs"
            docs_dir.mkdir()
            source_md = docs_dir / "source.md"
            source_md.write_text(
                "# Fixture\n\n"
                "[Missing target](missing-target.md)\n",
                encoding="utf-8",
            )

            gradlew_bat_bytes = b"@echo off\r\n"
            (repo / "gradlew.bat").write_bytes(gradlew_bat_bytes)
            expected_gradlew_bat_sha = hashlib.sha256(
                gradlew_bat_bytes
            ).hexdigest()

            with _helpers.patched_module_attribute(
                "REPO", repo
            ), _helpers.patched_module_attribute(
                "candidate_inventory", lambda args: [source_md]
            ), _helpers.patched_module_attribute(
                "GRADLEW_BAT_EXPECTED_SHA", expected_gradlew_bat_sha
            ):
                args = _make_args(
                    fail_fast=True,
                    require_clean=False,
                )
                with _helpers.capture_stdout_stderr() as (out, _):
                    result = validate_local.check_docs(args, True)

        self.assertFalse(result)
        rendered = out.getvalue()
        self.assertIn("FAIL docs/md-links", rendered)
        self.assertIn(
            "broken link in docs/source.md: missing-target.md", rendered
        )
        self.assertNotIn("link escapes repo", rendered)
        self.assertNotIn("prerequisite/release-contract", rendered)
        self.assertNotIn("docs/phase-headings", rendered)
        self.assertNotIn("docs/repository-consistency", rendered)


class VersionCatalogMalformedInputTests(unittest.TestCase):
    """The bounded release-critical version-catalog helper must reject
    duplicate expected keys, and the real ``check_android_content`` must
    surface that failure before the mandatory source-manifest path when
    ``fail_fast`` is true.

    The valid bounded shape is proved by calling the production helper
    directly. The duplicate-key integration is proved by invoking the
    real ``check_android_content`` against an isolated temporary
    repository that contains only ``gradle/libs.versions.toml`` and
    patching only ``validate_local.REPO``. The source-manifest path
    must never be reached, and no source-manifest fixture is created.
    """

    def setUp(self) -> None:
        self._saved = _helpers.save_validator_state()
        _helpers.reset_validator_state()

    def tearDown(self) -> None:
        _helpers.restore_validator_state(self._saved)

    def test_duplicate_expected_version_key_fails_android_content(self) -> None:
        valid_catalog = (
            '[versions]\n'
            'agp = "9.2.1"\n'
            'kotlinCompose = "2.3.10"\n'
            'composeBom = "2026.06.00"\n'
            'activityCompose = "1.13.0"\n'
        )
        duplicate_catalog = (
            '[versions]\n'
            'agp = "9.2.1"\n'
            'agp = "9.2.1"\n'
            'kotlinCompose = "2.3.10"\n'
            'composeBom = "2026.06.00"\n'
            'activityCompose = "1.13.0"\n'
        )

        self.assertEqual(validate_local._version_catalog_failures(valid_catalog), [])
        self.assertEqual(
            validate_local._version_catalog_failures(duplicate_catalog),
            ["agp=count:2"],
        )

        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            gradle_dir = repo / "gradle"
            gradle_dir.mkdir()
            (gradle_dir / "libs.versions.toml").write_text(
                duplicate_catalog, encoding="utf-8"
            )

            args = _make_args(fail_fast=True, require_clean=False)
            sdk = repo / "unused-sdk"
            with _helpers.patched_module_attribute("REPO", repo), _helpers.capture_stdout_stderr() as (out, _):
                result = validate_local.check_android_content(args, sdk)

        self.assertFalse(result)
        rendered = out.getvalue()
        self.assertIn("FAIL android/version-catalog", rendered)
        self.assertIn("agp=count:2", rendered)
        self.assertNotIn("PASS android/version-catalog", rendered)
        self.assertNotIn("android/source-manifest", rendered)
        self.assertNotIn("source manifest missing", rendered)
        self.assertNotIn("kotlinCompose=count", rendered)
        self.assertNotIn("composeBom=count", rendered)
        self.assertNotIn("activityCompose=count", rendered)


class WrapperJarSha256Tests(unittest.TestCase):
    """``check_required`` must verify the committed Gradle wrapper JAR's
    SHA-256 against the approved Gradle 9.4.1 value through the real
    ``required/wrapper-jar-sha256`` branch.

    Test 1 exercises the real repository: the committed wrapper JAR
    matches the approved SHA-256, so the validator must emit the
    ``PASS required/wrapper-jar-sha256`` line. Test 2 creates a
    controlled temporary JAR outside the repository whose bytes
    intentionally produce a different SHA-256, then invokes the real
    validator against that isolated tree and asserts the
    ``FAIL required/wrapper-jar-sha256`` line includes the observed
    SHA-256 and does not expose the temporary absolute path. Both
    tests invoke the real ``check_required`` against the production
    ``REQUIRED_FILES``, ``git_ls_files`` and ``check_release_contract``
    symbol names through narrow ``patched_module_attribute`` patches
    that are restored even when an assertion fails. No validator
    business logic is reimplemented.
    """

    def test_committed_wrapper_jar_passes_required_wrapper_jar_sha256(self) -> None:
        """The real committed Gradle 9.4.1 wrapper JAR must satisfy the
        bounded SHA-256 verification and emit the exact PASS line."""
        with _helpers.patched_module_attribute(
            "REQUIRED_FILES", ()
        ), _helpers.patched_module_attribute(
            "git_ls_files", lambda: []
        ), _helpers.patched_module_attribute(
            "check_release_contract", lambda *a, **k: True
        ):
            args = _make_args(fail_fast=False, require_clean=False)
            with _helpers.capture_stdout_stderr() as (out, _):
                validate_local.check_required(args, False)

        rendered = out.getvalue()
        self.assertIn(
            "PASS required/wrapper-jar-sha256 \u2014 wrapper JAR SHA-256 verified",
            rendered,
        )
        # The approved SHA value itself must be present in the real
        # validator's constant so the committed JAR continues to
        # match the maintainer-supplied approved value.
        self.assertEqual(
            validate_local.WRAPPER_JAR_EXPECTED_SHA,
            "55243ef57851f12b070ad14f7f5bb8302daceeebc5bce5ece5fa6edb23e1145c",
        )

    def test_mismatched_wrapper_jar_fails_required_wrapper_jar_sha256(self) -> None:
        """A controlled temporary JAR whose bytes produce a different
        SHA-256 must be rejected with FAIL that includes the observed
        SHA-256 and does not expose the temporary absolute path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            gradle_dir = tmp_root / "gradle" / "wrapper"
            gradle_dir.mkdir(parents=True)
            tmp_jar = gradle_dir / "gradle-wrapper.jar"
            tmp_jar_bytes = b"phase5a-mismatched-wrapper-jar-bytes"
            tmp_jar.write_bytes(tmp_jar_bytes)
            observed_sha = hashlib.sha256(tmp_jar_bytes).hexdigest()
            tmp_jar_abs = str(tmp_jar.resolve())

            with _helpers.patched_module_attribute(
                "REPO", tmp_root
            ), _helpers.patched_module_attribute(
                "REQUIRED_FILES", ()
            ), _helpers.patched_module_attribute(
                "git_ls_files", lambda: []
            ), _helpers.patched_module_attribute(
                "check_release_contract", lambda *a, **k: True
            ):
                args = _make_args(fail_fast=False, require_clean=False)
                with _helpers.capture_stdout_stderr() as (out, _):
                    validate_local.check_required(args, False)

        rendered = out.getvalue()
        self.assertIn(
            "FAIL required/wrapper-jar-sha256 \u2014 "
            f"unexpected SHA-256: {observed_sha}",
            rendered,
        )
        # The temporary absolute path must not appear in any output.
        self.assertNotIn(tmp_jar_abs, rendered)
        # The temporary root must not appear either, in any form.
        self.assertNotIn(str(tmp_root.resolve()), rendered)


class DependabotYamlTests(unittest.TestCase):
    """``check_required`` must verify the bounded Phase 5C Dependabot
    configuration through the real ``required/dependabot-yaml`` branch.

    Test 1 (positive) creates an isolated ``TemporaryDirectory`` containing
    only a ``.github/dependabot.yml`` populated with the canonical
    two-ecosystem configuration. It patches ``REPO``, ``REQUIRED_FILES``,
    ``git_ls_files`` and ``check_release_contract`` through
    ``_helpers.patched_module_attribute`` and invokes the real
    ``check_required`` against the controlled tree. It asserts the
    captured stdout contains the exact
    ``PASS required/dependabot-yaml — Dependabot configuration verified``
    line.

    Test 2 (representative negative case) uses the same isolated
    ``check_required`` invocation but with a controlled
    ``.github/dependabot.yml`` that omits the ``github-actions``
    ecosystem. It asserts the captured stdout contains the exact
    ``FAIL required/dependabot-yaml — ecosystems must equal: gradle, github-actions``
    line.

    Tests 3 through 7 invoke the production ``_dependabot_failures``
    helper directly (the single bounded Phase 5C source of truth) against
    mutated copies of the canonical text. The helper is the same logic
    that ``check_required`` invokes, so no parallel test-only parser or
    policy implementation is introduced.

    No validator business logic is reimplemented. No YAML library is
    used. ``tempfile``, ``Path``, and the existing ``_helpers`` are used.
    The real Git index is not touched. No non-ignored repository output
    is created. The real ``.github/dependabot.yml`` is not mutated by
    negative fixtures.
    """

    def _canonical_text(self) -> str:
        return (
            'version: 2\n'
            'updates:\n'
            '  - package-ecosystem: "gradle"\n'
            '    directory: "/"\n'
            '    schedule:\n'
            '      interval: "weekly"\n'
            '    open-pull-requests-limit: 5\n'
            '\n'
            '  - package-ecosystem: "github-actions"\n'
            '    directory: "/"\n'
            '    schedule:\n'
            '      interval: "weekly"\n'
            '    open-pull-requests-limit: 5\n'
        )

    def test_canonical_dependabot_configuration_passes_required_dependabot_yaml(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            gh_dir = tmp_root / ".github"
            gh_dir.mkdir()
            (gh_dir / "dependabot.yml").write_text(
                self._canonical_text(), encoding="utf-8",
            )
            with _helpers.patched_module_attribute(
                "REPO", tmp_root,
            ), _helpers.patched_module_attribute(
                "REQUIRED_FILES", (),
            ), _helpers.patched_module_attribute(
                "git_ls_files", lambda: [],
            ), _helpers.patched_module_attribute(
                "check_release_contract", lambda *a, **k: True,
            ):
                args = _make_args(fail_fast=False, require_clean=False)
                with _helpers.capture_stdout_stderr() as (out, _):
                    validate_local.check_required(args, False)
        self.assertIn(
            "PASS required/dependabot-yaml \u2014 Dependabot configuration verified",
            out.getvalue(),
        )

    def test_missing_one_required_ecosystem_fails_required_dependabot_yaml(
        self,
    ) -> None:
        only_gradle = (
            'version: 2\n'
            'updates:\n'
            '  - package-ecosystem: "gradle"\n'
            '    directory: "/"\n'
            '    schedule:\n'
            '      interval: "weekly"\n'
            '    open-pull-requests-limit: 5\n'
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            gh_dir = tmp_root / ".github"
            gh_dir.mkdir()
            (gh_dir / "dependabot.yml").write_text(
                only_gradle, encoding="utf-8",
            )
            with _helpers.patched_module_attribute(
                "REPO", tmp_root,
            ), _helpers.patched_module_attribute(
                "REQUIRED_FILES", (),
            ), _helpers.patched_module_attribute(
                "git_ls_files", lambda: [],
            ), _helpers.patched_module_attribute(
                "check_release_contract", lambda *a, **k: True,
            ):
                args = _make_args(fail_fast=False, require_clean=False)
                with _helpers.capture_stdout_stderr() as (out, _):
                    validate_local.check_required(args, False)
        rendered = out.getvalue()
        self.assertIn(
            "FAIL required/dependabot-yaml \u2014 ecosystems must equal: gradle, github-actions",
            rendered,
        )

    def test_additional_ecosystem_fails(self) -> None:
        text = (
            'version: 2\n'
            'updates:\n'
            '  - package-ecosystem: "gradle"\n'
            '    directory: "/"\n'
            '    schedule:\n'
            '      interval: "weekly"\n'
            '    open-pull-requests-limit: 5\n'
            '\n'
            '  - package-ecosystem: "github-actions"\n'
            '    directory: "/"\n'
            '    schedule:\n'
            '      interval: "weekly"\n'
            '    open-pull-requests-limit: 5\n'
            '\n'
            '  - package-ecosystem: "npm"\n'
            '    directory: "/"\n'
            '    schedule:\n'
            '      interval: "weekly"\n'
            '    open-pull-requests-limit: 5\n'
        )
        failures = validate_local._dependabot_failures(text)
        self.assertIn(
            "ecosystems must equal: gradle, github-actions", failures,
        )

    def test_top_level_version_other_than_2_fails(self) -> None:
        text = self._canonical_text().replace("version: 2", "version: 3", 1)
        failures = validate_local._dependabot_failures(text)
        self.assertIn("top-level version must equal 2", failures)

    def test_non_root_directory_fails(self) -> None:
        text = self._canonical_text().replace(
            'directory: "/"', 'directory: "/app"', 1,
        )
        failures = validate_local._dependabot_failures(text)
        # The first entry (gradle) has a non-root directory
        self.assertIn("gradle directory must equal /", failures)

    def test_wrong_schedule_interval_and_limit_fail(self) -> None:
        with self.subTest(variant="wrong schedule interval"):
            bad_interval = self._canonical_text().replace(
                '      interval: "weekly"', '      interval: "daily"', 1,
            )
            failures = validate_local._dependabot_failures(bad_interval)
            self.assertIn(
                "gradle schedule.interval must equal weekly", failures,
            )
        with self.subTest(variant="wrong open-pull-requests-limit"):
            bad_limit = self._canonical_text().replace(
                "open-pull-requests-limit: 5",
                "open-pull-requests-limit: 10",
                1,
            )
            failures = validate_local._dependabot_failures(bad_limit)
            self.assertIn(
                "gradle open-pull-requests-limit must equal 5", failures,
            )

    def test_forbidden_policy_keys_fail(self) -> None:
        forbidden_keys = (
            "auto-merge",
            "vulnerability-alerts",
            "groups",
            "assignees",
            "reviewers",
            "milestone",
            "ignore",
            "labels",
            "target-branch",
            "registries",
        )
        for key in forbidden_keys:
            with self.subTest(forbidden_key=key):
                text = self._canonical_text() + f"{key}:\n  enabled: true\n"
                failures = validate_local._dependabot_failures(text)
                self.assertIn(f"forbidden key: {key}", failures)


if __name__ == "__main__":
    unittest.main()
