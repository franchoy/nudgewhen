# Security Policy

NudgeWhen is in an early experimental stage. This document explains how to report a suspected security vulnerability, what to expect, and what the project does and does not promise.

## Current state

At the time of writing, there is no released or runnable application. There is no Android application code, no Gradle build, no APK, no test suite, no CI workflow, and no published release. There is no supported-version matrix. Supported-version guidance will be added when releasable software exists.

## Primary reporting route: GitHub private vulnerability reporting

GitHub private vulnerability reporting is enabled on this repository and is the primary route for reporting suspected security vulnerabilities. It submits the vulnerability privately to the repository maintainers.

To file a report:

1. Open the repository on GitHub.
2. Open the repository's **Security** area (sometimes labelled "Security and quality").
3. Select **Report a vulnerability**.
4. Complete and submit the private report.

This is the ordinary reporter workflow. It is distinct from the maintainer's draft-advisory workflow, which is not described here because it is not the reporter's route.

## Fallback route: minimal public issue requesting private contact

If GitHub private vulnerability reporting is not available for any reason, open a minimal public issue that requests a private contact route.

The issue body must contain only the request for private contact. It must NOT contain:

- Vulnerability details.
- Exploit steps.
- Reproduction steps.
- Proof of concept.
- Logs, stack traces, or screenshots.
- Personal data, credentials, or session identifiers.
- Affected component names, file paths, line numbers, or version strings.
- Any information that could be used to construct an exploit.

Sensitive material must not be filed as a normal public bug report.

## What to expect after a report

Reports are reviewed on a best-effort basis by the single project maintainer. The project does not promise:

- A response time.
- A remediation time.
- A coordinated-disclosure timeline or embargo length.
- CVE assignment.
- A bug bounty or any monetary award.
- A security audit or formal verification.
- A specific fix version or release date.
- Any other security guarantee.

## What the project does not have

The project does not currently have:

- A security audit.
- A bug bounty program.
- A published threat model.
- A signed release process.
- An out-of-band communication channel for security.
- Encryption guarantees beyond what the chosen platform provides.
- A privacy program.

## Ordinary non-security defects

Ordinary non-security defects (typos, broken links, missing documentation, application defects when an application exists) are reported through the bug-report issue form, not through the security-reporting route.

## Conduct reports are separate

Concerns about contributor behaviour are reported through the routes described in `CODE_OF_CONDUCT.md`, not through the security-reporting route.

## No invented contact channel

This document does not publish a personal email address. The reporting routes above are the only routes.

## Supported versions

There are no supported versions at this time. When a releasable version exists, this document will be updated to specify which versions receive security updates and on what basis.
