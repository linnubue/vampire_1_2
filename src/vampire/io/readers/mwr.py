"""
Read microwave radiometer data from HATPRO and LHUMPRO.
"""

import os
import pdb
from glob import glob

import numpy as np
import pandas as pd
import xarray as xr

from vampire.constants import Constants as Constants
from vampire.io.readers.band_pass import create_band_pass
from vampire.analysis.data_tools import identify_files_daterange


def cleanup(ds, channels):
    """
    Removes and renames some variables.
    """

    ds = ds.drop_vars(
        [
            "file_code",
            "Rad_ID",
            "RSFactor",
            "IntSampCnt",
            "Freq",
            "Min_TBs",
            "Max_TBs",
            "AziAng",
        ]
    )
    ds = ds.rename(
        {
            "number_frequencies": "channel",
            "TBs": "tb",
            "RF": "rain_flag",
            "ElAng": "angle",
        }
    )
    ds["channel"] = channels
    ds = ds.transpose("time", "channel")

    return ds


def cleanup_mwr_pro(ds: xr.Dataset, channels=None):
    
    if channels is None:
        n_freq_avail = len(ds.n_freq)
        if n_freq_avail == 14:
            channels = np.arange(len(Constants.CH_HATPRO)) + 1
        elif n_freq_avail == 8:
            channels = np.arange(len(Constants.CH_LHUMPRO)) + 15
        elif n_freq_avail == 22:
            channels = np.arange(len(Constants.CH_HATPRO) + len(Constants.CH_LHUMPRO)) + 1
    
    ds['channel'] = channels
    ds = ds.rename({'n_freq': 'channel', 'ele': 'angle'})
    
    return ds


def add_band_pass(ds, instrument):
    """
    Adds band pass information. Note that the channel order of the band pass
    data should match the data.
    """

    ds_bp_hatpro, ds_bp_lhumpro, _, ds_bp_hatpro_lhumpro = create_band_pass()

    if instrument == "hatpro":
        ds = xr.merge([ds, ds_bp_hatpro])
    elif instrument == "mirac-p":
        ds = xr.merge([ds, ds_bp_lhumpro])
    elif instrument == "hatpro_mirac-p":
        ds = xr.merge([ds, ds_bp_hatpro_lhumpro])
    else:
        print("Instrument name unknown.")

    return ds


def read_scans(
    d0,
    d1,
    scans=None,
    append_normal=True,
    keep_mismatch=True,
    keep_atmos=True,
    daily_file=False,
    rain_flag=False,
):
    """
    Reads all scans for a given range of days.

    Returns
    -------
    dct : dict
        Dictionary with the output of read_dual for all scans.
    """

    if scans is None:
        scans = Constants.SCANS

    if isinstance(scans, str):
        scans = [scans]

    dct = {}
    for scan in scans:
        dct[scan] = read_dual(
            d0=d0,
            d1=d1,
            scan=scan,
            keep_mismatch=keep_mismatch,
            keep_atmos=keep_atmos,
            daily_file=daily_file,
            rain_flag=rain_flag,
            append_normal=append_normal,
        )

    # add instrument in normal operation to zenith time series
    if "ZENITH" in scans and append_normal:
        try:
            ds_mwr_normal = read_dual(
                d0=d0,
                d1=d1,
                scan="",
                keep_mismatch=keep_mismatch,
                keep_atmos=keep_atmos,
                daily_file=daily_file,
                rain_flag=rain_flag,
                append_normal=append_normal,
            )
            
            if (type(dct["ZENITH"]) != xr.Dataset) and (type(ds_mwr_normal) == xr.Dataset):
                dct['ZENITH'] = ds_mwr_normal
            elif (type(dct["ZENITH"]) != xr.Dataset) and (type(ds_mwr_normal) != xr.Dataset):
                raise FileNotFoundError
            elif (type(dct["ZENITH"]) == xr.Dataset) and (type(ds_mwr_normal) == xr.Dataset):
                dct["ZENITH"] = xr.concat(
                    [dct["ZENITH"], ds_mwr_normal],
                    dim="time",
                    coords="minimal",
                    data_vars="minimal",
                )
            dct['ZENITH'] = dct['ZENITH'].sortby('time')

        except FileNotFoundError:
            pass

    return dct


