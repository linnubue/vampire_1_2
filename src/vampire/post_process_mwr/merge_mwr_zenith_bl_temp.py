import sys
import os
import datetime as dt
import pdb
from copy import deepcopy

import numpy as np
import xarray as xr

from vampire.io.readers.mwr_retrieval import (read_mwr_retrieval_output, 
                                              merge_temp_zen_and_bl, 
                                              weights_for_merged_temp_prof)
from vampire.post_process_mwr.post_process_mwr_atm import (load_retrieval_uncertainties,
                                                           add_retrieval_uncertainties)
from vampire.analysis.data_tools import encode_time

campaign = "VAMPIRE2"
if campaign == "vampire":
    from vampire.constants import Constants as Constants
elif campaign == 'VAMPIRE2':
    from vampire.constants import Constants_PS149 as Constants

script_name = os.path.basename(__file__)

var_translation = {'temp': 'temp',
                   'temp_bl': 'temp'}

def main():
    
    path_data = {'mwr_synergy_processed': os.environ['VAMPIRE_DATA'] + "mwr_synergy/for_publication/"}
    path_output = os.environ['VAMPIRE_DATA'] + "mwr_synergy/for_publication/temp_merged/"
    
    date_range = np.arange(np.datetime64(Constants.DATE_START),
                           np.datetime64(Constants.DATE_END) + np.timedelta64(2, "D"),
                           np.timedelta64(1, "D"))
    
    for date in date_range:
        date_str = date.astype('datetime64[D]').astype('str')
        print(date_str)
        date_range_short = np.array([date + np.timedelta64(-1, "D"),
                                     date,
                                     date + np.timedelta64(1, "D")])
    
        DS_dict = load_temp_bl_and_zenith_data(path_data['mwr_synergy_processed'], date_range_short)
        if len(DS_dict.keys()) == 0: continue

        DS_merged = merge_zenith_and_bl_temp(DS_dict)
        
        DS = DS_merged.sel(time=slice(date, date + np.timedelta64(1, "D")))
        if len(DS.time) > 0:
            export_merged_DS(DS, path_output)


def load_temp_bl_and_zenith_data(path: str, date_range: np.ndarray):
    
    file_pattern = (f"{Constants.CAMPAIGN_NAME}_uoc_hatpro_lhumpro-243-340_l2_var_v01" +
                    f"___DATE_STRING__[0-2][0-9][0-5][0-9][0-5][0-9].nc")
    
    vars = ['temp', 'temp_bl']
    DS_dict = dict()
    for var in vars:
        try:
            DS_dict[var] = read_mwr_retrieval_output(path_data=path,
                                                    vars_=[var],
                                                    with_processing=False,
                                                    file_pattern=file_pattern,
                                                    date_range=date_range,
                                                    remove_bad_flag_data=False,
                                                    merge_temp_zenith_and_bl=False,
                                                    mwr_pro_output=False)[var]
        except OSError:
            continue
    
    avail_vars = DS_dict.keys()
    for key in avail_vars:
        DS_dict[key] = DS_dict[key].load()
        DS_dict[key]['temp_rmse'] = DS_dict[key]['temp_rmse'].mean('time', keep_attrs=True)
        
    if ('temp' in avail_vars) and ('temp_bl' not in avail_vars):
        DS_dict['temp_bl'] = dummy_temp_bl_DS(DS_dict['temp'])
    elif ('temp' not in avail_vars) and ('temp_bl' in avail_vars):
        return {}
    
    return DS_dict


def dummy_temp_bl_DS(DS_zen: xr.Dataset):
    
    DS = deepcopy(DS_zen)
    for var in ['flag_h', 'flag_m']: DS[var][:] = 0
    for var in ['temp', 'temp_rmse']: DS[var][...] = np.nan
    DS = DS.isel(time=np.arange(1))
    DS = DS.assign_coords({'time': np.array([np.datetime64("1970-01-01T00:00:00")]).astype('datetime64[ns]')})
    
    ERROR_DS = load_retrieval_uncertainties(var='temp_bl')
    DS = add_retrieval_uncertainties(MWR_DS=DS, ERROR_DS=ERROR_DS, var='temp')
    
    return DS


