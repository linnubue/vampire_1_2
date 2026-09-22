import glob
import pdb
from copy import deepcopy

import xarray as xr
import numpy as np

from vampire.constants import Constants_PS149 as Constants
from vampire.analysis.data_tools import (running_mean_pdtime, mwr_pro_flags_to_2d_bits, 
                                         flag_values_to_2d_flag_bits, identify_files_daterange)
from vampire.io.readers.mwr import mwr_pro_flags_nan_to_num

var_name_translation = {'temp': 'ta',
                        'temp_bl': 'ta_bl',
                        'q': 'hus',
                        'rho_v': 'hua',
                        'prw': 'prw',
                        'lwp': 'clwvi'}

def read_mwr_retrieval_output(
    path_data: str, 
    vars_: list, 
    with_processing=True,
    file_pattern=f"{Constants.CAMPAIGN_NAME}_uoc_hatpro_lhumpro-243-340_l2_var_v00___DATE_STRING__[0-2][0-9][0-5][0-9][0-5][0-9].nc",
    date_range=np.array([]),
    remove_bad_flag_data=True,
    merge_temp_zenith_and_bl=False,
    mwr_pro_output=False,
    compress_error_vars=False):
    
    DS_dict = dict()
    for var in vars_:
        files_var = find_files(path_data, file_pattern, var, date_range)
        DS_dict[var] = xr.open_mfdataset(files_var, concat_dim='time', combine='nested')
        
        if mwr_pro_output:
            DS_dict[var] = mwr_pro_flags_nan_to_num(DS_dict[var])
                
        if (np.any(np.array(DS_dict[var].variables) == var_name_translation[var]) and 
            var_name_translation[var] != var) or ((var == 'temp_bl') and ('ta' in DS_dict[var].variables)):
            DS_dict[var] = unify_variable_names(DS_dict[var])
            
        if (var == 'temp') and merge_temp_zenith_and_bl:
            DS_BL = xr.open_mfdataset(find_files(path_data, file_pattern, 'temp_bl', date_range),
                                      concat_dim='time', combine='nested').load()
            DS_dict[var] = DS_dict[var].load()
            DS_dict[var]['temp'][:] = merge_temp_zen_and_bl(DS_dict[var].height, DS_dict[var].time, 
                                                            DS_dict[var].temp, DS_BL.temp)
        
        if with_processing:
            dims_ = [*DS_dict[var][var].dims]
            dims_.remove('time')
            DS_dict[var] = temporally_smooth_retrieval_output(DS_dict[var], var=var).load()
            if len(dims_) > 0:
                DS_dict[var] = DS_dict[var].sel(time=~DS_dict[var][var].isnull().all(dims_))
            else:
                DS_dict[var] = DS_dict[var].sel(time=~DS_dict[var][var].isnull())
        
            
        if remove_bad_flag_data and (not with_processing):
            DS_dict[var] = flag_bad_data(DS_dict[var])
        
        if compress_error_vars:
            DS_dict[var] = cut_time_dim(DS_dict[var])
    
    return DS_dict


def find_files(path_data: str, file_pattern: str, var: str, date_range=np.array([]), yyyymmdd_delim=""):
    
    def find_files_subroutine(path_data: str, file_pattern: str, date_range=np.array([])):
        
        if len(date_range) > 0:
            files = identify_files_daterange(path_data, date_range, file_pattern, yyyymmdd_delim=yyyymmdd_delim)
        else:
            yyyymmdd_expr = f"[0-9][0-9][0-9][0-9]{yyyymmdd_delim}[0-1][0-9]{yyyymmdd_delim}[0-3][0-9]"
            files = sorted(glob.glob(path_data + file_pattern.replace("__DATE_STRING__", yyyymmdd_expr)))
    
        return files
    
    files = list()
    files = find_files_subroutine(path_data, file_pattern.replace("var", var), date_range)
    
    if len(files) == 0:
        try:
            updated_file_pattern = file_pattern.replace("var", var_name_translation[var])
        except KeyError:
            return files
        files = find_files_subroutine(path_data, updated_file_pattern, date_range)
    if (len(files) == 0) and (var == "temp_bl") and ("ioppol_uoc_" in file_pattern):
        pdb.set_trace()   # check if new_substr_add works correctly here
        updated_file_pattern = file_pattern.replace("var", "ta").replace("mwr00", "mwrBL00")
        files = find_files_subroutine(path_data, updated_file_pattern, date_range)
        
    return files


