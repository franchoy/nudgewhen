# Phase List — NudgeWhen v0.1.5

**Document status:** Active v0.1.5 phase-ordering authority, documentary Phase 4 closure candidate; Phases 0 through 4 complete in this unlanded documentary candidate only. Phases 0–3 are recorded `Complete` with their earlier acceptance qualifications unchanged; Phase 4 — Minimal Compose Integration — is `Complete` **in the unlanded closure candidate only** (implementation `7879830a6310a3f9ea7a80e4cd6f86aff6414372` native `LANDED / S10_LANDED`; CI `42503663732` success; maintainer-confirmed one-device proof); Phases 5–7 are `Planned`. Proposed model `5 Complete / 3 Planned`; v0.1.4 remains the latest stable release, and v0.1.5 is not merged, tagged, published or release-ready.

## Phase 0 — Release Definition & Bootstrap

Phase 0 performs the v0.1.5 release-definition, governance, document-bootstrap synchronization, and the initial dirty-candidate repository-consistency validation. Phase 0 freezes the v0.1.5 release charter, the v0.1.5 phase list, the current-facing tracked governance, the machine-readable release contract, the local-validation documentation, and the Phase 0 evidence record.

Phase 0 non-goals:

- no implementation of reminder-time functionality;
- no `app/build.gradle.kts` change;
- no selection of a concrete v0.1.5 persistence representation;
- no modification of any product Kotlin;
- no modification of persistence production code;
- no modification of Compose;
- no Android identity alignment;
- no Gradle dependency change;
- no validator implementation change;
- no CI workflow change.

### Status

Complete

### Phase 0 formal acceptance

The maintainer accepted Phase 0 on 2026-10-18 after closure commit `2775cf64069a84adebde36366cddbee5459e67c5` was published and exact-head `CI` run `39114566018` / `validate` job `117637601837` succeeded. Python regression: 245 tests / OK; local and hosted clean validation: 41 passed, 0 failed, 0 skipped; `release_gate=SATISFIED`. The Phase 0 bootstrap exception termination is recorded in the terminal governance synchronization. Phase 1 remains `Planned` / `NOT_STARTED`; no Phase 1 work is authorized by this acceptance. That Phase-1 status is the state as of the 2026-10-18 Phase 0 acceptance and is preserved as historical evidence; Phase 1 was subsequently completed and formally accepted on 2026-11-04, as recorded in the Phase 1 section below.

## Phase 1 — Reminder Time Architecture Contract

Phase 1 owns the v0.1.5 reminder-time architecture contract. It decides the exact representation of an optional persistent reminder-time state on top of the existing v0.1.4 NWR2 reminder record while safely loading existing v0.1.4 data and preserving deterministic whole-list semantics. Phase 1 also decides the controller API for setting, changing, and clearing reminder time, the exact-id lookup contract, the UI affordance boundary, and any buffer behavior across Activity recreation. Phase 1 also evaluates and freezes the v0.1.5 persistence-format decision; Phase 0 records that decision as `PHASE_1_REQUIRED` and does not pre-select it.

Phase 1 is architecture-only and produces no product code, no production tests, and no Compose changes. Phase 1 forbids encoding reminder time inside reminder text, inside reminder id, or inside reminder done state. Phase 1 must not implement reminder time; Phase 2 owns the implementation and JVM proof.

Phase 1 is `Complete`. The accepted architecture contract is `docs/releases/v0.1.5/reminder-time-architecture.md`. The maintainer-accepted v0.1.5 persistence representation is **`NWR3`**, with NWR1/NWR2 backward loading and lazy same-file migration. That accepted Phase 1 decision supersedes the historical Phase 0 placeholder value `PHASE_1_REQUIRED` for the active lifecycle; the historical Phase 0 value remains recorded in the release charter and in `AGENTS.md` as historical evidence.

Phase 1 non-goals:

- no implementation of reminder-time behavior;
- no production `Reminder` model change;
- no production `ReminderController` change;
- no production `FileReminderStore` change;
- no persistence migration implementation;
- no Compose change;
- no Android identity alignment;
- no Gradle, validator, CI, or dependency change.

