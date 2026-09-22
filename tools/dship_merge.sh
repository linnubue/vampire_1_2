#!/bin/bash

# Updates DSHIP text files by combining old data and recent data. This is 
# only useful during the cruise if one wants to append to the old data file.

# Usage: ./update_file.sh old.dat new.dat

# Check if both files are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 old.dat new.dat comb.dat"
    exit 1
fi

OLD_FILE=$1
NEW_FILE=$2
COMBINED_FILE=$3

# Step 1: Find the start time from old.dat
START_TIME=$(sed -n "4p" "$NEW_FILE" | cut -c 1-10)

# Step 2: Find the overlap line (line number of START_TIME in old.dat)
OVERLAP_LINE=$(grep -n "$START_TIME" "$OLD_FILE" | cut -d: -f1)

# If no overlap is found, handle the case
if [ -z "$OVERLAP_LINE" ]; then
    echo "No overlap found. Exiting."
    exit 1
fi

# Step 3: Get previous data up to the overlap line
head -n "$OVERLAP_LINE" "$OLD_FILE" > "$COMBINED_FILE"

# Step 4: Append new data starting from line 5 of new.dat
tail -n +5 "$NEW_FILE" >> "$COMBINED_FILE"

echo "Data combined into $COMBINED_FILE"
