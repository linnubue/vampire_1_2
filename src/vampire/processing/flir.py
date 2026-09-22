"""
Computes daily statistics time series of FLIR infrared images.

Description
-----------
The input for this script are FLIR images in png 16-bit format, scaled with a
factor of 100. These images are exported manually with the FLIR research studio
software. The other input are time stamps from these images, which are 
extracted with another script from the FLIR seq binary files.

First, statistics (mean, min, max, std, histogram, center pixel) are computed
from the png images. In a second step, the time stamp is added to the dataset
and the data is stored in daily netcdf files. The camera settings changed 
during the campaigns and some times needed to be fixed manually.

Improvements
------------
More statistics can be added. And artifacts could be removed first when 
calculating the statistics, e.g., lens effects, vertical stripes. Also, times 
when lense is cleaned or people stand inside the image could be flagged. 
Finally, the temperature should be offset corrected using the in situ 
temperature measurements.
"""

import os
import sys
import pdb
import re
from glob import glob

import cmcrameri.cm as cmc
import dask
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from dask.array.image import imread
from dask.diagnostics import ProgressBar
from tqdm import tqdm

from vampire.constants import Constants

ProgressBar().register()

if Constants.CAMPAIGN_NAME == "PS144":
    campaign_name_long = "VAMPIRE"
elif Constants.CAMPAIGN_NAME == "PS149":
    campaign_name_long = "VAMPIRE2"


flir_img_dims = (240,320)

def calculate_statistics(start_doy, hist_dt, hist_tmin, hist_tmax):
    """
    Calculate statistics of all FLIR images with dask.
    """

    path = os.path.join(os.environ["VAMPIRE_DATA"], "flir/flir_png")
    with os.scandir(path) as path_scan: # faster than walking through everything; we can assume that no subdirs exist in 
                                        # each folder within path
        folders = sorted([p_s.name for p_s in path_scan if p_s.is_dir()])

    for folder in tqdm(folders):

        # skip day of year below the given day of year
        if int(folder.split("_")[0]) < start_doy:
            continue

        file_pattern_flir = os.path.join(
            path,
            folder,
            f"{campaign_name_long}-Rec-A315_48001241-*.png",
        )
        images_flir = imread(file_pattern_flir)
        images_flir = images_flir.rechunk("auto")

        comp = process_images(
            images_flir,
            hist_dt=hist_dt,
            hist_tmin=hist_tmin,
            hist_tmax=hist_tmax,
        )

        # get information from filename
        files_flir = sorted(glob(file_pattern_flir))
        df_info = get_filename_info(files_flir)

        # write to xarray dataset
        ds = xr.Dataset()

        ds.coords["video_frame"] = (
            df_info["video_number"].astype("str").str.zfill(5)
            + "_"
            + df_info["frame_number"].astype("str").str.zfill(5)
        ).values
        ds.coords["tb_bin"] = np.arange(
            hist_tmin, hist_tmax + hist_dt / 2, hist_dt
        )

        ds["video"] = ("video_frame", df_info["video_number"].astype(np.int32))
        ds["frame"] = ("video_frame", df_info["frame_number"].astype(np.int32))
        ds["time_video"] = ("video_frame", df_info["time_video"])

        ds["tb_center"] = ("video_frame", comp[0][0] * 1e-2)
        ds["tb_mean"] = ("video_frame", comp[0][1] * 1e-2)
        ds["tb_std"] = ("video_frame", comp[0][2] * 1e-2)
        ds["tb_min"] = ("video_frame", comp[0][3] * 1e-2)
        ds["tb_max"] = ("video_frame", comp[0][4] * 1e-2)
        ds["hist"] = (("video_frame", "tb_bin"), comp[0][5].astype(np.int32))

        # sort by frame
        ds = ds.isel(video_frame=np.argsort(ds.frame).values)

        # global attributes
        author = "Nils Risse"
        if Constants.CAMPAIGN_NAME == "PS149":
            author += ", Andreas Walbröl"
            folder = df_info['date_str'][0]
        
        ds.attrs = {
            "title": "FLIR infrared camera statistics",
            "description": (
                "Statistics and histogram of infrared temperature "
                f"observed with FLIR camera during {Constants.CAMPAIGN_NAME}."
            ),
            "comment": (
                "The original image can be found based on the unique "
                "combination of frame number and video number."
            ),
            "campaign": f"{Constants.CAMPAIGN_NAME}, VAMPIRE project",
            "platform": "Polarstern",
            "created": str(np.datetime64("now")),
            "author": "Nils Risse",
            "history": f"Created from png files of video '{folder}'",
        }

        file = os.path.join(
            os.environ["VAMPIRE_DATA"],
            "flir/stats",
            f"{campaign_name_long}_flir_statistics_{folder}.nc",
        )
        ds.to_netcdf(file)


