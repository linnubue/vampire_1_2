"""
Reader functions for radiosonde data.
"""

import datetime as dt
import os as os
import pdb
from glob import glob

import numpy as np
import pandas as pd
import xarray as xr

from vampire.analysis import met_tools, data_tools
from vampire.constants import Constants as Constants


def read_pamtra_simulation_all():
    """
    Reads PAMTRA simulation for all radiosondes
    """

    files, times = get_radiosondes()

    ix = ~np.isin(times, np.array(Constants.PS144_BAD_SONDES).astype("datetime64"))
    times = times[ix]
    files = files[ix]

    lst_s = []
    lst_h = []
    lst_m = []
    for time in times:
        ds_spectrum, ds_hatpro_lhumpro, ds_mirac_a = read_pamtra_simulations(time)
        lst_s.append(ds_spectrum)
        lst_h.append(ds_hatpro_lhumpro)
        lst_m.append(ds_mirac_a)
    ds_spectrum = xr.concat(lst_s, dim='launch_time').assign_coords(launch_time=times)
    ds_hatpro_lhumpro = xr.concat(lst_h, dim='launch_time').assign_coords(launch_time=times)
    ds_mirac_a = xr.concat(lst_m, dim='launch_time').assign_coords(launch_time=times)
    
    return ds_spectrum, ds_hatpro_lhumpro, ds_mirac_a


def read_pamtra_simulations(time):
    """
    Reads PAMTRA simulations for a specific radiosonde.
    """

    ds_spectrum = read_pamtra_simulation(time=time, name="spectrum")
    ds_hatpro_lhumpro = read_pamtra_simulation(time=time, name="tb_hatpro_lhumpro")
    ds_mirac_a = read_pamtra_simulation(time=time, name="tb_mirac_a")

    return ds_spectrum, ds_hatpro_lhumpro, ds_mirac_a


def read_pamtra_simulation(time, name):
    """
    Reads PAMTRA simulation of specific time and with specific name.

    Parameters
    ----------
    time : datetime
        Time of the radiosonde.
    name : str
        Name of the simulation. Options are: "spectrum", "tb_mirac_a", 
        "tb_hatpro_lhumpro"
    """

    time = pd.Timestamp(time)
    path = os.path.join(
        os.environ["VAMPIRE_DATA"],
        "radiosondes_pamtra",
    )

    ds = xr.open_dataset(
        os.path.join(
            path,
            f"pamtra_{name}_{time.strftime('%Y%m%d_%H')}.nc",
        )
    )

    return ds


def get_radiosondes(date=None, date_range=np.array([])):
    """
    Get all radiosonde files
    """

    if date is None:
        files = sorted(
            glob(
                os.path.join(
                    os.environ["VAMPIRE_DATA"],
                    "radiosondes",
                    "*_pangaea.txt",
                )
            )
        )
    
    else:
        date = pd.Timestamp(date)
        files = sorted(
            glob(
                os.path.join(
                    os.environ["VAMPIRE_DATA"],
                    "radiosondes",
                    f"{date.strftime('%Y%m%d')}*_pangaea.txt",
                )
            )
        )
        
    if len(date_range) > 0:
        files = list()
        for date in date_range:
            date_str = str(date).replace('-','')
            files_date = sorted(glob(os.path.join(
                os.environ['VAMPIRE_DATA'],
                'radiosondes',
                f"{date_str}*_pangaea.txt",
            )))
            files += files_date

    # get times from filenames
    times = [os.path.basename(f).split("_")[0] for f in files]
    times = pd.to_datetime(times, format="%Y%m%d%H")

    return np.array(files), np.array(times)


