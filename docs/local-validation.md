# Local Validation — NudgeWhen v0.1.1

**Document status:** Release-aware carried-forward baseline — the v0.1.0 Phase 4 local-validation baseline is carried forward into the active `v0.1.1` release train on `release/v0.1.1`; a single release-contract source was introduced in Phase 3A1, Phase 3A2 wires the `required` group to load, structurally validate, and cross-check that contract, and Phase 3A3a extends the `docs` group with contract-driven active release-document checks (active phase list, per-phase status, README active release, charter consistency) plus `.json` text hygiene — Android-group, CLI argument-parsing, and release-gate architectural refactoring remains for later Phase 3 subphases, Phase 3 is not yet complete, and no controlled negative-path regression coverage exists yet

## Purpose and scope

This document describes the Phase 4 local validation suite for the NudgeWhen `v0.1.0` release. The suite is a small, deterministic, dependency-free set of checks that the maintainer can run from a fresh checkout to confirm that the repository is in a valid pre-release state. The suite is intentionally local: it does not clone, fetch, push, commit, create worktrees, or modify repository content. It writes only into the ignored Gradle and Android build output paths when the Android group is run.

The Phase 4 local-validation implementation baseline is the `v0.1.0` local-validation baseline. It was established on `release/v0.1.0`, was carried through the released `v0.1.0` GitHub release, and remains the foundation of the active `v0.1.1` release train on `release/v0.1.1`. The v0.1.0 validator baseline remains the foundation; Phase 3A2 added the required-group release-contract validation that loads, structurally validates, and source cross-checks `scripts/release_contract.json` as a single `release-contract` check within the `required` group, and Phase 3A3a added contract-driven active release-document checks and `.json` text hygiene to the `docs` group. Android-group, CLI argument-parsing, and release-gate architectural refactoring remains for later Phase 3 work. Phase 3 is not complete, and controlled negative-path regression coverage remains deferred.

## Dynamic private-working-material invariant

The validator applies a privacy-safe aggregate check to the generic `session-ses_*.md` pattern. The invariant is not that a fixed number of matching paths exists, but that every matching path remains ignored, untracked, unstaged, and unnamed in publishable evidence. A change in the aggregate count does not by itself indicate a defect; the safety properties are the requirements. The invariant is:

- every matching path is ignored (the active `.gitignore` rule applies);
- every matching path is untracked (not present in `git ls-files`);
- every matching path is unstaged (not present in `git diff --cached`);
- no matching path fails any of those checks;
- the count itself is not fixed and is not a release-correctness invariant;
- matching filenames and file contents are never published as evidence.

The validator prints counts only and never prints a matching filename, file metadata, or content. The invariant is satisfied in the current candidate. Either clean-checkout proof, when performed, will record the post-proof aggregate state; the proof itself does not change the invariant.

## Release contract

Phase 3A1 introduced a single release-contract source at `scripts/release_contract.json`. The contract is a standard-library-readable, deterministic JSON document with two-space indentation, sorted logically by section, and a top-level `schema_version` field. It is the authoritative location for the active release identity, the active release documents, the phase model, the Android artifact identity (including the current committed version metadata and the Phase 5 target version metadata), the validation-group contract, and the historical release pointer. The current `v0.1.1` values are present in the file at the time of the Phase 3A1 Build.

