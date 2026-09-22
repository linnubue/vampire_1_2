import sys
import os
import glob
import datetime as dt
import pdb

import pandas as pd
import numpy as np
import xarray as xr

from vampire.analysis.data_tools import identify_files_daterange

file_pattern = f"__DATE_STRING___[0-2][0-9][0-5][0-9][0-5][0-9]_CR1000_SensorData.txt"


def get_radiation_dailyfiles(path: str, date_range: np.ndarray):
    
    """
    Loads the broadband radiation data from the Kipp and Zonen pyranometer and pyrgeometer that has
    been organised into daily files with process_radiation.py for a given date range.
    
    Parameters:
    -----------
    path : str
        Full path where the daily radiation data is located.
    date_range : np.ndarray
        Array of np.datetime64 objects indicating the date range.
    """
    
    files = identify_files_daterange(path, date_range, file_pattern=file_pattern)
    ds_list = list()
    for file in files:
        ds_list.append(load_radiation_data(file))
    ds = xr.concat(ds_list, dim='time')
    
    return ds


def load_radiation_data(file: str):
    
    """
    Imports the radiation data found in a given file.
    
    Parameters:
    -----------
    file : str
        Full path and file name of daily radiation file.
    """
    
    df = pd.read_csv(file, sep='\t', header=1, index_col=0)
    df, units = get_column_names_and_units(file, df)
    
    ds = radiation_df_to_xarray_dataset(df, units)
    
    return ds


def get_column_names_and_units(file: str, df: pd.DataFrame):
    
    df_names = pd.read_csv(file, sep='\t', header=0, index_col=0)
    df = df.rename(columns=dict(zip(df.columns, df_names.columns)))
    units = np.array([unit.replace("[", "").replace("]","").replace("°","deg") for unit in df_names.iloc[0].values])
    
    return df, units


def radiation_df_to_xarray_dataset(df: pd.DataFrame, units: np.ndarray):
    
    """
    Convert the pandas DataFrame into an xarray Dataset and add the units of the data.
    """
    
    times = np.array([np.datetime64(time.replace(" ","T")) for time in df.index.values])
    ds = xr.Dataset(coords={'time': (['time'], times.astype('datetime64[ns]'))
                            })
    for unit, dv in zip(units, df.columns):
        dv_name = (dv.replace(' ', '_').replace("CMP21", "SW").replace("SGR4V", "LW").replace(
            "voltage", "volt").replace("irradiance", "irrad"))
        ds[dv_name] = xr.DataArray(df[dv].values, dims=['time'], 
                                   attrs={'long_name': dv, 'units': unit})
    
    return ds