# Release Charter — NudgeWhen v0.1.2

**Document status:** Accepted — Phases 0 through 1 complete; Phase 2 current; Phases 2 through 7 Planned.
**Release name:** NudgeWhen v0.1.2 — Local Reminder Foundation.
**Version:** `v0.1.2`.
**Current Android artifact identity:** `versionCode = 2`, `versionName = "0.1.1"`. This is the v0.1.1 identity still recorded in `app/build.gradle.kts`; v0.1.2 does not yet deliver the target metadata.
**Target Android artifact identity:** `versionCode = 3`, `versionName = "0.1.2"`. The target metadata is **not yet delivered** to `app/build.gradle.kts` at Phase 0.
**Active release branch:** `release/v0.1.2`.

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

Phase 0 — Release Definition and Bootstrap — is the **current** lifecycle
phase for v0.1.2 at the time this charter is first created.

- The formal phase-list and release contract record Phase 0 and Phase 1 as
  `Complete`; Phases 2 through 7 remain `Planned`, with Phase 2 — Reminder
  Domain Core — the current lifecycle phase.
- **Candidate A** is `Complete, Committed, Pushed, Exact-head CI Pass`.
  Candidate A established the release-neutral product-scope validator
  architecture and the supporting experiment evidence.
- Candidate B completed active-release synchronization across `AGENTS.md`,
  `README.md`, `scripts/release_contract.json`, the v0.1.2 release charter,
  the v0.1.2 phase list, and cumulative `EXP-0035` evidence.
- This charter is the first Candidate B artifact. Candidate B is **not yet
  committed** when this charter is first created.
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
  Phase 1 `Complete`. Phase 2 — Reminder Domain Core — is the current
  lifecycle phase, remains `Planned`, and its implementation has not started.

Persistence technology is not yet frozen at Phase 0. Its selection requires
later architecture evidence and must remain within the no-new-component /
no-new-permission boundary unless separately justified.

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
runtime file APIs with no production persistence dependency. The exact
Kotlin/JVM test-library dependency remains unselected and is owned by
Phase 2. Any new helper, plugin, runtime guard, or other agentic-development
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
the no-new-component / no-new-permission boundary. The exact Kotlin/JVM
test-library dependency is owned by Phase 2 and is not selected here.

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