### Status

Complete

### Phase 1 formal acceptance

The maintainer formally accepted Phase 1 on 2026-11-04 after the accepted architecture commit `8f811b61328ff24fb6b8db1589316a81b30450bb` (parent `3605975ee5bd00c7c7837556dee8d2c0d2ca4fe2`; subject `docs: define v0.1.5 reminder-time architecture`) was published through the native nudge-land transaction `nudgewhen-v0.1.5-phase1-architecture-first-native-land-001`, whose terminal state was `LANDED / S10_LANDED`, and exact-head `CI` run `41907797725` / job `126847010004` concluded `success`. Python regression: 245 tests / OK; hosted clean validation: 41 passed, 0 failed, 0 skipped; `release_gate=SATISFIED`. The accepted architecture and its ten decisions are frozen and are normative for Phase 2, Phase 3, and Phase 4 implementation. Phase 1 acceptance authorizes no product implementation: Phase 2 — Reminder Time Domain Implementation & JVM Proof — remains `Planned` / `NOT_STARTED` and requires separate explicit maintainer authorization. That Phase-2 `Planned` / `NOT_STARTED` statement describes the lifecycle at the 2026-11-04 Phase 1 acceptance and is preserved as historical evidence. Phase 2 implementation subsequently landed at `9c10098b3cba5dc8109cc3e4b25a7b434424167b`; the present Phase 2 `Complete` designation is a formal closure-synchronization candidate pending terminal acceptance.

The native nudge-land receipts and the hosted CI run, job, conclusion, test counts, and release-gate value are maintainer-supplied external evidence that was previously reviewed outside this repository. They are not new network observations by any OpenCode agent.

## Phase 2 — Reminder Time Domain Implementation & JVM Proof

Phase 2 implements the frozen Phase 1 reminder-time domain API on top of the existing `Reminder` model and `ReminderController`. It adds the deterministic domain behavior and the deterministic JVM proof for that behavior. Phase 2 does not modify persistence production, does not modify Compose UI, and does not perform Android identity alignment.

Phase 2 non-goals:

- no persistence production change;
- no Compose UI change;
- no Android identity alignment;
- no `app/build.gradle.kts` change;
- no new Gradle dependency;
- no test dependency change;
- no validator architecture change;
- no CI workflow change;
- no UI integration.

### Status

Complete

### Phase 2 implementation landing and formal closure candidate

