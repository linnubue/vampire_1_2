import os
import datetime as dt
import pdb

import xarray as xr
import numpy as np

from vampire.analysis.data_tools import encode_time

campaign = "VAMPIRE2"
if campaign == "vampire":
    from vampire.constants import Constants as Constants
elif campaign == 'VAMPIRE2':
    from vampire.constants import Constants_PS149 as Constants


script_name = os.path.basename(__file__)

mwr_name_long = {'hatpro': "RPG-HATPRO-G5",
                 'mirac-p': "RPG-LHUMPRO-243-340-G5"}

def main():
    
    path_data = os.environ['VAMPIRE_DATA'] + "CSC/offsets/"
    path_output = os.environ['VAMPIRE_DATA'] + "CSC/offsets/for_publication/"
    
    instruments = ['hatpro', 'mirac-p']
    for instrument in instruments:
        DS = load_tb_offset_file(path=path_data, instrument=instrument)
        DS = post_process_tb_offset_data(DS=DS, instrument=instrument)
        export_tb_offset_data(DS, path_output)
    
    
def load_tb_offset_file(
    path=os.environ['VAMPIRE_DATA'] + "CSC/offsets/",
    instrument='hatpro'):
    
    filename = f"{Constants.CAMPAIGN_NAME}_{instrument}_radiometer_clear_sky_offset_correction.nc"
    DS = xr.open_dataset(path + filename).load()
    
    return DS


def post_process_tb_offset_data(DS: xr.Dataset, instrument='hatpro'):
    
    DS = update_attrs(DS, instrument)
    DS['n_samp'] = DS.n_samp.astype(np.int32)
    DS = improve_time_dim(DS)
    
    return DS


def update_attrs(DS: xr.Dataset, instrument='hatpro'):
    
    attrs_old = DS.attrs
    if 'contact_persion' in attrs_old.keys():
        attrs_old['contact_person'] = attrs_old['contact_persion']
        del attrs_old['contact_persion']
    
    attrs_new = {'title': (f"Brightness temperature corrections for {mwr_name_long[instrument]} " +
                           f"for Polarstern cruise {Constants.CAMPAIGN_NAME}")}
    
    for key in ['institution', 'contact_person', 'author', 'license', 'history', 'instrument']:
        attrs_new[key] = attrs_old[key]
    attrs_new['Convention'] = "1.13"
    
    attrs_new_keys = attrs_new.keys()
    for key in attrs_old.keys():
        if key not in attrs_new_keys:
            attrs_new[key] = attrs_old[key]
    
    attrs_new['license'] = "CC BY-NC 4.0"
    attrs_new['description'] = attrs_new['description'].replace("observed (obs)brightness",
                                                                "observed (obs) brightness")
    DS.attrs = attrs_new
    
    for var in ['slope', 'n_samp']:
        DS[var].attrs['units'] = "1"
    DS['n_samp'].attrs['comment'] = "If n_samp is 0, no offset/slope/bias could be computed for this calibration cycle"
    
    return DS


def improve_time_dim(DS: xr.Dataset):
    
    DS = DS.rename_dims({'time': 'calibration_cycle'})
    
    for var in ['calibration_period_start', 'calibration_period_end']:
        var_values = DS[var].values
        DS = DS.drop_vars(var)
        DS[var] = xr.DataArray(var_values, dims=['calibration_cycle'])
    
    return DS


def export_tb_offset_data(
    DS: xr.Dataset, 
    path_output=os.environ['VAMPIRE_DATA'] + "CSC/offsets/for_publication/"):
    
    attr_add = ""
    if ";" not in DS.attrs['history'][-2:]:
        attr_add = "; "
    DS.attrs['history'] += (f"{attr_add}{dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}" +
                            f", improved meta data to comply with CF conventions with {script_name}; ")
    
    for var in ['calibration_period_start', 'calibration_period_end']:
        DS = encode_time(DS,
                         time_var=var, 
                         time_dim='calibration_cycle', 
                         reference_period=np.datetime64("2020-01-01T00:00:00"))
        DS[var].attrs['calendar'] = "proleptic_gregorian"

    filename = os.path.basename(DS.encoding['source'])
    file_save = path_output + filename
    
    os.makedirs(path_output, exist_ok=True)
    DS.to_netcdf(file_save, mode='w', format="NETCDF4")
    DS = DS.close()
    print(f"Saved {file_save}")
    

if __name__ == '__main__':
    main()