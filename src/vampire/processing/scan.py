"""
Microwave radiometer scan definitions. This script helps to compare the 
defined scan times with the actual scan times. This can help to improve 
synchronization between MiRAC-P and HATPRO during the campaign.

Angle definitions: 0° is nadir, 180° is zenith (as for MiRAC-P during VAMPIRE)

Note: Experimental scan definitions, please check the documentation for the 
angles and times used during the campaign.
"""

import numpy as np
import xarray as xr
from glob import glob
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
import matplotlib.dates as mdates
import vampire

# duration of a calibration with 10 s integration time based on a test scan
T_10S_CALIBRATION = np.timedelta64(20, "s")

# time for writing a file
T_FILE_WRITING = np.timedelta64(4, "s")

BATCH = [
    "emis-scan",  # starts at 00 or 30 min
    "zenith",
    "emis",
    "zenith",
    "emis",
    "zenith",
    "bl-scan",
    # "zenith",  # this one only until 00 or 30 min
]

T_MIRROR = {
    "emis-scan": np.timedelta64(1, "s"),
    "zenith": np.timedelta64(1, "s"),
    "emis": np.timedelta64(2, "s"),
    "bl-scan": np.timedelta64(1, "s"),
}


def define_scans_mirac():
    """
    Definition of MiRAC-P scans. HATPRO scans are calculated from MiRAC-P 
    scans afterwards. Update this to the latest scan settings described in the 
    documentation.
    """

    scans_mirac = {
        "emis-scan": {
            "type": "general_scan",
            "integration_time": np.timedelta64(1, "s"),
            "start_scan": "scan1",
            "stop_scan": "scan2",
            "scans": {
                "scan1": {
                    "start": 25,
                    "stop": 65,
                    "increment": 10,
                    "samples": 15,
                },
                "scan2": {
                    "start": 115,
                    "stop": 155,
                    "increment": 10,
                    "samples": 15,
                },
            },
            "calibration": np.timedelta64(0, "s"),
        },
        "emis": {
            "type": "general_scan",
            "integration_time": np.timedelta64(1, "s"),
            "start_scan": "scan1",
            "stop_scan": "scan5",
            "scans": {
                "scan1": {
                    "start": 127,
                    "stop": 127,
                    "increment": 0,
                    "samples": 15,
                },
                "scan2": {
                    "start": 53,
                    "stop": 53,
                    "increment": 0,
                    "samples": 70,
                },
                "scan3": {
                    "start": 127,
                    "stop": 127,
                    "increment": 0,
                    "samples": 15,
                },
                "scan4": {
                    "start": 53,
                    "stop": 53,
                    "increment": 0,
                    "samples": 70,
                },
                "scan5": {
                    "start": 127,
                    "stop": 127,
                    "increment": 0,
                    "samples": 15,
                },
            },
            "calibration": np.timedelta64(0, "s"),
        },
        "zenith": {
            "type": "constant_angles",
            "integration_time": np.timedelta64(1, "s"),
            "angle": 180,
            "duration": np.timedelta64(360, "s"),
            "calibration": T_10S_CALIBRATION,
        },
        "bl-scan": {
            "type": "general_scan",
            "integration_time": np.timedelta64(10, "s"),
            "start_scan": "scan1",
            "stop_scan": "scan10",
            "scans": {
                "scan1": {
                    "start": 180,
                    "stop": 180,
                    "increment": 0,
                    "samples": 1,
                },
                "scan2": {
                    "start": 120,
                    "stop": 120,
                    "increment": 0,
                    "samples": 1,
                },
                "scan3": {
                    "start": 109.2,
                    "stop": 109.2,
                    "increment": 0,
                    "samples": 1,
                },
                "scan4": {
                    "start": 104.4,
                    "stop": 104.4,
                    "increment": 0,
                    "samples": 1,
                },
                "scan5": {
                    "start": 101.4,
                    "stop": 101.4,
                    "increment": 0,
                    "samples": 1,
                },
                "scan6": {
                    "start": 98.4,
                    "stop": 98.4,
                    "increment": 0,
                    "samples": 1,
                },
                "scan7": {
                    "start": 96.6,
                    "stop": 96.6,
                    "increment": 0,
                    "samples": 1,
                },
                "scan8": {
                    "start": 95.4,
                    "stop": 95.4,
                    "increment": 0,
                    "samples": 1,
                },
                "scan9": {
                    "start": 94.8,
                    "stop": 94.8,
                    "increment": 0,
                    "samples": 1,
                },
                "scan10": {
                    "start": 94.2,
                    "stop": 94.2,
                    "increment": 0,
                    "samples": 1,
                },
            },
            "calibration": np.timedelta64(0, "s"),
        },
    }

    return scans_mirac


def mirac2hatpro(scans):
    """
    Returns dict defined for MiRAC-P but 180 degrees minus the given angle.
    Note that this overwrites the input.
    """

    for scan_name in scans:
        if scans[scan_name]["type"] == "general_scan":
            for scan in scans[scan_name]["scans"]:
                scans[scan_name]["scans"][scan]["start"] = convert_lhumpro2hatpro(
                    scans[scan_name]["scans"][scan]["start"]
                )
                scans[scan_name]["scans"][scan]["stop"] = convert_lhumpro2hatpro(
                    scans[scan_name]["scans"][scan]["stop"]
                )
                scans[scan_name]["scans"][scan]["increment"] *= -1

        elif scans[scan_name]["type"] == "constant_angles":
            scans[scan_name]["angle"] = convert_lhumpro2hatpro(
                scans[scan_name]["angle"]
            )

    return scans


