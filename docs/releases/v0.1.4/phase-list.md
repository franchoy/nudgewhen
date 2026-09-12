# Phase List — NudgeWhen v0.1.4

**Document status:** v0.1.4 current lifecycle authority — Phases 0 through 0 complete; Phase 0 — Release Definition & Bootstrap — is `Complete`; Phase 1 — Done State Architecture Contract — is `Planned`; Phase 2 — Done State Domain Implementation & JVM Proof — is `Planned`; Phase 3 — Persistence Compatibility / Migration Proof — is `Planned`; Phase 4 — Minimal Compose Integration — is `Planned`; Phase 5 — Integration & Device Validation — is `Planned`; Phase 6 — Integrated Audit & Reconciliation — is `Planned`; Phase 7 — Full Pre-Release Gate — is `Planned`; phase model: `1 Complete / 7 Planned`. Phase 1 implementation has not started. This document is normative for the eight-phase ordering and per-phase scope. It does not claim that v0.1.4 is merged, tagged, published, or release-ready.

## Phase 0 — Release Definition & Bootstrap

Phase 0 completed the v0.1.4 release-definition, governance, and document-bootstrap synchronization, including the active release charter, phase list, current-facing tracked governance, machine-readable release contract, local-validation documentation, and the initial dirty-candidate repository-consistency validation. Phase 0 performed release-definition work only. Phase 0 did not implement any done-state functionality, did not change `app/build.gradle.kts`, did not select a concrete persistence representation, did not modify any product Kotlin, did not modify persistence production code, did not modify Compose, and did not perform Android identity alignment. The committed Android artifact identity remained unchanged at `versionCode 4 / versionName 0.1.3`; the v0.1.4 target identity of `versionCode 5 / versionName 0.1.4` is recorded as a future target only. Phase 1 — Done State Architecture Contract — is the next lifecycle phase, is `Planned`, and has not started.

### Status

Complete

## Phase 1 — Done State Architecture Contract

Phase 1 owns the exact done-state semantics contract. It decides the precise representation of a persistent boolean completion state on top of the existing v0.1.3 NWR1 reminder record while safely loading existing v0.1.3 data and preserving deterministic whole-list semantics. Phase 1 also decides the controller API for marking done / not done, the exact-id lookup contract, the save / cancel interaction, the affordance, and any buffer behavior across Activity recreation. Phase 1 is architecture-only and produces no product code, no production tests, and no Compose changes.

Phase 1 evaluates, but does not pre-select, between a compatible NWR1 extension, an NWR2 format, or another explicitly justified design. Phase 1 forbids encoding done state inside reminder text and inside reminder id. Phase 1 must not implement done state; Phase 2 owns the implementation and JVM proof.

Phase 1 non-goals:

- no implementation of done-state behavior;
- no production `Reminder` model change;
- no production `ReminderController` change;
- no production `FileReminderStore` change;
- no persistence migration implementation;
- no Compose change;
- no Android identity alignment;
- no Gradle, validator, CI, or dependency change.

### Status

Planned

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

### Status

Planned

## Phase 3 — Persistence Compatibility / Migration Proof

Phase 3 owns persistence compatibility for done-state operations. It determines and proves whether the existing `FileReminderStore` and the Phase-1-chosen representation remain valid through done-state changes and adds deterministic JVM proof for persistence across done-state toggling, restart survival of done state, and backward loading of existing v0.1.3 NWR1 data. Phase 0 does not pre-decide the persistence-format outcome; the final representation decision is `PHASE_1_REQUIRED`. A new persistence backend remains out of scope.

Phase 3 non-goals:

- no production UI change;
- no Android identity alignment;
- no Gradle, validator, or CI change.

### Status

Planned

## Phase 4 — Minimal Compose Integration

Phase 4 owns the minimal Compose done-state UX layered onto the existing `ReminderScreen` / `MainActivity` integration. It adds the bounded done / not-done affordance, retains `ReminderScreen`-owned Compose state, and keeps `MainActivity` free of `MutableState`. Phase 4 introduces no `ViewModel`, no `Flow`, no coroutines, no DI, and no navigation architecture solely for done state.

Phase 4 non-goals:

- no production `ReminderController` change beyond Phase 2;
- no production `FileReminderStore` change;
- no new Gradle dependency;
- no Android identity alignment;
- no integrated device validation;
- no reorder or custom sort behavior.

### Status

Planned

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

### Status

Planned

## Phase 6 — Integrated Audit & Reconciliation

Phase 6 owns the integrated audit and reconciliation pass for v0.1.4. It cross-checks the release charter, phase list, experiment evidence, validator evidence, and device evidence for consistency. Phase 6 introduces no product functionality, Android behavior, or Android permission.

### Status

Planned

## Phase 7 — Full Pre-Release Gate

Phase 7 owns the full pre-release gate for v0.1.4, including final exact-head CI, final validator run, and the closure-candidate landing record. Phase 7 does not itself merge, tag, or publish v0.1.4; the release-bearing pull request, tag, and GitHub release are separate maintainer repository actions.

### Status

Planned