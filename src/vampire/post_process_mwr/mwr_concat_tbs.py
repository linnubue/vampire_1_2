import sys
import os
import pdb
import datetime as dt

import xarray as xr
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from vampire.post_process_mwr.post_process_mwr_atm import (load_polarstern_track, add_ps_track_coords)
from vampire.io.readers.mwr import (read_mwr_pro_output)
from vampire.io.readers.mwr_retrieval import exclude_okay_flags
from vampire.analysis.data_tools import encode_time

campaign = "vampire"
if campaign == "vampire":
    data_end = np.datetime64("2024-10-09T12:00:00")
    from vampire.constants import Constants as Constants
elif campaign == 'VAMPIRE2':
    data_end = np.datetime64("2025-08-29T12:00:00")
    from vampire.constants import Constants_PS149 as Constants

script_name = os.path.basename(__file__)
instrument_file_label = {'hatpro': "hatpro",
                         'mirac-p': "lhumpro-243-340"}
all_product_scans = {'atm': {'atm': 'ZENITH', 'atm_bl': 'BL-SCAN', 'atm_transit': ''},
                     'sfc': {'sfc': ['EMIS', 'EMIS-SCAN']}}

def main():
    
    path_output = os.environ['VAMPIRE_DATA'] + "__INSTRUMENT__/for_publication/"
    
    instruments = ['hatpro', 'mirac-p']
    product_types = ['atm', 'sfc']
    date_range = np.arange(np.datetime64(Constants.DATE_START),
                           np.datetime64(Constants.DATE_END) + np.timedelta64(1, "D"),
                           np.timedelta64(1, "D"))
    
    path_data_base = {instr: os.environ['VAMPIRE_DATA'] + instr + "/" for instr in instruments}
    
    PS_DS = load_polarstern_track()
    
    for product_type in product_types:
        product_scans = [*all_product_scans[product_type].values()]
        if product_type == 'sfc':
            product_scans = product_scans[0]
        
        for instrument in instruments:
            path_data = path_data_base[instrument]
            path_output_instr = path_output.replace("__INSTRUMENT__", instrument)
            
            for date in date_range:
                date_str = date.astype('datetime64[D]').astype('str')
                print(date_str)
                date_range_short = np.array([date + np.timedelta64(-1, "D"),
                                            date,
                                            date + np.timedelta64(1, "D")])
                
                try:
                    DS = read_mwr_pro_output(path_data=path_data,
                                            date_range=date_range_short,
                                            scans=product_scans,
                                            with_default_bl_scan=True,
                                            sorted_into_daily_folders=False,
                                            radiometer=instrument,
                                            version='i00',
                                            concat_scans=True,
                                            drop_errs=True,
                                            drop_auxiliaries=False
                                            )
                except ValueError as e:
                    if str(e) == 'must supply at least one object to concatenate':
                        print(f"Insufficient data for {instrument} on {date_str}... skipping...")
                        continue
                if len(DS.time) == 0: continue
                
                DS = post_process_tb_data(DS=DS, 
                                          POLARSTERN_TRACK_DS=PS_DS, 
                                          path_data=path_data, 
                                          date_range_short=date_range_short, 
                                          date=date,
                                          instrument=instrument,
                                          product_type=product_type)
                if len(DS.time) > 0:
                    export_DS(DS, path_output_instr, date_str, instrument, product_type)
            

def post_process_tb_data(
    DS: xr.Dataset, 
    POLARSTERN_TRACK_DS: xr.Dataset, 
    path_data: str, 
    date_range_short: np.ndarray, 
    date: np.datetime64,
    instrument: str,
    product_type='atm'):
    
    if 'time_bnds' in DS.data_vars: DS = DS.drop_vars('time_bnds')
    DS = DS.load()
    
    if product_type == 'atm':
        DS = init_bl_flag(DS)
        if 'n_angle' in DS.dims: DS = expand_time_default_bl_scan(DS)
        try:
            DS = flag_manually_designed_bl_scans(DS, path_data, date_range_short, instrument)
        except ValueError as e:
            if str(e) != 'must supply at least one object to concatenate':
                raise
    
    DS = add_ps_track_coords(DS, POLARSTERN_TRACK_DS)
    DS = elevation_zenith_and_nadir_angles(DS, instrument)
    if product_type == 'sfc':
        DS = drop_wrong_ele_angle_data(DS, instrument)
    # visualise_ele_nadir(DS)
    DS = improve_flags(DS, instrument=instrument)
    DS = update_attrs(DS, instrument=instrument)
    DS = change_order_of_variables(DS)
    DS = remove_redundant_time_dims(DS)
    DS = DS.sel(time=slice(date, date + np.timedelta64(1, "D"))).sortby('time')
    
    DS = DS.sel(time=slice(None, data_end))
    
    return DS


