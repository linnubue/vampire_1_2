import sys
import os
import datetime as dt
import glob
import pdb

import numpy as np
import xarray as xr
import matplotlib as mpl
import matplotlib.pyplot as plt

from vampire.io.readers.radiosonde import read_radiosondes
from vampire.io.readers.mwr import read_mwr_pro_output
from vampire.analysis.data_tools import (Gband_double_side_band_average, compute_retrieval_statistics, 
                                         write_basic_attributes,
                                         get_temporal_overlap)
from run_pamtra import run_pamtra_run

os.environ['OPENBLAS_NUM_THREADS'] = "1"
if 'PAMTRA_DATADIR' not in os.environ:
    os.environ['PAMTRA_DATADIR'] = "" # actual path is not required, but the variable has to be defined.


def main():
    
    """
        This script is used to forward simulate radiosondes at HATPRO and MiRAC-P frequencies 
        so that differences between simulated and observed TBs can be analysed.
    """

    campaign = "PS144"
    if campaign == "PS144":
        from vampire.constants import Constants as Constants
        campaign_label = "vampire"
    elif campaign == "PS149":
        from vampire.constants import Constants_PS149 as Constants
        campaign_label = "VAMPIRE2"

    path_data = {dataset: (os.environ['VAMPIRE_DATA'] + dataset + "/") for dataset in ['radiosondes', 'hatpro', 'mirac-p']}
    path_pam_output = {dataset: (os.environ['VAMPIRE_DATA'] + f"CSC/{dataset}_freq/") for dataset in ['hatpro', 'mirac-p']}
    path_output = os.environ['VAMPIRE_DATA'] + "CSC/offsets/"
    path_plot = os.environ['PATH_PLOTS'] + "CSC/"
    
    freq_label = 'hatpro'       # either 'hatpro' or 'mirac-p'... it specifies which instrument is considered
    mwr_version = "i00"
    simulate = False    # if True, PAMTRA simulations are performed. If False, it's assumed that 
                       # simulations already exist
    interpolate = True # if True, interpolation of radiosondes to a new grid will be performed
    save_offset_slope = True
    window = 900       # time window in sec over which to average observed TBs
    date_range = np.arange(np.datetime64(Constants.DATE_START.strftime("%Y-%m-%d")), 
                           np.datetime64(Constants.DATE_END.strftime("%Y-%m-%d")) + np.timedelta64(1, "D"),
                           np.timedelta64(1, "D"))
    
    
    pamtra_settings = {'rs_wind': True,         # if True: wind data from radiosondes will be included
                       'lat': 79.0,                        # backup/dummy latitude in deg N
                       'lon': 5.0,                         # backup/dummy longitude in deg E
                       'obs_height': np.array([20.0]),     # height of radiosonde launch in m
                       'site': campaign,
                       }
    plot_settings = {'save_figures': True,
                     }


    freqs = define_freqs_to_simulate()

    if simulate:
        RS_DS = read_radiosondes(path_data['radiosondes'], date_range=date_range, wind_uv=pamtra_settings['rs_wind'])
        sonde_dict = prepare_radiosondes_for_pamtra(RS_DS, Constants, interpolate=interpolate)        
        check_for_nans(sonde_dict)

        for sonde_data in sonde_dict.values():
            pam = run_pamtra_run(sonde_data, freqs[freq_label], path_pam_output[freq_label], **pamtra_settings)
        print("Simulations are done. Activating self destruct.")
        1/0
    
    compare_simulated_and_observed_tbs(path_data, path_pam_output, path_output, path_plot, campaign, mwr_version,
                                       Constants,
                                       date_range, window, save_offset_slope, pamtra_settings, plot_settings)


def remove_cloudy_scenes(DS: xr.Dataset, Constants):
    
    clear_sky_times = np.asarray([np.datetime64(timestamp).astype('datetime64[s]') for timestamp in Constants.CLEARSKY_SONDES])
    DS = DS.sel(launch_time=np.sort(clear_sky_times), method='nearest', tolerance=np.timedelta64(300, "s"))
    
    return DS


