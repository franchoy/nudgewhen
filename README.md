# NudgeWhen

NudgeWhen is an early-stage experimental open-source project exploring a voice-first, local-first contextual-reminder application for Android. The long-term vision is a useful, privacy-respecting application that works offline by default and lets users capture reminders through voice or contextual triggers.

## Project status

NudgeWhen is currently in the `v0.1.4` release train, **Mark Reminder Done**, on the single branch `release/v0.1.4`. Phase 0 — Release Definition & Bootstrap — is `Complete`; Phase 1 — Done State Architecture Contract — is `Planned`; Phases 2 through 7 are `Planned`; phase model: `1 Complete / 7 Planned`. Phase 1 implementation has not started. v0.1.4 is **not** merged, **not** tagged, **not** published, and is not claimed release-ready. The pre-v0.1.4 maintenance window is closed; PR #11 setup-java v6 was merged into `main`; the current `setup-java` pin is `v6.0.0`; AGP remains `9.2.1`; Gradle remains `9.4.1`; PR #13 / AGP 9.4 migration is outside the v0.1.4 release train and is deferred until after v0.1.4. Phase 0 performed release-definition, governance, and document-bootstrap synchronization and the initial dirty-candidate repository-consistency validation. Phase 0 did not implement any done-state functionality; did not modify `app/build.gradle.kts`; did not modify any product Kotlin; did not modify persistence production code; did not modify Compose; did not perform Android identity alignment; and did not select a concrete persistence representation. The committed Android artifact identity remains `versionCode 4 / versionName 0.1.3`; the v0.1.4 target identity of `versionCode 5 / versionName 0.1.4` is recorded as a future target only. The latest stable published release is `v0.1.3` — Editable Local Reminders; v0.1.3 phase model: `8 Complete / 0 Planned`. At the retained Phase-7 pre-release evidence point, v0.1.3 had not yet been merged, tagged, or published and was not claimed release-ready; those values are historical-at-that-time evidence. Its release-bearing merge, annotated tag, and GitHub Release have since completed. Done-state functionality is **not** yet implemented; Phase 0 only froze the release definition. v0.1.3 Phase 2 has landed the domain-level reminder editing implementation and deterministic JVM proof; editing domain implementation: `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. v0.1.3 Phase 3 has landed the persistence compatibility proof: the existing NWR1 remains compatible with edit operations; id/index/neighbors/order persist across edit/reload; fresh store/controller restores edited text; existing valid NWR1 supports load/edit/save/reload; Unicode edit round-trip is proven; no production persistence change was made; NWR1 migration: `NOT_REQUIRED_BY_PHASE_3_TEST_EVIDENCE`. Persistence compatibility proof: `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. v0.1.3 Phase 4 has landed the minimal Compose editing UX layered onto the existing `ReminderScreen` integration; existing reminder text can now be edited from `ReminderScreen` while preserving identity, list position, and persistence contracts inherited from Phases 2/3. Compose editing UX: `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. User-facing textual editing: `IMPLEMENTED_AT_SOURCE_LEVEL`. Integrated local validation for v0.1.3 Phase 5: `PASS` (Python validator `Ran 100 tests / OK`; `required` `11/0/0`; `docs` `11/0/0`; full offline `39 / 0 / 0`; raw validator literal: `release_gate=SATISFIED`); current-facing Phase-7 pre-release evidence: accepted at first-landed HEAD `4213fd2f6750a71bc91d7e3516e043bf037aaff1` with exact-head hosted CI success, standard regression `244 / OK`, definitive clean validator `41 / 0 / 0`, and `release_gate=SATISFIED`; bounded physical-device validation: `PASS_ONE_PHYSICAL_DEVICE_ONLY`; P5_01 through P5_13: `PASS`. Current Android identity: `versionCode 4 / versionName 0.1.3`. Target Android identity: `versionCode 4 / versionName 0.1.3`. At that retained Phase-7 pre-release evidence point, release readiness was `NO`; merged was `NO`; tagged was `NO`; published was `NO`. General Android compatibility: `NOT_CLAIMED`. Multi-device validation: `NOT_CLAIMED`. Production readiness: `NOT_CLAIMED`. The completed `v0.1.2` — **Local Reminder Foundation** — release remains historical and provides the inherited local reminder baseline. Phases 0 and 1 did not implement reminder editing; Phase 2 implemented only the frozen edit domain API and its deterministic JVM proof and did not implement persistence across edit or any user-facing editing flow; Phase 3 proved persistence compatibility and did not implement any user-facing editing flow; Phase 4 implemented the bounded Compose editing UX on `ReminderScreen` and did not perform integrated/device validation or Android identity alignment. Phase 5 — Integration & Device Validation — has landed the Android artifact identity alignment, the integrated local validation at HEAD `1cfb9c373abfa24cf10f23daa152f4a410932d26`, and the bounded one-physical-device runtime acceptance; integrated/device validation and Android identity alignment are `Complete`; general Android compatibility, multi-device validation, and production readiness remain `NOT_CLAIMED`. That retained synchronized pre-release state did not claim v0.1.3 was merged, tagged, published, or release-ready.

