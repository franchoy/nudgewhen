# NudgeWhen v0.1.5 — Reminder-Time Architecture Contract

## Status

**Document status:** Phase-1 architecture **candidate** — awaiting independent review and maintainer acceptance.

This document is the proposed Phase-1 architecture contract for the active
NudgeWhen v0.1.5 release on branch `release/v0.1.5`.

It is a **candidate**. It is not frozen, not formally accepted, and it does not
close Phase 1. It becomes normative for Phase 2, Phase 3, and Phase 4 only if
the maintainer accepts it.

It defines Phase-1 architecture only. It implements no reminder-time behavior,
no product code, no production test, and no Compose change.

Current release: `v0.1.5`.

Active branch: `release/v0.1.5`.

Product scope: `["reminders", "persistence"]`.

Current Android identity: `versionCode 5 / versionName 0.1.4`.

Target Android identity: `versionCode 6 / versionName 0.1.5` — future target
only; Android identity alignment is Phase-5 work under separate explicit
maintainer authorization, and is not Phase-1 work.

Persistence-format decision: currently `PHASE_1_REQUIRED` as recorded by
Phase 0. This candidate proposes `NWR3` (§4). The recorded decision changes
only upon maintainer acceptance of this document.

Phase 1 status before the authoring Build: `Planned / NOT_STARTED`. This
document does not change that status.

## 0. Purpose, scope, and evidence base

### 0.1 Purpose

This contract decides, for the v0.1.5 **Set Reminder Time** release:

* the domain representation of an optional reminder time (§1);
* the precision, validity, and canonical representation rules for that value
  (§2);
* the controller API for setting, changing, and clearing a reminder time (§3);
* the on-disk persistence representation and its legacy-compatibility
  behavior (§4, §5);
* the rejected alternatives and their trade-offs (§6);
* the persistence test obligations that the frozen representation creates for
  Phase 3 (§7);
* the Compose UI boundary and the draft/commit separation (§8);
* the phase ownership of every resulting implementation obligation (§9).

### 0.2 In scope and out of scope

In scope: architecture decisions only.

Out of scope: all implementation. Phase 1 produces no product code, no
production test, no Compose change, no Gradle change, no validator change, no
CI change, and no Android identity change.

### 0.3 Evidence base

Every statement about existing behavior in this document derives from files
read directly at the recorded starting commit
`3605975ee5bd00c7c7837556dee8d2c0d2ca4fe2` on branch `release/v0.1.5`:

| Observed source | Used for |
|---|---|
| `docs/releases/v0.1.5/release-charter.md` | product promise, non-goals, persistence-decision boundary |
| `docs/releases/v0.1.5/phase-list.md` | phase ordering and per-phase scope |
| `app/src/main/kotlin/io/github/franchoy/nudgewhen/domain/Reminder.kt` | current domain model |
| `app/src/main/kotlin/io/github/franchoy/nudgewhen/domain/ReminderController.kt` | current controller contract, including `setDone` |
| `app/src/main/kotlin/io/github/franchoy/nudgewhen/data/FileReminderStore.kt` | current wire format, load/save guarantees |
| `app/src/main/kotlin/io/github/franchoy/nudgewhen/ui/ReminderScreen.kt` | current Compose state ownership |
| `app/src/main/kotlin/io/github/franchoy/nudgewhen/MainActivity.kt` | current wiring and file location |
| `app/build.gradle.kts` | `minSdk`, dependency inventory, current Android identity |
| `app/src/test/kotlin/io/github/franchoy/nudgewhen/data/FileReminderStoreTest.kt` | current persistence test obligations (§7) |
| `docs/releases/v0.1.4/done-state-architecture.md` | historical architecture-document structure |

## 1. Domain Model Contract

### 1.1 Frozen proposal

Propose extending the existing immutable data class as follows:

```kotlin
package io.github.franchoy.nudgewhen.domain

import java.time.LocalDateTime

data class Reminder(
    val id: String,
    val text: String,
    val done: Boolean = false,
    val time: LocalDateTime? = null,
)
```

### 1.2 Contract

* `time` is a **nullable** `java.time.LocalDateTime` with default value
  `null`.
* The value represents an optional **local wall-clock** date and time. It
  carries no timezone, no UTC offset, no zone identifier.
* Reaching the stored time performs **no** automatic action. The application
  does not wake, notify, ring, vibrate, schedule an alarm, or run background
  work because a reminder's time has arrived.
* `Reminder` remains immutable. Reminder-time updates replace the whole
  `Reminder` value rather than mutating it in place.
