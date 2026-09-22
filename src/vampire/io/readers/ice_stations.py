import pdb
import glob
import re
import datetime as dt

import pandas as pd
import numpy as np
import xarray as xr

from analysis.data_tools import identify_files_daterange

file_pattern = f"Ice_Station_[0-9][a-d]_Day[0-9]___DATE_STRING__.ods"

def get_ice_core_data_daterange(path: str, daterange: np.ndarray):
    
    """
    Loads ice core data found within a path for a given date range.
    
    Parameters:
    -----------
    path : str
        Full path where .ods files containing the ice core data are located.
    daterange : np.ndarray
        Array of np.datetime64 indicating the date range.
    """
    
    files = identify_files_daterange(path, daterange, file_pattern=file_pattern)
    ds_list = list()
    for file in files:
        ds_list.append(load_ice_core_data(file))
    ds = xr.merge(ds_list, join='outer')
    
    return ds


def get_ice_core_data_single_date(path: str, date: str):
    
    """
    Loads ice core data found within a path for a given date.
    
    Parameters:
    -----------
    path : str
        Full path where .ods files containing the ice core data are located.
    date : str
        Date in "yyyymmdd".
    """
    
    file = identify_file_date(path, date)
    ds = load_ice_core_data(file)
    
    return ds


def identify_file_date(path: str, date: str, file_pattern=file_pattern):
    
    """    
    Parameters:
    -----------
    path : str
        Full path where files containing the data are located.
    date : str
        Date in "yyyymmdd".
    """
    
    potential_files = sorted(glob.glob(path + file_pattern))
    file_for_import = list()
    for file in potential_files:
        match_str = re.search(r'\d{4}\d{2}\d{2}', file)
        if match_str.group() == date:
            file_for_import.append(file)

    if len(file_for_import) != 1:
        print("Could not find or found too many " + file_pattern + " files....")
        return None
    else:
        file_for_import = file_for_import[0]
    
    return file_for_import
    

def load_ice_core_data(file: str):
    
    """
    Loads ice core data found within a path for a given file.
    
    Parameters:
    -----------
    file : str
        Full path and filename of the .ods file containing the ice core data.
    """
    
    df_names = ['temp_core', "temp_core_dt", "temp", "sal_core", "sal_core_dt", "depth_info"]
    dt_kwargs = dict(index_col=0, usecols="A:B", header=None,
                     engine='odf', skiprows=3, nrows=2)
    df_dict = dict()
    for df_name in df_names: df_dict[df_name] = pd.DataFrame()
    if file:
        df_dict['temp_core'], df_dict['temp_core_dt'], df_dict['temp'] = get_temp_core_data(file, dt_kwargs)
        
        df_dict['sal_core'], df_dict['sal_core_dt'], df_dict['depth_info'] = get_sal_core_data(file, dt_kwargs)
    
    ds = ice_core_df_to_xr_dataset(df_dict)
    ds = check_and_repair_time(file, ds)
    
    return ds


def get_temp_core_data(file: str, dt_kwargs: dict):
    
    sheet = "Temperature Core"
    df_temp_core = pd.read_excel(file, sheet_name=sheet, 
                                 index_col=0, usecols="A:B", 
                                 engine='odf', 
                                 skiprows=22, nrows=37)
    df_temp_core_dt = pd.read_excel(file, sheet_name=sheet, **dt_kwargs)
    df_temp = pd.read_excel(file, sheet_name=sheet, 
                            index_col=0,
                            usecols="A:B", engine="odf", 
                            skiprows=9, nrows=5).transpose()
    
    return df_temp_core, df_temp_core_dt, df_temp


def get_sal_core_data(file: str, dt_kwargs: dict):
    sheet = "Salinity Density Core"
    df_sal_core = pd.read_excel(file, sheet_name=sheet,
                                index_col=0, usecols="B:I",
                                engine='odf', 
                                skiprows=16, nrows=33)
    df_sal_core['Volume (cm³)'] = np.pi * 4.5**2 * df_sal_core['Section Length [cm]']
    df_sal_core['Density (g cm-3)'] = df_sal_core['Weight (g)'] / df_sal_core['Volume (cm³)']
    
    df_sal_core_dt = pd.read_excel(file, sheet_name=sheet, **dt_kwargs)
    df_depth_info = pd.read_excel(file, sheet_name=sheet,
                                  index_col=0,
                                  usecols="A:B", engine="odf", 
                                  skiprows=8, nrows=6).transpose()
    
    return df_sal_core, df_sal_core_dt, df_depth_info


