# Phase List — NudgeWhen v0.1.2

**Document status:** Accepted — Phases 0 through 1 complete; Phase 2 current; Phases 2 through 7 Planned.
**Active release branch:** release/v0.1.2
**Active release charter:** docs/releases/v0.1.2/release-charter.md

## Release-wide sequencing rules

- All v0.1.2 work occurs on `release/v0.1.2`; no parallel release branch.
- All phases remain on the same branch.
- A later phase may refine an earlier current-release document only through explicitly scoped work.
- Exactly one release-bearing pull request is opened into `main` after all eight phases and the full pre-release gate are complete.
- Each phase transitions from `Planned` to `Complete` only after accepted completion evidence and maintainer review.
- Staging, commits, pushes, pull requests, tags, and releases each require separate explicit maintainer authorization.
- Phase 7 is pre-release only. Merge, merged-main validation/CI, the annotated tag, and the published GitHub release are separate release-completion actions.
- Every phase, subphase, and Build report uses the mandatory four-state validation checklist contract.

## Phase 0 — Release Definition & Bootstrap

### Objective

Establish the v0.1.2 release definition and active-release synchronization without implementing reminder or persistence functionality.

### Principal deliverables

- Recognition of the accepted Candidate A release-neutral product_scope validator bootstrap.
- Recognition of the accepted Candidate A evidence in `EXP-0034`.
- v0.1.2 release charter at `docs/releases/v0.1.2/release-charter.md`.
- This v0.1.2 phase list at `docs/releases/v0.1.2/phase-list.md`.
- `scripts/release_contract.json` transition to v0.1.2.
- `AGENTS.md` current-release synchronization to v0.1.2.
- `README.md` current-release synchronization to v0.1.2.
- Cumulative Candidate B experiment evidence under `EXP-0035`.
- Repository-consistency evidence sufficient to terminate the temporary v0.1.2 bootstrap exception.

Candidate A is already complete. Candidate B synchronization is accepted,
its repository boundary is closed, cumulative `EXP-0035` evidence exists,
and the temporary v0.1.2 bootstrap exception is `TERMINATED`. Phase 0
remains formally `Planned` pending the separately authorized formal closure
transition.

### Exact or bounded path scope

Phase 0 consists of the already accepted Candidate A work plus the accepted
Candidate B active-release synchronization. Candidate A remains separately
accepted and is not reopened by this phase-list declaration.

The final Candidate B path set is exactly:

- `scripts/release_contract.json`
- `docs/releases/v0.1.2/release-charter.md`
- `docs/releases/v0.1.2/phase-list.md`
- `AGENTS.md`
- `README.md`
- `docs/agentic-development/experiments/EXP-0035.md`

This list documents Candidate B scope only; it is not a complete enumeration
of all earlier Phase 0 work and does not itself authorize any modification.

### Required behavior

- Recognize Candidate A completion as already established and not re-performed.
- Accept the v0.1.2 release charter and phase list as Candidate-B deliverables.
- Synchronize the active-release context in `AGENTS.md` and `README.md` to v0.1.2.
- Transition `scripts/release_contract.json` to v0.1.2.
- Record cumulative Candidate B experiment evidence under `EXP-0035`.
- Produce repository-consistency evidence that terminates the temporary v0.1.2 bootstrap exception.

### Boundaries and exclusions

- No reminder-domain implementation.
- No persistence implementation.
- No Android manifest, component, or permission change.
- No network or external lookup.
- No dependency or toolchain change.
- No branch, tag, or release publication.
- No modification of historical v0.1.1 release documents.
- No premature claim that Candidate B is complete before its evidence is accepted.

### Required validation

- Validated local baseline on `release/v0.1.2` at the accepted starting commit.
- Working-tree baseline matches the authorized untracked-state exactly before each Phase 0 Build slice.
- Cached/index state remains empty throughout Phase 0 Build slices.
- No agent-initiated network commands, dependency installation, or external lookups.
- No private working material is opened, modified, staged, or committed.

### Completion evidence

- Accepted Candidate B synchronization across the final Candidate B path set.
- Accepted cumulative `EXP-0035` evidence covering Candidate B planning,
  maintainer corrections, Build and corrective stages, validation, and
  repository-action chronology.
