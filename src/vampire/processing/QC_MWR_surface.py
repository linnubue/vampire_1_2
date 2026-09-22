import xarray as xr
from vampire.constants import Constants
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import glob as glob

times_to_flag_VAMPIRE_people_potentially_in_footprint = [[pd.Timestamp('2024-08-16 14:40:00'),pd.Timestamp('2024-08-16 18:42:00')],
                                                         [pd.Timestamp('2024-08-29 17:15:00'),pd.Timestamp('2024-08-29 21:28:45')],
                                                         [pd.Timestamp('2024-08-30 08:31:30'),pd.Timestamp('2024-08-30 08:59:30')],
                                                         [pd.Timestamp('2024-09-02 21:05:00'),pd.Timestamp('2024-09-02 23:39:45')],
                                                         [pd.Timestamp('2024-09-05 06:54:00'),pd.Timestamp('2024-09-05 11:09:50')],
                                                         [pd.Timestamp('2024-09-08 08:30:00'),pd.Timestamp('2024-09-08 12:24:00')],
                                                         [pd.Timestamp('2024-09-08 18:33:30'),pd.Timestamp('2024-09-08 19:21:05')],
                                                         [pd.Timestamp('2024-09-10 22:25:00'),pd.Timestamp('2024-09-11 02:01:30')],
                                                         [pd.Timestamp('2024-09-11 02:05:05'),pd.Timestamp('2024-09-11 02:06:25')],
                                                         [pd.Timestamp('2024-09-13 08:15:00'),pd.Timestamp('2024-09-13 11:43:10')],
                                                         [pd.Timestamp('2024-09-18 21:50:00'),pd.Timestamp('2024-09-19 00:01:35')],
                                                         [pd.Timestamp('2024-09-19 08:01:35'),pd.Timestamp('2024-09-19 11:21:40')], ##no GoPro data between 8:30 and 11:20 but around 11:20 there are people in the footprint, so flag to be cautios
                                                         [pd.Timestamp('2024-09-19 13:40:05'),pd.Timestamp('2024-09-19 15:01:10')],
                                                         [pd.Timestamp('2024-09-19 19:55:10'),pd.Timestamp('2024-09-19 20:01:05')],
                                                         [pd.Timestamp('2024-09-19 20:24:18'),pd.Timestamp('2024-09-19 20:32:00')],
                                                         [pd.Timestamp('2024-09-23 06:45:00'),pd.Timestamp('2024-09-23 09:24:40')],
                                                         [pd.Timestamp('2024-09-26 00:00:00'),pd.Timestamp('2024-09-26 03:07:55')]
                                                        ]
times_to_flag_VAMPIRE_measurements_disturbed_surface = [[pd.Timestamp('2024-08-16 14:40:00'),pd.Timestamp('2024-08-17 04:04:45')],
                                                             [pd.Timestamp('2024-08-29 17:15:00'),pd.Timestamp('2024-08-30 11:33:30')],
                                                             [pd.Timestamp('2024-09-02 21:05:00'),pd.Timestamp('2024-09-03 00:57:34')],   
                                                             [pd.Timestamp('2024-09-05 06:54:00'),pd.Timestamp('2024-09-05 19:09:00')],
                                                             [pd.Timestamp('2024-09-08 08:30:00'),pd.Timestamp('2024-09-09 00:18:00')],
                                                             [pd.Timestamp('2024-09-10 22:25:00'),pd.Timestamp('2024-09-11 07:23:25')],
                                                             [pd.Timestamp('2024-09-13 08:15:00'),pd.Timestamp('2024-09-13 23:40:00')],
                                                             [pd.Timestamp('2024-09-18 21:50:00'),pd.Timestamp('2024-09-19 22:48:15')],
                                                             [pd.Timestamp('2024-09-23 06:45:00'),pd.Timestamp('2024-09-23 14:49:11')],
                                                             [pd.Timestamp('2024-09-26 00:00:00'),pd.Timestamp('2024-09-26 06:14:20')]
                                                            ]
