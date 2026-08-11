# Local Validation — NudgeWhen v0.1.1

**Document status:** Release-aware carried-forward baseline — the v0.1.0 Phase 4 local-validation baseline is carried forward into the active `v0.1.1` release train on `release/v0.1.1`; a single release-contract source was introduced in Phase 3A1, Phase 3A2 wires the `required` group to load, structurally validate, and cross-check that contract, Phase 3A3a extends the `docs` group with contract-driven active release-document checks (active phase list, per-phase status, README active release, charter consistency) plus `.json` text hygiene, Phase 3A4a added the clean missing-Git prerequisite failure that does not produce a traceback, Phase 3A4c made the active validation groups, default order, all-groups alias, and release-gate requirements contract-driven while preserving the existing CLI, candidate-mode, clean-checkout, exit-code, no-network, and no-dependency-installation semantics, and Phase 3A5 adds the invalid-Git-worktree prerequisite and moves the Android-group release-specific expectations (namespace, application ID, compile SDK, minimum SDK, target SDK, package name, current version code, current version name, source launcher activity, merged launcher activity, and the application-derived dynamic receiver permission name) onto the validated release contract — Phase 3's reusable validator architecture is accepted and complete; Phase 4 added the standard-library regression suite under `tests/` and additional repository-consistency checks in the validator and is accepted and complete; Phase 5 (Supply-Chain, Workspace Hygiene, and Release Metadata) is accepted and complete — Gradle distribution checksum, committed wrapper-JAR checksum validation, Python bytecode ignore rules, Dependabot configuration, Android version metadata transition, controlled Gradle bad-distribution rejection proof, and cumulative Phase 5 integration evidence are all recorded in `EXP-0029.md`.

## Purpose and scope

This document describes the Phase 4 local validation suite for the NudgeWhen release train. The suite is a small, deterministic, dependency-free set of checks that the maintainer can run from a fresh checkout to confirm that the repository is in a valid pre-release state. The suite is intentionally local: it does not clone, fetch, push, commit, create worktrees, or modify repository content. It writes only into the ignored Gradle and Android build output paths when the Android group is run.

The Phase 4 local-validation implementation baseline is the `v0.1.0` local-validation baseline. It was established on `release/v0.1.0`, was carried through the released `v0.1.0` GitHub release, and remains the foundation of the active `v0.1.1` release train on `release/v0.1.1`. The v0.1.0 validator baseline remains the foundation; Phase 3A2 added the required-group release-contract validation that loads, structurally validates, and source cross-checks `scripts/release_contract.json` as a single `release-contract` check within the `required` group, Phase 3A3a added contract-driven active release-document checks and `.json` text hygiene to the `docs` group, Phase 3A4a added the clean missing-Git prerequisite failure that does not produce a traceback, and Phase 3A4c made the active validation groups, default order, all-groups alias, and release-gate requirements contract-driven while preserving the existing CLI, candidate-mode, clean-checkout, exit-code, no-network, and no-dependency-installation semantics. Phase 3A5 completes the remaining Phase 3 implementation work by adding the invalid-Git-worktree prerequisite and by moving the Android-group release-specific expectations (namespace, application ID, compile SDK, minimum SDK, target SDK, package name, current version code, current version name, source launcher activity, merged launcher activity, and the application-derived dynamic receiver permission name) onto the validated release contract. The accepted Phase 3 reusable validator architecture is complete. Phase 4 added the standard-library regression suite under `tests/` and additional repository-consistency checks in the validator and is accepted and complete.

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

Phase 3A2 is intentionally narrow with respect to the `android` group, the CLI argument parser, and the release-gate calculation. At the time of Phase 3A2 the `android` group continued to use its embedded v0.1.0 Phase 4 expected values for the Gradle configuration, source-manifest boundary, merged-manifest allowlist, and APK metadata; the CLI argument parser and group-resolution logic, the prerequisite framework, the candidate and clean-checkout mode handling, the exit-code semantics (0, 1, 2), the release-gate calculation, the no-network behavior, and the no dependency-installation behavior were preserved without change. After Phase 3A2, broader Android-group, CLI, and release-gate architectural refactoring remained for later Phase 3 subphases; Phase 3A5 has since completed the Android-group expectation refactoring and the contract-driven CLI and release-gate work. The accepted Phase 3 reusable validator architecture is complete.

### Phase 3A3a — contract-driven docs-group wiring

Phase 3A3a extends the `docs` group to reuse the release contract that the `required` group loads and validates. `scripts/release_contract.json` is the authoritative current-release contract for both groups. The `required` group continues to load and validate the contract as a single `release-contract` check that emits `PASS required/release-contract — release contract loaded and validated`. The same cached contract is then reused silently by the `docs` group for its active release-document checks. A successful silent contract load in the `docs` group does not add a `PASS docs/...` line and does not change the docs count of eleven passes; a contract prerequisite failure emits exactly one `FAIL prerequisite/release-contract — [concise reason]` line and produces exit `2`. Comprehensive absolute-path redaction guarantees are not claimed for the docs-group output.

The phase-list path comes from `release_documents.phase_list`. The phase range comes from `phase_model.first_phase` and `phase_model.last_phase`. Expected statuses come from `phase_model.expected_statuses`. The `docs/phase-headings` check requires the exact ordered and unique declared range; for the current contract, Phase 0 through Phase 7 are required. Each phase is bounded from its own phase heading to the next phase heading or EOF. Each bounded phase requires exactly one `### Status` heading. The status subsection ends at the next Markdown heading of any level or the phase-section end. Exactly one nonblank, unformatted `Complete` or `Planned` line is required. The observed value must equal the phase-specific contract value; a later heading or phase cannot supply an earlier phase's status. The successful state for the current contract is `6 Complete, 2 Planned`.