* `time` participates in `equals`, `hashCode`, and `copy`.
* Source compatibility is preserved:
  * the existing two-argument construction `Reminder(id, text)` remains valid
    and yields `done = false`, `time = null`;
  * the existing three-argument construction `Reminder(id, text, done)`
    remains valid and yields `time = null`.
* Newly created reminders default to `time = null`.
* Legacy loads default to `time = null` (§5).
* Identity remains the `id` field. `time` is a property of an existing
  reminder and does not introduce a separate identity dimension.
* The reminder time is stored **only** in this field. It is never encoded in
  the reminder text, never encoded in the reminder id, and never encoded in
  the reminder done state.
* The reminder list remains a single ordered list. The reminder time does not
  introduce a sort, reorder, removal, dimming, or text-decoration rule.

### 1.3 Platform availability

`app/build.gradle.kts` observes `minSdk = 26`. The `java.time` package is
available from API level 26, so `LocalDateTime` requires **no** core-library
desugaring dependency and **no** Gradle change. No dependency is added by
this contract.

`app/build.gradle.kts` also observes `compileSdk = 37`, `targetSdk = 36`, and
Java 17 source/target compatibility.

## 2. Time Precision and Validity Contract

### 2.1 Precision

Propose **minute precision**.

An accepted non-null value must satisfy:

```kotlin
second == 0 && nano == 0
```

A value carrying seconds or a fractional component is **rejected**, not
silently truncated. Truncation would make the stored value differ from the
value the user chose and would make equality between two logically identical
reminders ambiguous.

### 2.2 Accepted calendar-year bounds

Propose the accepted calendar-year range **0001 to 9999 inclusive**.

Rationale:

* a four-digit year keeps the persisted time literal fixed-width, so the
  fourth wire field has a stable length and remains lexicographically
  sortable as a date-time string;
* it avoids the proleptic-year sign-prefixed forms that a wider year range
  would require (for example a `+10000` prefix), which would make the literal
  non-uniform in width;
* it excludes proleptic year zero, which is not a user-representable civil
  year.

This bound is a **proposed constraint of this candidate and is subject to
maintainer acceptance**. It is recorded as an open review question in §12.

### 2.3 Strict calendar validation

Calendar validation is **strict**: an invalid local calendar date or time
is rejected. A `LocalDateTime` is not an instant on the UTC timeline.

Examples of values that must be rejected:

* `2026-02-30T00:00` — February 30 does not exist.
* `2026-02-29T00:00` — 2026 is not a leap year.
* `2026-13-01T00:00` — month 13 does not exist.
* `2026-01-01T24:00` — hour 24 is not a valid hour-of-day.
* `2026-01-01T09:60` — minute 60 is not a valid minute-of-hour.

### 2.4 Canonical persisted literal

The canonical persisted time literal is:

```text
uuuu-MM-dd'T'HH:mm
```

Example: `2026-01-01T09:30`.

The literal is:

* four-digit proleptic year (`uuuu`), zero-padded;
* two-digit month, two-digit day;
* the literal separator `T`;
* two-digit hour-of-day and two-digit minute, using a 24-hour clock;
* **no** seconds field, **no** fractional field, **no** offset, **no** zone
  suffix.

### 2.5 Formatter construction

Propose an explicitly constructed formatter:

```kotlin
private val TIME_FORMATTER: DateTimeFormatter =
    DateTimeFormatter.ofPattern("uuuu-MM-dd'T'HH:mm")
        .withResolverStyle(ResolverStyle.STRICT)
```

Requirements:

* the resolver style is pinned to `ResolverStyle.STRICT` on the formatter
  instance, so strict calendar resolution is an explicit property of the
  persisted contract rather than an inherited default;
* the pattern pins the proleptic year field `uuuu` rather than the
  year-of-era field `yyyy`, because year-of-era cannot be resolved without
  an era under `ResolverStyle.STRICT`;
* the same formatter instance is used for parsing and for canonical
  re-serialization, so that the accepted literal and the emitted literal
  cannot drift apart.

**Technical correction preserved in this contract.** An earlier draft
recommendation asserted that Java's predefined
`DateTimeFormatter.ISO_LOCAL_DATE_TIME` uses `SMART` resolver style by
default. That assertion was incorrect and is withdrawn: the predefined ISO
formatters resolve with `ResolverStyle.STRICT` and the ISO proleptic
chronology. The explicitly constructed strict formatter above is nonetheless
specified, because it pins the exact pattern, the resolver style, and the
proleptic-year field in one place instead of inheriting them implicitly.