The maintainer independently accepted the Phase 2 implementation commit `9c10098b3cba5dc8109cc3e4b25a7b434424167b` (parent `d4c42f79b5a997df628b1da2b8879eccfff064c9`; subject `feat: implement v0.1.5 reminder-time domain`). The single-use native transaction `nudgewhen-v0.1.5-phase2-domain-native-land-001` reached `LANDED / S10_LANDED`; exact-head GitHub Actions `CI` push run [`42355553118`](https://github.com/franchoy/nudgewhen/actions/runs/42355553118) / required `validate` job `128352751312` concluded `success` on branch `release/v0.1.5` for that same commit.

Phase 2 implemented the frozen optional reminder-time domain behavior in `Reminder` and `ReminderController` with deterministic JVM tests. Retained implementation proof: 141 JVM tests passed; five-module Python regression 245 tests / `OK`; local `--skip-android` validator 22 passed / 0 failed / 0 skipped with `release_gate=NOT_SATISFIED` because the Android group was skipped. The hosted CI `validate` job succeeded; the partial local result is not relabelled as a complete release gate. Phase 2 did not change persistence production, Compose, Android identity, product scope, Gradle/test dependencies, validator implementation, or CI workflow.

Evidence: `EXP-0080` and `EXP-0081` preserve planning, implementation, evidence-correction chronology, deviations and independent reclassifications; `EXP-0082` records this separate lifecycle closure candidate, including the noncompliant planning attempt. Phase 2 is marked `Complete` **in this closure-synchronization candidate only**. At the time of the original Phase 2 closure-candidate preparation, a separate closure commit, push, exact-head CI, native landing and terminal maintainer acceptance had not yet occurred. The closure-synchronization commit subsequently landed at `605f250c031c25e35b36f976707bb518025fe1b4` with exact-head CI `42366706308` / success; terminal formal maintainer acceptance is not independently established.

At the original Phase 2 closure-candidate preparation point, Phase 3 — Persistence Compatibility / Migration Proof was `Planned` / `NOT_STARTED` / `NOT_AUTHORIZED` and required a separate authorization. The separately authorized Phase 3 implementation has since landed; see the Phase 3 section below. The frozen Phase 1 `NWR3` decision and all historical acceptance records remain unchanged.

The implementation native receipts and hosted run are maintainer-supplied external evidence independently reviewed outside OpenCode; this documentary update is not a new OpenCode network observation.

## Phase 3 — Persistence Compatibility / Migration Proof

Phase 3 owns persistence compatibility for reminder-time operations. Phase 3 implements and proves the Phase-1-selected v0.1.5 persistence representation under the frozen Phase-1 contract. Phase 3 adds deterministic JVM proof for persistence across reminder-time setting, changing, clearing, and restart survival, and for backward loading of existing v0.1.4 NWR2 data. A new persistence backend remains out of scope. Phase 3 owns implementation, backward-load behavior, lazy same-file migration when applicable, and persistence proof.

Phase 3 non-goals:

- no production UI change;
- no Android identity alignment;
- no Gradle, validator, or CI change.

### Status

Complete

### Phase 3 implementation landing and closure-synchronization candidate

The maintainer accepted the Phase 3 NWR3 persistence implementation commit `9a732495eb099b37bd835ab65c2c507bf2778694` (parent `605f250c031c25e35b36f976707bb518025fe1b4`; subject `feat: implement v0.1.5 reminder-time persistence`). The single-use native transaction `nudgewhen-v0.1.5-phase3-persistence-native-land-001` completed as `LANDED / S10_LANDED`. Hosted GitHub Actions `CI` run [42409878438](https://github.com/franchoy/nudgewhen/actions/runs/42409878438) / required `validate` job `128515492116` concluded `success` for `push` on `release/v0.1.5` at that exact commit. Hosted five-module Python regressions: 245 tests / `OK`; full clean validator: `41 / 0 / 0`; `release_gate=SATISFIED`. Maintainer-supplied JUnit XML evidence: 100 focused persistence tests and 180 total JVM tests, zero failures/errors/skips.

The implementation uses frozen `NWR3` with backward `NWR1`/`NWR2` loading and lazy same-file migration; the original order, identity, text, and done state remain preserved. `EXP-0083` retains unsuccessful OpenCode attempts, original violations, external corrective provenance and subsequent independent review; it is not rewritten by this closure. This Phase 3 **`Complete` status is a documentary closure candidate only**; no separately published Phase 3 lifecycle-closure commit or terminal formal maintainer acceptance is claimed. `EXP-0084` records this distinct preparation. At the time of the Phase 3 closure-candidate preparation, Phase 4 was `Planned` / `NOT_STARTED` / `NOT_AUTHORIZED`; it was subsequently separately authorized and its implementation landed. The current Phase 4 closure candidate is documented in the Phase 4 section below. No Compose, Android identity, Gradle, dependency, validator, CI, or product-scope change belongs to this closure.


## Phase 4 — Minimal Compose Integration

Phase 4 owns the minimal Compose reminder-time UX layered onto the existing `ReminderScreen` / `MainActivity` integration. It adds the bounded set / change / clear affordance, retains `ReminderScreen`-owned Compose state, and keeps `MainActivity` free of `MutableState`. Phase 4 introduces no `ViewModel`, no `Flow`, no coroutines, no DI, and no navigation architecture solely for reminder time.

Phase 4 non-goals:

- no production `ReminderController` change beyond Phase 2;
- no production `FileReminderStore` change;
- no new Gradle dependency;
- no Android identity alignment;
- no integrated device validation;
- no reminder-time-driven sort, reorder, removal, dimming, or text decoration;
- no notification, alarm, or background-work affordance.

### Status

Complete

### Phase 4 implementation landing and documentary lifecycle-closure candidate

The maintainer accepted the six-file Phase 4 implementation commit `7879830a6310a3f9ea7a80e4cd6f86aff6414372` (parent `b250b519f4fb88190e518834aacce5652101ba03`; subject `feat: integrate v0.1.5 reminder-time Compose UI`). Its native single-use authorization `nudgewhen-v0.1.5-phase4-compose-implementation-native-land-002` reached `LANDED / S10_LANDED`, without a hard stop or unavailable evidence. Hosted GitHub Actions `CI` [run `42503663732`](https://github.com/franchoy/nudgewhen/actions/runs/42503663732) / required `validate` job `128801561569` concluded `success` for `push` on `release/v0.1.5` at the exact implementation SHA. The prior separate `nudge-land` infrastructure repair also landed and passed CI. The initially failed Stage transactions remain historical evidence.

The maintainer independently ran a clean offline `:app:assembleDebug` and `:app:testDebugUnitTest` build (`BUILD SUCCESSFUL`; 42 tasks executed) and verified a matching APK signing certificate before testing the installed application on one Android phone. The original app-local NWR2 file was backed up privately with an integrity check and survived data-preserving installation and read-only app launch byte-for-byte. Creating one disposable reminder migrated the file lazily to NWR3 while retaining every original record, id, text, done value and order. Guarded NWR3 checks then verified Set (`2026-11-15T09:30`), Change (`2026-11-16T14:45`), and Clear (absent `-`) changed only the test reminder time field. Cancel/Edit/recreation non-save intervals preserved data, and the committed time survived a process restart. Separately, the maintainer confirmed all nine required UI observations, including picker Back/Cancel, edit-buffer preservation, recreation draft discard, restarted display and restored Set affordance. This is bounded one-device evidence, not general Android acceptance; `EXP-0088` records provenance and limitations.

The original OpenCode deviations and later correction history in `EXP-0085`–`EXP-0087` remain unchanged. One installation command was executed before the reviewer-requested separate approval checkpoint; this is preserved as a procedural deviation. The accepted `NWR3` contract and non-downgrade limitation remain unchanged. No application version identity advance, Gradle dependency, permission, scheduling, notification, background behavior, location, voice, network or new Android component is introduced.

**Lifecycle qualifier:** The `Complete` status in this file is a **proposed documentary closure-synchronization candidate**, not a separately landed lifecycle-closure commit, exact-head closure CI or terminal maintainer acceptance. Phase 5 — Integration & Device Validation — remains `Planned` / `NOT_STARTED` / `NOT_AUTHORIZED`. The release is not merged, tagged, published or release-ready.


## Phase 5 — Integration & Device Validation

Phase 5 owns the integrated local validation and the bounded physical-device runtime acceptance for v0.1.5. It advances the Android artifact identity from the current `versionCode 5 / versionName 0.1.4` to the v0.1.5 target `versionCode 6 / versionName 0.1.5` only under separate explicit maintainer authorization. Phase 5 accepts the integrated local validation result together with bounded one-physical-device runtime evidence.

Phase 5 non-goals:

- no new Android permission;
- no new Android component;
- no new Gradle dependency;
- no new test dependency;
- no validator-architecture change;
- no general Android compatibility claim;
- no production-readiness claim.

### Status

Planned

## Phase 6 — Integrated Audit & Reconciliation

Phase 6 owns the integrated audit and reconciliation pass for v0.1.5. It cross-checks the release charter, phase list, experiment evidence, validator evidence, and device evidence for consistency. Phase 6 introduces no product functionality, Android behavior, or Android permission.

### Status

Planned

## Phase 7 — Full Pre-Release Gate

Phase 7 owns the full pre-release gate for v0.1.5, including final exact-head CI, final validator run, and the closure-candidate landing record. Phase 7 does not itself merge, tag, or publish v0.1.5; the release-bearing pull request, tag, and GitHub release are separate maintainer repository actions.

### Status

Planned
