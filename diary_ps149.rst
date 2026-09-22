LOGBOOK:
--------
- 2025-08-29:
	08:28: Checked whether instruments, backups and cron jobs are running. Checked laptop disk 
		space: Nimbus: 305 GB, cirrus: 78 GB, cumulus: 252 GB. Converted radar lv1 files to NC for
		2025-08-28 using the RPG software. Started the final GoPro resizing: cirrus:
		gopro_processing.sh
	08:41: Checked time synchronisation of instruments and laptops, see time_offsets.txt.
	08:48: Checked blowers and heaters.
	08:52: Copied radiosonde files to the public server and the MyCloud backup NAS.

- 2025-08-28:
	08:30: Checked laptop disk space: Nimbus: 167 GB, cumulus: 273 GB, cirrus: 103 GB
	08:31: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	08:38: Restarted FLIR recording, converted radar lv1 files to netcdf, checked that instruments,
		backups and cron jobs are running.
	08:39: Checked and noted down time offsets in time_offsets.txt.
	Stowed away ice station devices from Gunnar.
	Salinity measurements of station 2d and 3d samples. 
	Test salinity measurements in salinometer room: Test probe has around 34 PSU, our salinometer
		shows 16.7 PSU.
	Digitalised salinity measurements.
	13:35:00: Stopped FLIR.
	13:41:50: Stopped GoPro measurements.
	Uninstalled the FLIR and GoPro. Packed MaMe18.
	Noted the end of the FLIR and GoPro measurements in 12_ATMOS/VAMPIRE2/
		vampire2_instrument_setup.xlsx and 07_IceStation_Events/Underway/
		UnderwayEvents_VAMPIRE.xlsx. Also added the measurement termination times to the cruise 
		report Cruise_report_VAMPIRE.docx.
	Checked how much disk space is required for one month of HATPRO, LHUMPRO and mobotix sky cam:
		In total, 12 GB are sufficient. We will empty the disk a bit more anyways.

- 2025-08-27:
	08:43: Restarted FLIR recording, converted radar lv1 files to netcdf, checked that instruments,
		backups and cron jobs are running.
	08:44: Checked and noted down time offsets in time_offsets.txt.
	08:47: Laptop disk space: nimbus: 183 GB, cirrus: 26.9 GB, cumulus: 275 GB.
	Updated station maps, only 3d missing. Changed packing lists, only box of Parsivel missing.
	Measured some salinity boxes from 10:50 to 11:10 so that we have enough boxes for S3d, day2.
	10:37: Deleted GRaWAC lv0 files for 2025-08-24 - 2025-08-25. Cirrus disk space: 105 GB
	Ice station 3d, day 2.
	MWR TB quicklooks: 2025-08-25 11 UTC onwards: The relative humidity sensor of LHUMPRO
		is still broken, but now shows 100 % relative humidity all the time instead of 30 %.
		2025-08-26 13:09 - 13:12: Ship position changed (moved backwards) resulting in strong
		positive TB peak in MiRAC-P. Until 13:19, the ship moved forwards again.
	Digitalised field notes of ice station 3d, day 2: 12_ATMOS/VAMPIRE/
		Ice_Stations/Station3d/Station3d_day2_250827/Ice_Station_3d_Day2_20250827.ods
	Uploaded surface roughness pictures to the respective ice stations.
	21:17: Restarted FLIR recording.
	
- 2025-08-26:
	09:46: Restarted FLIR recording, converted radar lv1 files to netcdf, checked that instruments,
		backups and cron jobs are running.
	09:53: Checked and noted down time offsets in time_offsets.txt.
	09:54: Laptop disk space: nimbus: 197 GB, cirrus: 80 GB, cumulus: 294 GB.
	10:04: Exchanged GoPRO SD card, cleaned lenses, checked heaters and blowers, started resizing
		of images, copied radiosondes to public folder.
	Digitalised field notes of ice station 3d, day 1: public server: 12_ATMOS/VAMPIRE/
		Ice_Stations/Station3d/Station3d_day1_250826/Ice_Station_3d_Day1_20250826.ods

- 2025-08-25:
	08:32: Restarted FLIR recording.
	08:36: Checked whether all instruments, backups and cron jobs are running.
	08:42: Converted radar lv1 to NC for 2025-08-24 using the RPG software.
	08:43: Checked laptop disk space: nimbus: 212 GB, cirrus: 80 GB, cumulus: 332 GB
	08:43: Checked time syncronisation of laptops and instruments, see time_offsets.txt.
	08:51:36: Stopped and restarted GoPro measurements. Exchanged SD cards.
	08:52: Checked blowers and heaters. Removed ice from various power connectors.
	08:56: Copied radiosonde files to the public server and the MyCloud backup NAS.
	Digitalised field notes from station 2d, day 1 (the marine edition): public server:.../
		12_ATMOS/VAMPIRE/Ice_Stations/Station2d/Station2d_day1_250823/
		Ice_Station_2d_Day1_20250823.ods. Also digitalised field notes from station 2d, day 2:
		../Station2d_day2_250824/Ice_Station_2d_Day2_20250824.ods
	11:14:30: Terminated GRaWAC measurements, restarted radar pc software (pw: administrator). 
		Noted the action in UnderwayEvents_VAMPIRE.xlsx and vampire2_instrument_setup.xlsx.
	13:05: Connected a screen to GraWAC because we still didn't have a connection. The radar 
		software just didn't start on the radar PC. Started it manually.
	13:14: Continued radar measurements: GR-2S-12KM-20M_NOSPEC.MDF
	Logged radar outage and restart in vampire2_instrument_setup.xlsx and 
		UnderwayEvents_VAMPIRE.xlsx.
	Entered the times of the above mentioned scans to vampire2_instrument_setup.xlsx and 
		UnderwayEvents_VAMPIRE.xlsx. Had to create a new cell for more HATPRO and LHUMPRO entries
		in vampire2_instrument_setup.xlsx because the other cells seem to have exceeded a max
		character limit.
	16:18: Noticed that GRaWAC seems to have lost connection just a few minutes after measurements
		were continued. Connection loss again at 13:20. Checked whether the blowers of the radar 
		are still on. Blowers are on. The radar software won't have closed itself, right?
	17:12: It turns out that the software was again, whyever, closed. Started it manually yet 
		again.
	18:22: Restarted FLIR recording.

- 2025-08_24:
	- Ship maneuvering to measure in RS site: there was another floe behind us so we couldn't
		maneuver freely to the site where we measured but measured at a distance of around
		5 m where surface looked similar. That spot was measured from 16:14 to 16:17 UTC.
	- HATPRO and LHUMPRO *_EMIS_LONG_V1.MBF started at 15:33. *_VAMPIRE_V1.MBF restarted at 16:30.
	Logged Station 2d events.
	Deleted GRaWAC lv0 data from 2025-08-17 to 2025-08-23 from cirrus. Laptop disk space: 92.6 GB.
	
- 2025-08-23:
	10:20: Restarted FLIR recording. Checked whether all instruments, backups and cron jobs are
		running. Converted radar lv1 files to NC for 2025-08-22 using the RPG software.
	10:33: Checked laptop disk space: nimbus. 237 GB, cirrus: 88 GB, cumulus: 410 GB
	10:35: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	10:42:07: Stopped and restarted GoPro measurements. 
	10:43: Checked blowers and heaters. Blower intakes of radars and MWRs were heavily iced.
	10:48: Started GoPro processing: cirrus:gopro_processing.sh
	Ice station 2d, day 1: Remote sensing site sampling - Marine edition

- 2025-08-22:
	08:27: Restarted FLIR recording. Checked whether all instruments, backups and cron jobs are
		running. The 00 UTC GRaWAC lv1 file from 2025-08-21 has an unusual time stamp in the 
		filename. GRaWAC GPS is back.
	08:41:53: Stopped and restarted GoPro measurements. Exchanged SD cards.
	08:43: Started GoPro processing: cirrus:gopro_processing.sh
	08:43: Checked whether all instruments, backups and cron jobs are running. Restarted FLIR 
		recording. Converted radar lv1 files for 2025-08-21 to NC using the RPG software.
	08:43: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	Digitalised salinity measurements in Ice_Station_3c_Day1_20250816.ods,
		Ice_Station_3c_Day2_20250817.ods and Ice_Station_3c_Day3_20250818.ods.
	
- 2025-08-21:
	09:20: Checked whether all instruments, backups and cron jobs are running. Restarted FLIR 
		recording. Converted radar lv1 files for 2025-08-20 to NC using the RPG software.
	09:21: Laptop disk space: nimbus: 263 GB, cirrus: 106 GB, cumulus: 428 GB.
	09:22: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	09:30: Changed SD-card, checked heaters and blowers, cleaned lenses, started resizing.
	Salinity measurements.
	Measured distances between sensors on the observation decks.
	Finished logging Station 3c events and copied file to 07_IceStation_Events.
	
