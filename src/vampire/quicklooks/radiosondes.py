"""
Radiosonde quicklook.
"""

import glob
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

try:
    from metpy.calc import (
        dewpoint_from_relative_humidity,
        potential_temperature,
        precipitable_water,
        specific_humidity_from_dewpoint,
        mixing_ratio_from_relative_humidity,
        vapor_pressure,
    )
    from metpy.units import units

    plot_qv_theta = True
except ImportError:
    plot_qv_theta = False

from vampire.io.readers.radiosonde import get_radiosondes, read_radiosonde


def main(date):
    """
    Plot radiosondes for a specific date.
    """

    files, times = get_radiosondes(date=date)

    for file, time in zip(files, times):
        df = read_radiosonde(file=file, index_col="height")

        plot_radiosonde(df=df, time=time, save=True, show=False)

        if plot_qv_theta:
            try:
                df = compute_theta_td_qv(df)
                iwv = precipitable_water(
                    df.loc[slice(0, 18000), "pres"].values * units.Pa,
                    df.loc[slice(0, 18000), "td"].values * units.degC,
                )

                # melting layer
                df["t_0"] = potential_temperature(
                    df["pres"].values * units.Pa,
                    273.15 * units.kelvin,
                )

                # relative humidity over ice
                df["m"] = mixing_ratio_from_relative_humidity(
                    df["pres"].values * units.Pa,
                    df["temp"].values * units.kelvin,
                    df["relhum"].values * 100 * units.percent,
                )
                df["e"] = vapor_pressure(
                    df["pres"].values * units.Pa,
                    df["m"].values * units.dimensionless,
                )
                df["e_si"] = vapor_saturation_pressure_ice(t=df["temp"])
                df["relhum_ice"] = df["e"] / df["e_si"]
                df["relhum_ice"] = df["relhum_ice"].where(
                    (df["temp"] > 213) & (df["temp"] < 273.16)
                )
                plot_radisonde_qv_theta(
                    df=df, time=time, iwv=iwv, save=True, show=False
                )

            except Exception as e:
                print(f"Error during qv and theta calculation for {file}: {e}")
                continue


def vapor_saturation_pressure_ice(t):
    """
    Water vapor saturation pressure over ice based on Rogers and Yau (1989). 
    Valid between 213 and 273.16 K.

    Parameters
    ----------
    t : float
        Temperature in Kelvin.
    """

    a = 3.64e12  # Pa
    b = 6148  # K
    e_si = a * np.exp(-b / t)

    return e_si


def compute_theta_td_qv(df):
    """
    Compute potential temperature, dewpoint temperature, and specific humidity
    of radiosonde.
    """

    df["theta"] = potential_temperature(
        df["pres"].values * units.Pa,
        df["temp"].values * units.kelvin,
    )
    df["td"] = dewpoint_from_relative_humidity(
        df["temp"].values * units.kelvin,
        df["relhum"].values * 100 * units.percent,
    )
    df["qv"] = specific_humidity_from_dewpoint(
        df["pres"].values * units.Pa,
        df["td"].values * units.degC,
    ).to("g/kg")

    return df