def read_dual(
    d0,
    d1,
    scan,
    keep_mismatch=True,
    keep_atmos=True,
    daily_file=False,
    rain_flag=False,
    append_normal=False,
):
    """
    Reads specific HATPRO and LHUMPRO scan for given range of days. Temporal
    mismatches of both instruments can be dropped. Atmospheric scans can be
    removed from surface scans.

    Examples:

    - Read emis: read_dual(date, scan="EMIS", keep_mismatch=True, keep_atmos=True)

    Parameters
    ----------
    date : datetime
        Observation date.
    keep_atmos : bool
        Keeps the intermediate atmospheric downwelling scan. Default is True.
    keep_mismatch : bool
        Keeps temporal mismatches between instruments. Default is True.
    """

    dates = pd.date_range(d0, d1, freq="1D")
    ds_lst = []
    for date in dates:
        try:
            ds_lst.append(
                read_dual_single(
                    date,
                    scan=scan,
                    keep_mismatch=keep_mismatch,
                    keep_atmos=keep_atmos,
                    daily_file=daily_file,
                    rain_flag=rain_flag,
                )
            )
        except FileNotFoundError:
            continue
        except IndexError:
            continue

    if len(ds_lst) == 0:
        if append_normal:
            return None
        else:
            raise FileNotFoundError(
                f"No '{scan}' mode data found between {d0} and {d1}"
            )
    else:
        ds_tb = xr.concat(ds_lst, dim="time", data_vars="minimal")

    return ds_tb


def read_dual_single(
    date,
    scan,
    keep_mismatch=True,
    keep_atmos=True,
    daily_file=False,
    rain_flag=False,
):
    """
    Reads specific HATPRO and LHUMPRO scan for one day. Temporal mismatches
    of both instruments can be dropped. Atmospheric scans can be removed from
    surface scans.

    Examples:

    - Read emis: read_dual(date, scan="EMIS", keep_mismatch=True, keep_atmos=True)

    Parameters
    ----------
    date : datetime
        Observation date.
    keep_atmos : bool
        Keeps the intermediate atmospheric downwelling scan. Default is True.
    keep_mismatch : bool
        Keeps temporal mismatches between instruments. Default is True.
    """

    ds_lst = []
    available_instrument = []
    for instrument in ["hatpro", "mirac-p"]:
        try:
            ds_instr = read_scan(
                            date=date,
                            instrument=instrument,
                            scan=scan,
                            daily_file=daily_file,
                            keep_atmos=keep_atmos,
                            rain_flag=rain_flag,
                            )
            if len(ds_instr.time) > 0:
                ds_lst.append(ds_instr)
                available_instrument.append(instrument)
        except FileNotFoundError:
            pass
    
    if len(available_instrument) == 2:
        ds = xr.concat(ds_lst, dim="number_frequencies")
        ds = cleanup(ds, channels=np.arange(1, 23))
    elif len(available_instrument) == 1:
        ds = ds_lst[0]
        if available_instrument[0] == "hatpro":
            ds = cleanup(ds, channels=np.arange(len(Constants.CH_HATPRO)) + 1)
        else:
            ds = cleanup(
                ds, channels=np.arange(len(Constants.CH_LHUMPRO)) + 15
            )
    else:
        raise FileNotFoundError(
            f"{date}: Cannot find HATPRO and LHUMPRO {scan} data."
        )

    # add band pass information
    ds = add_band_pass(ds, "hatpro_mirac-p")

    # ensure instruments see the same angle and record tb data
    if not keep_mismatch:
        ds = ds.sel(
            time=(ds.angle.isel(channel=0) == ds.angle.isel(channel=-1))
        )
        ds = ds.sel(time=~ds.tb.isnull().any("channel"))

    # drop times where all channels are nan
    ds = ds.sel(time=~ds.tb.isnull().all("channel"))

    return ds


