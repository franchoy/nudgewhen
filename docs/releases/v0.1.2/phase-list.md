# Phase List — NudgeWhen v0.1.2

**Document status:** Accepted — Phases 0 through 6 complete; Phase 7 current; Phase 7 Planned.
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

Complete

### Validation checklist

- [x] PASS — Accepted Phase 2 domain core: commit `6781bccacb5324dde854a5001a939754bb309165`, parent `c1dc3a5c94cf4116cf81d4b404694e3e4bf28a7a`, subject `feat: add reminder domain core` directly modified the Phase 2 reminder-domain paths on `release/v0.1.2`.
- [x] PASS — Accepted Phase 2 domain-core evidence: `Reminder`, `ReminderStore`, `ReminderController`; JUnit 4.13.2 selected as the Phase 2 test-only dependency; 2 `Reminder` tests; 25 `ReminderController` tests; 27 JVM tests total; 0 skipped; 0 failures; 0 errors.
- [x] PASS — Domain-core exact-head CI run `32708073861` (workflow `CI`, event `push`, branch `release/v0.1.2`, head SHA `6781bccacb5324dde854a5001a939754bb309165`, conclusion `success`) completed successfully.
- [x] PASS — Accepted validator integration: commit `ba6a581f00ad2d5d4f550f95e6ccfa5da716825f`, parent `6781bccacb5324dde854a5001a939754bb309165`, subject `test: integrate reminder JVM tests into validator`. The existing `android` validation group was retained; no new validation group was added; the `android/jvm-tests` check executes the separate Gradle task `:app:testDebugUnitTest` in the order `gradle-projects -> jvm-tests -> gradle-build`; a JVM failure short-circuits the later build/APK/manifest checks.
- [x] PASS — Validator exact-head CI run `32711898852` (workflow `CI`, event `push`, branch `release/v0.1.2`, head SHA `ba6a581f00ad2d5d4f550f95e6ccfa5da716825f`, conclusion `success`) completed successfully.
- [x] PASS — Accepted validator evidence: Python validator regression `100 tests / OK`; required group `11/0/0`; docs group `11/0/0`; android offline group `17/0/0`; `release_gate=NOT_SATISFIED`.
- [x] PASS — Formal Phase 2 closure synchronization: Phase 2 is `Complete`; Phase 3 — Local Persistence — is the current lifecycle phase and remains `Planned`; Phase 3 implementation has not started.

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

Complete

### Validation checklist

- [x] PASS — Phase 3 implementation commit `c3eb1b580b744111ed3024cfbd58a8ce3113ad35`, parent `31f9e255b0b3be56c08fb6c4bd4bf13271463d2b`, subject `feat: add local reminder persistence`, delivered exactly `FileReminderStore.kt` and `FileReminderStoreTest.kt`.
- [x] PASS — The Phase 3 persistence implementation delivers the frozen FileReminderStore contract and 29 deterministic persistence tests `P3_01` through `P3_29`; combined JVM evidence is `56 tests / 0 failures / 0 errors / 0 skipped`.
- [x] PASS — Accepted retained validation is Python validator `100 tests / OK`, required `11/0/0`, docs `11/0/0`, android offline `17/0/0`, and `release_gate=NOT_SATISFIED`.
- [x] PASS — Exact-head implementation CI run `32720528488` on `release/v0.1.2` at `c3eb1b580b744111ed3024cfbd58a8ce3113ad35` completed successfully.
- [x] PASS — Phase 3B-R1 corrected only the false CR/UTF-8 source comment; executable persistence semantics and tests were unchanged.
- [x] PASS — This formal closure candidate marks Phase 3 `Complete` and advances Phase 4 — Minimal Android Reminder UI — to the current lifecycle phase while Phase 4 remains `Planned`; Phase 4 implementation has not started.

## Phase 4 — Minimal Android Reminder UI

### Objective

Integrate the accepted reminder domain and persistence behavior into the existing single-activity Compose application.

### Principal deliverables

- Create-textual-reminder user flow.
- Display-existing-reminders user flow.
- Selected minimal lifecycle-ending user action.
- Source-level startup-restoration integration from `MainActivity` through `FileReminderStore` / `ReminderController` to the visible reminder state; physical-device/end-to-end restart proof remains Phase 5 ownership.

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

- Source-level UI integration establishes the textual create, display/list, and permanent-remove flows against the accepted domain and persistence contracts.
- Source-level startup-restoration integration is established through `MainActivity -> filesDir -> FileReminderStore -> ReminderController -> ReminderScreen`.
- Android build/lint/source/merged-manifest validation remains accepted for the Phase 4 structural integration boundary.
- Physical-device/end-to-end create/list/remove and restart-restoration evidence is explicitly deferred to Phase 5.
- Manifest, component, and permission boundary remains satisfied.
- Frozen release non-goals remain excluded.

