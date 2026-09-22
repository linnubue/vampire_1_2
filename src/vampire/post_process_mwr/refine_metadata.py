import sys
import os
import pdb
import glob

import numpy as np
import xarray as xr

from vampire.analysis.data_tools import update_netCDF_file_history, encode_time


def main():
    
    products = ['tb', 'tb_sfc', 'clwvi', 'prw', 'q', 'temp']
    radiometers = ['hatpro', 'mirac-p']
    
    path_data = {'tb': {rr: os.environ['VAMPIRE_DATA'] + f"{rr}/for_publication/" for rr in radiometers},
                 'clwvi': os.environ['VAMPIRE_DATA'] + "mwr_synergy/for_publication/"}

    for pippo in products:
        if pippo in ['prw', 'q', 'temp']:
            path_data[pippo] = path_data['clwvi']
        elif pippo in ['tb_sfc']:
            path_data[pippo] = path_data['tb']      
    
    for product in products:
        files = find_files_product(path_data, product, radiometers)

        improve_all_metadata(files, product)
        
        if product in ['tb', 'tb_sfc']:
            path_output_metadata = dict()
            metadata = dict()
            for radiometer in radiometers:
                files = find_files_product(path_data, product, [radiometer])
                metadata[radiometer] = generate_metadata_files(files, product)
                path_output_metadata[radiometer] = (os.environ['VAMPIRE_DATA'] + 
                                                    f"{radiometer}/for_publication/PANGAEA/")
        else:
            metadata = generate_metadata_files(files, product)
            path_output_metadata = (os.environ['VAMPIRE_DATA'] + "mwr_synergy/for_publication/PANGAEA/")
    
        save_metadata(metadata, path_output_metadata, product, radiometers)