def make_daily_files():
    """
    Add time to FLIR statistics data files and convert them to daily files.

    This script was developed to roughly get the time of images assuming a
    constant frame rate. Maybe with new camera settings it is becoming more
    accurate. Currently, deviations of +/-30 s are possible.

    Correction is linear. Assuming start time is always correct and 1 s
    between videos that are not manually stopped. For manually stopped videos,
    the offset per frame of a neighboring frame is used.

    Assume constant recording rate.

    VAMPIRE video time details:

    - All videos >= 68 (239_10) have the correct time stamp and need no correction

    The following measurements were stopped manually and need to be corrected
    with a mean value:

    - Video 2 (2841 frames) -> like Video 1
    - Video 4 (17804 frames) -> like Video 5
    - Video 46 (21600 frames)
    - Video 47 (3815 frames)
    - Video 50 (7 frames)
    - Video 51 (3600 frames)
    - Video 67 (239_08)

    Other special things:

    - Video 48 has no frames and is not in the dataset
    """

    ds = xr.open_mfdataset(
        os.path.join(
            os.environ["VAMPIRE_DATA"],
            "flir/stats",
            f"{campaign_name_long}_flir_statistics_*.nc",
        ),
        concat_dim="video_frame",
        preprocess=add_time,
        combine="nested",
    )
    ds = ds.sortby('time')

    # load relevant parameters to memory for time stamp correction
    ds_time = ds[["time", "video", "frame"]].load()
    ds_time = time_correction(ds_time)
    ds["time"] = ds_time["time"]  # set time on the larger dataset

    # set time as coordinate
    ds = ds.swap_dims({"video_frame": "time"}).reset_coords(drop=True)
    ds = ds.drop_vars("time_video")

    # store daily netcdf files
    dates = pd.date_range(Constants.DATE_START, Constants.DATE_END, freq="1D")
    for date in dates:
        print(date)
        t0 = date
        t1 = date + pd.Timedelta(24 * 3600 - 1, "s")
        ds_slice = ds.sel(time=slice(t0, t1))

        if len(ds_slice.time) > 0:
            file = os.path.join(
                os.environ["VAMPIRE_DATA"],
                "flir/time_series",
                f"{campaign_name_long}_flir_statistics_{date.strftime('%Y%m%d')}.nc",
            )
            print(f"Writing file for {t0} to {t1}: {file}.")
            ds_slice.to_netcdf(file)
        else:
            print(f"No data for {date}")


