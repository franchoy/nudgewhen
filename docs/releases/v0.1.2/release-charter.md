# Release Charter — NudgeWhen v0.1.2

**Document status:** Accepted — Phases 0 through 6 complete; Phase 7 current; Phase 7 Planned.
**Release name:** NudgeWhen v0.1.2 — Local Reminder Foundation.
**Version:** `v0.1.2`.
**Current Android artifact identity:** `versionCode = 3`, `versionName = "0.1.2"`. The landed Phase 5B commit `6b16a294b3d13151baf23a239e4cf0d330a27d3e` (subject `chore: align v0.1.2 artifact identity`) delivers this identity in `app/build.gradle.kts` and in `scripts/release_contract.json` (`android.current_version_code`, `android.current_version_name`). The Phase 5B exact-head CI run `32756426800` concluded `success` with the required `validate` job `success` and produced the debug APK artifact. At Phase 0 and through earlier completed phases, the committed identity remained `versionCode = 2`, `versionName = "0.1.1"`; that historical Phase 0 statement is preserved below as historical evidence.
**Target Android artifact identity:** `versionCode = 3`, `versionName = "0.1.2"`. The target identity is delivered by the landed Phase 5B commit `6b16a294b3d13151baf23a239e4cf0d330a27d3e` rather than still undelivered. Historical Phase 0 statement (preserved): at Phase 0, the target metadata was **not yet delivered** to `app/build.gradle.kts`.
**Active release branch:** `release/v0.1.2`.

## Phase 5B Android artifact identity alignment — landed (historical)

Phase 5B Android artifact identity alignment was accepted and landed before Phase 5 integrated validation and device evidence. This was a maintainer-selected phase sequencing decision: deliver the target identity before Phase 5 device evidence, not a release-document mandate. The Phase 5B landing is recorded here as historical evidence; it is not the current state of the release.

- Commit: `6b16a294b3d13151baf23a239e4cf0d330a27d3e`.
- Parent: `ed9ad96bebca79bf0f361ce165c133bde490a61b`.
- Subject: `chore: align v0.1.2 artifact identity`.
- Commit path set: exactly six paths — `app/build.gradle.kts`, `docs/agentic-development/experiments/EXP-0040.md`, `docs/releases/v0.1.2/release-charter.md`, `docs/releases/v0.1.2/phase-list.md`, `scripts/release_contract.json`, `tests/test_validator_repository.py`.
- Push: `PASS`.
- Remote exact SHA: `6b16a294b3d13151baf23a239e4cf0d330a27d3e`.
- Exact-head CI run: `32756426800` (workflow `CI`, event `push`, branch `release/v0.1.2`, head `6b16a294b3d13151baf23a239e4cf0d330a27d3e`, conclusion `success`, required `validate` job `success`).
- Debug APK: produced.
- Android identity at Phase 5B landing: `versionCode = 3`, `versionName = "0.1.2"`. `app/build.gradle.kts` records `versionCode = 3`, `versionName = "0.1.2"`; `scripts/release_contract.json` records `android.current_version_code = 3`, `android.current_version_name = "0.1.2"`. Target identity (`target_version_code = 3`, `target_version_name = "0.1.2"`) is unchanged and is now identical to the current identity.

At the time of the Phase 5B landing, the following state applied and is preserved here as historical evidence:

- Phase 5 — Integration & Device Validation — was the current lifecycle phase and remained `Planned`.
- Phase 5 device evidence remained `NOT_YET_PERFORMED`.
- Phase 5 was **not** marked `Complete` by the Phase 5B landing.
- Phase 6 — Integrated Audit & Agent Evaluation — remained `Planned`.
- Phase 7 — Full Pre-Release Gate — remained `Planned`.

Historical Phase 5B candidate descriptions from earlier uncommitted states are preserved in `EXP-0040.md` as historical evidence.

## Phase 5 — Integration & Device Validation — completion

Phase 5 is `Complete`. This section records the accepted Phase 5 completion evidence and supersedes the historical Phase 5B landing state above.

- **Phase 5C exact-head integrated validation:** Accepted.
  - Validated HEAD: `e6a10bde87aa5841c5669d91512d7040089b100a` on `release/v0.1.2`.
  - Python validator suites: `Ran 100 tests`, `OK`.
  - `required` group: `SUMMARY pass=11 fail=0 skip=0`.
  - `docs` group: `SUMMARY pass=11 fail=0 skip=0`.
  - Full offline: `SUMMARY pass=39 fail=0 skip=0`; `release_gate=SATISFIED`.
  - Tracked `git diff --check`: no output.
  - Final repository proof at Phase 5C acceptance: HEAD `e6a10bde87aa5841c5669d91512d7040089b100a`; worktree clean; index empty; tracked `git diff --check` produced no output.
  - OpenCode did not directly surface a numeric Python command exit status; the unittest `OK` output is the accepted success evidence.

