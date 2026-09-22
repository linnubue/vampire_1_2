import sys
import os
import glob
import re
import datetime as dt
import pdb
from copy import deepcopy

import numpy as np
import xarray as xr
import pandas as pd

from vampire.io.readers.mwr_retrieval import read_mwr_retrieval_output, exclude_okay_flags
from vampire.analysis.data_tools import convert_units, encode_time

campaign = "VAMPIRE2"
if campaign == "vampire":
    data_end = np.datetime64("2024-10-09T12:00:00")
    from vampire.constants import Constants as Constants
    position_source = ("Rabe, Benjamin; Geibert, Walter (2024): Master track of POLARSTERN cruise PS144 " +
                       "in 1 sec resolution (zipped, 243 MB) [dataset]. Alfred Wegener Institute, Helmholtz " +
                       "Centre for Polar and Marine Research, Bremerhaven, PANGAEA, " +
                       "https://doi.org/10.1594/PANGAEA.974028")
elif campaign == 'VAMPIRE2':
    data_end = np.datetime64("2025-08-29T12:00:00")
    from vampire.constants import Constants_PS149 as Constants
    position_source = ("Nicolaus, Marcel (2025): Master track of POLARSTERN cruise PS149 in 1 sec " +
                       "resolution (zipped, 221 MB) [dataset]. Alfred Wegener Institute, Helmholtz " +
                       "Centre for Polar and Marine Research, Bremerhaven, PANGAEA, " +
                       "https://doi.pangaea.de/10.1594/PANGAEA.987132")


script_name = os.path.basename(__file__)
std_name = {'prw': 'atmosphere_mass_content_of_water_vapor',      # translate to CF conventions standard_name
            'lwp': 'atmosphere_mass_content_of_cloud_liquid_water_content',
            'temp': 'air_temperature',
            'q': 'specific_humidity'}
rounding_val = {'temp': 0.1, 'q': 0.002}    # for rounding; in K, K, g kg-1
unit_conv_dict = {'q': [0.0, 0.001],      # from g kg-1 to kg kg-1
                  'temp': [0.0, 1.0]}     # from K to K
naming_translation = {'prw': 'iwv', 
                      'q': 'q', 
                      'temp': 'temp', 
                      'lwp': 'clwvi', 
                      'temp_bl': 'temp_bl'}
var_translation = {'prw': 'prw',
                   'q': 'q',
                   'temp': 'temp',
                   'lwp': 'lwp',
                   'temp_bl': 'temp'}


def main():
    
    path_data = {'mwr_synergy_output': os.environ['VAMPIRE_DATA'] + "mwr_synergy/output/",
                 'hatpro_mwr_pro': os.environ['VAMPIRE_DATA'] + "hatpro/atm/l2/",
                 'ps_track': os.environ['VAMPIRE_DATA'] + "polarstern_track/",
                 'mwr_synergy_eval': os.environ['VAMPIRE_DATA'] + synergetic_ret_eval_stats/}
    path_output = os.environ['VAMPIRE_DATA'] + "mwr_synergy/for_publication/"
    
    date_range = np.arange(np.datetime64(Constants.DATE_START),
                           np.datetime64(Constants.DATE_END) + np.timedelta64(1, "D"),
                           np.timedelta64(1, "D"))
    vars = ['prw', 'q', 'temp', 'temp_bl', 'lwp']
    
    PS_DS = load_polarstern_track(path_data['ps_track'])
    
    for var in vars:
        
        if var in ['prw', 'q', 'temp', 'temp_bl']:
            path_mwr = path_data['mwr_synergy_output']
            read_ret_kwargs = dict(mwr_pro_output=False)
            ERROR_DS = load_retrieval_uncertainties(path_data['mwr_synergy_eval'], var)
            
        else:
            path_mwr = path_data['hatpro_mwr_pro']
            read_ret_kwargs = dict(
                file_pattern=f"ioppol_uoc_mwr00_l2_var_i00___DATE_STRING__[0-2][0-9][0-5][0-9][0-5][0-9].nc",
                mwr_pro_output=True,
                )
            ERROR_DS = xr.Dataset()
        
        for date in date_range:
            date_str = date.astype('datetime64[D]').astype('str')
            print(date_str)
            try:
                MWR_DS = read_mwr_retrieval_output(path_data=path_mwr,
                                                   vars_=[var],
                                                   with_processing=False,
                                                   date_range=np.array([date]),
                                                   remove_bad_flag_data=False,
                                                   **read_ret_kwargs)
                MWR_DS = MWR_DS[var].load()
            except OSError:
                continue
            
            MWR_DS = add_ps_track_coords(MWR_DS, PS_DS.sel(time=date_str))
            MWR_DS = add_retrieval_uncertainties(MWR_DS, ERROR_DS, var_translation[var])
            MWR_DS = simplify_flags(MWR_DS, var)
            MWR_DS = flag_add_artifacts(MWR_DS)
            if var == 'lwp': MWR_DS = unify_attrs(MWR_DS)
            
            MWR_DS = MWR_DS.sel(time=slice(None, data_end))
            if len(MWR_DS.time) > 0:
                export_DS(MWR_DS, path_output, var)


