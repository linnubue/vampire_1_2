"""
Get Mobotix files.
"""

import os
from glob import glob

import pandas as pd

import vampire


def get_mobotix_files():
    """
    Get Mobotix files.
    """

    files = glob(
        os.path.join(
            os.environ["VAMPIRE_DATA"],
            "mobotix",
            "*/*/*",
            "ps_144_skycam_2024*.jpg",
        )
    )

    return files


def mobotix_dates():
    """
    Pandas DataFrame of Mobotix dates. This can be used for data
    availability plot.
    """

    df = pd.DataFrame()
    df["file"] = get_mobotix_files()
    df["time"] = pd.to_datetime(
        df["file"].str.split("_", expand=True).iloc[:, -1],
        format="%Y%m%d%H%M.jpg",
    )
    df = df.set_index("time")

    return df