times_to_flag_VAMPIRE2_people_potentially_in_footprint =[[pd.Timestamp('2025-07-09 17:38'),pd.Timestamp('2025-07-09 18:48')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from event labels, 
                                                         [pd.Timestamp('2025-07-10 12:40'),pd.Timestamp('2025-07-10 14:00')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from event labels
                                                         [pd.Timestamp('2025-07-11 09:08'),pd.Timestamp('2025-07-11 11:00')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from event labels
                                                         [pd.Timestamp('2025-07-15 13:15'),pd.Timestamp('2025-07-15 15:05')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp('2025-07-16 12:40'),pd.Timestamp('2025-07-16 15:09')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp('2025-07-17 08:52'),pd.Timestamp('2025-07-17 10:00')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from event labels
                                                         [pd.Timestamp('2025-07-20 12:45'),pd.Timestamp('2025-07-20 15:15')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp('2025-07-21 12:37'),pd.Timestamp('2025-07-21 15:34')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp('2025-07-22 12:30'),pd.Timestamp('2025-07-22 14:19')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from event labels
                                                         [pd.Timestamp('2025-07-26 12:32'),pd.Timestamp('2025-07-26 14:25')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp('2025-07-27 12:32'),pd.Timestamp('2025-07-27 14:11')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp('2025-07-28 09:05'),pd.Timestamp('2025-07-28 10:48')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp("2025-07-30 12:53"),pd.Timestamp('2025-07-30 14:22')],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp("2025-07-31 12:53"),pd.Timestamp("2025-07-31 14:22")],##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes (same as day before, but true to notes and event labels)
                                                         [pd.Timestamp("2025-08-01 12:42"),pd.Timestamp("2025-08-01 14:00")],##start from TIME_ICE_SAMPLING_CONTRASTS,
                                                         [pd.Timestamp('2025-08-04 07:00'),pd.Timestamp('2025-08-06 19:30')],##station 3b flagged completely, start and end from dship speed, checked with GoPro images
                                                         [pd.Timestamp("2025-08-09 15:42"),pd.Timestamp("2025-08-09 17:05")], ##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp("2025-08-10 12:32"),pd.Timestamp("2025-08-10 13:52")], ##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp('2025-08-12 08:00'),pd.Timestamp('2025-08-14 17:30')], ##station 2c flagged completely, start and end from dship speed, checked with GoPro images
                                                         [pd.Timestamp("2025-08-16 20:35"),pd.Timestamp("2025-08-16 21:57")], ##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp("2025-08-17 12:32"),pd.Timestamp("2025-08-17 13:59")], ##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp("2025-08-18 14:21"),pd.Timestamp("2025-08-18 16:56")], ##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp("2025-08-23 13:30"),pd.Timestamp("2025-08-23 14:22")], ##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp("2025-08-24 12:31"),pd.Timestamp("2025-08-24 14:57")], ##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp("2025-08-26 12:32"),pd.Timestamp("2025-08-26 15:18")], ##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                         [pd.Timestamp("2025-08-27 12:32"),pd.Timestamp("2025-08-27 14:08")], ##start from TIME_ICE_SAMPLING_CONTRASTS, end time from field notes
                                                        ]
times_to_flag_VAMPIRE2_measurements_disturbed_surface = [[pd.Timestamp('2025-07-09 17:38'),pd.Timestamp('2025-07-13 00:30')], ##from start of measurements day 1 until end of day3 determined from dship speed 
                                                         [pd.Timestamp('2025-07-15 13:15'),pd.Timestamp('2025-07-17 21:30')], ##from start of measurements day 1 until end of day3 determined from dship speed 
                                                         [pd.Timestamp('2025-07-20 12:45'),pd.Timestamp('2025-07-22 19:30')], ##from start of measurements day 1 until end of day3 determined from dship speed 
                                                         [pd.Timestamp('2025-07-26 12:32'),pd.Timestamp('2025-07-28 19:45')], ##from start of measurements day 1 until end of day3 determined from dship speed
                                                         [pd.Timestamp('2025-07-30 12:53'),pd.Timestamp('2025-08-01 21:00')], ##from start of measurements day 1 until end of day3 determined from dship speed
                                                         [pd.Timestamp('2025-08-04 07:00'),pd.Timestamp('2025-08-06 19:30')],##station 3b flagged completely, start and end from dship speed, checked with GoPro images
                                                         [pd.Timestamp('2025-08-09 15:42'),pd.Timestamp('2025-08-10 22:20')], ##from start of measurements day 1 until end of day3 determined from dship speed
                                                         [pd.Timestamp('2025-08-12 08:00'),pd.Timestamp('2025-08-14 17:30')], ##station 2c flagged completely, start and end from dship speed, checked with GoPro images
                                                         [pd.Timestamp('2025-08-16 20:35'),pd.Timestamp('2025-08-18 22:50')], ##from start of measurements day 1 until end of day3 determined from dship speed
                                                         [pd.Timestamp('2025-08-23 13:30'),pd.Timestamp('2025-08-24 16:25')], ##from start of measurements day 1 until end of day3 determined from dship speed
                                                         [pd.Timestamp('2025-08-26 12:32'),pd.Timestamp('2025-08-27 18:05')], ##from start of measurements day 1 until end of day3 determined from dship speed

             ]

# Original flag masks
flag_masks = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256, 512], dtype=np.int16)

# Adding two more flags
new_flag_masks = np.array([1024, 2048], dtype=np.int16)
flag_masks = np.concatenate((flag_masks, new_flag_masks))

def set_flags()
    all_hapro_files = glob.glob('PS144hatpro_mwrpro_sfc/*.nc')
    for file in all_hapro_files:
        ds = xr.open_dataset(file)
        filename = os.path.basename(file)
        ds["flag"].attrs["flag_masks"] = [
        1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]

        ds["flag"].attrs["flag_meanings"] = (
            "visual_inspection_filter_band1 visual_inspection_filter_band2 visual_inspection_filter_band3 " 
            "rain_flag sanity_receiver_band1 sanity_receiver_band2 sun_in_beam tb_threshold_band1 "
            "tb_threshold_band2 tb_threshold_band3 "
            "disturbed_footprint_duringafter_insitu_measurements people_potentially_in_footprint"
        )
        for time in times_to_flag_VAMPIRE_measurements_disturbed_surface:##flag 1024
            mask1 = (ds.time >= time[0]) & (ds.time <= time[1])
            ds["flag"] = ds["flag"].where(~mask1, ds["flag"] | 1024)

        for time in times_to_flag_VAMPIRE_people_potentially_in_footprint: ##flag 2048
            mask2 = (ds.time >= time[0]) & (ds.time <= time[1])
            ds["flag"] = ds["flag"].where(~mask2, ds["flag"] | 2048)
        ds.to_netcdf(f"flagged/{filename}")     
        
    all_mirac_files = glob.glob(f'PS144mirac_mwrpro_sfc/*.nc'')
    for file in all_mirac_files:

        ds = xr.open_dataset(file)
        filename = os.path.basename(file)
        ds["flag"].attrs["flag_masks"] = [
            1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048
        ]
        ds["flag"].attrs["flag_meanings"] = (
            "visual_inspection_filter_band1 visual_inspection_filter_band2 visual_inspection_filter_band3 " 
            "rain_flag sanity_receiver_band1 sanity_receiver_band2 sun_in_beam tb_threshold_band1 "
            "tb_threshold_band2 tb_threshold_band3 "
            "disturbed_footprint_duringafter_insitu_measurements people_potentially_in_footprint"
        )     
        for time in times_to_flag_VAMPIRE_measurements_disturbed_surface:##flag 1024
            mask1 = (ds.time >= time[0]) & (ds.time <= time[1])
            ds["flag"] = ds["flag"].where(~mask1, ds["flag"] | 1024)

        for time in times_to_flag_VAMPIRE_people_potentially_in_footprint: ##flag 2048
            mask2 = (ds.time >= time[0]) & (ds.time <= time[1])
            ds["flag"] = ds["flag"].where(~mask2, ds["flag"] | 2048)
        ds.to_netcdf(f"flagged/{filename}")     
                                
    all_hapro_files = glob.glob(f'PS149hatpro_mwrpro_sfc/*.nc')
    for file in all_hapro_files:
        print(file)
        ds = xr.open_dataset(file)
        filename = os.path.basename(file)
        ds["flag"].attrs["flag_masks"] = [
        1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]

        ds["flag"].attrs["flag_meanings"] = (
            "visual_inspection_filter_band1 visual_inspection_filter_band2 visual_inspection_filter_band3 " 
            "rain_flag sanity_receiver_band1 sanity_receiver_band2 sun_in_beam tb_threshold_band1 "
            "tb_threshold_band2 tb_threshold_band3 "
            "disturbed_footprint_duringafter_insitu_measurements people_potentially_in_footprint"
        )
        for time in times_to_flag_VAMPIRE2_measurements_disturbed_surface:##flag 1024
            mask1 = (ds.time >= time[0]) & (ds.time <= time[1])
            ds["flag"] = ds["flag"].where(~mask1, ds["flag"] | 1024)

        for time in times_to_flag_VAMPIRE2_people_potentially_in_footprint: ##flag 2048
            mask2 = (ds.time >= time[0]) & (ds.time <= time[1])
            ds["flag"] = ds["flag"].where(~mask2, ds["flag"] | 2048)
        ds.to_netcdf(f"{path_hatpro_VAMPIRE2}/flagged/{filename}")     
    all_mirac_files = glob.glob(f'PS149mirac_mwrpro_sfc/*.nc')
    for file in all_mirac_files:

        ds = xr.open_dataset(file)
        filename = os.path.basename(file)
        ds["flag"].attrs["flag_masks"] = [
            1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048
        ]
        ds["flag"].attrs["flag_meanings"] = (
            "visual_inspection_filter_band1 visual_inspection_filter_band2 visual_inspection_filter_band3 " 
            "rain_flag sanity_receiver_band1 sanity_receiver_band2 sun_in_beam tb_threshold_band1 "
            "tb_threshold_band2 tb_threshold_band3 "
            "disturbed_footprint_duringafter_insitu_measurements people_potentially_in_footprint"
        )     
        for time in times_to_flag_VAMPIRE2_measurements_disturbed_surface:##flag 1024
            mask1 = (ds.time >= time[0]) & (ds.time <= time[1])
            ds["flag"] = ds["flag"].where(~mask1, ds["flag"] | 1024)

        for time in times_to_flag_VAMPIRE2_people_potentially_in_footprint: ##flag 2048
            mask2 = (ds.time >= time[0]) & (ds.time <= time[1])
            ds["flag"] = ds["flag"].where(~mask2, ds["flag"] | 2048)
        ds.to_netcdf(f"flagged/{filename}")     
