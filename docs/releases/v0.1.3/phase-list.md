# Phase List — NudgeWhen v0.1.3

**Document status:** v0.1.3 Phase 5 closure lifecycle candidate — Phases 0 through 5 complete; Phase 0 — Release Definition & Bootstrap — is `Complete`; Phase 1 — Editing Architecture Contract — is `Complete`; Phase 2 — Editing Domain Implementation & JVM Proof — is `Complete`; Phase 3 — Persistence Compatibility Proof — is `Complete`; Phase 4 — Minimal Compose Editing UX — is `Complete`; Phase 5 — Integration & Device Validation — is `Complete` in this closure-synchronization candidate; Phase 6 — Integrated Audit & Reconciliation — is the next lifecycle phase and remains `Planned`; Phase 7 remains `Planned`; 6 Complete / 2 Planned. This document is normative for the eight-phase ordering and per-phase scope. It does not claim that v0.1.3 is merged, tagged, published, or release-ready.

## Phase 0 — Release Definition & Bootstrap

Phase 0 completed the v0.1.3 release-definition, governance, and document-bootstrap synchronization, including the active release charter, phase list, current-facing tracked governance, machine-readable release contract, local-validation documentation, and the initial dirty-candidate repository-consistency validation. Phase 0 did not implement reminder editing and did not change `app/build.gradle.kts`. Phase 1 — Editing Architecture Contract — is formally closed; Phase 2 — Editing Domain Implementation & JVM Proof — is the next lifecycle phase and remains `Planned`.

### Status

Complete

## Phase 1 — Editing Architecture Contract

Phase 1 owns the exact editing semantics contract. It decided whitespace normalization for edits, whitespace-only edit behavior, identical-text edit behavior, save/cancel interaction, the edit widget or affordance, and edit-buffer behavior across Activity recreation. Phase 1 was architecture-only and produced no product code or tests.

Phase 1 outcomes:

- editing architecture semantics are frozen;
- architecture candidate was landed at `9004b0f90f60d2d5c8b1ac4828d0a4521316ae5a`;
- exact-head CI run `33183197545` succeeded;
- Phase 1 architecture repository boundary is closed.

### Status

Complete

## Phase 2 — Editing Domain Implementation & JVM Proof

Phase 2 implemented the frozen Phase 1 edit domain API `edit(id: String, text: String): Boolean` on top of the existing `Reminder` model and `ReminderController`. It added the domain edit behavior and the deterministic JVM proof for that behavior. Phase 2 did not modify persistence production, did not modify Compose UI, and did not perform Android identity alignment.

Phase 2 outcomes:

- the frozen edit domain API `edit(id: String, text: String): Boolean` is implemented in `ReminderController`;
- the controller owns `text.trim()` normalization;
- invalid blank / whitespace-only / missing-id edits return `false` and do not save;
- identical normalized edits return `true` and do not save;
- a changed valid edit changes only the target text and returns `true`;
- target id, target index, neighbor order, and the complete candidate list ordering are preserved;
- the complete candidate list is saved exactly once;
- controller state is published only after a successful save;
- save failure propagates and preserves the previous controller state;
- `edit` never invokes `idGenerator`;
- Unicode text is supported;
- the source-level `ReminderControllerTest` count is 42: 25 existing `C_01` through `C_25` plus 17 edit responsibilities `E_01` through `E_17`;
- clean B3 direct JVM validation completed with `BUILD SUCCESSFUL`;
- implementation commit: `7eacbe3746807a36fecc2a33aac8768f30287686` (subject `feat: implement reminder editing domain`, parent `2fa810cce63e60c06d6c2b9ad04d80c30db2368d`);
- exact-head CI run `33239803189` succeeded;
- Phase 2 repository boundary is `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`;
- Phase 2 introduced no `Reminder` model change, no `FileReminderStore` change, no persistence production change, no Compose UI change, no Android identity change, no `app/build.gradle.kts` change, no new Gradle dependency, no test dependency change, no validator architecture change, and no CI workflow change.

