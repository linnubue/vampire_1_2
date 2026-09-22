import os
import pdb

import xarray as xr
import numpy as np
import matplotlib as mpl
mpl.use('agg')      # to avoid memory leak by TK
import matplotlib.pyplot as plt
from matplotlib import figure
import matplotlib.ticker as ticker
from cmcrameri import cm

from vampire.io.readers.flir import read_flir_statistics
from vampire.quicklooks.flir import get_flir_image
from vampire.quicklooks.radiosonde_mwr_composit import create_colourbar_hz


campaign_name_long_dict = {'PS144': "VAMPIRE",
                           'PS149': "VAMPIRE2"}

def main():
    
    campaign_label = {'PS144': 'vampire',
                      'PS149': "VAMPIRE2"}
    path_output = os.environ['VAMPIRE_DATA'] + f"{campaign_label[Constants.CAMPAIGN_NAME]}/flir/for_publication/flir_png/"
    
    dates = np.arange(np.datetime64(Constants.DATE_START), 
                      np.datetime64(Constants.DATE_END) + np.timedelta64(1, "D"),
                      np.timedelta64(1, "D")).astype('datetime64[s]')
    
    for date in dates:
        print(str(date))
        
        try:
            DS = read_flir_statistics(date, campaign_name=Constants.CAMPAIGN_NAME)
        except FileNotFoundError:
            continue
        
        path_output_date = os.path.join(path_output, 
                                        str(date.astype('datetime64[D]')).replace('-',''))
        os.makedirs(path_output_date, exist_ok=True)
        
        process_day(DS, date, path_output_date)


def process_day(DS: xr.Dataset, date: np.datetime64, path_output: str):
    
    minutes = np.arange(date, date + np.timedelta64(1, "D"), 
                        np.timedelta64(60, "s"))
    n_minutes = len(minutes)
    for k, minute in enumerate(minutes):
        if k % 60 == 0: print(minute)
        try:
            DS_m = DS.sel(time=minute, method='nearest', tolerance="2s")
        except KeyError:
            continue
        
        flir_img = get_flir_image(DS, DS_m.time.values, 
                                  campaign_name_long_dict[Constants.CAMPAIGN_NAME])
        
        plot_flir_img(flir_img, DS_m, path_output)
        
        
def plot_flir_img(flir_img: np.ndarray, DS_m: xr.Dataset, path_output: str):
    
    dpi = 96
    nhgt, nwidth = flir_img.shape
    time_text = str(DS_m.time.values.astype('datetime64[s]'))
    
    f1 = figure.Figure(figsize=(nwidth/dpi,(nhgt+50)/dpi), dpi=dpi)
    a1 = f1.subplots(1)
    f1.subplots_adjust(top=1., left=0., right=1., bottom=50/(nhgt+50))
    a1.axis("off")
    
    a1.text(0.01, 0.015, time_text.replace("T"," "),
            ha='left', va='bottom', fontsize=6, transform=f1.transFigure)
    
    im = a1.imshow(flir_img, cmap=cm.lipari)
    f1, a1 = create_colourbar_hz(f1, a1, im, "                 Brightness temperature (K)", 
                                 ypad=-0.021, cbheight=0.02,
                                 cb_kwargs={'ticks': ticker.MaxNLocator(5)})
    
    filename = f"{Constants.CAMPAIGN_NAME}_flir_tb_{time_text.replace('-', '').replace(':', '')}"
    outfile = os.path.join(path_output, filename + ".png")
    f1.savefig(outfile, dpi=96)
    plt.close(f1)


if __name__ == "__main__":
    
    campaign = "vampire"
    if campaign == "vampire":
        from vampire.constants import Constants as Constants
    elif campaign == 'VAMPIRE2':
        from vampire.constants import Constants_PS149 as Constants
    
    main()