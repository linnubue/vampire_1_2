import sys
import os
import glob
import pdb

import numpy as np
import pandas as pd
import xarray as xr

from vampire.constants import Constants_PS149 as Constants

def read_ir_target_temp_data(
    path_data="",
    daterange=None,
    date0=None,
    date1=None,
    file_pattern=f"IRtarget___BOX_NO___Temperature.dat",
    remove_sus_data=True,
    ):
    
    """
    Import temperature data of the reference IR targets (aluminium plates coasted with 
    Nextel Suede Coating 3101, 7329 S139 tiefschwarz, provided by Michael Haugeneder, 
    Matthias Jaggi and Ruzica Dadic).
    
    Parameters:
    -----------
    path_data : str
        Path of the ir_targets folder. That folder then contains folders of each event of the
        IR targets.
    daterange : np.ndarray or None
        If not None, a numpy.ndarray of datetime64 indicating for which dates the IR target data
        should be read.
    date0 : str or None
        If not None, start date as string "YYYY-MM-DD".
    date1 : str or None
        If not None, end date as string "YYYY-MM-DD".
    file_pattern : str
        Pattern of the temperature data .dat files.
    remove_sus_data : bool
        Whether or not to remove data of questionable quality (utter nonsense values).
    """
    
    if path_data == "":
        path_data = os.environ['VAMPIRE_DATA'] + "ir_targets/"
        
    daterange = handle_daterange_or_date_start_end(daterange, date0, date1)
    metadata = get_ir_target_data_avail(daterange)
    metadata = metadata.sel(time=metadata.box_no > -1)
    
    files = identify_ir_target_files(path_data, metadata, file_pattern)
    
    if isinstance(files, str):
        DS = read_ir_target_temp_file(files)
    else:
        DS = read_ir_target_temp_files(files)
    
    DS = add_box_number_info(DS, metadata)
    DS = remove_ir_target_inactive_times(DS)
    
    DS = quality_check(DS, remove_sus_data=remove_sus_data)
    
    DS['temp_mean'] = DS.temp.mean('port')
    DS['temp_std'] = DS.temp.std('port')
    
    DS = add_attributes(DS)
    
    return DS


def read_ir_target_service_data(
    path_data="", 
    daterange=None,
    date0=None,
    date1=None,
    file_pattern=f"IRtarget___BOX_NO___Service.dat",
    ):
    
    pdb.set_trace()


def add_attributes(DS: xr.Dataset):
    
    DS.attrs['title'] = "Temperatures of infrared targets"
    DS.attrs['author'] = "Michael Haugeneder, Matthias Jaggi, Ruzica Dadic"
    DS.attrs['comment'] = ("infrared targets are aluminium plates coasted with " +
                           "Nextel Suede Coating 3101, 7329 S139 tiefschwarz")
    
    return DS


def quality_check(DS: xr.Dataset, remove_sus_data=True):
    
    DS['flag'] = xr.DataArray(np.zeros(DS.temp.shape, dtype=np.int32), 
                              dims=['time', 'port'])
    DS['flag'] = DS.flag.where((~np.isnan(DS.temp)) & ((DS.temp > 203.15) & (DS.temp < 343.15)), other=1)
    
    if remove_sus_data:
        DS = DS.sel(time=(DS.flag==0).any('port'))
        DS['temp'] = DS.temp.where(DS.flag==0, other=np.nan)
    
    return DS


def add_box_number_info(DS: xr.Dataset, metadata: xr.Dataset):
    
    event_start, event_end = event_start_end_times()
    DS['box_no'] = xr.DataArray(np.ones((len(DS.time),), dtype=np.int32)*(-1), dims=['time'])
    for box, event in zip(metadata.box_no, metadata.event):
        event, box = event.item(), box.item()
        DS['box_no'].loc[{'time': slice(event_start[event], event_end[event])}] = box
        
    return DS


def remove_ir_target_inactive_times(DS: xr.Dataset):
    return DS.sel(time=DS.box_no > -1)


def read_ir_target_temp_files(files: list):
    
    DS_list = list()
    for file in files:
        DS = read_ir_target_temp_file(file)
        DS_list.append(DS)
        DS = DS.close()
    
    DS = xr.concat(DS_list, dim='time').sortby('time')
    
    return DS

 
def read_ir_target_temp_file(file: str):
    
    df = pd.read_csv(file, sep=',', header=0, skiprows=[0,2,3], index_col=0)
    DS = df.to_xarray()
    
    DS = DS.rename_dims({'TIMESTAMP': 'time'})
    DS = DS.assign_coords({'time': (['time'], DS.TIMESTAMP.values.astype('datetime64[s]'))}).drop_vars('TIMESTAMP')
    DS = DS.assign_coords({'port': (['port'], np.array([1,2,3]),
                                    {'long_name': "port number of logger",
                                     'comment': "IR target positions: 1: closest to ship, 3: furthest from ship"})})

    DS['temp'] = xr.DataArray((np.vstack((DS.Temperature_Port1.values,
                                          DS.Temperature_Port2.values,
                                          DS.Temperature_Port3.values)).T).astype(np.float64),
                              dims=['time', 'port'])
    DS = DS.drop_vars(['Temperature_Port1', 'Temperature_Port2', 'Temperature_Port3', 'RECORD'])
    
    DS['temp'] = DS.temp.where(DS['temp'] != -999., other=np.nan)
    DS['temp'] += 273.15
    DS['temp'].attrs['units'] = "K"
    
    return DS


