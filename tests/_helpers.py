"""Test-only helpers for the real ``scripts.validate_local`` module.

This helper module exists to support the Phase 4B regression suite. It
must not duplicate validator business logic, must not import third-party
libraries, must not invoke Gradle, Android tooling, or the network, must
not modify Git state, and must not inspect private working material.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import validate_local  # noqa: E402  (intentional post path-setup import)

_SAVED_NAMES: tuple[str, ...] = (
    "REPO",
    "RELEASE_CONTRACT_PATH",
    "_RESULTS",
    "_PREREQ_FAILED",
    "_CONTRACT",
    "_CONTRACT_ERROR",
    "_CONTRACT_LOADED",
)


def save_validator_state() -> dict[str, Any]:
    """Snapshot the validator's mutable module state for later restoration."""
    return {name: getattr(validate_local, name) for name in _SAVED_NAMES}


def restore_validator_state(saved: dict[str, Any]) -> None:
    """Restore the validator's mutable module state from a snapshot."""
    for name, value in saved.items():
        setattr(validate_local, name, value)


def reset_validator_state() -> None:
    """Reset the validator's mutable module state to known clean values."""
    validate_local._RESULTS = []
    validate_local._PREREQ_FAILED = False
    validate_local._CONTRACT = None
    validate_local._CONTRACT_ERROR = None
    validate_local._CONTRACT_LOADED = False


def save_validation_handlers() -> dict[str, Callable[..., Any]]:
    """Snapshot the validator's ``VALIDATION_HANDLERS`` registry."""
    return dict(validate_local.VALIDATION_HANDLERS)


def restore_validation_handlers(saved: dict[str, Callable[..., Any]]) -> None:
    """Restore the validator's ``VALIDATION_HANDLERS`` registry from a snapshot."""
    validate_local.VALIDATION_HANDLERS.clear()
    validate_local.VALIDATION_HANDLERS.update(saved)


def reset_validation_handlers_to_real() -> None:
    """Reset ``VALIDATION_HANDLERS`` to the real registry defined by the validator."""
    validate_local.VALIDATION_HANDLERS["required"] = validate_local.run_required_group
    validate_local.VALIDATION_HANDLERS["docs"] = validate_local.run_docs_group
    validate_local.VALIDATION_HANDLERS["android"] = validate_local.run_android_group


@contextlib.contextmanager
def patched_repo_and_contract(repo: Path, contract_path: Path) -> Iterator[None]:
    """Temporarily patch ``REPO`` and ``RELEASE_CONTRACT_PATH`` on the validator.

    The original values are restored on context exit, even if an exception
    is raised inside the with-block. The validator's cached contract state
    is reset on entry and the original state is restored on exit.
    """
    saved = save_validator_state()
    original_repo = validate_local.REPO
    original_contract = validate_local.RELEASE_CONTRACT_PATH
    validate_local.REPO = repo
    validate_local.RELEASE_CONTRACT_PATH = contract_path
    reset_validator_state()
    try:
        yield
    finally:
        validate_local.REPO = original_repo
        validate_local.RELEASE_CONTRACT_PATH = original_contract
        restore_validator_state(saved)


@contextlib.contextmanager
def patched_module_attribute(name: str, value: Any) -> Iterator[None]:
    """Temporarily set a single module attribute on the validator.

    The original attribute value is restored on context exit, even when
    an exception is raised inside the with-block. This standard-library
    context manager does not depend on ``unittest.mock``.
    """
    original = getattr(validate_local, name)
    setattr(validate_local, name, value)
    try:
        yield
    finally:
        setattr(validate_local, name, original)


