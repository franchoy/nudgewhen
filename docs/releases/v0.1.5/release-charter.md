# Release Charter — NudgeWhen v0.1.5

**Document status:** v0.1.5 current lifecycle charter — v0.1.5 — **Set Reminder Time** — is the active release train; active branch `release/v0.1.5`; Phase 0 — Release Definition & Bootstrap — is `Planned` / current / in progress; Phase 1 — Reminder Time Architecture Contract — is `Planned` / not started; Phase 2 — Reminder Time Domain Implementation & JVM Proof — is `Planned` / not started; Phase 3 — Persistence Compatibility / Migration Proof — is `Planned` / not started; Phase 4 — Minimal Compose Integration — is `Planned` / not started; Phase 5 — Integration & Device Validation — is `Planned` / not started; Phase 6 — Integrated Audit & Reconciliation — is `Planned` / not started; Phase 7 — Full Pre-Release Gate — is `Planned` / not started; phase model: `0 Complete / 8 Planned`; no lifecycle phase has been formally closed inside the accepted eight-phase v0.1.5 model. The historical v0.1.4 — **Mark Reminder Done** — release remains the latest stable published release and is preserved as historical evidence for the v0.1.5 train. v0.1.5 is **not** merged, **not** tagged, **not** published, and is not release-ready. This charter is normative for v0.1.5 release policy.

## Release identity

Version:

v0.1.5

Title:

NudgeWhen v0.1.5 — Set Reminder Time

Active branch:

release/v0.1.5

Previous release:

v0.1.4

Android current identity:

versionCode 5

versionName 0.1.4

Android target identity:

versionCode 6

versionName 0.1.5

The committed Android artifact identity remains `versionCode 5 / versionName 0.1.4`. The v0.1.5 target identity `versionCode 6 / versionName 0.1.5` is recorded as a future target only. Android identity alignment belongs to a later separately authorized phase and is NOT performed by Phase 0. `app/build.gradle.kts` remains unchanged in Phase 0.

## Single product promise

A user can set, change, or clear an optional local date-and-time on an existing reminder, see that value in the reminder UI, and retain it across application restart while preserving the reminder's identity, text, done state, and list position.

Reaching the selected time performs no automatic action.

## Goals

The positive goals of v0.1.5 are limited to:

- setting an optional local date-and-time on an existing reminder;
- changing an existing optional reminder-time on an existing reminder;
- clearing an existing optional reminder-time on an existing reminder;
- presenting the reminder-time value in the reminder UI when present;
- not displaying a reminder-time value when absent, while retaining an affordance to set one on the existing reminder;
- preserving stable reminder identity;
- preserving stable list position;
- preserving the existing reminder text;
- preserving the existing done state;
- retaining existing local persistence for reminder text and done state;
- retaining the new optional reminder-time across application restart;
- backward loading of existing v0.1.4 NWR2 reminder data;
- minimal Compose integration layered onto the existing `ReminderScreen`;
- bounded deterministic domain / JVM / persistence proof;
- bounded Android / device integration proof.

The reminder-time state belongs to the existing `reminders` capability. Persistent reminder-time state belongs to the existing `persistence` capability.

## Explicit non-goals

The release does NOT add:

- a new machine capability or `product_scope.allowed_capabilities` widening;
- a new Reminder model field beyond an optional reminder-time that belongs to the existing `persistence` capability;
- notifications;
- alarms;
- background wake-up;
- automatic scheduling or firing of reminders when their time is reached;
- recurrence;
- location, geofencing, or contextual / device-state triggers;
- voice or speech;
- networking or sync;
- analytics or telemetry;
- product background execution;
- a new Android Activity, Service, Receiver, or Provider;
- a new Android permission;
- Room or DataStore replacement;
- ViewModel, Flow, coroutines, DI, or navigation architecture solely for reminder time;
- a general Android compatibility claim;
- a production-readiness claim;
- unrelated dependency modernization;
- changes to nudge-land as product functionality;
- Hermes or MCP integration;
- encoding reminder time inside reminder text;
- encoding reminder time inside reminder id;
- encoding reminder time inside reminder done state;
- timezone conversion or automatic DST handling;
- calendar or event-sync functionality.

Reaching the selected reminder time performs no automatic action. The application does not wake the device, post a notification, ring, vibrate, schedule an alarm, or perform any background work because a reminder's time has arrived.

## Product-scope authorization

The machine-recognized product scope remains exactly:

["reminders", "persistence"]

No other machine capability is authorized. The reminder-time behavior is part of the existing `reminders` capability. Persistent reminder-time state is part of the existing `persistence` capability.

## Persistence decision boundary

The historical predecessor release `v0.1.4` persistence format is NWR2. Its reminder record stores:

`id + encoded text + done state`

NWR2 has no reminder-time field. The v0.1.5 persistence-format decision is NOT selected by Phase 0.

Phase 0 records the persistence-format decision as:

**`PHASE_1_REQUIRED`**

Phase 1 owns the evaluation and freezing of the v0.1.5 persistence representation. Phase 1 must evaluate and freeze the representation without Phase 0 having pre-selected it.

