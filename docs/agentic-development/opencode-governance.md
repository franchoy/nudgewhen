# OpenCode Governance — Companion Document

**Document status:** Draft — v0.1.1 release in progress

## Authority and link to `AGENTS.md`

This companion document explains the rules in [AGENTS.md](../../AGENTS.md). It cannot grant permissions or override `AGENTS.md`. When wording conflicts, `AGENTS.md` is authoritative. The complete four-category authorization matrix lives only in `AGENTS.md`; this document does not duplicate the complete matrix.

## Rationale for the authorization model

The model is structured by category to make the safety-critical rules directly visible. The matrix is the primary command-classification reference. It must be applied together with the current explicit maintainer authorization, the remaining rules in `AGENTS.md`, the active release charter and the experiment protocol. The matrix does not independently grant permission and cannot replace exact-path authorization, current-task restrictions, precedence rules or stop conditions. Storing rationale, examples, and history in a separate file keeps `AGENTS.md` short and makes the matrix harder to miss.

The model is built on three principles:

- **Documentation is the operative configuration.** No machine-readable OpenCode configuration file is included. The repository's OpenCode operating rules are the rules stated in `AGENTS.md`.
- **Exact-path scope.** File modifications are limited to the exact paths listed in a Build authorization. This prevents incidental changes and makes every modification traceable to a maintainer-authorized turn.
- **Separate authorizations for consequential actions.** A Build authorization does not implicitly authorize staging, commit, push, branch operations, pull requests, tags, releases, network access, configuration changes, or dependency installation. Each of those is a separate decision and a separate authorization.

## Stable versus current-release separation

`AGENTS.md` is organized in two clearly separated layers. The **stable repository-wide governance** layer records rules that apply across releases: precedence, the Plan/Build boundary, exact-path authorization, repository-action authorization, baseline verification, network restrictions, private-working-material handling, privacy and evidence rules, unsupported-claim prevention, scope-deviation handling, hard-stop behavior, the four-category authorization matrix, and the Hermes-not-integrated status. The **current release context** section identifies the active release, branch, charter, and phase list.

Release-specific details are kept out of the stable rules because they would become stale as new releases begin. A rule in the stable layer must be expressible in release-neutral form. A detail that depends on a particular version, branch, phase, or document is moved to the current release context section or to the active release charter.

## Phase 0 temporary bootstrap exception

`AGENTS.md` historically required a specific completed release branch in its baseline clause. When a new release begins, the tracked `AGENTS.md` therefore refers to a branch that may already be deleted. The maintainer may authorize a narrow bootstrap exception that allows Phase 0 to proceed on the released `main` baseline before the new `AGENTS.md` is written.

The exception terminates only after Phase 0D directly confirms that:

- the updated `AGENTS.md` recognizes the new release version and the new active branch;
- stable repository governance is separated from current-release context;
- no normative dependence on any completed release branch remains;
- the updated governance documents are mutually consistent.

Branch creation alone does not terminate the exception. The exception must remain active through Phase 0B (branch creation), Phase 0C (document Build), and Phase 0D (validation).

## Bootstrap exception closure

Phase 0D directly confirmed the four termination conditions. The maintainer accepted the Phase 0D evidence. The exception is terminated. Branch creation alone was not its termination event. Ordinary baseline rules now apply.

## Baseline dirty-state clarification

The working tree is clean by default. An explicitly authorized corrective task may name an exact dirty path or path/status set as its baseline; the actual state must match that set exactly, and any additional non-ignored path is itself a baseline mismatch. The agent must not clean, revert, or delete a path without separate explicit maintainer authorization. Reporting a mismatch does not authorize cleanup.

## Private-material authorization clarification

Concrete private paths must not be enumerated, listed, searched for, or otherwise discovered unless the current task explicitly authorizes metadata-only verification for that specific purpose. When metadata-only verification is explicitly authorized, the three existing checks (`git check-ignore -v`, `git ls-files --error-unmatch`, `git diff --cached --name-only`) apply, and reports record only the generic pattern, the matching-path count, and aggregate pass/fail results. The absence of private-path authorization must not be worked around with an unlisted search, enumeration, directory listing, or similar diagnostic command. If the task does not explicitly authorize private-path metadata verification, the agent must not enumerate or discover private paths at all.

