import os
import pdb

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import xarray as xr
from PIL import Image

from vampire.constants import Constants_PS149 as Constants


def main():
    
    set_dict = {'save_figures': True,
                'with_deck': True,
                'path_plots': os.environ['PATH_PLOTS'] + "quicklooks/instrument_setup/",
                }

    data = get_instrument_positions()
    plot_instrument_positions(data, **set_dict)
    # edit_peildeck_background(set_dict['path_plots'])
    
    
def get_instrument_positions():
    
    """
    Set instrument positions (in cm) from the front portside corner of the upper Peildeck (see
    sketch in notes, p. 226).
    x: relative latitudinal position (portside-starboard)
    y: relative longitudinal position (bow-aft)
    z: relative height of sensor to deck floor
    W: width of instrument (x direction)
    L: length of instrument (y direction)
    xs: x position of sensor 
    ys: y position of sensor
    """
    
    data = dict()
    L_upper_peildeck = 677.
    z_upper_peildeck = 161.         # with respect to lower peildeck
    x_lower_peildeck = 298.
    data['mobotix'] = {'x': 827.,
                       'y': -7.,
                       'z': 103.,
                       'W': 30.,
                       'L': -19.}   # negative sign because of anchor point relative to which L is measured
    data['mobotix']['xs'] = data['mobotix']['x'] + 15.
    data['mobotix']['ys'] = data['mobotix']['y'] -18.
    
    data['grawac'] = {'x': 435.,
                      'y': 300.,
                      'z': 121.,
                      'W': 102.,
                      'L': 108.}
    data['grawac']['xs'] = data['grawac']['x'] + 44.
    data['grawac']['ys'] = data['grawac']['y'] + data['grawac']['L'] - 44.
    
    data['mirac-a'] = {'x': 430.5,
                       'y': 425., # mean of obs from two directions (unfortunately, the Peildeck isn't square)
                       'z': 109.,
                       'W': 111.,
                       'L': 87.}
    data['mirac-a']['xs'] = data['mirac-a']['x'] + 29.
    data['mirac-a']['ys'] = data['mirac-a']['y'] + 33.
    
    data['parsivel'] = {'x': 587.,
                        'y': L_upper_peildeck-12.,
                        'z': 198.}
    
    data['usonic'] = {'x': 807.,
                      'y': L_upper_peildeck-15.,
                      'z': 206.}
    
    data['gopro'] = {'x': x_lower_peildeck-26.,
                     'y': L_upper_peildeck+364.,
                     'z': 113.}
    
    data['flir'] = {'x': x_lower_peildeck-35.,
                    'y': L_upper_peildeck+369.,
                    'z': 117.}
    
    data['mirac-p'] = {'x': x_lower_peildeck+16.,
                       'y': L_upper_peildeck+431.,
                       'z': 149.,
                       'L': 90.,
                       'W': -59.,
                       'xs': x_lower_peildeck-16.,
                       }
    data['mirac-p']['ys'] = data['mirac-p']['y'] + data['mirac-p']['L'] - 23.
    
    data['hatpro'] = {'x': x_lower_peildeck+16.,
                      'y': L_upper_peildeck+594.,
                      'z': 149.,
                      'L': 90.,
                      'W': -59.,
                      'xs': x_lower_peildeck-16.,}
    data['hatpro']['ys'] = data['hatpro']['y'] + 23.
    
    data['upper_peildeck'] = {'x': 0.,
                              'y': 0.,
                              'z': z_upper_peildeck,
                              'L': L_upper_peildeck,
                              'W': 1000.}
    data['lower_peildeck'] = {'x': x_lower_peildeck,
                              'y': L_upper_peildeck,
                              'z': 0.,
                              'L': 1000.,
                              'W': 1000.}
    
    for instrument in ['grawac', 'mirac-a', 'mobotix', 'parsivel', 'usonic']:
        data[instrument]['z'] += data['upper_peildeck']['z']
    
    return data


def edit_peildeck_background(path_plots=os.environ['PATH_PLOTS'] + "quicklooks/instrument_setup/"):
    
    background = np.asarray(Image.open(path_plots + "peildeck_background.png"))
    background = xr.DataArray(background, dims=['x','y','rgba'])
    background = background.where(background.sum('rgba') < 1020, other=0).values
    background = Image.fromarray(background, 'RGBA')
    background.save(path_plots + "peildeck_background_edited.png")


