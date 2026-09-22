"""
Quicklook of FLIR camera statistics. The statistics need to be computed first.
"""

import os
import sys
import pdb
from glob import glob

import cmcrameri.cm as cmc
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from skimage.io import imread as sk_imread

from vampire.io.readers.flir import read_flir_statistics

campaign = "VAMPIRE2"
if campaign == "VAMPIRE":
    from vampire.constants import Constants as Constants
elif campaign == 'VAMPIRE2':
    from vampire.constants import Constants_PS149 as Constants        

matplotlib.use("TkAgg")


def main(date):
    """
    Plot FLIR quicklooks for a specific date.
    """

    try:
        ds = read_flir_statistics(date, campaign_name=Constants.CAMPAIGN_NAME)
        quicklook_flir(date, ds, show=True, save=False)

    except FileNotFoundError:
        print(f"No FLIR statistics found for {date}.")


def number2file(video, frame, campaign_name_long=campaign):
    """
    Get FLIR image png file for a given frame number and video number.
    """

    # map video number to file name
    if isinstance(video, int):
        video_unique = np.array([video])
    else:
        video_unique = np.unique(video)
    base_name = {}
    for v in video_unique:
        base_name[v] = glob(
            os.path.join(
                os.environ["VAMPIRE_DATA"],
                f"flir/flir_png/*",
                f"{campaign_name_long}-Rec-A315_48001241-*-{str(v).zfill(5)}-IR_1.png",
            )
        )[0]

    # modify frame number of the file name
    if isinstance(video, int):
        return base_name[video].replace("1.png", f"{str(frame)}.png")

    else:
        files = []
        for i in range(len(video)):
            files.append(
                base_name[video[i]].replace("1.png", f"{str(frame[i])}.png")
            )
        return files


def number2file_fast(video: int, frame: int, campaign_name_long=campaign):
    
    time_str_video_no = glob(os.path.join(os.environ['VAMPIRE_DATA'],
                                          "flir/flir_timestamp/",
                                          f"{campaign_name_long}-Rec-A315_48001241-*-{video:05}-IR_times.csv"))
    if len(time_str_video_no) != 1: pdb.set_trace()
    time_str_video_no = os.path.basename(time_str_video_no[0]).split('-')[-3]
    
    flir_file_str = (f"{campaign_name_long}-Rec-A315_48001241-{time_str_video_no}-{video:05}-" + 
                     f"IR_{frame}.png")
    file = glob(os.path.join(os.environ['VAMPIRE_DATA'],
                             f"flir/flir_png/*",
                             flir_file_str))
    if len(file) != 1: pdb.set_trace()
    
    return file[0]


def flir_image(ds, time, campaign_name_long="VAMPIRE"):
    """
    Plot FLIR image at a given time from the time stamp in the FLIR statistics or time series
    dataset.
    """

    # get frame and video number at given time
    ds_img = ds.sel(time=time, method="nearest")

    # read the image png file
    file = number2file_fast(
        video=ds_img.video.item(),
        frame=ds_img.frame.item(),
        campaign_name_long=campaign_name_long,
    )
    img = sk_imread(file)

    plot_flir_image(img, time)


def get_flir_image(ds, time, campaign_name_long="VAMPIRE", return_file=False):
    """
    Return FLIR image at a given time from the time stamp in the FLIR statistics
    dataset as an array with IR TB in Kelvin.
    """

    # get frame and video number at given time
    ds_img = ds.sel(time=time, method="nearest")

    # read the image png file
    file = number2file_fast(
        video=ds_img.video.item(),
        frame=ds_img.frame.item(),
        campaign_name_long=campaign_name_long,
    )
    img = sk_imread(file)

    if return_file:
        return file, img * 10 ** (-2)
    else:
        return img * 10 ** (-2)


def plot_flir_image(
    img, time, imshow_kwargs=None, cbar_kwargs=None, show=True
):
    """
    Plot FLIR image
    """

    if imshow_kwargs is None:
        imshow_kwargs = {
            "cmap": cmc.lipari,
        }

    if cbar_kwargs is None:
        cbar_kwargs = {
            "label": "IR temperature [K]",
        }

    fig, ax = plt.subplots(1, 1, figsize=(7, 4))

    fig.suptitle(f"FLIR image {str(time)}")

    ax.axis("off")

    im = ax.imshow(img * 1e-2, **imshow_kwargs)
    fig.colorbar(im, ax=ax, **cbar_kwargs)

    if show:
        plt.show()
    else:
        return fig


