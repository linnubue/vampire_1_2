"""
Identifies microwave radiometer antenna pattern in camera images by correlating 
camera pixels with TB. The idea is that camera pixels in the center of the
antenna pattern have a higher correlation coefficient with the TB than those
at the edge or outside of the antenna pattern.

Algorithm description:

- read time series of each camera pixel and radiometer channel
- correlate each camera pixel with each radiometer channel
- separate correlation of camera pixels with each other from correlation of camera pixels with radiometer channels
- plot image of correlation coefficients, which should show the radiometer antenna pattern

Note:
    This is a proof of concept based on WALSEMA observations. The radiometer
    data format and the camera format might differ for VAMPIRE, but the 
    algorithm should work the same.

Improvements:

- consider ship motion, which stretches the antenna pattern
"""

from glob import glob
import os

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import cmcrameri.cm as cmc
from dask.diagnostics import ProgressBar
from dask.array.image import imread

from vampire.io.readers.gopro import read_rescaled, get_all_times
from vampire.io.readers.mwr import read_dual, read_tb_surface_walsema, read_scan
from vampire.io.readers.flir import read_flir_csv
from vampire.constants import Constants

ProgressBar().register()


def main_vampire_gopro():
    """
    Correlation for vampire data with FLIR IR camera
    """

    # TODO Provide then one cell for the 53 degrees scans and one for the various
    # angles
    # also, add some statistics for these scans, not just the correlation with
    # ir and vis. or maybe in a separate notebook.

    # date = np.datetime64("2024-08-14")
    # ds_tb = read_dual(date, scan="EMIS", keep_mismatch=True, keep_atmos=False)
    ds = read_dual(
        d0=Constants.DATE_START_ICE,
        d1=pd.Timestamp("2024-08-29"),
        scan="EMIS-SCAN",
        keep_mismatch=True,
        keep_atmos=False,
    )

    # read gopro images with dask and the corresponding time
    files = os.path.join(
        os.environ["VAMPIRE_DATA"],
        f"gopro/*/GOPRO_{Constants.CAMPAIGN_NAME}_GPS_date_*.JPG_rescaled.JPG",
    )
    images = imread(files)

    # select the time that aligns with radiometers
    times = get_all_times(sorted(glob(files)))
    ix = np.isin(times, ds.time.values)
    times = times[ix]
    images = images[ix]

    # TODO: convert images to dask xarray dataset
    ds_vis = xr.Dataset()
    ds_vis.coords["time"] = times
    ds_vis.coords["x"] = np.arange(images.shape[1])
    ds_vis.coords["y"] = np.arange(images.shape[2])
    ds_vis.coords["channel"] = np.arange(images.shape[3])
    ds_vis["gopro"] = (("time", "x", "y", "channel"), images)
    ds_vis["gopro"] = ds_vis["gopro"].chunk(
        {"time": 1, "x": 10, "y": 10, "channel": 3}
    )

    for angle in np.arange(25, 75, 10):

        print(f"Correlation for angle {angle} degrees")
        ds_ang = ds.where(ds.ElAng == angle)

        # match temporally
        ds_vis_match, ds_ang_match = xr.align(ds_vis, ds_ang)

        # correlate
        da_corr = make_correlation(
            ds_vis_match.gopro.sel(channel=0),
            ds_ang_match.TBs,
        )
        da_corr = da_corr.compute()
        plot_footprint(
            da_corr,
            suffix=f"vampire_vis_emis_scan_{angle}",
            label="Corr(MW, VIS)",
        )