The `docs/readme-active-release` check requires the README to contain the contract's active release version and active branch. The `docs/charter-consistency` check uses the charter path from `release_documents.charter` and verifies that the charter is consistent with the absence of all seven product-functionality categories in any non-negation context. The historical v0.1.0 charter and phase list are no longer treated as active sources for the active release-document checks. Historical `EXP-0007` structure validation is preserved as an intentionally historical stable check that is independent of the active contract.

The `.json` extension now participates in the docs-group UTF-8 and trailing-whitespace validation. `.json` files are added to the text inventory alongside the existing text extensions, and `scripts/release_contract.json` is included in the UTF-8 and trailing-whitespace checks through the same `docs/utf8` and `docs/trailing-ws` PASS lines.

The contract is a data source for the validator; it is not itself a validator, and it does not run, install dependencies, or perform network access. The contract is loaded through the standard library only (`open()` / `read_bytes()` / `json.loads()`); no third-party library is introduced. The Phase 3 reusable validator architecture is accepted and complete. The Phase 4 regression suite and repository-consistency enforcement are accepted and complete; controlled regression coverage for the negative-path contradiction classes is exercised by the accepted Phase 4 implementation.

### Phase 3A4 — contract-first CLI, Git prerequisite, group registry, and release gate

Phase 3A4a and Phase 3A4c together move the validator's command-line construction, active-group determination, all-groups alias, and release-gate calculation onto the validated release contract. Phase 3A4a is the missing-Git prerequisite; Phase 3A4c is the contract-driven CLI, group registry, and release gate.

#### Contract-first CLI construction

`main` loads and fully validates the cached release contract before constructing `argparse`. The parser's allowed real group identifiers and its all-groups alias come from that validated contract. As a direct consequence, an invalid contract takes precedence over `--help` handling, malformed CLI handling, and the Git prerequisite check: when the contract fails to load or validate, the validator emits a single `FAIL prerequisite/release-contract` result, prints `SUMMARY pass=0 fail=1 skip=0` and `release_gate=NOT_SATISFIED`, and exits `2` without constructing `argparse`. When the contract is valid, normal `argparse` usage, the standard `--help` output, and the standard `argparse` exit-`2` behavior for unknown options, missing `--group` values, unsupported groups, and unexpected positional arguments are preserved.

#### Git prerequisite (Phase 3A4a)

When the contract is valid and the resolved groups have been determined, the validator checks that the `git` executable is resolvable on `PATH` before executing any group. A missing `git` causes the validator to emit exactly three output lines:

```text
FAIL prerequisite/git — git executable not found
SUMMARY pass=0 fail=1 skip=0
release_gate=NOT_SATISFIED
```

The process then exits with status `2`; `exit=2` is not a fourth validator-output line. The historical controlled shell command that captured the missing-Git behavior printed `exit=2` separately to expose the captured process status. The three result lines contain no Python traceback, and the absolute path of the `git` executable is never included in the result message. The Git prerequisite is checked after contract validation and after `argparse` argument parsing; it is therefore not reached when the contract is invalid or when the CLI is malformed.

#### Static implementation-capability registry

`VALIDATION_HANDLERS` is a static implementation registry that maps the currently implemented real group identifiers (`required`, `docs`, `android`) to normalized wrapper functions. The registry represents code capability only. The contract determines which supported groups are active and their default order, but a contract group that is not present in `VALIDATION_HANDLERS` is rejected as an invalid contract before CLI construction. Arbitrary new group identifiers therefore cannot be activated merely by listing them in the contract; an implementation handler must exist for every active group. The registry contents and the contract group list are intentionally aligned: the contract validator requires that every identifier in `validation.groups` is a key in `VALIDATION_HANDLERS`.

#### Contract-driven validation block

The contract validator already required that the `validation` block satisfy several invariants before the Phase 3A4 refactor; the Phase 3A4 refactor preserves those invariants and documents them as the source of the active group set, the alias, and the release-gate set. The required invariants are:

- `validation.groups` is a non-empty list of non-empty unique identifiers, every one of which is a key in `VALIDATION_HANDLERS`;
- `validation.all_alias` is a non-empty string that is not equal to any real group identifier;
- `validation.release_gate_requires_groups` is a non-empty list of non-empty unique identifiers and is a subset of `validation.groups`;
- `validation.release_gate_requires_android_not_skipped` is a Boolean;
- when that Android flag is `true`, the identifier `android` appears in both `validation.groups` and `validation.release_gate_requires_groups`;
- `validation.require_clean_supported`, `validation.no_network`, and `validation.no_dependency_installation` are each `true`.

The current contract declares `groups: ["required", "docs", "android"]` in that order, `all_alias: "all"`, and `release_gate_requires_groups: ["required", "docs", "android"]`; these are current contract values rather than permanently hard-coded CLI constants. A future release that changes any of these values does not require a code change in the validator; a future release that adds a new group requires both a new `VALIDATION_HANDLERS` entry and a contract change.

### Phase 3A5 — invalid-Git-worktree prerequisite and contract-driven Android expectations

Phase 3A5 completes the two remaining Phase 3 implementation gaps and makes the Android-group release-specific expectations fully contract-driven.

