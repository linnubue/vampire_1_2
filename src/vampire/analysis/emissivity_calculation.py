import sys
import glob
import os as os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
import matplotlib as matplotlib
from datetime import datetime
from PIL import Image
import seaborn as sns
from scipy.optimize import curve_fit
from scipy.stats import norm


from vampire.io.readers.mwr import *

fontsizey=24
fontsizex=24
fontsizetix=20
fontsizelegend=16
fontsize_title =24

def gauss(x,mu,sigma,A):
    return A*np.exp(-(x-mu)**2/2/sigma**2)

def bimodal(x,mu1,sigma1,A1,mu2,sigma2,A2):
    return gauss(x,mu1,sigma1,A1)+gauss(x,mu2,sigma2,A2)
    
def threemodal(x,mu1,sigma1,A1,mu2,sigma2,A2,mu3,sigma3,A3):
    return gauss(x,mu1,sigma1,A1)+gauss(x,mu2,sigma2,A2)+ +gauss(x,mu3,sigma3,A3)
    
def surf_emi(TB, TB_down, Ts):
    """ surf_emi(TB, TB_down, Ts)"""
    return (TB- TB_down)/(Ts- TB_down)
         ###linear interpolation for scan of converted downwelling TBs
def lin_interpolation(endtb, starttb,time, length_scan=155): ###time is length of surface scan in seconds
    """lin_interpolation(endtb, starttb,time, length_scan=155)"""
    return (endtb-starttb)/length_scan *time +starttb
   
def calc_mwr_emissivity(time, instrument, surface_temp_method, show=True, ir_emi= 1.025 ):
    """  calc_emissivity(datetime, show=True) 
    uses the radiometer_measurements in 1 hour to derive emissivity using surf_emi (specular reflection, no upwelling TB
    """
    Hatpro_frequencies = [22.24,23.04,23.84,25.44,26.24,27.84,31.4,51.26,52.28,53.86,54.94,56.66,57.3,58]
    Mirac_frequencies = [183.91, 184.81, 185.81, 186.81, 188.31, 190.81, 243.  , 340.  ]

    mwr_ds  = read_scan(time, instrument, "EMIS",  daily_file=True)
    mwr_ds = mwr_ds.sel(time=pd.to_datetime(mwr_ds.time).hour==time.hour)
    mwr_surface_ds  = mwr_ds.sel(time=mwr_ds.ElAng == 53.0)
    mwr_down_ds = mwr_ds.sel(time=mwr_ds.ElAng == 127.0)
    ##calculate TBdown at beginning of first surface measurement and at end of first surface measurement, print standard deviation
    if instrument=="hatpro":
        frequencies = Hatpro_frequencies
        
    elif instrument=="lhumpro":
        frequencies = Mirac_frequencies
    len_freq = len(frequencies) 
    if len(mwr_surface_ds.time) != 620:
        print("this quicklook was hastily done for a specific setting with surface scans of length 155 s, please check code, this scan has lenght:",  len(mwr_surface_ds.time)/4)

    tb_down = {'tb': np.full((8, len_freq),np.nan)} 
    for k in range(8):   ##8 is number of intervals with angle=127
       # print("check correct time: ", mwr_down_ds.time[k*15:(k+1)*15])
        for n,freq in enumerate(frequencies):
            tb_down["tb"][k,n] = np.nanmean(mwr_down_ds.TBs[k*15:(k+1)*15, n])
            if  np.nanstd(mwr_down_ds.TBs[k*15:(k+1)*15, n]) > 1:
                ##raise warning:
                print(f"standard deviation of TB down at frequency {freq} at scan {k}", np.nanstd(mwr_down_ds.TBs[k*15:(k+1)*15, n]))
    len_time = len(mwr_surface_ds.time.values)
    emissivities = {"emi": np.full((len_time,len_freq), np.nan), 
                    "date": np.full(len_time,np.nan),
                    "surface_temp": np.full(len_time,np.nan)
                    }
    if surface_temp_method == "flir":
        flir_ds = xr.open_dataset(f"{os.environ['VAMPIRE_DATA']}flir/time_series/VAMPIRE_flir_statistics_{time:%Y%m%d}.nc")
    for k in range(4): ##4 is number of intervals with angle = 53
       # print("check correct time: ", mwr_surface_ds.time[k*155:(k+1)*155])
        for n,freq in enumerate(frequencies):
            tb_start = tb_down["tb"][2*k,n]
            tb_end = tb_down["tb"][2*k+1,n]
            for i in range(155):         
                if surface_temp_method == "flir": ##then take FLIR IR data          
                    index_colloc =  np.argmin(np.array(abs((flir_ds.time -mwr_surface_ds.time.values[(k*155)+i]))))
                    surface_temp = flir_ds.tb_center.values[index_colloc]*ir_emi      
                else:
                    surface_temp = surface_temp_method

                
                td = lin_interpolation(tb_end,tb_start,i)
                emi = surf_emi(mwr_surface_ds.TBs[(k*155)+i,n], td,surface_temp)