- 2025-08-20:
	08:45: Checked whether all instruments, backups and cron jobs are running. Restarted FLIR 
		recording. Mobotix lost connection on 2025-08-19 11:51 UTC.
	08:55: Converted radar lv1 files for 2025-08-19 to NC using the RPG software.
	08:55: Checked laptop disk space: nimbus: 280 GB, cirrus: 109 GB, cumulus: 432 GB
	08:56: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	09:03:40: Stopped and restarted GoPro measurements while exchanging the SD card. 
	09:04: Checked blowers and heaters. Lots of icing at bow railing and at the Mobotix sky camera.
		There was ice also inside the housing (water protection should be improved?). Removed ice
		and dried the interior a bit. Disconnected the mobotix camera inside the housing. After 
		reconnecting it, the signal was back.
	09:18: Disconnected Mobotix again because the connector itself is still wet and should be dried
		before using it again. Organised a heat gun / hair drier.
	Copied radiosonde data to the public folder and MyCloud backup NAS.
	Marked the time when Mobotix lost connection in vampire2_instrument_setup.xlsx and 
		UnderwayEvents_VAMPIRE.xlsx.
	10:21: Connected the Mobotix sky cam again. Added that time stamp also to 
		vampire2_instrument_setup.xlsx and UnderwayEvents_VAMPIRE.xlsx.
	Checked out the TB quicklooks: TB jump in K, V band and 243 GHz at 127 downwelling on 
		2025-08-17 19:20 to 19:40 UTC: Sky cleared a bit. LHUMPRO status seems out of the ordinary
		on 2025-08-18 at 15 to 21 UTC. HATPRO weather station detected rain at several occasions
		on 2025-08-18; the day with nice sunny and almost clear sky conditions. 2025-08-17 around
		16 UTC: TB peaks at 53 deg surface obs: Peaks caused by people in the footprint of HATPRO
		and LHUMPRO. Used two GoPro images to mark the current estimate of the MWR footprints.
		Saved the images to 12_ATMOS/VAMPIRE/mwr_footprint/. Note that the size of the ellipses
		indicating the footprint may not have the correct size.

- 2025-08-19:
	08:20: Restarted FLIR recording.
	08:28: Checked whether all instruments, backups and cron jobs are running. Backups of hatpro 
		and lhumpro are not yet completed. Still running.
	08:40: Laptop disk space: Nimbus: Nimbus: 293 GB, cirrus: 61 GB, cumulus: 432 GB. Deleted LV0
		files of GRaWAC from 2025-08-15 and 2025-08-16.
	08:42: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	08:49:45: Stopped and restarted GoPro measurements while exchanging SD cards. Removed ice from
		the GoPro's lens.
	08:50: Checked heaters and blowers. Also, HATPRO and LHUMPRO radomes are iced on the 
		surface-facing side and away from the blowers. Noticed slight sleet precipitation.
	08:55: Tried to carefully deice HATPRO and LHUMPRO with a towel.
	Digitalized Station 3c field notes from days 1-3. Logged Station 3c events except for salinity
		measurements.
	08:56: Started GoPro image processing: cirrus:gopro_processing.sh
	Live cruise report: /12_ATMOS/VAMPIRE/Cruise_report_VAMPIRE.docx. Started filling it.
	14:49: Checked HATPRO and MiRAC-P's radomes again. HATPRO was now blown ice free by the blower.
		Removed the remaining ice using a towel from MiRAC-P's radome. Checked the uSonic-3 and 
		radar alignment whether that truly agrees with the VAMPIRE setup from 2024. They do.
	19:20: Restarted FLIR recording.

- 2025-08-18:
	08:27: Checked whether all instruments, backups and cron jobs are running. Restarted FLIR
		recording. Converted radar lv1 data to nc.
	08:28: Laptop disk space: nimbus: 305 GB, cirrus: 68.4 GB, cumulus: 442 GB.
	08:30: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	08:39: Exchanged GoPRO SD-card, checked blowers and heaters, copied radiosondes to public
		server, and started resizing GoPRO images.

- 2025-08-17:
	08:19: Restarted FLIR recording.
	10:15: Checked whether instruments, backups and cron jobs are running. For unknown reasons, 
		almost all ubuntu terminals on cirrus were/are now powershell terminals.
	10:24: Converted radar lv1 files to NC for 2025-08-16 using the RPG software.
	10:24: Checked laptop disk space: Nimbus: 318 GB, cirrus: 34 GB; deleted lv0 GRaWAC files
		until 2025-08-15 -> cirrus disk space: 91 GB. Cumulus: 460 GB
	10:28: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	10:46:44: Stopped and restarted GoPro measurements while exchanging SD cards.
	10:47: Carefully wiped over the MWR radomes. Checked camera lenses (cleaned sky camera lenses),
		and heaters and blowers.
	10:50: Started GoPro resizing script: cirrus:gopro_processing.sh
	10:51: Copied radiosonde data to the public server and the backup NAS MyCloud.
	Updated MWR and radiosonde-MWR quicklooks in 12_ATMOS/VAMPIRE/quicklooks/. Checked out
		the MWR quicklooks. 2025-08-16 just before midnight: TB jump at 53 deg surface TBs in K and
		V bands (and also 243 and 190 GHz, less visible in other channels): Origin unclear. GoPro
		images do not show a change of the ship's alignment relative to our footprint.
	Ice station 3c, day 2.

- 2025-08-16:
	08:34: Checked whether all instruments, backups and cron jobs are running. Restarted FLIR
		recording.
	08:40: Checked laptop disk space: nimbus: 332 GB, cirrus: 60 GB, cumulus: < 80 GB -> deleted
		radar lv0 files (for MiRAC-A: only for 2025-07-02 to 2025-07-31).
	08:41: Checked time synchronisation of instruments and laptops, see time_offsets.txt.
	08:47:39: Stopped and restarted GoPro measurements while exchanging SD cards.
	08:48: Checked blowers and heaters and cleaned the lenses of the sky camera.
	Added salinity measurements into the digitalised field notes of station 2c:
		Ice_Station_2c_Day1_20250812.ods, Ice_Station_2c_Day2_20250813.ods, 
		Ice_Station_2c_Day3_20250814.ods
	Added RS site and IR target to station map of 2c and Station 2c event logging.
	Ice station 3c, day 1.

- 2025-08-15:
	08:40: Checked whether all instruments, backups and cron jobs are running. Restarted FLIR 
		recording.
	08:47: Checked laptop disk space: Nimbus: 345 GB, cirrus: 86 GB, cumulus: 104 GB
	08:48: Converted radar lv1 files to NC for 2025-08-14 using the RPG software.
	08:49: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	08:58:20: Stopped and restarted GoPro measurements while changing the SD card.
	08:59: Checked blowers and heaters and checked whether the lenses should be cleaned. Only the 
		sky camera was needed.
	09:01: Copied radiosonde data to the public folder and the MyCloud NAS.
	09:02: Started the GoPro resizing script: cirrus:gopro_processing.sh
	Added RS site on drone picture of Station 1c.
	Updated the underway events of all continuously operating instruments: ...07_IceStation_Events/
		Underway/UnderwayEvents_VAMPIRE.xlsx
	Updated MWR and MWR-radiosonde quicklooks in 12_ATMOS/VAMPIRE/quicklooks/.
	Checked out the TB quicklooks. The 127 deg downwelling TBs at G-band nicely show the
		persisting temperature inversion as the emitting water vapour is quite warm in layers
		detected by frequencies in the outer G-band channels. Surface TBs at 53 deg: strong
		TB jump in K and V band on 2025-08-13 18:19 to 18:40: Ship roll angle changed. 
	Created some MWR-radiosonde and ice core results slides: 12_ATMOS/VAMPIRE/
		vampire_overview_results_20250815.pptx
	Discussed the content of the ATMOS contribution of the AC3 post on meereisportal.
	Composed a draft for the AC3 post on meereisportal: 12_ATMOS/VAMPIRE/AC3_PS149_ATMOS.docx
	Salinity measurements of station 2c.
	19:41: Restarted FLIR recording.

- 2025-08-14:
	08:31: Checked time synchronization of laptops and instruments, see time_offsets.txt.
	08:32: Laptop disk space: nimbus: 358 GB, cirrus: 145 GB, cumulus: 131 GB.
	08:37: Checked whether all instrument, backups and cron jobs are running. Converted
		GRaWAC and MiRAC-A lv1 files to NC for 2025-08-13 using the RPG software.
	08:49: Stopped and restarted GoPro obs while exchanging SD cards. Started resizing of
		images.
	08:50: Checked blowers and heaters. A little bit of rain has accumulated on the far end
		of GRaWAC's radomes, gently wiped it away with cloth.
	Ice station 2c, day 3.
	Digitalized field notes of station 2c of all days, logged events except for salinity
		measurements.
	Copied ice station data and photos to NAS at Y:\vampire2\Ice_Stations.
	17:26:50: Terminated standard vampire measurements and started VAMPIRE_HATPRO_EMIS_LONG_V1.MDF,
		VAMPIRE_LHUMPRO_EMIS_LONG_V1.MDF.
	17:32:52: The area we wanted to sample broke off the main floe. Then also a crack appeared 
		right in the area we wanted to sample. Started VAMPIRE_HATPRO_V1.MBF and 
		VAMPIRE_LHUMPRO_V1.MBF.
	Added surface roughness photos from station 1c and 2c to the public folder.
	