def plot_radisonde_qv_theta(df, time, iwv, save=False, show=True):
    """
    Plot single radiosonde profile with potential temperature and specific
    humidity.
    """

    fig, (ax_t, ax_u) = plt.subplots(
        1,
        2,
        figsize=(6, 6),
        layout="constrained",
        width_ratios=[1, 0.3],
        sharey=True,
    )
    ax_rh = ax_t.twiny()
    ax_qv = ax_t.twiny()
    ax_qv.spines.top.set_position(("axes", 1.15))

    ax_d = ax_u.twiny()

    # thermodynamic variables
    ax_u.annotate(
        f"IWV: {round(iwv.magnitude, 1):.1f} kg m" + "$^{-2}$",
        xy=(1, 1.2),
        xycoords="axes fraction",
        ha="right",
        va="top",
    )

    h_min = 0
    h_max = 5000
    ax_t.plot(
        df.loc[slice(h_min, h_max), "theta"],
        df.loc[slice(h_min, h_max)].index * 1e-3,
        c="red",
    )
    ax_t.plot(
        df.loc[slice(h_min, h_max), "t_0"],  # 0 degree isotherme
        df.loc[slice(h_min, h_max)].index * 1e-3,
        c="k",
        linestyle=":",
        zorder=-1,
    )
    ax_qv.plot(
        df.loc[slice(h_min, h_max), "qv"],
        df.loc[slice(h_min, h_max)].index * 1e-3,
        c="olive",
        alpha=0.75,
    )
    ax_rh.plot(
        df.loc[slice(h_min, h_max), "relhum"] * 100,
        df.loc[slice(h_min, h_max)].index * 1e-3,
        c="blue",
        alpha=0.75,
    )
    ax_rh.plot(
        df.loc[slice(h_min, h_max), "relhum_ice"] * 100,
        df.loc[slice(h_min, h_max)].index * 1e-3,
        c="skyblue",
        alpha=0.75,
    )
    ax_rh.axvline(
        x=100,
        color="darkblue",
        linestyle=":",
        zorder=-1,
    )
    ax_u.plot(
        df.loc[slice(h_min, h_max), "wspeed"],
        df.loc[slice(h_min, h_max)].index * 1e-3,
        c="coral",
    )
    ax_d.scatter(
        df.loc[slice(h_min, h_max), "wdir"],
        df.loc[slice(h_min, h_max)].index * 1e-3,
        s=3,
        lw=0,
        c="gray",
        alpha=0.75,
    )

    ax_t.tick_params(axis="x", colors="red")
    ax_qv.tick_params(axis="x", colors="olive")
    ax_rh.tick_params(axis="x", colors="blue")
    ax_u.tick_params(axis="x", colors="coral")
    ax_d.tick_params(axis="x", colors="gray")

    ax_t.set_ylabel("Height [km]")
    ax_t.set_xlabel("Potential temperature [K]", color="red")
    ax_qv.set_xlabel("Specific humidity [g/kg]", color="olive")
    ax_rh.set_xlabel("Relative humidity [%]", color="blue")
    ax_u.set_xlabel("Wind speed [m/s]", color="coral")
    ax_d.set_xlabel("Wind direction [°]", color="gray")

    ax_d.set_xticks(np.arange(0, 361, 90))

    ax_t.set_ylim(h_min * 1e-3, h_max * 1e-3)
    ax_t.set_xlim(255, 315)
    ax_qv.set_xlim(left=0)
    ax_rh.set_xlim(0, 120)
    ax_u.set_xlim(left=0)
    ax_d.set_xlim(0, 360)

    ax_t.yaxis.set_minor_locator(mticker.MultipleLocator(0.1))
    ax_u.yaxis.set_minor_locator(mticker.MultipleLocator(0.1))

    if save:
        file = os.path.join(
            os.environ["PATH_PLOTS"],
            "quicklooks/radiosonde",
            f"radiosonde_quicklook_qv_theta_{pd.Timestamp(time).strftime('%Y%m%d_%H%M')}.png",
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


def plot_radiosonde(df, time, save=False, show=True):
    """
    Plot single radiosonde profile with temperature and relative humidity.
    """

    fig, ax_t = plt.subplots(1, 1, figsize=(6, 6), layout="constrained")
    ax_rh = ax_t.twiny()
    ax2_t = ax_t.inset_axes([0.5, 0.4, 0.45, 0.5])
    ax2_rh = ax2_t.twiny()

    ax_t.annotate(
        f"Launch time: {df['time'].iloc[0].strftime('%Y-%m-%d %H:%M')} UTC\n"
        f"Position: {df['lat'].iloc[0]}°N, {df['lon'].iloc[0]}°E\n"
        f"Max. altitude: {round(df.index.max() *1e-3, 3):.3f} km",
        xy=(0, 1.2),
        xycoords="axes fraction",
        ha="left",
        va="top",
    )

    ax_t.plot(df["temp"] - 273.15, df.index * 1e-3, c="red")
    ax2_t.plot(df["temp"] - 273.15, df.index * 1e-3, c="red")
    ax_rh.plot(df["relhum"] * 100, df.index * 1e-3, c="blue", alpha=0.75)
    ax2_rh.plot(df["relhum"] * 100, df.index * 1e-3, c="blue", alpha=0.75)

    ax_t.tick_params(axis="x", colors="red")
    ax_rh.tick_params(axis="x", colors="blue")
    ax2_t.tick_params(axis="x", colors="red")
    ax2_rh.tick_params(axis="x", colors="blue")

    ax_t.set_ylabel("Height [km]")
    ax2_t.set_ylabel("Height [km]")

    ax_t.set_xlabel("Temperature [°C]", color="red")
    ax2_t.set_xlabel("Temperature [°C]", color="red")
    ax_rh.set_xlabel("Relative humidity [%]", color="blue")
    ax2_rh.set_xlabel("Relative humidity [%]", color="blue")

    ax_t.set_ylim(0, 38)
    ax2_t.set_ylim(0, 10)
    ax_t.set_xlim(-70, 20)
    ax2_t.set_xlim(-70, 20)
    ax_rh.set_xlim(0, 100)
    ax2_rh.set_xlim(0, 100)

    ax_t.yaxis.set_minor_locator(mticker.MultipleLocator(1))
    ax2_t.yaxis.set_minor_locator(mticker.MultipleLocator(1))

    if save:
        file = os.path.join(
            os.environ["PATH_PLOTS"],
            "quicklooks/radiosonde",
            f"radiosonde_quicklook_{pd.Timestamp(time).strftime('%Y%m%d_%H%M')}.png",
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


def plot_IWV_map(save=False, show=True):
    """not ready yet"""
    files = sorted(glob.glob(path_testdata["radiosondes"] + "*.txt"))
    sonde_dict = import_radiosondes_PS144_txt(
        files, add_loc_info=True, add_info=True
    )
    ### IWV time series
    dates = np.array([])
    IWV = []
    lat = []
    lon = []
    for i in sonde_dict.keys():
        dates = np.append(
            dates, pd.to_datetime(sonde_dict[i]["launch_time_npdt"])
        )
        IWV = np.append(IWV, sonde_dict[i]["IWV"])
    IWV_VAMPIRE_radiosondes = pd.DataFrame({"date": dates, "IWV": IWV})
    if save:
        file = os.path.join(
            os.environ["PATH_PLOTS"],
            "quicklooks/radiosondes",
            f"radiosonde_quicklook_IWV_map_VAMPIRE.png",
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


if __name__ == "__main__":
    main(date=sys.argv[1])
