#!/usr/bin/env bash
# tools/wii/devkitpro.sh — run a command inside devkitPro with devkitPPC (Wii).
# Usage: tools/wii/devkitpro.sh <command...>
# Modeled on tools/switch/devkitpro.sh.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Pin the image so the toolchain doesn't drift under the build.
DEVKITPRO_IMAGE="${DEVKITPRO_IMAGE:-devkitpro/devkitppc:20261102}"

# The build tree must be visible inside the container at the same path,
# because CMake caches absolute paths.
docker run --rm \
  -v "$REPO_ROOT:$REPO_ROOT" \
  -w "$REPO_ROOT" \
  -e DEVKITPRO=/opt/devkitpro \
  -e DEVKITPPC=/opt/devkitpro/devkitPPC \
  -e CCACHE_DIR="${CCACHE_DIR:-$REPO_ROOT/build/.ccache}" \
  -u "$(id -u):$(id -g)" \
  "$DEVKITPRO_IMAGE" \
  "$@"
  