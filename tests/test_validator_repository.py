"""Repository-bound regression tests for ``scripts.validate_local``.

Exercises the real validator functions against isolated, non-repository
fixtures. No validator business logic is reimplemented. Python standard
library only. No Gradle, no Android tooling, no network, no persistent
Git configuration, no private material.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import validate_local
from tests import _helpers


class MissingReleaseContractTests(unittest.TestCase):
    """When the release contract file is absent, ``_load_release_contract``
    must return ``None``, set ``_CONTRACT_ERROR`` to a concise reason, and
    must not raise an expected missing-contract exception."""

    def test_missing_contract_returns_none_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = repo / "scripts" / "release_contract.json"
            with _helpers.patched_repo_and_contract(repo, contract_path):
                result = validate_local._load_release_contract()
                self.assertIsNone(result)
                err = validate_local._CONTRACT_ERROR
                self.assertIsNotNone(err)
                self.assertIn("contract file missing", err or "")


class InvalidWorktreePrerequisiteTests(unittest.TestCase):
    """When the validator's ``REPO`` is not inside a Git worktree, the
    prerequisite check must return ``False``, emit the exact concise
    failure line, and set ``_PREREQ_FAILED``."""

    def test_non_worktree_repo_emits_prereq_failure(self) -> None:
        self.assertIsNotNone(
            shutil.which("git"),
            "git executable must be available on the development environment",
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = repo / "scripts" / "release_contract.json"
            with _helpers.patched_repo_and_contract(repo, contract_path):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    result = validate_local.check_git_worktree_prerequisite()
                rendered = out.getvalue()
                self.assertFalse(result)
                self.assertIn(
                    "FAIL prerequisite/git-worktree \u2014 repository is not a Git worktree",
                    rendered,
                )
                self.assertTrue(validate_local._PREREQ_FAILED)


class MissingGitPrerequisiteChildTests(unittest.TestCase):
    """End-to-end regression of the real missing-Git prerequisite path.

    The validator is launched in a fresh child process with ``PATH``
    pointing only to a fresh empty temporary directory, so the real
    ``shutil.which("git")`` is ``None`` inside the child. The child runs
    from the real repository root, imports the real
    ``scripts.validate_local``, and exits with the value returned by
    ``main(["--group", "required"])``. The parent environment is never
    mutated; the child uses ``sys.executable`` directly. No shell
    wrapper is used.
    """

    def test_child_process_missing_git_returns_two(self) -> None:
        completed = _helpers.run_validator_child_with_clean_path()

        self.assertEqual(completed.returncode, 2)
        stdout = completed.stdout
        self.assertIn("FAIL prerequisite/git \u2014 git executable not found", stdout)
        self.assertIn("SUMMARY pass=0 fail=1 skip=0", stdout)
        self.assertIn("release_gate=NOT_SATISFIED", stdout)
        self.assertNotIn("Traceback", completed.stderr)


class TemporaryGitCleanDirtyTests(unittest.TestCase):
    """Real ``validate_local.git_status_short`` must report an empty
    status for a freshly initialised temporary repository and must
    identify a subsequently created untracked file. The temporary
    repository is created with ``git init --quiet`` and the test never
    creates a commit, never runs ``git config``, and never touches the
    real repository's index. The real ``REPO`` is patched only inside
    the test and is restored even when an assertion fails."""

    def test_temp_git_repo_clean_then_untracked_file(self) -> None:
        self.assertIsNotNone(
            shutil.which("git"),
            "git executable must be available on the development environment",
        )
        with tempfile.TemporaryDirectory() as td:
            temp_repo = Path(td)
            subprocess.run(
                ["git", "init", "--quiet", str(temp_repo)],
                check=True,
            )
            with _helpers.patched_module_attribute("REPO", temp_repo):
                initial_status = validate_local.git_status_short()
            self.assertEqual(initial_status, "")

            scratch = temp_repo / "scratch_file.txt"
            scratch.write_text("temporary fixture content\n", encoding="utf-8")

            with _helpers.patched_module_attribute("REPO", temp_repo):
                dirty_status = validate_local.git_status_short()
            self.assertIn("?? scratch_file.txt", dirty_status)


class MalformedReleaseContractJsonTests(unittest.TestCase):
    """When the release contract file contains intentionally malformed
    JSON, the real ``_load_release_contract`` must return ``None`` and
    set ``_CONTRACT_ERROR`` to the exact concise reason
    ``contract JSON is malformed``. No traceback or expected JSON
    exception should propagate. The contract state is restored through
    the existing ``_helpers.patched_repo_and_contract`` helper after
    the test."""

    def test_malformed_contract_returns_none_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = repo / "scripts" / "release_contract.json"
            contract_path.parent.mkdir(parents=True, exist_ok=True)
            contract_path.write_text(
                "{ this is not valid JSON", encoding="utf-8"
            )
            with _helpers.patched_repo_and_contract(repo, contract_path):
                result = validate_local._load_release_contract()
                self.assertIsNone(result)
                err = validate_local._CONTRACT_ERROR
                self.assertIsNotNone(err)
                self.assertIn("contract JSON is malformed", err or "")


class InvalidReleaseContractStructureTests(unittest.TestCase):
    """When the release contract JSON is syntactically valid but its
    top-level structure does not satisfy the contract schema, the real
    ``_load_release_contract`` must return ``None`` and set
    ``_CONTRACT_ERROR`` to the exact concise reason
    ``schema_version must equal 1``. The test uses the existing
    contract/repository patch helper and constructs no unrelated
    repository files."""

    def test_empty_top_level_object_returns_none_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = repo / "scripts" / "release_contract.json"
            contract_path.parent.mkdir(parents=True, exist_ok=True)
            contract_path.write_text("{}", encoding="utf-8")
            with _helpers.patched_repo_and_contract(repo, contract_path):
                result = validate_local._load_release_contract()
                self.assertIsNone(result)
                err = validate_local._CONTRACT_ERROR
                self.assertIsNotNone(err)
                self.assertIn("schema_version must equal 1", err or "")


class RepositoryConsistencyTests(unittest.TestCase):
    """Tests for the new ``docs/repository-consistency`` active-release
    identity check. The check uses the real loaded contract and operates
    on REPO-relative paths. Negative cases use isolated temporary
    synthetic fixtures; no live governance file is mutated.
    """

    GOOD_README = (
        "# NudgeWhen\n"
        "\n"
        "NudgeWhen is currently in the `v0.1.1` release train, "
        "a documentation release on the single branch `release/v0.1.1`. "
        "The previous `v0.1.0` release is complete and historical; "
        "its branch `release/v0.1.0` is no longer the active branch.\n"
        "\n"
        "## Current release train\n"
        "\n"
        "The current active branch is `release/v0.1.1`. "
        "The previous `v0.1.0` release train on `release/v0.1.0` is "
        "complete and historical.\n"
        "\n"
        "v0.1.0 phases (historical, complete):\n"
        "\n"
        "- Phase 0 — Test\n"
    )

    GOOD_PHASE_LIST = (
        "# Phase List — NudgeWhen v0.1.1\n"
        "\n"
        "**Document status:** Accepted — Phases 0 through 7 complete; v0.1.1 release in progress\n"
        "\n"
        "## Phase 0 — Test\n"
        "### Status\n"
        "Planned\n"
    )

    GOOD_CHARTER = (
        "# Release Charter — NudgeWhen v0.1.1\n"
        "\n"
        "**Document status:** Accepted — Phases 0 through 7 complete; v0.1.1 release in progress\n"
        "\n"
        "## Explicit non-goals\n"
        "\n"
        "- No new features.\n"
    )

    HISTORICAL_SAFE_README = (
        "# NudgeWhen\n"
        "\n"
        "NudgeWhen is currently in the `v0.1.1` release train, "
        "a documentation release.\n"
        "\n"
        "## Current release train\n"
        "\n"
        "The current active branch is `release/v0.1.1`.\n"
        "\n"
        "## Historical references\n"
        "\n"
        "The previous v0.1.0 release is complete and historical.\n"
        "v0.1.0 phases (historical, complete):\n"
        "- Release charter — v0.1.0 (historical)\n"
        "- Phase list — v0.1.0 (historical)\n"
    )

    GOOD_CI_WORKFLOW = (
        "name: CI\n"
        "\n"
        "on:\n"
        "  push:\n"
        "    branches:\n"
        "      - release/**\n"
        "      - main\n"
        "  pull_request:\n"
        "    branches:\n"
        "      - main\n"
        "  workflow_dispatch:\n"
        "\n"
        "permissions:\n"
        "  contents: read\n"
        "\n"
        "concurrency:\n"
        "  group: ${{ github.workflow }}-${{ github.ref }}\n"
        "  cancel-in-progress: true\n"
        "\n"
        "jobs:\n"
        "  validate:\n"
        "    name: validate\n"
        "    runs-on: ubuntu-24.04\n"
        "    timeout-minutes: 30\n"
        "    steps:\n"
        "      - name: checkout\n"
        "        uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0\n"
    )

    GOOD_AGENTS = (
        "# AGENTS.md\n"
        "\n"
        "## Current release context\n"
        "\n"
        "- **Active release:** `v0.1.1`\n"
        "- **Release title:** `NudgeWhen v0.1.1 — Post-Release Closure and Reusable Validation Baseline`\n"
        "- **Active branch:** `release/v0.1.1`\n"
        "- **Active release charter:** `docs/releases/v0.1.1/release-charter.md`\n"
        "- **Active phase list:** `docs/releases/v0.1.1/phase-list.md`\n"
        "- **Current phase:** Phase 6 — Integrated Evidence and Agent Evaluation\n"
        "- **Bootstrap exception (historical, terminated):** The previous `v0.1.0` release and `release/v0.1.0` branch are historical and not active.\n"
    )

    def _make_args(self) -> argparse.Namespace:
        return argparse.Namespace(
            require_clean=False,
            fail_fast=False,
            skip_android=False,
        )

    def _last_repo_consistency_result(self) -> tuple[str, str, str, str]:
        results = [
            r for r in validate_local._RESULTS if r[2] == "repository-consistency"
        ]
        self.assertEqual(len(results), 1, "expected exactly one repository-consistency result")
        return results[0]

    def _write_ci_workflow(self, repo: Path, content: str) -> None:
        ci_path = repo / ".github" / "workflows" / "ci.yml"
        ci_path.parent.mkdir(parents=True, exist_ok=True)
        ci_path.write_text(content, encoding="utf-8")

    def _write_agents(self, repo: Path, content: str) -> None:
        (repo / "AGENTS.md").write_text(content, encoding="utf-8")

    def test_matching_active_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertTrue(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "PASS")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("v0.1.1", message)
                self.assertIn("release/v0.1.1", message)

    def test_stale_readme_active_version_fails(self) -> None:
        stale_readme = self.GOOD_README.replace(
            "is currently in the `v0.1.1` release train",
            "is currently in the `v0.1.0` release train",
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, stale_readme, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("active version declaration", message)
                self.assertIn("v0.1.0", message)
                self.assertIn("v0.1.1", message)

    def test_stale_readme_active_branch_fails(self) -> None:
        stale_readme = self.GOOD_README.replace(
            "The current active branch is `release/v0.1.1`",
            "The current active branch is `release/v0.1.0`",
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, stale_readme, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("active branch declaration", message)
                self.assertIn("release/v0.1.0", message)
                self.assertIn("release/v0.1.1", message)

    def test_historical_references_alone_do_not_fail(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo,
                self.HISTORICAL_SAFE_README,
                self.GOOD_PHASE_LIST,
                self.GOOD_CHARTER,
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertTrue(ok)
                status, _, _, _ = self._last_repo_consistency_result()
                self.assertEqual(status, "PASS")

    def test_phase_list_title_mismatch_fails(self) -> None:
        wrong_phase_list = (
            "# Phase List — NudgeWhen v0.1.0\n"
            "\n"
            "**Document status:** Accepted — Phases 0 through 7 complete; v0.1.1 release in progress\n"
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, wrong_phase_list, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("phase-list", message)
                self.assertIn("v0.1.0", message)
                self.assertIn("v0.1.1", message)

    def test_charter_presenting_historical_as_active_fails(self) -> None:
        wrong_charter = (
            "# Release Charter — NudgeWhen v0.1.0\n"
            "\n"
            "**Document status:** Accepted — Phases 0 through 7 complete; v0.1.1 release in progress\n"
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, wrong_charter
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("charter", message)
                self.assertIn("v0.1.0", message)
                self.assertIn("v0.1.1", message)

    def test_phase_list_document_status_summary_mismatch_fails(self) -> None:
        """B5A: when the phase-list document-status line claims an
        earlier completed-range prefix than the contract requires, the
        real ``check_repository_consistency`` must return ``False`` and
        emit a single ``docs/repository-consistency`` FAIL whose message
        identifies the phase-list document-status summary, the observed
        completed-range claim, and the contract-required completed range.
        All other active identity fields remain valid.
        """
        stale_phase_list = (
            "# Phase List — NudgeWhen v0.1.1\n"
            "\n"
            "**Document status:** Accepted — Phases 0 through 3 complete; v0.1.1 release in progress\n"
            "\n"
            "## Phase 0 — Test\n"
            "### Status\n"
            "Planned\n"
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, stale_phase_list, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("phase-list", message)
                self.assertIn("Phases 0 through 3 complete", message)
                self.assertIn("Phases 0 through 7 complete", message)

    def test_charter_document_status_summary_mismatch_fails(self) -> None:
        """B5A: when the release-charter document-status line claims an
        earlier completed-range prefix than the contract requires, the
        real ``check_repository_consistency`` must return ``False`` and
        emit a single ``docs/repository-consistency`` FAIL whose message
        identifies the release-charter document-status summary, the
        observed completed-range claim, and the contract-required
        completed range. All other active identity fields remain valid.
        """
        stale_charter = (
            "# Release Charter — NudgeWhen v0.1.1\n"
            "\n"
            "**Document status:** Accepted — Phases 0 through 3 complete; v0.1.1 release in progress\n"
            "\n"
            "## Explicit non-goals\n"
            "\n"
            "- No new features.\n"
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, stale_charter
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("charter", message)
                self.assertIn("Phases 0 through 3 complete", message)
                self.assertIn("Phases 0 through 7 complete", message)

    def test_ci_missing_release_push_fails(self) -> None:
        """B5B: when the persistent CI workflow omits ``release/**`` from
        ``push.branches`` while retaining all other CI invariants, the
        real ``check_repository_consistency`` must return ``False`` and
        emit a single ``docs/repository-consistency`` FAIL whose message
        identifies the missing ``release/**`` push coverage. All other
        active identity fields remain valid."""
        bad_ci = self.GOOD_CI_WORKFLOW.replace(
            "      - release/**\n",
            "",
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, bad_ci)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("CI workflow lacks push coverage for release/**", message)

    def test_ci_missing_main_push_fails(self) -> None:
        """B5B: when the persistent CI workflow omits ``main`` from
        ``push.branches`` while retaining all other CI invariants, the
        real ``check_repository_consistency`` must return ``False`` and
        emit a single ``docs/repository-consistency`` FAIL whose message
        identifies the missing ``main`` push coverage. All other active
        identity fields remain valid."""
        bad_ci = self.GOOD_CI_WORKFLOW.replace(
            "  push:\n"
            "    branches:\n"
            "      - release/**\n"
            "      - main\n",
            "  push:\n"
            "    branches:\n"
            "      - release/**\n",
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, bad_ci)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("CI workflow lacks push coverage for main", message)

    def test_ci_missing_main_pull_request_fails(self) -> None:
        """B5B: when the persistent CI workflow omits ``main`` from
        ``pull_request.branches`` while retaining all other CI
        invariants, the real ``check_repository_consistency`` must
        return ``False`` and emit a single ``docs/repository-consistency``
        FAIL whose message identifies the missing ``main`` pull_request
        coverage. All other active identity fields remain valid."""
        bad_ci = self.GOOD_CI_WORKFLOW.replace(
            "  pull_request:\n"
            "    branches:\n"
            "      - main\n",
            "  pull_request:\n"
            "    branches:\n"
            "      - develop\n",
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, bad_ci)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn(
                    "CI workflow lacks pull_request coverage for main", message
                )

    def test_ci_missing_workflow_dispatch_fails(self) -> None:
        """B5B: when the persistent CI workflow omits the
        ``workflow_dispatch`` trigger while retaining all other CI
        invariants, the real ``check_repository_consistency`` must
        return ``False`` and emit a single ``docs/repository-consistency``
        FAIL whose message identifies the missing ``workflow_dispatch``
        trigger. All other active identity fields remain valid."""
        bad_ci = self.GOOD_CI_WORKFLOW.replace(
            "  workflow_dispatch:\n",
            "",
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, bad_ci)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("CI workflow lacks workflow_dispatch", message)

    def test_ci_missing_validate_job_fails(self) -> None:
        """B5B: when the persistent CI workflow omits the stable
        ``validate`` job while retaining all other CI invariants, the
        real ``check_repository_consistency`` must return ``False`` and
        emit a single ``docs/repository-consistency`` FAIL whose message
        identifies the missing stable ``validate`` job. All other active
        identity fields remain valid."""
        bad_ci = self.GOOD_CI_WORKFLOW.replace(
            "  validate:\n",
            "  build:\n",
            1,
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, bad_ci)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("CI workflow lacks stable validate job", message)

    def test_ci_workflow_missing_fails(self) -> None:
        """B5B-R1: when the persistent CI workflow is entirely absent
        from the repository, the real ``check_repository_consistency``
        must return ``False`` and emit a single
        ``docs/repository-consistency`` FAIL whose message contains all
        five existing CI invariant failures. All other active identity
        fields remain valid. The workflow is intentionally not written
        for this test, so it represents the missing persistent workflow
        case."""
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("CI workflow lacks push coverage for release/**", message)
                self.assertIn("CI workflow lacks push coverage for main", message)
                self.assertIn("CI workflow lacks pull_request coverage for main", message)
                self.assertIn("CI workflow lacks workflow_dispatch", message)
                self.assertIn("CI workflow lacks stable validate job", message)

    def test_ci_missing_top_level_on_mapping_fails(self) -> None:
        """B5C: when the persistent CI workflow omits the top-level
        ``on:`` mapping while otherwise retaining all existing B5B
        trigger text, the real ``check_repository_consistency`` must
        return ``False`` and emit a single
        ``docs/repository-consistency`` FAIL whose message identifies
        the missing top-level ``on:`` mapping. This is the bounded
        malformed required structure invariant. All other active
        identity fields remain valid."""
        bad_ci = self.GOOD_CI_WORKFLOW.replace(
            "on:\n",
            "",
            1,
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, bad_ci)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn("CI workflow lacks top-level on mapping", message)

    def test_ci_validate_display_name_mismatch_fails(self) -> None:
        """B5C: when the persistent CI workflow's ``validate`` job
        has a child display name other than ``validate`` while
        retaining the ``jobs.validate`` key, all existing B5B trigger
        text, and the top-level ``permissions: contents: read``
        permission, the real ``check_repository_consistency`` must
        return ``False`` and emit a single
        ``docs/repository-consistency`` FAIL whose message identifies
        the validate job display name. The display name check is
        bounded to the ``validate`` job. All other active identity
        fields remain valid."""
        bad_ci = self.GOOD_CI_WORKFLOW.replace(
            "    name: validate\n",
            "    name: build\n",
            1,
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, bad_ci)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn(
                    "CI workflow validate job display name is not 'validate'",
                    message,
                )

    def test_ci_contents_permission_not_read_fails(self) -> None:
        """B5C: when the persistent CI workflow's top-level
        ``permissions`` section declares a non-read ``contents``
        scope while retaining all existing B5B trigger text, the
        ``jobs.validate`` key with its ``name: validate`` display
        name, and the top-level ``on:`` mapping, the real
        ``check_repository_consistency`` must return ``False`` and
        emit a single ``docs/repository-consistency`` FAIL whose
        message identifies the missing read-only contents
        permission. The permission check is bounded to the top-level
        ``permissions`` block. All other active identity fields
        remain valid."""
        bad_ci = self.GOOD_CI_WORKFLOW.replace(
            "  contents: read\n",
            "  contents: write\n",
            1,
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, bad_ci)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn(
                    "CI workflow lacks read-only contents permission",
                    message,
                )

    def test_agents_historical_release_as_active_fails(self) -> None:
        """B5D: when the bounded ``## Current release context`` section
        of ``AGENTS.md`` places the historical release in the
        ``Active release`` field while retaining the active branch and
        all other active identity surfaces, the real
        ``check_repository_consistency`` must return ``False`` and emit
        a single ``docs/repository-consistency`` FAIL whose message
        identifies the historical release as active and names the
        contract-required active release. The message must not report
        an AGENTS active-branch mismatch."""
        bad_agents = self.GOOD_AGENTS.replace(
            "- **Active release:** `v0.1.1`",
            "- **Active release:** `v0.1.0`",
            1,
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, bad_agents)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn(
                    "AGENTS current release context identifies historical "
                    "release 'v0.1.0' as active",
                    message,
                )
                self.assertIn("contract requires 'v0.1.1'", message)
                self.assertNotIn(
                    "AGENTS current release context active branch is",
                    message,
                )
                self.assertNotIn(
                    "AGENTS current release context identifies historical branch",
                    message,
                )
                self.assertNotIn(
                    "AGENTS current release context lacks Active branch",
                    message,
                )

    def test_agents_historical_branch_as_active_fails(self) -> None:
        """B5D: when the bounded ``## Current release context`` section
        of ``AGENTS.md`` places the historical branch in the
        ``Active branch`` field while retaining the active release and
        all other active identity surfaces, the real
        ``check_repository_consistency`` must return ``False`` and emit
        a single ``docs/repository-consistency`` FAIL whose message
        identifies the historical branch as active and names the
        contract-required active branch. The message must not report
        an AGENTS active-release mismatch."""
        bad_agents = self.GOOD_AGENTS.replace(
            "- **Active branch:** `release/v0.1.1`",
            "- **Active branch:** `release/v0.1.0`",
            1,
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, bad_agents)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn(
                    "AGENTS current release context identifies historical "
                    "branch 'release/v0.1.0' as active",
                    message,
                )
                self.assertIn("contract requires 'release/v0.1.1'", message)
                self.assertNotIn(
                    "AGENTS current release context active release is",
                    message,
                )
                self.assertNotIn(
                    "AGENTS current release context identifies historical release",
                    message,
                )
                self.assertNotIn(
                    "AGENTS current release context lacks Active release",
                    message,
                )

    def test_agents_empty_file_fails_as_missing_current_release_context(self) -> None:
        """B5D-R1: when ``AGENTS.md`` is a successfully readable
        zero-byte UTF-8 text file, the real
        ``check_repository_consistency`` must return ``False`` and emit
        a single ``docs/repository-consistency`` FAIL whose message
        identifies the missing ``## Current release context`` section.
        The message must not report the AGENTS file as unreadable, and
        must not fabricate the active release or active branch
        declaration failures because parsing cannot reach declarations
        without the section. All other active identity fields remain
        valid."""
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, "")
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn(
                    "AGENTS.md lacks '## Current release context' section",
                    message,
                )
                self.assertNotIn(
                    "AGENTS.md is not readable as UTF-8",
                    message,
                )
                self.assertNotIn(
                    "AGENTS current release context lacks Active release",
                    message,
                )
                self.assertNotIn(
                    "AGENTS current release context lacks Active branch",
                    message,
                )

    def test_current_contributing_false_android_absence_fails(self) -> None:
        """B5E: when the current-facing ``CONTRIBUTING.md`` asserts the
        false Android-absence claim while all other active identity
        surfaces remain valid and no other B5E false-absence signatures
        are present, the real ``check_repository_consistency`` must
        return ``False`` and emit a single ``docs/repository-consistency``
        FAIL whose message identifies the false Android-absence claim in
        ``CONTRIBUTING.md``. The message must not report a false CI or
        false released-baseline absence claim. ``SECURITY.md`` is
        intentionally absent because missing B5E current-facing sources
        are owned by the existing required/files contract, not by this
        B5E slice."""
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, self.GOOD_AGENTS)
            (repo / "CONTRIBUTING.md").write_text(
                "## Current state of the project\n\n"
                "There is no Android application code.\n",
                encoding="utf-8",
            )
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn(
                    "CONTRIBUTING.md falsely claims Android application code is absent",
                    message,
                )
                self.assertNotIn(
                    "falsely claims CI workflow is absent", message
                )
                self.assertNotIn(
                    "falsely claims the released baseline is absent", message
                )

    def test_current_readme_false_ci_absence_fails(self) -> None:
        """B5E: when the current-facing ``README.md`` asserts the false
        CI-absence claim while all other active identity surfaces
        remain valid and no other B5E false-absence signatures are
        present, the real ``check_repository_consistency`` must return
        ``False`` and emit a single ``docs/repository-consistency``
        FAIL whose message identifies the false CI-absence claim in
        ``README.md``. The message must not report a false Android or
        false released-baseline absence claim. ``CONTRIBUTING.md`` and
        ``SECURITY.md`` are intentionally absent because missing B5E
        current-facing sources are owned by the existing required/files
        contract, not by this B5E slice."""
        bad_readme = self.GOOD_README + (
            "\nThere is no CI workflow.\n"
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, bad_readme, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, self.GOOD_AGENTS)
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn(
                    "README.md falsely claims CI workflow is absent",
                    message,
                )
                self.assertNotIn(
                    "falsely claims Android application code is absent", message
                )
                self.assertNotIn(
                    "falsely claims the released baseline is absent", message
                )

    def test_current_security_false_published_release_absence_fails(self) -> None:
        """B5E: when the current-facing ``SECURITY.md`` asserts the
        false published-release-absence claim while all other active
        identity surfaces remain valid and no other B5E false-absence
        signatures are present, the real ``check_repository_consistency``
        must return ``False`` and emit a single
        ``docs/repository-consistency`` FAIL whose message identifies
        the false released-baseline-absence claim in ``SECURITY.md``.
        The message must not report a false Android or false CI absence
        claim. The production rule recognizes both
        ``no published release`` and ``no released or runnable
        application`` as released-baseline-absence signatures; this
        regression exercises the first."""
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo, self.GOOD_README, self.GOOD_PHASE_LIST, self.GOOD_CHARTER
            )
            self._write_ci_workflow(repo, self.GOOD_CI_WORKFLOW)
            self._write_agents(repo, self.GOOD_AGENTS)
            (repo / "SECURITY.md").write_text(
                "## Current state\n\n"
                "There is no published release.\n",
                encoding="utf-8",
            )
            with _helpers.patched_repo_and_contract(repo, contract_path):
                ok = validate_local.check_repository_consistency(
                    self._make_args(), False
                )
                self.assertFalse(ok)
                status, group, check, message = self._last_repo_consistency_result()
                self.assertEqual(status, "FAIL")
                self.assertEqual(group, "docs")
                self.assertEqual(check, "repository-consistency")
                self.assertIn(
                    "SECURITY.md falsely claims the released baseline is absent",
                    message,
                )
                self.assertNotIn(
                    "falsely claims Android application code is absent", message
                )
                self.assertNotIn(
                    "falsely claims CI workflow is absent", message
                )


class AndroidContractNegativeTests(unittest.TestCase):
    """B5F2: when the real ``_load_release_contract`` is invoked against
    an isolated temporary fixture whose only deviation is a negative
    source-Android-manifest or a premature current application-version
    metadata value, the loader must return ``None`` and set
    ``_CONTRACT_ERROR`` to the exact concise production reason. These
    tests are regression characterization only; no production code is
    changed. The temporary fixture is constructed by
    ``_helpers.create_consistency_fixture`` and is restored to a clean
    state by ``tempfile.TemporaryDirectory`` when the test exits.
    """

    def test_malformed_source_android_manifest_fails_release_contract(self) -> None:
        """B5F2 row 18: when the temporary fixture's source
        ``app/src/main/AndroidManifest.xml`` is intentionally
        overwritten with deterministic malformed UTF-8 XML after the
        otherwise-valid consistency fixture has been constructed, the
        real ``_load_release_contract`` must return ``None`` and set
        ``_CONTRACT_ERROR`` exactly to
        ``app/src/main/AndroidManifest.xml unreadable``. No other
        fixture field is mutated. The test does not patch
        ``_load_release_contract`` and does not reproduce the
        ``ET.ParseError`` handling; the production loader owns that
        behavior."""
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo,
                RepositoryConsistencyTests.GOOD_README,
                RepositoryConsistencyTests.GOOD_PHASE_LIST,
                RepositoryConsistencyTests.GOOD_CHARTER,
            )
            manifest = repo / "app" / "src" / "main" / "AndroidManifest.xml"
            manifest.write_text("<manifest>", encoding="utf-8")
            with _helpers.patched_repo_and_contract(repo, contract_path):
                result = validate_local._load_release_contract()
                self.assertIsNone(result)
                self.assertEqual(
                    validate_local._CONTRACT_ERROR,
                    "app/src/main/AndroidManifest.xml unreadable",
                )

    def test_current_app_version_name_mismatch_fails_release_contract(self) -> None:
        """B5F2 row 19: when the temporary fixture's
        ``app/build.gradle.kts`` is intentionally overwritten so that
        the current ``versionName`` line changes from ``"0.1.1"`` to
        the premature future ``"0.1.2"`` while every other Gradle
        contract-derived field remains valid, the real
        ``_load_release_contract`` must return ``None`` and set
        ``_CONTRACT_ERROR`` to the exact concise production reason
        ``app/build.gradle.kts does not match contract: ['versionName']``.
        The test asserts the message identifies ``versionName`` and
        does NOT identify ``versionCode``, isolating the row 19
        contradiction to the current versionName. The temporary
        ``"0.1.2"`` value is used only as invalid Phase 5D boundary
        test input; the real ``app/build.gradle.kts`` is not modified.
        No production code is changed."""
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            contract_path = _helpers.create_consistency_fixture(
                repo,
                RepositoryConsistencyTests.GOOD_README,
                RepositoryConsistencyTests.GOOD_PHASE_LIST,
                RepositoryConsistencyTests.GOOD_CHARTER,
            )
            gradle = repo / "app" / "build.gradle.kts"
            gradle_text = gradle.read_text(encoding="utf-8")
            self.assertIn('versionName = "0.1.1"', gradle_text)
            bad_gradle = gradle_text.replace(
                'versionName = "0.1.1"',
                'versionName = "0.1.2"',
                1,
            )
            gradle.write_text(bad_gradle, encoding="utf-8")
            with _helpers.patched_repo_and_contract(repo, contract_path):
                result = validate_local._load_release_contract()
                self.assertIsNone(result)
                err = validate_local._CONTRACT_ERROR
                self.assertIsNotNone(err)
                self.assertIn(
                    "app/build.gradle.kts does not match contract", err or ""
                )
                self.assertIn("versionName", err or "")
                self.assertNotIn("versionCode", err or "")


if __name__ == "__main__":
    unittest.main()