def read_radiosonde(date=None, file=None, index_col="height"):
    """
    Reads a single radiosonde in PANGAEA format with pandas. This is the format
    during PS144. The first 26 lines are a comment. All parameters are
    converted to SI units.

    Units (file -> output):

    - geopotential height: m
    - pressure: hPa -> Pa
    - temperature: deg C -> K
    - relative humidity: % -> 1
    - wind direction: deg
    - wind speed: m/s
    """

    if file is None:
        date = pd.Timestamp(date)
        file = os.path.join(
            os.environ["VAMPIRE_DATA"],
            "radiosondes",
            f"{date.strftime('%Y%m%d%H')}_pangaea.txt",
        )

    # find row where header ends
    with open(file, "r") as f:
        for i, line in enumerate(f):
            if line.startswith("*/"):
                header_row = i
                break

    # read data
    df = pd.read_csv(file, sep="\t", skiprows=header_row + 1, parse_dates=[1])
    df = df.drop(labels="Event ", axis=1)
    df = df.rename(
        columns={
            " Date/Time ": "time",
            " Latitude ": "lat",
            " Longitude ": "lon",
            " Altitude [m] (Geopotential height above sea...) ": "height",
            " PPPP [hPa]": "pres",
            "TTT [°C]": "temp",
            "RH [%]": "relhum",
            "dd [deg]": "wdir",
            "ff [m/s]": "wspeed",
        }
    )
    df = df.set_index(index_col)

    # change units
    df["pres"] = df["pres"] * 100  # hPa to Pa
    df["temp"] = df["temp"] + 273.15  # deg C to K
    df["relhum"] = df["relhum"] * 0.01  # % to 1

    # set unrealistic values to nan
    df.loc[df["relhum"] < 0, "relhum"] = np.nan
    
    df["q"] = met_tools.convert_rh_to_spechum(df["temp"], df["pres"], df["relhum"])

    return df


def read_radiosondes(path: str, date_range=np.array([]), wind_uv=False):
    files, _ = get_radiosondes(date_range=date_range)
    
    rs_dict = import_radiosondes_PS144_txt(files)
    launch_times = np.array([rs_dict[key]['launch_time_npdt'] for key in rs_dict.keys()]).astype('datetime64[ns]')
    
    height_bins = np.arange(0., 30000.1, 10.)
    ds_lst = []
    for file in files:
        df = read_radiosonde(file=file)
        
        df["height_bin"] = pd.cut(df.index, bins=height_bins)
        df = df.groupby("height_bin", observed=False).mean(numeric_only=True)
        df["height"] = (height_bins[1:] + height_bins[:-1]) / 2
        df = df.set_index("height")
        
        if wind_uv:
            df['u'], df['v'] = met_tools.wspeed_wdir_to_u_v(df['wspeed'], df['wdir'], convention='from')

        ds_lst.append(df.to_xarray())
    DS = xr.concat(ds_lst, dim='launch_time')
    DS = DS.assign_coords({'launch_time': (['launch_time'], launch_times)})
    
    DS['pres'] = DS.pres.interpolate_na(dim='height', method='linear', limit=int(0.05*len(DS.height)))
    iwv = np.array([met_tools.compute_IWV_q(q, pres, nan_threshold=0.05) for q, pres in zip(DS.q.values, DS.pres.values)])
    DS['IWV'] = xr.DataArray(iwv, dims=['launch_time'])
    DS['rho_v'] = met_tools.convert_rh_to_abshum(DS['temp'], DS['relhum'])
    
    return DS


