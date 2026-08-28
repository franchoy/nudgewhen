# Release Charter — NudgeWhen v0.1.3

**Document status:** v0.1.3 Phase 0 closure charter — Phases 0 through 0 complete; Phase 0 — Release Definition & Bootstrap — is `Complete`; Phases 1 through 7 remain `Planned`; 1 Complete / 7 Planned. Phase 1 — Editing Architecture Contract — is the next lifecycle phase and has not started. This charter is normative for v0.1.3 release policy. It does not claim release readiness.

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

## Editing semantics deferred to Phase 1

The following editing semantics are explicitly deferred to Phase 1 and are
not decided by this charter:

- edit whitespace normalization;
- whitespace-only edit behavior;
- identical-text edit behavior;
- save/cancel interaction;
- edit widget or affordance;
- edit-buffer behavior across Activity recreation.

Phase 1 owns the exact editing semantics contract.

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

Phase 0 — Release Definition & Bootstrap — is `Complete`. Phases 1 through 7 remain `Planned`; 1 Complete / 7 Planned. Phase 1 — Editing Architecture Contract — is the next lifecycle phase and has not started.

Phase 0 completed the v0.1.3 release-definition, governance, and document-bootstrap synchronization and the initial dirty-candidate repository-consistency validation. Phase 0 did not implement reminder editing. Phase 1 owns the Editing Architecture Contract and remains `Planned`.

This charter does not claim v0.1.3 is merged, tagged, published, or
complete. The release is not ready.