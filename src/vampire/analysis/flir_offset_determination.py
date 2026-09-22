import os
import sys
import pdb

import xarray as xr
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib as mpl
import matplotlib.pyplot as plt

from vampire.io.readers.flir import read_flir_statistics
from vampire.quicklooks.flir import (flir_image, get_flir_image, plot_flir_image)
from vampire.quicklooks.gopro import gopro_image
from vampire.io.readers.gopro import get_gopro_rescaled_file_data_campaigns
from vampire.io.readers.ir_targets import read_ir_target_temp_data, event_start_end_times
from vampire.analysis.data_tools import(write_basic_attributes,
                                        update_netCDF_file_history,
                                        encode_time,
                                        get_temporal_overlap)


def main():
    
    path_output = os.environ['VAMPIRE_DATA'] + "flir/offset_correction/"
    path_plots = os.environ['PATH_PLOTS'] + "flir/offset_correction/"
    visualise = False
    set_dict = {'save_figures': False,
                'path_plots': path_plots}
    
    dates_icestation = get_icestation_datetimes(Constants.CAMPAIGN_NAME)
    
    surface_temp_ds = get_insitu_surface_temp(Constants.CAMPAIGN_NAME)
    surface_temp_ds = add_flir_TBs(surface_temp_ds, dates_icestation, Constants.CAMPAIGN_NAME)
    
    dates_icestation = visual_inspection_conditions_ice_stations(dates_icestation)
    surface_temp_ds = surface_temp_ds.sel(time=dates_icestation)
    
    assumptions = flir_tb_correction_assumptions(dates_icestation, 
                                                 campaign_name=Constants.CAMPAIGN_NAME, 
                                                 ref_surface='sea_ice')
    mean_ratio, bias, mean_bias, ratio_average = get_surface_temp_differences_flir_insitu(surface_temp_ds,
                                                                                          assumptions)
    
    d_tb_flir, d_emissivity, d_tb_atm, d_temp_skin_insitu = flir_correction_insitu_stds(surface_temp_ds)
    bias_uncertainty = bias_error_propagation(surface_temp_ds.temp_groundtruth.values,
                                              assumptions['tb_atm'],
                                              assumptions['emissivity'],
                                              d_tb_flir,
                                              d_temp_skin_insitu,
                                              d_tb_atm, 
                                              d_emissivity)
    
    ir_bias, ir_bias_uncertainty = None, None
    FLIR_IR_TB, IR_TEMP = None, None
    if Constants.CAMPAIGN_NAME == "PS149":
        ir_bias, ir_bias_uncertainty, FLIR_IR_TB, IR_TEMP = flir_offset_corr_ir_targets()
    
    if visualise:
        visualise_sfc_temp_flir_insitu(surface_temp_ds, dates_icestation, assumptions, bias, **set_dict)
    
    offset_ds = generate_temp_offset_dataset(surface_temp_ds, 
                                             dates_icestation,
                                             assumptions,
                                             bias,
                                             bias_uncertainty,
                                             ir_bias,
                                             ir_bias_uncertainty,
                                             FLIR_IR_TB,
                                             IR_TEMP)
    
    export_offset_ds(offset_ds, path_output, campaign_name=Constants.CAMPAIGN_NAME)
    
    
def get_icestation_datetimes(campaign_name: str):
    
    if campaign_name == "PS144":
        dates_icestation = pd.to_datetime(Constants.TIME_ICE_STATION).tolist()
    elif campaign_name == "PS149":
        dates_icestation = pd.to_datetime(Constants.TIME_ICE_SAMPLING).to_list()
    
    return dates_icestation