## What exists now

- A minimal Android application project.
- One `:app` module.
- Kotlin and Jetpack Compose.
- One launcher activity.
- Gradle wrapper `9.4.1`.
- Android Gradle Plugin `9.2.1`.
- Compile and target SDK `36`; minimum SDK `26`.
- A repeatable local validation suite at [`scripts/validate-local.sh`](scripts/validate-local.sh) and [`scripts/validate_local.py`](scripts/validate_local.py) covering `required`, `docs`, and `android` groups, with a deterministic `release_gate=SATISFIED` literal printed only on the all-groups run.
- Local validation documentation in [docs/local-validation.md](docs/local-validation.md).
- A GitHub Actions CI workflow.
- Historical `v0.1.0` release evidence, including the published GitHub `v0.1.0` release and the v0.1.0 release documentation under `docs/releases/v0.1.0/`.
- A locally generated debug APK at `app/build/outputs/apk/debug/app-debug.apk` (ignored and not committed).
- The inherited v0.1.2 Phase 2 reminder domain core remains part of the current baseline: a deterministic `Reminder` model, a `ReminderStore` interface, a `ReminderController`, and deterministic JVM tests for the domain core under `app/src/test/kotlin/...`. JUnit 4.13.2 is the Phase 2 test-only dependency. The existing `android` validation group now runs `:app:testDebugUnitTest`; no new validation group was added.
- The inherited v0.1.2 Phase 3 local persistence layer remains part of the current baseline: a `FileReminderStore` production implementation belonging to the local persistence layer; deterministic persistence JVM tests; persistence round-trip proven; persisted ordering proven; removal persistence proven at the store/domain boundary; restoration proven using a newly constructed `FileReminderStore`/`ReminderController` in JVM evidence; combined JVM total of 56 tests, 0 failures, 0 errors, and 0 skipped.
- The inherited v0.1.2 Phase 4 minimal Android reminder UI remains part of the current baseline: `ReminderScreen` is implemented; `MainActivity` integrates the local persistence (`FileReminderStore` over app-private `filesDir`) with the `ReminderController`; textual create, visible reminder list, and permanent remove are present; persisted/oldest-first ordering is preserved; production UUID reminder IDs are used; source-level application-startup restoration is integrated; Compose presentation state is owned by `ReminderScreen`; no new Android component or permission was introduced.
- The inherited v0.1.2 Phase 5 integrated validation and one-device runtime-acceptance evidence remains part of the current baseline: Phase 5B Android artifact identity alignment is landed; Phase 5C exact-head integrated local validation is accepted at HEAD `e6a10bde87aa5841c5669d91512d7040089b100a` (Python validator `Ran 100 tests / OK`; `required` `11/0/0`; `docs` `11/0/0`; full offline `39/0/0`; `release_gate=SATISFIED`); Phase 5D-R8 one-device runtime acceptance is accepted on one physical `PA2310GBB` running Android 13 (`ONE_PHYSICAL_DEVICE_ONLY`); runtime checkpoints P5-01 through P5-07 are `PASS`; P5-08 is `DEVICE_PROOF_NOT_REQUIRED` because retained deterministic Phase 3 JVM persistence evidence already covers malformed-file rejection. The local reminder lifecycle is now implemented at source level with persisted ordering, permanent removal, and start-up restoration; the runtime evidence is explicitly scoped to one physical `PA2310GBB` on Android 13 and is not a general Android compatibility or production-readiness statement.

## What still does not exist

