# NudgeWhen v0.1.2 — Reminder Architecture Contract

**Document status:** Candidate — Phase 1 architecture contract pending validation and maintainer closure.

## Authority and scope

This document records the Phase 1 Reminder Architecture Contract candidate authorized
for NudgeWhen v0.1.2 by the maintainer.

Scope:

- This document records architecture decisions only.
- It is frozen at the conclusion of Phase 1 audit (1A, 1A-R1, 1A-R2) and Phase 1B
  candidate authoring.
- It does not implement reminder functionality.
- It does not modify Kotlin, Gradle, manifest, validator, CI, release contract,
  `AGENTS.md`, `README.md`, the release charter, or the phase list.
- Implementation of the architecture described here belongs to Phase 2 and
  later phases and is not part of this candidate.

Every claim in this document is an architecture decision. No product
functionality is described as already implemented.

## Existing architecture evidence

The repository, at the Phase 1B starting HEAD
`d61e41caed1b558688b9fd48ad3ca43ffacf97ca` on branch `release/v0.1.2`, contains the
following directly observed existing components relevant to the reminder
architecture:

- Android entry point: `app/src/main/kotlin/io/github/franchoy/nudgewhen/MainActivity.kt`
- Existing theme boundary: `app/src/main/kotlin/io/github/franchoy/nudgewhen/ui/theme/Theme.kt`
- Android manifest: `app/src/main/AndroidManifest.xml`
- Application build script: `app/build.gradle.kts`
- Project build script: `build.gradle.kts`
- Version catalog: `gradle/libs.versions.toml`
- Gradle settings: `settings.gradle.kts`
- Local validator entry point: `scripts/validate-local.sh`
- Local validator implementation: `scripts/validate_local.py`

Existing repository evidence also establishes:

- no tracked `app/src/test/...` tree currently exists at the Phase 1B
  starting HEAD;
- no tracked `app/src/androidTest/...` tree currently exists at the
  Phase 1B starting HEAD.

Direct evidence establishes that the current local validation does NOT execute
Kotlin/JVM unit tests. Current CI does NOT directly execute a Kotlin/JVM
Gradle unit-test task. This is the existing baseline that the validator/CI
follow-up boundary in a later section explicitly references.

`app/src/test/kotlin/...` is the architecture-selected FUTURE location for
Phase 2 and Phase 3 ordinary JVM tests. It is not an existing source
root and is not exercised by the current local validator or CI.

No additional reminder-related Kotlin sources, Gradle modules, persistence
configuration, or test-source directories exist at the Phase 1B starting
HEAD. The remainder of this document defines the architecture to be
implemented in Phase 2 and later phases.

## Reminder domain contract

Freeze the following domain model.

`Reminder`:

- `id: String`
- `text: String`

The `Reminder` model contains exactly these two fields. No other fields are
permitted.

The following are explicitly excluded and must not be added to `Reminder`:

- `createdAt`
- `updatedAt`
- `completed`
- `completedAt`
- `dueAt`
- `priority`
- `category`
- `location`
- `schedule`
- `metadata`

The model has no time semantics. There is no field that represents creation
time, completion time, due time, or any other temporal or scheduling
property.

Reminder ordering is represented by persisted list order. No field of
`Reminder` participates in ordering. In particular, ordering does not
derive from `id`.

## Text creation contract

The text accepted when a reminder is created is processed as follows.

Input behavior:

- Trim leading and trailing whitespace from the supplied text.
- If the trimmed result is empty, reject the input. The reminder is not
  created.
- Otherwise persist the normalized trimmed text as the reminder's `text`.

Do not parse or interpret the supplied text. The following are explicitly
excluded:

- date parsing
- time parsing
- priority parsing
- voice parsing
- context extraction
- rich text
- categories
- tags

The stored `text` is the trimmed UTF-8 string supplied at creation time.

## Display and ordering contract

Display and ordering follow these rules:

- Display every currently stored reminder.
- Persisted list order is the creation and display order.
- The oldest reminder is displayed first.
- A new reminder is appended to the end of the list.
- Removal of a reminder preserves the relative order of all remaining
  reminders.

No timestamp is required for ordering.

No alternative ordering (alphabetical, priority-based, due-time-based) is
defined for v0.1.2.

## Lifecycle contract

Freeze the following lifecycle semantic:

**PERMANENT REMOVAL.**

Reminder lifecycle:

```
absent -> create -> present -> remove -> absent
```

A reminder is created, becomes present in the list, and may later be removed
permanently. There is no completion state and no archival state.

The following are explicitly excluded:

- a `completed` flag
- a `completedAt` field
- completed-item filtering
- a completed-item archive

A removed reminder is gone from the list. There is no later retrieval of a
removed reminder from v0.1.2 persistence.

## Ownership and package boundaries

Conceptual package ownership is frozen as follows.

`io.github.franchoy.nudgewhen.domain`

- `Reminder`
- `ReminderStore`
- `ReminderController`

`io.github.franchoy.nudgewhen.data`

- `FileReminderStore`

`io.github.franchoy.nudgewhen.ui`

- `ReminderScreen`

Existing:

- `io.github.franchoy.nudgewhen.MainActivity`
- `io.github.franchoy.nudgewhen.ui.theme`

These two existing entries remain the Android entry point and the existing
theme boundary.

The domain, controller, and store implementations must remain
Android-framework independent. They do not import Android framework
classes.

`MainActivity` is the Android adapter. It owns access to `filesDir` and
supplies a `java.io.File` to `FileReminderStore`. `FileReminderStore` itself
receives a `File` and has no Android import.

The following are explicitly excluded for v0.1.2:

- `ViewModel`
- a Repository framework
- a dependency injection framework
- a navigation framework
- a new `Activity`
- a `Service`
- a `Receiver`
- a `Provider`

## Persistence technology

Freeze the following persistence technology for v0.1.2.

- A single app-private file is the production storage mechanism.
- Production persistence uses standard Java/Kotlin runtime file APIs only.
- No production persistence dependency is added.

The following persistence technologies are explicitly excluded for v0.1.2
production persistence:

- Room
- raw SQLite
- DataStore
- SharedPreferences
- Gson
- Moshi
- `kotlinx.serialization`
- `org.json`

The intended file is supplied through the following chain:

```
MainActivity -> app-private filesDir -> FileReminderStore
```

`FileReminderStore` receives a `File` and has no Android import. The
domain, controller, and store implementations remain Android-framework
independent.

## Persistence file format

Freeze the following persistence file format for v0.1.2.

- File name: `reminders-v1.txt`
- File encoding: UTF-8
- Format version marker, exact first line: `NWR1`

After the first line, the file contains zero or more reminder records. Each
reminder record occupies a single line of the form:

```
<id><TAB><base64url-text>
```

The Base64URL codec is frozen as follows:

- Encoder: `java.util.Base64.getUrlEncoder().encodeToString(...)`.
- Decoder: `java.util.Base64.getUrlDecoder()`.
- Normal Java encoder padding is retained.

The codec uses only standard runtime APIs. No JSON dependency is used.

Record order equals reminder creation and display order.

Unsupported or malformed file contents must not be silently reinterpreted.
Detailed user-facing persistence-error UX remains outside v0.1.2.

## ReminderStore contract

The conceptual `ReminderStore` contract is frozen as:

```
load(): List<Reminder>
save(reminders: List<Reminder>)
```

`ReminderStore` owns only load and save. It does not own creation or
removal lifecycle behavior.

`load()` behavior:

- If `reminders-v1.txt` does not exist, `load()` returns `emptyList()`.
- For an existing file:
  - the first line must equal `NWR1` exactly;
  - every subsequent line must contain exactly one record separator TAB;
  - every ID must satisfy the frozen ID grammar;
  - every Base64URL text must decode successfully;
  - duplicate IDs make the file malformed;
  - blank or otherwise malformed records make the file malformed;
  - any malformed or unsupported content fails the complete load;
  - a malformed or unsupported file does NOT cause `load()` to return a
    partially recovered reminder list;
  - `load()` must not silently reinterpret another format.

Detailed user-facing recovery UX remains outside v0.1.2. No migration
behavior beyond recognizing the exact `NWR1` format is defined.

`save(reminders)` behavior:

- If `save(reminders)` receives an empty list, the resulting file contains
  exactly the `NWR1` header line and no reminder records.
- Every saved record satisfies the same per-record and ID grammar rules
  enforced by `load()`.

The mutation ordering rule for any write through `ReminderStore` is:

1. Derive the candidate reminder list.
2. Persist the candidate list.
3. Expose or update the new state only after persistence succeeds.