- Candidate A remains separately recorded in `EXP-0034`.
- Accepted repository-consistency proof that terminates the temporary v0.1.2 bootstrap exception.
- Accepted maintainer review marking Phase 0 `Complete`.

### Status

Complete

### Validation checklist

- [x] PASS — The maintainer-authorized formal Phase 0 closure transition is applied after accepted Candidate B synchronization, repository-consistency evidence, cumulative `EXP-0035` evidence, and bootstrap-exception termination; Phase 0 status is `Complete`.
- [x] PASS — Accepted Candidate B synchronization and repository-consistency evidence terminated the temporary v0.1.2 bootstrap exception, and cumulative `EXP-0035` evidence exists.

## Phase 1 — Reminder Architecture Contract

### Objective

Freeze the minimal reminder lifecycle and architecture before any product implementation.

### Principal deliverables

- Reminder domain model selection from evidence.
- Textual reminder creation contract.
- Display/list contract.
- Exact lifecycle-ending action semantics, selecting completion versus removal or another explicitly selected minimal semantic.
- Persistence abstraction and ownership boundary.
- Persistence technology choice.
- Restore-after-restart behavior contract.
- Repository/package/file ownership boundaries.
- Test boundaries.
- Integration boundary with the existing Compose application.

### Exact or bounded path scope

Phase 1 path scope is not pre-authorized here. Concrete Phase 1 paths will be enumerated when a Phase 1 Build authorization is issued. Candidate B does not authorize any Phase 1 path.

### Required behavior

- Select the minimal reminder lifecycle semantics from evidence rather than from inference.
- Select the persistence technology only from evidence; persistence is not frozen in Phase 0.
- Define the integration boundary with the existing Compose application explicitly.
- Establish the restore-after-restart behavior contract explicitly.
- Establish repository/package/file ownership boundaries explicitly.
- Establish test boundaries explicitly.

### Boundaries and exclusions

- Phase 1 is architecture-only. Reminder-domain, persistence, and UI
  implementation belong to later phases under their own explicit
  authorizations after the Phase 1 architecture contract is accepted.
- No voice or speech input or output.
- No notifications.
- No time scheduling or alarms.
- No location or geofencing.
- No contextual or device-state triggers.
- No background behavior.
- No networking or sync.
- No new Android permissions or components.

### Required validation

- Architecture decisions are traceable to direct evidence, not inference.
- No premature product code is introduced.
- No persistence technology is frozen in Phase 0; Phase 1 selects it only from evidence.
- Frozen release non-goals remain excluded.

### Completion evidence

- Accepted Phase 1 architecture contract.
- Accepted Phase 1 experiment evidence.
- Accepted maintainer review marking Phase 1 `Complete`.

### Status

Complete

### Validation checklist

- [x] PASS — The Phase 1 architecture contract at `docs/releases/v0.1.2/reminder-architecture.md` and the Phase 1 experiment evidence `EXP-0036` were accepted.
- [x] PASS — The Phase 1 architecture candidate passed staged validation (98 tests / OK; required group 11/0/0; docs group 11/0/0; skip-Android integrated 22/0/0).
- [x] PASS — Architecture commit `ca322ac75ff66fe545d3d0ca1709d2fa1b0f6648` was pushed to `origin/release/v0.1.2`.
- [x] PASS — Exact-head architecture CI run `32665472700` (workflow `CI`, event `push`, branch `release/v0.1.2`, head SHA `ca322ac75ff66fe545d3d0ca1709d2fa1b0f6648`, conclusion `success`, validate job `success`) completed successfully.
- [x] PASS — The formal Phase 1 closure synchronization marks Phase 1 `Complete`; Phase 2 is now the current lifecycle phase and remains `Planned`.

## Phase 2 — Reminder Domain Core

### Objective

Implement the deterministic reminder-domain core established by Phase 1.

### Principal deliverables

- Reminder model and domain state.
- Lifecycle-ending domain behavior selected in Phase 1.
- Deterministic unit tests for the domain core.
- Any domain-integration contract necessary for the eventual persistence and UI integration, without crossing into persistence or UI implementation.