def interp_to_lowest_common_max_height(DS: xr.Dataset):
    
    min_common_max_alt = np.floor(DS.height.values[np.where(np.all(~np.isnan(DS.relhum + DS.temp), axis=0))[0][-1]]*0.001)*1000.
    DS = DS.sel(height=slice(None,min_common_max_alt))
            
    return DS


def radiosonde_dataset_to_dict(DS: xr.Dataset):
    
    data_dict = dict()
    n_time = len(DS.launch_time)
    for idx in range(n_time):
        sonde_key = str(idx)
        data_dict[sonde_key] = dict()
        for var in DS.variables:
            
            if ('launch_time' not in DS[var].dims) and ('height' in DS[var].dims):
                data_dict[sonde_key][var] = DS[var].values
                continue
            
            data_dict[sonde_key][var] = DS[var].values[idx,...]
            
            if (data_dict[sonde_key][var].ndim == 0) and (data_dict[sonde_key][var].dtype in [float,int]):
                data_dict[sonde_key][var] = float(data_dict[sonde_key][var])
    
    return data_dict


def fill_nans(DS: xr.Dataset, variables: list):
    
    max_gap = 500.      # in m
    hgt_diff_median = DS.height.diff('height').median()
    idx_max_gap = int(max_gap / hgt_diff_median)
    for var in variables:
        DS[var] = DS[var].interpolate_na(dim='height', method='linear', max_gap=idx_max_gap)
        
    return DS


def prepare_radiosondes_for_pamtra(DS: xr.Dataset, Constants, interpolate=True):
    
    DS = remove_cloudy_scenes(DS, Constants)
    if interpolate:
        DS = interp_to_lowest_common_max_height(DS)

    DS['relhum'] *= 100.        # to %
    DS['launch_time_npdt'] = xr.DataArray(DS.launch_time.values, dims=['launch_time'])

    n_time = len(DS.launch_time)
    for var in ['lat', 'lon', 'temp']:
        DS[f'ref_{var}'] = xr.DataArray(np.asarray([DS[var].values[k,~np.isnan(DS[var].values[k,:])][0] for k in range(n_time)]),
                                        dims=DS.launch_time.dims)
    DS = DS.rename({'ref_temp': 'skt'})
    DS['siconc'] = xr.DataArray(np.ones(n_time, dtype=np.float32), dims=DS.launch_time.dims)
        
    DS = fill_nans(DS, variables=['temp', 'relhum', 'pres', 'u', 'v'])
    sonde_dict = radiosonde_dataset_to_dict(DS)
        
    return sonde_dict


def define_freqs_to_simulate():
    
    freqs = {'hatpro': [22.24, 23.04, 23.84, 25.44, 26.24, 27.84, 31.4,
                        51.26, 52.28, 53.86, 54.94, 56.66, 57.3, 58.0],
            'mirac-p': np.sort([183.31-0.6, 183.31+0.6, 183.31-1.5, 183.31+1.5,
                        183.31-2.5, 183.31+2.5, 183.31-3.5, 183.31+3.5,
                        183.31-5.0, 183.31+5.0, 183.31-7.5, 183.31+7.5, 
                        243.0, 340.0])}
    
    return freqs


def check_for_nans(sonde_dict: dict):
    
    """
    Check for nans: count nans for the critical variables.
    """

    n_time = len(sonde_dict.keys())
    n_nans = np.zeros((n_time,))
    for idx in sonde_dict.keys():
        sonde_no = int(idx)
        n_nans[sonde_no] = np.count_nonzero(np.isnan(sonde_dict[idx]['temp'] + 
                                                     sonde_dict[idx]['relhum'] + 
                                                     sonde_dict[idx]['pres']))
        
    assert np.sum(n_nans) == 0


