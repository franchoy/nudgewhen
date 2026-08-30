# NudgeWhen v0.1.3 — Editing Architecture Contract

**Document status:** Accepted — Phase 1 Editing Architecture Contract.

Architecture repository boundary:
closed.

Architecture commit:

`9004b0f90f60d2d5c8b1ac4828d0a4521316ae5a`

Parent:

`f570055d70aa6569ec8260f9165c1f92c1580da8`

Frozen SHA-256:

`71a8c56e3515a17ebfebd4bde42be90991caab7afeb8528ca4173eec3a0630c5`

Remote branch exact SHA:

`9004b0f90f60d2d5c8b1ac4828d0a4521316ae5a`

Exact-head CI:

`33183197545`

CI result:

`success`

Phase 1:
Complete in this closure-synchronization candidate.

Phase 2:
Complete.

Phase 3:
Complete.

Phase 4:
Complete.

Phase 5:
Complete in this closure-synchronization candidate.

Phase 6:
Planned / next / not started.

Phase 7:
Planned.

Release readiness:
NO.

This document is the accepted architecture contract for the Phase 1
Editing Architecture phase of v0.1.3. It does not implement editing.
The frozen API, persistence, and UI semantics below are preserved
unchanged from the landed architecture commit and are the normative
contract for the later Phase 2+ implementation phases.

## 7A. Authority and scope

Release:
v0.1.3

Title:
NudgeWhen v0.1.3 — Editable Local Reminders

Single product promise:

A user can edit the text of an existing local reminder without deleting and
recreating it, while preserving that reminder's identity, list position, and
persistence across restart.

This document defines architecture only. It does not implement editing.

Phase 2 owns domain implementation.

Phase 3 owns persistence compatibility proof.

Phase 4 owns minimal Compose UX.

Phase 5 owns integrated/device validation and, if separately
authorized, Android identity alignment. The accepted Phase 5 outcome is
recorded in the current v0.1.3 Phase 5 synchronized lifecycle record and
in `EXP-0048`.

## 7B. Existing architecture baseline

The current architecture is recorded here as retained direct evidence from
the Phase 1 entry source tree at HEAD
`f570055d70aa6569ec8260f9165c1f92c1580da8` on branch `release/v0.1.3`:

- `Reminder`:
  `id + text` only.

- `ReminderStore`:
  whole-list load/save.

- `ReminderController`:
  current create/remove;
  controller owns normalization;
  derive -> save -> publish pattern;
  save failure propagates;
  edit absent at Phase 1 entry.

- `FileReminderStore`:
  NWR1 whole-list persistence;
  strict UTF-8;
  Base64URL text;
  list-order serialization.

- `ReminderScreen`:
  Compose-owned `remember` presentation state;
  create/remove;
  list keyed by `id`;
  no edit UI at Phase 1 entry.

- `MainActivity`:
  single Android `Activity`;
  constructs `FileReminderStore` and `ReminderController`;
  no `MutableState`.

Current Android identity:

- versionCode 3
- versionName 0.1.2

Target Android identity:

- versionCode 4
- versionName 0.1.3

Identity alignment is not Phase 1 work.

## 7C. Frozen domain edit API

Freeze conceptually:

```kotlin
fun edit(id: String, text: String): Boolean
```

The Boolean means:

- `EDIT_REQUEST_ACCEPTED`

It does **not** mean:

- `PERSISTED_TEXT_CHANGED`

Algorithm:

1. Find index by exact `id`.
2. Missing id:
   - return `false`;
   - no `save`;
   - no state mutation;
   - no `idGenerator`.
3. Normalize: `text.trim()`.
4. Normalized empty:
   - return `false`;
   - no `save`;
   - no mutation.
5. Normalized text identical to current text:
   - return `true`;
   - no `save`;
   - no mutation.
6. Changed valid text:
   - replace only the target reminder at the same index using the same
     `id`.
7. Derive the full candidate list.
8. Call `store.save(candidate)` exactly once.
9. Only after successful `save`:
   - publish the candidate controller state.
10. Return `true`.
11. If `save` throws:
    - propagate;
    - controller state remains unchanged;
    - no Boolean result is returned.

## 7D. Identity and ordering invariants

Freeze:

- `Reminder.id`:
  preserved exactly.
- Reminder index:
  preserved exactly.
- Neighboring reminders:
  unchanged.
- Neighboring order:
  unchanged.
- `idGenerator`:
  never invoked during edit.