### Status

Complete

## Phase 3 — Persistence Compatibility Proof

Phase 3 owns persistence compatibility for edit operations. It determines
and proves whether the existing `FileReminderStore` and `NWR1` persisted
format remain valid through edits and adds deterministic JVM proof for
persistence across edit. Phase 0 does not pre-decide the persistence-format
outcome; any format change would require separate Phase 3 evidence and
authorization. A new persistence backend remains out of scope.

Phase 3 outcomes (closure-synchronization candidate):

- Phase 3 is `Complete` in this closure-synchronization candidate;
- implementation path: `app/src/test/kotlin/io/github/franchoy/nudgewhen/data/FileReminderStoreTest.kt`;
- existing `P3_01` through `P3_29` preserved;
- `P3E_01` through `P3E_10` added and semantically accepted;
- source-level `FileReminderStoreTest` count: 39;
- persistence edit round-trip proven;
- same `id` after reload;
- same list index after reload;
- neighbors/order/content unchanged;
- new store/controller restores edited text;
- existing valid NWR1 supports load/edit/save/reload;
- NWR1 header unchanged;
- record grammar unchanged;
- Unicode edited text round-trip;
- NWR1 migration: `NOT_REQUIRED_BY_PHASE_3_TEST_EVIDENCE`;
- production `FileReminderStore` change: `NONE`;
- production `ReminderController` change during Phase 3: `NONE`;
- implementation commit: `b77af048950a720482c4ec279762d51f7f65ca5f` (subject `test: prove reminder edit persistence compatibility`, parent `fa387ece5eeb972f4344ea4bd04582749b6bbf02`);
- frozen B3 SHA: `74e46f94fcfbc823911faf971124c4600f70f5d02002b5dc4e6f2a1d623aa4a7`;
- exact-head CI: `33245690596 / success`;
- repository boundary: `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`;
- no Compose edit UX;
- no Android identity alignment;
- Phase 4 not started.

### Status

Complete

## Phase 4 — Minimal Compose Editing UX

Phase 4 owns the minimal Compose editing UX layered onto the existing `ReminderScreen` / `MainActivity` integration. It adds the bounded editing affordance, retains `ReminderScreen`-owned Compose state, and keeps `MainActivity` free of `MutableState`. Phase 4 introduces no `ViewModel`, no `Flow`, no coroutines, no DI, and no navigation architecture solely for editing.

Phase 4 outcomes (closure-synchronization candidate):

- Phase 4 is `Complete` in this closure-synchronization candidate;
- implementation path: `app/src/main/kotlin/io/github/franchoy/nudgewhen/ui/ReminderScreen.kt`;
- no Phase 4 test path was added;
- `P4_01` through `P4_20` were accepted by the B2 semantic audit;
- `editingId: String?` and `editBuffer: String` are owned by `ReminderScreen`;
- ordinary `remember(controller)` is the editing state holder;
- a normal row renders reminder text plus Edit and Remove `TextButton`s;
- an editing row renders an `OutlinedTextField` plus Save and Cancel `TextButton`s;
- Save derives the explicit non-null `activeEditingId` from the active editing row and calls `controller.edit(activeEditingId, editBuffer)`;
- an accepted `true` refreshes `controller.reminders`, exits edit mode, and clears `editBuffer`;
- a normalized-identical accepted `true` also exits edit mode;
- an accepted `false` retains the editing state and `editBuffer`;
- a thrown `controller.edit` causes no success transition;
- Cancel performs no controller mutation, exits edit mode, and clears `editBuffer`;
- the create input remains independent and usable during editing;
- the `LazyColumn` row key remains the stable `reminder.id`;
- no reorder or sort behavior was introduced;
- implementation commit: `673951082061562b45a40096bc2f9f5debdfb72d` (subject `feat: add reminder editing ux`, parent `938a38c7b2ba659e11eb31588b3a21526f180492`);
- B3 frozen candidate SHA: `322c57bb2adfa192e0eb3115e9bfb5233bc7e29beb18a2ef9641411be9bb3add`;
- exact-head CI: `33250408328 / success`;
- repository boundary: `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`;
- `MainActivity` change: `NONE`;
- `Reminder` model change: `NONE`;
- Phase 4 production `ReminderController` change: `NONE`;
- persistence production change: `NONE`;
- dependency change: `NONE`;
- validator change: `NONE`;
- CI change: `NONE`;
- Android identity alignment: `NONE`;
- integrated/device validation: `NOT_STARTED`;
- Phase 5 has not started.

