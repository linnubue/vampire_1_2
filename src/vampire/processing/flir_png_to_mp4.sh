#!/bin/bash

# FLIR pngs to mp4 with 24 fps (1 day == 60 sec)

campaign="vampire2"
campaign_label="PS149"
source_dir_base="/path/to/flir/flir_png"
dest_dir="/path/to/flir/flir_mp4/"
filename_base=$campaign_label"_flir_tb_"

for dir in $source_dir_base/*
do
    if [[ -d $dir ]]; then
        filename=$(basename $dir)
        echo $dest_dir"$filename_base$filename.mp4"
        ffmpeg -f image2 -framerate 24 -pattern_type glob -i "$dir/"$campaign_label"_flir_tb_*.png" -pix_fmt yuv420p -vcodec libx264rgb -crf 0 $dest_dir"$filename_base$filename.mp4"
    fi

done