#### Invalid-Git-worktree prerequisite

After the existing missing-Git prerequisite passes and after the resolved groups have been determined, the validator runs an ordinary local Git worktree query against the repository root:

```text
git rev-parse --is-inside-work-tree
```

The check is performed only after contract validation, after `argparse` argument parsing, and after the missing-Git prerequisite; it therefore never executes when the contract is invalid, when the CLI is malformed, or when `git` is not on `PATH`. The check handles a nonzero Git exit status, an unexpected stdout value other than the exact worktree-positive literal, and a raised `OSError` from the subprocess call without propagating an exception, a Python traceback, or an absolute path.

On success the check emits no result line, so a successful run's summary totals are not increased. On failure the check emits exactly three output lines and returns process status `2`:

```text
FAIL prerequisite/git-worktree — repository is not a Git worktree
SUMMARY pass=0 fail=1 skip=0
release_gate=NOT_SATISFIED
```

The ordering of the four prerequisite and CLI steps is therefore:

1. invalid release contract (release-contract prerequisite);
2. argparse help or malformed invocation;
3. missing Git executable (git prerequisite);
4. invalid Git worktree (git-worktree prerequisite);
5. selected validation groups.

Missing Git and invalid worktree are distinct prerequisite conditions with distinct result identifiers (`prerequisite/git` versus `prerequisite/git-worktree`); the two are not conflated.

#### Contract-driven Android expectations

The Android group no longer embeds the v0.1.0 Phase 4 expected values for the release or application identity. The validated `android` block of `scripts/release_contract.json` is now the single source of truth for every existing Android expectation that represents release or application identity. The contract schema is unchanged; the contract's existing fields are sufficient.

The Android group uses the contract for at least the following:

- `android.compile_sdk` is the required SDK Platform directory and the user-facing result text for the `sdk-platform` prerequisite.
- `android.namespace`, `android.application_id`, `android.compile_sdk`, `android.min_sdk`, and `android.target_sdk` generate the release-specific `app-build-config` expectations.
- `android.launcher_activity_source` replaces the previous hard-coded `.MainActivity` expectation in the source-manifest check. The exhaustive source-manifest boundary and intent-filter checks are preserved unchanged.
- `android.package_name`, `android.current_version_code`, `android.current_version_name`, `android.compile_sdk`, `android.min_sdk`, `android.target_sdk`, and `android.launcher_activity_merged` generate the expected `aapt2 dump badging` values for the `apk-metadata` check.
- `android.launcher_activity_merged` replaces the previous hard-coded `io.github.franchoy.nudgewhen.MainActivity` expectation in the merged-manifest check.
- The application-derived dynamic receiver permission name is now built as `f"{android.package_name}.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION"` rather than embedding the package name twice.

At the time Phase 3A5 was accepted, the successful repository expected version code `1` and version name `0.1.0` for the `apk-metadata` check because those were then the contract's current committed `current_version_code` and `current_version_name` values. Phase 5D subsequently updated the candidate contract and Gradle metadata to version code `2` and version name `0.1.1` without requiring another Python source edit for those APK fields; those values are now the committed Phase 5 metadata. The validator continues to validate APK metadata against `current_version_code` and `current_version_name` rather than against the target fields.

#### Stable Android implementation invariants

The following Android expectations remain stable implementation constants because no corresponding release-contract field currently exists:

- the Build Tools `36.0.0` directory and the corresponding `sdk-build-tools` and `aapt2` prerequisite text;
- Java 17 source and target compatibility in `app-build-config`;
- Compose enablement (`compose = true`) in `app-build-config`;
- the exhaustive source-manifest boundary and intent-filter structure;
- the merged-manifest provider, receiver, metadata, and optional-library allowlists;
- the AGP-merged-manifest strictness and the source-manifest strictness themselves.

A future release that wishes to change any of those invariants must add a corresponding release-contract field and a contract-validation rule; the validator will not derive them from the contract until that future field exists.

#### Generic validator identity

The module docstring, the `argparse` description, and any other user-facing or module-level wording that described the validator itself as exclusively for the `v0.1.0` release has been replaced with release-neutral wording. Historical checks whose purpose is explicitly to preserve v0.1.0 evidence (such as the `EXP-0007` structure validation, the `v0.1.0` historical release pointer in the contract, and the historical v0.1.0 charter and phase list allowlists) are preserved unchanged.

## Primary command

```bash
./scripts/validate-local.sh
```

This runs every check in the `required`, `docs`, and `android` groups, aggregates failures, and prints a final `release_gate=...` line.

## Groups

The suite exposes the groups declared by the validated release contract. For the current contract, three groups are active: `required`, `docs`, and `android`. The current contract's `validation.groups` list is `["required", "docs", "android"]` in that order; the current `validation.all_alias` is `"all"`. These are current contract values rather than permanently hard-coded CLI constants. A future release that lists a different set of supported groups in its contract does not require a validator code change; a future release that adds a new real group requires both a new `VALIDATION_HANDLERS` entry and a contract change. `--group` is repeatable. The current real group identifiers and the current alias are accepted as `--group` values; the alias is a real `argparse` choice that is not equal to any real group identifier.

