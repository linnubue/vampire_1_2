import pyPamtra
import numpy as np
import os
import pdb
import multiprocessing
import datetime as dt

def run_pamtra_run(
    sonde_dict: dict, 
    freqs: np.ndarray,
    path_output: str, 
    lon=0.,
    lat=50.,
    rs_wind=False,
    obs_height=np.array([0.]),
    site='pippo'):

    """
    This function sets PAMTRA's settings and takes radiosonde data to simulate
    brightness temperatures out of radiosonde data with certain settings (i.e., 
    salinity, sea surface temperature, elevation angle, ...).

    Parameters:
    -----------
    sonde_dict : dict
        Dictionary of radiosonde data. 'temp' for temperature in K, 'pres' for pressure in Pa,
        'relhum' in %, wind data in U and V direction in m s-1.
    freqs : np.ndarray
        Frequencies in GHz to simulate.
    path_output : str
        Full path where simulations should be saved to.
    lon : float
        (Dummy) Reference longitude in deg east in case none is provided in the radiosonde data.
    lat : float
        (Dummy) Reference latitude in deg north in case none is provided in the radiosonde data.
    rs_wind : bool
        If True: wind data from radiosondes will be included. Otherwise, wind will be set to 0.
    obs_height : np.ndarray of floats
        Height of radiosonde launch in m.
    site : str
        Name of the campaign / site of the radiosonde data.

    Output:
    -------
    pam : pam object
        Pam object in which simulated brightness temperatures can be found.
    """

    lt_string = dt.datetime.strptime(str(sonde_dict['launch_time_npdt'].astype('datetime64[s]')),
                                     "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d_%H%M%SZ")
    print(lt_string)

    # create pam object:
    pam = pyPamtra.pyPamtra()


    # general settings:
    pam.nmlSet['passive'] = True                        # passive simulation
    pam.nmlSet['active'] = False                        # False: no radar
    pam.nmlSet['creator'] = "awalbroe"

    # define the pamtra profile: temp, relhum, pres, height, lat, lon, timestamp, lfrac, obs_height, ...
    pamData = dict()
    shape2d = (1,1)

    if ('ref_lon' in sonde_dict.keys()) and ('ref_lat' in sonde_dict.keys()):
        pamData['lon'] = np.broadcast_to(sonde_dict['ref_lon'], shape2d)
        pamData['lat'] = np.broadcast_to(sonde_dict['ref_lat'], shape2d)
    else:
        pamData['lon'] = np.broadcast_to(np.array([lon]), shape2d)
        pamData['lat'] = np.broadcast_to(np.array([lat]), shape2d)
    pamData['timestamp'] = np.broadcast_to(sonde_dict['launch_time'].astype('datetime64[s]').astype('float'), shape2d)


    # surface properties: first, over ocean. Then, distinguish between sea ice and open ocean:
    pamData['sfc_type'] = np.zeros(shape2d)
    pamData['sfc_model'] = np.zeros(shape2d)
    pamData['sfc_refl'] = np.chararray(shape2d,unicode=True)
    pamData['sfc_refl'][:] = "F"
    # pamData['sfc_salinity'] = np.broadcast_to(set_dict['salinity'], shape2d)      # in PSU

    pamData['sfc_sif'] = np.broadcast_to(sonde_dict['siconc'], shape2d)
    ice_idx = (pamData['sfc_sif'] > 0.05)
    pamData['sfc_type'][ice_idx] = 1
    pamData['sfc_model'][ice_idx] = 0
    pamData['sfc_refl'][ice_idx] = "L"


    pamData['obs_height'] = np.broadcast_to(obs_height, shape2d + (len(obs_height), ))
    

    # make sure relative humidity doesn't exceed sensible values:
    if np.any(sonde_dict['relhum'] > 100.0): pdb.set_trace()
    sonde_dict['relhum'][sonde_dict['relhum'] > 100.0] = 100.0
    sonde_dict['relhum'][sonde_dict['relhum'] < 0.0] = 0.0


    # put meteo data into pamData:
    shape3d = (1,1,len(sonde_dict['height']))
    pamData['hgt_lev'] = sonde_dict['height']               # level specification (instead of layer) in m
    pamData['relhum_lev'] = np.broadcast_to(sonde_dict['relhum'], shape3d)  # in %
    pamData['press_lev'] = np.broadcast_to(sonde_dict['pres'], shape3d)     # in Pa
    pamData['temp_lev'] = np.broadcast_to(sonde_dict['temp'], shape3d)      # in K

    # Surface winds (over ocean: use them; over ice: do not)
    if rs_wind:
        pamData['wind10u'] = np.reshape(sonde_dict['u'][0], shape2d)
        pamData['wind10v'] = np.reshape(sonde_dict['v'][0], shape2d)
    else:
        pamData['wind10u'] = np.reshape(np.array([0.]), shape2d)
        pamData['wind10v'] = np.reshape(np.array([0.]), shape2d)
    pamData['wind10u'][ice_idx] = 0.0
    pamData['wind10v'][ice_idx] = 0.0
    pamData['groundtemp'] = np.reshape(sonde_dict['skt'], shape2d)


    # 4d variables: hydrometeors:
    # with hydrometeors computed from cwp, iwp, rwp and swp of the testcase:
    # LWP will later be replaced by modified adiabatic computation in clouds
    # detected via 95 % rel. humidity (see /Notes/Miscallaneous/MiRAC-P_retrieval.txt).
    cwc = 0                 # cloud water content
    iwc = 0                 # ice water content
    rwc = 0                 # rain water content
    swc = 0                 # snow water content

    shape4d_lay = [1, 1, len(pamData['hgt_lev'])-1, 4]
    shape3d_lay = [1, 1, len(pamData['hgt_lev'])-1]
    pamData['hydro_q'] = np.zeros(shape4d_lay)
    # pamData["hydro_q"][:,:,:,0] = cwc

    pam.df.readFile("/home/tenweg/pamtra/descriptorfiles/descriptor_file_ecmwf.txt")

    # create pamtra profile from pamData and run pamtra at all specified frequencies:
    pam.createProfile(**pamData)
    n_cpus = int(multiprocessing.cpu_count()*0.65)      # number of available CPUs * some fractional factor
    pam.runParallelPamtra(freqs, pp_deltaX=0, pp_deltaY=0, pp_deltaF=1, pp_local_workers=n_cpus)

    os.makedirs(path_output, exist_ok=True)
    filename_out = path_output + f"{site}_radiosonde_pam_out_{lt_string}.nc"
    pam.writeResultsToNetCDF(filename_out, xarrayCompatibleOutput=True, ncCompression=True)

    return pam