def get_insitu_surface_temp(campaign_name: str):
    
    ice_station_times = get_icestation_datetimes(campaign_name)
    surface_temp_ds = xr.Dataset(coords={'time': (['time'], 
                                                  np.array(ice_station_times).astype('datetime64[ns]'))})
    n_time = len(surface_temp_ds.time)
    for var in ['temp_groundtruth', 'temp_groundtruth_mean', 'temp_groundtruth_std', 
                'tb_flir_center', 'tb_flir_mean', 'tb_flir_std']:
        surface_temp_ds[var] = xr.DataArray(np.full((n_time,), np.nan), dims=['time'])

    if campaign_name == "PS144":

        surface_temp_ds["temp_groundtruth"][:] = np.array([
            -0.1, 
            -0.5, 
            -2.6,
            -3.2,
            -7.6,
            -2.5,
            -6.7,
            -10.2,
            -9,
            -13.2,
            -8.9]) + 273.15 ##until datetime(2024,9,19,13,40)
        surface_temp_ds["temp_groundtruth_mean"][:] = np.array([
            -0.1, 
            np.mean([-0.4,-0.5,-0.4,-0.3,-0.3,-0.3,-0.4,-0.4,-0.4,-0.4,-0.4,-0.4,-0.4,-0.4]),
            np.mean([-2.6,-2.7,-2.7,-2.9,-3,-2.9]),
            -3.2,
            np.mean([-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-6.,-7.,-7.5]),
            np.mean([-2,-2,-2.2,-2,-2.2,-2.5,-2.3,-2.3,-2.5,-2.6]),
            np.mean([-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.8]),
            np.mean([-12.1,-12.5,-12.2,-12.4,-11.7,-12,-10.8,-11.7,-12,-11,-12,-11.9,-12.6]),
            np.mean([-9.2,-9,-9.2,-9.1]),
            np.mean([-13,-13.3,-13.3,-13.3,-13.2,-13.2,-13.2,-13.2,-13.2,-13.2,-13.2]),
            np.mean([-9.7,-9.6,-9.5,-9.8,-9.7,-9.5,-9.6,-9.4,-9.5,-9.3,-9.3,-9.3])]) + 273.15
        surface_temp_ds["temp_groundtruth_std"][:] = np.array([
            np.nan,
            np.std([-0.4,-0.5,-0.4,-0.3,-0.3,-0.3,-0.4,-0.4,-0.4,-0.4,-0.4,-0.4,-0.4,-0.4]),
            np.std([-2.6,-2.7,-2.7,-2.9,-3,-2.9]),
            np.nan,
            np.std([-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-7.,-6.,-7.,-7.5]),
            np.std([-2,-2,-2.2,-2,-2.2,-2.5,-2.3,-2.3,-2.5,-2.6]),
            np.std([-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.,-6.8]),
            np.std([-12.1,-12.5,-12.2,-12.4,-11.7,-12,-10.8,-11.7,-12,-11,-12,-11.9,-12.6]),
            np.std([-9.2,-9,-9.2,-9.1]),
            np.std([-13,-13.3,-13.3,-13.3,-13.2,-13.2,-13.2,-13.2,-13.2,-13.2,-13.2]),
            np.std([-9.7,-9.6,-9.5,-9.8,-9.7,-9.5,-9.6,-9.4,-9.5,-9.3,-9.3,-9.3])])
        
    elif campaign_name == "PS149":
        surface_temp_ds["temp_groundtruth"][:] = np.array([
            -0.1,   # 1a, day 1
            -0.2,
            0.1,
            -0.1,   # 2a, day 1
            0.0,
            0.0,
            0.1,    # 3a, day 1
            -1.0,
            -0.2,
            0.0,    # 1b, day 1
            0.0,
            -0.1,
            -0.3,   # 2b, day 1
            -0.1,
            0.0,
            np.median(np.array([-0.1,0.2,0.,0.,0.2,0.])),    # 3b, day 1
            -0.1,
            0.0,    # not in MWR footprint, but several meters towards bow of ship
            0.2,    # 1c, day 1
            0.1,
            np.nan,   # 2c, day 1; deleted values because never in MWR or FLIR footprint
            np.nan,
            np.nan,
            0.0,    # 3c, day 1
            0.0,
            0.2,
            -0.9,   # 2d, day 1
            np.nan,     # deleted value because not in MWR footprint
            0.1,    # 3d, day 1
            0.0,
            ]) + 273.15 ##until datetime(2024,9,19,13,40)
        surface_temp_ds["temp_groundtruth_mean"][:] = np.array([
            -0.1, 
            -0.2,
            0.1,
            np.mean(np.array([-0.1,-0.1,-0.1,-0.1,-0.2])),
            np.mean(np.array([0.,-0.1,-0.2,-0.1,-0.1])),
            np.mean(np.array([-0.1,0.,0.,0.1,0.2])),
            np.mean(np.array([0.,0.,0.,0.,0.])),
            np.mean(np.array([-0.6,-0.9,-1.0,-0.9,-0.8])),
            np.mean(np.array([0.,-0.1,-0.7,0.,0.1,-0.1,0.4,0.,0.])),
            np.mean(np.array([-0.1,0.,-0.1,-0.1,0.,0.])),
            np.mean(np.array([0.1,0.,0.,0.,0.,0.,-0.1,0.])),
            np.mean(np.array([-0.1,-0.1,-0.1,-0.1,-0.1,0.,-0.1,-0.1,-0.1])),
            np.mean(np.array([-0.5,-0.3,-0.2,-0.3,-0.2,-0.2])),
            np.mean(np.array([0.,0.,-0.1,-0.1,-0.1,-0.1,-0.1])),
            np.mean(np.array([0.2,0.3,0.,0.,0.,0.])),
            np.mean(np.array([-0.1,0.2,0.,0.,0.2,0.])),     # in MWR footprint, not at coring site
            np.mean(np.array([0.,-0.1,-0.1,-0.1,-0.1,0.,-0.1,-0.1])),
            np.mean(np.array([0.,0.,0.,0.,0.,0.,0.])),
            np.mean(np.array([0.3,0.1,0.1,0.2,0.,0.2])),
            np.mean(np.array([0.2,0.2,0.,0.2,0.,0.1])),
            np.nan,
            np.nan,
            np.nan,
            np.mean(np.array([0.,0.,0.,0.,0.,-0.1,0.])),
            np.mean(np.array([0.,0.,0.,0.,0.,-0.1,0.,-0.1])),
            np.mean(np.array([0.3,0.1,0.4,0.2,0.35,0.1])),
            -0.9,
            np.nan,
            np.mean(np.array([0.1,-0.1,0.3,0.3,-0.1,0.2,0.2])),
            np.mean(np.array([0.2,0.1,0.,-0.1,-0.1,-0.1,0.,0.,0.])),
            ]) + 273.15
        surface_temp_ds["temp_groundtruth_std"][:] = np.array([
            np.nan,
            np.nan,
            np.nan,
            np.std(np.array([-0.1,-0.1,-0.1,-0.1,-0.2])),
            np.std(np.array([0.,-0.1,-0.2,-0.1,-0.1])),
            np.std(np.array([-0.1,0.,0.,0.1,0.2])),
            np.std(np.array([0.,0.,0.,0.,0.])),
            np.std(np.array([-0.6,-0.9,-1.0,-0.9,-0.8])),
            np.std(np.array([0.,-0.1,-0.7,0.,0.1,-0.1,0.4,0.,0.])),
            np.std(np.array([-0.1,0.,-0.1,-0.1,0.,0.])),
            np.std(np.array([0.1,0.,0.,0.,0.,0.,-0.1,0.])),
            np.std(np.array([-0.1,-0.1,-0.1,-0.1,-0.1,0.,-0.1,-0.1,-0.1])),
            np.std(np.array([-0.5,-0.3,-0.2,-0.3,-0.2,-0.2])),
            np.std(np.array([0.,0.,-0.1,-0.1,-0.1,-0.1,-0.1])),
            np.std(np.array([0.2,0.3,0.,0.,0.,0.])),
            np.std(np.array([-0.1,0.2,0.,0.,0.2,0.])),     # in MWR footprint, not at coring site
            np.std(np.array([0.,-0.1,-0.1,-0.1,-0.1,0.,-0.1,-0.1])),
            np.std(np.array([0.,0.,0.,0.,0.,0.,0.])),
            np.std(np.array([0.3,0.1,0.1,0.2,0.,0.2])),
            np.std(np.array([0.2,0.2,0.,0.2,0.,0.1])),
            np.nan,
            np.nan,
            np.nan,
            np.std(np.array([0.,0.,0.,0.,0.,-0.1,0.])),
            np.std(np.array([0.,0.,0.,0.,0.,-0.1,0.,-0.1])),
            np.std(np.array([0.3,0.1,0.4,0.2,0.35,0.1])),
            np.nan,
            np.nan,
            np.std(np.array([0.1,-0.1,0.3,0.3,-0.1,0.2,0.2])),
            np.std(np.array([0.2,0.1,0.,-0.1,-0.1,-0.1,0.,0.,0.])),
            ])
        
    return surface_temp_ds