def merge_zenith_and_bl_temp(DS_dict: dict):
    
    temp_merged = merge_temp_zen_and_bl(DS_dict['temp'].height, DS_dict['temp'].time,
                                        DS_dict['temp'].temp, DS_dict['temp_bl'].temp)
    
    DS = deepcopy(DS_dict['temp'])
    DS = DS.rename({'temp': 'temp_zen', 'temp_rmse': 'temp_zen_rmse'})
    
    time_match_thres = np.timedelta64(1800, "s")
    time_match_idx, time_match_mask = get_idx_of_bl_time_on_zen_time_grid(DS.time.values, 
                                                                          DS_dict['temp_bl'].time.values,
                                                                          time_match_thres)
    DS['temp_bl'] = get_temp_bl_on_zenith_grid(DS, DS_dict['temp_bl'], time_match_idx, time_match_mask)
    DS['temp_bl_rmse'] = deepcopy(DS_dict['temp_bl']['temp_rmse'])
    
    DS['temp'] = temp_merged
    DS = add_retrieval_uncertainties_merged(DS)
    
    time_interp_thres = np.timedelta64(3*3600, "s")
    DS = add_flag_for_temp_prof_usage(DS, DS_dict['temp_bl'].time.values, time_match_idx, 
                                      time_interp_thres, time_match_thres, time_match_mask)

    DS = update_attrs(DS, DS_dict['temp_bl'])
    
    return DS


def get_idx_of_bl_time_on_zen_time_grid(
    time_zen: np.ndarray, 
    time_bl: np.ndarray, 
    time_thres=np.timedelta64(1800, "s")):
    
    time_match_idx = np.asarray([[np.argmin(np.abs(time_zen - t_bl)), 
                                  np.min(np.abs(time_zen - t_bl).astype('timedelta64[s]').astype(np.int64))] 
                                 for t_bl in time_bl])
    time_match_mask = time_match_idx[:,1] < (time_thres.astype('timedelta64[s]').astype(np.int64))
    
    return time_match_idx, time_match_mask


def get_temp_bl_on_zenith_grid(
    DS: xr.Dataset, 
    DS_bl: xr.Dataset, 
    time_match_idx: np.ndarray,
    time_match_mask: np.ndarray):
    
    temp_bl = xr.DataArray(np.full(DS.temp_zen.shape, np.nan), dims=DS.temp_zen.dims)
    temp_bl[time_match_idx[time_match_mask,0],:] = DS_bl.temp.values[time_match_mask,:]
    
    return temp_bl


def add_flag_for_temp_prof_usage(
    DS: xr.Dataset, 
    time_bl: np.ndarray,
    time_match_idx: np.ndarray, 
    time_thres: np.timedelta64,
    time_match_thres: np.timedelta64,
    time_match_mask: np.ndarray):
    
    n_time = len(DS.time)
    DS['flag_usage'] = xr.DataArray(np.full((n_time,), 0, dtype=np.int32), dims='time',
                                    attrs={'standard_name': 'status_flag', 
                                           'long_name': "temperature profile usage flag",
                                           'flag_meanings': "0 = use temp; 1 = use temp_zen",
                                           'comment': ("If time difference between two boundary layer scans is "+
                                                       f"> {time_thres.astype('timedelta64[m]').astype('int')} min, " +
                                                       "the linear interpolation of temp_bl used in temp could be " +
                                                       "inaccurate. For these occasions, flag_usage is 1. " +
                                                       "Further, flag_usage is 1 if a boundary layer scan is >= " +
                                                       f"{time_match_thres.astype('timedelta64[m]').astype('int')} min " +
                                                       "from a zenith time step. " +
                                                       "For times where flag_usage=1, it may be more accurate to " +
                                                       "use temp_zen (e.g., in rapidly changing meteo conditions). " +
                                                       "However, that may lead to sudden temperature " +
                                                       "changes in 0-2 km height at bounds where flag_usage " +
                                                       "switches from 0 to 1 or back.")})
    
    is_there_a_time_bl_match = np.any(time_match_mask)
    if not is_there_a_time_bl_match:
        DS['flag_usage'][:] = 1
    
    time_bl_diff_mask = np.diff(time_bl).astype('timedelta64[s]') > time_thres
    for k, mask in enumerate(time_bl_diff_mask):
        if mask:
            DS['flag_usage'][slice(time_match_idx[k,0], time_match_idx[k+1,0])] = 1

    return DS


