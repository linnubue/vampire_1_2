import sys
import os
import glob
import pdb

import numpy as np
import xarray as xr
import matplotlib as mpl
import matplotlib.pyplot as plt

remote_exe = False

def main(instr="hatpro", obs_type="ZENITH", campaign="PS144", daily_folders=False):
    
    path_data = build_path_data(instr, obs_type, campaign)
    
    files = sorted(glob.glob(path_data + "*.nc"))
    if campaign == "PS149":
        date_range = np.arange(np.datetime64("2025-07-01"), np.datetime64("2025-10-16"), 
                               np.timedelta64(1, "D"))
    elif campaign == "PS144":
        date_range = np.arange(np.datetime64("2024-08-09"), np.datetime64("2024-10-12"), 
                               np.timedelta64(1, "D"))
    if remote_exe: daily_folders = True
    
    for date in date_range:
        date_yyyymmdd = str(date.astype('datetime64[D]')).replace("-","")
        
        if daily_folders or remote_exe:
            path_date = path_data + "/".join(str(date).split('-')) + "/"
            files = sorted(glob.glob(path_date + "*.nc"))
        file = [file for file in files if ("_" + date_yyyymmdd) in file]

        if len(file) > 1:
            file = [ff for ff in file if "_mwr0" in ff]
            if len(file) > 1: pdb.set_trace()
        elif len(file) == 0:
            continue
        
        date_str = str(date.astype('datetime64[D]'))
        print(date_str)
        DS = xr.open_dataset(file[0]).load()
        if obs_type in ['ZENITH', ""]:
            plot_data(DS, instr, date_str)
        elif obs_type == "BL-SCAN":
            plot_data_bl(DS, instr, date_str)
            
            
def build_path_data(instr="hatpro", obs_type="ZENITH", campaign="PS144"):

    path_label_obs_type = ""
    if obs_type == "ZENITH":
        path_label_obs_type = "atm"
    elif obs_type == "BL-SCAN":
        path_label_obs_type = "atm_bl"
    elif obs_type == "":
        path_label_obs_type = "atm_transit"
    campaign_label = "vampire"
    if campaign == "PS149": campaign_label = "VAMPIRE2"
    
    path_base = os.environ['VAMPIRE_DATA']
    path_data = path_base + f"{campaign_label}/{instr}/{path_label_obs_type}/l1/"
    
    return path_data
        

def plot_data(DS: xr.Dataset, instr="hatpro", date_str="2024-08-10"):
    
    f1, axs = plt.subplots(3,1, sharex=True, figsize=(12,8))
    
    plt.subplots_adjust(right=0.8)
    
    if instr == "hatpro":
        for k in range(0,7):
            axs[0].plot(DS.time, DS.tb[:,k], label=f"{DS.freq_sb.values[k]:.2f} GHz")
        for k in range(7,14):
            axs[1].plot(DS.time, DS.tb[:,k], label=f"{DS.freq_sb.values[k]:.2f} GHz")
    
    elif instr == "mirac-p":
        for k in range(0,6):
            axs[0].plot(DS.time, DS.tb[:,k], label=f"{DS.freq_sb.values[k]:.2f} GHz")
        for k in range(6,8):
            axs[1].plot(DS.time, DS.tb[:,k], label=f"{DS.freq_sb.values[k]:.2f} GHz")
            
    axs[2].plot(DS.time, DS.ele, color=(0,0,0), linewidth=1.25)
    axs[0].set_title(date_str)
    
    for ax in axs:
        lh, ll = ax.get_legend_handles_labels()
        ax.legend(lh,ll, loc='upper left', bbox_to_anchor=(1.02, 1.0))
        
    plt.show()
    pdb.set_trace()
    plt.close()


def plot_data_bl(DS: xr.Dataset, instr="hatpro", date="2024-08-10"):
    
    ele_unique = np.unique(DS.ele)
    n_ele = len(ele_unique)
    n_rows = int(np.ceil(n_ele/2))
    f1, axs = plt.subplots(n_rows,2, sharex=True, figsize=(12,10))
    axs = axs.flatten()
    
    plt.subplots_adjust(left=0.05, right=0.8, wspace=0.5)
    
    if instr == 'hatpro':
        freq_idx = [0,7]
    elif instr == 'mirac-p':
        freq_idx = [-3,-2]
    for k, ele in enumerate(np.unique(ele_unique)):
        ds_ele = DS.sel(time=DS.ele == ele)
        
        axs[k].text(0.0, 1.0, f"{ele:.2f} deg", ha='left', va='bottom', transform=axs[k].transAxes)
        
        for freq_i in freq_idx:
            axs[k].plot(ds_ele.time, ds_ele.tb[:,freq_i], linestyle='none', marker='.',
                        label=f"{ds_ele.freq_sb.values[freq_i]:.2f} GHz")
        
            
    axs[0].set_title(date)
    
    for ax in axs:
        lh, ll = ax.get_legend_handles_labels()
        ax.legend(lh,ll, loc='upper left', bbox_to_anchor=(1.02, 1.0))
        
    plt.show()
    pdb.set_trace()
    plt.close()


if __name__ == "__main__":
    instr = "mirac-p"
    obs_type = ""
    campaign = "PS144"
    daily_folders = True
    main(instr=instr, obs_type=obs_type, campaign=campaign, daily_folders=daily_folders)