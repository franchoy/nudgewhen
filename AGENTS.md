# AGENTS.md

**Document status:** Accepted — Phase 2 complete

## Purpose and scope

`AGENTS.md` is the required project-local OpenCode configuration and operational contract for Phase 2 of the v0.1.0 release. No machine-readable OpenCode configuration file (`opencode.json`, `opencode.jsonc`, `.opencode/`, or any successor) is included in Phase 2. The authoritative OpenCode operating rules for this repository are the rules stated in this document.

This file is concise. It contains the mandatory operational rules and the complete four-category authorization matrix. Rationale, examples, and historical detail are kept in the companion document.

## Related documents

- [Companion governance document](docs/agentic-development/opencode-governance.md)
- [Release charter](docs/releases/v0.1.0/release-charter.md)
- [Experiment protocol](docs/agentic-development/experiment-protocol.md)
- [Evaluation template](docs/agentic-development/evaluation-template.md)
- [Release phase list](docs/releases/v0.1.0/phase-list.md)

## Precedence model

- `docs/releases/v0.1.0/release-charter.md` is authoritative for release policy.
- `docs/agentic-development/experiment-protocol.md` is authoritative for experiment and evidence policy.
- `AGENTS.md` is authoritative for repository-local OpenCode operation where its rules are consistent with the release charter and the experiment protocol.
- `AGENTS.md` is authoritative over the companion document `docs/agentic-development/opencode-governance.md`. The companion explains; it cannot grant permissions or override this file.
- Any conflict among the release charter, the experiment protocol, and `AGENTS.md` is a baseline stop condition that requires explicit maintainer clarification. The agent must not resolve the conflict unilaterally.

## Single release-branch and one-final-PR policy

- All v0.1.0 work happens on the single branch `release/v0.1.0`. No parallel release branches.
- Exactly one pull request is opened into `main` after all release phases and the full pre-release gate are complete.
- One annotated tag and one GitHub release are created only after the release pull request is merged.
- Branch creation, switching, renaming, and deletion always require a separate explicit maintainer authorization.

## Plan, Build, post-Build administrative action, and repository-action boundaries

- **Plan mode.** Read-only local repository inspection, evidence drafting, plan authoring. No file modification. No staging, commit, push, or network access. Reading a local remote-tracking reference is a local operation and is not network access. No `git ls-remote`, `git fetch`, or `git pull` in Plan mode.
- **Build mode.** Execution of an explicitly scoped, separately authorized set of file modifications, plus the validation commands explicitly listed in the task authorization. Build authorization does not authorize staging, commit, push, branch operations, pull requests, tags, releases, dependency changes, configuration changes, or network access. Each of those is a separate category.
- **Post-Build administrative action.** Insertion of post-Build evidence, maintainer review, closure synchronization of `README.md` and `docs/releases/v0.1.0/phase-list.md`, and `EXP-0005.md` finalization. These are Build-stage actions and each requires its own separate explicit maintainer authorization.
- **Repository action.** Repository actions are consequential Git or project-state operations outside ordinary scoped Build modification, including staging, committing, pushing, branch operations, pull requests, tags, releases, dependency changes and configuration changes. Each requires its own separate explicit maintainer authorization. A Build authorization does not implicitly authorize a repository action.

## Exact-path authorization requirements

- The agent may read any relevant tracked file needed for the current task.
- A non-private untracked file may be read only when the current task explicitly authorizes or requires it.
- File modifications are limited to the exact paths listed in the Build authorization. Creating parent directories strictly required by those exact paths is permitted.
- Any modification outside the authorized exact path or action set is a scope deviation. Stop further consequential work and report it. Cleanup or reversion of the unauthorized item requires separate explicit maintainer authorization.

## Baseline and stop conditions

Before any file modification the agent verifies:

- branch is `release/v0.1.0`;
- local HEAD matches the expected Build starting commit;
- working tree is clean against tracked and non-ignored content;
- every path matching the explicitly designated private-working-material pattern is ignored, untracked, and unstaged.

On any baseline mismatch the agent stops before any modification and reports.

## Network restrictions

- Plan and ordinary Build work do not authorize network access. Local remote-tracking-reference reads are local operations and are not network access.
- Network commands (`git ls-remote`, `git fetch`, `git pull`, network-backed `gh`, and any other command whose intent is to access the network) are Category C and require separate explicit maintainer authorization.
- Network access during a Build requires a separate explicit maintainer authorization. Listing a command in a Build authorization does not by itself permit a network operation; the authorization must explicitly permit network access for that command.
- Successful output from the explicitly authorized `git push` used in this workflow is evidence that the referenced remote update succeeded. It does not establish unrelated remote state.

## Private-working-material handling

- Ignored status alone does not determine privacy.
- Only files matching an explicitly designated private-working-material rule, including raw OpenCode session exports matched by the generic `session-ses_*.md` pattern, are private working material.
- Other ignored artifacts (build output, IDE state, generated files) retain their normal classification unless another project rule explicitly classifies them as private.
- Private working material must not be opened, modified, staged, or committed.
- Concrete private paths may be used only as local command arguments for metadata-only checks. They must be omitted from committed evidence, governance examples, final reports, and reusable prompts.

## Metadata-only private-file verification

For every path matching the generic `session-ses_*.md` pattern, the agent must run, in order:

- `git check-ignore -v -- <private-path>` — must identify the active ignore rule.
- `git ls-files --error-unmatch -- <private-path>` — must return non-zero, establishing that the path is not tracked.
- `git diff --cached --name-only -- <private-path>` — must return no output, establishing that the path is not staged.

Reports record only the generic pattern, the matching-path count, and aggregate pass/fail results. The complete ignored/untracked/unstaged condition is established by these three checks, not by `git status` or by tracked-only `git diff` commands.

## Privacy and evidence rules

- The personal email value associated with the Git identity is not committed as evidence.
- Private session identifiers, machine names, and unnecessary local workspace paths are not committed as evidence.
- If a value appears in raw command output without an identity-query command intent, the report records the raw-output exposure neutrally and omits the value.
- The three sanctioned placeholders (`Not available`, `Not applicable`, `Pending maintainer input`) are the only placeholders permitted in release-critical evidence.
- Generic patterns such as `session-ses_*.md` and generic references to `ses_`-prefixed identifiers are permitted in governance documents.

## Unsupported-claim prevention

The agent must not claim that a command, check, or remote state has executed unless the claim is supported by retained evidence. Specifically:

- `git rev-parse origin/<branch>` reads a local remote-tracking reference; it is not an independent remote query.
- Successful output from the explicitly authorized `git push` is evidence that the referenced remote update succeeded; it does not establish unrelated remote state.
- Tracked-only commands (`git diff --name-status`, `git diff --stat`, `git diff --check`) cannot prove the absence or contents of untracked files.
- Pattern-based privacy scans cannot prove the absence of every unknown private-identifier format; manual review remains the qualitative backstop.
- Exact validation totals are not claimed unless mechanically and reproducibly calculated.

## Scope-deviation handling

On discovering a scope deviation the agent:

- stops further consequential work;
- reports the deviation neutrally;
- preserves the deviation in experiment evidence.

Self-correction is permitted only when both the defect and the correction are wholly inside the currently authorized path and action scope. When a deviation affects an unauthorized path or action, the agent must not edit, delete, revert, move, or otherwise clean up the affected item without a separate explicit maintainer authorization. Reporting a deviation does not authorize cleanup. A later authorization may classify the resulting correction as `deviation with approval`, but it does not erase the historical deviation.

## Self-correction versus maintainer correction

