# Phase List — NudgeWhen v0.1.1

**Document status:** Accepted — Phases 0 through 3 complete; v0.1.1 release in progress
**Active release branch:** release/v0.1.1
**Active release charter:** docs/releases/v0.1.1/release-charter.md

## Release-wide sequencing rules

- All work for this release happens on the single branch `release/v0.1.1`. No parallel release branches are created.
- All phases remain on the same branch. A later phase may refine an earlier document only through explicitly scoped work.
- Exactly one pull request is opened into `main` after all release phases and the full pre-release gate are complete.
- Each phase ends with a maintainer review. Phase status transitions to `Complete` only after the review.
- No commit, push, pull request, tag, or release may be created without explicit maintainer authorization in the current task.
- Phase 7 covers only the final pre-release gate and the preparation of release actions. The merged pull request, the resulting `main` commit, CI on the merged `main` commit, the annotated tag, and the published GitHub release are separate post-merge release-completion actions and are not Phase 7 outputs.
- Every phase, subphase, and Build-stage report must end with a `Validation checklist` section as its final subsection. Each checklist item must use exactly one of `[x] PASS`, `[ ] FAIL`, `[ ] BLOCKED`, or `[-] NOT APPLICABLE` with concise, directly observed evidence. A blanket "all checks passed" statement is insufficient.

## Phase 0 — Release Definition and Governance Bootstrap

### Objective

Define the `v0.1.1` release intent, the ordered phase list, the governance documents, and the Phase 0 evidence record. Replace the obsolete v0.1.0-specific branch coupling in `AGENTS.md` with a durable, release-neutral structure.

### Principal deliverables

- `AGENTS.md` (generalized, with stable governance separated from a small current-release context)
- `docs/agentic-development/opencode-governance.md` (companion updated to match)
- `docs/agentic-development/experiment-protocol.md` (added rules for direct evidence, hard stops, mode recording, command-form deviations, and the mandatory checklist contract)
- `docs/agentic-development/evaluation-template.md` (extended template with authorization, scope, direct-observation, inference, and final validation-checklist sections)
- `docs/releases/v0.1.1/release-charter.md` (new)
- `docs/releases/v0.1.1/phase-list.md` (this document)
- `docs/agentic-development/experiments/EXP-0013.md` (new)

### Exact or bounded path scope

Exactly the seven paths listed in Principal deliverables.

### Required behavior

- `AGENTS.md` recognizes `v0.1.1` and `release/v0.1.1` in its current release context section.
- Stable repository-wide governance is separated from current-release context in `AGENTS.md`.
- No active governance rule requires `release/v0.1.0`.
- The complete four-category authorization matrix remains only in `AGENTS.md`.
- The mandatory phase-checklist reporting contract is present in `AGENTS.md`, the experiment protocol, and the evaluation template.
- The experiment protocol and the evaluation template use the four exact checklist result forms: `[x] PASS`, `[ ] FAIL`, `[ ] BLOCKED`, `[-] NOT APPLICABLE`.
- The v0.1.1 charter identifies the correct release, objective, in-scope deliverables, non-goals, single-release-branch policy, human approval boundaries, pre-release gates, post-merge release-completion evidence, definition of completion, and cross-references.
- The phase list contains exactly Phases 0 through 7, each with the required subsections in the required order, each ending with an explicit `Validation checklist`, each initially `Planned`.
- `EXP-0013.md` follows the experiment protocol without fabricated values and preserves the audited chronology.
- Historical v0.1.0 evidence remains unmodified.

### Boundaries and exclusions

- No application functionality or Android behavior change.
- No CI, validator, dependency, workflow, or remote-setting change.
- No change to `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/local-validation.md`, `.github/workflows/ci.yml`, `scripts/validate_local.py`, `scripts/validate-local.sh`, `.gitignore`, `app/build.gradle.kts`, or any v0.1.0 document.
- No ordinary content Build authorizes staging. The historical pre-closure staging and the two observed Phase 0 commits (`c2011b10…` and `aa5fc6e…`) have already occurred. The seven-path post-Phase-0 recovery candidate was committed in `8c89dc9cb6d7983d3927201bbd8ebe1acea273ec` (subject `docs: reconcile v0.1.1 phase 0 evidence`, parent `aa5fc6e…`), which directly modified the seven reconciliation paths: `AGENTS.md`, `docs/agentic-development/evaluation-template.md`, `docs/agentic-development/experiment-protocol.md`, `docs/agentic-development/experiments/EXP-0013.md`, `docs/agentic-development/opencode-governance.md`, `docs/releases/v0.1.1/phase-list.md`, and `docs/releases/v0.1.1/release-charter.md`. No retained direct evidence establishes an immediate pre-commit cached-index validation for `8c89dc9…`; the unavailable pre-commit cached validation is preserved as unavailable and is not fabricated. No active Phase 0 recovery candidate remains. Commit, push, branch, remote, pull-request, tag, and release actions remain separately authorized.
- No network access, installation, or external lookup.
- No claim that Phase 0 is `Complete` before evidence and maintainer acceptance exist.

### Required validation

- The original seven-path unstaged Phase 0 candidate was directly observed.
- The seven paths were separately staged in their pre-closure form.
- The pre-closure staged index passed accepted mechanical validation; the retained `Phase 0 staged-index validation` evidence records the cached name-status set, the cached whitespace-check output, the absence of an unstaged tracked diff, and seven stage-zero index records; numeric exit statuses were not surfaced and remain `Not available`.
- Phase 0G created the exact four-path unstaged closure overlay; the four-path overlay was later committed in `aa5fc6e42a85ecd00aaec4e86ed5d75c06bb4b1a`.
- The two-commit history on `release/v0.1.1` (parent `2a092ed013d21f49044142395a8fedd24f9432b5`, then `c2011b10c10fbd04b9911876bcf3d71f8c317d48`, then `aa5fc6e42a85ecd00aaec4e86ed5d75c06bb4b1a`) commits the seven authorized Phase 0 paths in full: the initial content commit modified the seven paths (4 modifications, 3 additions), and the closure-synchronization commit modified the four overlay paths. The complete two-commit range contains exactly seven distinct Phase 0 paths; four paths were modified in both commits.
- No retained direct evidence establishes a cached/index validation of the four-path closure overlay immediately before `aa5fc6e…`; the later two-commit-range `git diff --check` result is post-commit whitespace evidence and is not a substitute for the unavailable pre-commit cached validation.
- `git rev-parse HEAD` confirms HEAD is `aa5fc6e42a85ecd00aaec4e86ed5d75c06bb4b1a` on `release/v0.1.1`; HEAD^ is `c2011b10c10fbd04b9911876bcf3d71f8c317d48`; HEAD^^ is `2a092ed013d21f49044142395a8fedd24f9432b5`. HEAD has advanced from the starting commit; that advance is the expected outcome of the two-commit history and is not a deviation.
- Phase 0D performed the structural and documentation validation pass and confirmed that the new governance documents are mutually consistent and that the bootstrap exception has terminated.

