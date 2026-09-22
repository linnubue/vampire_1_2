###!/usr/bin/env python
"""
| *author*: Linnu Bühler
| *created*: 26.11.2024

Convert shipmotion csv file to a netcdf file
"""

# %% import modules
import pandas as pd
import datetime as dt
import pytz
import calendar

# %% set date and time
day = '13'
month = '09'
year  = '24'
time = '06'

# %% set paths
data_path = ''
output_path = ''
filename = 'shipmotion_PS144.csv' #'heaveroll_%s%s%s.dat'%(day,month,year)

# %% read in data
df = pd.read_csv(f'{data_path}/{filename}', sep='\t', header=2, parse_dates=True,encoding='unicode_escape')

# %% clean data
#df = df.drop(columns=['Benutzer-ID', 'Anzeigename des Nutzers'])
# convert to long format
#df = pd.melt(df, id_vars='Zeitstempel', var_name='question', value_name='answer')
df['datetime'], df['timestamp'] = pd.Series(), pd.Series()

df = df.rename(columns={"Unnamed: 0": "time"})
df = df.rename(columns={"m": "heave"})
df = df.rename(columns={"°": "roll"})
for i in range(0,len(df['time'])):
    try:
        df.loc[i, 'datetime'] = dt.datetime.strptime(df['time'][i], '%Y/%m/%d %H:%M:%S.%f')
        #dataset.loc[i, 'timestamp'] = dt.datetime.strptime(dataset['time'][i], '%Y/%m/%d %H:%M:%S.%f').timestamp()
        df.loc[i, 'timestamp'] = calendar.timegm(pd.Timestamp(df['time'][i], tzinfo=pytz.utc).timetuple())
    except ValueError:
        continue
df.set_index('datetime', inplace=True)
#df['index1'] = df.index


# %% convert to netcdf
ds = df.to_xarray()
#ds = ds.rename(index='id')
ds['datetime'] = ds['datetime'].astype('datetime64[ns]')
ds['datetime'] = ds['datetime'].values.astype('datetime64[s]') #.astype('int')
ds['roll'].attrs = dict(units='°')
ds['datetime'].attrs = dict(units='seconds since 1970-01-01')
ds['heave'].attrs = dict(units='m')

ds.attrs = dict(
    title='Ship motions on research vessel Polarstern on %s%s%s'%(year,month,day),
    author='Linnu Bühler, l.buehler@uni-koeln.de',
    institution='University of Cologne, Germany',
    created=f'{dt.datetime.now(dt.UTC):%c UTC}',
    licence='CC-BY 4.0',

)

# %% save to netCDF
ds.to_netcdf(f'{output_path}/shipmotion_%s%s%s.nc'%(year,month,day)) #, encoding=dict(time=dict(units='seconds since 1970-01-01')))
