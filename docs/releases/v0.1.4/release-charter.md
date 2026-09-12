# Release Charter — NudgeWhen v0.1.4

**Document status:** v0.1.4 current lifecycle charter — Phases 0 through 1 complete; Phase 0 — Release Definition & Bootstrap — is `Complete`; Phase 1 — Done State Architecture Contract — is `Complete`; Phase 2 — Done State Domain Implementation & JVM Proof — is `Planned` and `NOT_STARTED`; Phase 3 — Persistence Compatibility / Migration Proof — is `Planned`; Phase 4 — Minimal Compose Integration — is `Planned`; Phase 5 — Integration & Device Validation — is `Planned`; Phase 6 — Integrated Audit & Reconciliation — is `Planned`; Phase 7 — Full Pre-Release Gate — is `Planned`; phase model: `2 Complete / 6 Planned`. Phase 2 is the next lifecycle phase; Phase-2 implementation has not started. v0.1.4 is **not** merged, **not** tagged, **not** published, and is not claimed release-ready. This charter is normative for v0.1.4 release policy.

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

The current released persistence format is NWR1. Its reminder record stores:

`id + encoded text`

NWR1 has no completion-state field. Phase 1 selected the persistence-format decision:

**Phase 1 selected:** `NWR2_WITH_NWR1_BACKWARD_LOAD`.

Current production/released persistence remains NWR1.

Phase 3 owns implementation, backward-load behavior, lazy same-file migration, and persistence proof.

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

Phase 0 — Release Definition & Bootstrap — is `Complete`. Phase 1 — Done State Architecture Contract — is `Complete`. Phases 2 through 7 are `Planned`. Phase 2 — Done State Domain Implementation & JVM Proof — is the next lifecycle phase; Phase-2 implementation has not started. Phase model: `2 Complete / 6 Planned`.

Phase 0 performed the v0.1.4 release-definition, governance, document-bootstrap synchronization, and the initial dirty-candidate repository-consistency validation. Phase 0 did not implement any done-state functionality, did not modify `app/build.gradle.kts`, did not modify any product Kotlin, did not modify persistence, did not modify Compose, did not perform Android identity alignment, and did not select a concrete persistence representation.

Phase 1 — Done State Architecture Contract — is architecture-only and produced the frozen done-state architecture contract (`docs/releases/v0.1.4/done-state-architecture.md`); it selected the NWR2_WITH_NWR1_BACKWARD_LOAD persistence-format decision and froze the complete done-state semantics contract, but did not implement any done-state behavior in product Kotlin or persistence.

Phase 2 must not own UI integration. Phase 3 owns the old v0.1.3 data compatibility / migration proof. Phase 4 owns minimal UI integration only after domain/persistence proof. Phase 5 owns integrated and bounded physical-device proof. Phase 6 owns integrated audit plus reconciliation. Phase 7 owns the full final pre-release gate.

## Maintenance window

The pre-v0.1.4 maintenance window is closed:

- PR #11 (setup-java v6) is merged into `main` before v0.1.4 branch creation;
- the current `setup-java` pin is `v6.0.0`;
- AGP remains `9.2.1`;
- Gradle remains `9.4.1`;
- PR #13 is outside the v0.1.4 release train and is deferred until after v0.1.4.

This charter does not claim v0.1.4 is merged, tagged, published, or
complete. Release readiness: `NO`. The release is not ready.