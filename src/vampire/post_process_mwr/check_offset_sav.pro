;
;******************************
PRO CHECK_OFFSET_SAV
;******************************

;******************************
; CONTROL ROOM
;******************************

campaign = "VAMPIRE2"   ; "vampire" or "VAMPIRE2"
instr = "hatpro"       ; "hatpro" or "mirac-p"

;******************************
; END OF CONTROL ROOM
;******************************


IF instr EQ 'hatpro' THEN BEGIN
 mwr_name_short = "hat"
ENDIF ELSE IF instr EQ 'mirac-p' THEN BEGIN
 mwr_name_short = "mir"
ENDIF


; path of offset data for vampire/VAMPIRE2:
path_output = "/home/hatpro/mwr_pro_vampire/mwr_pro/scripts/"
file_sav = path_output + campaign + "_tb_offset_pol_" + mwr_name_short + ".sav"
RESTORE, file = file_sav

STOP

END