| Group | Purpose |
|---|---|
| `required` | Required file presence, prohibited file absence (no tracked `local.properties`, APK, AAB, `app/build/`, `.gradle/`, `.kotlin/`, screenshot, bytecode, or private-session export), `.gitignore` and `.gitattributes` contracts, Gradle wrapper presence, `gradlew` executable bit, shell entry-point executable bit, and release-contract loading, structural validation, and source cross-checking of `scripts/release_contract.json` (single `release-contract` check added by Phase 3A2). |
| `docs` | UTF-8 and trailing-whitespace hygiene (including `.json` files), `gradlew.bat` CRLF and SHA-256 verification, Markdown link integrity (relative, root-relative, anchors, optional fragments, optional quoted titles, external URLs), contract-driven active release-document checks (ordered phase headings from the active phase list, per-phase status bounded to the phase section, README active release version and branch, charter non-functionality consistency for all seven categories), experiment-record minimum structure, EXP-0007 full Phase 4 structure, publishable-content placeholder and privacy scan. |
| `android` | Prerequisite checks (Python 3.10+, Java 17+, SDK via `ANDROID_HOME`/`ANDROID_SDK_ROOT`, Platform 36, Build Tools 36.0.0, `aapt2`, `gradlew`); root and app `build.gradle.kts` prohibited-Kotlin configuration; version-catalog and `app/build.gradle.kts` configuration; exact source-manifest boundary; AGP-merged-manifest exact contract; Gradle project discovery; debug assembly; lint; APK existence and metadata. |

When no `--group` is given, the selection is the contract-declared groups in their contract order. The alias expands to every contract-declared group at the alias's position in the invocation. Repeated groups and overlaps caused by alias expansion are deduplicated. Deduplication preserves the first-seen order of the alias-expanded invocation: if the invocation is `--group required all docs`, the resolved selection is `(required, docs)`; if the invocation is `--group all docs required`, the resolved selection is `(required, docs)` in that order, because `all` expanded first and `required` was the first of its expanded groups to be deduplicated against. The current default and `--group all` therefore produce the same resolved order, namely the contract order, while a hand-written invocation may interleave and still produce a first-seen deduplicated selection.

## Options

| Option | Effect |
|---|---|
| `--group NAME` | Add a group to the selection. Repeatable. NAME is one of the current real group identifiers declared in the contract or the current all-groups alias. |
| `--skip-android` | Remove the `android` group from the default or `--group all` selection. The default `--skip-android` invocation and `--group all --skip-android` are both valid and remove Android from the expanded or default selection. |
| `--offline` | Pass `--offline` to Gradle. Required on subsequent runs once the machine-level caches are provisioned. |
| `--fail-fast` | Stop after the first failed check. The default is to aggregate. |
| `--require-clean` | Require a clean non-ignored Git state before and after validation. In clean mode, every required release file must be tracked; filesystem presence alone is insufficient. |
| `--help` | Show usage. |

Explicit `--group android --skip-android` is an invocation conflict: the user has both named Android as a selected group and asked that Android be skipped. That invocation exits `2` with a `FAIL invocation — --skip-android combined with explicit --group android` message, prints the summary and `release_gate=NOT_SATISFIED`, and does not execute any group.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Every selected check passed. |
| `1` | One or more selected checks failed (a normal repository-content defect). |
| `2` | Invocation or prerequisite error. Includes missing or outdated `python3` (Python below 3.10); missing Java; Java below 17; neither `ANDROID_HOME` nor `ANDROID_SDK_ROOT` resolving to a usable SDK; missing Platform 36; missing Build Tools 36.0.0; missing or non-executable `aapt2`; missing or non-executable Gradle wrapper; conflicting command-line options such as `--skip-android` combined with explicit `--group android`; release-contract prerequisite failures (a missing, unreadable, malformed, structurally invalid, or internally inconsistent `scripts/release_contract.json` state). Argparse usage errors also exit `2`. |

The valid-contract missing-Git behavior added by Phase 3A4a is exactly three output lines from the validator:

```text
FAIL prerequisite/git — git executable not found
SUMMARY pass=0 fail=1 skip=0
release_gate=NOT_SATISFIED
```

The process then exits with status `2`; `exit=2` is not a fourth validator-output line. The historical controlled shell command that captured the missing-Git behavior printed `exit=2` separately to expose the captured process status. The three result lines contain no Python traceback, and the absolute path of the `git` executable is never included in the result message. The Git prerequisite is checked only after contract validation and after `argparse` argument parsing; it is therefore not reached when the contract is invalid (in which case the contract prerequisite failure exits `2` first) or when the CLI is malformed (in which case `argparse` exits `2` first).

A missing Java executable produces a single `FAIL prerequisite/java` line and exit `2`; it does not produce a Python traceback or expose the absolute executable path. A release-contract prerequisite failure produces a single `FAIL prerequisite/release-contract` line and exit `2`; expected handled prerequisite failures do not produce a Python traceback. An invalid contract takes precedence over `--help`, malformed CLI handling, and the Git prerequisite: the contract is loaded and validated before `argparse` is constructed, so an invalid contract replaces the standard `argparse` help or error output for that invocation. The accepted Phase 4 regression suite provides the controlled negative-path coverage for the implemented contradiction classes; comprehensive path-redaction guarantees are not yet claimed.

The valid-contract invalid-Git-worktree behavior added by Phase 3A5 is exactly three output lines from the validator:

```text
FAIL prerequisite/git-worktree — repository is not a Git worktree
SUMMARY pass=0 fail=1 skip=0
release_gate=NOT_SATISFIED
```

