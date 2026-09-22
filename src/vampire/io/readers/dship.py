"""
Reader functions for DSHIP sensors. The main sensors are Hydrins for angles,
GPS for position, and weather sensors (temperature etc.). 

DSHIP provides only one file for a given time range. To update the file with
recent data use ``tools/dship_merge.sh``
"""

import os
import re

import pandas as pd

import vampire


def read_hydrins():
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

    file = os.path.join(
        os.environ["VAMPIRE_DATA"], "dship/hydrins/hydrins.dat"
    )

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


def read_gps():
    """
    Reads Trimble-1 GPS data with 1 Hz resolution from DSHIP.

    Input units -> output units:

    - Time: seconds since 1970 -> np.datetime64[s]
    - Course: Degrees
    - Latitude: Decimal degrees
    - Longitude: Decimal degrees
    - Speed: Knots -> m/s
    """

    file = os.path.join(
        os.environ["VAMPIRE_DATA"], "dship/trimble1/trimble1.dat"
    )

    df = pd.read_csv(
        file,
        sep=";",
        na_values=" ",
        encoding="latin-1",
        skiprows=3,
        header=None,
        dtype={0: int, 1: float, 2: float, 3: float, 4: float},
        names=["time", "course", "lat", "lon", "speed"],
    )
    df["time"] = df["time"].astype("timedelta64[s]") + pd.Timestamp(
        "1970-01-01 00:00"
    )
    df = df.set_index("time")
    df.index = df.index.astype("datetime64[ns]")

    # convert units
    df["speed"] *= 0.514444

    return df


def read_weather():
    """
    Reads weather data with 1 min resolution from DSHIP.

    Input units -> output units:

    - Time: seconds since 1970 -> np.datetime64[s]
    - Pressure: hPa
    - Air temperature: degC -> K
    - Ceiling: m
    - Dewpoint: degC -> K
    - Global radiation: W m-2
    - Relative humidity: %
    - Visibility: m
    - Water temperature: degC -> K
    - Relative wind direction: deg
    - True wind direction: deg
    - Relative wind speed: m/s
    - True wind speed: m/s
    """

    file = os.path.join(
        os.environ["VAMPIRE_DATA"], "dship/weather/weather.dat"
    )

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
        },
        names=[
            "time",
            "p",
            "t_air",
            "ceil",
            "t_dew",
            "global_radiation",
            "rh",
            "vis",
            "t_water",
            "wdir_rel",
            "wdir_true",
            "wspeed_rel",
            "wspeed_true",
        ],
    )
    df["time"] = df["time"].astype("timedelta64[s]") + pd.Timestamp(
        "1970-01-01 00:00"
    )
    df = df.set_index("time")
    df.index = df.index.astype("datetime64[ns]")

    # convert units
    df["t_air"] += 273.15
    df["t_dew"] += 273.15
    df["t_water"] += 273.15

    # set missing values to nan
    df.loc[df["ceil"] == -9999, "ceil"] = pd.NA

    # set 99999 m ceiling to nan and create a cloud mask from ceilometer.
    df["ceil_cloud_mask"] = (df["ceil"] < 99999).astype(int)
    df.loc[df["ceil"].isnull(), "ceil_cloud_mask"] = pd.NA
    df.loc[df["ceil"] == 99999, "ceil"] = pd.NA

    return df


def dms2dd(s):
    """
    Converts lat/lon in degress to decimals, adapted for ATWAICE D-SHIP data,
    where seconds not used (thus here seconds=0)
    """

    multiplier = -1 if s[-1] in ["N", "E"] else 1
    s = s[:-2]  ##remove N/E/W/S
    degrees, minutes, seconds = re.split("[°'\ ]+", s)
    seconds = 0  ##for atwaice!
    dd = (
        -1 * float(degrees)
        - 1 * float(minutes) / 60
        - 1 * float(seconds) / (60 * 60)
    )

    return dd * multiplier


def read_dship(file):
    """
    Reads dship data from csv file, probably needs to be adapted for use in
    VAMPIRE
    """

    dship_data = pd.read_csv(
        file,
        skiprows=3,
        parse_dates=["date"],
        names=[
            "date",
            "course",
            "heading",
            "lat",
            "lon",
            "speed",
            "time",
            "air_pressure",
            "air_temperature",
            "ceiling",
            "dewpoint",
            "direct_radiation",
            "global_rad",
            "precipitation",
            "rel_humidity",
            "rel_wind_direction",
            "rel_wind_velocity",
            "sunshine_indicator",
            "true_wind_direction",
            "true_wind_velocity",
            "visibility",
            "water_temperature",
        ],
    )
    ddata = dship_data[dship_data.lat != "9"]  ##filter out noise
    ddata = ddata[ddata.air_temperature != 9]

    ddata["latdd"] = [
        dms2dd(ddata.lat.values[i]) for i in range(len(ddata))
    ]  ##lat and lon in decimals
    ddata["londd"] = [dms2dd(ddata.lon.values[i]) for i in range(len(ddata))]

    return ddata
