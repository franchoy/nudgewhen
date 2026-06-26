# Phase List — NudgeWhen v0.1.0

**Document status:** Accepted — Phases 0, 1, 2, 3 and 4 complete

## Release-wide sequencing rules

- All work for this release happens on the single branch `release/v0.1.0`. No parallel release branches are created.
- All phases remain on the same branch. A later phase may refine an earlier document only through explicitly scoped work.
- Exactly one pull request is opened into `main` after all release phases and the full pre-release gate are complete.
- Each phase ends with a maintainer review. Phase status transitions to `Complete` only after the review.
- No commit, push, pull request, tag, or release may be created without explicit maintainer authorization in the current task.
- Phase 7 covers only the final pre-release gate and the preparation of release actions. The merged pull request, the resulting `main` commit, CI on the merged `main` commit, the annotated tag, and the published GitHub release are separate post-merge release-completion actions and are not Phase 7 outputs.

## Phase 0 — Release Charter and Experiment Protocol

- **Objective.** Define the `v0.1.0` release intent, the ordered phase list, and the evidence protocol used to evaluate OpenCode and MiniMax M3 throughout the release.
- **Principal deliverables.**
  - `docs/releases/v0.1.0/release-charter.md`
  - `docs/releases/v0.1.0/phase-list.md`
  - `docs/agentic-development/experiment-protocol.md`
  - `docs/agentic-development/evaluation-template.md`
  - `docs/agentic-development/experiments/EXP-0001.md`
  - `docs/agentic-development/experiments/EXP-0002.md`
- **Boundaries / exclusions.** No application code, no `AGENTS.md`, no `opencode.json`, no CI files, no community-health files, no commits, no pushes, no pull requests, no tags, no releases.
- **Completion evidence.** All six files present on `release/v0.1.0`; the phase-completion checklist for Phase 0 reports `PASS` on every applicable item; `EXP-0002` records both the Plan and Build stages; the maintainer has reviewed the checklist and final report.
- **Status.** `Complete`

## Phase 1 — Open-Source Community Baseline