The following functionality does not yet exist in the current repository state:

- Multi-device or general Android compatibility validation of the integrated v0.1.2 reminder lifecycle; only one physical `PA2310GBB` on Android 13 has runtime acceptance evidence (`ONE_PHYSICAL_DEVICE_ONLY`).
- Scheduling, contextual-list, or checklist functionality.
- Notification functionality.
- Voice or speech functionality.
- Location, geofencing, or device-state functionality.
- Contextual triggers.
- Background service.
- Application networking.
- Analytics or telemetry.
- A production-readiness, stability, security, or compatibility guarantee.

`v0.1.3` — **Editable Local Reminders** — is the latest stable published release and remains historical evidence for the active `v0.1.4` release train. `v0.1.3` inherits the completed `v0.1.2` Local Reminder Foundation baseline: the reminder domain core, local `FileReminderStore` persistence, minimal Compose reminder UI, textual create, visible reminder list, permanent remove, persisted ordering, startup restoration, and the accepted one-device Android 13 runtime evidence remain implemented. `v0.1.3` authorizes textual editing of an existing local reminder while preserving its identity, list position, and persistence across restart. `v0.1.3` phase model: `8 Complete / 0 Planned`. Phases 0 and 1 of `v0.1.3` did not implement reminder editing; Phase 1 produced the frozen editing architecture contract. Phase 2 — Editing Domain Implementation & JVM Proof — has landed the frozen `edit(id: String, text: String): Boolean` domain API and the deterministic controller JVM proof; the editing domain implementation is `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. Phase 3 — Persistence Compatibility Proof — has landed the persistence compatibility proof: the existing NWR1 remains compatible with edit operations; id/index/neighbors/order persist across edit/reload; fresh store/controller restores edited text; existing valid NWR1 supports load/edit/save/reload; Unicode edit round-trip is proven; no production persistence change was made; NWR1 migration: `NOT_REQUIRED_BY_PHASE_3_TEST_EVIDENCE`. The persistence compatibility proof is `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`. Phase 4 — Minimal Compose Editing UX — has landed the bounded Compose editing UX on the existing `ReminderScreen`: existing reminder text can now be edited from `ReminderScreen` while the identity/list position/persistence contracts inherited from Phases 2/3 are preserved; the Compose editing UX is `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`; user-facing textual editing is `IMPLEMENTED_AT_SOURCE_LEVEL`. Integrated/device validation for `v0.1.3` Phase 5 is `Complete`: integrated local validation accepted at HEAD `1cfb9c373abfa24cf10f23daa152f4a410932d26` (`required` `11/0/0`; `docs` `11/0/0`; full offline `39 / 0 / 0`; raw validator literal: `release_gate=SATISFIED`); current-facing Phase-7 pre-release evidence: accepted at first-landed HEAD `4213fd2f6750a71bc91d7e3516e043bf037aaff1` with exact-head hosted CI success, standard regression `244 / OK`, definitive clean validator `41 / 0 / 0`, and `release_gate=SATISFIED`; bounded physical-device validation: `PASS_ONE_PHYSICAL_DEVICE_ONLY`; P5_01 through P5_13: `PASS`; general Android compatibility: `NOT_CLAIMED`; multi-device validation: `NOT_CLAIMED`; production readiness: `NOT_CLAIMED`. Current Android identity: `versionCode 4 / versionName 0.1.3`; target Android identity: `versionCode 4 / versionName 0.1.3`; Android identity alignment is `Complete`. At that retained Phase-7 pre-release evidence point, release readiness was `NO`; merged was `NO`; tagged was `NO`; published was `NO`. Phase 7 — Full Pre-Release Gate — is `Complete` in this closure-synchronization candidate. Completion or archive, new `Reminder` model fields, reorder or custom sort, scheduling or alarms, notifications, voice or speech, location or geofencing, contextual or device-state triggers, background execution, application networking or sync, analytics or telemetry, new Android Activity/Service/Receiver/Provider components, new Android permissions, Room or DataStore replacement, ViewModel/Flow/coroutines/DI/navigation expansion solely for editing, a general Android compatibility claim, a production-readiness claim, unrelated dependency modernization, product/runtime exposure or integration of repository landing tooling such as nudge-land / nudge-commit, and Hermes or MCP integration remain explicit release non-goals.

## Long-term design intentions

The long-term design intentions for NudgeWhen, presented as goals rather than implemented features, are:

- **Voice-first.** Capture reminders through voice in a natural way, with low friction.
- **Local-first.** Work offline by default. User data stays on the device unless the user explicitly opts into a sync mechanism.
- **Contextual reminders.** Let reminders be triggered by context (time, location, device state, or other signals) rather than by manual checks.

These are long-term goals. Voice-first capture and contextual-reminder behavior remain future goals. The completed `v0.1.2` Local Reminder Foundation supplies the inherited minimal local reminder lifecycle and accepted one-device Android 13 runtime evidence. The active `v0.1.4` release — **Mark Reminder Done** — is at Phase 0 `Complete` and Phase 1 `Planned`/not-started; phase model: `1 Complete / 7 Planned`. Done-state functionality is **not** yet implemented; Phase 0 only froze the v0.1.4 release definition. The completed `v0.1.3` historical release — **Editable Local Reminders** — is at phase model `8 Complete / 0 Planned`: Phase 0 — Release Definition & Bootstrap — and Phase 1 — Editing Architecture Contract — are formally closed; Phase 2 — Editing Domain Implementation & JVM Proof — is `Complete`; Phase 3 — Persistence Compatibility Proof — is `Complete`; Phase 4 — Minimal Compose Editing UX — is `Complete`; Phase 5 — Integration & Device Validation — is `Complete`; Phase 6 — Integrated Audit & Reconciliation — is `Complete`; Phase 7 — Full Pre-Release Gate — is `Complete` in this closure-synchronization candidate. Phase 6-C real-use nudge-land evidence is `Complete` at landing-core commit `844db073394b9d76e847f4078b7eb12b79b07a78` (terminal state `LANDED / S10_LANDED`); the completed single-use Phase 6-C authorization `nudgewhen-v0.1.3-phase6c-first-use-001` is `PROHIBITED` from reuse. Phase 7 — Full Pre-Release Gate — is `Complete` in this closure-synchronization candidate. Phases 0 and 1 of `v0.1.3` did not implement reminder editing; Phase 2 implemented only the frozen edit domain API and its deterministic JVM proof and did not implement persistence across edit or any user-facing editing flow; Phase 3 proved persistence compatibility and did not implement any user-facing editing flow; Phase 4 implemented the bounded Compose editing UX on `ReminderScreen` and did not perform integrated/device validation or Android identity alignment. Current-facing Phase-7 pre-release evidence: accepted at first-landed HEAD `4213fd2f6750a71bc91d7e3516e043bf037aaff1` with exact-head hosted CI success, standard regression `244 / OK`, definitive clean validator `41 / 0 / 0`, and `release_gate=SATISFIED`. At that retained Phase-7 pre-release evidence point, release readiness was `NO`; merged was `NO`; tagged was `NO`; published was `NO`. General Android compatibility: `NOT_CLAIMED`. Multi-device validation: `NOT_CLAIMED`. Production readiness: `NOT_CLAIMED`.

## Agentic-development experiment

This repository is also used to evaluate OpenCode and MiniMax M3 (3x usage) as part of an open-source agentic-development methodology. Later, Hermes may be evaluated for bounded orchestration of an already validated OpenCode workflow. Hermes is not yet integrated. The methodology is documented in `docs/agentic-development/`.

## Current release train

The project follows a phased release train on the single branch `release/vX.Y.Z`. The current active branch is `release/v0.1.4` — **Mark Reminder Done**. Phase 0 — Release Definition & Bootstrap — is `Complete`; Phase 1 — Done State Architecture Contract — is `Planned`/not-started; Phases 2 through 7 are `Planned`; phase model: `1 Complete / 7 Planned`. The completed `v0.1.3` release is historical and provides the inherited edit-on-text baseline; `v0.1.2`, `v0.1.1`, and `v0.1.0` remain historical evidence.

`v0.1.0` phases (historical, complete):

- Phase 0 — Release charter and experiment protocol: complete.
- Phase 1 — Open-source community baseline: complete.
- Phase 2 — OpenCode governance baseline: complete.
- Phase 3 — Minimal static Android technical baseline: complete.
- Phase 4 — Local validation baseline: complete.
- Phase 5 — GitHub Actions CI baseline: complete.
- Phase 6 — Agent evaluation evidence: complete.
- Phase 7 — Final pre-release gate: complete.

Historical `v0.1.1` was the documentation, governance, validation, CI, supply-chain, workspace-hygiene, and release-metadata hardening release that followed the v0.1.0 baseline.

Historical `v0.1.2` — **Local Reminder Foundation** — is complete and provides the inherited local reminder baseline. Historical `v0.1.3` — **Editable Local Reminders** — is the latest stable published release and remains historical evidence for the active `v0.1.4` release train. `v0.1.3` phase model: `8 Complete / 0 Planned`. Phase 0 — Release Definition & Bootstrap — and Phase 1 — Editing Architecture Contract — are formally closed; Phase 2 — Editing Domain Implementation & JVM Proof — is `Complete`; Phase 3 — Persistence Compatibility Proof — is `Complete`; Phase 4 — Minimal Compose Editing UX — is `Complete`; Phase 5 — Integration & Device Validation — is `Complete`; Phase 6 — Integrated Audit & Reconciliation — is `Complete`; Phase 7 — Full Pre-Release Gate — is `Complete` in this closure-synchronization candidate. Phase 6-C real-use nudge-land evidence is `Complete` at landing-core commit `844db073394b9d76e847f4078b7eb12b79b07a78` (terminal state `LANDED / S10_LANDED`); the completed single-use Phase 6-C authorization `nudgewhen-v0.1.3-phase6c-first-use-001` is `PROHIBITED` from reuse. Reminder editing was not implemented by `v0.1.3` Phases 0 or 1; `v0.1.3` Phase 2 implemented only the frozen edit domain API and its deterministic JVM proof; `v0.1.3` Phase 3 proved persistence compatibility and did not implement any user-facing editing flow; `v0.1.3` Phase 4 implemented the bounded Compose editing UX on `ReminderScreen` and did not perform integrated/device validation or Android identity alignment. `v0.1.3` Phase 5 — Integration & Device Validation — has landed the Android artifact identity alignment, the integrated local validation at HEAD `1cfb9c373abfa24cf10f23daa152f4a410932d26`, and the bounded one-physical-device runtime acceptance; integrated/device validation and Android identity alignment are `Complete`; general Android compatibility, multi-device validation, and production readiness remain `NOT_CLAIMED`. Current-facing Phase-7 pre-release evidence: accepted at first-landed HEAD `4213fd2f6750a71bc91d7e3516e043bf037aaff1` with exact-head hosted CI success, standard regression `244 / OK`, definitive clean validator `41 / 0 / 0`, and `release_gate=SATISFIED`. At that retained Phase-7 pre-release evidence point, release readiness was `NO`; merged was `NO`; tagged was `NO`; published was `NO`. That retained synchronized pre-release state did not claim v0.1.3 was merged, tagged, published, or release-ready.

No delivery dates or completion promises are made.

## Phase 2 — OpenCode governance baseline (v0.1.0 historical)

Phase 2 of `v0.1.0` established the project-local OpenCode governance baseline. The Phase 2 governance baseline consists of:

- Repository-root [`AGENTS.md`](AGENTS.md) — the repository-local OpenCode operational contract.
- [`docs/agentic-development/opencode-governance.md`](docs/agentic-development/opencode-governance.md) — the companion governance document that explains the rationale and selected examples.
- [`docs/agentic-development/experiments/EXP-0005.md`](docs/agentic-development/experiments/EXP-0005.md) — the Phase 2 experiment evidence.

`AGENTS.md` is the repository-local OpenCode operational contract. A machine-readable OpenCode configuration file (`opencode.jsonc`) and project-local agent definitions under `.opencode/agents/` were introduced after Phase 2. OpenCode skills, custom commands, plugins, MCP configuration, and Hermes integration remain deferred.

## Phase 3 — Android technical baseline (v0.1.0 historical)

Phase 3 of `v0.1.0` established a minimal static Android technical baseline. It does not introduce any reminder, voice, location, or background functionality. The application displays a single static text string and exists only to prove the project builds, lints, installs, launches, and displays the declared content on a real device.

See [EXP-0006](docs/agentic-development/experiments/EXP-0006.md) for the complete experiment evidence, including the recorded build-attempt chronology, the five Stage 2 deviations, the maintainer-approved AndroidX merged-manifest allowlist, and the physical-device launch evidence.

## Phase 4 — Local validation baseline (v0.1.0 historical)

Phase 4 of `v0.1.0` established a repeatable local validation baseline. The validation suite covers required-files presence, documentation hygiene, and Android build / lint / APK / merged-manifest checks.

The local validation suite runs locally and does not require network access during ordinary execution. The literal `release_gate=SATISFIED` is printed only on the all-groups run. Partial runs and runs that include `--skip-android` do not satisfy the release gate.

See [docs/local-validation.md](docs/local-validation.md) for the local validation guide and [EXP-0007](docs/agentic-development/experiments/EXP-0007.md) for the Phase 4 experiment evidence.

## Reproducible local build

### Prerequisites

- JDK 17 or newer.
- Android SDK Platform 36.
- Android SDK Build Tools 36.0.0.
- An Android SDK environment configured through `ANDROID_HOME` or `ANDROID_SDK_ROOT`.

The Phase 3 build was verified using OpenJDK 25.0.2 on Linux x86_64. This does not imply that this is the only supported environment. Other configurations may work, but they were not validated during Phase 3.

### Commands

```bash
./gradlew projects
./gradlew :app:assembleDebug
./gradlew :app:lintDebug
```

### Output

The debug APK is generated at `app/build/outputs/apk/debug/app-debug.apk`. Build output and caches are ignored and not committed.

## Physical-device verification (v0.1.0 Phase 3 historical evidence)

The `v0.1.0` Phase 3 application was installed and launched on one physical device, not as a compatibility matrix:

- Device: UMIDIGI A15T.
- Android version: 13.
- Processor: MediaTek Helio G95.
- Memory: 8 GB RAM.
- Installation and launch succeeded.
- The exact static text was visible.

This is one evidence device, not a general compatibility statement.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the kinds of contributions useful at this stage, the issue-first discussion convention, the small-and-focused pull-request convention, the AI-assistance disclosure requirement, and the rules of engagement.

## Code of conduct

All participants are expected to follow the project code of conduct. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

To report a suspected security vulnerability, see [SECURITY.md](SECURITY.md). The primary route is GitHub private vulnerability reporting. The fallback is a minimal public issue requesting a private contact route, with no sensitive content. Security vulnerabilities are not filed as ordinary public bug reports.

## Support

This is an experimental project with a single maintainer and no formal support channel. Best-effort help is available through the configured GitHub issue forms when one matches the request:

- Defects use the bug-report form.
- Proposals use the feature-request form.
- Security reports use [SECURITY.md](SECURITY.md).
- Conduct reports use [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

No dedicated general-support form exists at this stage. No response time or support availability is guaranteed.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for the full license text.

## Related documents

- [Release charter — v0.1.4 (active)](docs/releases/v0.1.4/release-charter.md)
- [Phase list — v0.1.4 (active)](docs/releases/v0.1.4/phase-list.md)
- [Release charter — v0.1.3 (historical)](docs/releases/v0.1.3/release-charter.md)
- [Phase list — v0.1.3 (historical)](docs/releases/v0.1.3/phase-list.md)
- [Release charter — v0.1.2 (historical)](docs/releases/v0.1.2/release-charter.md)
- [Phase list — v0.1.2 (historical)](docs/releases/v0.1.2/phase-list.md)
- [Release charter — v0.1.1 (historical)](docs/releases/v0.1.1/release-charter.md)
- [Phase list — v0.1.1 (historical)](docs/releases/v0.1.1/phase-list.md)
- [Release charter — v0.1.0 (historical)](docs/releases/v0.1.0/release-charter.md)
- [Phase list — v0.1.0 (historical)](docs/releases/v0.1.0/phase-list.md)
- [Experiment protocol](docs/agentic-development/experiment-protocol.md)
- [Evaluation template](docs/agentic-development/evaluation-template.md)
- [Local validation guide](docs/local-validation.md)
- [Experiment records directory](docs/agentic-development/experiments/)
- [EXP-0006 — Phase 3 evidence](docs/agentic-development/experiments/EXP-0006.md)
- [EXP-0007 — Phase 4 evidence](docs/agentic-development/experiments/EXP-0007.md)
- [AGENTS.md](AGENTS.md)
- [OpenCode governance companion](docs/agentic-development/opencode-governance.md)
