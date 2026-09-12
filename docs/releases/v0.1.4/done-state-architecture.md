# NudgeWhen v0.1.4 — Done-State Architecture Contract

## Status

This document is the frozen Phase-1 architecture contract for the active
NudgeWhen v0.1.4 release on branch `release/v0.1.4`.

It defines Phase-1 architecture only.

It does not implement done state.

It is normative for later Phase 2, Phase 3, and Phase 4 implementation.

Current release: `v0.1.4`.

Active branch: `release/v0.1.4`.

Product scope: `["reminders", "persistence"]`.

Current Android identity: `versionCode 4 / versionName 0.1.3`.

Target Android identity: `versionCode 5 / versionName 0.1.4`.

Android identity alignment is not Phase-1 work.

Phase 1 remains `Planned / NOT_STARTED` until this architecture candidate
is independently audited and separately landed.

This document does not claim that Phase 1 is landed, committed, pushed,
or CI accepted.

## 1. Domain Model Contract

Freeze the following exact Reminder model:

```kotlin
data class Reminder(
    val id: String,
    val text: String,
    val done: Boolean = false,
)
```

Contract:

* `done` is a non-null `Boolean`.
* The default value of `done` is `Boolean = false`.
* The existing two-argument Reminder construction remains
  source-compatible; existing call sites continue to compile unchanged.
* `Reminder` remains immutable.
* Done-state updates replace the whole Reminder value rather than mutate
  it in place.
* `done` participates in `equals` and `hashCode`.
* Identity remains the `id` field; `done` is a property of an existing
  reminder and does not introduce a separate identity dimension.
* Newly created reminders default to `done = false`.
* Legacy NWR1 reminders load with `done = false`.

## 2. Controller Contract

Freeze the following exact controller method:

```kotlin
fun setDone(id: String, done: Boolean): Boolean
```

Exact semantics:

EXISTING ID + DIFFERENT STATE:

* Return `true`.
* Derive the candidate Reminder at the same index.
* Preserve the reminder's `id`.
* Preserve the reminder's `text`.
* Apply the requested `done` value.
* Save exactly once.
* Publish the candidate only after the save succeeds.

EXISTING ID + SAME STATE:

* Return `true`.
* Do not save.
* Do not mutate.

MISSING / NON-MATCHING ID:

* Return `false`.
* Do not save.
* Do not mutate.

EXTERNAL INVALID OR NON-MATCHING ID:

* No new validation layer is added.
* Behavior follows the missing-id path.

SAVE FAILURE:

* The original exception propagates unchanged.
* No `Boolean` result is produced.
* Controller state remains unchanged.

Boolean meanings:

`true` means `SET_DONE_REQUEST_ACCEPTED`.

`false` means `REMINDER_ID_NOT_FOUND`.

No other meaning is assigned to `false`.

No `idGenerator` invocation occurs on any `setDone` path.

## 3. Edit / Create / Remove Interoperability

Freeze the following interoperability rules:

* `edit(done = false)` preserves `done = false`.
* `edit(done = true)` preserves `done = true`.
* `setDone` preserves the reminder's `text`.
* `edit` preserves the reminder's `done` value.
* `create` produces a new reminder with `done = false`.
* `remove` treats done and not-done reminders identically.
* No reorder, sort, archive, or delete side effect arises from
  `setDone`.

The current edit replacement must be adapted in Phase 2 so that it does
not reset `done` to `false`.

Acceptable implementation semantics include:

```kotlin
copy(text = normalizedText)
```

or any equivalent explicit construction that preserves the existing
`done` value.

The exact Phase-2 implementation syntax is not mandated by this
architecture contract.

## 4. Phase-2 Persistence Boundary

Freeze the following Phase-2 boundary:

* Phase 2 changes the model and controller only.
* Phase 2 does not modify `FileReminderStore`.
* Phase 2 therefore does not claim durable done-state survival through
  the real file store.
* Phase-2 JVM proof uses the existing fake `ReminderStore` seam.
* No user-facing Compose path invokes `setDone` before Phase 4.

## 5. NWR2 Persistence Contract

Freeze `NWR2` as the future Phase-3 write format.

Exact grammar:

```text
NWR2
<id><TAB><base64url-encoded-utf-8-text><TAB><done>
...
```

Done literals:

`0` represents `false`.

`1` represents `true`.

No other done literal is valid on load.

Each NWR2 record:

* Contains exactly two `<TAB>` separators.
* Contains exactly three fields.

Text field encoding:

* Strict UTF-8 bytes.
* Base64URL with padding.

Line separator: LF only.

Trailing LF: forbidden.

Blank record: forbidden.

Duplicate ids: forbidden.