def load_polarstern_track(path=os.environ['VAMPIRE_DATA'] + "polarstern_track/"):
    
    file = path + f"{Constants.CAMPAIGN_NAME}_mastertrack.txt"
    DF = pd.read_csv(file, sep="\t", header=0, index_col=0, 
                     usecols=[0,1,2],
                     dtype={'Latitude': np.float64,
                            'Longitude': np.float64})
    
    DS = DF.to_xarray()
    DS = DS.rename({'Date/Time (UTC)': 'time'})
    DS = DS.assign_coords({'time': DS.time.astype('datetime64[ns]')})
    
    return DS


def load_retrieval_uncertainties(
    path: str,
    var='prw'):
        
    file = path + f"NN_syn_ret_ERA5_eval_data_error_stats_{naming_translation[var]}.nc"
    DS = xr.open_dataset(file).load()
    
    return DS


def add_ps_track_coords(MWR_DS: xr.Dataset, PS_DS: xr.Dataset):
    
    PS_DS_ip = PS_DS.interp(time=MWR_DS.time, method='linear')
    for mwr_var, ps_var in zip(['lat', 'lon'], ['Latitude', 'Longitude']):
        MWR_DS[mwr_var][:] = PS_DS_ip[ps_var].values
        
    MWR_DS.attrs['position_source'] = position_source
    
    return MWR_DS


def simplify_flags(DS: xr.Dataset, var='prw'):
    
    if ('flag_h' not in DS.data_vars) & ('flag_m' not in DS.data_vars) & (var in ['lwp', 'clwvi']):
        DS['flag_h'] = DS.flag.astype(np.short)
        DS['flag_h'].attrs = {'long_name': "quality control flags for HATPRO",
                              'standard_name': "status_flag",
                              'units': "1",
                              'flag_masks': DS.flag.flag_masks,
                              'flag_meanings': ("visual_inspection_filter_band1 " +
                                                "visual_inspection_filter_band2 " +
                                                "visual_inspection_filter_band3 " +
                                                "rain_flag " +
                                                "sanity_receiver_band1 " +
                                                "sanity_receiver_band2 " + 
                                                "sun_in_beam " +
                                                "tb_threshold_band1 " +
                                                "tb_threshold_band2 " +
                                                "tb_threshold_band3 " +
                                                "retrieved_quantity_threshold"),
                              'valid_range': np.array([0,2047], dtype=np.short),
                              'comment': ("Flags indicate data that the user should only use with care. " +
                                          "In cases of doubt, please discuss with the contact person. " +
                                          "A value of 0 means that data has not been flagged. " +
                                          "Bands refer to the measurement ranges (if applicable) of the " +
                                          "microwave radiometer; i.e band 1: 20-35 GHz, band 2: 50-60 GHz, " +
                                          "band 3: 90 GHz; tb valid range: [  2.70, 330.00] in K; " +
                                          "retrieved quantity valid range: [-0.2, 3.0] in kg m-2; ")}

        DS['flag_m'] = deepcopy(DS.flag_h)
        DS['flag_m'][:] = 0
        DS['flag_m'].attrs['long_name'] = DS['flag_m'].attrs['long_name'].replace("HATPRO", 
                                                                                  "MiRAC-P (LHUMPRO-243-340)")
        DS['flag_m'].attrs['flag_meanings'] = DS['flag_m'].attrs['flag_meanings'].replace(
            "tb_threshold_band1 tb_threshold_band2 tb_threshold_band3 retrieved_quantity_threshold", 
            "unused unused unused unused"
        )
        DS['flag_m'].attrs['comment'] = ("Flags indicate data that the user should only use with care. " +
                                         "In cases of doubt, please discuss with the contact person. " +
                                         "A value of 0 means that data has not been flagged. " +
                                         "Bands refer to the measurement ranges (if applicable) of the " +
                                         "microwave radiometer; i.e band 1: all lhumpro frequencies " +
                                         "(170-200, 243, and 340 GHz); tb valid range: [  2.70, 330.00] in K; ")
        DS = DS.drop_vars('flag')
    
    
    for flag_name in ['flag_h', 'flag_m']:
        if flag_name == 'flag_m':
            also_okay_flag_values = np.array([16])
        elif flag_name == 'flag_h':
            also_okay_flag_values = np.array([])
        
        DS = exclude_okay_flags(DS, flag_name, also_okay_flag_values)
        DS[flag_name].attrs['recommendation'] = ("Flag values of 0 should be used. All other data must be used " + 
                                                 "with care or should be discarded.")
    
    return DS


