# Release Charter — NudgeWhen v0.1.1

**Document status:** Accepted — Phases 0 through 3 complete; v0.1.1 release in progress
**Release name:** NudgeWhen v0.1.1 — Post-Release Closure and Reusable Validation Baseline
**Version:** v0.1.1
**Android artifact identity:** versionCode = 2, versionName = "0.1.1" (delivered in Phase 5)
**Active release branch:** release/v0.1.1 (created under separate authorization in Phase 0B)

## Background

The NudgeWhen project has two long-term intended outcomes:

1. A useful voice-first, local-first contextual reminder application for Android.
2. A validated agentic open-source development methodology for using OpenCode, MiniMax M3, and later Hermes to create, manage, maintain, and support open-source GitHub projects.

`v0.1.0` was the first release of the project and was merged into `main` after the full pre-release gate and the single release-bearing pull request. The remote `release/v0.1.0` branch was deleted after release completion; the state of the old local `release/v0.1.0` branch was not established by Phase 0B. The `v0.1.0` release charter, phase list, and experiment records remain in `docs/releases/v0.1.0/` for traceability and are historical evidence.

## Phase 0 status

Phase 0 is `Complete`. The observed two-commit history on `release/v0.1.1` is the initial Phase 0 content commit `c2011b10c10fbd04b9911876bcf3d71f8c317d48` (subject `v0.1.1 continuation`, parent `2a092ed013d21f49044142395a8fedd24f9432b5`), which directly modified the seven authorized Phase 0 paths (4 modifications and 3 additions), followed by the Phase 0 closure-synchronization commit `aa5fc6e42a85ecd00aaec4e86ed5d75c06bb4b1a` (subject `v0.1.1`, parent `c2011b10…`), which directly modified the four closure-overlay paths. The complete range from `2a092ed0…` through `aa5fc6e…` contains exactly seven distinct Phase 0 paths. Four paths were modified in both commits. The semantic descriptions "initial Phase 0 content commit" and "closure-synchronization commit" are strongly supported inferences based on path sets and chronology, not direct observations. The retained `Phase 0 staged-index validation` evidence records the cached name-status set, the cached whitespace-check output, the absence of an unstaged tracked diff, and seven stage-zero index records for the seven-path pre-closure candidate; numeric exit statuses were not surfaced and remain `Not available`; chronology strongly supports that this retained validation preceded `c2011b10…` and that relationship is labelled as inference. No retained direct evidence establishes a cached/index validation of the four-path closure overlay immediately before `aa5fc6e…`; the later two-commit-range `git diff --check` result is post-commit whitespace evidence and is not a substitute for the unavailable pre-commit cached validation. After `aa5fc6e…`, the seven-path post-Phase-0 recovery candidate that had been staged for evidence synchronization was committed in `8c89dc9cb6d7983d3927201bbd8ebe1acea273ec` (subject `docs: reconcile v0.1.1 phase 0 evidence`, parent `aa5fc6e…`), which directly modified the seven reconciliation paths: `AGENTS.md`, `docs/agentic-development/evaluation-template.md`, `docs/agentic-development/experiment-protocol.md`, `docs/agentic-development/experiments/EXP-0013.md`, `docs/agentic-development/opencode-governance.md`, `docs/releases/v0.1.1/phase-list.md`, and `docs/releases/v0.1.1/release-charter.md`. The former seven-path recovery candidate is no longer pending or unstaged; no active Phase 0 recovery candidate remains. No retained direct evidence establishes an immediate pre-commit cached-index validation for `8c89dc9…`; the unavailable pre-commit cached validation is preserved as unavailable and is not fabricated. Immediately before Phase 1R0 began, the repository was directly observed clean at `1d1754da86182d21820b88a819cfd6879eba9ed8` on `release/v0.1.1`. The four post-`8c89dc9…` commits — `ccc56edb1fe4084a02caf56680ca67085039a9fa` introducing the bounded OpenCode harness, `7a3e57bbd1e0f231ce8e8e6af0a3831c38d35fec` recording the permission audit, `9f2e283516db5822e63d86fbe83ac7f222283ba0` hardening `nudge-audit`, and `1d1754da86182d21820b88a819cfd6879eba9ed8` activating the bounded `nudge-build` harness — are preparatory machine-readable harness increments performed while Phase 1 is current; they are recorded in `AGENTS.md` and `EXP-0014` through `EXP-0017` and are not formally defined Phase 1 deliverables. Formal Phase 1 documentation implementation has not started. The current phase is Phase 1; Phase 1 has not started implementation work beyond becoming the current phase, and therefore remains `Planned`.