@contextlib.contextmanager
def capture_stdout_stderr() -> Iterator[tuple[io.StringIO, io.StringIO]]:
    """Capture ``stdout`` and ``stderr`` into ``StringIO`` buffers."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        yield out, err


def build_minimal_validation_contract(
    groups: tuple[str, ...] = ("required", "docs", "android"),
    all_alias: str = "all",
    release_gate_requires_groups: tuple[str, ...] = ("required", "docs", "android"),
    release_gate_requires_android_not_skipped: bool = True,
) -> dict[str, Any]:
    """Build a minimal synthetic ``validation`` contract section.

    The returned mapping contains only the keys read by ``main()``; it is
    not a full validated release contract. The shape is the minimum that
    lets ``main()`` proceed past contract loading without re-running the
    full contract validator. The defaults match the standard Phase 4
    contract: groups ``required``, ``docs``, ``android``; alias ``all``;
    release-gate requires all three groups; Android-not-skipped is true.
    """
    return {
        "validation": {
            "groups": list(groups),
            "all_alias": all_alias,
            "release_gate_requires_groups": list(release_gate_requires_groups),
            "release_gate_requires_android_not_skipped":
                release_gate_requires_android_not_skipped,
        }
    }


def run_validator_child_with_clean_path() -> subprocess.CompletedProcess:
    """Spawn the validator in a fresh child process with a clean ``PATH``.

    The child process is launched with the already-resolved
    ``sys.executable`` (so Python itself does not depend on the child's
    ``PATH``), runs from the real repository root, and is given an
    environment whose ``PATH`` is a fresh empty temporary directory.
    Inside the child, ``shutil.which("git")`` is therefore ``None`` and
    the real ``check_git_prerequisite`` must fail.

    The child invokes the real ``validate_local.main(["--group",
    "required"])`` and exits with that returned value. The parent
    environment is not mutated. No shell wrapper is used. The temporary
    directory is created and torn down within this call.
    """
    with tempfile.TemporaryDirectory() as empty_path:
        env = os.environ.copy()
        env["PATH"] = empty_path
        env["PYTHONPATH"] = str(_REPO_ROOT)
        child_code = (
            "from scripts import validate_local\n"
            "import sys\n"
            "sys.exit(validate_local.main(['--group', 'required']))\n"
        )
        return subprocess.run(
            [sys.executable, "-B", "-c", child_code],
            cwd=_REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )


def create_consistency_fixture(
    repo: Path,
    readme_text: str,
    phase_list_text: str,
    charter_text: str,
) -> Path:
    """Create a temporary repository fixture for the new
    ``docs/repository-consistency`` check.

    Copies the real release contract from the live repository into the
    fixture so the contract-driven check sees a valid contract, parses
    the copied fixture contract with the standard-library ``json``
    module, and resolves every required current-release path, the
    historical release-doc root, and the Android fixture values from
    the exact contract fields. No Git, HEAD, index, or untracked-file
    state is inspected.

    The active-release charter, phase-list, and local-validation paths
    come from ``release_documents``; the historical directory comes
    from ``historical.previous_release_docs_root``; and the Android
    fixture values (namespace, application id, SDK levels, current
    version code/name, and launcher activity) come from the
    ``android`` section. No release version literal is hard-coded in
    this helper.

    No live governance file is mutated. No real Android or Gradle file
    is read for analysis. The temporary directory is the caller's
    responsibility and is cleaned up automatically by
    ``tempfile.TemporaryDirectory``.

    Returns the contract path inside the fixture.
    """
    real_contract = Path(str(validate_local.RELEASE_CONTRACT_PATH))
    contract_dir = repo / "scripts"
    contract_dir.mkdir(parents=True, exist_ok=True)
    contract_path = contract_dir / "release_contract.json"
    shutil.copy(str(real_contract), str(contract_path))

    with contract_path.open("r", encoding="utf-8") as fh:
        contract = json.load(fh)

    release_documents = contract["release_documents"]
    historical_cfg = contract["historical"]
    android_cfg = contract["android"]

    (repo / "README.md").write_text(readme_text, encoding="utf-8")

    # Contract-required local-validation file. Minimal deterministic
    # content; the contract loader only requires this path to exist as
    # a file.
    local_validation_path = repo / release_documents["local_validation"]
    local_validation_path.parent.mkdir(parents=True, exist_ok=True)
    local_validation_path.write_text("# Local validation fixture\n", encoding="utf-8")

    # Contract-required current-release charter and phase list.
    charter_path = repo / release_documents["charter"]
    charter_path.parent.mkdir(parents=True, exist_ok=True)
    charter_path.write_text(charter_text, encoding="utf-8")

    phase_list_path = repo / release_documents["phase_list"]
    phase_list_path.parent.mkdir(parents=True, exist_ok=True)
    phase_list_path.write_text(phase_list_text, encoding="utf-8")

    # Historical release-doc root. The real contract requires the path
    # to exist as a directory; no historical charter or phase list is
    # needed for this test.
    previous_release_docs_root = repo / historical_cfg["previous_release_docs_root"]
    previous_release_docs_root.mkdir(parents=True, exist_ok=True)

    # Minimal app/build.gradle.kts satisfying the contract cross-check.
    android_namespace = android_cfg["namespace"]
    android_application_id = android_cfg["application_id"]
    android_compile_sdk = android_cfg["compile_sdk"]
    android_min_sdk = android_cfg["min_sdk"]
    android_target_sdk = android_cfg["target_sdk"]
    android_version_code = android_cfg["current_version_code"]
    android_version_name = android_cfg["current_version_name"]
    android_launcher_activity_source = android_cfg["launcher_activity_source"]

    app_gradle = repo / "app" / "build.gradle.kts"
    app_gradle.parent.mkdir(parents=True, exist_ok=True)
    app_gradle.write_text(
        f'namespace = "{android_namespace}"\n'
        f'applicationId = "{android_application_id}"\n'
        f"compileSdk = {android_compile_sdk}\n"
        f"minSdk = {android_min_sdk}\n"
        f"targetSdk = {android_target_sdk}\n"
        f"versionCode = {android_version_code}\n"
        f'versionName = "{android_version_name}"\n',
        encoding="utf-8",
    )

    # Minimal AndroidManifest.xml satisfying the contract cross-check.
    manifest_dir = repo / "app" / "src" / "main"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifest_dir / "AndroidManifest.xml"
    manifest.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<manifest xmlns:android="http://schemas.android.com/apk/res/android">\n'
        "    <application>\n"
        f'        <activity android:name="{android_launcher_activity_source}" />\n'
        "    </application>\n"
        "</manifest>\n",
        encoding="utf-8",
    )

    return contract_path
