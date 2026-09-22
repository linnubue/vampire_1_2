"""
Quicklooks for MWRs HATPRO and LHUMPRO.
"""

import glob
import os as os
import sys
import pdb
from datetime import datetime

import matplotlib as matplotlib
matplotlib.use("WebAgg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# import seaborn as sns
import xarray as xr

# from vampire.io.readers.flir import read_flir_statistics
from vampire.io.readers.mwr import open_mwr_file, read_scan
# from vampire.quicklooks.flir import get_flir_image

campaign = "vampire"
if campaign == "vampire":
    from vampire.constants import Constants as Constants
elif campaign == 'VAMPIRE2':
    from vampire.constants import Constants_PS149 as Constants

fontsizey = 24
fontsizex = 24
fontsizetix = 20
fontsizelegend = 18
fontsize_title = 24
msize = 2  ##markersize
mscale = 5


def get_mwr_scan(date, instrument: str, scan: str, daily_file: bool):
    
    try:
        ds = read_scan(date, instrument, scan, daily_file)
    except:
        ds = xr.Dataset(coords={'time': (['time'], np.array([np.datetime64(date.strftime("%Y-%m-%d"))])),
                                'Freq': (['Freq'], np.array([22.24, 23.04, 23.84, 25.44, 26.24, 27.84, 31.4,
                                                             51.26, 52.28, 53.86, 54.94, 56.66, 57.30, 58.0]))})
        ds['TBs'] = xr.DataArray(np.full((len(ds.time), len(ds.Freq)), np.nan), dims=['time', 'Freq'])
        ds['ElAng'] = xr.DataArray(np.full((len(ds.time),), np.nan), dims=['time'])
        
    return ds


def plot_mwr_daily_quicklook(
    date, scan, downwelling=False, show=True, save=False
):
    """
     plot_mwr_zenith_daily_quicklook(date,show=True, save=False)
    Time series of TB zenith measurement of HATPRO and LHUMPRO for one day
    date is the day the plot is created for
    scan is the scan type (ZENITH or EMIS), boundary layer scan has extra plotting function
    if downwelling is True and scan type is EMIS then the downwelling TB at 127 degrees are plotted.
    """

    hatpro_ds = get_mwr_scan(date, "hatpro", scan, daily_file=True)
    lhumpro_ds = get_mwr_scan(date, "mirac-p", scan, daily_file=True)
    Hatpro_frequencies = [
        22.24,
        23.04,
        23.84,
        25.44,
        26.24,
        27.84,
        31.4,
        51.26,
        52.28,
        53.86,
        54.94,
        56.66,
        57.3,
        58,
    ]

    Mirac_frequencies = lhumpro_ds.Freq.data
    if scan == "ZENITH":
        dates_hatpro = hatpro_ds.time.values
        TBs_hatpro = hatpro_ds.TBs.values
        dates_mirac = lhumpro_ds.time.values
        TBs_mirac = lhumpro_ds.TBs.values
        title = "MWR observation zenith"
        filename = "zenith"
    elif scan == "EMIS" and downwelling == False:
        dates_hatpro = hatpro_ds.time.values[hatpro_ds.ElAng == 53.0]
        TBs_hatpro = hatpro_ds.TBs.values[hatpro_ds.ElAng == 53.0]
        dates_mirac = lhumpro_ds.time.values[lhumpro_ds.ElAng == 53]
        TBs_mirac = lhumpro_ds.TBs.values[lhumpro_ds.ElAng == 53]
        title = "MWR surface observation 53° off-nadir"
        filename = "surface_53"
    elif scan == "EMIS" and downwelling == True:
        dates_hatpro = hatpro_ds.time.values[hatpro_ds.ElAng == 127.0]
        TBs_hatpro = hatpro_ds.TBs.values[hatpro_ds.ElAng == 127.0]
        dates_mirac = lhumpro_ds.time.values[lhumpro_ds.ElAng == 127.0]
        TBs_mirac = lhumpro_ds.TBs.values[lhumpro_ds.ElAng == 127.0]
        title = "MWR downwelling TB observation 127° off-nadir"
        filename = "downwelling_127"

    fig = plt.figure(figsize=(20, 20))
    
    plt.suptitle(f"{title}", x=0.5, y=0.9, fontsize=fontsize_title)
    gs = fig.add_gridspec(
        4, 1, hspace=0.45, wspace=0.05
    )  # width_ratios= [1,1,1,1],
    axkband = fig.add_subplot(gs[0, :])
    axkband.text(
        -0.1, 1.1, "a)", transform=axkband.transAxes, size=20, weight="bold"
    )
    axvband = fig.add_subplot(gs[1, :], sharex=axkband)
    axvband.text(
        -0.1, 1.1, "b)", transform=axvband.transAxes, size=20, weight="bold"
    )
    axmirac1 = fig.add_subplot(gs[2, :], sharex=axkband)
    axmirac1.text(
        -0.1, 1.1, "c)", transform=axmirac1.transAxes, size=20, weight="bold"
    )
    axmirac2 = fig.add_subplot(gs[3, :], sharex=axkband)
    axmirac2.text(
        -0.1, 1.1, "d)", transform=axmirac2.transAxes, size=20, weight="bold"
    )
    ###labels
    axmirac2.set_ylabel("TB (K)", fontsize=fontsizey)
    axmirac1.set_ylabel("TB (K)", fontsize=fontsizey)
    axkband.set_ylabel("TB (K)", fontsize=fontsizey)
    axvband.set_ylabel("TB (K)", fontsize=fontsizey)
    axmirac2.set_xlabel("Date (UTC)", fontsize=fontsizey)

    for nn, ax in enumerate([axkband, axvband, axmirac1, axmirac2]):
        ax.set_xlim(
            datetime(date.year, date.month, date.day, 0),
            datetime(date.year, date.month, date.day, 23, 58),
        )
        locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.get_offset_text().set_size(
            fontsizetix
        )  ##access concise date formatter thing
        ax.tick_params(axis='both', labelsize=fontsizetix)

    ###plot
    for m, freq in enumerate(Hatpro_frequencies):
        if np.prod(TBs_hatpro.shape) == 0: continue
        if m < 7:
            axkband.plot(
                dates_hatpro,
                TBs_hatpro[:, m],
                "o",
                label=f"{Hatpro_frequencies[m]} GHz",
                markersize=msize,
            )
        else:
            axvband.plot(
                dates_hatpro,
                TBs_hatpro[:, m],
                "o",
                label=f"{Hatpro_frequencies[m]} GHz",
                markersize=msize,
            )
    axvband.legend(fontsize=fontsizelegend, markerscale=mscale,
                    bbox_to_anchor=(1,1), loc='upper left')
    axkband.legend(fontsize=fontsizelegend, markerscale=mscale, 
                    bbox_to_anchor=(1,1), loc='upper left')

    for m, freq in enumerate(Mirac_frequencies[:]):
        if np.prod(TBs_mirac.shape) == 0: continue
        if m >= 6:
            axmirac2.plot(
                dates_mirac,
                TBs_mirac[:, m],
                "o",
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                markersize=msize,
            )
        else:
            axmirac1.plot(
                dates_mirac,
                TBs_mirac[:, m],
                "o",
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                markersize=msize,
            )
    axmirac1.legend(fontsize=fontsizelegend, markerscale=mscale,
                    bbox_to_anchor=(1,1), loc='upper left')
    axmirac2.legend(fontsize=fontsizelegend, markerscale=mscale,
                    bbox_to_anchor=(1,1), loc='upper left')
    
    plt.subplots_adjust(right=0.84)

    hatpro_ds = hatpro_ds.close()
    lhumpro_ds = lhumpro_ds.close()
    if save:        
        plot_path = os.path.join(os.environ["PATH_PLOTS"],
                                 f"quicklooks/mwr/{filename}")
        os.makedirs(plot_path, exist_ok=True)
        plotname = f"{Constants.CAMPAIGN_NAME}_hatpro_mirac-p_{filename}_tb_quicklook_{date.strftime('%Y%m%d')}"
        plotfile = os.path.join(plot_path, plotname + ".png")
        print(f"Saved {plotfile}....")
        plt.savefig(
            plotfile,
            dpi=150,
            bbox_inches="tight",
        )
        
    if show:
        plt.show()

    plt.close()


def plot_mwr_hourly_quicklook_boundarylayerscan_byangle(
    date, show=True, save=False
):
    """
     plot_mwr_hourly_quicklook_boundarylayerscan_byangle(date,show=True, save=False)
    Time series of boundary layer measurement of HATPRO and LHUMPRO for one hour
    date is the day and hour the plot is created for, there are two scans per hour therefore there are two columns per band to show these two.
    """
    hatpro_ds = read_scan(date, "hatpro", "BL-SCAN", daily_file=True)
    lhumpro_ds = read_scan(date, "mirac-p", "BL-SCAN", daily_file=True)
    Hatpro_frequencies = [
        22.24,
        23.04,
        23.84,
        25.44,
        26.24,
        27.84,
        31.4,
        51.26,
        52.28,
        53.86,
        54.94,
        56.66,
        57.3,
        58,
    ]
    Mirac_frequencies = lhumpro_ds.Freq.data
    hatpro_ds = hatpro_ds.sel(
        time=pd.to_datetime(hatpro_ds.time).hour == date.hour
    )
    lhumpro_ds = lhumpro_ds.sel(
        time=pd.to_datetime(lhumpro_ds.time).hour == date.hour
    )
    dates_hatpro = hatpro_ds.time.values
    TBs_hatpro = hatpro_ds.TBs.values
    dates_mirac = lhumpro_ds.time.values
    TBs_mirac = lhumpro_ds.TBs.values
    title = f"MWR observation boundary layer scan {date:%Y%m%dT%H}"
    filename = "bl_scan"
    #  lhumpro_angles = np.float32([  94.18,  94.77,  95.37,  96.57,  98.37, 101.38, 104.37, 109.19,
    #     119.99, 179.97])
    #  hatpro_angles = np.float32( [ 94.25,  94.83,  95.43,  96.63,  98.43, 101.42, 104.42, 109.21,
    #     119.96, 120.03, 179.98, 180.02])

    fig = plt.figure(figsize=(15.5, 20))
    matplotlib.rcParams["ytick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    matplotlib.rcParams["xtick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    plt.suptitle(f"{title}", x=0.5, y=0.925, fontsize=fontsize_title)
    gs = fig.add_gridspec(
        4, 3, hspace=0.45, wspace=0.25, width_ratios=[1, 1, 0.35]
    )
    axkband = fig.add_subplot(gs[0, 0])
    axkband.text(
        -0.1,
        1.1,
        "1st scan K-Band",
        transform=axkband.transAxes,
        size=20,
        weight="bold",
    )
    axkband2 = fig.add_subplot(gs[0, 1])
    axkband2.text(
        -0.1,
        1.1,
        "2nd scan K-Band)",
        transform=axkband2.transAxes,
        size=20,
        weight="bold",
    )
    axvband = fig.add_subplot(gs[1, 0], sharex=axkband)
    axvband.text(
        -0.1,
        1.1,
        "1st scan V-Band",
        transform=axvband.transAxes,
        size=20,
        weight="bold",
    )
    axvband2 = fig.add_subplot(gs[1, 1], sharex=axkband)
    axvband2.text(
        -0.1,
        1.1,
        "2nd scan V-Band",
        transform=axvband2.transAxes,
        size=20,
        weight="bold",
    )
    axmirac1 = fig.add_subplot(gs[2, 0], sharex=axkband)
    axmirac1.text(
        -0.1,
        1.1,
        "1st scan G-Band",
        transform=axmirac1.transAxes,
        size=20,
        weight="bold",
    )
    axmirac1b = fig.add_subplot(gs[2, 1], sharex=axkband)
    axmirac1b.text(
        -0.1,
        1.1,
        "2nd scan G-Band",
        transform=axmirac1b.transAxes,
        size=20,
        weight="bold",
    )
    axmirac2 = fig.add_subplot(gs[3, 0], sharex=axkband)
    axmirac2.text(
        -0.1,
        1.1,
        "1st scan high freqs",
        transform=axmirac2.transAxes,
        size=20,
        weight="bold",
    )
    axmirac2b = fig.add_subplot(gs[3, 1], sharex=axkband)
    axmirac2b.text(
        -0.1,
        1.1,
        "2nd scan high freqs",
        transform=axmirac2b.transAxes,
        size=20,
        weight="bold",
    )
    axkbandleg = fig.add_subplot(gs[0, 2])
    axvbandleg = fig.add_subplot(gs[1, 2])
    axmirac1leg = fig.add_subplot(gs[2, 2])
    axmirac2leg = fig.add_subplot(gs[3, 2])
    ###labels
    axmirac2.set_ylabel("TB (K)", fontsize=fontsizey)
    axmirac1.set_ylabel("TB (K)", fontsize=fontsizey)
    axkband.set_ylabel("TB (K)", fontsize=fontsizey)
    axvband.set_ylabel("TB (K)", fontsize=fontsizey)
    axmirac2.set_xlabel("Angle (°)", fontsize=fontsizey)
    axmirac2b.set_xlabel("Angle (°)", fontsize=fontsizey)

    ###plot
    msize = 15
    mscale = 2
    alpha = 0.7
    idx_secondscan = np.argmax(np.diff(hatpro_ds.time.values) * 10 ** (-9)) + 1
    #  print(hatpro_ds.time.values[idx_secondscan])
    for m, freq in enumerate(Hatpro_frequencies):
        if m < 7:
            axkband.scatter(
                hatpro_ds.ElAng.values[:idx_secondscan],
                TBs_hatpro[:idx_secondscan, m],
                label=f"{Hatpro_frequencies[m]} GHz",
                s=msize,
            )
            axkband2.scatter(
                hatpro_ds.ElAng.values[idx_secondscan:],
                TBs_hatpro[idx_secondscan:, m],
                label=f"{Hatpro_frequencies[m]} GHz",
                s=msize,
            )
        else:
            axvband.scatter(
                hatpro_ds.ElAng.values[:idx_secondscan],
                TBs_hatpro[:idx_secondscan, m],
                label=f"{Hatpro_frequencies[m]} GHz",
                s=msize,
            )
            axvband2.scatter(
                hatpro_ds.ElAng.values[idx_secondscan:],
                TBs_hatpro[idx_secondscan:, m],
                label=f"{Hatpro_frequencies[m]} GHz",
                s=msize,
            )
    #    axvband2.legend(fontsize=fontsizelegend, markerscale=mscale)
    #    axkband2.legend(fontsize=fontsizelegend, markerscale=mscale)

    h, l = (
        axkband.get_legend_handles_labels()
    )  # get labels and handles from axkband
    axkbandleg.legend(h, l, fontsize=fontsizelegend, markerscale=mscale)
    h, l = (
        axvband.get_legend_handles_labels()
    )  # get labels and handles from axvband
    axvbandleg.legend(h, l, fontsize=fontsizelegend, markerscale=mscale)

    idx_secondscan = (
        np.argmax(np.diff(lhumpro_ds.time.values) * 10 ** (-9)) + 1
    )

    for m, freq in enumerate(Mirac_frequencies[:]):
        if m >= 6:
            axmirac2.scatter(
                lhumpro_ds.ElAng.values[:idx_secondscan],
                TBs_mirac[:idx_secondscan, m],
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                s=msize,
                alpha=alpha,
            )
            axmirac2b.scatter(
                lhumpro_ds.ElAng.values[idx_secondscan:],
                TBs_mirac[idx_secondscan:, m],
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                s=msize,
                alpha=alpha,
            )

        else:
            axmirac1.scatter(
                lhumpro_ds.ElAng.values[:idx_secondscan],
                TBs_mirac[:idx_secondscan, m],
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                s=msize,
                alpha=alpha,
            )
            axmirac1b.scatter(
                lhumpro_ds.ElAng.values[idx_secondscan:],
                TBs_mirac[idx_secondscan:, m],
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                s=msize,
                alpha=alpha,
            )

    h, l = (
        axmirac1b.get_legend_handles_labels()
    )  # get labels and handles from ax1
    axmirac1leg.legend(h, l, fontsize=fontsizelegend, markerscale=mscale)
    h, l = (
        axmirac2b.get_legend_handles_labels()
    )  # get labels and handles from ax1
    axmirac2leg.legend(h, l, fontsize=fontsizelegend, markerscale=mscale)
    hatpro_ds.close()
    lhumpro_ds.close()
    for ax in [axkbandleg, axvbandleg, axmirac1leg, axmirac2leg]:
        ax.axis("off")
    if save:
        file = os.path.join(
            os.environ["PATH_PLOTS"],
            "quicklooks/mwr/blscans/",
            f"{Constants.CAMPAIGN_NAME}_hatpro_mirac-p_{filename}_quicklook_{date.strftime('%Y%m%d%H')}.png",
        )
        print(f"Writing plot {file}")
        plt.savefig(
            file,
            dpi=100,
            bbox_inches="tight",
        )
    if show:
        plt.show()

    plt.close()


def plot_mwr_hourly_quicklook_emissivityscan_byangle(
    date, show=True, save=False
):
    """
     plot_mwr_hourly_quicklook_emissivityscan_byangle(date,show=True, save=False)
    Time series of surface observations at different angles (emissivity scans) of HATPRO and LHUMPRO for one hour
    date is the day and hour the plot is created for, there are two scans per hour therefore there are two columns per band to show these two.

    """
    hatpro_ds = read_scan(date, "hatpro", "EMIS-SCAN", daily_file=True)
    lhumpro_ds = read_scan(date, "mirac-p", "EMIS-SCAN", daily_file=True)
    Hatpro_frequencies = [
        22.24,
        23.04,
        23.84,
        25.44,
        26.24,
        27.84,
        31.4,
        51.26,
        52.28,
        53.86,
        54.94,
        56.66,
        57.3,
        58,
    ]
    Mirac_frequencies = lhumpro_ds.Freq.data

    hatpro_ds = hatpro_ds.sel(
        time=pd.to_datetime(hatpro_ds.time).hour == date.hour
    )
    lhumpro_ds = lhumpro_ds.sel(
        time=pd.to_datetime(lhumpro_ds.time).hour == date.hour
    )
    dates_hatpro = hatpro_ds.time.values
    TBs_hatpro = hatpro_ds.TBs.values
    dates_mirac = lhumpro_ds.time.values
    TBs_mirac = lhumpro_ds.TBs.values
    title = f"MWR surface and atmosphere observation scan {date:%Y%m%dT%H}"
    filename = "emis_scan"

    #  angles = ([ 25.  35.  45.  55.  65. 115. 125. 135. 145. 155.])

    fig = plt.figure(figsize=(15, 20))
    matplotlib.rcParams["ytick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    matplotlib.rcParams["xtick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    plt.suptitle(f"{title}", x=0.5, y=0.925, fontsize=fontsize_title)
    gs = fig.add_gridspec(
        4, 3, hspace=0.45, wspace=0.25, width_ratios=[1, 1, 0.35]
    )
    axkband = fig.add_subplot(gs[0, 0])
    axkband.text(
        -0.1,
        1.1,
        "1st scan K-Band",
        transform=axkband.transAxes,
        size=20,
        weight="bold",
    )
    axkband2 = fig.add_subplot(gs[0, 1])
    axkband2.text(
        -0.1,
        1.1,
        "2nd scan K-Band)",
        transform=axkband2.transAxes,
        size=20,
        weight="bold",
    )
    axkbandleg = fig.add_subplot(gs[0, 2])

    axvband = fig.add_subplot(gs[1, 0], sharex=axkband)
    axvband.text(
        -0.1,
        1.1,
        "1st scan V-Band",
        transform=axvband.transAxes,
        size=20,
        weight="bold",
    )
    axvband2 = fig.add_subplot(gs[1, 1], sharex=axkband)
    axvband2.text(
        -0.1,
        1.1,
        "2nd scan V-Band",
        transform=axvband2.transAxes,
        size=20,
        weight="bold",
    )
    axvbandleg = fig.add_subplot(gs[1, 2])

    axmirac1 = fig.add_subplot(gs[2, 0], sharex=axkband)
    axmirac1.text(
        -0.1,
        1.1,
        "1st scan G-Band",
        transform=axmirac1.transAxes,
        size=20,
        weight="bold",
    )
    axmirac1b = fig.add_subplot(gs[2, 1], sharex=axkband)
    axmirac1b.text(
        -0.1,
        1.1,
        "2nd scan G-Band",
        transform=axmirac1b.transAxes,
        size=20,
        weight="bold",
    )
    axmirac2 = fig.add_subplot(gs[3, 0], sharex=axkband)
    axmirac2.text(
        -0.1,
        1.1,
        "1st scan high freqs",
        transform=axmirac2.transAxes,
        size=20,
        weight="bold",
    )
    axmirac1leg = fig.add_subplot(gs[2, 2])
    axmirac2leg = fig.add_subplot(gs[3, 2])

    axmirac2b = fig.add_subplot(gs[3, 1], sharex=axkband)
    axmirac2b.text(
        -0.1,
        1.1,
        "2nd scan high freqs",
        transform=axmirac2b.transAxes,
        size=20,
        weight="bold",
    )
    ###labels
    axmirac2.set_ylabel("TB (K)", fontsize=fontsizey)
    axmirac1.set_ylabel("TB (K)", fontsize=fontsizey)
    axkband.set_ylabel("TB (K)", fontsize=fontsizey)
    axvband.set_ylabel("TB (K)", fontsize=fontsizey)
    axmirac2.set_xlabel("Angle (°)", fontsize=fontsizey)
    axmirac2b.set_xlabel("Angle (°)", fontsize=fontsizey)
    for ax in [axkbandleg, axvbandleg, axmirac1leg, axmirac2leg]:
        ax.axis("off")
    ###plot
    msize = 15
    mscale = 2
    alpha = 0.7
    idx_secondscan = np.argmax(np.diff(hatpro_ds.time.values) * 10 ** (-9)) + 1
    #  print(hatpro_ds.time.values[idx_secondscan])
    for m, freq in enumerate(Hatpro_frequencies):
        if m < 7:
            axkband.scatter(
                hatpro_ds.ElAng.values[:idx_secondscan],
                TBs_hatpro[:idx_secondscan, m],
                label=f"{Hatpro_frequencies[m]} GHz",
                s=msize,
            )
            axkband2.scatter(
                hatpro_ds.ElAng.values[idx_secondscan:],
                TBs_hatpro[idx_secondscan:, m],
                label=f"{Hatpro_frequencies[m]} GHz",
                s=msize,
            )
        else:
            axvband.scatter(
                hatpro_ds.ElAng.values[:idx_secondscan],
                TBs_hatpro[:idx_secondscan, m],
                label=f"{Hatpro_frequencies[m]} GHz",
                s=msize,
            )
            axvband2.scatter(
                hatpro_ds.ElAng.values[idx_secondscan:],
                TBs_hatpro[idx_secondscan:, m],
                label=f"{Hatpro_frequencies[m]} GHz",
                s=msize,
            )

    h, l = (
        axkband.get_legend_handles_labels()
    )  # get labels and handles from axkband
    axkbandleg.legend(h, l, fontsize=fontsizelegend, markerscale=mscale)
    h, l = (
        axvband.get_legend_handles_labels()
    )  # get labels and handles from axvband
    axvbandleg.legend(h, l, fontsize=fontsizelegend, markerscale=mscale)

    idx_secondscan = (
        np.argmax(np.diff(lhumpro_ds.time.values) * 10 ** (-9)) + 1
    )

    for m, freq in enumerate(Mirac_frequencies[:]):
        if m >= 6:
            axmirac2.scatter(
                lhumpro_ds.ElAng.values[:idx_secondscan],
                TBs_mirac[:idx_secondscan, m],
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                s=msize,
                alpha=alpha,
            )
            axmirac2b.scatter(
                lhumpro_ds.ElAng.values[idx_secondscan:],
                TBs_mirac[idx_secondscan:, m],
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                s=msize,
                alpha=alpha,
            )

        else:
            axmirac1.scatter(
                lhumpro_ds.ElAng.values[:idx_secondscan],
                TBs_mirac[:idx_secondscan, m],
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                s=msize,
                alpha=alpha,
            )
            axmirac1b.scatter(
                lhumpro_ds.ElAng.values[idx_secondscan:],
                TBs_mirac[idx_secondscan:, m],
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                s=msize,
                alpha=alpha,
            )

    h, l = (
        axmirac1b.get_legend_handles_labels()
    )  # get labels and handles from ax1
    axmirac1leg.legend(h, l, fontsize=fontsizelegend, markerscale=mscale)
    h, l = (
        axmirac2b.get_legend_handles_labels()
    )  # get labels and handles from ax1
    axmirac2leg.legend(h, l, fontsize=fontsizelegend, markerscale=mscale)
    hatpro_ds.close()
    lhumpro_ds.close()
    if save:
        file = os.path.join(
            os.environ["PATH_PLOTS"],
            f"quicklooks/mwr/{filename}",
            f"{Constants.CAMPAIGN_NAME}_hatpro_mirac-p_{filename}_quicklook_{date.strftime('%Y%m%d%H')}.png",
        )
        print(f"Writing plot {file}")
        plt.savefig(
            file,
            dpi=100,
            bbox_inches="tight",
        )
    if show:
        plt.show()

    plt.close()


def plot_mwr_hourly_quicklook_boundarylayerscan(date, show=True, save=False):
    """
     plot_mwr_hourly_quicklook_boundarylayerscan(date,show=True, save=False)
    Time series of TB boundary layer measurement of HATPRO and LHUMPRO for one hour
    date is the day the plot is created for
    """
    hatpro_ds = read_scan(date, "hatpro", "BL-SCAN", daily_file=True)
    lhumpro_ds = read_scan(date, "mirac-p", "BL-SCAN", daily_file=True)
    Hatpro_frequencies = [
        22.24,
        23.04,
        23.84,
        25.44,
        26.24,
        27.84,
        31.4,
        51.26,
        52.28,
        53.86,
        54.94,
        56.66,
        57.3,
        58,
    ]
    Mirac_frequencies = lhumpro_ds.Freq.data
    print(len(hatpro_ds))
    hatpro_ds = hatpro_ds.sel(
        time=pd.to_datetime(hatpro_ds.time).hour == date.hour
    )
    lhumpro_ds = lhumpro_ds.sel(
        time=pd.to_datetime(lhumpro_ds.time).hour == date.hour
    )
    print(len(hatpro_ds))
    dates_hatpro = hatpro_ds.time.values
    TBs_hatpro = hatpro_ds.TBs.values
    dates_mirac = lhumpro_ds.time.values
    TBs_mirac = lhumpro_ds.TBs.values
    title = "MWR observation boundary layer scan"
    filename = "bl_scan"
    lhumpro_angles = np.float32(
        [
            94.18,
            94.77,
            95.37,
            96.57,
            98.37,
            101.38,
            104.37,
            109.19,
            119.99,
            179.97,
        ]
    )
    hatpro_angles = np.float32(
        [
            94.25,
            94.83,
            95.43,
            96.63,
            98.43,
            101.42,
            104.42,
            109.21,
            119.96,
            120.03,
            179.98,
            180.02,
        ]
    )

    prop_cycle = plt.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    colors = np.append(colors, ["black", "grey"])
    hatpro_color_dict = dict(zip(hatpro_angles, colors))
    print(hatpro_color_dict)
    lhumpro_color_dict = dict(zip(lhumpro_angles, colors))
    fig = plt.figure(figsize=(20, 20))
    matplotlib.rcParams["ytick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    matplotlib.rcParams["xtick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    plt.suptitle(f"{title}", x=0.5, y=0.9, fontsize=fontsize_title)
    gs = fig.add_gridspec(
        4, 1, hspace=0.45, wspace=0.05
    )  # width_ratios= [1,1,1,1],
    axkband = fig.add_subplot(gs[0, :])
    axkband.text(
        -0.1, 1.1, "a)", transform=axkband.transAxes, size=20, weight="bold"
    )
    axvband = fig.add_subplot(gs[1, :], sharex=axkband)
    axvband.text(
        -0.1, 1.1, "b)", transform=axvband.transAxes, size=20, weight="bold"
    )
    axmirac1 = fig.add_subplot(gs[2, :], sharex=axkband)
    axmirac1.text(
        -0.1, 1.1, "c)", transform=axmirac1.transAxes, size=20, weight="bold"
    )
    axmirac2 = fig.add_subplot(gs[3, :], sharex=axkband)
    axmirac2.text(
        -0.1, 1.1, "d)", transform=axmirac2.transAxes, size=20, weight="bold"
    )
    ###labels
    axmirac2.set_ylabel("TB (K)", fontsize=fontsizey)
    axmirac1.set_ylabel("TB (K)", fontsize=fontsizey)
    axkband.set_ylabel("TB (K)", fontsize=fontsizey)
    axvband.set_ylabel("TB (K)", fontsize=fontsizey)
    axmirac2.set_xlabel("Date (UTC)", fontsize=fontsizey)

    for nn, ax in enumerate([axkband, axvband, axmirac1, axmirac2]):
        # ax.set_xlim(datetime(date.year, date.month, date.day, 0), datetime(date.year, date.month, date.day, 23, 58))
        locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.get_offset_text().set_size(
            fontsizetix
        )  ##access concise date formatter thing

    ###plot
    markers = ["x", "o", "p", "v", ">", "s", "P", "*"]
    c_hatpro = [
        hatpro_color_dict[hatpro_ds.ElAng.values[i]]
        for i in range(len(hatpro_ds.ElAng))
    ]
    for m, freq in enumerate(Hatpro_frequencies):
        if m < 7:
            axkband.scatter(
                dates_hatpro,
                TBs_hatpro[:, m],
                marker=markers[m],
                c=c_hatpro,
                label=f"{Hatpro_frequencies[m]} GHz",
                s=msize,
            )
        else:
            axvband.plot(
                dates_hatpro,
                TBs_hatpro[:, m],
                markers[m - 7],
                label=f"{Hatpro_frequencies[m]} GHz",
                markersize=msize,
            )
    axvband.legend(fontsize=fontsizelegend, markerscale=mscale, ncol=7)
    axkband.legend(fontsize=fontsizelegend, markerscale=mscale, ncol=7)

    for m, freq in enumerate(Mirac_frequencies[:]):
        if m >= 6:
            axmirac2.plot(
                dates_mirac,
                TBs_mirac[:, m],
                "o",
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                markersize=msize,
            )
        else:
            axmirac1.plot(
                dates_mirac,
                TBs_mirac[:, m],
                "o",
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                markersize=msize,
            )
    axmirac1.legend(fontsize=fontsizelegend, markerscale=mscale, ncol=6)
    axmirac2.legend(fontsize=fontsizelegend, markerscale=mscale)

    hatpro_ds.close()
    lhumpro_ds.close()
    if save:
        file = os.path.join(
            os.environ["PATH_PLOTS"],
            "quicklooks/mwr",
            f"{Constants.CAMPAIGN_NAME}_hatpro_mirac-p_{filename}_quicklook_{date.strftime('%Y%m%d')}.png",
        )
        print(f"Writing plot {file}")
        plt.savefig(
            file,
            dpi=300,
            bbox_inches="tight",
        )
    if show:
        plt.show()

    plt.close()


def plot_all_mwr_surface_observations_visual_hour(
    date,
    xlim="default",
    vline=False,
    vis=False,
    ir=True,
    save=False,
    show=True,
    cropped=True,
    path_gopro="",
    footprint=True,
):
    """plot_all_mwr_surface_observations_hour(date, xlim="default")
    plots data for one hour,
    with xlim one can adapt the xlimits further,
    vline sets a vertical line to aid the eye at a certain time if true
    vis adds a go pro image at the vertical line if set to true
    ir adds the infrared image at the vertical line if set to true
    save saves the images
    show shows the image
    """
    from PIL import Image

    #  data_hatpro = read_tb_surface_vampire(date, "HATPRO") ##use this once this works
    #  data_mirac = read_tb_surface_vampire(date, "MIRAC")
    data_hatpro = read_scan(date, "hatpro", "EMIS", daily_file=True)
    data_mirac = read_scan(date, "mirac-p", "EMIS", daily_file=True)
    ###maybe the HATPRO frequencies are in the nc file for newer versions
    Hatpro_frequencies = [
        22.24,
        23.04,
        23.84,
        25.44,
        26.24,
        27.84,
        31.4,
        51.26,
        52.28,
        53.86,
        54.94,
        56.66,
        57.3,
        58,
    ]
    Mirac_frequencies = data_mirac.Freq.data

    ##select for this hour
    data_hatpro = data_hatpro.sel(
        time=pd.to_datetime(data_hatpro.time).hour == date.hour
    )
    data_mirac = data_mirac.sel(
        time=pd.to_datetime(data_mirac.time).hour == date.hour
    )
    dates_hatpro = data_hatpro.time.values[data_hatpro.ElAng == 53]
    TBs_hatpro = data_hatpro.TBs.values[data_hatpro.ElAng == 53]
    dates_mirac = data_mirac.time.values[data_mirac.ElAng == 53.0]
    TBs_mirac = data_mirac.TBs.values[data_mirac.ElAng == 53.0]

    ##configure plot
    matplotlib.rcParams["ytick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    matplotlib.rcParams["xtick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )

    # plt.suptitle("Zenith angle 53° ",x=0.5,y=0.9, fontsize=fontsize_title)
    if vis == True and ir == False:
        fig = plt.figure(figsize=(20, 30))

        gs = fig.add_gridspec(
            5, 1, hspace=0.45, wspace=0.05, height_ratios=[1, 1, 1, 1, 2]
        )  # ,
    elif vis == True and ir == True:
        fig = plt.figure(figsize=(20, 30))

        gs = fig.add_gridspec(
            5, 2, hspace=0.45, wspace=0.05, height_ratios=[1, 1, 1, 1, 2]
        )  # ,
    else:
        fig = plt.figure(figsize=(20, 20))

        gs = fig.add_gridspec(
            4, 1, hspace=0.45, wspace=0.05
        )  # width_ratios= [1,1,1,1],

    axkband = fig.add_subplot(gs[0, :])
    axkband.text(
        -0.1, 1.1, "a)", transform=axkband.transAxes, size=20, weight="bold"
    )
    axvband = fig.add_subplot(gs[1, :], sharex=axkband)
    axvband.text(
        -0.1, 1.1, "b)", transform=axvband.transAxes, size=20, weight="bold"
    )
    axmirac1 = fig.add_subplot(gs[2, :], sharex=axkband)
    axmirac1.text(
        -0.1, 1.1, "c)", transform=axmirac1.transAxes, size=20, weight="bold"
    )
    axmirac2 = fig.add_subplot(gs[3, :], sharex=axkband)
    axmirac2.text(
        -0.1, 1.1, "d)", transform=axmirac2.transAxes, size=20, weight="bold"
    )
    mscale = 5  ##set markerscale in legend

    ###labels
    axmirac2.set_ylabel("TB (K)", fontsize=fontsizey)
    axmirac1.set_ylabel("TB (K)", fontsize=fontsizey)
    axkband.set_ylabel("TB (K)", fontsize=fontsizey)
    axvband.set_ylabel("TB (K)", fontsize=fontsizey)

    axmirac2.set_xlabel("Date (UTC)", fontsize=fontsizey)

    for nn, ax in enumerate([axkband, axvband, axmirac1, axmirac2]):
        locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.get_offset_text().set_size(
            fontsizetix
        )  ##access concise date formatter thing

    ###plot
    for m, freq in enumerate(Hatpro_frequencies):
        if m < 7:
            axkband.plot(
                dates_hatpro,
                TBs_hatpro[:, m],
                "o",
                label=f"{Hatpro_frequencies[m]} GHz",
                markersize=msize,
            )
        else:
            axvband.plot(
                dates_hatpro,
                TBs_hatpro[:, m],
                "o",
                label=f"{Hatpro_frequencies[m]} GHz",
                markersize=msize,
            )

    for m, freq in enumerate(Mirac_frequencies[:]):
        if m >= 6:
            axmirac2.plot(
                dates_mirac,
                TBs_mirac[:, m],
                "o",
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                markersize=msize,
            )
        else:
            axmirac1.plot(
                dates_mirac,
                TBs_mirac[:, m],
                "o",
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                markersize=msize,
            )

    data_hatpro.close()
    data_mirac.close()
    axmirac2.legend(fontsize=fontsizelegend, markerscale=mscale)
    axmirac1.legend(fontsize=fontsizelegend, markerscale=mscale)
    axvband.legend(fontsize=fontsizelegend, markerscale=mscale)
    axkband.legend(fontsize=fontsizelegend, markerscale=mscale)
    if xlim != "default":
        axkband.set_xlim(xlim[0], xlim[1])
    if vline != False:
        axkband.vlines(
            [vline],
            np.nanmin(TBs_hatpro[:, :7]),
            np.nanmax(TBs_hatpro[:, :7]),
        )
        axvband.vlines(
            [vline], np.nanmin(TBs_hatpro[:, 7:]), np.nanmax(TBs_hatpro[:, 7:])
        )
        axmirac1.vlines(
            [vline], np.nanmin(TBs_mirac[:, :6]), np.nanmax(TBs_mirac[:, :6])
        )
        axmirac2.vlines(
            [vline], np.nanmin(TBs_mirac[:, 6:]), np.nanmax(TBs_mirac[:, 6:])
        )

        if vis:
            filename = f"_vis_{vline:%Y%m%d%H%M%S}"
            files_gopro  = glob.glob(f"{path_gopro}{date:%Y%m%d%H}/*") ##all files in that hour
          #  print( len(files_gopro)  )
            time_go_pro = pd.to_datetime([files_gopro[m][-31:-17]  for m in range(len(files_gopro))])
            index_colloc = np.argmin(abs((time_go_pro -vline).total_seconds()))
            vis = Image.open(files_gopro[index_colloc])
            axvis = fig.add_subplot(gs[4,0])
            if cropped:
                vis = np.array(vis)[200:600,300:700,:]
                
            axvis.imshow(vis)  
            axvis.set_xticks([])
            axvis.set_yticks([])
            axvis.set_title(f"{time_go_pro[index_colloc]}", fontsize=fontsizey)# {dtimes[idx_colloc]}
            if footprint==True:
                if cropped:
                    x_min = 483-300
                    x_max=517-300
                    y_min = 455-200
                    y_max= 497-200
                else:
                    x_min = 483
                    x_max=517
                    y_min = 455
                    y_max= 497
                axvis.plot([x_min, x_max, x_max, x_min, x_min], [y_min, y_min, y_max, y_max,y_min],color="red")
        
        ###add IR image
        if ir:
            ds = read_flir_statistics(vline)
            img = get_flir_image(ds, time=vline)
            axir = fig.add_subplot(gs[4,1])
            CS = axir.imshow(img-3.82857,cmap=plt.cm.plasma)
            
            axir.set_xticks([])
            axir.set_yticks([])
            axir.set_title(f"{vline}", fontsize=fontsizey)# {dtimes[idx_colloc]}

            cbar = fig.colorbar(CS, shrink=0.8)
            cbar.ax.set_ylabel('surface temperature (K)', fontsize=fontsizey)
            if footprint==True:
                x_min = 83
                x_max=132
                y_min = 90
                y_max= 150
                axir.plot([x_min, x_max, x_max, x_min, x_min], [y_min, y_min, y_max, y_max,y_min],color="red")
    else:
        filename = ""
    if save:

        file = os.path.join(
            os.environ["PATH_PLOTS"],
            "quicklooks/mwr/emiscans_vis/",
            f"{Constants.CAMPAIGN_NAME}_hatpro_mirac-p_quicklook_{date.strftime('%Y%m%d')}{filename}.png",
        )
        print(f"Writing plot {file}")
        plt.savefig(
            file,
            dpi=100,
            bbox_inches="tight",
        )
    if show:
        plt.show()
    plt.close()


def plot_mwr_daily_quicklook_oneband(
    date,
    scan,
    band="V",
    downwelling=False,
    show=True,
    save=False,
    print_stats=False,
    ylim="default",
):
    """
    plot_mwr_daily_quicklook_oneband(date,scan, band="V", downwelling=False, show=True, save=False, print_stats=False, ylim="default"
    Time series of TB zenith measurement of one band for one day
    date is the day the plot is created for
    scan is the scan type (ZENITH or EMIS), boundary layer scan has extra plotting function
    band is the band that should be plotted: "K", "V", "G", or "highfreq"
    if downwelling is True and scan type is EMIS then the downwelling TB at 127 degrees are plotted.
    """

    hatpro_ds = read_scan(date, "hatpro", scan, daily_file=True)
    lhumpro_ds = read_scan(date, "mirac-p", scan, daily_file=True)
    Hatpro_frequencies = [
        22.24,
        23.04,
        23.84,
        25.44,
        26.24,
        27.84,
        31.4,
        51.26,
        52.28,
        53.86,
        54.94,
        56.66,
        57.3,
        58,
    ]
    Mirac_frequencies = lhumpro_ds.Freq.data
    if scan == "ZENITH":
        dates_hatpro = hatpro_ds.time.values
        TBs_hatpro = hatpro_ds.TBs.values
        dates_mirac = lhumpro_ds.time.values
        TBs_mirac = lhumpro_ds.TBs.values
        title = "MWR observation zenith"
        filename = "zenith"
    elif scan == "EMIS" and downwelling == False:
        dates_hatpro = hatpro_ds.time.values[hatpro_ds.ElAng == 53.0]
        TBs_hatpro = hatpro_ds.TBs.values[hatpro_ds.ElAng == 53.0]
        dates_mirac = lhumpro_ds.time.values[lhumpro_ds.ElAng == 53]
        TBs_mirac = lhumpro_ds.TBs.values[lhumpro_ds.ElAng == 53]
        title = "MWR surface observation 53° off-nadir"
        filename = "surface_53"
    elif scan == "EMIS" and downwelling == True:
        dates_hatpro = hatpro_ds.time.values[hatpro_ds.ElAng == 127.0]
        TBs_hatpro = hatpro_ds.TBs.values[hatpro_ds.ElAng == 127.0]
        dates_mirac = lhumpro_ds.time.values[lhumpro_ds.ElAng == 127.0]
        TBs_mirac = lhumpro_ds.TBs.values[lhumpro_ds.ElAng == 127.0]
        title = "MWR downwelling TB observation 127° off-nadir"
        filename = "downwelling_127"

    fig = plt.figure(figsize=(20, 10))
    matplotlib.rcParams["ytick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    matplotlib.rcParams["xtick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    plt.suptitle(
        f"{title} {band} band", x=0.5, y=0.94, fontsize=fontsize_title
    )
    gs = fig.add_gridspec(
        1, 1
    )  # , hspace=0.45,wspace=0.05) #width_ratios= [1,1,1,1],
    ax = fig.add_subplot(gs[0, :])

    ###labels
    ax.set_ylabel("TB (K)", fontsize=fontsizey)
    ax.set_xlabel("Date (UTC)", fontsize=fontsizey)

    for nn, ax in enumerate([ax]):
        ax.set_xlim(
            datetime(date.year, date.month, date.day, 0),
            datetime(date.year, date.month, date.day, 23, 58),
        )
        locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.get_offset_text().set_size(
            fontsizetix
        )  ##access concise date formatter thing

    ###plot
    if band == "K":
        for m, freq in enumerate(Hatpro_frequencies):
            if m < 7:
                ax.plot(
                    dates_hatpro,
                    TBs_hatpro[:, m],
                    "o",
                    label=f"{Hatpro_frequencies[m]} GHz",
                    markersize=msize,
                )
                if print_stats:
                    print(
                        f"{freq} GHz: daily mean:{np.nanmean(TBs_hatpro[:,m])} , daily max: {np.nanmax(TBs_hatpro[:,m])}, daily min {np.nanmin(TBs_hatpro[:,m])}, daily std: {np.nanstd(TBs_hatpro[:,m])}"
                    )
            else:
                pass
    elif band == "V":
        for m, freq in enumerate(Hatpro_frequencies):
            if m < 7:
                pass
            else:
                ax.plot(
                    dates_hatpro,
                    TBs_hatpro[:, m],
                    "o",
                    label=f"{Hatpro_frequencies[m]} GHz",
                    markersize=msize,
                )
                if print_stats:
                    print(
                        f"{freq} GHz: daily mean:{np.nanmean(TBs_hatpro[:,m])} , daily max: {np.nanmax(TBs_hatpro[:,m])}, daily min {np.nanmin(TBs_hatpro[:,m])}, daily std: {np.nanstd(TBs_hatpro[:,m])}"
                    )
    elif band == "highfreq":
        for m, freq in enumerate(Mirac_frequencies[:]):
            if m >= 6:
                ax.plot(
                    dates_mirac,
                    TBs_mirac[:, m],
                    "o",
                    label=f"{Mirac_frequencies[m]:.2f} GHz",
                    markersize=msize,
                )
                if print_stats:
                    print(
                        f"{freq} GHz: daily mean:{np.nanmean(TBs_mirac[:,m])} , daily max: {np.nanmax(TBs_mirac[:,m])}, daily min {np.nanmin(TBs_mirac[:,m])}, daily std: {np.nanstd(TBs_mirac[:,m])}"
                    )
            else:
                pass
    elif band == "G":
        for m, freq in enumerate(Mirac_frequencies[:]):
            if m < 6:
                ax.plot(
                    dates_mirac,
                    TBs_mirac[:, m],
                    "o",
                    label=f"{Mirac_frequencies[m]:.2f} GHz",
                    markersize=msize,
                )
            else:
                pass
                if print_stats:
                    print(
                        f"{freq} GHz: daily mean:{np.nanmean(TBs_mirac[:,m])} , daily max: {np.nanmax(TBs_mirac[:,m])}, daily min {np.nanmin(TBs_mirac[:,m])}, daily std: {np.nanstd(TBs_mirac[:,m])}"
                    )
    else:
        print("band must be either K, V, G or highfreq")
    ax.legend(fontsize=fontsizelegend, markerscale=mscale)
    if ylim != "default":
        ax.set_ylim(ylim[0], ylim[1])
    hatpro_ds.close()
    lhumpro_ds.close()
    if save:
        file = os.path.join(
            os.environ["PATH_PLOTS"],
            f"quicklooks/mwr/{filename}",
            f"{Constants.CAMPAIGN_NAME}_hatpro_mirac-p_{filename}_quicklook_{band}band_{date.strftime('%Y%m%d')}.png",
        )
        print(f"Writing plot {file}")
        plt.savefig(
            file,
            dpi=300,
            bbox_inches="tight",
        )
    if show:
        plt.show()

    plt.close()


def plot_mwr_stats_quicklook_oneband(
    startdate,
    enddate,
    scan,
    temporal_resolution="1h",
    band="V",
    ylim="default",
    downwelling=False,
    show=True,
    save=False,
    print_stats=False,
):
    """
     plot_mwr_zenith_daily_quicklook(date,show=True, save=False)
    Time series of TB measurement (min,max, mean) per hour of HATPRO or LHUMPRO for one day
    date is the day the plot is created for
    scan is the scan type (ZENITH or EMIS), boundary layer scan has extra plotting function
    band is the band that should be plotted: "K", "V", "G", or "highfreq"
    if downwelling is True and scan type is EMIS then the downwelling TB at 127 degrees are plotted.
    """

    fig = plt.figure(figsize=(15, 10))
    matplotlib.rcParams["ytick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    matplotlib.rcParams["xtick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    gs = fig.add_gridspec(4, 2, width_ratios=[1, 0.3])
    axmean = fig.add_subplot(gs[0, 0])
    axmin = fig.add_subplot(gs[1, 0])
    axmax = fig.add_subplot(gs[2, 0])
    axstd = fig.add_subplot(gs[3, 0])

    axleg = fig.add_subplot(gs[0, 1])

    prop_cycle = plt.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    for date in pd.date_range(startdate, enddate):
        print("reading in date", date)
        Hatpro_frequencies = [
            22.24,
            23.04,
            23.84,
            25.44,
            26.24,
            27.84,
            31.4,
            51.26,
            52.28,
            53.86,
            54.94,
            56.66,
            57.3,
            58,
        ]
        Mirac_frequencies = [
            183.91,
            184.81,
            185.81,
            186.81,
            188.31,
            190.81,
            243.0,
            340.0,
        ]
        if scan == "ZENITH":
            title = (
                f"MWR observation zenith resampled to {temporal_resolution}"
            )
            filename = "zenith"
        elif scan == "EMIS" and downwelling == False:
            title = f"MWR surface observation 53° off-nadir resampled to {temporal_resolution}"
            filename = "surface_53"
        elif scan == "EMIS" and downwelling == True:
            title = f"MWR downwelling TB observation 127° off-nadir resampled to {temporal_resolution}"
            filename = "downwelling_127"
        if band == "K":
            hatpro_ds = read_scan(date, "hatpro", scan, daily_file=True)
            hatpro_ds = hatpro_ds.resample(
                time=temporal_resolution
            )  # .reduce(np.nanmin)
            for m, freq in enumerate(Hatpro_frequencies):
                if m < 7:
                    axmean.plot(
                        hatpro_ds.reduce(np.nanmean).time,
                        hatpro_ds.reduce(np.nanmean).TBs[:, m],
                        "o",
                        label=f"{Hatpro_frequencies[m]} GHz",
                        markersize=msize,
                        color=colors[m],
                    )
                    axmin.plot(
                        hatpro_ds.reduce(np.nanmin).time,
                        hatpro_ds.reduce(np.nanmin).TBs[:, m],
                        "o",
                        label=f"{Hatpro_frequencies[m]} GHz",
                        markersize=msize,
                        color=colors[m],
                    )
                    axmax.plot(
                        hatpro_ds.reduce(np.nanmax).time,
                        hatpro_ds.reduce(np.nanmax).TBs[:, m],
                        "o",
                        label=f"{Hatpro_frequencies[m]} GHz",
                        markersize=msize,
                        color=colors[m],
                    )
                    axstd.plot(
                        hatpro_ds.reduce(np.nanstd).time,
                        hatpro_ds.reduce(np.nanstd).TBs[:, m],
                        "o",
                        label=f"{Hatpro_frequencies[m]} GHz",
                        markersize=msize,
                        color=colors[m],
                    )
                else:
                    pass

        elif band == "V":
            hatpro_ds = read_scan(date, "hatpro", scan, daily_file=True)
            hatpro_ds = hatpro_ds.resample(
                time=temporal_resolution
            )  # .reduce(np.nanmin)
            for m, freq in enumerate(Hatpro_frequencies):
                if m >= 7:
                    axmean.plot(
                        hatpro_ds.reduce(np.nanmean).time,
                        hatpro_ds.reduce(np.nanmean).TBs[:, m],
                        "o",
                        label=f"{Hatpro_frequencies[m]} GHz",
                        markersize=msize,
                        color=colors[m - 7],
                    )
                    axmin.plot(
                        hatpro_ds.reduce(np.nanmin).time,
                        hatpro_ds.reduce(np.nanmin).TBs[:, m - 7],
                        "o",
                        label=f"{Hatpro_frequencies[m]} GHz",
                        markersize=msize,
                        color=colors[m - 7],
                    )
                    axmax.plot(
                        hatpro_ds.reduce(np.nanmax).time,
                        hatpro_ds.reduce(np.nanmax).TBs[:, m],
                        "o",
                        label=f"{Hatpro_frequencies[m]} GHz",
                        markersize=msize,
                        color=colors[m - 7],
                    )
                    axstd.plot(
                        hatpro_ds.reduce(np.nanstd).time,
                        hatpro_ds.reduce(np.nanstd).TBs[:, m],
                        "o",
                        label=f"{Hatpro_frequencies[m]} GHz",
                        markersize=msize,
                        color=colors[m - 7],
                    )
                else:
                    pass

        #  hatpro_ds.close()

        elif band == "highfreq":
            lhumpro_ds = read_scan(date, "mirac-p", scan, daily_file=True)
            lhumpro_ds = lhumpro_ds.resample(time=temporal_resolution)
            for m, freq in enumerate(Mirac_frequencies[:]):
                if m >= 6:
                    axmean.plot(
                        lhumpro_ds.reduce(np.nanmean).time,
                        lhumpro_ds.reduce(np.nanmean).TBs[:, m],
                        "o",
                        label=f"{Mirac_frequencies[m]:.2f} GHz",
                        markersize=msize,
                        color=colors[m - 6],
                    )
                    axmin.plot(
                        lhumpro_ds.reduce(np.nanmean).time,
                        lhumpro_ds.reduce(np.nanmin).TBs[:, m],
                        "o",
                        label=f"{Mirac_frequencies[m]:.2f} GHz",
                        markersize=msize,
                        color=colors[m - 6],
                    )
                    axmax.plot(
                        lhumpro_ds.reduce(np.nanmean).time,
                        lhumpro_ds.reduce(np.nanmax).TBs[:, m],
                        "o",
                        label=f"{Mirac_frequencies[m]:.2f} GHz",
                        markersize=msize,
                        color=colors[m - 6],
                    )
                    axstd.plot(
                        lhumpro_ds.reduce(np.nanstd).time,
                        lhumpro_ds.reduce(np.nanstd).TBs[:, m],
                        "o",
                        label=f"{Mirac_frequencies[m]:.2f} GHz",
                        markersize=msize,
                        color=colors[m - 6],
                    )
                else:
                    pass
        elif band == "G":
            lhumpro_ds = read_scan(date, "mirac-p", scan, daily_file=True)
            lhumpro_ds = lhumpro_ds.resample(time=temporal_resolution)
            for m, freq in enumerate(Mirac_frequencies[:]):
                if m >= 6:
                    pass
                else:
                    axmean.plot(
                        lhumpro_ds.reduce(np.nanmean).time,
                        lhumpro_ds.reduce(np.nanmean).TBs[:, m],
                        "o",
                        label=f"{Mirac_frequencies[m]:.2f} GHz",
                        markersize=msize,
                        color=colors[m - 6],
                    )
                    axmin.plot(
                        lhumpro_ds.reduce(np.nanmean).time,
                        lhumpro_ds.reduce(np.nanmin).TBs[:, m],
                        "o",
                        label=f"{Mirac_frequencies[m]:.2f} GHz",
                        markersize=msize,
                        color=colors[m - 6],
                    )
                    axmax.plot(
                        lhumpro_ds.reduce(np.nanmean).time,
                        lhumpro_ds.reduce(np.nanmax).TBs[:, m],
                        "o",
                        label=f"{Mirac_frequencies[m]:.2f} GHz",
                        markersize=msize,
                        color=colors[m - 6],
                    )
                    axstd.plot(
                        lhumpro_ds.reduce(np.nanstd).time,
                        lhumpro_ds.reduce(np.nanstd).TBs[:, m],
                        "o",
                        label=f"{Mirac_frequencies[m]:.2f} GHz",
                        markersize=msize,
                        color=colors[m - 6],
                    )
        #   lhumpro_ds.close()

        else:

            print("band must be either K, V, G or highfreq")
    #  ax.legend(fontsize=fontsizelegend, markerscale=mscale)
    for nn, ax in enumerate([axmean, axmax, axmin, axstd]):
        ax.set_xlim(startdate, enddate)
        locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.get_offset_text().set_size(
            fontsizetix
        )  ##access concise date formatter thing
        ###labels
    axstd.set_xlabel("Date (UTC)", fontsize=fontsizey)
    plt.suptitle(
        f"{title} {band} band", x=0.5, y=0.94, fontsize=fontsize_title
    )
    axmean.set_ylabel("mean TB (K)", fontsize=fontsizey)
    axmax.set_ylabel("max TB (K)", fontsize=fontsizey)
    axmin.set_ylabel("min TB (K)", fontsize=fontsizey)
    axstd.set_ylabel("std TB (K)", fontsize=fontsizey)
    #  axmean.set_xticks([])
    if band == "K":

        for m, freq in enumerate(Hatpro_frequencies):
            if m < 7:
                axleg.plot(
                    [],
                    [],
                    "o",
                    label=f"{Hatpro_frequencies[m]} GHz",
                    markersize=msize,
                    color=colors[m],
                )
            else:
                pass
    elif band == "V":

        for m, freq in enumerate(Hatpro_frequencies):
            if m >= 7:
                axleg.plot(
                    [],
                    [],
                    "o",
                    label=f"{Hatpro_frequencies[m]} GHz",
                    markersize=msize,
                    color=colors[m - 7],
                )
            else:
                pass

    #  hatpro_ds.close()
    elif band == "highfreq":

        for m, freq in enumerate(Mirac_frequencies[:]):
            if m >= 6:
                axleg.plot(
                    [],
                    [],
                    "o",
                    label=f"{Mirac_frequencies[m]:.2f} GHz",
                    markersize=msize,
                    color=colors[m - 6],
                )
            else:
                pass
    elif band == "G":

        for m, freq in enumerate(Mirac_frequencies[:]):
            if m >= 6:
                pass
            else:
                axleg.plot(
                    [],
                    [],
                    "o",
                    label=f"{Mirac_frequencies[m]:.2f} GHz",
                    markersize=msize,
                    color=colors[m - 6],
                )
    axleg.axis("off")
    axleg.legend(fontsize=fontsizelegend, markerscale=mscale)
    if axstd.get_ylim()[1] > 100:
        axstd.set_ylim(0, 100)

    if axmax.get_ylim()[1] > 285:
        axmax.set_ylim(0, 285)

    if save:        
        plot_path = os.path.join(os.environ["PATH_PLOTS"],
                                 "quicklooks/mwr/stats/")
        os.makedirs(plot_path, exist_ok=True)
        plotname = f"{Constants.CAMPAIGN_NAME}_mwr_stats_{filename}_quicklook_{band}band_{startdate.strftime('%Y%m%d')}-{enddate.strftime('%Y%m%d')}"
        plotfile = os.path.join(plot_path, plotname + ".png")
        print(f"Saved {plotfile}....")
        plt.savefig(
            plotfile,
            dpi=150,
            bbox_inches="tight",
        )
    if show:
        plt.show()

    plt.close()


def plot_mwr_daily_quicklook_histogram(
    date,
    scan,
    downwelling=False,
    show=True,
    save=False,
    kde_kwargs={"bw_adjust": 0.2},
):
    """
     plot_mwr_daily_quicklook_histogram(date, scan, downwelling=False, show=True, save=False,kde_kwargs={ bw_adjust:0.2}):
    Histogram of TB measurement of HATPRO and LHUMPRO for one day
    date is the day the plot is created for
    scan is the scan type (ZENITH or EMIS), boundary layer scan has extra plotting function
    if downwelling is True and scan type is EMIS then the downwelling TB at 127 degrees are plotted.
    """

    hatpro_ds = read_scan(date, "hatpro", scan, daily_file=True)
    lhumpro_ds = read_scan(date, "mirac-p", scan, daily_file=True)
    Hatpro_frequencies = [
        22.24,
        23.04,
        23.84,
        25.44,
        26.24,
        27.84,
        31.4,
        51.26,
        52.28,
        53.86,
        54.94,
        56.66,
        57.3,
        58,
    ]
    Mirac_frequencies = lhumpro_ds.Freq.data
    if scan == "ZENITH":
        dates_hatpro = hatpro_ds.time.values
        TBs_hatpro = hatpro_ds.TBs.values
        dates_mirac = lhumpro_ds.time.values
        TBs_mirac = lhumpro_ds.TBs.values
        title = f"MWR observation zenith {date:%Y-%m-%d}"
        filename = "zenith"
    elif scan == "EMIS" and downwelling == False:
        dates_hatpro = hatpro_ds.time.values[hatpro_ds.ElAng == 53.0]
        TBs_hatpro = hatpro_ds.TBs.values[hatpro_ds.ElAng == 53.0]
        dates_mirac = lhumpro_ds.time.values[lhumpro_ds.ElAng == 53]
        TBs_mirac = lhumpro_ds.TBs.values[lhumpro_ds.ElAng == 53]
        title = f"MWR surface observation 53° off-nadir {date:%Y-%m-%d}"
        filename = "surface_53"
    elif scan == "EMIS" and downwelling == True:
        dates_hatpro = hatpro_ds.time.values[hatpro_ds.ElAng == 127.0]
        TBs_hatpro = hatpro_ds.TBs.values[hatpro_ds.ElAng == 127.0]
        dates_mirac = lhumpro_ds.time.values[lhumpro_ds.ElAng == 127.0]
        TBs_mirac = lhumpro_ds.TBs.values[lhumpro_ds.ElAng == 127.0]
        title = (
            f"MWR downwelling TB observation 127° off-nadir {date:%Y-%m-%d}"
        )
        filename = "downwelling_127"

    fig = plt.figure(figsize=(20, 20))
    matplotlib.rcParams["ytick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    matplotlib.rcParams["xtick.labelsize"] = (
        fontsizetix  ##to adjust colorbar ticklabels
    )
    plt.suptitle(f"{title}", x=0.5, y=0.95, fontsize=fontsize_title)
    gs = fig.add_gridspec(
        2, 2, hspace=0.35, wspace=0.35
    )  # width_ratios= [1,1,1,1],
    axkband = fig.add_subplot(gs[0, 0])
    axkband.text(
        -0.1, 1.1, "a)", transform=axkband.transAxes, size=20, weight="bold"
    )
    axvband = fig.add_subplot(gs[0, 1])
    axvband.text(
        -0.1, 1.1, "b)", transform=axvband.transAxes, size=20, weight="bold"
    )
    axmirac1 = fig.add_subplot(gs[1, 0])
    axmirac1.text(
        -0.1, 1.1, "c)", transform=axmirac1.transAxes, size=20, weight="bold"
    )
    axmirac2 = fig.add_subplot(gs[1, 1])
    axmirac2.text(
        -0.1, 1.1, "d)", transform=axmirac2.transAxes, size=20, weight="bold"
    )

    for nn, ax in enumerate([axkband, axvband, axmirac1, axmirac2]):
        ax.grid(alpha=0.5)
        # ax.set_xticks(fontsize=14)
        # ax.set_yticks(fontsize=14)
        ax.set_ylabel("Density", fontsize=fontsizey)
        ax.set_xlabel("TB (K)", fontsize=fontsizey)
    ###plot
    for m, freq in enumerate(Hatpro_frequencies):
        if m < 7:
            sns.kdeplot(
                TBs_hatpro[:, m],
                ax=axkband,
                label=f"{Hatpro_frequencies[m]} GHz",
                **kde_kwargs,
            )
        else:
            sns.kdeplot(
                TBs_hatpro[:, m],
                ax=axvband,
                label=f"{Hatpro_frequencies[m]} GHz",
                **kde_kwargs,
            )
    axvband.legend(fontsize=fontsizelegend, markerscale=mscale)
    axkband.legend(fontsize=fontsizelegend, markerscale=mscale)

    for m, freq in enumerate(Mirac_frequencies[:]):
        if m >= 6:
            sns.kdeplot(
                TBs_mirac[:, m],
                ax=axmirac1,
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                **kde_kwargs,
            )
        else:
            sns.kdeplot(
                TBs_mirac[:, m],
                ax=axmirac2,
                label=f"{Mirac_frequencies[m]:.2f} GHz",
                **kde_kwargs,
            )
    axmirac1.legend(fontsize=fontsizelegend, markerscale=mscale, ncol=6)
    axmirac2.legend(fontsize=fontsizelegend, markerscale=mscale)

    hatpro_ds.close()
    lhumpro_ds.close()
    if save:
        file = os.path.join(
            os.environ["PATH_PLOTS"],
            "quicklooks/mwr/histograms_daily",
            f"{Constants.CAMPAIGN_NAME}_hatpro_mirac-p_{filename}_quicklook_{date.strftime('%Y%m%d')}_histogram.png",
        )
        print(f"Writing plot {file}")
        plt.savefig(
            file,
            dpi=300,
            bbox_inches="tight",
        )
    if show:
        plt.show()

    plt.close()


def main(date):
    """
    Runs quicklooks for HATPRO and LHUMPRO for a specific date.
    """
    
    for scan in ["ZENITH", "EMIS"]:
        downwelling = [False]
        if scan == 'EMIS': downwelling = [False, True]
        for dw in downwelling:
            try:
                plot_mwr_daily_quicklook(datetime.strptime(date, "%Y-%m-%d"), 
                                        scan, 
                                        downwelling=dw,
                                        save=True,
                                        show=False)
            except FileNotFoundError:
                continue

    # weather station and housekeeping data quicklook
    for variable in ["MET", "HKD"]:
        for instrument in ["hatpro", "mirac-p"]:
            try:
                # combines files from all scans into a single file
                ds_list = list()
                for scan in (Constants.SCANS + ("",)):
                    try:
                        ds = open_mwr_file(
                            variable=variable,
                            date=date,
                            instrument=instrument,
                            scan=scan,
                            daily_file=False,
                            allow_duplicates=False)
                        ds_list.append(ds)
                    except FileNotFoundError:
                        continue
                if len(ds_list) > 0:
                    ds = xr.concat(ds_list, dim='time').sortby('time')
                else:
                    continue

                if variable == "HKD":
                    quicklook_hkd(date, instrument, ds, show=False, save=True)

                elif variable == "MET":
                    quicklook_met(date, instrument, ds, show=False, save=True)

            except FileNotFoundError:
                print(f"No {instrument} {variable} data found for {date}.")


def quicklook_hkd(date, instrument, ds, show=True, save=False):
    """
    Time series of MWR housekeeping data for one day.
    """

    date = pd.Timestamp(date)

    fig, axes = plt.subplots(
        8, 1, figsize=(6, 8), sharex=True, layout="constrained"
    )

    fig.suptitle(
        f"{instrument.upper()} housekeeping data ({date.strftime('%Y-%m-%d')})"
    )

    kwargs = {"s": 5, "lw": 0}

    axes[0].scatter(ds.time, ds.Rec1_T, label="R1", **kwargs)
    axes[0].scatter(ds.time, ds.Rec2_T, label="R2", **kwargs)
    axes[0].set_ylabel("$T_{rec}$ [K]")
    axes[0].legend(loc="center left", bbox_to_anchor=(1, 0.5))

    axes[1].scatter(ds.time, ds.Rec1_Stab, label="R1", **kwargs)
    axes[1].scatter(ds.time, ds.Rec2_Stab, label="R2", **kwargs)
    axes[1].set_ylabel("Rec. stab. [K]")
    axes[1].legend(loc="center left", bbox_to_anchor=(1, 0.5))

    axes[2].scatter(ds.time, ds.AT1_T, label="AT1", **kwargs)
    axes[2].scatter(ds.time, ds.AT2_T, label="AT2", **kwargs)
    axes[2].set_ylabel("$T_{amb}$ [K]")
    axes[2].legend(loc="center left", bbox_to_anchor=(1, 0.5))

    axes[3].scatter(ds.time, ds.AlFl, **kwargs)
    axes[3].set_ylim(-0.1, 1.1)
    axes[3].set_ylabel("Alarm")

    axes[4].scatter(ds.time, ds.QualFl, **kwargs)
    axes[4].set_ylabel("Quality")

    axes[5].scatter(ds.time, ds.StatFl, **kwargs)
    axes[5].set_ylabel("Status")

    axes[6].scatter(ds.time, ds.GPSLong, **kwargs)
    axes[6].set_ylabel("Lon [°E]")

    axes[7].scatter(ds.time, ds.GPSLat, **kwargs)
    axes[7].set_ylabel("Lat [°N]")

    axes[-1].set_xlabel("Time [UTC]")
    axes[-1].xaxis.set_major_locator(mdates.HourLocator(interval=3))
    axes[-1].xaxis.set_minor_locator(mdates.HourLocator(interval=1))
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H"))
    axes[-1].set_xlim(date, date + pd.Timedelta(24 * 3600 - 1, "s"))

    if save:
        
        plot_path = os.path.join(os.environ["PATH_PLOTS"],
                                 "quicklooks/mwr/hkd")
        os.makedirs(plot_path, exist_ok=True)
        plotname = f"{Constants.CAMPAIGN_NAME}_{instrument}_hkd_quicklook_{date.strftime('%Y%m%d')}"
        plotfile = os.path.join(plot_path, plotname + ".png")
        print(f"Writing {instrument} HKD plot {plotfile}")
        plt.savefig(
            plotfile,
            dpi=150,
            bbox_inches="tight",
        )

    if show:
        plt.show()

    plt.close()


def quicklook_met(date, instrument, ds, show=True, save=False):
    """
    Time series of MWR weather station data for one day.
    """

    date = pd.Timestamp(date)

    # rename rame rate variable like all other variables
    ds = ds.rename_vars({"maximum_Rain_Rate": "Max_RR"})

    # wind speed to m/s
    ds["Surf_WS"] /= 3.6
    ds["Min_WS"] /= 3.6
    ds["Max_WS"] /= 3.6

    fig, axes = plt.subplots(
        7, 1, figsize=(6, 8), sharex=True, layout="constrained"
    )

    fig.suptitle(
        f"{instrument.upper()} weather station ({date.strftime('%Y-%m-%d')})"
    )

    kwargs = {"s": 5, "lw": 0}

    # rain flag
    axes[0].scatter(ds.time, ds.RF, label="R1", **kwargs)
    axes[0].set_ylim(-0.1, 1.1)
    axes[0].set_yticks([0, 1])
    axes[0].set_yticklabels(["no rain", "rain"])

    # other variables
    ylabels = {
        "P": "p [hPa]",
        "T": "T [K]",
        "RH": "RH [%]",
        "WS": "U [m/s]",
        "WD": "D [°]",
        "RR": "RR [mm/h]",
    }
    var_lst = ["RR", "P", "T", "RH", "WS", "WD"]
    stats = ["Surf", "Min", "Max"]
    for i, v in enumerate(var_lst, start=1):
        for stat in stats:
            axes[i].scatter(
                ds.time, ds[f"{stat}_{v}"], label=stat.lower(), **kwargs
            )
        axes[i].set_ylabel(ylabels[v])
        axes[i].legend(loc="center left", bbox_to_anchor=(1, 0.5))

    axes[-1].set_xlabel("Time [UTC]")
    axes[-1].xaxis.set_major_locator(mdates.HourLocator(interval=3))
    axes[-1].xaxis.set_minor_locator(mdates.HourLocator(interval=1))
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H"))
    axes[-1].set_xlim(date, date + pd.Timedelta(24 * 3600 - 1, "s"))

    if save:
        plot_path = os.path.join(os.environ["PATH_PLOTS"],
                                 "quicklooks/mwr/met")
        os.makedirs(plot_path, exist_ok=True)
        plotname = f"{Constants.CAMPAIGN_NAME}_{instrument}_met_quicklook_{date.strftime('%Y%m%d')}"
        plotfile = os.path.join(plot_path, plotname + ".png")
        print(f"Writing {instrument} MET plot {plotfile}")
        plt.savefig(
            plotfile,
            dpi=150,
            bbox_inches="tight",
        )

    if show:
        plt.show()
        pdb.set_trace()

    plt.close()


if __name__ == "__main__":
    daterange = np.arange(np.datetime64(str(Constants.DATE_START)).astype('datetime64[D]'), 
                          np.datetime64(str(Constants.DATE_END)) + np.timedelta64(1,"D"), 
                          np.timedelta64(1,"D"))
    for date in daterange:
        main(date=str(date))