def add_calib_times(DS: xr.Dataset, freq_labels: list, Constants):
    
    calib_time_labels = {'hatpro': "HATPRO", 'mirac-p': "LHUMPRO"}
    for freq_label in freq_labels:
        calib_times = np.asarray([np.datetime64(calib_time) 
                                  for calib_time in Constants.__dict__['CALIBRATION_TIME_'+calib_time_labels[freq_label]]
                                  ])
        
        if calib_times[0] > Constants.DATE_START:
            calib_period_start = np.insert(calib_times, 0, np.datetime64(Constants.DATE_START))
            calib_period_end = np.append(calib_times, np.datetime64(Constants.DATE_END))
        else:
            calib_period_start = calib_times
            calib_period_start[0] = np.datetime64(Constants.DATE_START)
            calib_period_end = np.append(calib_times[1:], np.datetime64(Constants.DATE_END))
        
        DS['calib_period_start_'+freq_label] = xr.DataArray(calib_period_start, 
                                                            dims='calib_period_start_'+freq_label)
        DS['calib_period_end_'+freq_label] = xr.DataArray(calib_period_end, 
                                                          dims='calib_period_end_'+freq_label)
    
    return DS


def compare_simulated_and_observed_tbs(
    path_data: dict,
    path_pam_output: dict,
    path_output: str,
    path_plot: str,
    campaign: str,
    mwr_version: str,
    Constants,
    date_range: np.ndarray,
    window: int,
    save_offset_slope: bool,
    pamtra_settings: dict,
    plot_settings: dict):
    
    """
    Requires the simulations of hatpro and mirac-p frequencies to be complete.
    """
    
    freq_labels = ['hatpro', 'mirac-p']
    
    PAM_DS = load_pamtra_output(path_pam_output, freq_labels)
    DS_dict = {'sim': PAM_DS}


    DS_overlap_dict = dict()
    launch_time = DS_dict['sim'].time.values
    for freq_label in freq_labels:
        DS_dict[freq_label] = load_mwr_data(path_data[freq_label], date_range, radiometer=freq_label, version=mwr_version)
        DS_overlap_dict[freq_label] = merge_sonde_and_mwr(DS_dict[freq_label], launch_time, window)
        
    DS_dict['obs_merged'] = xr.merge([DS_overlap_dict['hatpro'], DS_overlap_dict['mirac-p']])
    DS_dict['obs_merged'] = add_calib_times(DS_dict['obs_merged'], freq_labels, Constants)
    
    plot_tb_offsets(DS_dict, path_plot, plot_settings, campaign)
    if save_offset_slope:
        save_offsets_slopes(DS_dict, path_output, pamtra_settings, freq_labels, campaign)
    
    
def load_pamtra_output(path_pam_output: dict, freq_labels: list):
    
    DS_list = list()
    for frq_lb in freq_labels:
        files = sorted(glob.glob(path_pam_output[frq_lb] + "*.nc"))
        assert len(files) > 0
        DS_list.append(xr.open_mfdataset(files, concat_dim='grid_x', combine='nested', 
                                         preprocess=pam_out_drop_useless_dims))
    PAM_DS = xr.merge(DS_list, join='outer').load()
    del DS_list

    PAM_DS = post_process_pamtra_tbs(PAM_DS)
    
    return PAM_DS
    
    
def post_process_pamtra_tbs(DS: xr.Dataset):
    
    """
    Post process PAMTRA TBs: Apply double side band averaging.
    """
    
    tb_dsba, freqs_dsba = Gband_double_side_band_average(DS.tb, DS.frequency, xarray_compatibility=True, 
                                                         freq_dim_name='frequency')
    DS = DS.sel(frequency=freqs_dsba)
    DS['tb'] = tb_dsba

    DS = DS.rename({'frequency': 'freqs'}).drop('passive_polarisation')
    DS['tb'].attrs = {'long_name': "Simulated brightness temperatures", 'units': "K"}
    DS['freqs'].attrs = {'long_name': "Simulated frequencies", 'units': "GHz"}
    DS['angles'].attrs = {'long_name': "Zenith (or incidence) angles", 'units': "deg"}

    pam_time = DS.datatime.values
    DS = DS.rename_dims({'grid_x': 'time'})
    DS = DS.assign_coords({'time': pam_time}).drop('grid_x')
    
    return DS