### Completion evidence

- Accepted Phase 4 minimal UI implementation.
- Accepted Phase 4 UI integration evidence.
- Accepted Phase 4 experiment evidence.
- Accepted maintainer review marking Phase 4 `Complete`.

### Status

Complete

### Validation checklist

- [x] PASS — Phase 4A planning/audit accepted with maintainer refinements; no repository mutation was performed by the audit.
- [x] PASS — Phase 4B `ReminderScreen` implementation accepted; Android validation `17 / 0 / 0`; `release_gate=NOT_SATISFIED`.
- [x] PASS — Phase 4C `MainActivity` integration accepted; Android validation `17 / 0 / 0`; tracked `git diff --check` `PASS`.
- [x] PASS — Phase 4D integration audit accepted with `BLOCKING_DEFECTS: NONE` and candidate `VALIDATED_FOR_STAGING`.
- [x] PASS — Maintainer staged exactly the two implementation paths; `git diff --cached --check` produced no output; staged proof is `M app/src/main/kotlin/io/github/franchoy/nudgewhen/MainActivity.kt` and `A app/src/main/kotlin/io/github/franchoy/nudgewhen/ui/ReminderScreen.kt`.
- [x] PASS — Phase 4 implementation commit `05503d58416e287afd96cc1fc7c6f78df8fd2784`, parent `1e612d5c43c740f5aabfc4825992fce8ae8c7e9e`, subject `feat: add minimal reminder UI` on `release/v0.1.2`.
- [x] PASS — Exact-head implementation CI run `32739280349` (workflow `CI`, event `push`, branch `release/v0.1.2`, head `05503d58416e287afd96cc1fc7c6f78df8fd2784`, conclusion `success`, required `validate` job `success`) completed successfully.
- [x] PASS — This formal closure candidate marks Phase 4 `Complete` and advances Phase 5 — Integration & Device Validation — to the current lifecycle phase while Phase 5 remains `Planned` and implementation `NOT_STARTED`.
- [x] PASS — Physical-device/end-to-end restart evidence is NOT claimed here and remains Phase 5 ownership.

## Phase 5 — Integration & Device Validation

Phase 5 is `Complete`. Phase 5B Android artifact identity alignment is
landed (historical). Phase 5C exact-head integrated local validation is
accepted. Phase 5D-R8 one-device runtime acceptance is accepted on one
physical `PA2310GBB` running Android 13 (`ONE_PHYSICAL_DEVICE_ONLY`).

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
- Surface the eventual v0.1.2 artifact target identity `versionCode = 3`, `versionName = "0.1.2"`. The landed Phase 5B commit `6b16a294b3d13151baf23a239e4cf0d330a27d3e` (subject `chore: align v0.1.2 artifact identity`) delivers this identity: `app/build.gradle.kts` records `versionCode = 3`, `versionName = "0.1.2"`, and `scripts/release_contract.json` records `android.current_version_code = 3`, `android.current_version_name = "0.1.2"`. Historical Phase 0 statement (preserved): at Phase 0, the current Android artifact identity was `versionCode = 2`, `versionName = "0.1.1"`, and the target identity was not yet delivered.

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

Complete

### Phase 5B — Android artifact identity alignment (landed — historical)

PHASE_5B_ANDROID_IDENTITY_ALIGNMENT:
LANDED

The Phase 5B Android artifact identity alignment is landed in source. This is a maintainer-selected phase sequencing decision: deliver the target identity before Phase 5 device evidence, not a release-document mandate. This is recorded here as historical Phase 5B landing evidence; the current Phase 5 completion state is recorded above.

- Commit: `6b16a294b3d13151baf23a239e4cf0d330a27d3e`.
- Parent: `ed9ad96bebca79bf0f361ce165c133bde490a61b`.
- Subject: `chore: align v0.1.2 artifact identity`.
- Commit path set: exactly six paths — `app/build.gradle.kts`, `docs/agentic-development/experiments/EXP-0040.md`, `docs/releases/v0.1.2/phase-list.md`, `docs/releases/v0.1.2/release-charter.md`, `scripts/release_contract.json`, `tests/test_validator_repository.py`.
- Push: `PASS`.
- Remote exact SHA: `6b16a294b3d13151baf23a239e4cf0d330a27d3e`.
- Exact-head CI run: `32756426800` (workflow `CI`, event `push`, branch `release/v0.1.2`, head `6b16a294b3d13151baf23a239e4cf0d330a27d3e`, conclusion `success`, required `validate` job `success`).
- Debug APK: produced.
- Android identity delivered: `versionCode = 3`, `versionName = "0.1.2"` (identity `3 / 0.1.2`).
- `app/build.gradle.kts`: `versionCode = 3`, `versionName = "0.1.2"`.
- `scripts/release_contract.json`: `android.current_version_code = 3`, `android.current_version_name = "0.1.2"`. Target identity (`target_version_code = 3`, `target_version_name = "0.1.2"`) is unchanged and is now identical to the current identity.

