#!/bin/bash

set -e

echo "======================================"
echo "HIAA Climate Data Pipeline"
echo "======================================"

# Determine project directory dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Calculate yesterday's date in UTC
TARGET_DATE=$(date -u -d "yesterday" +"%Y-%m-%d")

echo "Running pipeline for date: $TARGET_DATE"
echo "Start time: $(date -u)"

# Execute pipeline using project virtual environment
"$SCRIPT_DIR/.venv/bin/python" -m pipeline.main --date "$TARGET_DATE"

echo "Pipeline finished successfully"
echo "End time: $(date -u)"