# Release Charter — NudgeWhen v0.1.4

**Document status:** v0.1.4 current lifecycle charter — Phases 0 through 4 complete; Phase 0 — Release Definition & Bootstrap — is `Complete`; Phase 1 — Done State Architecture Contract — is `Complete`; Phase 2 — Done State Domain Implementation & JVM Proof — is `Complete`; Phase 3 — Persistence Compatibility / Migration Proof — is `Complete`; Phase 4 — Minimal Compose Integration — is `Complete`; Phase 5 — Integration & Device Validation — is `Planned` and the next lifecycle phase; Phase 6 — Integrated Audit & Reconciliation — is `Planned`; Phase 7 — Full Pre-Release Gate — is `Planned`; phase model: `5 Complete / 3 Planned`. Phase-4 implementation is `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. v0.1.4 is **not** merged, **not** tagged, **not** published, and is not claimed release-ready. This charter is normative for v0.1.4 release policy.

## Release identity

Version:

v0.1.4

Title:

NudgeWhen v0.1.4 — Mark Reminder Done

Active branch:

release/v0.1.4

Previous release:

v0.1.3

Android current identity:

versionCode 4

versionName 0.1.3

Android target identity:

versionCode 5

versionName 0.1.4

The current committed Android artifact identity at Phase 0 closure is unchanged at `versionCode 4 / versionName 0.1.3`. The v0.1.4 target artifact identity is `versionCode 5 / versionName 0.1.4` and is recorded separately as a future target only; Phase 0 does not modify `app/build.gradle.kts` or the committed contract's `android.current_version_code` / `android.current_version_name`. The Android identity transition to `5 / 0.1.4` is reserved for a separately authorized phase.

## Single product promise

A user can mark an existing local reminder as done or not done while
preserving its identity, list position, text, and persistence across restart.

## Goals

The positive goals of v0.1.4 are limited to:

- marking an existing local reminder as done;
- unmarking a previously marked reminder as not done;
- preserving stable reminder identity;
- preserving stable list position;
- preserving the existing reminder text;
- retaining existing local persistence for both the reminder text and the new done state;
- backward loading of existing v0.1.3 NWR1 reminder data;
- minimal Compose integration layered onto the existing `ReminderScreen`;
- bounded deterministic domain/JVM/persistence proof;
- bounded Android/device integration proof.

The done / not-done behavior is part of the existing `reminders` capability. Persistent completion state is part of the existing `persistence` capability.

## Explicit non-goals

The release does NOT add:

- a new machine capability or `product_scope.allowed_capabilities` widening;
- a new Reminder model field beyond a persistent completion state that belongs to the existing `persistence` capability;
- archive;
- automatic removal of completed reminders;
- completed-history screen;
- filtering of completed reminders;
- manual reorder;
- custom sorting;
- priority;
- checklist or sub-items;
- due-time scheduling;
- alarms;
- notifications;
- voice or speech;
- location or geofencing;
- contextual or device-state triggers;
- networking or sync;
- analytics or telemetry;
- product background execution;
- a new Android Activity, Service, Receiver, or Provider;
- a new Android permission;
- Room or DataStore replacement;
- ViewModel, Flow, coroutines, DI, or navigation architecture solely for done state;
- a general Android compatibility claim;
- a production-readiness claim;
- unrelated dependency modernization;
- AGP 9.4 migration;
- Gradle 9.6 migration;
- changes to nudge-land as product functionality;
- Hermes or MCP integration;
- encoding done state inside reminder text;
- encoding done state inside reminder id.

## Product-scope authorization

The machine-recognized product scope remains exactly:

["reminders", "persistence"]

No other machine capability is authorized. The done / not-done behavior is part of the existing `reminders` capability. Persistent completion state is part of the existing `persistence` capability.

## Persistence decision boundary

The latest stable published release `v0.1.3` persistence format is NWR1. Its reminder record stores:

`id + encoded text`

NWR1 has no completion-state field. Phase 1 selected the persistence-format decision:

**Phase 1 selected:** `NWR2_WITH_NWR1_BACKWARD_LOAD`.

After the Phase-3 implementation landing, the active v0.1.4 release-branch `FileReminderStore` candidate behavior is NWR2 writes; NWR1 backward loading; lazy same-file migration on the first successful persistence-changing save; no load-time rewrite; order / id / text / done-state preservation under the frozen Phase-3 contract. The latest stable published v0.1.3 release remains NWR1.

Phase 3 owns implementation, backward-load behavior, lazy same-file migration, and persistence proof under the frozen Phase-3 contract.

The Phase 1 architecture contract (`docs/releases/v0.1.4/done-state-architecture.md`) freezes the full NWR2 write grammar, the NWR1 backward-load contract, the lazy same-file migration semantics, and the persistence-format rationale.

The persistence decision must:

- preserve the existing v0.1.3 NWR1 reminder data on load;
- preserve reminder id, text, and list position across done-state changes;
- preserve deterministic whole-list semantics.

Done state must NOT be encoded inside reminder text. Done state must NOT be encoded inside reminder id.

## Phase model

The accepted eight-phase model for v0.1.4 is:

- Phase 0 — Release Definition & Bootstrap
- Phase 1 — Done State Architecture Contract
- Phase 2 — Done State Domain Implementation & JVM Proof
- Phase 3 — Persistence Compatibility / Migration Proof
- Phase 4 — Minimal Compose Integration
- Phase 5 — Integration & Device Validation
- Phase 6 — Integrated Audit & Reconciliation
- Phase 7 — Full Pre-Release Gate

Phase 0 — Release Definition & Bootstrap — is `Complete`. Phase 1 — Done State Architecture Contract — is `Complete`. Phase 2 — Done State Domain Implementation & JVM Proof — is `Complete`. Phase 3 — Persistence Compatibility / Migration Proof — is `Complete`. Phase 4 — Minimal Compose Integration — is `Complete`. Phases 5 through 7 are `Planned`. Phase 5 — Integration & Device Validation — is the next lifecycle phase; Phase-5 implementation has not started and is not authorized. Phase model: `5 Complete / 3 Planned`.

Phase 0 performed the v0.1.4 release-definition, governance, document-bootstrap synchronization, and the initial dirty-candidate repository-consistency validation. Phase 0 did not implement any done-state functionality, did not modify `app/build.gradle.kts`, did not modify any product Kotlin, did not modify persistence, did not modify Compose, did not perform Android identity alignment, and did not select a concrete persistence representation.

Phase 1 — Done State Architecture Contract — is architecture-only and produced the frozen done-state architecture contract (`docs/releases/v0.1.4/done-state-architecture.md`); it selected the NWR2_WITH_NWR1_BACKWARD_LOAD persistence-format decision and froze the complete done-state semantics contract, but did not implement any done-state behavior in product Kotlin or persistence.

Phase 2 must not own UI integration. Phase 3 owns the old v0.1.3 data compatibility / migration proof. Phase 4 owns minimal UI integration only after domain/persistence proof. Phase 5 owns integrated and bounded physical-device proof. Phase 6 owns integrated audit plus reconciliation. Phase 7 owns the full final pre-release gate.

### Phase 2 formal closure summary

Phase 2 — Done State Domain Implementation & JVM Proof — is `Complete` for the active v0.1.4 release on `release/v0.1.4`. Implementation boundary: `658f607f4fda3e886fecdd7e785d325b37a31010` (subject `feat: implement v0.1.4 done-state domain`, parent `0d93dea8446a45d76c3a8c869fdc02e8b2944e32`). Repository boundary: `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. Implementation exact-head CI: `34751025153 / success`. Validate job: `103707474220 / success`. Implementation evidence: `EXP-0052`. Formal closure-sync planning + Build evidence: `EXP-0053`. The full Phase 2 test matrix and JVM proof totals are recorded in `docs/releases/v0.1.4/phase-list.md` and `EXP-0052.md`; this charter preserves only the policy summary. Phase 3 — Persistence Compatibility / Migration Proof — has since completed and is `Complete`; Phase 4 — Minimal Compose Integration — is the next lifecycle phase and is `Planned`; Phase-4 implementation has not started and is not authorized.

