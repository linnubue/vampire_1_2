import os
import pdb
import glob
from copy import deepcopy

import numpy as np
import xarray as xr
import matplotlib as mpl
import matplotlib.pyplot as plt

from vampire.analysis.radiosonde_mwr_comparison import (load_data_to_be_compared,
                                                        get_spatio_temporal_matches,
                                                        add_lin_fit)

path_plots_default = os.environ['PATH_PLOTS']+"quicklooks/radiosonde_mwr_comparison/for_publication/"

def main():
    
    path_plots = path_plots_default
    set_dict = {'save_figures': True,
                'path_plots': path_plots}
    
    vars_to_compare = ['prw']
    reference_instr = 'radiosonde'
    mwr_instr = ['mwr_synergy']
    instruments = [reference_instr,] + mwr_instr
    
    COMP_DS = dict()
    COMP_REF_DS = dict()
    for campaign in ['vampire', 'VAMPIRE2']:
        
        if campaign == 'vampire': 
            from vampire.constants import Constants as Constants
        elif campaign == 'VAMPIRE2':
            from vampire.constants import Constants_PS149 as Constants
            
        path_data = {'radiosondes': os.environ['VAMPIRE_DATA'] + "radiosondes/",
                     'mwr_synergy': os.environ['VAMPIRE_DATA'] + "mwr_synergy/for_publication/PANGAEA/"}

        DS_DICT = load_data_to_be_compared(path_data, mwr_instr, reference_instr, vars_to_compare,
                                           for_paper=True, 
                                           CAMPAIGN_NAME=Constants.CAMPAIGN_NAME)
    
        vars_1d = [var for var in vars_to_compare if DS_DICT[reference_instr][var].ndim == 1]
        vars_2d = [var for var in vars_to_compare if DS_DICT[reference_instr][var].ndim == 2]
        COMP_DS[Constants.CAMPAIGN_NAME], COMP_REF_DS[Constants.CAMPAIGN_NAME] = (
            get_spatio_temporal_matches(DS_DICT=DS_DICT, 
                                        vars_=vars_to_compare,
                                        non_ref_instr=mwr_instr,
                                        ref=reference_instr,
                                        vars_1d=vars_1d,
                                        vars_2d=vars_2d)
            )
    
    plot_iwv(COMP_DS, COMP_REF_DS, 
             instruments, reference_instr,
             **set_dict)


def plot_iwv(
    COMP_DS: xr.Dataset, 
    COMP_REF_DS: xr.Dataset,
    instruments: list,
    ref: str,
    save_figures=False,
    path_plots=path_plots_default):
    
    instrument_labels = {'radiosonde': "Radiosonde",
                        'mwr_synergy': "MWRs"}
    var_labels = {'prw': "IWV"}
    var_units = {'prw': "kg$\,$m$^{-2}$"}
    non_ref_instr = [instr for instr in instruments if instr != ref]
    
    for ins in non_ref_instr:
        
        scatterplot_paper_both_campaigns(COMP_REF_DS, 
                                         COMP_DS, 
                                         instrument_labels=instrument_labels,
                                         var_labels=var_labels,
                                         var_units=var_units,
                                         instrument=ins,
                                         ref=ref,
                                         path_plots=path_plots,
                                         save_figures=save_figures)


def scatterplot_paper_both_campaigns(
    DS_ref: dict, 
    DS_eval: dict,
    instrument_labels: dict,
    var_labels: dict,
    var_units: dict,
    instrument: str, 
    ref: str,
    path_plots=path_plots_default,
    save_figures=False):
    
    from vampire.analysis.data_tools import compute_retrieval_statistics, lowercase_letter_from_number
    
    var = 'prw'
    xy_lims = np.array([0., 30.])
    
    f1, axs = plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True, figsize=(7.5,4))
    plt.subplots_adjust(left=0.08, right=0.97, bottom=0.12, top=0.96, wspace=0.1)
    
    for ix, campaign in enumerate(DS_ref.keys()):
        data_ref = DS_ref[campaign][f'{var}_{instrument}']
        data_eval = DS_eval[campaign][f'{var}_{instrument}']
        error_dict = compute_retrieval_statistics(data_ref, data_eval, compute_stddev=True)
    
        axs[ix].errorbar(data_ref, data_eval,yerr=0., linestyle='none', elinewidth=1.0, capsize=0.5, capthick=1.0,
                         ecolor='tab:blue', marker='o', markersize=5, markeredgecolor=(0,0,0), 
                        markerfacecolor='tab:blue')
        axs[ix] = add_lin_fit(axs[ix], data_ref.values, data_eval.values, xy_lims)
        
        axs[ix].text(0.98, 0.02, 
                     f"RMSD: {error_dict['rmse']:.2g}\n" +
                     f"Bias: {error_dict['bias']:.2g}\n" +
                     f"Std: {error_dict['stddev']:.2g}\n" +
                     f"R: {error_dict['R']:.2f}\n" +
                     f"N: {error_dict['N']}", 
                     ha='right', va='bottom', transform=axs[ix].transAxes)
        axs[ix].text(0.01, 1.01,
                     f"{lowercase_letter_from_number(ix)})",
                     ha='left', va='bottom', transform=axs[ix].transAxes)
        
        lh, ll = axs[ix].get_legend_handles_labels()
        axs[ix].legend(lh, ll, loc='upper left', frameon=False)
    
        axs[ix].set_xlim(xy_lims)
        axs[ix].set_ylim(xy_lims)
        axs[ix].set_aspect('equal')

        axs[ix].grid(which='both', axis='both', color=(0.5,0.5,0.5), alpha=0.5)
        
        axs[ix].set_xlabel(f"{var_labels[var]}" + "$_{\mathrm{" + f"{instrument_labels[ref]}" + "}}$" +
                           f" ({var_units[var]})")
        axs[ix].set_ylabel(f"{var_labels[var]}" + "$_{\mathrm{" + f"{instrument_labels[instrument]}" + "}}$" +
                           f" ({var_units[var]})")
        
        axs[ix].label_outer()
        
    
    if save_figures:
        os.makedirs(path_plots, exist_ok=True)
        
        plotname = f"PS144_PS149_{ref}_{instrument}_scatterplot_{var}"
        plotfile = os.path.join(path_plots, plotname + ".pdf")
        f1.savefig(plotfile, dpi=300)

        print(f"Saved {plotfile} ....")
    else:
        plt.show()
        pdb.set_trace()
        
    plt.close()


if __name__ == "__main__":
    
    main()