The store implementation must not publish a state change that has not been
persisted.

## ReminderController contract

`ReminderController` owns creation and removal lifecycle behavior.

The conceptual construction is frozen as:

```
ReminderController(
    store: ReminderStore,
    idGenerator: () -> String
)
```

The exact Kotlin syntax above is conceptual architecture, not
implementation. No Kotlin source for this controller exists in Phase 1.

`ReminderController` uses a `ReminderStore` for persistence and provides
the lifecycle operations that the Compose UI calls:

- create a reminder from supplied text, applying the text creation contract
  and persisting through the store;
- expose the current reminder list for display;
- remove a reminder by identity, persisting through the store.

Creation behavior:

1. Trim leading and trailing whitespace from the supplied text.
2. If the trimmed result is empty:
   - reject the input;
   - do not call `idGenerator`;
   - do not call `save`;
   - the in-memory state remains unchanged.
3. Otherwise, obtain the new reminder's ID from `idGenerator`.
4. Validate the ID grammar and uniqueness within the current reminder
   list.
5. Derive the appended candidate list.
6. Save the candidate list through `ReminderStore`.
7. Expose the candidate state only after `save()` succeeds.

Removal behavior:

- Unknown ID:
  - the operation is a no-op;
  - `save()` is not called;
  - the in-memory state remains unchanged.
- Known ID:
  1. Derive the candidate list with that reminder removed.
  2. Save the candidate list through `ReminderStore`.
  3. Expose the candidate state only after `save()` succeeds.

Persistence failure:

- propagates to the caller;
- any previously exposed in-memory state remains unchanged.

A detailed user-facing error UX is not frozen in this architecture
contract.

`ReminderController` is a plain Kotlin controller. It is not an Android
`ViewModel` and does not require any Android lifecycle component.

## Reminder identity

Reminder IDs are opaque strings.

Frozen identity constraints:

- `id` is non-empty;
- `id` must contain no TAB, CR, or LF characters;
- IDs must be unique within the current reminder list;
- deterministic test IDs must satisfy the same grammar;
- production UUID strings satisfy this grammar.

Production implementations may generate IDs with:

```kotlin
java.util.UUID.randomUUID().toString()
```

Ordering does not derive from the identifier. The list order, not the ID,
determines display and creation order.

Tests must be able to supply deterministic identifiers.

The following are explicitly excluded:

- time-derived IDs
- counter-derived IDs that are exposed in the public surface as ordinals

## Compose integration boundary

Freeze the following UI and state ownership:

- a plain Kotlin `ReminderController`
- plus Compose-owned presentation state.

Android `ViewModel` is not required for v0.1.2.

The following are explicitly excluded:

- an Android `ViewModel` dependency
- a navigation framework
- a navigation dependency

`MainActivity` remains the single Android composition entry point.

`ReminderScreen` eventually owns the minimal UI surface:

- a text input
- a create action
- a reminder list
- a remove action

No UI implementation occurs during Phase 1. UI implementation belongs to
Phase 4 and later phases and is not part of this candidate.

## Restore-after-restart contract

Restore after restart means:

- During normal `MainActivity` startup, before presenting the reminder
  list, load the app-private reminder file.
- Initialize the in-memory reminder state from the file contents.

Restore is synchronous for v0.1.2.

The following are explicitly excluded:

- `Flow`
- background restoration
- `WorkManager`
- `AlarmManager`
- a `Service`
- a `BroadcastReceiver`
- an `androidx.startup` initializer
- network access
- sync
- a loading or retry architecture

No claim is made about production-scale IO latency. v0.1.2 accepts that
restore is synchronous and bounded by the size of the persisted file.

## Test boundary

Freeze the following test boundary:

- ordinary local JVM tests under `app/src/test/kotlin/...`

Phase 2 owns deterministic tests for:

- `Reminder`
- `ReminderController`
- lifecycle behavior
- input normalization

Phase 3 owns deterministic tests for:

- `FileReminderStore`
- format round-trip
- ordering
- removal persistence
- restore from a new `FileReminderStore` instance

Phase 3 tests use temporary files.

No instrumented Android test is required for domain or persistence proof
in v0.1.2.

The exact Kotlin/JVM test-library dependency is NOT selected in Phase 1.
Phase 2 must separately select and authorize the minimum test dependency
before adding it.

