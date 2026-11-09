# Release Charter — NudgeWhen v0.1.5

**Document status:** Active v0.1.5 release policy; documentary Phase 4 lifecycle-closure candidate; Phases 0 through 4 complete in this unlanded documentary candidate only. Phases 0–3 remain `Complete` under their existing historical qualification; Phase 4 is `Complete` **in this closure candidate only** after implementation `7879830a6310a3f9ea7a80e4cd6f86aff6414372` and successful exact-head CI `42503663732` plus maintainer-confirmed one-device interaction proof; Phases 5–7 remain `Planned`; projected model `5 Complete / 3 Planned`. Terminal closure acceptance and publication are pending; v0.1.5 is not merged, tagged, published or release-ready.

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

### Accepted Phase 1 persistence decision

The `PHASE_1_REQUIRED` value above is the historical Phase 0 decision value and is preserved as historical evidence: it recorded that Phase 0 did not pre-select a representation. Phase 1 has since evaluated and frozen the v0.1.5 representation, and the maintainer formally accepted that Phase 1 decision on 2026-11-04.

The accepted v0.1.5 persistence-format decision is:

**`NWR3`**

`NWR3` is the accepted v0.1.5 format. It carries NWR1/NWR2 backward loading and lazy same-file migration. It is the maintainer-accepted outcome of the Phase 1 evaluation, it is normative for Phase 2, Phase 3, and Phase 4 implementation, and it supersedes the historical Phase 0 placeholder value for the active lifecycle. The accepted architecture contract is `docs/releases/v0.1.5/reminder-time-architecture.md`.

The machine-readable release contract `scripts/release_contract.json` contains **no** persistence-format decision field. It records the phase statuses and carries no persistence-format key at all.

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

Phase 0 — Release Definition & Bootstrap — is `Complete` / formally accepted on 2026-10-18. Phase 1 — Reminder Time Architecture Contract — is `Complete` / formally accepted on 2026-11-04. Phase 2 — Reminder Time Domain Implementation & JVM Proof — is `Complete` in the closure candidate (formal terminal acceptance pending). Phase 3 — Persistence Compatibility / Migration Proof — is `Complete` in the Phase 3 closure candidate (terminal formal acceptance not yet recorded). Phase 4 — Minimal Compose Integration — is `Complete` in the Phase 4 documentary lifecycle-closure candidate (implementation and one-device proof accepted; separate landing and terminal closure acceptance pending). Phase 5 — Integration & Device Validation — is `Planned` / not started. Phase 6 — Integrated Audit & Reconciliation — is `Planned` / not started. Phase 7 — Full Pre-Release Gate — is `Planned` / not started. Phase model: `5 Complete / 3 Planned`; Phase 0 formal acceptance is supported by exact-head CI run `39114566018` for `2775cf64069a84adebde36366cddbee5459e67c5`; Phase 1 formal acceptance is supported by exact-head CI run `41907797725` for `8f811b61328ff24fb6b8db1589316a81b30450bb`.

Phase 0 is bounded to release-definition, governance, document-bootstrap synchronization, and the initial dirty-candidate repository-consistency validation. Phase 0 does not implement any reminder-time functionality, does not change `app/build.gradle.kts`, does not select a concrete persistence representation, does not modify any product Kotlin, does not modify persistence production code, does not modify Compose, and does not perform Android identity alignment.

Phase 1 — Reminder Time Architecture Contract — owns the architecture contract and freezes the v0.1.5 persistence representation. Phase 1 is architecture-only and produces no product code, no production tests, and no Compose changes. Phase 1 forbids encoding reminder time inside reminder text, inside reminder id, or inside reminder done state. Phase 1 must not implement reminder time; Phase 2 owns the implementation and JVM proof.

Phase 2 owns the domain implementation and JVM proof after Phase 1 freezes the architecture. Phase 3 owns persistence compatibility / migration implementation and proof after Phase 1 freezes the representation. Phase 4 owns minimal Compose integration. Phase 5 owns integrated and bounded physical-device proof, including the later Android artifact identity alignment under separate explicit maintainer authorization. Phase 6 owns integrated audit plus reconciliation. Phase 7 owns the full final pre-release gate.