def add_flir_TBs(surface_temp_ds: xr.Dataset, dates_icestation: list, campaign_name: str):
    
    """
    Load FLIR data. It actually measures surface temperatures but in the settings, the assumed
    emissivity is 1.0. Thus, the FLIR data can be seen as brightness temperatures (TBs).
    """
    
    campaign_name_long = "VAMPIRE"
    if campaign_name == "PS149":
        campaign_name_long = "VAMPIRE2"
    
    path_flir = os.environ['VAMPIRE_DATA'] + "flir/time_series/"
    for k, time in enumerate(dates_icestation):
        flir_ds = xr.open_dataset(f"{path_flir}{campaign_name_long}_flir_statistics_{time:%Y%m%d}.nc")
        index_colloc = np.argmin(np.array(abs((pd.to_datetime(flir_ds.time.values) - time))))
        tb = flir_ds.tb_center.values[index_colloc]
        tb_mean = flir_ds.tb_mean.values[index_colloc]
        tb_std = flir_ds.tb_std.values[index_colloc]

        flir_ds = flir_ds.close()
        surface_temp_ds["tb_flir_center"][k] = tb
        surface_temp_ds["tb_flir_mean"][k] = tb_mean
        surface_temp_ds["tb_flir_std"][k] = tb_std
    
    return surface_temp_ds


def flir_tb_correction_assumptions(
    dates_icestation=list(), 
    campaign_name="PS144",
    ref_surface='sea_ice'):
    
    """
    For a non-perfect emitting surface, the contribution of the reflected downwelling atmospheric
    radiation must be taken into account.
    
    Parameters:
    -----------
    dates_icestation : list
        List of pd.Timestamps of ice station times.
    campaign_name : str
        Name of the Polarstern cruise for VAMPIRE-1 ('PS144') or VAMPIRE-2 ('PS149').
    ref_surface : str
        Label to indicate whether the reference surface temperature is sea ice ('sea_ice') or
        a reference infrared target ('ir_target').
    """
    
    emissivity = {'ir_target': 0.98     # see e-mail by Michi Haugeneder, 2025-11-21
                  }
    assumptions = dict()
    
    # thermal-infrared emissivity of snow for incidence angle of around 53 deg
    emissivity_fresh_snow = 0.996   # Thielke et al., 2022, https://doi.org/10.1038/s41597-022-01461-9;
                                    # Fig. 8 and 9 in Nalliet al., 2023, https://doi.org/10.3390/rs15235509
    emissivity_old_snow = 0.985     # Fig. 8 and 9 in Nalliet al., 2023, https://doi.org/10.3390/rs15235509;
                                    # Cox et al., 2023, https://doi.org/10.1038/s41597-023-02415-5
    tb_atm_cloudy = 273.15          # assumed downwelling brightness temperature for cloudy conditions in K
    tb_atm_clear_sky = 205.         # assumed downwelling brightness temperature for clear-sky conditions in K,
                                    # see Smith and Tuomi, 2008, https://doi.org/10.1175/2007JAMC1615.1
    
    if campaign_name == 'PS144':
        assumptions['tb_atm'] = np.array([tb_atm_cloudy,    # 2024-08-16 15:45:00
                                          tb_atm_cloudy,    # 2024-08-29 17:15:00
                                          tb_atm_cloudy,    # 2024-09-02 21:05:00
                                          tb_atm_cloudy,    # 2024-09-05 06:50:00
                                          0.5*(tb_atm_cloudy + tb_atm_clear_sky), # 2024-09-08 08:30:00
                                          tb_atm_cloudy,    # 2024-09-10 21:40:00
                                          tb_atm_clear_sky, # 2024-09-13 08:15:00
                                          tb_atm_clear_sky, # 2024-09-18 21:50:00
                                          tb_atm_cloudy,    # 2024-09-19 13:40:00
                                          tb_atm_clear_sky, # 2024-09-23 06:45:00
                                          0.5*(tb_atm_clear_sky + tb_atm_cloudy), # 2024-09-26 00:00:00
                                          ])
        emissivity['sea_ice'] = np.array([emissivity_old_snow,      # 2024-08-16 15:45:00
                                          emissivity_old_snow,      # 2024-08-29 17:15:00
                                          emissivity_fresh_snow,    # 2024-09-02 21:05:00
                                          emissivity_fresh_snow,    # 2024-09-05 06:50:00
                                          emissivity_fresh_snow,    # 2024-09-08 08:30:00
                                          emissivity_fresh_snow,    # 2024-09-10 21:40:00
                                          emissivity_fresh_snow,    # 2024-09-13 08:15:00
                                          emissivity_fresh_snow,    # 2024-09-18 21:50:00
                                          emissivity_fresh_snow,    # 2024-09-19 13:40:00
                                          emissivity_fresh_snow,    # 2024-09-23 06:45:00
                                          emissivity_fresh_snow,    # 2024-09-26 00:00:00
                                          ])
        
    elif campaign_name == 'PS149':
        if ref_surface == 'sea_ice':
            assumptions['tb_atm'] = np.array([tb_atm_cloudy,    # 2025-07-09 17:38:00
                                              tb_atm_cloudy,    # 2025-07-10 12:40:00
                                              tb_atm_cloudy,    # 2025-07-16 12:40:00
                                              tb_atm_cloudy,    # 2025-07-17 08:52:00
                                              tb_atm_cloudy,    # 2025-07-20 12:45:00
                                              tb_atm_cloudy,    # 2025-07-27 12:32:00
                                              tb_atm_cloudy,    # 2025-07-30 12:53:00
                                              tb_atm_cloudy,    # 2025-08-05 12:33:00
                                              tb_atm_cloudy,    # 2025-08-13 12:31:00
                                              tb_atm_cloudy,    # 2025-08-16 20:35:00
                                              tb_atm_cloudy,    # 2025-08-17 12:32:00
                                              tb_atm_cloudy,    # 2025-08-24 12:31:00
                                              0.5*(tb_atm_clear_sky + tb_atm_cloudy), # 2025-08-26 12:32:00
                                              0.5*(tb_atm_clear_sky + tb_atm_cloudy), # 2025-08-27 12:32:00
                                              ])
        elif ref_surface == 'ir_target':
            assumptions['tb_atm'] = np.array([
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_clear_sky, tb_atm_clear_sky, tb_atm_clear_sky, tb_atm_clear_sky,
                tb_atm_clear_sky, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, 0.5*(tb_atm_clear_sky + tb_atm_cloudy),
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy, tb_atm_cloudy,
                tb_atm_cloudy])
        emissivity['sea_ice'] = np.array([emissivity_old_snow,      # 2025-07-09 17:38:00
                                          emissivity_old_snow,      # 2025-07-10 12:40:00
                                          emissivity_old_snow,      # 2025-07-16 12:40:00
                                          emissivity_old_snow,      # 2025-07-17 08:52:00
                                          emissivity_old_snow,      # 2025-07-20 12:45:00
                                          emissivity_old_snow,      # 2025-07-27 12:32:00
                                          emissivity_old_snow,      # 2025-07-30 12:53:00
                                          emissivity_old_snow,      # 2025-08-05 12:33:00
                                          emissivity_old_snow,      # 2025-08-13 12:31:00
                                          emissivity_old_snow,      # 2025-08-16 20:35:00
                                          emissivity_old_snow,      # 2025-08-17 12:32:00
                                          emissivity_fresh_snow,    # 2025-08-24 12:31:00
                                          emissivity_old_snow,      # 2025-08-26 12:32:00
                                          emissivity_old_snow,      # 2025-08-27 12:32:00
                                          ])
    
    if ref_surface == 'sea_ice': 
        assert len(emissivity['sea_ice']) == len(dates_icestation)
        assert len(dates_icestation) == len(assumptions['tb_atm'])
    
    assumptions['emissivity'] = emissivity[ref_surface]
    
    return assumptions


