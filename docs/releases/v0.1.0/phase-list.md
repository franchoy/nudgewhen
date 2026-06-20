# Phase List — NudgeWhen v0.1.0

**Document status:** Accepted — Phase 0 complete

## Release-wide sequencing rules

- All work for this release happens on the single branch `release/v0.1.0`. No parallel release branches are created.
- All phases remain on the same branch. A later phase may refine an earlier document only through explicitly scoped work.
- Exactly one pull request is opened into `main` after full pre-release validation.
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
- **Initial status.** `Complete`

## Phase 1 — Open-Source Community Baseline

- **Objective.** Establish the public-project profile required for a healthy open-source repository.
- **Principal deliverables.** Rich `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue templates, pull-request template, and any other community-health files required by the GitHub community profile for public repositories.
- **Boundaries / exclusions.** No application code, no CI changes, no agent governance rules.
- **Completion evidence.** All declared community-health files present on `release/v0.1.0`; documented review confirms consistency with `LICENSE` and the release charter; the corresponding experiment record is committed.
- **Initial status.** `Planned`

## Phase 2 — OpenCode Governance Baseline

- **Objective.** Establish the project-local OpenCode governance layer derived from the policy defined in Phase 0.
- **Required deliverables.** `AGENTS.md`; OpenCode configuration (for example, `opencode.json` or its successor); explicit permission boundaries; basic project procedures for routine OpenCode actions.
- **Conditional deliverables (evidence-backed).** Reusable OpenCode skills and custom commands are deliverables only when the experiment evidence available at the time of Phase 2 satisfies the promotion threshold defined in `experiment-protocol.md`. They are conditional outputs justified by the corresponding experiment records; they are not assumed to be required, and their absence is not, by itself, a Phase 2 failure.
- **Boundaries / exclusions.** No application code, no CI changes. Any included skill or command must be justified by evidence recorded in experiment records from earlier phases.
- **Completion evidence.** Required governance files present on `release/v0.1.0`; permissions align with the human-approval boundaries in the release charter; the corresponding experiment record is committed; any conditional skills or commands are referenced from that experiment record and from the Phase 6 evaluation summary.
- **Initial status.** `Planned`

## Phase 3 — Android Technical Baseline

- **Objective.** Introduce a minimal Android project that builds successfully and contains no reminder or voice behavior.
- **Principal deliverables.** Gradle project structure, manifest, a single activity or composable that displays static baseline content, and reproducible build instructions.
- **Boundaries / exclusions.** No reminder scheduling, no notification channels, no voice or speech APIs, no background services.
- **Completion evidence.** A documented clean build succeeds on the supported local environment declared by Phase 3 or Phase 4; the static-baseline app launches and displays the declared content; the corresponding experiment record is committed.
- **Initial status.** `Planned`

## Phase 4 — Local Validation Baseline

- **Objective.** Define a repeatable local validation suite that exits successfully from a clean checkout.
- **Principal deliverables.** Validation script(s) covering at minimum: documentation consistency, link integrity, required-files presence, and Android build. Phase 3 or Phase 4 must document the supported local environment on which the Android build portion of the local validation suite must pass before release. The exact supported environment is not decided in Phase 0.
- **Boundaries / exclusions.** No CI integration, no Android functionality changes.
- **Completion evidence.** Suite passes on a clean checkout on the documented supported local environment; the corresponding experiment record is committed.
- **Initial status.** `Planned`

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
