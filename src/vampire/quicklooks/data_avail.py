"""
Plots the daily data availability based on time series data of the following 
instruments:

- MiRAC-A: W-band radar
- GRaWAC: G-band radar
- HATPRO: MWR
- LHUMPRO: MWR
- Parsivel: Disdrometer
- Ultrasonic: Anenometer
- FLIR: IR ice camera
- GoPRO: VIS ice camera
- Mobotix: IR/VIS sky camera
- Mini IMU: IMU 1
- RaspberryPi IMU: IMU 2
- Hydrins: INS 20 Hz record from Polarstern
- Radiosonde 00: Our sondes
- Radiosonde 06: DWD sondes
- Radiosonde 12: DWD sondes
- Radiosonde ++: Our additional sondes

Extension
---------
For some times there might be files but while radars were covered with plastic 
or so. Those times should be removed by the radar reader.
"""

import os

import cmcrameri.cm as cmc
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from vampire.constants import Constants
from vampire.io.readers.flir import read_flir_statistics_multiple
from vampire.io.readers.gopro import get_all_times
from vampire.io.readers.hydrins import read_hydrins_multiple
from vampire.io.readers.imupi import read_imupi_multiple
from vampire.io.readers.mobotix import mobotix_dates
from vampire.io.readers.mwr import read_scans
from vampire.io.readers.parsivel import read_parsivel_multiple
from vampire.io.readers.radar import read_all_times
from vampire.io.readers.radiosonde import get_radiosondes
from vampire.io.readers.read_imu import read_imu_multiple
from vampire.io.readers.usonic import read_usonic_multiple


def main():

    da_dct = {}

    print("Mini IMU")
    da_dct = da_miniimu(da_dct)

    print("Radiosonde")
    da_dct = da_radiosonde(da_dct)

    print("MWR")
    da_dct = da_mwr(da_dct)

    print("GRaWAC")
    da_dct = da_grawac(da_dct)

    print("MiRAC-A")
    da_dct = da_mirac_a(da_dct)

    print("FLIR")
    da_dct = da_flir(da_dct)

    print("GoPRO")
    da_dct = da_gopro(da_dct)

    print("Ultrasonic")
    da_dct = da_ultrasonic(da_dct)

    print("Parsivel")
    da_dct = da_parsivel(da_dct)

    print("IMU RaspberryPi")
    da_dct = da_imupi(da_dct)

    print("Hydrins 20 Hz")
    da_dct = da_hydrins(da_dct)

    print("Mobotix")
    da_dct = da_mobotix(da_dct)

    # ensure that no days are missing that get interpolated in the plot
    ds_da = xr.Dataset()
    ds_da.coords["time"] = pd.date_range(
        Constants.DATE_START, Constants.DATE_END, freq="1D"
    )
    for v in da_dct:
        ds_da[v] = da_dct[v]

    # adjustments
    ds_da = adjust(
        ds_da,
        name="MiRAC-A",
        values=100,
        dates=[
            pd.Timestamp("2024-09-05").date(),
            pd.Timestamp("2024-09-06").date(),
            pd.Timestamp("2024-09-07").date(),
        ],
    )

    plot_da(ds_da)


def adjust(ds_da, name, values, dates):
    """
    Allows manual adjustment.
    """

    print("Manually setting {name} to {values} at {dates} ")
    ds_da[name].loc[{"time": dates}] = values

    return ds_da


