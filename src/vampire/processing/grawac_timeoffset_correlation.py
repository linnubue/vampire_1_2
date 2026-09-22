import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import glob
import datetime as dt
import matplotlib.dates as md
import os
import pandas as pd
from datetime import datetime
from scipy import signal
import calendar
import pytz

#hydrins = xr.open_dataset('shipmotion_PS149.nc')

plotpath = ''

date_start = pd.Timestamp('2025-07-02')
#date_end = pd.Timestamp('2024-09-01')
#date_end = pd.Timestamp(dt.date.today())
date_end = pd.Timestamp('2025-08-30')
dates = pd.date_range(date_start, date_end, freq="1D")
df = {}
df['time'], df['shift_grawac_roll_COM'], df['shift_grawac_roll_hydrins'] = [], [], []

#for PS149 vampire2
for date in dates:
    day = str(date).split(' ')[0].split('-')[2]
    month = str(date).split('-')[1]
    datapath = '/path/to/data/grawac/'

    for hour in range(0,24):
        hourr, hour2, day2, month2 = str(hour).zfill(2), str(hour+1).zfill(2), day, month
        if hour==23:
            hour2, day2 = '00', str(int(day)+1).zfill(2)
            if (month=='08' and day== '31') or (month=='09' and day=='30') or (month=='07' and day=='31'):
                day2, month2 = str('01'), str(int(month)+1).zfill(2)
        print(month,day,hourr,month2,day2,hour2)

        #hydrins is data downloaded from DShip
        hydrins = xr.open_dataset('shipmotion_PS149.nc')
        hydrins = hydrins.sortby('datetime')
        hydrnew = hydrins.sel(datetime=slice("2025-%s-%sT%s:00:00"%(month,day,hour), "2025-%s-%sT%s:00:00"%(month2,day2,hour2)))
        hydrins = hydrnew.where(hydrnew>-100) #remove nans

        #select only where roll is strong enough to make useful correlation, leads to wrong results when roll is too small
        if len(hydrins['roll'])>0:
            if np.max(abs(hydrins['roll']))>1:

                #read grawac radar files
                gfiles = sorted(glob.glob(datapath+'2025/%s/%s/grawac_2025%s%s_%s*lv1.NC'%(month,day,month,day,hourr)))

                if len(gfiles) == 0: continue
                print(date, hour)
                grawacrpg = xr.open_dataset(gfiles[0])
                elax = grawacrpg.Inc_ElA+1.23 #add 1.23 to reducce offset between the two roll measurements
                elax2 = grawacrpg.Inc_ElA+0.6 #same for hydrins. why are roll of COM-port ship and hydrins different? should be the same data
                elax, elax2 = elax.rename({'Time': 'time'}), elax2.rename({'Time': 'time'})
                elax["time"], elax2["time"] = np.datetime64("2001-01-01").astype("datetime64[ns]") + elax["time"].values.astype("timedelta64[s]").astype("timedelta64[ns]"), np.datetime64("2001-01-01").astype("datetime64[ns]") + elax2["time"].values.astype("timedelta64[s]").astype("timedelta64[ns]")
                elax["time"].encoding, elax2["time"].encoding = {"units": "seconds since 2001-01-01 00:00:00"}, {"units": "seconds since 2001-01-01 00:00:00"}
                elint2 = elax2.drop_duplicates(dim='time').interp(time=hydrins['datetime'], method='linear')

                #for hydrins data from DShip
                el2 = elint2.sel(datetime=slice(elax['time'][0],elax['time'][-1]))
                hy = hydrins.sel(datetime=slice(elax['time'][0],elax['time'][-1]))
                
                hydrinscorr = signal.correlate(hy['roll'], el2, mode='full', method='direct')
                lagsroll2 = signal.correlation_lags(hy['roll'].size, el2.size, mode='full')
                lagroll2 = lagsroll2[np.argmax(abs(hydrinscorr))]
                hydrinscorr /= np.max(abs(hydrinscorr))
                print(lagroll2/20)

                #plot correlation function
                fig, ax = plt.subplots(nrows=1, sharex=True)
                fig.suptitle('%s.%s.2025 %s UTC shiftroll=%s sec'%(day, month, hour, lagroll2/20))
                ax.plot(lagsroll2/20, hydrinscorr, "o", markersize=1, label='roll', c='b')
                plt.xlabel('shift in sec')
                plt.savefig(plotpath+'correlation_roll_vampire_%s%s_%s.png'%(month,day,hour),dpi=300)
                print('first plot saved')

                #plot original and shifted roll grawac compared to measured ship roll
                fmt = md.DateFormatter('%H:%M:%S')
                fig, ax = plt.subplots(nrows=1, sharex=True, figsize=(15, 7))
                fig.suptitle('%s.%s.2025 %s UTC shiftroll=%s'%(day, month, hour, lagroll2/20))
                ax.plot(el2['time'], el2.values, "o", ms=1, c='b', label='roll grawac')
                #ax.plot(ds['time'], ds['roll'], "o", ms=1, c='r', label='roll ship')
                #ax.plot(el['time'], el2.shift(time=lagroll), "o", ms=1, c='darkorchid', label='roll grawac shifted')
                ax.plot(hy['datetime'], hy['roll'], "o", ms=1, c='g', label='roll hydrins')
                ax.plot(el2['time'], el2.shift(datetime=lagroll2), "o", ms=1, c='turquoise', label='roll grawac shifted hydrins')
                ax.legend()
                ax.set_ylabel('roll [°]')
                ax.xaxis.set_major_formatter(fmt)
                ax.set_xlabel('Time UTC')
                ax.set_xlim(dt.datetime(2025,int(month),int(day),int(hour)), dt.datetime(2025,int(month2),int(day2),int(hour2)))
                fig.savefig(plotpath+'hydrins_zoomed_shiftedbyroll_%s%s_%s.png'%(month,day,hour),dpi=300)

                df['time'] = np.append(df['time'], date + dt.timedelta(hours=hour))
                df['shift_grawac_roll_COM'] = np.append(df['shift_grawac_roll_COM'], 0)
                df['shift_grawac_roll_hydrins'] = np.append(df['shift_grawac_roll_hydrins'], lagroll2/20)

pf = pd.DataFrame()
pf['time'] = df['time']
#save both shifts (from COM-port stream and DShip)
pf['shift_grawac_roll_COM'] = df['shift_grawac_roll_COM']
pf['shift_grawac_roll_hydrins'] = df['shift_grawac_roll_hydrins']

filename = 'VAMPIRE2_grawac_shift_holes_%s_%s.txt'%(date_start.strftime('%Y%m%d'),date_end.strftime('%Y%m%d'))

pf.to_csv(filename)