def get_events(campaign: str):
    
    event_ids = dict()
    event_times = dict()
    if campaign == 'vampire':
        event_ids = {'hatpro': np.array(["PS144_0_Underway-14"]),
                     'mirac-p': np.array(["PS144_0_Underway-16"])}
        event_times = {'hatpro': np.array([[np.datetime64("2024-08-09T08:00:00"),np.datetime64("2024-10-08T09:00:00")]]),
                       'mirac-p': np.array([[np.datetime64("2024-08-09T08:00:00"), np.datetime64("2024-10-08T12:08:45")]])}
    elif campaign == 'VAMPIRE2':
        event_ids = {'hatpro': np.array(["PS149_0-HATPRO_ICEHAT-01",
                                         "PS149_0-HATPRO_ICEHAT-02",
                                         "PS149_0-HATPRO_ICEHAT-03",
                                         "PS149_0-HATPRO_ICEHAT-04",
                                         "PS149_0-HATPRO_ICEHAT-05",
                                         "PS149_0-HATPRO_ICEHAT-06",
                                         "PS149_0-HATPRO_ICEHAT-07",
                                         "PS149_0-HATPRO_ICEHAT-08",
                                         "PS149_0-HATPRO_ICEHAT-09",
                                         "PS149_0-HATPRO_ICEHAT-10",
                                         "PS149_0-HATPRO_ICEHAT-11",
                                         "PS149_0-HATPRO_ICEHAT-12",
                                         "PS149_0-HATPRO_ICEHAT-13",
                                         "PS149_0-HATPRO_ICEHAT-14",
                                         "PS149_0-HATPRO_ICEHAT-15",
                                         "PS149_0-HATPRO_ICEHAT-16",
                                         "PS149_0-HATPRO_ICEHAT-17",
                                         "PS149_0-HATPRO_ICEHAT-18",
                                         ]),
                     'mirac-p': np.array(["PS149_0-MiRAC-P-01",
                                          "PS149_0-MiRAC-P-02",
                                          "PS149_0-MiRAC-P-03",
                                          "PS149_0-MiRAC-P-04",
                                          "PS149_0-MiRAC-P-05",
                                          "PS149_0-MiRAC-P-06",
                                          "PS149_0-MiRAC-P-07",
                                          "PS149_0-MiRAC-P-08",
                                          "PS149_0-MiRAC-P-09",
                                          "PS149_0-MiRAC-P-10",
                                          "PS149_0-MiRAC-P-11",
                                          "PS149_0-MiRAC-P-12",
                                          "PS149_0-MiRAC-P-13",
                                          "PS149_0-MiRAC-P-14",
                                          "PS149_0-MiRAC-P-15",
                                          "PS149_0-MiRAC-P-16",
                                          "PS149_0-MiRAC-P-17",
                                          "PS149_0-MiRAC-P-18",
                                          "PS149_0-MiRAC-P-19",
                                          "PS149_0-MiRAC-P-20",
                                          "PS149_0-MiRAC-P-21",
                                          ])}
        event_times = {'hatpro': np.array([[np.datetime64("2025-07-04T18:01:58"),np.datetime64("2025-07-06T08:00:29")],
                                           [np.datetime64("2025-07-06T08:03:00"),np.datetime64("2025-07-22T19:31:00")],
                                           [np.datetime64("2025-07-22T19:31:00"),np.datetime64("2025-07-22T19:31:00")],
                                           [np.datetime64("2025-07-23T11:30:00"),np.datetime64("2025-07-31T18:05:00")],
                                           [np.datetime64("2025-07-31T18:02:09"),np.datetime64("2025-07-31T18:02:09")],
                                           [np.datetime64("2025-08-02T11:34:00"),np.datetime64("2025-08-02T12:39:00")],
                                           [np.datetime64("2025-08-02T12:45:00"),np.datetime64("2025-08-02T12:52:00")],
                                           [np.datetime64("2025-08-02T12:54:00"),np.datetime64("2025-08-03T10:08:13")],
                                           [np.datetime64("2025-08-03T09:54:00"),np.datetime64("2025-08-03T16:44:00")],
                                           [np.datetime64("2025-08-03T16:44:00"),np.datetime64("2025-08-06T15:42:28")],
                                           [np.datetime64("2025-08-06T15:42:28"),np.datetime64("2025-08-06T16:28:21")],
                                           [np.datetime64("2025-08-06T16:28:21"),np.datetime64("2025-08-06T16:29:34")],
                                           [np.datetime64("2025-08-06T19:13:12"),np.datetime64("2025-08-06T19:35:06")],
                                           [np.datetime64("2025-08-06T19:36:00"),np.datetime64("2025-08-14T17:26:50")],
                                           [np.datetime64("2025-08-14T17:26:50"),np.datetime64("2025-08-14T17:32:52")],
                                           [np.datetime64("2025-08-14T17:32:52"),np.datetime64("2025-08-24T15:33:52")],
                                           [np.datetime64("2025-08-24T15:34:19"),np.datetime64("2025-08-24T16:19:50")],
                                           [np.datetime64("2025-08-24T16:30:00"),np.datetime64("2025-08-29T12:00:00")],
                                           ]),
                       'mirac-p': np.array([[np.datetime64("2025-07-04T06:55:33"), np.datetime64("2025-07-06T08:00:41")],
                                            [np.datetime64("2025-07-06T08:03:00"), np.datetime64("2025-07-31T11:21:00")],
                                            [np.datetime64("2025-07-31T11:21:00"), np.datetime64("2025-08-02T10:03:00")],
                                            [np.datetime64("2025-08-02T10:03:00"), np.datetime64("2025-08-02T10:18:00")],
                                            [np.datetime64("2025-08-02T10:18:00"), np.datetime64("2025-08-02T11:22:00")],
                                            [np.datetime64("2025-08-02T11:22:00"), np.datetime64("2025-08-02T11:32:00")],
                                            [np.datetime64("2025-08-02T11:32:00"), np.datetime64("2025-08-03T14:43:00")],
                                            [np.datetime64("2025-08-03T14:43:00"), np.datetime64("2025-08-03T15:35:00")],
                                            [np.datetime64("2025-08-03T15:35:00"), np.datetime64("2025-08-03T16:48:00")],
                                            [np.datetime64("2025-08-03T16:48:00"), np.datetime64("2025-08-03T16:58:00")],
                                            [np.datetime64("2025-08-03T16:58:00"), np.datetime64("2025-08-06T15:42:24")],
                                            [np.datetime64("2025-08-06T15:42:24"), np.datetime64("2025-08-06T16:52:08")],
                                            [np.datetime64("2025-08-06T16:52:08"), np.datetime64("2025-08-06T16:53:36")],
                                            [np.datetime64("2025-08-06T16:53:36"), np.datetime64("2025-08-06T17:05:04")],
                                            [np.datetime64("2025-08-06T17:05:04"), np.datetime64("2025-08-06T17:06:10")],
                                            [np.datetime64("2025-08-06T19:13:24"), np.datetime64("2025-08-06T19:34:57")],
                                            [np.datetime64("2025-08-06T19:36:00"), np.datetime64("2025-08-14T17:26:50")],
                                            [np.datetime64("2025-08-14T17:26:50"), np.datetime64("2025-08-14T17:32:52")],
                                            [np.datetime64("2025-08-14T17:32:52"), np.datetime64("2025-08-24T15:34:22")],
                                            [np.datetime64("2025-08-24T15:34:36"), np.datetime64("2025-08-24T16:19:41")],
                                            [np.datetime64("2025-08-24T16:30:00"), np.datetime64("2025-08-29T12:00:00")],
                                            ])}
    
    return event_ids, event_times