### Exact or bounded path scope

Phase 2 path scope is not pre-authorized here. Concrete Phase 2 paths will be enumerated when a Phase 2 Build authorization is issued. Candidate B does not authorize any Phase 2 path.

### Required behavior

- Implement the Phase 1 domain model and lifecycle-ending behavior deterministically.
- Cover the domain core with deterministic unit tests.
- Keep the domain core free of Android-framework ownership unless the accepted architecture explicitly requires it.

### Boundaries and exclusions

- No persistence implementation except interfaces or boundaries explicitly established by Phase 1.
- No UI implementation except contracts necessary for domain integration.
- No voice, notifications, time scheduling, location, contextual triggers, background behavior, networking, or sync.
- No new Android permissions or components.

### Required validation

- Deterministic unit-test pass for the domain core.
- No Android-framework dependency introduced without accepted architectural justification.
- Frozen release non-goals remain excluded.

### Completion evidence

- Accepted Phase 2 domain-core implementation.
- Accepted Phase 2 deterministic unit-test evidence.
- Accepted Phase 2 experiment evidence.
- Accepted maintainer review marking Phase 2 `Complete`.

### Status

Planned

### Validation checklist

- [-] NOT APPLICABLE — Phase execution and completion evidence have not yet been performed; phase status remains `Planned`.

## Phase 3 — Local Persistence

### Objective

Implement the accepted local on-device persistence architecture and prove restore-after-restart semantics at the persistence and domain boundary.

### Principal deliverables

- The selected local persistence implementation.
- Mapping, serialization, and storage logic required by the accepted architecture.
- Deterministic persistence tests.
- Repository or store integration with the domain core from Phase 2.

### Exact or bounded path scope

Phase 3 path scope is not pre-authorized here. Concrete Phase 3 paths will be enumerated when a Phase 3 Build authorization is issued. Candidate B does not authorize any Phase 3 path.

### Required behavior

- Implement the persistence layer selected by Phase 1.
- Prove restore-after-restart behavior at the persistence and domain boundary.
- Integrate the repository or store with the Phase 2 domain core deterministically.

### Boundaries and exclusions

- No networking or sync.
- No background scheduling.
- No additional Android activity, service, receiver, provider, or Android
  permission; these remain explicit v0.1.2 non-goals, and an ordinary
  Phase 3 authorization cannot waive this frozen release boundary.
- No expansion into notification, location, or contextual behavior.
- No voice or speech.

### Required validation

- Deterministic persistence-test pass.
- Restore-after-restart behavior demonstrated at the persistence and domain boundary.
- Manifest, component, and permission boundary remains satisfied.
- Frozen release non-goals remain excluded.

### Completion evidence

- Accepted Phase 3 persistence implementation.
- Accepted Phase 3 restore-after-restart evidence.
- Accepted Phase 3 experiment evidence.
- Accepted maintainer review marking Phase 3 `Complete`.

### Status

Planned

### Validation checklist

- [-] NOT APPLICABLE — Phase execution and completion evidence have not yet been performed; phase status remains `Planned`.

## Phase 4 — Minimal Android Reminder UI

### Objective

Integrate the accepted reminder domain and persistence behavior into the existing single-activity Compose application.

### Principal deliverables

- Create-textual-reminder user flow.
- Display-existing-reminders user flow.
- Selected minimal lifecycle-ending user action.
- Restored reminders appearing after application restart as defined by the accepted architecture.

### Exact or bounded path scope

Phase 4 path scope is not pre-authorized here. Concrete Phase 4 paths will be enumerated when a Phase 4 Build authorization is issued. Candidate B does not authorize any Phase 4 path.

### Required behavior

- Stay inside the existing single-activity Compose boundary.
- Wire the Phase 2 domain core and Phase 3 persistence into the existing Compose UI.
- Honor the restore-after-restart contract selected in Phase 1.

### Boundaries and exclusions

- Existing single-activity boundary only; no additional Android Activity.
  Internal Compose screen/navigation structure is not frozen by this phase
  list and remains subject to the accepted architecture.