ID validation: preserve existing rules.

Whole-list ordering: preserved exactly.

## 6. Exact NWR2 Examples

False:

```text
NWR2
id-1	SGVsbG8=	0
```

Escaped:

`NWR2\nid-1\tSGVsbG8=\t0`

True:

```text
NWR2
id-1	SGVsbG8=	1
```

Escaped:

`NWR2\nid-1\tSGVsbG8=\t1`

A one-TAB NWR2 example is not permitted and is never emitted by a valid
save.

## 7. NWR2 Validation Contract

SAVE SIDE:

Because `Reminder.done` is a non-null Boolean:

* `false` serializes as `0`.
* `true` serializes as `1`.
* No other textual done literal can be emitted from a valid Reminder.
* There is no invalid-done-literal save-side error contract for the
  done field itself.

Retain actual save-side validation for:

* Invalid id.
* Duplicate id.
* Complete-list validation before write.

LOAD SIDE:

* `0` decodes to `false`.
* `1` decodes to `true`.
* Any other done field value is malformed input.
* A malformed done literal raises `IllegalStateException`.

## 8. Physical Storage Path

Freeze:

`filesDir/reminders-v1.txt`

The wire format changes from NWR1 to NWR2.

The physical file location does not change.

No second persistence file is introduced.

`MainActivity` does not change merely because NWR2 is introduced.

Reason: existing v0.1.3 device data must continue to be discovered at
the same path.

## 9. Legacy NWR1 Contract

A valid NWR1 file:

```text
NWR1
<id><TAB><base64url-encoded-utf-8-text>
...
```

must load successfully.

Every NWR1 record loads with `done = false`.

Preserve:

* `id`.
* `text`.
* List order.

Load alone does NOT rewrite the file.

The first later successful save rewrites the same physical file as
NWR2.

Accepted or no-save operations do NOT migrate.

Explicit examples:

* Legacy `setDone(id, false)` when already `false`:
  returns `true` with no save; the file remains NWR1.
* Identical edit:
  returns `true` with no save; the file remains NWR1.
* Changed edit:
  successful save migrates the file to NWR2.
* Create:
  successful save migrates the file to NWR2.
* Remove:
  successful save migrates the file to NWR2.
* State-changing `setDone`:
  successful save migrates the file to NWR2.

## 10. Save / Failure Semantics

Freeze the derive -> save -> publish order.

State-changing `setDone`:

* Derives the candidate Reminder.
* Calls `save` exactly once.
* The old controller state remains observable during the save.
* Publishes the candidate only after the save succeeds.

If `save` throws:

* The exception propagates unchanged.
* The old controller state remains.
* No `Boolean` result is produced.

No rollback layer is added because controller state is not published
before a successful save.

Preserve `FileReminderStore`'s complete-input-validation-before-write
boundary.

## 11. Identity / Order Invariants

Freeze:

* Same `id` on `setDone`.
* Same `text` on `setDone`.
* Same `index` on `setDone`.
* Same neighboring reminders.
* Same neighboring order.
* No done-based sorting.
* No movement to top or bottom.
* No archive.
* No automatic removal.

Whole-list persistence preserves list order exactly.

## 12. Future UI Contract

Phase 4 only.

Freeze one controlled Material 3 `Checkbox` per reminder.

Checked state:

`checked = reminder.done`

Conceptual action:

`controller.setDone(reminder.id, newChecked)`

Only after normal return AND `accepted == true`:

`reminders = controller.reminders`

When the result is `false`:

* No success transition occurs.
* The existing list is retained.

On exception:

* Do not optimistically publish the checked state.
* Do not refresh as if the save had succeeded.
* Do not swallow the persistence exception solely for done state.

Detailed persistence-error UX remains outside the v0.1.4 scope.

## 13. Done / Edit UI Interoperability

Freeze the following behavior:

Done state remains available while text editing is active.

A successful done-state change:

* Persists immediately.
* Refreshes the reminders list.
* Does not clear `editingId`.
* Does not clear `editBuffer`.
* Does not save `editBuffer`.
* Does not cancel `editBuffer`.

A later edit Save preserves the reminder's `done` value.

A later edit Cancel discards only the text buffer; it does not undo the
persisted done state.

On Activity recreation:

* The persisted done state is restored.
* An unsaved edit buffer is discarded.
* No pending done-state buffer is retained.

No `ViewModel`, `Flow`, coroutines, DI, or navigation expansion is
introduced solely for done state.

## 14. Phase-2 JVM Proof Obligations

Freeze obligations only; do not write tests in Phase 1.

Include at minimum:

* Two-argument Reminder defaults `done = false`.
* Equality includes `done`.
* `setDone` transitions `false -> true`.
* `setDone` transitions `true -> false`.
* Same-state `setDone` returns `true` with no save.
* Missing-id `setDone` returns `false` with no save.
* `id` is preserved by `setDone`.
* `text` is preserved by `setDone`.
* `index` is preserved by `setDone`.
* Neighbors and order are preserved by `setDone`.
* Exactly one save occurs on a changed state.
* No `idGenerator` invocation occurs on any `setDone` path.
* The old controller state remains observable during the save.
* A save failure propagates as an exception.
* A save failure preserves the old controller state.
* `create` defaults `done = false`.
* `edit` preserves `done = false`.
* `edit` preserves `done = true`.
* `setDone` after `edit` preserves the edited text.
* `edit` after `setDone` preserves the done state.
* `remove` works normally for done reminders.

Explicitly state: real-file NWR1 / NWR2 proof is NOT a Phase 2
obligation.

## 15. Phase-3 Persistence Proof Obligations

Freeze obligations only; do not freeze a numerical test total in this
document.

Include at minimum:

* NWR2 empty-list header.
* NWR2 false record.
* NWR2 true record.
* Mixed done-state round trip.
* Exact ordering.
* Unicode handling.
* Same id, text, and order.
* Fresh store/controller reload.
* NWR1 backward load.
* NWR1 defaults `done = false`.
* NWR1 load alone preserves the original bytes.
* NWR1 state-changing `setDone` plus save -> NWR2.
* NWR1 changed edit plus save -> NWR2.
* NWR1 create plus save -> NWR2.
* NWR1 remove plus save -> NWR2.
* An idempotent no-save operation leaves NWR1 unchanged.
* Invalid NWR2 done literal rejected on LOAD.
* Missing or extra TAB fields rejected.
* Unsupported header rejected.
* Duplicate ids rejected.
* Strict UTF-8 enforcement.
* Base64URL validation.
* No trailing LF.
* Full-list validation before write.

Do NOT add an invalid textual done-literal save-side test contract.

## 16. Existing Persistence-Test Reconciliation

Explicitly classify at least:

* `P3_03`: revision required — NWR1 -> NWR2 empty save.
* `P3_04`: revision required — NWR1 two-field -> NWR2 three-field
  record.
* `P3_08`: revision required — NWR1 header / one-TAB assertions become
  NWR2 / two-TAB assertions.
* `P3E_06`: scenario retained; the post-save format becomes NWR2.
* `P3E_07`: revision required — the post-save header becomes NWR2.
* `P3E_08`: revision required — the post-save record grammar becomes
  NWR2.
* `P3E_10`: revision required — replace the no-migration contract with
  load-only-no-migration plus first-successful-save migration.

State explicitly:

* Tests whose semantics remain valid may be retained.
* No final Phase-3 test total is frozen by this architecture document.

## 17. Persistence Option Rationale

NWR1 extension is technically viable.

It is NOT rejected because of ambiguity.

Two-field legacy versus three-field extension is deterministic because
the id and Base64URL text cannot contain a TAB character.

NWR2 is preferred because:

* Explicit version signaling.
* One grammar per header.
* Clearer migration boundary.
* Cleaner future evolution.
* Easier forensic and debug interpretation.

## 18. Phase Boundaries

Phase 1: architecture contract only.

Phase 2: add the `Reminder.done` field, implement the `setDone`
controller behavior, satisfy the edit / create / remove
interoperability rules, and produce the domain / controller JVM proof.

Phase 3: add dual NWR1 / NWR2 load, NWR2 writes, lazy same-file
migration, persist the reconciliation of existing persistence tests,
and produce the persistence JVM proof.

Phase 4: add the minimal controlled Material 3 Checkbox UI.

Phase 5: integrated validation; the separately authorized Android
identity alignment to `versionCode 5 / versionName 0.1.4`; bounded
device acceptance.

Phase 6: integrated audit and reconciliation.

Phase 7: full pre-release gate.

## 19. Document Non-Goals

This architecture contract explicitly does not authorize or require any
of the following:

* Archive.
* Automatic removal.
* Completed-history screen.
* Filtering.
* Reorder or custom sort.
* Priority.
* Checklist or sub-items.
* Scheduling.
* Alarms.
* Notifications.
* Voice or speech.
* Location, geofencing, context, or device triggers.
* Networking or sync.
* Analytics.
* Product background execution.
* New Android component.
* New Android permission.
* Room or DataStore migration.
* `ViewModel`, `Flow`, coroutines, DI, or navigation solely for done
  state.
* Unrelated dependency modernization.
* AGP 9.4.
* Gradle 9.6.
* Nudge-land product functionality.
* Hermes / MCP integration.