`v0.1.1` is a patch release with no new product functionality. It does not introduce reminder scheduling, notifications, voice or speech behavior, location handling, contextual triggers, persistence, networking, services, receivers, providers, background execution, or analytics. It exists only to convert the successful but release-specific `v0.1.0` repository into a durable baseline for future development.

## Phase 3 status

Phase 3 (Reusable Local-Validator Architecture) is `Complete`. The accepted implementation outcome is `Successful with correction`. The Phase 3 implementation and evidence commit is `cad89bfe241e10d6661a7746058721e22a5b9880` (subject `refactor: complete phase 3 local validator architecture`, branch `release/v0.1.1`), which directly modified the three authorized Phase 3 paths (`docs/agentic-development/experiments/EXP-0027.md` added; `docs/local-validation.md` and `scripts/validate_local.py` modified) and was successfully pushed to `origin/release/v0.1.1`. The exact-head CI run is `30949699383` (workflow `CI`, event `push`, branch `release/v0.1.1`, head SHA `cad89bfe241e10d6661a7746058721e22a5b9880`, conclusion `success`). No product functionality, Android behavior, or Android permission was added or changed by the Phase 3 implementation; the deliverable is the reusable validator architecture, its single release-contract source, and its updated documentation. Phase 4 (Validator Regression Suite and Repository-Consistency Enforcement) remains unstarted or planned. The overall `v0.1.1` release remains in progress; no pull request, merge, tag, published release, or release completion is claimed by this charter. Phase 0, Phase 1, and Phase 2 are also `Complete`.

## Release identity

- Version: `v0.1.1`
- Release title: `NudgeWhen v0.1.1 — Post-Release Closure and Reusable Validation Baseline`
- Active release branch: `release/v0.1.1`
- Active release charter: `docs/releases/v0.1.1/release-charter.md`
- Active phase list: `docs/releases/v0.1.1/phase-list.md`
- Current phase: Phase 4 — Validator Regression Suite and Repository-Consistency Enforcement

## Exact release objective

`v0.1.1` must:

- correct stale post-release documentation so that current-facing files accurately describe the released `v0.1.0` baseline and the repository's real capabilities;
- establish durable governance by generalizing `AGENTS.md` and the companion documents away from the completed `release/v0.1.0` branch and into a release-neutral structure that supports this and subsequent release trains;
- generalize CI to cover future release branches, pull requests targeting `main`, pushes to `main`, and manual dispatch, while preserving a stable `validate` job identity;
- refactor the existing `v0.1.0`-specific validator into a reusable release-aware validation architecture with one authoritative release contract;
- add a standard-library validator regression test suite and repository-consistency enforcement, so that the validator itself is tested and catches stale-state contradictions that escaped `v0.1.0` validation;
- strengthen supply-chain and workspace-hygiene controls (Gradle distribution checksum, approved wrapper-JAR checksum validation, bytecode ignore patterns, review-only Dependabot configuration for Gradle and GitHub Actions);
- update release metadata to `versionCode = 2` and `versionName = "0.1.1"` for the Android artifact (delivered in Phase 5);
- produce integrated OpenCode and MiniMax M3 evaluation evidence that distinguishes repository-enforced controls, tool-enforced controls, prose-only controls, and deferred candidates;
- prepare, but not execute, a single release-bearing pull request from `release/v0.1.1` into `main`, an annotated tag, and a GitHub release.

`v0.1.1` does not introduce any reminder capability or other product functionality.

## Agentic-development objective

The release must produce shareable evidence that the agent-assisted workflow used to build it is reproducible and reviewable. The methodology must distinguish:

- OpenCode as the agentic coding environment.
- MiniMax M3 as the implementation model, including consumption tracking.
- Hermes, deferred to a future evaluation, as a bounded orchestrator of an already validated OpenCode workflow.

The v0.1.1 work continues to use OpenCode and MiniMax M3. The exact displayed model string `MiniMax M3 (3x usage)` is recorded verbatim when directly available and is not generalized into an unsupported model-performance claim. The Phase 0 design accounts for MiniMax M3 by requiring narrowly bounded tasks, exact authorized paths, explicit ordered instructions, one phase at a time, Plan mode before ambiguous or architectural Builds, no silent scope expansion, immediate stop after an unexpected command failure or scope deviation, no replacement of a failed validation command with a different command unless separately authorized, structured final reports, and an explicit validation checklist at the end of every phase. No claim is made about MiniMax M3 capabilities or limitations beyond what the experiment protocol records.

