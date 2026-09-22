;
;******************************
PRO CREATE_OFFSET_SAV
;******************************

;  The tb_offset_file must be of IDL binary format (.sav) and contain the parameters defined in the following:
;  date_offset=DBLARR(n_date_offset): specifies the times AFTER which a certain offset correction is valid (Julian day format!)
;  freq_offset=DBLARR(n_freq_offset): frequency channels that offset correction is applied to (GHz)
;  ang_offset=DBLARR(n_ang_offset): elevation angles that offset correction is applied to (elevation angle)
;  tb_offset=DBLARR(n_date_offset, n_freq_offset, n_ang_offset): tb offset correction values (K) to be SUBTRACTED from
;  original values to ensure correct values

;******************************
; CONTROL ROOM
;******************************

campaign = "VAMPIRE2"   ; "vampire" or "VAMPIRE2"
instr = "hatpro"       ; "hatpro" or "mirac-p"

;******************************
; END OF CONTROL ROOM
;******************************



; path of offset data for WALSEMA, created with CSC:
path_data = "/path/to/data/" + campaign + "/CSC/offsets/"
path_output = "/path/to/data/" + campaign + "/CSC/offsets/"

campaign_label = "PS144"
IF STRCMP(campaign, "VAMPIRE2") THEN BEGIN
  campaign_label = "PS149"
ENDIF

filename = campaign_label + "_" + instr + "_radiometer_clear_sky_offset_correction.nc"
nc_id = NCDF_open(path_data + filename)

bias_id = NCDF_VARID(nc_id, 'bias')
frequency_id = NCDF_VARID(nc_id, 'frequency')
cal_start_id = NCDF_VARID(nc_id, 'calibration_period_start')
cal_end_id = NCDF_VARID(nc_id, 'calibration_period_end')

NCDF_VARGET, nc_id, bias_id, bias
NCDF_VARGET, nc_id, frequency_id, frequency
NCDF_VARGET, nc_id, cal_start_id, cal_start
NCDF_VARGET, nc_id, cal_end_id, cal_end


n_date_offset = N_ELEMENTS(cal_start)
n_freq_offset = N_ELEMENTS(frequency)
n_ang_offset = 1

date_offset = DBLARR(n_date_offset)
freq_offset = DBLARR(n_freq_offset)
ang_offset = DBLARR(n_ang_offset)
tb_offset = REFORM(DBLARR(n_date_offset, n_freq_offset, n_ang_offset), [n_date_offset, n_freq_offset, n_ang_offset])



; Compute Julian Day:
IF STRCMP(campaign, "vampire") THEN BEGIN
 IF STRCMP(instr, "hatpro") THEN BEGIN
  CAL_Y = [2024, 2024, 2024]
  CAL_M = [8, 8, 9]
  CAL_D = [9, 9, 11]
  CAL_H = [0, 12, 14]
  CAL_MIN = [0, 0, 0]
  CAL_S = [0, 0, 0]
 ENDIF ELSE IF STRCMP(instr, "mirac-p") THEN BEGIN
  CAL_Y = [2024, 2024]
  CAL_M = [8, 9]
  CAL_D = [9, 11]
  CAL_H = [0, 13]
  CAL_MIN = [0, 0]
  CAL_S = [0, 0]
 ENDIF
ENDIF ELSE IF STRCMP(campaign, "VAMPIRE2") THEN BEGIN
 IF STRCMP(instr, "hatpro") THEN BEGIN
  CAL_Y = [2025, 2025, 2025]
  CAL_M = [7, 7, 8]
  CAL_D = [2, 2, 6]
  CAL_H = [0, 14, 16]
  CAL_MIN = [0, 0, 28]
  CAL_S = [0, 0, 21]
 ENDIF ELSE IF STRCMP(instr, "mirac-p") THEN BEGIN
  CAL_Y = [2025, 2025, 2025]
  CAL_M = [7, 7, 8]
  CAL_D = [2, 2, 6]
  CAL_H = [0, 14, 17]
  CAL_MIN = [0, 30, 5]
  CAL_S = [0, 0, 4]
 ENDIF
ENDIF

JD = JULDAY(CAL_M, CAL_D, CAL_Y, CAL_H, CAL_MIN, CAL_S)


; Set variables:
date_offset = JD
freq_offset = frequency
ang_offset(0) = 90.0
tb_offset = REFORM(TRANSPOSE(bias), [n_date_offset, n_freq_offset, n_ang_offset])

outfile_suffix = ''
IF instr EQ 'hatpro' THEN BEGIN
 outfile_suffix = '_hat'
ENDIF ELSE IF instr EQ 'mirac-p' THEN BEGIN
 outfile_suffix = '_mir'
ENDIF

outfile = path_output + campaign + '_tb_offset_pol' + outfile_suffix + '.sav'
SAVE, date_offset, freq_offset, ang_offset, tb_offset, FILENAME=outfile, /VERBOSE

END