Phase 3A2 wires only the `required` group to load, structurally validate, and cross-check this contract. Within the `required` group, the `check_release_contract` step (1) loads `scripts/release_contract.json` from the repository root, (2) decodes the bytes as UTF-8, (3) parses the JSON and verifies the top-level `schema_version`, the presence of every top-level object (`release`, `release_documents`, `phase_model`, `android`, `validation`, `historical`), and the type and value constraints of every required field, (4) cross-checks the `release.active_branch` and `release.version` consistency, (5) verifies that each `release_documents` path resolves inside the repository and points to an existing file, (6) verifies the `phase_model.expected_statuses` prefix-of-Complete-then-Planned ordering across the declared `first_phase`/`last_phase` range, (7) cross-checks the `android` block against the source `app/build.gradle.kts` (`namespace`, `applicationId`, `compileSdk`, `minSdk`, `targetSdk`, `versionCode`, `versionName`) and against the source `app/src/main/AndroidManifest.xml` (presence of the declared launcher activity), (8) verifies the `validation` group contract (the literal `required`/`docs`/`android` group list, the `all` alias, the `release_gate_requires_groups` list, the `release_gate_requires_android_not_skipped`, `require_clean_supported`, `no_network`, and `no_dependency_installation` boolean invariants), and (9) verifies the `historical` block (`previous_release_version`, `previous_release_docs_root` resolving to an existing directory, `previous_release_is_historical` boolean). A failure in any of these conditions emits a `FAIL prerequisite/release-contract` line, blocks the remainder of the `required` group, and prevents release-gate satisfaction. A successful check emits a single `PASS required/release-contract` line and the `required` group proceeds to its remaining file-presence, executable-bit, wrapper, `.gitignore`, and `.gitattributes` checks.

Phase 3A2 is intentionally narrow with respect to the `android` group, the CLI argument parser, and the release-gate calculation. The `android` group continues to use its embedded v0.1.0 Phase 4 expected values for the Gradle configuration, source-manifest boundary, merged-manifest allowlist, and APK metadata; the CLI argument parser and group-resolution logic, the prerequisite framework, the candidate and clean-checkout mode handling, the exit-code semantics (0, 1, 2), the release-gate calculation, the no-network behavior, and the no dependency-installation behavior are preserved without change. Broader Android-group, CLI, and release-gate architectural refactoring remains for later Phase 3 subphases; this document does not claim that Phase 3 is complete and does not claim that controlled negative-path regression coverage exists yet.

### Phase 3A3a — contract-driven docs-group wiring

Phase 3A3a extends the `docs` group to reuse the release contract that the `required` group loads and validates. `scripts/release_contract.json` is the authoritative current-release contract for both groups. The `required` group continues to load and validate the contract as a single `release-contract` check that emits `PASS required/release-contract — release contract loaded and validated`. The same cached contract is then reused silently by the `docs` group for its active release-document checks. A successful silent contract load in the `docs` group does not add a `PASS docs/...` line and does not change the docs count of ten passes; a contract prerequisite failure emits exactly one `FAIL prerequisite/release-contract — [concise reason]` line and produces exit `2`. Controlled negative-path regression testing remains deferred to Phase 4 and is not yet claimed; comprehensive absolute-path redaction guarantees are not claimed for the docs-group output.

The phase-list path comes from `release_documents.phase_list`. The phase range comes from `phase_model.first_phase` and `phase_model.last_phase`. Expected statuses come from `phase_model.expected_statuses`. The `docs/phase-headings` check requires the exact ordered and unique declared range; for the current contract, Phase 0 through Phase 7 are required. Each phase is bounded from its own phase heading to the next phase heading or EOF. Each bounded phase requires exactly one `### Status` heading. The status subsection ends at the next Markdown heading of any level or the phase-section end. Exactly one nonblank, unformatted `Complete` or `Planned` line is required. The observed value must equal the phase-specific contract value; a later heading or phase cannot supply an earlier phase's status. The successful state for the current contract is `3 Complete, 5 Planned`. Controlled negative fixtures for the active phase-list and per-phase status checks remain deferred to Phase 4 and do not yet exist.

The `docs/readme-active-release` check requires the README to contain the contract's active release version and active branch. The `docs/charter-consistency` check uses the charter path from `release_documents.charter` and verifies that the charter is consistent with the absence of all seven product-functionality categories in any non-negation context. The historical v0.1.0 charter and phase list are no longer treated as active sources for the active release-document checks. Historical `EXP-0007` structure validation is preserved as an intentionally historical stable check that is independent of the active contract.

The `.json` extension now participates in the docs-group UTF-8 and trailing-whitespace validation. `.json` files are added to the text inventory alongside the existing text extensions, and `scripts/release_contract.json` is included in the UTF-8 and trailing-whitespace checks through the same `docs/utf8` and `docs/trailing-ws` PASS lines.

