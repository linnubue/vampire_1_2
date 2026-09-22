"""
Reads the prepared hydrins NetCDF files in 1 Hz or 20 Hz resolution. The data
comes from the ship angle stream.
"""

import os

import pandas as pd
import xarray as xr

import vampire


def read_hydrins_multiple(d0, d1, resolution):
    """
    Reads hydrins data for a range of dates.
    """

    dates = pd.date_range(d0, d1, freq="1D")
    ds_lst = []
    for date in dates:
        try:
            ds_lst.append(read_hydrins(date=date, resolution=resolution))
        except FileNotFoundError:
            print(f"No Hydrins data found for {date}")
    ds = xr.concat(ds_lst, dim="time")

    return ds


def read_hydrins(date, resolution):
    """
    Read Hydrins data for a specific date.

    Parameters
    ----------
    date : pd.Timestamp
       Date of file.
    resolution : int
       Resolution of data in Hz
    """

    date = pd.Timestamp(date)
    resolution = f"{resolution}hz"

    ds = xr.open_dataset(
        os.path.join(
            os.environ["VAMPIRE_DATA"],
            "ship",
            "hydrins",
            f"VAMPIRE_hydrins_{resolution}_{date.strftime('%Y%m%d')}.nc",
        )
    )

    return ds