def da_radiosonde(da_dct):
    """Distinguish 00 UTC, 12 UTC, and additional sondes."""

    files, times = get_radiosondes()
    df = pd.DataFrame(
        index=pd.date_range(Constants.DATE_START, times.max(), freq="h")
    )
    df["sonde"] = 0
    df.loc[times, "sonde"] = 1
    df_12 = df.loc[df.index.hour == 12, "sonde"]
    df_06 = df.loc[df.index.hour == 6, "sonde"]
    df_00 = df.loc[df.index.hour == 0, "sonde"]
    df_extra = df.loc[
        (df.index.hour != 0) & (df.index.hour != 6) & (df.index.hour != 12),
        "sonde",
    ]

    da_dct["Radiosonde 12"] = (
        df_12.groupby(df_12.index.date).sum().to_xarray() * 100
    )
    da_dct["Radiosonde 06"] = (
        df_06.groupby(df_06.index.date).sum().to_xarray() * 100
    )
    da_dct["Radiosonde 00"] = (
        df_00.groupby(df_00.index.date).sum().to_xarray() * 100
    )
    da_dct["Radiosonde ++"] = (
        df_extra.groupby(df_extra.index.date).sum().to_xarray() * 100
    )

    da_dct["Radiosonde 12"] = da_dct["Radiosonde 12"].rename({"index": "time"})
    da_dct["Radiosonde 06"] = da_dct["Radiosonde 06"].rename({"index": "time"})
    da_dct["Radiosonde 00"] = da_dct["Radiosonde 00"].rename({"index": "time"})
    da_dct["Radiosonde ++"] = da_dct["Radiosonde ++"].rename({"index": "time"})

    return da_dct


def da_mwr(da_dct):
    """
    Normalize by the typical time interval of *about* 1s. Slightly different
    for both instruments because HATPRO is slower in mirror movement. On daily
    average, measurements are every 1.16 s (LHUMPRO) and 1.22 s (HATPRO).
    """

    ds_mwr = read_scans(
        d0=Constants.DATE_START,
        d1=Constants.DATE_END,
        keep_mismatch=True,
        keep_atmos=True,
        daily_file=True,
        rain_flag=False,
    )

    ds_hatpro = xr.concat(
        [
            ds_mwr[scan].tb.sel(channel=Constants.CH_HATPRO[0])
            for scan in Constants.SCANS
        ],
        dim="time",
    )
    ds_lhumpro = xr.concat(
        [
            ds_mwr[scan].tb.sel(channel=Constants.CH_LHUMPRO[0])
            for scan in Constants.SCANS
        ],
        dim="time",
    )

    # drop where tb is nan
    ds_hatpro = ds_hatpro.sel(time=~np.isnan(ds_hatpro))
    ds_lhumpro = ds_lhumpro.sel(time=~np.isnan(ds_lhumpro))

    n_max = 24 * 3600 * 0.815  # ensures maximum is around 100 %
    da_dct["HATPRO"] = ds_hatpro.groupby(ds_hatpro.time.dt.date).count()
    da_dct["HATPRO"] = da_dct["HATPRO"] / n_max * 100
    da_dct["HATPRO"] = da_dct["HATPRO"].rename({"date": "time"})

    n_max = 24 * 3600 * 0.86  # ensures maximum is around 100 %
    da_dct["MiRAC-P"] = ds_lhumpro.groupby(ds_lhumpro.time.dt.date).count()
    da_dct["MiRAC-P"] = da_dct["MiRAC-P"] / n_max * 100
    da_dct["MiRAC-P"] = da_dct["MiRAC-P"].rename({"date": "time"})

    return da_dct


def da_grawac(da_dct):
    """
    Normalize by the daily mean time interval between samples without gaps.
    """

    ds_grawac = read_all_times(instrument="grawac")

    da_dt = ds_grawac.time.diff("time") / np.timedelta64(1, "s")
    da_dt = da_dt.where(da_dt < 10)  # remove large time gaps
    da_dt = da_dt.groupby(da_dt.time.dt.date).mean()
    n_max = 24 * 3600 / da_dt
    da_dct["GRaWAC"] = ds_grawac.groupby(ds_grawac.time.dt.date).count()
    da_dct["GRaWAC"] = da_dct["GRaWAC"] / n_max * 100
    da_dct["GRaWAC"] = da_dct["GRaWAC"].rename({"date": "time"})

    return da_dct


