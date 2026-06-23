# NudgeWhen

NudgeWhen is an early-stage experimental open-source project exploring a voice-first, local-first contextual-reminder application for Android. The long-term vision is a useful, privacy-respecting application that works offline by default and lets users capture reminders through voice or contextual triggers.

## Project status

This project is in the very early stages of an open-source release train. At the time of writing:

- There is no Android application project, no application code, and no runnable build.
- There is no Gradle configuration, no APK, no test suite, no CI workflow, and no published release.
- There is no installation procedure.
- The repository currently contains project and release documentation, community-health files, OpenCode governance documentation, and agentic-development experiment records.
- A single maintainer is responsible for the project.

## What does not exist yet

The following are explicitly out of scope for the current state of the project:

- Reminder functionality (scheduling, notifications, storage of reminders, or any related behaviour).
- Voice or speech functionality (recording, transcription, or synthesis).
- Location, geofencing, device-state, contextual-list, or checklist functionality.
- An Android application project, Gradle build, APK, test suite, or CI workflow.
- A published release, installation procedure, architecture guide, API documentation, or compatibility matrix.
- A moderation team, a multi-maintainer body, or a formal support channel.
- A production readiness, stability, security, or support guarantee.

## Long-term design intentions

The long-term design intentions for NudgeWhen, presented as goals rather than implemented features, are:

- **Voice-first.** Capture reminders through voice in a natural way, with low friction.
- **Local-first.** Work offline by default. User data stays on the device unless the user explicitly opts into a sync mechanism.
- **Contextual reminders.** Let reminders be triggered by context (time, location, device state, or other signals) rather than by manual checks.

These are long-term goals. None of them is implemented in the current state of the repository.

## Agentic-development experiment

This repository is also used to evaluate OpenCode and MiniMax M3 (3x usage) as part of an open-source agentic-development methodology. Later, Hermes may be evaluated for bounded orchestration of an already validated OpenCode workflow. Hermes is not yet integrated. The methodology is documented in `docs/agentic-development/`.

## Current release train

The project follows a phased release train on the single branch `release/v0.1.0`. At the time of writing:

- **Phase 0** — Release charter and experiment protocol: complete.
- **Phase 1** — Open-source community baseline: complete.
- **Phase 2** — OpenCode governance baseline: complete.
- **Phase 3** — Minimal static Android technical baseline: planned.
- Later phases — local validation, CI, evaluation evidence, and the final pre-release gate: planned.

No delivery dates or completion promises are made.

## Phase 2 — OpenCode governance baseline

Phase 2 established the project-local OpenCode governance baseline. The Phase 2 governance baseline consists of:

- Repository-root [`AGENTS.md`](AGENTS.md) — the repository-local OpenCode operational contract and the project-local OpenCode configuration for Phase 2.
- [`docs/agentic-development/opencode-governance.md`](docs/agentic-development/opencode-governance.md) — the companion governance document that explains the rationale and selected examples.
- `docs/agentic-development/experiments/EXP-0005.md` — the Phase 2 experiment evidence.

`AGENTS.md` is the repository-local OpenCode operational contract. No machine-readable OpenCode configuration file (`opencode.json`, `opencode.jsonc`, `.opencode/`, or any successor) was added in Phase 2. OpenCode skills, custom commands, agents, plugins, MCP configuration, and Hermes integration remain deferred. There is still no Android application project or implemented application functionality. Phase 3 — Android Technical Baseline is the next planned phase.

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
- [Experiment records directory](docs/agentic-development/experiments/)