def read_scan(
    date,
    instrument,
    scan,
    daily_file=False,
    keep_atmos=True,
    rain_flag=False,
    allow_duplicates=False,
):
    """
    Read BRT.NC file from VAMPIRE campaign. This reads the daily file of a
    given scan. The elevation angles are defined such that 0 degrees is nadir
    and 180 degrees is zenith.

    The RPG software created daily files automatically. However, these files
    do not always contain all hourly files. This reader can read either
    hourly files for one day or directly the daily files. The hourly file
    reading can be much slower depending on the number of files.

    Note that the rain flag was not checked against other sensors (disdrometer)
    and might also flag snowfall.

    Parameters
    ----------
    date : datetime
        Observation date.
    instrument : str
        Instrument name (hatpro or mirac-p).
    scan : str
        Scan type (ZENITH, EMIS, EMIS-SCAN, BL-SCAN, ELE40, ...).
    daily_files : bool
        Whether to read daily files or hourly files. Sometimes the daily file
        might not contain all hourly files. Default is False.
    """

    instrument = instrument.lower()
    scan = scan.upper()
    date = pd.Timestamp(date)

    ds = open_mwr_file(
        variable="BRT",
        date=date,
        instrument=instrument,
        scan=scan,
        daily_file=daily_file,
        allow_duplicates=allow_duplicates,
    )

    if rain_flag:
        ds = ds.sel(time=(ds.RF == 0))

    ds = drop_errors(ds, instrument=instrument)

    if instrument == "hatpro" and scan != "":
        ds["ElAng"] = 180 - ds["ElAng"]

    # make instrument in normal position like zenith scan in flipped position
    if scan == "":
        scan = "ZENITH"  # assume that these are zenith scans

        # same definition of zenith scan as when instrument is flipped
        ds_position = mwr_position()
        ds["ElAng"] += ds_position[instrument].sel(time=ds.time)

    # ensure that numeric value of elevation angle is exact
    if scan in ["ZENITH", "EMIS", "EMIS-SCAN", ""]:
        ds["ElAng"] = np.round(ds["ElAng"])
    elif scan in ["BL-SCAN"]:
        ds["ElAng"] = np.round(ds["ElAng"] * 10) / 10

    # sometimes, the above rounding still does not work, e.g. 180 degree
    # is stored at 179.1 degree
    da_ang = xr.DataArray(
        data=np.array(getattr(Constants, scan.replace("-", "_"))),
        dims=["angle"],
        coords={"angle": np.array(getattr(Constants, scan.replace("-", "_")))},
    )

    # make sure that angles are not completely different now
    all_angles_close = np.allclose(
        ds["ElAng"].values,
        da_ang.sel(angle=ds["ElAng"].values, method="nearest").values,
        rtol=0.1,
        atol=1,
    )
    # at edge of scan file, data from wrong scan can be included. Delete it:
    if not(all_angles_close):
        angles_close = np.isclose(ds["ElAng"].values, 
                                  da_ang.sel(angle=ds["ElAng"].values, method="nearest").values,
                                  rtol=0.1,
                                  atol=1,)
        ds = ds.sel(time=angles_close)

    ds["ElAng"] = (
        "time",
        da_ang.sel(angle=ds["ElAng"].values, method="nearest").values,
    )

    # basic checks
    if instrument == "hatpro":
        assert (
            len(ds.number_frequencies) == 14
        ), f"hatpro data {date} length of frequencies is {len(ds.number_frequencies)}"

    elif instrument == "mirac-p":
        assert (
            len(ds.number_frequencies) == 8
        ), f"mirac-p data {date} length of frequencies is {len(ds.number_frequencies)}"

    if not keep_atmos:
        ds = ds.where(ds.ElAng < 90)

    return ds