## Phase 0 formal acceptance evidence

The maintainer formally accepted Phase 0 on 2026-10-18 after the exact ten-path closure commit `2775cf64069a84adebde36366cddbee5459e67c5` was published and GitHub Actions `CI` push run `39114566018` / required `validate` job `117637601837` completed successfully. Local and hosted regression: 245 Python tests / OK; clean validator 41/0/0; `release_gate=SATISFIED`. Historical OpenCode deviations remain documented without retrospective compliance waivers. The acceptance does not authorize Phase 1, any new capability, an Android identity change, or a v0.1.5 release.

This section records the lifecycle state as of the 2026-10-18 Phase 0 acceptance and is preserved as historical evidence. Phase 1 — Reminder Time Architecture Contract — was subsequently completed and formally accepted on 2026-11-04, as recorded in the Phase 1 formal acceptance evidence section below. The Phase 0 acceptance authorized neither Phase 1 nor any later phase.

## Phase 1 formal acceptance evidence

The maintainer formally accepted Phase 1 — Reminder Time Architecture Contract — on 2026-11-04 after the accepted architecture commit `8f811b61328ff24fb6b8db1589316a81b30450bb` (parent `3605975ee5bd00c7c7837556dee8d2c0d2ca4fe2`; subject `docs: define v0.1.5 reminder-time architecture`) was published through the native nudge-land transaction `nudgewhen-v0.1.5-phase1-architecture-first-native-land-001`, whose terminal authorization state was `LANDED` and terminal verified state was `S10_LANDED`, and GitHub Actions `CI` push run `41907797725` / job `126847010004` concluded `success` for that exact head. Published validation at that head: Python regression 245 tests / OK; clean validation 41 passed, 0 failed, 0 skipped; `release_gate=SATISFIED`.

The accepted architecture contract is `docs/releases/v0.1.5/reminder-time-architecture.md`. The accepted v0.1.5 persistence representation is `NWR3` with NWR1/NWR2 backward loading and lazy same-file migration. The accepted architecture and its frozen decisions are normative for Phase 2, Phase 3, and Phase 4 implementation.

Phase 1 was architecture-only. It produced no product code, no production tests, and no Compose change. Phase 1 acceptance authorizes no product implementation: Phase 2 — Reminder Time Domain Implementation & JVM Proof — remains `Planned` / `NOT_STARTED` and requires a separate explicit maintainer authorization. That Phase-2 `Planned` / `NOT_STARTED` statement describes the 2026-11-04 Phase 1 acceptance and is retained as historical evidence; Phase 2 implementation subsequently landed at `9c10098b3cba5dc8109cc3e4b25a7b434424167b`, and its formal closure synchronization remains a separate candidate.

The native nudge-land receipts and the hosted CI run, job, conclusion, test counts, and release-gate value are maintainer-supplied external evidence that was reviewed outside this repository. They are not new network observations by any OpenCode agent.

## Phase 2 implementation landing and formal closure-synchronization candidate