def identify_ir_target_files(path_data: str, metadata: xr.Dataset, file_pattern: str):
    
    files = list()
    for event in np.unique(metadata.event):
        
        folder = os.path.join(path_data, event)
        box_nos = np.unique(metadata.box_no[metadata.event == event])
        files_event = [os.path.join(folder, file_pattern.replace("__BOX_NO__", str(box_no))) for box_no in box_nos]
        files.extend(files_event)
    
    return files


def handle_daterange_or_date_start_end(daterange=None, date0=None, date1=None):
    
    if daterange is None:
        daterange = np.arange(Constants.DATE_START, Constants.DATE_END, np.timedelta64(1, "D"))
    elif (daterange is None) and ((date0 is not None) and (date1 is not None)):
        daterange = np.arange(np.datetime64(date0), np.datetime64(date1) + np.timedelta64(1, "D"),
                              np.timedelta64(1, "D"))
        
    return daterange


def get_ir_target_data_avail(daterange=None):
    
    """
    Station 1b: 2025-07-26 14:25 BOX 1 (1,2,3) - 2025-07-28 10:50 : PS149_21-1_irtarget1
    Station 2b: 2025-07-30 14:54 BOX 3 (1,2,3) - 2025-08-01 14:10 : PS149_25-1_irtarget3
    Station 1c: 2025-08-10 14:11 BOX 5 (1,2,3) - 2025-08-10 18:54 : PS149_32-1_irtarget5
    Station 2c: 2025-08-12 13:09 BOX 4 (1,2,3) - 2025-08-14 14:21 : PS149_36-1_irtarget4
    (Station 3c: 2025-08-17 16:59 BOX 3 (1,2,3) - 2025-08-18 ??:?? : PS149_36-1_irtarget3)
    
    The last station / event is excluded here because the data could not be identified 
    unambiguously. The file exists 
    https://marine-data.de/data/6a4a3c8e-6c87-4d05-9cd8-1d414b2bca03/ir_targets_slf/ but
    has different times. So, this file probably belongs to a different measurement site.
    """
    
    if daterange is None: daterange = handle_daterange_or_date_start_end()
    n_dates = len(daterange)
    
    metadata_ds = xr.Dataset(coords={'time': (['time'], daterange)})
    
    metadata_ds['box_no'] = xr.DataArray(np.zeros((n_dates,), dtype=np.int32) - 1, dims=['time'])
    metadata_ds['box_no'].loc[{'time': slice("2025-07-26", "2025-07-28")}] = 1
    metadata_ds['box_no'].loc[{'time': slice("2025-07-30", "2025-08-01")}] = 3
    metadata_ds['box_no'].loc[{'time': slice("2025-08-10", "2025-08-10")}] = 5
    metadata_ds['box_no'].loc[{'time': slice("2025-08-12", "2025-08-14")}] = 4
    # metadata_ds['box_no'].loc[{'time': slice("2025-08-17", "2025-08-18")}] = 3
    
    metadata_ds['event'] = xr.DataArray(np.full((n_dates,), "", dtype="<U10"), dims=['time'])
    metadata_ds['event'].loc[{'time': slice("2025-07-26", "2025-07-28")}] = "PS149_21-1"
    metadata_ds['event'].loc[{'time': slice("2025-07-30", "2025-08-01")}] = "PS149_25-1"
    metadata_ds['event'].loc[{'time': slice("2025-08-10", "2025-08-10")}] = "PS149_32-1"
    metadata_ds['event'].loc[{'time': slice("2025-08-12", "2025-08-14")}] = "PS149_36-1"
    # metadata_ds['event'].loc[{'time': slice("2025-08-17", "2025-08-18")}] = "PS149_36-1"
    
    return metadata_ds


def event_start_end_times():
    
    event_start = {"PS149_21-1": np.datetime64("2025-07-26T14:25:00"),
                   "PS149_25-1": np.datetime64("2025-07-30T14:54:00"),
                   "PS149_32-1": np.datetime64("2025-08-10T14:11:00"),
                   "PS149_36-1": np.datetime64("2025-08-12T13:09:00"),
                #    "PS149_36-1": np.datetime64("2025-08-17T16:59:00"), # data not found for this time frame
                   }
    event_end = {"PS149_21-1": np.datetime64("2025-07-28T10:50:00"),
                 "PS149_25-1": np.datetime64("2025-08-01T14:10:00"),
                 "PS149_32-1": np.datetime64("2025-08-10T18:54:00"),
                 "PS149_36-1": np.datetime64("2025-08-14T14:21:00"),
                #  "PS149_36-1": np.datetime64("2025-08-18T23:59:59"),  # data not found for this time frame
                 }
    
    return event_start, event_end