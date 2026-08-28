# Release Charter — NudgeWhen v0.1.3

**Document status:** v0.1.3 Phase 1 closure charter — Phases 0 through 1 complete; Phase 0 — Release Definition & Bootstrap — is `Complete`; Phase 1 — Editing Architecture Contract — is `Complete`; Phases 2 through 7 remain `Planned`; 2 Complete / 6 Planned. Phase 2 — Editing Domain Implementation & JVM Proof — is the next lifecycle phase and has not started. This charter is normative for v0.1.3 release policy. It does not claim release readiness.

## Release identity

Version:
v0.1.3

Title:
NudgeWhen v0.1.3 — Editable Local Reminders

Active branch:
release/v0.1.3

Previous release:
v0.1.2

Android current identity:
versionCode 3
versionName 0.1.2

Android target identity:
versionCode 4
versionName 0.1.3

The CURRENT Android identity (versionCode 3 / versionName 0.1.2) remains unchanged during Phase 0. CURRENT identity may advance to versionCode 4 / versionName 0.1.3 only in a later separately authorized candidate that changes `app/build.gradle.kts` consistently. The TARGET Android identity is versionCode 4 / versionName 0.1.3. No `app/build.gradle.kts` change is authorized by Phase 0.

## Single product promise

A user can edit the text of an existing local reminder without deleting and
recreating it, while preserving that reminder's identity, list position,
and persistence across restart.

## Goals

The positive goals of v0.1.3 are limited to:

- textual editing of an existing local reminder;
- preserving stable reminder identity;
- preserving stable list position;
- retaining existing local persistence;
- minimal Compose integration;
- bounded deterministic domain/JVM/persistence proof;
- bounded Android/device integration proof.

## Explicit non-goals

The release does NOT add:

- completion or archive;
- new Reminder model fields;
- reorder or custom sort;
- scheduling or alarms;
- notifications;
- voice or speech;
- location or geofencing;
- contextual or device-state triggers;
- networking or sync;
- analytics or telemetry;
- background execution;
- a new Android Activity, Service, Receiver, or Provider;
- a new Android permission;
- Room or DataStore replacement;
- ViewModel, Flow, coroutines, DI, or navigation architecture solely for
  editing;
- a general Android compatibility claim;
- a production-readiness claim;
- unrelated dependency modernization;
- nudge-land / nudge-commit;
- Hermes or MCP integration.

## Product-scope authorization

The machine-recognized product scope remains exactly:

["reminders", "persistence"]

No other machine capability is authorized.

## Editing semantics resolved by Phase 1

The following editing semantics are resolved by the accepted Phase 1
architecture contract (`docs/releases/v0.1.3/editing-architecture.md`) and
are normative for v0.1.3:

- domain API: `edit(id: String, text: String): Boolean`;
- the Boolean means the edit request was accepted; it does not mean
  persisted text changed;
- the controller owns whitespace normalization (`text.trim()`);
- an invalid edit (blank or missing) returns `false` and does not save;
- an identical normalized edit returns `true` and does not save;
- a changed valid edit returns `true` and saves exactly once after
  successful save;
- reminder identity and list index are preserved;
- no `NWR1` migration; the existing compatible whole-file rewrite remains;
- `ReminderScreen` owns the edit presentation state;
- the unsaved edit buffer is discarded on Activity recreation.

No architecture semantic change is authorized in this closure synchronization.

## Phase model

The accepted eight-phase model for v0.1.3 is:

- Phase 0 — Release Definition & Bootstrap
- Phase 1 — Editing Architecture Contract
- Phase 2 — Editing Domain Implementation & JVM Proof
- Phase 3 — Persistence Compatibility Proof
- Phase 4 — Minimal Compose Editing UX
- Phase 5 — Integration & Device Validation
- Phase 6 — Integrated Audit & Reconciliation
- Phase 7 — Full Pre-Release Gate

Phase 0 — Release Definition & Bootstrap — is `Complete`. Phase 1 — Editing Architecture Contract — is `Complete`. Phases 2 through 7 remain `Planned`; 2 Complete / 6 Planned. Phase 2 — Editing Domain Implementation & JVM Proof — is the next lifecycle phase and has not started.

Phase 0 completed the v0.1.3 release-definition, governance, and document-bootstrap synchronization and the initial dirty-candidate repository-consistency validation. Phase 1 produced the frozen editing architecture contract at `docs/releases/v0.1.3/editing-architecture.md` (architecture commit `9004b0f90f60d2d5c8b1ac4828d0a4521316ae5a`, exact-head CI run `33183197545` succeeded). Phases 0 and 1 did not implement reminder editing. Phase 2 owns the editing domain implementation and deterministic JVM proof and remains `Planned`.

This charter does not claim v0.1.3 is merged, tagged, published, or
complete. The release is not ready.