The historical v0.1.4 persistence decision boundary (NWR2 writes, NWR1 backward loading, lazy same-file migration) was selected by v0.1.4 Phase 1 and implemented by v0.1.4 Phase 3. v0.1.5 may extend, retain, or replace that representation only through the v0.1.5 Phase 1 architecture contract.

The persistence decision must:

- preserve the existing v0.1.4 NWR2 reminder data on load;
- preserve reminder id, text, done state, and list position across reminder-time changes;
- preserve deterministic whole-list semantics;
- not encode reminder time inside reminder text;
- not encode reminder time inside reminder id;
- not encode reminder time inside reminder done state.

## Phase model

The accepted eight-phase model for v0.1.5 is:

- Phase 0 — Release Definition & Bootstrap
- Phase 1 — Reminder Time Architecture Contract
- Phase 2 — Reminder Time Domain Implementation & JVM Proof
- Phase 3 — Persistence Compatibility / Migration Proof
- Phase 4 — Minimal Compose Integration
- Phase 5 — Integration & Device Validation
- Phase 6 — Integrated Audit & Reconciliation
- Phase 7 — Full Pre-Release Gate

Phase 0 — Release Definition & Bootstrap — is `Planned` / current / in progress. Phase 1 — Reminder Time Architecture Contract — is `Planned` / not started. Phase 2 — Reminder Time Domain Implementation & JVM Proof — is `Planned` / not started. Phase 3 — Persistence Compatibility / Migration Proof — is `Planned` / not started. Phase 4 — Minimal Compose Integration — is `Planned` / not started. Phase 5 — Integration & Device Validation — is `Planned` / not started. Phase 6 — Integrated Audit & Reconciliation — is `Planned` / not started. Phase 7 — Full Pre-Release Gate — is `Planned` / not started. Phase model: `0 Complete / 8 Planned`; no lifecycle phase has been formally closed inside the accepted eight-phase v0.1.5 model.

Phase 0 is bounded to release-definition, governance, document-bootstrap synchronization, and the initial dirty-candidate repository-consistency validation. Phase 0 does not implement any reminder-time functionality, does not change `app/build.gradle.kts`, does not select a concrete persistence representation, does not modify any product Kotlin, does not modify persistence production code, does not modify Compose, and does not perform Android identity alignment.

Phase 1 — Reminder Time Architecture Contract — owns the architecture contract and freezes the v0.1.5 persistence representation. Phase 1 is architecture-only and produces no product code, no production tests, and no Compose changes. Phase 1 forbids encoding reminder time inside reminder text, inside reminder id, or inside reminder done state. Phase 1 must not implement reminder time; Phase 2 owns the implementation and JVM proof.

Phase 2 owns the domain implementation and JVM proof after Phase 1 freezes the architecture. Phase 3 owns persistence compatibility / migration implementation and proof after Phase 1 freezes the representation. Phase 4 owns minimal Compose integration. Phase 5 owns integrated and bounded physical-device proof, including the later Android artifact identity alignment under separate explicit maintainer authorization. Phase 6 owns integrated audit plus reconciliation. Phase 7 owns the full final pre-release gate.

## Bootstrap exception

`V0_1_5_PHASE_0_BOOTSTRAP_EXCEPTION` is `ACTIVE`. The exception narrowly bridges the inherited v0.1.4 tracked release identity to the new v0.1.5 Phase 0 release context while Phase 0C synchronizes the active release context, the release charter, the phase list, and `scripts/release_contract.json`. The exception grants NO independent authority for product implementation, arbitrary mutation, staging, commit, push, network access, pull request, tag, release, dependencies, toolchain, configuration changes, or Android identity alignment. The exception remains active after Phase 0C. Termination requires later accepted validation that the v0.1.5 current-facing governance / contract synchronization is mutually consistent, plus explicit maintainer acceptance.

The historical `POST_V0_1_4_MAIN_MAINTENANCE_BOOTSTRAP_EXCEPTION` remains `TERMINATED`; it is not reactivated, renamed, or reused by this v0.1.5 exception.

## Maintenance window

The historical v0.1.4 release-bearing merge into `main`, the annotated `v0.1.4` tag, and the GitHub Release for v0.1.4 are complete. v0.1.4 is `RELEASED_AND_CLOSED`. v0.1.4 is the latest stable published release. The post-v0.1.4 / pre-v0.1.5 maintenance window is formally closed. The v0.1.5 release train is now active on the single branch `release/v0.1.5`.

## v0.1.5 release state

v0.1.5 is **not** merged, **not** tagged, **not** published, and is not release-ready. Phase 0 is `Planned` / current / in progress. Phase 1 — Reminder Time Architecture Contract — has NOT started. The formal Phase 0 → Phase 1 transition requires later independent validation and explicit maintainer acceptance. No v0.1.5 release action is authorized by this charter.

Product scope, the persistence-format decision (`PHASE_1_REQUIRED`), and the Android identity non-mutation rule (`app/build.gradle.kts` remains at `versionCode 5 / versionName 0.1.4`) remain unchanged.
