#!/bin/bash
# This script calls vampire quicklooks given a range of dates and specified instruments
# usage: bash ./quicklooks.sh 2024-08-20 2024-08-27 mirac_a,usonic

START_DATE=$1
END_DATE=$2
INSTRUMENTS=$3  # New parameter for multiple instruments

# convert the input dates to seconds since epoch
start=$(date -I -d "$START_DATE")
end=$(date -I -d "$END_DATE")

current_date="$start"

# Convert the comma-separated instruments to an array
IFS=',' read -r -a instrument_array <<< "$INSTRUMENTS"

while [[ "$current_date" < "$end" || "$current_date" == "$end" ]]; do
  for instrument in "${instrument_array[@]}"; do
    # Run the appropriate Python script based on each instrument specified
    case "$instrument" in
      radiosonde)
        python -m vampire.quicklooks.radiosondes "$current_date"
        ;;
      sonde_radar)
        python -m vampire.quicklooks.sonde_radar "$current_date"
        ;;
      mwr)
        python -m vampire.quicklooks.mwr_quicklook "$current_date"
        ;;
      radar)
        python -m vampire.quicklooks.radar "$current_date"
        ;;
      radar_cfad)
        python -m vampire.quicklooks.cfad "$current_date"
        ;;
      usonic)
        python -m vampire.quicklooks.usonic "$current_date"
        ;;
      parsivel)
        python -m vampire.quicklooks.parsivel "$current_date"
        ;;
      flir)
        python -m vampire.quicklooks.flir "$current_date"
        ;;
      pamtra)
        python -m vampire.processing.run_pamtra "$current_date"
        ;;
      hydrins)
        python -m vampire.quicklooks.hydrins "$current_date"
        ;;
      weather)
        python -m vampire.quicklooks.weather "$current_date"
        ;;
      ship)
        python -m vampire.quicklooks.ship "$current_date"
        ;;
      *)
        echo "Unknown instrument: $instrument"
        echo "Please specify one or more of: radiosonde, mwr, radar, radar_cfad, usonic, parsivel, flir, pamtra, hydrins, weather, ship"
        exit 1
        ;;
    esac
  done
  current_date=$(date -I -d "$current_date + 1 day")
done
