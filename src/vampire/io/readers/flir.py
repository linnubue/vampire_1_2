"""
Reads FLIR IR camera images.

THis script requires the following package: 

- libimage-exiftool-perl (install with apt)

FLIR formats:

- radiometric jpg: contains a plot of the IR values and the raw radiometric 
  signal that needs to be converted to temperature values. The formula is 
  not available here. But this format contains the time in the EXIF data
- png 16 bit: contains the temperature values based on the settings in the
  software during export. No time information is stored in this format.
  This format is also the most compact as it stores only the int values.
- csv: contains time for every image in header and the temperature values,
  but files are rather large. These files could be merged to netcdf to 
  save space and enable faster reading.

- netcdf: prepared data hourly data in float 16 to reduce file size.
"""

import xarray as xr
import os
import numpy as np

import vampire
import pandas as pd


def read_flir_statistics_multiple(d0, d1, xr_kwargs={}, to_second=True, verbose=False):
    """
    Reads Parsivel for a range of dates
    """

    dates = pd.date_range(d0, d1, freq="1D")
    ds_lst = []
    for date in dates:
        try:
            ds_lst.append(read_flir_statistics(date, xr_kwargs=xr_kwargs))
        except FileNotFoundError:
            if verbose:
                print(f"No FLIR statistics data found for {date}")
    ds = xr.concat(ds_lst, dim="time")

    if to_second:
        ds = round_to_second(ds)

    return ds


def read_flir_statistics(date, xr_kwargs={}, campaign_name="PS144"):
    """
    Read computed statistics of FLIR images.
    """
    
    campaign_name_long = "VAMPIRE"
    if campaign_name == "PS149":
        campaign_name_long = "VAMPIRE2"

    date = pd.Timestamp(date)
    file = os.path.join(
        os.environ["VAMPIRE_DATA"],
        "flir/time_series",
        f"{campaign_name_long}_flir_statistics_{date.strftime('%Y%m%d')}.nc",
    )
    ds = xr.open_dataset(file, **xr_kwargs)

    return ds


def round_to_second(ds):
    """
    Round data to nearest second and drop duplicate seconds
    """

    ds["time"] = ds["time"].dt.round("1s")
    _, ix = np.unique(ds["time"].values, return_index=True)
    ds = ds.isel(time=ix)

    return ds
