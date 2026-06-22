# Experiment Protocol — Agent-Assisted Tasks

**Document status:** Accepted — Phase 0 complete

## Purpose

This protocol defines how evidence is produced and recorded for agent-assisted tasks on NudgeWhen. It is intended to make the behavior of OpenCode, MiniMax M3, and any later agent components observable, reviewable, and comparable across tasks.

## Scope

This protocol applies to every agent-assisted task on the repository, including planning, building, reviewing, and corrective work. It covers OpenCode and MiniMax M3 from the outset and is designed to extend to Hermes without modification.

The protocol does not apply to maintainer-only actions performed entirely outside OpenCode.

## Principles

1. **Evidence over assumptions.** Findings must be supported by recorded observations, not by inference or expectation.
2. **No fabricated measurements.** Usage, version, timing, validation output, and any other quantitative value must come from a real source. Unknown values are written as `Not available`, `Not applicable`, or `Pending maintainer input` with an explanation.
3. **Distinguish tool behavior from model behavior.** Observations about OpenCode are recorded separately from observations about MiniMax M3.
4. **Distinguish implementation failures from task-specification failures.** A model that does the wrong thing is different from a model that does the right thing for the wrong specification. The protocol tracks both.
5. **Preserve human authority over consequential repository actions.** Commits, pushes, pull requests, tags, releases, branch changes, and tracked-file deletion or renaming always require explicit maintainer authorization.
6. **Record unsuccessful experiments as useful evidence.** A blocked or partial outcome is information. Such records are not downgraded, hidden, or rewritten.

## Experiment ID convention

Every experiment record uses a stable identifier of the form `EXP-NNNN`, where `NNNN` is a zero-padded four-digit sequence. IDs are assigned in chronological order of task start. IDs are never reused, even if the original record is later corrected or withdrawn.

## When an experiment record is required

An experiment record is required for every agent-assisted task, including:

- A new phase of work.
- A corrective task within a phase.
- A follow-up task driven by a review finding or a later defect.
- A scope amendment granted by the maintainer.

A phase is not a sufficient unit of evidence on its own. Multiple experiment records may exist for a single phase.

## Required pre-task snapshot

Before the Build stage of an experiment begins, the following must be captured when available:

- OpenCode version.
- Selected model display string.
- Displayed model variant.
- Agent mode (`Plan` or `Build`).
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

## Scope-compliance tracking

Each experiment record states:

- The files the task was authorized to create or modify.
- The files the task was authorized to read.
- The actions the task was authorized to perform.
- The observed actual changes and actions.
- A scope-compliance result: `compliant`, `deviation with approval`, or `deviation without approval`.

## Validation tracking

Each experiment record lists:

- Validation commands the task was required to run.
- Validation commands actually run.
- Validation results, including exit status and any captured output excerpts.
- Any requested validation that was not executed, with reason.

## Review-findings tracking

Each experiment record includes a section for findings discovered after the experiment is recorded:

- Review findings raised by the maintainer.
- Defects discovered later.
- Corrections applied in a follow-up experiment.
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

Experiment evidence informs the pre-release gates defined in the release charter. Pre-release gate 6 requires a sanitized experiment record for every agent-assisted task. Pre-release gate 7 explicitly allows blocked classifications as long as no phase objective or release gate is left unsatisfied.

## Cross-reference

- Evaluation template: [evaluation-template.md](./evaluation-template.md)