def find_files_product(path: dict, product: str, radiometers: list):
    
    path_product = path[product]
    if product in ['tb', 'tb_sfc']:
        files = list()
        for rr in radiometers:
            files.extend(sorted(glob.glob(path_product[rr] + f"{Constants.CAMPAIGN_NAME}_uoc_{instrument_file_label[rr]}_l1_{product}_v01_*.nc")))
    else:
        files = sorted(glob.glob(path_product + f"{Constants.CAMPAIGN_NAME}*_{product}_v01_*.nc"))
    
    return files


def improve_all_metadata(files: list, product: str):
    
    for file in files:
        ds = xr.open_dataset(file)
        
        ds = correct_metadata(ds, product)
        ds = remove_unused_data_vars(ds)
        
        path_output = (ds.encoding['source'].replace(os.path.basename(ds.encoding['source']), "") +
                        "PANGAEA/")
        export_DS(ds, path_output)


def correct_metadata(DS: xr.Dataset, product: str):

    DS.attrs = {key.lower() if key != 'Conventions' else key: val for key, val in DS.attrs.items()}

    DS.attrs['measurement_site'] = "Arctic Ocean, RV Polarstern"
    for time_var, idx in zip(['time_start', 'time_end'], [0,-1]):
        DS.attrs[time_var] = str(DS.time.values[idx].astype('datetime64[s]')).replace('T', ' ') + "Z"
    
    DS.attrs['Conventions'] = "CF-1.13"
    DS.attrs['licence'] = "CC BY-NC 4.0, https://creativecommons.org/licenses/by-nc/4.0/"
    if 'position_source' in DS.attrs.keys(): 
        DS.attrs['references'] = "lat, lon data source: " + DS.attrs['position_source']
        del DS.attrs['position_source']
    
    if "mwrpro-v04" in DS.attrs['history']:
        DS.attrs['references'] += ("; mwrpro-v04: Löhnert, U. et al. 2023: Ground-based microwave radiometer " +
                                   "reprocessing mwr_pro, Zenodo, https://doi.org/10.5281/zenodo.7973553")
    
    if 'license' in DS.attrs.keys(): del DS.attrs['license']
    
    DS.attrs['contact_person'] = "Andreas Walbroel (a.walbroel@uni-koeln.de, https://orcid.org/0000-0003-2603-2724)"
    DS.attrs = {'contact' if key == 'contact_person' else key: val for key, val in DS.attrs.items()}
    
    if campaign == "vampire":
        if product in ['tb', 'tb_sfc']:
            DS.attrs['author'] = "Andreas Walbroel, Janna Rueckert, Linnu Buehler, Nils Risse, Pavel Krobot, Mario Mech"
        else:
            DS.attrs['author'] = "Andreas Walbroel, Mario Mech"
    elif campaign == "VAMPIRE2":
        if product == "tb":
            DS.attrs['author'] = "Andreas Walbroel, Linnu Buehler, Pavel Krobot, Mario Mech"
        elif product == 'tb_sfc':
            DS.attrs['author'] = "Andreas Walbroel, Janna Rueckert, Linnu Buehler, Pavel Krobot, Mario Mech"
        else:
            DS.attrs['author'] = "Andreas Walbroel, Mario Mech"
    
    if ('comments' in DS.attrs.keys()) and (len(DS.attrs['comments']) <= 1):
        del DS.attrs['comments']
    DS.attrs['project'] = ("DFG (German Research Foundation) project number 268020496 - TRR 172, Transregional " +
                           "Collaborative Research Center 'ArctiC Amplification: Climate Relevant Atmospheric " +
                           "and SurfaCe Processes, and Feedback Mechanisms (AC)3")
    
    if 'dependencies' in DS.attrs.keys(): del DS.attrs['dependencies']
    
    if product == 'clwvi': 
        DS.attrs['title'] = DS.attrs['title'].replace(
            "atmosphere_mass_content_of_cloud_liquid_water_content",
            "atmosphere_mass_content_of_cloud_liquid_water")
        
        DS['clwvi'].attrs['standard_name'] = "atmosphere_mass_content_of_cloud_liquid_water"
        DS['clwvi_err'].attrs['standard_name'] = "atmosphere_mass_content_of_cloud_liquid_water standard_error"
        for var in ['clwvi_offset_zeroing', 'clwvi_offset']:
            DS[var].attrs['long_name'] = DS[var].attrs['long_name'].replace(
                "atmosphere_mass_content_of_cloud_liquid_water_content", "atmosphere_mass_content_of_cloud_liquid_water"
                )
            
    if product == 'tb':
        DS['flag_bl'].attrs['flag_values'] = np.array([0,1,2], dtype=np.short)
        DS['flag_bl'].attrs['flag_meanings'] = f"not_bl_scan default_bl_scan manually_designed_bl_scan_{Constants.CAMPAIGN_NAME}"
        DS['flag_bl'].attrs['comment'] = "default_bl_scan: instrument standard used e.g., during transit"
        
    if product == 'temp':
        DS['flag_usage'].attrs['flag_meanings'] = ("use_temp use_temp_zen")
        DS['flag_usage'].attrs['flag_values'] = np.array([0, 1], dtype=np.short)
    
    return DS