def import_radiosondes_PS144_txt(files, add_info=False, add_loc_info=False):
    """
    Imports radiosonde data gathered during PS144 from Polarstern during the ArcWatch
    campaign. The Integrated Water Vapour will be computed using the saturation
    water vapour pressure according to Hyland and Wexler 1983. Measurements will be
    given in SI units.
    The radiosonde data will be stored in a dict with keys being the sonde index and
    the values are 1D arrays with shape (n_data_per_sonde,).

    Parameters:
    -----------
    files : str
            List of filename + path of the Polarstern PS131 radiosonde data (.tab) taken
            directly from the ship.
    add_info : bool
            If True, auxiliary information is added to the returned dictionary
            (i.e., operator of radiosonde, max altitude before burst).
    add_loc_info : bool
            If True, latitude and longitude position of the radiosonde at launch will be provided in
            the returned dictionary as well. The data is extracted from the radiosonde .txt file
            header.
    """

    n_sondes = len(
        files
    )  # just a preliminary assumption of the amount of radiosondes
    n_data_per_sonde = 12000  # assumption of max. time (data) points per sonde
    reftime = dt.datetime(1970, 1, 1)

    # the radiosonde dict will be structured as follows:
    # rs_dict['0'] contains all data from the first radiosonde: rs_dict['0']['temp'] contains temperature
    # rs_dict['1'] : second radiosonde, ...
    # this structure allows to have different time dimensions for each radiosonde
    rs_dict = dict()
    for k in range(n_sondes):
        rs_dict[str(k)] = {
            "height": np.full((n_data_per_sonde,), np.nan),  # in m
            "pres": np.full((n_data_per_sonde,), np.nan),  # in Pa
            "temp": np.full((n_data_per_sonde,), np.nan),  # in K
            "relhum": np.full((n_data_per_sonde,), np.nan),  # in [0,1]
            "wdir": np.full((n_data_per_sonde,), np.nan),  # in deg
            "wspeed": np.full((n_data_per_sonde,), np.nan),
        }  # in m s^-1

    # loop over files:
    for kk, file in enumerate(files):
        f_handler = open(file, "r")
        s_idx = str(kk)
        # print(file)
        mm = 0  # runs though all data points of one radiosonde and is reset to 0 for each new radiosonde
        headersize = 27  ##ignore first line of data as that is the one required during initialization
        for k, line in enumerate(f_handler):
            if k < headersize:  # to extract launch time
                lt_idx = line.find("DATE/TIME START: ")
                if lt_idx != -1:
                    rs_dict[s_idx]["launch_time_npdt"] = np.datetime64(
                        line[
                            lt_idx
                            + len("DATE_TIME START: ") : lt_idx
                            + len("DATE_TIME START: ")
                            + 19
                        ]
                    )
                    rs_dict[s_idx]["launch_time"] = rs_dict[s_idx][
                        "launch_time_npdt"
                    ].astype(
                        np.float64
                    )  # in sec since 1970-01-01 00:00:00

                if add_info:
                    op_idx = line.find(
                        "Operator: "
                    )  # person who launched the sonde
                    ma_idx = line.find(
                        "MAXIMUM ALTITUDE: "
                    )  # altitude where the balloon burst
                    if op_idx != -1:
                        rs_dict[s_idx]["op"] = line[
                            op_idx + len("Operator: ") : line.find("\n")
                        ]

                    if ma_idx != -1:
                        rs_dict[s_idx]["max_alt"] = int(
                            line[
                                ma_idx
                                + len("MAXIMUM ALTITUDE: ") : line.find("\n")
                                - 1
                            ]
                        )

                if add_loc_info:
                    lat_idx = line.find("LATITUDE: ")
                    lon_idx = line.find("LONGITUDE: ")
                    if lat_idx != -1:
                        if (
                            rs_dict[s_idx].get("ref_lat") is not None
                        ):  # if it was not already foundif my_dict.get(key_to_check) is not None
                            pass
                        else:
                            rs_dict[s_idx]["ref_lat"] = float(
                                line[
                                    lat_idx
                                    + len("LATITUDE: ") : line.find("*")
                                    - 1
                                ]
                            )

                    if lon_idx != -1:
                        if (
                            rs_dict[s_idx].get("ref_lon") is not None
                        ):  # if it was not already found
                            pass
                        else:
                            rs_dict[s_idx]["ref_lon"] = float(
                                line[
                                    lon_idx
                                    + len("LONGITUDE: ") : line.find("\n")
                                ]
                            )

            else:  # skip header
                # 	print(line)
                current_line = line.strip().split("\t")  # split by tabs

                # extract data:
                try:
                    rs_dict[s_idx]["height"][mm] = float(current_line[0])
                    rs_dict[s_idx]["pres"][mm] = float(current_line[1]) * 100.0
                    rs_dict[s_idx]["temp"][mm] = (
                        float(current_line[2]) + 273.15
                    )
                    rs_dict[s_idx]["relhum"][mm] = (
                        float(current_line[3]) * 0.01
                    )
                    rs_dict[s_idx]["wdir"][mm] = float(current_line[4])
                    rs_dict[s_idx]["wspeed"][mm] = float(current_line[5])

                except ValueError:  # then at least one measurement is missing:
                    for ix, cr in enumerate(current_line):
                        # print(current_line[9])
                        if cr == "":
                            current_line[ix] = "nan"
                    rs_dict[s_idx]["height"][mm] = float(current_line[4])
                    rs_dict[s_idx]["pres"][mm] = float(current_line[5]) * 100.0
                    rs_dict[s_idx]["temp"][mm] = (
                        float(current_line[6]) + 273.15
                    )
                    rs_dict[s_idx]["relhum"][mm] = (
                        float(current_line[7]) * 0.01
                    )
                    rs_dict[s_idx]["wdir"][mm] = float(current_line[8])
                    rs_dict[s_idx]["wspeed"][mm] = float(current_line[9])

                mm += 1

        # finally truncate unneeded data lines and compute specific humidity and IWV:
        last_nonnan = np.array(
            [
                np.where(~np.isnan(rs_dict[s_idx][key]))[0][-1] + 1
                for key in rs_dict[s_idx].keys()
                if key
                not in [
                    "launch_time",
                    "launch_time_npdt",
                    "max_alt",
                    "op",
                    "ref_lat",
                    "ref_lon",
                ]
            ]
        ).min()
        for key in rs_dict[s_idx].keys():
            if key not in [
                "launch_time",
                "launch_time_npdt",
                "op",
                "max_alt",
                "ref_lat",
                "ref_lon",
            ]:
                rs_dict[s_idx][key] = rs_dict[s_idx][key][:last_nonnan]
        rs_dict[s_idx]["relhum"][
            rs_dict[s_idx]["relhum"] < -1
        ] = np.nan  ##faulty radiosonde
        rs_dict[s_idx]["q"] = met_tools.convert_rh_to_spechum(
            rs_dict[s_idx]["temp"],
            rs_dict[s_idx]["pres"],
            rs_dict[s_idx]["relhum"],
        )

        rs_dict[s_idx]["IWV"] = met_tools.compute_IWV_q(
            rs_dict[s_idx]["q"], rs_dict[s_idx]["pres"]
        )

    return rs_dict