At the time of the Phase 5B landing, the following state applied and is preserved here as historical evidence:

- Phase 5 was the current lifecycle phase and remained `Planned`.
- Integrated Phase 5 validation and device validation were not yet complete.
- Phase 5 device/runtime evidence had not yet occurred (`NOT_YET_PERFORMED`).
- Phase 6 — Integrated Audit & Agent Evaluation — remained `Planned`.
- Phase 7 — Full Pre-Release Gate — remained `Planned`.
- Phase 5 was **not** marked `Complete` by the Phase 5B landing.

The active document-status completed range at the time of the Phase 5B landing was `Phases 0 through 4 complete`; Phase 5 was still `Planned`.

### Phase 5C — exact-head integrated local validation

Phase 5C exact-head integrated local validation is accepted.

- Validated HEAD: `e6a10bde87aa5841c5669d91512d7040089b100a`.
- Branch: `release/v0.1.2`.
- Android identity: `versionCode = 3`, `versionName = "0.1.2"`.
- Python validator suites: `Ran 100 tests`, `OK`.
- `required` group: `SUMMARY pass=11 fail=0 skip=0`.
- `docs` group: `SUMMARY pass=11 fail=0 skip=0`.
- Full offline: `SUMMARY pass=39 fail=0 skip=0`; `release_gate=SATISFIED`.
- Final repository proof at Phase 5C acceptance: HEAD `e6a10bde87aa5841c5669d91512d7040089b100a`; worktree clean; index empty; tracked `git diff --check` produced no output.
- The OpenCode tool did not directly surface a numeric Python command exit status; the unittest `OK` output is the accepted success evidence.

### Phase 5D — physical-device runtime acceptance

Phase 5D one-device runtime acceptance is accepted as R8 on one physical device.

- Accepted attempt: `Phase 5D-R8`.
- Branch: `release/v0.1.2`.
- HEAD: `e6a10bde87aa5841c5669d91512d7040089b100a`.
- Device model: `PA2310GBB`.
- Android version: `13`.
- Evidence scope: `ONE_PHYSICAL_DEVICE_ONLY`.
- Pre-reinstall installed identity: `versionCode=3`, `versionName=0.1.2`.
- Installation method: `adb install -r app/build/outputs/apk/debug/app-debug.apk` → `Success`.
- Post-reinstall installed identity: `versionCode=3`, `versionName=0.1.2`.
- Clean-first-launch setup: `adb shell pm clear io.github.franchoy.nudgewhen` → `Success`.

Runtime checkpoints P5-01 through P5-07: `PASS`.

P5-08: `DEVICE_PROOF_NOT_REQUIRED`. Retained deterministic Phase 3 JVM persistence evidence already covers malformed-file rejection; device-side malformed persistence injection and detailed recovery UX are outside the v0.1.2 Phase 5 acceptance contract.

The Phase 5D device evidence is scoped to `PA2310GBB / Android 13` and `ONE_PHYSICAL_DEVICE_ONLY`. It is **not** a general Android compatibility statement. It is **not** a production-readiness statement.

### Validation checklist

- [x] PASS — Phase 5B Android artifact identity alignment landed (commit `6b16a294b3d13151baf23a239e4cf0d330a27d3e`, exact-head CI `32756426800`, conclusion `success`); Android identity delivered as `versionCode = 3`, `versionName = "0.1.2"`.
- [x] PASS — Phase 5C exact-head integrated local validation accepted at HEAD `e6a10bde87aa5841c5669d91512d7040089b100a` (Python validator `Ran 100 tests / OK`; required `11/0/0`; docs `11/0/0`; full offline `39/0/0`; `release_gate=SATISFIED`; tracked `git diff --check` produced no output; final repository proof clean at HEAD).
- [x] PASS — Phase 5D-R8 one-device runtime acceptance accepted on one physical `PA2310GBB` running Android 13 (`ONE_PHYSICAL_DEVICE_ONLY`); runtime checkpoints P5-01 through P5-07 `PASS`; P5-08 `DEVICE_PROOF_NOT_REQUIRED`; Android identity `3 / 0.1.2` preserved pre- and post-reinstall.
- [x] PASS — Cumulative Phase 5 experiment evidence recorded in `EXP-0040`; historical Phase 5 chronology preserved including Phase 5C blocked attempts and Phase 5D blocked attempts through R7 before the accepted R8 run.
- [x] PASS — This formal Phase 5 closure candidate marks Phase 5 `Complete` and advances Phase 6 — Integrated Audit & Agent Evaluation — to the current lifecycle phase while Phase 6 remains `Planned`; Phase 6 implementation has not started.
- [x] PASS — The v0.1.2 release is **not** claimed ready, merged, tagged, or published by this Phase 5 closure.