def pam_out_drop_useless_dims(DS):

    """
    Preprocessing the PAMTRA output file dataset before concatenation.
    Removing undesired dimensions (average over polarisation, use zenith only,
    remove y dimension). Additionally, it adds another variable (DataArray)
    containing the datatime in sec since epochtime.

    Parameters:
    -----------
    ds : xarray dataset
        Dataset of the PAMTRA output.
    """

    # Zenith only ("-1"): PAMTRA angles is relative to ZENITH
    # Average over polarisation (".mean(axis=-1)")
    # Remove redundant dimensions: ("0,0")
    DS = DS.isel(grid_y=0, angles=-1, outlevel=0)
    DS['tb'] = DS.tb.mean(axis=-1)
    
    # remove some variables:
    DS = DS.drop(['model_i', 'model_j', 'longitude', 'latitude'])

    return DS


def load_mwr_data(
    path_data,
    date_range,
    radiometer,
    version="i00"):

    """
    Load radiometer data (i.e., as they are stored on the cologne servers in daily subfolders)
    and generate an xarray dataset out of the loaded data (stored in a dictionary). 

    Parameters:
    -----------
    path_data : str
        String indicating the super directory of the MWR data (i.e., 
        /path/to/data/hatpro/). Contains subdirectories
        indicating the current year, month and day (i.e., ./2022/07/21/).
    date_range : np.ndarray of np.datetime64
        Range of dates.
    radiometer : str
        String indicating which radiometer data is addressed. Options:
        'hatpro', 'mirac-p'
    version : str
        String indicating the version number of the data.
    """

    DS = read_mwr_pro_output(path_data, date_range=date_range, scans=['ZENITH', ''],
                             sorted_into_daily_folders=False,
                             radiometer=radiometer, version=version)
    DS = DS.rename({'freq_sb': 'freqs', 'n_freq': 'freqs'})
    
    for var in DS.data_vars:
        if var not in ['tb']: DS = DS.drop_vars(var)

    DS = DS.load()
    
    return DS


def handle_clear_sky_exceptions(time_bins: np.ndarray):
    
    """
    Handle cases where the best MWR-radiosonde overlap is slightly different from the time selected
    by default.
    """
    
    exceptional_times = np.array([np.datetime64("2025-07-30T22:59:34"),
                                  np.datetime64("2025-08-10T06:57:16")])
    for ET in exceptional_times:
        idx_et = np.where(np.abs(time_bins['default'][:,0] - ET) < np.timedelta64(30, "s"))[0]
        if len(idx_et) == 0: continue
        
        if ET == np.datetime64("2025-07-30T22:59:34"):
            time_bins['default'][idx_et[0],:] = np.array([[np.datetime64("2025-07-30T22:49:34"),
                                                           np.datetime64("2025-07-30T23:04:34")]])
            time_bins['extended'][idx_et[0],:] = np.array([[np.datetime64("2025-07-30T22:44:34"),
                                                            np.datetime64("2025-07-30T23:04:34")]])
            
        elif ET == np.datetime64("2025-08-10T06:57:16"):
            time_bins['default'][idx_et[0],:] = np.array([[np.datetime64("2025-08-10T06:28:00"),
                                                           np.datetime64("2025-08-10T06:39:00")]])
            time_bins['extended'][idx_et[0],:] = np.array([[np.datetime64("2025-08-10T06:28:00"),
                                                            np.datetime64("2025-08-10T06:39:00")]])

    return time_bins    


