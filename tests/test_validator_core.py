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


class TrackedPycRejectionTests(unittest.TestCase):
    """``check_required`` must reject tracked ``.pyc`` paths through the
    real ``required/no-pyc`` branch. Because ``fail_fast`` is true, the
    real checker must stop immediately after this rejection and the
    wrapper, ``.gitignore``, and ``.gitattributes`` fixtures must never
    be reached. The validator's own ``REQUIRED_FILES``, ``git_ls_files``
    and ``check_release_contract`` are temporarily patched, and every
    patched object is restored even when an assertion fails."""

    def test_tracked_pyc_is_rejected_with_required_no_pyc_line(self) -> None:
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
            "FAIL required/no-pyc \u2014 tracked bytecode: bad.pyc",
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


if __name__ == "__main__":
    unittest.main()