## Validator and CI follow-up boundary

Direct evidence establishes the following about the current local
validator and CI configuration:

- Current local validation does NOT execute Kotlin/JVM unit tests.
- Current CI does NOT directly execute a Kotlin/JVM Gradle unit-test task.

Before Phase 2 can close, separately authorized validator evolution must
make the deterministic JVM tests part of release evidence.

The preferred minimum future change is:

- Extend the EXISTING android validation surface so it executes
  `:app:testDebugUnitTest`.

Do NOT create a new validation group merely for this purpose unless later
evidence requires one.

Because CI already executes `./scripts/validate-local.sh --require-clean`,
CI does not require a new workflow command if `validate-local` itself
begins executing `:app:testDebugUnitTest`.

That validator change is NOT part of Phase 1B. It is a separate, later,
separately authorized validator evolution that must be completed before
Phase 2 closure.

## Explicit non-goals

The architecture for v0.1.2 continues to exclude the following. None of
these is implemented, scheduled, or in scope for v0.1.2.

- voice
- speech
- notifications
- time scheduling
- alarms
- location
- geofencing
- contextual or device-state triggers
- background execution
- networking
- sync
- analytics
- additional Android activities
- services
- receivers
- providers
- new Android permissions
- production-readiness guarantees
- Hermes integration
- MCP integration
- provider migration or reversion

## Phase ownership

The reminder work for v0.1.2 is split across phases as follows.

- Phase 1 — Reminder Architecture Contract (current; `Planned`):
  this document is the deliverable. No product code is produced.
- Phase 2 — Domain and controller implementation and deterministic tests:
  implements `Reminder`, `ReminderController`, and the Phase 2 test set
  using the test-library dependency selected and authorized in Phase 2.
- Phase 3 — Persistence implementation and round-trip tests:
  implements `FileReminderStore` and the Phase 3 test set using temporary
  files.
- Phase 4 — UI implementation and Compose integration:
  implements `ReminderScreen` and integrates with `MainActivity`.
- Phase 5 — Integration & Device Validation: integrates the Phase 2
  through Phase 4 deliverables and performs device validation work as
  defined by the active phase list.
- Phase 6 — Integrated Audit & Agent Evaluation: performs the integrated
  audit and agent evaluation work as defined by the active phase list.
- Phase 7 — Full Pre-Release Gate: executes the full pre-release gate as
  defined by the active phase list.

The release-bearing pull request, the merge of that pull request, the
merged-`main` verification, the annotated tag, the GitHub release, and
the release-branch cleanup are separate repository and release actions
that occur after the applicable Phase 7 / pre-release boundary. Phase 7
itself is not described as release publication.

Phase ownership of validator evolution is recorded under the validator and
CI follow-up boundary above. The validator change is not part of Phase 1B
and is owned by a later, separately authorized phase.

## Acceptance conditions

This candidate is accepted as the Phase 1 architecture contract when the
maintainer explicitly accepts it after Phase 1B staged validation.

This architecture document remains a Candidate during Phase 1B. After
accepted staged validation, the maintainer may accept the architecture
candidate. Phase 1 remains formally `Planned` until a separately
authorized release state synchronization updates the phase model and the
current-facing documents. Only after that synchronization is validated
and accepted does Phase 1 become `Complete` and Phase 2 become current.
No Phase 2 implementation has started as of this candidate.

Acceptance conditions for Phase 1 architecture closure:

- This document exists in tracked form at the Phase 1 closure commit.
- The frozen decisions in this document match the architecture freeze
  authorized in the Phase 1B Build task.
- No product functionality is described as already implemented.
- No path outside the two authorized Phase 1B paths
  (`docs/releases/v0.1.2/reminder-architecture.md` and
  `docs/agentic-development/experiments/EXP-0036.md`) was modified by
  Phase 1B.
- No staging, commit, push, branch, tag, pull request, dependency change,
  configuration change, Gradle run, or network access occurred during
  Phase 1B.
- Historical Phase 1A, 1A-R1, and 1A-R2 audit outcomes and their lesson
  dispositions are preserved in `EXP-0036.md` without rewrite.

Phase 1 closure does not imply Phase 2 closure, Phase 3 closure, Phase 4
closure, Phase 5 closure, Phase 6 closure, Phase 7 closure, or release
readiness.