**Historical Phase 0 validator context**

- The three new Phase 0 files were excluded from the current fixed candidate allowlist while untracked.
- They became visible through `git ls-files` after separately authorized staging.
- Phase 3 generalizes candidate-mode inventory and v0.1.1 semantic checks.
- The existing validator was not run in Phase 0C, Phase 0C2, Phase 0C3, or Phase 0C4.

### Completion evidence

- All seven authorized files are present on `release/v0.1.1` and pass the end-of-file readback.
- `AGENTS.md` no longer treats `release/v0.1.0` as the active branch.
- Stable governance is separated from current-release context.
- The bootstrap exception was bounded through Phase 0D and was terminated by the accepted Phase 0D evidence and the maintainer acceptance; ordinary baseline rules now apply.
- `EXP-0013.md` preserves the accepted chronology through the Phase 0G-R1 maintainer audit and the two-commit reconciliation. The seven authorized paths are committed in the observed two-commit history on `release/v0.1.1`. The current phase is Phase 1.
- Phase 0 remains `Complete`; the observed two-commit history (`c2011b10…` then `aa5fc6e…`) is retained; the seven-path pre-closure staged validation is retained in the `Phase 0 staged-index validation` record; the four-path pre-commit cached/index validation remains unavailable. The seven-path post-Phase-0 reconciliation was committed in `8c89dc9cb6d7983d3927201bbd8ebe1acea273ec`, which directly modified the seven reconciliation paths. The missing immediate pre-commit cached-index evidence for `8c89dc9…` remains unavailable and is not fabricated. The later preparatory harness and evidence commits (`ccc56edb1fe4084a02caf56680ca67085039a9fa`, `7a3e57bbd1e0f231ce8e8e6af0a3831c38d35fec`, `9f2e283516db5822e63d86fbe83ac7f222283ba0`, and `1d1754da86182d21820b88a819cfd6879eba9ed8`) advanced HEAD through `1d1754da86182d21820b88a819cfd6879eba9ed8` on `release/v0.1.1` and immediately before Phase 1R0 began, the repository was directly observed clean. The current phase is Phase 1.

### Status

Complete

### Validation checklist

- [x] PASS — The v0.1.1 charter exists, identifies the correct release (`v0.1.1`) and the correct objective (post-release closure and reusable validation baseline, no new product functionality). Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — The v0.1.1 phase list exists and defines Phases 0 through 7 in the required order. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Every phase ends with an explicit `Validation checklist` subsection. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Phase 0 has status `Complete`; Phases 1 through 7 have status `Planned`. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — `AGENTS.md` no longer treats `release/v0.1.0` as the active branch. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Stable governance is separated from current-release context in `AGENTS.md`. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Current release context identifies `v0.1.1`, `release/v0.1.1`, the charter path, and the phase-list path. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — The temporary bootstrap exception was bounded through Phase 0D and was terminated by the accepted Phase 0D evidence and the maintainer acceptance. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — The OpenCode and MiniMax M3 execution profile is recorded without unsupported model claims. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — The mandatory checklist-reporting contract is present in `AGENTS.md`, the experiment protocol, and the evaluation template. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — `EXP-0013.md` follows the experiment protocol without fabricated values and preserves the audited chronology. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Historical v0.1.0 evidence remains unmodified. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — No application, Android, CI, dependency, workflow, validator, or remote-setting change occurred in Phase 0. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Only the seven authorized Phase 0 paths were modified or created. Directly verified by the pre-edit readback; accepted by Phase 0D and maintainer.
- [x] PASS — Structural and documentation consistency: the terminal maintainer audit and the synchronized evidence resolve the recovery candidate's active structural contradiction.
- [x] PASS — Repository state through the observed commit history is accurately reported. The original two-commit range `2a092ed0…aa5fc6e…` contains exactly seven distinct Phase 0 paths; `git diff --check 2a092ed0…aa5fc6e…` returns no diagnostic. The historical Phase 0 recovery Build started from the exact seven-path unstaged recovery baseline with no staged or untracked path; that working tree was not clean. The seven-path post-Phase-0 reconciliation was later committed in `8c89dc9cb6d7983d3927201bbd8ebe1acea273ec` on `release/v0.1.1`. Immediately before Phase 1R0 began, the repository was directly observed clean at `1d1754da86182d21820b88a819cfd6879eba9ed8`; no active Phase 0 recovery-staging sequence remains.
- [x] PASS — The seven Phase 0 documents contain no unresolved lifecycle or evidence-record contradiction: the historical two-commit evidence remains intact; the historical dirty recovery baseline and the later `8c89dc9…` reconciliation commit are accurately distinguished; both recovery Builds and their maintainer classifications are recorded; no active Phase 0 recovery-staging sequence remains.
- [x] PASS — Phase 0 was not marked complete before accepted structural evidence and accepted pre-closure staged-index validation existed.

## Phase 1 — Post-Release State and Documentation Closure

### Objective

Correct current-facing documentation so that the repository accurately describes the released v0.1.0 baseline and the repository's real capabilities. Remove stale claims that the repository lacks Android, Gradle, CI, an APK, a published release, application validation, or a completed v0.1.0 release train.

