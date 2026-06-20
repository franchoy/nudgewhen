# Release Charter — NudgeWhen v0.1.0

**Document status:** Accepted — Phase 0 complete
**Release name:** NudgeWhen v0.1.0 — Project and Agentic Workflow Baseline

## Background

The NudgeWhen project has two long-term intended outcomes:

1. A useful voice-first, local-first contextual reminder application.
2. A validated agentic open-source development methodology for using OpenCode, MiniMax M3, and later Hermes to create, manage, maintain, and support open-source GitHub projects.

`v0.1.0` is the first release of the project. It does not yet contain a useful application. It establishes only:

- a minimal static Android technical baseline that displays declared baseline content and contains no reminder behavior; and
- the first methodology baseline for evaluating the agent-assisted workflow.

Subsequent releases will work toward the first long-term outcome. The methodology baseline established here is the foundation for the second.

## Product objective

The NudgeWhen project aims to ship a voice-first, local-first contextual reminder application for Android. The application will work offline by default and is described at a high level in the repository `README.md`. Detailed product design is out of scope for this charter.

`v0.1.0` does not implement the product objective. It establishes only the static technical baseline described above. Reminder functionality, voice or speech behavior, and any user-facing product flow are explicitly out of scope for this release and are tracked in the phase list as future work.

## Agentic-development objective

The release must produce shareable evidence that the agent-assisted workflow used to build it is reproducible and reviewable. The methodology must distinguish:

- OpenCode as the agentic coding environment.
- MiniMax M3 as the implementation model, including consumption tracking.
- Hermes, deferred to a future evaluation, as a bounded orchestrator of an already validated OpenCode workflow.

`v0.1.0` is the first methodology baseline. Its experiment records describe the early behavior of OpenCode and MiniMax M3 on this repository, and they identify candidate process improvements that may be promoted into project rules, validation checks, or reusable OpenCode skills in later releases.

## Exact release objective

The release must establish:

- An open-source governance baseline.
- OpenCode operating rules.
- MiniMax M3 evaluation evidence.
- A minimal Android application that displays static baseline content and contains no reminder behavior.
- Repeatable local validation.
- Basic GitHub Actions CI.
- A complete branch-to-release rehearsal.

## In-scope deliverables

1. **Open-source governance baseline.** License, community-health documents, and contribution guidance suitable for a public project.
2. **OpenCode operating rules.** Project-local guidance for the agent, including permissions, scope discipline, and human-approval boundaries.
3. **MiniMax M3 evaluation evidence.** Sanitized experiment records for every agent-assisted task, with consumption tracking and outcome classification.
4. **Minimal Android application.** A static-baseline app that displays declared baseline content, builds successfully, and contains no reminder or voice behavior.
5. **Repeatable local validation.** A documented sequence of commands that exits successfully on a supported environment from a clean checkout.
6. **Basic GitHub Actions CI.** Required status checks that pass on the release branch.
7. **Complete branch-to-release rehearsal.** One pull request from the release branch into `main`, one annotated tag, and one published GitHub release, executed end to end.

## Explicit non-goals

The release must not add:

- Reminder functionality (scheduling, notifications, storage of reminders, or any related behavior).
- Voice or speech functionality (recording, transcription, or synthesis).
- Hermes integration or configuration.
- A production-grade Android application.
- A published application binary distributed outside the validated release artifact.

## Hard release gates

The release is complete when every pre-release gate passes and every release-completion evidence step is satisfied. Phase 7 covers only the pre-release side. Merging the release pull request, the resulting `main` commit, CI on the merged `main` commit, the annotated tag, and the published GitHub release are separate post-merge release-completion actions, not Phase 7 outputs.

### Pre-release gates

1. Phases 0 through 7 are marked `Complete`, with their required completion evidence committed.
2. Every change in `git diff main..release/v0.1.0` is accounted for by an approved phase deliverable or documented corrective task.
3. The complete local validation suite passes from a clean checkout on a documented supported environment.
4. Every required GitHub status check passes on `release/v0.1.0`.
5. Required governance, Android baseline, validation, CI, and release documents exist and are mutually consistent.
6. A sanitized experiment record exists for every agent-assisted task, not merely one record per phase.
7. An experiment may retain any valid outcome classification, including a blocked classification. However, unresolved work that prevents a phase objective or release gate from being satisfied remains release-blocking.
8. No `Pending maintainer input` remains in release-critical evidence at the pre-release gate. `Not available` and `Not applicable` are permitted final values when accompanied by an explanation.
9. Human review confirms that no secret, credential, unsupported capability claim, unexplained dependency, licensing problem, or unaccounted scope deviation remains.
10. The working tree is clean and the single release pull request is opened only after all pre-release gates pass.

### Release-completion evidence (applied after pre-release gates pass)

1. Exactly one release-bearing pull request from `release/v0.1.0` is merged into `main`.
2. Required CI passes on the resulting `main` commit.
3. Annotated tag `v0.1.0` points to the intended merged commit on `main`.
4. The GitHub release is published from that tag.
5. Release notes and any published artifacts correspond to the validated release contents.

The tag and GitHub release do not have to exist before the release pull request is merged. None of these five items are required for Phase 7 completion.

## Evaluation measurements (informative, not gating)

- **Per-phase OpenCode observations.** How the agent environment behaved, including tool call patterns, validation behavior, and adherence to scope.
- **Per-phase MiniMax M3 observations.** How the implementation model performed, including corrective prompts, plan revisions, and lesson promotion.
- **Per-experiment consumption tracking.** Usage snapshots recorded before and after each Build stage.
- **Cross-experiment lessons.** Patterns that recur across multiple experiments and may be promoted into project rules, validation checks, or OpenCode skills.
- **Review findings and later defects.** Any issues discovered after a phase is marked `Complete` that warrant a corrective experiment.

These measurements inform methodology refinement but do not by themselves block release.

## Human approval boundaries

The approved task specification itself authorizes:

- Edits to its explicitly allowed files.
- Creation of explicitly allowed parent directories.
- Read-only repository inspection.
- The validation commands explicitly listed in the task.

Explicit maintainer approval is required before:

- Changing a file outside the allowed task scope.
- Adding an unrequested file.
- Deleting or renaming a tracked file.
- Changing dependencies, Gradle versions, toolchains, or generated project structure outside explicit scope.
- Changing licenses.
- Changing GitHub Actions, repository permissions, secrets, or security-sensitive configuration outside explicit scope.
- Executing a destructive command.
- Performing unrequested network access.
- Creating, switching, renaming, or deleting branches unless explicitly authorized.
- Committing.
- Pushing.
- Opening, modifying, or merging a pull request.
- Creating a tag.
- Publishing a release.

`README.md` and `.gitignore` do not have permanent special protection; later explicitly scoped phases may modify them. A `LICENSE` change always requires explicit maintainer authorization. The OpenCode governance phase may refine these boundaries later.

## Definition of release completion

The release is complete when, and only when:

1. All ten pre-release gates are satisfied.
2. All five release-completion evidence steps are satisfied.
3. The maintainer has signed off on the final report.

## Cross-references

- Phase list: [phase-list.md](./phase-list.md)
- Experiment protocol: [../../agentic-development/experiment-protocol.md](../../agentic-development/experiment-protocol.md)
- Evaluation template: [../../agentic-development/evaluation-template.md](../../agentic-development/evaluation-template.md)
- Retrospective bootstrap record: [../../agentic-development/experiments/EXP-0001.md](../../agentic-development/experiments/EXP-0001.md)
- Current Phase 0 experiment: [../../agentic-development/experiments/EXP-0002.md](../../agentic-development/experiments/EXP-0002.md)