def merge_sonde_and_mwr(
    DS,
    launch_time,
    window):

    """
    Find overlapping radiometer time and radiosonde launch times. Then compute the average and
    standard deviation of the observed brightness temperatures over that overlapping time span.

    Parameters:
    -----------
    DS : xarray dataset
        Data set containing brightness temperature (tb), freuency (freqs) and time
        information, loaded with the function load_mwr_data.
    launch_time : np.ndarray of np.datetime64
        Radiosonde launch time array.
    window : int
        Time window for overlap in s.
    """
    
    time_bins = {'default': np.array([[time, time + np.timedelta64(window, "s")] for time in launch_time]),
                 'extended': np.array([[time - np.timedelta64(600, "s"), 
                                        time + np.timedelta64(600, "s")] for time in launch_time])}
    time_bins = handle_clear_sky_exceptions(time_bins)
    
    DS_dict = dict()
    for key, time_bins_val in time_bins.items():
        tb_mean, tb_std = get_temporal_overlap(DS.tb, time_bins=time_bins_val, time_dim_name="time", return_std=True)
        DS_dict[key] = xr.Dataset({'tb_mean': (['time', 'freqs'], tb_mean, {'units': "K"}), 
                                   'tb_std': (['time', 'freqs'], tb_std, {'units': "K"})},
                                  coords= {'time': (['time'], launch_time), 
                                           'freqs': (['freqs'], DS.freqs.values, 
                                                     {'units': "GHz"})})
    
    DS_overlap = DS_dict['default']
    for tb_var in DS_overlap.data_vars:
        DS_overlap[tb_var] = DS_overlap[tb_var].where(~np.isnan(DS_overlap[tb_var]).all('freqs'), 
                                                      other=DS_dict['extended'][tb_var])

    return DS_overlap


