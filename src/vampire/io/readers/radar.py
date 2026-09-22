"""
Read MiRAC-A or GRaWAC radar data.
"""

import os
from glob import glob

import numpy as np
import xarray as xr


def get_all_files(instrument):
    """
    Returns list of all filenames of either GRaWAC or MiRAC.
    """

    files = sorted(
        glob(
            os.path.join(
                os.environ["VAMPIRE_DATA"],
                f"{instrument}/Y2024/M*/D*",
                f"24*_*_ZEN.LV1.NC",
            )
        )
    )

    return files


def read_times(files):
    """
    Reads only
    """

    ds = xr.open_mfdataset(
        files,
        preprocess=lambda ds: ds["C1ZE"].isel(C1Range=0),
        concat_dim="Time",
        combine="nested",
    )
    ds = ds.load()

    ds = convert_to_time(ds)
    ds = clean_data(ds)

    return ds


def read_all_times(instrument):
    """
    Reads all times when the radar measures.
    """

    files = get_all_files(instrument=instrument)
    ds = read_times(files=files)

    return ds


def read_radar(
    instrument, chirp_program=None, date=None, hourly=False, tb_only=False, ze_only=False,
):
    """
    Read MiRAC-A or GRaWAC data to dask array. Options are to load all data,
    daily data, or hourly data.

    Parameters
    ----------
    instrument : str
        "grawac" or "mirac-a"
    chirp_program : str
        e.g. "P06"
    date : pd.Timestamp
        Date to read data from. If None, all data is read.
    hourly : bool
        If False, data for the entire day is read. If True, data for the given
        hour is read.
    """

    instrument = instrument.lower()
    instrument = instrument.replace("_", "-")

    if date:
        day = date.strftime("%d")
        month = date.strftime("%m")
    else:
        day = "*"
        month = "*"

    if hourly:
        hour = date.strftime("%H")
    else:
        hour = "*"

    if chirp_program is None:
        chirp_program = "*"

    files = sorted(
        glob(
            os.path.join(
                os.environ["VAMPIRE_DATA"],
                f"{instrument}/Y2024/M{month}/D{day}",
                f"24{month}{day}_{hour}*_{chirp_program}_ZEN.LV1.NC",
            )
        )
    )

    # the following files have a bad time format
    drop_files = ["240831_090000_P09_ZEN.LV1.NC"]
    files = [f for f in files if os.path.basename(f) not in drop_files]

    if len(files) == 0:
        return
    else:
        print(f"Reading {len(files)} files with dask.")
        if tb_only:
            ds = xr.open_mfdataset(
                files, preprocess=preprocess_tb, combine="by_coords"
            )
        elif ze_only:
            ds = xr.open_mfdataset(
                files, preprocess=preprocess_ze, combine="by_coords"
            )
        else:
            ds = xr.open_mfdataset(
                files, preprocess=preprocess_radar, combine="by_coords"
            )
        print(f"Done.")
        return ds


def combine_chirps(ds):
    """
    Combine chirps to a single range dimension.
    """

    # combine chirps by concatenating variables with range as dimension
    ds_lst = []
    for i in range(len(ds.Chirp)):
        chirp_variables = [
            v
            for v in ds.data_vars
            if f"C{i+1}" in v and f"C{i+1}Range" in ds[v].dims
        ]
        ds_lst.append(
            ds[chirp_variables]
            .rename({v: v.replace(f"C{i+1}", "") for v in chirp_variables})
            .rename({f"C{i+1}Range": "range"})
            .copy()
        )
        ds = ds.drop_vars(chirp_variables)
        ds = ds.drop_dims(f"C{i+1}Range")

    ds = xr.merge([ds] + ds_lst)

    # drop every variable related to chirp settings, because number of chirp
    # might change during the flight
    ds = ds.drop_vars([v for v in ds.data_vars if "Chirp" in ds[v].dims])

    return ds


def preprocess_tb(ds):
    """
    Preprocessor when reading only TB data.
    """

    ds = convert_to_time(ds)
    ds = clean_data(ds)
    ds = extract_tb(ds)

    if len(ds.time) == 0:
        print("Empty file:", ds.encoding["source"])
        return None

    return ds


def preprocess_ze(ds):
    """
    Preprocessor for radar data.
    """

    ds = preprocess_radar(ds)
    ds = ds.ZE
    ds = ds.rename("ze")

    return ds


def preprocess_radar(ds):
    """
    Preprocessor for radar data.
    """

    ds = convert_to_time(ds)
    ds = clean_data(ds)
    ds = combine_chirps(ds)

    ds["MeanVel"] = ds["MeanVel"].where(ds["MeanVel"] != -999)
    ds["ZE"] = ds["ZE"].where(ds["ZE"] != -999)

    # TODO: add option to resample to a regular range grid

    if len(ds.time) == 0:
        print("Empty file:", ds.encoding["source"])
        return None

    return ds


def extract_tb(ds):
    """
    Extracts the brightness temperature from MiRAC-A data.
    """

    da_tb = ds.DDTb
    da_tb = da_tb.rename("tb")

    return da_tb


def convert_to_time(ds):
    """
    Convert unix time to datetime and drop duplicate times.
    """

    ds = ds.rename({"Time": "time"})

    # remove duplicate times
    _, ix = np.unique(ds["time"], return_index=True)
    ds = ds.isel(time=ix)

    # change time in seconds to actual datetime
    ds["time"] = np.datetime64("2001-01-01").astype("datetime64[ns]") + ds[
        "time"
    ].values.astype("timedelta64[s]").astype("timedelta64[ns]")
    ds["time"].encoding = {"units": "seconds since 2001-01-01 00:00:00"}

    return ds


def clean_data(ds):
    """
    Removes some bad data
    """

    ds = ds.sel(time=(ds.time < np.datetime64("2100-01-01")))

    # times when instruments were covered in plastic.
    ds = ds.sel(
        time=~(
            (ds.time >= np.datetime64("2024-08-27 10:05"))
            & (ds.time <= np.datetime64("2024-08-27 18:45"))
        )
    )

    return ds