def plot_instrument_positions(
    data: dict, 
    with_deck=True,
    save_figures=False, 
    path_plots=os.environ['PATH_PLOTS'] + "quicklooks/instrument_setup/"):
    
    colour_dict = {'grawac': np.array([31.,119.,180.]),
                   'mirac-a': np.array([255.,127.,14.]),
                   'parsivel': np.array([214.,39.,40.]),
                   'usonic': np.array([148.,103.,189.]),
                   'hatpro': np.array([140.,86.,75.]),
                   'mirac-p': np.array([227.,119.,194.]),
                   'gopro': np.array([27.,27.,27.]),
                   'flir': np.array([188.,189.,34.]),
                   'mobotix': np.array([23.,190.,207.])}
    label_dict = {'grawac': "GRaWAC",
                  'mirac-a': "MiRAC-A",
                  'parsivel': "Parsivel",
                  'usonic': "uSonic-3",
                  'hatpro': "HATPRO",
                  'mirac-p': "MiRAC-P",
                  'gopro': "GoPro",
                  'mobotix': "Total sky imager",
                  'flir': "FLIR"}
    for key in colour_dict.keys(): 
        colour_dict[key] *= (1./255.)
        label_dict[key] += f" (height: {int(data[key]['z'])} cm)"
    
    deck_line_kwargs = {'linewidth': 1.5, 'color':'k'}
    x_lims = np.array([-100., 1000.])
    y_lims = np.array([-100., 1400.])

    f1 = plt.figure(figsize=(6.5,5))
    a1 = plt.axes()
    plt.subplots_adjust(right=0.5)
    a1.grid(which='major', axis='both', color=(0,0,0), alpha=0.125)
    a1.spines[['top', 'right']].set_visible(False)
    
    if with_deck:
        a1.hlines(data['upper_peildeck']["y"], xmin=data['upper_peildeck']["x"], 
                xmax=data['upper_peildeck']["x"] + data['upper_peildeck']['W'], **deck_line_kwargs)
        a1.vlines(data['upper_peildeck']["x"], ymin=data['upper_peildeck']['y'],
                ymax=data['upper_peildeck']['y'] + data['upper_peildeck']['L'], **deck_line_kwargs)
        a1.hlines(data['upper_peildeck']["y"] + data['upper_peildeck']['L'], 
                xmin=data['upper_peildeck']["x"], 
                xmax=data['upper_peildeck']["x"] + data['upper_peildeck']['W'], **deck_line_kwargs)
        a1.vlines(data['lower_peildeck']['x'], ymin=data['lower_peildeck']['y'],
                ymax=data['lower_peildeck']['y'] + data['lower_peildeck']['L'], **deck_line_kwargs)
    
    for name, data_instr in data.items():
        if name in ['mobotix', 'grawac', 'mirac-a', 'hatpro', 'mirac-p']:
            instr_plot = patches.Rectangle((data_instr['x'], data_instr['y']),
                                        width=data_instr['W'], height=data_instr['L'],
                                        facecolor=colour_dict[name],
                                        edgecolor=colour_dict[name],
                                        label=label_dict[name])
            a1.add_artist(instr_plot)
            a1.scatter(np.array([data_instr['xs']]), np.array([data_instr['ys']]), s=16,
                       c="k", marker='x')
    
        elif name in ['parsivel', 'usonic', 'gopro', 'flir']:
            a1.scatter(np.array([data_instr['x']]), np.array([data_instr['y']]), s=36,
                       color=colour_dict[name], marker='o',
                       label=label_dict[name])
            
    lh, ll = a1.get_legend_handles_labels()
    a1.legend(lh, ll, loc='upper left', bbox_to_anchor=(1.0, 1.0), frameon=False)
    
    a1.set_xlim(x_lims)
    a1.set_ylim(y_lims[::-1])
    a1.set_aspect("equal")
    a1.set_xlabel("Distance (cm)")
    a1.set_ylabel("Distance (cm)")
    
    if save_figures:
        suffix = ""
        if not with_deck:
            suffix = "_no_deck"
        plotname = f"{Constants.CAMPAIGN_NAME}_instrument_setup" + suffix
        plotfile = path_plots + plotname + ".png"
        f1.savefig(plotfile, dpi=300)

        print(f"Saved {plotfile} ....")
    else:
        plt.show()
        pdb.set_trace()
        
    plt.close()
    
if __name__ == '__main__':
    main()