def ice_core_df_to_xr_dataset(df_dict: dict):
    
    """
    Converts several pandas DataFrames to one xarray Dataset.
    
    Parameters:
    df_dict : dict
        Dictionary containing pd.DataFrame objects.
    """
    
    df_vars_profiles = ['Temperature [°C]', 'Salinity', 'Bottom [cm]', 'Density (g cm-3)']
    df_vars_temp_add = ['Air temp 2m [°C]', 'Air temp 5cm [°C]', 'Surface temp [°C]', 
                        'Snow-Ice temp [°C]', 'Water temp [°C] (in core hole top)']
    df_vars_sal_add = ['Freeboard [cm]', 'Snow Thickness [cm]', 'Bottom to Ice surface [cm]']
    
    ds_vars_profiles = ["temp", "sal", "depth_sal_bot", 'density']
    ds_vars_temp_add = ["temp2m", "temp5cm", "temp_snow_air", "temp_snow_ice", "temp_water"]
    ds_vars_sal_add = ["freeboard", "snow_depth", 'bottom_to_ice']
    
    translate_dict = dict(zip(df_vars_profiles+df_vars_temp_add+df_vars_sal_add,
                              ds_vars_profiles+ds_vars_temp_add+ds_vars_sal_add))
    df_dict = rename_columns(df_dict, translate_dict)
    
    ds = init_ice_core_ds(df_dict['temp_core_dt'], df_dict['sal_core_dt'],
                          ds_vars_profiles, ds_vars_temp_add, ds_vars_sal_add)
    del df_dict['temp_core_dt'], df_dict['sal_core_dt']
    ds = insert_data(df_dict, ds, ds_vars_profiles)
    
    return ds


def init_ice_core_ds(
    df_temp_core_dt: pd.DataFrame, 
    df_sal_core_dt: pd.DataFrame, 
    ds_vars_profiles: list, 
    ds_vars_temp_add: list, 
    ds_vars_sal_add: list):
    
    depth_coords_temp = np.arange(0., 350.01, 0.5)
    depth_coords_sal = np.arange(0., 250.01, 0.5)
    n_depth = {'sal': len(depth_coords_sal), 'temp': len(depth_coords_temp)}
    ds = xr.Dataset(coords={'depth_temp': (['depth_temp'], depth_coords_temp),
                            'depth_sal': (['depth_sal'], depth_coords_sal),
                            'time_temp': (['time_temp'], 
                                          np.array([extract_datetime(df_temp_core_dt)])),
                            'time_sal': (['time_sal'], 
                                         np.array([extract_datetime(df_sal_core_dt)]))
                            })
    
    for dv in ds_vars_profiles:
        if dv in ['depth_sal_bot', 'density']:
            ds[dv] = xr.DataArray(np.full((1,n_depth['sal']), np.nan), dims=[f'time_sal', 'depth_sal'])
        else:
            ds[dv] = xr.DataArray(np.full((1,n_depth[dv]), np.nan), dims=[f'time_{dv}', f'depth_{dv}'])
    for dv in ds_vars_temp_add:
        ds[dv] = xr.DataArray(np.full((1,), np.nan), dims=['time_temp'])
    for dv in ds_vars_sal_add:
        ds[dv] = xr.DataArray(np.full((1,), np.nan), dims=['time_sal'])
        
    return ds


def extract_datetime(df: pd.DataFrame):

    time_dt = df.loc['Time'].values[0]
    date_pd = df.loc['Date'].values[0]
    if type(time_dt) != dt.time:
        time_dt = dt.time(0,0,0)
    time = date_pd + pd.Timedelta(time_dt.strftime("%H:%M:%S"))
    
    return np.datetime64(str(time)).astype('datetime64[ns]')


def check_and_repair_time(file: str, ds: xr.Dataset):
    
    """
    If no time and date is entered in one of the sheets, the resulting time is NaT. If so, try
    using the date and time info from the 'Station Overview' sheet.
    
    file : str
        Full path and filename of the ice station notes.
    ds : xr.Dataset
        Dataset containing the ice station data.
    """
    
    time_vars = np.array([coords for coords in ds.coords if 'time' in coords])
    time_is_NaT = np.array([np.isnan(ds[tv].values[0]) for tv in time_vars])
    for tv in time_vars[time_is_NaT]:
        ds = repair_time(file, ds, str(tv))
    
    return ds


def repair_time(file: str, ds: xr.Dataset, time_variable: str):
    
    df = pd.read_excel(file, sheet_name="Station Overview", 
                       index_col=0, usecols="A:B", 
                       header=None,
                       engine='odf', 
                       skiprows=16, nrows=2)
    df = df.rename(index={'Starting Time': "Time", "Starting Date": "Date"})
    time = extract_datetime(df)
    ds[time_variable] = ([time_variable], np.array([time]))
    
    return ds


def rename_columns(df_dict: dict, translate_dict: dict):
    
    for key in df_dict.keys():
        df_dict[key] = df_dict[key].rename(columns=translate_dict, errors='ignore')
        
    return df_dict


def insert_data(
    df_dict: dict, 
    ds: xr.Dataset, 
    vars_profiles: list):
    
    for key in df_dict.keys():
        if len(df_dict[key].index) == 0:
            continue
        for dv in ds.data_vars:
            if dv in df_dict[key].columns:
                if dv in vars_profiles:
                    df_coords = df_dict[key].index.values
                    where_okay = ~np.isnan(df_dict[key].index.values)
                    if np.any(np.diff(df_coords) < 0):
                        where_okay[np.where(np.diff(df_coords) < 0)[0][0]+1:] = False
                    df_coords = df_coords[where_okay]
                    
                    if ('sal' in dv) or (dv == 'density'):
                        depth_dim_name = 'depth_sal'
                    else:
                        depth_dim_name = 'depth_temp'

                    da = xr.DataArray(df_dict[key][dv].values[where_okay], 
                                      dims=depth_dim_name, 
                                      coords={depth_dim_name: ([depth_dim_name], df_coords)})
                    ds[dv][0,:].loc[{depth_dim_name: da[depth_dim_name].values}] = da.values

                else:
                    ds[dv][:] = df_dict[key][dv].values
            
    return ds