- No new Android permission.
- No services, receivers, or providers.
- No notifications.
- No voice.
- No location.
- No time scheduling.
- No networking.
- No contextual or device-state trigger.

### Required validation

- UI integration exercises create, display, and lifecycle-ending behavior.
- Restored reminders appear after application restart as defined by the accepted architecture.
- Manifest, component, and permission boundary remains satisfied.
- Frozen release non-goals remain excluded.

### Completion evidence

- Accepted Phase 4 minimal UI implementation.
- Accepted Phase 4 UI integration evidence.
- Accepted Phase 4 experiment evidence.
- Accepted maintainer review marking Phase 4 `Complete`.

### Status

Planned

### Validation checklist

- [-] NOT APPLICABLE — Phase execution and completion evidence have not yet been performed; phase status remains `Planned`.

## Phase 5 — Integration & Device Validation

### Objective

Prove the complete local reminder lifecycle through integrated local validation and physical-device or otherwise explicitly accepted Android evidence.

### Principal deliverables

- Regression tests covering the integrated behavior.
- Domain and persistence test results.
- Android build, lint, and artifact validation results.
- Manifest, component, and permission boundary confirmation.
- Create, display, and lifecycle-ending behavior evidence.
- Persistence and restart-restoration evidence.
- Release metadata alignment required for the eventual v0.1.2 artifact when separately authorized.

### Exact or bounded path scope

Phase 5 path scope is not pre-authorized here. Concrete Phase 5 paths will be enumerated when a Phase 5 Build authorization is issued. Candidate B does not authorize any Phase 5 path. `app/build.gradle.kts` is not modified by Candidate B.

### Required behavior

- Run the full local validation surface and the full Android validation surface.
- Prove the integrated local reminder lifecycle end-to-end on the accepted device or Android evidence channel.
- Surface the eventual v0.1.2 artifact target identity `versionCode = 3`, `versionName = "0.1.2"`, without claiming it has already been delivered. The current Android artifact identity remains `versionCode = 2`, `versionName = "0.1.1"`.

### Boundaries and exclusions

- No Android metadata change in Candidate B.
- No networking or sync.
- No background scheduling.
- No new Android permission or component.
- No notifications, voice, location, time scheduling, or contextual triggers.

### Required validation

- Complete regression suite passes.
- Android build, lint, and artifact validation passes.
- Manifest, component, and permission boundary remains satisfied.
- Restore-after-restart behavior validated end-to-end.
- Frozen release non-goals remain excluded.

### Completion evidence

- Accepted Phase 5 integrated validation results.
- Accepted Phase 5 device or accepted Android evidence.
- Accepted Phase 5 experiment evidence.
- Accepted maintainer review marking Phase 5 `Complete`.

### Status

Planned

### Validation checklist

- [-] NOT APPLICABLE — Phase execution and completion evidence have not yet been performed; phase status remains `Planned`.

## Phase 6 — Integrated Audit & Agent Evaluation

### Objective

Audit the integrated v0.1.2 result, evaluate Candidate A and Candidate B and any later agent-assisted work, reconcile experiment evidence, and determine whether the release objectives and non-goals are actually respected.

### Principal deliverables

- Updated release-specific agent evaluation.
- Synchronized release documents.
- Accepted experiment evidence for completed work.
- Explicit MiniMax lesson recurrence and disposition.
- Explicit disposition of any new governance or tooling candidate arising from v0.1.2 evidence.

### Exact or bounded path scope

Phase 6 path scope is not pre-authorized here. Concrete Phase 6 paths will be enumerated when a Phase 6 Build authorization is issued. Candidate B does not authorize any Phase 6 path.

### Required behavior

- Re-examine the integrated release against the frozen release objectives and non-goals.
- Reconcile experiment evidence across completed phases.
- Evaluate Candidate A and Candidate B and any later agent-assisted work.
- Surface any new governance or tooling candidate explicitly, rather than introducing it by default.

### Boundaries and exclusions