### Phase 3 formal closure summary

Phase 3 — Persistence Compatibility / Migration Proof — is `Complete` for the active v0.1.4 release on `release/v0.1.4`. Implementation boundary: `6c3ca643d47acf94e813d4f62f904d43b967a6e1` (subject `feat: implement v0.1.4 persistence migration`, parent `fe876b86977f0f34bded3c3e774ffcaec016591f`). Repository boundary: `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. Implementation exact-head CI: `CI / 6c3ca643d47acf94e813d4f62f904d43b967a6e1 / release/v0.1.4 / push / success`. Implementation evidence: `EXP-0056`. The active v0.1.4 release-branch `FileReminderStore` candidate behavior is NWR2 writes; NWR1 backward loading; lazy same-file migration on the first successful persistence-changing save; no load-time rewrite; order / id / text / done-state preservation under the frozen Phase-3 contract. The latest stable published v0.1.3 release remains NWR1. Phase 4 — Minimal Compose Integration — has since completed and is `Complete`; Phase 5 — Integration & Device Validation — is the next lifecycle phase and is `Planned` / `NOT_STARTED` / `NOT_AUTHORIZED`. The full Phase 3 test matrix and JVM proof totals are recorded in `docs/releases/v0.1.4/phase-list.md` and `EXP-0056.md`; this charter preserves only the policy summary.

### Phase 4 formal closure summary

Phase 4 — Minimal Compose Integration — is `Complete` for the active v0.1.4 release on `release/v0.1.4`. Implementation boundary: `e173dd69335e0b1dcbade07b4797c78f91c0668e` (subject `feat: implement v0.1.4 mark reminder done UI`, parent `d15703c8667fd228475b34a018ade8177a2be67c`). Repository boundary: `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. Implementation exact-head CI: `CI / e173dd69335e0b1dcbade07b4797c78f91c0668e / release/v0.1.4 / push / success`. Implementation evidence: `EXP-0058`. Phase 4 implemented the bounded source-level done-state Compose integration on the existing `ReminderScreen`: a controlled Material3 Checkbox is integrated into both normal and editing reminder rows; checked state is sourced from `reminder.done`; action delegates to `controller.setDone(reminder.id, newChecked)`; screen refresh occurs only after accepted success; no second done-state UI authority exists; no optimistic done-state publish exists; editing state is preserved during done toggling; no done-specific sort, reorder, removal, dimming, or text decoration was added. Phase 4 did not perform Android identity alignment and did not perform integrated/device validation. Phase 5 — Integration & Device Validation — is the next lifecycle phase and is `Planned` / `NOT_STARTED` / `NOT_AUTHORIZED`. The full Phase 4 test matrix and JVM proof totals are recorded in `docs/releases/v0.1.4/phase-list.md` and `EXP-0058.md`; this charter preserves only the policy summary.

## Maintenance window

The pre-v0.1.4 maintenance window is closed:

- PR #11 (setup-java v6) is merged into `main` before v0.1.4 branch creation;
- the current `setup-java` pin is `v6.0.0`;
- AGP remains `9.2.1`;
- Gradle remains `9.4.1`;
- PR #13 is outside the v0.1.4 release train and is deferred until after v0.1.4.

This charter does not claim v0.1.4 is merged, tagged, published, or
complete. Release readiness: `NO`. The release is not ready.