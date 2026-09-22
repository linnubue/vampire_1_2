import os
import glob
import pdb

import xarray as xr
import numpy as np

from vampire.analysis.data_tools import write_basic_attributes, encode_time, update_netCDF_file_history


def main():
    
    path_data = os.path.join(os.environ['VAMPIRE_DATA'],
                             "flir/time_series/")
    path_output = os.path.join(os.environ['VAMPIRE_DATA'],
                               "flir/time_series/for_publication/")
    
    os.makedirs(path_output, exist_ok=True)
    
    files = get_flir_time_series_files(path_data, campaign_name=Constants.CAMPAIGN_NAME)
    for file in files:
        process_time_series_file(file, path_output, Constants.CAMPAIGN_NAME)

    
def process_time_series_file(
    file: str, 
    path_output: str,
    campaign_name='PS144'):
    
    ds = xr.open_dataset(file).load()
    ds = improve_variable_metadata(ds)
    ds = improve_global_metadata(ds, campaign_name)
    
    export_ds(ds, path_output, campaign_name)

 
def improve_variable_metadata(ds: xr.Dataset):
    
    ds['video'].attrs = {'long_name': "video number of the FLIR recording",
                         'units': "1"}
    ds['frame'].attrs = {'long_name': "FLIR image frame number for a given video",
                         'units': "1"}
    
    for var in ['tb_center', 'tb_mean', 'tb_min', 'tb_max']:
        ds[var].attrs = {'standard_name': "brightness_temperature",
                         'units': "K"}
    ds['tb_center'].attrs['long_name'] = "brightness temperature in the centre of a FLIR image"
    ds['tb_mean'].attrs['long_name'] = "mean brightness temperature of a FLIR image"
    ds['tb_min'].attrs['long_name'] = "minimum brightness temperature of a FLIR image"
    ds['tb_max'].attrs['long_name'] = "maximum brightness temperature of a FLIR image"
    ds['tb_std'].attrs = {'long_name': "standard deviation of the brightness temperature of a FLIR image",
                          'units': "K"}
    
    ds['tb_bin'].attrs = {'long_name': "brightness temperature bin centres for histogram",
                          'units': "K"}
    ds['hist'].attrs = {'long_name': 'brightness temperature histogram',
                        'comment': "count of brightness temperature values within bins",
                        'units': "1"}
    
    return ds


def improve_global_metadata(ds: xr.Dataset, campaign_name='PS144'):
    
    del ds.attrs['description'], ds.attrs['comment'], ds.attrs['history']
    
    ds.attrs['title'] = f"FLIR A315 infrared camera brightness temperature statistics for Polarstern expedition {campaign_name}"
    ds.attrs['institution'] = "Institute for Geophysics and Meteorology, University of Cologne, Cologne, Germany"
    ds.attrs['contact'] = "Andreas Walbroel (a.walbroel@uni-koeln.de, https://orcid.org/0000-0003-2603-2724)"
    ds.attrs['author'] = "Nils Risse, Andreas Walbröl"
    ds.attrs['licence'] = "CC BY-NC 4.0, https://creativecommons.org/licenses/by-nc/4.0/"
    ds.attrs['history'] = "2026-03-12 09:14:11, calculated statistics and created daily files with flir.py; "
    ds = update_netCDF_file_history(ds, os.path.basename(__file__),
                                    "refined metadata with")
    ds.attrs['comment'] = (f"uncorrected brightness temperatures, please use {campaign_name}_flir_tb_offset_correction.nc " +
                           "for correction")
    
    ds.attrs['measurement_site'] = "Arctic Ocean, RV Polarstern"
    ds.attrs['time_start'] = str(ds.time.values[0].astype('datetime64[s]')).replace("T", " ") + "Z"
    ds.attrs['time_end'] = str(ds.time.values[-1].astype('datetime64[s]')).replace("T", " ") + "Z"
    ds.attrs['project'] = ("DFG (German Research Foundation) project number 268020496 - TRR 172, " +
                           "Transregional Collaborative Research Center 'ArctiC Amplification: " +
                           "Climate Relevant Atmospheric and SurfaCe Processes, and Feedback Mechanisms (AC)3'")
    ds.attrs['Conventions'] = "CF-1.13"
    
    return ds


def export_ds(ds: xr.Dataset, path_output: str, campaign_name="PS144"):
    
    date_str = str((ds.time.values[0] + 0.5*(ds.time.values[-1] - ds.time.values[0])).astype('datetime64[D]'))
    
    ds = encode_time(ds, reference_period=np.datetime64("2024-01-01T00:00:00"))
    for var in ds.coords:
        ds[var].encoding['_FillValue'] = None
    
    filename = f"{campaign_name}_flir_tb_statistics_{date_str.replace('-','')}"
    outfile = os.path.join(path_output, filename + ".nc")
    ds.to_netcdf(outfile, mode='w', format="NETCDF4")
    ds = ds.close()
    print(f"Saved {outfile}....")


def get_flir_time_series_files(path: str, campaign_name="PS144"):
    
    if campaign_name == 'PS144':
        campaign_label = "VAMPIRE"
    elif campaign_name == 'PS149':
        campaign_label = "VAMPIRE2"
    
    return sorted(glob.glob(path + f"{campaign_label}_flir_statistics_*.nc"))


if __name__ == '__main__':
    campaign = "vampire"
    if campaign == "vampire":
        from vampire.constants import Constants as Constants
    elif campaign == 'VAMPIRE2':
        from vampire.constants import Constants_PS149 as Constants
    
    
    main()