def quicklook_flir(date, ds, show=True, save=False):
    """
    Time series of FLIR camera statistics for one day.

    Parameters
    ----------
    date : pd.Timestamp
        Date to plot.
    ds : xr.Dataset
        Time series of temperature histograms and statistics.
    """

    date = pd.Timestamp(date)

    fig, ax = plt.subplot_mosaic(
        [["hist"], ["mean"], ["minmax"], ["std"]],
        figsize=(7, 5),
        layout="constrained",
        sharex=True,
    )

    t_slice = slice(
        date + pd.Timedelta(0, "D"),
        date + pd.Timedelta(1, "D"),
    )

    fig.suptitle(f"FLIR statistics {date.date()}")

    # histogram
    im = ax["hist"].pcolormesh(
        ds.time.sel(time=t_slice),
        ds.tb_bin,
        ds.hist.sel(time=t_slice).T / (240 * 320) / 0.1,
        cmap=cmc.batlow,
        vmin=0,
    )
    fig.colorbar(im, ax=ax["hist"], pad=-0.1, label="Density [K$^{-1}$]")

    ax["hist"].axhline(273.15, color="k", linestyle=":")
    ax["hist"].set_ylim(
        ds.tb_min.sel(time=t_slice)
        .resample({"time": "5min"})
        .mean()
        .min()
        .item(),
        ds.tb_max.sel(time=t_slice)
        .resample({"time": "5min"})
        .mean()
        .max()
        .item(),
    )

    # mean
    ax["mean"].scatter(
        ds.time.sel(time=t_slice),
        ds.tb_mean.sel(time=t_slice),
        s=5,
        lw=0,
        color="k",
        label="mean",
    )
    ax["mean"].axhline(273.15, color="k", linestyle=":")
    leg = ax["mean"].legend(
        loc="center left", bbox_to_anchor=(1, 0.5), frameon=False
    )
    leg.set_in_layout(False)

    # min and max
    ax["minmax"].scatter(
        ds.time.sel(time=t_slice),
        ds.tb_max.sel(time=t_slice),
        s=5,
        lw=0,
        color="coral",
        label="max",
    )
    ax["minmax"].scatter(
        ds.time.sel(time=t_slice),
        ds.tb_min.sel(time=t_slice),
        s=5,
        lw=0,
        color="blue",
        label="min",
    )
    ax["minmax"].axhline(273.15, color="k", linestyle=":")
    ax["minmax"].legend(
        loc="center left", bbox_to_anchor=(1, 0.5), frameon=False
    )
    leg.set_in_layout(False)

    # standard deviation
    ax["std"].scatter(
        ds.time.sel(time=t_slice),
        ds.tb_std.sel(time=t_slice),
        s=5,
        lw=0,
        color="k",
        label="std",
    )
    ax["std"].set_ylim(bottom=0)
    ax["std"].legend(loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)
    leg.set_in_layout(False)

    ax["hist"].set_ylabel("T [K]")
    ax["mean"].set_ylabel("T [K]")
    ax["minmax"].set_ylabel("T [K]")
    ax["std"].set_ylabel("Std(T) [K]")
    ax["std"].set_xlabel("Time")

    ax["std"].xaxis.set_major_locator(mdates.HourLocator(interval=3))
    ax["std"].xaxis.set_minor_locator(mdates.HourLocator(interval=1))
    ax["std"].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax["std"].set_xlim(date, date + pd.Timedelta(24 * 3600 - 1, "s"))

    if save:
        file = os.path.join(
            os.environ["PATH_PLOTS"],
            "quicklooks/flir",
            f"flir_quicklook_{date.strftime('%Y%m%d')}.png",
        )
        print(f"Writing FLIR plot {file}")
        plt.savefig(
            file,
            dpi=300,
            bbox_inches="tight",
        )

    if show:
        plt.show()

    plt.close()


if __name__ == "__main__":
    main(date=sys.argv[1])
