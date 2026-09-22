"""
Convert ultrasonic to 1 minute res csv files
"""

import os

import pandas as pd
from metpy.calc import wind_direction
from metpy.units import units

from vampire.constants import Constants
from vampire.io.readers.usonic import read_usonic_multiple


def main():

    dates = pd.date_range(Constants.DATE_START, Constants.DATE_END, freq="1D")
    names = ["x", "y", "z", "T", "vel", "vels"]

    for date in dates:
        print(f"Processing {date}")
        try:
            df = read_usonic_multiple(
                d0=date, d1=date + pd.Timedelta(23, "h"), product="instant"
            )
        except:
            continue
        df_1min = df[names].resample("1min").mean()

        # recalculate wind direction from u and v
        df_1min["dir"] = wind_direction(
            u=df_1min["x"].values * units("m/s"),
            v=df_1min["y"].values * units("m/s"),
        )

        df_1min.to_csv(
            os.path.join(
                os.environ["VAMPIRE_DATA"],
                "usonic/csv_1min",
                f"{Constants.CAMPAIGN_NAME.lower()}_vampire_ultrasonic_1min_{date.strftime('%Y%m%d')}.csv",
            )
        )


if __name__ == "__main__":
    main()
