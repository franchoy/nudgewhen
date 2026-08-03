# AGENTS.md

**Document status:** Accepted — Phase 0 governance baseline; v0.1.1 release in progress

## Purpose and scope

`AGENTS.md` is the required project-local OpenCode configuration and operational contract for the NudgeWhen repository. Increment A introduces bounded machine-readable OpenCode configuration through `opencode.jsonc` and `.opencode/agents/`. `AGENTS.md` remains the authoritative repository-local operational contract. Machine-readable permissions are capability ceilings, not task authorization. Every consequential action still requires the exact current maintainer authorization. The authoritative OpenCode operating rules for this repository are the rules stated in this document.

This file is concise. It contains the mandatory operational rules and the complete four-category authorization matrix. Rationale, examples, and historical detail are kept in the companion document.

`AGENTS.md` is organized in two clearly separated layers:

1. **Stable repository-wide governance** (rules that apply across releases).
2. **Current release context** (rules and pointers that apply to the active release only).

The current release context is the final section. It does not duplicate the full phase list.

## Related documents

Stable cross-references:

- [Companion governance document](docs/agentic-development/opencode-governance.md)
- [Experiment protocol](docs/agentic-development/experiment-protocol.md)
- [Evaluation template](docs/agentic-development/evaluation-template.md)

Current release context cross-references:

- [Active release charter](docs/releases/v0.1.1/release-charter.md)
- [Active phase list](docs/releases/v0.1.1/phase-list.md)

Historical v0.1.0 documents remain in `docs/releases/v0.1.0/` for traceability and are not normative for future work.

## Precedence model

- The active release charter is authoritative for release policy.
- The experiment protocol is authoritative for experiment and evidence policy.
- `AGENTS.md` is authoritative for repository-local OpenCode operation where its rules are consistent with the active release charter and the experiment protocol.
- `AGENTS.md` is authoritative over the companion document `docs/agentic-development/opencode-governance.md`. The companion explains; it cannot grant permissions or override this file.
- Completed release charters (including the v0.1.0 charter) are historical evidence and are not normative for future work.
- Any conflict among the active release charter, the experiment protocol, and `AGENTS.md` is a baseline stop condition that requires explicit maintainer clarification. The agent must not resolve the conflict unilaterally.

## Single release-branch and one-final-PR policy

- All work for a given release happens on the single branch named in the current release context section. No parallel release branches.
- Exactly one pull request is opened into `main` after all release phases and the full pre-release gate are complete.
- One annotated tag and one GitHub release are created only after the release pull request is merged.
- Branch creation, switching, renaming, and deletion always require a separate explicit maintainer authorization.

## Plan, Build, post-Build administrative action, and repository-action boundaries

- **Plan mode.** Read-only local repository inspection, evidence drafting, plan authoring. No file modification. No staging, commit, push, or network access. Reading a local remote-tracking reference is a local operation and is not network access. No `git ls-remote`, `git fetch`, or `git pull` in Plan mode.
- **Build mode.** Execution of an explicitly scoped, separately authorized set of file modifications, plus the validation commands explicitly listed in the task authorization. Build authorization does not authorize staging, commit, push, branch operations, pull requests, tags, releases, dependency changes, configuration changes, or network access. Each of those is a separate category.
- **Post-Build administrative action.** Insertion of post-Build evidence, maintainer review, and closure synchronization. These are Build-stage actions and each requires its own separate explicit maintainer authorization.
- **Repository action.** Repository actions are consequential Git or project-state operations outside ordinary scoped Build modification, including staging, committing, pushing, branch operations, pull requests, tags, releases, dependency changes and configuration changes. Each requires its own separate explicit maintainer authorization. A Build authorization does not implicitly authorize a repository action.

## Exact-path authorization requirements

- The agent may read any relevant tracked file needed for the current task.
- A non-private untracked file may be read only when the current task explicitly authorizes or requires it.
- File modifications are limited to the exact paths listed in the Build authorization. Creating parent directories strictly required by those exact paths is permitted.
- Any modification outside the authorized exact path or action set is a scope deviation. Stop further consequential work and report it. Cleanup or reversion of the unauthorized item requires separate explicit maintainer authorization.