def open_mwr_file(
    variable, date, instrument, scan, daily_file=False, allow_duplicates=True
):
    """
    Opens a NetCDF file of HATPRO or LHUMPRO. This can open BRT, HKD, LV0, and
    MET files. Options are to open all hourly files of a day or directly the
    daily file.
    """

    instrument = instrument.lower()
    scan = scan.upper()
    date = pd.Timestamp(date)

    assert variable in ["BRT", "HKD", "LV0", "MET"]

    if daily_file:
        if len(scan) == 0:
            filename = f'{date.strftime("%y%m%d")}.{variable}.NC'
        else:
            filename = f'{scan}_{date.strftime("%y%m%d")}.{variable}.NC'

        file = os.path.join(
            os.environ["VAMPIRE_DATA"],
            instrument,
            date.strftime("Y%Y/M%m/D%d"),
            filename,
        )

        if not os.path.exists(file):
            raise FileNotFoundError(
                f"{date}: Cannot find {instrument} {scan} file."
            )

        ds = xr.open_dataset(file)

    else:
        if len(scan) == 0:
            filename = f'{date.strftime("%y%m%d")}??.{variable}.NC'
        else:
            filename = f'{scan}_{date.strftime("%y%m%d")}_*.{variable}.NC'

        file_pattern = os.path.join(
            os.environ["VAMPIRE_DATA"],
            instrument,
            date.strftime("Y%Y/M%m/D%d"),
            filename,
        )
        files = sorted(glob(file_pattern))

        if len(files) == 0:
            raise FileNotFoundError(
                f"{date}: Cannot find {instrument} {scan} files."
            )

        ds = xr.open_mfdataset(
            files, concat_dim="time", combine="nested"
        ).load()

    if not allow_duplicates:
        ds = drop_duplicates(ds)

    return ds


def read_multiscan_met(
    date: str, 
    instrument: str, 
    scans: list, 
    daily_file=False, 
    allow_duplicates=True,
    mwr_pro_output=False,
    version="i00"):
    
    if isinstance(scans, str):
        scans = [scans]
    
    ds_list = list()
    for scan in scans:
        try:
            if mwr_pro_output:
                ds = read_mwr_pro_output_scan(scan=scan, 
                                              date_range=np.array([np.datetime64(date)]),
                                              file_pattern=get_mwr_pro_filepattern(instrument, version=version),
                                              radiometer=instrument,
                                              drop_errs=False,
                                              drop_auxiliaries=False)
            else:
                ds = open_mwr_file("MET", date, instrument=instrument, scan=scan,
                                    daily_file=daily_file, allow_duplicates=allow_duplicates)

        except FileNotFoundError:
            continue
        ds_list.append(ds)
    
    try:
        ds = xr.concat(ds_list, dim="time").sortby('time')
    except ValueError:
        ds = xr.Dataset()
    
    return ds


def get_best_met(
    date: str, 
    scans: list, 
    daily_file=False, 
    allow_duplicates=True, 
    mwr_pro_output=False):

    ds_l = read_multiscan_met(date, instrument='mirac-p', scans=scans, daily_file=daily_file, 
                                allow_duplicates=allow_duplicates, mwr_pro_output=mwr_pro_output)
    ds_h = read_multiscan_met(date, instrument='hatpro', scans=scans, daily_file=daily_file, 
                                allow_duplicates=allow_duplicates, mwr_pro_output=mwr_pro_output)
    t2m_period_hat = [[item[0], item[1]] for item in Constants.T2M_HATPRO_LHUMPRO if item[2]=='hatpro']
    t2m_period_lhu = [[item[0], item[1]] for item in Constants.T2M_HATPRO_LHUMPRO if item[2]=='mirac-p']
    
    ds_list = list()
    for ds_, t2m_period in zip([ds_h, ds_l], [t2m_period_hat, t2m_period_lhu]):
        try:
            ds_ = merge_subperiods(ds_, t2m_period)
        except AttributeError:
            ds_ = xr.Dataset(coords={'time': (['time'], np.array([],dtype='datetime64[ns]'))})
        
        for dim in ds_.dims:
            if dim != "time": ds_ = ds_.drop_dims(dim)
        ds_list.append(ds_)
        
    ds = xr.concat(ds_list, dim='time').sortby('time')
    
    if "Surf_T" in ds.data_vars: ds = ds.rename({'Surf_T': "ta"})
    
    return ds