#                if emi < 0 and freq==243:
#                    print("negative emissivity, freq: ", freq, "tb", mwr_surface_ds.TBs.values[(k*155)+i,n], "td: ", td, "surfacetemp", surface_temp)

                emissivities["emi"][(k*155)+i,n] = emi.values
                emissivities["date"][(k*155)+i] = mwr_surface_ds.time.values[(k*155)+i]
                emissivities["surface_temp"][(k*155)+i] = surface_temp

    if show:
        for n,freq in enumerate(frequencies):
            fig = plt.figure(figsize=(10,5))
            plt.plot(pd.to_datetime(emissivities["date"]), emissivities["emi"][:, n], "o", label=f"{freq} GHz")
            plt.legend()
        #    locator = mdates.AutoDateLocator(minticks=2, maxticks=6)    
        #    formatter = mdates.ConciseDateFormatter(locator)  
        #    plt.xaxis.set_major_locator(locator)     
        #    plt.xaxis.set_major_formatter(formatter)
            plt.show()
            plt.close()
    if surface_temp_method == "flir":
        flir_ds.close()
    
    mwr_ds.close()
    return emissivities
    
def get_dual_emissivities(emidict_hatpro, emidict_lhumpro):
    """get_dual_emissivities(emidict_hatpro, emidict_lhumpro)
    get overlapping emissivities"""
    df1 = pd.DataFrame({"date":emidict_hatpro["date"]}).set_index("date")
    df2 = pd.DataFrame({"date":emidict_lhumpro["date"]}).set_index("date")
    for n,freq in enumerate(Hatpro_frequencies):
        df1[freq] = emidict_hatpro["emi"][:,n]
    for n,freq in enumerate(Mirac_frequencies):
        df2[freq] = emidict_lhumpro["emi"][:,n]   
    common_index = list((df1.index).intersection(df2.index))
    df1 = df1.loc[common_index].copy()
    df2 = df2.loc[common_index].copy()
    return df1, df2
    
def get_dual_emissivities_whole_day(day,surface_temp_method="flir"):
    """get_dual_emissivities_whole_day(day,surface_temp_method="flir")
    returns dataframes for hatpro and lhumpro for a whole day, only those that overlap"""
    df_hatpro = pd.DataFrame({"date":[]}).set_index("date")
    df_lhumpro = pd.DataFrame({"date":[]}).set_index("date")
    for hour in pd.date_range(day, day+timedelta(days=1),inclusive="left", freq="1h"):
        print(hour)
        emidict_hatpro = calc_mwr_emissivity(hour, "hatpro", surface_temp_method, show=False , ir_emi = 1.01)
        emidict_lhumpro = calc_mwr_emissivity(hour, "lhumpro", surface_temp_method, show=False , ir_emi = 1.01)
        df1, df2 = get_dual_emissivities(emidict_hatpro, emidict_lhumpro)
        df_hatpro = pd.concat([df_hatpro, df1])
        df_lhumpro = pd.concat([df_lhumpro, df2])
    return df_hatpro, df_lhumpro



def get_RGB(time, x_min =483, x_max= 517, y_min =455, y_max=497 ):
    """gets the RGB values at a certain time averaged over the rectangle specified by x_min, x_max, y_min, y_max"""
    files_gopro  = glob.glob(f"{os.environ['GOPRO_DATA']}/{time:%Y%m%d%H}/*") ##all files in that hour
    if len(files_gopro) !=0:
        time_go_pro = pd.to_datetime([files_gopro[m][-31:-17]  for m in range(len(files_gopro))])
        index_colloc =  np.argmin(abs((time_go_pro -time).total_seconds()))
        if np.min(abs((time_go_pro -time).total_seconds())) > 15:
            print("no go pro data within 15 seconds?", time)
            R_values = np.nan
            G_values = np.nan
            B_values = np.nan
        else:
            vis =Image.open(files_gopro[index_colloc])
            RGB = np.mean(np.mean(np.array(vis)[x_min:x_max, y_min:y_max],axis=0), axis=0)
            R_values = RGB[0]
            G_values = RGB[1]
            B_values = RGB[2]
    else:
        R_values = np.nan
        G_values = np.nan
        B_values = np.nan
    return R_values, G_values, B_values