The contract is a data source for the validator; it is not itself a validator, and it does not run, install dependencies, or perform network access. The contract is loaded through the standard library only (`open()` / `read_bytes()` / `json.loads()`); no third-party library is introduced. Phase 3 is not yet complete; Android-group, CLI, and release-gate architectural refactoring remains for later Phase 3 subphases, and no controlled negative-path regression coverage exists yet.

## Primary command

```bash
./scripts/validate-local.sh
```

This runs every check in the `required`, `docs`, and `android` groups, aggregates failures, and prints a final `release_gate=...` line.

## Groups

The suite exposes three groups. `--group` is repeatable.

| Group | Purpose |
|---|---|
| `required` | Required file presence, prohibited file absence (no tracked `local.properties`, APK, AAB, `app/build/`, `.gradle/`, `.kotlin/`, screenshot, bytecode, or private-session export), `.gitignore` and `.gitattributes` contracts, Gradle wrapper presence, `gradlew` executable bit, shell entry-point executable bit, and release-contract loading, structural validation, and source cross-checking of `scripts/release_contract.json` (single `release-contract` check added by Phase 3A2). |
| `docs` | UTF-8 and trailing-whitespace hygiene (including `.json` files), `gradlew.bat` CRLF and SHA-256 verification, Markdown link integrity (relative, root-relative, anchors, optional fragments, optional quoted titles, external URLs), contract-driven active release-document checks (ordered phase headings from the active phase list, per-phase status bounded to the phase section, README active release version and branch, charter non-functionality consistency for all seven categories), experiment-record minimum structure, EXP-0007 full Phase 4 structure, publishable-content placeholder and privacy scan. |
| `android` | Prerequisite checks (Python 3.10+, Java 17+, SDK via `ANDROID_HOME`/`ANDROID_SDK_ROOT`, Platform 36, Build Tools 36.0.0, `aapt2`, `gradlew`); root and app `build.gradle.kts` prohibited-Kotlin configuration; version-catalog and `app/build.gradle.kts` configuration; exact source-manifest boundary; AGP-merged-manifest exact contract; Gradle project discovery; debug assembly; lint; APK existence and metadata. |

`--group all` is equivalent to selecting all three groups. The default selection when no `--group` is given is also all three groups.

## Options

| Option | Effect |
|---|---|
| `--group NAME` | Add a group to the selection. Repeatable. NAME is one of `required`, `docs`, `android`, `all`. |
| `--skip-android` | Remove the `android` group from the default or `--group all` selection. |
| `--offline` | Pass `--offline` to Gradle. Required on subsequent runs once the machine-level caches are provisioned. |
| `--fail-fast` | Stop after the first failed check. The default is to aggregate. |
| `--require-clean` | Require a clean non-ignored Git state before and after validation. In clean mode, every required release file must be tracked; filesystem presence alone is insufficient. |
| `--help` | Show usage. |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Every selected check passed. |
| `1` | One or more selected checks failed (a normal repository-content defect). |
| `2` | Invocation or prerequisite error. Includes missing or outdated `python3` (Python below 3.10); missing Java; Java below 17; neither `ANDROID_HOME` nor `ANDROID_SDK_ROOT` resolving to a usable SDK; missing Platform 36; missing Build Tools 36.0.0; missing or non-executable `aapt2`; missing or non-executable Gradle wrapper; conflicting command-line options such as `--skip-android` combined with explicit `--group android`; release-contract prerequisite failures (a missing, unreadable, malformed, structurally invalid, or internally inconsistent `scripts/release_contract.json` state). Argparse usage errors also exit `2`. A missing Java executable produces a single `FAIL prerequisite/java` line and exit `2`; it does not produce a Python traceback or expose the absolute executable path. A release-contract prerequisite failure produces a single `FAIL prerequisite/release-contract` line and exit `2`; expected handled prerequisite failures do not produce a Python traceback. Controlled negative-path regression coverage and comprehensive path-redaction guarantees are not yet claimed. |

## Prerequisites

The shell entry point requires:

- `python3` on `PATH`;
- Python 3.10 or newer;
- the `validate_local.py` script present at `scripts/validate_local.py` next to the shell entry point.

The Android group additionally requires:

- `java` on `PATH`, with major version at least 17;
- `ANDROID_HOME` or `ANDROID_SDK_ROOT` set to a valid SDK directory;
- SDK Platform 36 present;
- SDK Build Tools 36.0.0 present, with `aapt2` present and executable;
- the repository Gradle wrapper present and executable.

A failure in any prerequisite produces a `FAIL prerequisite/NAME` line and process exit `2`. The suite does not print concrete installation paths.

## Release-gate semantics

The literal `release_gate=SATISFIED` is printed only when the effective selection is all three groups, every required prerequisite passed, the `required`, `docs`, and `android` groups all passed, Android was not skipped, and no selected check failed. In every other case the literal `release_gate=NOT_SATISFIED` is printed.

The `SUMMARY` line is the authoritative count of every emitted `PASS`, `FAIL`, and `SKIP` result. Prerequisite passes and prerequisite failures are recorded through the same result collector as content checks, and every emitted result contributes to the summary exactly once. No `PASS` or `FAIL` is printed without being counted, and no result is counted without being printed.

Consequences:

- `--group required` may exit `0` and still print `release_gate=NOT_SATISFIED`. A partial run never satisfies the release gate.
- `--group docs` may exit `0` and still print `release_gate=NOT_SATISFIED`.
- `--group android` may exit `0` and still print `release_gate=NOT_SATISFIED`.
- `--skip-android` removes Android from the selection; the run cannot satisfy the release gate.
- A prerequisite failure (exit `2`) always prevents release-gate satisfaction.
- Only the complete all-groups run without `--skip-android` and without prerequisite failures can satisfy the release gate.

## Expected summary counts (Phase 4 candidate)

The following counts describe the Phase 4 candidate and may change only when the declared validation inventory changes. A maintainer reading a frozen result can compare the printed `SUMMARY` line against these counts to detect missing checks, duplicate emissions, or summary-accounting defects.

| Run | Expected summary | Expected `release_gate` | Expected exit |
|---|---|---|---|
| `--group required` (succeeding) | `SUMMARY pass=8 fail=0 skip=0` | `NOT_SATISFIED` | `0` |
| `--group docs` (succeeding) | `SUMMARY pass=10 fail=0 skip=0` | `NOT_SATISFIED` | `0` |
| `--group android --offline` (succeeding) | `SUMMARY pass=16 fail=0 skip=0` | `NOT_SATISFIED` | `0` |
| `--skip-android` (succeeding) | `SUMMARY pass=18 fail=0 skip=0` | `NOT_SATISFIED` | `0` |
| `--offline` all-groups (succeeding) | `SUMMARY pass=34 fail=0 skip=0` | `SATISFIED` | `0` |
| Missing Java (`--group android`) | `SUMMARY pass=1 fail=1 skip=0` | `NOT_SATISFIED` | `2` |
| Missing SDK (`--group android`) | `SUMMARY pass=2 fail=1 skip=0` | `NOT_SATISFIED` | `2` |

The Android-group total of sixteen passes is the sum of the six prerequisite passes (`python`, `java`, `sdk-platform`, `sdk-build-tools`, `aapt2`, `gradlew-exec`) and the ten content checks (`build-config`, `version-catalog`, `gradle-wrapper`, `app-build-config`, `source-manifest`, `gradle-projects`, `gradle-build`, `apk-exists`, `apk-metadata`, `merged-manifest`). The all-groups total of thirty-four passes is the sum of eight required, ten docs, and sixteen android. The required-group total of eight passes is the sum of one `release-contract` check (loaded, structurally validated, and cross-checked by Phase 3A2) and seven pre-existing checks (`files`, `no-prohibited`, `gradlew-exec`, `shell-exec`, `wrapper-jar`, `gitignore`, `gitattributes`); the seven pre-existing checks remain unchanged in their semantics. The docs-group total of ten passes is the sum of `utf8`, `trailing-ws`, `gradlew-bat-crlf`, `md-links`, `phase-headings`, `phase-status`, `readme-active-release`, `charter-consistency`, `exp7-structure`, and `no-pii`; for the current `v0.1.1` release contract, the active phase list reports `3 Complete, 5 Planned` (Phase 0, Phase 1, Phase 2 are `Complete`; Phase 3, Phase 4, Phase 5, Phase 6, Phase 7 are `Planned`).

