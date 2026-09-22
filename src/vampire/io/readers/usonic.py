"""
Reads ultrasonic data.
"""

import os

import pandas as pd
import vampire
import numpy as np


def read_usonic_multiple(d0, d1, product="INSTANT", verbose=False):
    """
    Reads usonic data for one day. The data is read in hourly files and
    concatenated to a single DataFrame.
    """

    if product == "AVERAGED":
        freq = "D"
    elif product == "INSTANT":
        freq = "h"

    times = pd.date_range(d0, d1, freq=freq)
    df_lst = []
    for time in times:
        try:
            df_lst.append(read_usonic(time=time, product=product))
        except FileNotFoundError:
            if verbose:
                print(f"File not found for {time}.")
            continue

    df = pd.concat(df_lst)

    return df


def read_usonic(time, product="INSTANT"):
    """
    Reads instant 30 Hz ultrasonic anemometer data for a specific time. The
    data is read in hourly files and the hour of the given time is read here.

    Note: automatic inference of headers does not work. Therefore, headers are
    assigned manually.

    Parameters
    ----------
    time : np.timedelta64
        Time object providing the date and hour to read.
    product : str
        Product name (INSTANT or AVERAGE).
    """

    time = pd.Timestamp(time)
    product = product.upper()

    if product == "AVERAGED":
        file = os.path.join(
            os.environ["VAMPIRE_DATA"],
            "usonic",
            product,
            time.strftime("%Y/%m/%d"),
            f"{time.strftime('%y%m%d')}AV.SNC",
        )
    elif product == "INSTANT":
        file = os.path.join(
            os.environ["VAMPIRE_DATA"],
            "usonic",
            product,
            time.strftime("%Y/%m/%d"),
            f"{time.strftime('%y%m%d%H')}.SNC",
        )
    else:
        raise ValueError("Product must be INSTANT or AVERAGE.")

    names = [
        "state",
        "YYYY-MM-DD HH:mm:ss",
        "msec.",
        "timezone",
        "r12",
        "r14",
        "r16",
        "r32",
        "r34",
        "r36",
        "r52",
        "r54",
        "r56",
        "t12",
        "t14",
        "t16",
        "t32",
        "t34",
        "t36",
        "t52",
        "t54",
        "t56",
        "P1",
        "P2",
        "P3",
        "x",
        "y",
        "z",
        "T",
        "vel",
        "dir",
        "vels",
        "dirs",
        "roll",
        "pitch",
        "rotate",
    ]

    df = pd.read_csv(
        file,
        skiprows=32,
        delimiter=";",
        names=names,
        usecols=np.arange(len(names)),
        encoding="latin-1",  # status might contain bytes that cannot be decoded with utf-8 or ascii
    )

    df["time"] = pd.to_datetime(
        df.iloc[:, 1], format="%Y-%m-%d %H:%M:%S"
    ) + df.iloc[:, 2].astype("float").astype("timedelta64[ms]")
    df.set_index("time", inplace=True)

    return df
