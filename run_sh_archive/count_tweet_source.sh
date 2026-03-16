#!/bin/bash

ARCHIVE_JA_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive_ja/"
DEVICE_COUNT_TABLE_PATH="/work/s245302/Ota-Workspace/tables/sampled_device_counts.csv"
SAMPLE_PER_FILE=1000

TEMP_DEVICES=$(mktemp)
trap "rm -f '$TEMP_DEVICES'" EXIT

mkdir -p "$(dirname "$DEVICE_COUNT_TABLE_PATH")"

echo "Processing files..."

# Process all .txt files
find "$ARCHIVE_JA_PATH" -type f -name "*.txt" | while read -r txtfile; do
  # Random sampling → extract source → remove HTML tags
  shuf -n "$SAMPLE_PER_FILE" "$txtfile" 2>/dev/null | cut -f2 | \
    jq -r '.source // "(EMPTY)"' 2>/dev/null | \
    sed 's/<[^>]*>//g'
  echo "finished $txtfile"
done > "$TEMP_DEVICES"

echo "Aggregating counts..."

# Aggregate and output to CSV
{
  echo "device,count"
  sort "$TEMP_DEVICES" | uniq -c | sort -rn | sed -E 's/^ *([0-9]+) (.*)/\2,\1/'
} > "$DEVICE_COUNT_TABLE_PATH"

echo "Complete!  Output: $DEVICE_COUNT_TABLE_PATH"
head -n 11 "$DEVICE_COUNT_TABLE_PATH"