The Phase 2 domain implementation at commit `9c10098b3cba5dc8109cc3e4b25a7b434424167b` (parent `d4c42f79b5a997df628b1da2b8879eccfff064c9`; subject `feat: implement v0.1.5 reminder-time domain`) was independently accepted. Native authorization `nudgewhen-v0.1.5-phase2-domain-native-land-001` completed `LANDED / S10_LANDED`. GitHub Actions `CI` push run [`42355553118`](https://github.com/franchoy/nudgewhen/actions/runs/42355553118) / required `validate` job `128352751312` concluded `success` at the exact implementation head on `release/v0.1.5`. Repository boundary for the **implementation**: `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`.

Implementation proof retained: 141 JVM tests passed; Python five-module regression 245 tests / `OK`; local partial validation 22/0/0 with Android skipped, explicitly `release_gate=NOT_SATISFIED`. The hosted validation job concluded successfully. The frozen optional reminder-time domain API and tests were implemented without production persistence changes, Compose changes, Android identity alignment, new Gradle/test dependencies, validator changes, CI changes, or scope widening.

The implementation chronology and original OpenCode deviations remain recorded in the unmodified `EXP-0080` and `EXP-0081`. The separate `EXP-0082` records lifecycle closure preparation and the independent review of a noncompliant read-only planning attempt. At the original Phase 2 closure-candidate preparation point, the phase model was projected as `3 Complete / 5 Planned` **as an uncommitted closure-synchronization candidate**. That synchronization subsequently landed at `605f250c031c25e35b36f976707bb518025fe1b4` with exact-head CI `42366706308` / success; terminal formal maintainer acceptance is not independently established. No new closure-synchronization commit, push, exact-head CI, native landing or terminal formal maintainer acceptance is claimed.

The current Phase 1 architecture remains frozen; the accepted persistence representation remains `NWR3` with NWR1/NWR2 backward loading and lazy same-file migration. Product scope remains `["reminders", "persistence"]`.

At the original Phase 2 closure-candidate preparation point, Phase 3 — Persistence Compatibility / Migration Proof remained `Planned` / `NOT_STARTED` / `NOT_AUTHORIZED`; that earlier closure candidate did not authorize Phase 3 or release v0.1.5. Phase 3 implementation subsequently landed at `9a732495eb099b37bd835ab65c2c507bf2778694` and is the subject of a separate closure candidate. Native landing and hosted CI evidence cited here were independently reviewed outside OpenCode and are not represented as network calls performed by an OpenCode Build.

## Bootstrap exception

`V0_1_5_PHASE_0_BOOTSTRAP_EXCEPTION` is `TERMINATED` by formal maintainer acceptance on 2026-10-18 following successful publication and exact-head CI of Phase 0 closure commit `2775cf64069a84adebde36366cddbee5459e67c5` (run `39114566018`). The exception historically bridged only the inherited v0.1.4 release-context predicate during v0.1.5 bootstrap; it did not grant independent authority for product implementation, staging, commit, push, network, pull request, tag, release, dependencies, toolchain, configuration changes, or Android identity alignment. The v0.1.5 governance/contract synchronization is accepted and mutually consistent. The exception cannot be reused or reactivated. As of that 2026-10-18 termination, Phase 1 remained `NOT_STARTED` until separately authorized; that statement describes the state on 2026-10-18 and is preserved as historical evidence, not as a current lifecycle assertion. Phase 1 was subsequently completed and formally accepted on 2026-11-04, as recorded in the Phase 1 formal acceptance evidence section above.

The historical `POST_V0_1_4_MAIN_MAINTENANCE_BOOTSTRAP_EXCEPTION` remains `TERMINATED`; it is not reactivated, renamed, or reused by this v0.1.5 exception.

## Maintenance window

The historical v0.1.4 release-bearing merge into `main`, the annotated `v0.1.4` tag, and the GitHub Release for v0.1.4 are complete. v0.1.4 is `RELEASED_AND_CLOSED`. v0.1.4 is the latest stable published release. The post-v0.1.4 / pre-v0.1.5 maintenance window is formally closed. The v0.1.5 release train is now active on the single branch `release/v0.1.5`.

## Phase 3 implementation landing and documentary closure candidate

The v0.1.5 Phase 3 persistence implementation and test evidence landed at `9a732495eb099b37bd835ab65c2c507bf2778694` (parent `605f250c031c25e35b36f976707bb518025fe1b4`; subject `feat: implement v0.1.5 reminder-time persistence`). The native transaction `nudgewhen-v0.1.5-phase3-persistence-native-land-001` ended `LANDED / S10_LANDED`; exact-head `CI` run [42409878438](https://github.com/franchoy/nudgewhen/actions/runs/42409878438) / required `validate` job `128515492116` completed successfully for a `push` to `release/v0.1.5`. Hosted regression: 245 Python tests / `OK`; hosted full clean validator 41 passed, zero failed, zero skipped; `release_gate=SATISFIED`. Maintainer JUnit XML: focused persistence 100/100 and full JVM 180/180, zero failures/errors/skips. `EXP-0083` preserves original unsuccessful OpenCode attempts and independent corrections without erasure; `EXP-0084` is the new lifecycle-closure preparation evidence.

The Phase 3 `Complete` designation is a **documentary closure candidate** pending its own separate publication, exact-head CI, and terminal maintainer acceptance. No Phase 4 implementation, Android identity alignment, permission, scheduling, notification, networking, release, merge, tag or general compatibility guarantee is claimed.

## Phase 4 implementation landing and documentary lifecycle-closure candidate

The six-file minimal Compose reminder-time implementation landed at `7879830a6310a3f9ea7a80e4cd6f86aff6414372` (parent `b250b519f4fb88190e518834aacce5652101ba03`; subject `feat: integrate v0.1.5 reminder-time Compose UI`). The single-use native transaction `nudgewhen-v0.1.5-phase4-compose-implementation-native-land-002` finished `LANDED / S10_LANDED`. Exact-head GitHub Actions push [`CI` run `42503663732`](https://github.com/franchoy/nudgewhen/actions/runs/42503663732) / `validate` job `128801561569` concluded `success`. Original OpenCode source/evidence failures, subsequent corrections and native landing infrastructure recovery remain separate historical records in `EXP-0085`–`EXP-0087` and `EXP-0088` (the new Phase 4 closure candidate).

The maintainer completed a fresh offline debug-APK rebuild and JVM test task, a private backup of existing NWR2 reminders, signing comparison and data-preserving APK installation on one connected Android phone. Byte-level evidence confirms no load-time migration; one disposable reminder triggered NWR3 migration while preserving all originals; Set/Change/Clear changed only the new reminder time; Cancel/Edit and recreation periods caused no persisted changes; confirmed time survived process restart. Nine UI observations, including draft discard after Activity recreation, were separately and explicitly confirmed by the maintainer. Installation preceded a requested explicit review checkpoint; that deviation remains recorded. Neither physical-device scope nor this evidence implies general compatibility or Phase 5 completion.

**Closure boundary:** `Complete` is proposed only in this documentary candidate; it is not a terminal formal Phase 4 acceptance and no new closure landing or exact-head CI is claimed. Phase 5 integration and Android identity alignment (`6 / 0.1.5`) remain `Planned` and separately authorized. Current committed Android identity remains `5 / 0.1.4`. The frozen NWR3 format, product scope `["reminders", "persistence"]`, no-notification/no-alarm/no-background limitations, and v0.1.4 latest stable published release remain unchanged.

## v0.1.5 release state

v0.1.5 is **not** merged, **not** tagged, **not** published, and is not release-ready. Phase 0 — Release Definition & Bootstrap — is `Complete` / formally accepted on 2026-10-18. Phase 1 — Reminder Time Architecture Contract — is `Complete` / formally accepted on 2026-11-04, with the accepted architecture contract frozen at `docs/releases/v0.1.5/reminder-time-architecture.md` and the accepted persistence representation `NWR3` with NWR1/NWR2 backward loading and lazy same-file migration. Phase 2 — Reminder Time Domain Implementation & JVM Proof — is `Complete` in the closure-synchronization candidate (terminal acceptance pending), supported by accepted native implementation landing `9c10098b3cba5dc8109cc3e4b25a7b434424167b` and exact-head CI run `42355553118`. Phase 3 — Persistence Compatibility / Migration Proof — is `Complete` in the Phase 3 closure-synchronization candidate; its implementation landed at `9a732495eb099b37bd835ab65c2c507bf2778694` with native `LANDED / S10_LANDED` and exact-head CI `42409878438` / `success`, but terminal formal acceptance of the lifecycle closure is not yet recorded. Phase 4 is `Complete` in the pending documentary lifecycle-closure candidate: implementation and bounded one-device proof accepted, but no separate closure landing, exact-head closure CI or terminal formal acceptance is claimed. Phase 5 remains `Planned` / `NOT_STARTED` / `NOT_AUTHORIZED` and requires separate authorization. No v0.1.5 release action is authorized by this charter.

Product scope remains exactly `["reminders", "persistence"]`. The active persistence-format decision is `NWR3` with NWR1/NWR2 backward loading and lazy same-file migration; the historical Phase 0 placeholder value `PHASE_1_REQUIRED` is preserved above as historical Phase 0 evidence and is not the active decision. The Android identity non-mutation rule is unchanged: `app/build.gradle.kts` remains at `versionCode 5 / versionName 0.1.4`, and the v0.1.5 target identity `versionCode 6 / versionName 0.1.5` remains a future target only.
