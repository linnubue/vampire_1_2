import sys
import os
import datetime as dt
import pdb

import numpy as np

"""
Creates the .dat filter files used by MWR_PRO to set manual flags from .txt files where the time stamps 
of artifacts have been marked. 
"""

mwr_name_description = {'hatpro': "HATPRO", 'mirac-p': "MiRAC-P"}

def main():
    
    mwr_name = "hatpro"
    obs_type = "atm_transit"
    campaign_name = "vampire"

    path = os.getcwd() + "/vampire/post_process_mwr/"
    file = path + f"{campaign_name}_{mwr_name_description[mwr_name]}_outliers.txt"
    path_output = os.environ['VAMPIRE_DATA'] + f"{campaign_name}/{mwr_name}/{obs_type}/"
    outfile = path_output + f"filter_{campaign_name}_{mwr_name}.dat"

    flagged_times, bands = read_outliers_txt(file)
    string_for_file = create_filter_dat_content(flagged_times, bands)

    footer_lines = ["date of last change", dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")[2:], ""]
    string_for_file = string_for_file + footer_lines

    with open(outfile, "w") as f_handler:
        f_handler.write("\n".join(string_for_file))
    print(f"Created {outfile}....")


def read_outliers_txt(file: str):
    
    n_lines = get_number_of_lines(file)
    n_outliers = n_lines - 1        # subtracting the header

    flagged_times = np.full((n_outliers,2), np.datetime64("1970-01-01T00:00:00"))
    bands = np.zeros((n_outliers,3), dtype=np.int32)
    with open(file, "r") as f_handler:
        ii = 0
        for k, line in enumerate(f_handler):
            line_str = line.strip()

            if k > 0:
                line_elems = line_str.split(" ")
                flagged_times[ii,0], flagged_times[ii,1] = extract_flagged_times(line_elems)

                bands[ii,0] = int(line_elems[12])       # K or band 1
                bands[ii,1] = int(line_elems[13])       # V or band 2
                bands[ii,2] = int(line_elems[14])       # W or band 3

                ii += 1
                
    return flagged_times, bands


def get_number_of_lines(file: str):
    with open(file, "r") as f_handler:
        n_lines = len(f_handler.readlines())
        
    return n_lines


def extract_flagged_times(line_elems: list):
    """
    Extract the time stamps of the flagged times from the line element list line_elems.
    """
    
    hh0 = line_elems[3]
    min0 = line_elems[4]
    flagged_times_start = np.datetime64("-".join(line_elems[:3])+"T"+
                                        hh0+":"+min0+":00")
    hh1 = line_elems[10]
    min1 = line_elems[11]
    flagged_times_end = np.datetime64("-".join(line_elems[7:10])+"T"+
                                        hh1+":"+min1+":00")
    
    return flagged_times_start, flagged_times_end


def get_flagged_dates(flagged_times):
    
    #Get all individual dates and count occurrences of each date.
    all_dates = np.unique(flagged_times[:,0].astype('datetime64[D]'))
    n_occ_dates = np.asarray([np.count_nonzero(flagged_times[:,0].astype('datetime64[D]') == date) for date in all_dates])

    return all_dates, n_occ_dates


def datetime64_to_decimal_hours(flagged_times, date):
    
    """
    Numpy's datetime64 is converted to decimal hours. E.g., 2024-07-25T03:37:00 will be converted
    to 3.62.
    """
    
    ft_dates = flagged_times[flagged_times[:,0].astype('datetime64[D]') == date,:]
    decimal_hour_start = np.asarray([str(ft_date)[11:13] + 
                                     f"{np.floor(100*(int(str(ft_date)[14:16])/60))*0.01:.2f}"[1:] 
                                     for ft_date in ft_dates[:,0]])
    decimal_hour_end = np.asarray([str(ft_date)[11:13] + 
                                   f"{np.ceil(100*(int(str(ft_date)[14:16])/60))*0.01:.2f}"[1:] 
                                   for ft_date in ft_dates[:,1]])
    
    return decimal_hour_start, decimal_hour_end


def format_flagging_info_to_dat_string(
    date_str: str, 
    decimal_hour_start, 
    decimal_hour_end,
    bands_dates, 
    n_occ_date):
    
    """
    Create string containing the flagged times information (times, number of flagged times per day,
    flagged bands):
    """
    
    str_line = " "*33
    str_line = date_str[2:] + str_line[6:]

    if n_occ_date >= 10:
        str_line = str_line[:7] + str(n_occ_date) + str_line[9:]
    else:
        str_line = str_line[:8] + str(n_occ_date) + str_line[9:]        
    
    str_line = str_line[:10] + decimal_hour_start[0] + " " + decimal_hour_end[0] + " " + " ".join(bands_dates[0].astype('str'))
    
    return str_line


def format_additional_flagged_times_for_date(
    string_for_file,
    decimal_hour_start, 
    decimal_hour_end,
    bands_dates,
    n_occ_date):
    
    """
    Additional flagged times for a date must not include the date string. Therefore, separate formatting
    compared to format_flagging_info_to_dat_string is required.
    """
    
    for k in range(1, n_occ_date):
        str_line_add = " "*33
        str_line_add = (str_line_add[:10] + decimal_hour_start[k] + " " + decimal_hour_end[k] +
                        " " + " ".join(bands_dates[k].astype('str')))
        
        string_for_file.append(str_line_add)
        
    return string_for_file


def create_filter_dat_content(
    flagged_times: np.ndarray, 
    bands: np.ndarray):
    
    """
    From the extracted flagged times and MWR bands, create a list of strings, which will form the 
    content of the filter...dat files, following the convention needed for MWR_PRO.
    
    Parameters:
    -----------
    flagged_times : np.ndarray of np.datetime64[s]
        Start and end of flagged times. 2D array where the first dimension corresponds to the 
        number of flagged times and the second dimension distinguishes between the start and end
        of the flagged time (first, and second element, respectively).
    bands : np.ndarray of int
        Integers indicating whether the MWR band (axis 1 of the 2D array) is flagged. 
        Shape: (n_flagged_times,number_of_bands)
    """

    # create string for .dat file: count occurrences of each date:
    all_dates, n_occ_dates = get_flagged_dates(flagged_times)


    # add header:
    string_for_file = [
        "#This file contains manually set quality control flags for MWR data.",
        "#Faulty data times can be manually set and will be flagged in quicklooks and final netcdf products.",
        "#Possible reasons: disturbances on radome, radio-frequency interference, mis-calibration, ...",
        "#Note: TBs and products will still be available during the specified times.",
        "#1st column contains date of faulty data following format specification",
        "#2cnd column contains number of faulty intervals on one day",
        "#3rd and 4th column: start time and end time in decimal(!) hours - note, e.g. 19:30=19.50 ",
        "#5th column: set to 1 if Band1 channels are subject to error",
        "#6th column: set to 1 if Band2 (if existing) channels are subject to error",
        "#7th column: set to 1 if Band3 (if existing) channels are subject to error",
        '#The second to last line must always contain the string "date of last change"',
        "#The last row must contain the actual date of last change.",
        "#You must adhere to formats given in the example below!",
        "#BEGIN OF EXAMPLE",
        "yymmdd nn hh.hh hh.hh 1 2 3",
        "110117  1 19.00 21.00 1 0 0",
        "110118  2 10.00 11.00 1 0 0",
        "          12.50 14.50 1 0 0",
        "date of last change",
        "130710",
        "#END OF EXAMPLE"]

    for i_d, date in enumerate(all_dates):
        date_str = str(date).replace("-","")

        decimal_hour_start, decimal_hour_end = datetime64_to_decimal_hours(flagged_times, date)
        bands_dates = bands[flagged_times[:,0].astype('datetime64[D]') == date,:]

        str_line = format_flagging_info_to_dat_string(date_str, decimal_hour_start, decimal_hour_end,
                                                      bands_dates, n_occ_dates[i_d])
        string_for_file.append(str_line)

        if n_occ_dates[i_d] > 1:
            string_for_file = format_additional_flagged_times_for_date(string_for_file,
                                                                       decimal_hour_start, 
                                                                       decimal_hour_end,
                                                                       bands_dates, 
                                                                       n_occ_dates[i_d])
            
    return string_for_file
        

if __name__ == "__main__":
    main()
