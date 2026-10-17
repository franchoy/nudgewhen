# Phase List — NudgeWhen v0.1.5

**Document status:** v0.1.5 current lifecycle authority — v0.1.5 — **Set Reminder Time** — is the active release train on branch `release/v0.1.5`; Phase 0 — Release Definition & Bootstrap — is `Planned` / current / in progress; Phase 1 — Reminder Time Architecture Contract — is `Planned` / not started; Phase 2 — Reminder Time Domain Implementation & JVM Proof — is `Planned` / not started; Phase 3 — Persistence Compatibility / Migration Proof — is `Planned` / not started; Phase 4 — Minimal Compose Integration — is `Planned` / not started; Phase 5 — Integration & Device Validation — is `Planned` / not started; Phase 6 — Integrated Audit & Reconciliation — is `Planned` / not started; Phase 7 — Full Pre-Release Gate — is `Planned` / not started; phase model: `0 Complete / 8 Planned`; no lifecycle phase has been formally closed inside the accepted eight-phase v0.1.5 model. The historical v0.1.4 — **Mark Reminder Done** — release remains the latest stable published release and is preserved as historical evidence. v0.1.5 is **not** merged, **not** tagged, **not** published, and is not release-ready. This document is normative for the eight-phase ordering and per-phase scope.

## Phase 0 — Release Definition & Bootstrap

Phase 0 performs the v0.1.5 release-definition, governance, document-bootstrap synchronization, and the initial dirty-candidate repository-consistency validation. Phase 0 freezes the v0.1.5 release charter, the v0.1.5 phase list, the current-facing tracked governance, the machine-readable release contract, the local-validation documentation, and the Phase 0 evidence record.

Phase 0 non-goals:

- no implementation of reminder-time functionality;
- no `app/build.gradle.kts` change;
- no selection of a concrete v0.1.5 persistence representation;
- no modification of any product Kotlin;
- no modification of persistence production code;
- no modification of Compose;
- no Android identity alignment;
- no Gradle dependency change;
- no validator implementation change;
- no CI workflow change.

### Status

Planned

## Phase 1 — Reminder Time Architecture Contract

Phase 1 owns the v0.1.5 reminder-time architecture contract. It decides the exact representation of an optional persistent reminder-time state on top of the existing v0.1.4 NWR2 reminder record while safely loading existing v0.1.4 data and preserving deterministic whole-list semantics. Phase 1 also decides the controller API for setting, changing, and clearing reminder time, the exact-id lookup contract, the UI affordance boundary, and any buffer behavior across Activity recreation. Phase 1 also evaluates and freezes the v0.1.5 persistence-format decision; Phase 0 records that decision as `PHASE_1_REQUIRED` and does not pre-select it.

Phase 1 is architecture-only and produces no product code, no production tests, and no Compose changes. Phase 1 forbids encoding reminder time inside reminder text, inside reminder id, or inside reminder done state. Phase 1 must not implement reminder time; Phase 2 owns the implementation and JVM proof.

Phase 1 non-goals:

- no implementation of reminder-time behavior;
- no production `Reminder` model change;
- no production `ReminderController` change;
- no production `FileReminderStore` change;
- no persistence migration implementation;
- no Compose change;
- no Android identity alignment;
- no Gradle, validator, CI, or dependency change.

### Status

Planned

## Phase 2 — Reminder Time Domain Implementation & JVM Proof

Phase 2 implements the frozen Phase 1 reminder-time domain API on top of the existing `Reminder` model and `ReminderController`. It adds the deterministic domain behavior and the deterministic JVM proof for that behavior. Phase 2 does not modify persistence production, does not modify Compose UI, and does not perform Android identity alignment.

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

### Status

Planned

## Phase 3 — Persistence Compatibility / Migration Proof

Phase 3 owns persistence compatibility for reminder-time operations. Phase 3 implements and proves the Phase-1-selected v0.1.5 persistence representation under the frozen Phase-1 contract. Phase 3 adds deterministic JVM proof for persistence across reminder-time setting, changing, clearing, and restart survival, and for backward loading of existing v0.1.4 NWR2 data. A new persistence backend remains out of scope. Phase 3 owns implementation, backward-load behavior, lazy same-file migration when applicable, and persistence proof.

Phase 3 non-goals:

- no production UI change;
- no Android identity alignment;
- no Gradle, validator, or CI change.

### Status

Planned

## Phase 4 — Minimal Compose Integration

Phase 4 owns the minimal Compose reminder-time UX layered onto the existing `ReminderScreen` / `MainActivity` integration. It adds the bounded set / change / clear affordance, retains `ReminderScreen`-owned Compose state, and keeps `MainActivity` free of `MutableState`. Phase 4 introduces no `ViewModel`, no `Flow`, no coroutines, no DI, and no navigation architecture solely for reminder time.

Phase 4 non-goals:

- no production `ReminderController` change beyond Phase 2;
- no production `FileReminderStore` change;
- no new Gradle dependency;
- no Android identity alignment;
- no integrated device validation;
- no reminder-time-driven sort, reorder, removal, dimming, or text decoration;
- no notification, alarm, or background-work affordance.

### Status

Planned

## Phase 5 — Integration & Device Validation

Phase 5 owns the integrated local validation and the bounded physical-device runtime acceptance for v0.1.5. It advances the Android artifact identity from the current `versionCode 5 / versionName 0.1.4` to the v0.1.5 target `versionCode 6 / versionName 0.1.5` only under separate explicit maintainer authorization. Phase 5 accepts the integrated local validation result together with bounded one-physical-device runtime evidence.

Phase 5 non-goals:

- no new Android permission;
- no new Android component;
- no new Gradle dependency;
- no new test dependency;
- no validator-architecture change;
- no general Android compatibility claim;
- no production-readiness claim.

### Status

Planned

## Phase 6 — Integrated Audit & Reconciliation

Phase 6 owns the integrated audit and reconciliation pass for v0.1.5. It cross-checks the release charter, phase list, experiment evidence, validator evidence, and device evidence for consistency. Phase 6 introduces no product functionality, Android behavior, or Android permission.

### Status

Planned

## Phase 7 — Full Pre-Release Gate

Phase 7 owns the full pre-release gate for v0.1.5, including final exact-head CI, final validator run, and the closure-candidate landing record. Phase 7 does not itself merge, tag, or publish v0.1.5; the release-bearing pull request, tag, and GitHub release are separate maintainer repository actions.

### Status

Planned