def remove_unused_data_vars(DS: xr.Dataset):
    
    vars_to_remove = ['clwvi_off_zenith', 'clwvi_off_zenith_offset', 'azi']
    for var in vars_to_remove:
        if var in DS.data_vars:
            DS = DS.drop_vars(var)
    
    return DS


def export_DS(DS: xr.Dataset, path_output: str):
    
    os.makedirs(path_output, exist_ok=True)
    
    DS = update_netCDF_file_history(DS, script_name,
                                    summary_str="improved metadata")
    DS = encode_time(DS, reference_period=np.datetime64("2024-01-01T00:00:00"))
    
    
    vars_fill_value = ['lat', 'lon', 'zsl', 'tb', 'ta', 'pa', 'hur', 'nadir', 'zen', 'ele',
                       'azi', 'ele_ret', 'clwvi', 'clwvi_offset_zeroing', 'clwvi_offset',
                       'clwvi_err', 'prw', 'prw_rmse', 'q', 'q_rmse', 'temp_rmse', 'temp',
                       'temp_bl_rmse', 'temp_bl', 'temp_zen_rmse', 'temp_zen']
    vars_remove_fill_value = ['time', 'flag', 'freq_sb', 'tb_bias_estimate', 'freq_shift',
                              'tb_absolute_accuracy', 'flag_bl', 'flag_h', 'flag_m', 'height',
                              'flag_usage']
    for ds_var in DS.variables:
        if ds_var in vars_fill_value:
            DS[ds_var].encoding['_FillValue'] = float(-9999.)
        elif ds_var in vars_remove_fill_value:
            DS[ds_var].encoding['_FillValue'] = None
    
    filename = os.path.basename(DS.encoding['source'])
    outfile = path_output + filename
    
    DS.to_netcdf(outfile, mode='w', format="NETCDF4")
    DS = DS.close()
    print(f"Saved {outfile}....")


def generate_metadata_files(files: list, product: str):
    
    metadata = {key: list() for key in ['event', 'filename', 'start_time', 
                                        'start_lat', 'start_lon', 'end_time',
                                        'end_lat', 'end_lon']}
    for file in files:
        metadata = extract_metadata(metadata, file, product)
    
    return metadata