- **Objective.** Establish the public-project profile required for a healthy open-source repository.
- **Principal deliverables.** Rich `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue templates, pull-request template, and any other community-health files required by the GitHub community profile for public repositories.
- **Boundaries / exclusions.** No application code, no CI changes, no agent governance rules.
- **Completion evidence.** All declared community-health files present on `release/v0.1.0`; documented review confirms consistency with `LICENSE` and the release charter; the corresponding experiment record (`EXP-0003.md`) is finalized and accepted by the maintainer.
- **Status.** `Complete`

## Phase 2 — OpenCode Governance Baseline

- **Objective.** Establish the project-local OpenCode governance layer derived from the policy defined in Phase 0.
- **Selected architecture.** Repository-root `AGENTS.md` is the project-local OpenCode configuration and operational contract for this phase. `AGENTS.md` contains the complete four-category authorization matrix, the precedence model, the single release-branch and one-final-PR policy, the Plan/Build/post-Build/repository-action boundaries, the exact-path authorization requirements, the baseline and stop conditions, the network restrictions, the private-working-material handling, the metadata-only private-file verification, the privacy and evidence rules, the unsupported-claim prevention, the scope-deviation handling, the self-correction versus maintainer-correction rules, the validation and final-report expectations, and the explicit statement that Hermes is not integrated.
- **Companion governance rationale.** `docs/agentic-development/opencode-governance.md` contains the rationale, the local remote-tracking-reference semantics, the tracked-only versus untracked-file verification, the command intent versus accidental raw-output metadata exposure, the valid authorization wording, the self-correction versus maintainer-correction explanation, the experiment execution versus later repository actions distinction, and the Hermes-not-integrated status. The companion does not duplicate the complete matrix.
- **Experiment evidence.** `docs/agentic-development/experiments/EXP-0005.md` records the Phase 2 Plan and Build stages, the pre-Build and post-Build usage snapshots, the measured core-Build delta, the Stage 1 and Stage 2 event accounting, the scope-compliance assessment, the manual-review result, and the maintainer acceptance.
- **No machine-readable OpenCode configuration required.** No `opencode.json`, `opencode.jsonc`, or `.opencode/` configuration was required for the Phase 2 baseline. The project-local OpenCode configuration role is fulfilled by `AGENTS.md`; the release charter, the experiment protocol, and the precedence model in `AGENTS.md` together govern the agent. No application code or CI work was included in Phase 2.
- **Deferred deliverables.** Reusable OpenCode skills, custom commands, agents, plugins, MCP configuration, and Hermes integration remain deferred. They are conditional outputs justified by the corresponding experiment records; their absence is not, by itself, a Phase 2 failure.
- **Boundaries / exclusions.** No application code, no CI changes. Any included skill or command must be justified by evidence recorded in experiment records from earlier phases.
- **Completion evidence.** Required governance files present on `release/v0.1.0`; permissions align with the human-approval boundaries in the release charter; the corresponding experiment record (`EXP-0005.md`) is finalized; the Stage 1 and Stage 2 event accounting is preserved; the measured core-Build delta is arithmetically verified; the maintainer has accepted `EXP-0005`.
- **Status.** `Complete`

## Phase 3 — Android Technical Baseline

- **Objective.** Introduce a minimal Android project that builds successfully and contains no reminder or voice behavior.
- **Selected architecture.** Kotlin and Jetpack Compose in a single `:app` module; one launcher activity; one static screen displaying the string `NudgeWhen — Android technical baseline`; Gradle wrapper `9.4.1`; Android Gradle Plugin `9.2.1`; compile and target SDK `36`; minimum SDK `26`; Java source and target `17`; namespace and application ID `io.github.franchoy.nudgewhen`; AndroidX-generated merged-manifest entries limited to the exact maintainer-approved allowlist (one signature permission, one AndroidX provider with three initializer metadata entries, one AndroidX receiver, two optional libraries with `required="false"`).
- **Boundaries / exclusions.** No reminder scheduling, no notification channels, no voice or speech APIs, no background services, no analytics, no telemetry, no application networking, no persistence, no contextual triggers.
- **Completion evidence.** The minimal Android project exists; Gradle project discovery succeeded; debug APK assembly succeeded; Android lint succeeded; APK metadata was verified through `aapt2 dump badging`; the source and merged manifests were reviewed; physical-device installation and launch succeeded on the maintainer-provided UMIDIGI A15T running Android 13; the exact static text was visibly confirmed; `EXP-0006` is finalized and accepted.
- **Status.** `Complete`

## Phase 4 — Local Validation Baseline

- **Objective.** Define a repeatable local validation suite that exits successfully from a clean checkout.
- **Selected implementation.** A thin shell entry point at `scripts/validate-local.sh` invokes a Python standard-library validator at `scripts/validate_local.py` that exposes three groups — `required`, `docs`, and `android` — plus an `all` alias. The validator uses only the Python standard library and never performs network access, repository cloning, or staging. The full local validation contract is documented in `docs/local-validation.md`. The Phase 4 experiment record is `docs/agentic-development/experiments/EXP-0007.md`.
- **Principal deliverables.**
  - `.gitattributes` declaring the exact text- and binary-attribute contract.
  - The shell and Python local validators.
  - Local-validation documentation (`docs/local-validation.md`).
  - Phase 4 experiment evidence (`docs/agentic-development/experiments/EXP-0007.md`).
  - Governance-status synchronization across `AGENTS.md` and `docs/agentic-development/opencode-governance.md`.
  - Repeatable `required`, `docs`, and `android` validation groups.
  - Candidate-mode and clean-checkout modes with deterministic release-gate semantics.
  - Exact `.gitattributes`, source-manifest, merged-manifest, and APK-metadata contracts.
  - Tracked build-output, screenshot, bytecode, and `__pycache__` rejection.
  - Python bytecode suppression at the shell entry point and at every Python invocation.
  - Prerequisite exit code `2`, separated from content exit code `1`.
  - Dynamic private-working-material invariant: every matching private session export is ignored, untracked, unstaged, and unnamed in publishable evidence.
- **Boundaries / exclusions.** No CI integration, no Android functionality changes, no production code changes, no merging of pull requests, no commit on `main`, no tag, no release.
- **Completion evidence.** The Phase 4 implementation scope is complete in the current release-train candidate; the local validation suite runs successfully end to end in the documented candidate environment and prints the literal `release_gate=SATISFIED` only on the complete all-groups run. The corresponding experiment record is recorded on the working tree of `release/v0.1.0`; staging, committing, the release pull request, the annotated tag, and the GitHub release are separate post-Build administrative and repository actions and are not part of the Phase 4 implementation scope. The clean-checkout proof execution and the repository commit are still pending and remain separately gated.
- **Status.** `Complete`

## Phase 5 — GitHub Actions CI Baseline

- **Objective.** Establish the required status checks on `release/v0.1.0`.
- **Principal deliverables.** Workflow file(s) under `.github/workflows/`, declared as required checks for the release branch, and any necessary permissions or secrets documentation. A debug APK may be uploaded as a workflow artifact for validation purposes.
- **Boundaries / exclusions.** No additional release automation beyond the required checks. Phase 5 must not include publishing a public GitHub release, production signing, app-store publication, or deployment.
- **Completion evidence.** Required checks pass on the release branch; any debug APK artifact is retained for review; the corresponding experiment record is committed.
- **Initial status.** `Planned`

## Phase 6 — Agent Evaluation Evidence

- **Objective.** Aggregate and review the experiment records produced across Phases 0 through 5 and promote repeated lessons into project rules, validation checks, or reusable OpenCode skills.
- **Principal deliverables.** An evaluation summary document; any promoted project rules, validation checks, or skills; and a list of candidate follow-up experiments deferred to a future release.
- **Boundaries / exclusions.** No new application code, no new CI changes. All changes must be justified by evidence from earlier experiment records.
- **Completion evidence.** Evaluation summary committed on `release/v0.1.0`; every promoted artifact is referenced from the evaluation summary; the corresponding experiment record is committed.
- **Initial status.** `Planned`

## Phase 7 — Pre-Release Gate and Release-Pull-Request Preparation

- **Objective.** Run the final pre-release gate end to end and prepare, but not execute, the release actions.
- **Principal deliverables.**
  - Final pre-release validation evidence.
  - A release-gate report.
  - A proposed pull-request title and body.
  - A proposed release title and release notes.
  - A documented intended tag (name and target commit).
  - A closing pre-release experiment record.
  - Confirmation that the branch is ready for the single release pull request.
- **Boundaries / exclusions.** No merging of pull requests, no commit on `main`, no CI invocation on the merged `main` commit, no creation of the annotated tag, and no publishing of a GitHub release. Those are post-merge release-completion actions, not Phase 7 outputs.
- **Completion evidence.**
  - All pre-release gates pass.
  - The release branch is clean.
  - The maintainer has accepted the pre-release report.
  - The branch is ready for the one release-bearing pull request.
- **Initial status.** `Planned`

## Cross-references

- Release charter: [release-charter.md](./release-charter.md)
- Experiment protocol: [../../agentic-development/experiment-protocol.md](../../agentic-development/experiment-protocol.md)