## Partial-run limitations

Partial runs (any subset of the three groups) are useful for a maintainer checking a single concern. They do not by themselves satisfy the Phase 4 release gate. The Phase 4 release gate is satisfiable only by the complete all-groups run.

## `--skip-android` limitation

`--skip-android` is intended for fast documentation-only iteration. A run that uses `--skip-android` cannot satisfy the Phase 4 release gate, even if every other group passes.

## `--require-clean` behavior

`--require-clean` is the strictest run. It requires the non-ignored Git state to be empty before validation starts, and to remain empty after validation finishes. The validation suite itself does not write tracked content; an increase in non-ignored status lines after the run is a failure of the run, not of the suite.

In `--require-clean` mode, every required release file must be returned by `git ls-files`. Filesystem presence alone is insufficient; an ignored-but-untracked required file does not satisfy the check. The five Phase 4 candidate files remain required in clean mode and must be tracked — they are not excluded from the required-file list.

`--require-clean` is intended for the clean-checkout proof, not for ordinary developer iteration. The ordinary maintainer run is `release_gate` oriented and does not require a clean state.

## Candidate and clean-checkout modes

Without `--require-clean` the validator operates in candidate mode. The documentation/text inventory is built from every path returned by `git ls-files -z` plus the five allowed untracked candidate paths (`.gitattributes`, `scripts/validate-local.sh`, `scripts/validate_local.py`, `docs/local-validation.md`, `docs/agentic-development/experiments/EXP-0007.md`) when present on disk. UTF-8, line-ending, trailing-whitespace, Markdown link, placeholder and privacy checks apply to the untracked candidate files as well as to the tracked text files.

In candidate mode the shell entry point must be executable in the working tree; in clean mode it must be tracked and executable in Git.

The validator never uses `find`, repository-wide `grep`, recursive globbing over the working tree, or ignored-file enumeration. It never reads ignored private working material.

## SDK environment-variable requirements

The `android` group discovers the Android SDK in this order:

1. `ANDROID_HOME`
2. `ANDROID_SDK_ROOT`

The suite does not hard-code any home, workspace, SDK-installation, Java-installation, Gradle-installation, or cache path. If neither variable is set or neither points at a valid SDK directory, the `android` group exits with a prerequisite error (`2`).

A common invocation is to set the two environment variables command-scoped to the existing local SDK installation and invoke the suite:

```bash
ANDROID_HOME="$SDK_PATH" ANDROID_SDK_ROOT="$SDK_PATH" ./scripts/validate-local.sh --offline
```

The exact SDK path is a local command argument and is not recorded anywhere in committed evidence.

## Supported environment

> "The Phase 4 local validation suite was validated on Linux x86_64 using OpenJDK 25.0.2, Python 3.12.1, GNU Bash, Android SDK Platform 36, Android SDK Build Tools 36.0.0 and the repository Gradle 9.4.1 wrapper. Java source and target compatibility remain 17. JDK 17 or newer is the documented minimum prerequisite. Other environments may work, but they were not validated during Phase 4."

## First developer run

A first developer run on a fresh checkout may require dependency downloads. Gradle will resolve the AGP, Kotlin Compose, Compose BOM, and Activity Compose dependencies. Once the machine-level caches are provisioned, subsequent runs can use `--offline`.

## Official Phase 4 proof

The official Phase 4 proof is the clean-checkout run, performed by an authorized post-Build administrative action that creates a temporary local clone, commits the nine final candidate paths into the clone with command-scoped synthetic identity, runs the suite inside the clone with `--offline --require-clean`, requires `release_gate=SATISFIED`, and removes the clone. The proof is performed under a separate authorization, not by the suite itself.

The Phase 4 proof uses `--offline` because the documented environment already has the required machine-level caches provisioned.

## Empty-cache and fresh-machine reproducibility

Phase 4 does not claim empty-cache reproducibility. The suite does not install dependencies, populate caches, or download the Android SDK. A fresh machine without the documented caches will fail the `android` group with a clear prerequisite or environment error.