def get_surface_temp_differences_flir_insitu(surface_temp_ds: xr.Dataset, assumptions: dict):
    
    mean_ratio = ratio_correction(surface_temp_ds['tb_flir_center'].values, 
                                  surface_temp_ds['temp_groundtruth'].values,
                                  emissivity=assumptions['emissivity'],
                                  tb_atm=assumptions['tb_atm'])
    print("mean ratio:", mean_ratio)
    
    bias = bias_correction(surface_temp_ds['tb_flir_center'].values,
                           surface_temp_ds['temp_groundtruth'].values,
                           emissivity=assumptions['emissivity'],
                           tb_atm=assumptions['tb_atm'])
    print("mean diff flir-insitu", bias)
    
    mean_bias = bias_correction(surface_temp_ds["tb_flir_mean"].values,
                                surface_temp_ds["temp_groundtruth_mean"].values,
                                emissivity=assumptions['emissivity'],
                                tb_atm=assumptions['tb_atm'])
    print("mean diff flir-insitu mean", mean_bias)
    
    ratio_average = ratio_correction(surface_temp_ds["tb_flir_mean"].values,
                                     surface_temp_ds["temp_groundtruth_mean"].values,
                                     emissivity=assumptions['emissivity'],
                                     tb_atm=assumptions['tb_atm'])
    print("average ratio flir_mean/insitu_mean", ratio_average)
    
    return mean_ratio, bias, mean_bias, ratio_average


def flir_offset_corr_ir_targets():
    
    REF_DS = read_ir_target_temp_data()
    ir_target_starts, ir_target_ends = event_start_end_times()
    
    FLIR_TEMP_DS = get_flir_tb_at_targets(ir_target_starts, ir_target_ends)
    
    IR_TARGET_TEMP = xr.DataArray(np.full(FLIR_TEMP_DS.tb_mean.shape, np.nan), dims=['time'],
                                  coords=FLIR_TEMP_DS.tb_mean.coords)
    IR_TARGET_TEMP[:] = get_temporal_overlap(
        REF_DS.temp_mean, 
        time_bins=np.array([FLIR_TEMP_DS.time.values - np.timedelta64(60, "s"),
                            FLIR_TEMP_DS.time.values + np.timedelta64(60, "s")]).T
        )
    
    assumptions = flir_tb_correction_assumptions(campaign_name="PS149",
                                                 ref_surface='ir_target')
    
    bias = bias_correction(FLIR_TEMP_DS.tb_mean.values, IR_TARGET_TEMP.values,
                           emissivity=assumptions['emissivity'],
                           tb_atm=assumptions['tb_atm'])
    bias_uncertainty = bias_error_propagation(IR_TARGET_TEMP.values,
                                              assumptions['tb_atm'],
                                              assumptions['emissivity'],
                                              FLIR_TEMP_DS.tb_std.mean().item(),
                                              REF_DS.temp_std.mean().item(),
                                              np.std(np.array([205., 239.075, 273.15])),
                                              0.0)
    
    return bias, bias_uncertainty, FLIR_TEMP_DS.tb_mean, IR_TARGET_TEMP


def get_flir_tb_at_targets(start_times: dict, end_times: dict):
    
    """
    Manually read out the x,y position of the reference IR targets in FLIR images for each hour
    between IR target deployment and recovery.
    """
    
    FLIR_TEMP_DS = dict()
    for event in start_times.keys():
        start_time, end_time = start_times[event], end_times[event]
        lookup_times = np.arange(start_time + np.timedelta64(1800, "s"), 
                                 end_time + np.timedelta64(3599, "s"), 
                                 np.timedelta64(3600, "s"))
        dates = np.unique(lookup_times.astype('datetime64[D]'))

        FLIR_STAT_DS = xr.concat([read_flir_statistics(date, campaign_name="PS149") for date in dates], 
                                 dim='time').sortby('time')
        FLIR_TEMP_DS[event] = flir_image_target_tb(FLIR_STAT_DS, lookup_times, event)
        
    FLIR_TEMP_DS = xr.concat([*FLIR_TEMP_DS.values()], dim='time').sortby('time')
    
    return FLIR_TEMP_DS


