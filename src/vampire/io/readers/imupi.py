"""
Reader for Raspberry Pi IMU sensor.
"""

import os
import pandas as pd
import vampire


def read_imupi_multiple(d0, d1):
    """
    Read hourly IMU RaspberryPi sensor data for a given range of days
    """

    times = pd.date_range(d0, d1, freq="1h")
    df_lst = []
    for time in times:
        try:
            df_lst.append(read_imupi(time=time))
        except FileNotFoundError:
            print(f"No IMU RaspberryPi data found for {time}")
    df = pd.concat(df_lst)

    return df


def read_imupi(time):
    """
    Read hourly IMU RaspberryPi sensor data
    """

    time = pd.Timestamp(time)
    
    file = os.path.join(
        os.environ["VAMPIRE_DATA"],
        "imupi",
        f"mpu_{time.strftime('%Y%m%d')}_{time.strftime('%H%M%S')}.csv",
    )

    df = pd.read_csv(
        file,
        header=[1],
        sep=",",
        skiprows=[2],
    )

    df["time"] = pd.to_datetime(df["time"], format=f"%Y-%m-%dT%H:%M:%S.%f")

    df.set_index("time", inplace=True)

    return df


def read_mpu_file(file):
    """
    Read MPU text file.
    """

    df = pd.read_csv(
        os.path.join(os.environ["VAMPIRE_DATA"], "imupi", file),
        header=[1],
        sep=",",
        skiprows=[2],
    )

    return df
