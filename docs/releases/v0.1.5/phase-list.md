# Phase List — NudgeWhen v0.1.5

**Document status:** v0.1.5 current lifecycle authority — Phases 0 through 1 complete (formally accepted on 2026-10-18 and on 2026-11-04 respectively); v0.1.5 — **Set Reminder Time** — is the active release train on branch `release/v0.1.5`; Phase 0 — Release Definition & Bootstrap — is `Complete` / formally accepted on 2026-10-18; Phase 1 — Reminder Time Architecture Contract — is `Complete` / formally accepted on 2026-11-04; Phase 2 — Reminder Time Domain Implementation & JVM Proof — is `Planned` / not started; Phase 3 — Persistence Compatibility / Migration Proof — is `Planned` / not started; Phase 4 — Minimal Compose Integration — is `Planned` / not started; Phase 5 — Integration & Device Validation — is `Planned` / not started; Phase 6 — Integrated Audit & Reconciliation — is `Planned` / not started; Phase 7 — Full Pre-Release Gate — is `Planned` / not started; phase model: `2 Complete / 6 Planned`; Phase 0 formal acceptance is supported by exact-head CI run `39114566018` for `2775cf64069a84adebde36366cddbee5459e67c5`; Phase 1 formal acceptance is supported by exact-head CI run `41907797725` for `8f811b61328ff24fb6b8db1589316a81b30450bb`; the accepted v0.1.5 persistence representation is `NWR3` with NWR1/NWR2 backward loading and lazy same-file migration; Phase 2 implementation is `NOT_STARTED`. The historical v0.1.4 — **Mark Reminder Done** — release remains the latest stable published release and is preserved as historical evidence. v0.1.5 is **not** merged, **not** tagged, **not** published, and is not release-ready. This document is normative for the eight-phase ordering and per-phase scope.

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

Complete

### Phase 0 formal acceptance

The maintainer accepted Phase 0 on 2026-10-18 after closure commit `2775cf64069a84adebde36366cddbee5459e67c5` was published and exact-head `CI` run `39114566018` / `validate` job `117637601837` succeeded. Python regression: 245 tests / OK; local and hosted clean validation: 41 passed, 0 failed, 0 skipped; `release_gate=SATISFIED`. The Phase 0 bootstrap exception termination is recorded in the terminal governance synchronization. Phase 1 remains `Planned` / `NOT_STARTED`; no Phase 1 work is authorized by this acceptance. That Phase-1 status is the state as of the 2026-10-18 Phase 0 acceptance and is preserved as historical evidence; Phase 1 was subsequently completed and formally accepted on 2026-11-04, as recorded in the Phase 1 section below.

## Phase 1 — Reminder Time Architecture Contract

Phase 1 owns the v0.1.5 reminder-time architecture contract. It decides the exact representation of an optional persistent reminder-time state on top of the existing v0.1.4 NWR2 reminder record while safely loading existing v0.1.4 data and preserving deterministic whole-list semantics. Phase 1 also decides the controller API for setting, changing, and clearing reminder time, the exact-id lookup contract, the UI affordance boundary, and any buffer behavior across Activity recreation. Phase 1 also evaluates and freezes the v0.1.5 persistence-format decision; Phase 0 records that decision as `PHASE_1_REQUIRED` and does not pre-select it.

Phase 1 is architecture-only and produces no product code, no production tests, and no Compose changes. Phase 1 forbids encoding reminder time inside reminder text, inside reminder id, or inside reminder done state. Phase 1 must not implement reminder time; Phase 2 owns the implementation and JVM proof.

Phase 1 is `Complete`. The accepted architecture contract is `docs/releases/v0.1.5/reminder-time-architecture.md`. The maintainer-accepted v0.1.5 persistence representation is **`NWR3`**, with NWR1/NWR2 backward loading and lazy same-file migration. That accepted Phase 1 decision supersedes the historical Phase 0 placeholder value `PHASE_1_REQUIRED` for the active lifecycle; the historical Phase 0 value remains recorded in the release charter and in `AGENTS.md` as historical evidence.

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

Complete

### Phase 1 formal acceptance

The maintainer formally accepted Phase 1 on 2026-11-04 after the accepted architecture commit `8f811b61328ff24fb6b8db1589316a81b30450bb` (parent `3605975ee5bd00c7c7837556dee8d2c0d2ca4fe2`; subject `docs: define v0.1.5 reminder-time architecture`) was published through the native nudge-land transaction `nudgewhen-v0.1.5-phase1-architecture-first-native-land-001`, whose terminal state was `LANDED / S10_LANDED`, and exact-head `CI` run `41907797725` / job `126847010004` concluded `success`. Python regression: 245 tests / OK; hosted clean validation: 41 passed, 0 failed, 0 skipped; `release_gate=SATISFIED`. The accepted architecture and its ten decisions are frozen and are normative for Phase 2, Phase 3, and Phase 4 implementation. Phase 1 acceptance authorizes no product implementation: Phase 2 — Reminder Time Domain Implementation & JVM Proof — remains `Planned` / `NOT_STARTED` and requires separate explicit maintainer authorization.

The native nudge-land receipts and the hosted CI run, job, conclusion, test counts, and release-gate value are maintainer-supplied external evidence that was previously reviewed outside this repository. They are not new network observations by any OpenCode agent.

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
