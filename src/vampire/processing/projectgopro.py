#!/usr/bin/env python
"""\
This script projects GoPro imagery a given time range

Usage: projectgopro.py start end

Note that you must have installed exiftool for this to work (https://exiftool.org/)
Also, please adapt the first lines of code to your pathes and adapt the read hydrins function if necessary

start and end are of the form "yyyymmddHHMM"
"""

import xarray as xr
import pandas as pd
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
import glob as glob
import os
import numpy as np
import cameratransform as ct
import cv2
from PIL import Image
import subprocess
import sys 


###### USER INPUT ######### ADAPT
overwrite = True ##whether to process a file where a projected image already exists
#path to the hydrins file containing roll/pitch
hydrinsfile = "hydrins.dat"
mounting_angle = 37 # this is how the camera is mounted relative to the ship, adapt for certain time ranges
## intrinsic camera parameters
scale_factor = 0.2 ##this is from the downsizing of the images
f = 19 * scale_factor#in mm 

sensor_size = ( 6.47 , 5.05 ) #Physical dimensions of the active sensor area (width and height), typically in millimeters. Here of GoPro Hero11  https://cameradecision.com/faq/what-is-the-Sensor-Size-of-GoPro-Hero11-Black
image_size = (1114, 974) ## width, height
## latitude/longitude information
file = "PS144track.txt" ##this is file containing the ship track file to get lat/lon info
mastertrack = pd.read_csv(file,  sep='\s+', parse_dates=["datetime"])
input_data_dir = "GOPRO/"
output_data_dir = "GOPRO/Projected/"
#####end of user input
###functions
def read_hydrins(file):
    """
    Reads Hydrins data with 1 Hz resolution from DSHIP.

    Input units -> output units:

    - Time: seconds since 1970 -> np.datetime64[s]
    - Course: deg
    - Heading: deg
    - Heading_rate: deg/s
    - Heave: m
    - Lat: deg
    - Lon: deg
    - Pitch: deg
    - Pitch_rate: deg/s
    - Roll: deg
    - Roll_rate: deg/s
    - Speed: kn -> m/s
    - Speed_x: m/s
    - Speed_y: m/s
    - Speed_z: m/s
    """

    df = pd.read_csv(
        file,
        sep=";",
        na_values=" ",
        encoding="latin-1",
        skiprows=3,
        header=None,
        dtype={
            0: int,
            1: float,
            2: float,
            3: float,
            4: float,
            5: float,
            6: float,
            7: float,
            8: float,
            9: float,
            10: float,
            11: float,
            12: float,
            13: float,
        },
        names=[
            "time",
            "course",
            "heading",
            "heading_rate",
            "heave",
            "lat",
            "lon",
            "pitch",
            "pitch_rate",
            "roll",
            "roll_rate",
            "speed",
            "speed_x",
            "speed_y",
            "speed_z",
        ],
    )
    df["time"] = df["time"].astype("timedelta64[s]") + pd.Timestamp(
        "1970-01-01 00:00"
    )
    df = df.set_index("time")
    df.index = df.index.astype("datetime64[ns]")

    # convert units
    df["speed"] *= 0.514444

    return df