def init_bl_flag(DS: xr.Dataset):
    
    DS['flag_bl'] = xr.DataArray(np.zeros(len(DS.time), dtype=np.short), dims=['time'],
                                 attrs={'standard_name': "status_flag",
                                        'long_name': "flag indicating whether obs is a bl-scan or not",
                                        'units': "1",
                                        'flag_meanings': ("0: no bl-scan, " +
                                                          "1: default bl-scan (e.g., transit), " +
                                                          f"2: manually designed bl-scan for {Constants.CAMPAIGN_NAME}")})
    
    return DS


def expand_time_default_bl_scan(DS: xr.Dataset):
    
    bl_mask = np.abs(DS.ele.diff('n_angle')).max('n_angle') > 0
    idx_bl = np.where(bl_mask)[0]
    time_diff = DS.time.diff('time').values.astype('timedelta64[s]')
    
    n_angles = len(DS.n_angle)
    
    DS_add = list()
    for idx in idx_bl:
        if (time_diff[idx] > np.timedelta64(91, "s")) & (n_angles < 9):
            DS_ = xr.Dataset(coords={'time': (['time'], np.arange(DS.time.values[idx] + np.timedelta64(1, "s"),
                                                                  DS.time.values[idx] + np.timedelta64(91, "s"),
                                                                  np.timedelta64(10, "s"))),
                                    'freq_sb': DS.freq_sb})
            DS_ = DS_.isel(time=slice(None, n_angles))
            
            DS_ = reshape_default_bl_scan_data_and_update_flag(DS_, DS, idx)                
            DS_add.append(DS_)
            
        elif (n_angles < 9) & (time_diff[idx] <= np.timedelta64(91, "s")):
            pdb.set_trace()     # debug
    
    
    DS = DS.sel(time=~bl_mask).isel(n_angle=0)
    DS = xr.concat([DS,] + DS_add, dim='time').sortby('time')
    DS['flag'].loc[{'time': DS.flag_bl == 1}] += 2      # because HATPRO measured the wrong quadrant during transit BL scans
    
    return DS


def reshape_default_bl_scan_data_and_update_flag(
    DS_bl: xr.Dataset, 
    DS: xr.Dataset, 
    bl_time_idx: int):

    for var in DS.data_vars:
        var_dims = [*DS[var].dims]
        if 'time' not in var_dims: pdb.set_trace()
        
        DA = DS[var][bl_time_idx,...]
        
        if 'n_angle' in var_dims:
            var_dims.remove('n_angle')
            DA_new = DA.transpose('n_angle', ...).values
        elif len(var_dims) == 1:
            if var == 'flag_bl': DA[...] = 1
            DA_new = np.broadcast_to(DA.values, DS_bl.time.shape)
        else:
            DA_new = np.broadcast_to(DA.values, DS_bl.time.shape + DA.values.shape)
        
        DS_bl[var] = xr.DataArray(DA_new, dims=var_dims, attrs=DS[var].attrs)

    return DS_bl


def flag_manually_designed_bl_scans(
    DS: xr.Dataset, 
    path_radiometer: str,
    date_range: np.ndarray,
    instrument='hatpro'):
    
    DS_BL = read_mwr_pro_output(path_data=path_radiometer,
                                date_range=date_range,
                                scans=["BL-SCAN"],
                                with_default_bl_scan=False,
                                sorted_into_daily_folders=False,
                                radiometer=instrument,
                                version='i00',
                                concat_scans=True,
                                drop_errs=True,
                                drop_auxiliaries=False
                                )
    
    intersect_result = np.intersect1d(DS.time.values, DS_BL.time.values, return_indices=True)
    idx_isct = intersect_result[1]
    
    DS['flag_bl'][idx_isct] = 2
    
    return DS