## In-scope deliverables

1. **Generalized `AGENTS.md`.** Stable repository-wide governance separated from a small current-release context section. The complete four-category authorization matrix lives only in `AGENTS.md`. The companion document explains but does not duplicate the matrix. The mandatory phase-checklist reporting contract is in `AGENTS.md`. The companion `opencode-governance.md` is updated to match. The hard-stop behavior, the unsupported-claim prevention rules, the private-working-material handling, the metadata-only private-file verification, and the network restrictions are preserved and generalized.
2. **Updated experiment protocol and evaluation template.** The experiment protocol adds direct-evidence versus inference rules, mandatory hard-stop rules, tool-mode recording, mode-mismatch observation, command-form deviation rules, and the mandatory phase and subphase validation checklist contract. The evaluation template adds explicit fields for execution attempt or stage identifier, directly observed OpenCode mode, authorized shell-command set, authorized read path set, authorized mutation path set, commands actually executed, command-form deviations, hard-stop trigger and response, repository result, outcome classification, scope compliance, maintainer-audit corrections, direct observations, inferences, corroborating evidence, and a final `Validation checklist` section.
3. **v0.1.1 release charter and phase list.** A new `docs/releases/v0.1.1/release-charter.md` and `docs/releases/v0.1.1/phase-list.md` containing exactly Phases 0 through 7 as defined in the active phase list, each with the required subsections in the required order, each ending with an explicit `Validation checklist`, each initially `Planned`.
4. **Phase 0 experiment evidence.** A new `docs/agentic-development/experiments/EXP-0013.md` following the accepted experiment protocol, recording the Phase 0 chronology (the three Phase 0A attempts, Phase 0R, Phase 0R2, Phase 0B, Phase 0C and its corrective Builds, and the later validation and separately authorized repository-action stages).
5. **Persistent CI for future release branches.** Generalize `.github/workflows/ci.yml` so that the `validate` job runs on pushes to `release/**`, on pull requests targeting `main`, on pushes to `main`, and on manual `workflow_dispatch`. Preserve the stable `validate` job name and verify the protected-branch or ruleset configuration on `main`. This deliverable is in Phase 2 and is described here only for charter scope.
6. **Reusable local-validator architecture.** Refactor `scripts/validate_local.py` and the wrapper to a release-aware structure with one authoritative release contract. Preserve the existing `required`, `docs`, and `android` groups, the `all` alias, the candidate and clean-checkout modes, the release-gate semantics, the exit-code contract, and the existing Android manifest and artifact checks at least as strict as `v0.1.0`. This deliverable is in Phase 3.
7. **Validator regression suite and repository-consistency enforcement.** Add a standard-library test suite under an agreed `tests/` structure, with bounded fixtures, that invokes the actual validator behavior and that detects the stale-state contradictions that escaped `v0.1.0` validation. This deliverable is in Phase 4.
8. **Supply-chain, workspace hygiene, and release metadata.** Add the Gradle 9.4.1 `distributionSha256Sum`, validate the committed Gradle wrapper JAR against the approved checksum, preserve `validateDistributionUrl=true`, continue pinning GitHub Actions to full commit SHAs, add a review-only Dependabot configuration for Gradle and GitHub Actions, add the `__pycache__/` and `*.py[cod]` ignore patterns, and update the Android version metadata to `versionCode = 2` and `versionName = "0.1.1"`. This deliverable is in Phase 5.
9. **Integrated evidence and agent evaluation.** Produce an evaluation summary that classifies controls as repository-enforced, tool-enforced, prose-only, or deferred, and that records the disposition of relevant `v0.1.0` deferred candidates. This deliverable is in Phase 6.
10. **Pre-release gate and release-pull-request preparation.** Run the full clean pre-release gate and prepare, but not execute, the single release-bearing pull request, merge, annotated tag, GitHub release, and release-branch deletion. This deliverable is in Phase 7.

## Explicit non-goals

The release must not add:

- reminder functionality (scheduling, notifications, storage of reminders, or any related behavior);
- voice or speech functionality (recording, transcription, or synthesis);
- location or geofencing functionality;
- contextual triggers or device-state functionality;
- persistence beyond the existing v0.1.0 baseline;
- application networking;
- services, receivers, providers, or background execution beyond the existing AndroidX baseline;
- analytics or telemetry;
- Hermes integration or configuration;
- a production-grade Android application;
- a published application binary distributed outside the validated release artifact;
- any change to the existing `v0.1.0` historical evidence (the v0.1.0 charter, phase list, and experiment records remain unmodified);
- any new application functionality, permission, or runtime behavior.