def flir_image_target_tb(FLIR_STAT_DS: xr.Dataset, lookup_times: np.ndarray, event: str, visualise=False):
    
    if visualise:
        for lookup_time in lookup_times:
            flir_img = get_flir_image(FLIR_STAT_DS, lookup_time)
            # gopro_image(lookup_time, campaign_name="PS149")
            plot_flir_image(img=flir_img*10**2, time=lookup_time)
    else:
    
        # these two variables (idx_x and idx_y) are manually filled using the plotted FLIR images
        idx_x = {'PS149_21-1': [np.arange(227,234),np.arange(192,201), # 3
                                np.arange(190,199),np.arange(214,222),
                                np.arange(218,227),np.arange(219,228),
                                np.arange(219,227),np.arange(217,226),
                                np.arange(212,221),np.arange(210,219),
                                np.arange(210,219),np.arange(209,218),
                                np.arange(211,219),np.arange(211,219),
                                np.arange(220,228),np.arange(215,223),
                                np.arange(218,226),np.arange(208,216),
                                np.arange(208,215),np.arange(212,220),
                                np.arange(220,228),np.arange(239,247),
                                np.arange(232,239),np.arange(214,222),
                                np.arange(216,224),np.arange(227,235),
                                np.arange(211,219),np.arange(233,240),
                                np.arange(230,238),np.arange(217,226),
                                np.arange(208,217),np.arange(207,216),
                                np.arange(206,214),np.arange(206,206), # fog/rain making partly obsure IR targets
                                np.arange(202,210),np.arange(202,210),
                                np.arange(193,201),np.arange(196,203),
                                np.arange(197,203),np.arange(193,200),
                                np.arange(186,193),np.arange(185,192),
                                np.arange(186,193),np.arange(188,195),
                                np.arange(200,200), # targets recovered
                                ],
                 'PS149_25-1': [np.arange(201,203),np.arange(205,208), # 3
                                np.arange(176,179),np.arange(215,216),
                                np.arange(173,174),np.arange(169,170),
                                np.arange(181,182),np.arange(183,184),
                                np.arange(174,175),np.arange(178,181),
                                np.arange(154,156),np.arange(155,155), # drops on lens
                                np.arange(158,160),np.arange(209,211),
                                np.arange(235,237),np.arange(183,185),
                                np.arange(195,197),np.arange(164,166),
                                np.arange(186,188),np.arange(175,178),
                                np.arange(147,150),np.arange(227,229),
                                np.arange(194,196),np.arange(136,138),
                                np.arange(141,143),np.arange(259,261),
                                np.arange(178,181),np.arange(187,190),
                                np.arange(194,196),np.arange(194,194), # again, partly obscured targets
                                np.arange(134,136),np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # lens dirty/still wet
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                ],
                 'PS149_32-1': [np.arange(202,205),np.arange(207,211),
                                np.arange(158,162),np.arange(151,155),
                                np.arange(74,78),np.arange(74,74), # targets recovered
                                ],
                 'PS149_36-1': [np.arange(211,214),
                                np.arange(205,209),
                                np.arange(208,211),
                                np.arange(206,210),
                                np.arange(206,212),
                                np.arange(205,210),
                                np.arange(201,206),
                                np.arange(192,197),
                                np.arange(195,199),
                                np.arange(195,195), # fog/rain
                                np.arange(197,200),
                                np.arange(199,202),
                                np.arange(199,202),
                                np.arange(201,204),
                                np.arange(198,203),
                                np.arange(199,203),
                                np.arange(196,200),
                                np.arange(193,195),
                                np.arange(191,194),
                                np.arange(186,189),
                                np.arange(184,187),
                                np.arange(185,187),
                                np.arange(187,190),
                                np.arange(186,188),
                                np.arange(194,197),
                                np.arange(196,197),
                                np.arange(196,196), # fog/rain
                                np.arange(196,196), # fog/rain
                                np.arange(213,215),
                                np.arange(201,203),
                                np.arange(191,195),
                                np.arange(50,50), # fog/rain
                                np.arange(50,50), # fog/rain
                                np.arange(193,196),
                                np.arange(50,50), # fog/rain
                                np.arange(199,202),
                                np.arange(50,50), # fog/rain
                                np.arange(50,50), # fog/rain
                                np.arange(198,200),
                                np.arange(200,203),
                                np.arange(194,197),
                                np.arange(50,50), # fog/rain
                                np.arange(183,185),
                                np.arange(184,186),
                                np.arange(185,189),
                                np.arange(185,189),
                                np.arange(185,188),
                                np.arange(184,187),
                                np.arange(185,188),
                                np.arange(50,50), # targets recovered
                                ]}
        idx_y = {'PS149_21-1': [np.arange(199,204),np.arange(196,202), # 3
                                np.arange(198,204),np.arange(201,207),
                                np.arange(203,209),np.arange(204,210),
                                np.arange(205,211),np.arange(204,210),
                                np.arange(185,192),np.arange(182,188),
                                np.arange(179,185),np.arange(177,183),
                                np.arange(174,181),np.arange(173,179),
                                np.arange(173,179),np.arange(184,190),
                                np.arange(183,189),np.arange(183,189),
                                np.arange(183,189),np.arange(197,203),
                                np.arange(189,195),np.arange(193,198),
                                np.arange(199,206),np.arange(197,203),
                                np.arange(199,205),np.arange(203,209),
                                np.arange(203,209),np.arange(210,216),
                                np.arange(211,217),np.arange(209,215),
                                np.arange(208,214),np.arange(207,213),
                                np.arange(207,212),np.arange(207,207), # fog/rain making partly obsure IR targets
                                np.arange(206,211),np.arange(204,210),
                                np.arange(201,207),np.arange(201,207),
                                np.arange(203,209),np.arange(203,208),
                                np.arange(201,206),np.arange(203,209),
                                np.arange(204,209),np.arange(205,210),
                                np.arange(200,200), # targets recovered
                                ],
                 'PS149_25-1': [np.arange(192,193),np.arange(197,199), # 3
                                np.arange(200,202),np.arange(210,211),
                                np.arange(213,215),np.arange(212,214),
                                np.arange(211,212),np.arange(210,211),
                                np.arange(180,182),np.arange(176,178),
                                np.arange(176,178),np.arange(176,176), # drops on lens
                                np.arange(172,174),np.arange(165,166),
                                np.arange(164,166),np.arange(163,165),
                                np.arange(162,164),np.arange(169,170),
                                np.arange(174,176),np.arange(174,176),
                                np.arange(182,184),np.arange(173,175),
                                np.arange(169,171),np.arange(175,177),
                                np.arange(187,189),np.arange(180,182),
                                np.arange(164,165),np.arange(178,180),
                                np.arange(177,179),np.arange(177,177), # again, partly obscured targets
                                np.arange(186,188),np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # lens dirty/still wet
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                np.arange(134,134), # drops
                                ],
                 'PS149_32-1': [np.arange(114,116),np.arange(116,119),
                                np.arange(113,116),np.arange(107,111),
                                np.arange(113,116),np.arange(113,113), # targets recovered
                                ],
                 'PS149_36-1': [np.arange(68,70),
                                np.arange(66,68),
                                np.arange(71,74),
                                np.arange(72,74),
                                np.arange(67,69),
                                np.arange(69,71),
                                np.arange(71,73),
                                np.arange(76,78),
                                np.arange(77,80),
                                np.arange(195,195), # fog/rain
                                np.arange(73,75),
                                np.arange(73,75),
                                np.arange(72,74),
                                np.arange(72,75),
                                np.arange(73,75),
                                np.arange(73,76),
                                np.arange(74,76),
                                np.arange(69,71),
                                np.arange(68,69),
                                np.arange(82,83),
                                np.arange(74,76),
                                np.arange(70,71),
                                np.arange(86,87),
                                np.arange(68,70),
                                np.arange(69,70),
                                np.arange(68,70),
                                np.arange(196,196), # fog/rain
                                np.arange(196,196), # fog/rain
                                np.arange(56,58),
                                np.arange(74,77),
                                np.arange(74,76),
                                np.arange(50,50), # fog/rain
                                np.arange(50,50), # fog/rain
                                np.arange(77,79),
                                np.arange(50,50), # fog/rain
                                np.arange(79,81),
                                np.arange(50,50), # fog/rain
                                np.arange(50,50), # fog/rain
                                np.arange(78,80),
                                np.arange(79,81),
                                np.arange(78,80),
                                np.arange(50,50), # fog/rain
                                np.arange(77,79),
                                np.arange(79,81),
                                np.arange(81,84),
                                np.arange(82,84),
                                np.arange(81,83),
                                np.arange(81,83),
                                np.arange(90,92),
                                np.arange(50,50), # targets recovered
                                ]}
    
        
        FLIR_TEMP_DS = xr.Dataset(coords={'time': (['time'], lookup_times)})
        n_time = len(lookup_times)
        for var in ['tb_mean', 'tb_std', 'tb_q75']:
            FLIR_TEMP_DS[var] = xr.DataArray(np.full((n_time,), np.nan), dims=['time'])
        
        for k, lookup_time in enumerate(lookup_times):
            flir_img = xr.DataArray(get_flir_image(FLIR_STAT_DS, lookup_time,
                                                   campaign_name_long="VAMPIRE2"), dims=['y','x'])
            if len(idx_x[event][k]) == 0: continue
            flir_img_sel = flir_img.sel(x=idx_x[event][k], y=idx_y[event][k])

            FLIR_TEMP_DS['tb_mean'][k] = flir_img_sel.mean().item()
            FLIR_TEMP_DS['tb_std'][k] = flir_img_sel.std().item()
            try:
                FLIR_TEMP_DS['tb_q75'][k] = flir_img_sel.quantile(0.75).item()
            except:
                pdb.set_trace()
    
    return FLIR_TEMP_DS


