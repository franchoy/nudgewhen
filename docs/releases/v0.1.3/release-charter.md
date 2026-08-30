# Release Charter — NudgeWhen v0.1.3

**Document status:** v0.1.3 Phase 5 closure charter candidate — Phases 0 through 5 complete; Phase 0 — Release Definition & Bootstrap — is `Complete`; Phase 1 — Editing Architecture Contract — is `Complete`; Phase 2 — Editing Domain Implementation & JVM Proof — is `Complete`; Phase 3 — Persistence Compatibility Proof — is `Complete`; Phase 4 — Minimal Compose Editing UX — is `Complete`; Phase 5 — Integration & Device Validation — is `Complete` in this closure-synchronization candidate; Phase 6 — Integrated Audit & Reconciliation — is the next lifecycle phase and remains `Planned`; Phase 7 — Full Pre-Release Gate — remains `Planned`; 6 Complete / 2 Planned. This charter is normative for v0.1.3 release policy. It does not claim release readiness.

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

versionCode 4
versionName 0.1.3

Android target identity:

versionCode 4
versionName 0.1.3

Phase 5-B advanced CURRENT identity to 4 / 0.1.3 under separate authorization and landed that identity at commit `1cfb9c373abfa24cf10f23daa152f4a410932d26`.
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

## Established Phase 4 outcome

Phase 4 — Minimal Compose Editing UX — is `Complete` in this closure-synchronization candidate. The Phase 4 outcome statement is:

- Phase 4 is `Complete` in this closure-synchronization candidate;
- the bounded Compose editing UX is implemented on the existing `ReminderScreen`; the exact implementation path is `app/src/main/kotlin/io/github/franchoy/nudgewhen/ui/ReminderScreen.kt`;
- implementation commit: `673951082061562b45a40096bc2f9f5debdfb72d` (subject `feat: add reminder editing ux`, parent `938a38c7b2ba659e11eb31588b3a21526f180492`);
- B3 frozen candidate SHA: `322c57bb2adfa192e0eb3115e9bfb5233bc7e29beb18a2ef9641411be9bb3add`;
- exact-head CI run `33250408328` succeeded;
- Phase 4 repository boundary: `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`;
- no Phase 4 test path was added;
- the B2 semantic audit accepted `P4_01` through `P4_20`;
- `ReminderScreen` owns the editing presentation state (`editingId: String?`, `editBuffer: String`);
- ordinary `remember(controller)` is the editing state holder;
- a normal row renders reminder text plus Edit and Remove `TextButton`s;
- an editing row renders an `OutlinedTextField` plus Save and Cancel `TextButton`s;
- Save derives the explicit non-null `activeEditingId` from the active editing row and calls `controller.edit(activeEditingId, editBuffer)`; only on accepted `true` does Save refresh `controller.reminders`, exit edit mode, and clear `editBuffer`;
- a normalized-identical accepted `true` also exits edit mode;
- an accepted `false` retains the editing state and `editBuffer`;
- a thrown `controller.edit` causes no success transition;
- Cancel performs no controller mutation, exits edit mode, and clears `editBuffer`;
- the create input remains independent and usable during editing;
- the `LazyColumn` row key remains the stable `reminder.id`;
- no reorder or sort behavior was introduced;
- Phase 4 introduced no `MainActivity` change;
- Phase 4 introduced no `Reminder` model change;
- Phase 4 introduced no Phase 4 production `ReminderController` change;
- Phase 4 introduced no persistence production change;
- Phase 4 introduced no dependency change;
- Phase 4 introduced no Android identity alignment;
- user-facing textual editing is `IMPLEMENTED_AT_SOURCE_LEVEL`;
- integrated/device validation is `NOT_STARTED`.

## Established Phase 5 outcome

Phase 5 — Integration & Device Validation — is `Complete` in this closure-synchronization candidate. The Phase 5 outcome statement is:

- Phase 5 is `Complete` in this closure-synchronization candidate;
- Phase 5-B Android identity implementation commit: `1cfb9c373abfa24cf10f23daa152f4a410932d26` (subject `chore: align v0.1.3 android identity`, parent `3ba8470918a28acd4376639cf061f20209f78735`);
- Phase 5-B identity implementation paths: `app/build.gradle.kts` and `scripts/release_contract.json`;
- Phase 5-B exact-head identity CI: `33255108409 / success`;
- Phase 5-C integrated full offline validation at HEAD `1cfb9c373abfa24cf10f23daa152f4a410932d26`: Python validator regression `100 tests / OK`; `required` `11/0/0`; `docs` `11/0/0`; full offline `39/0/0`; `release_gate=SATISFIED`;
- frozen debug APK path: `app/build/outputs/apk/debug/app-debug.apk`;
- frozen APK SHA-256: `209bfb2a11628a903d7163ca807776a01aeb107e9fbe4c7168e6984a715f8908`;
- frozen APK identity: package `io.github.franchoy.nudgewhen`, `versionCode 4`, `versionName 0.1.3`;
- P5_01 through P5_13: `PASS`;
- physical runtime evidence: `ONE_PHYSICAL_DEVICE_ONLY`;
- general Android compatibility: `NOT_CLAIMED`;
- multi-device validation: `NOT_CLAIMED`;
- production readiness: `NOT_CLAIMED`;
- supported Android version range: `NOT_CLAIMED`;
- original D1 `adb install` CLI failure: `FAIL_PRESERVED`;
- accepted D1-R1, D1-R2, and D1-R3 recovery: installed bytes exactly matched the frozen Phase 5-C APK and physical `MainActivity` cold launch was observed;
- D2-A-R3: accepted edit, list-position preservation, and restart-persistence evidence;
- D2-B-R1: accepted Cancel / whitespace / create / remove / restart evidence;
- Phase 5 introduced no new Android permission, no new Android component, no new Gradle dependency, no new test dependency, and no validator-architecture change;
- Phase 6 is `NOT_STARTED`.

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

Phase 0 — Release Definition & Bootstrap — is `Complete`. Phase 1 — Editing Architecture Contract — is `Complete`. Phase 2 — Editing Domain Implementation & JVM Proof — is `Complete`. Phase 3 — Persistence Compatibility Proof — is `Complete`. Phase 4 — Minimal Compose Editing UX — is `Complete`. Phase 5 — Integration & Device Validation — is `Complete` in this closure-synchronization candidate. Phases 6 and 7 remain `Planned`. Phase model: 6 Complete / 2 Planned. Phase 6 — Integrated Audit & Reconciliation — is the next lifecycle phase, remains `Planned`, and has not started. Phase 7 — Full Pre-Release Gate — remains `Planned`.

Phase 0 completed the v0.1.3 release-definition, governance, and document-bootstrap synchronization and the initial dirty-candidate repository-consistency validation. Phase 1 produced the frozen editing architecture contract at `docs/releases/v0.1.3/editing-architecture.md` (architecture commit `9004b0f90f60d2d5c8b1ac4828d0a4521316ae5a`, exact-head CI run `33183197545` succeeded). Phases 0 and 1 did not implement reminder editing. Phase 2 implemented the frozen edit domain API and the deterministic controller JVM proof on top of the existing `Reminder` model and `ReminderController` (implementation commit `7eacbe3746807a36fecc2a33aac8768f30287686`, exact-head CI run `33239803189` succeeded). Phase 3 — Persistence Compatibility Proof — proved persistence compatibility with the existing `FileReminderStore` and `NWR1` (implementation commit `b77af048950a720482c4ec279762d51f7f65ca5f`, exact-head CI run `33245690596` succeeded); the persistence compatibility proof is `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. Phase 4 — Minimal Compose Editing UX — has landed the bounded Compose editing UX on `ReminderScreen` (implementation commit `673951082061562b45a40096bc2f9f5debdfb72d`, exact-head CI run `33250408328` succeeded); the Compose editing UX is `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. Phase 5 — Integration & Device Validation — has landed the Android current-identity alignment to `versionCode 4 / versionName 0.1.3` (commit `1cfb9c373abfa24cf10f23daa152f4a410932d26`, exact-head CI run `33255108409` succeeded) and accepted the integrated local validation together with the bounded one-physical-device runtime evidence; the Phase 5 technical boundary is `COMPLETE` and runtime evidence is explicitly scoped to `ONE_PHYSICAL_DEVICE_ONLY`.

This charter does not claim v0.1.3 is merged, tagged, published, or
complete. Release readiness: `NO`. The release is not ready.