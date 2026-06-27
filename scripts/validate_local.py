#!/usr/bin/env python3
"""Local validation suite for the NudgeWhen v0.1.0 release.

Phase 4 — Local Validation Baseline. Python standard library only.

CLI:
  --group {required,docs,android,all}   (repeatable; default: all)
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
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NS_ANDROID = "http://schemas.android.com/apk/res/android"

GROUP_ORDER = ("required", "docs", "android")

GRADLEW_BAT_EXPECTED_SHA = (
    "fedad02c18e266ec094995a5751b7fe1eb6e74f66bf75db64fae2e50eb22c234"
)

PRIVATE_PATTERN = re.compile(r"^session-ses_[A-Za-z0-9_]+\.md$")

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

CANDIDATE_UNTRACKED_ALLOWLIST = (
    ".gitattributes",
    "scripts/validate-local.sh",
    "scripts/validate_local.py",
    "docs/local-validation.md",
    "docs/agentic-development/experiments/EXP-0007.md",
)

TEXT_EXTENSIONS = (
    ".md", ".kts", ".kt", ".xml", ".yml", ".yaml",
    ".toml", ".properties", ".sh", ".py",
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="validate-local.py",
        description="Local validation suite for the NudgeWhen v0.1.0 release.",
    )
    p.add_argument("--group", action="append", choices=list(GROUP_ORDER) + ["all"])
    p.add_argument("--skip-android", action="store_true")
    p.add_argument("--offline", action="store_true")
    p.add_argument("--fail-fast", action="store_true")
    p.add_argument("--require-clean", action="store_true")
    return p.parse_args(argv)


def resolve_groups(args: argparse.Namespace) -> tuple[str, ...] | int:
    selected: list[str] = []
    if args.group:
        for g in args.group:
            if g == "all":
                selected.extend(GROUP_ORDER)
            else:
                selected.append(g)
    else:
        selected.extend(GROUP_ORDER)

    if args.skip_android:
        if "android" in selected and any(g in ("required", "docs") for g in selected):
            for g in ("required", "docs"):
                if g not in selected:
                    selected.append(g)
        if args.group and "android" in args.group and "android" in selected:
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
    "docs/local-validation.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
)

GITIGNORE_REQUIRED = (
    "build/", "local.properties", "*.apk", "*.aab", "*.jks", "*.keystore", "session-ses_*.md",
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


def check_required(args: argparse.Namespace, fail_fast: bool) -> bool:
    ok = True
    tracked = set(git_ls_files())
    clean_mode = args.require_clean

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
        if base.endswith(".pyc"):
            emit("FAIL", "required", "no-pyc", f"tracked bytecode: {rel}")
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

    phase_list = REPO / "docs/releases/v0.1.0/phase-list.md"
    phase_nums: list[int] = []
    if phase_list.is_file():
        text = phase_list.read_text(encoding="utf-8")
        phase_nums = [int(x) for x in re.findall(r"^## Phase (\d+) — .*$", text, flags=re.M)]
    if phase_nums != [0, 1, 2, 3, 4, 5, 6, 7]:
        emit("FAIL", "docs", "phase-headings", f"unexpected heading order: {phase_nums}")
        ok = False
        if fail_fast: return False
    else:
        emit("PASS", "docs", "phase-headings", "Phase 0–7 headings ordered and unique")

    if not ok and fail_fast: return False

    phase_status: dict[int, str] = {}
    if phase_list.is_file():
        text = phase_list.read_text(encoding="utf-8")
        for n in range(0, 8):
            m = re.search(
                rf"## Phase {n} — [^\n]*\n.*?\*\*(?:Initial )?[Ss]tatus\.\*\*\s*`(\w+)`",
                text, flags=re.S,
            )
            if m:
                phase_status[n] = m.group(1).lower()

    observed = [phase_status.get(i, "") for i in range(0, 8)]

    if len(observed) != 8:
        emit("FAIL", "docs", "phase-status", f"expected 8 phase statuses, got {len(observed)}")
        ok = False
        if fail_fast: return False
    else:
        unknown = [i for i, s in enumerate(observed) if s not in ("complete", "planned")]
        if unknown:
            emit("FAIL", "docs", "phase-status", f"unknown phase status at indices {unknown}: {observed}")
            ok = False
            if fail_fast: return False
        else:
            complete_count = observed.count("complete")
            planned_count = observed.count("planned")
            contiguous_complete = all(observed[i] == "complete" for i in range(complete_count))
            contiguous_planned = all(observed[i] == "planned" for i in range(complete_count, 8))
            if not (contiguous_complete and contiguous_planned):
                emit("FAIL", "docs", "phase-status", f"phase statuses not in contiguous prefix/suffix order: {observed}")
                ok = False
                if fail_fast: return False
            elif complete_count < 4:
                emit("FAIL", "docs", "phase-status", f"complete prefix length {complete_count} below minimum 4: {observed}")
                ok = False
                if fail_fast: return False
            elif complete_count > 8:
                emit("FAIL", "docs", "phase-status", f"complete prefix length {complete_count} above maximum 8: {observed}")
                ok = False
                if fail_fast: return False
            else:
                emit("PASS", "docs", "phase-status", f"contiguous phase status: {complete_count} Complete, {planned_count} Planned")

    readme = REPO / "README.md"
    if readme.is_file() and phase_list.is_file():
        readme_text = readme.read_text(encoding="utf-8")
        m = re.search(r"- Phase 4.*?(\bcomplete\b|\bplanned\b)", readme_text, flags=re.I)
        if m:
            readme_p4 = m.group(1).lower()
            pl_p4 = phase_status.get(4, "")
            if readme_p4 != pl_p4:
                emit("FAIL", "docs", "readme-phase4", f"README Phase 4 status '{readme_p4}' differs from phase-list '{pl_p4}'")
                ok = False
                if fail_fast: return False
            else:
                emit("PASS", "docs", "readme-phase4", f"README and phase-list agree on Phase 4 ({readme_p4})")
        else:
            emit("FAIL", "docs", "readme-phase4", "could not locate README Phase 4 status")
            ok = False
            if fail_fast: return False

    charter = REPO / "docs/releases/v0.1.0/release-charter.md"
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
            # Also check inline negation in the 150 chars before and after
            start = max(0, pos - 150)
            ctx_before = lower[start:pos]
            ctx_after = lower[pos:pos + 150]
            combined = ctx_before + " " + ctx_after
            if re.search(
                r"(no |not |without |excludes? |lacks? |absence of |must not add|does not add|does not implement|contains no|out of scope|explicitly out|non-goal)",
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

    if not ok and fail_fast: return False

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

    sdk = find_sdk()
    if sdk is None:
        emit_prereq("sdk", "ANDROID_HOME and ANDROID_SDK_ROOT not set or invalid")
        return None
    if not (sdk / "platforms/android-36").is_dir():
        emit_prereq("sdk-platform", "SDK Platform 36 missing")
        return None
    emit("PASS", "android", "sdk-platform", "Platform 36 present")
    build_tools = sdk / "build-tools/36.0.0"
    if not build_tools.is_dir():
        emit_prereq("sdk-build-tools", "SDK Build Tools 36.0.0 missing")
        return None
    aapt2 = build_tools / "aapt2"
    if not aapt2.is_file() or not os.access(aapt2, os.X_OK):
        emit_prereq("aapt2", "Build Tools 36.0.0 aapt2 missing or not executable")
        return None
    emit("PASS", "android", "sdk-build-tools", "Build Tools 36.0.0 present")
    emit("PASS", "android", "aapt2", "aapt2 present and executable")

    gradlew = REPO / "gradlew"
    if not gradlew.is_file() or not os.access(gradlew, os.X_OK):
        emit_prereq("gradlew-exec", "gradlew missing or not executable in working tree")
        return None
    emit("PASS", "android", "gradlew-exec", "gradlew present and executable")
    return sdk


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
        expectations = {"agp": "9.2.1", "kotlinCompose": "2.3.10", "composeBom": "2026.06.00", "activityCompose": "1.13.0"}
        bad = []
        for key, expected in expectations.items():
            m = re.search(rf'^{key}\s*=\s*"([^"]+)"', text, flags=re.M)
            if not m or m.group(1) != expected:
                bad.append(f"{key}={m.group(1) if m else None}")
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
        expectations = {
            "namespace": 'namespace = "io.github.franchoy.nudgewhen"',
            "applicationId": 'applicationId = "io.github.franchoy.nudgewhen"',
            "compileSdk": "compileSdk = 36",
            "minSdk": "minSdk = 26",
            "targetSdk": "targetSdk = 36",
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
    if (act.get(f"{{{NS_ANDROID}}}name") != ".MainActivity"
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
    expectations = {
        "package": "package: name='io.github.franchoy.nudgewhen'",
        "versionCode": "versionCode='1'",
        "versionName": "versionName='0.1.0'",
        "compileSdkVersion": "compileSdkVersion='36'",
        "minSdkVersion": "minSdkVersion:'26'",
        "targetSdkVersion": "targetSdkVersion:'36'",
        "launchable": "launchable-activity: name='io.github.franchoy.nudgewhen.MainActivity'",
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
    if sig_name != "io.github.franchoy.nudgewhen.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION":
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
    if (act.get(f"{{{NS_ANDROID}}}name") != "io.github.franchoy.nudgewhen.MainActivity"
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


# ---------- main ----------

def print_summary_and_gate(args: argparse.Namespace) -> None:
    passed = sum(1 for r in _RESULTS if r[0] == "PASS")
    failed = sum(1 for r in _RESULTS if r[0] == "FAIL")
    skipped = sum(1 for r in _RESULTS if r[0] == "SKIP")
    print(f"SUMMARY pass={passed} fail={failed} skip={skipped}")
    sel = resolve_groups(args)
    if isinstance(sel, tuple):
        all_three = set(sel) == set(GROUP_ORDER)
        no_fail = failed == 0
        not_skipped = "android" in sel
        if all_three and no_fail and not_skipped and not args.skip_android:
            print("release_gate=SATISFIED")
        else:
            print("release_gate=NOT_SATISFIED")


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    sel = resolve_groups(args)
    if isinstance(sel, int):
        return sel

    if args.require_clean:
        before = git_status_short()
        if before.strip():
            emit("FAIL", "required", "clean-state", "non-ignored uncommitted changes present")
            print_summary_and_gate(args)
            return 1
        emit("PASS", "required", "clean-state", "non-ignored state clean before validation")

    overall_ok = True
    for grp in sel:
        if grp == "required":
            grp_ok = check_required(args, args.fail_fast)
        elif grp == "docs":
            grp_ok = check_docs(args, args.fail_fast)
        elif grp == "android":
            grp_ok = check_android(args)
        else:
            continue
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

    if _PREREQ_FAILED:
        print_summary_and_gate(args)
        return 2
    print_summary_and_gate(args)
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