- 2025-08-13:
	08:30: Checked whether all instrument, backups and cron jobs are running. Restarted FLIR 
		recording. Converted GRaWAC and MiRAC-A lv1 files to NC for 2025-08-12 using the
		RPG software.
	08:31: Checked time synchronization of laptops and instruments, see time_offsets.txt.
	08:32: Laptop disk space: cumulus: 164 GB, cirrus: 145 GB, nimbus: 371 GB.
	08:45: Exchanged GoPro SD-card, started resizing of images, checked blowers and heaters,
		copied radiosonde files to public server and backup NAS.
	Ice station 2c, day 2.
	Digitalized field notes of Station 2c, day 1. 
	Looked through the TB quicklooks: Downwelling 127 deg G-band TBs are still 
		somewhat noisy. Brief periods when offsets of more than 5 K to previous period exist,
		e.g. 2025-08-11 15-16 UTC -> related to internal calibration? Surface 53 deg TB jump in
		K and V band on 2025-08-12 around 12:00 UTC and 20:00 UTC: Ship position changed.
	
- 2025-08-12:
	08:47: Checked whether all instrument, backups and cron jobs are running. Restarted FLIR 
		recording. Converted GRaWAC and MiRAC-A lv1 files to NC for 2025-08-11 using the
		RPG software.
	08:40: Checked laptop disk space: nimbus: 384 GB, cirrus: 142 GB, cumulus: 171 GB
	08:44:57: Stopped and restarted GoPro obs while exchanging SD cards.
	08:48: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	Scouted for a potential remote sensing sampling site. Found one around 100 m away from the aft
		of the ship.
	Ice station 2c, day 1. Sampled a site that is currently not in the MWR footprint.
	
- 2025-08-11:
	08:33: Checked whether all instrument, backups and cron jobs are running. Restarted FLIR 
		recording.
	08:37: Converted GRaWAC and MiRAC-A lv1 files to NC for 2025-08-10 using the RPG software.
	08:41: Laptop disk space: nimbus: 397 GB, cirrus: 148 GB, cumulus: 175 GB
	08:42: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	Digitalized field notes of Station 1c days 1 and 2, logged Station 1c events and copied them
		to 07_IceStation_Events, measured salinity and digitalized those as well.
	Salinity measurements.
	Packed MaMe20.
	Added remote sensing site location to the station maps where missing. 1c currently not possible
		because accessed by someone else. Also added the location of the IR targets in the map.
	Checked the MET quicklooks for times when which T2m sensor looks more reliable:
		LHUMPRO: 2025-07-04 06:55:33 - 2025-07-04 18:01:58, 
					2025-07-22 19:31:00 - 2025-07-24 00:00:00,
					2025-07-31 18:05:00 - 2025-08-01 20:30:00,
					2025-08-03 09:54:00 - 2025-08-03 16:44:00,
		HATPRO:  2025-07-04 18:01:58 - 2025-07-06 08:03:00, 
					2025-07-06 08:03:00 - 2025-07-22 19:31:00,
					2025-07-24 00:00:00 - 2025-07-31 18:05:00,
					2025-08-01 20:30:00 - 2025-08-03 09:54:00,
					2025-08-03 16:44:00 - now
	Updated the MWR TB histogram plot for all current ice stations (including revisits). Will be 
		reorganised to a 4x3 panel plot soon. Saved to ...12_ATMOS/VAMPIRE/quicklooks/mwr/tb_hist/.

- 2025-08-10:
	09:32: Checked: instruments, backup, cronjobs running. Restarted FLIR, converted radar
		lv1 files to nc.
	09:39: Laptop disk space: nimbus: 410 GB, cirrus: 153 GB, cumulus: 179 GB.
	09:40: Time offsets, see time_offsets.txt.
	10:31:50: Stopped and restarted GoPro measurements to exchange SD cards.
	10:33: Checked heaters and blowers of the radars and radiometers.
	10:34: Executed GoPro processing: cirrus:gopro_processing.sh
	
- 2025-08-09:
	08:30: Checked: instruments running, backups, cronjobs. Restarted FLIR, converted radar
		lv1 files to nc.
	08:30: Deleted GRaWAC lv0 and NC data from 2025-08-04 to 2025-08-08. Laptop disk space now:
		nimbus: 423 GB, cirrus: 157 GB, cumulus: 181 GB.
	08:42: Checked time offsets, see time_offsets.txt.
	08:50: Exchanged GoPro SD card, checked heaters and blowers, copied radiosonde files.
	
- 2025-08-08:
	09:52: Checked whether all instruments, cron jobs and backups are running. Restarted FLIR 
		recording.
	10:00: Converted lv1 radar files to NC for GRaWAC and MiRAC-A for 2025-08-06 using the RPG
		software.
	10:00: Checked laptop disk space: nimbus: 436 GB, cirrus: 90 GB, cumulus: 193 GB
	10:02: Checked laptop and instrument time synchronisation, see time_offsets.txt.
	10:08:57: Stopped and restarted GoPro measurements. Exchanged SD card.
	10:10: Copied radiosonde files to public server and to the NAS backup.
	Noted times when radiometer measurements were started and terminated on 2025-08-06 in 
		vampire2_instrument_setup.xlsx.
	HATPRO calibration test obs on cold load: 2025-08-06 16:28:21 - 16:29:34
	LHUMPRO calibration test obs on cold load: 2025-08-06 16:52:08 - 16:53:36 and
		17:05:04 - 17:06:10
	Digitalized salinity measurements and completed logging events of station 3b.

