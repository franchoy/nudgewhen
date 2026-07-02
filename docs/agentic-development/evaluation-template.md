# Evaluation Template — Agent-Assisted Experiment Record

**Document status:** Draft — v0.1.1 release in progress

**Usage.** Copy this template, replace every field, and save as `docs/agentic-development/experiments/EXP-NNNN.md`. Every unknown value is written as `Not available`, `Not applicable`, or `Pending maintainer input` with an inline explanation. No value is guessed.

---

## Identification

- **Experiment ID:** EXP-NNNN
- **Date:** YYYY-MM-DD
- **Release:** vX.Y.Z
- **Phase:** Phase N — <name>
- **Repository:** <owner>/<name>
- **Branch:** <branch>
- **Starting commit:** <full SHA>
- **Ending commit:** <full SHA, or `Not applicable` when no commit is produced by this experiment>
- **Execution attempt or stage identifier:** <chronology label, e.g. `Phase 0A attempt 3`>

## Tool and model

- **Tool:** OpenCode
- **Access service / provider:** <display string or `Pending maintainer input`>
- **Model (display string):** <display string>
- **Displayed model variant:** <variant or `None`>
- **Directly observed OpenCode mode (this stage):** Plan or Build — as actually displayed by the interface
- **OpenCode version:** <exact stdout of `opencode --version`, or `Not available` with explanation>
- **Relevant configuration:** <free text, or `Not available`>
- **Session identifier:** <identifier, or `Not available` with explanation>
- **Mode-mismatch observation:** <None, or description of any divergence between the task authorization and the displayed mode>

## Consumption

- **Experiment-start usage snapshot:** <value, or `Not available` with explanation>
- **Pre-Build usage snapshot:** <value, or `Not available` with explanation>
- **Post-Build usage snapshot:** <value, or `Not available` with explanation>
- **Calculated Build-stage delta:** <value and unit, or `Not computable` with explanation, or `Pending maintainer input`>
- **Measurement source:** <source name>
- **Units displayed by the provider:** <unit>
- **Snapshot timestamps:** <ISO-8601 timestamp(s)>
- **Missing-data explanations:** <one bullet per missing field>

## Authorization and scope

- **Authorized shell-command set:** <list of commands explicitly authorized for this task>
- **Authorized read path set:** <list of paths the task was authorized to read>
- **Authorized mutation path set:** <list of paths the task was authorized to create or modify>
- **Commands actually executed:** <list of commands actually run, in order>
- **Command-form deviations:** <list, with original and executed forms, or `None`>
- **Hard-stop trigger and response:** <description of any hard stop that occurred, or `None`>
- **Unexpected tool behavior:** <list or `None`>
- **Unexpected questions:** <list or `None`>

## Task

- **Objective:** <one sentence>
- **Original specification reference:** <commit, message, or document>
- **Expected files:** <list of files the task was authorized to create or modify>
- **Forbidden changes:** <list of files and actions the task was not authorized to perform>
- **Required validation:** <list of commands the task was required to run>

## Execution

- **Start timestamp:** <ISO-8601>
- **End timestamp:** <ISO-8601>
- **Agent mode (this stage):** Plan or Build — as displayed by the interface
- **Agent question event count:** <integer>
- **Maintainer decision event count:** <integer>
- **Maintainer approval event count:** <integer>
- **Maintainer corrective-prompt event count:** <integer>
- **Counting method:** <free text describing how events were grouped>
- **Unexpected questions:** <list or `None`>
- **Unexpected tool behavior:** <list or `None`>

## Results

- **Files actually changed:** <list>
- **Unexpected files changed:** <list or `None`>
- **Validation requested:** <list>
- **Validation actually executed:** <list>
- **Validation results:** <one bullet per command with exit status and excerpt; mark `Not available` for any exit status the tool did not surface>
- **First-pass result:** <free text>
- **Final result:** <free text>
- **Repository result:** <free text describing what actually happened in the repository>
- **Outcome classification:** one of `Successful first pass`, `Successful with correction`, `Partially successful`, `Unsuccessful`, `Blocked by environment`, `Blocked by specification`
- **Scope compliance:** `compliant` / `deviation with approval` / `deviation without approval`
- **Self-corrections:** <list, or `None`>
- **Maintainer-audit corrections:** <list, or `None`>
- **Review findings:** <list or `None`>
- **Defects found later:** <list or `None`>

## Assessment

- **OpenCode observations:** <free text>
- **Model observations:** <free text>
- **Task-specification observations:** <free text>
- **Environment observations:** <free text>
- **Direct observations:** <bulleted list of values with direct evidence>
- **Inferences:** <bulleted list of values derived from indirect signals; each is labelled as inference>
- **Corroborating evidence:** <bulleted list of later observations that corroborate earlier unavailable observations; each is labelled as corroboration>
- **Lessons supported by this experiment:** <bulleted list>
- **Candidate rule changes:** <list or `None`>
- **Candidate validation changes:** <list or `None`>
- **Candidate reusable skills or commands:** <list or `None`>

## Status

- **Maintainer review:** Pending maintainer input
- **Follow-up experiments required:** <list of EXP-NNNN, or `None`>

## Validation checklist

Reproduce and complete every item. Use exactly one status per item:

- `[x] PASS`
- `[ ] FAIL`
- `[ ] BLOCKED`
- `[-] NOT APPLICABLE`

Add concise, directly observed evidence to every item. A blanket "all checks passed" statement is insufficient. An item must not be marked `PASS` when its evidence is pending, supplied only by assumption, depends on a future repository action, or was inferred rather than directly observed.

The checklist is the final section of the experiment record. Its content is determined by the phase or subphase that the experiment supports.