def merge_subperiods(ds: xr.Dataset, list_of_intervals: list):
    
    ds_list = list()
    for interval in list_of_intervals:
        ds_list.append(
            ds.sel(
                time=((ds.time >= interval[0]) & 
                      (ds.time < interval[1]))
                )
            )
    ds = xr.concat(ds_list, dim='time').sortby('time')
    
    return ds


def drop_duplicates(ds):
    """
    Drop duplicate times from the dataset.
    """

    _, ix = np.unique(ds.time, return_index=True)
    ds = ds.isel(time=ix)

    return ds


def correct_scan_lims_for_correct_ele(scan_lims: dict, instrument: str):
    
    if instrument == 'hatpro':
        for key in scan_lims.keys():
            scan_lims[key] += 90.
            scan_lims[key][scan_lims[key] > 90.5] = (180. - scan_lims[key])
    elif instrument == 'mirac-p':
        for key in scan_lims.keys(): scan_lims[key] -= 90.
        
    return scan_lims


def drop_errors(ds, instrument, ele_ang_varname="ElAng", mwr_pro_output=False):
    """
    Drops errors in time stamp. 0 degrees is nadir and 180 degrees is zenith
    """

    # Some time values are 2001-01-01. E.g. the zenith-scan by HATPRO right
    # before the measurement on 2024-08-18T00:00:01. TB is also 0.
    ds = ds.sel(time=ds.time > np.datetime64("2001-01-01"))

    # this hatpro zenith observation is contained in the bl-scan file. This
    # was triggered by instrument switch off. To avoid confusion it is dropped.
    t0, t1 = (
        np.datetime64("2024-08-18T14:03:28"),
        np.datetime64("2024-08-18T14:05:33"),
    )
    ds = ds.sel(time=~((ds.time >= t0) & (ds.time <= t1)))

    # use data only from 2024-08-10 onwards. The hatpro zenith scan on
    # the 2024-08-10 contains also data from 2024-08-09T19:00:00 to
    # 2024-08-09T19:13:50 - this gets removed here
    ds = ds.sel(time=ds.time >= np.datetime64("2024-08-10 00:00:00"))

    # drop 25 degree scans, because they are not sensitive to the
    # surface. Some tolerance is added to the angle, because they are not
    # exactly 25 in the files
    # the corresponding atmospheric scan is removed too
    scans_to_drop_lims = {'atm': np.array([23., 27.]),
                          'sfc': np.array([153., 157.]),
                          'horizon': np.array([90.])}
    if mwr_pro_output:
        scans_to_drop_lims = correct_scan_lims_for_correct_ele(scans_to_drop_lims, instrument=instrument)
    for key in scans_to_drop_lims.keys(): scans_to_drop_lims[key] = np.sort(scans_to_drop_lims[key])
        
    if ds[ele_ang_varname].ndim == 1:
        ds = ds.sel(time=~((ds[ele_ang_varname] > scans_to_drop_lims['atm'][0]) & 
                           (ds[ele_ang_varname] < scans_to_drop_lims['atm'][1])))
        ds = ds.sel(time=~((ds[ele_ang_varname] > scans_to_drop_lims['sfc'][0]) & 
                           (ds[ele_ang_varname] < scans_to_drop_lims['sfc'][1])))
        
        # times when instruments were covered in plastics from above. Only scans
        # below the horizon can be used for these times.
        ds = ds.sel(
            time=~(
                (ds.time >= np.datetime64("2024-08-27 10:05"))
                & (ds.time <= np.datetime64("2024-08-27 18:45"))
                & (ds[ele_ang_varname] > scans_to_drop_lims['horizon'])
            )
        )
    elif ds[ele_ang_varname].ndim == 2:     # for MWR_PRO generated TB files of atmospheric boundary layer scans
        ds = ds.sel(time=~(((ds[ele_ang_varname] > scans_to_drop_lims['atm'][0]) & 
                            (ds[ele_ang_varname] < scans_to_drop_lims['atm'][1])).any('n_angle')))
        ds = ds.sel(time=~(((ds[ele_ang_varname] > scans_to_drop_lims['sfc'][0]) & 
                            (ds[ele_ang_varname] < scans_to_drop_lims['sfc'][1])).any('n_angle')))

        ds = ds.sel(
            time=~(
                (ds.time >= np.datetime64("2024-08-27 10:05"))
                & (ds.time <= np.datetime64("2024-08-27 18:45"))
                & ((ds[ele_ang_varname] > scans_to_drop_lims['horizon']).any('n_angle'))
            )
        )

    # hatpro was still flipped for calibration when measurement was started
    if instrument == "hatpro":
        ds = ds.sel(
            time=~(
                (ds.time >= np.datetime64("2024-09-11 13:00"))
                & (ds.time <= np.datetime64("2024-09-11 15:20"))
            )
        )
        
        # PS149: remove data before 2025-07-04 18:01:58 since that was only testing and
        # calibration:
        ds = ds.sel(time=~((ds.time >= np.datetime64("2025-07-01 00:00:00")) & 
                           (ds.time < np.datetime64("2025-07-04 18:01:58"))))
        
        # PS149: remove test measurements after HATPRO outage due to short circuit:
        ds = ds.sel(time=~((ds.time >= np.datetime64("2025-08-02 10:11:00")) &
                           (ds.time < np.datetime64("2025-08-02 12:46:12"))))
        
        # PS149: remove hatpro calibration:
        ds = ds.sel(time=~((ds.time >= np.datetime64("2025-08-06 15:42:28")) &
                           (ds.time < np.datetime64("2025-08-06 19:13:12"))))
        
    if instrument == 'mirac-p':
        
        # PS149: remove test obs and calibration:
        ds = ds.sel(time=~((ds.time >= np.datetime64("2025-07-01 00:00:00")) &
                           (ds.time < np.datetime64("2025-07-04 06:55:33"))))
        
        # PS149: calibration:
        ds = ds.sel(time=~((ds.time >= np.datetime64("2025-08-06 15:42:24")) &
                           (ds.time < np.datetime64("2025-08-06 19:13:24"))))

    return ds


