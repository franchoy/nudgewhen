# Experiment Protocol — Agent-Assisted Tasks

**Document status:** Draft — v0.1.1 release in progress

## Purpose

This protocol defines how evidence is produced and recorded for agent-assisted tasks on NudgeWhen. It is intended to make the behavior of OpenCode, MiniMax M3, and any later agent components observable, reviewable, and comparable across tasks.

## Scope

This protocol applies to every agent-assisted planning, Build, corrective, and repository-action task on the repository. It covers OpenCode and MiniMax M3 from the outset and is designed to extend to Hermes without modification.

The protocol does not apply to maintainer-only actions performed entirely outside OpenCode.

## Principles

1. **Evidence over assumptions.** Findings must be supported by recorded observations, not by inference or expectation.
2. **No fabricated measurements.** Usage, version, timing, validation output, and any other quantitative value must come from a real source. Unknown values are written as `Not available`, `Not applicable`, or `Pending maintainer input` with an explanation.
3. **Distinguish tool behavior from model behavior.** Observations about OpenCode are recorded separately from observations about MiniMax M3.
4. **Distinguish implementation failures from task-specification failures.** A model that does the wrong thing is different from a model that does the right thing for the wrong specification. The protocol tracks both.
5. **Preserve human authority over consequential repository actions.** Commits, pushes, pull requests, tags, releases, branch changes, and tracked-file deletion or renaming always require explicit maintainer authorization.
6. **Record unsuccessful experiments as useful evidence.** A blocked or partial outcome is information. Such records are not downgraded, hidden, or rewritten.
7. **Preserve failed and corrected attempts.** An attempt that ends in a hard stop, a deviation, or a maintainer correction is preserved in the experiment record. A later success does not erase the earlier deviation. Maintainer-audit corrections supplement history; they do not rewrite it.
8. **Distinguish repository result, outcome classification, and scope compliance.** These three fields are recorded separately and are not merged into a single unlabelled conclusion.

## Experiment ID convention

Every experiment record uses a stable identifier of the form `EXP-NNNN`, where `NNNN` is a zero-padded four-digit sequence. IDs are assigned in chronological order of task start. IDs are never reused, even if the original record is later corrected or withdrawn.

## When an experiment record is required

An experiment record is required for every agent-assisted task, including:

- A new phase of work.
- A corrective task within a phase.
- A follow-up task driven by a review finding or a later defect.
- A scope amendment granted by the maintainer.
- A planning stage, a Build stage, or a corrective attempt within a single phase.

A phase is not a sufficient unit of evidence on its own. Multiple experiment records may exist for a single phase. Multiple attempts may belong to one experiment record when their chronology remains explicit and each attempt's outcome, scope compliance, and deviations are recorded separately.

## Required pre-task snapshot

Before the Build stage of an experiment begins, the following must be captured when available:

- OpenCode version.
- Selected model display string.
- Displayed model variant.
- Agent mode (`Plan` or `Build`) as actually displayed by the interface.
- Access service or provider.
- Usage snapshot, with units, timestamp, and measurement source.
- Session identifier, only if it can be safely and reliably obtained.

If a value is not directly and reliably available, the corresponding field is `Not available` or `Pending maintainer input`. Values are never inferred from request counts, elapsed time, or any other indirect signal.

## Required post-task snapshot

After the Build stage of an experiment ends, the same set of values is captured again. The delta between the pre-task and post-task snapshots is recorded and reported, but only when the two values use directly comparable units.

## Consumption-recording rules

- The exact displayed value is recorded verbatim, including any unit suffix shown by the provider.
- The measurement source is named (for example, "OpenCode Go usage console").
- The snapshot timestamp is recorded.
- If a snapshot contains multiple displayed values (for example, hourly, weekly, and monthly allowances), each value is recorded on its own line.
- A delta is computed and reported only when the two snapshots being compared use the same unit and the same measurement basis.
- When the experiment-start snapshot is missing, the recorded delta measures only the Build stage. This distinction is made explicit in the record and in any report derived from it.