- Hermes, MCP, helper, plugin, or runtime-guard integration is not introduced merely because it is available; any such change requires independent evidence and explicit scope.
- No Android metadata change in Phase 6 unless separately authorized.
- No networking, sync, background scheduling, notifications, voice, location, time scheduling, or contextual triggers.

### Required validation

- Audit conclusions are traceable to direct evidence.
- Any new governance or tooling candidate is justified against direct evidence and explicit scope.
- Frozen release non-goals remain excluded.

### Completion evidence

- Accepted Phase 6 audit and agent-evaluation report.
- Accepted synchronized release documents.
- Accepted experiment reconciliation.
- Accepted maintainer review marking Phase 6 `Complete`.

### Status

Planned

### Validation checklist

- [-] NOT APPLICABLE — Phase execution and completion evidence have not yet been performed; phase status remains `Planned`.

## Phase 7 — Full Pre-Release Gate

### Objective

Run the complete clean v0.1.2 pre-release gate and prepare the single release-bearing pull request and the later release-completion actions.

### Principal deliverables

- Every prior phase marked `Complete`.
- Complete validator regression suite passing.
- Complete clean local release gate passing with `release_gate=SATISFIED`.
- Clean validated candidate on the release branch.
- Exact-head release-branch CI success.
- Stable `validate` job success.
- Android artifact matching the accepted target identity
  `versionCode = 3`, `versionName = "0.1.2"` by the final gate. Delivery of
  that target metadata may occur in an earlier separately authorized phase.
- Confirmation that the single-activity, no-new-permission, and component boundary remains satisfied.
- No unaccounted tracked output; private working material is not opened,
  tracked, staged, or committed. Ignored private local working material is
  not required to be physically absent.
- Prepared release pull request title, body, and later tag and release proposals.

### Exact or bounded path scope

Phase 7 path scope is not pre-authorized here. Concrete Phase 7 paths will be enumerated when a Phase 7 Build authorization is issued. Candidate B does not authorize any Phase 7 path.

### Required behavior

- Run the full pre-release gate on a clean working tree at the exact Phase 7 starting commit.
- Surface the final pre-release evidence without crossing into release-completion repository actions.
- Prepare, but do not execute, the single release-bearing pull request and the later tag and release proposals.

### Boundaries and exclusions

- Phase 7 must not merge the release pull request.
- Phase 7 must not create or publish the annotated tag.
- Phase 7 must not publish the GitHub release.
- Phase 7 must not delete the release branch.
- Those actions are separate later repository actions.
- Phase 7 does not itself require an Android metadata mutation. If the
  accepted target identity was not delivered earlier, any metadata change
  remains a separate explicitly authorized operation.
- No networking, sync, background scheduling, notifications, voice, location, time scheduling, or contextual triggers.

### Required validation

- Clean working tree at the Phase 7 starting commit.
- Complete validator regression suite passes.
- Complete clean local release gate passes with `release_gate=SATISFIED`.
- Exact-head release-branch CI run is successful.
- Stable `validate` job is successful.
- Android artifact, when produced, matches the accepted target identity.
- Manifest, component, and permission boundary remains satisfied.
- No unaccounted tracked output is present, and no private working material
  is opened, tracked, staged, or committed.
- Frozen release non-goals remain excluded.

### Completion evidence

- Accepted Phase 7 pre-release gate results.
- Accepted Phase 7 prepared release-PR title/body and later
  release-completion proposals; the release pull request itself remains
  unopened during Phase 7.
- Accepted Phase 7 experiment evidence.
- Accepted maintainer review marking Phase 7 `Complete`.

### Status

Planned

### Validation checklist

- [-] NOT APPLICABLE — Phase execution and completion evidence have not yet been performed; phase status remains `Planned`.

## Cross-references

- [Release charter](release-charter.md)
- [Active AGENTS.md](../../../AGENTS.md)
- [Experiment protocol](../../agentic-development/experiment-protocol.md)
- [Evaluation template](../../agentic-development/evaluation-template.md)
- [OpenCode governance companion](../../agentic-development/opencode-governance.md)
- [v0.1.1 release charter (historical evidence)](../v0.1.1/release-charter.md)
- [v0.1.1 phase list (historical evidence)](../v0.1.1/phase-list.md)