def mwr_position():
    """
    Time series of the MWR angle offset. This gives a 90 degree offset to
    zenith scans in normal position. Then, zenith is defined as 180 for both
    HATPRO and LHUMPRO.
    """

    times = pd.date_range(
        Constants.DATE_START,
        Constants.DATE_END,
        freq="1s",
    )

    # start and end times when instrument was in normal position
    start_end_normal = {
        "hatpro": [
            (
                pd.Timestamp("2024-10-05T09:53:23"),
                pd.Timestamp("2024-10-09T23:59:59"),
            ),
            (
                pd.Timestamp("2025-07-04 18:01:58"),
                pd.Timestamp("2025-07-06 08:00:29"),
            ),
            (
                pd.Timestamp("2025-08-29T12:00:00"),
                pd.Timestamp("2025-08-31T23:59:59")
            ),
        ],
        "mirac-p": [
            (
                pd.Timestamp("2024-10-05T09:54:12"),
                pd.Timestamp("2024-10-09T23:59:59"),
            ),
            (
                pd.Timestamp("2025-07-04 06:55:33"),
                pd.Timestamp("2025-07-06 08:00:41"),
            ),
            (
                pd.Timestamp("2025-08-29T12:00:00"),
                pd.Timestamp("2025-08-31T23:59:59"),
            ),
        ],
    }

    # angle offset
    df = pd.DataFrame(index=times, data={"hatpro": 0, "mirac-p": 0})
    df.index.name = "time"
    for instrument in ["hatpro", "mirac-p"]:
        for t0, t1 in start_end_normal[instrument]:
            df.loc[slice(t0, t1), instrument] += 90

    return df.to_xarray()


def mwr_pro_flags_nan_to_num(DS: xr.Dataset):
    
    DS['flag'][np.isnan(DS['flag'])] = 0.
    
    return DS