## Rules for missing or inaccessible measurements

Unknown values use one of three explicit tokens, each with an inline explanation:

- **`Not available`** — the value exists but could not be obtained for this record.
- **`Not applicable`** — the value does not apply to this experiment (for example, there is no Build stage for a purely retrospective record).
- **`Pending maintainer input`** — the value must be supplied by the maintainer; the record will be updated when the value is available.

These three tokens are the only sanctioned placeholders. No other placeholder text is permitted in release-critical evidence.

## Human-intervention tracking

Each experiment record maintains a concise event list of human interventions during the experiment. The list distinguishes four event types and tracks each as an event count:

- **Agent question event count** — the number of distinct agent-to-maintainer question turns that blocked or shaped the task.
- **Maintainer decision event count** — the number of distinct maintainer turns that selected between presented options or otherwise directed the task.
- **Maintainer approval event count** — the number of distinct maintainer turns that explicitly authorized a consequential action.
- **Maintainer corrective-prompt event count** — the number of distinct maintainer turns that redirected or corrected the agent.

**Event definition.** An event is one conversational turn serving that function. A single message containing several related bullets counts as one event, unless it contains clearly independent decisions that must be tracked separately. Counts are not inflated by paragraph count, sentence count, or option count within a single turn. A single turn may count under more than one event type when it contains clearly distinct kinds of content (for example, both a decision and a corrective prompt).

The counting method is described in the record alongside the event list.

## Tool-mode recording

Every experiment record states the OpenCode mode actually displayed by the interface for the relevant stages of the experiment. A mode mismatch between the task authorization and the displayed mode is recorded as an observable execution condition, not as a condition that prompt text can override.

## Direct evidence versus inference

A value is direct evidence when the OpenCode tool surfaced it explicitly in its result text. A value is inference when it is derived from indirect signals such as expected content, the absence of an error message, or later behavior. The experiment record distinguishes the two and labels each value with its source.

Successful later behavior may corroborate an earlier fact but does not turn the earlier unavailable observation into direct evidence. A checklist item is not marked `PASS` when its evidence is pending, supplied only by assumption, depends on a future repository action, or was inferred rather than directly observed.

## Unavailable command exit status

A numeric command exit status may be recorded only when the OpenCode tool result surfaced that exit status directly. If the tool did not surface a numeric exit status, the status is recorded as `Not available` with an explanation, and the experiment does not infer the status from the absence of an error message, the expected content of the result, or the success of a later command.

## Command-form deviations

A command-form deviation is any change to the form of an authorized command: a wrapper, a redirection, a pipeline, a command substitution, a shell loop, a shell function, an alias, a diagnostic supplement, or any other modification. Command-form deviations are recorded with the original authorized form, the executed form, and the reason for the deviation. A successful wrapper exit does not prove the primary command succeeded; a failed wrapper exit may have failed for an unrelated reason.

## Mandatory hard stops

A required FAIL, BLOCKED, or unexpected command failure, a baseline mismatch, a missing required tracked file, an unavailable mandatory command exit status, or a detected scope deviation is a hard stop. The agent stops further consequential work, reports the failure neutrally, and preserves it in the experiment record. A desired final deliverable never overrides a hard stop. A standalone Python invocation, an ad hoc shell check, or a wrapper that hides the primary command's exit status does not satisfy a hard-stop requirement.

## Correction preservation

A self-correction is an agent-detected defect that the agent fixes entirely within the authorized path and action scope. It is recorded in the experiment record as a non-event for human-intervention counting. A maintainer correction is a maintainer turn that redirects or corrects the agent. It is recorded as a corrective-prompt event. An agent that detects a defect inside its authorized scope may correct it; an agent that detects a defect outside its authorized scope must stop and report.

Maintainer-audit corrections supplement history. They do not rewrite the original record. A reclassification from `compliant` to `deviation without approval`, for example, is recorded as a new entry, not as a silent edit to the earlier record.

## Final-report overstatement as a review finding