def ratio_correction(
    tb_flir: np.ndarray, 
    temp_ref: np.ndarray,
    emissivity=1.0,
    tb_atm=None):
    
    """
    Ratio to correct the measured FLIR TBs. The corrected FLIR TB would be:
    tb_flir_corrected = tb_flir / mean_ratio
    
    Parameters:
    -----------
    tb_flir : np.ndarray
        Data measured by FLIR (actually surface temperature but with an emissivity set to 1.0), 
        which can be interpreted as brightness temperature (TB).
    temp_ref : np.ndarray
        Reference surface temperature (ground truth).
    emissivity : float or np.ndarray
        Assumed surface emissivity.
    tb_atm : np.ndarray or None
        If not None, indicates the assumed downwelling atmospheric brightness temperature.
    """
    
    if tb_atm is None: tb_atm = np.full(tb_flir.shape, 273.15)
    
    ratio = tb_flir / (emissivity*temp_ref + (1-emissivity)*tb_atm)
    mean_ratio = np.nanmean(ratio)
    
    return mean_ratio


def bias_correction(
    tb_flir: np.ndarray, 
    temp_ref: np.ndarray,
    emissivity=1.0,
    tb_atm=None):
    
    """
    As ratio_correction, but correcting FLIR TBs with an added offset. The corrected FLIR TB would
    be:
    tb_flir_corrected = tb_flir - bias
    """
    
    if tb_atm is None: tb_atm = np.full(tb_flir.shape, 273.15)
    
    offsets = tb_flir - (1-emissivity)*tb_atm - emissivity*temp_ref
    bias = np.nanmean(offsets)
    
    return bias


def bias_error_propagation(
    temp_skin_insitu: np.ndarray,
    tb_atm,
    emissivity,
    d_tb_flir,
    d_temp_skin_insitu,
    d_tb_atm,
    d_emissivity):
    
    d_bias = np.sqrt(d_tb_flir**2 + 
                     np.nanmean(tb_atm - temp_skin_insitu)**2*d_emissivity**2 + 
                     np.nanmean(emissivity - 1)**2*d_tb_atm**2 +
                     np.nanmean(emissivity)**2*d_temp_skin_insitu**2)
    
    return d_bias


def temp_flir_error_propagation(
    tb_flir: np.ndarray,
    tb_atm,
    emissivity,
    d_tb_flir, 
    d_tb_atm,
    d_emissivity,
    mean=True):
    
    if mean:
        d_temp_skin_flir = np.sqrt(np.nanmean(1/emissivity)**2*d_tb_flir**2 +
                                   np.nanmean((tb_atm - tb_flir)/(emissivity**2))**2*d_emissivity**2 +
                                   np.nanmean(1 - 1/emissivity)**2*d_tb_atm**2)
    else:
        d_temp_skin_flir = np.sqrt((1/emissivity)**2*d_tb_flir**2 +
                                   ((tb_atm - tb_flir)/(emissivity**2))**2*d_emissivity**2 +
                                   (1 - 1/emissivity)**2*d_tb_atm**2)
    
    return d_temp_skin_flir


def flir_correction_insitu_stds(surface_temp_ds: xr.Dataset):
    
    d_tb_flir = surface_temp_ds.tb_flir_std.mean().item()
    d_emissivity = np.std(np.array([0.985,0.996]))
    d_tb_atm = np.std(np.array([205., 239.075, 273.15]))
    d_temp_skin_insitu = surface_temp_ds.temp_groundtruth_std.mean().item()
    
    return d_tb_flir, d_emissivity, d_tb_atm, d_temp_skin_insitu


def visual_inspection_conditions_ice_stations(dates: list, visualise=False):
    
    if visualise: visualise_conditions_ice_stations(dates)
    
    skip_days = ["2025-07-11", 
                 "2025-07-15", 
                 "2025-07-21",  # too much variation of surface temp because of differential sunlight
                 "2025-07-22",  # FLIR footprint destroyed
                 "2025-07-26",
                 "2025-07-28", 
                 "2025-07-31", 
                 "2025-08-01",
                 "2025-08-04", 
                 "2025-08-06",
                 "2025-08-09",  # potential biases in FLIR and in-situ skin temperature due to solar radiation
	             "2025-08-10", 
                 "2025-08-12", 
                 "2025-08-14", 
                 "2025-08-18",  # potential biases in FLIR and in-situ skin temperature due to solar radiation
                 "2025-08-23"]
    dates = [date for date in dates if date.strftime('%Y-%m-%d') not in skip_days]
    
    return dates


def visualise_conditions_ice_stations(dates: list):
    
    for date in dates:
        ds = read_flir_statistics(date.strftime("%Y-%m-%d"), campaign_name=Constants.CAMPAIGN_NAME)
        
        flir_image(ds, np.datetime64(date))
        gopro_image(np.datetime64(date), campaign_name=Constants.CAMPAIGN_NAME)