def get_mwr_pro_filepattern(radiometer="hatpro", version="i00"):
    
    if radiometer == 'hatpro':
        mwr_number = "00"
    elif radiometer == 'mirac-p':
        mwr_number = "01"
    file_pattern = f"ioppol__FILEPATTERN___uoc_mwr{mwr_number}_l1_tb_{version}___DATE_STRING__[0-2][0-9][0-5][0-9][0-5][0-9].nc"
    
    return file_pattern


def read_mwr_pro_dual(
    path_data="",
    date_range=None,
    d0=None,
    d1=None, 
    scans=None,
    keep_mismatch=True,
    sorted_into_daily_folders=False,
    version="i00",
    drop_errs=True,
    drop_auxiliaries=False,
    clean_up=False):
    
    DS_list = list()
    for radiometer in ['hatpro', 'mirac-p']:
        DS = read_mwr_pro_output(path_data=path_data, 
                                 date_range=date_range, 
                                 d0=d0, 
                                 d1=d1,
                                 scans=scans, 
                                 with_default_bl_scan=False,
                                 sorted_into_daily_folders=sorted_into_daily_folders,
                                 radiometer=radiometer,
                                 version=version, 
                                 concat_scans=True,
                                 drop_errs=False,       # for better performance it's performed after full import here
                                 drop_auxiliaries=drop_auxiliaries)
        
        if drop_errs: DS = drop_errors(DS, instrument=radiometer, ele_ang_varname='ele', mwr_pro_output=True)
        if len(DS.time) > 0:
            DS['flag'] = DS['flag'].expand_dims(
                dim={'n_freq': DS.freq_sb}, axis=1).assign_coords(n_freq=DS.freq_sb).drop('n_freq')
            DS_list.append(DS)
    
    DS = xr.concat(DS_list, dim='n_freq')
    DS = DS.transpose('time', 'n_freq', ...)
    

    if np.any((DS.ele.max('n_freq') - DS.ele.min('n_freq')) > 0.1): pdb.set_trace()
    if (((DS['ele'] > 23) & (DS['ele'] < 27)) | ((DS['ele'] > 153) & (DS['ele'] < 157))).any(): pdb.set_trace()
    
    if not keep_mismatch:
        DS = DS.sel(time=np.abs(DS.ele.isel(n_freq=0) - DS.ele.isel(n_freq=-1)) <= 0.1)
        DS = DS.sel(time=~DS.tb.isnull().any("n_freq"))

    DS = DS.sel(time=~DS.tb.isnull().all("n_freq"))
    if len(DS.time) == 0:
        raise ValueError
    
    if clean_up:
        DS = cleanup_mwr_pro(ds=DS)
        instr_avail = {'14': "hatpro", "8": "mirac-p", "22": "hatpro_mirac-p"}
        DS = add_band_pass(DS, instr_avail[str(len(DS['channel']))])
    
    return DS


def read_mwr_pro_output(
    path_data="", 
    date_range=None, 
    d0=None, 
    d1=None, 
    scans=None,
    with_default_bl_scan=False,
    sorted_into_daily_folders=False,
    radiometer="hatpro",
    version="i00",
    concat_scans=True,
    drop_errs=True,
    drop_auxiliaries=False):
    
    """
    Read MWR_PRO output for dates between d0 and d1 or, if d0 and d1 are None, for all available dates.
    
    Parameters:
    -----------
    with_default_bl_scan : bool
        Should be set True if .BLB file based MWR_PRO output, where TB data has time, frequency 
        and elevation angle dimensions, is used. Else, False.
    """
    
    if scans is None:
        scans = Constants.SCANS

    if (date_range is None) and ((d0 is not None) and (d1 is not None)):
        date_range = np.arange(np.datetime64(d0), np.datetime64(d1) + np.timedelta64(1, "D"),
                               np.timedelta64(1, "D"))
    
    file_pattern = get_mwr_pro_filepattern(radiometer=radiometer, version=version)
    
    DS_dict = dict() 
    for scan in scans:
        try:
            ds_ = read_mwr_pro_output_scan(path_data=path_data, 
                                           scan=scan,
                                           date_range=date_range, 
                                           file_pattern=file_pattern,
                                           radiometer=radiometer,
                                           sorted_into_daily_folders=sorted_into_daily_folders,
                                           drop_errs=drop_errs,
                                           drop_auxiliaries=drop_auxiliaries)
        except FileNotFoundError:
            continue
        
        DS_dict[scan] = ds_
        
        if with_default_bl_scan and (radiometer == 'hatpro') and (scan == ''):
            try:
                ds_ = read_mwr_pro_output_scan(
                    path_data=path_data, 
                    scan=scan,
                    date_range=date_range, 
                    file_pattern=file_pattern.replace("mwr00", "mwrBL00"),
                    sorted_into_daily_folders=sorted_into_daily_folders, 
                    )
            except FileNotFoundError:
                continue
            
            DS_dict[scan+"_bl"] = ds_
    
    if concat_scans:
        DS = xr.concat([*DS_dict.values()], dim='time').sortby('time')
        
        return DS
    
    return DS_dict