## Single-release-branch and one-final-PR policy

- All `v0.1.1` work happens on the single branch `release/v0.1.1`. No parallel release branches.
- Exactly one pull request is opened into `main` after all release phases and the full pre-release gate are complete.
- One annotated tag and one GitHub release are created only after the release pull request is merged.
- Branch creation, switching, renaming, and deletion always require a separate explicit maintainer authorization.

## Human approval boundaries

The approved task specification itself authorizes:

- edits to its explicitly allowed files;
- creation of explicitly allowed parent directories;
- read-only repository inspection;
- the validation commands explicitly listed in the task.

Explicit maintainer approval is required before:

- changing a file outside the allowed task scope;
- adding an unrequested file;
- deleting or renaming a tracked file;
- changing dependencies, Gradle versions, toolchains, or generated project structure outside explicit scope;
- changing licenses;
- changing GitHub Actions, repository permissions, secrets, or security-sensitive configuration outside explicit scope;
- executing a destructive command;
- performing unrequested network access;
- creating, switching, renaming, or deleting branches unless explicitly authorized;
- committing;
- pushing;
- opening, modifying, or merging a pull request;
- creating a tag;
- publishing a release.

`README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/local-validation.md`, `.github/workflows/ci.yml`, `scripts/validate_local.py`, `scripts/validate-local.sh`, `.gitignore`, `app/build.gradle.kts`, and any v0.1.0 document do not have permanent special protection; later explicitly scoped phases may modify them. A `LICENSE` change always requires explicit maintainer authorization.

## Pre-release gates

The release is complete when every pre-release gate passes and every release-completion evidence step is satisfied. Phase 7 covers only the pre-release side. Merging the release pull request, the resulting `main` commit, CI on the merged `main` commit, the annotated tag, and the published GitHub release are separate post-merge release-completion actions, not Phase 7 outputs.

1. Phases 0 through 7 are marked `Complete`, with their required completion evidence committed.
2. Every change in `git diff main..release/v0.1.1` is accounted for by an approved phase deliverable or documented corrective task.
3. The complete local validation suite passes from a clean checkout on a documented supported environment, including the validator regression suite.
4. Every required GitHub status check passes on `release/v0.1.1`. The required check is the stable `validate` job.
5. Required governance, Android baseline, validation, CI, and release documents exist and are mutually consistent.
6. A sanitized experiment record exists for every agent-assisted task, not merely one record per phase.
7. An experiment may retain any valid outcome classification, including a blocked classification. However, unresolved work that prevents a phase objective or release gate from being satisfied remains release-blocking.
8. No `Pending maintainer input` remains in release-critical evidence at the pre-release gate. `Not available` and `Not applicable` are permitted final values when accompanied by an explanation.
9. Human review confirms that no secret, credential, unsupported capability claim, unexplained dependency, licensing problem, or unaccounted scope deviation remains.
10. The working tree is clean and the single release pull request is opened only after all pre-release gates pass.

## Post-merge release-completion evidence (applied after pre-release gates pass)

1. Exactly one release-bearing pull request from `release/v0.1.1` is merged into `main`.
2. Required CI passes on the resulting `main` commit.
3. Annotated tag `v0.1.1` points to the intended merged commit on `main`.
4. The GitHub release is published from that tag.
5. Release notes and any published artifacts correspond to the validated release contents.

The tag and GitHub release do not have to exist before the release pull request is merged. None of these five items are required for Phase 7 completion.

## Definition of release completion

The release is complete when, and only when:

1. All ten pre-release gates are satisfied.
2. All five release-completion evidence steps are satisfied.
3. The maintainer has signed off on the final report.

## Cross-references

- Active phase list: [phase-list.md](./phase-list.md)
- Active `AGENTS.md`: [AGENTS.md](../../../AGENTS.md)
- Experiment protocol: [../../agentic-development/experiment-protocol.md](../../agentic-development/experiment-protocol.md)
- Evaluation template: [../../agentic-development/evaluation-template.md](../../agentic-development/evaluation-template.md)
- OpenCode governance companion: [../../agentic-development/opencode-governance.md](../../agentic-development/opencode-governance.md)
- v0.1.0 release charter (historical evidence): [../v0.1.0/release-charter.md](../v0.1.0/release-charter.md)
- v0.1.0 phase list (historical evidence): [../v0.1.0/phase-list.md](../v0.1.0/phase-list.md)