### 2.6 Canonicality enforcement

A literal that parses successfully but does not re-serialize identically is
**not** canonical and must be rejected.

Proposed rule, applied to every candidate literal:

1. parse the literal with the strict formatter;
2. reject if parsing fails;
3. reject if the parsed year is outside the accepted bounds (§2.2);
4. reject if the parsed value carries a non-zero second or nano component
   (§2.1);
5. re-serialize the parsed value with the same formatter and require exact
   string equality with the input literal; otherwise reject as non-canonical.

The combined strict parsing, year-bound and canonicality checks reject:

* a literal carrying seconds (`2026-01-01T09:30:00`);
* a literal carrying a fractional component;
* a literal carrying a UTC offset (`2026-01-01T09:30+01:00`);
* a literal carrying a zone suffix (`2026-01-01T09:30Z`);
* a literal carrying a year outside the accepted bounds
  (`0000-01-01T00:00`, `10000-01-01T00:00`).

### 2.7 Rejection surface

| Context | Rejected by | Exception type |
|---|---|---|
| Controller input (`setTime`) | minute-precision and year-bound checks | `IllegalArgumentException` |
| Direct `FileReminderStore.save` input | validate every non-null `Reminder.time` for minute precision and year bounds before writing | `IllegalArgumentException` |
| Persisted file content on load | strict grammar, calendar, canonicality and year checks | `IllegalStateException`, matching the existing malformed-file convention |

A caller can construct an invalid `Reminder.time` without using the controller.
Therefore, `FileReminderStore.save` must independently validate **every** time
value before opening or truncating the file. It must reject invalid values,
not silently discard seconds, fractional parts or out-of-range years during
serialization. A failed validation preserves the previous file bytes.

Caller-supplied invalid values use `IllegalArgumentException`; malformed
persisted file content uses `IllegalStateException`.

## 3. Controller Contract

### 3.1 Frozen proposal

Propose the following exact method on `ReminderController`:

```kotlin
fun setTime(id: String, time: LocalDateTime?): Boolean
```

### 3.2 Exact semantics

EXISTING ID + UNCHANGED VALUE:

* Return `true`.
* Perform no save.
* Leave the in-memory state unchanged.

EXISTING ID + INVALID NON-NULL TIME:

* Throw `IllegalArgumentException`.
* Perform no save.
* Leave the in-memory state unchanged.

EXISTING ID + EFFECTIVE CHANGE:

* Return `true`.
* Derive the candidate `Reminder` at the same list index.
* Preserve the reminder's `id`.
* Preserve the reminder's `text`.
* Preserve the reminder's `done`.
* Preserve the reminder's list index and the position of every other
  reminder.
* Save the complete candidate list exactly once.
* Publish the new controller state only after the save returns successfully.
* If the save throws, the exception propagates to the caller and the
  in-memory state remains the pre-call state.

MISSING ID:

* Return `false`.
* Perform no save.
* Leave the in-memory state unchanged.
* Do not validate the supplied time. **ID lookup occurs before time
  validation**, so a missing id is a `false` result even when the supplied
  time would be invalid.

CLEARING A TIME:

* `null` clears the time. It is an ordinary effective change when the
  reminder currently has a non-null time, and it is an unchanged no-op
  returning `true` when the reminder already has a `null` time.

### 3.3 Additional invariants

* `idGenerator` is **never** called by `setTime`.
* The operation neither creates nor removes a reminder. The list length is
  unchanged.
* The operation does not reorder the list and does not modify any other
  reminder's fields.
* The operation writes the complete list, not a delta. This preserves the
  existing whole-list save model.

### 3.4 Comparison with the observed `setDone`

The observed `ReminderController.setDone(id, done)` reads:

```kotlin
fun setDone(id: String, done: Boolean): Boolean {
    val index = state.indexOfFirst { it.id == id }
    if (index < 0) return false

    if (state[index].done == done) return true

    val mutableCandidate = state.toMutableList()
    mutableCandidate[index] = state[index].copy(done = done)
    val candidate: List<Reminder> = mutableCandidate
    store.save(candidate)
    state = candidate
    return true
}
```

Comparison:

| Property | Observed `setDone` | Proposed `setTime` | Relation |
|---|---|---|---|
| ID lookup | exact, case-sensitive, first match by `id` | identical | same |
| Missing id | `false`, no save | `false`, no save | same |
| Unchanged value | `true`, no save | `true`, no save | same |
| Input validation | none needed; `Boolean` admits no invalid value | minute precision and accepted-year bound | **one additional step** |
| Validation order | not applicable | after ID lookup, before the unchanged check | **new** |
| Candidate derivation | `copy(done = done)` at the same index | `copy(time = time)` at the same index | same shape |
| Save count | exactly one | exactly one | same |
| Save-before-publish | `store.save(candidate)` precedes `state = candidate` | identical | same |
| Save failure | exception propagates; `state` unchanged | identical | same |
| `idGenerator` use | never called | never called | same |
| List size / index | unchanged | unchanged | same |

`setTime` therefore follows the established `setDone` shape exactly and adds
precisely one element: a validation step, placed after the ID lookup and
before the unchanged-value check. Placing validation after the lookup keeps
the missing-id contract stable: a missing id is always `false`, never an
exception.

The unchanged-value comparison is `state[index].time == time`. Kotlin
`==` on `LocalDateTime?` is null-safe and `LocalDateTime.equals` compares
the date and time fields exactly, so an unchanged-value comparison is
well-defined for minute-precision values.

## 4. Persistence Representation Contract — NWR3

### 4.1 Decision

Propose **NWR3**, preserving the existing single-file storage design.

### 4.2 NWR3 header

```text
NWR3
```

The header is the format discriminator, exactly as it is for `NWR1` and
`NWR2` today.

### 4.3 NWR3 record grammar

```text
<id><TAB><base64url-encoded-utf8-text><TAB><done-literal><TAB><time-literal>
```

Fields:

* `id` — unchanged ID grammar: non-empty, and free of TAB, CR, and LF.
* `base64url-encoded-utf8-text` — unchanged encoding: Base64URL with padding
  over the UTF-8 bytes of the reminder text.
* `done-literal` — exactly `0` for `done = false` or `1` for `done = true`.
  The literal set is unchanged from NWR2.
* `time-literal` — either a strictly validated canonical local date/time
  (§2.4, §2.6), or the reserved literal `-` when the reminder has no time.

The reserved absent marker `-` is chosen because it cannot collide with a
canonical time literal: a canonical literal always begins with a four-digit
year and always contains `T`.

### 4.4 File layout

* The header line is followed by one record line per reminder.
* Records are separated by a single LF (`\n`).
* There is **no** trailing LF after the final record.
* `save(emptyList())` writes exactly the NWR3 header, with **no** trailing
  newline — the byte content is exactly `NWR3`.
* The persistence file name and location are unchanged. `MainActivity`
  observes `File(filesDir, "reminders-v1.txt")`. The header, not the file
  name, carries the format version; renaming the file is not proposed.

### 4.5 Load-time validation

An NWR3 record must contain exactly three TAB separators. The following must
be rejected:

* a record with fewer than three TAB separators (missing required field);
* a record with more than three TAB separators (extra separator);
* an empty fourth field;
* an invalid `done` literal (anything other than `0` or `1`);
* a fourth field that is neither `-` nor a strictly validated canonical time
  literal;
* a fourth field that parses but is not canonical (§2.6);
* a fourth field denoting an impossible calendar date (§2.3);
* a fourth field whose year is outside the accepted bounds (§2.2).

The existing NWR2 negative-path guarantees — missing done-field separator,
extra TAB separator, invalid done literal, blank record, duplicate id, ID
grammar violations, malformed Base64URL, malformed UTF-8, trailing LF, empty
file — remain intact and are not weakened by the introduction of NWR3.

### 4.6 Write-path guarantees carried forward

* **Validation before write.** The complete input list is validated before
  the target file is opened or truncated, so a failed validation cannot
  destroy an existing valid file on disk.
* **Deterministic serialization.** The complete output is serialized in
  memory before writing. The original list order is preserved exactly.
  Saving the same list twice produces byte-identical output.
* **Write atomicity is not claimed.** The observed implementation writes with
  `file.writeBytes(encoded)`, which truncates and rewrites the target file in
  place. That is **not** a crash-safe atomic replacement, and this contract
  makes **no** guarantee that prior on-disk bytes are preserved after an
  actual filesystem I/O failure during the write.

  **Technical correction preserved in this contract.** An earlier draft
  described the write as an atomic filesystem replacement with guaranteed
  preservation after an I/O failure. That description was incorrect and is
  withdrawn. The guarantee that *does* hold is the validation-before-write
  guarantee, which covers rejection of invalid input but not failure during
  the physical write itself.

## 5. Legacy Loading, Migration, and Downgrade Behavior