def import_radiosondes_PS131_txt(files, add_info=False, add_loc_info=False):
    """
    Imports radiosonde data gathered during PS131 from Polarstern during the ATWAICE
    campaign. The Integrated Water Vapour will be computed using the saturation
    water vapour pressure according to Hyland and Wexler 1983. Measurements will be
    given in SI units.
    The radiosonde data will be stored in a dict with keys being the sonde index and
    the values are 1D arrays with shape (n_data_per_sonde,).

    Parameters:
    -----------
    files : str
            List of filename + path of the Polarstern PS131 radiosonde data (.tab) taken
            directly from the ship.
    add_info : bool
            If True, auxiliary information is added to the returned dictionary
            (i.e., operator of radiosonde, max altitude before burst).
    add_loc_info : bool
            If True, latitude and longitude position of the radiosonde at launch will be provided in
            the returned dictionary as well. The data is extracted from the radiosonde .txt file
            header.
    """

    n_sondes = len(
        files
    )  # just a preliminary assumption of the amount of radiosondes
    n_data_per_sonde = 12000  # assumption of max. time (data) points per sonde
    reftime = dt.datetime(1970, 1, 1)

    # the radiosonde dict will be structured as follows:
    # rs_dict['0'] contains all data from the first radiosonde: rs_dict['0']['temp'] contains temperature
    # rs_dict['1'] : second radiosonde, ...
    # this structure allows to have different time dimensions for each radiosonde
    rs_dict = dict()
    for k in range(n_sondes):
        rs_dict[str(k)] = {
            "height": np.full((n_data_per_sonde,), np.nan),  # in m
            "pres": np.full((n_data_per_sonde,), np.nan),  # in Pa
            "temp": np.full((n_data_per_sonde,), np.nan),  # in K
            "relhum": np.full((n_data_per_sonde,), np.nan),  # in [0,1]
            "wdir": np.full((n_data_per_sonde,), np.nan),  # in deg
            "wspeed": np.full((n_data_per_sonde,), np.nan),
        }  # in m s^-1

    # loop over files:
    for kk, file in enumerate(files):
        f_handler = open(file, "r")
        s_idx = str(kk)

        mm = 0  # runs though all data points of one radiosonde and is reset to 0 for each new radiosonde
        headersize = 16
        for k, line in enumerate(f_handler):
            if k < headersize:  # to extract launch time
                lt_idx = line.find("DATE/TIME START: ")
                if lt_idx != -1:
                    rs_dict[s_idx]["launch_time_npdt"] = np.datetime64(
                        line[
                            lt_idx
                            + len("DATE_TIME START: ") : lt_idx
                            + len("DATE_TIME START: ")
                            + 19
                        ]
                    )
                    rs_dict[s_idx]["launch_time"] = rs_dict[s_idx][
                        "launch_time_npdt"
                    ].astype(
                        np.float64
                    )  # in sec since 1970-01-01 00:00:00

                if add_info:
                    op_idx = line.find(
                        "Operator: "
                    )  # person who launched the sonde
                    ma_idx = line.find(
                        "MAXIMUM ALTITUDE: "
                    )  # altitude where the balloon burst
                    if op_idx != -1:
                        rs_dict[s_idx]["op"] = line[
                            op_idx + len("Operator: ") : line.find("\n")
                        ]

                    if ma_idx != -1:
                        rs_dict[s_idx]["max_alt"] = int(
                            line[
                                ma_idx
                                + len("MAXIMUM ALTITUDE: ") : line.find("\n")
                                - 1
                            ]
                        )

                if add_loc_info:
                    lat_idx = line.find("LATITUDE: ")
                    lon_idx = line.find("LONGITUDE: ")
                    if lat_idx != -1:
                        rs_dict[s_idx]["ref_lat"] = float(
                            line[
                                lat_idx
                                + len("LATITUDE: ") : line.find("*")
                                - 1
                            ]
                        )

                    if lon_idx != -1:
                        rs_dict[s_idx]["ref_lon"] = float(
                            line[
                                lon_idx + len("LONGITUDE: ") : line.find("\n")
                            ]
                        )

            else:  # skip header
                current_line = line.strip().split("\t")  # split by tabs

                # extract data:
                try:
                    rs_dict[s_idx]["height"][mm] = float(current_line[0])
                    rs_dict[s_idx]["pres"][mm] = float(current_line[1]) * 100.0
                    rs_dict[s_idx]["temp"][mm] = (
                        float(current_line[2]) + 273.15
                    )
                    rs_dict[s_idx]["relhum"][mm] = (
                        float(current_line[3]) * 0.01
                    )
                    rs_dict[s_idx]["wdir"][mm] = float(current_line[4])
                    rs_dict[s_idx]["wspeed"][mm] = float(current_line[5])

                except ValueError:  # then at least one measurement is missing:
                    for ix, cr in enumerate(current_line):
                        if cr == "":
                            current_line[ix] = "nan"
                    rs_dict[s_idx]["height"][mm] = float(current_line[0])
                    rs_dict[s_idx]["pres"][mm] = float(current_line[1]) * 100.0
                    rs_dict[s_idx]["temp"][mm] = (
                        float(current_line[2]) + 273.15
                    )
                    rs_dict[s_idx]["relhum"][mm] = (
                        float(current_line[3]) * 0.01
                    )
                    rs_dict[s_idx]["wdir"][mm] = float(current_line[4])
                    rs_dict[s_idx]["wspeed"][mm] = float(current_line[5])

                mm += 1

        # finally truncate unneeded data lines and compute specific humidity and IWV:
        last_nonnan = np.array(
            [
                np.where(~np.isnan(rs_dict[s_idx][key]))[0][-1] + 1
                for key in rs_dict[s_idx].keys()
                if key
                not in [
                    "launch_time",
                    "launch_time_npdt",
                    "max_alt",
                    "op",
                    "ref_lat",
                    "ref_lon",
                ]
            ]
        ).min()
        for key in rs_dict[s_idx].keys():
            if key not in [
                "launch_time",
                "launch_time_npdt",
                "op",
                "max_alt",
                "ref_lat",
                "ref_lon",
            ]:
                rs_dict[s_idx][key] = rs_dict[s_idx][key][:last_nonnan]
        rs_dict[s_idx]["q"] = met_tools.convert_rh_to_spechum(
            rs_dict[s_idx]["temp"],
            rs_dict[s_idx]["pres"],
            rs_dict[s_idx]["relhum"],
        )

        rs_dict[s_idx]["IWV"] = met_tools.compute_IWV_q(
            rs_dict[s_idx]["q"], rs_dict[s_idx]["pres"]
        )

    return rs_dict