def visualise_sfc_temp_flir_insitu(
    surface_temp_ds: xr.Dataset, 
    dates_icestation: list, 
    assumptions: dict,
    bias: float,
    save_figures=False,
    path_plots=os.environ['PATH_PLOTS'] + "flir/offset_correction/"):
    
    temp_flir = ((surface_temp_ds["tb_flir_center"] - (1 - assumptions['emissivity'])*assumptions['tb_atm']) / 
                 assumptions['emissivity'])
    
    d_tb_flir, d_emissivity, d_tb_atm, _ = flir_correction_insitu_stds(surface_temp_ds)
    d_temp_flir = temp_flir_error_propagation(surface_temp_ds["tb_flir_center"].values,
                                              assumptions['tb_atm'],
                                              assumptions['emissivity'],
                                              d_tb_flir,
                                              d_tb_atm,
                                              d_emissivity,
                                              mean=False)
    
    temp_flir_corr = ((surface_temp_ds["tb_flir_center"] - bias - (1 - assumptions['emissivity'])*assumptions['tb_atm']) /
                      assumptions['emissivity'])
    temp_insitu = surface_temp_ds["temp_groundtruth"]
    
    t_min = np.floor(np.nanmin(np.vstack((temp_flir, temp_insitu)).ravel()))
    t_max = np.ceil(np.nanmax(np.vstack((temp_flir, temp_insitu)).ravel()))
    
    f1 = plt.figure(figsize=(5.5,4.5))
    a1 = plt.axes()
    plt.subplots_adjust(top=0.975, right=0.975, left=0.15)
    
    a1.plot(np.linspace(t_min, t_max), np.linspace(t_min, t_max), color="k", linewidth=0.75, label="1:1")
    
    res = stats.linregress(temp_insitu, temp_flir)
    x = np.linspace(t_min,t_max)
    y = x*res.slope + res.intercept
    
    a1.errorbar(temp_insitu, temp_flir,
                xerr=surface_temp_ds['temp_groundtruth_std'], yerr=d_temp_flir, 
                fmt='o', color='orange', label='center and std.')
    a1.plot(x, y, color='orange', label='fit in-situ - FLIR')
    
    a1.scatter(temp_insitu, temp_flir_corr, color='green', label='corrected')

    for i, label in enumerate(dates_icestation):
        plt.text(temp_insitu[i], temp_flir[i], label, fontsize=5, ha="right")
    
    lh, ll = a1.get_legend_handles_labels()
    a1.legend(lh, ll, loc='lower right', frameon=False)

    a1.set_xlim(t_min, t_max)
    a1.set_ylim(t_min, t_max)
    a1.set_xlabel("surface temperature in situ (K)")
    a1.set_ylabel("surface temperature flir (K)")
    
    if save_figures:
        os.makedirs(path_plots, exist_ok=True)
        filename = f"{Constants.CAMPAIGN_NAME}_flir_offset_corr"
        outfile = os.path.join(path_plots, filename + ".png")
        f1.savefig(outfile, dpi=150)
        
        print(f"Saved {outfile} ....")
    
    else:
        plt.show()
        pdb.set_trace()
    plt.close()
    