### 5.1 Load behavior by header

| Header | `done` | `time` | Record fields |
|---|---|---|---|
| `NWR1` | `false` | `null` | `id`, `encoded text` |
| `NWR2` | as stored | `null` | `id`, `encoded text`, `done-literal` |
| `NWR3` | as stored | as stored, or `null` for `-` | `id`, `encoded text`, `done-literal`, `time-literal` |

Any other header is rejected with `IllegalStateException`, unchanged from the
observed behavior.

### 5.2 Lazy same-file migration

* Loading never rewrites the file. There is no load-time rewrite and no
  migration flag.
* The **first successful persistence-changing save** rewrites the same file
  in the NWR3 format.
* Pure loading and no-op controller operations must not rewrite the file.
  Existing `setDone` same-state and normalized-identical `edit` paths were
  observed to avoid `save`. The **proposed** `setTime` unchanged-value path
  must provide the same no-save behavior when Phase 2 implements it.

### 5.3 Forward compatibility is not promised

Backward loading is required: v0.1.5 must load existing v0.1.4 NWR2 data and
existing v0.1.3 NWR1 data.

Forward compatibility is **not** promised. A v0.1.4 application that opens a
file written by v0.1.5 in NWR3 format will reject that file, because the
observed v0.1.4 store rejects any header other than `NWR1` and `NWR2` with
`IllegalStateException`.

Downgrading an installation after v0.1.5 has written NWR3 data is therefore
not a supported path: the reminder file may be unreadable by the older
application. This is recorded as an explicit limitation of the candidate,
subject to maintainer acceptance, and is an open review question in §12.

## 6. Alternatives Considered and Trade-offs

### 6.1 Change the NWR2 grammar in place — rejected

Rejected. This would keep the header `NWR2` while adding a fourth field to
the record.

* A v0.1.4 reader **unambiguously rejects** four-field records under an
  `NWR2` header because its released parser permits exactly three fields.
  It would not load those new records.
* A v0.1.5 reader **could distinguish** old three-field and new four-field
  records by their TAB counts; those records are not intrinsically
  indistinguishable. However, using one `NWR2` header for two grammars would
  weaken the header as a version discriminator and require changing the
  released NWR2 extra-field rejection behavior.
* The release charter mandates backward loading of existing NWR2 data; it
  does **not** expressly prohibit an NWR2 extension or require retaining
  every prior malformed-record rejection. Preserving the exact existing
  NWR2 grammar and its negative-path tests is an **explicit recommendation
  of this architecture candidate**, not an invented charter prohibition.
* A separate `NWR3` header keeps header-driven migration and validation
  unambiguous, avoiding those compatibility and maintenance trade-offs.

Introducing a new header keeps every existing negative path intact and adds
a new format beside the old ones instead of redefining an existing one.

### 6.2 Separate time storage — rejected

Rejected. Storing times in a second file would break the existing
single-file, whole-list snapshot property.

* Saving the list and saving the time map would be two separate writes. A
  failure between them can leave the reminder list and its time map
  inconsistent, with no recoverable single point of truth.
* Lazy migration would become a multi-file migration with an ordering
  requirement between the two files.
* The second file would need its own lifecycle rules: creation, deletion
  when the list becomes empty, orphan handling, and interaction with the
  existing whole-list save model.
* Cross-file consistency is not achievable under the current synchronous
  single-save model without a journal or transaction, which is out of scope
  for this release.

### 6.3 Epoch-millisecond representation (`Long?`) — rejected, with a corrected rationale

Rejected.

**Technical correction preserved in this contract.** An earlier draft objected
to a nullable `Long?` on the grounds that it would collide with epoch zero.
That objection was incorrect and is withdrawn: a nullable `Long?` does **not**
collide with epoch zero, because `null` is the absent marker and `0L` is a
legitimate epoch-millisecond value. There is no sentinel collision.

The actual objection is semantic. An epoch-millisecond value is a coordinate
on the UTC timeline. Presenting it as the local date and time the user chose
requires an explicit timezone conversion, which:

* conflicts with the charter's explicit exclusion of timezone conversion and
  automatic DST handling;
* makes the stored value depend on the device timezone at the moment of
  writing;
* makes the displayed value shift if the device timezone later changes;
* introduces daylight-saving ambiguity for a value the user entered as a
  plain wall-clock time.

A `LocalDateTime` stores exactly the wall-clock value the user selected and
nothing else.

### 6.4 Date-only or time-only representations — rejected