## Generated build output

Generated Gradle and Android build output is written to `app/build/`, `.gradle/`, and `.kotlin/`. These paths are ignored. The suite does not delete or inspect that output beyond the explicit APK and merged-manifest paths required by the `android` group.

## Manifest and APK validation (high level)

The `android` group validates the source `AndroidManifest.xml` for the exact boundary declared in the Phase 3 evidence and the Phase 4 contract: exactly one root `application`; no root-level `uses-permission`, permission, service, receiver, provider, `activity-alias`, `meta-data`, `uses-library`, or other unexpected child; the application direct children must be exactly one `activity`; the activity is `.MainActivity` exported true, with one intent filter, one `MAIN` action, one `LAUNCHER` category, no data element, and no unexpected descendants.

The `android` group then parses the AGP-merged debug manifest and requires the exact maintainer-approved allowlist: one signature permission `io.github.franchoy.nudgewhen.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION` with a matching `uses-permission`; the application direct children must be exactly one activity, one provider, one receiver, and two `uses-library` elements; the provider is `androidx.startup.InitializationProvider` (exported false) with exactly three initializer metadata entries (`EmojiCompatInitializer`, `ProcessLifecycleInitializer`, `ProfileInstallerInitializer`) each with value `androidx.startup`; the receiver is `androidx.profileinstaller.ProfileInstallReceiver` (exported true, permission `android.permission.DUMP`); the optional libraries are `androidx.window.extensions` and `androidx.window.sidecar`, each with `required="false"`.

The `android` group then runs `aapt2 dump badging` on the produced debug APK and requires the exact package, version code, version name, compile SDK, minimum SDK, target SDK, and launcher activity values from the Phase 3 evidence.

## Release-charter non-functionality predicate

The `docs` group verifies that the release charter is consistent with the absence of all seven current-capability categories:

- reminders;
- notifications;
- voice or speech;
- location or geofencing;
- persistence;
- networking;
- background behavior.

The charter must contain a non-goals section, and any textual pattern that would indicate adding one of these capabilities must appear only in a non-goal context. A positive claim outside a non-goal context is a release-gate defect.

## Clean-checkout creation

The suite does not perform clean-checkout creation, deletion, or any related orchestration. Clean-checkout proof is a separate post-Build administrative action.

## CI

Phase 5 of `v0.1.0` established the GitHub Actions CI baseline on the `release/v0.1.0` branch. The committed workflow is `.github/workflows/ci.yml`; its only `validate` job step runs `./scripts/validate-local.sh --require-clean`. The shell script (`scripts/validate-local.sh`) sets `PYTHONDONTWRITEBYTECODE=1` and `exec`s `scripts/validate_local.py` with the passed arguments. The Python validator's `release_gate=SATISFIED` literal (printed by `print_summary_and_gate` at `scripts/validate_local.py` lines 1001-1014) is emitted only when all three validator groups (`required`, `docs`, `android`) are selected, no failures are recorded, the `android` group is in the selection, and `--skip-android` is not set; it is not emitted on the basis of the required and documentation groups alone. The `v0.1.0` release branch required the `validate` check (a single required check with classic branch protection). The Phase 4 local validator remains the command executed by CI on `v0.1.0`; the persistent CI configuration for `v0.1.1` is a Phase 2 deliverable and is not described here.

## Phase 5

Phase 5 (GitHub Actions CI Baseline) is complete on `v0.1.0`. The release branch required the `validate` check, the Phase 4 local validator was the command executed by CI, and the published `v0.1.0` GitHub release reflects this state. Phase 6 (Agent Evaluation Evidence) of `v0.1.0` is also complete; the historical "Phase 6 remains `Planned`" wording in earlier drafts of this document reflected the document's draft state at that time and no longer represents the final `v0.1.0` release state. The present document does not claim that any new release has been published or that any release pull request has been merged on the active `v0.1.1` train.

## Product functionality

The suite does not introduce reminder, notification, voice, location, persistence, networking, contextual, or background functionality. It validates the technical baseline only. The release charter remains consistent with the absence of product functionality.