def cut_time_dim(DS: xr.Dataset):
    
    data_vars = np.array(DS.data_vars)
    is_error_var = np.asarray(['_rmse' in dv for dv in data_vars])
    idx_error_var = np.where(is_error_var)[0]
    
    if np.any(is_error_var):
        idx_error_var = np.where(is_error_var)[0]
        time_invariant_error_var = np.asarray([data_vars[idx] for idx in idx_error_var if 
                                               'height' in DS[data_vars[idx]].dims])
        for var in time_invariant_error_var:
            DS[var] = DS[var].mean('time', keep_attrs=True)
    
    return DS


def exclude_okay_flags(
    DS: xr.Dataset, 
    flag_name: str, 
    also_okay_flag_values: np.ndarray):
    
    if len(also_okay_flag_values) == 0: return DS
    
    okay_flag_bin = flag_values_to_2d_flag_bits(also_okay_flag_values, 
                                                n_bits=int(np.log2(also_okay_flag_values).max())+1)
    idx_okay_flags = -1*(okay_flag_bin.shape[1] - np.where(okay_flag_bin == 1)[1])
    
    DS = mwr_pro_flags_to_2d_bits(DS, quality_flag_name=flag_name, n_bits=len(DS[flag_name].flag_masks))
    for idx_okay, okay_flag in zip(idx_okay_flags, also_okay_flag_values):
        DS[flag_name][DS[flag_name+"_bits"][:,idx_okay] == 1] -= okay_flag
    
    if flag_name+"_bits" in DS.data_vars: DS = DS.drop_vars([flag_name+"_bits"])
    if 'bit' in DS.dims: DS = DS.drop_dims('bit')
        
    return DS


def flag_bad_data(DS: xr.Dataset):
        
    if 'flag' in DS.variables:
        also_okay_flag_values = np.array([16])
        DS = exclude_okay_flags(DS, 'flag', also_okay_flag_values)            
        DS = DS.sel(time=(DS.flag == 0))
        
    if ("flag_h" in DS.variables) and ("flag_m" in DS.variables):
        
        for flag_name in ['flag_h', 'flag_m']:
            if flag_name == 'flag_m':
                also_okay_flag_values = np.array([16])
            elif flag_name == 'flag_h':
                also_okay_flag_values = np.array([])
            
            DS = exclude_okay_flags(DS, flag_name, also_okay_flag_values)
        
        DS = DS.sel(time=(DS.flag_h == 0) & (DS.flag_m == 0))
        
    return DS


def temporally_smooth_retrieval_output(DS: xr.Dataset, var: str):
    
    DS = flag_bad_data(DS)
    
    if 'height' in DS.variables:
        DS = DS.resample(time="30min").mean()
    elif var in ['prw', 'clwvi', 'lwp']:
        DS[var][:] = running_mean_pdtime(DS[var].values, 300, DS.time.values)
    
    return DS


def merge_temp_zen_and_bl(
    height_zen: xr.DataArray, 
    time_zen: xr.DataArray, 
    temp_zen: xr.DataArray, 
    temp_BL: xr.DataArray):
    
    """
    Merges the zenith and boundary layer scan temperature profiles. The boundary layer profiles
    are temporally interpolated onto the zenith time axis. 
    0-2000 m: BL profile, 2000-2500 m: linear transition, 2500-end: zenith profile
    """
    
    idx_bl, idx_transition, weight_bl, weight_zen = weights_for_merged_temp_prof(height_zen.values)
    
    temp_bl = temp_BL.interp(coords={'time': time_zen})
    temp_combined = deepcopy(temp_zen)
    nonnan_idx = np.where(~temp_bl[:,idx_bl].isnull().all('height'))[0]
    
    try:
        temp_combined[nonnan_idx, idx_bl] = temp_bl[nonnan_idx, idx_bl]
        temp_combined[nonnan_idx, idx_transition] = (weight_bl*temp_bl[nonnan_idx, idx_transition] + 
                                                     weight_zen*temp_zen[nonnan_idx, idx_transition])
    except NotImplementedError:
        print("Please use the .load() function on the xarray.Datasets or xarray.DataArrays used in this function.")
        
    return temp_combined


def weights_for_merged_temp_prof(height: np.ndarray):
    
    h_bl, h_transition = 2000., 2500.       # height in m
    idx_bl = np.where(height <= h_bl)[0]
    idx_transition = np.where((height > h_bl) & 
                              (height <= h_transition))[0]
    
    weight_bl = (-1./(h_transition-h_bl))*height[idx_transition] + 1./(h_transition-h_bl)*h_transition
    weight_zen = 1 - weight_bl
    
    return idx_bl, idx_transition, weight_bl, weight_zen


def unify_variable_names(ds: xr.Dataset):
    
    for key, value in var_name_translation.items():
        if value in ds.variables:
            ds = ds.rename({value: key})
            
    return ds