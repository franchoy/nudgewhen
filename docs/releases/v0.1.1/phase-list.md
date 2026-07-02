# Phase List — NudgeWhen v0.1.1

**Document status:** Draft — v0.1.1 release in progress
**Active release branch:** release/v0.1.1
**Active release charter:** docs/releases/v0.1.1/release-charter.md

## Release-wide sequencing rules

- All work for this release happens on the single branch `release/v0.1.1`. No parallel release branches are created.
- All phases remain on the same branch. A later phase may refine an earlier document only through explicitly scoped work.
- Exactly one pull request is opened into `main` after all release phases and the full pre-release gate are complete.
- Each phase ends with a maintainer review. Phase status transitions to `Complete` only after the review.
- No commit, push, pull request, tag, or release may be created without explicit maintainer authorization in the current task.
- Phase 7 covers only the final pre-release gate and the preparation of release actions. The merged pull request, the resulting `main` commit, CI on the merged `main` commit, the annotated tag, and the published GitHub release are separate post-merge release-completion actions and are not Phase 7 outputs.
- Every phase, subphase, and Build-stage report must end with a `Validation checklist` section as its final subsection. Each checklist item must use exactly one of `[x] PASS`, `[ ] FAIL`, `[ ] BLOCKED`, or `[-] NOT APPLICABLE` with concise, directly observed evidence. A blanket "all checks passed" statement is insufficient.

## Phase 0 — Release Definition and Governance Bootstrap

### Objective

Define the `v0.1.1` release intent, the ordered phase list, the governance documents, and the Phase 0 evidence record. Replace the obsolete v0.1.0-specific branch coupling in `AGENTS.md` with a durable, release-neutral structure.

### Principal deliverables

- `AGENTS.md` (generalized, with stable governance separated from a small current-release context)
- `docs/agentic-development/opencode-governance.md` (companion updated to match)
- `docs/agentic-development/experiment-protocol.md` (added rules for direct evidence, hard stops, mode recording, command-form deviations, and the mandatory checklist contract)
- `docs/agentic-development/evaluation-template.md` (extended template with authorization, scope, direct-observation, inference, and final validation-checklist sections)
- `docs/releases/v0.1.1/release-charter.md` (new)
- `docs/releases/v0.1.1/phase-list.md` (this document)
- `docs/agentic-development/experiments/EXP-0013.md` (new)

### Exact or bounded path scope

Exactly the seven paths listed in Principal deliverables.

### Required behavior

- `AGENTS.md` recognizes `v0.1.1` and `release/v0.1.1` in its current release context section.
- Stable repository-wide governance is separated from current-release context in `AGENTS.md`.
- No active governance rule requires `release/v0.1.0`.
- The complete four-category authorization matrix remains only in `AGENTS.md`.
- The mandatory phase-checklist reporting contract is present in `AGENTS.md`, the experiment protocol, and the evaluation template.
- The experiment protocol and the evaluation template use the four exact checklist result forms: `[x] PASS`, `[ ] FAIL`, `[ ] BLOCKED`, `[-] NOT APPLICABLE`.
- The v0.1.1 charter identifies the correct release, objective, in-scope deliverables, non-goals, single-release-branch policy, human approval boundaries, pre-release gates, post-merge release-completion evidence, definition of completion, and cross-references.
- The phase list contains exactly Phases 0 through 7, each with the required subsections in the required order, each ending with an explicit `Validation checklist`, each initially `Planned`.
- `EXP-0013.md` follows the experiment protocol without fabricated values and preserves the audited chronology.
- Historical v0.1.0 evidence remains unmodified.

### Boundaries and exclusions

- No application functionality or Android behavior change.
- No CI, validator, dependency, workflow, or remote-setting change.
- No change to `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/local-validation.md`, `.github/workflows/ci.yml`, `scripts/validate_local.py`, `scripts/validate-local.sh`, `.gitignore`, `app/build.gradle.kts`, or any v0.1.0 document.
- No staging, commit, push, branch operation, pull request, tag, or release action.
- No network access, installation, or external lookup.
- No claim that Phase 0 is `Complete` before evidence and maintainer acceptance exist.

### Required validation