## OpenCode mode as evidence

The active OpenCode mode is whatever the interface displays. Prompt wording does not change the displayed mode. A task that says "this is Plan mode" while the interface displays Build is an observable execution condition. The agent must record the displayed mode in every experiment and must not assert a mode that the interface does not display. A mode mismatch between the task authorization and the displayed mode is a recordable deviation, not a condition that prompt text can override.

## Exact-command discipline

A Build authorization names exact commands. The agent must execute each command exactly as written. Wrappers, redirections, pipelines, command substitutions, aliases, and other modifications change the command form and may hide the primary command's exit status. A successful wrapper exit does not prove the primary command succeeded. A failed wrapper exit may have failed for a reason unrelated to the primary command. Reporting the wrapper exit as the primary command's exit is an unsupported claim.

When the OpenCode bash tool result does not surface a numeric exit status, the status is reported as unavailable. The agent must not infer the status from the absence of an error message, from the expected content, or from later behavior. Inferred state is not direct observation.

## Hard-stop precedence over task completion

A hard stop is a required FAIL, BLOCKED, or unexpected command failure, a baseline mismatch, a missing required tracked file, an unavailable mandatory command exit status, or a detected scope deviation. A desired final deliverable never overrides a hard stop. The agent stops further consequential work, reports neutrally, and preserves the failure or deviation in the experiment record. A standalone Python invocation, an ad hoc shell check, or a wrapper that hides the primary command's exit status does not satisfy a hard-stop requirement.

## Direct observation, inference, and corroboration

Direct observation is a value the OpenCode tool surfaced explicitly in its result. Inference is a value derived from indirect signals such as expected content, the absence of an error message, or later behavior. Successful later behavior may corroborate an earlier fact but does not turn the earlier unavailable observation into direct evidence. A checklist item must not be marked `PASS` when its evidence is inferred, supplied only by assumption, depends on a future repository action, or was missing and filled in from a later observation.

## Mandatory checklist-reporting contract

Every phase, subphase, and Build-stage report must end with a validation checklist that uses exactly one of `[x] PASS`, `[ ] FAIL`, `[ ] BLOCKED`, or `[-] NOT APPLICABLE` per item, with concise directly observed evidence. A blanket "all checks passed" statement is insufficient. The full contract is in `AGENTS.md` §"Mandatory phase-checklist reporting" and in the experiment protocol.

## Repository result, outcome, and scope compliance as separate fields

The repository result, the outcome classification, and the scope compliance are three separate fields. The repository result records what actually happened in the repository (for example, "no tracked mutation"). The outcome classification records how the task is classified per the experiment protocol (for example, `Successful first pass`, `Partially successful`, `Successful with correction`, `Unsuccessful`, `Blocked by environment`, `Blocked by specification`). The scope compliance records whether the task stayed within its authorized path and action scope (`compliant`, `deviation with approval`, `deviation without approval`). They are not merged into a single unlabelled conclusion.

## Tracked-only versus untracked-file verification

`git diff`, `git diff --name-status`, `git diff --stat`, and `git diff --check` do not inspect untracked-file contents. Untracked files require `--untracked-files=all` on `git status` or a separate path enumeration.

`git status` normally reports tracked changes and may report non-ignored untracked paths depending on options and configuration. `git status --short --untracked-files=all` explicitly requests all non-ignored untracked paths. Ordinary `git status` does not prove the existence or absence of ignored files.

The three approved metadata checks for explicitly designated private working material (`git check-ignore -v`, `git ls-files --error-unmatch`, `git diff --cached --name-only`) are required to establish the ignored/untracked/unstaged condition. `git status` alone is insufficient.

Files added to the Git index are returned by `git ls-files` before they are committed. An untracked file is not in the index; a staged file is in the index but not yet committed; a committed file is returned by `git ls-files` and by `git ls-tree -r HEAD`. The transition from untracked to staged to committed is observable through `git status`, `git diff --cached`, `git ls-files`, and `git log`, in that order.

## Command intent versus accidental raw-output metadata exposure