def flag_add_artifacts(DS: xr.Dataset):
    
    time_mask = (((DS.time >= np.datetime64("2024-08-12T11:06:00")) & 
                (DS.time <= np.datetime64("2024-08-12T11:08:59"))) |
                ((DS.time >= np.datetime64("2024-08-12T12:29:00")) & 
                (DS.time <= np.datetime64("2024-08-12T18:24:59"))) |
                ((DS.time >= np.datetime64("2024-08-15T07:34:00")) & 
                (DS.time <= np.datetime64("2024-08-15T07:35:30"))) |
                ((DS.time >= np.datetime64("2024-08-17T08:45:30")) & 
                (DS.time <= np.datetime64("2024-08-17T08:46:00"))))
    for flag_var in ['flag_h', 'flag_m']:
        DS[flag_var].loc[{'time': time_mask}] += 3
    
    return DS


def add_retrieval_uncertainties(MWR_DS: xr.Dataset, ERROR_DS: xr.Dataset, var='prw'):
    
    ret_unc_attrs = {'long_name': f"Estimated uncertainty of {var} given as root mean squared error",
                     'standard_name': f"{std_name[var]} standard_error",
                     'units': MWR_DS[var].attrs['units'],
                     'comment': ("Root mean squared error has been computed over 4 years of ERA5 data " +
                                 "and rounded up to the next ...")}
    
    if var == 'prw':
        n_time = len(MWR_DS.time)
        var_rmse = xr.DataArray(np.full((n_time,), -9999.0), 
                                dims=MWR_DS[var].dims, 
                                coords=MWR_DS[var].coords)
        
        for i_bin, bin in enumerate(ERROR_DS.bins):
            rmse_bins_mean = np.ceil((ERROR_DS.rmse_bins_mean[i_bin].values+1e-09)*10.)*0.1
            var_rmse = xr.where((MWR_DS[var] >= ERROR_DS.bins_bnds[i_bin,0].values) &
                                (MWR_DS[var] < ERROR_DS.bins_bnds[i_bin,1].values),
                                rmse_bins_mean, var_rmse)
            
        var_rmse[(var_rmse < 0.1) & (var_rmse >= 0.0)] = 0.1        # as abs. min rmse in kg m-2
        
        MWR_DS[f'{var}_rmse'] = xr.DataArray(var_rmse.astype(np.float32))
        ret_unc_attrs['comment'] = ret_unc_attrs['comment'].replace("...", "0.1.")
        
    elif var == 'lwp':
        MWR_DS[f'{var}_rmse'] = MWR_DS[f'{naming_translation[var]}_err'].mean('time', keep_attrs=True)
        
    else:
        rmse_mean = np.ceil((ERROR_DS.rmse_tot_mean.values+1e-09)/rounding_val[var])*rounding_val[var]
        rmse_mean = convert_units(rmse_mean, unit_conv_list=unit_conv_dict[var])

        MWR_DS[f'{var}_rmse'] = xr.DataArray(rmse_mean.astype(np.float32), dims=['height'])
        ret_unc_attrs['comment'] = ret_unc_attrs['comment'].replace(
            "...", 
            f"{str(rounding_val[var]*unit_conv_dict[var][1])}. Errors may vary over the seasons."
            )

    MWR_DS[f'{var}_rmse'].attrs = ret_unc_attrs
    MWR_DS[f'{var}_rmse'].encoding["_FillValue"] = float(-9999.)
    
    return MWR_DS


