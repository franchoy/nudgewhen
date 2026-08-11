FROM mcr.microsoft.com/devcontainers/base:noble@sha256:c5cc2b45afe06a1df3aba17e58ba0dc4a02b999493198dab37dd0ccd4e2b0705

ARG OPENCODE_VERSION=1.18.16
ENV DEBIAN_FRONTEND=noninteractive

# Core OS packages required for the NudgeWhen Codespace.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    openjdk-17-jdk-headless \
    python3 \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI from the official upstream apt repository.
# Verify the keyring SHA-256 before configuring apt to prevent supply-chain tampering.
RUN curl -fsSL -o /tmp/githubcli-archive-keyring.gpg \
        https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    && echo "6084d5d7bd8e288441e0e94fc6275570895da18e6751f70f057485dc2d1a811b  /tmp/githubcli-archive-keyring.gpg" \
        | sha256sum -c - \
    && mkdir -p /etc/apt/keyrings \
    && chmod 0755 /etc/apt/keyrings \
    && install -m 0644 /tmp/githubcli-archive-keyring.gpg /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && rm -rf /tmp/githubcli-archive-keyring.gpg /var/lib/apt/lists/*

# Android SDK location.
ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=/opt/android-sdk

# Download, verify, and install Android command-line tools.
RUN mkdir -p "${ANDROID_HOME}/cmdline-tools" \
    && curl -fsSL -o /tmp/commandlinetools.zip \
        https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip \
    && echo "4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583  /tmp/commandlinetools.zip" \
        | sha256sum -c - \
    && unzip -q /tmp/commandlinetools.zip -d "${ANDROID_HOME}/cmdline-tools" \
    && mv "${ANDROID_HOME}/cmdline-tools/cmdline-tools" "${ANDROID_HOME}/cmdline-tools/latest" \
    && rm -f /tmp/commandlinetools.zip

# PATH includes Android tools, preserving base image PATH.
ENV PATH="${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/build-tools/36.0.0:${PATH}"

# Accept Android SDK licenses and install required SDK packages.
RUN yes | sdkmanager --licenses > /dev/null \
    && sdkmanager --install "platforms;android-36" "build-tools;36.0.0" "platform-tools"

# Install OpenCode CLI without modifying shell profile.
# The official installer places the executable at ${HOME}/.opencode/bin/opencode;
# copy it to /usr/local/bin/opencode after build-time version verification.
RUN curl -fsSL https://opencode.ai/install \
        | bash -s -- \
            --version "${OPENCODE_VERSION}" \
            --no-modify-path \
    && test -x "${HOME}/.opencode/bin/opencode" \
    && install -m 0755 "${HOME}/.opencode/bin/opencode" /usr/local/bin/opencode \
    && [ "$(/usr/local/bin/opencode --version)" = "${OPENCODE_VERSION}" ] \
    && rm -rf "${HOME}/.opencode"