The process then exits with status `2`. The three result lines contain no Python traceback, and the validator never includes the absolute path of any non-worktree directory in its result message. The Git-worktree prerequisite is checked only after contract validation, after `argparse` argument parsing, and after the missing-Git prerequisite; it is therefore not reached when the contract is invalid, when the CLI is malformed, or when `git` is not on `PATH`. The two Git prerequisites are not conflated: a missing executable is reported as `prerequisite/git`, and a non-worktree repository is reported as `prerequisite/git-worktree`.

## Prerequisites

The shell entry point requires:

- `python3` on `PATH`;
- Python 3.10 or newer;
- the `validate_local.py` script present at `scripts/validate_local.py` next to the shell entry point.

The Python validator additionally requires:

- `git` on `PATH` (added by Phase 3A4a). When the contract is valid, a missing `git` executable is detected before any group is executed and produces the exact valid-contract missing-Git output described in the `## Exit codes` section, with exit `2` and no Python traceback.
- that the repository root is inside a Git worktree (added by Phase 3A5). When the contract is valid, `git` is on `PATH`, and the repository root is not inside a Git worktree, the validator emits the exact valid-contract invalid-Git-worktree output described in the `## Exit codes` section, with exit `2` and no Python traceback. The check does not raise the historical unhandled Git error. The check is performed only after the missing-Git prerequisite passes; missing Git and invalid worktree are distinct prerequisite conditions.

The Android group additionally requires:

- `java` on `PATH`, with major version at least 17;
- `ANDROID_HOME` or `ANDROID_SDK_ROOT` set to a valid SDK directory;
- SDK Platform 36 present;
- SDK Build Tools 36.0.0 present, with `aapt2` present and executable;
- the repository Gradle wrapper present and executable.

A failure in any prerequisite produces a `FAIL prerequisite/NAME` line and process exit `2`. The suite does not print concrete installation paths.

## Release-gate semantics

The literal `release_gate=SATISFIED` is printed only when all of the following are true, evaluated against the validated release contract:

- every identifier in `validation.release_gate_requires_groups` is present in the resolved selection (containment, not exact set equality);
- no selected check produced a `FAIL` result;
- if `validation.release_gate_requires_android_not_skipped` is `true`, the identifier `android` is in the resolved selection and `--skip-android` is not set.

Containment is used rather than exact set equality: an extra group in the selection does not prevent the release gate from being satisfied, as long as the contract's required groups are all present and no check has failed. For the current contract, `validation.release_gate_requires_groups` is `["required", "docs", "android"]` and `validation.release_gate_requires_android_not_skipped` is `true`, so a successful complete `required` + `docs` + `android` run without `--skip-android` still satisfies the release gate, and a `--group required docs android --offline` run produces `SUMMARY pass=38 fail=0 skip=0` and `release_gate=SATISFIED` with exit `0`.

The `SUMMARY` line is the authoritative count of every emitted `PASS`, `FAIL`, and `SKIP` result. Prerequisite passes and prerequisite failures are recorded through the same result collector as content checks, and every emitted result contributes to the summary exactly once. No `PASS` or `FAIL` is printed without being counted, and no result is counted without being printed.

Consequences:

- `--group required` may exit `0` and still print `release_gate=NOT_SATISFIED`. A partial run never satisfies the release gate.
- `--group docs` may exit `0` and still print `release_gate=NOT_SATISFIED`.
- `--group android` may exit `0` and still print `release_gate=NOT_SATISFIED`.
- `--skip-android` removes Android from the selection; the run cannot satisfy the release gate for the current contract.
- A prerequisite failure (exit `2`) always prevents release-gate satisfaction.
- Only a successful run that contains every contract-required group, that records no failures, and that does not skip Android when the contract forbids skipping it can satisfy the release gate.

## Expected summary counts

The following counts describe the current validation inventory and may change only when the declared validation inventory changes. A maintainer reading a frozen result can compare the printed `SUMMARY` line against these counts to detect missing checks, duplicate emissions, or summary-accounting defects.

| Run | Expected summary | Expected `release_gate` | Expected exit |
|---|---|---|---|
| `--group required` (succeeding) | `SUMMARY pass=11 fail=0 skip=0` | `NOT_SATISFIED` | `0` |
| `--group docs` (succeeding) | `SUMMARY pass=11 fail=0 skip=0` | `NOT_SATISFIED` | `0` |
| `--group android --offline` (succeeding) | `SUMMARY pass=16 fail=0 skip=0` | `NOT_SATISFIED` | `0` |
| `--skip-android` (succeeding) | `SUMMARY pass=22 fail=0 skip=0` | `NOT_SATISFIED` | `0` |
| `--offline` all-groups (succeeding) | `SUMMARY pass=38 fail=0 skip=0` | `SATISFIED` | `0` |
| Missing Java (`--group android`) | `SUMMARY pass=1 fail=1 skip=0` | `NOT_SATISFIED` | `2` |
| Missing SDK (`--group android`) | `SUMMARY pass=2 fail=1 skip=0` | `NOT_SATISFIED` | `2` |

