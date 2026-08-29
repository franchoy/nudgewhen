# Release Charter — NudgeWhen v0.1.3

**Document status:** v0.1.3 Phase 3 closure charter candidate — Phases 0 through 3 complete; Phase 0 — Release Definition & Bootstrap — is `Complete`; Phase 1 — Editing Architecture Contract — is `Complete`; Phase 2 — Editing Domain Implementation & JVM Proof — is `Complete`; Phase 3 — Persistence Compatibility Proof — is `Complete`; Phases 4 through 7 remain `Planned`; 4 Complete / 4 Planned. Phase 4 — Minimal Compose Editing UX — is the next lifecycle phase and has not started. This charter is normative for v0.1.3 release policy. It does not claim release readiness.

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

## Established Phase 2 outcome

Phase 2 — Editing Domain Implementation & JVM Proof — is `Complete`. The Phase 2 outcome statement is:

- the frozen edit domain API `edit(id: String, text: String): Boolean` is implemented in `ReminderController`;
- implementation commit: `7eacbe3746807a36fecc2a33aac8768f30287686` (subject `feat: implement reminder editing domain`, parent `2fa810cce63e60c06d6c2b9ad04d80c30db2368d`);
- exact-head CI run `33239803189` succeeded;
- Phase 2 repository boundary: `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`;
- the source-level controller-test count is 42 (25 existing responsibilities plus 17 edit responsibilities);
- clean B3 direct JVM validation completed with `BUILD SUCCESSFUL`;
- Phase 2 introduced no persistence production change, no Compose change, and no Android identity alignment;
- Phase 2 did not prove persistence across edit; the persistence compatibility proof is `NOT_STARTED`;
- Phase 2 did not implement any user-facing editing flow; the Compose editing UX is `NOT_STARTED`.

## Established Phase 3 outcome

Phase 3 — Persistence Compatibility Proof — is `Complete` in this closure-synchronization candidate. The Phase 3 outcome statement is:

- the bounded persistence compatibility proof is achieved through the deterministic JVM test path `app/src/test/kotlin/io/github/franchoy/nudgewhen/data/FileReminderStoreTest.kt`;
- implementation commit: `b77af048950a720482c4ec279762d51f7f65ca5f` (subject `test: prove reminder edit persistence compatibility`, parent `fa387ece5eeb972f4344ea4bd04582749b6bbf02`);
- B3 frozen SHA: `74e46f94fcfbc823911faf971124c4600f70f5d02002b5dc4e6f2a1d623aa4a7`;
- exact-head CI run `33245690596` succeeded;
- Phase 3 repository boundary: `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`;
- the 29 existing `P3_01` through `P3_29` tests are preserved;
- the 10 new `P3E_01` through `P3E_10` responsibilities are accepted;
- the source-level `FileReminderStoreTest` count is 39;
- the bounded persistence compatibility proof demonstrates: changed edit round-trip; same `id` after reload; same list index; neighbors/order/content unchanged; new store/controller restores edited text; existing valid NWR1 supports load/edit/save/reload;
- the existing `NWR1` header is unchanged;
- the existing record grammar (`<id><TAB><base64url-encoded-utf-8-text>`) is unchanged;
- the existing compatible whole-file rewrite remains the physical save behavior;
- `NWR1` migration is `NOT_REQUIRED_BY_PHASE_3_TEST_EVIDENCE`;
- Phase 3 introduced no production `FileReminderStore` change;
- Phase 3 introduced no production `ReminderController` change during Phase 3;
- Phase 3 introduced no Compose UX change;
- Phase 3 introduced no Android identity alignment;
- Phase 3 did not implement any user-facing editing flow; the Compose editing UX is `NOT_STARTED`.

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

Phase 0 — Release Definition & Bootstrap — is `Complete`. Phase 1 — Editing Architecture Contract — is `Complete`. Phase 2 — Editing Domain Implementation & JVM Proof — is `Complete`. Phase 3 — Persistence Compatibility Proof — is `Complete`. Phases 4 through 7 remain `Planned`; 4 Complete / 4 Planned. Phase 4 — Minimal Compose Editing UX — is the next lifecycle phase and has not started.

Phase 0 completed the v0.1.3 release-definition, governance, and document-bootstrap synchronization and the initial dirty-candidate repository-consistency validation. Phase 1 produced the frozen editing architecture contract at `docs/releases/v0.1.3/editing-architecture.md` (architecture commit `9004b0f90f60d2d5c8b1ac4828d0a4521316ae5a`, exact-head CI run `33183197545` succeeded). Phases 0 and 1 did not implement reminder editing. Phase 2 implemented the frozen edit domain API and the deterministic controller JVM proof on top of the existing `Reminder` model and `ReminderController` (implementation commit `7eacbe3746807a36fecc2a33aac8768f30287686`, exact-head CI run `33239803189` succeeded). Phase 3 — Persistence Compatibility Proof — proved persistence compatibility with the existing `FileReminderStore` and `NWR1` (implementation commit `b77af048950a720482c4ec279762d51f7f65ca5f`, exact-head CI run `33245690596` succeeded); the persistence compatibility proof is `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. Phase 4 — Minimal Compose Editing UX — is `Planned` and has not started; the Compose editing UX is `NOT_STARTED`.

This charter does not claim v0.1.3 is merged, tagged, published, or
complete. Release readiness: `NO`. The release is not ready.