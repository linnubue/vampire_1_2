"""
Quicklook of MiRAC-A Ze and Tb or GRaWAC Ze.
"""

import os
import sys
from glob import glob

import cmcrameri.cm as cmc
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from vampire.io.readers.radar import read_radar

INSTRUMENTS = {"grawac": "GRaWAC", "mirac-a": "MiRAC-A"}


def main(date, instrument, chirp_program):
    """
    Plots hourly MiRAC-A Ze and TB or GRaWAC Ze quicklooks for a given date.
    """

    date = pd.Timestamp(date)
    times = pd.date_range(date, date + pd.Timedelta(23, "h"), freq="1h")

    for time in times:

        ds = read_radar(
            instrument=instrument,
            chirp_program=chirp_program,
            date=time,
            hourly=True,
        )

        if ds is None:
            print(
                f"No {INSTRUMENTS[instrument]} {chirp_program} data for {str(time)}"
            )
            continue

        print("Starting plot")
        plot_ze_tb(ds=ds, instrument=instrument, time=time)
        plot_vm(ds=ds, instrument=instrument, time=time)


def plot_ze_tb(ds, instrument, time):
    """
    Plot Ze and TB.
    """

    if instrument == "mirac-a":
        subplot_kwargs = dict(
            mosaic=[["ze"], ["tb"]], height_ratios=[4, 1], sharex=True
        )
    elif instrument == "grawac":
        subplot_kwargs = dict(mosaic=[["ze"]])

    fig, axs = plt.subplot_mosaic(
        figsize=(7, 5),
        layout="constrained",
        **subplot_kwargs,
    )

    axs["ze"].set_title(f"{INSTRUMENTS[instrument]} ({str(time)})")

    im = axs["ze"].pcolormesh(
        ds.time,
        ds.range * 1e-3,
        10 * np.log10(ds["ZE"].T),
        vmin=-45,
        vmax=30,
        cmap=cmc.batlow,
    )
    fig.colorbar(im, ax=axs["ze"], label="Ze [dBz]")
    axs["ze"].set_ylabel("Range [km]")

    # 89 GHz tb
    if instrument == "mirac-a":
        axs["tb"].scatter(
            ds.time,
            ds.DDTb,
            color="k",
            s=5,
            lw=0,
        )
        axs["tb"].set_ylabel("89 GHz TB [K]")

        axs["tb"].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        axs["tb"].set_xlim(time, time + pd.Timedelta(1, "h"))

    else:
        axs["ze"].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        axs["ze"].set_xlim(time, time + pd.Timedelta(1, "h"))

    outdir = os.path.join(
        os.environ["PATH_PLOTS"],
        f"quicklooks/{instrument}/",
        time.strftime("%Y%m%d"),
    )
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    axs["ze"].set_ylim(0, 12)
    plt.savefig(
        os.path.join(
            outdir,
            f"VAMPIRE_{instrument}_0to12km_{time.strftime('%Y%m%d_%H')}.png",
        ),
        dpi=300,
    )

    axs["ze"].set_ylim(0, 3)
    plt.savefig(
        os.path.join(
            outdir,
            f"VAMPIRE_{instrument}_0to3km_{time.strftime('%Y%m%d_%H')}.png",
        ),
        dpi=300,
    )

    plt.close()


def plot_vm(ds, instrument, time):
    """
    Plot mean Doppler velocity.
    """

    fig, ax = plt.subplots(
        1,
        1,
        figsize=(7, 5),
        layout="constrained",
    )

    ax.set_title(f"{INSTRUMENTS[instrument]} ({str(time)})")

    im = ax.pcolormesh(
        ds.time,
        ds.range * 1e-3,
        ds.MeanVel.T,
        vmin=-3,
        vmax=3,
        cmap=cmc.berlin,
    )
    fig.colorbar(im, ax=ax, label="Vm [m/s]")
    ax.set_ylabel("Range [km]")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.set_xlim(time, time + pd.Timedelta(1, "h"))

    outdir = os.path.join(
        os.environ["PATH_PLOTS"],
        f"quicklooks/{instrument}/",
        time.strftime("%Y%m%d"),
    )
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    ax.set_ylim(0, 12)
    plt.savefig(
        os.path.join(
            outdir,
            f"VAMPIRE_{instrument}_vm_0to12km_{time.strftime('%Y%m%d_%H')}.png",
        ),
        dpi=300,
    )

    ax.set_ylim(0, 3)
    plt.savefig(
        os.path.join(
            outdir,
            f"VAMPIRE_{instrument}_vm_0to3km_{time.strftime('%Y%m%d_%H')}.png",
        ),
        dpi=300,
    )

    plt.close()


def chirp_programs():
    """
    Chirp programs as a function of time based on file names:

    240816_120000_P00_ZEN.LV1.NC
    """

    chirps = {}
    for s in INSTRUMENTS:
        chirps[s] = pd.DataFrame()
        chirps[s][f"files"] = glob(
            os.path.join(os.environ["VAMPIRE_DATA"], f"{s}/Y2024/M*/D*/*.NC")
        )
        chirps[s][f"c"] = (
            chirps[s][f"files"]
            .str.split("_", expand=True)
            .iloc[:, -2]
            .str[1:]
            .astype(int)
        )
        chirps[s][f"time"] = pd.to_datetime(
            chirps[s][f"files"].str[-28:-15], format="%y%m%d_%H%M%S"
        )

    fig, ax = plt.subplots(2, 1, sharex=True, figsize=(10, 5), sharey=True)

    for i, (s, label) in enumerate(INSTRUMENTS.items()):
        ax[i].set_title("Chirp programs " + label)
        ax[i].scatter(
            chirps[s]["time"],
            chirps[s]["c"],
            c=chirps[s]["c"],
            cmap=cmc.batlow,
        )

        ax[i].yaxis.set_major_locator(mticker.MultipleLocator(base=1))

        ax[i].xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax[i].xaxis.set_major_formatter(mdates.DateFormatter("%d"))

        ax[i].grid()

    ax[0].set_ylabel("Chirp program")
    ax[1].set_ylabel("Chirp program")
    ax[-1].set_xlabel("Day of month")

    plt.savefig(
        os.path.join(
            os.environ["PATH_PLOTS"],
            f"quicklooks/",
            f"VAMPIRE_mirac_a_grawac_chirp_time_series.png",
        ),
        dpi=300,
    )

    plt.close()


if __name__ == "__main__":
    chirp_programs()
    main(date=sys.argv[1], instrument="grawac", chirp_program="P00")
    main(date=sys.argv[1], instrument="grawac", chirp_program="P02")
    main(date=sys.argv[1], instrument="grawac", chirp_program="P04")
    main(date=sys.argv[1], instrument="grawac", chirp_program="P05")
    main(date=sys.argv[1], instrument="grawac", chirp_program="P06")
    main(date=sys.argv[1], instrument="grawac", chirp_program="P09")

    main(date=sys.argv[1], instrument="mirac-a", chirp_program="P00")
    main(date=sys.argv[1], instrument="mirac-a", chirp_program="P04")
    main(date=sys.argv[1], instrument="mirac-a", chirp_program="P07")
    main(date=sys.argv[1], instrument="mirac-a", chirp_program="P08")
    main(date=sys.argv[1], instrument="mirac-a", chirp_program="P09")
