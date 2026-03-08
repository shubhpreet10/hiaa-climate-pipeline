#!/bin/bash

set -e

echo "======================================"
echo "HIAA Climate Data Pipeline"
echo "======================================"

# Calculate yesterday's date in UTC
TARGET_DATE=$(date -u -d "yesterday" +"%Y-%m-%d")

echo "Running pipeline for date: $TARGET_DATE"
echo "Start time: $(date -u)"

# Run pipeline
python -m pipeline.main --date "$TARGET_DATE"

echo "Pipeline finished successfully"
echo "End time: $(date -u)"