def read_mwr_pro_output_scan(
    path_data="", 
    scan="ZENITH",
    date_range=None,
    file_pattern="",
    radiometer="hatpro",
    sorted_into_daily_folders=False,
    drop_errs=True,
    drop_auxiliaries=False):
    
    def preprocess_mwr_pro(DS: xr.Dataset):      
        
        DS = DS.assign_coords({'freq_sb': (['n_freq'], DS.freq_sb.values,
                                           DS.freq_sb.attrs)})
        if 'n_freq2' in DS.dims: 
            DS = DS.drop_dims('n_freq2')
        
        time_rounded = pd.Series(DS.time.values, dtype='datetime64[ns]').round('s')
        DS = DS.assign_coords({'time': (['time'], time_rounded.astype('datetime64[ns]'))})
          
        return DS
    
    
    if path_data == "":
        path_data = os.environ['VAMPIRE_DATA'] + radiometer + "/"
        
    path_add = {'ZENITH': "atm", 'BL-SCAN': "atm_bl", '': "atm_transit",
                'EMIS': "sfc", 'EMIS-SCAN': 'sfc'}
    file_pattern_add = {'ZENITH': "", 'BL-SCAN': "_BL", '': "",
                        'EMIS': "", 'EMIS-SCAN': ""}
    path_data = path_data + "/".join([path_add[scan], "l1", ""])
    file_pattern = file_pattern.replace("__FILEPATTERN__", file_pattern_add[scan])
    
    
    if sorted_into_daily_folders:
        raise NotImplementedError("Import of data sorted into daily folders has not been implemented yet...")
    else:
        if (date_range is not None):
            files = identify_files_daterange(path_data, date_range, file_pattern=file_pattern, yyyymmdd_delim="")
        else:
            files = sorted(glob(path_data + file_pattern))
    
    if len(files) == 0:
        raise FileNotFoundError(
            f"{date_range}: Cannot find {radiometer} {scan} file."
        )
    
    DS = xr.open_mfdataset(files, concat_dim='time', combine='nested', preprocess=preprocess_mwr_pro)
    DS = DS.drop_duplicates('time')
    
    DS['ele'] = np.round(DS.ele * 10.) / 10.
    if radiometer == 'hatpro':
        DS['ele'] = DS.ele.where((DS.ele >= 0.) & (DS.ele < 90.5), other=180. - DS.ele)
    
    DS = mwr_pro_flags_nan_to_num(DS)
    
    if drop_errs:
        DS = drop_errors(DS, instrument=radiometer, ele_ang_varname='ele', mwr_pro_output=True)
    
    if drop_auxiliaries:
        vars_to_drop = [var for var in DS.data_vars if var not in ['tb', 'ele', 'flag']]
        DS = DS.drop_vars(vars_to_drop)
    else:
        for var in ['wl_irp', 'tb_irp', 'ele_irp']:     # were not installed during VAMPIRE-1 and -2
            if var in DS.data_vars: DS = DS.drop_vars(var)
    
    return DS