- **Phase 5D-R8 one-device runtime acceptance:** Accepted.
  - Device model: `PA2310GBB`.
  - Android version: `13`.
  - Evidence scope: `ONE_PHYSICAL_DEVICE_ONLY`.
  - Pre-reinstall installed identity: `versionCode=3`, `versionName=0.1.2`.
  - Installation method: `adb install -r app/build/outputs/apk/debug/app-debug.apk` → `Success`.
  - Post-reinstall installed identity: `versionCode=3`, `versionName=0.1.2`.
  - Clean-first-launch setup: `adb shell pm clear io.github.franchoy.nudgewhen` → `Success`.
  - Runtime checkpoints P5-01 through P5-07: `PASS`.
  - P5-08: `DEVICE_PROOF_NOT_REQUIRED`. Retained deterministic Phase 3 JVM persistence evidence already covers malformed-file rejection; device-side malformed persistence injection and detailed recovery UX are outside the v0.1.2 Phase 5 acceptance contract.

- **Device evidence boundary:** This evidence is scoped to one physical `PA2310GBB` on Android 13 only. It is `ONE_PHYSICAL_DEVICE_ONLY` evidence. It is **not** a general Android compatibility statement. It is **not** a production-readiness statement.

- **No new Android permission, component, or Gradle dependency** was introduced by Phase 5C or Phase 5D-R8.

- **Android artifact identity** remains `versionCode = 3`, `versionName = "0.1.2"`.

- **Phase 6 — Integrated Audit & Agent Evaluation — is now the current lifecycle phase and remains `Planned`.**

- **Phase 7 — Full Pre-Release Gate — remains `Planned`.**

- **v0.1.2 release is not claimed ready, merged, tagged, or published** by this Phase 5 closure.

## Background

NudgeWhen v0.1.1 completed the reusable release-aware validation baseline,
the full pre-release gate, and the agentic-development framework on which
v0.1.2 builds. The release-neutral `product_scope` extension was introduced
later by v0.1.2 Candidate A and must not be attributed to historical v0.1.1
work.

v0.1.2 is the first release to authorize reminder and persistence
capabilities through the active release-neutral product-scope contract.
Candidate B synchronization made the v0.1.2 contract active. It must add the
smallest possible footprint that delivers a complete local reminder lifecycle
while preserving the single-activity, no-new-permission Android boundary and
the agentic-development contracts established by v0.1.1.

## Phase 0 status

Phase 0 — Release Definition and Bootstrap — was the **current** lifecycle
phase for v0.1.2 at the time this charter is first created (historical).

- At the time this charter was first created, the formal phase-list and
  release contract recorded Phases 0 through 4 as `Complete`; Phases 5
  through 7 remained `Planned`; Phase 5 — Integration & Device Validation —
  was the current lifecycle phase.
- **Candidate A** is `Complete, Committed, Pushed, Exact-head CI Pass`.
  Candidate A established the release-neutral product-scope validator
  architecture and the supporting experiment evidence.
- Candidate B completed active-release synchronization across `AGENTS.md`,
  `README.md`, `scripts/release_contract.json`, the v0.1.2 release charter,
  the v0.1.2 phase list, and cumulative `EXP-0035` evidence.
- This charter is the first Candidate B artifact. Candidate B is **not yet
  committed** when this charter is first created (historical).
- The temporary v0.1.2 bootstrap exception is `TERMINATED` after accepted
  repository-consistency evidence established that the synchronized
  current-release surfaces are mutually consistent.
- Candidate-B planning, Build, corrective, validation, evidence,
  commit/push, and exact-head CI chronology is recorded in `EXP-0035`.