def drop_wrong_ele_angle_data(DS: xr.Dataset, instrument: str):
    
    """
    Some ZENITH data seems to have been mistakenly saved to EMIS or EMIS-SCAN files in the 
    original data. These values should be removed from the data set.
    """
    
    DS = DS.sel(time=~((DS.ele > 89.) & (DS.ele < 91.)))
    if instrument == 'mirac-p':
        DS = DS.sel(time=~((DS.time >= np.datetime64("2025-08-02T11:21:00")) & 
                           (DS.time < np.datetime64("2025-08-02T11:23:00"))))
    
    return DS


def elevation_zenith_and_nadir_angles(DS: xr.Dataset, instrument='hatpro'):
    
    if instrument == 'hatpro':
        DS['azi'][...] = 90.
    elif instrument == 'mirac-p':
        DS['azi'][...] = 270.
    DS['azi'].attrs['comment'] = ("Relative to RV Polarstern bow: 0=towards bow, 90=towards starboard side, 180=towards aft, " +
                                  "270=towards portside. Only for reconstruction of original sensor elevation angles.")
    
    if np.any(DS.ele.values > 90.5): 
        # pdb.set_trace()         # can eventually be deleted
        DS['ele'] = DS.ele.where(DS.ele <= 90.5, other=np.round((180. - DS.ele)*10.)*0.1)
    
    DS['nadir'] = xr.DataArray(ele_to_nadir_ang(DS.ele.values), dims=DS.ele.dims,
                               attrs={'units': 'degrees',
                                      'standard_name': 'sensor_nadir_angle',
                                      'long_name': 'nadir angle of the observation',
                                      'valid_range': np.array([0.0, 180.0], dtype=np.float32),
                                      'comment': "Nadir angle of 0 degrees: Directly below, 180 degrees: directly overhead"})
    DS['zen'] = xr.DataArray(ele_to_zenith_ang(DS.ele.values), dims=DS.ele.dims,
                             attrs={'units': 'degrees',
                                    'standard_name': 'sensor_zenith_angle',
                                    'long_name': 'zenith angle of the observation',
                                    'valid_range': np.array([0.0, 180.0], dtype=np.float32),
                                    'comment': "Zenith angle of 0 degrees: Directly overhead, 180 degrees: directly below"})
    
    return DS


def ele_to_nadir_ang(ang):
    return ang + 90.


def ele_to_zenith_ang(ang):
    return np.abs(ang - 90.)


def visualise_ele_nadir(DS: xr.Dataset):
    
    f1 = plt.figure()
    a1 = plt.axes()
    
    a1.plot(DS.time, DS.ele, label='ele')
    a1.plot(DS.time, DS.zen, label='zen')
    a1.plot(DS.time, DS.nadir, label='nad')
    
    lh, ll = a1.get_legend_handles_labels()
    a1.legend(lh, ll, loc='upper right')
    
    a1.set_ylabel("Angle (deg)")
    
    plt.show()


def improve_flags(DS: xr.Dataset, instrument='hatpro'):
    
    also_okay_flag_values = np.array([])
    if instrument == 'mirac-p':
        also_okay_flag_values = np.array([16])
    
    DS = exclude_okay_flags(DS, 'flag', also_okay_flag_values)
    DS['flag'].attrs['recommendation'] = ("Flag values of 0 should be used. All other data must be used " + 
                                          "with care or should be discarded.")
        
    DS['flag'] = DS.flag.astype(np.short)

    return DS