The current phase model is `6 Complete, 2 Planned`: `Complete` is `Phase 0`, `Phase 1`, `Phase 2`, `Phase 3`, `Phase 4`, and `Phase 5`; `Planned` is `Phase 6` and `Phase 7`. The required-group total of eleven passes consists of one `release-contract` check (loaded, structurally validated, and cross-checked by Phase 3A2), seven pre-Phase-5 checks (`files`, `no-prohibited`, `gradlew-exec`, `shell-exec`, `wrapper-jar`, `gitignore`, `gitattributes`), and three Phase 5 additions (`wrapper-jar-sha256`, `gitignore-python`, `dependabot-yaml`); `1 + 7 + 3 = 11`. The Phase 5A `wrapper-jar-sha256` check confirms the committed `gradle-wrapper.jar` matches the approved `WRAPPER_JAR_EXPECTED_SHA`; the Phase 5B `gitignore-python` check confirms the canonical Python bytecode ignore rules (`__pycache__/`, `*.py[cod]`) are present; the Phase 5C `dependabot-yaml` check confirms the bounded Dependabot configuration. The Android-group total of sixteen passes is the sum of the six prerequisite passes (`python`, `java`, `sdk-platform`, `sdk-build-tools`, `aapt2`, `gradlew-exec`) and the ten content checks (`build-config`, `version-catalog`, `gradle-wrapper`, `app-build-config`, `source-manifest`, `gradle-projects`, `gradle-build`, `apk-exists`, `apk-metadata`, `merged-manifest`). The ordinary all-groups total of thirty-eight passes is the sum of eleven required, eleven docs, and sixteen android (`11 + 11 + 16 = 38`). The skip-Android total of twenty-two passes is the sum of eleven required and eleven docs (`11 + 11 = 22`). The docs-group total of eleven passes is the sum of `utf8`, `trailing-ws`, `gradlew-bat-crlf`, `md-links`, `phase-headings`, `phase-status`, `readme-active-release`, `charter-consistency`, `exp7-structure`, `no-pii`, and the Phase 4 repository-consistency check (`repository-consistency`); for the current `v0.1.1` release contract, the active phase list reports `6 Complete, 2 Planned` (Phase 0, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5 are `Complete`; Phase 6, Phase 7 are `Planned`).

The Phase 5 inventory progression that brought the `required` group from eight to eleven is recorded as:

```text
Phase 5A:
+1 required/wrapper-jar-sha256

Phase 5B:
+1 required/gitignore-python

Phase 5C:
+1 required/dependabot-yaml

Phase 5D:
no validator-count change

Phase 5I:
no validator-count change
```

The cumulative regression inventory is `78 tests` from `python3 -B -m unittest tests.test_validator_core tests.test_validator_repository`.

## Partial-run limitations

Partial runs (any subset of the three groups) are useful for a maintainer checking a single concern. They do not by themselves satisfy the Phase 4 release gate. The Phase 4 release gate is satisfiable only by the complete all-groups run.

## `--skip-android` limitation

`--skip-android` is intended for fast documentation-only iteration. A run that uses `--skip-android` cannot satisfy the Phase 4 release gate, even if every other group passes.

## `--require-clean` behavior

`--require-clean` is the strictest run. It requires the non-ignored Git state to be empty before validation starts, and to remain empty after validation finishes. The validation suite itself does not write tracked content; an increase in non-ignored status lines after the run is a failure of the run, not of the suite.

In `--require-clean` mode, every required release file must be returned by `git ls-files`. Filesystem presence alone is insufficient; an ignored-but-untracked required file does not satisfy the check. The four Phase 4 regression-suite paths are required tracked files in clean mode and must be tracked — they are not excluded from the required-file list:

```text
tests/__init__.py
tests/_helpers.py
tests/test_validator_core.py
tests/test_validator_repository.py
```

`--require-clean` is intended for the clean-checkout proof, not for ordinary developer iteration. The ordinary maintainer run is `release_gate` oriented and does not require a clean state.

## Candidate and clean-checkout modes

Without `--require-clean` the validator operates in candidate mode. The documentation/text inventory is built from every path returned by `git ls-files -z` plus the nine-entry candidate-mode allowlist (`.gitattributes`, `scripts/validate-local.sh`, `scripts/validate_local.py`, `docs/local-validation.md`, `docs/agentic-development/experiments/EXP-0007.md`, `tests/__init__.py`, `tests/_helpers.py`, `tests/test_validator_core.py`, `tests/test_validator_repository.py`) when present on disk. UTF-8, line-ending, trailing-whitespace, Markdown link, placeholder and privacy checks apply to the untracked candidate files as well as to the tracked text files.

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

The official Phase 4 proof is the accepted implementation/evidence commit and the maintainer-supplied remote CI evidence, not a temporary local clone or a synthetic-identity commit. The accepted proof is:

```text
implementation/evidence commit:
65a41bf59ef0b05a3ff40217a031a585e503036f

subject:
test: enforce validator repository consistency

post-commit working tree:
clean

regression command:
python3 -B -m unittest tests.test_validator_core tests.test_validator_repository

regression:
Ran 64 tests
OK

clean gate command:
./scripts/validate-local.sh --require-clean

clean gate:
SUMMARY pass=37 fail=0 skip=0
release_gate=SATISFIED

push:
release/v0.1.1 advanced to 65a41bf59ef0b05a3ff40217a031a585e503036f

exact-head CI:
run 31258760694
workflow CI
event push
branch release/v0.1.1
head SHA 65a41bf59ef0b05a3ff40217a031a585e503036f
conclusion success
required job validate
required job result success
```

The exact-head CI run `31258760694` is maintainer-supplied completed remote evidence; this Build did not query GitHub and did not run GitHub Actions itself. The accepted proof records the real implementation/evidence commit, the clean committed-state regression, the clean committed-state validator, the push of `release/v0.1.1` to `65a41bf59ef0b05a3ff40217a031a585e503036f`, and the exact-head CI run that followed. The clean committed/CI canonical Phase 4 sequence is:

```bash
python3 -B -m unittest tests.test_validator_core tests.test_validator_repository
./scripts/validate-local.sh --require-clean
```

The accepted Phase 4 dirty-candidate iteration sequence is:

```bash
python3 -B -m unittest tests.test_validator_core tests.test_validator_repository
./scripts/validate-local.sh --group required
./scripts/validate-local.sh --group docs
./scripts/validate-local.sh --skip-android
```

Dirty partial runs correctly report `release_gate=NOT_SATISFIED`; the dirty-candidate sequence is not a substitute for the clean committed/CI canonical gate.

## Empty-cache and fresh-machine reproducibility

Phase 4 does not claim empty-cache reproducibility. The suite does not install dependencies, populate caches, or download the Android SDK. A fresh machine without the documented caches will fail the `android` group with a clear prerequisite or environment error.

## Generated build output

Generated Gradle and Android build output is written to `app/build/`, `.gradle/`, and `.kotlin/`. These paths are ignored. The suite does not delete or inspect that output beyond the explicit APK and merged-manifest paths required by the `android` group.

## Manifest and APK validation (high level)

The `android` group validates the source `AndroidManifest.xml` for the exact boundary declared in the Phase 3 evidence and the Phase 4 contract: exactly one root `application`; no root-level `uses-permission`, permission, service, receiver, provider, `activity-alias`, `meta-data`, `uses-library`, or other unexpected child; the application direct children must be exactly one `activity`; the activity name is taken from `android.launcher_activity_source` in the validated release contract (the current contract value is `.MainActivity`), the activity is exported true, with one intent filter, one `MAIN` action, one `LAUNCHER` category, no data element, and no unexpected descendants.

The `android` group then parses the AGP-merged debug manifest and requires the exact maintainer-approved allowlist: one signature permission whose name is built as `f"{android.package_name}.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION"` (for the current contract this resolves to `io.github.franchoy.nudgewhen.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`) with a matching `uses-permission`; the application direct children must be exactly one activity, one provider, one receiver, and two `uses-library` elements; the activity name is taken from `android.launcher_activity_merged` in the validated contract; the provider is `androidx.startup.InitializationProvider` (exported false) with exactly three initializer metadata entries (`EmojiCompatInitializer`, `ProcessLifecycleInitializer`, `ProfileInstallerInitializer`) each with value `androidx.startup`; the receiver is `androidx.profileinstaller.ProfileInstallReceiver` (exported true, permission `android.permission.DUMP`); the optional libraries are `androidx.window.extensions` and `androidx.window.sidecar`, each with `required="false"`.

The `android` group then runs `aapt2 dump badging` on the produced debug APK and requires the exact package, version code, version name, compile SDK, minimum SDK, target SDK, and launcher activity values generated from the validated contract's `android` block (`package_name`, `current_version_code`, `current_version_name`, `compile_sdk`, `min_sdk`, `target_sdk`, and `launcher_activity_merged`). Phase 5D introduced the candidate `current_version_code = 2` and `current_version_name = 0.1.1`; those values are now committed in the maintainer-supplied Phase 5 implementation/evidence commit `edf9da3cf5fef652c595936188e5918c2bd6e7f2`. The APK-metadata check therefore currently expects version code `2` and version name `0.1.1`.

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

The committed workflow is `.github/workflows/ci.yml`; its `validate` job runs the accepted Phase 4 regression suite immediately before the existing clean-checkout validator gate. The clean committed/CI Phase 4 validation sequence is:

```bash
python3 -B -m unittest tests.test_validator_core tests.test_validator_repository
./scripts/validate-local.sh --require-clean
```

The regression suite runs first and uses ordinary GitHub Actions sequential-step semantics, so a failure in the regression step prevents the later validator step from running. The `-B` flag passed to the Python interpreter prevents Python bytecode emission during this command. The second command is the existing full clean-state validator gate; `--require-clean` is appropriate for a clean committed checkout or CI. The shell script (`scripts/validate-local.sh`) sets `PYTHONDONTWRITEBYTECODE=1` and `exec`s `scripts/validate_local.py` with the passed arguments. The Python validator's `release_gate=SATISFIED` literal is emitted only when the validated contract's `release_gate_requires_groups` identifiers are all present in the resolved selection, no failures are recorded, and either `release_gate_requires_android_not_skipped` is `false` or Android is selected and not skipped; it is not emitted on the basis of a partial run.

The persistent CI configuration for `v0.1.1` was generalized in Phase 2 to run on pushes to `release/**`, on pull requests targeting `main`, on pushes to `main`, and on manual `workflow_dispatch`, preserving the stable `validate` job name. Phase 3 work subsequently landed on the active `release/v0.1.1` branch and the following two exact-head CI runs on the active branch are maintainer-supplied remote evidence of the Phase 3A4 subphases:

- commit `7612620dc252a9987a6b0e7519fbabb7501884aa` (Phase 3A4a, missing-Git prerequisite), automatic CI run `30740368544`, workflow `CI`, branch `release/v0.1.1`, head SHA `7612620dc252a9987a6b0e7519fbabb7501884aa`, conclusion `success`, job `validate` `success`;
- commit `f0ae1e1faed6c364008c7a8fccac37f631b53562` (Phase 3A4c, contract-driven groups, CLI and release gate), automatic CI run `30743100368`, workflow `CI`, branch `release/v0.1.1`, head SHA `f0ae1e1faed6c364008c7a8fccac37f631b53562`, conclusion `success`, job `validate` `success`, `validate-local` step `success`, `upload-debug-apk` step `success`.

