# Phase List — NudgeWhen v0.1.3

**Document status:** v0.1.3 Phase 0 closure phase-list — Phases 0 through 0 complete; Phase 0 — Release Definition & Bootstrap — is `Complete`; Phase 1 — Editing Architecture Contract — is the next lifecycle phase and remains `Planned`; Phases 2 through 7 remain `Planned`; 1 Complete / 7 Planned. This document is normative for the eight-phase ordering and per-phase scope. It does not claim that Phase 1 has started or that v0.1.3 is ready.

## Phase 0 — Release Definition & Bootstrap

Phase 0 completed the v0.1.3 release-definition, governance, and document-bootstrap synchronization, including the active release charter, phase list, current-facing tracked governance, machine-readable release contract, local-validation documentation, and the initial dirty-candidate repository-consistency validation. Phase 0 did not implement reminder editing and did not change `app/build.gradle.kts`. Phase 1 — Editing Architecture Contract — is the next lifecycle phase and remains `Planned`.

### Status

Complete

## Phase 1 — Editing Architecture Contract

Phase 1 owns the exact editing semantics contract. It decides whitespace normalization for edits, whitespace-only edit behavior, identical-text edit behavior, save/cancel interaction, the edit widget or affordance, and edit-buffer behavior across Activity recreation. Phase 1 is architecture-only and produces no product code or tests.

### Status

Planned

## Phase 2 — Editing Domain Implementation & JVM Proof

Phase 2 owns the domain-level edit implementation on top of the existing `Reminder` model and `ReminderController`. It adds the domain edit behavior and deterministic JVM proof. Phase 2 does not modify persistence or Compose UI.

### Status

Planned

## Phase 3 — Persistence Compatibility Proof

Phase 3 owns persistence compatibility for edit operations. It determines
and proves whether the existing `FileReminderStore` and `NWR1` persisted
format remain valid through edits and adds deterministic JVM proof for
persistence across edit. Phase 0 does not pre-decide the persistence-format
outcome; any format change would require separate Phase 3 evidence and
authorization. A new persistence backend remains out of scope.

### Status

Planned

## Phase 4 — Minimal Compose Editing UX

Phase 4 owns the minimal Compose editing UX layered onto the existing `ReminderScreen` / `MainActivity` integration. It adds the bounded editing affordance, retains `ReminderScreen`-owned Compose state, and keeps `MainActivity` free of `MutableState`. Phase 4 introduces no `ViewModel`, no `Flow`, no coroutines, no DI, and no navigation architecture solely for editing.

### Status

Planned

## Phase 5 — Integration & Device Validation

Phase 5 owns the integrated local validation and the bounded device/end-to-end validation for v0.1.3. If separately authorized, Phase 5 may also own the Android current-identity alignment (versionCode 4 / versionName 0.1.3) via a consistent `app/build.gradle.kts` change. Phase 5 introduces no new Android permission, component, Gradle dependency, test dependency, or validator architecture.

### Status

Planned

## Phase 6 — Integrated Audit & Reconciliation

Phase 6 owns the integrated audit and reconciliation pass for v0.1.3. It cross-checks release charter, phase list, experiment evidence, validator evidence, and device evidence for consistency. Phase 6 introduces no product functionality, Android behavior, or Android permission.

### Status

Planned

## Phase 7 — Full Pre-Release Gate

Phase 7 owns the full pre-release gate for v0.1.3, including final exact-head CI, final validator run, and the closure-candidate landing record. Phase 7 does not itself merge, tag, or publish v0.1.3; the release-bearing pull request, tag, and GitHub release are separate maintainer repository actions.

### Status

Planned