A final report that marks a checklist item `PASS` based on pending, assumed, inferred, or future evidence is a review finding. The finding is recorded with the original claim, the basis on which it was unsupported, and the maintainer's later classification.

## Scope-compliance tracking

Each experiment record states:

- The files the task was authorized to create or modify.
- The files the task was authorized to read.
- The actions the task was authorized to perform.
- The observed actual changes and actions.
- A scope-compliance result: `compliant`, `deviation with approval`, or `deviation without approval`.

The scope-compliance field is separate from the outcome classification and from the repository result. A task can be `Partially successful` and `deviation without approval`. A task can be `Successful with correction` and `compliant`. The three fields are not merged.

## Validation tracking

Each experiment record lists:

- Validation commands the task was required to run.
- Validation commands actually run.
- Validation results, including exit status (when directly surfaced) and any captured output excerpts.
- Any requested validation that was not executed, with reason.
- A clear separation between direct evidence and inferred or corroborated state.

## Review-findings tracking

Each experiment record includes a section for findings discovered after the experiment is recorded:

- Review findings raised by the maintainer.
- Defects discovered later.
- Corrections applied in a follow-up experiment.
- Maintainer-audit reclassifications.
- Status (open, corrected, accepted, deferred).

## Classification of outcomes

Every experiment record is classified with one of the following:

- **`Successful first pass`** — the task completed without human correction during the Build stage.
- **`Successful with correction`** — the task completed, but human intervention was required to redirect, correct, or approve during the Build stage.
- **`Partially successful`** — the task completed some but not all of its objectives, and the missing parts are tracked.
- **`Unsuccessful`** — the task did not achieve its stated objective.
- **`Blocked by environment`** — the task could not proceed because of an environment limitation (network, tool, or platform).
- **`Blocked by specification`** — the task could not proceed because the specification was incomplete, contradictory, or required a maintainer decision that was not made.

A blocked classification does not, by itself, make a phase release-blocking. An experiment that classifies as `Blocked` only blocks release if the unresolved work it represents prevents a phase objective or release gate from being satisfied.

## Promotion of repeated lessons

A lesson observed in a single experiment is recorded but does not change project rules. A lesson observed in two or more independent experiments, with the same or equivalent context, becomes a candidate for promotion.

Promoted lessons may become:

- A project rule, recorded in the relevant governance document.
- A validation check, added to the local validation suite.
- An OpenCode skill or command, added to the repository's OpenCode governance layer.
- A future Hermes procedure, recorded for use after Hermes is integrated.

Every promotion is recorded as a follow-up experiment or as an explicit entry in the relevant document.

## Transcript policy

- Raw agent sessions are not committed to the repository by default.
- Only reviewed and sanitized evidence may be committed.
- Secrets, credentials, personal paths, machine names, and unnecessary personal data must not be published.
- Personal email addresses, even when used as a Git identity, are not committed as evidence. The detection and correction of identity issues is described in neutral terms.

## Relationship to release gates

Experiment evidence informs the pre-release gates defined in the release charter. A pre-release gate may require a sanitized experiment record for every agent-assisted task. A pre-release gate may allow blocked classifications as long as no phase objective or release gate is left unsatisfied.

## Mandatory phase and subphase validation checklists

Every phase, subphase, and Build-stage report must end with a `Validation checklist` section as the final subsection. Each checklist item must use exactly one of:

- `[x] PASS`
- `[ ] FAIL`
- `[ ] BLOCKED`
- `[-] NOT APPLICABLE`

Each item must contain concise, directly observed evidence. A blanket statement such as "all checks passed" is insufficient. An item must not be marked `PASS` when its evidence is pending, supplied only by assumption, depends on a future repository action, or was inferred rather than directly observed.

## Cross-reference

- Evaluation template: [evaluation-template.md](./evaluation-template.md)
- OpenCode governance companion: [opencode-governance.md](./opencode-governance.md)
- `AGENTS.md`: [../../AGENTS.md](../../AGENTS.md)