- No new `Reminder` field.
- No reorder or sorting behavior.

## 7E. Text semantics

Freeze:

- normalization:
  `String.trim()`
- normalization owner:
  `ReminderController`
- empty:
  invalid / `false` / no save
- whitespace-only:
  invalid / `false` / no save
- exact identical:
  accepted `true` / no save
- normalized-identical:
  accepted `true` / no save
- changed normalized non-empty:
  accepted `true` / save once
- Unicode:
  supported as ordinary `Reminder.text`

No parsing for:

- date
- time
- priority
- voice
- context
- location
- schedule
- metadata
- rich text

## 7F. Persistence compatibility

Freeze:

- `NWR1_FORMAT`:
  `NO_MIGRATION`
- `PHYSICAL_SAVE_BEHAVIOR`:
  `EXISTING_COMPATIBLE_WHOLE_FILE_REWRITE`

Explain:

- The existing NWR1 record remains:
  `<id><TAB><base64url-encoded-utf-8-text>`.
- Editing changes only the text.
- Same `id`.
- Same list position.
- No new format marker.
- No new field.
- No filename change.
- No backend change.
- No migration.
- No production `FileReminderStore` change expected.

Retain the existing storage correctness boundary:

- `FileReminderStore` validates complete input before write.
- Controller publishes new state only after `save` succeeds.
- Actual filesystem I/O failure does **not** gain a new rollback guarantee.

## 7G. Compose editing contract

Freeze:

- state owner:
  `ReminderScreen`
- additional conceptual state:
  - `editingId: String?`
  - `editBuffer: String`
- derived conceptual active-editing identity:
  - `activeEditingId`:
    the non-null id of the reminder currently in edit mode;
    defined only while a row is in editing row state;
    non-null by construction because Save is rendered /
    invoked only for the active editing row.
- ordinary `remember(controller)` state.
- No `rememberSaveable` solely for editing.
- At most one edit at a time.

Normal row:

- Text
- Edit `TextButton`
- Remove `TextButton`

Editing row:

- `OutlinedTextField`
- Save `TextButton`
- Cancel `TextButton`

No simultaneous Remove is required in the editing row.

Edit:

- prefill buffer with current text;
- set `editingId`;
- entering edit for another reminder discards the previous unsaved buffer.

Save:

Save is available only for the row currently in edit mode. The conceptual
Save call therefore passes the explicit non-null active-editing id, not
the nullable `editingId` state directly:

```
accepted = controller.edit(activeEditingId, editBuffer)
```

`activeEditingId` is non-null by construction because Save is rendered /
invoked only for the active editing row.

Only after normal return AND `accepted == true`:

- refresh `reminders` from `controller.reminders`;
- exit edit mode;
- clear edit buffer.

`accepted == false`:

- remain editing;
- retain edit buffer;
- no success transition.

`controller.edit` throws:

- no post-success UI transition;
- do not swallow solely for editing;
- do not clear edit state as though Save succeeded;
- detailed persistence-error UX remains outside v0.1.3.

Cancel:

- no controller call;
- exit edit mode;
- clear edit buffer.

Create input remains independent and usable.

- No `ViewModel`.
- No `Flow`.
- No coroutines.
- No DI.
- No navigation.

`MainActivity` is unchanged.

## 7H. Activity recreation

Freeze:

- `SAVED_REMINDER_STATE`:
  restored from existing local persistence through a newly constructed
  `FileReminderStore` / `ReminderController`.
- `UNSAVED_EDIT_BUFFER`:
  discarded.

No `rememberSaveable` is required.

This intentionally matches the existing create-input lifecycle. The release
promise concerns persisted successful edits, not unsaved drafts.

## 7I. Phase 2 deterministic test contract

Record the minimum required controller proof:

- changed edit returns `true`;
- only the target text changes;
- `id` preserved;
- index preserved;
- neighbors/order unchanged;
- trim normalization;
- empty `false` / no save;
- whitespace `false` / no save;
- missing `id` `false` / no save;
- exact identical `true` / no save;
- normalized-identical `true` / no save;
- changed edit saves exactly once with full candidate;
- `idGenerator` not invoked;
- old state exposed during save;
- save failure propagates;
- save failure preserves previous state;
- Unicode supported.

## 7J. Phase 3 deterministic persistence contract

Record the minimum persistence proof:

- changed edit round-trip;
- same `id` after reload;
- same list position;
- neighbors/order/content unchanged;
- new store/controller restores edited text;
- existing valid NWR1 load -> edit -> save -> reload;
- exact NWR1 header unchanged;
- record grammar unchanged;
- Unicode edit round-trip;
- no migration.

## 7K. Phase ownership and expected path boundary

Phase 2 expected:

- `app/src/main/kotlin/io/github/franchoy/nudgewhen/domain/ReminderController.kt`
- `app/src/test/kotlin/io/github/franchoy/nudgewhen/domain/ReminderControllerTest.kt`

Phase 3 expected:

- `app/src/test/kotlin/io/github/franchoy/nudgewhen/data/FileReminderStoreTest.kt`

Phase 4 expected:

- `app/src/main/kotlin/io/github/franchoy/nudgewhen/ui/ReminderScreen.kt`

Not expected to change for the edit feature itself:

- `Reminder.kt`
- `ReminderStore.kt`
- `FileReminderStore.kt` production source
- `MainActivity.kt`
- `AndroidManifest.xml`

Android identity alignment is owned by a later, separately authorized
Phase 5 boundary.

## 7L. Explicit non-goals

Repeat the v0.1.3 non-goals accurately:

- completion / archive
- new `Reminder` fields
- reorder / custom sort
- scheduling / alarms
- notifications
- voice / speech
- location / geofencing / context / device-state triggers
- networking / sync
- analytics / telemetry
- background execution
- new Android `Activity` / `Service` / `Receiver` / `Provider`
- new Android permission
- Room / DataStore
- `ViewModel` / `Flow` / coroutines / DI / navigation solely for editing
- general Android compatibility claim
- production-readiness claim
- unrelated dependency modernization
- nudge-land / nudge-commit
- Hermes / MCP

Product scope remains:

```json
["reminders", "persistence"]
```

## 7M. Acceptance boundary and later phases

Historical architecture starting state:

- HEAD `f570055d70aa6569ec8260f9165c1f92c1580da8` on `release/v0.1.3`
  was the Phase 1 entry baseline;
- no editing API existed in `ReminderController`;
- `NWR1` and `FileReminderStore` were complete with no edit operation;
- `ReminderScreen` and `MainActivity` were complete with no edit UI;
- Phase 1 produced architecture only and no product code.

Accepted architecture decisions (frozen):

- domain API: `edit(id: String, text: String): Boolean`;
- Boolean means the edit request was accepted;
- controller owns `text.trim()` normalization;
- invalid blank / whitespace-only / missing-id edits are `false` with no
  save;
- identical normalized edits are `true` with no save;
- changed valid edits are `true` with save exactly once after successful
  save;
- reminder identity, list index, and neighbor order are preserved;
- `NWR1` format remains with no migration and no new field;
- existing compatible whole-file rewrite remains the physical save
  behavior;
- `ReminderScreen` owns the edit presentation state (`editingId`,
  `editBuffer`) via ordinary `remember(controller)`;
- Save passes an explicit non-null `activeEditingId` derived from the
  active editing row, not the nullable `editingId` state directly;
- the unsaved edit buffer is discarded on Activity recreation; no
  `rememberSaveable` is required for editing.

Later Phase 2+ implementation (not authorized by this document):

- Phase 2 owns the editing domain implementation and deterministic JVM
  proof on top of the existing `Reminder` model and `ReminderController`;
- Phase 3 owns persistence compatibility proof;
- Phase 4 owns minimal Compose editing UX;
- Phase 5 owns later integrated/device validation and, if separately
  authorized, Android identity alignment.

Architecture repository boundary:

- architecture commit: `9004b0f90f60d2d5c8b1ac4828d0a4521316ae5a`
  (parent `f570055d70aa6569ec8260f9165c1f92c1580da8`);
- frozen SHA-256:
  `71a8c56e3515a17ebfebd4bde42be90991caab7afeb8528ca4173eec3a0630c5`;
- remote branch exact SHA:
  `9004b0f90f60d2d5c8b1ac4828d0a4521316ae5a`;
- exact-head CI: `33183197545`, result `success`;
- architecture repository boundary: closed.

Phase lifecycle in this closure-synchronization candidate:

- Phase 0 `Complete`
- Phase 1 `Complete`
- Phase 2 `Complete`
- Phase 3 `Complete`
- Phase 4 `Complete`
- Phase 5 `Complete`
- Phase 6 `Planned` / next / not started
- Phase 7 `Planned`

Release readiness is **not** claimed. The v0.1.3 release is not merged,
not tagged, not published, and not release-ready.