def time_correction(ds):
    """
    Time correction of FLIR images.
    """
    
    def apply_time_offset(offset, time, frame, ix):
        
        time_cor = (time.loc[{"video_frame": ix}]
                    + (offset * 1e9).astype("timedelta64[ns]")
                    * (frame.loc[{"video_frame": ix}] + 1)).values
        return time_cor

    # basic checks
    assert ds.time.diff("video_frame").min() > np.timedelta64(0, "s")
    assert ds.time.max() <= Constants.DATE_END
    assert ds.time.min() >= Constants.DATE_START

    # get time difference between videos
    da_from = ds.video.diff("video_frame", label="lower") > 0
    da_to = ds.video.diff("video_frame", label="upper") > 0
    da_from = da_from.sel(video_frame=da_from)
    da_to = da_to.sel(video_frame=da_to)

    # time difference between frames (keeps index of from video)
    dt_sec = (
        ds.time.sel(video_frame=da_to.video_frame).values
        - ds.time.sel(video_frame=da_from.video_frame)
    ) * 1e-9
    dt_sec = dt_sec.assign_coords(
        {"video_frame": ds.video.sel(video_frame=dt_sec.video_frame)}
    )
    dt_sec = dt_sec.rename({"video_frame": "video"})
    dt_sec = (
        dt_sec - 1
    )  # this ensures that 1s increment remains after correction

    # number of samples in previous frame
    frame = ds.frame.sel(video_frame=da_from.video_frame).values + 1

    # video number of previous frame
    video = ds.video.sel(video_frame=da_from.video_frame).values

    # average frame rate
    n_frames = ds.frame.groupby(ds.video).max() + 1
    duration = (
        ds.time.groupby(ds.video).max() - ds.time.groupby(ds.video).min()
    )
    duration_h = (duration / np.timedelta64(1, "h")).values
    duration_s_per_frame = (
        duration / np.timedelta64(1, "s") / n_frames
    ).values

    # print everything to get an overview
    for i in range(len(video)):
        print(
            video[i],
            frame[i],
            duration_h[i],
            dt_sec.values[i],
            duration_s_per_frame[i],
        )

    # videos that are not optimized
    if Constants.CAMPAIGN_NAME == "PS144":
        not_optimize = np.array([2, 4, 46, 47, 48, 50, 51, 67])  # and all >= 68
        optimize = np.arange(1, 68)
        optimize = optimize[~np.isin(optimize, not_optimize)]
        optimize = optimize[np.isin(optimize, np.unique(ds.video.values))]
        
        # get the time difference for these and add a linear offset
        time_offset = dt_sec.sel(video=optimize).astype("float") / n_frames
        
        # add the time offset to each frame of the given video
        ix = np.isin(ds.video, optimize)
        offset = time_offset.sel(video=ds.video.sel(video_frame=ix))
        ds["time"].loc[{"video_frame": ix}] = apply_time_offset(offset, 
                                                                ds["time"], 
                                                                ds["frame"], 
                                                                ix)
        
        # correct manually interrupted videos with a mean offset
        ix = np.isin(ds.video, not_optimize)
        mean_offset = offset.mean()
        ds["time"].loc[{"video_frame": ix}] = apply_time_offset(mean_offset, 
                                                                ds["time"],
                                                                ds["frame"],
                                                                ix)

    return ds


def get_time(time_str, video):
    """
    Reads the time of each frame of a video. This time was extracted from the
    binary files. The function needs some parameters to create the filename.

    Parameters
    ----------
    time_str : str
       String like "223_13_15_00_019".
    video : int
       Video number.
    """

    # read flir image time from file
    df = pd.read_csv(
        os.path.join(
            os.environ["VAMPIRE_DATA"],
            "flir/flir_timestamp",
            f"{campaign_name_long}-Rec-A315_48001241-{time_str}-{str(video).zfill(5)}-IR_times.csv",
        ),
        header=None,
    )
    time = (
        np.datetime64("1970-01-01")
        + df.iloc[:, 0].astype("timedelta64[s]")
        + df.iloc[:, 1].astype("timedelta64[ms]")
    )

    return time


def add_time(ds):
    """
    Adds time from csv files to dataset. Assumes that both are ordered by
    frame number.
    """
    
    
    ds_filename = os.path.basename(ds.encoding["source"])
    time_str = re.search(r'[0-3][0-9][0-9]_[0-2][0-9]_[0-5][0-9]_[0-5][0-9]_[0-9][0-9][0-9]', ds_filename).group()
    video = ds.video.isel(video_frame=0).values
    time = get_time(time_str=time_str, video=video)

    if (len(time) != len(ds.video_frame)) & (("_A" in ds_filename) | ("_B" in ds_filename)):
        mask = np.isin(time.index.values, ds.frame.values)
        time = time[mask]
        
    assert len(time) == len(
        ds.video_frame
    ), f"Number of frames ({len(ds.video_frame)}) does not match number of times ({len(time)})"
    ds["time"] = ("video_frame", time)

    return ds