A date-only value cannot express a time of day, which the release promise
requires. A time-of-day-only value cannot express the calendar date, and
would make the persisted field ambiguous across days. A `LocalDateTime`
holds both parts in one value with one absence marker.

### 6.5 Recommended option — candidate awaiting acceptance

NWR3 keeps: a single file; a single whole-list snapshot per save; one
explicit format discriminator; one explicit absent marker; a self-describing
canonical time literal that is independently verifiable on load; and every
existing NWR2 negative-path guarantee unchanged.

## 7. Persistence Test Obligations (Phase 3)

Phase 1 modifies no test. This section records the obligations that the
frozen representation creates for Phase 3.

### 7.1 Existing assertions that Phase 3 must reconcile

| Existing test | Current assertion | Required Phase-3 action |
|---|---|---|
| `P3_12b_unsupported_header_NWR3_rejected_with_IllegalStateException` | a file whose header is `NWR3` is rejected with `IllegalStateException` | **replace.** The header becomes supported. Replace with unknown-header rejection tests using headers that remain unsupported, plus positive NWR3 loading tests. |
| `P3_03_save_empty_list_writes_exact_NWR2_header_without_trailing_LF` | the exact bytes written by `save(emptyList())` are `NWR2`, with no trailing LF | **update.** The exact bytes written by `save(emptyList())` become `NWR3`, with no trailing LF. |

Existing NWR2 malformed-record rejection tests must remain intact. The NWR2
malformed-record behavior must not be relaxed to accommodate NWR3.

### 7.2 New obligations

**Compatibility.**

* An NWR3 file loads to the exact `Reminder` values it encodes: `id`, `text`,
  `done`, and `time`.
* An NWR1 file loads with `done = false` and `time = null`.
* An NWR2 file loads with its stored done state and `time = null`.
* An unknown header is still rejected with `IllegalStateException`.

**Round-trip.**

* A list containing a null time, a present time, `done = false`, and
  `done = true` round-trips through save and load to an equal list, in the
  same order.
* A null time is written as `-` and reads back as `null`.
* A present time is written as the canonical literal and reads back equal.
* Saving the same list twice produces byte-identical output.

**Migration.**

* Loading an NWR1 or NWR2 file does not modify the file bytes.
* The first effective save of an NWR1 or NWR2 file rewrites the same path in
  NWR3 format.
* The migrated file loads to the same reminders, with `time = null` where the
  reminder had no time.

**No-op preservation.**

* A controller `setTime` with an unchanged value leaves the file bytes
  unchanged.
* A controller `setDone` with an unchanged value leaves the file bytes
  unchanged.

**Malformed input rejection.** Each of the following must be rejected on load
with `IllegalStateException`:

* an empty fourth field;
* an extra TAB separator;
* a non-canonical time literal;
* an impossible calendar date, for example `2026-02-30T00:00`;
* `2026-02-29T00:00` in a non-leap year;
* a time literal carrying seconds, for example `2026-01-01T09:30:00`;
* a time literal carrying an offset, for example `2026-01-01T09:30+01:00`;
* a time literal carrying a zone suffix, for example `2026-01-01T09:30Z`;
* a year outside the accepted bounds, for example `0000-01-01T00:00` and
  `10000-01-01T00:00`;
* an invalid done literal;
* a duplicate id, a blank record, a trailing LF, and an empty file, all
  unchanged from the existing suite.

**Save-side validity and failure preservation.**

* Direct `FileReminderStore.save` calls must reject any `Reminder.time`
  whose second or nanosecond is nonzero or whose year is outside
  `0001`–`9999`, using `IllegalArgumentException` before opening/truncating
  the file. A controller is not the only possible store caller.
* A full-list save with a valid early reminder and an invalid later
  reminder must reject the entire list before writing; the previously valid
  file bytes must remain unchanged.
* A save whose input fails validation leaves the previously valid file bytes
  unchanged. The validation-before-write guarantee must still hold for the
  NWR3 write path.
* The absence of a crash-safe atomic write is not tested as a guarantee; it
  is a documented limitation (§4.6).

## 8. Compose UI Boundary Contract

### 8.1 Approach

Extend the **existing** `ReminderScreen`. Introduce no new screen, no
navigation, no `ViewModel`, no `Flow`, no coroutine, no dependency
injection, and no new application architecture.

The observed `ReminderScreen` holds its Compose state as `remember(controller)`
state: `input`, `reminders`, `editingId`, and `editBuffer`. The observed
`MainActivity` holds no `MutableState`; it constructs the store and the
controller and calls `setContent`. Both properties must be preserved.