def add_retrieval_uncertainties_merged(DS: xr.Dataset):
    
    idx_bl, idx_transition, weight_bl, weight_zen = weights_for_merged_temp_prof(DS.height.values)
    
    DS['temp_rmse'] = deepcopy(DS.temp_zen_rmse)
    DS['temp_rmse'][idx_bl] = DS.temp_bl_rmse[idx_bl]
    DS['temp_rmse'][idx_transition] = (weight_bl*DS.temp_bl_rmse[idx_transition] +
                                        weight_zen*DS.temp_zen_rmse[idx_transition])
    
    return DS


def update_attrs(DS: xr.Dataset, DS_bl: xr.Dataset):
    
    
    DS['temp_zen'].attrs['long_name'] = "zenith " + DS['temp_zen'].attrs['long_name']
    DS['temp_zen'].attrs['ancillary_variables'] = "temp_zen_rmse"
    DS['temp_zen_rmse'].attrs['long_name'] = DS['temp_zen_rmse'].attrs['long_name'].replace(" temp ", " temp_zen ")
    
    DS['temp_bl'].attrs = DS_bl.temp.attrs
    DS['temp_bl'].attrs['ancillary_variables'] = "temp_bl_rmse"
    DS['temp_bl'].attrs['comment'] = ("Note that the height grid does not reflect the true vertical " +
                                      "resolution of the retrieved profile. The vertical resolution of " +
                                      "microwave radiometer retrievals is usually much lower. " +
                                      "For boundary layer scans, it is on the order of hundreds of metres " +
                                      "in the lower troposphere.")
    DS['temp_bl_rmse'].attrs['long_name'] = DS['temp_bl_rmse'].attrs['long_name'].replace(" temp ", " temp_bl ")
    
    DS['temp'].attrs['long_name'] = ("merged " + DS['temp'].attrs['long_name'] + 
                                     " from zenith and boundary layer observations")
    DS['temp'].attrs['comment'] += (" However, in the lower troposphere, this merged product profits from the " +
                                    "higher vertical resolution of the boundary layer scans (hundreds of metres).")
    DS['temp_rmse'].attrs['comment'] += " This uncertainty estimate is a merged product of temp_zen_rmse and temp_bl_rmse."
    
    DS.attrs['comment'] = ("Temperature profiles from boundary layer (bl) scan and zenith (zen) observations " +
                           "were merged: 0-2 km: bl, 2-2.5 km: bl-zen mixture, 2.5-top: zen. " +
                           "We recommend using temp in combination with flag_h, flag_m and flag_usage.")
    
    return DS


def export_merged_DS(
    DS: xr.Dataset, 
    path_output=os.environ['VAMPIRE_DATA'] + "mwr_synergy/for_publication/temp_merged/"):
    
    os.makedirs(path_output, exist_ok=True)
    
    dates, counts = np.unique(DS.time.values.astype('datetime64[D]'), return_counts=True)
    date_str = dates[np.argmax(counts)].astype('str').replace("-","") + "000000"
        
    attr_add = ""
    if ";" not in DS.attrs['history'][-2:]:
        attr_add = "; "
    DS.attrs['history'] += (f"{attr_add}{dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}" +
                            f", merged zenith and bl-scan temp profiles with {script_name}; ")
    
    vars_fill_value = ['lat', 'lon', 'zsl', 'zen', 'temp_zen', 'temp_zen_rmse',
                       'temp_bl', 'temp_bl_rmse', 'temp', 'temp_rmse']
    vars_remove_fill_value = ['time', 'height', 'flag_h', 'flag_m', 'flag_usage']

    DS = encode_time(DS)
    DS['time'].attrs['standard_name'] = 'time'
    for ds_var in DS.variables:
        if ds_var in vars_fill_value:
            DS[ds_var].encoding['_FillValue'] = float(-9999.)
        elif ds_var in vars_remove_fill_value:
            DS[ds_var].encoding['_FillValue'] = None
    
    filename = f"{Constants.CAMPAIGN_NAME}_uoc_hatpro_lhumpro-243-340_l2_temp_v01_{date_str}.nc"
    
    outfile = path_output + filename
    DS.to_netcdf(outfile, mode='w', format="NETCDF4")
    DS = DS.close()
    print(f"Saved {outfile}....")


if __name__ == '__main__':
    main()