def process_images(images_flir, hist_dt, hist_tmin, hist_tmax):

    bin_edges = (
        np.arange(hist_tmin - hist_dt / 2, hist_tmax + hist_dt, hist_dt) * 100
    )
    tb_hist = np.apply_along_axis(
        compute_histogram,
        1,
        images_flir.reshape(len(images_flir), flir_img_dims[0] * flir_img_dims[1]),
        bin_edges,
    )

    tb_center = images_flir[:, int(round(flir_img_dims[0]*0.5)), int(round(flir_img_dims[1]*0.5))]
    tb_mean = images_flir.mean(axis=[1, 2])
    tb_std = images_flir.std(axis=[1, 2])
    tb_min = images_flir.min(axis=[1, 2])
    tb_max = images_flir.max(axis=[1, 2])

    comp = dask.compute((tb_center, tb_mean, tb_std, tb_min, tb_max, tb_hist))

    return comp


def compute_histogram(arr, bins):
    hist, _ = np.histogram(arr, bins=bins)
    return hist


def get_filename_info(files_flir):
    """
    Extract information from filename.

    Example file: ``VAMPIRE-Rec-A315_48001241-229_14_38_53_800-00024-IR_0.png``
    """

    refyear = 2024
    if Constants.CAMPAIGN_NAME == "PS149":
        refyear = 2025

    df = pd.DataFrame()
    df["file"] = files_flir
    df["frame_number"] = (
        df["file"].str.split("_", expand=True).iloc[:, -1].str.replace(".png", "").astype(int)
    )
    filenames_split1 = df["file"].str.split("-", expand=True)
    df["video_number"] = (
        filenames_split1.iloc[:, -2].astype(int)
    )
    df["date_str"] = filenames_split1.iloc[:, -3]

    date_names = ["doy", "hh", "mm", "ss", "ms"]
    df[date_names] = df["date_str"].str.split("_", expand=True)
    df["doy"] = df["doy"].astype(int)

    df["date"] = np.datetime64(f"{refyear}-01-01") + (
        (df["doy"] - 1) * 24 * 3600
    ).astype("timedelta64[s]")
    assert (df["date"].dt.dayofyear == df["doy"]).all()

    df["time_video"] = (
        pd.to_datetime(
            df["hh"] + df["mm"] + df["ss"] + df["ms"], format="%H%M%S%f"
        )
        - pd.Timestamp("1900-01-01")
    ) + df["date"]

    return df


def plot_residual(time):
    """
    Plot TB residual for one hour of FLIR data.
    """

    # TODO: this script should be run with all FLIR images.

    ds_mean_t = ds["tb"].astype("float32").mean("time")
    ds_mean_txy = ds["tb"].astype("float32").mean(["time", "x", "y"])
    ds_mean_tx = ds["tb"].astype("float32").mean(["time", "x"])
    ds_mean_ty = ds["tb"].astype("float32").mean(["time", "y"])
    ds_res_x = ds_mean_tx - ds_mean_txy
    ds_res_y = ds_mean_ty - ds_mean_txy
    ds_res = ds_mean_t - ds_mean_txy

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(6, 5),
        height_ratios=[1, 3],
        width_ratios=[3, 1],
        sharex="col",
        sharey="row",
        layout="constrained",
    )
    axes[0, 1].remove()
    axes[0, 0].plot(ds.y, ds_res_x)
    axes[1, 1].plot(ds_res_y, ds.x)
    im = axes[1, 0].imshow(ds_res, vmin=-0.75, vmax=0.75, cmap=cmc.bam)
    fig.colorbar(
        im,
        ax=axes[1, 0],
        orientation="horizontal",
        label="$\Delta T_b$ [K]",
        shrink=0.5,
    )

    axes[1, 0].set_xlabel("y")
    axes[1, 0].set_ylabel("x")
    axes[0, 0].set_ylabel("$\Delta T_b$ [K]")
    axes[1, 1].set_xlabel("$\Delta T_b$ [K]")

    plt.savefig(
        os.path.join(
            os.environ["PATH_PLOTS"],
            f"flir_residual{time.strftime('%Y%m%d_%H%M%S')}.png",
        )
    )


if __name__ == "__main__":
    if len(sys.argv) == 1: sys.argv.append("0")
    calculate_statistics(
        start_doy=int(sys.argv[1]), hist_dt=0.1, hist_tmin=260, hist_tmax=295
    )
    make_daily_files()