- Candidate A remains separately recorded in `EXP-0034`.
- Phase 0 is formally `Complete`. Phase 1 — Reminder Architecture Contract —
  is formally `Complete` in this charter after acceptance of the Phase 1
  architecture contract, the architecture commit push, and the exact-head
  CI evidence; the formal Phase 1 closure synchronization now marks
  Phase 1 `Complete`. Phase 2 — Reminder Domain Core — is `Complete`
  after acceptance of the Phase 2 domain-core commit
  `6781bccacb5324dde854a5001a939754bb309165` (`feat: add reminder domain core`,
  exact-head CI run `32708073861`, conclusion `success`), the Phase 2
  validator-integration commit
  `ba6a581f00ad2d5d4f550f95e6ccfa5da716825f` (`test: integrate reminder JVM
  tests into validator`, exact-head CI run `32711898852`, conclusion
  `success`), and the cumulative `EXP-0037` evidence. Phase 3 — Local
  Persistence — is `Complete`. Accepted implementation commit:
  `c3eb1b580b744111ed3024cfbd58a8ce3113ad35`. Subject: `feat: add local reminder persistence`. Implementation exact-head CI: `32720528488`,
  conclusion `success`. Cumulative Phase 3 closure evidence: `EXP-0038`.
  JVM evidence: 56 tests, 0 failures, 0 errors, 0 skipped. Phase 4 —
  Minimal Android Reminder UI — is `Complete`. Implementation commit:
  `05503d58416e287afd96cc1fc7c6f78df8fd2784` (parent
  `1e612d5c43c740f5aabfc4825992fce8ae8c7e9e`, subject
  `feat: add minimal reminder UI`). Implementation exact-head CI run:
  `32739280349`, conclusion `success`. Exact implementation paths:
  `app/src/main/kotlin/io/github/franchoy/nudgewhen/MainActivity.kt`
  and
  `app/src/main/kotlin/io/github/franchoy/nudgewhen/ui/ReminderScreen.kt`.
  Retained Android validation: `17 / 0 / 0`; release gate remained
  `NOT_SATISFIED` at that boundary. Accepted chronology: Phase 4A accepted with
  maintainer refinements; Phase 4B ReminderScreen accepted; Phase 4C
  MainActivity integration accepted; Phase 4D integration audit
   accepted with blocking defects `NONE`. At the Phase 4 closure
   boundary, Phase 5 — Integration & Device Validation — was the
   current lifecycle phase, remained `Planned`, and its
   implementation had not started (historical).

Persistence technology is not yet frozen at Phase 0 (historical). Its selection requires
later architecture evidence and must remain within the no-new-component /
no-new-permission boundary unless separately justified.

## Phase 5 closure summary

Phase 5 — Integration & Device Validation — is `Complete`. The accepted
Phase 5 completion evidence is:

- Phase 5B Android artifact identity alignment: landed (historical
  evidence preserved above).
- Phase 5C exact-head integrated local validation: accepted at HEAD
  `e6a10bde87aa5841c5669d91512d7040089b100a`.
- Phase 5D-R8 one-device runtime acceptance: accepted on one physical
  `PA2310GBB` running Android 13. Evidence scope is
  `ONE_PHYSICAL_DEVICE_ONLY` and is **not** a general Android
  compatibility or production-readiness statement.
- Cumulative Phase 5 experiment evidence: `EXP-0040`.

Phase 5 is `Complete`. Phase 6 — Integrated Audit & Agent Evaluation — is
now the current lifecycle phase and remains `Planned`. Phase 7 — Full
Pre-Release Gate — remains `Planned`. v0.1.2 release is **not** claimed
ready, merged, tagged, or published by this Phase 5 closure.

## Phase 6 closure summary

Phase 6 is `Complete`. The accepted Phase 6 completion evidence is:

- Phase 6F: `ACCEPTED_WITH_CORRECTION; COMPLETE`.
- Phase 6G: `ACCEPTED_WITH_CORRECTION; COMPLETE`.
- Phase 6H-A: `ACCEPTED_WITH_CORRECTION; COMPLETE`.
- C3 retained integrated validation: Python validator `Ran 100 tests / OK`; `required` `SUMMARY pass=11 fail=0 skip=0`; `docs` `SUMMARY pass=11 fail=0 skip=0`; `android offline` `SUMMARY pass=17 fail=0 skip=0`; `full offline` `SUMMARY pass=39 fail=0 skip=0`; `release_gate=SATISFIED`.
- Dependabot six pull requests #3, #4, #6, #7, #8, #9 are `CLOSED` and `UNMERGED`. Evidence class: `MAINTAINER-SUPPLIED DECISION/OBSERVATION`.
- `SUBSTANTIVE_BLOCKER_COUNT`: `0`.

Phase 7 is `Planned` and is the `next lifecycle phase`. Phase 7 is `not begun` and is `not authorized by this closure synchronization`. The v0.1.2 release is **not** claimed ready, merged, tagged, or published by this Phase 6 closure candidate.

