# NudgeWhen

NudgeWhen is an early-stage experimental open-source project exploring a voice-first, local-first contextual-reminder application for Android. The long-term vision is a useful, privacy-respecting application that works offline by default and lets users capture reminders through voice or contextual triggers.

## Project status

This project is in the v0.1.0 release train on the single branch `release/v0.1.0`.

## What exists now

- A minimal Android application project.
- One `:app` module.
- Kotlin and Jetpack Compose.
- One launcher activity.
- One static screen displaying the string: `NudgeWhen — Android technical baseline`.
- Gradle wrapper `9.4.1`.
- Android Gradle Plugin `9.2.1`.
- Compile and target SDK `36`; minimum SDK `26`.
- A locally generated debug APK at `app/build/outputs/apk/debug/app-debug.apk` (ignored and not committed).
- Successful local project discovery, debug assembly, and Android lint.
- Successful physical-device installation and launch on one UMIDIGI A15T running Android 13, with the exact baseline text visibly confirmed.
- Phase 3 experiment evidence in [EXP-0006](docs/agentic-development/experiments/EXP-0006.md).
- A repeatable local validation suite at [`scripts/validate-local.sh`](scripts/validate-local.sh) and [`scripts/validate_local.py`](scripts/validate_local.py) covering `required`, `docs`, and `android` groups, with a deterministic `release_gate=SATISFIED` literal printed only on the all-groups run.
- Local validation documentation in [docs/local-validation.md](docs/local-validation.md).
- Phase 4 experiment evidence in [EXP-0007](docs/agentic-development/experiments/EXP-0007.md).

## What still does not exist

The following are explicitly out of scope at this stage:

- Reminder, scheduling, contextual-list, or checklist functionality.
- Notification functionality.
- Voice or speech functionality.
- Location, geofencing, or device-state functionality.
- Persistence.
- Contextual triggers.
- Background service.
- Application networking.
- Analytics or telemetry.
- Test suite.
- CI workflow.
- A published APK or release.
- A production-readiness, stability, security, or compatibility guarantee.

A locally generated debug APK exists; no APK is published as a release artifact. Phase 4 implementation scope is complete in the current release-train candidate; clean-checkout proof execution, the repository commit, the release pull request, the annotated tag, and the GitHub release remain separately gated and have not yet occurred.

## Long-term design intentions

The long-term design intentions for NudgeWhen, presented as goals rather than implemented features, are:

- **Voice-first.** Capture reminders through voice in a natural way, with low friction.
- **Local-first.** Work offline by default. User data stays on the device unless the user explicitly opts into a sync mechanism.
- **Contextual reminders.** Let reminders be triggered by context (time, location, device state, or other signals) rather than by manual checks.

These are long-term goals. None of them is implemented in the current state of the repository.

## Agentic-development experiment

This repository is also used to evaluate OpenCode and MiniMax M3 (3x usage) as part of an open-source agentic-development methodology. Later, Hermes may be evaluated for bounded orchestration of an already validated OpenCode workflow. Hermes is not yet integrated. The methodology is documented in `docs/agentic-development/`.

## Current release train

The project follows a phased release train on the single branch `release/v0.1.0`:

- **Phase 0** — Release charter and experiment protocol: complete.
- **Phase 1** — Open-source community baseline: complete.
- **Phase 2** — OpenCode governance baseline: complete.
- **Phase 3** — Minimal static Android technical baseline: complete.
- Phase 4 — Local validation baseline: complete.
- **Phase 5** — GitHub Actions CI baseline: complete.
- **Phase 6** — Agent evaluation evidence: complete.
- **Phase 7** and later — the final pre-release gate: planned.

No delivery dates or completion promises are made.

## Phase 2 — OpenCode governance baseline

Phase 2 established the project-local OpenCode governance baseline. The Phase 2 governance baseline consists of:

- Repository-root [`AGENTS.md`](AGENTS.md) — the repository-local OpenCode operational contract and the project-local OpenCode configuration for Phase 2.
- [`docs/agentic-development/opencode-governance.md`](docs/agentic-development/opencode-governance.md) — the companion governance document that explains the rationale and selected examples.
- `docs/agentic-development/experiments/EXP-0005.md` — the Phase 2 experiment evidence.

`AGENTS.md` is the repository-local OpenCode operational contract. No machine-readable OpenCode configuration file (`opencode.json`, `opencode.jsonc`, `.opencode/`, or any successor) was added in Phase 2. OpenCode skills, custom commands, agents, plugins, MCP configuration, and Hermes integration remain deferred.

## Phase 3 — Android technical baseline

Phase 3 established a minimal static Android technical baseline. It does not introduce any reminder, voice, location, or background functionality. The application displays a single static text string and exists only to prove the project builds, lints, installs, launches, and displays the declared content on a real device.

See [EXP-0006](docs/agentic-development/experiments/EXP-0006.md) for the complete experiment evidence, including the recorded build-attempt chronology, the five Stage 2 deviations, the maintainer-approved AndroidX merged-manifest allowlist, and the physical-device launch evidence.

## Phase 4 — Local validation baseline

Phase 4 established a repeatable local validation baseline. The validation suite covers required-files presence, documentation hygiene, and Android build / lint / APK / merged-manifest checks. The Phase 4 implementation scope is complete in the current release-train candidate.

The local validation suite runs locally and does not require network access during ordinary execution. The literal `release_gate=SATISFIED` is printed only on the all-groups run. Partial runs and runs that include `--skip-android` do not satisfy the release gate. Clean-checkout proof execution and the repository commit remain separately gated and have not yet been performed.

See [docs/local-validation.md](docs/local-validation.md) for the local validation guide and [EXP-0007](docs/agentic-development/experiments/EXP-0007.md) for the Phase 4 experiment evidence, including the recorded attempt chronology, the accepted Stage 2 result, the accepted post-Build usage evidence and Build-stage delta, and the current closure-stage state.

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

The debug APK is generated at `app/build/outputs/apk/debug/app-debug.apk`. Build output and caches are ignored and not committed. No APK is published as a release artifact.

## Physical-device verification

The Phase 3 application was installed and launched on one physical device, not as a compatibility matrix:

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

- [Release charter](docs/releases/v0.1.0/release-charter.md)
- [Phase list](docs/releases/v0.1.0/phase-list.md)
- [Experiment protocol](docs/agentic-development/experiment-protocol.md)
- [Evaluation template](docs/agentic-development/evaluation-template.md)
- [Local validation guide](docs/local-validation.md)
- [Experiment records directory](docs/agentic-development/experiments/)
- [EXP-0006 — Phase 3 evidence](docs/agentic-development/experiments/EXP-0006.md)
- [EXP-0007 — Phase 4 evidence](docs/agentic-development/experiments/EXP-0007.md)
- [AGENTS.md](AGENTS.md)
- [OpenCode governance companion](docs/agentic-development/opencode-governance.md)