def plot_tb_offsets(
    DS_dict: dict, 
    path_plot: str,
    plot_settings: dict, 
    campaign: str):

    # visualize:
    color_calib = np.array([[0.6,0.0,0.05], [0,0.55,1], [0.2,0.9,0.25]])

    # axis limits
    ax_lim_DS = xr.DataArray(np.asarray([[10.0, 60.0], [10.0, 60.0], [10.0, 60.0], [8.0, 60.0],
                                        [8.0, 60.0], [8.0, 60.0], [8.0, 60.0],   # K band
                                        [100.0, 130.0], [130.0, 160.0], [230.0, 260.0], [255.0, 285.0],
                                        [260.0, 285.0], [260.0, 285.0], [260.0, 285.0], # V band
                                        [260.0, 285.0], [250.0, 290.0], [240.0, 290.0], 
                                        [220.0, 290.0], [185.0, 285.0], [140.0, 280.0], # G band
                                        [80, 220.0], [170.0, 280.0]]),               # 243+340
                             dims=['freqs', 'lim'], 
                             coords={'freqs': np.array([ 22.240, 23.040, 23.840, 25.440, 26.240, 27.840, 31.400,
                                        51.260, 52.280, 53.860, 54.940, 56.660, 57.300, 58.000,
                                        183.910, 184.810, 185.810, 186.810, 188.310, 190.810,
                                        243.000, 340.000])})

    calib_period_start_dict = {'hatpro': DS_dict['obs_merged'].calib_period_start_hatpro,
                               'mirac-p': DS_dict['obs_merged']['calib_period_start_mirac-p']}
    calib_period_end_dict = {'hatpro': DS_dict['obs_merged'].calib_period_end_hatpro,
                               'mirac-p': DS_dict['obs_merged']['calib_period_end_mirac-p']}

    fs_small = 8
    fs_micro = 6
    
    f1, a1 = plt.subplots(ncols=6, nrows=4, figsize=(9,6), constrained_layout=True)

    a1 = a1.flatten()

    for k, freq in enumerate(DS_dict['sim'].freqs.values):
        
        DS_sim = DS_dict['sim'].sel(freqs=freq)
        DS_obs = DS_dict['obs_merged'].sel(freqs=freq)
        calib_start, calib_end = calib_period_start_dict['hatpro'], calib_period_end_dict['hatpro']
        if freq > 60.:
            calib_start, calib_end = calib_period_start_dict['mirac-p'], calib_period_end_dict['mirac-p']

        # compute retrieval statistics:
        ret_stat_dict = compute_retrieval_statistics(DS_sim.tb.values, DS_obs.tb_mean.values,
                                                     compute_stddev=True)

        ax_lim = ax_lim_DS.sel(freqs=f"{freq:.2f}")

        kk = 0
        for c_start, c_end in zip(calib_start, calib_end):
            a1[k].errorbar(DS_sim.tb.sel(time=slice(c_start, c_end)), 
                           DS_obs.tb_mean.sel(time=slice(c_start, c_end)),
                           yerr=DS_obs.tb_std.sel(time=slice(c_start, c_end)),
                           ecolor=color_calib[kk], elinewidth=1.4, capsize=3, 
                           markerfacecolor=color_calib[kk], markeredgecolor=(0,0,0),
                           linestyle='none', marker='o', markersize=5.0, linewidth=1.2, capthick=1.2)
            kk += 1


        # generate a linear fit with least squares approach: notes, p.2:
        # filter nan values:
        nonnan_idx = np.where(~np.isnan(DS_obs.tb_mean.values) & 
                                    ~np.isnan(DS_sim.tb.values))[0]
        x_fit = DS_sim.tb.values[nonnan_idx]
        y_fit = DS_obs.tb_mean.values[nonnan_idx]

        # there must be at least 2 measurements to create a linear fit:
        if (len(y_fit) > 1) and (len(x_fit) > 1):
            G_fit = np.array([x_fit, np.ones((len(x_fit),))]).T
            m_fit = np.linalg.inv(G_fit.T@G_fit)@G_fit.T@y_fit  # least squares solution
            a = m_fit[0]
            b = m_fit[1]

            ds_fit = a1[k].plot(ax_lim, a*ax_lim + b, color=(0,0,0), linewidth=1.2)

        # plot a line for orientation which would represent a perfect fit:
        a1[k].plot(ax_lim, ax_lim, color=(0,0,0), linewidth=1.0, alpha=0.5)


        # add statistics:
        mean_both = np.nanmean(np.concatenate((DS_sim.tb.values, DS_obs.tb_mean.values), axis=0))
        a1[k].text(0.99, 0.01, f"N = {ret_stat_dict['N']} \nbias = {ret_stat_dict['bias']:.2f} \n" +
                f"rmse = {ret_stat_dict['rmse']:.2f} \nstd. = {ret_stat_dict['stddev']:.2f} \nR = {ret_stat_dict['R']:.3f} ",
                ha='right', va='bottom', transform=a1[k].transAxes, fontsize=fs_micro)

        # add subplot label:
        a1[k].text(0.02, 0.98, f"{freq:.2f} GHz", ha='left', va='top', transform=a1[k].transAxes, fontsize=fs_small)

        if k == 0:  # dummy plots
            for kk in range(len(color_calib)):
                a1[k].errorbar(np.nan, np.nan, yerr=np.nan, ecolor=color_calib[kk], elinewidth=1.4, capsize=3, 
                               markerfacecolor=color_calib[kk], markeredgecolor=(0,0,0), linestyle='none', marker='o', 
                               markersize=5.0, linewidth=1.2, capthick=1.2, 
                               label=f"Calib. period {int(kk+1)}")

            ds_fit = a1[k].plot([np.nan, np.nan], [np.nan, np.nan], color=(0,0,0), linewidth=1.2, label="Best fit")

            # plot a line for orientation which would represent a perfect fit:
            a1[k].plot([np.nan, np.nan], [np.nan, np.nan], color=(0,0,0), linewidth=1.2, alpha=0.5, label="Theoretical perfect fit")
            
            # legend:
            leg_pos = np.asarray(a1[len(DS_dict['sim'].freqs)].get_position())
            leg_handles, leg_labels = a1[k].get_legend_handles_labels()
            f1.legend(handles=leg_handles, labels=leg_labels, loc='lower left',
                        bbox_to_anchor=(leg_pos[0,0]+0.01,leg_pos[0,1]-0.01), frameon=False, fontsize=fs_small)


        # set axis limits and aspect ratio:
        a1[k].set_xlim(ax_lim)
        a1[k].set_ylim(ax_lim)
        a1[k].set_aspect('equal')

        # set ticks and tick labels and parameters:
        a1[k].tick_params(axis='both', labelsize=fs_micro)

        # grid:
        a1[k].minorticks_on()
        a1[k].grid(axis='both', which='both', color=(0.5,0.5,0.5), alpha=0.25)

        # set labels:
        if k%6 == 0:
            a1[k].set_ylabel("TB$_{\mathrm{obs}}$ (K)", fontsize=fs_small)

        if k >= 18:
            a1[k].set_xlabel("TB$_{\mathrm{sim}}$ (K)", fontsize=fs_small)

    # remaining axes removed or used for legend:
    for k in range(len(DS_dict['sim'].freqs.values), len(a1)):
        a1[k].axis('off')
    
    f1.suptitle(f"{campaign} simulated vs. observed TBs")

    if plot_settings['save_figures']:
        plotname = f"{campaign}_hatpro_mirac-p_radiosonde_pamtra_tb_scatterplot_all_freqs"
        plotfile = path_plot + plotname + ".png"
        
        os.makedirs(path_plot, exist_ok=True)
        
        f1.savefig(plotfile, dpi=250, bbox_inches='tight')
        print(f"Saved {plotfile}....")
    else:
        plt.show()
        pdb.set_trace()
    plt.close()


