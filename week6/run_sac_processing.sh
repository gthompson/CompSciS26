#!/usr/bin/env bash
set -euo pipefail

# run_sac_processing.sh
# Runs the SAC macro process.m in the current directory.
#
# Requirements:
#   - SAC installed and available as `sac` on your PATH
#   - SAC files in this directory (default: *.SAC)
#
# Optional: edit process.m to change INPUT_GLOB and filter band.

if ! command -v sac >/dev/null 2>&1; then
  echo "ERROR: `sac` not found on PATH. Install SAC or load its environment first." >&2
  exit 1
fi

if [[ ! -f "process.m" ]]; then
  echo "ERROR: process.m not found in current directory." >&2
  exit 1
fi

echo "Running SAC macro: process.m"
sac process.m
echo "Done."
