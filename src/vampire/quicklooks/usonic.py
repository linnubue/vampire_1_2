"""
Plots hourly ultrasonic anemometer data for a given time range.
"""

import os
import sys

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from vampire.io.readers.usonic import read_usonic

matplotlib.use("TkAgg")


def main(date):

    times = pd.date_range(
        date, pd.Timestamp(date) + pd.Timedelta(23, "h"), freq="h"
    )
    for time in times:
        try:
            df_inst = read_usonic(time, product="instant")
            df_avg = read_usonic(time, product="averaged")
            quicklook_usonic(
                time=time,
                df_inst=df_inst,
                df_avg=df_avg,
                show=False,
                save=True,
            )

        except FileNotFoundError:
            print(f"No ultrasonic data found for {time}.")


def quicklook_usonic(time, df_inst, df_avg, show=True, save=False):
    """
    Time series of ultrasonic anemometer data for one hour.
    """

    fig, axes = plt.subplots(9, 1, figsize=(6, 8), sharex=True)

    axes[0].set_title(f"Ultrasonic anemometer ({time})")

    kwargs_inst = dict(s=1, lw=0, alpha=0.5, color="k", label="30 Hz")
    kwargs_avg = dict(s=5, lw=0, color="gray", label="10 s avg.")

    # wind speed
    axes[0].scatter(df_inst.index, df_inst["vel"], **kwargs_inst)
    axes[0].scatter(df_avg.index, df_avg["vel"], **kwargs_avg)
    axes[0].set_ylabel("U [m s$^{-1}$]")
    axes[0].set_ylim(0, df_inst["vel"].max())

    # wind direction
    axes[1].scatter(df_inst.index, df_inst["dir"], **kwargs_inst)
    axes[1].scatter(df_avg.index, df_avg["dir"], **kwargs_avg)
    axes[1].set_ylabel("D [°]")
    axes[1].set_ylim(0, 360)

    # wind component x
    axes[2].scatter(df_inst.index, df_inst["x"], **kwargs_inst)
    axes[2].scatter(df_avg.index, df_avg["x"], **kwargs_avg)
    axes[2].axhline(0, color="red")
    axes[2].set_ylabel("x [m s$^{-1}$]")
    axes[2].set_ylim(df_inst["x"].min(), df_inst["x"].max())

    # wind component y
    axes[3].scatter(df_inst.index, df_inst["y"], **kwargs_inst)
    axes[3].scatter(df_avg.index, df_avg["y"], **kwargs_avg)
    axes[3].axhline(0, color="red")
    axes[3].set_ylabel("y [m s$^{-1}$]")
    axes[3].set_ylim(df_inst["y"].min(), df_inst["y"].max())

    # wind component z
    axes[4].scatter(df_inst.index, df_inst["z"], **kwargs_inst)
    axes[4].scatter(df_avg.index, df_avg["z"], **kwargs_avg)
    axes[4].axhline(0, color="red")
    axes[4].set_ylabel("z [m s$^{-1}$]")
    axes[4].set_ylim(df_inst["z"].min(), df_inst["z"].max())

    # roll
    axes[5].scatter(df_inst.index, df_inst["roll"], **kwargs_inst)
    axes[5].scatter(df_avg.index, df_avg["roll"], **kwargs_avg)
    axes[5].axhline(0, color="red")
    axes[5].set_ylabel("Roll [°]")
    axes[5].set_ylim(df_inst["roll"].min(), df_inst["roll"].max())

    # pitch
    axes[6].scatter(df_inst.index, df_inst["pitch"], **kwargs_inst)
    axes[6].scatter(df_avg.index, df_avg["pitch"], **kwargs_avg)
    axes[6].axhline(0, color="red")
    axes[6].set_ylabel("Pitch [°]")
    axes[6].set_ylim(df_inst["pitch"].min(), df_inst["pitch"].max())

    # rotate
    axes[7].scatter(df_inst.index, df_inst["rotate"], **kwargs_inst)
    axes[7].scatter(df_avg.index, df_avg["rotate"], **kwargs_avg)
    axes[7].axhline(0, color="red")
    axes[7].set_ylabel("Rot. [°]")
    axes[7].set_ylim(-2, 2)

    # temperature
    axes[8].scatter(df_inst.index, df_inst["T"], **kwargs_inst)
    axes[8].scatter(df_avg.index, df_avg["T"], **kwargs_avg)
    axes[8].set_ylabel("T [°C]")
    axes[8].set_ylim(df_inst["T"].min(), df_inst["T"].max())

    axes[8].legend(
        loc="lower center", bbox_to_anchor=(0.5, -1.2), ncol=2, frameon=False
    )
    axes[8].xaxis.set_major_locator(mdates.HourLocator(interval=3))
    axes[8].xaxis.set_minor_locator(mdates.HourLocator(interval=1))
    axes[8].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    axes[8].set_xlim(df_inst.index.min(), df_inst.index.max())

    for ax in axes:
        ax.grid()

    if save:
        outdir = os.path.join(
            os.environ["PATH_PLOTS"],
            "quicklooks/usonic",
            time.strftime('%Y%m%d'),
        )
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        file = os.path.join(
            outdir,
            f"usonic_quicklook_{time.strftime('%Y%m%d_%H%M')}.png",
        )
        print(f"Writing ultrasonic plot {file}")
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
