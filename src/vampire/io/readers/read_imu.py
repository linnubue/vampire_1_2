"""
Read Mini IMU data.
"""

import os
from datetime import timedelta
from glob import glob

import numpy as np
import pandas as pd
import xarray as xr
from natsort import natsorted

import vampire


def read_imu_multiple(d0, d1):
    """
    Reads IMU data for several days.
    """

    dates = pd.date_range(d0, d1, freq="1D")
    ds_lst = []
    for date in dates:
        try:
            ds_lst.append(read_imu_nc(date=date))
            print(f"Found Mini IMU data for {date}")
        except FileNotFoundError:
            print(f"No Mini IMU data for {date}.")
            continue

    df = xr.concat(ds_lst, dim="time")

    return df


def read_imu_nc(date):
    """
    Reads IMU netcdf file.
    """

    date = pd.Timestamp(date)

    ds = xr.open_dataset(
        os.path.join(
                os.environ["VAMPIRE_DATA"],
                "miniimu/netcdf",
                f"VAMPIRE_miniimu_1hz_{date.strftime('%Y%m%d')}.nc",
            )
        )
    
    return ds


def read_imu(date):
    """
    Read Mini IMU data for one day. Note that this only filters the day based
    on the directory, but the directory contents can start later and extend
    into the next day.
    """

    date = pd.Timestamp(date)

    files = natsorted(
        glob(
            os.path.join(
                os.environ["VAMPIRE_DATA"],
                "miniimu",
                date.strftime("%Y-%m-%d"),
                "*/data*.csv",
            )
        )
    )

    if len(files) == 0:
        raise FileNotFoundError

    df_lst = []
    for file in files:
        df_lst.append(read_imu_file(file))
    df = pd.concat(df_lst)

    return df


def read_imu_file(file):
    """
    Reads a single Mini IMU file. For VAMPIRE, the columns are separated by
    "," and the decimal separator is "," as well. For all but the first
    column, the delimiter is followed by a space. This allows to read the
    data more easily. The first two columns are split after the initial
    file reading. Headers are assigned in the end, because they are not
    having a space after the comma.
    """

    # read header from file
    with open(file, "r") as f:
        names = f.readline().strip()
    names = names.split(",")
    names[0] = "Time"

    df = pd.read_csv(
        file,
        on_bad_lines="skip", 
        delimiter=", ",
        encoding="iso-8859-1",
        decimal=",",
        engine="python",
        skiprows=1,
        header=None,
        parse_dates=[1],
    )

    # separate values in first column
    df.columns += 1
    df = pd.concat(
        [df.loc[:, 1].str.split(pat=",", expand=True), df.iloc[:, 1:]], axis=1
    )
    df.rename(columns={i: s for i, s in enumerate(names)}, inplace=True)

    # rename times
    df.rename(
        columns={"Chip Time()": "time_chip", "Time": "time_of_day"},
        inplace=True,
    )

    df["time_of_day"] = pd.to_timedelta(df["time_of_day"])

    # Note that there is a non-constant difference between Time and ChipTime.
    # Time(s) is the correct time, but contains no date
    # The date is infered from chip time with special care around midnight
    # fix changes to next day, which are either too early or too late depending
    # on the sign of offset between time and chip time
    df["time"] = df["time_of_day"] + df["time_chip"].dt.floor("D")
    offset = (df["time"] - df["time_chip"]).dt.total_seconds()
    df.loc[offset > 50000, "time"] -= np.timedelta64(1, "D")
    df.loc[offset < -50000, "time"] += np.timedelta64(1, "D")

    offset_corrected = (df["time"] - df["time_chip"]).dt.total_seconds()
    assert np.abs(offset_corrected).max() < 3600  # less than one hour

    df.set_index("time", inplace=True)

    return df


def read_imu_day(date):
    """
    Read Mini IMU data for one day. This takes data from two days earlier and later to include all data as they are not neccessarily in the correct folder
    """
    files = []
    for day in pd.date_range(date- timedelta(days=1), date + timedelta(days=1)):
        day = pd.Timestamp(day)

        files = np.append(files,natsorted(
            glob(
                os.path.join(
                    os.environ["VAMPIRE_DATA"],
                    "miniimu",
                    day.strftime("%Y-%m-%d"),
                    "*/data*.csv",
                )
            )
        ))

    df_lst = []
    if len(files) ==0:
        print(f"No files found for {date.date()}")
        df = []
    else:
        for file in files:
            df_lst.append(read_imu_file(file))
        if len(df_lst) == 0:
            print(f"No files found for {date.date()}")
            df = []
        else:
            df = pd.concat(df_lst)
            df = df[df.index.date == date.date()]
    return df