## Phase 6 — Integrated Audit & Agent Evaluation

Phase 6 is `Complete`. Phase 6F, Phase 6G, and Phase 6H-A are each
`ACCEPTED_WITH_CORRECTION; COMPLETE`. Phase 6H-B1 is the current
core-tracked lifecycle-transition candidate; Phase 6H closure acceptance
remains a later separately authorized operation.

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

Complete

### Phase 6 closure summary

Phase 6 is `Complete`. The accepted Phase 6 completion evidence is:

- Phase 6F: `ACCEPTED_WITH_CORRECTION; COMPLETE`.
- Phase 6G: `ACCEPTED_WITH_CORRECTION; COMPLETE`.
- Phase 6H-A: `ACCEPTED_WITH_CORRECTION; COMPLETE`.
- C3 retained integrated validation: Python validator `Ran 100 tests / OK`; `required` `SUMMARY pass=11 fail=0 skip=0`; `docs` `SUMMARY pass=11 fail=0 skip=0`; `android offline` `SUMMARY pass=17 fail=0 skip=0`; `full offline` `SUMMARY pass=39 fail=0 skip=0`; `release_gate=SATISFIED`.
- Dependabot six pull requests #3, #4, #6, #7, #8, #9 are `CLOSED` and `UNMERGED`. Evidence class: `MAINTAINER-SUPPLIED DECISION/OBSERVATION`.
- `SUBSTANTIVE_BLOCKER_COUNT`: `0`.

Phase 7 is `Planned` and is the `next lifecycle phase`. Phase 7 is `NOT started` and is `NOT authorized by this synchronization`. The v0.1.2 release is **not** claimed ready, merged, tagged, or published by this Phase 6 closure candidate.

### Validation checklist

- [x] PASS — Phase 6F, Phase 6G, and Phase 6H-A are each `ACCEPTED_WITH_CORRECTION; COMPLETE`.
- [x] PASS — C3 retained integrated validation: Python validator `Ran 100 tests / OK`; `required` `SUMMARY pass=11 fail=0 skip=0`; `docs` `SUMMARY pass=11 fail=0 skip=0`; `android offline` `SUMMARY pass=17 fail=0 skip=0`; `full offline` `SUMMARY pass=39 fail=0 skip=0`; `release_gate=SATISFIED`.
- [x] PASS — Dependabot six pull requests #3, #4, #6, #7, #8, #9 are `CLOSED` and `UNMERGED`; classification `MAINTAINER-SUPPLIED DECISION/OBSERVATION`.
- [x] PASS — `SUBSTANTIVE_BLOCKER_COUNT`: `0`; `README_CURRENT_STATE_BLOCKER` `CORRECTED`; `POST_6F_DEPENDABOT_GATE` `SATISFIED`.
- [x] PASS — This Phase 6H-B1 candidate synchronizes only the core active/current-release surfaces to `Phase 6: Complete` / `Phase 7: Planned` (next lifecycle phase). Phase 6H completion acceptance and Phase 7 start/authorization remain separate later maintainer actions; the v0.1.2 release is **not** claimed ready, merged, tagged, or published.

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

- [-] NOT APPLICABLE — Phase execution and completion evidence have not yet been performed; phase status remains `Planned`; Phase 7 is the `next lifecycle phase`; Phase 7 is `NOT started` and is `NOT authorized by this synchronization`.

## Cross-references

- [Release charter](release-charter.md)
- [Active AGENTS.md](../../../AGENTS.md)
- [Experiment protocol](../../agentic-development/experiment-protocol.md)
- [Evaluation template](../../agentic-development/evaluation-template.md)
- [OpenCode governance companion](../../agentic-development/opencode-governance.md)
- [v0.1.1 release charter (historical evidence)](../v0.1.1/release-charter.md)
- [v0.1.1 phase list (historical evidence)](../v0.1.1/phase-list.md)