## Baseline and stop conditions

Before any file modification the agent verifies:

- the current branch matches the branch named in the current release context section;
- local HEAD matches the expected Build starting commit;
- the working-tree state matches the task-authorized baseline exactly. A clean working tree is the default. An explicitly authorized corrective task may name an exact dirty path or path/status set as its baseline; the actual state must match that set exactly, and any additional non-ignored path is itself a baseline mismatch.

Private-path metadata verification is not part of the default baseline. Private-path metadata verification occurs only when the current task explicitly authorizes metadata-only verification for that specific purpose. When such authorization is absent, the agent does not perform any private-path search, enumeration, or metadata check as part of the baseline.

On any baseline mismatch the agent stops before any modification and reports. The agent must not clean, revert, or delete a path without separate explicit maintainer authorization. Reporting a mismatch does not authorize cleanup.

## Network restrictions

- Plan and ordinary Build work do not authorize network access. Local remote-tracking-reference reads are local operations and are not network access.
- Network commands (`git ls-remote`, `git fetch`, `git pull`, network-backed `gh`, and any other command whose intent is to access the network) are Category C and require separate explicit maintainer authorization.
- Network access during a Build requires a separate explicit maintainer authorization. Listing a command in a Build authorization does not by itself permit a network operation; the authorization must explicitly permit network access for that command.
- Successful output from the explicitly authorized `git push` used in this workflow is evidence that the referenced remote update succeeded. It does not establish unrelated remote state.

## Private-working-material handling

- Ignored status alone does not determine privacy.
- Only files matching an explicitly designated private-working-material rule, including raw OpenCode session exports matched by the generic `session-ses_*.md` pattern, are private working material.
- Other ignored artifacts (build output, IDE state, generated files) retain their normal classification unless another project rule explicitly classifies them as private.
- Private working material must not be opened, modified, staged, or committed. The agent must never open, read, or inspect the content of a private working-material file.
- Concrete private paths must not be enumerated, listed, searched for, or otherwise discovered unless the current task explicitly authorizes metadata-only verification for that specific purpose.
- When metadata-only verification is explicitly authorized, the three existing checks (`git check-ignore -v`, `git ls-files --error-unmatch`, `git diff --cached --name-only`) apply, and reports record only the generic pattern, the matching-path count, and aggregate pass/fail results.
- The absence of private-path authorization must not be worked around with an unlisted search, enumeration, directory listing, or similar diagnostic command. If the task does not explicitly authorize private-path metadata verification, the agent must not enumerate or discover private paths at all.
- Concrete private paths must be omitted from committed evidence, governance examples, final reports, and reusable prompts.

## Metadata-only private-file verification

When the current task explicitly authorizes metadata-only verification for a specific private-working-material purpose, the agent runs the following three checks for every path matching the generic `session-ses_*.md` pattern, in order:

- `git check-ignore -v -- <private-path>` — must identify the active ignore rule.
- `git ls-files --error-unmatch -- <private-path>` — must return non-zero, establishing that the path is not tracked.
- `git diff --cached --name-only -- <private-path>` — must return no output, establishing that the path is not staged.

When the current task does not explicitly authorize metadata-only verification, the agent does not run any of the three checks. The check order and the aggregate-reporting rule are preserved for the case when verification is explicitly authorized. Reports record only the generic pattern, the matching-path count, and aggregate pass/fail results.

Files added to the Git index are returned by `git ls-files` before they are committed. An untracked file is not in the index; a staged file is in the index but not yet committed; a committed file is returned by `git ls-files` and by `git ls-tree -r HEAD`.

## Privacy and evidence rules

- The personal email value associated with the Git identity is not committed as evidence.
- Private session identifiers, machine names, and unnecessary local workspace paths are not committed as evidence.
- If a value appears in raw command output without an identity-query command intent, the report records the raw-output exposure neutrally and omits the value.
- The three sanctioned placeholders (`Not available`, `Not applicable`, `Pending maintainer input`) are the only placeholders permitted in release-critical evidence.
- Generic patterns such as `session-ses_*.md` and generic references to `ses_`-prefixed identifiers are permitted in governance documents.

