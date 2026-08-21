#!/usr/bin/env python3
"""Local validation suite for the NudgeWhen release train.

Phase 3A5 — Reusable Validator Completion. Phase 4 — Local Validation
Baseline. Python standard library only.

CLI:
  --group NAME   (repeatable; default: all contract-declared groups)
  --skip-android                        (remove android from default/all)
  --offline                             (append --offline to Gradle)
  --fail-fast                           (stop after first failed check)
  --require-clean                       (require clean non-ignored Git state)
  --help

Exit codes:
  0 — all selected checks passed
  1 — one or more validation checks failed
  2 — invocation or prerequisite error
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NS_ANDROID = "http://schemas.android.com/apk/res/android"

RELEASE_CONTRACT_PATH = REPO / "scripts/release_contract.json"

GRADLEW_BAT_EXPECTED_SHA = (
    "fedad02c18e266ec094995a5751b7fe1eb6e74f66bf75db64fae2e50eb22c234"
)

WRAPPER_JAR_EXPECTED_SHA = (
    "55243ef57851f12b070ad14f7f5bb8302daceeebc5bce5ece5fa6edb23e1145c"
)

PRIVATE_PATTERN = re.compile(r"^session-ses_[A-Za-z0-9_]+\.md$")

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

CANDIDATE_UNTRACKED_ALLOWLIST = (
    ".gitattributes",
    "scripts/validate-local.sh",
    "scripts/validate_local.py",
    "docs/local-validation.md",
    "docs/agentic-development/experiments/EXP-0007.md",
    "tests/__init__.py",
    "tests/_helpers.py",
    "tests/test_validator_core.py",
    "tests/test_validator_repository.py",
)

TEXT_EXTENSIONS = (
    ".md", ".kts", ".kt", ".xml", ".yml", ".yaml",
    ".toml", ".properties", ".sh", ".py", ".json",
)

NON_FUNCTIONALITY_CATEGORIES = (
    ("reminders", ("reminder scheduling", "reminder functionality", "reminder behavior")),
    ("notifications", ("notification scheduling", "notification channels", "notification functionality")),
    ("voice-or-speech", ("voice recording", "speech recording", "voice transcription", "speech synthesis")),
    ("location-or-geofencing", ("geofencing", "location tracking", "location functionality")),
    ("persistence", ("persistent storage of reminders", "user data persistence")),
    ("networking", ("application networking", "network requests", "http client")),
    ("background-behavior", ("background service", "background work", "background execution")),
)

_RESULTS: list[tuple[str, str, str, str]] = []
_PREREQ_FAILED = False
_CONTRACT: dict | None = None
_CONTRACT_ERROR: str | None = None
_CONTRACT_LOADED: bool = False


def emit(status: str, group: str, check: str, message: str) -> None:
    print(f"{status} {group}/{check} — {message}")
    _RESULTS.append((status, group, check, message))


def emit_prereq(check: str, message: str) -> None:
    global _PREREQ_FAILED
    emit("FAIL", "prerequisite", check, message)
    _PREREQ_FAILED = True


def git_ls_files() -> list[str]:
    r = subprocess.run(["git", "ls-files", "-z"], capture_output=True, check=True, cwd=REPO)
    return [p.decode() for p in r.stdout.split(b"\x00") if p]


def git_status_short() -> str:
    r = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        capture_output=True, text=True, cwd=REPO,
    )
    return r.stdout


def check_git_prerequisite() -> bool:
    """Verify that the git executable is resolvable from PATH.

    On success, returns True without emitting any result line. On
    failure, emits a single ``FAIL prerequisite/git`` line, sets the
    module-level prerequisite-failure flag, and returns False. The
    absolute path of the git executable is never included in the
    result message.
    """
    if shutil.which("git") is None:
        emit_prereq("git", "git executable not found")
        return False
    return True


def check_git_worktree_prerequisite() -> bool:
    """Verify that the repository root is inside a Git worktree.

    On success, returns True without emitting any result line. On
    failure, emits a single ``FAIL prerequisite/git-worktree`` line,
    sets the module-level prerequisite-failure flag, and returns False.
    The result message never includes an absolute path. The check
    handles a nonzero ``git`` exit status, an unexpected stdout value
    other than the exact worktree-positive literal, and a raised
    ``OSError`` from the subprocess call, in every case without
    propagating an exception or a Python traceback. The exact failure
    message is the constant string ``repository is not a Git worktree``.
    """
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, cwd=REPO,
        )
    except OSError:
        emit_prereq("git-worktree", "repository is not a Git worktree")
        return False
    if r.returncode != 0:
        emit_prereq("git-worktree", "repository is not a Git worktree")
        return False
    if r.stdout.strip() != "true":
        emit_prereq("git-worktree", "repository is not a Git worktree")
        return False
    return True


def parse_args(
    argv: list[str],
    groups: tuple[str, ...],
    all_alias: str,
) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="validate-local.py",
        description="Local validation suite for the NudgeWhen release train.",
    )
    p.add_argument("--group", action="append", choices=list(groups) + [all_alias])
    p.add_argument("--skip-android", action="store_true")
    p.add_argument("--offline", action="store_true")
    p.add_argument("--fail-fast", action="store_true")
    p.add_argument("--require-clean", action="store_true")
    return p.parse_args(argv)


def resolve_groups(
    args: argparse.Namespace,
    groups: tuple[str, ...],
    all_alias: str,
) -> tuple[str, ...] | int:
    selected: list[str] = []
    if args.group:
        for g in args.group:
            if g == all_alias:
                selected.extend(groups)
            else:
                selected.append(g)
    else:
        selected.extend(groups)

    if args.skip_android:
        if args.group and "android" in args.group:
            print("FAIL invocation — --skip-android combined with explicit --group android", file=sys.stderr)
            return 2
        selected = [g for g in selected if g != "android"]

    seen: set[str] = set()
    out: list[str] = []
    for g in selected:
        if g not in seen:
            out.append(g)
            seen.add(g)
    return tuple(out)


# ---------- required group ----------

REQUIRED_FILES = (
    ".gitattributes", ".gitignore", "LICENSE", "README.md",
    "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "AGENTS.md",
    "settings.gradle.kts", "build.gradle.kts", "gradle.properties",
    "gradle/libs.versions.toml",
    "gradle/wrapper/gradle-wrapper.properties", "gradle/wrapper/gradle-wrapper.jar",
    "gradlew", "gradlew.bat",
    "app/build.gradle.kts", "app/src/main/AndroidManifest.xml",
    "app/src/main/kotlin/io/github/franchoy/nudgewhen/MainActivity.kt",
    "app/src/main/kotlin/io/github/franchoy/nudgewhen/ui/theme/Theme.kt",
    "app/src/main/res/values/strings.xml", "app/src/main/res/values/themes.xml",
    "docs/releases/v0.1.0/release-charter.md", "docs/releases/v0.1.0/phase-list.md",
    "docs/agentic-development/experiment-protocol.md",
    "docs/agentic-development/evaluation-template.md",
    "docs/agentic-development/opencode-governance.md",
    "docs/agentic-development/experiments/EXP-0001.md",
    "docs/agentic-development/experiments/EXP-0002.md",
    "docs/agentic-development/experiments/EXP-0003.md",
    "docs/agentic-development/experiments/EXP-0004.md",
    "docs/agentic-development/experiments/EXP-0005.md",
    "docs/agentic-development/experiments/EXP-0006.md",
    "docs/agentic-development/experiments/EXP-0007.md",
    "scripts/validate-local.sh", "scripts/validate_local.py",
    "scripts/release_contract.json",
    "docs/local-validation.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/dependabot.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    "tests/__init__.py",
    "tests/_helpers.py",
    "tests/test_validator_core.py",
    "tests/test_validator_repository.py",
)

GITIGNORE_REQUIRED = (
    "build/", "local.properties", "*.apk", "*.aab", "*.jks", "*.keystore", "session-ses_*.md",
)

GITIGNORE_PYTHON_REQUIRED = (
    "__pycache__/",
    "*.py[cod]",
)

GITATTRIBUTES_CONTRACT = (
    "gradlew text eol=lf",
    "gradlew.bat -text",
    "gradle/wrapper/gradle-wrapper.jar binary",
    "*.sh text eol=lf",
    "*.py text eol=lf",
    "*.kt text eol=lf",
    "*.kts text eol=lf",
    "*.xml text eol=lf",
    "*.md text eol=lf",
    "*.yml text eol=lf",
    "*.yaml text eol=lf",
    "*.toml text eol=lf",
    "*.properties text eol=lf",
)

PROHIBITED_TRACKED_PREFIXES = ("app/build/", ".gradle/", ".kotlin/")


def _is_safe_repo_relative(path_str: object) -> bool:
    if not isinstance(path_str, str) or not path_str:
        return False
    if path_str.startswith("/"):
        return False
    if len(path_str) >= 2 and path_str[1] == ":":
        return False
    parts = path_str.replace("\\", "/").split("/")
    if any(p == ".." for p in parts):
        return False
    return True


def _check_release_contract_int(value: object, key: str, positive: bool = True) -> str | None:
    if not (isinstance(value, int) and not isinstance(value, bool)):
        return f"{key} must be an integer"
    if positive and value <= 0:
        return f"{key} must be a positive integer"
    return None


def _check_release_contract_doc_path(container: dict, key: str, must_be: str) -> str | None:
    val = container.get(key)
    if not isinstance(val, str) or not val:
        return f"{key} must be a non-empty string"
    if not _is_safe_repo_relative(val):
        return f"{key} is not a safe repository-relative path"
    try:
        resolved = (REPO / val).resolve()
        try:
            resolved.relative_to(REPO.resolve())
        except ValueError:
            return f"{key} resolves outside the repository"
        if must_be == "file" and not resolved.is_file():
            return f"{key} file does not exist: {val}"
        if must_be == "dir" and not resolved.is_dir():
            return f"{key} directory does not exist: {val}"
        return None
    except (OSError, RuntimeError):
        return f"{key} could not be resolved"


def _load_release_contract() -> dict | None:
    """Load and fully validate the release contract, returning the validated dict
    on success or None on failure. The result is cached at module scope so the
    contract is loaded and fully validated at most once per validator process.

    On failure, ``_CONTRACT_ERROR`` is set to a concise reason string. This
    function does not emit any result line; callers are responsible for
    emitting the appropriate PASS/FAIL.
    """
    global _CONTRACT, _CONTRACT_ERROR, _CONTRACT_LOADED
    if _CONTRACT_LOADED:
        return _CONTRACT
    _CONTRACT_LOADED = True

    if not RELEASE_CONTRACT_PATH.is_file():
        _CONTRACT_ERROR = (
            f"contract file missing: {RELEASE_CONTRACT_PATH.relative_to(REPO).as_posix()}"
        )
        return None
    try:
        raw = RELEASE_CONTRACT_PATH.read_bytes()
    except OSError as e:
        _CONTRACT_ERROR = f"contract file unreadable: {e}"
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        _CONTRACT_ERROR = f"contract file is not valid UTF-8: {e}"
        return None
    try:
        contract = json.loads(text)
    except json.JSONDecodeError as e:
        _CONTRACT_ERROR = f"contract JSON is malformed: {e}"
        return None
    if not isinstance(contract, dict):
        _CONTRACT_ERROR = "contract must be a JSON object"
        return None

    # Top level
    if contract.get("schema_version") != 1:
        _CONTRACT_ERROR = "schema_version must equal 1"
        return None
    for k in ("release", "release_documents", "phase_model", "android", "validation", "historical"):
        if not isinstance(contract.get(k), dict):
            _CONTRACT_ERROR = f"{k} must be a JSON object"
            return None

    # Release
    rel = contract["release"]
    for k in ("version", "version_name", "active_branch", "title"):
        v = rel.get(k)
        if not isinstance(v, str) or not v:
            _CONTRACT_ERROR = f"release.{k} must be a non-empty string"
            return None
    err = _check_release_contract_int(rel.get("version_code"), "release.version_code")
    if err is not None:
        _CONTRACT_ERROR = err
        return None
    if rel["version"] != "v" + rel["version_name"]:
        _CONTRACT_ERROR = "release.version must equal 'v' + release.version_name"
        return None
    if rel["active_branch"] != "release/" + rel["version"]:
        _CONTRACT_ERROR = "release.active_branch must equal 'release/' + release.version"
        return None

    # Release documents
    docs = contract["release_documents"]
    for k in ("charter", "phase_list", "local_validation"):
        err = _check_release_contract_doc_path(docs, k, "file")
        if err is not None:
            _CONTRACT_ERROR = err
            return None

    # Phase model
    pm = contract["phase_model"]
    err = _check_release_contract_int(pm.get("first_phase"), "phase_model.first_phase", positive=False)
    if err is not None:
        _CONTRACT_ERROR = err
        return None
    err = _check_release_contract_int(pm.get("last_phase"), "phase_model.last_phase", positive=False)
    if err is not None:
        _CONTRACT_ERROR = err
        return None
    if pm["first_phase"] > pm["last_phase"]:
        _CONTRACT_ERROR = "phase_model.first_phase must be <= last_phase"
        return None
    expected = pm.get("expected_statuses")
    if not isinstance(expected, dict):
        _CONTRACT_ERROR = "phase_model.expected_statuses must be an object"
        return None
    expected_keys = [f"Phase {i}" for i in range(pm["first_phase"], pm["last_phase"] + 1)]
    actual_keys = list(expected.keys())
    if actual_keys != expected_keys:
        _CONTRACT_ERROR = f"phase_model.expected_statuses keys must be {expected_keys}"
        return None
    for k in expected_keys:
        if expected[k] not in ("Complete", "Planned"):
            _CONTRACT_ERROR = f"phase_model.expected_statuses.{k} must be Complete or Planned"
            return None
    statuses = [expected[k] for k in expected_keys]
    complete_count = statuses.count("Complete")
    contiguous_complete = all(s == "Complete" for s in statuses[:complete_count])
    contiguous_planned = all(s == "Planned" for s in statuses[complete_count:])
    if not (contiguous_complete and contiguous_planned):
        _CONTRACT_ERROR = (
            "phase_model.expected_statuses must be a contiguous Complete prefix followed by a Planned suffix"
        )
        return None

    # Android
    andr = contract["android"]
    for k in (
        "namespace", "application_id", "package_name",
        "current_version_name", "target_version_name",
        "launcher_activity_source", "launcher_activity_merged",
    ):
        v = andr.get(k)
        if not isinstance(v, str) or not v:
            _CONTRACT_ERROR = f"android.{k} must be a non-empty string"
            return None
    for k in (
        "compile_sdk", "min_sdk", "target_sdk",
        "current_version_code", "target_version_code",
    ):
        err = _check_release_contract_int(andr.get(k), f"android.{k}")
        if err is not None:
            _CONTRACT_ERROR = err
            return None
    if andr["application_id"] != andr["package_name"]:
        _CONTRACT_ERROR = "android.application_id must equal android.package_name"
        return None
    if andr["target_version_code"] < andr["current_version_code"]:
        _CONTRACT_ERROR = "android.target_version_code must be >= android.current_version_code"
        return None

    # Cross-check app/build.gradle.kts
    app_gradle = REPO / "app/build.gradle.kts"
    if not app_gradle.is_file():
        _CONTRACT_ERROR = "app/build.gradle.kts is missing"
        return None
    try:
        gradle_text = app_gradle.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        _CONTRACT_ERROR = "app/build.gradle.kts unreadable"
        return None
    gradle_expectations = [
        ("namespace", f'namespace = "{andr["namespace"]}"'),
        ("applicationId", f'applicationId = "{andr["application_id"]}"'),
        ("compileSdk", f"compileSdk = {andr['compile_sdk']}"),
        ("minSdk", f"minSdk = {andr['min_sdk']}"),
        ("targetSdk", f"targetSdk = {andr['target_sdk']}"),
        ("versionCode", f"versionCode = {andr['current_version_code']}"),
        ("versionName", f'versionName = "{andr["current_version_name"]}"'),
    ]
    bad = [name for name, expected_str in gradle_expectations if expected_str not in gradle_text]
    if bad:
        _CONTRACT_ERROR = f"app/build.gradle.kts does not match contract: {bad}"
        return None

    # Cross-check AndroidManifest.xml
    manifest_path = REPO / "app/src/main/AndroidManifest.xml"
    if not manifest_path.is_file():
        _CONTRACT_ERROR = "app/src/main/AndroidManifest.xml is missing"
        return None
    try:
        tree = ET.parse(manifest_path)
    except (OSError, ET.ParseError):
        _CONTRACT_ERROR = "app/src/main/AndroidManifest.xml unreadable"
        return None
    expected_activity_name = andr["launcher_activity_source"]
    found_activity = False
    for activity in tree.getroot().iter("activity"):
        if activity.get(f"{{{NS_ANDROID}}}name") == expected_activity_name:
            found_activity = True
            break
    if not found_activity:
        _CONTRACT_ERROR = (
            f"AndroidManifest.xml has no activity with android:name {expected_activity_name!r}"
        )
        return None

    # Validation
    val = contract["validation"]
    if not isinstance(val, dict):
        _CONTRACT_ERROR = "validation must be a JSON object"
        return None

    # validation.groups
    groups_val = val.get("groups")
    if not isinstance(groups_val, list) or not groups_val:
        _CONTRACT_ERROR = "validation.groups must be a non-empty list"
        return None
    if not all(isinstance(g, str) and g for g in groups_val):
        _CONTRACT_ERROR = "validation.groups must contain only non-empty strings"
        return None
    if len(set(groups_val)) != len(groups_val):
        _CONTRACT_ERROR = "validation.groups identifiers must be unique"
        return None
    unknown_groups = [g for g in groups_val if g not in VALIDATION_HANDLERS]
    if unknown_groups:
        _CONTRACT_ERROR = (
            f"validation.groups identifiers not in registry: {unknown_groups}"
        )
        return None

    # validation.all_alias
    all_alias = val.get("all_alias")
    if not isinstance(all_alias, str) or not all_alias:
        _CONTRACT_ERROR = "validation.all_alias must be a non-empty string"
        return None
    if all_alias in groups_val:
        _CONTRACT_ERROR = "validation.all_alias must not equal any real group identifier"
        return None

    # validation.release_gate_requires_groups
    rg_groups = val.get("release_gate_requires_groups")
    if not isinstance(rg_groups, list) or not rg_groups:
        _CONTRACT_ERROR = "validation.release_gate_requires_groups must be a non-empty list"
        return None
    if not all(isinstance(g, str) and g for g in rg_groups):
        _CONTRACT_ERROR = (
            "validation.release_gate_requires_groups must contain only non-empty strings"
        )
        return None
    if len(set(rg_groups)) != len(rg_groups):
        _CONTRACT_ERROR = "validation.release_gate_requires_groups identifiers must be unique"
        return None
    missing_in_groups = [g for g in rg_groups if g not in groups_val]
    if missing_in_groups:
        _CONTRACT_ERROR = (
            "validation.release_gate_requires_groups contains identifiers not in validation.groups: "
            f"{missing_in_groups}"
        )
        return None

    # Android gate flag
    android_flag = val.get("release_gate_requires_android_not_skipped")
    if not isinstance(android_flag, bool):
        _CONTRACT_ERROR = "validation.release_gate_requires_android_not_skipped must be a Boolean"
        return None
    if android_flag:
        if "android" not in groups_val:
            _CONTRACT_ERROR = (
                "validation.release_gate_requires_android_not_skipped is true but 'android' "
                "is not in validation.groups"
            )
            return None
        if "android" not in rg_groups:
            _CONTRACT_ERROR = (
                "validation.release_gate_requires_android_not_skipped is true but 'android' "
                "is not in validation.release_gate_requires_groups"
            )
            return None

    for k in (
        "require_clean_supported",
        "no_network",
        "no_dependency_installation",
    ):
        if val.get(k) is not True:
            _CONTRACT_ERROR = f"validation.{k} must be true"
            return None

    # Historical
    hist = contract["historical"]
    for k in ("previous_release_version", "previous_release_docs_root"):
        v = hist.get(k)
        if not isinstance(v, str) or not v:
            _CONTRACT_ERROR = f"historical.{k} must be a non-empty string"
            return None
    if hist.get("previous_release_is_historical") is not True:
        _CONTRACT_ERROR = "historical.previous_release_is_historical must be true"
        return None
    err = _check_release_contract_doc_path(hist, "previous_release_docs_root", "dir")
    if err is not None:
        _CONTRACT_ERROR = err
        return None

    _CONTRACT = contract
    _CONTRACT_ERROR = None
    return _CONTRACT


def get_release_contract() -> dict | None:
    """Return the cached validated release contract, loading and validating it
    on first call. Returns None if the contract failed to load or validate.

    This accessor does not emit any result line. Callers that need a
    prerequisite failure should also call ``get_release_contract_error`` and
    emit the FAIL only when no prerequisite has already been emitted.
    """
    return _load_release_contract()


def get_release_contract_error() -> str | None:
    """Return the concise error string from the most recent contract load
    attempt, or None if the contract loaded successfully or has not been
    attempted yet. Triggers a load attempt if one has not yet occurred.
    """
    if not _CONTRACT_LOADED:
        _load_release_contract()
    return _CONTRACT_ERROR


def check_release_contract(args: argparse.Namespace, fail_fast: bool) -> bool:
    del args, fail_fast  # contract check is unconditional
    contract = _load_release_contract()
    if contract is None:
        emit_prereq("release-contract", _CONTRACT_ERROR or "contract load failed")
        return False
    emit("PASS", "required", "release-contract", "release contract loaded and validated")
    return True


def check_required(args: argparse.Namespace, fail_fast: bool) -> bool:
    ok = True
    tracked = set(git_ls_files())
    clean_mode = args.require_clean

    if not check_release_contract(args, fail_fast):
        return False

    for rel in REQUIRED_FILES:
        if clean_mode:
            present = rel in tracked
        else:
            present = rel in tracked or (REPO / rel).is_file()
        if not present:
            emit("FAIL", "required", "files", f"missing required file: {rel}")
            ok = False
            if fail_fast:
                return False
    if ok:
        label = "all required files present (tracked)" if clean_mode else "all required files present"
        emit("PASS", "required", "files", label)

    # Bounded Dependabot configuration check (Phase 5C). Runs only
    # after the required-file presence check has established that
    # .github/dependabot.yml exists in the working tree. Uses the
    # production _dependabot_failures helper as the single source of
    # truth for the bounded Dependabot policy. No YAML dependency
    # is introduced; the helper is a bounded line/indentation parser.
    dependabot_path = REPO / ".github/dependabot.yml"
    if dependabot_path.is_file():
        dependabot_text = dependabot_path.read_text(encoding="utf-8")
        dependabot_bad = _dependabot_failures(dependabot_text)
        if dependabot_bad:
            emit(
                "FAIL", "required", "dependabot-yaml",
                "; ".join(dependabot_bad),
            )
            ok = False
            if fail_fast:
                return False
        else:
            emit(
                "PASS", "required", "dependabot-yaml",
                "Dependabot configuration verified",
            )

    for rel in tracked:
        base = rel.split("/")[-1]
        if base == "local.properties":
            emit("FAIL", "required", "no-local-properties", f"tracked: {rel}")
            ok = False
            if fail_fast: return False
        if base.endswith(".apk") or base.endswith(".aab"):
            emit("FAIL", "required", "no-apk-aab", f"tracked build artifact: {rel}")
            ok = False
            if fail_fast: return False
        if PRIVATE_PATTERN.match(base):
            emit("FAIL", "required", "no-private-export", f"tracked private-session export: {rel}")
            ok = False
            if fail_fast: return False
        if rel.startswith(PROHIBITED_TRACKED_PREFIXES):
            emit("FAIL", "required", "no-build-output", f"tracked build output: {rel}")
            ok = False
            if fail_fast: return False
        if base.lower().endswith((".png", ".jpg", ".jpeg")):
            emit("FAIL", "required", "no-screenshot", f"tracked screenshot: {rel}")
            ok = False
            if fail_fast: return False
        if (
            base.endswith(".pyc")
            or base.endswith(".pyo")
            or base.endswith(".pyd")
            or "__pycache__" in rel.split("/")
        ):
            emit("FAIL", "required", "no-bytecode", f"tracked bytecode: {rel}")
            ok = False
            if fail_fast: return False
    if ok:
        emit("PASS", "required", "no-prohibited", "no tracked local.properties, APK/AAB, build output, screenshot, bytecode, or private-session export")

    gradlew_mode = subprocess.run(["git", "ls-files", "-s", "gradlew"], capture_output=True, text=True, cwd=REPO).stdout.split()
    if gradlew_mode and gradlew_mode[0] == "100755":
        emit("PASS", "required", "gradlew-exec", "gradlew is executable in Git")
    else:
        emit("FAIL", "required", "gradlew-exec", f"gradlew is not executable in Git: {gradlew_mode}")
        ok = False
        if fail_fast: return False

    if clean_mode:
        shell_mode = subprocess.run(["git", "ls-files", "-s", "scripts/validate-local.sh"], capture_output=True, text=True, cwd=REPO).stdout.split()
        if shell_mode and shell_mode[0] == "100755":
            emit("PASS", "required", "shell-exec", "validate-local.sh is executable in Git")
        else:
            emit("FAIL", "required", "shell-exec", f"validate-local.sh not executable in Git: {shell_mode}")
            ok = False
            if fail_fast: return False
    else:
        shell = REPO / "scripts/validate-local.sh"
        if shell.is_file() and os.access(shell, os.X_OK):
            emit("PASS", "required", "shell-exec", "validate-local.sh is executable in working tree")
        else:
            emit("FAIL", "required", "shell-exec", "validate-local.sh not executable in working tree")
            ok = False
            if fail_fast: return False

    jar = REPO / "gradle/wrapper/gradle-wrapper.jar"
    if jar.is_file() and jar.stat().st_size > 0:
        emit("PASS", "required", "wrapper-jar", "wrapper JAR is non-empty")
        jar_hash = hashlib.sha256(jar.read_bytes()).hexdigest()
        if jar_hash == WRAPPER_JAR_EXPECTED_SHA:
            emit("PASS", "required", "wrapper-jar-sha256", "wrapper JAR SHA-256 verified")
        else:
            emit("FAIL", "required", "wrapper-jar-sha256", f"unexpected SHA-256: {jar_hash}")
            ok = False
            if fail_fast: return False
    else:
        emit("FAIL", "required", "wrapper-jar", "wrapper JAR missing or empty")
        ok = False
        if fail_fast: return False

    gitignore = REPO / ".gitignore"
    if gitignore.is_file():
        text = gitignore.read_text(encoding="utf-8")
        missing = [r for r in GITIGNORE_REQUIRED if r not in text]
        if missing:
            emit("FAIL", "required", "gitignore", f"missing rules: {', '.join(missing)}")
            ok = False
            if fail_fast: return False
        else:
            emit("PASS", "required", "gitignore", "all required rules present")
            missing_py = [r for r in GITIGNORE_PYTHON_REQUIRED if r not in text]
            if missing_py:
                emit("FAIL", "required", "gitignore-python", f"missing rules: {', '.join(missing_py)}")
                ok = False
                if fail_fast: return False
            else:
                emit("PASS", "required", "gitignore-python", "Python bytecode ignore rules present")
    else:
        emit("FAIL", "required", "gitignore", ".gitignore missing")
        ok = False
        if fail_fast: return False

    gitattr = REPO / ".gitattributes"
    if gitattr.is_file():
        text = gitattr.read_text(encoding="utf-8")
        nonblank = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if nonblank == list(GITATTRIBUTES_CONTRACT):
            emit("PASS", "required", "gitattributes", "contract enforced exactly")
        else:
            extras = [ln for ln in nonblank if ln not in GITATTRIBUTES_CONTRACT]
            missing = [r for r in GITATTRIBUTES_CONTRACT if r not in nonblank]
            emit("FAIL", "required", "gitattributes", f"missing: {missing}; extras: {extras}")
            ok = False
            if fail_fast: return False
    else:
        emit("FAIL", "required", "gitattributes", ".gitattributes missing")
        ok = False
        if fail_fast: return False

    return ok


# ---------- docs group ----------

EVAL_TEMPLATE_PLACEHOLDERS = (
    "Not available", "Not applicable", "Pending maintainer input",
    "<value>", "<identifier>", "<free text", "<variant or `None`>",
    "<source name>", "<ISO-8601 timestamp(s)>", "<commit, message, or document>",
    "<list of files the task was authorized to create or modify>",
    "<list of files and actions the task was not authorized to perform>",
    "<list of commands the task was required to run>",
    "<list or `None`>", "<owner>/<name>", "<branch>", "<full SHA>",
    "<full SHA, or `Not applicable` when no commit is produced by this experiment>",
    "<display string or `Pending maintainer input`>", "<display string>",
    "<exact stdout of `opencode --version`, or `Not available` with explanation>",
    "<value, or `Not available` with explanation>",
    "<value and unit, or `Not computable` with explanation, or `Pending maintainer input`>",
    "<unit>", "<one bullet per missing field>", "<one sentence>", "<integer>",
    "<free text describing how events were grouped>", "<bulleted list>",
    "`Successful first pass`, `Successful with correction`, `Partially successful`, `Unsuccessful`, `Blocked by environment`, `Blocked by specification`",
)

RESERVED_INVALID_ADDRESSES = ("validation@invalid.example",)

PROHIBITED_PLACEHOLDER_LITERALS = ("<sdk>", "TBD", "to be filled", "to be filled at Build time")
BARE_PENDING_PATTERN = re.compile(r"(?<![A-Za-z])pending(?! maintainer)(?![A-Za-z])")


def candidate_inventory(args: argparse.Namespace) -> list[Path]:
    seen: set[str] = set()
    out: list[Path] = []
    for rel in git_ls_files():
        if rel in seen:
            continue
        seen.add(rel)
        p = REPO / rel
        if p.is_file():
            out.append(p)
    if not args.require_clean:
        for rel in CANDIDATE_UNTRACKED_ALLOWLIST:
            p = REPO / rel
            if p.is_file() and p.as_posix() not in {x.as_posix() for x in out}:
                out.append(p)
    return out


def iter_text_files(inventory: list[Path]) -> list[Path]:
    return [p for p in inventory if p.suffix in TEXT_EXTENSIONS]


def resolve_md_link(target_raw: str) -> tuple[bool, bool, str]:
    """Return (is_filesystem, is_root_relative, resolved_path_string)."""
    target_raw = target_raw.strip()
    if not target_raw:
        return False, False, ""
    if "://" in target_raw:
        return False, False, ""
    if target_raw.startswith("#"):
        return False, False, ""
    parts = target_raw.split()
    first = parts[0]
    is_root = first.startswith("/")
    if "#" in first:
        first = first.split("#", 1)[0]
    if not first:
        return False, False, ""
    return True, is_root, first


def check_repository_consistency(args: argparse.Namespace, fail_fast: bool) -> bool:
    """Cohesive repository-consistency check for active release identity.

    Uses the already-loaded release contract to derive the active release
    version, the active release branch, and the previous release version.
    Operates on repository files through REPO-relative paths, emits
    deterministic PASS/FAIL output, respects fail_fast, and returns a
    boolean compatible with the existing validator architecture.

    The check distinguishes active declarations (the specific declarative
    sentences that assert the project's current release identity) from
    historical narrative references (mentions of previous releases in
    context such as "v0.1.0 phases (historical, complete):" or
    "v0.1.0 release is complete and historical"). A legitimate
    historical mention in a current document does not fail; only a
    stale active declaration fails.
    """
    del args  # no group-specific arguments required
    contract = get_release_contract()
    if contract is None:
        if not _PREREQ_FAILED:
            err = get_release_contract_error() or "contract load failed"
            emit_prereq("release-contract", err)
        return False

    active_version = contract["release"]["version"]
    active_branch = contract["release"]["active_branch"]
    historical_version = contract["historical"]["previous_release_version"]

    failures: list[str] = []

    # 1. README active release version declaration.
    readme = REPO / "README.md"
    if readme.is_file():
        try:
            readme_text = readme.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            failures.append("README.md is not readable as UTF-8")
            readme_text = ""
        if readme_text:
            m = re.search(
                r"is currently in the `([^`]+)` release train",
                readme_text,
            )
            if m is None:
                failures.append(
                    "README lacks 'is currently in the X release train' declaration"
                )
            elif m.group(1) != active_version:
                failures.append(
                    f"README active version declaration is '{m.group(1)}' "
                    f"but contract requires '{active_version}'"
                )

            m = re.search(
                r"The current active branch is `([^`]+)`",
                readme_text,
            )
            if m is None:
                failures.append(
                    "README lacks 'the current active branch is X' declaration"
                )
            elif m.group(1) != active_branch:
                failures.append(
                    f"README active branch declaration is '{m.group(1)}' "
                    f"but contract requires '{active_branch}'"
                )
    else:
        failures.append("README.md is missing")

    # 2. Phase-list document title.
    phase_list_rel = contract["release_documents"]["phase_list"]
    phase_list = REPO / phase_list_rel
    if phase_list.is_file():
        try:
            phase_list_text = phase_list.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            failures.append(f"{phase_list_rel} is not readable as UTF-8")
            phase_list_text = ""
        if phase_list_text:
            m = re.search(
                r"^# Phase List — NudgeWhen (\S+)\s*$",
                phase_list_text,
                flags=re.M,
            )
            if m is None:
                failures.append(
                    f"{phase_list_rel} lacks '# Phase List — NudgeWhen X' title"
                )
            elif m.group(1) != active_version:
                failures.append(
                    f"{phase_list_rel} title identifies '{m.group(1)}' "
                    f"but contract requires '{active_version}'"
                )
    else:
        failures.append(f"{phase_list_rel} is missing")

    # 3. Release-charter document title (must not present historical as active).
    charter_rel = contract["release_documents"]["charter"]
    charter = REPO / charter_rel
    if charter.is_file():
        try:
            charter_text = charter.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            failures.append(f"{charter_rel} is not readable as UTF-8")
            charter_text = ""
        if charter_text:
            m = re.search(
                r"^# Release Charter — NudgeWhen (\S+)\s*$",
                charter_text,
                flags=re.M,
            )
            if m is None:
                failures.append(
                    f"{charter_rel} lacks '# Release Charter — NudgeWhen X' title"
                )
            elif m.group(1) != active_version:
                if m.group(1) == historical_version:
                    failures.append(
                        f"{charter_rel} title identifies historical release "
                        f"'{m.group(1)}' as if it were active; "
                        f"contract requires '{active_version}'"
                    )
                else:
                    failures.append(
                        f"{charter_rel} title identifies '{m.group(1)}' "
                        f"but contract requires '{active_version}'"
                    )
    else:
        failures.append(f"{charter_rel} is missing")

    # 4. Document-status phase-progress summary (B5A).
    # The authoritative phase state comes only from
    # contract["phase_model"]["expected_statuses"]. The contract loader
    # already guarantees a contiguous Complete prefix followed by a
    # Planned suffix, so the highest completed phase is found by scanning
    # the inclusive numeric range [first_phase, last_phase] in order and
    # stopping at the first non-Complete entry.
    phase_model = contract["phase_model"]
    first_phase = phase_model["first_phase"]
    last_phase = phase_model["last_phase"]
    expected_statuses = phase_model["expected_statuses"]
    last_complete = first_phase - 1
    for n in range(first_phase, last_phase + 1):
        if expected_statuses[f"Phase {n}"] == "Complete":
            last_complete = n
        else:
            break
    if last_complete >= first_phase:
        expected_completed_phrase = (
            f"Phases {first_phase} through {last_complete} complete"
        )
    else:
        expected_completed_phrase = "(no phases complete)"

    def _check_doc_status_summary(rel_path: str, text: str) -> None:
        if not text:
            return
        sm = re.search(
            r"^\*\*Document status:\*\*\s*(.+?)\s*$",
            text,
            flags=re.M,
        )
        if sm is None:
            failures.append(
                f"{rel_path} lacks **Document status:** declaration"
            )
            return
        summary_text = sm.group(1).strip()
        claim_match = re.search(
            r"Phases?\s+(\d+)\s+through\s+(\d+)\s+complete",
            summary_text,
        )
        if claim_match is None:
            observed_claim = "(no completed-range claim)"
        else:
            observed_claim = (
                f"Phases {claim_match.group(1)} through "
                f"{claim_match.group(2)} complete"
            )
        if observed_claim != expected_completed_phrase:
            failures.append(
                f"{rel_path} document-status summary is "
                f"'{summary_text}'; observed completed-range claim is "
                f"'{observed_claim}' but contract requires "
                f"'{expected_completed_phrase}'"
            )

    _check_doc_status_summary(phase_list_rel, phase_list_text)
    _check_doc_status_summary(charter_rel, charter_text)

    # 5. Persistent CI workflow consistency (B5B).
    # Inspects only .github/workflows/ci.yml using narrowly targeted
    # deterministic text/regular-expression checks matched to the
    # current workflow layout. Verifies exactly five stable CI
    # invariants: release/** push coverage, main push coverage,
    # main pull_request coverage, workflow_dispatch presence, and
    # jobs.validate presence. Does not implement a generic YAML
    # parser and does not contact GitHub or execute CI.
    ci_path = REPO / ".github/workflows/ci.yml"
    ci_text = ""
    if ci_path.is_file():
        try:
            ci_text = ci_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            ci_text = ""
    # B5C: bounded malformed CI/YAML required structure.
    # Verifies that the persistent CI workflow owns a top-level
    # ``on:`` mapping. Removing only the ``on:`` line while leaving
    # the trigger entries textually present would otherwise leave
    # the existing B5B checks all satisfied, so this invariant
    # characterizes a representative malformed required workflow
    # structure. Not a generic YAML parser.
    if not re.search(
        r"^on:\s*$",
        ci_text, flags=re.M,
    ):
        failures.append("CI workflow lacks top-level on mapping")
    if not re.search(
        r"^  push:\s*\n[ \t]+branches:\s*\n[ \t]+-[ \t]+release/\*\*\s*$",
        ci_text, flags=re.M,
    ):
        failures.append("CI workflow lacks push coverage for release/**")
    push_section = re.search(
        r"^  push:\s*\n((?:[ \t]{4,}[^\n]*\n)*)",
        ci_text, flags=re.M,
    )
    if not push_section or not re.search(
        r"^[ \t]+-[ \t]+main\s*$",
        push_section.group(1), flags=re.M,
    ):
        failures.append("CI workflow lacks push coverage for main")
    pull_request_section = re.search(
        r"^  pull_request:\s*\n((?:[ \t]{4,}[^\n]*\n)*)",
        ci_text, flags=re.M,
    )
    if not pull_request_section or not re.search(
        r"^[ \t]+-[ \t]+main\s*$",
        pull_request_section.group(1), flags=re.M,
    ):
        failures.append("CI workflow lacks pull_request coverage for main")
    if not re.search(
        r"^  workflow_dispatch:\s*$",
        ci_text, flags=re.M,
    ):
        failures.append("CI workflow lacks workflow_dispatch")
    jobs_section = re.search(
        r"^jobs:\s*\n((?:[ \t]+[^\n]*\n)*)",
        ci_text, flags=re.M,
    )
    if not jobs_section or not re.search(
        r"^  validate:\s*$",
        jobs_section.group(1), flags=re.M,
    ):
        failures.append("CI workflow lacks stable validate job")
    # B5C: bounded stable ``validate`` job display name. The display
    # name must belong to the ``validate`` job, not the file as a
    # whole. Derive the ``validate`` job body from the already-derived
    # ``jobs_section`` and require the literal child name
    # ``name: validate``. No generic YAML parser.
    validate_job = None
    if jobs_section:
        validate_job = re.search(
            r"^  validate:\s*\n((?:[ \t]{4,}[^\n]*\n)*)",
            jobs_section.group(1),
            flags=re.M,
        )
    if not validate_job or not re.search(
        r"^    name:\s*validate\s*$",
        validate_job.group(1) if validate_job else "",
        flags=re.M,
    ):
        failures.append("CI workflow validate job display name is not 'validate'")
    # B5C: bounded read-only ``contents`` permission at the top level.
    # Verifies the persistent CI workflow declares
    # ``permissions: contents: read`` so the validate job receives
    # read-only token scope. Not a remote GitHub permissions check.
    permissions_section = re.search(
        r"^permissions:\s*\n((?:[ \t]+[^\n]*\n)*)",
        ci_text,
        flags=re.M,
    )
    if not permissions_section or not re.search(
        r"^  contents:\s*read\s*$",
        permissions_section.group(1),
        flags=re.M,
    ):
        failures.append("CI workflow lacks read-only contents permission")

    # 6. AGENTS.md current-release-context active declarations (B5D).
    # AGENTS.md is the authoritative repository-local operational
    # contract. The bounded check inspects only the
    # ``## Current release context`` section and verifies the two
    # declarative active fields there. Historical narrative references
    # elsewhere in AGENTS.md, including historical release narrative
    # inside the terminated bootstrap-exception record, remain legal.
    # A historical value placed in an active field fails. No current
    # phase or current branch generation check is added.
    agents_path = REPO / "AGENTS.md"
    agents_text: str | None = None
    if not agents_path.is_file():
        failures.append("AGENTS.md is missing")
    else:
        try:
            agents_text = agents_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            failures.append("AGENTS.md is not readable as UTF-8")

    if agents_text is not None:
        section_match = re.search(
            r"^## Current release context\s*\n",
            agents_text,
            flags=re.M,
        )
        if section_match is None:
            failures.append(
                "AGENTS.md lacks '## Current release context' section"
            )
        else:
            section_start = section_match.end()
            next_heading = re.search(
                r"^## [^#].*$",
                agents_text[section_start:],
                flags=re.M,
            )
            if next_heading is None:
                section_text = agents_text[section_start:]
            else:
                section_text = agents_text[
                    section_start : section_start + next_heading.start()
                ]
            active_release_match = re.search(
                r"^- \*\*Active release:\*\*\s*`([^`]+)`\s*$",
                section_text,
                flags=re.M,
            )
            if active_release_match is None:
                failures.append(
                    "AGENTS current release context lacks Active release declaration"
                )
            else:
                observed_release = active_release_match.group(1)
                if observed_release == historical_version:
                    failures.append(
                        f"AGENTS current release context identifies "
                        f"historical release '{observed_release}' as active; "
                        f"contract requires '{active_version}'"
                    )
                elif observed_release != active_version:
                    failures.append(
                        f"AGENTS current release context active release is "
                        f"'{observed_release}' but contract requires "
                        f"'{active_version}'"
                    )
            active_branch_match = re.search(
                r"^- \*\*Active branch:\*\*\s*`([^`]+)`\s*$",
                section_text,
                flags=re.M,
            )
            historical_branch = f"release/{historical_version}"
            if active_branch_match is None:
                failures.append(
                    "AGENTS current release context lacks Active branch declaration"
                )
            else:
                observed_branch = active_branch_match.group(1)
                if observed_branch == historical_branch:
                    failures.append(
                        f"AGENTS current release context identifies "
                        f"historical branch '{observed_branch}' as active; "
                        f"contract requires '{active_branch}'"
                    )
                elif observed_branch != active_branch:
                    failures.append(
                        f"AGENTS current release context active branch is "
                        f"'{observed_branch}' but contract requires "
                        f"'{active_branch}'"
                    )

    # 7. B5E current-facing false-absence contradiction scan.
    # Inspects exactly three current-facing documents for the three
    # historical stale-absence concepts owned by this slice: Android
    # application code absent, CI workflow absent, and published or
    # released baseline absent. Missing current-facing files are owned
    # by the existing required/files contract and are not duplicated
    # here. Files that exist but cannot be read as UTF-8 fail closed.
    # Not a generic natural-language truth checker; not a historical
    # document scan; not a production-readiness or product-feature
    # absence check.
    current_state_paths = (
        "README.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
    )
    b5e_android_absence = re.compile(
        r"\bno\s+Android\s+application\s+code\b", re.I,
    )
    b5e_ci_absence = re.compile(
        r"\bno\s+CI\s+workflow\b", re.I,
    )
    b5e_release_absence = (
        re.compile(r"\bno\s+published\s+release\b", re.I),
        re.compile(r"\bno\s+released\s+or\s+runnable\s+application\b", re.I),
    )
    for b5e_rel in current_state_paths:
        b5e_path = REPO / b5e_rel
        if not b5e_path.is_file():
            continue
        try:
            b5e_text = b5e_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            failures.append(
                f"{b5e_rel} is not readable as UTF-8 for "
                f"current-state consistency"
            )
            continue
        if b5e_android_absence.search(b5e_text):
            failures.append(
                f"{b5e_rel} falsely claims Android application code is absent"
            )
        if b5e_ci_absence.search(b5e_text):
            failures.append(
                f"{b5e_rel} falsely claims CI workflow is absent"
            )
        for b5e_release_pat in b5e_release_absence:
            if b5e_release_pat.search(b5e_text):
                failures.append(
                    f"{b5e_rel} falsely claims the released baseline is absent"
                )
                break

    if failures:
        emit("FAIL", "docs", "repository-consistency", "; ".join(failures))
        return False

    emit(
        "PASS",
        "docs",
        "repository-consistency",
        f"active release identity consistent "
        f"(version='{active_version}', branch='{active_branch}')",
    )
    return True


def check_docs(args: argparse.Namespace, fail_fast: bool) -> bool:
    ok = True
    inventory = candidate_inventory(args)
    text_files = iter_text_files(inventory)

    for p in text_files:
        try:
            p.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            emit("FAIL", "docs", "utf8", f"not UTF-8: {p.relative_to(REPO)}")
            ok = False
            if fail_fast: return False
    if ok:
        emit("PASS", "docs", "utf8", "all candidate text files are valid UTF-8")

    for p in text_files:
        if p.name == "gradlew.bat":
            continue
        text = p.read_text(encoding="utf-8")
        if re.search(r"[ \t]+(?:\r\n|\n)", text):
            emit("FAIL", "docs", "trailing-ws", f"trailing whitespace in {p.relative_to(REPO)}")
            ok = False
            if fail_fast: return False
    if ok:
        emit("PASS", "docs", "trailing-ws", "no trailing whitespace in candidate text files")

    gradlew_bat = REPO / "gradlew.bat"
    if gradlew_bat.is_file():
        data = gradlew_bat.read_bytes()
        h = hashlib.sha256(data).hexdigest()
        if h != GRADLEW_BAT_EXPECTED_SHA:
            emit("FAIL", "docs", "gradlew-bat-hash", f"unexpected SHA-256: {h}")
            ok = False
        elif b"\r\n" not in data:
            emit("FAIL", "docs", "gradlew-bat-crlf", "no CRLF sequences"); ok = False
        elif data.replace(b"\r\n", b"").count(b"\r") > 0:
            emit("FAIL", "docs", "gradlew-bat-crlf", "lone CR present"); ok = False
        elif data.replace(b"\r\n", b"").count(b"\n") > 0:
            emit("FAIL", "docs", "gradlew-bat-crlf", "lone LF present"); ok = False
        elif b"\x00" in data:
            emit("FAIL", "docs", "gradlew-bat-crlf", "NUL byte present"); ok = False
        else:
            emit("PASS", "docs", "gradlew-bat-crlf", "gradlew.bat CRLF structure and SHA-256 verified")
    else:
        emit("FAIL", "docs", "gradlew-bat-crlf", "gradlew.bat missing")
        ok = False

    if not ok and fail_fast: return False

    md_files = [p for p in text_files if p.suffix == ".md"]
    link_re = re.compile(r"\]\(([^)]+)\)")
    for p in md_files:
        text = p.read_text(encoding="utf-8")
        for m in link_re.finditer(text):
            is_fs, is_root, target = resolve_md_link(m.group(1))
            if not is_fs:
                continue
            if is_root:
                resolved = (REPO / target.lstrip("/")).resolve()
            else:
                resolved = (p.parent / target).resolve()
            try:
                resolved.relative_to(REPO.resolve())
            except ValueError:
                emit("FAIL", "docs", "md-links", f"link escapes repo: {p.relative_to(REPO)} -> {target}")
                ok = False
                if fail_fast: return False
                continue
            if not resolved.exists():
                emit("FAIL", "docs", "md-links", f"broken link in {p.relative_to(REPO)}: {target}")
                ok = False
                if fail_fast: return False
    if ok:
        emit("PASS", "docs", "md-links", "all relative Markdown links resolve")

    # Load the contract silently for the remaining contract-driven docs checks.
    # A successful load must not add a result line; a failure must emit exactly
    # one prerequisite FAIL (only if no prerequisite has already been emitted).
    contract = get_release_contract()
    if contract is None:
        if not _PREREQ_FAILED:
            err = get_release_contract_error() or "contract load failed"
            emit_prereq("release-contract", err)
        return False

    # Active phase list wiring (contract-driven)
    phase_list_rel = contract["release_documents"]["phase_list"]
    phase_list = REPO / phase_list_rel
    first_phase = contract["phase_model"]["first_phase"]
    last_phase = contract["phase_model"]["last_phase"]
    expected_range = list(range(first_phase, last_phase + 1))
    phase_nums: list[int] = []
    if phase_list.is_file():
        text = phase_list.read_text(encoding="utf-8")
        phase_nums = [int(x) for x in re.findall(r"^## Phase (\d+) — .*$", text, flags=re.M)]
    if phase_nums != expected_range:
        emit("FAIL", "docs", "phase-headings", f"unexpected heading order: {phase_nums}")
        ok = False
        if fail_fast: return False
    else:
        emit("PASS", "docs", "phase-headings", f"Phase {first_phase}–{last_phase} headings ordered and unique")

    if not ok and fail_fast: return False

    # Active phase status wiring (contract-driven, bounded per phase section).
    # Each expected phase obtains its status exclusively from its own bounded
    # section, defined as beginning at the phase heading and ending immediately
    # before the next "## Phase N — ..." heading (EOF for the last phase). A
    # missing status in one phase is never borrowed from a later phase.
    expected_statuses = contract["phase_model"]["expected_statuses"]
    SUPPORTED_STATUSES = ("Complete", "Planned")
    phase_status: dict[int, str] = {}
    missing_status: list[int] = []
    duplicate_status: list[str] = []
    unsupported_status: list[str] = []
    mismatched_status: list[str] = []

    if phase_list.is_file():
        text = phase_list.read_text(encoding="utf-8")
        # Identify all active phase-heading matches and their character positions.
        all_headings: list[tuple[int, int]] = []
        for hm in re.finditer(r"^## Phase (\d+) — .*$", text, flags=re.M):
            all_headings.append((int(hm.group(1)), hm.start()))
        all_headings.sort(key=lambda x: x[1])

        status_heading_re = re.compile(r"^### Status\s*$", flags=re.M)

        for n in expected_range:
            # Locate the heading for phase n.
            start_idx: int | None = None
            for pn, pos in all_headings:
                if pn == n:
                    start_idx = pos
                    break
            if start_idx is None:
                missing_status.append(n)
                continue

            # End the section immediately before the next phase heading; EOF for the last phase.
            end_idx = len(text)
            for pn, pos in all_headings:
                if pos > start_idx:
                    end_idx = pos
                    break

            section = text[start_idx:end_idx]

            # Require exactly one `### Status` heading within the bounded section.
            status_matches = list(status_heading_re.finditer(section))
            if len(status_matches) == 0:
                missing_status.append(n)
                continue
            if len(status_matches) > 1:
                duplicate_status.append(f"Phase {n}: {len(status_matches)} ### Status headings")
                continue

            # Bound the status subsection: begin immediately after the single
            # `### Status` heading and end immediately before the next Markdown
            # heading of any level (`#` through `######`) within the phase
            # section, or at the phase-section end when no later heading exists.
            sub_start = status_matches[0].end()
            sub_end = len(section)
            any_heading_re = re.compile(r"^#{1,6}\s+\S", flags=re.M)
            for hm in any_heading_re.finditer(section, pos=sub_start):
                sub_end = hm.start()
                break
            status_block = section[sub_start:sub_end]

            # Within the bounded status subsection require exactly one
            # unformatted, nonblank value line.
            value_lines: list[str] = [
                ln.strip() for ln in status_block.splitlines() if ln.strip()
            ]
            if len(value_lines) == 0:
                missing_status.append(n)
                continue
            if len(value_lines) > 1:
                duplicate_status.append(f"Phase {n}: {len(value_lines)} status values")
                continue

            value = value_lines[0]
            # Accept only the exact unformatted status literals supported by
            # the validated contract.
            if value not in SUPPORTED_STATUSES:
                unsupported_status.append(f"Phase {n}: {value}")
                continue

            phase_status[n] = value

    for n in expected_range:
        key = f"Phase {n}"
        expected = expected_statuses.get(key)
        observed = phase_status.get(n)
        if observed is not None and observed != expected:
            mismatched_status.append(f"{key}: expected {expected}, got {observed}")

    if missing_status or duplicate_status or unsupported_status or mismatched_status:
        details: list[str] = []
        if missing_status:
            details.append(f"missing statuses: {[f'Phase {n}' for n in missing_status]}")
        if duplicate_status:
            details.append(f"duplicate Status headings: {duplicate_status}")
        if unsupported_status:
            details.append(f"unsupported statuses: {unsupported_status}")
        if mismatched_status:
            details.append(f"mismatches: {mismatched_status}")
        emit("FAIL", "docs", "phase-status", "; ".join(details))
        ok = False
        if fail_fast: return False
    else:
        complete_count = sum(1 for v in expected_statuses.values() if v == "Complete")
        planned_count = sum(1 for v in expected_statuses.values() if v == "Planned")
        emit("PASS", "docs", "phase-status", f"contiguous phase status: {complete_count} Complete, {planned_count} Planned")

    if not ok and fail_fast: return False

    # README active-release check (contract-driven)
    readme = REPO / "README.md"
    active_version = contract["release"]["version"]
    active_branch = contract["release"]["active_branch"]
    if readme.is_file():
        readme_text = readme.read_text(encoding="utf-8")
        missing_items: list[str] = []
        if active_version not in readme_text:
            missing_items.append(f"version '{active_version}'")
        if active_branch not in readme_text:
            missing_items.append(f"branch '{active_branch}'")
        if missing_items:
            emit("FAIL", "docs", "readme-active-release", f"README missing: {', '.join(missing_items)}")
            ok = False
            if fail_fast: return False
        else:
            emit("PASS", "docs", "readme-active-release", f"README contains active release version '{active_version}' and branch '{active_branch}'")
    else:
        emit("FAIL", "docs", "readme-active-release", "README.md missing")
        ok = False
        if fail_fast: return False

    if not ok and fail_fast: return False

    # Active charter wiring (contract-driven)
    charter_rel = contract["release_documents"]["charter"]
    charter = REPO / charter_rel
    if charter.is_file():
        text = charter.read_text(encoding="utf-8")
        lower = text.lower()
        has_non_goals = bool(
            re.search(r"^##\s+explicit non-goals\b|^##\s+non-goals\b|^##\s+out of scope\b", text, flags=re.M | re.I)
        )
        # Find the character offset of each section heading
        heading_positions: list[tuple[int, str]] = []
        for hm in re.finditer(r"^##\s+(.+)$", text, flags=re.M):
            heading_positions.append((hm.start(), hm.group(1).strip()))

        def nearest_heading(pos: int) -> str:
            best = ""
            for hpos, htext in heading_positions:
                if hpos <= pos:
                    best = htext
                else:
                    break
            return best

        def is_negation_context(pos: int) -> bool:
            """Return True if the position is in a negation/non-goal context."""
            heading = nearest_heading(pos).lower()
            if any(kw in heading for kw in ("non-goal", "out of scope", "explicit non-goal")):
                return True
            # Also check inline negation in the 300 chars before and after
            start = max(0, pos - 300)
            ctx_before = lower[start:pos]
            ctx_after = lower[pos:pos + 300]
            combined = ctx_before + " " + ctx_after
            if re.search(
                r"(no |not |without |excludes? |lacks? |absence of |must not add|does not add|does not implement|does not introduce|contains no|out of scope|explicitly out|non-goal)",
                combined,
            ):
                return True
            return False

        category_failures: list[str] = []
        for cat_name, cat_patterns in NON_FUNCTIONALITY_CATEGORIES:
            for pat in cat_patterns:
                if pat in lower:
                    for m in re.finditer(re.escape(pat), lower):
                        if not is_negation_context(m.start()):
                            category_failures.append(cat_name)
                            break
        if not has_non_goals:
            emit("FAIL", "docs", "charter-consistency", "charter lacks non-goals section")
            ok = False
            if fail_fast: return False
        elif category_failures:
            emit("FAIL", "docs", "charter-consistency", f"charter claims to add: {category_failures}")
            ok = False
            if fail_fast: return False
        else:
            emit("PASS", "docs", "charter-consistency", "charter consistent with absence of all product functionality categories")
    else:
        emit("FAIL", "docs", "charter-consistency", f"charter file not found: {charter_rel}")
        ok = False
        if fail_fast: return False

    if not ok and fail_fast: return False

    if not check_repository_consistency(args, fail_fast):
        ok = False
        if fail_fast: return False

    exp_min = {
        "title": re.compile(r"^# EXP-\d{4} — .+", re.MULTILINE),
        "doc_status": re.compile(r"^\*\*Document status:\*\*", re.MULTILINE),
        "identification": re.compile(r"^## Identification", re.MULTILINE),
        "tool": re.compile(r"^## Tool and model", re.MULTILINE),
        "consumption": re.compile(r"^## Consumption", re.MULTILINE),
        "status": re.compile(r"^## Status", re.MULTILINE),
    }
    for n in range(1, 7):
        p = REPO / f"docs/agentic-development/experiments/EXP-{n:04d}.md"
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        missing = [name for name, pat in exp_min.items() if not pat.search(text)]
        if missing:
            emit("FAIL", "docs", "exp-structure", f"EXP-{n:04d} missing: {', '.join(missing)}")
            ok = False
            if fail_fast: return False

    exp_full = {
        "identification": r"^## Identification",
        "tool": r"^## Tool and model",
        "consumption": r"^## Consumption",
        "stage1": r"## Stage 1 evidence|## Preserved Stage 1",
        "stage2": r"## Stage 2 evidence|## Execution|## Preserved Stage 2",
        "task": r"^## Task",
        "execution": r"^## Execution",
        "results": r"^## Results",
        "assessment": r"^## Assessment",
        "status": r"^## Status",
    }
    exp7 = REPO / "docs/agentic-development/experiments/EXP-0007.md"
    if exp7.is_file():
        text = exp7.read_text(encoding="utf-8")
        missing7 = [name for name, key in exp_full.items() if not re.search(key, text, re.M)]
        if missing7:
            emit("FAIL", "docs", "exp7-structure", f"EXP-0007 missing: {', '.join(missing7)}")
            ok = False
            if fail_fast: return False
        else:
            emit("PASS", "docs", "exp7-structure", "EXP-0007 satisfies full Phase 4 structure")

    if not ok and fail_fast: return False

    publish = []
    for rel in ("docs/local-validation.md", "docs/agentic-development/experiments/EXP-0007.md"):
        p = REPO / rel
        if p.is_file():
            publish.append(p)

    bad_pii = False
    for p in publish:
        text = p.read_text(encoding="utf-8")
        rel = p.relative_to(REPO).as_posix()
        for m in EMAIL_PATTERN.findall(text):
            if m in EVAL_TEMPLATE_PLACEHOLDERS:
                continue
            if m in RESERVED_INVALID_ADDRESSES:
                if "validation@invalid.example" not in text or "temporary-clone" not in text.lower():
                    emit("FAIL", "docs", "no-pii", f"undocumented reserved address in {rel}: {m}")
                    bad_pii = True
                continue
            emit("FAIL", "docs", "no-pii", f"email in {rel}: {m}")
            bad_pii = True
        for m in PRIVATE_PATTERN.findall(text):
            if m == "session-ses_*.md":
                continue
            emit("FAIL", "docs", "no-private-export", f"concrete private-session filename in {rel}")
            bad_pii = True
        for lit in PROHIBITED_PLACEHOLDER_LITERALS:
            if lit in text:
                emit("FAIL", "docs", "placeholders", f"prohibited placeholder '{lit}' in {rel}")
                bad_pii = True
        for m in BARE_PENDING_PATTERN.findall(text):
            emit("FAIL", "docs", "placeholders", f"bare 'pending' in {rel}")
            bad_pii = True
        for m in re.findall(r"<[^>\n]{1,40}>", text):
            if m in EVAL_TEMPLATE_PLACEHOLDERS or m in ("<>", "</>"):
                continue
            emit("FAIL", "docs", "placeholders", f"unsupported angle-bracket placeholder '{m}' in {rel}")
            bad_pii = True
        for m in re.findall(r"/(?:home|Users|root|workspace|android|sdk|java|gradle|cache)/[^\s)\"']+", text):
            emit("FAIL", "docs", "no-paths", f"concrete absolute path in {rel}")
            bad_pii = True

    if not bad_pii:
        emit("PASS", "docs", "no-pii", "publishable Phase 4 content has no PII or prohibited placeholders")

    return ok and not bad_pii


# ---------- android group ----------

def find_sdk() -> Path | None:
    for k in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        v = os.environ.get(k)
        if v and Path(v).is_dir():
            return Path(v)
    return None


def check_android_prerequisites() -> Path | None:
    """Emit prerequisite passes and failures. Return SDK path on success, None on failure."""
    if sys.version_info < (3, 10):
        emit_prereq("python", "Python 3.10 or newer is required")
        return None
    emit("PASS", "android", "python", "Python 3.10 or newer")

    java_executable = shutil.which("java")
    if java_executable is None:
        emit_prereq("java", "java executable not found")
        return None
    try:
        r = subprocess.run(
            [java_executable, "-version"],
            capture_output=True, text=True,
        )
    except OSError:
        emit_prereq("java", "java executable not found")
        return None
    java_output = r.stderr or r.stdout or ""
    if not java_output:
        emit_prereq("java", "java executable not found")
        return None
    m = re.search(r'"(\d+)\.(\d+)', java_output)
    if not m:
        emit_prereq("java", "java major version not parseable")
        return None
    major = int(m.group(1))
    if major < 17:
        emit_prereq("java", f"Java major version {major} below 17")
        return None
    emit("PASS", "android", "java", f"Java major version {major}")

    # The compile SDK value is contract-driven; the Build Tools version
    # is a stable implementation constant because no corresponding
    # release-contract field currently exists. The release contract is
    # loaded and validated defensively here, so that an invalid
    # contract can be surfaced as a prerequisite failure with a
    # concise reason rather than producing a hard-coded fallback.
    contract = get_release_contract()
    if contract is None:
        emit_prereq(
            "release-contract",
            get_release_contract_error() or "contract load failed",
        )
        return None

    compile_sdk = contract["android"]["compile_sdk"]
    build_tools_version = "36.0.0"

    sdk = find_sdk()
    if sdk is None:
        emit_prereq("sdk", "ANDROID_HOME and ANDROID_SDK_ROOT not set or invalid")
        return None
    if not (sdk / f"platforms/android-{compile_sdk}").is_dir():
        emit_prereq("sdk-platform", f"SDK Platform {compile_sdk} missing")
        return None
    emit("PASS", "android", "sdk-platform", f"Platform {compile_sdk} present")
    build_tools = sdk / f"build-tools/{build_tools_version}"
    if not build_tools.is_dir():
        emit_prereq("sdk-build-tools", f"SDK Build Tools {build_tools_version} missing")
        return None
    aapt2 = build_tools / "aapt2"
    if not aapt2.is_file() or not os.access(aapt2, os.X_OK):
        emit_prereq("aapt2", f"Build Tools {build_tools_version} aapt2 missing or not executable")
        return None
    emit("PASS", "android", "sdk-build-tools", f"Build Tools {build_tools_version} present")
    emit("PASS", "android", "aapt2", "aapt2 present and executable")

    gradlew = REPO / "gradlew"
    if not gradlew.is_file() or not os.access(gradlew, os.X_OK):
        emit_prereq("gradlew-exec", "gradlew missing or not executable in working tree")
        return None
    emit("PASS", "android", "gradlew-exec", "gradlew present and executable")
    return sdk


def _version_catalog_failures(text: str) -> list[str]:
    """Return version-catalog mismatch descriptions for the four release-critical keys.

    Bounded repository-specific textual validation. Counts every exact
    release-critical key in ``text`` and enforces the four expected
    values. Not a generic TOML parser.
    """
    expectations = {
        "agp": "9.2.1",
        "kotlinCompose": "2.3.10",
        "composeBom": "2026.06.00",
        "activityCompose": "1.13.0",
    }
    bad: list[str] = []
    for key, expected in expectations.items():
        matches = re.findall(
            rf'^{re.escape(key)}\s*=\s*"([^"]+)"',
            text,
            flags=re.M,
        )
        if len(matches) != 1:
            bad.append(f"{key}=count:{len(matches)}")
        elif matches[0] != expected:
            bad.append(f"{key}={matches[0]}")
    return bad


DEPENDABOT_EXPECTED_ECOSYSTEMS = ("gradle", "github-actions")

DEPENDABOT_FORBIDDEN_KEYS = (
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


def _dependabot_failures(text: str) -> list[str]:
    """Return Dependabot configuration mismatch descriptions for the
    bounded Phase 5C contract.

    Bounded repository-specific textual validation. Verifies the
    narrow two-ecosystem configuration required by Phase 5C and
    rejects forbidden policy keys. Not a generic YAML parser.
    Deterministic line/indentation parsing and regular expressions only.
    """
    bad: list[str] = []

    # 1. Top-level version must equal 2
    version_match = re.search(r"^version:\s*(\d+)\s*$", text, flags=re.M)
    if version_match is None:
        bad.append("top-level version must equal 2")
        return bad
    if version_match.group(1) != "2":
        bad.append("top-level version must equal 2")
        return bad

    # 2. Top-level updates: block. Locate the start of the updates
    # body; the bounded parser then scans forward to EOF to find each
    # list entry, since the empty line that may separate the two
    # required entries is part of the bounded configuration shape.
    updates_match = re.search(r"^updates:\s*\n", text, flags=re.M)
    if not updates_match:
        bad.append("malformed bounded Dependabot configuration")
        return bad
    entries_text = text[updates_match.end():]

    # 3. Each list entry begins with "- package-ecosystem: ..."
    entry_re = re.compile(
        r"^  - package-ecosystem:\s*\"([^\"]+)\"\s*\n"
        r"((?:[ \t]{4,}[^\n]*\n)*)",
        flags=re.M,
    )
    entries = list(entry_re.finditer(entries_text))

    if len(entries) != 2:
        bad.append("ecosystems must equal: gradle, github-actions")
        return bad

    ecosystems = [m.group(1) for m in entries]
    if ecosystems != list(DEPENDABOT_EXPECTED_ECOSYSTEMS):
        bad.append("ecosystems must equal: gradle, github-actions")
        return bad

    # 4. Per-entry directory / schedule.interval / open-pull-requests-limit
    for idx, m in enumerate(entries):
        body = m.group(2)
        ecosystem = ecosystems[idx]

        d_match = re.search(
            r"^    directory:\s*\"([^\"]+)\"\s*$", body, flags=re.M,
        )
        if d_match is None or d_match.group(1) != "/":
            bad.append(f"{ecosystem} directory must equal /")

        sched_match = re.search(
            r"^    schedule:\s*\n((?:[ \t]{6,}[^\n]*\n)*)",
            body, flags=re.M,
        )
        if not sched_match:
            bad.append(f"{ecosystem} schedule.interval must equal weekly")
        else:
            int_match = re.search(
                r"^      interval:\s*\"([^\"]+)\"\s*$",
                sched_match.group(1), flags=re.M,
            )
            if int_match is None or int_match.group(1) != "weekly":
                bad.append(f"{ecosystem} schedule.interval must equal weekly")

        oprl_match = re.search(
            r"^    open-pull-requests-limit:\s*(\d+)\s*$",
            body, flags=re.M,
        )
        if oprl_match is None or oprl_match.group(1) != "5":
            bad.append(f"{ecosystem} open-pull-requests-limit must equal 5")

    # 5. Forbidden keys (any reasonable indentation)
    for key in DEPENDABOT_FORBIDDEN_KEYS:
        pattern = rf"^[ \t]*{re.escape(key)}\s*:"
        if re.search(pattern, text, flags=re.M):
            bad.append(f"forbidden key: {key}")

    return bad


def check_android_content(args: argparse.Namespace, sdk: Path) -> bool:
    ok = True
    prohibited = ("org.jetbrains.kotlin.android", "android.kotlinOptions", "kotlinCompilerExtensionVersion")
    for rel in ("build.gradle.kts", "app/build.gradle.kts"):
        p = REPO / rel
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        bad = [pr for pr in prohibited if pr in text]
        if bad:
            emit("FAIL", "android", "build-config", f"prohibited in {rel}: {bad}")
            ok = False
    if ok:
        emit("PASS", "android", "build-config", "no prohibited Kotlin config in build scripts")

    toml = REPO / "gradle/libs.versions.toml"
    if toml.is_file():
        text = toml.read_text(encoding="utf-8")
        bad = _version_catalog_failures(text)
        if bad:
            emit("FAIL", "android", "version-catalog", f"unexpected: {', '.join(bad)}")
            ok = False
        else:
            emit("PASS", "android", "version-catalog", "AGP/Compose versions match")

    gradle_props = REPO / "gradle/wrapper/gradle-wrapper.properties"
    if gradle_props.is_file():
        text = gradle_props.read_text(encoding="utf-8")
        if "gradle-9.4.1-bin.zip" in text:
            emit("PASS", "android", "gradle-wrapper", "wrapper 9.4.1")
        else:
            emit("FAIL", "android", "gradle-wrapper", "wrapper version mismatch")
            ok = False

    app_gradle = REPO / "app/build.gradle.kts"
    if app_gradle.is_file():
        text = app_gradle.read_text(encoding="utf-8")
        # Release-specific Android expectations are derived from the
        # validated release contract. Java 17 compatibility and Compose
        # enablement remain stable implementation constants because no
        # corresponding release-contract field currently exists.
        contract = get_release_contract()
        if contract is None:
            emit("FAIL", "android", "app-build-config", "release contract unavailable")
            return False
        android_block = contract["android"]
        expectations = {
            "namespace": f'namespace = "{android_block["namespace"]}"',
            "applicationId": f'applicationId = "{android_block["application_id"]}"',
            "compileSdk": f"compileSdk = {android_block['compile_sdk']}",
            "minSdk": f"minSdk = {android_block['min_sdk']}",
            "targetSdk": f"targetSdk = {android_block['target_sdk']}",
            "source": "JavaVersion.VERSION_17",
            "target": "JavaVersion.VERSION_17",
            "compose": "compose = true",
        }
        bad = [k for k, v in expectations.items() if v not in text]
        if bad:
            emit("FAIL", "android", "app-build-config", f"missing: {bad}")
            ok = False
        else:
            emit("PASS", "android", "app-build-config", "app build config matches")

    if not ok and args.fail_fast: return False

    # Source manifest exhaustive
    manifest = REPO / "app/src/main/AndroidManifest.xml"
    if not manifest.is_file():
        emit("FAIL", "android", "source-manifest", "source manifest missing")
        return False
    # The source-manifest launcher activity expectation is
    # contract-driven via android.launcher_activity_source. The
    # exhaustive boundary and intent-filter checks remain unchanged.
    contract = get_release_contract()
    if contract is None:
        emit("FAIL", "android", "source-manifest", "release contract unavailable")
        return False
    expected_source_activity = contract["android"]["launcher_activity_source"]
    tree = ET.parse(manifest)
    root = tree.getroot()
    if len(root.findall("application")) != 1:
        emit("FAIL", "android", "source-manifest", "application count != 1")
        return False
    # Reject any root-level unexpected children
    unexpected_root = []
    for child in list(root):
        tag = child.tag.split("}", 1)[-1]
        if tag not in ("application",):
            unexpected_root.append(tag)
    if unexpected_root:
        emit("FAIL", "android", "source-manifest", f"unexpected root children: {unexpected_root}")
        return False
    app = root.find("application")
    direct_kids: dict[str, int] = {}
    for child in list(app):
        tag = child.tag.split("}", 1)[-1]
        direct_kids[tag] = direct_kids.get(tag, 0) + 1
    if direct_kids != {"activity": 1}:
        emit("FAIL", "android", "source-manifest", f"application direct children: {direct_kids}")
        return False
    act = app.findall("activity")[0]
    if (act.get(f"{{{NS_ANDROID}}}name") != expected_source_activity
            or act.get(f"{{{NS_ANDROID}}}exported") != "true"):
        emit("FAIL", "android", "source-manifest", "activity name/exported mismatch")
        return False
    filters = act.findall("intent-filter")
    actions = list(act.iter("action"))
    categories = list(act.iter("category"))
    datas = list(act.iter("data"))
    if (len(filters) != 1
            or len(actions) != 1 or actions[0].get(f"{{{NS_ANDROID}}}name") != "android.intent.action.MAIN"
            or len(categories) != 1 or categories[0].get(f"{{{NS_ANDROID}}}name") != "android.intent.category.LAUNCHER"
            or datas):
        emit("FAIL", "android", "source-manifest", "intent-filter structure mismatch")
        return False
    emit("PASS", "android", "source-manifest", "exact source-manifest boundary satisfied")

    env = os.environ.copy()
    env["GRADLE_OPTS"] = "-Xmx1000m"
    gradle_common = ["--console=plain", "--no-daemon", "--no-parallel"]
    if args.offline:
        gradle_common.append("--offline")

    gradle = REPO / "gradlew"
    r = subprocess.run([str(gradle), "projects", *gradle_common], cwd=REPO, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        emit("FAIL", "android", "gradle-projects", f"exit {r.returncode}")
        return False
    if ":app" not in r.stdout:
        emit("FAIL", "android", "gradle-projects", "':app' not in projects output")
        return False
    emit("PASS", "android", "gradle-projects", "project discovery includes :app")

    r = subprocess.run([str(gradle), ":app:assembleDebug", ":app:lintDebug", *gradle_common], cwd=REPO, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        emit("FAIL", "android", "gradle-build", f"exit {r.returncode}")
        return False
    emit("PASS", "android", "gradle-build", "assembleDebug+lintDebug succeeded")

    apk = REPO / "app/build/outputs/apk/debug/app-debug.apk"
    if not apk.is_file() or apk.stat().st_size == 0:
        emit("FAIL", "android", "apk-exists", "APK missing or empty")
        return False
    emit("PASS", "android", "apk-exists", f"APK present ({apk.stat().st_size} bytes)")

    aapt2 = sdk / "build-tools/36.0.0/aapt2"
    r = subprocess.run([str(aapt2), "dump", "badging", str(apk)], capture_output=True, text=True)
    if r.returncode != 0:
        emit("FAIL", "android", "aapt2", f"aapt2 dump badging exit {r.returncode}")
        return False
    # APK metadata expectations are generated from the validated
    # contract. The current values are version code 1 and version name
    # 0.1.0 because those are the contract's current committed values
    # before Phase 5. A future Phase 5 update of the contract and
    # Gradle metadata will not require another Python source edit for
    # these APK fields.
    contract = get_release_contract()
    if contract is None:
        emit("FAIL", "android", "apk-metadata", "release contract unavailable")
        return False
    android_block = contract["android"]
    package_name = android_block["package_name"]
    current_version_code = android_block["current_version_code"]
    current_version_name = android_block["current_version_name"]
    compile_sdk = android_block["compile_sdk"]
    min_sdk = android_block["min_sdk"]
    target_sdk = android_block["target_sdk"]
    launcher_merged = android_block["launcher_activity_merged"]
    expectations = {
        "package": f"package: name='{package_name}'",
        "versionCode": f"versionCode='{current_version_code}'",
        "versionName": f"versionName='{current_version_name}'",
        "compileSdkVersion": f"compileSdkVersion='{compile_sdk}'",
        "minSdkVersion": f"minSdkVersion:'{min_sdk}'",
        "targetSdkVersion": f"targetSdkVersion:'{target_sdk}'",
        "launchable": f"launchable-activity: name='{launcher_merged}'",
    }
    bad = [k for k, v in expectations.items() if v not in r.stdout]
    if bad:
        emit("FAIL", "android", "apk-metadata", f"missing: {bad}")
        return False
    emit("PASS", "android", "apk-metadata", "APK metadata matches")

    merged = REPO / "app/build/intermediates/merged_manifests/debug/processDebugManifest/AndroidManifest.xml"
    if not merged.is_file():
        emit("FAIL", "android", "merged-manifest", "merged manifest not found")
        return False
    # The merged launcher activity and the application-derived dynamic
    # receiver permission name are contract-driven. The merged
    # permission name is built from android.package_name plus the
    # stable DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION suffix.
    contract = get_release_contract()
    if contract is None:
        emit("FAIL", "android", "merged-manifest", "release contract unavailable")
        return False
    android_block = contract["android"]
    package_name = android_block["package_name"]
    launcher_merged = android_block["launcher_activity_merged"]
    expected_sig_perm = f"{package_name}.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION"
    try:
        tree = ET.parse(merged)
    except ET.ParseError:
        emit("FAIL", "android", "merged-manifest", "merged manifest parse error")
        return False
    mroot = tree.getroot()
    perms_decl = mroot.findall("permission")
    uses_perms = mroot.findall("uses-permission")
    if len(perms_decl) != 1 or len(uses_perms) != 1:
        emit("FAIL", "android", "merged-manifest", f"perms: decl={len(perms_decl)} use={len(uses_perms)}")
        return False
    sig = perms_decl[0]
    sig_name = sig.get(f"{{{NS_ANDROID}}}name")
    sig_level = sig.get(f"{{{NS_ANDROID}}}protectionLevel")
    if sig_name != expected_sig_perm:
        emit("FAIL", "android", "merged-manifest", f"permission name: {sig_name}")
        return False
    if sig_level != "signature":
        emit("FAIL", "android", "merged-manifest", f"protectionLevel: {sig_level}")
        return False
    if uses_perms[0].get(f"{{{NS_ANDROID}}}name") != sig_name:
        emit("FAIL", "android", "merged-manifest", "uses-permission does not match declared permission")
        return False
    apps = mroot.findall("application")
    if len(apps) != 1:
        emit("FAIL", "android", "merged-manifest", f"applications: {len(apps)}")
        return False
    app = apps[0]
    direct_kids = {}
    for child in list(app):
        tag = child.tag.split("}", 1)[-1]
        direct_kids[tag] = direct_kids.get(tag, 0) + 1
    expected_direct = {"activity": 1, "provider": 1, "receiver": 1, "uses-library": 2}
    if direct_kids != expected_direct:
        emit("FAIL", "android", "merged-manifest", f"direct children: {direct_kids}")
        return False
    activities = app.findall("activity")
    act = activities[0]
    if (act.get(f"{{{NS_ANDROID}}}name") != launcher_merged
            or act.get(f"{{{NS_ANDROID}}}exported") != "true"):
        emit("FAIL", "android", "merged-manifest", "merged activity mismatch")
        return False
    filters = act.findall("intent-filter")
    actions = list(act.iter("action"))
    categories = list(act.iter("category"))
    datas = list(act.iter("data"))
    if (len(filters) != 1
            or len(actions) != 1 or actions[0].get(f"{{{NS_ANDROID}}}name") != "android.intent.action.MAIN"
            or len(categories) != 1 or categories[0].get(f"{{{NS_ANDROID}}}name") != "android.intent.category.LAUNCHER"
            or datas):
        emit("FAIL", "android", "merged-manifest", "merged activity filter mismatch")
        return False
    providers = app.findall("provider")
    prov = providers[0]
    if (prov.get(f"{{{NS_ANDROID}}}name") != "androidx.startup.InitializationProvider"
            or prov.get(f"{{{NS_ANDROID}}}exported") != "false"):
        emit("FAIL", "android", "merged-manifest", "merged provider mismatch")
        return False
    pmetas = prov.findall("meta-data")
    expected_meta_names = {
        "androidx.emoji2.text.EmojiCompatInitializer",
        "androidx.lifecycle.ProcessLifecycleInitializer",
        "androidx.profileinstaller.ProfileInstallerInitializer",
    }
    if len(pmetas) != 3 or {m.get(f"{{{NS_ANDROID}}}name") for m in pmetas} != expected_meta_names:
        emit("FAIL", "android", "merged-manifest", f"provider metadata: {[m.get(f'{{{NS_ANDROID}}}name') for m in pmetas]}")
        return False
    if not all(m.get(f"{{{NS_ANDROID}}}value") == "androidx.startup" for m in pmetas):
        emit("FAIL", "android", "merged-manifest", "provider metadata value mismatch")
        return False
    receivers = app.findall("receiver")
    rcv = receivers[0]
    if (rcv.get(f"{{{NS_ANDROID}}}name") != "androidx.profileinstaller.ProfileInstallReceiver"
            or rcv.get(f"{{{NS_ANDROID}}}exported") != "true"
            or rcv.get(f"{{{NS_ANDROID}}}permission") != "android.permission.DUMP"):
        emit("FAIL", "android", "merged-manifest", "merged receiver mismatch")
        return False
    libs = app.findall("uses-library")
    expected_libs = {"androidx.window.extensions", "androidx.window.sidecar"}
    if {l.get(f"{{{NS_ANDROID}}}name") for l in libs} != expected_libs:
        emit("FAIL", "android", "merged-manifest", f"uses-library: {[l.get(f'{{{NS_ANDROID}}}name') for l in libs]}")
        return False
    if not all(l.get(f"{{{NS_ANDROID}}}required") == "false" for l in libs):
        emit("FAIL", "android", "merged-manifest", "uses-library required mismatch")
        return False
    emit("PASS", "android", "merged-manifest", "merged-manifest contract satisfied")
    return True


def check_android(args: argparse.Namespace) -> bool:
    sdk = check_android_prerequisites()
    if sdk is None:
        return False
    return check_android_content(args, sdk)


# ---------- normalized group wrappers and registry ----------

def run_required_group(args: argparse.Namespace) -> bool:
    return check_required(args, args.fail_fast)


def run_docs_group(args: argparse.Namespace) -> bool:
    return check_docs(args, args.fail_fast)


def run_android_group(args: argparse.Namespace) -> bool:
    return check_android(args)


VALIDATION_HANDLERS: dict[str, Callable[[argparse.Namespace], bool]] = {
    "required": run_required_group,
    "docs": run_docs_group,
    "android": run_android_group,
}


# ---------- main ----------

def print_summary_and_gate(
    args: argparse.Namespace,
    selected_groups: tuple[str, ...],
    release_gate_requires_groups: tuple[str, ...],
    release_gate_requires_android_not_skipped: bool,
) -> None:
    passed = sum(1 for r in _RESULTS if r[0] == "PASS")
    failed = sum(1 for r in _RESULTS if r[0] == "FAIL")
    skipped = sum(1 for r in _RESULTS if r[0] == "SKIP")
    print(f"SUMMARY pass={passed} fail={failed} skip={skipped}")
    all_required_selected = set(release_gate_requires_groups).issubset(selected_groups)
    no_fail = failed == 0
    android_required_and_present = (
        not release_gate_requires_android_not_skipped
        or ("android" in selected_groups and not args.skip_android)
    )
    if all_required_selected and no_fail and android_required_and_present:
        print("release_gate=SATISFIED")
    else:
        print("release_gate=NOT_SATISFIED")


def main(argv: list[str]) -> int:
    # 1. Load and fully validate the cached release contract.
    contract = get_release_contract()
    if contract is None:
        err = get_release_contract_error() or "contract load failed"
        emit_prereq("release-contract", err)
        print("SUMMARY pass=0 fail=1 skip=0")
        print("release_gate=NOT_SATISFIED")
        return 2

    # 3. From the valid contract obtain the four keys.
    val = contract["validation"]
    groups = tuple(val["groups"])
    all_alias = val["all_alias"]
    release_gate_requires_groups = tuple(val["release_gate_requires_groups"])
    release_gate_requires_android_not_skipped = val["release_gate_requires_android_not_skipped"]

    # 4. Construct argparse from the contract group identifiers and alias.
    # 5. Parse the invocation.
    args = parse_args(argv, groups, all_alias)

    # 6. Resolve the selected groups exactly once.
    sel = resolve_groups(args, groups, all_alias)
    if isinstance(sel, int):
        # 7. Invocation conflict (e.g. --group android --skip-android).
        return sel

    # 8. Check the Git prerequisite.
    if not check_git_prerequisite():
        print_summary_and_gate(
            args, sel, release_gate_requires_groups, release_gate_requires_android_not_skipped
        )
        return 2

    # 8b. Check the Git worktree prerequisite. When the resolved Git
    # executable exists but the repository root is not inside a Git
    # worktree, the validator must not raise a Python exception or emit
    # an absolute path; it must emit the concise prerequisite failure
    # and return 2 without executing any validation group.
    if not check_git_worktree_prerequisite():
        print_summary_and_gate(
            args, sel, release_gate_requires_groups, release_gate_requires_android_not_skipped
        )
        return 2

    if args.require_clean:
        before = git_status_short()
        if before.strip():
            emit("FAIL", "required", "clean-state", "non-ignored uncommitted changes present")
            print_summary_and_gate(
                args, sel, release_gate_requires_groups, release_gate_requires_android_not_skipped
            )
            return 1
        emit("PASS", "required", "clean-state", "non-ignored state clean before validation")

    # 9. Execute resolved groups in their resolved order.
    overall_ok = True
    for grp in sel:
        grp_ok = VALIDATION_HANDLERS[grp](args)
        if not grp_ok:
            overall_ok = False
            if args.fail_fast:
                break

    if args.require_clean:
        after = git_status_short()
        if after.strip():
            emit("FAIL", "required", "clean-state", "validation produced non-ignored changes")
            overall_ok = False
        else:
            emit("PASS", "required", "clean-state", "non-ignored state clean after validation")

    # 10. Calculate the summary and release gate from the already-resolved
    # selection and the validated contract.
    if _PREREQ_FAILED:
        print_summary_and_gate(
            args, sel, release_gate_requires_groups, release_gate_requires_android_not_skipped
        )
        return 2
    print_summary_and_gate(
        args, sel, release_gate_requires_groups, release_gate_requires_android_not_skipped
    )
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
