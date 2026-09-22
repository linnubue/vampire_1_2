"""
Reads OTT Parsivel Disdrometer data.
"""

import os

import pandas as pd
import numpy as np
import xarray as xr


# particle diameter velocity bins (TODO: are these also used for our instrument?)
# velocity in m/s
# diameter in mm
V_BINS = np.array(
    [
        0.05,
        0.15,
        0.25,
        0.35,
        0.45,
        0.55,
        0.65,
        0.75,
        0.85,
        0.95,
        1.1,
        1.3,
        1.5,
        1.7,
        1.9,
        2.2,
        2.6,
        3,
        3.4,
        3.8,
        4.4,
        5.2,
        6,
        6.8,
        7.6,
        8.8,
        10.4,
        12,
        13.6,
        15.2,
        17.6,
        20.8,
    ]
)

D_BINS = np.array(
    [
        0.062,
        0.187,
        0.312,
        0.437,
        0.562,
        0.687,
        0.812,
        0.937,
        1.062,
        1.187,
        1.375,
        1.625,
        1.875,
        2.125,
        2.375,
        2.75,
        3.25,
        3.75,
        4.25,
        4.75,
        5.5,
        6.5,
        7.5,
        8.5,
        9.5,
        11,
        13,
        15,
        17,
        19,
        21.5,
        24.5,
    ]
)

# precipitation codes after Tab 4680
P_CODES = {
    00: ("", ""),
    51: ("drizzle", "light"),
    52: ("drizzle", "moderate"),
    53: ("drizzle", "heavy"),
    57: ("drizzle+rain", "light"),
    58: ("drizzle+rain", "moderate/heavy"),
    61: ("rain", "light"),
    62: ("rain", "moderate"),
    63: ("rain", "heavy"),
    67: ("rain/drizzle+snow", "light"),
    68: ("rain/drizzle+snow", "moderate/heavy"),
    71: ("snow", "light"),
    72: ("snow", "moderate"),
    73: ("snow", "heavy"),
    77: ("snow grains", "unknown"),
    87: ("soft hail", "light"),
    88: ("soft hail", "moderate/heavy"),
    89: ("hail", "unknown"),
}

PRECIP_TYPES = [
    "none",
    "drizzle",
    "drizzle+rain",
    "rain",
    "rain/drizzle+snow",
    "snow grains",
    "snow",
    "soft hail",
    "hail",
]
INTENSITIES = [
    "none",
    "unknown",
    "light",
    "moderate",
    "moderate/heavy",
    "heavy",
]
INTENSITIES_INT = np.arange(0, len(INTENSITIES) + 1)


def read_parsivel_multiple(d0, d1):
    """
    Reads Parsivel for a range of dates
    """

    dates = pd.date_range(d0, d1, freq="1D")
    ds_lst = []
    for date in dates:
        try:
            ds_lst.append(read_parsivel(date, to_xarray=True))
        except FileNotFoundError:
            print(f"No Parsivel data found for {date}")
    ds = xr.concat(ds_lst, dim="time")

    return ds


def read_parsivel(date, to_xarray=True):
    """
    Read Parsivel data for a given day. Note that the data has one additional
    delimiter in the end, which is not in the header. Therefore, pandas uses
    the first column as index. This shifts the headers by one to the right.
    It is reversed by removing the last column.
    """

    date = pd.Timestamp(date)

    file = os.path.join(
        os.environ["VAMPIRE_DATA"],
        "parsivel/csv/",
        date.strftime("%Y/%m/%d"),
        f"{date.strftime('%Y%m%d')}_vampire.csv",
    )

    with open(file, "rb") as f:
        line = f.readline()

    df = pd.read_csv(file, delimiter=";", encoding="iso-8859-1")

    # rename the column with temperature, because of decoding issues
    for col in df.columns:
        if "Temperature sensor" in col:
            df = df.rename(columns={col: "Temperature sensor [C]"})

    # this fixes the additional nan column in the data fields
    cols = list(df.columns)
    df = df.iloc[:, :-1]
    df.reset_index(inplace=True)
    df.columns = cols

    df["time"] = pd.to_datetime(df.iloc[:, 0], format="%Y-%m-%d %H:%M:%S")
    df.set_index("time", inplace=True)

    if to_xarray:
        return parsivel_to_xarray(df)

    else:
        return df


def parsivel_to_xarray(df):
    """
    Convert Parsivel dataframe to xarray. Variable names can be improved.
    """

    ds = xr.Dataset()
    ds.coords["time"] = df.index
    ds.coords["velocity"] = V_BINS
    ds.coords["diameter"] = D_BINS

    ds["dist_d"] = (
        ("time", "diameter"),
        df.iloc[:, 18:50].values.reshape(len(df.index), 32),
    )
    ds["dist_v"] = (
        ("time", "velocity"),
        df.iloc[:, 50:82].values.reshape(len(df.index), 32),
    )

    ds["dist_vd"] = (
        ("time", "velocity", "diameter"),
        df.iloc[:, 82:1106].values.reshape(len(df.index), 32, 32),
    )

    ds = xr.merge([ds, df.iloc[:, :18].to_xarray()])

    # set negative values to zero
    ds["dist_d"] = ds["dist_d"].where(ds["dist_d"] > 0, 0)
    ds["dist_v"] = ds["dist_v"].where(ds["dist_v"] > 0, 0)
    ds["dist_vd"] = ds["dist_vd"].where(ds["dist_vd"] > 0, 0)

    # read wawa code
    ds["precip_type"] = ("time", [P_CODES[x][0] for x in ds["wawa"].values])
    ds["intensity"] = ("time", [P_CODES[x][1] for x in ds["wawa"].values])

    # create array of intensities for each precip type
    ds.coords["precip"] = PRECIP_TYPES
    ds["intensity_int"] = xr.zeros_like(ds.intensity, dtype="int")
    for i in range(len(INTENSITIES)):
        ds["intensity_int"] = xr.where(
            ds["intensity"] == INTENSITIES[i],
            INTENSITIES_INT[i],
            ds["intensity_int"],
        )
    ds["precip_type_flag"] = (ds["precip_type"] == ds["precip"]) * ds[
        "intensity_int"
    ]

    return ds