## Unsupported-claim prevention

The agent must not claim that a command, check, or remote state has executed unless the claim is supported by retained direct evidence. Specifically:

- A numeric command exit status may be claimed only when the OpenCode tool result surfaced that exit status directly. If the tool did not surface a numeric exit status, the status is reported as unavailable and not inferred.
- A read is complete only when the file-read tool returned an explicit end-of-file result for the path.
- `git rev-parse origin/<branch>` reads a local remote-tracking reference; it is not an independent remote query.
- Successful output from the explicitly authorized `git push` is evidence that the referenced remote update succeeded; it does not establish unrelated remote state.
- Tracked-only commands (`git diff --name-status`, `git diff --stat`, `git diff --check`) cannot prove the absence or contents of untracked files.
- Direct reads of `.git/HEAD`, loose reference files, packed references, the Git index, or other `.git` internals are not substitutes for an explicitly required Git command. When a mandatory Git command is unavailable or denied, the agent stops and reports the unavailable evidence.
- Pattern-based privacy scans cannot prove the absence of every unknown private-identifier format; manual review remains the qualitative backstop.
- Exact validation totals are not claimed unless mechanically and reproducibly calculated.
- Inferred state is not direct observation. Successful later behavior may corroborate an earlier fact but does not turn the earlier unavailable observation into direct evidence.
- A checklist item must not be marked `PASS` when its evidence is pending, supplied only by assumption, depends on a future repository action, or was inferred rather than directly observed.
- Repository result, outcome classification, and scope compliance are separate fields. They are not merged into a single unlabelled conclusion.

## Hard-stop behavior

A required FAIL, BLOCKED, or unexpected command failure, a baseline mismatch, a missing required tracked file, an unavailable mandatory command exit status, or a detected scope deviation is a hard stop.

On a hard stop the agent must:

- stop further consequential work immediately;
- not continue by inference;
- not retry, weaken, wrap, replace, or supplement the failed command unless separately authorized;
- report the failure, the unavailable evidence, or the deviation neutrally;
- preserve the failure or deviation in the experiment record.
- A missing tool capability for a mandatory baseline command is an unavailable mandatory command and therefore a hard stop. The agent must not continue the requested analysis after substituting partial evidence.

A desired final deliverable never overrides a hard-stop rule. A standalone Python invocation, an ad hoc shell check, or a wrapper that hides the primary command's exit status does not satisfy a hard-stop requirement.

## Scope-deviation handling

On discovering a scope deviation the agent:

- stops further consequential work;
- reports the deviation neutrally;
- preserves the deviation in experiment evidence.

Self-correction is permitted only when both the defect and the correction are wholly inside the currently authorized path and action scope. When a deviation affects an unauthorized path or action, the agent must not edit, delete, revert, move, or otherwise clean up the affected item without a separate explicit maintainer authorization. Reporting a deviation does not authorize cleanup. A later authorization may classify the resulting correction as `deviation with approval`, but it does not erase the historical deviation. Maintainer-audit corrections supplement history; they do not rewrite it.

## Self-correction versus maintainer correction

- Self-correction is an agent-detected defect that the agent fixes entirely within the authorized path and action scope. It is recorded in the experiment record as a non-event for human-intervention counting.
- Maintainer correction is a maintainer turn that redirects or corrects the agent. It is recorded as a corrective-prompt event.
- An agent that detects a defect inside its authorized scope may correct it; an agent that detects a defect outside its authorized scope must stop and report.

## Validation and final-report expectations

- Validation commands are limited to those explicitly listed in the current Build authorization.
- Validation does not install dependencies, does not execute agent-initiated repository network commands, and does not open private working material.
- Reports state only whether agent-initiated repository network commands, package installations or external lookups were executed. Reports do not make claims about model-service or platform telemetry activity.
- The final report enumerates the affected path set, the validation commands and results, any self-correction, the scope-compliance classification, the exact `git status --short --untracked-files=all` output, and explicit confirmations that HEAD is unchanged and that nothing was staged, committed, or pushed.

