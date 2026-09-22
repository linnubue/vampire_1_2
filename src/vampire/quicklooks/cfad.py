"""
CFAD for MiRAC-A and GRaWAC
"""

import os
import sys

import cmcrameri.cm as cmc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xhistogram
import xhistogram.xarray
from dask.diagnostics import ProgressBar

from vampire.io.readers.radar import read_radar

ProgressBar().register()

INSTRUMENTS = {"grawac": "GRaWAC", "mirac_a": "MiRAC-A"}


def main(date, instrument, chirp_program, all=False):
    """
    Plot CFADs.

    Parameters
    ----------
    date : str
        Date in format YYYYMMDD.
    instrument : str
        Instrument name.
    chirp_program : str
        Chirp program.
    all : bool
        Plot all dates as a single CFAD. Default is False.
    """

    date = pd.Timestamp(date)

    if all:
        ds = read_radar(
            instrument=instrument,
            chirp_program=chirp_program,
            date=None,
            hourly=False,
        )
        da_hist_lst = compute_cfad(ds)
        plot_cfad(instrument, da_hist_lst, chirp_program, suffix="all")

    # specific date
    ds = read_radar(
        instrument=instrument, chirp_program=chirp_program, date=date
    )
    if ds is None:
        print(f"No data {instrument} {chirp_program} for {str(date)}")
    else:
        da_hist_lst = compute_cfad(ds)
        plot_cfad(
            instrument,
            da_hist_lst,
            chirp_program,
            suffix=date.strftime("%Y%m%d"),
        )


def compute_cfad(ds):

    try:
        n_chirps = ds.ChirpNum.values[0]
    except:
        n_chirps = ds.ChirpNum.values.item()

    # compute cfad for every chirp range
    ze_bins = np.arange(-80, 50, 0.5)
    d_ze = ze_bins[1:] - ze_bins[:-1]
    ze_bin_edges = np.concatenate(
        [
            [ze_bins[0] - d_ze[0] / 2],
            ze_bins[:-1] + d_ze / 2,
            [ze_bins[-1] + d_ze[-1] / 2],
        ]
    )
    da_hist_lst = []
    for i in range(1, n_chirps + 1):
        da_hist = xhistogram.xarray.histogram(
            10 * np.log10(ds[f"C{str(i)}ZE"]),
            bins=[ze_bin_edges],
            dim=["Time"],
            density=False,
        )
        da_hist = da_hist.compute()
        da_hist_lst.append(da_hist)

    return da_hist_lst


def plot_cfad(instrument, da_hist_lst, chirp_program, suffix):
    """
    Plot radar CFAD
    """

    fig, ax = plt.subplots(1, 1, figsize=(7, 5))

    vmax = da_hist_lst[0].max() * 0.75
    for i, da_hist in enumerate(da_hist_lst, start=1):
        da_hist = da_hist.where(da_hist > 0)
        im = ax.pcolormesh(
            da_hist[f"C{str(i)}ZE_bin"],
            da_hist[f"C{str(i)}Range"] * 1e-3,
            da_hist,
            cmap=cmc.batlow,
            vmin=0,
            vmax=vmax,
            shading="nearest",
        )
    fig.colorbar(im, ax=ax, label="Count")
    ax.set_ylabel("Range [km]")
    ax.set_xlabel("Ze [dB]")

    ax.set_title(
        f"{INSTRUMENTS[instrument]} CFAD {suffix} {chirp_program} (0-12 km)"
    )
    ax.set_ylim(0, 12)
    plt.savefig(
        os.path.join(
            os.environ["PATH_PLOTS"],
            f"quicklooks/{instrument}_cfad",
            f"cfad_{instrument}_{chirp_program}_0to12km_{suffix}.png",
        ),
        dpi=300,
    )

    ax.set_title(
        f"{INSTRUMENTS[instrument]} CFAD {suffix} {chirp_program} (0-6 km)"
    )
    ax.set_ylim(0, 6)
    plt.savefig(
        os.path.join(
            os.environ["PATH_PLOTS"],
            f"quicklooks/{instrument}_cfad",
            f"cfad_{instrument}_{chirp_program}_0to6km_{suffix}.png",
        ),
        dpi=300,
    )

    ax.set_title(
        f"{INSTRUMENTS[instrument]} CFAD {suffix} {chirp_program} (0-3 km)"
    )
    ax.set_ylim(0, 3)
    plt.savefig(
        os.path.join(
            os.environ["PATH_PLOTS"],
            f"quicklooks/{instrument}_cfad",
            f"cfad_{instrument}_{chirp_program}_0to3km_{suffix}.png",
        ),
        dpi=300,
    )

    plt.close()


if __name__ == "__main__":
    main(date=sys.argv[1], instrument="grawac", chirp_program="P00")
    main(date=sys.argv[1], instrument="grawac", chirp_program="P02")
    main(date=sys.argv[1], instrument="grawac", chirp_program="P04")
    main(date=sys.argv[1], instrument="grawac", chirp_program="P05")
    main(date=sys.argv[1], instrument="grawac", chirp_program="P06")
    main(date=sys.argv[1], instrument="grawac", chirp_program="P09")

    main(date=sys.argv[1], instrument="mirac_a", chirp_program="P00")
    main(date=sys.argv[1], instrument="mirac_a", chirp_program="P04")
    main(date=sys.argv[1], instrument="mirac_a", chirp_program="P07")
    main(date=sys.argv[1], instrument="mirac_a", chirp_program="P08")
    main(date=sys.argv[1], instrument="mirac_a", chirp_program="P09")
