# Evaluation Template — Agent-Assisted Experiment Record

**Document status:** Accepted — Phase 0 complete

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

## Tool and model

- **Tool:** OpenCode
- **Access service / provider:** <display string or `Pending maintainer input`>
- **Model (display string):** <display string>
- **Displayed model variant:** <variant or `None`>
- **Agent mode (this stage):** Plan or Build
- **OpenCode version:** <exact stdout of `opencode --version`, or `Not available` with explanation>
- **Relevant configuration:** <free text, or `Not available`>
- **Session identifier:** <identifier, or `Not available` with explanation>

## Consumption

- **Experiment-start usage snapshot:** <value, or `Not available` with explanation>
- **Pre-Build usage snapshot:** <value, or `Not available` with explanation>
- **Post-Build usage snapshot:** <value, or `Not available` with explanation>
- **Calculated Build-stage delta:** <value and unit, or `Not computable` with explanation, or `Pending maintainer input`>
- **Measurement source:** <source name>
- **Units displayed by the provider:** <unit>
- **Snapshot timestamps:** <ISO-8601 timestamp(s)>
- **Missing-data explanations:** <one bullet per missing field>

## Task

- **Objective:** <one sentence>
- **Original specification reference:** <commit, message, or document>
- **Expected files:** <list of files the task was authorized to create or modify>
- **Forbidden changes:** <list of files and actions the task was not authorized to perform>
- **Required validation:** <list of commands the task was required to run>

## Execution

- **Start timestamp:** <ISO-8601>
- **End timestamp:** <ISO-8601>
- **Agent mode (this stage):** Plan or Build
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
- **Validation results:** <one bullet per command with exit status and excerpt>
- **First-pass result:** <free text>
- **Final result:** <free text>
- **Scope compliance:** `compliant` / `deviation with approval` / `deviation without approval`
- **Review findings:** <list or `None`>
- **Defects found later:** <list or `None`>

## Assessment

- **OpenCode observations:** <free text>
- **Model observations:** <free text>
- **Task-specification observations:** <free text>
- **Environment observations:** <free text>
- **Lessons supported by this experiment:** <bulleted list>
- **Candidate rule changes:** <list or `None`>
- **Candidate validation changes:** <list or `None`>
- **Candidate reusable skills or commands:** <list or `None`>
- **Final outcome classification:** one of `Successful first pass`, `Successful with correction`, `Partially successful`, `Unsuccessful`, `Blocked by environment`, `Blocked by specification`

## Status

- **Maintainer review:** Pending maintainer input
- **Follow-up experiments required:** <list of EXP-NNNN, or `None`>