def main():
    hydrinsdf = read_hydrins(hydrinsfile) ##this reads in the hydrins data needed for getting the angles,
    #the corresponding file you can just download it in 1 Hz resolution from DSHIP
    start = datetime.strptime(sys.argv[1], "%Y%m%d%H%M")
    end = datetime.strptime(sys.argv[2], "%Y%m%d%H%M")

    for date in pd.date_range(start,end, freq="h"): ##freq="h" four hourly because of the filestructure
        print(date)
    ##loop through files
        input_path = f"{input_data_dir}{date:%Y%m%d%H}/" ##path to the GoPro files (VAMPIRE1 had folders per hour)
        out = f"{output_data_dir}{date:%Y%m%d%H}"
        os.makedirs(out, exist_ok=True)
        for file in glob.glob(f"{input_path}/*.JPG"): 
            filename = os.path.basename(file)
          #  print(filename)
            time_go_pro =  pd.to_datetime(filename.split("_")[4][:14], format="%Y%m%d%H%M%S") ##read the time from the filename
          #  ###find closest lat lon
            track = mastertrack[mastertrack.datetime.dt.date == date.date()]
            ###lat lon from closest time in polarstern track:
            idx_colloc_ddata = abs(time_go_pro - track.datetime).idxmin()
            lon =  track.lon.loc[idx_colloc_ddata]
            lat =  track.lat.loc[idx_colloc_ddata]
            
            #find closest angle measurement in time:
            min_time_diff = np.nanmin(abs(hydrinsdf.index - np.datetime64(time_go_pro)))
            idx_colloc = pd.Series(abs(hydrinsdf.index - np.datetime64(time_go_pro))).idxmin()
            
            if min_time_diff.astype('timedelta64[s]') < 1: #if there is data within 1 s
        
                tilt = hydrinsdf["roll"].iloc[idx_colloc]
                roll = hydrinsdf["pitch"].iloc[idx_colloc]
            else: #using average tilt
                print("using mean tilt")
                tilt = 0
                roll = 0
            cam = ct.Camera(ct.RectilinearProjection(focallength_mm = f, sensor = sensor_size, image= image_size),
                            ct.SpatialOrientation(elevation_m = 20, tilt_deg = 53 + tilt, roll_deg=roll)) 
            ##mounting angle was 37° -> tilt_deg = 90-37 #assuming 20 m elevation
            im=Image.open(file)
            if im.mode == "RGB": ##add transparancy channel
                a_channel = Image.new('L', im.size, 255)   # 'L' 8-bit pixels, black and white 
            im.putalpha(a_channel)
            im = np.asarray(im)

            output_path = f"{out}/{filename[:-4]}_proj.tiff"
            if overwrite == False:
                if os.path.isfile(output_path):
                    print("file exists already")
                else:
                    j = im.copy()
                    ##make railing transparent
                    j[700:,:,3] = 0
                    j[520:620,750:,3] = 0
                    j[420:520,830:,3] = 0
                    j[520:700,840:,3] = 0
                    j[620:700,750:800,3] = 0
                    j[660:700,800:840,3] = 0
                    top_im = cam.getTopViewOfImage(j,[-25,15,12,50],do_plot=False) ##actual projection
                    j = Image.fromarray(top_im)
                 #   plt.show()
                    j.convert("RGBA").save(output_path, compression="lzma") ##saves projected image and compresses

                    ##write metadata:
                    lat_ref = 'N' if lat >= 0 else 'S' 
                    lon_ref = 'E' if lon >= 0 else 'W'
                    subprocess.run([ 'exiftool',  f"-AllDates={time_go_pro:%Y:%m:%d %H:%M:%S}", f'-GPSLatitude={abs(lat)}', f'-GPSLatitudeRef={lat_ref}', 
                                    f'-GPSLongitude={abs(lon)}', f'-GPSLongitudeRef={lon_ref}', '-overwrite_original', output_path ], check=True)
            else:
                j = im.copy()
                ##make railing transparent
                j[700:,:,3] = 0
                j[520:620,750:,3] = 0
                j[420:520,830:,3] = 0
                j[520:700,840:,3] = 0
                j[620:700,750:800,3] = 0
                j[660:700,800:840,3] = 0
                top_im = cam.getTopViewOfImage(j,[-25,15,12,50],do_plot=False) ##actual projection
                j = Image.fromarray(top_im)
             #   plt.show()
                j.convert("RGBA").save(output_path, compression="lzma") ##saves projected image and compresses
                ##write metadata:
                lat_ref = 'N' if lat >= 0 else 'S' 
                lon_ref = 'E' if lon >= 0 else 'W'
                subprocess.run([ 'exiftool',  f"-AllDates={time_go_pro:%Y:%m:%d %H:%M:%S}", f'-GPSLatitude={abs(lat)}', f'-GPSLatitudeRef={lat_ref}', 
                                f'-GPSLongitude={abs(lon)}', f'-GPSLongitudeRef={lon_ref}', '-overwrite_original', output_path ], check=True)

if __name__ == "__main__":
    main()