def da_mirac_a(da_dct):
    """
    Normalize by the daily mean time interval between samples without gaps.
    """

    ds_mirac_a = read_all_times(instrument="mirac_a")

    da_dt = ds_mirac_a.time.diff("time") / np.timedelta64(1, "s")
    da_dt = da_dt.where(da_dt < 10)  # remove large time gaps
    da_dt = da_dt.groupby(da_dt.time.dt.date).mean()
    n_max = 24 * 3600 / da_dt
    da_dct["MiRAC-A"] = ds_mirac_a.groupby(ds_mirac_a.time.dt.date).count()
    da_dct["MiRAC-A"] = da_dct["MiRAC-A"] / n_max * 100
    da_dct["MiRAC-A"] = da_dct["MiRAC-A"].rename({"date": "time"})

    return da_dct


def da_flir(da_dct):
    """
    Normalize by number of seconds per day.
    """

    ds_flir = read_flir_statistics_multiple(
        d0=Constants.DATE_START,
        d1=Constants.DATE_END,
        xr_kwargs={"drop_variables": "hist"},
    )

    n_max = 24 * 3600
    da_dct["FLIR"] = ds_flir.time.groupby(ds_flir.time.dt.date).count()
    da_dct["FLIR"] = da_dct["FLIR"] / n_max * 100
    da_dct["FLIR"] = da_dct["FLIR"].rename({"date": "time"})

    return da_dct


def da_gopro(da_dct):
    """
    Temporal resolution is 2 s.
    """

    times = get_all_times()

    df_gopro = pd.DataFrame(index=times)
    df_gopro["i"] = 1

    # data availability
    n_max = 24 * 3600 / 2
    da_dct["GoPRO"] = df_gopro.i.resample("1D").count().to_xarray()
    da_dct["GoPRO"] = da_dct["GoPRO"] / n_max * 100
    da_dct["GoPRO"] = da_dct["GoPRO"].rename({"index": "time"})

    return da_dct


def da_ultrasonic(da_dct):
    """
    DA relative to total number of 10 s per day.
    """

    df_usonic = read_usonic_multiple(
        d0=Constants.DATE_START, d1=Constants.DATE_END, product="AVERAGED"
    )

    n_max = 24 * 60 * 6
    da_dct["Ultrasonic"] = df_usonic.vel.resample("1D").count().to_xarray()
    da_dct["Ultrasonic"] = da_dct["Ultrasonic"] / n_max * 100

    return da_dct


def da_parsivel(da_dct):
    """
    DA relative to total number of minutes per day.
    """

    ds_par = read_parsivel_multiple(
        d0=Constants.DATE_START, d1=Constants.DATE_END
    )

    # data availability
    n_max = 24 * 60
    da_dct["Parsivel"] = ds_par.time.groupby(ds_par.time.dt.date).count()
    da_dct["Parsivel"] = da_dct["Parsivel"] / n_max * 100
    da_dct["Parsivel"] = da_dct["Parsivel"].rename({"date": "time"})

    return da_dct


def da_imupi(da_dct):
    """
    Data availability assumes 10 Hz measurement frequency.
    """

    df_imupi = read_imupi_multiple(
        d0=Constants.DATE_START, d1=Constants.DATE_END
    )

    # data availability
    n_max = 24 * 3600 * 10
    da_dct["RaspberryPi IMU"] = (
        df_imupi.gyr_x.resample("1D").count().to_xarray()
    )
    da_dct["RaspberryPi IMU"] = da_dct["RaspberryPi IMU"] / n_max * 100

    return da_dct


def da_hydrins(da_dct):
    """
    Data availability of 1 Hz data (not 20 Hz).
    """

    ds_hyd = read_hydrins_multiple(
        d0=Constants.DATE_START,
        d1=Constants.DATE_END,
        resolution=1,
    )

    # data availability
    n_max = 24 * 3600
    da_dct["Hydrins 20 Hz"] = ds_hyd.time.groupby(ds_hyd.time.dt.date).count()
    da_dct["Hydrins 20 Hz"] = da_dct["Hydrins 20 Hz"] / n_max * 100
    da_dct["Hydrins 20 Hz"] = da_dct["Hydrins 20 Hz"].rename({"date": "time"})

    return da_dct