def main_vampire():
    """
    Correlation for vampire data with FLIR IR camera
    """

    date = np.datetime64("2024-08-14")

    ds_tb_hatpro = read_scan(date=date, instrument="hatpro", scan="EMIS")
    ds_tb_lhumpro = read_scan(date=date, instrument="mirac-p", scan="EMIS")
    # ds_tb_hatpro["ElAng"] = 180 - ds_tb_hatpro["ElAng"] # already done in read_scan
    ds_tb_hatpro = ds_tb_hatpro.sel(
        time=(ds_tb_hatpro.ElAng > 51) & (ds_tb_hatpro.ElAng < 55)
    )
    ds_tb_lhumpro = ds_tb_lhumpro.sel(
        time=(ds_tb_lhumpro.ElAng > 51) & (ds_tb_lhumpro.ElAng < 55)
    )
    ds_tb = xr.concat([ds_tb_hatpro, ds_tb_lhumpro], dim="number_frequencies")
    ds_tb = ds_tb.sel(time=~ds_tb.TBs.isnull().any("number_frequencies"))

    ds_ir = read_flir_csv(date, find_times=ds_tb.time.values)       # comment: no longer exists

    time_gopro = get_all_times()
    gopro_match = np.isin(time_gopro, ds_tb.time.values)
    time_gopro_match = time_gopro[gopro_match]
    da_vis = gopro2da(time_gopro_match)

    # keep only unique flir times (decimal seconds where dropped)
    _, ix = np.unique(ds_ir["time"].values, return_index=True)
    ds_ir = ds_ir.isel(time=ix)

    # keep only images with larger temperature gradients
    # ds_ir = ds_ir.sel(time=(ds_ir.max(["x", "y"]) - ds_ir.min(["x", "y"])) > 2)

    # match temporally
    ds_ir, ds_tb = xr.align(ds_ir, ds_tb)

    # plot time series
    fig, axes = plt.subplots(2, 1, sharex=True)
    axes[0].scatter(
        ds_tb.time, ds_tb.TBs.isel(number_frequencies=1), s=10, lw=0, color="k"
    )
    axes[1].scatter(
        ds_ir.time, ds_ir.isel(x=120, y=160), s=10, lw=0, color="k"
    )
    # axes[0].set_xlim(np.datetime64("2024-08-14 03:09"), np.datetime64("2024-08-14 03:11"))
    # axes[0].set_xlim(np.datetime64("2024-08-14 04:38"), np.datetime64("2024-08-14 04:42"))
    plt.show()

    # TODO: this is a test with less data
    t0, t1 = np.datetime64("2024-08-14 02:39"), np.datetime64(
        "2024-08-14 02:41"
    )
    ds_ir = ds_ir.sel(time=slice(t0, t1))
    ds_tb = ds_tb.sel(time=slice(t0, t1))

    # plot all instances
    for i in range(len(ds_ir.time)):
        print(i)
        fig, axs = plt.subplots(
            2, 1, figsize=(6, 4), height_ratios=[1, 3], layout="constrained"
        )
        axs[0].set_title(ds_tb.time.isel(time=i).values)
        axs[0].scatter(
            ds_tb.Freq, ds_tb.TBs.isel(time=i), s=10, lw=0, color="k"
        )
        im = axs[1].imshow(
            ds_ir.isel(time=i), vmin=275, vmax=278, cmap=cmc.batlow
        )
        fig.colorbar(im, ax=axs[1], label="IR temperature [K]")
        axs[0].set_ylim(150, 300)
        plt.savefig(
            os.path.join(
                os.environ["PATH_PLOTS"],
                "tb_ir",
                f"tb_ir_{str(i).zfill(4)}.png",
            ),
            dpi=300,
        )
        plt.close()

    # correlate
    da_corr = make_correlation(
        ds_ir.chunk({"x": 100, "y": 100}),
        ds_tb.TBs.chunk({"number_frequencies": 1}),
    )
    da_corr = da_corr.compute()
    plot_footprint(
        da_corr, suffix=f"vampire_ir_{pd.Timestamp(date).strftime('%Y%m%d')}"
    )

    # correlated with rescaled ir image
    ds_ir_scaled = (ds_ir - ds_ir.quantile(0.01, ["x", "y"])) / (
        ds_ir.quantile(0.99, ["x", "y"]) - ds_ir.quantile(0.01, ["x", "y"])
    )

    da_corr_scaled = make_correlation(
        ds_ir_scaled.chunk({"x": 100, "y": 100}),
        ds_tb.TBs.chunk({"number_frequencies": 1}),
    )
    da_corr_scaled = da_corr_scaled.compute()
    plot_footprint(
        da_corr_scaled,
        suffix=f"vampire_irscaled_{pd.Timestamp(date).strftime('%Y%m%d')}",
        label="Corr(MW, IR)",
    )


def main():
    """
    Identify antenna pattern from camera images
    """

    print("start")

    ds_hatpro = read_tb_surface_walsema("2022-07-18", instrument="hatpro")
    ds_mirac_p = read_tb_surface_walsema("2022-07-18", instrument="mirac-p")

    # combine both radiometer data sets
    ds = xr.concat([ds_hatpro, ds_mirac_p], dim="number_frequencies")

    ds = ds.sel(time=slice("2022-07-18 14:00:00", "2022-07-18 19:00:00"))

    # gets gopro images where radiometer measures surface tb
    times_gopro = get_all_times()
    times_selection = times_gopro[np.isin(times_gopro, ds.time)]
    times_selection = np.sort(times_selection)

    print(len(times_selection))

    da_img = gopro2da(times=times_selection)

    # align radiometer tb and image times
    da_img, ds = xr.align(da_img, ds)

    da_tb = ds.TBs

    da_corr = make_correlation(da_img, da_tb)


def gopro2da(times):

    # read rescaled gopro images
    imgs = [read_rescaled(time)[:, :, 0] for time in times]

    # concatenate images
    img = np.stack(imgs)

    # write images to xarray data array with time as dimension
    da_img = xr.DataArray(img, dims=("time", "y", "x"), coords={"time": times})

    return da_img


def plot_footprint(da_corr, suffix, label):
    """
    Plot correlations picture for each channel.
    """

    print("Plotting")
    fig, ax = plt.subplots(
        5, 5, figsize=(8, 8), sharey=True, sharex=True, constrained_layout=True
    )

    for i in da_corr.number_frequencies.values:

        # annotate frequency
        fig.axes[i].annotate(
            str(i + 1),
            xy=(0.5, 1),
            ha="center",
            va="bottom",
            xycoords="axes fraction",
        )

        fig.axes[i].set_xticks([])
        fig.axes[i].set_yticks([])

        im = fig.axes[i].imshow(
            da_corr.isel(number_frequencies=i),
            cmap=cmc.tofino,
            vmin=-1,
            vmax=1,
        )

    fig.colorbar(
        im,
        ax=fig.axes,
        orientation="horizontal",
        label=label,
    )

    plt.savefig(
        os.path.join(
            os.environ["PATH_PLOTS"], f"antenna_from_correlation_{suffix}.png"
        ),
        dpi=300,
    )


def make_correlation(da_img, da_tb):
    """
    Correlate camera pixels with radiometer channels. Expects time series of
    tb for different channels and an array of images from the camera.

    Parameters
    ----------
    da_img : xr.DataArray
        Camera images with dimensions (x, y, time).
    da_tb : xr.DataArray
        Tb with dimensions (time, number_frequencies).
    """

    da_corr = xr.corr(da_img, da_tb, dim="time")

    return da_corr


if __name__ == "__main__":
    main_vampire_gopro()
