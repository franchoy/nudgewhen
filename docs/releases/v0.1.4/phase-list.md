# Phase List — NudgeWhen v0.1.4

**Document status:** v0.1.4 current lifecycle authority — Phases 0 through 5 complete; Phase 0 — Release Definition & Bootstrap — is `Complete`; Phase 1 — Done State Architecture Contract — is `Complete`; Phase 2 — Done State Domain Implementation & JVM Proof — is `Complete`; Phase 3 — Persistence Compatibility / Migration Proof — is `Complete`; Phase 4 — Minimal Compose Integration — is `Complete`; Phase 5 — Integration & Device Validation — is `Complete`; Phase 6 — Integrated Audit & Reconciliation — is `Planned`; Phase 7 — Full Pre-Release Gate — is `Planned`; phase model: `6 Complete / 2 Planned`. Phase-5 implementation is `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. This document is normative for the eight-phase ordering and per-phase scope. It does not claim that v0.1.4 is merged, tagged, published, or release-ready.

## Phase 0 — Release Definition & Bootstrap

Phase 0 completed the v0.1.4 release-definition, governance, and document-bootstrap synchronization, including the active release charter, phase list, current-facing tracked governance, machine-readable release contract, local-validation documentation, and the initial dirty-candidate repository-consistency validation. Phase 0 performed release-definition work only. Phase 0 did not implement any done-state functionality, did not change `app/build.gradle.kts`, did not select a concrete persistence representation, did not modify any product Kotlin, did not modify persistence production code, did not modify Compose, and did not perform Android identity alignment. The committed Android artifact identity remained unchanged at `versionCode 4 / versionName 0.1.3`; the v0.1.4 target identity of `versionCode 5 / versionName 0.1.4` is recorded as a future target only. Phase 1 — Done State Architecture Contract — was the next lifecycle phase after Phase 0 closure and has now completed.

### Status

Complete

## Phase 1 — Done State Architecture Contract

Phase 1 owns the exact done-state semantics contract. It decides the precise representation of a persistent boolean completion state on top of the existing v0.1.3 NWR1 reminder record while safely loading existing v0.1.3 data and preserving deterministic whole-list semantics. Phase 1 also decides the controller API for marking done / not done, the exact-id lookup contract, the save / cancel interaction, the affordance, and any buffer behavior across Activity recreation. Phase 1 is architecture-only and produces no product code, no production tests, and no Compose changes.

Phase 1 evaluates, but does not pre-select, between a compatible NWR1 extension, an NWR2 format, or another explicitly justified design. Phase 1 forbids encoding done state inside reminder text and inside reminder id. Phase 1 must not implement done state; Phase 2 owns the implementation and JVM proof.

### Phase 1 closure record

Phase 1 is `Complete`. Architecture path: `docs/releases/v0.1.4/done-state-architecture.md`. Architecture commit: `84446af3d6360cbcb35371fbf451ad9d1b180691`. Parent: `193fe336b2b147f897b87636b29a2d439d2e1219`. CI run: `34686932221` (success). Validate job: `103535431436` (success). Phase 1 was architecture-only; no product implementation occurred in Phase 1.

Phase 1 selected the persistence-format decision `NWR2_WITH_NWR1_BACKWARD_LOAD`: NWR2 writes; backward NWR1 loading; lazy same-file migration. Phase 3 owns NWR2 implementation, backward-load behavior, lazy same-file migration, and the persistence proof.

Phase 1 non-goals (preserved):

- no implementation of done-state behavior;
- no production `Reminder` model change;
- no production `ReminderController` change;
- no production `FileReminderStore` change;
- no persistence migration implementation;
- no Compose change;
- no Android identity alignment;
- no Gradle, validator, CI, or dependency change.

### Status

Complete

## Phase 2 — Done State Domain Implementation & JVM Proof

Phase 2 implements the frozen Phase 1 done-state domain API on top of the existing `Reminder` model and `ReminderController`. It adds the deterministic domain behavior and the deterministic JVM proof for that behavior. Phase 2 does not modify persistence production, does not modify Compose UI, and does not perform Android identity alignment.

Phase 2 non-goals:

- no persistence production change;
- no Compose UI change;
- no Android identity alignment;
- no `app/build.gradle.kts` change;
- no new Gradle dependency;
- no test dependency change;
- no validator architecture change;
- no CI workflow change;
- no UI integration.

### Phase 2 closure record

Phase 2 — Done State Domain Implementation & JVM Proof — is `Complete` for the active v0.1.4 release on `release/v0.1.4`.

Implementation commit:

`658f607f4fda3e886fecdd7e785d325b37a31010`

Parent:

`0d93dea8446a45d76c3a8c869fdc02e8b2944e32`

Subject:

`feat: implement v0.1.4 done-state domain`

Repository boundary:

`LANDED_AND_EXACT_HEAD_CI_ACCEPTED`

Implementation exact-head CI:

`34751025153` / `success`

Validate job:

`103707474220` / `success`

Principal implementation proof:

- `ReminderTest`: `2 / 0 / 0 / 0`
- `ReminderControllerTest`: `51 / 0 / 0 / 0`
- affected-class total: `53`
- standard regression: `244 / OK`
- `required`: `11 / 0 / 0`
- `docs`: `11 / 0 / 0`
- `skip-Android`: `22 / 0 / 0`

Phase-2 implementation facts preserved by this closure:

- `Reminder.done` default `false` is implemented.
- `ReminderController.setDone(id: String, done: Boolean)` is implemented.
- `ReminderController.edit(...)` preserves the existing done state across edit.
- `FileReminderStore` production is unchanged.
- Persistence implementation is unchanged.
- Compose is unchanged.
- Android identity is unchanged (`versionCode 4 / versionName 0.1.3`).
- Gradle dependency state is unchanged.
- Test dependency state is unchanged.
- Validator architecture is unchanged.
- CI workflow is unchanged.

Implementation Build evidence:

`EXP-0052`

Formal closure-sync planning + Build evidence:

`EXP-0053`

Next lifecycle phase:

`Phase 3 — Persistence Compatibility / Migration Proof`

Phase 3 has since completed and is `Complete`; Phase 4 — Minimal Compose Integration — has since completed and is `Complete`; Phase 5 — Integration & Device Validation — has since completed and is `Complete`; Phase 6 — Integrated Audit & Reconciliation — is the next lifecycle phase and is `Planned` / `NOT_STARTED` / `NOT_AUTHORIZED`. Phase 3 owned NWR2 writes, NWR1 backward loading, lazy same-file migration, and real-file persistence proof under the frozen Phase-3 contract.

### Status

Complete

## Phase 3 — Persistence Compatibility / Migration Proof

Phase 3 owns persistence compatibility for done-state operations. It implements and proves the Phase-1-selected `NWR2_WITH_NWR1_BACKWARD_LOAD` representation: NWR2 writes; backward NWR1 loading; lazy same-file migration. Phase 3 adds deterministic JVM proof for persistence across done-state toggling, restart survival of done state, and backward loading of existing v0.1.3 NWR1 data. A new persistence backend remains out of scope. Phase 3 owns implementation, backward-load behavior, lazy same-file migration, and persistence proof.

Phase 3 non-goals:

- no production UI change;
- no Android identity alignment;
- no Gradle, validator, or CI change.

### Phase 3 closure record

Phase 3 — Persistence Compatibility / Migration Proof — is `Complete` for the active v0.1.4 release on `release/v0.1.4`.

Implementation commit:

`6c3ca643d47acf94e813d4f62f904d43b967a6e1`

Parent:

`fe876b86977f0f34bded3c3e774ffcaec016591f`

Subject:

`feat: implement v0.1.4 persistence migration`

Repository boundary:

`LANDED_AND_EXACT_HEAD_CI_ACCEPTED`

Implementation exact-head CI:

`CI / 6c3ca643d47acf94e813d4f62f904d43b967a6e1 / release/v0.1.4 / push / success`

Implementation evidence:

`EXP-0056`

Phase-3 implementation facts preserved by this closure:

- The active v0.1.4 release-branch `FileReminderStore` candidate behavior is NWR2 writes; NWR1 backward loading; lazy same-file migration on the first successful persistence-changing save; no load-time rewrite.
- Order / id / text / done-state preservation is proven under the frozen Phase-3 contract.
- Phase 3 did not modify Compose.
- Phase 3 did not perform Android identity alignment.
- Gradle dependency state is unchanged.
- Test dependency state is unchanged.
- Validator architecture is unchanged.
- CI workflow is unchanged.

Next lifecycle phase:

`Phase 4 — Minimal Compose Integration`

Phase 4 has since completed and is `Complete`; Phase 5 — Integration & Device Validation — has since completed and is `Complete`; Phase 6 — Integrated Audit & Reconciliation — is the next lifecycle phase and is `Planned` / `NOT_STARTED` / `NOT_AUTHORIZED`.

### Status

Complete

## Phase 4 — Minimal Compose Integration

Phase 4 owns the minimal Compose done-state UX layered onto the existing `ReminderScreen` / `MainActivity` integration. It adds the bounded done / not-done affordance, retains `ReminderScreen`-owned Compose state, and keeps `MainActivity` free of `MutableState`. Phase 4 introduces no `ViewModel`, no `Flow`, no coroutines, no DI, and no navigation architecture solely for done state.

Phase 4 non-goals:

- no production `ReminderController` change beyond Phase 2;
- no production `FileReminderStore` change;
- no new Gradle dependency;
- no Android identity alignment;
- no integrated device validation;
- no reorder or custom sort behavior.

### Phase 4 closure record

Phase 4 — Minimal Compose Integration — is `Complete` for the active v0.1.4 release on `release/v0.1.4`.

Implementation commit:

`e173dd69335e0b1dcbade07b4797c78f91c0668e`

Parent:

`d15703c8667fd228475b34a018ade8177a2be67c`

Subject:

`feat: implement v0.1.4 mark reminder done UI`

Repository boundary:

`LANDED_AND_EXACT_HEAD_CI_ACCEPTED`

Implementation evidence:

`EXP-0058`

Frozen ReminderScreen SHA:

`b8e84da641d6ecab9727a9477a1fc265ddc2e5b8eea416c83bcb8cd3f8965f06`

Frozen EXP-0058 SHA:

`6da6409c077e2f843e276921790e27be73dec0a3d717ca4cd8329ce0cbf8f2ec`

Exact-head CI:

`CI / e173dd69335e0b1dcbade07b4797c78f91c0668e / release/v0.1.4 / push / success`

Phase 4 implemented the bounded source-level done-state Compose integration on the existing `ReminderScreen`: a controlled Material3 Checkbox is integrated into both normal and editing reminder rows; checked state is sourced from `reminder.done`; action delegates to `controller.setDone(reminder.id, newChecked)`; screen refresh occurs only after accepted success; no second done-state UI authority exists; no optimistic done-state publish exists; editing state is preserved during done toggling; no done-specific sort, reorder, removal, dimming, or text decoration was added. Phase 4 did not perform Android identity alignment, did not perform integrated device validation, did not introduce a `ViewModel`, `Flow`, coroutine, DI, or navigation solely for done state, did not add a new Android `Activity`, `Service`, `Receiver`, or `Provider`, did not add a new Android permission, did not introduce a Gradle dependency or test dependency, did not change validator architecture, and did not change CI workflow. Phase 5 — Integration & Device Validation — has since completed and is `Complete`; Phase 6 — Integrated Audit & Reconciliation — is the next lifecycle phase and is `Planned` / `NOT_STARTED` / `NOT_AUTHORIZED`.

### Status

Complete

## Phase 5 — Integration & Device Validation

Phase 5 owns the integrated local validation and the bounded physical-device runtime acceptance for v0.1.4. It advances the Android artifact identity from the current `versionCode 4 / versionName 0.1.3` to the v0.1.4 target `versionCode 5 / versionName 0.1.4` only under separate explicit maintainer authorization. Phase 5 accepts the integrated local validation result together with bounded one-physical-device runtime evidence.

Phase 5 non-goals:

- no new Android permission;
- no new Android component;
- no new Gradle dependency;
- no new test dependency;
- no validator-architecture change;
- no general Android compatibility claim;
- no production-readiness claim.

### Phase 5 closure record

Phase 5 — Integration & Device Validation — is `Complete` for the active v0.1.4 release on `release/v0.1.4`.

Identity landing commit:

`e8c9c08920f5a0c146189c0087b293c260c2701d`

Identity landing parent:

`846d291d2e262fbad7c1e03d2fa1e3b7ec63cf10`

Subject:

`chore: align v0.1.4 android identity`

Implementation repository boundary:

`LANDED_AND_EXACT_HEAD_CI_ACCEPTED`

Android identity:

`versionCode 5 / versionName 0.1.4`

Phase-5 cumulative evidence:

`EXP-0060`

P5_01 through P5_13:

`ACCEPTED`

P5_13:

`ONE_PHYSICAL_DEVICE_ONLY`

`GENERAL_ANDROID_COMPATIBILITY`:

`NOT_CLAIMED`

`MULTI_DEVICE_VALIDATION`:

`NOT_CLAIMED`

`PRODUCTION_READINESS`:

`NOT_CLAIMED`

`SUPPORTED_ANDROID_VERSION_RANGE`:

`NOT_CLAIMED`

Phase 5 advanced the Android artifact identity from `versionCode 4 / versionName 0.1.3` to the v0.1.4 target `versionCode 5 / versionName 0.1.4`; Phase 5 did not add a new Android permission, did not add a new Android component, did not introduce a new Gradle dependency, did not introduce a new test dependency, did not change validator architecture, did not make a general Android compatibility claim, and did not make a production-readiness claim.

Next lifecycle phase:

`Phase 6 — Integrated Audit & Reconciliation`

Phase 6:

`Planned / NOT_STARTED / NOT_AUTHORIZED`

### Status

Complete

## Phase 6 — Integrated Audit & Reconciliation

Phase 6 owns the integrated audit and reconciliation pass for v0.1.4. It cross-checks the release charter, phase list, experiment evidence, validator evidence, and device evidence for consistency. Phase 6 introduces no product functionality, Android behavior, or Android permission.

### Status

Planned

## Phase 7 — Full Pre-Release Gate

Phase 7 owns the full pre-release gate for v0.1.4, including final exact-head CI, final validator run, and the closure-candidate landing record. Phase 7 does not itself merge, tag, or publish v0.1.4; the release-bearing pull request, tag, and GitHub release are separate maintainer repository actions.

### Status

Planned