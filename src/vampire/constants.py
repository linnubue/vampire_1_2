"""
Stores VAMPIRE constants shared among all scripts.

Scan colors are from cmcrameri
import cmcrameri.cm as cmc
import matplotlib
import numpy as np
for i in range(4):
    print(matplotlib.colors.to_hex(cmc.batlow(np.linspace(0, 0.9, 4))[i]))
"""

from dataclasses import dataclass
from typing import List, Dict

import pandas as pd


@dataclass(frozen=True)
class Constants:
    """
    Constants of ArcWatchII (PS144, VAMPIRE) campaign.
    
    Parameters
    ----------
    DATE_START : pd.Timestamp
        Start of VAMPIRE campaign.
    DATE_END : pd.Timestamp
        End of VAMPIRE campaign.
    DATE_START_ICE : pd.Timestamp
        Date from when ship was within sea ice
    DATE_ICE_STATION : List[pd.Timestamp]
        List of ice station dates.
    SCANS : List[str]
        List of HATPRO and LHUMPRO scans.
    """

    # campaign dates
    CAMPAIGN_NAME: str = "PS144"
    DATE_START: pd.Timestamp = pd.Timestamp("2024-08-09")
    DATE_END: pd.Timestamp = pd.Timestamp("2024-10-13")
    DATE_START_ICE: pd.Timestamp = pd.Timestamp("2024-08-14")
    DATE_END_ICE: pd.Timestamp = pd.Timestamp("2024-10-04")

    # ice station info
    STATION_ID: List[str] = (
        "7-1",
        "23-1",
        "42-1",
        "50-1",
        "67-1",
        "80-1",
        "85-1",
        "109-1",
        "134-1",
    )
    # note these dates are when we measure in the footprint. Start or end
    # of ice station might be on previous or next day.
    DATE_ICE_STATION: List[pd.Timestamp] = (
        pd.Timestamp("2024-08-16"),
        pd.Timestamp("2024-08-29"),
        pd.Timestamp("2024-09-02"),
        pd.Timestamp("2024-09-05"),
        pd.Timestamp("2024-09-08"),
        pd.Timestamp("2024-09-10"),
        pd.Timestamp("2024-09-13"),
        pd.Timestamp("2024-09-18"),
        pd.Timestamp("2024-09-23"),
        pd.Timestamp("2024-09-25"),
    )

    # times 10 minutes before measurement in IR footprint. multiple times per
    # ice station possible
    TIME_ICE_STATION = [
        pd.Timestamp("2024-08-16 15:45"),
        pd.Timestamp("2024-08-29 17:15"),
        pd.Timestamp("2024-09-02 21:05"),
        pd.Timestamp("2024-09-05 06:50"),
        pd.Timestamp("2024-09-08 08:30"),
        pd.Timestamp("2024-09-10 21:40"),
        pd.Timestamp("2024-09-13 08:15"),
        pd.Timestamp("2024-09-18 21:50"),
        pd.Timestamp("2024-09-19 13:40"),
        pd.Timestamp("2024-09-23 06:45"),
        pd.Timestamp("2024-09-26 00:00"),
    ]

    TIME_ICE_STATION_START: List[pd.Timestamp] = (
        pd.Timestamp("2024-08-16 11:30"),
        pd.Timestamp("2024-08-29 13:05"),
        pd.Timestamp("2024-09-02 20:50"),
        pd.Timestamp("2024-09-04 20:45"),
        pd.Timestamp("2024-09-08 06:20"),
        pd.Timestamp("2024-09-10 20:15"),
        pd.Timestamp("2024-09-12 19:25"),
        pd.Timestamp("2024-09-13 06:40"),
        pd.Timestamp("2024-09-18 20:20"),
        pd.Timestamp("2024-09-23 06:25"),
        pd.Timestamp("2024-09-25 05:30"),
        pd.Timestamp("2024-09-25 21:40"),
    )

    TIME_ICE_STATION_END: List[pd.Timestamp] = (
        pd.Timestamp("2024-08-17 04:08"),
        pd.Timestamp("2024-08-30 11:34"),
        pd.Timestamp("2024-09-03 01:00"),
        pd.Timestamp("2024-09-05 19:15"),
        pd.Timestamp("2024-09-09 00:25"),
        pd.Timestamp("2024-09-11 07:45"),
        pd.Timestamp("2024-09-13 02:28"),
        pd.Timestamp("2024-09-13 23:45"),
        pd.Timestamp("2024-09-19 22:55"),
        pd.Timestamp("2024-09-23 14:52"),
        pd.Timestamp("2024-09-25 09:06"),
        pd.Timestamp("2024-09-26 06:20"),
    )

    # mwr scan modes
    SCANS: List[str] = ("ZENITH", "BL-SCAN", "EMIS", "EMIS-SCAN")

    # angles
    ZENITH: List[int] = (180,)
    BL_SCAN: List[int] = (
        94.2,
        94.8,
        95.4,
        96.6,
        98.4,
        101.4,
        104.4,
        109.2,
        120.0,
        180,
    )
    EMIS: List[int] = (53, 127)
    EMIS_SCAN: List[int] = (35, 45, 55, 65, 115, 125, 135, 145)

    # angles surface
    EMIS_SURF: List[int] = (53,)
    EMIS_SCAN_SURF: List[int] = (35, 45, 55, 65)
    EMIS_SCAN_SURF2: List[int] = (25, 35, 45, 55, 65)

    # angles sky
    ZENITH_SKY: List[int] = (180,)
    BL_SCAN_SKY: List[int] = (
        94.2,
        94.8,
        95.4,
        96.6,
        98.4,
        101.4,
        104.4,
        109.2,
        120.0,
        180,
    )
    EMIS_SKY: List[int] = (127,)
    EMIS_SCAN_SKY: List[int] = (115, 125, 135, 145)

    # colors (same order as SCANS variable)
    SCAN_COLORS: List[str] = ("#011959", "#30685c", "#b38e2f", "#fdb9c2")

    # radiosondes
    # careful: selection is based on ceilometer cloud mask, not radar
    CLEARSKY_SONDES_OLD: List[pd.Timestamp] = (
        #pd.Timestamp("2024-08-10 12:00"),  # mostly clear-sky in ceilometer
        pd.Timestamp("2024-08-25 12:00"),  # clear-sky in ceilometer
        pd.Timestamp("2024-09-08 12:00"),  # clear-sky in ceilometer
        pd.Timestamp("2024-09-09 00:00"),  # clear-sky in ceilometer
        pd.Timestamp("2024-09-09 06:00"),  # clear-sky in ceilometer
        pd.Timestamp("2024-09-09 12:00"),  # clear-sky in ceilometer
        pd.Timestamp("2024-09-14 00:00"),  # clear-sky in ceilometer
        pd.Timestamp("2024-09-14 06:00"),  # clear-sky in ceilometer
        pd.Timestamp("2024-09-19 00:00"),  # mostly clear-sky in ceilometer
        pd.Timestamp("2024-09-21 12:00"),  # clear-sky in ceilometer
        pd.Timestamp("2024-09-22 06:00"),  # clear-sky in ceilometer
        pd.Timestamp("2024-09-29 00:00"),  # mostly clear-sky in ceilometer
        pd.Timestamp("2024-09-29 06:00"),  # mostly clear-sky in ceilometer
        pd.Timestamp("2024-10-01 12:00"),  # clear-sky in ceilometer
    )
    CLEARSKY_SONDES: List[pd.Timestamp] = (
        # pd.Timestamp("2024-08-20 10:54:07"), # shallow fog
        # pd.Timestamp("2024-08-25 10:50:22"), # when using TBs at 1100-1105 UTC
        pd.Timestamp("2024-09-08 10:53:56"), # okay
        # pd.Timestamp("2024-09-08 22:50:08"), # cirrus
        # pd.Timestamp("2024-09-09 04:35:16"), # when using TBs at 05:00 UTC, otherwise, evtl cirrus
        pd.Timestamp("2024-09-09 10:54:11"), # okay
        pd.Timestamp("2024-09-12 16:52:44"), # okay
        pd.Timestamp("2024-09-12 22:50:52"), # okay
        pd.Timestamp("2024-09-13 22:52:28"), # okay, evtl some cirrus off zenith
        pd.Timestamp("2024-09-14 04:37:15"), # okay
        pd.Timestamp("2024-09-14 10:53:29"), # okay, cirrus off zenith
        # pd.Timestamp("2024-09-18 22:49:27"), # shallow Sc
        # pd.Timestamp("2024-09-19 04:34:49"), # when using TBs at 0450-0500 UTC
        # pd.Timestamp("2024-09-21 10:56:30"), # shallow fog
        pd.Timestamp("2024-09-21 22:49:45"), # okay
        # pd.Timestamp("2024-09-22 04:36:59"), # shallow fog and Ci off zenith
        # pd.Timestamp("2024-09-25 22:57:55"), # shallow fog
        pd.Timestamp("2024-09-28 22:52:58"), # okay
        pd.Timestamp("2024-09-29 04:36:38"), # okay
        # pd.Timestamp("2024-09-29 10:55:49"), # evtl shallow fog
        # pd.Timestamp("2024-09-30 10:56:38"), # shallow fog
        pd.Timestamp("2024-10-01 10:55:08"), # okay
        pd.Timestamp("2024-10-07 04:33:56"), # okay, clouds only at horizon
    )
    PS144_BAD_SONDES: List[pd.Timestamp] = (pd.Timestamp("2024-08-23 00:00"),)

    # radiometer
    CH_HATPRO: List[int] = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
    CH_LHUMPRO: List[int] = (15, 16, 17, 18, 19, 20, 21, 22)
    
    CALIBRATION_TIME_HATPRO: List[pd.Timestamp] = (
        pd.Timestamp("2024-08-09 12:00:00"),
        pd.Timestamp("2024-09-11 14:00:00"),
        
    )
    CALIBRATION_TIME_LHUMPRO: List[pd.Timestamp] = (
        pd.Timestamp("2024-08-08 12:00:00"),
        pd.Timestamp("2024-09-11 13:00:00"),
    )
    
    T2M_HATPRO_LHUMPRO: List[list] = (
        [pd.Timestamp("2024-08-09 07:25:17"), pd.Timestamp("2024-08-11 07:08:54"), 'hatpro'],
        [pd.Timestamp("2024-08-11 07:08:54"), pd.Timestamp("2024-08-14 00:00:00 "), 'mirac-p'],
        [pd.Timestamp("2024-08-14 00:00:00"), pd.Timestamp("2024-08-16 00:00:00"), 'hatpro'],
        [pd.Timestamp("2024-08-16 00:00:00"), pd.Timestamp("2024-08-26 00:00:00 "), 'mirac-p'],
        [pd.Timestamp("2024-08-26 00:00:00"), pd.Timestamp("2024-09-09 00:00:00"), 'hatpro'],
        [pd.Timestamp("2024-09-09 00:00:00"), pd.Timestamp("2024-09-11 00:00:00"), 'mirac-p'],
        [pd.Timestamp("2024-09-11 00:00:00"), pd.Timestamp("2024-10-08 08:24:41"), 'hatpro'],
    )