def handle_exceptional_tbs(DS_obs: xr.Dataset):
    
    if np.any(np.abs(DS_obs.freqs.values - 243.) < 0.1):
        DS_obs['tb_mean'].loc[{'time': slice('2025-07-02T14:30:00', '2025-08-06T17:05:04'), 
                               'freqs': slice(242.,244.)}] = np.nan
    
    return DS_obs


def stats_for_each_calib_period(DS_obs: xr.Dataset, DS_sim: xr.Dataset, freq_label: str, campaign: str):
        
    n_calib_periods = len(DS_obs['calib_period_start_'+freq_label])
    n_freq = len(DS_obs.freqs)
    calib_start, calib_end = DS_obs['calib_period_start_'+freq_label], DS_obs['calib_period_end_'+freq_label]

    STAT_DS = xr.Dataset(coords={'frequency': (['frequency'], DS_obs.freqs.values, 
                                               {'description': "Microwave radiometer channel frequency", 
                                                'units': "GHz"}),
                                 'calibration_period_start': (['time'], calib_start.values, 
                                                              {'description': f"Start of calibration period or start of {campaign}",
                                                               'units': "seconds since 1970-01-01 00:00:00 UTC"
                                                              }),
                                 'calibration_period_end': (['time'], calib_end.values,
                                                            {'description': f"End of calibration period or end of {campaign}",
                                                             'units': "seconds since 1970-01-01 00:00:00 UTC"
                                                            })
                                 }
                         )
    for var in ['slope', 'offset', 'bias']:
        STAT_DS[var] = xr.DataArray(np.zeros((n_calib_periods, n_freq)), dims=['time', 'frequency'])
    STAT_DS['slope'] += 1       # base value should be 1
    STAT_DS['slope'].attrs = {'description': "Slope of the linear fit: TB_sim = slope*TB_obs + offset",
                              'units': ""}
    STAT_DS['offset'].attrs = {'description': "Offset of the linear fit: TB_sim = slope*TB_obs + offset",
                            'units': "K"}
    STAT_DS['bias'].attrs = {'description': ("Bias of observed TBs with respect to simulated TBs. " +
                                            "Bias = mean(TB_obs - TB_sim, dim='time')"),
                            'units': "K"}
    STAT_DS['n_samp'] = xr.DataArray(np.zeros((n_calib_periods,)), dims=['time'],
                                     attrs={'description': ("Number of samples that were used to compute bias, slope " +
                                                            "and offset for this calibration period."),
                                            'units': ""})

    for k in range(n_calib_periods):
        c_start, c_end = calib_start[k], calib_end[k]

        # limit observed and simulated TBs to current calib period:
        DS_sim_c = DS_sim.sel(time=slice(c_start,c_end))
        DS_obs_c = DS_obs.sel(time=slice(c_start,c_end))
        if len(DS_sim_c.time) == 0: continue
        DS_obs_c = handle_exceptional_tbs(DS_obs_c)

        bias_c = np.nanmean(DS_obs_c.tb_mean.values - DS_sim_c.tb.values, axis=0)
        nn_idx = np.where(~np.isnan(bias_c))[0]
        STAT_DS['bias'][k,nn_idx] = bias_c[nn_idx]
        STAT_DS['n_samp'][k] = np.count_nonzero(~np.isnan(DS_obs_c.tb_mean.values + DS_sim_c.tb.values), axis=0).max()

        for jj, freq in enumerate(DS_obs_c.freqs.values):
            y_fit = DS_sim_c.tb.values[:,jj]
            x_fit = DS_obs_c.tb_mean.values[:,jj]

            mask = np.isfinite(x_fit + y_fit)       # check for nans and inf.

            y_fit = y_fit[mask]
            x_fit = x_fit[mask]

            # there must be at least 2 measurements to create a linear fit:
            if (len(y_fit) > 1) and (len(x_fit) > 1):
                slope, offset = np.polyfit(x_fit, y_fit, 1)
                STAT_DS['slope'][k,jj] = slope
                STAT_DS['offset'][k,jj] = offset
                
    return STAT_DS