def generate_temp_offset_dataset(
    surface_temp_ds: xr.Dataset,
    dates_icestation: dict,
    assumptions: dict,
    bias: float,
    bias_err: float,
    ir_bias: float,
    ir_bias_err: float,
    FLIR_IR_TB: xr.DataArray,
    IR_TEMP: xr.DataArray):
    
    DS = xr.Dataset(coords={'time': (['time'], np.array(dates_icestation).astype('datetime64[ns]'))})
    
    for var in ['tb_flir_center', 'tb_flir_mean', 'tb_flir_std']:
        DS[var] = xr.DataArray(surface_temp_ds[var].values.astype(np.float64), dims='time',
                               attrs={'standard_name': "brightness_temperature",
                                      'units': "K"
                                      })
        if var == 'tb_flir_std':
            del DS[var].attrs['standard_name']
            DS[var].attrs['long_name'] = "standard deviation of all brightness temperatures of a FLIR image"
        elif var == 'tb_flir_mean':
            DS[var].attrs['long_name'] = "mean of all brightness temperatures of a FLIR image"
            DS[var].attrs['ancillary_variables'] = 'temp_flir_std'
        elif var == 'tb_flir_center':
            DS[var].attrs['long_name'] = "brightness temperature in the center of the FLIR image"
            
    
    DS['temp_flir_center'] = ((DS['tb_flir_center'] - (1 - assumptions['emissivity'])*assumptions['tb_atm']) / 
                              assumptions['emissivity'])
    DS['temp_flir_center'].attrs = {'units': "K",
                                    'long_name': ("calculated surface temperature from FLIR brightness temperatures " +
                                                  "and assumptions of emissivity and downwelling atmospheric " +
                                                  "brightness temperatures"),
                                    'comment': "=(tb_flir_center - (1-emissivity)*tb_atm) / emissivity"}
    DS['emissivity'] = xr.DataArray(assumptions['emissivity'], dims=['time'],
                                    attrs={'standard_name': "surface_longwave_emissivity",
                                           'units': "1",
                                           'long_name': "assumed emissivity of the sea ice",
                                           'comment': ("emissivity assumption based on " +
                                                       "Thielke et al., 2022, https://doi.org/10.1038/s41597-022-01461-9; " +
                                                       "Nalli et al., 2023, https://doi.org/10.3390/rs15235509; " +
                                                       "Cox et al., 2023, https://doi.org/10.1038/s41597-023-02415-5")})
    DS['tb_atm'] = xr.DataArray(assumptions['tb_atm'], dims=['time'],
                                attrs={'standard_name': "brightness_temperature",
                                       'units': "K",
                                       'long_name': ("assumed downwelling atmospheric brightness temperature " +
                                                     "in the thermal-infrared"),
                                       'comment': ("assumption based on " +
                                                   "Smith and Tuomi, 2008, https://doi.org/10.1175/2007JAMC1615.1")})
    
    for var in ['temp_groundtruth', 'temp_groundtruth_mean', 'temp_groundtruth_std']:
        var_ds = var.replace('groundtruth', 'in_situ')
        DS[var_ds] = xr.DataArray(surface_temp_ds[var].values.astype(np.float64), dims='time',
                                  attrs={'standard_name': "surface_temperature",
                                         'units': "K",
                                         'comment': ("manual, hand-held measurements where influence " +
                                                     "of wind or radiation cannot be fully excluded")})
        
        if var == 'temp_groundtruth':
            DS[var_ds].attrs['long_name'] = "in-situ surface temperature observation in/near MWR footprint"
        elif var == 'temp_groundtruth_mean':
            DS[var_ds].attrs['long_name'] = "mean of in-situ surface temperature observations around MWR footprint"
            DS[var_ds].attrs['ancillary_variables'] = 'temp_in_situ_std'
        elif var == 'temp_groundtruth_std':
            DS[var_ds].attrs['long_name'] = "standard deviation of in-situ surface temperature observations around MWR footprint"
    
    
    if (FLIR_IR_TB is not None) and (IR_TEMP is not None):
        DS = DS.assign_coords({'time_ir': (['time_ir'], IR_TEMP.time.values)})
        DS['temp_ir_target'] = xr.DataArray(IR_TEMP.values, dims=['time_ir'],
                                            attrs={'standard_name': "surface_temperature",
                                                   'units': "K",
                                                   'long_name': "mean surface temperature of three infrared targets",
                                                   'comment': ("aluminium plates coated with Nextel Suede " +
                                                               "Coating 3101, 7329 S139 tiefschwarz with an " +
                                                               "emissivity of 0.98")})
        DS['tb_flir_ir_target'] = xr.DataArray(FLIR_IR_TB.values, dims=['time_ir'],
                                               attrs={'standard_name': "brightness_temperature",
                                                      'units': "K",
                                                      'long_name': "FLIR brightness temperature of the infrared targets"})
    
    for name, var in zip(['is_bias', 'is_bias_err', 'ir_bias', 'ir_bias_err'], 
                         [bias, bias_err, ir_bias, ir_bias_err]):
        DS[name] = xr.DataArray(np.float64(var))
        if 'ratio' in name:
            DS[name].attrs['units'] = "1"
        else:
            DS[name].attrs['units'] = "K"
    
    
    DS['is_bias'].attrs['long_name'] = "bias of FLIR brightness temperatures based on in-situ temperatures"
    DS['is_bias'].attrs['comment'] = ("is_bias was computed in such a way that, when applied to FLIR brightness " + 
                                      "temperatures, the FLIR brightness temperatures yield bias corrected surface " +
                                      "temperatures. " +
                                      "Apply as follows to obtain in-situ-bias-corrected FLIR brightness temperatures: " +
                                      "FLIR_corrected = FLIR - is_bias")
    DS['is_bias'].attrs['ancillary_variables'] = "is_bias_err"
    
    DS['is_bias_err'].attrs['long_name'] = "uncertainty of is_bias"
    DS['is_bias_err'].attrs['comment'] = ("estimated with error propagation; uses standard deviations of " +
                                          "mean tb_flir_std, used emissivity values, " +
                                          "used tb_atm values, mean temp_in_situ_std")
    
    DS['ir_bias'].attrs['long_name'] = "bias of FLIR brightness temperatures based on infrared target temperatures"
    DS['ir_bias'].attrs['comment'] = ("the infrared targets are aluminium plates coasted with " +
                                      "Nextel Suede Coating 3101, 7329 S139 tiefschwarz with an emissivity of 0.98. " +
                                      "ir_bias was computed in such a way that, when applied to FLIR brightness " + 
                                      "temperatures, the FLIR brightness temperatures yield bias corrected surface " +
                                      "temperatures of the infrared targets. " +
                                      "Apply as follows to obtain infrared-target-bias-corrected FLIR brightness temperatures: " +
                                      "FLIR_corrected = FLIR - ir_bias")
    DS['ir_bias'].attrs['ancillary_variables'] = "ir_bias_err"
    
    DS['ir_bias_err'].attrs['long_name'] = "uncertainty of ir_bias"
    DS['ir_bias_err'].attrs['comment'] = ("estimated with error propagation; uses standard deviations of " +
                                          "mean tb_flir_std and standard deviations over the temperatures " +
                                          "of three infrared targets")
    
    recommended_bias = bias
    recommended_bias_err = bias_err
    for name, var in zip(['bias', 'bias_err'], [recommended_bias, recommended_bias_err]):
        DS[name] = xr.DataArray(np.float64(var))
        DS[name].attrs['units'] = "K"
        DS[name].attrs['long_name'] = "bias of FLIR brightness temperatures"
        DS[name].attrs['comment'] = f"equals {'is_'+name} if available, otherwise: {'ir_'+name}"
    DS['bias'].attrs['ancillary_variables'] = "bias_err"
    
    DS['bias_err'].attrs['long_name'] = "uncertainty of bias"
    
    return DS
    

def export_offset_ds(DS: xr.Dataset, path_output: str, campaign_name: str):
    
    os.makedirs(path_output, exist_ok=True)
    
    add_site_comment = ""
    if campaign_name == "PS149":
        add_site_comment = " and infrared target"
    
    DS.attrs['title'] = f"Brightness temperature offset correction for FLIR A315 during {campaign_name}"
    DS = write_basic_attributes(DS)
    DS.attrs['Conventions'] = "CF-1.13"
    if campaign_name == 'PS144':
        DS.attrs['author'] = "Janna Rückert, Andreas Walbröl, Linnu Bühler, Nils Risse, Pavel Krobot"
    elif campaign_name == "PS149":
        DS.attrs['author'] = "Andreas Walbröl, Linnu Bühler, Janna Rückert, Pavel Krobot"
    DS = update_netCDF_file_history(DS, 
                                    script_name=os.path.basename(__file__), 
                                    summary_str="computed FLIR offsets")
    DS.attrs['measurement_site'] = "Arctic Ocean, sea ice portside of RV Polarstern"
    DS.attrs['comment'] = (f"in-situ{add_site_comment} measurements took place within, near or around the " +
                           "microwave radiometer (MWR) footprint on the sea ice")
    DS.attrs['recommendation'] = "use bias"
    DS.attrs['project'] = ("DFG (German Research Foundation) project number 268020496 - TRR 172, " +
                     "Transregional Collaborative Research Center 'ArctiC Amplification: Climate Relevant " +
                     "Atmospheric and SurfaCe Processes, and Feedback Mechanisms (AC)3")
    
    for var in ['time', 'time_ir']:
        if var in DS.coords:
            DS = encode_time(DS, time_var=var, time_dim=var, reference_period=np.datetime64("2024-01-01T00:00:00"))
            DS[var].encoding['_FillValue'] = None
    
    filename = f"{campaign_name}_flir_tb_offset_correction.nc"
    outfile = path_output + filename
    
    DS.to_netcdf(outfile, mode='w', format="NETCDF4")
    DS = DS.close()
    print(f"Saved {outfile}....")


if __name__ == "__main__":
    
    campaign = "vampire"
    if campaign == "vampire":
        from vampire.constants import Constants as Constants
    elif campaign == 'VAMPIRE2':
        from vampire.constants import Constants_PS149 as Constants
    
    main()