- The working tree at the end of Phase 0 contains exactly the seven authorized paths: four tracked modifications and three untracked new files.
- `git diff --name-status` enumerates only the four tracked modifications and matches the authorized path set.
- A direct file-by-file content read of each of the seven paths by the agent, each completed through an explicit end-of-file result.
- `git rev-parse HEAD` confirms HEAD is unchanged.
- Phase 0D performs the structural and documentation validation pass and confirms that the new governance documents are mutually consistent and that the bootstrap exception has terminated.

**Current-validator limitations**

- While untracked, the three new Phase 0 files are excluded from the current fixed candidate allowlist.
- After separately authorized staging, the three new Phase 0 files become visible through `git ls-files` before commit.
- Phase 3 generalizes candidate-mode inventory and v0.1.1 semantic checks.
- The existing validator was not run in Phase 0C, Phase 0C2, Phase 0C3, or Phase 0C4.

### Completion evidence

- All seven authorized files are present on `release/v0.1.1` and pass the end-of-file readback.
- `AGENTS.md` no longer treats `release/v0.1.0` as the active branch.
- Stable governance is separated from current-release context.
- The bootstrap exception was bounded through Phase 0D and was terminated by the accepted Phase 0D evidence and the maintainer acceptance; ordinary baseline rules now apply.
- `EXP-0013` preserves the accepted chronology through the Phase 0F-R1 maintainer audit and remains open until final Phase 0 closure.
- Phase 0 status transitions from `Planned` to `Complete` only after accepted Phase 0D evidence, mechanical staged-index validation, final Phase 0 closure synchronization, final index validation, and maintainer acceptance.

### Status

Planned

### Validation checklist

- [x] PASS — The v0.1.1 charter exists, identifies the correct release (`v0.1.1`) and the correct objective (post-release closure and reusable validation baseline, no new product functionality). Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — The v0.1.1 phase list exists and defines Phases 0 through 7 in the required order. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Every phase ends with an explicit `Validation checklist` subsection. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Every phase contains a `### Status` subsection whose value is `Planned`. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — `AGENTS.md` no longer treats `release/v0.1.0` as the active branch. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Stable governance is separated from current-release context in `AGENTS.md`. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Current release context identifies `v0.1.1`, `release/v0.1.1`, the charter path, and the phase-list path. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — The temporary bootstrap exception was bounded through Phase 0D and was terminated by the accepted Phase 0D evidence and the maintainer acceptance. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — The OpenCode and MiniMax M3 execution profile is recorded without unsupported model claims. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — The mandatory checklist-reporting contract is present in `AGENTS.md`, the experiment protocol, and the evaluation template. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — `EXP-0013.md` follows the experiment protocol without fabricated values and preserves the audited chronology. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Historical v0.1.0 evidence remains unmodified. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — No application, Android, CI, dependency, workflow, validator, or remote-setting change occurred in Phase 0. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Only the seven authorized Phase 0 paths were modified or created. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [ ] BLOCKED — Required structural and documentation validation passes (mechanical staged-index validation and final closure synchronization remain pending). Pending mechanical staged-index validation, final closure synchronization, final index validation, and maintainer acceptance.
- [ ] BLOCKED — Final repository state and all repository actions are accurately reported. Pending staging, final closure synchronization, final index validation, and the separately authorized Phase 0 commit.
- [ ] BLOCKED — No unresolved contradiction remains among the charter, phase list, `AGENTS.md`, experiment protocol, evaluation template, and governance companion. Pending completion of the current evidence correction's seven-file post-edit readback, maintainer acceptance, and the later staged-state and final-closure evidence.
- [x] PASS — Phase 0 is not marked `Complete` before Phase 0D evidence and maintainer acceptance exist. Phase 0 remains `Planned` after accepted Phase 0D evidence and maintainer acceptance.

## Phase 1 — Post-Release State and Documentation Closure

### Objective

Correct current-facing documentation so that the repository accurately describes the released v0.1.0 baseline and the repository's real capabilities. Remove stale claims that the repository lacks Android, Gradle, CI, an APK, a published release, application validation, or a completed v0.1.0 release train.

### Principal deliverables