### Mandatory phase-checklist reporting

The final response of every phase, subphase, and Build-stage report must reproduce the active phase checklist as the final section of the report. Each checklist item must use exactly one of:

- `[x] PASS`
- `[ ] FAIL`
- `[ ] BLOCKED`
- `[-] NOT APPLICABLE`

Each item must contain concise, directly observed evidence. A blanket statement such as "all checks passed" is insufficient. An item must not be marked `PASS` when its evidence is pending, supplied only by assumption, depends on a future repository action, or was inferred rather than directly observed. The final response must also continue to report the items listed in the validation and final-report expectations above.

## Hermes not integrated

Hermes is not integrated. Any reference to Hermes in evidence is a future-boundary statement and does not authorize current action.

## Machine-readable OpenCode harness (Increment A)

Increment A introduces a project-local machine-readable OpenCode harness consisting of `opencode.jsonc` and the agent definitions under `.opencode/agents/`. This harness constrains capabilities but never independently grants permission. Every consequential action still requires the exact current maintainer authorization in the current task. Machine-readable permissions are capability ceilings, not authorization grants.

The project harness defines three custom selectable primary agents:

- **`nudge-plan`** is the default selectable primary agent. It is planning-only. Its bounded command allowlist permits only the read-only local Git inspection commands and the `opencode --version` query explicitly listed in its definition; all other shell commands are denied. It does not mutate repository content, the Git index, commits, branches, remotes, configuration, dependencies, or external systems. Machine-readable permissions remain capability ceilings: every command and read still requires the exact current maintainer authorization.
- **`nudge-audit`** is a read-only auditing primary agent. Its bounded command allowlist permits only the read-only `git` inspection commands and the two `opencode` introspection commands explicitly listed in its definition. It does not mutate files, the Git index, commits, branches, remotes, configuration, dependencies, or external systems.
- **`nudge-build`** is the bounded, approval-gated implementation primary agent introduced by Increment B2. It automatically allows only the baseline read-only Git and OpenCode introspection commands listed in its definition. Ordinary edits and non-allowlisted local commands are approval-gated, while private material, OpenCode-harness edits, repository-action Git commands, network tools, dependency installers, shell wrappers, external-directory access, delegation, skills, search tools, and plan transitions are denied. Machine-readable permissions remain capability ceilings; every read, exact mutation path, and command still requires the exact current maintainer authorization.

The built-in selectable agents `build`, `plan`, `general`, `explore`, and `scout` are disabled in `opencode.jsonc`. Hidden system agents required for compaction, titles, and summaries are deliberately left available and are not disabled.

Raw session exports matching the generic `session-ses_*.md` pattern remain private working material. All three custom agents (`nudge-plan`, `nudge-audit`, and `nudge-build`) are explicitly denied from reading any path matching `*session-ses_*.md`.

Fresh-process runtime validation is mandatory after every permanent harness change. The accepted `nudge-audit` boundary is recorded in `EXP-0016`. The accepted `nudge-build` boundary is recorded in `EXP-0017`, including separate fresh-process automatic-allow, one-shot approval, and representative denial evidence. Ordinary implementation use remains subject to exact current maintainer authorization. Writing an agent definition does not itself prove that a running OpenCode process loaded it; `EXP-0017` records the required fresh-process evidence for the current candidate.

## Complete four-category authorization matrix

The complete matrix is recorded only in this file. The companion document must not duplicate the complete matrix.

### A. Allowed read-only by default

- `git status`, `git status --short`, `git status --short --untracked-files=all`.
- `git branch --show-current`, `git branch -vv`, `git branch -a`.
- `git rev-parse HEAD`.
- `git rev-parse origin/<branch>` — reads a local remote-tracking reference; not an independent remote query.
- `git ls-tree -r HEAD`, `git ls-tree -r HEAD --name-only`.
- `git log`, `git log --oneline`, `git log --oneline --decorate -1`.
- `git diff`, `git diff --name-status`, `git diff --stat`, `git diff --check`, `git diff -- <path>`.
- `git diff --cached --name-status`, `git diff --cached --stat`, `git diff --cached --check`, `git diff --cached -- <path>`.
- Tracked and cached diff commands do not prove the absence or contents of untracked files.
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

