"""
Read GPS and angles from ship stream.
"""

import os
import numpy as np

import pandas as pd


def read_ship_angles(time):
    """
    Reads stream of ship angles.
    """

    time = pd.Timestamp(time)

    if time <= pd.Timestamp("2024-08-19 17:00"):
        df = read_ship_angles_clean(time)
    else:
        df = read_ship_angles_raw(time)

    return df


def ship_csv_to_data(df: pd.DataFrame):
    df["time"] = pd.to_datetime(
        df["time"], format="%Y-%m-%dT%H:%M:%S.%f", errors="coerce"
    )
    df["roll"] = pd.to_numeric(df["roll"], errors="coerce")
    df["pitch"] = pd.to_numeric(df["pitch"], errors="coerce")
    df["heading"] = pd.to_numeric(df["heading"], errors="coerce")
    
    return df


def filter_outliers(df: pd.DataFrame):
    
    """
    Filter outliers from temporal differences until number of outliers is
    stable. Those might occur at larger time gaps
    """
    
    i = 0
    n_max = 20
    n_outliers_total = 0
    d_outliers = 1
    while (i < n_max) and (d_outliers > 0):
        d_pitch = df["pitch"].diff().abs()
        d_roll = df["roll"].diff().abs()
        d_heading_cos = np.cos(np.deg2rad(df["heading"])).diff().abs()
        d_heading_sin = np.sin(np.deg2rad(df["heading"])).diff().abs()
        ix_drop = (
            (d_pitch > 0.5)
            | (d_roll > 0.5)
            | (d_heading_cos > 0.01)
            | (d_heading_sin > 0.01)
        )
        df = df.drop(ix_drop.index[ix_drop])

        if i == 0:
            n_outliers = ix_drop.sum()
            d_outliers = 1
        else:
            n_outliers = ix_drop.sum()
            d_outliers = n_outliers - ix_drop.sum()

        n_outliers_total += n_outliers
        i += 1
        
    print(f"Filtered {n_outliers} outliers")
        
    return df, n_outliers


def mask_unrealistic_values(df: pd.DataFrame):
    
    df.loc[df["heading"] > 360, "heading"] = np.nan
    df.loc[df["heading"] < 0, "heading"] = np.nan

    df.loc[df["roll"] > 20, "roll"] = np.nan
    df.loc[df["roll"] < -20, "roll"] = np.nan
    df.loc[df["pitch"] > 20, "pitch"] = np.nan
    df.loc[df["pitch"] < -20, "pitch"] = np.nan
    
    # drop where any of the numeric conversions failed or unrealistic value occurs
    df = df.loc[~df.isnull().any(axis=1), :]
    
    return df


def read_ship_angles_raw(time):
    """
    Reads the raw stream. Many lines are incomplete or in wrong order. This
    format is written during VAMPIRE after 2024-08-??
    """

    # TODO: many outliers remain in roll angle. Could be fixed with a proper
    # outlier detection. The current approach is to filter out the most
    # obvious outliers.

    time = pd.Timestamp(time)

    file = os.path.join(
        os.environ["VAMPIRE_DATA"],
        "ship/angles",
        f"shipstream_angles_{time.strftime('%Y%m%d_%H')}.txt",
    )

    # the following loop avoids problem if first line has less commas
    is_err = True
    skip = 0
    while is_err:
        try:
            df = pd.read_csv(
                file,
                sep=",",
                header=None,
                on_bad_lines="skip",
                skiprows=skip,
                usecols=[0, 1, 2, 3, 4],
            )
            is_err = False
        except ValueError:
            skip += 1
            is_err = True
        
    df = df.drop(columns=1)
    df.loc[:, 4] = df.loc[:, 4].str.split("*", expand=True)[0]
    df = df.rename(columns={0: "time", 2: "pitch", 3: "roll", 4: "heading"})

    df = ship_csv_to_data(df)

    df = mask_unrealistic_values(df)
    df = df.set_index("time")
    df = filter_outliers(df)

    return df


def read_ship_angles_clean(time):
    """
    Read recorded ship angles
    """

    time = pd.Timestamp(time)

    file = os.path.join(
        os.environ["VAMPIRE_DATA"],
        "ship/angles",
        f"shipstream_angles_{time.strftime('%Y%m%d_%H')}.txt",
    )

    names = ["time", "pitch", "roll", "heading"]
    df = pd.read_csv(file, sep=",", header=None, names=names)
    df = ship_csv_to_data(df)

    df = mask_unrealistic_values(df)
    df = df.set_index("time")
    df = filter_outliers(df)

    return df