## Release identity

- **Version:** `v0.1.2`.
- **Release title:** NudgeWhen v0.1.2 — Local Reminder Foundation.
- **Active release branch:** `release/v0.1.2`.
- **Authorized product-scope capabilities for v0.1.2** (the active
  synchronized contract authorizes exactly these):
  - `reminders`
  - `persistence`

  This authorization means those capabilities are **permitted** for v0.1.2.
  It does **not** mean they are already implemented. Reminder functionality
  and persistence are **in scope** for v0.1.2 but are **not yet implemented**
  at Phase 0.

- **Explicitly not authorized for v0.1.2:**

  Machine-recognized product_scope capabilities NOT authorized:
  - notifications
  - voice-or-speech
  - location-or-geofencing
  - networking
  - background-behavior

  Broader charter non-goals that are also excluded for v0.1.2:
  - time scheduling/alarms
  - contextual/device-state triggers
  - analytics/telemetry
- **Android boundary:** single-activity, no new permissions, no additional
  activities, services, receivers, or providers.

## Exact release objective

Deliver the first minimal, offline local reminder lifecycle while preserving
the existing single-activity, no-new-permission Android boundary and the
reusable v0.1.1 release framework. The reminder lifecycle is local-only and offline, with minimal integration
into the existing Compose application; it has no time-based, location-based,
network-based, or background behavior.

## Agentic-development objective

Reuse and extend the v0.1.1 agentic-development framework — including the
phase model, experiment-protocol evidence discipline, the
`AGENTS.md` four-category authorization matrix, the OpenCode harness
`nudge-plan` / `nudge-audit` / `nudge-build` boundary, and the local
validator — to deliver the v0.1.2 product scope. No new Android permissions or additional Android components are introduced
by the frozen release boundary. Phase 1 has frozen v0.1.2 persistence
technology as a single app-private file using standard Java/Kotlin
runtime file APIs with no production persistence dependency. Phase 2
selected JUnit 4.13.2 as the test-only JVM test dependency. Any new
helper, plugin, runtime guard, or other agentic-development
mechanism requires independent evidence and explicit scope.

## In-scope deliverables

v0.1.2 may add, in the order addressed by the phase list:

- Creation of a textual reminder.
- Local on-device persistence of reminders.
- Restoration of reminders after app restart.
- Display of existing reminders in the existing Compose application.
- One minimal lifecycle-ending action for a reminder. The exact
  completion-or-removal semantics are defined in Phase 1.
- Deterministic domain and persistence tests.
- Minimal integration into the existing single-activity Compose application.
- Release-aware validator and documentation changes that are strictly
  necessary to permit reminder and persistence functionality.

Phase 1 has frozen v0.1.2 persistence technology as a single app-private
file using standard Java/Kotlin runtime file APIs, with no production
persistence dependency. This frozen persistence technology remains within
the no-new-component / no-new-permission boundary. Phase 2 selected
JUnit 4.13.2 as the test-only JVM test dependency.

## Explicit non-goals

v0.1.2 must **not** add any of the following:

- Voice or speech input, output, recognition, or synthesis.
- Notifications of any kind, including user-visible and heads-up
  notifications, notification channels, and notification listeners.
- Time-based scheduling, alarms, timers, or `WorkManager`-style deferred
  work.
- Location, geofencing, or any location-derived reminder trigger.
- Contextual, sensor, or device-state triggers.
- Background execution, foreground services, or any
  services/receivers/providers.
- Application networking, sync, cloud backend, or remote APIs.
- Analytics, telemetry, or any user-behavior measurement.
- Additional Android activities, services, broadcast receivers, or content
  providers.
- New Android permissions of any kind.
- Production-readiness guarantees (release stability, signed-release
  readiness, Play Store metadata, or store-listing assets).
- Hermes or MCP integration.
- A new plugin, helper, or runtime guard without accepted evidence.
- Provider migration or reversion as part of the product scope.

Reminder functionality and persistence are in scope for v0.1.2 but are
**not yet implemented** at Phase 0. They must not be described as already
existing.

## Single-release-branch and one-final-PR policy

All v0.1.2 work happens on the single branch `release/v0.1.2`. No
parallel release branches. Exactly one pull request is opened into `main`
after all eight phases and the full pre-release gate are complete. One
annotated tag and one GitHub release are created only after the release pull
request is merged. Branch creation, switching, renaming, and deletion
require a separate explicit maintainer authorization each time, as recorded
in `AGENTS.md`.