def visualize_emissivities(day,surface_temp_method="flir", x_min =480, x_max= 520, y_min =450, y_max=500, 
                           freq1=22.24, freq2=243 ):
    """day,surface_temp_method="flir", x_min =480, x_max= 520, y_min =450, y_max=500, 
                           freq1=22.24, freq2=243 )
                           some plots for quicklooks of emissivity calculation of a whole day
                           x_min, x_max, y_
    """
    df_hatpro, df_lhumpro =get_dual_emissivities_whole_day(day,surface_temp_method)
    
    plt.figure(figsize=(12,4))
    plt.plot(pd.to_datetime(df_hatpro.index), df_hatpro[22.24],"o", label="ϵ at 22.24 GHz")
    plt.plot(pd.to_datetime(df_lhumpro.index), df_lhumpro[243],"o",label="ϵ at 243 GHz")
    plt.legend()
    #plt.xlim(datetime(2024,8,29,15), datetime(2024,8,30,10))
    #plt.ylim(0.8,1)
    
    plt.figure(figsize=(5,5))
    
    plt.plot(df_hatpro[22.24],df_lhumpro[243],"o")
    plt.xlabel("ϵ at 22.24 GHz")
    plt.ylabel("ϵ at 243 GHz")
    plt.show()
    plt.close()
    print("get RGB now")
    R_values = []
    B_values = []
    G_values = []
       
    for t in pd.to_datetime(df_hatpro.index):
        r,g,b = get_RGB(t, x_min, x_max, y_min, y_max )#default:xmin =483, x_max= 517, ymin =455, y_max=497 
        R_values = np.append(R_values,r)
        G_values = np.append(G_values, g)
        B_values = np.append(B_values, b)
    
    matplotlib.rcParams['xtick.labelsize'] = 16
    matplotlib.rcParams['ytick.labelsize'] = 16
    matplotlib.rcParams['axes.labelsize' ] = 18
    
    df = pd.DataFrame({"emi22.24":df_hatpro[22.24],"emi243":df_lhumpro[243], "R":R_values, "G":G_values, "B":B_values, 
                       "RBratio":R_values/B_values, "GBratio":G_values/B_values,
                       "RminusB": R_values-B_values, "meanRGB":np.mean([R_values, B_values, G_values],axis=0)})
    test = sns.JointGrid(data=df,x=df["emi22.24"], y=df["RBratio"], ratio=2,marginal_ticks=True,xlim=(0.3,1.06),ylim=(0.46,1.05))
    cax = test.figure.add_axes([0.61, .14, .02, .2])
    
    test.plot_joint( sns.histplot,cbar=True,cbar_kws=dict(extend="max"),cmap="light:#03012d", cbar_ax=cax,bins=40, vmax=70)
                 #  marginal_kws=dict(binwidth=0.01,kde=True, fill=True, kde_kws={"bw_adjust":0.2}))
    test.plot_marginals(sns.histplot, binwidth=0.01,kde=True, fill=True)#, kde_kws={"bw_adjust":0.2})#color="#03012d",
    test.set_axis_labels("$ϵ$ at 22.24 GHz", 'R:B ratio', fontsize=16)
    #expected=( 0.5, 0.01, 400,0.95,.01,200)#mu1,sigma1,A1,mu2,sigma2,A2)
    
    #x, y = test.ax_marg_x.lines[-1].get_data()
    #params,cov=curve_fit(bimodal,x,y,expected)
    #print(params)
    #test.ax_marg_x.plot(x,bimodal(x,*params),color='red',lw=1,ls="dashed",label=f'fitted Gaussian, mu={params[0]:.2f}, σ = {params[1]:.2f}')
    fig = test.fig
    fig.suptitle("2024-09-03")
    
    #f = "/home/jrueckert/Output/atwaice-data-analyses/results/figures_surface_scans/Emi22_RBratiov3_fittedGaussian_revised_arial.pdf"
    #fig.savefig(f, dpi=300, bbox_inches="tight")
    fig

    test = sns.JointGrid(data=df,x=df["emi243"], y=df["RBratio"], ratio=2,marginal_ticks=True,xlim=(0.3,1.06),ylim=(0.46,1.05))
    cax = test.figure.add_axes([0.61, .14, .02, .2])
    
    test.plot_joint( sns.histplot,cbar=True,cbar_kws=dict(extend="max"),cmap="light:#03012d", cbar_ax=cax,bins=40, vmax=70)
                 #  marginal_kws=dict(binwidth=0.01,kde=True, fill=True, kde_kws={"bw_adjust":0.2}))
    test.plot_marginals(sns.histplot, binwidth=0.01,kde=True, fill=True)#, kde_kws={"bw_adjust":0.2})#color="#03012d",
    test.set_axis_labels("$ϵ$ at 22.24 GHz", 'R:B ratio', fontsize=16)
    #expected=( 0.5, 0.01, 400,0.95,.01,200)#mu1,sigma1,A1,mu2,sigma2,A2)
    
    #x, y = test.ax_marg_x.lines[-1].get_data()
    #params,cov=curve_fit(bimodal,x,y,expected)
    #print(params)
    #test.ax_marg_x.plot(x,bimodal(x,*params),color='red',lw=1,ls="dashed",label=f'fitted Gaussian, mu={params[0]:.2f}, σ = {params[1]:.2f}')
    fig = test.fig
    fig.suptitle("2024-09-03")
    
    #f = "/home/jrueckert/Output/atwaice-data-analyses/results/figures_surface_scans/Emi22_RBratiov3_fittedGaussian_revised_arial.pdf"
    #fig.savefig(f, dpi=300, bbox_inches="tight")
    fig