The Material3 date and time picker composables come from the
`androidx.compose.material3` dependency that `app/build.gradle.kts` already
declares. **No** new Gradle dependency is required or authorized.

### 8.2 Required affordances

On each reminder row, the future UI must provide:

* **set** a time when none is present;
* **change** an existing time;
* **clear** an existing time;
* **display** the time when one is present.

When `time == null`, no time value is displayed, while the affordance to set
one remains available on that reminder.

### 8.3 Draft, confirmation, and cancellation

* A draft selection is **transient Compose state**. It does not live in the
  domain and is not written to the controller.
* The **committed** value belongs to the domain and controller. The UI calls
  `controller.setTime(reminder.id, draft)` and refreshes its local `reminders`
  state only after an accepted result, mirroring the observed `setDone`
  usage pattern.
* Confirmation is explicit. Cancellation is explicit and always available.
* A cancelled selector must **never** save anything: no `store.save`, no
  `controller.setTime`, and no `controller.edit`.
* Opening the date/time selector must not discard **and** must not commit an
  in-progress reminder-text edit. The observed `editingId` and `editBuffer`
  state must remain intact while a time draft is open.

### 8.4 Draft lifetime across Activity recreation

Propose that an **unconfirmed draft is discarded** on Activity recreation,
while a **confirmed** value remains persisted and survives recreation and
restart.

The observed `ReminderScreen` uses `remember`, not `rememberSaveable`, for
`editBuffer`. Consistent with that observed behavior, the time draft should
use `remember` semantics: recreation resets the draft, and only a confirmed
value is persisted.

### 8.5 Material3 picker timestamp interpretation

The calendar date must not be shifted by timezone conversion.

Material3 picker state represents a selected date as a UTC-midnight
millisecond value. That value must be interpreted using **that picker's own
calendar-date convention** — that is, the calendar date is read directly from
the millisecond value as a UTC calendar date — and must **not** be converted
blindly through the device's default timezone. A blind conversion through the
device timezone can shift the selected calendar day, for example in zones
west of UTC.

The proposed reading rule is: derive the calendar date from the picker's
millisecond value under a UTC calendar-date convention, and combine it with
the picker's hour and minute fields to build the `LocalDateTime`. The exact
API mapping against the resolved Material3 version is a Phase-4
implementation detail to be confirmed against the pinned dependency.

### 8.6 Initial display format

Propose a deterministic, locale-independent numeric display format for a
present time:

```text
yyyy-MM-dd HH:mm
```

Example: `2026-01-01 09:30`.

This is a **display-only** decision. It is deliberately distinct from the
persisted wire literal `uuuu-MM-dd'T'HH:mm` (§2.4): the display format may be
refined during Phase 4 without changing the persisted representation, and the
persisted representation may not change to satisfy a display preference.

The display format is a candidate decision subject to maintainer acceptance
and is recorded as an open review question in §12.

### 8.7 Prohibited in the UI boundary

No dependency, no new Android component, no new Android permission, no
scheduler, no alarm, no notification, no background behavior, no reminder-time
sort, reorder, removal, dimming, or text decoration, and no second
reminder-time authority in the UI.

## 9. Phase Ownership Boundaries

Phase 1 is architecture-only. The obligations below are **assigned, not
executed**. No item in this section was performed by the authoring Build.

### Phase 2 — Reminder Time Domain Implementation & JVM Proof

Owns:

* the `Reminder.time` field per §1;
* `ReminderController.setTime` per §3;
* deterministic JVM proof for the domain behavior: minute-precision
  rejection, missing-id `false` including the invalid-time case, unchanged
  `true`, effective change, identity / text / done / index preservation,
  `idGenerator` never called, no creation or removal, save-before-publish,
  and failed-save propagation leaving the in-memory state unchanged.

Does not own: persistence production code, Compose changes, Android identity
alignment, dependency changes, validator changes, CI changes.

### Phase 3 — Persistence Compatibility / Migration Proof

Owns:

* the NWR3 write path, the NWR1/NWR2/NWR3 load paths, and the lazy
  same-file migration per §4 and §5;
* the persistence test reconciliation and the new obligations in §7.

Does not own: production UI changes, Android identity alignment, Gradle,
validator, or CI changes.

### Phase 4 — Minimal Compose Integration

Owns:

* the minimal `ReminderScreen` integration and the interaction proof per §8:
  set, change, clear, display, confirmation, cancellation, draft discard on
  Activity recreation, text-edit preservation across selector use, and the
  picker calendar-date interpretation.