- 2025-08-07:
	08:33: Checked whether all instruments, backups, cron jobs are running. Restarted FLIR 
		recording. All laptops went into locked mode. Blocked Windows updates for another 5
		weeks.
	08:43: Checked laptop disk space: nimbus: 451 GB, cirrus: 113 GB, cumulus: 214 GB
	08:44: Converted lv1 radar files to NC for GRaWAC and MiRAC-A for 2025-08-06 using the RPG
		software.
	08:46: Checked laptop and instrument time synchronisation, see time_offsets.txt.
	08:53:23: Stopped and restarted GoPro measurements while exchanging the SD card.
	08:54: Checked heaters and blowers of the radiometers and radars and checked whether the
		lenses require cleaning. They don't.
	08:56: Started resizing GoPro images: cirrus:gopro_processing.sh
	08:58: Copied radiosonde data to the public folder and the NAS system.
	Updated HATPRO-only retrieval training data (included more elevation angles for BL-scan
		products, added specific humidity) to create HATPRO only retrieval products for IWV,
		LWP, temperature, absolute humidity and specific humidity (prw, clwvi, ta, hua, hus),
		and the boundary layer scan temperature profile (ta_bl).
	Compared the performance of the MWR synergy with the HATPRO only retrieval. Plots saved to
		...12_ATMOS/VAMPIRE/quicklooks/radiosonde_mwr_comparison/.
	Implemented LWP time series in the MWR-Radiosonde composit. Plots saved to ...12_ATMOS/
		VAMPIRE/quicklooks/radiosonde_mwr_composit/.
	22:15 - 22:45: Nice virga event (GRaWAC, MiRAC-A and radiosonde (down to 19 % relative humidity
		between 0 and 2 km) and clear aliasing effect in GRaWAC.

- 2025-08-06:
	12:22: Checked whether all instruments, backups and cron jobs are running. Restarted FLIR 
		recording. GRaWAC: lv1 file is missing for 2025-08-05 08:00.
	12:28: Converted lv1 files of GRaWAC and MiRAC-A to NC for 2025-08-05 using the RPG software.
	12:31: Checked laptop disk space: nimbus: 91 GB, cirrus: 116 GB, cumulus: 214 GB
	12:33: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	12:44: Copied radiosondes to public server and backup system.
	Digitalized filed notes of Station 3b, day 2 and 3. Logged Station 3b events except for salinity
		measurements.
	Prepared for calibration: Stopped HATPRO and LHUMPRO measurements. Flipped them. Loaded the
		dewer with liquid nitrogen, measured its temperature (when filling up, after filling the
		large radiometer target (HATPRO), after filling the small radiometer target (LHUMPRO), 
		after filling the radar target). Mounted the calibration tables to the radiometer stands
		(HATPRO: as usual: LHUMPRO, rotate the table by 90 deg and put a screen cardboard box on
		it).
	Calibrated HATPRO, LHUMPRO, GRaWAC, MiRAC-A. LHUMPRO required two attempts. The second attempt
		was the better one (less noisy test measurements onto the cold target in the G-band). 
		MiRAC-A required 3 attempts to obtain a decent calibration. The first two were likely 
		corrupted by the metal bar of the calibration target table being slightly in the receiver
		field of view.
	Performed a longer surface EMIS scan with HATPRO and LHUMPRO to sample the region of the ice
		we marked before.
	21:38: Restarted FLIR recording.

- 2025-08-05:
	08:37: Checked: instruments, backups, cronjobs running. Restarted FLIR, converted radar lv1 data.
	08:38: Laptop disk spaces: nimbus: 105 GB, cirrus: 146 GB, cumulus: 233 GB.
	08:39: Checked time offsets, see time_offsets.txt.
	08:56: Exchanged SD cards, started resizing.
	08:56: Copied radiosondes to public server and backup.
	Finished digitalizing field notes of Station 2b day 2.
	10:33: Quite substantial reflectivity differences between MiRAC-A and GRaWAC. MiRAC-A sees more
		than 0 dBZ while GRaWAC shows nothing?!
	Updated the ice station field notes template Ice_Station_Xa_DayD_yyyymmdd_Template.ods.
	Digitalised field notes of Station 2b, day 3: Ice_Station_2b_Day3_20250801.ods
	12:23: Corrected GoPro alignment even more.
	Digitalized salinity measurements of Station 2b.
	Digitalized Station 3b day 1 field notes.

- 2025-08-04:
	08:28: Checked: instruments, backups, cronjobs working. Restarted FLIR. Converted radar lv1 data
		to nc. Deleted lv0 and nc files from cirrus from 2025-08-01 to 2025-08-03.
	08:29: Laptop disk space: nimbus: 118 GB, cirrus: 151 GB, cumulus: 248 GB.
	08:36: Checked time offsets, see time_offsets.txt.
	Replaced the station number noted in the digitalised ice station field notes by the event 
		number assigned to each station (13, 16, 18, 21, 25).
	08:41: Stopped and restarted GoPro measurements while changing the SD card. Corrected the 
		alignment (is it really well aligned now?).
	Digitalized field notes of Station 2b day 1 and 2 (except for HydraProbe on day2).
	Ice station 3b, day 1.
	16:17: Restarted FLIR recording.
	Uploaded plots showing MWR-radiosonde composits (IWV, temperature, specific humidity) as well
		as radiosonde-MWR comparison plots to the public server: .../12_ATMOS/VAMPIRE/quicklooks/
		radiosonde_mwr_comparison and radiosonde_mwr_composit.

- 2025-08-03:
	08:37: Checked whether all instruments are running. Restarted FLIR recording. Checked backups
		and cron jobs.
	08:44: Converted radar lv1 files to NC for 2025-08-02 using the RPG software.
	08:46: Checked laptop disk space: nimbus: 131 GB, cirrus: 70 GB, cumulus: 262 GB
	08:48: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	09:02: Stopped and restarted GoPro measurements while exchanging SD cards. Checked blowers and
		heaters. There are some droplets (evtl. frozen) on the MWR radomes. Dried the GoPro lens.
	09:08: Wiped the droplets off the MWR radomes.
	Executed mwr_quicklook.py for 
		2025-07-28 - 2025-08-02. Saved quicklooks to the public server. 
	Looked through the quicklooks. It seems that LHUMPRO weather station measurements are corrupted
		since 2025-08-01 21:00 UTC. 2025-07-31 07 - 11 UTC: EMIS scan obs show strong gradual 
		increase in TBs over time: Sun is again being reflected from the sea ice surface. However, 
		also the vessel moved a bit forward and might have caught a different surface. Clouds also
		slightly thickened (see MiRAC-A quicklooks and GoPro images).
	Logged station 2b events and put them in scientists/PS149/07_IceStation_Events/Ice_Station_2b.
	Measured salinity of station 2b samples. 
	Repaired the ice corer (one blade was lost while coring on ice station 2b, day 3). Rather check
		the screws holding the blade after each ice station.
	14:43: Briefly disconnected the LHUMPRO's weather station and reconnected it, hoping to fix the
		meteo data. After this, LHUMPRO lost connection?? Won't turn on. 
	Turns out that there was water running along the cables into the weather protection (trash bag)
		and now flooded the LHUMPRO power connectors. Dried them together with the electrician 
		Stefan, tested the cable and connected everything again.
	15:31: Turned LHUMPRO on again.
	15:35: LHUMPRO was connected again to host software. Started VAMPIRE_LHUMPRO_V1.MBF.
	16:34: Radar monitoring nicely shows the approaching warm front.
	16:38: Noticed that HATPRO doesn't measure. Connection lost. 
	16:40: Turned HATPRO off. Waited 25 s. Turned it on again.
	16:44: Connection to HATPRO is back. Restarted HATPRO measurements: VAMPIRE_HATPRO_V1.MB
	16:48: Stopped LHUMPRO obs to improve the weather protection of the power connectors again.
	16:50: Deactivated LHUMPRO. Unplugged the device. Improved weather protection.
	16:54: Activated LHUMPRO
	16:58: Activated LHUMPRO obs: VAMPIRE_LHUMPRO_V1.MBF

- 2025-08-02:
	08:37: Restarted FLIR recording.
	08:38: Checked whether all instruments are running. Also checked backups and cron jobs.
	08:45: Checked laptop disk space: nimbus: 144 GB, cirrus: 29 GB, cumulus: 274 GB. Freed some
		disk space on cirrus (deleting lv0 and lv1 NC files from GRaWAC for 2025-07-28 to 
		2025-07-31).
	09:45: Changed GoPro SD card, started resizing images, checked blowers and heaters, cleaned
		lenses.
	09:40: Copied radiosondes to public server and backup.
	10:03: Stopped LHUMPRO measurements to test whether its cable works on HATPRO. Only plugged
		in LHUMPRO's power cable into HATPRO's socket and did not change the blower cables.
		HATPRO started and connected but Noise diodes did not respond and no TBs were displayed
		even after calibration.
	10:18: Restarted LHUMPRO and the measurements: VAMPIRE_LHUMPRO_V1.MBF. However, the blower 
		does not run at full speed (yet?). Checking again after 10:30 when the measurements are
		actually starting. Receiver stability is currently not perfect because the MWR was 
		turned off for some time.
	Checked the HATPRO operating manual
		and found a similar (or the same?) error message concerning the noise diodes: "No
		noise diode response. Calibration terminated!" -> might indicate malfunction of noise
		diode.
	In the RPG radiometer software, manually set the speed and relative humidity threshold of the
		blower again: Control -> Diagnostics.
	Informed the Labor ELO "Hütte" about our cable issue / damage. 
	Tried finding the source of the cable failure. Fuse was blown where the HATPRO radiometer 
		cable was connected. Found that there was water in both Schuko connectors (in the blower
		and the radiometer cables). The radiometer cable was totally soaked while the blower
		cable was only slightly wet (but still too much). Dried both cables and had them checked
		by Stefan from the crew. Replaced one of the Schuko to 3-pin power adapters because it
		was apparently fried. Added some additional weather shielding (trash bag) to the HATPRO
		radiometer and blower cables, as well as to the LHUMPRO radiometer and blower cables.
	11:22: Turned LHUMPRO off to improve the weather shielding of the cables near the sockets.
	11:27: Turned LHUMPRO on again.
	11:30: Turned HATPRO on. It turned on and the host software could connect to the radiometer.
	Adjusted the blower speeds of HATPRO and LHUMPRO manually via the RPG software.
	11:32: Restarted LHUMPRO measurements: VAMPIRE_LHUMPRO_V1.MBF
	11:34: Started some test measurements for HATPRO: VAMPIRE_HATPRO_ZENITH_TRANSIT.MDF
	The relative humidity measurements from LHUMPRO's weather station seem far too low now
		(30 % relative humidity during fog/rain).
	12:38: HATPRO V band now also shows measurements that look okayish but the K band TBs are
		too noisy. That was just because the radiometer wasn't pointing in zenith direction
		but looked horizontally into the atmosphere. 
	12:45: Activated a test zenith measurement VAMPIRE_HATPRO_ZENITH.MDF to check actual zenith
		obs: Looks much better: less noise, TBs within a plausible range.
	Copied ice station photos and surface roughness pictures for stations 1b and 2b onto public server.
	22:53: Restarted FLIR recording.

- 2025-08-01:
	11:22: Checked whether all instruments are running. HATPRO measurements seem to have stopped on
		2027-07-31 18:02:09 (at least the host software indicates no measurements afterwards).
		Again, connection to radiometer was lost. Also checked backups and cron jobs.
	11:36: Deactivated HATPRO and stopped GoPro measurements. Exchanged SD cards. GoPro alignment 
		may have changed while opening the case. The alignment was rather easy to change. Need to 
		tighten the screw a bit more.
	11:37:20: Reactivated GoPro measurements and activated HATPRO.
	11:42: Still no connection to HATPRO. Restarted HATPRO's host software. Nothing.
	11:45: Checked with HATPRO again. Blower is still off. Issue with the cable or is it a software
		issue and the blower is just not on because the radiometer software doesn't tell it to do
		so?
	11:48: Checked laptop disk space: nimbus: 156 GB, cirrus: 80 GB, cumulus: 319 GB
	12:23: Checked time synchronisation of instruments and laptops. See time_offsets.txt.
	Ice station 2b, day 3.
	Connected a screen to HATPRO to check whether we see it activated there. It seems indeed not 
		able to turn on. Manually turned HATPRO off and on again. Still nothing.
	22:53: Restarted FLIR recording. 

- 2025-07-31:
	09:03: Checked: instruments, backups, cronjobs running. Restarted FLIR, converted radar files.
	09:04: Laptop disk space: nimbus: 172 GB, cirrus: 106 GB, cumulus: 342 GB.
	09:05: Laptop time synchronization. See time_offsets.txt.
	09:15: Copied radiosondes to public server and our Backup.
	09:25: Cleaned GRaWAC radome, there were small water droplets accumulating on far side of blower.
	09:27: Changed GoPro SD card, started resizing images, checked heaters and blowers, cleaned lenses.
	09:28: Falling ice on the observation deck since yesterday, should check radomes regularly, there
		are small indents in radiometer radomes. Should also think about calibration soon.
	11:19: Because this year's HATPRO deployed during VAMPIRE is newer than that used last year, 
		the time for mirror adjustment is probably similar to that of MiRAC-P unlike last year when
		MiRAC-P was faster and needed to "wait" for HATPRO by sampling some more. Noticed in a 
		zoomed in time series that LHUMPRO is currently lagging behind. Thus, corrected the 
		VAMPIRE_LHUMPRO_EMIS_V1.MDF, setting the number of samples again to 155 for scan #2.
	11:21: Stopped and restarted LHUMPRO measurements: VAMPIRE_LHUMPRO_V1.MBF
	Updated vampire2_instrument_setup.xlsx in the public folder.
	Ice station 2b, day 2.
	17:35: Restarted FLIR recording.
	
- 2025-07-30:
	08:38: Checked: instruments running, backups running, cronjobs running. Restarted FLIR,
		converted radar data.
	08:38: Laptop disk space: nimbus: 175 GB, cirrus: 112 GB, cumulus: 347 GB.
	08:39: Checked time synchronization. Exchanged GoPro SD card and started resizing of images.
	10:27: Checked blowers and heaters and cleaned lenses.
	10:34: Copied radiosonde files to the public server and the MyCloud NAS.
	Ice station 2b, day 1.

- 2025-07-29:
	08:55: Checked laptop disk space: nimbus: 188 GB, cirrus: 121 GB, cumulus: 359 GB
	09:00: Transferred radiosonde data first to the public server, then to the MyCloud NAS.
	09:00: Checked time synchronisation of instruments and laptops: See time_offsets.txt.
	Digitalised the field notes from station 1b, days 2 and 3: Ice_Station_1b_Day2_20250727.ods
		and Ice_Station_1b_Day3_20250728.ods.
	Digitalised salinity measurements of Station 1b.

- 2025-07-28:
	08:26: Checked whether instruments are running. Restarted FLIR recording. Checked backups and
		whether cron jobs are running.
	08:35: Checked laptop disk space: Nimbus: 201 GB, cirrus: 45 GB, cumulus: 381 GB
	08:37: Created NC files of the radar lv1 files for 2025-07-27 using the RPG software.
	08:38: Deleted lv0 GRaWAC files from 2025-07-25 to 2025-07-27. Deleted the lv1 and lv1.NC 
		files from 2025-07-01 to 2025-07-26.
	08:48: Checked time synchronisation of laptops and instruments. 
	Ice station 1b, day 3.
	12:25: The floe broke apart.
	12:39: Stopped and restarted GoPro measurements when exchanging SD cards.
	12:40: Started resizing GoPro images: cirrus:gopro_processing.sh.
	Logged station 1b events, except for time of salinity measurements, still need to be added.

- 2025-07-27:
	10:32: Unplugged the pyrgeometer fan and instead only plugged in the pyranometer and 
		pyrgeometer sensors.
	11:17: Checked whether all instruments, backups and cron jobs are running. Restarted FLIR
		recording.
	11:25: Remote control of the surface GoPro is working again. No idea why. Stopped measurements
		to exchange SD cards. Peildeck seems to be closed right now (maybe because of the ice 
		falling off the crow's nest?). Restarted GoPro measurements.
	11:26: Converted GRaWAC and MiRAC-P lv1 files to NC for 2025-07-26 using the RPG software.
	11:31: Checked laptop disk space: nimbus: 219 GB, cirrus: 71 GB, cumulus: 406 GB
	11:33: Checked time offsets of laptops and instruments: See time_offsets.txt and 
		time_offsets.ods.
	Ice station 1b, day 2. Measurements as usual + density measurements of snow pit
	17:21: Exchanged GoPro SD cards. For this, manually stopped and restarted the measurements.
		Checked whether lenses have to be cleaned. Checked blowers and heaters.
	17:24: Restarted FLIR recording.
	Summarised the pyranometer and pyrgeometer tests of the past days and sent them to Mario and
		Pavel. 
	Digitalised the field notes from station 1b, day 1: Ice_Station_1b_Day1_20250726.ods.

- 2025-07-26:
	09:00: Disconnected radiation sensors from power.
	09:02: Checked: instruments running, cronjobs running, backups running. Converted radar files.
		FLIR restarted.
	09:02: Laptop disk space: nimbus: 229 GB, cirrus 90.1 GB, cumulus: 419 GB.
	09:05: Checked times. See time_offsets.txt.
	09:23: Exchanged GoPro SD card, started resizing, checked blowers and heaters, cleaned lenses.
	10:03: Activated the broadband radiation power again but disconnected the pyranometer and 
		pyrgeometer sensor and kept only the pyrgeometer fan running.
	Wrote a script that corrects the naming convention of some of the GoPro images before the
		naming convention was set back to the same type used during PS144: 
		correct_filenames_gopro_vampire2.py. Also uploaded it to .../12_ATMOS/VAMPIRE/scripts/.
	Executed correct_filenames_gopro_vampire2.py on cirrus.
	Created a table to note the time offsets of the computers and instruments in a machine readable
		format: time_offsets.ods.
	Ice station 1b, day 1: Snow pit and ice core for temperature, density and salinity profiles.
	14:25: Activated IR targets from the Swiss Gang deployed in the footprint of FLIR for 
		reference temperature targets. They can be used to calibrate the FLIR measurements.

- 2025-07-25:
	08:13: Checked: instruments running, backup running, cronjobs running, FLIR restarted. Converted
		radar lv1 data to netcdf.
	08:14: Deleted grawac lv0 data from cirrus to free up disk space for July 19th - 24th. Laptop
		disk space: nimbus: 243 GB, cirrus 125 GB, cumulus 448 GB. 
	08:28: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	08:35: Exchanged GoPro SD card, restarted measurements and started processing. Checked blowers
		and heaters and cleaned camera lenses.
	10:40: Measured salinity samples of station 3a.
	Completed Event log of station 3a. Added RS site to the drone images of station 2a and 3a.
	Strong snowfall event at 13:15 UTC.
	Executed mwr_quicklooks.py for TB quicklooks using plot_mwr_daily_quicklook for ZENITH and EMIS
		scans for all dates from 2025-07-06 until today. Added them to .../12_ATMOS/VAMPIRE/
		quicklooks/mwr/.
	Looked through the TB quicklooks of HATPRO and MiRAC-P: Weird TB jump at 2025-07-13T10:00:00 in
		both HATPRO and LHUMPRO. Maybe just clouds clearing? Yes, this was caused by clouds 
		clearing over that time. 
		The MiRAC-P 243 GHz outlier on 2025-07-21T19:32 - 2025-07-21T19:39 is an artifact of 
		unknown origin. 
		Also the outliers (positive TB deviations up to > 276 K) of the 185.81, 184.81 and 183.91 
		GHz channels on 2025-07-17 around 11:50 UTC might be a true w.v. signal but could also be 
		an artifact. 
		The strong and long lasting peak on 2025-07-21T01:50 - 2025-07-21T04:10 can be explained 
		by the sun being reflected: Initially, clouds cleared and gave way for direct sunshine, 
		causing a sudden TB increase. Then, as the sun progressed eastwards, the TB anomaly 
		started fading and is almost totally absent again at 04:10 UTC.
	Entered the salinity measurements in the digitalised field notes:
		Ice_Station_3a_Day3_20250722.ods, Ice_Station_3a_Day2_20250721.ods,
		Ice_Station_3a_Day1_20250720.ods
	Looked for the spare pyrgeometer from the Swiss Gang.
	Test setup of the pyrgeometer, which actually also contains pyranometer and is both up and
		downlooking.
	Extracted logged broadband radiation data. Thermal measurements are still quite variable over 
		time. Also voltages are alternating between -30 and +4 mV.
	14:46: Turned off the radiometers and changed the cable connection from S to T. 14:48:30: 
		Pointed the headlamp to our pyranometer to be able to identify whether this is being 
		logged. Recorded data showed that the pyranometer was still correctly logged.
	15:09: Turned off the power supply of the pyranometer and pyrgeometer setup and plugged in the
		TROPOS pyrgeometer again as a final test.
	15:40: Turned off the power supply of the broadband radiation sensors.
	18:22: Turned power back on.
	18:22: Restarted FLIR recording.
	
- 2025-07-24:
	10:25: Checked whether all instruments are running. Restarted FLIR recording. Checked backups.
		Converted radar lv1 files to NC for 2025-07-23 using the RPG software.
	10:35: Checked laptop disk space: nimbus: 255 GB, cirrus: 80 GB, cumulus: 466 GB
	10:38: Checked time synchronisation of laptops and instruments, see time_offsets.txt.
	10:45: Exchanged GoPro SD card. Manually stopped and restarted measurements at the device.
	10:47:00: Restarted GoPro measurements. Started cirrus:gopro_processing.sh.
	10:50: Checked blowers and heaters of MWRs and radars and cleaned lenses where necessary.
	10:57: Copied radiosonde data to the public server and the MyCloud backup NAS.
	Entered Events logs for stations 2a and 3a, except salinity measurement of 3a datetime
		needs to be added later.
	Digitalised field notes from station 3, day 2: Ice_Station_3a_Day2_20250721.ods
	19:10: Restarted FLIR recording.
	Digitalised field notes from station 3, day 3: Ice_Station_3a_Day3_20250722.ods

- 2025-07-23:
	09:16: Checked whether all instruments are running. Restarted FLIR recording. HATPRO live view
		seems to be stuck since 2025-07-22 19:31:43. Restarted the host software. Seems to have 
		lost connection to the radiometer. All other instruments are running.
	09:28: Checked whether backups are running and converted lv1 radar files from 2025-07-22 to NC 
		using the RPG software.
	09:30: Checked laptop disk space: Nimbus: 268 GB, cirrus: 104 GB, cumulus: 486 GB
	09:31: Checked time synchronisation of laptops and instruments. See time_offsets.txt.
	09:51: Raspberry pi seems unable to turn of shutter of GoPro (no bluetooth connection 
		possible). Manually deactivated GoPro, exchanged SD cards. Turned the GoPro off and 
		ejected the battery for a few seconds. Then, tried activating the GoPro again using the
		raspberry pi commands. Nope, failed to connect. Started cirrus:
		gopro_processing.sh
	09:56: Checked HATPRO and LHUMPRO blowers and heaters.
	11:10: Checked the cables and tried pinging HATPRO. In vain.
	11:16: Turned off HATPRO for 25 s and turned it back on.
	11:19: Started VAMPIRE_HATPRO_V1.MBF. Is working again. Woohoo!
	Adapted /vampire-main/src/vampire/quicklooks/mwr_quicklook.py and /vampire-main/src/vampire/
		constants.py for PS149 (defined new class in the latter).
	HKD and MET quicklooks generated and copied to the public server: .../12_ATMOS/VAMPIRE/
		quicklooks/mwr/.
	Created /vampire-main/src/vampire/quicklooks/mwr_emis_hist_stations.py to visualize the TBs of
		EMIS scans during the 3 past ice stations before we destroyed the footprint.
	It seems that the HATPRO EMIS files can also contain a few time steps with the wrong elevation
		angles (e.g., from ZENITH), thus, wrongly sorted into this file. Caught those wrongly 
		sorted data in /vampire-main/src/vampire/io/readers/mwr.py.read_scan.
	21:40: Deep precipitating clouds. Good for GRaWAC-based w.v. profiles?
	21:42: Restarted FLIR recording.

- 2025-07-22:
	08:30: Checked all instruments running, backup running, cronjobs running, converted radar files.
	08:40: Checked time offsets. See time_offsets.txt.
	08:45: Laptop disk space: nimbus: 282 GB, cumulus: 110 GB, cirrus: 492 GB.
	08:55: Changed SD card, checked heaters and blowers, cleaned lenses. However, GoPro doesn't recognize
		its power cable and says it doesn't have any battery left and powered itself off. Cannot be
		turned on again. Checked that cable is working (it is), tried to find different battery to
		try with, didn't find one, then the battery was working again. No data recording between
		08:45 and 09:28 UTC. Checked settings before turning it on again.
	Digitalised the ice station field notes from ice station 3, day 1: 
		Ice_Station_3a_Day1_20250720.ods. 
	Extended the quicklooks of the ice core data using .../
		vampire/quicklooks/ice_cores_quicklooks.py.
	11:11: Polar 5 overpass over the floe.
	Ice station 3, day 3: Snow pit (at rs site and at ridge), temperature core and density profile
		of top 30 cm (ran out of boxes afterwards).

- 2025-07-21:
	08:46: Checked whether all instruments are running. FLIR recording could not be stopped. Checked 
		backups. Checked cron jobs.
	08:47: Converted GRaWAC and MiRAC-A lv1 files from 2025-07-19 to NC using the RPG software.
	08:48: Laptop disk space: nimbus: 295 GB, cirrus: 113 GB, cumulus: 496 GB
	08:50: Checked time synchronization of laptops. See time_offsets.txt.
	09:04: Checked blowers and heaters, cleaned lenses, exchanged SD and started resizing script.
	09:05: Could not stop FLIR recording manually in FLIR app, so had to close the app and stop
		recording like that. Could restart recording after opening the app again.
	09:50: Copied radiosonde files to the public server, then to our backup NAS MyCloud.
	Ice station 3, day 2: Snow pit, temperature/salinity core ...
	14:50: Made daily quicklooks of usonic and parsivel, added them to the public server in
		./12_ATMOS/VAMPIRE/quicklooks/ folder. 
	Started digitalising the field notes from station 2, day 3. Created 
		Ice_Station_2_Day3_20250717.ods using Ice_Station_X_DayD_yyyymmdd_Template.ods. Finished 
		it. Also entered the salinity measurements in the station 2, day 1 and day 2 files:
		Ice_Station_2_Day2_20250716.ods and Ice_Station_2_Day1_20250715.ods.
	Updated the naming of all ice station files, including the template to allow distinguishing
		between the first, second and third visits: Ice_Station_X_DayD_yyyymmdd_Template.ods
		-> Ice_Station_Xa_DayD_yyyymmdd_Template.ods. Added "a" to each station number visited by 
		now.
	Updated /vampire-main/src/vampire/io/readers/ice_stations.py according to the new file names
		and improved error handling for missing date and time values.
	Uploaded the new scripts to generate the quicklooks of the ice station core data to the public
		server: .../12_ATMOS/VAMPIRE/scripts/: data_tools.py, ice_stations.py, 
		ice_station_quicklooks.py; the latter is used to actually create quicklooks.
	Added the quicklook of the ice station core salinity and temperature data to .../12_ATMOS/
		VAMPIRE/quicklooks/.

- 2025-07-20:
	10:49: Checked whether all instruments are running and restarted FLIR recording. Checked 
		backups.
	10:58: Converted GRaWAC and MiRAC-A lv1 files from 2025-07-19 to NC using the RPG software.
	11:01: Checked whether cron jobs are running.
	11:02: Checked laptop disk space: nimbus: 306 GB, cirrus: 115 GB, cumulus: 500 GB
	11:03: Checked time synchronisation of laptops and instruments: See time_offsets.txt.
	11:01: Stopped GoPro measurements and exchanged SD card.
	11:14: Reactivated GoPro measurements and launched cirrus:gopro_processing.sh.
	Ice station 3, day 1: Snow pit, temperature/salinity core, ...
	Digitalised the notes from station 2, day 2. Also had to correct some more formatting issues 
		in the template: Ice_Station_X_DayD_yyyymmdd_Template.ods.
	21:22: Copied radiosonde files from the radiosonde PC to the public server, then to our 
		backup NAS MyCloud.

- 2025-07-19:
	08:38: Checked whether all instruments are running. Checked whether backups are running.
	08:39: Restarted FLIR recording.
	08:48: Generated radar .NC files from the lv1 files.
	08:49: Checked laptop disk space: nimbus: 320 GB, cirrus: 77 GB, cumulus: 516 GB
	08:51: Checked laptop and instrument times, see time_offsets.txt.
	09:18: Stopped GoPro measurements and exchanged SD cards.
	09:22: Restarted GoPro measurements. The remote control from cumulus found 2 bluetooth devices
		and therefore failed initially when trying to set the shutter off. However, for setting the
		shutter on, it then tried both devices and successfully sent the command to one of them.
		The right one, it seems. Launched cirrus:gopro_processing.sh.
	09:24: Checked heaters and blowers of the MWRs and radars and cleaned FLIR, GoPro and Mobotix
		sky camera lenses.
	09:31: Deleted lv0 GRaWAC files for 2025-07-17 and 2025-07-18 to free some disk space on 
		cirrus. Now, 126 GB free disk space available.
	09:51: Started setting up the broadband radiometers for a functionality test in the office.
	Salinity measurements of all samples collected during Ice station 2.
	Finished setting up the broadband radiometer test. 
	Collected remaining broadband radiation data and copied them to the Synology NAS (backup).
	11:36: For sensitivity tests, let my head lamp illuminate the pyranometer. Deactivated the 
		light at 12:00.
	Checked out the quicklooks of the radiation data using bbradiation_quicklooks.py. According to
		this, the shortwave obs strongly changed on 2025-07-15 16:18, which does not agree with the
		time noted when Marcel informed us about the detached sensor. Eventually, there's a 1 h
		time difference? Or the solar irradiance change on 2025-07-15 14:54 marks the failure of
		the metal rod holding the sensor and 2025-07-15 16:18 is the time when we disconnected the
		sensor.
	The tests this morning showed that the sensor is still sensitive to illumination changes as the
		headlamp is recognised.
	14:46: Held my hand over the pyrgeometer for one minute. Repeated at 15:21 when I also pointed
		the headlamp at the sensor again. Also shielded the pyrgeometer from the ventilation. 
	15:28: For 30 s, repeated the experiment: Held my hands (heated up with hot water) over the
		pyrgeometer again and slightly covered the pyranometer with my other hand.

- 2025-07-18:
	08:39: Checked whether all instruments are running. 23.04 GHz TB higher than 22.24 GHz, which
		looks a bit unusual because then again, the 23.84 GHz is lower than both 22.24 and 23.04
		GHz. GRaWAC lv1 data grawac_20250717_030000_P05_ZEN.lv1 is also missing.
	08:43: Restarted FLIR recording.
	09:01: Checked laptop disk space: nimbus: 333 GB, cirrus: 108 GB, cumulus: 544 GB
	09:02: Checked laptop and instrument times, see time_offsets.txt.
	Created lv1.NC files out of the lv1 files for GRaWAC and MiRAC-A for 2025-07-17 (one hourly 
		lv1 file is still missing for GRaWAC).
	09:12: Stopped GoPro measurements and exchanged SD card.
	09:15: Restarted GoPro measurements and executed cirrus:gopro_processing.sh.
	09:16: Checked whether blowers and heaters are working and cleaned lenses of GoPro, FLIR and
		Mobotix sky camera. FLIR was visibly quite dirty.
	Wrote an importer for ice station field note data directly from the files filled out using the
		template Ice_Station_X_DayD_yyyymmdd_Template.ods. Temperature and salinity cores for now, 
		but can easily be expanded to load more data).
	17:18: Restarted FLIR recording.

- 2025-07-17:
	Ice station 2, day 3: Snow pit. Briefly interrupted due to a polar bear alarm (false alarm
		though).
	10:50: Checked instruments and backups, and cronjobs, all running.
	11:00: Deleted grawac l0 data foe July 11th-16th to clear disk space. Now disk space is at
		cumulus: 550 GB, cirrus: 123 GB, nimbus: 338 GB
	11:10: Checked laptop times. See time_offsets.txt
	11:20: GRaWAC is missing file 20250716_190000.lv1, but the lv0 data is there, so it can be 
		recovered.
	With the help of the crew, uninstalled the remaining brackets of the broadband radiation 
		sensors, the cables and the cable box. Brought everything to the A-113 office for drying.
		Later, needs to be sorted and secured for ice transit.
	16:48: Restarted FLIR recording.
	16:49: Stopped GoPro measurements and exchanged SD card.
	16:53: Reactivated GoPro measurements and started the resizing script: cirrus:
		gopro_processing.sh
	Transferred the pictures from ice station 2 to the public server.
	Secured the broadband radiation sensors for ice transit.

- 2025-07-16:
	08:25: Laptop disk spaces: cumulus: 584 GB, cirrus: 77.1 GB, nimbus: 353 GB.
		Time offsets checked, are in time_offsets.txt
	08:36: Instruments are all running, backups checked, cronjobs running. Converted radar files.
	09:00: Flori says that the ATMOS team has one extra radiation sensor, we should ask Sandro if we
		can maybe have that?
	09:30: Changed SD card, resized GoPro photos, checked blowers and heaters, cleaned camera lenses.
		What are the settings should be enabled? 
		>> Time lapse mode, 2 s interval.
	Started digitalising the field notes from ice station 2, day 1: Ice_Station_2_250715_Day1.ods
		on the public folder. Finished it and corrected some more formatting issues in that
		file and in the template: Ice_Station_Fieldnotes_Template.ods.
	Ice station 2, day 2: Snow pit, temperature/density core.
	Checked out options to mount the longwave infrared sensor (pyrgeometer) from TROPOS above
		the crow's nest.
	Started uninstalling the rest of the setup at the bow mast (power and data cables, logging
		PC). Yet to unmount: Cable box, sensor cables, brackets.
	17:32: Restarted FLIR recording.

- 2025-07-15:
	08:45: All instruments are running. Checked heaters and blowers of MWRs and radars. Backups running.
		Cleaned lenses.
	08:50: Changed GoPro SD card. From 2025-07-14 09:02, not time lapse but video was recording, so
		our processing routine doesn't work. Copied video files manually to /.../gopro/
		20250714_video, but we need to figure out if we can convert them to images.
	08:55: Checked time offsets. See time_offsets.txt.
	09:05: Laptop disk space. cumulus: 606 GB, cirrus: 102 GB, nimbus: 366 GB.
	12:25: Stopped GoPro measurements. Manually set the GoPro time again (it resetted). 
	12:31: Restarted GoPro measurements.
	Ice station 2, day 1: Snow obs and temperature/density core.
	15:00: Marcel informed us that one of the bow mast radiation sensors is no longer attached to
		the bow mast.
	16:15: Investigated what happened to the sensor. The metal rod holding it in place broke. The
		instrument was still held in place by the two cables. Disconnected the sensor (shortwave
		radiation sensor) and also decided to uninstall the longwave sensor.
	17:43: Restarted FLIR recording.
	18:11: Snowfall again.
	Added the end of recording of the broadband radiation sensors to the instrument tables:
		vampire2_instrument_setup.xlsx and UnderwayEvents_VAMPIRE.xlsx.
	
- 2025-07-14:
	08:45: Checked whether all instruments are running: LHUMPRO ambient temperature deviates from 
		the target temperature by > 0.3 K (marked red in the RPG software). Apart from that, all 
		looks fine with LHUMPRO. All other instruments are running.
	08:53: Checked laptop and instrument times. See time_offsets.txt.
	09:03: Stopped GoPro measurements and exchanged SD cards. Cleaned camera lenses.
	09:06: Checked whether backups are running.
	09:07: Checked laptop disk space. cumulus: 618 GB, cirrus: 118 GB, nimbus: 379 GB
	09:09: Restarted GoPro measurements.
	Informed the home-based vampire team of the mobotix issues and how we solved them.

- 2025-07-13: 
	08:27: Restarted FLIR recording.
	08:31: Checked whether all instruments and backups are running.
	08:45: Checked times of laptops and instruments. See time_offsets.txt.
	08:55: Checked laptop disk space: cumulus: 625 GB, cirrus: 127 GB, nimbus: 393 GB
	08:58: Stopped GoPro measurements. 
	09:01: Restarted GoPro measurements and started gopro_processing.sh on cirrus.
	09:01: Checked HATPRO, LHUMPRO and radar blowers.
	09:06: Copied radiosonde files from the public folder to the MyCloud NAS: /.../
		radiosondes/.
	09:30: Collected broadband radiation data and checked the time offset between the radiation
		host PC and stratus. See time_offsets.txt. The broadband radiation data has a gap from
		2025-07-12 16:39:55 to 2025-07-12 23:08:28. Reason unknown.
	12:40-12:50: light snowfall (needles)
	Logged the ice station devices of Station 1 for Ingrid.
	20:02: Stopped and restarted FLIR measurements.

- 2025-07-12:
	10:16: Checked times of laptops and filled out time_offsets.txt on the public server.
	10:27: Checked laptop disk space: cumulus: 632 GB, cirrus: 133 GB, nimbus: 405 GB
	10:35: Stopped GoPro measurements, exchanged SD card. Restarted measurements.
	Extracted broadband radiation data manually.
	Salinity measurements in the dry lab, which is now a wet lab.
	Checked the Mobotix sky camera cable connections at the box again. Eventually, the weather-
		proof ethernet connector is damaged (fried). Took photos of it.
	13:45: Gently wiped over the zenith facing parts of HATPRO's and MiRAC-P's radomes.
	Played hide and seek with the Labor Elo. Found him in the winch control room. Informed him
		about our fried ethernet (RJ45) connector. He and the Sys-Man will first practice the
		replacement with a spare cable of theirs.
	16:52: Mobotix sky cam is back. RJ45 ethernet connector has been replaced by the Sysman and 
		Labor Elo.

- 2025-07-11:
	08:25: All systems except mobotix are running. "No images" and connection to live feed not
		possible.
	08:29: Checked whether backups are running. They are.
	08:37: Checked laptop disk space: cumulus: 647 GB, cirrus: 28 GB, nimbus: 420 GB
	08:48: Disconnected the main ethernet cable inside the mobotix box. Disconnected and 
		reconnected the blue mobotix adapter.
	Ice station 1, day 3 on the ice: Sampled a temperature core and surface scattering layer.
		Rescued a freediving mobile phone.
	12:20: connected Mobotix ethernet cable directly, no ping signal, but don't know if that's
		because of connection or because the converter is somehow needed for recognition
	12:31: Deleted L0 grawac files from cirrus after checking back-ups to free up disk space, now
		cirrus is at 146 GB free.
	12:37: Gave sensor cleaning papers to Aki (Deck's crew), he will clean radiation sensors every
		second day from now on.
	13:23: Transferred field notes of Station 1, day 1 (2025-07-09) into template on public server.
		Put all days of Station 1 into one file or different ones?
	13:30: Put a little photo story in Picture of the Day :) accessed the photos on your camera for
		that, hope that was okay. Yes, that's okay.
	14:40: Got broadband radiation sensor data.
	Lost mobotix sky camera already on 2025-07-09 04:03 UTC. Noted in the 
		IceStationEvents_VAMPIRE.xlsx.

- 2025-07-10:
	08:37: Checked whether all instruments and their backups are running: hatpro, lhumpro, mobotix,
		flir, parsivel, usonic, gopro, grawac, mirac-a: okay
	09:05: Checked time differences. See time_offsets.txt.
	09:14: Checked laptop disk space: cirrus: 63 GB, cumulus: 677 GB, nimbus: 433 GB
	09:19: Copied radiosonde data to the public server.
	09:19: Stopped GoPro measurements. Exchanged SD card.
	09:23: Restarted GoPro measurements and initiated the GoPro processing: cirrus:
		gopro_processing.sh
	09:28: Checked blowers and heaters. All okay. Checked whether surface or sky camera lenses
		should be cleaned. They should. Didn't find the cleaning sheets though.
	09:34: Created netCDF files of the .LV1 data of GRaWAC and MiRAC-A for 2025-07-09.

- 2025-07-09:
	07:40: Checked whether all instruments are running. All is well.
	07:41: Checked time synchronisation.
	07:49: Stopped GoPro measurements. Exchanged SD card.
	07:52: Restarted GoPro measurements.
	08:06: Checked whether the broadband radiation data is properly recorded and checked the time 
		diff. Data are available. Time diff < 1 s. Noted in time_offsets.txt in the public folder.
	08:15: Manually copied the broadband radiation files from stratus to the Synology NAS.
	Ice station preparations were interrupted by a chilling ice bear.
	We went out to sample surface in the MWR footprint: Surface scattering layer properties 
		(snow pit, snow imager, ...?), and an ice core (no temperature profile because we forgot 
		small drill bits).

- 2025-07-08:
	Ice station planning meeting.
	VAMPIRE plan: day 1: footprint coring and snow obs, eventually also another site close by, 
		day 2: salinity measurements and bear guard support, day 3: repeat day 1 where needed.
	08:17: FLIR focus was not properly set up: Manually adjusted the focus using the software:
		Setting gear next to temperature symbol close to the bottom right corner can be used
		to adjust the focus point.
	08:18: Stopped and restarted FLIR recording.
	Made sure that HATPRO and MiRAC-P are running. Also data is available.
	Backup of usonic and MiRAC-A were not working. Reason: mounting the NAS systems was not 
		included in the backup scripts called by crontab on cumulus. Added the mount commands.
	08:24: Nimbus disk space: 459 GB, Cumulus: 704 GB, Cirrus: 93 GB.
	08:27: Checked time synchronisation of laptops: within 1 sec. Also checked raspberry pi
		time diff and noted it time_offsets.txt.
	08:36: Stopped GoPro measurements. Exchanged SD card. Started GoPro processing on cirrus:
		gopro_processing.sh.
	08:40: Restarted GoPro measurements.
	Radio and skidoo introduciton.
	Packed the Pulkas for tomorrow's ice station.
	Defined a new chirp table for MiRAC-A because the polarsternCrui was overall quite noisy.
		Noted the new chrip table, as well as start and stop times for MiRAC-A in the
		vampire2_instrument_setup.xlsx.
	15:18: Stopped and restarted FLIR recording.

- 2025-07-07:
	06:32: Stopped and restarted FLIR measurements.
	06:34: Checked whether all other instruments controlled by cumulus, cirrus and nimbus are still
		running. HATPRO: 1, LHUMPRO: 1, MOBOTIX: 1, FLIR: 1, GRaWAC: 1, GOPRO: 1, USONIC: 1, 
		MiRAC-A: 1. Usonic backup is a bit behind!
	07:04: Stopped GoPro measurements. Exchanged SD card. 
	07:08: Restarted GoPro measurements.
	07:46: Laptops, radar and MWR software times are all within 1 second.
	07:49: Checked laptop disk space and whether heaters and blowers were still working.
	08:30: Copied radiation files from lenti to stratus.
	Migrated the backup of the broadband radiation sensor data to /.../ (Synology NAS).
	Checked out the ice station instruments from and with Gunnar.
	Supervised the cleaning of the broadband radiation sensors. Also found that both are not 
		perfectly aligned:: Portside: outside part lower than inner side. Starboard: same -> 
		extremer view looking towards the bow of the ship from the ship's centre: "/ \"
		Data gap around 12 UTC might be due to cable being disconnected during cleaning and 
		alignment check.
	Parsivel update: COM3 connection doesn't seem to be possible according to our findings and
		Pavel's conclusion. Switched the USB port to COM6 and tried MobaXTerm and Putty connection
		with updated Serialo Session settings (COM6).
	14:28: Stopped and restarted FLIR recording.

- 2025-07-06:
	07:00: Exchanged the GoPro SD card. Stopped and restarted measurements. Initiated file transfer
		via gopro_processing.sh on cirrus. 
	First sea ice was observed at 07:00 UTC.
	07:31 UTC: Started FLIR measurements. Image seems a bit blurry.
	07:40: Flipped HATPRO and MiRAC-P to surface scanning position. 
	08:00: Terminated HATPRO and MiRAC-P measurements to switch MDF / MBF files.
	08:03: Started VAMPIRE_HATPRO_V1.MBF and VAMPIRE_LHUMPRO_V1.MBF, the combined scanning mode.
	Changed Usonic download time to 02 UTC and backup to 04 UTC.
	Cleaned lenses of FLIR, GoPro, SkyCamera
	Backups are working, instruments are all running except for Parsivel and radiation
	Changed Usonic download time to 02 UTC and backup to 04 UTC.
	Corrected the VAMPIRE_LHUMPRO_EMIS_V1.MDF, setting the number of samples again to 175. The
		different "Samples / Pos." numbers between LHUMPRO and HATPRO is due to the longer time
		it takes HATPRO to complete the scan.
	Discussed the use of time servers. Idea to follow VAMPIRE 1: Sync one laptop to ****
		and have all other laptops synchronise that other laptop's time. **** seems harder
		to connect to than .... Only cirrus is able to connect to time servers.
		Both nimbus and cumulus are unable to connect to .... Restarting cumulus 
		also didn't solve the issue.
	Observed the Tara Polar Station docking.
	Installed the broadband radiation sensor power supply and network connection near the bow mast.
	Finished setting up the power supply after obtaining an outdoor multiplug from GUNNAR. Tested
		the remote connection to acquire the data: Use laptop "stratus", connect via ethernet to
		the lenti usb-c to ethernet adapter: Then, connect to **** (written on the
		PC housing and on the lenti adapter), password. ****. Data located in /.../
		radiation_tmp/. We think that no data was logged and suspected that the cron job wasn't 
		running. Took the small computer to the lab and investigated whether cron was installed.
		There's no full Windows Subsystem for Linux on that PC but Cygwin64, which features an
		alternative. Had trouble finding out whether the cron job was running. "cronevents" 
		eventually revealed that the cron job is actually working. Brought the PC back to the bow
		of the ship.
	Stratus time diff (which is synched to ...): 6 s
	15:25: Stopped and restarted FLIR measurements.
	15:30: raspberry pi - cirrus time (synched): 15:33:00 - 15:31:07: 113 s
	Time offsets will be documented in time_offsets.txt!

- 2025-07-05:
	Installation of radiation sensors at mast, mast will be installed at bow in the afternoon
	Exchanged GoPro SD card, stopped and restarted GoPro measurements.
	Adapted cirrus gopro_processing.py. Added daily folders.
	Checked the measurements. Checked if the GoPro file transfer was complete. Checked all 
		backups.

- 2025-07-04:
	Started LHUMPRO zenith measurements (VAMPIRE_LHUMPRO_ZENITH_TRANSIT.MDF) at 6:55 UTC
	Started Mobotix at 8:10 UTC
	Back-up of HATPRO, LHUMPRO, MiRAC-A, GRaWAC, Mobotix, USonic running: grawac backup:
		cirrus: backup_grawac.sh, called by cronjob at 03:30 UTC. Backups of HATPRO,
		LHUMPRO, MOBOTIX (and FLIR): nimbus: make_vampire2_backup.sh, called by
		cronjob at 02:20 UTC.
	Changed time servers to ... on all 3 main campaign laptops. The 
		synchronisation sometimes failes.
	Check if cronjob on cirrus and cumulus is working
	Problems: 	- cumulus and nimbus are not syncing to the ship time server arktus
			- where do radars and radiometers get their times from? turn GPS sync on of keep off?
			- parsivel not working
	Setting up the GoPro time lapse. Then, the commands can be found in
		/.../gopro/command/. If bluetooth connection between raspberry pi and GoPro is not
		possible, check manually if GoPro is on.
	Changed VAMPIRE_LHUMPRO_EMIS_V1.MDF samples/pos. from 175 to 155
	Fixed parsivel data connection issue at 9:15 UTC
	Parsivel's status inquired via MobaXTerm's serial session + "CS/L" typed into the empty 
		terminal has a time stamp which is slightly ahead of the ship's time (30s).
	Found the SD cards, rescaling the GoPro images on cirrus: gopro_processing.sh
	Started HATPRO zenith measurements (VAMPIRE_HATPRO_ZENITH_TRANSIT_WITH_BL.MDF) at 18 UTC
	Asked Ingrid to add Linnu as editor for all devices on registry
	Restarted GoPro at 17:44 UTC.
	
- 2025-07-03:
	Opened the Parsivel box to check if everything's okay there (control LEDs blinking green
		and yellow). Looks okay.
	Checked out FLIR settings. Apparently, 1 sec. Runs for two days. Okay?
	Mounted the NAS systems (Synology and Mycloud) to the campaign laptops.
	Checked the time synchronisation servers of the campaign laptops: Nimbus: now set to 
		****. Also set cirrus to that time server.
	Created a new archive script for the Mobotix skycam images: nimbus pc:
		archive_camera_ps149.sh based on ./archive_camera_ps144.sh. In archive_camera_ps149.sh,
		adapted the prefix for ps149.
	Mounted the NAS also to all other campaign laptops. Except stratus.
	Paused Windows updates for the longest possible period. Until 2025-08-07.
	Tried connecting the Parsivel to cumulus instead of nimbus using Putty. Didn't work.
	Connected to Ultrasonic usonic with user, pw: service, 8189035. Worked but don't know what
		to set up here.
		
- 2025-07-02:
	Boarded Polarstern.
	Helped setting up the instruments: cable management, get liquid nitrogen, fill calibration
		targets, calibrated G-band and W-band radar. Started GRaWAC (gr-2s-12km-20m) and MiRAC-A
		(wr-2s-12km-20m) measurements. Got some more liquid nitrogen (filling up the second
		container took quite some time because the filter nozzle was completely iced. just
		unscrew the filter and you're good to go). Calibrated HATPRO and LHUMPRO. Pavel
		showed me some solar/ir radiometer setup steps.
	Problems: Parsivel data connection not established. Liquid nitrogen container missing or 
		locked into one of the big containers.
	Connection to Synology NAS could not be established. Solution: Synology NAS just wasn't 
		activated.