def radiosonde_dict_to_dataset(rs_data: dict, vert_interp='avg'):
    
    height = np.arange(0., 20000.1, 10.)
    n_sondes = len(rs_data.keys())
    n_height = len(height)
    vars = ['pres', 'temp', 'relhum', 'wdir', 'wspeed', 'q', 'IWV']
    
    launch_times = np.array([rs_data[key]['launch_time_npdt'] for key in rs_data.keys()]).astype('datetime64[ns]')
    
    DS = xr.Dataset(coords={'time': (['time'], launch_times),
                            'height': (['height'], height)})
    for var in vars:
        if var not in ["IWV"]:
            DS[var] = xr.DataArray(np.full((n_sondes, n_height), np.nan),
                                dims=['time', 'height'])
        else:
            DS[var] = xr.DataArray(np.full((n_sondes,), np.nan),
                                dims=['time'])
    
    for k, key in enumerate(rs_data.keys()):
        for var in vars:
            if var not in ['IWV']:
                DS[var][k,...] = data_tools.vertical_interpolation(height, rs_data[key]['height'], rs_data[key][var],
                                                                   vert_interp)
            else:
                DS[var][k] = rs_data[key][var]
                
    return DS


def import_radiosondes_MOSAIC_blendedprofiles_txt(files, add_loc_info=False):
    """
    Imports blended radiosonde data from Polarstern gathered during the MOSAiC
    campaign. The Integrated Water Vapour will be computed using the saturation
    water vapour pressure according to Hyland and Wexler 1983. Measurements will be
    given in SI units.
    The radiosonde data will be stored in a dict with keys being the sonde index and
    the values are 1D arrays with shape (n_data_per_sonde,).

    Parameters:
    -----------
    files : str
            List of filename + path of the radiosonde data from the Blended Profile product (Dahlke et al)

    add_loc_info : bool
            If True, latitude and longitude position of the radiosonde at launch will be provided in
            the returned dictionary as well. The data is extracted from the radiosonde .txt file
            header.
    """

    n_sondes = len(
        files
    )  # just a preliminary assumption of the amount of radiosondes
    n_data_per_sonde = 12000  # assumption of max. time (data) points per sonde
    reftime = dt.datetime(1970, 1, 1)

    # the radiosonde dict will be structured as follows:
    # rs_dict['0'] contains all data from the first radiosonde: rs_dict['0']['temp'] contains temperature
    # rs_dict['1'] : second radiosonde, ...
    # this structure allows to have different time dimensions for each radiosonde
    rs_dict = dict()
    for k in range(n_sondes):
        rs_dict[str(k)] = {
            "height": np.full((n_data_per_sonde,), np.nan),  # in m
            "pres": np.full((n_data_per_sonde,), np.nan),  # in Pa
            "temp": np.full((n_data_per_sonde,), np.nan),  # in K
            "relhum": np.full((n_data_per_sonde,), np.nan),  # in [0,1]
            "wdir": np.full((n_data_per_sonde,), np.nan),  # in deg
            "wspeed": np.full((n_data_per_sonde,), np.nan),
        }  # in m s^-1

    # loop over files:
    for kk, file in enumerate(files):
        f_handler = open(file, "r")
        s_idx = str(kk)

        mm = 0  # runs though all data points of one radiosonde and is reset to 0 for each new radiosonde
        headersize = 21
        for k, line in enumerate(f_handler):
            if k < headersize:  # to extract launch time
                lt_idx = line.find("Radiosonde launch: ")
                if lt_idx != -1:
                    rs_dict[s_idx]["launch_time_npdt"] = np.datetime64(
                        line[
                            lt_idx
                            + len("Radiosonde launch: ") : lt_idx
                            + len("Radiosonde launch: ")
                            + 19
                        ]
                    )
                    # print(rs_dict[s_idx]['launch_time_npdt'] )
                    rs_dict[s_idx]["launch_time"] = rs_dict[s_idx][
                        "launch_time_npdt"
                    ].astype(
                        np.float64
                    )  # in sec since 1970-01-01 00:00:00

                # if add_info:
                # 	op_idx = line.find("Operator: ")			# person who launched the sonde
                # 	ma_idx = line.find("MAXIMUM ALTITUDE: ")	# altitude where the balloon burst
                # 	if op_idx != -1:
                # 		rs_dict[s_idx]['op'] = line[op_idx+len("Operator: "):line.find("\n")]

                # 	if ma_idx != -1:
                # 		rs_dict[s_idx]['max_alt'] = int(line[ma_idx+len("MAXIMUM ALTITUDE: "):line.find("\n")-1])
                # this will probably not work with blended profiles
                if add_loc_info:
                    lat_idx = line.find("LATITUDE: ")
                    lon_idx = line.find("LONGITUDE: ")
                    if lat_idx != -1:
                        rs_dict[s_idx]["ref_lat"] = float(
                            line[
                                lat_idx
                                + len("LATITUDE: ") : line.find("*")
                                - 1
                            ]
                        )

                    if lon_idx != -1:
                        rs_dict[s_idx]["ref_lon"] = float(
                            line[
                                lon_idx + len("LONGITUDE: ") : line.find("\n")
                            ]
                        )

            else:  # skip header
                current_line = line.strip().split("\t")  # split by tabs
                # 	print(current_line)
                # extract data:
                ## set fillvalue (-9999) to nan

                # format is 'Date/Time[UTC] Altitude[m] Pressure[hPa] latitude[degrees N] longitude[degrees E] Temperature[degC] Temperature_FLAG[] Relative humidity[percent] Relative Humidity_FLAG[] Wind speed[m/s] Wind direction[degrees]'
                try:
                    if (
                        current_line[2] != "-9999"
                    ):  ##if there is pressure data (take only data where is is that)
                        rs_dict[s_idx]["height"][mm] = (
                            float(current_line[1])
                            if current_line[1] != "-9999"
                            else np.nan
                        )
                        rs_dict[s_idx]["pres"][mm] = (
                            float(current_line[2]) * 100.0
                            if current_line[2] != "-9999"
                            else np.nan
                        )
                        rs_dict[s_idx]["temp"][mm] = (
                            float(current_line[5]) + 273.15
                            if current_line[5] != "-9999"
                            else np.nan
                        )
                        rs_dict[s_idx]["relhum"][mm] = (
                            float(current_line[7]) * 0.01
                            if current_line[7] != "-9999"
                            else np.nan
                        )
                        rs_dict[s_idx]["wdir"][mm] = (
                            float(current_line[9])
                            if current_line[10] != "-9999"
                            else np.nan
                        )
                        rs_dict[s_idx]["wspeed"][mm] = (
                            float(current_line[8])
                            if current_line[9] != "-9999"
                            else np.nan
                        )
                    else:
                        # 		print("pressure data nan", mm)
                        mm -= 1  ##to avoid a line of nans
                        pass
                except ValueError:  # then at least one measurement is missing:
                    for ix, cr in enumerate(current_line):
                        if cr == "":
                            current_line[ix] = "nan"
                    if (
                        current_line[2] != "nan"
                    ):  ##if there is pressure data (take only data where is is that)
                        rs_dict[s_idx]["height"][mm] = (
                            float(current_line[1])
                            if current_line[1] != "-9999"
                            else np.nan
                        )
                        rs_dict[s_idx]["pres"][mm] = (
                            float(current_line[2]) * 100.0
                            if current_line[2] != "-9999"
                            else np.nan
                        )
                        rs_dict[s_idx]["temp"][mm] = (
                            float(current_line[5]) + 273.15
                            if current_line[5] != "-9999"
                            else np.nan
                        )
                        rs_dict[s_idx]["relhum"][mm] = (
                            float(current_line[7]) * 0.01
                            if current_line[7] != "-9999"
                            else np.nan
                        )
                        rs_dict[s_idx]["wdir"][mm] = (
                            float(current_line[9])
                            if current_line[10] != "-9999"
                            else np.nan
                        )
                        rs_dict[s_idx]["wspeed"][mm] = (
                            float(current_line[8])
                            if current_line[9] != "-9999"
                            else np.nan
                        )
                    else:
                        mm -= 1
                        pass

                mm += 1
        # finally truncate unneeded data lines and compute specific humidity and IWV:

        last_nonnan = np.array(
            [
                np.where(~np.isnan(rs_dict[s_idx][key]))[0][-1] + 1
                for key in rs_dict[s_idx].keys()
                if key
                not in [
                    "launch_time",
                    "launch_time_npdt",
                    "max_alt",
                    "op",
                    "ref_lat",
                    "ref_lon",
                ]
            ]
        ).min()
        for key in rs_dict[s_idx].keys():
            if key not in [
                "launch_time",
                "launch_time_npdt",
                "op",
                "max_alt",
                "ref_lat",
                "ref_lon",
            ]:
                rs_dict[s_idx][key] = rs_dict[s_idx][key][:last_nonnan]

        rs_dict[s_idx]["q"] = met_tools.convert_rh_to_spechum(
            rs_dict[s_idx]["temp"],
            rs_dict[s_idx]["pres"],
            rs_dict[s_idx]["relhum"],
        )

        rs_dict[s_idx]["IWV"] = met_tools.compute_IWV_q(
            rs_dict[s_idx]["q"], rs_dict[s_idx]["pres"], nan_threshold=0.05
        )

    return rs_dict