def unify_attrs(DS: xr.Dataset):
    
    for var in DS.data_vars:
        if 'lwp' in var:
            DS = DS.rename_vars({var: var.replace('lwp', naming_translation['lwp'])})
    
    DS = DS.drop_vars(['clwvi_err', 'time_bnds'])
    DS = DS.rename_vars({'clwvi_rmse': 'clwvi_err'})
    DS['clwvi_err'].attrs['long_name'] = DS['clwvi_err'].attrs['long_name'].replace(
        " given as root mean squared error", "")
    del DS['clwvi_err'].attrs['comment']
    
    DS['clwvi'].attrs['long_name'] = "liquid water path or total liquid cloud water"
    DS['clwvi'].attrs['ancillary_variables'] = 'clwvi_err'
    DS['clwvi'].attrs['valid_min'] = float(-0.2)
    DS['clwvi'].attrs['valid_max'] = float(3.0)
    
    DS['ele_ret'] = DS['ele_ret'].mean('time', keep_attrs=True)
    
    DS['time'].attrs['standard_name'] = "time"
    
    DS.attrs = {'title': ("Retrieved atmosphere_mass_content_of_cloud_liquid_water_content (clwvi) " +
                          f"from microwave radiometer measurements during the {Constants.CAMPAIGN_NAME} expedition"),
                'institution': "Institute for Geophysics and Meteorology, University of Cologne, Cologne, Germany",
                'contact_person': "Andreas Walbroel (a.walbroel@uni-koeln.de)",
                'author': "Andreas Walbroel (a.walbroel@uni-koeln.de)",
                'license': "For non-commercial use only.",
                'source': "Microwave radiometers RPG HATPRO G5",
                'dependencies': "HATPRO brightness temperatures",
                'Conventions': "CF-1.8",
                'history': (DS.attrs['Processing_date'].replace(", ", " ") + ", " +
                            DS.attrs['History'].replace("CologneRetrieval", "Cologne, Retrieval; ")),
                'measurement_site': "RV Polarstern",
                'position_source': DS.attrs['position_source'],
                }
    
    return DS


def export_DS(
    DS: xr.Dataset,
    path_output=os.environ['VAMPIRE_DATA'] + "mwr_synergy/for_publication/",
    var='prw'):
    
    os.makedirs(path_output, exist_ok=True)
        
    attr_add = ""
    if ";" not in DS.attrs['history'][-2:]:
        attr_add = "; "
    DS.attrs['history'] += (f"{attr_add}{dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}" +
                            f", added RV Polarstern coords and retrieval errors with {script_name}; ")
    
    vars_fill_value = ['lat', 'lon', 'zsl', 'azi', 'ele', 'ele_ret', 'zen', 'prw',
                       'clwvi', 'clwvi_offset', 'clwvi_off_zenith', 'clwvi_offset_zeroing', 'clwvi_off_zenith_offset',
                       'temp', 'q']
    vars_remove_fill_value = ['time', 'height', 'flag_h', 'flag_m']

    DS = encode_time(DS)
    DS['time'].attrs['standard_name'] = 'time'
    for ds_var in DS.variables:
        if ds_var in vars_fill_value:
            DS[ds_var].encoding['_FillValue'] = float(-9999.)
        elif ds_var in vars_remove_fill_value:
            DS[ds_var].encoding['_FillValue'] = None
    
    filename = os.path.basename(DS.encoding['source'])
    if (Constants.CAMPAIGN_NAME not in filename) & ("ioppol" in filename) & (var == 'lwp'):
        date_file = dt.datetime.strptime(filename[-17:-3], "%Y%m%d%H%M%S").date().strftime("%Y%m%d%H%M%S")
        filename = f"{Constants.CAMPAIGN_NAME}_uoc_hatpro_lhumpro-243-340_l2_clwvi_v00_{date_file}.nc"

    outfile = path_output + filename.replace("v00", "v01")
    DS.to_netcdf(outfile, mode='w', format="NETCDF4")
    DS = DS.close()
    print(f"Saved {outfile}....")

    
if __name__ == "__main__":
    main()