- Self-correction by the agent is recorded in the experiment record as a non-event for human-intervention counting.
- Maintainer corrections are recorded as corrective-prompt events.
- An agent that detects a defect inside its authorized scope may correct it; an agent that detects a defect outside its authorized scope must stop and report.

## Validation and final-report expectations

- Validation commands are limited to those explicitly listed in the current Build authorization.
- Validation does not install dependencies, does not execute agent-initiated repository network commands, and does not open private working material.
- Reports state only whether agent-initiated repository network commands, package installations or external lookups were executed. Reports do not make claims about model-service or platform telemetry activity.
- The final report enumerates the affected path set, the validation commands and results, any self-correction, the scope-compliance classification, the exact `git status --short --untracked-files=all` output, and explicit confirmations that HEAD is unchanged and that nothing was staged, committed, or pushed.

## Hermes not integrated

Hermes is not integrated. Any reference to Hermes in evidence is a future-boundary statement and does not authorize current action.

## Complete four-category authorization matrix

The complete matrix is recorded only in this file. The companion document must not duplicate the complete matrix.

### A. Allowed read-only by default

- `git status`, `git status --short`, `git status --short --untracked-files=all`.
- `git branch --show-current`, `git branch -vv`, `git branch -a`.
- `git rev-parse HEAD`.
- `git rev-parse origin/<branch>` — reads a local remote-tracking reference; not an independent remote query.
- `git ls-tree -r HEAD`, `git ls-tree -r HEAD --name-only`.
- `git log`, `git log --oneline`, `git log --oneline --decorate -1`.
- `git diff`, `git diff --name-status`, `git diff --stat`, `git diff --check`, `git diff -- <path>` — do not inspect untracked-file contents.
- Reading relevant tracked repository files needed for the current task.
- Reading a non-private untracked file when the current task explicitly authorizes or requires it.
- `opencode --version`.
- Bounded local validation that does not modify files, install dependencies, inspect private content, or execute network commands.

### B. Allowed only inside explicit Build scope

- Creating or modifying the exact authorized paths listed in the current Build authorization.
- Creating only the parent directories strictly required by those exact paths.
- Executing the local validation commands explicitly listed in the current Build authorization.
- Self-correcting defects only when both the defect and the correction are wholly inside the authorized path and action scope.

Build authorization does not authorize staging, committing, pushing, branch operations, pull requests, tags, releases, dependency changes, configuration changes, or network access. Each of those requires its own separate explicit authorization under Category C.

### C. Requires separate explicit maintainer authorization

- Reading Git identity or configuration values, or any command whose intent is to inspect identity.
- Modifying Git configuration, including any `git config` invocation.
- Network commands, including `git ls-remote`, `git fetch`, `git pull`, and network-backed `gh` commands.
- Staging (`git add`).
- Committing (`git commit`).
- Pushing (`git push`).
- Creating, switching, renaming, or deleting branches.
- Deleting or renaming tracked files.
- Opening, editing, or merging pull requests.
- Creating tags.
- Publishing releases.
- Installing or changing dependencies or toolchains.
- Any modification outside the already authorized exact path set.

Category C items are not "prohibited." They are deferred until a separate explicit maintainer authorization is issued. The default for an unresolved Category C item is "no action."

### D. Never allowed under normal project policy

- Opening or committing raw OpenCode session exports or other explicitly private working material.
- Reproducing private emails, private session identifiers, machine names, or unnecessary local paths in evidence.
- Fabricating command execution, measurements, validation results, or remote-state claims.
- Silently widening scope (modifying a file outside the authorized exact path set without reporting it).
- Force-pushing (`git push --force`, `git push -f`).
- Amending an accepted commit (`git commit --amend`).
- Destructive cleanup such as `git reset --hard` or `git clean -fd` unless a future exceptional maintainer authorization explicitly changes project policy.

Category D items cannot be authorized by a normal maintainer turn. A change to Category D requires an explicit policy change recorded in a project document, not a one-off authorization.