A command that targets identity or configuration is an identity-query command and is Category C. A command whose raw output incidentally contains author metadata is a raw-output exposure and is not a Category C action on its own. Reports distinguish the two: raw-output exposures are recorded neutrally and the value is omitted from evidence. The intent of the command is what determines the category.

## Valid authorization wording

A valid Build authorization names the exact paths and the validation commands and explicitly excludes staging, commit, push, branch operations, pull requests, tags, releases, network access, configuration changes, and dependency installation. A request, a discussion, or an answer to a question is not an authorization. A Build authorization does not authorize Category C actions.

## Self-correction versus maintainer correction

A self-correction is an agent-detected defect that the agent fixes entirely within the authorized path and action scope. A maintainer correction is a maintainer turn that redirects or corrects the agent. Self-corrections are recorded in the experiment record as non-events for human-intervention counting; maintainer corrections are recorded as corrective-prompt events.

## Scope-deviation handling

A scope deviation is any observed action outside the authorized exact path set or outside the authorized action scope. On discovering a scope deviation, the agent stops further consequential work, reports the deviation neutrally, and preserves it in experiment evidence. Self-correction is permitted only when both the defect and the correction are wholly inside the currently authorized path and action scope. When a deviation affects an unauthorized path or action, the agent must not edit, delete, revert, move, or otherwise clean up the affected item without a separate explicit maintainer authorization. Reporting a deviation does not authorize cleanup. A later authorization may classify the resulting correction as `deviation with approval`, but it does not erase the historical deviation. The full rule is in `AGENTS.md`.

## Experiment execution versus later repository actions

Running the experiment and creating experiment files is Build work. Staging, committing, pushing, opening a pull request, creating a tag, and publishing a release are repository actions. Each repository action requires its own separate explicit maintainer authorization. The Build does not include any of them.

## Maintainer-audit corrections

A maintainer audit may reclassify an earlier attempt's outcome or scope compliance. Maintainer-audit corrections supplement history; they do not rewrite it. The earlier attempt's record is preserved and the correction is recorded as a new entry, not as a silent edit to the earlier record. A reclassification from `compliant` to `deviation without approval`, for example, must be visible in the experiment record alongside the original classification.

## Hermes is not integrated

Hermes is not integrated. Any reference to Hermes in evidence is a future-boundary statement and does not authorize current action. Future integration of Hermes will require a separate plan, a separate authorization, and an update to the precedence model and the authorization matrix.

## Selected examples and edge cases

- A read of a local remote-tracking reference (`git rev-parse origin/<branch>`) is Category A; it is not a remote query.
- `git status --short --untracked-files=all` lists non-ignored untracked files in addition to tracked changes. Untracked content may be hidden from the default short status depending on options and configuration.
- `git diff --check` reports trailing whitespace and similar issues in tracked changes only; it does not validate untracked file content.
- A `git config --local --replace-all user.email ...` change is a configuration change and is Category C even when the value is small.
- A `git add` of a file that is in the authorized path set is still Category C; Build authorization does not include staging.
- A `git push` of a commit that was authorized by a separate commit authorization is the evidence that the referenced remote update succeeded; the push itself still requires its own separate Category C authorization.
- An agent that detects a missing or malformed `.gitignore` rule during a Build must stop and report; creating or editing `.gitignore` is outside the current Build scope unless explicitly authorized.
- Path enumeration over repository content (for example, listing files matching a glob under the repository root) is Category A only when it cannot reveal explicitly private paths. Private-path discovery or enumeration requires explicit metadata-verification authorization. Not opening a file is insufficient when its private filename would still be exposed.
- A `git fetch` of the local remote-tracking reference is a network command and is Category C; reading the local remote-tracking reference with `git rev-parse` is Category A.
- A historical example: `The remote release/v0.1.0 branch was deleted after release completion; the old local branch state was not established by Phase 0B.`

## What this document does not contain

This document does not contain the complete authorization matrix. It does not contain a speculative future-phase implementation or validation proposal. It does not repeat historical detail already preserved in experiment records. It does not contain a release-specific document; release-specific governance lives in the active release charter and the active phase list.
