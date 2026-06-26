# OpenCode Governance — Companion Document

**Document status:** Accepted — Phase 2 complete

## Authority and link to `AGENTS.md`

This companion document explains the rules in [AGENTS.md](../../AGENTS.md). It cannot grant permissions or override `AGENTS.md`. When wording conflicts, `AGENTS.md` is authoritative. The complete four-category authorization matrix lives only in `AGENTS.md`; this document does not duplicate it.

## Rationale for the authorization model

The model is structured by category to make the safety-critical rules directly visible. The matrix is the primary command-classification reference. It must be applied together with the current explicit maintainer authorization, the remaining rules in `AGENTS.md`, the release charter and the experiment protocol. The matrix does not independently grant permission and cannot replace exact-path authorization, current-task restrictions, precedence rules or stop conditions. Storing rationale, examples, and history in a separate file keeps `AGENTS.md` short and makes the matrix harder to miss.

The model is built on three principles:

- **Documentation is the operative configuration.** No machine-readable OpenCode configuration file is included in Phase 2. The repository's OpenCode operating rules are the rules stated in `AGENTS.md`.
- **Exact-path scope.** File modifications are limited to the exact paths listed in a Build authorization. This prevents incidental changes and makes every modification traceable to a maintainer-authorized turn.
- **Separate authorizations for consequential actions.** A Build authorization does not implicitly authorize staging, commit, push, branch operations, pull requests, tags, releases, network access, configuration changes, or dependency installation. Each of those is a separate decision and a separate authorization.

## Local remote-tracking-reference semantics

`git rev-parse origin/<branch>` reads a local remote-tracking reference. It is not an independent remote query. A local remote-tracking reference is local state; it is normally updated by network-backed Git operations such as fetch, pull, or push, but it can also be altered by explicit local reference manipulation. Therefore reading it is not independent proof of current remote state.

## Why successful push output is remote-advancement evidence

Successful output from the explicitly authorized `git push` used in this workflow is evidence that the referenced remote update succeeded. It does not establish unrelated remote state, and it is not the only possible operation that can mutate a remote branch.

## Tracked-only versus untracked-file verification

`git diff`, `git diff --name-status`, `git diff --stat`, and `git diff --check` do not inspect untracked-file contents. Untracked files require `--untracked-files=all` on `git status` or a separate path enumeration.

`git status` normally reports tracked changes and may report non-ignored untracked paths depending on options and configuration. `git status --short --untracked-files=all` explicitly requests all non-ignored untracked paths. Ordinary `git status` does not prove the existence or absence of ignored files.

The three approved metadata checks for explicitly designated private working material (`git check-ignore -v`, `git ls-files --error-unmatch`, `git diff --cached --name-only`) are required to establish the ignored/untracked/unstaged condition. `git status` alone is insufficient.

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

## Hermes is not integrated

Hermes is not integrated. Any reference to Hermes in evidence is a future-boundary statement and does not authorize current action. Future integration of Hermes will require a separate plan, a separate authorization, and an update to the precedence model and the authorization matrix.

## Selected examples and edge cases

- `git rev-parse origin/release/v0.1.0` returns the local remote-tracking reference. Reading it is Category A; it is not a remote query.
- `git status --short --untracked-files=all` lists non-ignored untracked files in addition to tracked changes. Untracked content may be hidden from the default short status depending on options and configuration.
- `git diff --check` reports trailing whitespace and similar issues in tracked changes only; it does not validate untracked file content.
- A `git config --local --replace-all user.email ...` change is a configuration change and is Category C even when the value is small.
- A `git add` of a file that is in the authorized path set is still Category C; Build authorization does not include staging.
- A `git push` of a commit that was authorized by a separate commit authorization is the evidence that the referenced remote update succeeded; the push itself still requires its own separate Category C authorization.
- An agent that detects a missing or malformed `.gitignore` rule during a Build must stop and report; creating or editing `.gitignore` is outside any current Phase 2 Build scope.
- Path enumeration over repository content (for example, listing files matching a glob under the repository root) is a Category A read when it does not open private working material. Content inspection of any matching private working material file is prohibited.
- A `git fetch` of the local remote-tracking reference is a network command and is Category C; reading the local remote-tracking reference with `git rev-parse` is Category A.

## What this document does not contain

This document does not contain the complete authorization matrix. It does not contain a speculative Phase 4 implementation or validation proposal. It does not repeat historical detail already preserved in experiment records.