### Status

Complete

## Phase 5 — Integration & Device Validation

Phase 5 — Integration & Device Validation — is `Complete` in this closure-synchronization candidate. The Phase 5 outcome statement is:

- Phase 5 is `Complete` in this closure-synchronization candidate;
- Android CURRENT identity advanced to `versionCode 4` / `versionName 0.1.3`;
- identity implementation commit: `1cfb9c373abfa24cf10f23daa152f4a410932d26` (subject `chore: align v0.1.3 android identity`, parent `3ba8470918a28acd4376639cf061f20209f78735`);
- identity implementation paths: `app/build.gradle.kts` and `scripts/release_contract.json`;
- exact-head identity CI: `33255108409 / success`;
- integrated local validation at HEAD `1cfb9c373abfa24cf10f23daa152f4a410932d26`: Python validator regression `100 tests / OK`; `required` `11/0/0`; `docs` `11/0/0`; `android offline` `17/0/0`; full offline `39/0/0`; `release_gate=SATISFIED`;
- frozen APK identity: package `io.github.franchoy.nudgewhen`, `versionCode 4`, `versionName 0.1.3`;
- frozen debug APK path: `app/build/outputs/apk/debug/app-debug.apk`;
- frozen APK SHA-256: `209bfb2a11628a903d7163ca807776a01aeb107e9fbe4c7168e6984a715f8908`;
- P5_01 through P5_13 accepted: identity, integrated local validation, APK identity, installed-artifact reconciliation and physical-device launch, bounded runtime reminder-list baseline, accepted user-facing edit, observable logical identity/list-position preservation, restart-persistence, create-after-edit, remove-after-edit, Cancel-leaves-original, whitespace-save-retains-editing, and `ONE_PHYSICAL_DEVICE_ONLY` runtime boundary;
- original D1 `adb install` CLI failure: `FAIL_PRESERVED`;
- accepted D1-R1, D1-R2, and D1-R3 recovery reconciled installed bytes to the Phase 5-C frozen APK and proved physical `MainActivity` cold launch;
- D2-A-R3 accepted edit, list-position preservation, and restart-persistence evidence;
- D2-B-R1 accepted Cancel / whitespace / create / remove / restart evidence;
- physical runtime evidence: `ONE_PHYSICAL_DEVICE_ONLY`;
- general Android compatibility: `NOT_CLAIMED`;
- production readiness: `NOT_CLAIMED`;
- supported Android version range: `NOT_CLAIMED`;
- multi-device validation: `NOT_CLAIMED`;
- Phase 5 introduced no new Android permission, no new Android component, no new Gradle dependency, no new test dependency, and no validator-architecture change;
- Phase 6 is `NOT_STARTED`.

### Status

Complete

## Phase 6 — Integrated Audit & Reconciliation

Phase 6 is the next lifecycle phase and remains `Planned`; Phase 6 has not started. Phase 6 owns the integrated audit and reconciliation pass for v0.1.3. It cross-checks release charter, phase list, experiment evidence, validator evidence, and device evidence for consistency. Phase 6 introduces no product functionality, Android behavior, or Android permission.

### Status

Planned

## Phase 7 — Full Pre-Release Gate

Phase 7 owns the full pre-release gate for v0.1.3, including final exact-head CI, final validator run, and the closure-candidate landing record. Phase 7 does not itself merge, tag, or publish v0.1.3; the release-bearing pull request, tag, and GitHub release are separate maintainer repository actions.

### Status

Planned