### Principal deliverables

- `README.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `docs/local-validation.md`
- `docs/releases/v0.1.0/phase-list.md` (status summary correction only, if needed)
- `docs/releases/v0.1.0/agent-evaluation.md` (closure note, if needed)
- Any directly affected cross-references
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Preparatory work note

Increment A and Increment B2 are preparatory machine-readable harness increments completed while Phase 1 is current; they are recorded in `AGENTS.md` and `EXP-0014` through `EXP-0017` and are not formally defined Phase 1 deliverables. Formal Phase 1 documentation implementation was completed by the Phase 1B Build and manually committed and pushed by the maintainer; see the Status section and the updated validation checklist below. Phase 1 is now `Complete`.

### Exact or bounded path scope

The current-facing documentation paths listed above. Historical v0.1.0 evidence is preserved with explicit closure annotations; raw command evidence, measurements, classifications, and historical experiment outcomes are not modified.

### Required behavior

- Current-facing documentation describes the released v0.1.0 baseline and the repository's real capabilities.
- Current-facing documentation does not direct contributors or agents to the deleted `release/v0.1.0` branch.
- Historical v0.1.0 evidence remains identifiable and unaltered except for explicit closure annotations.
- The v0.1.0 phase-list status summary agrees with the per-phase statuses.
- The v0.1.0 evaluation document carries a clearly labelled post-release closure note where its former "Phase 6 remains Planned" statement no longer represents the final release state.
- Links resolve.

### Boundaries and exclusions

- No workflow changes, remote GitHub configuration, validator refactoring, dependency changes, or Android changes.
- No product functionality.

### Required validation

- A direct read of each affected current-facing file.
- A repository-wide search confirms no current-facing false claim identified by the v0.1.0 audit.
- Historical evidence remains identifiable and unaltered except for explicit closure annotations.
- `docs/local-validation.md` is read through an explicit end-of-file result.

### Completion evidence

- The affected current-facing files are present on `release/v0.1.1` and pass the end-of-file readback.
- A repository-wide search finds no current-facing false claim identified by the v0.1.0 audit.
- Historical evidence remains identifiable and unaltered except for explicit closure annotations.
- Links resolve.
- Documentation status declarations agree with document content.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Status

Complete

### Validation checklist

- [x] PASS — `README.md` describes the released v0.1.0 baseline and the repository's real capabilities. Directly observed by the pre-mutation readback; the document lists the Android application project, the `:app` module, Kotlin and Jetpack Compose, the launcher activity, the static text, the Gradle wrapper, AGP, compile and target SDK, the local validation suite, the local-validation documentation, the GitHub Actions CI workflow, the published v0.1.0 release, and the locally generated debug APK. No stale absence claim remains.
- [x] PASS — `CONTRIBUTING.md` does not claim that the repository lacks Android, Gradle, CI, an APK, a published release, or a completed v0.1.0 release train. Directly observed by the pre-mutation readback; the document names the v0.1.0 release as complete and historical, names the v0.1.1 release train as active, and lists Android source, Gradle build files, manifest, resources, validation, and CI artefacts.
- [x] PASS — `SECURITY.md` does not claim the same absence. Directly verified by the pre-mutation readback; the Build replaced the stale "Current state" paragraph that listed "no released or runnable application…no Android application code, no Gradle build, no APK…no CI workflow, and no published release" with a paragraph naming the v0.1.0 historical released baseline, the v0.1.1 active release train, and the real repository capabilities. The experimental/no-support nature of the project is preserved; security reporting guidance is preserved; no production support promise is created.
- [x] PASS — `docs/local-validation.md` does not direct contributors or agents to a deleted `release/v0.1.0` branch. Directly verified by the post-mutation readback; the Build reframed the "Purpose and scope" prose to describe the validator as the v0.1.0 local-validation baseline carried forward into v0.1.1 until Phase 3 refactors it, and reframed the "Phase 5" section to record that v0.1.0 Phase 6 is also complete. The exact validator behavior, command semantics, release-gate semantics, Android SDK / JDK / build-tools requirements, and Phase 4 proof contract are preserved unmodified.
- [x] PASS — The v0.1.0 phase list status summary agrees with the per-phase statuses. Directly verified by the post-mutation readback; the document-status line and the historical-closure annotation now state that all eight phases of v0.1.0 (Phases 0 through 7) are `Complete`. No raw historical evidence, measurement, classification, or experiment outcome was rewritten.
- [x] PASS — The v0.1.0 evaluation document carries a closure note where the former "Phase 6 remains Planned" statement no longer represents the final release state. Directly verified by the post-mutation readback; the Build added a clearly labelled `Post-release closure note (added in the v0.1.1 Phase 1 documentation closure)` blockquote immediately below the document header. No raw historical evidence, measurement, classification, or experiment outcome was rewritten.
- [x] PASS — General contributor and project documentation uses branch conventions such as `release/vX.Y.Z` rather than embedding the currently active patch branch. Directly observed by the pre-mutation readbacks of `README.md`, `CONTRIBUTING.md`, and `SECURITY.md`; the `release/v0.1.0` references that remain in current-facing documents are framed as historical evidence of the completed v0.1.0 release, not as the active branch.
- [x] PASS — Links resolve. Directly observed by the docs-group validation result `docs/md-links — all relative Markdown links resolve`; the validator was run in this Build and produced no failure.
- [x] PASS — Documentation status declarations agree with document content. Directly observed by the post-mutation readbacks of `SECURITY.md`, `docs/local-validation.md`, `docs/releases/v0.1.0/phase-list.md`, `docs/releases/v0.1.0/agent-evaluation.md`, and the synchronized Phase 1 status in this file.
- [x] PASS — Phase experiment record; ID assigned when the task starts according to the experiment protocol. Directly observed by the existence of `docs/agentic-development/experiments/EXP-0019.md` recording the Phase 1B Build.
- [x] PASS — The required-group validation completed without any `FAIL` line. Directly observed by the post-mutation validation run `SUMMARY pass=7 fail=0 skip=0` on `./scripts/validate-local.sh --group required`.
- [x] PASS — The docs-group validation completed without any `FAIL` line. Directly observed by the post-mutation validation run `SUMMARY pass=10 fail=0 skip=0` on `./scripts/validate-local.sh --group docs`.
- [x] PASS — The `--skip-android` validation completed without any `FAIL` line. Directly observed by the post-mutation validation run `SUMMARY pass=17 fail=0 skip=0` on `./scripts/validate-local.sh --skip-android`.
- [x] PASS — A repository-wide stale-claim search was performed against the eight target patterns using the harness's `Grep` tool. Directly recorded in `EXP-0019.md`; no denied command or unapproved substitution occurred.
- [x] PASS — Commit, push, and post-Build acceptance of the documentation candidate are now performed via the maintainer's manual repository action. Commit hash: `fc288a2bb5103832a4c4969bbc67cd3bfe7aab6a`; commit message: `docs: close v0.1.1 phase 1 documentation state`; commit summary: 6 files changed, 402 insertions(+), 19 deletions(-); create mode `100644 docs/agentic-development/experiments/EXP-0019.md`. Push evidence: `8f28638..fc288a2 release/v0.1.1 -> release/v0.1.1`. The Build produced the candidate; the maintainer manually performed the staging, commit, and push. A prior `nudge-build` R1 attempt to perform the same `git add` was blocked by the OpenCode harness permission boundary; the maintainer's manual action followed that block.
- [x] PASS — The maintainer accepted the Phase 1 documentation candidate by manually staging, committing, and pushing exactly the six Phase 1B paths in commit `fc288a2bb5103832a4c4969bbc67cd3bfe7aab6a` on `release/v0.1.1`. The Build produced the candidate; the maintainer's manual commit and push constitutes post-Build documentation acceptance.

## Phase 2 — Persistent CI and Protected-Branch Enforcement

### Objective

Replace the one-release-only CI configuration with a persistent validation policy for future release branches, pull requests targeting `main`, and merged `main` commits. Verify the protected-branch or ruleset configuration on `main` through separately authorized remote administration.

### Principal deliverables

- Updated `.github/workflows/ci.yml`
- CI-policy documentation in the v0.1.1 release directory
- Verified `main` protection or ruleset configuration
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Exact or bounded path scope

`.github/workflows/ci.yml`, the v0.1.1 CI-policy documentation, and the protected-branch or ruleset configuration on the remote `main` branch.

### Required behavior

- The stable `validate` job runs on pushes to `release/**`, on pull requests targeting `main`, on pushes to `main`, and on manual `workflow_dispatch`.
- The required job name remains `validate` so branch protection can require it without being tied to one release version.
- Read-only default permissions, full-SHA action pinning, bounded timeout, concurrency cancellation, and debug APK upload after successful validation are preserved.
- The active `main` protection or ruleset requires a pull request before merge, the stable `validate` status check, no force pushes, and no branch deletion.
- Remote settings are independently read back and recorded.

### Boundaries and exclusions

- No validator refactor, no application functionality, no dependency upgrades, no automatic merging, no release publication, no production signing.

### Required validation

- A push to `release/v0.1.1` automatically starts the workflow.
- The resulting `validate` run passes.
- The workflow file covers `release/**`, pull requests into `main`, and pushes to `main`.
- The `main` ruleset explicitly requires the stable `validate` check.
- Remote settings are independently read back and recorded.
- A direct read of `.github/workflows/ci.yml` confirms the trigger coverage and the stable job name.

### Completion evidence

- A push to `release/v0.1.1` automatically starts the workflow.
- The resulting `validate` run passes.
- The workflow file covers `release/**`, pull requests into `main`, and pushes to `main`.
- The `main` ruleset explicitly requires the stable `validate` check.
- Remote settings are independently read back and recorded.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Status

Complete

### Validation checklist

- [x] PASS — `.github/workflows/ci.yml` triggers on pushes to `release/**`. Directly observed by the post-mutation readback; the workflow `on.push.branches` list contains the `release/**` pattern. Phase 2A produced the local candidate; the actual push, the resulting workflow run, and the remote ruleset verification are separate actions.
- [x] PASS — `.github/workflows/ci.yml` triggers on pull requests targeting `main`. Directly observed by the post-mutation readback; the workflow `on.pull_request.branches` list contains `main`. Phase 2A produced the local candidate; the actual pull request, the resulting workflow run, and the remote ruleset verification are separate actions.
- [x] PASS — `.github/workflows/ci.yml` triggers on pushes to `main`. Directly observed by the post-mutation readback; the workflow `on.push.branches` list contains `main` in addition to `release/**`. Phase 2A produced the local candidate; the actual push to `main`, the resulting workflow run, and the remote ruleset verification are separate actions.
- [x] PASS — `.github/workflows/ci.yml` triggers on manual `workflow_dispatch`. Directly observed by the post-mutation readback; the workflow `on` map contains the `workflow_dispatch` key.
- [x] PASS — The required job name is stable as `validate`. Directly observed by the post-mutation readback; the `jobs` map has a single `validate` key with `name: validate`. Branch protection or ruleset configuration can require the stable `validate` job by name.
- [x] PASS — Read-only default permissions, full-SHA action pinning, bounded timeout, concurrency cancellation, and debug APK upload are preserved. Directly observed by the post-mutation readback; `permissions: contents: read` is at the top level, all three `uses:` references are pinned to full commit SHAs with version comments, `timeout-minutes: 30` is set on the job, `concurrency.cancel-in-progress: true` is set, and the `upload-debug-apk` step with `if: success()` is preserved.
- [x] PASS — CI policy documentation exists. Directly observed by the existence of `docs/releases/v0.1.1/ci-policy.md` recording the purpose and scope, trigger matrix, stable job name, security posture, validation behavior, branch protection boundary, and release-train status.
- [x] PASS — Phase experiment record exists. Directly observed by the creation of `docs/agentic-development/experiments/EXP-0020.md` recording the Phase 2A Build.
- [x] PASS — A push to `release/v0.1.1` automatically starts the workflow. Directly recorded by the maintainer-supplied GitHub Actions evidence: run ID `29036989383`, workflow name `CI`, branch `release/v0.1.1`, event `push`, head SHA `e754e9a54913633adbd6e858004836f2b51b7cb2`, run status `completed`, run conclusion `success`, run URL `https://github.com/franchoy/nudgewhen/actions/runs/29036989383`. The commit `e754e9a54913633adbd6e858004836f2b51b7cb2` (`ci: generalize validation workflow`) and the push `d73fd3e..e754e9a release/v0.1.1 -> release/v0.1.1` are maintainer-supplied evidence. The local post-commit working tree was clean.
- [x] PASS — The resulting `validate` run passes. Directly recorded by the maintainer-supplied GitHub Actions evidence: run ID `29036989383` completed with conclusion `success`; job name `validate` completed with conclusion `success`; `validate-local` step `success`; `upload-debug-apk` step `success`; job URL `https://github.com/franchoy/nudgewhen/actions/runs/29036989383/job/86184292611`. The stable `validate` job name is the exact required check identifier.
- [x] PASS — The `main` ruleset explicitly requires the stable `validate` check. Directly recorded by the maintainer-supplied ruleset readback evidence: ruleset ID `17924125`, name `Protect main`, target `branch`, enforcement `active`, conditions `ref_name include ["~DEFAULT_BRANCH"]`, exclude empty, `current_user_can_bypass: never`, `bypass_actors` empty. Active rules applying to `main`: `deletion`, `non_fast_forward`, `pull_request`, `required_status_checks`. `required_status_checks` parameters: required context `validate`, integration ID `15368`, `strict_required_status_checks_policy: false`, `do_not_enforce_on_create: false`.
- [x] PASS — Remote settings are independently read back and recorded. Directly recorded by the maintainer-supplied ruleset readback evidence listed in the previous item, plus the maintainer-supplied GitHub Rulesets UI corroboration that `Require a pull request before merging` is checked, `Require status checks to pass` is checked, and `Status checks that are required` includes `validate` with GitHub Actions. The prior attempted API write to the classic branch protection endpoint returned `403 Resource not accessible by integration`; this limitation does not block the ruleset readback. The successful ruleset setting was made manually through the GitHub UI by the maintainer; no remote write was performed by an agent Build. All recorded in `EXP-0021.md`.

## Phase 3 — Reusable Local-Validator Architecture

### Objective

Refactor the v0.1.0-specific validator into a reusable, release-aware validation architecture without weakening its existing contracts.

### Principal deliverables

- Refactored `scripts/validate_local.py`
- Updated `scripts/validate-local.sh` where required
- A single documented source for release-specific validation expectations
- Updated `docs/local-validation.md`
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Exact or bounded path scope

The validator implementation, its shell entry point, its documentation, and the single release-contract source.

### Required behavior

- Stable repository checks, current-release checks, Android build and artifact checks, release-gate calculation, and user-facing command-line handling are clearly separated.
- Release-specific information is not duplicated throughout the implementation. Release version, version code, release branch, active release-document paths, and expected phase range or completion state are read from one authoritative location.
- The release-contract representation is human-reviewable, standard-library-readable, deterministic, validatable, and free of network requirements.
- Running outside a Git worktree produces a concise prerequisite failure and exit `2`, not a traceback.
- Historical release documents are not mistaken for the active release contract.
- Stable checks do not require source edits merely because a new release directory is introduced.
- Existing Android manifest and artifact checks remain at least as strict as v0.1.0.

### Boundaries and exclusions

- No broad feature expansion, no Android behavior change, no third-party Python library, no CI redesign, no remote configuration.

### Required validation

- Existing valid v0.1.0-style repository behavior remains accepted where still applicable.
- The active v0.1.1 release contract is read from one authoritative location.
- Missing-Git and invalid-invocation paths fail cleanly with exit `2`.
- No traceback appears for expected prerequisite failures.
- Candidate and clean-checkout semantics remain deterministic.
- A direct read of `scripts/validate_local.py` and `scripts/validate-local.sh` confirms the refactor.
- A direct read of `docs/local-validation.md` confirms the updated documentation.

### Completion evidence

- Existing v0.1.0-style repository behavior remains accepted where still applicable.
- The active v0.1.1 release contract is read from one authoritative location.
- Missing-Git and invalid-invocation paths fail cleanly with exit `2`.
- No traceback appears for expected prerequisite failures.
- Candidate and clean-checkout semantics remain deterministic.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

**Phase 3 closure evidence (synchronized after manual repository action).** The accepted Phase 3 implementation outcome is `Successful with correction`; the accepted experiment evidence is `EXP-0027`. The exact three-path implementation and evidence commit is `cad89bfe241e10d6661a7746058721e22a5b9880` (subject `refactor: complete phase 3 local validator architecture`, parent recorded in the `EXP-0027` chronology), which directly modified `docs/agentic-development/experiments/EXP-0027.md` (addition), `docs/local-validation.md` (modification), and `scripts/validate_local.py` (modification). That commit was successfully pushed to `origin/release/v0.1.1`; the local HEAD and the remote-tracking hash were established as identical. The exact-head CI run is `30949699383` (workflow `CI`, event `push`, branch `release/v0.1.1`, head SHA `cad89bfe241e10d6661a7746058721e22a5b9880`, conclusion `success`). No product functionality, Android behavior, or Android permission was added or changed; only the validator architecture, its documentation, and the corresponding experiment record were modified. Historical attempt deviations recorded in `EXP-0027.md` remain historical evidence and have not been erased.

### Status

Complete

### Validation checklist

- [x] PASS — The validator separates stable, current-release, Android, release-gate, and command-line handling. Directly observed by the Phase 3A5-R2 readbacks of `scripts/validate_local.py` (1705 lines through explicit EOF) and `docs/local-validation.md` (374 lines through explicit EOF); the architecture is reflected in the Phase 3A4a, Phase 3A4c, and Phase 3A5 sections of `docs/local-validation.md`.
- [x] PASS — Release-specific information is not duplicated and is read from one authoritative location. Directly observed by `scripts/release_contract.json` (read through explicit EOF at 65 lines), which is the single source for active release identity, phase model, Android identity, validation groups, and historical pointer; the Phase 3A2 wiring of the `required` group loads, structurally validates, and cross-checks this contract.
- [x] PASS — The release-contract representation is human-reviewable, standard-library-readable, deterministic, validatable, and free of network requirements. Directly observed by the two-space-indented JSON with sorted logical sections and a top-level `schema_version` field, loaded via the standard library only (`open()`/`read_bytes()`/`json.loads()`), and by the accepted validation totals `SUMMARY pass=8 fail=0 skip=0` (required), `pass=10 fail=0 skip=0` (docs), and `pass=18 fail=0 skip=0` (skip-Android), with `release_gate=NOT_SATISFIED` on the partial runs.
- [x] PASS — The `required`, `docs`, `android`, and `all` groups are preserved. Directly observed by the contract's `validation.groups = ["required", "docs", "android"]` and `validation.all_alias = "all"`, by the `VALIDATION_HANDLERS` registry that maps each real group identifier to a wrapper, and by the accepted validation totals above.
- [x] PASS — Candidate and clean-checkout modes are preserved. Directly observed by `docs/local-validation.md` lines 284-290 (the `Candidate and clean-checkout modes` subsection), which retains the candidate-mode untracked-path inventory and the clean-mode tracked-only requirement.
- [x] PASS — Exit codes `0`, `1`, and `2` are preserved with the same semantics. Directly observed by the exit-code table in `docs/local-validation.md` (lines 178-184) and by the accepted Phase 3A5-R2 validation totals, which were produced with the expected exit codes for the partial and complete runs.
- [x] PASS — `release_gate=SATISFIED` is emitted only on the complete all-groups run. Directly observed by the release-gate semantics in `docs/local-validation.md` (lines 232-250) and by the accepted Phase 3A5-R2 full-offline run `SUMMARY pass=34 fail=0 skip=0` with `release_gate=SATISFIED`, while the partial runs reported `release_gate=NOT_SATISFIED`.
- [x] PASS — No staging, repository mutation, dependency installation, or network activity is introduced. Directly observed by `docs/local-validation.md` (the `SDK environment-variable requirements` and `--require-clean` sections) and by the validator's `no_network` and `no_dependency_installation` invariants in the contract; the only Phase 3 paths modified are the three that commit `cad89bfe…` touches.
- [x] PASS — Missing-Git and invalid-invocation paths fail cleanly with exit `2`. Directly observed by the missing-Git output `FAIL prerequisite/git — git executable not found` / `SUMMARY pass=0 fail=1 skip=0` / `release_gate=NOT_SATISFIED` documented in `docs/local-validation.md` (lines 56-62) and by the invalid-Git-worktree output `FAIL prerequisite/git-worktree — repository is not a Git worktree` / `SUMMARY pass=0 fail=1 skip=0` / `release_gate=NOT_SATISFIED` documented at lines 89-101; the Phase 3A5-R2 controlled invalid-worktree output matched the required three-line result.
- [x] PASS — Historical release documents are not mistaken for the active release contract. Directly observed by the `historical` block of `scripts/release_contract.json` (`previous_release_version = "v0.1.0"`, `previous_release_docs_root = "docs/releases/v0.1.0"`, `previous_release_is_historical = true`) and by the Phase 3A3a `charter-consistency` check that uses the active charter from `release_documents.charter`.
- [x] PASS — Existing Android manifest and artifact checks remain at least as strict as v0.1.0. Directly observed by the Phase 3A5 contract-driven Android expectations and the `apk-metadata` / `source-manifest` / `merged-manifest` documentation in `docs/local-validation.md` (lines 113-127 and 332-337), and by the accepted Phase 3A5-R2 Android-offline run `SUMMARY pass=16 fail=0 skip=0` and full-offline run `SUMMARY pass=34 fail=0 skip=0` with `release_gate=SATISFIED`.
- [x] PASS — Phase experiment record; ID assigned when the task starts according to the experiment protocol. Directly observed by the existence of `docs/agentic-development/experiments/EXP-0027.md` (read through explicit EOF at 563 lines), which preserves the Phase 3R2, Phase 3A5, Phase 3A5-R1, and Phase 3A5-R2 chronology and records the accepted Phase 3 implementation outcome `Successful with correction`.

## Phase 4 — Validator Regression Suite and Repository-Consistency Enforcement

### Objective

Add tests for the validator itself and ensure the repository gate detects the stale-state contradictions that escaped v0.1.0 validation.

### Principal deliverables

- Standard-library Python test suite under an agreed `tests/` structure
- Minimal deterministic fixtures
- Additional repository-consistency checks in the validator
- A single documented command or gate sequence that runs both the validator tests and the repository validation
- CI integration for the validator test suite
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Exact or bounded path scope

The test suite, its fixtures, the consistency check additions, the documented run command, and the CI integration for the test suite.

### Required behavior

- Tests cover argument parsing, group resolution, unknown and contradictory arguments, exit codes `0`, `1`, and `2`, release-gate calculation, missing `.git` or non-worktree execution, malformed XML, TOML, YAML, or release-contract input where applicable, broken relative Markdown links, stale active-release branch references, current documents falsely claiming that Android, CI, or releases do not exist, phase-status summary disagreement, incorrect CI trigger coverage, missing wrapper-distribution checksum, generated bytecode or prohibited output detection, clean and dirty working-tree behavior, and direct invocation of the actual repository validator code rather than a parallel reimplementation.
- The validator detects at least: active governance pointing to a completed release, current-facing documentation naming a deleted release branch, contradictions between individual phase statuses and their summary, CI restricted to one historical release branch, and application version metadata disagreeing with the active release contract.
- Tests use temporary directories, avoid network access, avoid touching the real Git index, avoid creating non-ignored output in the repository, and run with Python bytecode generation suppressed or safely isolated.

### Boundaries and exclusions

- No Android functionality, no production dependencies, no network-backed tests, no emulator tests, no attempt to test conversational agent behavior that is not repository-observable.

### Required validation

- The complete validator regression suite passes.
- At least one controlled negative fixture exists for every newly enforced contradiction class.
- Removing or corrupting each required contract causes the corresponding test to fail.
- CI executes both the tests and the real validator.
- The clean repository remains clean after the complete test run.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Completion evidence

- The complete validator regression suite passes.
- At least one controlled negative fixture exists for every newly enforced contradiction class.
- Removing or corrupting each required contract causes the corresponding test to fail.
- CI executes both the tests and the real validator.
- The clean repository remains clean after the complete test run.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Status

Planned

### Validation checklist

- [ ] BLOCKED — A standard-library test suite exists under an agreed `tests/` structure. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Tests cover argument parsing, group resolution, unknown and contradictory arguments, exit codes, release-gate calculation, missing `.git`, malformed inputs, broken Markdown links, stale active-branch references, false absence claims, phase-status summary disagreement, CI trigger coverage, missing wrapper checksum, bytecode detection, clean and dirty working-tree behavior, and direct invocation of the real validator. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The validator detects active governance pointing to a completed release, current-facing documentation naming a deleted release branch, contradictions between individual phase statuses and their summary, CI restricted to one historical release branch, and application version metadata disagreeing with the active release contract. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Tests use temporary directories, avoid network access, avoid touching the real Git index, avoid creating non-ignored output, and run with Python bytecode generation suppressed or safely isolated. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The complete validator regression suite passes. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — CI executes both the tests and the real validator. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Phase experiment record; ID assigned when the task starts according to the experiment protocol. The phase has not started; direct completion evidence is not yet available.

## Phase 5 — Supply-Chain, Workspace Hygiene, and Release Metadata

### Objective

Close the remaining deterministic supply-chain and workspace-hygiene gaps and align the Android artifact with v0.1.1.

### Principal deliverables

- Updated `gradle/wrapper/gradle-wrapper.properties`
- Updated `.gitignore`
- Wrapper-integrity validation
- `.github/dependabot.yml`
- Updated Android version metadata
- Any directly affected validation expectations and documentation
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Exact or bounded path scope

The Gradle wrapper, the `.gitignore` ignore patterns, the wrapper-integrity check, the `.github/dependabot.yml` configuration, and the Android version metadata in `app/build.gradle.kts`.

### Required behavior

- The official Gradle 9.4.1 `distributionSha256Sum` is added.
- The committed Gradle wrapper JAR is validated against the approved checksum.
- `validateDistributionUrl=true` is preserved.
- GitHub Actions continue to be pinned to full commit SHAs.
- Dependabot is configured for Gradle dependencies and GitHub Actions, creates reviewable PRs only, and does not auto-merge.
- The `__pycache__/` and `*.py[cod]` ignore patterns are added.
- Validation continues rejecting tracked bytecode and prohibited generated output.
- The Android version metadata is updated to `versionCode = 2` and `versionName = "0.1.1"`.
- The package name, namespace, minimum SDK, target SDK, compile SDK, launcher activity, and visible baseline behavior remain unchanged.

### Boundaries and exclusions

- No new application behavior, no dependency upgrade train, no production signing, no publication to an app store, no permission, service, receiver, provider, networking, or persistence changes.

### Required validation

- Gradle rejects a distribution whose checksum does not match.
- The wrapper JAR checksum matches the approved value.
- Python compilation cannot leave visible non-ignored bytecode in the repository.
- Dependabot configuration parses and covers both declared ecosystems.
- The assembled APK reports `versionCode = 2` and `versionName = 0.1.1`.
- Source and merged manifest allowlists remain satisfied.

### Completion evidence

- Gradle rejects a distribution whose checksum does not match.
- The wrapper JAR checksum matches the approved value.
- Python compilation cannot leave visible non-ignored bytecode in the repository.
- Dependabot configuration parses and covers both declared ecosystems.
- The assembled APK reports `versionCode = 2` and `versionName = 0.1.1`.
- Source and merged manifest allowlists remain satisfied.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Status

Planned

### Validation checklist

- [ ] BLOCKED — The Gradle 9.4.1 `distributionSha256Sum` is present in `gradle/wrapper/gradle-wrapper.properties`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The committed Gradle wrapper JAR matches the approved checksum. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `validateDistributionUrl=true` is preserved. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — GitHub Actions remain pinned to full commit SHAs. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `.github/dependabot.yml` covers Gradle and GitHub Actions ecosystems. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Dependabot creates reviewable PRs only and does not auto-merge. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The `__pycache__/` and `*.py[cod]` ignore patterns are present in `.gitignore`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The validator rejects tracked bytecode and prohibited generated output. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The Android artifact reports `versionCode = 2` and `versionName = 0.1.1`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Source and merged manifest allowlists remain satisfied. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Phase experiment record; ID assigned when the task starts according to the experiment protocol. The phase has not started; direct completion evidence is not yet available.

## Phase 6 — Integrated Evidence and Agent Evaluation

### Objective

Evaluate the v0.1.1 work, determine whether the v0.1.0 problems were actually prevented, and close all release documentation before the final gate.

### Principal deliverables

- `docs/releases/v0.1.1/agent-evaluation.md`
- Updated status fields in the v0.1.1 charter and phase list
- Completed experiment records for Phases 0 through 5
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.
- Explicit disposition of relevant v0.1.0 deferred candidates

### Exact or bounded path scope

The v0.1.1 agent evaluation document, the v0.1.1 charter and phase-list status fields, the experiment records for Phases 0 through 5, and the disposition of relevant v0.1.0 deferred candidates.

### Required behavior

- The evaluation determines whether generalized governance prevented stale-branch blocking, whether current-state checks caught contradictions that v0.1.0 missed, whether validator tests exercised the real validator, whether any Build continued after a normalized failure, whether any unauthorized files, bytecode, temporary files, retries, or remote mutations were created, whether final reports distinguished observed, inferred, supplied, and pending evidence, and whether the new controls are repository-enforced, tool-enforced, or prose-only.
- The evaluation explicitly records the disposition of relevant v0.1.0 deferred candidates.
- No additional helper, skill, plugin, MCP integration, shell guard, or reporting framework is introduced merely because it appeared in the v0.1.0 shortlist. Each requires independent evidence and explicit scope.

### Boundaries and exclusions

- No new app functionality, no new CI architecture, no unrelated refactor, no speculative OpenCode or Hermes integration.

### Required validation

- Every completed phase has accepted experiment evidence.
- Every deviation is classified and resolved or explicitly accepted.
- No unsupported "the validator guarantees agent behavior" claim is made.
- The evaluation clearly separates deterministic controls from conversational or transcript-only behavior.
- All Phase 0 through 5 statuses are synchronized.

### Completion evidence

- Every completed phase has accepted experiment evidence.
- Every deviation is classified and resolved or explicitly accepted.
- No unsupported "the validator guarantees agent behavior" claim is made.
- The evaluation clearly separates deterministic controls from conversational or transcript-only behavior.
- All Phase 0 through 5 statuses are synchronized.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Status

Planned

### Validation checklist

- [ ] BLOCKED — `docs/releases/v0.1.1/agent-evaluation.md` exists and classifies each repeated lesson. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Every completed phase has an accepted experiment record. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Every deviation is classified and resolved or explicitly accepted. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The evaluation distinguishes repository-enforced, tool-enforced, prose-only, and deferred controls. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — No unsupported "the validator guarantees agent behavior" claim is made. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The v0.1.0 deferred candidates are explicitly dispositioned. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — All Phase 0 through 5 statuses are synchronized. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Phase experiment record; ID assigned when the task starts according to the experiment protocol. The phase has not started; direct completion evidence is not yet available.

## Phase 7 — Full Pre-Release Gate and Release-PR Preparation

### Objective

Run the complete v0.1.1 gate from a clean release candidate and prepare the single release-bearing pull request and post-merge actions.

### Principal deliverables

- Full clean-checkout validation evidence
- Validator regression-suite evidence
- Automatic release-branch CI evidence
- Protected-branch configuration evidence
- Debug APK metadata and digest
- Final release-gate report
- Proposed pull-request title and body
- Proposed annotated-tag command and message
- Proposed GitHub release title and Markdown body
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.

### Exact or bounded path scope

The pre-release validation and CI evidence, the protected-branch configuration evidence, the APK metadata, the final release-gate report, the proposed pull-request and release assets, and the Phase experiment record.

### Required behavior

- The complete local validation suite, including the validator regression suite, passes from a clean checkout.
- The release gate prints `release_gate=SATISFIED`.
- The push to `release/v0.1.1` automatically triggers CI; the `validate` job passes; the debug APK is produced; the APK reports `versionCode=2` and `versionName=0.1.1`; source and merged manifests satisfy the approved allowlists.
- No product functionality or permissions are introduced.
- No stale current-facing v0.1.0 branch or capability claim remains.
- `main` protection requires the stable `validate` check.
- Wrapper and distribution integrity checks pass.
- The dependency-update configuration is present and review-only.
- The branch contains no tracked build output, bytecode, screenshots, private material, or unintended files.
- The release branch is clean and ready for the one final pull request.

### Boundaries and exclusions

- Phase 7 does not open or merge the pull request, commit directly to `main`, create the tag, publish the release, or delete the release branch. These are post-merge release-completion actions.

### Required validation

- All previous phases are `Complete`.
- The validator regression suite passes.
- The complete local repository gate passes.
- The release gate prints `release_gate=SATISFIED`.
- Validation leaves the clean checkout clean.
- CI ran automatically on `release/v0.1.1`.
- The `validate` job passed.
- The debug APK was produced.
- The APK reports `versionCode=2` and `versionName=0.1.1`.
- Source and merged manifests satisfy the approved allowlists.
- No product functionality or permissions were introduced.
- No stale current-facing v0.1.0 branch or capability claim remains.
- `main` protection requires the stable `validate` check.
- Wrapper and distribution integrity checks pass.
- The dependency-update configuration is present and review-only.
- The branch contains no tracked build output, bytecode, screenshots, private material, or unintended files.
- The release branch is clean and ready for the one final pull request.

### Completion evidence

- All mandatory pre-release gates pass.
- Phase experiment record; ID assigned when the task starts according to the experiment protocol.
- The maintainer accepts the release-gate report.
- The branch is ready for the single pull request into `main`.

### Status

Planned

### Validation checklist

- [ ] BLOCKED — Every previous phase is `Complete`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The validator regression suite passes. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The complete local repository gate passes. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The release gate prints `release_gate=SATISFIED`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Validation leaves the clean checkout clean. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — CI ran automatically on `release/v0.1.1`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The `validate` job passed. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The debug APK was produced. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The APK reports `versionCode=2` and `versionName=0.1.1`. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Source and merged manifests satisfy the approved allowlists. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — No product functionality or permissions were introduced. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — No stale current-facing v0.1.0 branch or capability claim remains. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — `main` protection requires the stable `validate` check. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Wrapper and distribution integrity checks pass. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The dependency-update configuration is present and review-only. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The branch contains no tracked build output, bytecode, screenshots, private material, or unintended files. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The release branch is clean and ready for the one final pull request. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — The pull request has not been opened; the tag has not been created; the release has not been published; the branch has not been deleted. The phase has not started; direct completion evidence is not yet available.
- [ ] BLOCKED — Phase experiment record; ID assigned when the task starts according to the experiment protocol. The phase has not started; direct completion evidence is not yet available.

## Cross-references

- [Release charter](release-charter.md)
- [Active AGENTS.md](../../../AGENTS.md)
- [Experiment protocol](../../agentic-development/experiment-protocol.md)
- [Evaluation template](../../agentic-development/evaluation-template.md)
- [OpenCode governance companion](../../agentic-development/opencode-governance.md)
- [v0.1.0 release charter (historical evidence)](../v0.1.0/release-charter.md)
- [v0.1.0 phase list (historical evidence)](../v0.1.0/phase-list.md)