def convert_lhumpro2hatpro(x):
    """convert_lhumpro2hatpro MiRAC-P scan angle to HATPRO angle."""
    return 180 - x


def define_scans():
    """
    Creates dictionary of scans from MiRAC-P and HATPRO.
    """

    scans_mirac = define_scans_mirac()
    scans_hatpro = mirac2hatpro(define_scans_mirac())

    return scans_mirac, scans_hatpro


def main():
    """
    Simulate duration of batch
    """

    scans_mirac, scans_hatpro = define_scans()

    durations = compute_duration()

    test_scan(durations)


def test_scan(durations):
    """
    Check times of test scans and compare with the settings.
    """

    files1 = sorted(
        glob(
            os.path.join(
                os.environ["VAMPIRE_DATA"], "hatpro/2024/06/19/*BRT.NC"
            )
        )
    )
    files2 = sorted(
        glob(
            os.path.join(
                os.environ["VAMPIRE_DATA"], "hatpro/2024/06/20/*BRT.NC"
            )
        )
    )

    # ds1 = xr.open_mfdataset(files1, combine="by_coords")
    # ds1 = ds1.sel(time=np.sort(ds1.time))
    # ds1 = ds1.load()

    ds2 = xr.open_mfdataset(files2, combine="by_coords")
    ds2 = ds2.sel(time=np.sort(ds2.time))
    ds2 = ds2.load()

    # amount of samples during 30 minutes
    n_samples = len(
        ds2.time.sel(
            time=slice(
                np.min(ds2.time),
                np.min(ds2.time.values) + np.timedelta64(30, "m"),
            )
        )
    )
    n_max_samples = 60 * 30 - 24 * 3
    f_samples = n_samples / n_max_samples * 100

    fig, ax = plt.subplots(1, 1, figsize=(6, 4))

    ax.scatter(
        np.datetime64("2024-01-01") + (ds2.time - np.min(ds2.time)),
        ds2.ElAng,
        c="red",
        s=10,
        lw=0,
    )

    # ax.scatter(
    #    np.datetime64("2024-01-01") + (ds1.time - np.min(ds1.time)),
    #    ds1.ElAng,
    #    c="blue",
    #    label="test 1",
    #    s=10,
    # )

    # add vertical line and label for the scans with at expected time
    for i in range(len(BATCH)):
        ax.axvline(
            np.datetime64("2024-01-01") + np.sum(durations[:i]),
            color="black",
            linestyle="--",
        )
        ax.text(
            np.datetime64("2024-01-01") + np.sum(durations[:i]),
            175,
            BATCH[i],
            rotation=90,
            verticalalignment="top",
        )

    # ax.legend()

    ax.set_ylim(0, 180)
    ax.axhline(90, color="black", linestyle=":")

    ax.set_yticks([0, 45, 90, 135, 180])

    ax.set_xlabel("Duration [MM:SS]")
    ax.set_ylabel("Elevation angle [°]")

    # mm format
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.set_xlim(
        np.datetime64("2024-01-01"),
        np.datetime64("2024-01-01") + np.timedelta64(30, "m"),
    )

    # annotate sample fraction
    ax.annotate(
        f"Samples: {n_samples} ({f_samples:.1f}%)",
        xy=(1, 1),
        xycoords="axes fraction",
        ha="right",
        va="bottom",
    )

    plt.savefig(
        os.path.join(os.environ["PATH_PLOTS"], "test_scan.png"), dpi=300
    )


def compute_duration():
    """
    Compute the duration of the batch including duration of mirror adjustment
    and calibrations.
    """

    durations = np.array([], dtype="timedelta64[s]")
    for scan in BATCH:
        duration = np.timedelta64(0, "s")

        # calibration time
        # duration += SCANS[scan]["calibration"]

        if SCANS[scan]["type"] == "general_scan":

            # scan duration
            for scan_name in SCANS[scan]["scans"]:
                if SCANS[scan]["scans"][scan_name]["increment"] > 0:
                    n_angles = (
                        int(
                            abs(
                                (
                                    SCANS[scan]["scans"][scan_name]["start"]
                                    - SCANS[scan]["scans"][scan_name]["stop"]
                                )
                                / SCANS[scan]["scans"][scan_name]["increment"]
                            )
                        )
                        + 1
                    )
                else:
                    n_angles = 1

                # measurement time
                duration += (
                    SCANS[scan]["scans"][scan_name]["samples"]
                    * SCANS[scan]["integration_time"]
                    * n_angles
                )

                # mirror adjustment time
                duration += T_MIRROR[scan] * n_angles

        else:

            # measurement time
            duration += SCANS[scan]["duration"]

            # mirror adjustment time
            duration += T_MIRROR[scan]

        # file writing time
        duration += np.timedelta64(T_FILE_WRITING, "s")

        durations = np.append(durations, duration)

    # duration per scan pattern
    for i in range(len(BATCH)):
        print(f"Duration of {BATCH[i]}: {durations[i]}")

    # print total duration of scan pattern
    total_duration = np.sum(durations)
    minutes = total_duration.astype("timedelta64[m]")
    seconds = total_duration.astype("timedelta64[s]") - minutes.astype(
        "timedelta64[s]"
    )
    print(f"Duration: {minutes} and {seconds}")

    return durations


if __name__ == "__main__":
    main()
