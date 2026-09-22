"""
Reads GoPro camera images.

Currently available:

- get_all_times: Get all available times of GoPro images.
- read_gopro: Reads one GoPro camera image at a specific time.
- read_rescaled: Reads one rescaled GoPro camera image at a specific time.
"""

import os
import zipfile
from datetime import timedelta
from glob import glob

import pandas as pd
import numpy as np
from vampire.constants import Constants
from PIL import Image


def get_all_times():
    """
    Get all times from zipped and unzipped archives. Drops any duplicates.
    """

    times = get_all_times_zip().append(get_all_times_extracted())
    times = list(dict.fromkeys(times))
    times = sorted(times)

    return times


def get_all_times_zip():
    """
    Get all times from zip archives. Archives are names "yyyymmddhh.zip"
    """

    archive_dirs = glob(
        os.path.join(os.environ["VAMPIRE_DATA"], "gopro/*.zip")
    )
    files = []
    for archive_dir in archive_dirs:
        archive = zipfile.ZipFile(archive_dir, "r")
        files.extend(archive.namelist())
    times = pd.to_datetime(
        [file.split("_")[4][:14] for file in files], format="%Y%m%d%H%M%S"
    )

    return times


def get_all_times_extracted(files=None):
    """
    Get all available times of GoPro images
    """

    if files is None:
        files = glob(os.path.join(os.environ["VAMPIRE_DATA"], "gopro/*/*"))
    files = [os.path.basename(file) for file in files]
    times = pd.to_datetime(
        [file.split("_")[4][:14] for file in files], format="%Y%m%d%H%M%S"
    )

    return times


def get_gopro_rescaled_file_data_campaigns(time: np.datetime64, campaign_name=Constants.CAMPAIGN_NAME):
    
    pd_time = pd.Timestamp(time)

    path = os.path.join(os.environ['VAMPIRE_DATA'],
                        f"gopro/{pd_time.strftime('%Y%m%d')}/",
                        f"{pd_time.strftime('%Y%m%d%H')}/")
    files = sorted(glob(path + f"GOPRO_{campaign_name}_GPS_date_*.JPG_rescaled.JPG"))
    
    df = pd.DataFrame(data=files, columns=['file'])
    
    times_gopro = pd.to_datetime(df['file'], 
                                 format=f"{path}GOPRO_{campaign_name}_GPS_date_%Y%m%d%H%M%S.JPG_rescaled.JPG")

    file = files[np.argmin(np.abs(times_gopro.values - time))]
    
    return file


def get_gopro_rescaled_filepattern(time):

    filepattern = os.path.join(
        os.environ["VAMPIRE_DATA"],
        "gopro/",
        time.strftime("%Y%m%d%H"),
        f"GOPRO_{Constants.CAMPAIGN_NAME}_GPS_date_{time.strftime('%Y%m%d%H%M%S')}.JPG_rescaled.JPG",
        )
    
    return filepattern

def read_gopro(time):
    """
    Reads one GoPro camera image at a specific time.

    Note: This does also includes files with "_no_GPSdata" in the filename.
    """
    
    import cv2

    time = pd.Timestamp(time)

    img = cv2.imread(
        glob(
            os.path.join(
                os.environ["VAMPIRE_DATA"],
                "gopro/",
                time.strftime("%Y%m%d"),
                f"GOPRO_{time.strftime('%Y%m%d%H%M%S')}*.JPG",
            )
        )[0]
    )

    return img


def read_rescaled(time):
    """
    Reads one rescaled GoPro camera image at a specific time.
    """
    
    import cv2

    time = pd.Timestamp(time)

    img = cv2.imread(
        get_gopro_rescaled_filepattern(time)
    )

    return img


def read_rescaled_withPillow(time):
    """
    Reads one rescaled GoPro camera image at a specific time using Image from Pillow package as cv2 somehow switches RGB weirdly, also checks whether there is data from that second, otherwise takes the next second
    """

    time = pd.Timestamp(time)
    file = glob(
        get_gopro_rescaled_filepattern(time)
    )
    if len(file) == 0:
        time = time + timedelta(seconds=1)  ##take image from next second
        file = glob(
            get_gopro_rescaled_filepattern(time)
        )
    img = Image.open(file[0])

    return img