@dataclass(frozen=True)
class Constants_PS149:
    """
    Constants of CONTRASTS (PS149, VAMPIRE2) campaign.
    """

    # campaign dates
    CAMPAIGN_NAME: str = "PS149"
    DATE_START: pd.Timestamp = pd.Timestamp("2025-07-02")
    DATE_END: pd.Timestamp = pd.Timestamp("2025-09-01")
    DATE_START_ICE: pd.Timestamp = pd.Timestamp("2025-07-06")
    DATE_END_ICE: pd.Timestamp = pd.Timestamp("2025-08-31")     ########### to be updated

    # ice station info
    # ICE STATION TIMES source: DSHIP Logs of Events
    ICE_STATION_TIMES = {
        '13-1': [pd.Timestamp("2025-07-09 06:32:22"), pd.Timestamp("2025-07-12 18:25:00")],
        '16-1': [pd.Timestamp("2025-07-14 12:36:36"), pd.Timestamp("2025-07-17 17:58:01")],
        '18-1': [pd.Timestamp("2025-07-19 17:45:41"), pd.Timestamp("2025-07-22 18:00:00")],
        '21-1': [pd.Timestamp("2025-07-25 16:30:00"), pd.Timestamp("2025-07-28 16:40:09")],
        '25-1': [pd.Timestamp("2025-07-30 07:00:05"), pd.Timestamp("2025-08-01 17:31:26")],
        '30-1': [pd.Timestamp("2025-08-04 07:28:09"), pd.Timestamp("2025-08-06 19:30:46")],
        '32-1': [pd.Timestamp("2025-08-09 08:00:12"), pd.Timestamp("2025-08-10 22:07:56")],
        '36-1': [pd.Timestamp("2025-08-12 06:52:05"), pd.Timestamp("2025-08-14 17:22:33")],
        '41-1': [pd.Timestamp("2025-08-16 19:55:00"), pd.Timestamp("2025-08-18 22:30:07")],
        '46-1': [pd.Timestamp("2025-08-23 06:51:59"), pd.Timestamp("2025-08-24 18:32:02")],
        '47-1': [pd.Timestamp("2025-08-26 07:10:51"), pd.Timestamp("2025-08-27 20:15:46")],
    }
    
    ICE_STATION_LABELS = {
        '13-1': "1a",
        '16-1': "2a",
        '18-1': "3a",
        '21-1': "1b",
        '25-1': "2b",
        '30-1': "3b",
        '32-1': "1c",
        '36-1': "2c",
        '41-1': "3c",
        '46-1': "2d",
        '47-1': '3d',
    }
    
    STATION_ID: List[str] = (
        "13-1", "13-1", "13-1",
        "16-1", "16-1", "16-1",
        "18-1", "18-1", "18-1",
        "21-1", "21-1", "21-1",
        "25-1", "25-1", "25-1",
        "30-1", "30-1", "30-1",
        "32-1", "32-1",
        "36-1", "36-1", "36-1", 
        "41-1", "41-1", "41-1",
        "46-1", "46-1",
        "47-1", "47-1",
    )
    
    SAMPLING_LABEL: List[str] = (
        "1a", "1a", "1a",
        "2a", "2a", "2a",
        "3a", "3a", "3a",
        "1b", "1b", "1b",
        "2b", "2b", "2b",
        "3b", "3b", "3b",
        "1c", "1c",
        "2c", "2c", "2c",
        "3c", "3c", "3c",
        "2d", "2d",
        "3d", "3d",
    )
    
    # note these dates are when we measure in the footprint. Start or end
    # of ice station might be on previous or next day.
    DATE_ICE_SAMPLING: List[pd.Timestamp] = (
        pd.Timestamp("2025-07-09"), pd.Timestamp("2025-07-10"), pd.Timestamp("2025-07-11"),
        pd.Timestamp("2025-07-15"), pd.Timestamp("2025-07-16"), pd.Timestamp("2025-07-17"),
        pd.Timestamp("2025-07-20"), pd.Timestamp("2025-07-21"), pd.Timestamp("2025-07-22"),
        pd.Timestamp("2025-07-26"), pd.Timestamp("2025-07-27"), pd.Timestamp("2025-07-28"),
        pd.Timestamp("2025-07-30"), pd.Timestamp("2025-07-31"), pd.Timestamp("2025-08-01"),
        pd.Timestamp("2025-08-04"), pd.Timestamp("2025-08-05"), pd.Timestamp("2025-08-06"),
        pd.Timestamp("2025-08-09"), pd.Timestamp("2025-08-10"),
        pd.Timestamp("2025-08-12"), pd.Timestamp("2025-08-13"), pd.Timestamp("2025-08-14"),
        pd.Timestamp("2025-08-16"), pd.Timestamp("2025-08-17"), pd.Timestamp("2025-08-18"),
        pd.Timestamp("2025-08-23"), pd.Timestamp("2025-08-24"), 
        pd.Timestamp("2025-08-26"), pd.Timestamp("2025-08-27"),
    )

    # times 10 minutes before sampling on the ice. Here, 10 minutes before start 
    # time in field notes "Station Overview".
    TIME_ICE_SAMPLING: List[pd.Timestamp] = (
        pd.Timestamp("2025-07-09 17:38"), pd.Timestamp("2025-07-10 12:40"), pd.Timestamp("2025-07-11 09:08"),
        pd.Timestamp("2025-07-15 13:15"), pd.Timestamp("2025-07-16 12:40"), pd.Timestamp("2025-07-17 08:52"),
        pd.Timestamp("2025-07-20 12:45"), pd.Timestamp("2025-07-21 12:37"), pd.Timestamp("2025-07-22 12:30"),
        pd.Timestamp("2025-07-26 12:32"), pd.Timestamp("2025-07-27 12:32"), pd.Timestamp("2025-07-28 09:05"),
        pd.Timestamp("2025-07-30 12:53"), pd.Timestamp("2025-07-31 12:53"), pd.Timestamp("2025-08-01 12:42"),
        pd.Timestamp("2025-08-04 12:42"), pd.Timestamp("2025-08-05 12:33"), pd.Timestamp("2025-08-06 10:11"),
        pd.Timestamp("2025-08-09 15:42"), pd.Timestamp("2025-08-10 12:32"),
        pd.Timestamp("2025-08-12 13:27"), pd.Timestamp("2025-08-13 12:31"), pd.Timestamp("2025-08-14 12:30"),
        pd.Timestamp("2025-08-16 20:35"), pd.Timestamp("2025-08-17 12:32"), pd.Timestamp("2025-08-18 14:21"),
        pd.Timestamp("2025-08-23 13:30"), pd.Timestamp("2025-08-24 12:31"),
        pd.Timestamp("2025-08-26 12:32"), pd.Timestamp("2025-08-27 12:32"),
    )
    
    SAMPLING_IN_MWR_FOOTPRINT: List[bool] = (
        True, True, True,
        True, True, True,
        True, True, True,
        True, True, True,
        True, True, True,
        False, False, False,
        True, True,
        False, False, False,
        True, True, True,
        True, False,
        True, True,
    )

    # mwr scan modes
    SCANS: List[str] = ("ZENITH", "BL-SCAN", "EMIS", "EMIS-SCAN")

    # angles
    ZENITH: List[int] = (180,)
    BL_SCAN: List[int] = (
        94.2,
        94.8,
        95.4,
        96.6,
        98.4,
        101.4,
        104.4,
        109.2,
        120.0,
        180,
    )
    EMIS: List[int] = (53, 127)
    EMIS_SCAN: List[int] = (35, 45, 55, 65, 115, 125, 135, 145)

    # angles surface
    EMIS_SURF: List[int] = (53,)
    EMIS_SCAN_SURF: List[int] = (35, 45, 55, 65)
    EMIS_SCAN_SURF2: List[int] = (25, 35, 45, 55, 65)

    # angles sky
    ZENITH_SKY: List[int] = (180,)
    BL_SCAN_SKY: List[int] = (
        94.2,
        94.8,
        95.4,
        96.6,
        98.4,
        101.4,
        104.4,
        109.2,
        120.0,
        180,
    )
    EMIS_SKY: List[int] = (127,)
    EMIS_SCAN_SKY: List[int] = (115, 125, 135, 145)

    # colors (same order as SCANS variable)
    SCAN_COLORS: List[str] = ("#011959", "#30685c", "#b38e2f", "#fdb9c2")

    # radiosondes
    # careful: selection is based on ceilometer cloud mask, not radar
    CLEARSKY_SONDES: List[pd.Timestamp] = (
        # pd.Timestamp("2025-07-08 10:51:54"), # cirrus
        pd.Timestamp("2025-07-14 06:00:26"), # okay
        # pd.Timestamp("2025-07-14 11:02:40"), # cirrus
        pd.Timestamp("2025-07-21 05:53:33"), # okay
        pd.Timestamp("2025-07-21 10:59:49"), # okay
        pd.Timestamp("2025-07-21 22:58:36"), # okay
        # pd.Timestamp("2025-07-22 08:50:28"), # thick cirrus
        # pd.Timestamp("2025-07-22 10:59:21"), # cirrus;
        # pd.Timestamp("2025-07-22 22:57:08"), # cirrus 
        pd.Timestamp("2025-07-23 06:45:56"), # okay or evtl thin cirrus off zenith
        # pd.Timestamp("2025-07-23 11:02:15"), # cirrus
        pd.Timestamp("2025-07-30 22:59:34"), # okay when using TBs in range 22:40 - 23:04
        pd.Timestamp("2025-08-06 22:56:44"), # thin cirrus (evtl not in MWR fov)
        # pd.Timestamp("2025-08-09 07:02:23"), # shallow fog;
        pd.Timestamp("2025-08-09 22:59:41"), # okay
        pd.Timestamp("2025-08-10 06:57:16"), # cirrus but evtl okay when using e.g. between 06:28 and 06:39
        pd.Timestamp("2025-08-18 11:00:42"), # evtl okay else cirrus
        pd.Timestamp("2025-08-18 22:58:09"), # okay
        pd.Timestamp("2025-08-20 22:55:54"), # okay 
        pd.Timestamp("2025-08-21 06:00:31"), # okay
        pd.Timestamp("2025-08-21 11:01:28"), # okay 
        pd.Timestamp("2025-08-22 06:25:49"), # okay 
        pd.Timestamp("2025-08-22 10:56:16"), # thin cirrus
        # pd.Timestamp("2025-08-27 10:55:03"), # cirrus
        pd.Timestamp("2025-08-27 23:02:40"), # okay
        pd.Timestamp("2025-08-28 06:47:34"), # okay 
    )
    BAD_SONDES: List[pd.Timestamp] = ()

    # radiometer
    CH_HATPRO: List[int] = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
    CH_LHUMPRO: List[int] = (15, 16, 17, 18, 19, 20, 21, 22)
    
    
    # Calibration times:
    CALIBRATION_TIME_HATPRO: List[pd.Timestamp] = (
        pd.Timestamp("2025-07-02 14:00:00"),
        pd.Timestamp("2025-08-06 16:28:21"),
        
    )
    CALIBRATION_TIME_LHUMPRO: List[pd.Timestamp] = (
        pd.Timestamp("2025-07-02 14:30:00"),
        pd.Timestamp("2025-08-06 17:05:04"),
    )
    
    T2M_HATPRO_LHUMPRO: List[list] = (
        [pd.Timestamp("2025-07-04 06:55:33"), pd.Timestamp("2025-07-04 18:01:58"), 'mirac-p'],
        [pd.Timestamp("2025-07-04 18:01:58"), pd.Timestamp("2025-07-22 19:31:00"), 'hatpro'],
        [pd.Timestamp("2025-07-22 19:31:00"), pd.Timestamp("2025-07-24 00:00:00"), 'mirac-p'],
        [pd.Timestamp("2025-07-24 00:00:00"), pd.Timestamp("2025-07-31 18:05:00"), 'hatpro'],
        [pd.Timestamp("2025-07-31 18:05:00"), pd.Timestamp("2025-08-01 20:30:00"), 'mirac-p'],
        [pd.Timestamp("2025-08-01 20:30:00"), pd.Timestamp("2025-08-03 09:54:00"), 'hatpro'],
        [pd.Timestamp("2025-08-03 09:54:00"), pd.Timestamp("2025-08-03 16:44:00"), 'mirac-p'],
        [pd.Timestamp("2025-08-03 16:44:00"), pd.Timestamp("2025-09-02 00:00:00"), 'hatpro'],        
    )
    