def extract_metadata(metadata: dict, file: str, product: str):
    
    ds = xr.open_dataset(file)
    
    radiometer = ""
    if ((product in ['tb', 'tb_sfc']) and ("/hatpro/" in file)) or (product == 'clwvi'):
        radiometer = "hatpro"
    elif product in ['tb', 'tb_sfc'] and ("/mirac-p/" in file):
        radiometer = "mirac-p"
    elif product in ['prw', 'q', 'temp']:
        radiometer = ['hatpro', 'mirac-p']

    events_for_file = get_event_for_daily_data(ds, radiometer)
    
    start_end_lat, start_end_lon = extract_lat_lon(ds)
    
    metadata['event'].append(events_for_file)
    metadata['filename'].append(os.path.basename(file))
    metadata['start_time'].append(str(ds.time.values[0].astype('datetime64[s]')))
    metadata['start_lat'].append(f"{start_end_lat[0]:.5f}")
    metadata['start_lon'].append(f"{start_end_lon[0]:.5f}")
    metadata['end_time'].append(str(ds.time.values[-1].astype('datetime64[s]')))
    metadata['end_lat'].append(f"{start_end_lat[-1]:.5f}")
    metadata['end_lon'].append(f"{start_end_lon[-1]:.5f}")
    
    ds = ds.close()
    
    return metadata


def extract_lat_lon(ds: xr.Dataset):
    
    start_end_lat_lon = dict()
    nonnan_idx = {key: np.where(~np.isnan(ds[key]))[0] for key in ['lat', 'lon']}
    for key in ['lat', 'lon']:
        start_end_lat_lon[key] = np.array([ds[key].values[nonnan_idx[key][0]],
                                           ds[key].values[nonnan_idx[key][-1]]])
    
    return start_end_lat_lon['lat'], start_end_lat_lon['lon']


def get_event_for_daily_data(DS: xr.Dataset, radiometer: str):
    
    event_list = list()
    if isinstance(radiometer, list):
        for rm in radiometer:
            event_list.extend(get_event_for_daily_data_radiometer(DS, rm))
            
    else:
        event_list = get_event_for_daily_data_radiometer(DS, radiometer)
    
    event = ",".join(event_list)
    
    return event


def get_event_for_daily_data_radiometer(DS: xr.Dataset, radiometer: str):
    
    e_ids_r = event_ids[radiometer]
    e_times_r = event_times[radiometer]
    
    start_time = DS.time.values[0]
    end_time = DS.time.values[-1]
    
    idx_include = np.where(~((end_time < e_times_r[:,0]) | (start_time > e_times_r[:,1])))[0]
    event = e_ids_r[idx_include].tolist()
    
    return event


def save_metadata(metadata, path_output, product: str, radiometers: list):
    
    if product in ['tb', 'tb_sfc']:
        for radiometer in radiometers:
            save_metadata_file(metadata[radiometer], path_output[radiometer], product, radiometer)
            
    else:
        save_metadata_file(metadata, path_output, product)


def save_metadata_file(
    metadata: dict, 
    path_output: str, 
    product: str, 
    radiometer=None):
    
    if radiometer is None: 
        mwr_label = "_".join(instrument_file_label.values())
    else:
        mwr_label = instrument_file_label[radiometer]
    
    os.makedirs(path_output, exist_ok=True)
    
    metadata_txt = list()
    metadata_vars = metadata.keys()
    for idx, event in enumerate(metadata['event']):
        metadata_txt.append([metadata[key][idx] for key in metadata_vars])
    
    metadata_header = [key for key in metadata_vars]
    
    filename = f"metadata_{Constants.CAMPAIGN_NAME}_uoc_{mwr_label}_{product}_v01"
    outfile = path_output + filename + ".txt"
    with open(outfile, "w") as f:
        f.write('\t'.join(metadata_header) + "\n")
        f.writelines('\t'.join(txt_row) + "\n" for txt_row in metadata_txt)
    
    print(f"Saved {outfile}....")


if __name__ == '__main__':
    
    campaign = "VAMPIRE2"
    if campaign == "vampire":
        from vampire.constants import Constants as Constants
    elif campaign == 'VAMPIRE2':
        from vampire.constants import Constants_PS149 as Constants

    script_name = os.path.basename(__file__)
    instrument_file_label = {'hatpro': "hatpro",
                            'mirac-p': "lhumpro-243-340"}
    
    event_ids, event_times = get_events(campaign)  
    
    main()