Does not own: `ReminderController` changes beyond Phase 2, `FileReminderStore`
changes, new Gradle dependencies, Android identity alignment, integrated
device validation.

### Phase 5 — Integration & Device Validation

Owns:

* integrated local validation and bounded one-physical-device runtime proof;
* the Android artifact identity advance from `versionCode 5 / versionName
  0.1.4` to `versionCode 6 / versionName 0.1.5`, under separate explicit
  maintainer authorization.

Does not own: new permissions, new Android components, new Gradle or test
dependencies, validator-architecture changes, general Android compatibility
claims, production-readiness claims.

### Phase 6 and Phase 7

Phase 6 owns the integrated audit and reconciliation. Phase 7 owns the full
pre-release gate. Neither is authorized by this document.

## 10. Explicitly Excluded From v0.1.5

This contract does not add, and no later phase may infer authorization for:

* notifications, alarms, background wake-up, automatic scheduling or firing
  at the selected time;
* recurrence, geofencing, contextual triggers, voice, networking, sync,
  analytics, or telemetry;
* a new Android Activity, Service, Receiver, or Provider;
* a new Android permission;
* a Room or DataStore replacement;
* `ViewModel`, `Flow`, coroutines, dependency injection, or navigation added
  solely for reminder time;
* encoding reminder time inside reminder text, reminder id, or reminder done
  state;
* timezone conversion or automatic DST handling;
* a general Android compatibility claim or a production-readiness claim;
* a change to nudge-land as product functionality;
* a change to the local validator architecture, the CI workflow, or the
  OpenCode harness.

## 11. Landing and Delivery Note

**`NW-DEVEX — Restore and streamline nudge-land delivery`**
Priority: HIGH.

This is a delivery-infrastructure task, separate from reminder-time product
functionality. The existing native `stage → commit → push → verify_ci`
implementation is expected to be used for the first architecture-document
landing if this candidate is accepted.

The maintainer has independently verified local `gh` availability and a
successful GitHub Actions API response. That verification is maintainer
evidence; it was not performed or re-verified by the authoring Build.

No nudge-land code change and no OpenCode harness change is authorized by
this document or by the authoring Build. No nudge-land transaction has been
created.

## 12. Open Review Questions

These are the decisions this candidate proposes that require maintainer
acceptance before they become frozen:

1. **Accepted calendar-year bounds.** Accept `0001`–`9999` inclusive as the
   accepted range, with fixed-width four-digit years on the wire (§2.2)?
2. **Canonical persisted literal.** Accept `uuuu-MM-dd'T'HH:mm` with an
   explicitly constructed `ResolverStyle.STRICT` formatter as the frozen wire
   literal (§2.4, §2.5)?
3. **Minute precision with rejection, not truncation.** Accept rejection of
   any value whose second or nano component is non-zero (§2.1)?
4. **NWR3 and the reserved absent marker.** Accept `NWR3` as the v0.1.5
   format and `-` as the absent-time literal (§4)?
5. **Downgrade is not a supported path.** Accept that a v0.1.4 application
   cannot read an NWR3 file, and that only backward loading is promised
   (§5.3)?
6. **Draft lifetime.** Accept that an unconfirmed draft is discarded on
   Activity recreation while a confirmed value persists (§8.4)?
7. **Initial display format.** Accept `yyyy-MM-dd HH:mm` as the deterministic
   initial display format, distinct from the persisted literal (§8.6)?
8. **Missing-id precedence.** Accept that a missing id returns `false` even
   when the supplied time is invalid, because ID lookup precedes time
   validation (§3.2)?
9. **Controller exception type.** Accept `IllegalArgumentException` for an
   invalid caller-supplied time and `IllegalStateException` for malformed
   persisted content (§2.7)?
10. **Non-atomic write is a documented limitation.** Accept that no
    crash-safe atomic replacement is promised and that the guarantee offered
    is validation-before-write only (§4.6)?

## 13. Document Status

This document is a **candidate awaiting independent review and maintainer
acceptance**.

* It does not formally accept Phase 1.
* It does not change the Phase 0-recorded persistence decision from
  `PHASE_1_REQUIRED`; that decision changes only upon acceptance.
* It implements nothing.
* It authorizes no staging, commit, push, branch operation, pull request,
  tag, release, dependency change, configuration change, or network access.
* It does not claim a commit, a push, an exact-head CI result, or a native
  nudge-land transaction. Landing evidence is open for a separately
  authorized, append-only reconciliation.