## Human approval boundaries

Every consequential action in the v0.1.2 workflow follows the
`AGENTS.md` four-category authorization matrix:

- **Category A — read-only by default:** inspection of the local working
  tree, tracked diff, cached index, and tracked validation outputs.
- **Category B — explicit Build scope:** modifications limited to the exact
  path set authorized by the current Candidate-B slice.
- **Category C — separate explicit maintainer authorization:** staging,
  committing, pushing, branch operations, pull requests, tags, releases,
  dependency changes, configuration changes, network access, and any
  identity inspection.
- **Category D — never allowed under normal project policy:** opening or
  committing private session exports; reproducing private identifiers;
  force-push; amending accepted commits; destructive cleanup.

Machine-readable permissions in `opencode.jsonc` and `.opencode/agents/`
are capability ceilings; every action still requires the exact current
maintainer authorization in the current task.

## Pre-release gates

The full pre-release gate for v0.1.2 is owned by Phase 7 — Full
Pre-Release Gate — and inherits the v0.1.1 reusable validation baseline.
At minimum, the pre-release gate must satisfy, with direct evidence and
without inferred state:

1. The active `scripts/release_contract.json` defines
   `product_scope.allowed_capabilities` as exactly
   `["reminders", "persistence"]` and remains consistent with the explicit
   non-goals.
2. All eight phases are `Complete`, each with its own accepted experiment
   evidence.
3. The complete local validator gate passes from a clean release candidate
   with no `FAIL` result and `release_gate=SATISFIED`.
4. The full unit-test matrix passes, including any v0.1.2-introduced
   domain and persistence tests.
5. The exact-head CI run on `release/v0.1.2` completes with `success` and
   the required `validate` job passes.
6. The validated pre-release candidate has a clean working tree before the
   single release-bearing pull request is opened.
7. The Android artifact identity delivered to `app/build.gradle.kts`
   matches the target v0.1.2 identity, and no Android permission or
   component outside the v0.1.1 baseline is present.

## Post-merge release-completion evidence (applied after pre-release gates pass)

Once the v0.1.2 release pull request is merged into `main` and the
pre-release gates pass, the following repository actions are performed in
order, each as a separately authorized Category C action:

1. Verify the merged `main` and the required CI.
2. Create the annotated tag `v0.1.2` at the intended merged-main commit.
3. Publish the GitHub release from that tag.
4. Verify the published release contents/artifacts correspond to the
   validated release.

## Definition of release completion

A release of v0.1.2 is **complete** when **all** of the following are
true, with direct evidence recorded in the applicable experiment records and
synchronized v0.1.2 release documents:

- Every phase (0 through 7) is `Complete`.
- The Phase 7 pre-release gate is `Satisfied`, with the exact-head CI run
  on `release/v0.1.2` succeeding and the local validator reporting
  `release_gate=SATISFIED`.
- The release pull request is merged into `main`.
- The annotated tag `v0.1.2` exists at the merged release-PR commit.
- The GitHub release for `v0.1.2` is published.
- The active `scripts/release_contract.json` and `AGENTS.md` current-release
  context remain synchronized with the closed v0.1.2 release identity.
- Required post-merge repository-state evidence is clean at the applicable
  maintainer verification boundary.

Completion of v0.1.2 closes the v0.1.2 lifecycle; the next release, if any,
will be defined under its own release charter and its own
`docs/releases/<version>/` directory.

## Cross-references

- `AGENTS.md` identifies the active v0.1.2 lifecycle.
- `scripts/release_contract.json` is the active v0.1.2 contract and
  authorizes reminders and persistence.
- `README.md` reflects the active v0.1.2 release state.
- `docs/agentic-development/opencode-governance.md` — companion governance
  document.
- `docs/agentic-development/experiment-protocol.md` — authoritative
  experiment and evidence policy; governs Candidate B's cumulative evidence
  record and the separate experiment records assigned to later agent-assisted
  tasks.
- `docs/agentic-development/evaluation-template.md` — evaluation template
  used by Phase 6.
- `docs/releases/v0.1.1/release-charter.md` — historical v0.1.1 release
  charter; reference only, not normative for v0.1.2.
- `docs/releases/v0.1.1/phase-list.md` — historical v0.1.1 phase list;
  reference only, not normative for v0.1.2.
- `docs/releases/v0.1.2/phase-list.md` — the active v0.1.2 phase list,
  updated as phases produce accepted evidence.