The Phase 4 implementation/evidence commit `65a41bf59ef0b05a3ff40217a031a585e503036f` (subject `test: enforce validator repository consistency`) was pushed to `release/v0.1.1` and the following exact-head CI run is maintainer-supplied remote evidence of the Phase 4 closure:

- commit `65a41bf59ef0b05a3ff40217a031a585e503036f` (Phase 4 implementation/evidence), automatic CI run `31258760694`, workflow `CI`, branch `release/v0.1.1`, head SHA `65a41bf59ef0b05a3ff40217a031a585e503036f`, conclusion `success`, job `validate` `success`.

This document records those runs as maintainer-supplied evidence; the Build that produced this documentation did not independently query the remote and did not run GitHub Actions itself.

## Dirty-candidate iteration

An intentionally dirty cumulative Phase 4 development candidate — one that still contains uncommitted or untracked changes under maintainer review — is not expected to pass `--require-clean` and is therefore validated through a different sequence than the clean committed/CI gate. The accepted Phase 4 dirty-candidate iteration sequence is:

```bash
python3 -B -m unittest tests.test_validator_core tests.test_validator_repository
./scripts/validate-local.sh --group required
./scripts/validate-local.sh --group docs
./scripts/validate-local.sh --skip-android
```

The regression command runs first, the `required` and `docs` groups are exercised next, and the `android` group is exercised with `--skip-android` because Android is expected to be exercised separately under the maintainer's documented Android environment. The dirty-candidate iteration is a partial run: a partial run and a run that uses `--skip-android` produce `release_gate=NOT_SATISFIED` rather than `release_gate=SATISFIED`, and that outcome is correct for a still-dirty candidate. The clean committed/CI canonical gate described in the previous section, not this iteration sequence, is what establishes Phase 4 release-gate satisfaction.

## Phase 5

Phase 5 is `Complete`. The current phase is `Phase 6 — Integrated Evidence and Agent Evaluation`; Phase 6 remains `Planned`. The committed v0.1.1 Android metadata is `versionCode = 2` and `versionName = 0.1.1`. Those values are committed in the maintainer-supplied Phase 5 implementation/evidence commit `edf9da3cf5fef652c595936188e5918c2bd6e7f2`. The implementation/evidence commit and its successful push and exact-head CI are established by maintainer-supplied repository evidence; this recovery Build does not independently query the remote.

### v0.1.1 Phase 5 integration

```text
5A Gradle supply-chain integrity:
implemented and technically accepted

5B Python workspace hygiene:
implemented and technically accepted

5C Dependabot:
implemented and technically accepted

5D Android release metadata:
implemented and technically accepted

controlled Gradle bad-distribution checksum rejection:
directly proven by Phase 5I

Android/APK metadata:
directly observed by Phase 5I

Phase 5:
Complete; implementation/evidence commit and exact-head CI
established by maintainer-supplied evidence
```

#### Phase 5I direct validator evidence

```text
required:
11/0/0

docs:
11/0/0

skip-Android:
22/0/0

Android offline:
16/0/0

full offline:
38/0/0
release_gate=SATISFIED

Android source-manifest:
PASS

Android APK metadata:
PASS

Android merged-manifest:
PASS

controlled Gradle bad-distribution checksum rejection:
PASS

regression:
78 tests / OK
```

Phase 5 owns the Gradle distribution checksum, the approved wrapper-JAR checksum, the `.gitignore` bytecode rules, Dependabot, and the Android version metadata transition. The Phase 5A / 5B / 5C / 5D source implementations and the Phase 5D evidence chain are technically accepted. The controlled Gradle bad-distribution checksum rejection proof is recorded as a direct Phase 5I observation against a temporary `file://` distribution with an isolated `GRADLE_USER_HOME`, a temporary wrapper properties file, and a temporary fake distribution, leaving the repository and its wrapper files untouched. The Phase 5I Android/offline run directly observed the assembled debug APK carrying the Phase 5D contract-driven metadata (`versionCode = 2`, `versionName = 0.1.1`) through the successful `android/apk-metadata` check together with the contract and live `app/build.gradle.kts` readback. Phase 5 is `Complete`.
The retained Phase 5A/5B/5C/5D technical implementations, the retained Phase 5I technical integration, and the retained controlled Gradle bad-distribution checksum rejection proof remain accepted as direct evidence.
The implementation/evidence commit `edf9da3cf5fef652c595936188e5918c2bd6e7f2` (subject `chore: complete phase 5 implementation and evidence`) and its exact-head CI run `31334416352` remain the accepted Phase 5 technical implementation evidence.
The Phase 5 formal-closure repository action is established by commit `b7f3f5201ab9840be64c383fee33243186fd96ce` (subject `chore: close phase 5 formal closure`, parent `edf9da3cf5fef652c595936188e5918c2bd6e7f2`), its successful push to `origin/release/v0.1.1`, the matching remote release-branch SHA, and exact-head CI run `31468730138` with conclusion `success` and required `validate` job successful.
The current phase is `Phase 6 — Integrated Evidence and Agent Evaluation`; Phase 6 remains `Planned`.

## Product functionality

The suite does not introduce reminder, notification, voice, location, persistence, networking, contextual, or background functionality. It validates the technical baseline only. The release charter remains consistent with the absence of product functionality.