def da_miniimu(da_dct):
    """
    Data availability assumes 1 Hz measurement frequency.
    """

    ds_imu = read_imu_multiple(d0=Constants.DATE_START, d1=Constants.DATE_END)

    # data availability
    n_max = 24 * 3600
    da_dct["Mini IMU"] = ds_imu.time.groupby(ds_imu.time.dt.date).count()
    da_dct["Mini IMU"] = da_dct["Mini IMU"] / n_max * 100
    da_dct["Mini IMU"] = da_dct["Mini IMU"].rename({"date": "time"})

    return da_dct


def da_mobotix(da_dct):
    """
    Data availability checks number of images per minute.
    """

    df_mob = mobotix_dates()

    # data availability
    n_max = 24 * 60
    da_dct["Mobotix"] = df_mob["file"].resample("1D").count().to_xarray()
    da_dct["Mobotix"] = da_dct["Mobotix"] / n_max * 100

    return da_dct


def plot_da(ds_da):
    """
    Plot data availability for all instruments
    """

    fig, axs = plt.subplot_mosaic(
        [
            ["MiRAC-A"],
            ["GRaWAC"],
            ["HATPRO"],
            ["MiRAC-P"],
            ["Parsivel"],
            ["Ultrasonic"],
            ["FLIR"],
            ["GoPRO"],
            ["Mobotix"],
            ["Mini IMU"],
            ["RaspberryPi IMU"],
            ["Hydrins 20 Hz"],
            ["Radiosonde 00"],
            ["Radiosonde 06"],
            ["Radiosonde 12"],
            ["Radiosonde ++"],
        ],
        figsize=(8, 5),
        layout="constrained",
        sharex=True,
        sharey=True,
    )

    bounds = np.linspace(0, 100, 21)
    cmap = cmc.lapaz_r
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    for ax in fig.axes:
        ax.set_yticks([])
        ax.set_yticklabels([])
        ax.set_ylim(0, 1)
        ax.set_facecolor(cmap(0))

        ax.set_ylabel(ax.get_label(), rotation=0, ha="right", va="center")

        # mark start and end of ice observations
        ax.scatter(
            Constants.DATE_START_ICE,
            0.8,
            marker="v",
            s=10,
            lw=0,
            zorder=10,
            color="coral",
        )
        ax.scatter(
            Constants.DATE_END_ICE,
            0.8,
            marker="v",
            s=10,
            lw=0,
            zorder=10,
            color="coral",
        )

        # mark ice station dates
        for date in Constants.DATE_ICE_STATION:
            ax.scatter(
                date,
                0.8,
                marker="p",
                s=10,
                lw=0,
                zorder=10,
                color="gray",
            )

        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.tick_params(axis="x", rotation=90)

    fig.axes[0].annotate(
        "Ice edge",
        xy=(Constants.DATE_START_ICE, 1),
        xycoords="data",
        ha="center",
        va="bottom",
        color="coral",
    )
    fig.axes[0].annotate(
        "Ice edge",
        xy=(Constants.DATE_END_ICE, 1),
        xycoords="data",
        ha="center",
        va="bottom",
        color="coral",
    )
    fig.axes[0].annotate(
        "Ice station",
        xy=(Constants.DATE_ICE_STATION[1], 1),
        xycoords="data",
        ha="center",
        va="bottom",
        color="gray",
    )

    for instrument in ds_da.data_vars:

        im = axs[instrument].pcolormesh(
            ds_da[instrument].time,
            np.array([0, 1]),
            np.array([ds_da[instrument].values.T, ds_da[instrument].values.T]),
            shading="nearest",
            cmap=cmap,
            norm=norm,
        )

    fig.axes[-1].set_xlabel("Date")

    fig.colorbar(
        im,
        ax=fig.axes,
        label="Data availability [%]",
        orientation="vertical",
        ticks=np.arange(0, 101, 10),
    )

    ax.set_xlim(
        Constants.DATE_START - pd.Timedelta(12, "h"),
        Constants.DATE_END + pd.Timedelta(12, "h"),
    )

    file_plot = os.path.join(
        os.environ["PATH_PLOTS"], "quicklooks", "data_availability.png"
    )
    plt.savefig(
        file_plot,
        dpi=300,
        bbox_inches="tight",
    )

    print(f"Created figure: {file_plot}")


if __name__ == "__main__":
    main()