def update_attrs(DS: xr.Dataset, instrument: str):
    
    DS.attrs['Source'] = DS.attrs['Source'].replace("MIRAC-P", "MiRAC-P")
    DS.attrs['History'] = (DS.attrs['Processing_date'].replace(", ", " ") + ", " + DS.attrs['History']) + "; "
    del DS.attrs['Processing_date']
    DS.attrs['History'] += (f"{dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}" +
                            f", concatenated atmospheric TB measurements, added RV Polarstern coords and " +
                            f"different observation angles with {script_name}; ")
    DS.attrs['Author'] += ", Andreas Walbröl (a.walbroel@uni-koeln.de)"
    
    DS['lat'].attrs['long_name'] = "latitude of RV Polarstern"
    DS['lon'].attrs['long_name'] = "longitude of RV Polarstern"
    DS['lat'].attrs['valid_range'] = np.array([-90., 90.], dtype=np.float32)
    DS['lon'].attrs['valid_range'] = np.array([-180., 180.], dtype=np.float32)
    DS['zsl'].attrs['long_name'] = "altitude of instrument above mean sea level"
    DS['azi'].attrs['long_name'] = "azimuth angle of the observation"
    DS['ele'].attrs = {'units': 'degrees',
                       'standard_name': 'sensor_elevation_angle',
                       'long_name': "elevation angle of the sensor",
                       'valid_range': np.array([0., 180.], dtype=np.float32),
                       'comment': 'Elevation angle of 0 degrees: Horizontal, 90 degrees: directly overhead'}
    DS['tb_bias_estimate'].attrs['comment'] = DS['tb_bias_estimate'].attrs['comment'].replace(
        "systemmatic", 
        "systematic"
    )
    DS['flag'].attrs['flag_meanings'] = DS['flag'].attrs['flag_meanings'].replace(
        "visual_inspection_filter_band_1",
        "visual_inspection_filter_band1"
        )
    
    if instrument == 'mirac-p':
        DS['flag'].attrs['comment'] = DS['flag'].attrs['comment'].replace(
            "band 1: 20-40 GHz, band 2: 40-70 GHz, band 3: <20 or >70 GHz",
            "band 1: 170-195 GHz, band 2: 243-340 GHz, band 3: unused"
            )
    
    return DS


def remove_redundant_time_dims(DS: xr.Dataset):
    
    for var in ['tb_absolute_accuracy', 'freq_shift']:
        if (var in DS.data_vars) and ('time' in DS[var].dims):
            DS[var] = DS[var].mean('time', keep_attrs=True)
    
    return DS


def change_order_of_variables(DS: xr.Dataset):
    
    data_vars = [*DS.variables]
    data_vars.remove('ele')
    data_vars.append('ele')
    data_vars.remove('azi')
    data_vars.append('azi')
    
    DS = DS[data_vars]
    
    return DS


def export_DS(
    DS: xr.Dataset,
    path_output: str, 
    date_str: str, 
    instrument: str, 
    product_type='atm'):
    
    
    os.makedirs(path_output, exist_ok=True)
    
    date_str = date_str.replace("-","") + "000000"
    
    vars_fill_value = ['lat', 'lon', 'zsl', 'azi', 'ele', 'zen', 'nadir',
                       'tb', 'ta', 'pa', 'hur']
    vars_remove_fill_value = ['time', 'flag', 'flag_bl', 'freq_sb', 'tb_bias_estimate',
                              'freq_shift', 'tb_absolute_accuracy']

    DS = encode_time(DS)
    DS['time'].attrs['standard_name'] = 'time'
    for ds_var in DS.variables:
        if ds_var in vars_fill_value:
            DS[ds_var].encoding['_FillValue'] = float(-9999.)
        elif ds_var in vars_remove_fill_value:
            DS[ds_var].encoding['_FillValue'] = None
    
    product_type_suffix = ""
    if product_type == 'sfc':
        product_type_suffix = "_sfc"
    filename = f"{Constants.CAMPAIGN_NAME}_uoc_{instrument_file_label[instrument]}_l1_tb{product_type_suffix}_v01_{date_str}.nc"
    
    outfile = path_output + filename
    DS.to_netcdf(outfile, mode='w', format="NETCDF4")
    DS = DS.close()
    print(f"Saved {outfile}....")


if __name__ == '__main__':
    main()