def add_global_attrs(STAT_DS: xr.Dataset, campaign, pamtra_settings):

    # add some attributes:
    STAT_DS.attrs['recommendation'] = ("The author recommends to use 'bias' only instead of the linear fit correction "
                                       "('slope' and 'offset') because of the low amount of clear sky radiosondes.")
    STAT_DS.attrs['description'] = ("Offset and slope of a linear fit between simulated (sim) and observed (obs)" +
                                    "brightness temperatures (TBs) for each frequency and calibration " +
                                    "period of the instrument. Linear fit: TB_sim = slope*TB_obs + offset")
    STAT_DS.attrs['HOW_TO_APPLY'] = ("To correct the measured TBs of your chosen radiometer, compute the following: " +
                                     "TB_corrected = slope*TB_obs + offset")
    STAT_DS.attrs['HOW_TO_APPLY_BIAS'] = ("In case you just want to correct a bias independent of TBs, use: " +
                                          "TB_corrected = (TB_obs - bias)")
    STAT_DS.attrs['forward_model'] = "PAMTRA, DOI: 10.5194/gmd-13-4229-2020"
    STAT_DS.attrs['add_info'] = (f"Simulations are based on {campaign} radiosondes. Zenith " +
                                 f"looking geometry. Assumed height (in m) of instrument above MSL: {pamtra_settings['obs_height'][0]}")
    STAT_DS = write_basic_attributes(STAT_DS)
    STAT_DS.attrs['history'] = (f"{dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}, " +
                                f"created with {os.path.basename(__file__)}")
    
    return STAT_DS


def save_offsets_slopes(
    DS_dict: dict, 
    path_output: str, 
    pamtra_settings: dict, 
    freq_labels: list,
    campaign: str):

    """
    Save offset and slope of the observed TB for each instrument and calibration period
    and all frequencies.
    """
    
    freq_lims = {'hatpro': np.array([20., 60.]),
                 'mirac-p': np.array([160., 350.])}
    for freq_label in freq_labels:
        DS_obs = DS_dict['obs_merged'].sel(freqs=slice(*freq_lims[freq_label]))
        DS_sim = DS_dict['sim'].sel(freqs=slice(*freq_lims[freq_label]))
        
        STAT_DS = stats_for_each_calib_period(DS_obs, DS_sim, freq_label, campaign)

        STAT_DS = add_global_attrs(STAT_DS, campaign, pamtra_settings)
        STAT_DS.attrs['instrument'] = freq_label

        # time encoding
        for var in ['calibration_period_start', 'calibration_period_end']:
            STAT_DS[var] = STAT_DS[var].values.astype("datetime64[s]").astype(np.float64)
            STAT_DS[var].attrs['units'] = "seconds since 1970-01-01 00:00:00"
            STAT_DS[var].encoding['units'] = 'seconds since 1970-01-01 00:00:00'
            STAT_DS[var].encoding['dtype'] = 'double'

        filename = f"{campaign}_{freq_label}_radiometer_clear_sky_offset_correction"
        file_save = path_output + filename + ".nc"
        
        os.makedirs(path_output, exist_ok=True)
        STAT_DS.to_netcdf(file_save, mode='w', format="NETCDF4")
        STAT_DS = STAT_DS.close()
        print(f"Saved {file_save}")

    print("Done")


if __name__ == "__main__":
    main()