## Current release context

- **Active release:** `v0.1.1`
- **Release title:** `NudgeWhen v0.1.1 — Post-Release Closure and Reusable Validation Baseline`
- **Active branch:** `release/v0.1.1`
- **Active release charter:** `docs/releases/v0.1.1/release-charter.md`
- **Active phase list:** `docs/releases/v0.1.1/phase-list.md`
- **Current phase:** Phase 1 — Post-Release State and Documentation Closure
- **Bootstrap exception (historical, terminated):** The tracked `AGENTS.md` baseline clause historically required a specific completed release branch; that historical coupling required a narrow bootstrap exception for Phase 0 to proceed on the released `main` baseline before the new `AGENTS.md` was written. Branch creation alone did not terminate the exception. Phase 0D directly confirmed the four termination conditions: (a) this `AGENTS.md` recognizes `v0.1.1` and `release/v0.1.1`; (b) stable repository governance is separated from current-release context; (c) no normative dependence on any completed release branch remains; (d) the updated governance documents are mutually consistent. The maintainer accepted the Phase 0D evidence. The exception is now terminated. Ordinary baseline rules apply to later tasks.
- **Phase 0 closure record:** Phase 0 is `Complete`. The observed two-commit history on `release/v0.1.1` is the initial Phase 0 content commit `c2011b10c10fbd04b9911876bcf3d71f8c317d48` (subject `v0.1.1 continuation`, parent `2a092ed013d21f49044142395a8fedd24f9432b5`), which directly modified the seven authorized Phase 0 paths (4 modifications of existing governance files and 3 additions of the release-definition and experiment files), followed by the Phase 0 closure-synchronization commit `aa5fc6e42a85ecd00aaec4e86ed5d75c06bb4b1a` (subject `v0.1.1`, parent `c2011b10…`), which directly modified the four closure-overlay paths. The complete range from `2a092ed0…` through `aa5fc6e…` contains exactly seven distinct Phase 0 paths. Four paths were modified in both commits. The semantic descriptions "initial Phase 0 content commit" and "closure-synchronization commit" are strongly supported inferences based on path sets and chronology, not direct observations. The retained `Phase 0 staged-index validation` evidence records the cached name-status set, the cached whitespace-check output, the absence of an unstaged tracked diff, and seven stage-zero index records for the seven-path pre-closure candidate; numeric exit statuses were not surfaced and remain `Not available`; chronology strongly supports that this retained validation preceded `c2011b10…` and that relationship is labelled as inference. No retained direct evidence establishes a cached/index validation of the four-path closure overlay immediately before `aa5fc6e…`; the later two-commit-range `git diff --check` result is post-commit whitespace evidence and is not a substitute for the unavailable pre-commit cached validation. The current phase is Phase 1. Ordinary baseline rules continue to apply.
- **Machine-readable OpenCode harness:** Increment A introduced the project-local harness consisting of `opencode.jsonc` and the three custom primary agent definitions under `.opencode/agents/`: `nudge-plan` as the default planning-only agent, `nudge-audit` as the bounded read-only auditing agent, and `nudge-build` initially as an intentionally inert placeholder. The built-in selectable agents `build`, `plan`, `general`, `explore`, and `scout` remain disabled, while the hidden `compaction`, `summary`, and `title` system agents remain available. The accepted `nudge-audit` boundary is recorded in `EXP-0016`. Increment B2 replaces the initial `nudge-build` placeholder with the bounded, approval-gated implementation agent described above; the accepted `nudge-build` boundary is recorded in `EXP-0017`. Ordinary implementation use remains subject to exact current maintainer authorization, and every future permanent harness change requires fresh-process revalidation. Writing agent content does not itself prove that a running OpenCode process loaded it.