- `README.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `docs/local-validation.md`
- `docs/releases/v0.1.0/phase-list.md` (status summary correction only, if needed)
- `docs/releases/v0.1.0/agent-evaluation.md` (closure note, if needed)
- Any directly affected cross-references
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Exact or bounded path scope

The current-facing documentation paths listed above. Historical v0.1.0 evidence is preserved with explicit closure annotations; raw command evidence, measurements, classifications, and historical experiment outcomes are not modified.

### Required behavior

- Current-facing documentation describes the released v0.1.0 baseline and the repository's real capabilities.
- Current-facing documentation does not direct contributors or agents to the deleted `release/v0.1.0` branch.
- Historical v0.1.0 evidence remains identifiable and unaltered except for explicit closure annotations.
- The v0.1.0 phase-list status summary agrees with the per-phase statuses.
- The v0.1.0 evaluation document carries a clearly labelled post-release closure note where its former "Phase 6 remains Planned" statement no longer represents the final release state.
- Links resolve.

### Boundaries and exclusions

- No workflow changes, remote GitHub configuration, validator refactoring, dependency changes, or Android changes.
- No product functionality.

### Required validation

- A direct read of each affected current-facing file.
- A repository-wide search confirms no current-facing false claim identified by the v0.1.0 audit.
- Historical evidence remains identifiable and unaltered except for explicit closure annotations.
- `docs/local-validation.md` is read through an explicit end-of-file result.

### Completion evidence

- The affected current-facing files are present on `release/v0.1.1` and pass the end-of-file readback.
- A repository-wide search finds no current-facing false claim identified by the v0.1.0 audit.
- Historical evidence remains identifiable and unaltered except for explicit closure annotations.
- Links resolve.
- Documentation status declarations agree with document content.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Status

Planned

### Validation checklist

- [ ] BLOCKED — `README.md` describes the released v0.1.0 baseline and the repository's real capabilities. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `CONTRIBUTING.md` does not claim that the repository lacks Android, Gradle, CI, an APK, a published release, or a completed v0.1.0 release train. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `SECURITY.md` does not claim the same absence. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `docs/local-validation.md` does not direct contributors or agents to the deleted `release/v0.1.0` branch. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The v0.1.0 phase list status summary agrees with the per-phase statuses. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The v0.1.0 evaluation document carries a closure note where the former "Phase 6 remains Planned" statement no longer represents the final release state. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — General contributor and project documentation uses branch conventions such as `release/vX.Y.Z` rather than embedding the currently active patch branch. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Links resolve. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Documentation status declarations agree with document content. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Phase experiment record; ID assigned when the task starts according to the experiment protocol. The phase has not started; direct completion evidence is not yet available.

## Phase 2 — Persistent CI and Protected-Branch Enforcement

### Objective

Replace the one-release-only CI configuration with a persistent validation policy for future release branches, pull requests targeting `main`, and merged `main` commits. Verify the protected-branch or ruleset configuration on `main` through separately authorized remote administration.

### Principal deliverables

- Updated `.github/workflows/ci.yml`
- CI-policy documentation in the v0.1.1 release directory
- Verified `main` protection or ruleset configuration
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Exact or bounded path scope

`.github/workflows/ci.yml`, the v0.1.1 CI-policy documentation, and the protected-branch or ruleset configuration on the remote `main` branch.

### Required behavior

- The stable `validate` job runs on pushes to `release/**`, on pull requests targeting `main`, on pushes to `main`, and on manual `workflow_dispatch`.
- The required job name remains `validate` so branch protection can require it without being tied to one release version.
- Read-only default permissions, full-SHA action pinning, bounded timeout, concurrency cancellation, and debug APK upload after successful validation are preserved.
- The active `main` protection or ruleset requires a pull request before merge, the stable `validate` status check, no force pushes, and no branch deletion.
- Remote settings are independently read back and recorded.

### Boundaries and exclusions

- No validator refactor, no application functionality, no dependency upgrades, no automatic merging, no release publication, no production signing.

### Required validation

- A push to `release/v0.1.1` automatically starts the workflow.
- The resulting `validate` run passes.
- The workflow file covers `release/**`, pull requests into `main`, and pushes to `main`.
- The `main` ruleset explicitly requires the stable `validate` check.
- Remote settings are independently read back and recorded.
- A direct read of `.github/workflows/ci.yml` confirms the trigger coverage and the stable job name.

### Completion evidence

- A push to `release/v0.1.1` automatically starts the workflow.
- The resulting `validate` run passes.
- The workflow file covers `release/**`, pull requests into `main`, and pushes to `main`.
- The `main` ruleset explicitly requires the stable `validate` check.
- Remote settings are independently read back and recorded.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Status

Planned

### Validation checklist

- [ ] BLOCKED — `.github/workflows/ci.yml` triggers on pushes to `release/**`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `.github/workflows/ci.yml` triggers on pull requests targeting `main`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `.github/workflows/ci.yml` triggers on pushes to `main`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `.github/workflows/ci.yml` triggers on manual `workflow_dispatch`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The required job name is stable as `validate`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Read-only default permissions, full-SHA action pinning, bounded timeout, concurrency cancellation, and debug APK upload are preserved. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — A push to `release/v0.1.1` automatically starts the workflow. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The resulting `validate` run passes. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The `main` ruleset explicitly requires the stable `validate` check. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Remote settings are independently read back and recorded. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Phase experiment record; ID assigned when the task starts according to the experiment protocol. The phase has not started; direct completion evidence is not yet available.

## Phase 3 — Reusable Local-Validator Architecture

### Objective

Refactor the v0.1.0-specific validator into a reusable, release-aware validation architecture without weakening its existing contracts.

### Principal deliverables

- Refactored `scripts/validate_local.py`
- Updated `scripts/validate-local.sh` where required
- A single documented source for release-specific validation expectations
- Updated `docs/local-validation.md`
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Exact or bounded path scope

The validator implementation, its shell entry point, its documentation, and the single release-contract source.

### Required behavior

- Stable repository checks, current-release checks, Android build and artifact checks, release-gate calculation, and user-facing command-line handling are clearly separated.
- Release-specific information is not duplicated throughout the implementation. Release version, version code, release branch, active release-document paths, and expected phase range or completion state are read from one authoritative location.
- The release-contract representation is human-reviewable, standard-library-readable, deterministic, validatable, and free of network requirements.
- Running outside a Git worktree produces a concise prerequisite failure and exit `2`, not a traceback.
- Historical release documents are not mistaken for the active release contract.
- Stable checks do not require source edits merely because a new release directory is introduced.
- Existing Android manifest and artifact checks remain at least as strict as v0.1.0.

### Boundaries and exclusions

- No broad feature expansion, no Android behavior change, no third-party Python library, no CI redesign, no remote configuration.

### Required validation

- Existing valid v0.1.0-style repository behavior remains accepted where still applicable.
- The active v0.1.1 release contract is read from one authoritative location.
- Missing-Git and invalid-invocation paths fail cleanly with exit `2`.
- No traceback appears for expected prerequisite failures.
- Candidate and clean-checkout semantics remain deterministic.
- A direct read of `scripts/validate_local.py` and `scripts/validate-local.sh` confirms the refactor.
- A direct read of `docs/local-validation.md` confirms the updated documentation.

### Completion evidence

- Existing v0.1.0-style repository behavior remains accepted where still applicable.
- The active v0.1.1 release contract is read from one authoritative location.
- Missing-Git and invalid-invocation paths fail cleanly with exit `2`.
- No traceback appears for expected prerequisite failures.
- Candidate and clean-checkout semantics remain deterministic.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Status

Planned

### Validation checklist

- [ ] BLOCKED — The validator separates stable, current-release, Android, release-gate, and command-line handling. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Release-specific information is not duplicated and is read from one authoritative location. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The release-contract representation is human-reviewable, standard-library-readable, deterministic, validatable, and free of network requirements. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The `required`, `docs`, `android`, and `all` groups are preserved. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Candidate and clean-checkout modes are preserved. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Exit codes `0`, `1`, and `2` are preserved with the same semantics. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `release_gate=SATISFIED` is emitted only on the complete all-groups run. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — No staging, repository mutation, dependency installation, or network activity is introduced. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Missing-Git and invalid-invocation paths fail cleanly with exit `2`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Historical release documents are not mistaken for the active release contract. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Existing Android manifest and artifact checks remain at least as strict as v0.1.0. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Phase experiment record; ID assigned when the task starts according to the experiment protocol. The phase has not started; direct completion evidence is not yet available.

## Phase 4 — Validator Regression Suite and Repository-Consistency Enforcement

### Objective

Add tests for the validator itself and ensure the repository gate detects the stale-state contradictions that escaped v0.1.0 validation.

### Principal deliverables

- Standard-library Python test suite under an agreed `tests/` structure
- Minimal deterministic fixtures
- Additional repository-consistency checks in the validator
- A single documented command or gate sequence that runs both the validator tests and the repository validation
- CI integration for the validator test suite
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Exact or bounded path scope

The test suite, its fixtures, the consistency check additions, the documented run command, and the CI integration for the test suite.

### Required behavior

- Tests cover argument parsing, group resolution, unknown and contradictory arguments, exit codes `0`, `1`, and `2`, release-gate calculation, missing `.git` or non-worktree execution, malformed XML, TOML, YAML, or release-contract input where applicable, broken relative Markdown links, stale active-release branch references, current documents falsely claiming that Android, CI, or releases do not exist, phase-status summary disagreement, incorrect CI trigger coverage, missing wrapper-distribution checksum, generated bytecode or prohibited output detection, clean and dirty working-tree behavior, and direct invocation of the actual repository validator code rather than a parallel reimplementation.
- The validator detects at least: active governance pointing to a completed release, current-facing documentation naming a deleted release branch, contradictions between individual phase statuses and their summary, CI restricted to one historical release branch, and application version metadata disagreeing with the active release contract.
- Tests use temporary directories, avoid network access, avoid touching the real Git index, avoid creating non-ignored output in the repository, and run with Python bytecode generation suppressed or safely isolated.

### Boundaries and exclusions

- No Android functionality, no production dependencies, no network-backed tests, no emulator tests, no attempt to test conversational agent behavior that is not repository-observable.

### Required validation

- The complete validator regression suite passes.
- At least one controlled negative fixture exists for every newly enforced contradiction class.
- Removing or corrupting each required contract causes the corresponding test to fail.
- CI executes both the tests and the real validator.
- The clean repository remains clean after the complete test run.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Completion evidence

- The complete validator regression suite passes.
- At least one controlled negative fixture exists for every newly enforced contradiction class.
- Removing or corrupting each required contract causes the corresponding test to fail.
- CI executes both the tests and the real validator.
- The clean repository remains clean after the complete test run.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Status

Planned

### Validation checklist

- [ ] BLOCKED — A standard-library test suite exists under an agreed `tests/` structure. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Tests cover argument parsing, group resolution, unknown and contradictory arguments, exit codes, release-gate calculation, missing `.git`, malformed inputs, broken Markdown links, stale active-branch references, false absence claims, phase-status summary disagreement, CI trigger coverage, missing wrapper checksum, bytecode detection, clean and dirty working-tree behavior, and direct invocation of the real validator. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The validator detects active governance pointing to a completed release, current-facing documentation naming a deleted release branch, contradictions between individual phase statuses and their summary, CI restricted to one historical release branch, and application version metadata disagreeing with the active release contract. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Tests use temporary directories, avoid network access, avoid touching the real Git index, avoid creating non-ignored output, and run with Python bytecode generation suppressed or safely isolated. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The complete validator regression suite passes. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — CI executes both the tests and the real validator. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Phase experiment record; ID assigned when the task starts according to the experiment protocol. The phase has not started; direct completion evidence is not yet available.

## Phase 5 — Supply-Chain, Workspace Hygiene, and Release Metadata

### Objective

Close the remaining deterministic supply-chain and workspace-hygiene gaps and align the Android artifact with v0.1.1.

### Principal deliverables

- Updated `gradle/wrapper/gradle-wrapper.properties`
- Updated `.gitignore`
- Wrapper-integrity validation
- `.github/dependabot.yml`
- Updated Android version metadata
- Any directly affected validation expectations and documentation
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Exact or bounded path scope

The Gradle wrapper, the `.gitignore` ignore patterns, the wrapper-integrity check, the `.github/dependabot.yml` configuration, and the Android version metadata in `app/build.gradle.kts`.

### Required behavior

- The official Gradle 9.4.1 `distributionSha256Sum` is added.
- The committed Gradle wrapper JAR is validated against the approved checksum.
- `validateDistributionUrl=true` is preserved.
- GitHub Actions continue to be pinned to full commit SHAs.
- Dependabot is configured for Gradle dependencies and GitHub Actions, creates reviewable PRs only, and does not auto-merge.
- The `__pycache__/` and `*.py[cod]` ignore patterns are added.
- Validation continues rejecting tracked bytecode and prohibited generated output.
- The Android version metadata is updated to `versionCode = 2` and `versionName = "0.1.1"`.
- The package name, namespace, minimum SDK, target SDK, compile SDK, launcher activity, and visible baseline behavior remain unchanged.

### Boundaries and exclusions

- No new application behavior, no dependency upgrade train, no production signing, no publication to an app store, no permission, service, receiver, provider, networking, or persistence changes.

### Required validation

- Gradle rejects a distribution whose checksum does not match.
- The wrapper JAR checksum matches the approved value.
- Python compilation cannot leave visible non-ignored bytecode in the repository.
- Dependabot configuration parses and covers both declared ecosystems.
- The assembled APK reports `versionCode = 2` and `versionName = 0.1.1`.
- Source and merged manifest allowlists remain satisfied.

### Completion evidence

- Gradle rejects a distribution whose checksum does not match.
- The wrapper JAR checksum matches the approved value.
- Python compilation cannot leave visible non-ignored bytecode in the repository.
- Dependabot configuration parses and covers both declared ecosystems.
- The assembled APK reports `versionCode = 2` and `versionName = 0.1.1`.
- Source and merged manifest allowlists remain satisfied.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Status

Planned

### Validation checklist

- [ ] BLOCKED — The Gradle 9.4.1 `distributionSha256Sum` is present in `gradle/wrapper/gradle-wrapper.properties`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The committed Gradle wrapper JAR matches the approved checksum. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `validateDistributionUrl=true` is preserved. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — GitHub Actions remain pinned to full commit SHAs. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `.github/dependabot.yml` covers Gradle and GitHub Actions ecosystems. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Dependabot creates reviewable PRs only and does not auto-merge. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The `__pycache__/` and `*.py[cod]` ignore patterns are present in `.gitignore`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The validator rejects tracked bytecode and prohibited generated output. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The Android artifact reports `versionCode = 2` and `versionName = 0.1.1`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Source and merged manifest allowlists remain satisfied. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Phase experiment record; ID assigned when the task starts according to the experiment protocol. The phase has not started; direct completion evidence is not yet available.

## Phase 6 — Integrated Evidence and Agent Evaluation

### Objective

Evaluate the v0.1.1 work, determine whether the v0.1.0 problems were actually prevented, and close all release documentation before the final gate.

### Principal deliverables

- `docs/releases/v0.1.1/agent-evaluation.md`
- Updated status fields in the v0.1.1 charter and phase list
- Completed experiment records for Phases 0 through 5
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.
- Explicit disposition of relevant v0.1.0 deferred candidates

### Exact or bounded path scope

The v0.1.1 agent evaluation document, the v0.1.1 charter and phase-list status fields, the experiment records for Phases 0 through 5, and the disposition of relevant v0.1.0 deferred candidates.

### Required behavior

- The evaluation determines whether generalized governance prevented stale-branch blocking, whether current-state checks caught contradictions that v0.1.0 missed, whether validator tests exercised the real validator, whether any Build continued after a normalized failure, whether any unauthorized files, bytecode, temporary files, retries, or remote mutations were created, whether final reports distinguished observed, inferred, supplied, and pending evidence, and whether the new controls are repository-enforced, tool-enforced, or prose-only.
- The evaluation explicitly records the disposition of relevant v0.1.0 deferred candidates.
- No additional helper, skill, plugin, MCP integration, shell guard, or reporting framework is introduced merely because it appeared in the v0.1.0 shortlist. Each requires independent evidence and explicit scope.

### Boundaries and exclusions

- No new app functionality, no new CI architecture, no unrelated refactor, no speculative OpenCode or Hermes integration.

### Required validation

- Every completed phase has accepted experiment evidence.
- Every deviation is classified and resolved or explicitly accepted.
- No unsupported "the validator guarantees agent behavior" claim is made.
- The evaluation clearly separates deterministic controls from conversational or transcript-only behavior.
- All Phase 0 through 5 statuses are synchronized.

### Completion evidence

- Every completed phase has accepted experiment evidence.
- Every deviation is classified and resolved or explicitly accepted.
- No unsupported "the validator guarantees agent behavior" claim is made.
- The evaluation clearly separates deterministic controls from conversational or transcript-only behavior.
- All Phase 0 through 5 statuses are synchronized.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Status

Planned

### Validation checklist

- [ ] BLOCKED — `docs/releases/v0.1.1/agent-evaluation.md` exists and classifies each repeated lesson. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Every completed phase has an accepted experiment record. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Every deviation is classified and resolved or explicitly accepted. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The evaluation distinguishes repository-enforced, tool-enforced, prose-only, and deferred controls. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — No unsupported "the validator guarantees agent behavior" claim is made. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The v0.1.0 deferred candidates are explicitly dispositioned. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — All Phase 0 through 5 statuses are synchronized. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Phase experiment record; ID assigned when the task starts according to the experiment protocol. The phase has not started; direct completion evidence is not yet available.

## Phase 7 — Full Pre-Release Gate and Release-PR Preparation

### Objective

Run the complete v0.1.1 gate from a clean release candidate and prepare the single release-bearing pull request and post-merge actions.

### Principal deliverables

- Full clean-checkout validation evidence
- Validator regression-suite evidence
- Automatic release-branch CI evidence
- Protected-branch configuration evidence
- Debug APK metadata and digest
- Final release-gate report
- Proposed pull-request title and body
- Proposed annotated-tag command and message
- Proposed GitHub release title and Markdown body
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Exact or bounded path scope

The pre-release validation and CI evidence, the protected-branch configuration evidence, the APK metadata, the final release-gate report, the proposed pull-request and release assets, and the Phase experiment record.

### Required behavior

- The complete local validation suite, including the validator regression suite, passes from a clean checkout.
- The release gate prints `release_gate=SATISFIED`.
- The push to `release/v0.1.1` automatically triggers CI; the `validate` job passes; the debug APK is produced; the APK reports `versionCode=2` and `versionName=0.1.1`; source and merged manifests satisfy the approved allowlists.
- No product functionality or permissions are introduced.
- No stale current-facing v0.1.0 branch or capability claim remains.
- `main` protection requires the stable `validate` check.
- Wrapper and distribution integrity checks pass.
- The dependency-update configuration is present and review-only.
- The branch contains no tracked build output, bytecode, screenshots, private material, or unintended files.
- The release branch is clean and ready for the one final pull request.

### Boundaries and exclusions

- Phase 7 does not open or merge the pull request, commit directly to `main`, create the tag, publish the release, or delete the release branch. These are post-merge release-completion actions.

### Required validation

- All previous phases are `Complete`.
- The validator regression suite passes.
- The complete local repository gate passes.
- The release gate prints `release_gate=SATISFIED`.
- Validation leaves the clean checkout clean.
- CI ran automatically on `release/v0.1.1`.
- The `validate` job passed.
- The debug APK was produced.
- The APK reports `versionCode=2` and `versionName=0.1.1`.
- Source and merged manifests satisfy the approved allowlists.
- No product functionality or permissions were introduced.
- No stale current-facing v0.1.0 branch or capability claim remains.
- `main` protection requires the stable `validate` check.
- Wrapper and distribution integrity checks pass.
- The dependency-update configuration is present and review-only.
- The branch contains no tracked build output, bytecode, screenshots, private material, or unintended files.
- The release branch is clean and ready for the one final pull request.

### Completion evidence

- All mandatory pre-release gates pass.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.
- The maintainer accepts the release-gate report.
- The branch is ready for the single pull request into `main`.

### Status

Planned

### Validation checklist

- [ ] BLOCKED — Every previous phase is `Complete`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The validator regression suite passes. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The complete local repository gate passes. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The release gate prints `release_gate=SATISFIED`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Validation leaves the clean checkout clean. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — CI ran automatically on `release/v0.1.1`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The `validate` job passed. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The debug APK was produced. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The APK reports `versionCode=2` and `versionName=0.1.1`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Source and merged manifests satisfy the approved allowlists. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — No product functionality or permissions were introduced. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — No stale current-facing v0.1.0 branch or capability claim remains. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `main` protection requires the stable `validate` check. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Wrapper and distribution integrity checks pass. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The dependency-update configuration is present and review-only. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The branch contains no tracked build output, bytecode, screenshots, private material, or unintended files. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The release branch is clean and ready for the one final pull request. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The pull request has not been opened; the tag has not been created; the release has not been published; the branch has not been deleted. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Phase experiment record; ID assigned when the task starts according to the experiment protocol. The phase has not started; direct completion evidence is not yet available.

## Cross-references

- [Release charter](release-charter.md)
- [Active AGENTS.md](../../../AGENTS.md)
- [Experiment protocol](../../agentic-development/experiment-protocol.md)
- [Evaluation template](../../agentic-development/evaluation-template.md)
- [OpenCode governance companion](../../agentic-development/opencode-governance.md)
- [v0.1.0 release charter (historical evidence)](../v0.1.0/release-charter.md)
- [v0.1.0 phase list (historical evidence)](../v0.1.0/phase-list.md)
