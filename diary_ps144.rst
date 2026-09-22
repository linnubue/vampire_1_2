Diary
=====

The diary lists events and activities for each cruise day. These could include:

- **Instruments**: instrument issues and status
- **Operations**: in situ activities and calibrations
- **Science**: interesting observations
- **Weather and sea ice**: significant weather events or special sea ice conditions

.. image:: img/data_availability.png
  :width: 500
  :alt: Data availability

2024-08-08
----------
set up radiometers and radars, FLIR, weather stations, connected radiometers 
and radars to power (except MiRAC-A), HATPRO blower not working properly 
(only weakly), 16:15: first calibration of MiRAC-P but 183er did not work 
(only 40 K when directed to the cold load), thus we performed a second 
calibration of only this band. Got radiometer screws from workshop on board 
(30 mm) because ours were a litte short. Tested that G-Band radar fits into 
box with Ronden (no need to remove them for freight back). We plan to put 
boxes in boxes and need to find a place to store them during the cruise. 
Radisondes are still on working deck. Note down IP addresses of radars! 
Software on GRaWAC does not start automatically, but we could access it with 
monitor and mouse ( would be nice to have battery powered monitor!). Parseval 
installed, but too much vibration, we need to shorten the poles by 60 cm! 
There are not enough outside power plugs, can we use a Mehrfachstecker? 
-> check power consumption of instruments

2024-08-09
----------
Preparations. Ca. 10:15 start calibration of HATPRO, measured temperature of 
the nitrogen: 78.5 K (calculated pressure using link from Mario). after first 
calibration attempt 2 K offset when observing cold load but we also did not 
select the correct target. Doing a second calibration with different software 
version and correct choice of target gives very good calibration results 
(measurements of cold load are super close to 78.5 K)

- Calibration GRaWAC: 14:40:12 UTC
- Calibration MiRAC-A: 14:19:57 UTC

- Started Ultrasonic at 16:38:52 UTC

2024-08-10
----------
Preparations. First sun photometer scan at 21:15 LT. Started HATPRO 
(2024-08-10 22:30 LT) and MiRAC-P (2024-08-10 00:00 LT) scans. Both instrument 
are synchronized every 30 min. The BL scans were set to 1s integration time 
and 10 samples. This could help to identify effect of ship motion.

2024-08-11
----------
- HATPRO/LHUMPRO 07:30 UTC: fixed that LHUMPRO stored data in HATPRO's directory since scan patterns started. Renamed file prefix from EMISSIVITY-SCAN to EMIS-SCAN 

We managed to store all our boxes on blue 
container on Peildeck (Janna put the key in the cabin of her and Linnea). 
we now joined forces with sea ice physics team: daily group meeting at 8:45 
from now on in our office with the view! "Offical" start of measurements 
(see table in other file) of the radiometers, radars and FLIR around 19:00 UTC. 
Issues with Parseval (logs only one value).

- Started FLIR: 19:19 UTC
- started HATPRO: 19 UTC (roughly)
- started LHUMPRO: 19:30 UTC (roughly)
- started MiRAC-A: 18:53 UTC
- started GRaWAC: 18:54 UTC

2024-08-12
----------
first cloud in both radars at 3 UTC!  cleaning of radomes (both radars and 
radiometers) at 11 UTC with water, and in the case of HATPRO with a towel 
(because blower/heater is not working). GRaWAC radar disconnected from computer 
several times and stopped measuring, we changed the network adapter, and kept 
the radar computer open via remote-desktop at all times, is working again from 
17 UTC, changed chirp settings several times during the day. Configured time 
synchronization on raspberry pi. It gets its time from 192.168.211.11 (cumulus). 
GoPro measurements where started but stopped shortly after (realized next day): 
no power (power adaptor is dead). Weather observations: good in the morning 
but then fog and frontal system. Fixed broken power adaptor from GoPro. 
Parseval logger not working properly. Mini-IMU from UB not working, the mini-PC 
does not recognize anything in the USB port. Installed instrument on desk on 
A-Deck in front of DWD office, started test measurements at 13:33, calibration 
at 15:12 at the final position of the IMU, 15:14: started recording data of the
mini-IMU. Exact position needs to be measured (also relative to the 
radiometers!). Raspberry Pi IMU started measurements at 20:34:40

- Started RaspberryPi IMU: 20:34:40 UTC
- Started Mini IMU: 15:14 UTC
- Started GOPro: 12:15 UTC

- GRaWAC: Running: 0-10, 12:33-13, 13:55-14,15:24-16, 16:30: changed network adapter, 16:57-22

2024-08-13
----------
Routine check was at 07:35 UTC. Thomas Rose (RPG) has been on the w-band radar 
and changed the noise threshold to 9 (it was 6). That should be enough. He 
couldn't access the G-band. Routine checks revealed that the screws at the 
poles (ultrasonic, Parseval,FLIR) needed to be adjusted. GoPro seems buggy, 
did not start, removing battery worked: from now on always remove battery 
when exchanging SD cards! Linnea mastered mobotix which is now recording 
reasonable images (cronjob saves the current image to nimbus). Nils mastered 
the Polarstern, good measurements now started at 19:45 UTC. GoPro images are 
rescaled to reduce file size and saved on external hard disk. Created cronjobs 
for radiometers and FLIR to backup every night after midnight to mycloud. 
Mario fixed ultrasonic issues. Parseval still problematic. We discovered issue 
with HATPRO MDBs: measurements take longer than half an hour and then the new 
round is not triggered -> means we have surface observations only every other 
half hour. We tried to fix it by shortening the zenith scan before boundary 
layer scan around 21:30, this needs to be checked tomorrow! First radiosonde
was launched today by DWD, we should do that tomorrow with Christian. 
Discovered that Raspberry Pi stopped logging around 12:56, maybe a terminal
was closed?, restarted logging at 22:15. 17:00 UTC fixed scale of Mobotix 
images to 310-400. 07:30 UTC MiRAC and GRaWAC noise level was changed from 6 to 9.

- started mobotix: 17:00 UTC
- GRaWAC: Running: 7:09-24:00, 7:30 changed noise level to 9
- in the evening around 19 UTC first sight of sea ice

2024-08-14
----------
**Routine check (07:30 UTC)**

- **outdoor**

  - GoPRO was full, only 12 hours fit, and we should change it 3 times daily. 
  - Cleaning of radomes
  - Fixed screws of sky camera. 
  - All other things are ok. 

- **indoor**

  - laptop storage: cumulus 585 GB free, nimbus 24 GB free, cirrus 50 GB free. 
  - Backups: **no backups for** MiRAC, GPS stream, angles stream, parsivel, ultrasonic, imupi (raspberryPi), grawac, hatpro (only directories exist for days), lhumpro (no backup), mobotix. **backups present for** FLIR. **unclear** GoPRO, how we handle radiosondes later. 
  - time synchronization of laptops is ok. time synchronization of pi with cumulus is ok. 
  - Instrument performace: 
    - GRaWAC: OK
    - MiRAC-A: OK 
    - HATPRO: OK
    - LHUMPRO: 340 GHz channels noisy, all others look stable
    - LHUMPRO finishes scans 4 min before 00/30, HATPRO 2 min before 00/30 -> they are not synchronous
    - Mobotix: images are ok and saved, scale had to be adapted (we only save plots at this time, no IR TB data)
    - FLIR: looks good and is running, maybe 3-4 K warmer TB over ice and water (to be checked once we plot the data)
    - Parsivel: not yet running
    - Ultrasonic: no data gets written
    - Raspberry: Pi Ok
    - IMU: not checked
    - Polarstern stream: gps is ok, angles failed and unclear why
    - GoPRO: OK and SD exchanged

- Started parsivel: 15:09:30 UTC

LB: 14 UTC: GRaWAC spectral compression disabled

NR: Mobotix images not saved after 08 UTC. Tried to fix with cronjob, but it does
not seem to start. Manually running the bash script for saving images works.

NR: Tried to run crontab with sudo to backup FLIR, LHUMPRO, and HATPRO. Started it
with hourly backup to see if it works. One script for the three instruments.

**Changing MDF of MWRs**: HATPRO takes longer for the scanning a 30 min batch
than LHUMPRO. With the script ``mwr_sync.py`` we found the reason for this 
from observations on 2024-08-14 00 to 12 UTC. 
Short scans (all but zenith scans) randomly take multiples of 10 s longer for 
HATPRO. For LHUMPRO, the scans mostly take as long as specified. The mirror 
adjustment, i.e., the time during scans is about the same. As we do not know 
which scans are causing this problem and when, we decided to change two things:

1. Both radiometers: Remove the intermediate atmospheric scan between the emis 53 deg scans and fill it with emis 53 deg scans.
2. LHUMPRO: Increase the duration of the surface scans by 20 s.

Previous:

- **surface HATPRO**: 53° (15s), 127° (70s), 53° (15s), 127° (70s), 53° (15 samples at 53° and 70 samples at 127°, 1s integration time)
- **surface LHUMPRO**: 127° (15s), 53° (70s), 127° (15s), 53° (70s), 127° (15 samples at 127° and 70 samples at 53°, 1s integration time)

New:

- **surface HATPRO**: 53° (15s), 127° (155s), 53° (15 samples at 53° and 155 samples at 127°, 1s integration time)
- **surface LHUMPRO**: 127° (15s), 53° (175s), 127° (15 samples at 127° and 175 samples at 53°, 1s integration time)

Additionally, the final short zenith scan that should fill up the 30 min batch
was increased from 180 s to 240 s, because there seems to be enough buffer 
(currently 200 s for LHUMPRO and 120 s for HATPRO). The changes made here 
should make both MWRs end at about the same time, 60 - 120 s before the 30 min
are over.

The new definitions are named ``VAMPIRE_*_EMIS_V1.MDF`` and ``VAMPIRE_*_V1.MBF``.
They are started at 22:30 UTC, without causing a gap in the previous definition. :-)

2024-08-15
----------
**Routine check (13:30 UTC)**

- **Indoor**

  - laptop storage: cumulus 510 GB free, cirrus 26 GB free, nimbus 29 GB free
  - instrument storage: raspberry pi 7.9 GB free
  - data written to backup: not working yet, we do it manually
  - Instrument performace: 
    - GRaWAC: OK, did not measure during night due to software failure (lost connection to radar)
    - MiRAC-A: OK 
    - HATPRO: OK
    - LHUMPRO: OK
    - LHUMPRO and HATPRO likely synchronization improved, maybe adapt last zenith scan of HATPRO to be shorter
    - Mobotix: images are ok and saved, but unrealistic mean temperature 
    - FLIR: looks good and is running, still 3-4 K warmer TB over ice and water
    - Parsivel: writes csv files
    - Ultrasonic: writes files
    - Raspberry Pi: Ok
    - IMU: not checked
    - Polarstern stream: gps and angles are running
    - GoPRO: OK and SD exchanged

We **lost all raspberry pi data** until 2024-08-15 12 UTC while moving data to cumulus and deleting files before setting the correct time.

Polarstern backup hard drive (15 TB) available on cirrus.

- No sonde, problem with radiosonde software (only DWD sonde available for 12 UTC)

2024-08-16
----------
- Date of first ice station!

**Routine check (06:30 UTC)**

- **Indoor**

  - laptop storage: cumulus 496 GB free, cirrus 16 GB free, nimbus 17 GB free
  - instrument storage: raspberry pi ?
  - data written to backup: crontab backup of: FLIR, hatpro, lhumpro (nimbus), motobix and imu not yet; mirac-a, ultrasonic (cumulus), parsivel and dship not yet, Mario is working on backup of grawac onto ship
  - Instrument performace: 
    - GRaWAC: OK, did not measure during night due to software failure (lost connection to radar); stopped at 23:35:27 due to radar software stop
    - MiRAC-A: OK 
    - HATPRO: OK
    - LHUMPRO: OK
    - LHUMPRO and HATPRO likely synchronization improved, maybe adapt last zenith scan of HATPRO to be shorter
    - Mobotix: images are ok and saved, but unrealistic mean temperature 
    - FLIR: looks good and is running
    - Parsivel: writes csv files
    - Ultrasonic: writes files
    - Raspberry Pi: Not writing
    - IMU: OK
    - Polarstern stream: gps and angles are running
    - GoPRO: changed at 6:45 UTC, OK

LB: 6:30 UTC: changed Mobotix temperature settings, maybe now more realistic temperatures, time calibration mini-IMU
liquid drops on HATPRO radome, ask Pavel again for blower infos

MWRs at 11:35 UTC: started surface-only scan at 53° incidence angle to help
define footprint center location from people passing through the footprint.
Continued with regular program at 12:30 UTC 

- 06:45 UTC: calibrated time of mini IMU
- 11 UTC. grawac and mirac chirp changed to ice station chirp, then changed back to cruise chirp setting
- No sonde due to software issue (also no DWD sonde due to software issue)

2024-08-17
----------
- **Indoor**

  - laptop storage: cumulus, cirrus, nimbus 69 GB free
  - GRaWAC: measurement stopped during night due to software failure on radar; started GRaWAC_PS_CRUISE_NEW_5_NOISE9 at 05:54:00

- 08:45 UTC: discovered frozen drops on HATPRO and used heat gun to remove them

  - no data from mini IMU from yesterday (Aug 16) 7:39 to today 17.8. 8:56, unknown why

2024-08-18
----------
- 0:00 successful radiosonde launch
- 7:20 discovered that there are frozen droplets on all instruments (there was freezing rain), so used heat gun to remove them
- stoppe HATPRO for dew blower check at 11:30 UTC, restared at 12:30 UTC (and again at 14:10 for 30 min)

- GRawac Running: 07:00-08:00, 09:09-10:00, 12:18:13:00, 13:30: restarted radar PC and hardware, 13:58-24:00

2024-08-19
----------
- 0:00 UTC: no radiosonde launch (DWD sonde problems)
- 07:35 UTC: radome cleaning of HATPRO (during zenith scan)
- 03:00 UTC: for unknown reasons mobotix changed itself to default settings 
- 12:30 UTC: interrupted HATPRO to unmounted heater for maintenance
- 13:00 UTC: restarted HATPRO
- 12:50 UTC: interrupted MiRAC-P to remove standing water inside the blower
- 13:30 UTC: restarted MiRAC-P
- 17:00 UTC: logging of ship IMU data failed
- Radiosonde at 00 UTC failed

2024-08-20
----------
- around 1:00 UTC - 7:00 UTC: no rasperry pi IMU data
- 08:30 UTC: switched off HATPRO to reconnect the heater
- 09:00 UTC: HATPRO running again, for the first time with blower on max speed. this can be seen in data clearly
- 11:05 UTC: removed droplets on LHUMPRO radome
- 13:30 UTC: COM-Port stream of ship caused problems with mouse on cumulus. MiRAC-A, parsivel, and raspberrypi stopped for about 1 hour. Trying to find a solution for ship streams, maybe on another laptop or with reduced data frequency.
- 15:00 UTC: Removed the 25° and 155° from EMIS-SCAN (assuming 0 is nadir and 180 is zenith) for HATPRO/LHUMPRO, because railing affected the 25° downward scan. Also, increased ZENITH-SHORT (final zenith scan) by 30 s to 270 s.
- The ship stream logger for angles moved from cumulus to stratus laptop, because it causes problems with the mouse on cumulus. THe gps stream remains on cumulus, because stratus only has one COM port.
- additional sonde at 18 UTC

2024-08-21
----------
- morning routine check: no cleaning of radomes needed (blower is fixed now!), checked screws, cleaned lenses
- GoPro did not record between 20.08.24 16:40 UTC and 21.08.24 around 07:10 UTC because it had not been properly connected to power cable
- JR did GAIA weekly tasks
- manually started backups on Cumulus, as it was restarted yesterday the Backup had to be mounted again 
- sometime during the night GRaWAC stopped working

2024-08-22
----------
- 6:30 UTC restarted GRaWAC
- 9:50 UTC GRaWAC stopped again, we now assigned the ports on the Radar computer new and restarted measuring at 11:50 UTC
- 10:00 UTC: stopped FLIR camera
- 10:31 UTC: restarted FLIR camera
- 11:30 UTC: trying to restart FLIR camera without showing live image (planned)

  - Test for one hour (11:41 UTC to 12:41 UTC): no displaying of live images (new setting). The duration displayed was exactly 1h, matching the 3600 frames. We found after 60 min an offset of about 40 s (FLIR time is behind GoPro time). Beginning is OK.
  - Test for one hour (12:42 UTC to 13:43 UTC): display live images at 30 Hz (as before). first write to RAM of computer and then to file (new). We found after 60 min an offset of about 38 s (FLIR time is behind GoPro time). Beginning is OK. 

- 13:47 UTC: FLIR back to normal operation
- 15:00 UTC: LHUMPRO stopped to exchange heater. The heater likely did not work at all before.
- 15:30 UTC: LHUMPRO back to normal operation, heater works now

After these two tests, we compare the FLIR images with GoPRO. For the previous setting and the two tests.
We find a constant offset independent of the three possible settings. We continue
with the settings of the past days and adjust the FLIR time somehow...

Maybe manually or with template matching (https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html).

- grawac: Running: 06:39 – 09:00, 11:30: reconfigured COM ports, 11:50-15, 16:30-16:53, 17:19-17:23, 17:25: restarted radar PC, 17:28-21:07

2024-08-23
----------
- daily routine, no need to dry radomes
- drizzle/rain, sysyphos work to clean lenses
- 11:00-11:30 UTC: stopped LHUMPRO for maintenance
- 11:00 removed heater of HATPRO temporarily to get rid of the water inside the blower, needs to be monitored! -> this is also visible in the data: could it be that prior to this the blower blowed humid air above the radom? 
- got in contact with the FLIR company to try whether they can do something about the timestamp issue  
- 13:50 UTC some snow(like)! Check Parsival for signal tomorrow!  

2024-08-24
----------
- everything worked today.

2024-08-25
----------
- daily checks are OK
- 9 UTC: RaspberryPi lost connection in the night. Restarted the script with nohup now to avoid this.
- around 2 UTC: GRaWAC stopped working and got restarted at 06:30 UTC.
- at 15:20 UTC: new chirp and MDF for GRaWAC with lower total integration time and lower resolution to fit better with MiRAC time grid -> but afterwards GRaWAC did not work anymore

- grawac: Running: 0-2, 6:37-15, afterwards weird signal with noise and bad chirp settings

2024-08-26
----------
- GRaWAC did not work most of the day, only at 17:19 UTC we could start a recording (we were in touch with RPG)
- got reply from FLIR to use different settings, stopped recording at 10:45 to change settings and restarted at 10:50 UTC with new settings
- additional radiosonde at 18:00, 21:00 UTC because of warm air advection
- checked new FLIR settings, now timestamp is correct, that means the first two weeks cannot be used directly but need (manual) correction, now the caveat is that we have to restart the measurements by hand. We try to set them to a large number of frames and then restart every day twice. 
- got information from people in Ny-Alesund that they measure high aerosol (plume of volcanic eruption on iceland)? These air masses might be reaching us as well

- Additional radiosondes: 18 and 21 UTC

- grawac Weird settings until 14, running: 14:54-15, restart PC, 17:19-23

2024-08-27
----------
- radiosondes at 00:00, 03:00 and 09:00 UTC because of warm air advection
- several problems of GRaWAC (software on radar pc always stops)
- both blowers had collected some water so we cleaned them around 07:15 UTC
- freezing rain during the night led to large pieces of ice falling on A-Deck and Peildeck and thus on our radoms therefore we decided to cover them with plastic bags and cardboard, stopped measurements at 10:05 (also of radiometers), we then restarted radiometer measurements at 11:30 UTC to have at least the surface scans, at 11:40 we changed that to emissivity measurements only (EMIS_ONLY.MBF)
- took off the cover of radiometers and radars at 18:45 UTC and restarted the measurement of MiRAC-A, changed radiometers to usual scanning routine

2024-08-28
----------
- accidentally deleted go pro images from Aug 27 7:00 - 17:00
- calibrated time of mini IMU at 19:10 UTC, there might be an offset before that because the time was not correctly synchronized to the ship server

2024-08-29
----------
- 12:22 mirac-a started with new chirp setting that is parallel to grawac's chirp setting (wr-2s-20km-20m)
- 12:30 adjusted grawac's chirp settings: chirp 2 changed resolution from 14.4 to 23.5 and vmax from 2.5 to 3.4 so that (hopefully) we have no Doppler spectra aliasing

2024-08-30
----------
- 6:44 UTC calibrated time of mini-IMU
- did measurements with Hydra Probe around 8:30 UTC until around 9:00 but the ship had moved, so likely we are not in footprint, but still
- at 13:25 we stopped the X-band ice radar to check whether that can explain the weird signal we see in MiRAC-A but that did not resolve anything

2024-08-31
----------
- at 0 UtC (when the sonde was started) it started to snow (big flakes around 1 cm!), would be interesting to see in Parsivel, radars!)
- 8:10 UTC calibrated time mini-IMU
- interesting day in terms of precipitation (schneegriesel, snow, undercooled drizzle...)   
- around 9:00 UTC stopped both ice radars to exclude that they cause weird radar signal
- around 10:30 stopped radar measurements to move MiRAC-A to a new position  
- 10:58 restarted GRaWAC
- 11:09 restarted MiRAC-A
- 12:40 restarted rasperry pi
- 17:15 MiRAC-A stopped for unknown reasons 

2024-09-01
----------
- 08:05 stopped GRaWAC to move MiRAC-A back to original position
- MiRAC-A measurements could not be terminated, finally we managed using the chirp settings on the radar PC itself which have a terminate measurement button
- 10:26 calibrated time mini-IMU
- Unsuccessful attempts to calibrate MiRAC-A, realized only later that the software had stopped already yesterday and that there is some problem with it that could not be fixed until the late evening
- snowfall during the night
- 16:27:12 Parsivel stopped logging because we turned off/on the computer, afterwards we restarted it and it said it was logging but no data was recorded

2024-09-02
----------
- 6:56 calibrated time mini-IMU
- 8:39 restarted Parsivel
- Clear-sky radiosonde at 18 UTC. Some haze/thin fog present close to the ground, but otherwise clear sky.

2024-09-03
----------
- around 6:00 UTC (and later on) new ice in fooprint, frazil, you can see Langmuir circulation! Cool! Also some light snowfall
- there is still some water in the blower of HATPRO, consider drilling another hole
- 10:00 drilled another hole, but did not connect blower properly after, then heater had to be dried and only worked again at 13:15 UTC, zenith measurements in that time period are faulty because there was snow on the radom!
- 06:11 UTC calibrated time mini-IMU 
- Found 20 K offset at 243 GHz compared to clear-sky sonde on 2024-09-02. Unclear why

2024-09-04
----------
- 06:26 calibrated time mini-IMU
- 14:00-15:00 successful liquid nitrogen calibration of MiRAC-A!!! Jippie!!! Afterwards started measurements and the weird artefact seems to be gone! yey! 

2024-09-05
----------
- around 6:15 removed holders of the calibration stand that were still connected to the radar
- 6:19 calibrated time mini-IMU
- 9:30 second starlink antenna was switched on, it is close the our radars
- ice station in the morning, also tried walking through footprint twice
- there were still some weird horizontal and vertical lines in mirac-a, changed chirp settings to polarstern cruise at 12:53
- 14:54 UTC: changed chirp settings (wr-2s-20km-20m) chirp 3: chirp repetition from 2560 to 2048 so that integration time of grawac and mirac-a are closer together, now mirac-a runs without horizontal and vertical stripes
- 15 UTC: Andreas (sysman) asked us not to copy grawac data directly from pc to ship server but to do it via a different pc, so that the internet can run more smoothly. Will do that from tomorrow on, data is still copying right now
- MiRAC-A recorded only LV0 files from 2024-09-05 14:54 UTC until 2024-09-07 12:49 UTC

2024-09-06
----------
- in the night from 5th to 6th there was snow on GRaWAC's radoms as the blower did not work
- 6:47 snow was removed manually 
- 6:50 stopped measurements, turned off GRaWAC outside and on again, blower started to work again and we restarted measurements at 6:55
- 6:57 calibrated time mini-IMU
- 7:50 grawac: changed chirp 3: resolution from 25 to 44.4 m, chirp repetition from 2560 to 4096, Doppler max vel from 1.6 to 2.5, IF low from 799 to 899, total integration time from 1.89 to 1.91 s, noise from 9 to 6
- 7:53 grawac changed noise level back from 6 to 9
- 8:56 mirac changed chirp 1: resolution from 6.7 to 4.2, Doppler max vel from 9.2 to 8.3, Doppler vel resolution from 0.018 to 0.016, IF low from 499 to 400
- 11:15 UTC: stopped all measurements on Nimbus to restart the laptop due to problems reading USB devices.
- 11:30 UTC: restarted all measurements on Nimbus.

2024-09-07
----------
- from 2024-09-05 at 14 UTC to 2024-09-07 at 12 UTC, only LV0 data has been written for MiRAC-A, is it possible to generate the LV1 data from it and where?
- calibrated time mini-IMU (as this is daily routine always done before new recording, this will no longer be written in the diary!)

2024-09-08
----------
- mobotix: only ir from 2024-09-07 18:12 to 2024-09-08 at 6:45
- ice station, walking through footprint in hour 19

2024-09-09
----------
- problems with mobotix: no real image from 2024-09-08 at 8:32 until 2024-09-09 at 13:52; from 2024-09-08 at 8:32 only occasional IR images except between 2024-09-08 at 19:01 and 2024-09-09 at 00:27, 2024-09-09 from 00:40 to 03:03, from 03:09 to 05:09, from 10:13 to 11:11, stable again since 2024-09-09 at 13:52, probably the software doesn't write anything when there's clear sky
- frost flowers! Possibly in footprint around 8:10

2024-09-10
----------
- fixed mobotix color scale at 09:13, reboot at 09:14 to store configuration permanently so that our settings are back in place after outage
- ice station during the night to the 11th
- GRaWAC: no LV1 data at 21 UTC

2024-09-11
----------
- big calibration of HATPRO, LHUMPRO, MiRAC-A and GRaWAC. Stopped LHUMPRO around 11:15, restarted at 14:30, stopped HATPRO around 11:37, restart around 14:30 but data before 15:20 needs to be removed (only then did we put HATPRO back in the correct position). 
-  Needed to fill the bucket with liquid nitrogen twice to be able to fill HATPRO target. 
- First three tries to calibrate LHUMPRO did not work well (test measurements were scattered and off), but when we dried the target radom with hair dryer the test measurements looked good (close to measured temperature of the liquid N2 of about 79 Kelvin, but measurements were tricky because the thermometer was not easily placed in target). However, 340 GHz was still a bit noisy and had slightly lower temperatures than 79 Kelvin. 
- HATPRO calibration worked well, here measured temperature with thermometer of the N2 was a bit lower than in the small target of LHUMPRO
- MiRAC-A: tried twice, still drop at high frequencies in calibration curve
- GRaWAC: worked well
- Bergfest 
- SD card of GoPro was full when exchanged around 23:30, probably about 1 to 2 hour data missing in the night 
- the LHUMPRO file "EMIS_240911_131126" only has 183 GHz receiver running.

GRaWAC calibration: 16:00 UTC

2024-09-12
----------
- thick fog in the morning but only 95% relative humidity according to ship measurements, interesting!
- calibration repeated of MiRAC-A, this time the absorber covered the transmitter when looking at cold target, calibration curve looks fine now! yey! 
- clear sky sonde at 18:00 UTC
- start of ice station in the evening (around 19 UTC), beautiful surface hoar!! A bit foggy in patches (slight fog bow), also diamond dust!   

2024-09-13
----------
- 6:16 UTC realized the mini-IMU has stopped working some time between yesterday morning and now, restarted

2024-09-14
----------
- 7:47 UTC: beautiful frost flowers in footprint! :)
- Had to restart nimbus 

2024-09-15
----------
- Cron did not run after nimbus restart, no mobotix from 14.9. at 12:44 until 15.9. at 8:58.
- mnt/share unmounted, remounted again on 16.9.

2024-09-16
----------
- GPS of GRaWAC was not working for some time (last position was still 85°N, 147°E) and there is a time offset between GRaWACs angles and the ones from the ship stream. Time was somehow not synced to host-PC/ship server but to some wrong time (probably one that was not updated due to issues with the GPS). We stopped measurements and probably lost all from hour 11 and then restarted. GPS is now correct but we still do not know how the time is treated in the radar software.
-  There is likely an offset between the radar measurements and the other instruments as both radars had in there software the option "sync. to Radar GPS" enabled so far. We changed that around 14:45
- at 16:30 UTC we removed the GPS from radiometers and radars, trusting in the information from Thomas/Mario that the radar/radiometer PCs then get the time from the host PC  

2024-09-17
----------
- GRaWAC stopped measuring at 00:45, started again at 07:54
- around 14:15 we reached a large Pfütze with nilas! :)
  
2024-09-18
----------
- figured out that GPS Trimble 2 is the one right next to our radars 

2024-09-19
----------
- Cumulus stopped over night, maybe because of full storage. Restarted MiRAC-A, Parsivel, and RaspberryPi in the morning.
- around 11 UTC we discovered that the gopro had no more power, it did not recognize the power cable, we exchanged the batteries and it worked again around 11:20. Some data might be missing (not more than 5 hours)
- over night white frost (raureif) collected on GRaWAC's radoms, we used a hairdryer first and then the heat gun to remove it between 8:50 UTC and 10:10 UTC (photos taken)
- similarily white frost collected on the opening of the blowers of the radiometers, was removed around noon

2024-09-20
----------
- there was a little bit of white frost again on GRaWAC's radom, was quickly removed (took around 5 minutes) in the morning, approximately at 7:25 UTC
- FLIR stopped running at 19:13, restarted at 19:43

2024-09-21
----------
- nimbus shut down at 23:30 on 2024-09-20, restarted FLIR at 06:30, mobotix at 07:04, no HATPRO and LHUMPRO from 2024-09-20 at 19:12 until 06:25, first measurements of 21st are in folder 20 
- interesting air mass exchange: strong drop in (surface)temperature around noon

2024-09-22
----------
- late calibration of mini-IMU (after lunch)
- instruments all working

2024-09-23
----------
- small ice station
- Nils' birthday! :)

2024-09-24
----------
- all is well with our instruments

2024-09-25
----------
- realized in the morning that cumulus was in screen saver mode. stopped mirac measurements at 6:58 UTC and shut down computer because Parsivel was not recognized, when only shutting down and rebooting, we still could the familiar error message "... could not open port 'COM3': PermissionError(13, 'Zugriff verweigert', None, 5)", shutting down, removing all usb connection (mouse and parsivel), booting and then pluggin in and then starting the logger again  works, restarted measurements around 7:17
- at night around 22:35 realized that mobotix is having troubles, very likely because of clear sky (no image)

2024-09-26
----------
- 00:00 UTC clear sky sonde
- blower of MiRAC-A sounded strange and indeed a lot of snow had collected in front of the blower openings (the entrance that has this extra case), was removed around 10 UTC

2024-09-27
----------
- 14:55 to 15:30 UTC: turned off MiRAC-A to open the blower channel to see whether ice accumulated, couldn't see any, see whether we need to check it again or hope that it works out until end of cruise
- saw that there is a hole in the transmitter radome, will change it tomorrow

2024-09-28
----------


2024-09-29
----------
- 00:00 UTC: clear sky during radiosonde launch
- 6:50-7:20 UTC removed white frost from GrAWAC's radoms using the heat gun, blower is very weak
- removed the snow/ice accumulated in front of the blowers of radiometers and radars
- 8 UTC: removed frost from GRaWAC's radomes using the heat gun
- 12:20 UTC: removed frost from GRaWAC's radomes using the heat gun

2024-09-30
----------
- 7:00- 7:15, 7:50, 14:20, 18:30 removed white frost from GrAWAC's radoms using heat gun
- removing snow accumulated in front of radiometer and radar blowers

2024-10-01
----------
- 08:20 UTC removed white frost from GrAWAC's radoms + removing snow accumulatedin front of blowers of all four instruments (not as much as yesterday) 
- 12:15-12:40 removed white frost with heat gun from GrAWAC's radoms
2024-10-02
----------
- since yesterday afternoon, GRaWAC's blower is strong again and there was no need for heat gunning
- around 14:00/15:00 UTC quite a lot of open water in radiometer footprint
2024-10-03
----------


2024-10-04
----------
- really nice and small pancake ice around 11 UTC, could be a cool flir video! :)
- left ice around 13 UTC (already before very little ice /scattered floes)
- we have wildlfe around us again! the lines in mirac from 14:10 UTC are probably birds flying around the ship's bow
- grawac data from 6 and 12 UTC doesn't want to be converted to netcdf

2024-10-05
----------
- stopped flir at 8:30 UTC
- packed away flir, gopro, parsival and ultrasonic!
- GRaWAC PC turns off for 2 to 5 minutes and then restarts, the measurement continues afterwards
- offical end times of instruments (dship):
ir_flir_a315 bis 5.10.2024 8:30

Parsivel bis 5.10.2024 8:30

sonic_anemometer_3D bis 5.10.2024 12:58

raspberry_pi_imu bis 4.10.2024 06:18

mini-IMU bis 6.10.2024 08:50

gopro_uoc  bis 5.10.2024 10:54

- hatpro and lhumpro changed to zenith only measurements at 10:00 UTC
2024-10-06
----------


2024-10-07
----------


2024-10-08
----------
-realized that GRaWAC stopped working yesterday night (on October 7 at 22:06), restarted 6:37 UTC
- GRaWAC also had occasional stops for unknown reasons
- Lhumpro stopped recording already yesterday in the afternoon, unknown reason as measurements were still running today 
- 8:25 turned off radiometer for final disassembling
- 8:28 turned off mobotix for final disassembling
- 12:16 turned off measurents radars for final disassembling but still had them on (blower was still working)

2024-10-09
----------
- turned off radars completely and diassembled them. Strangely blower of MiRAC was blowing even when turned off

2024-10-10
----------
- diassembled radiometer stands

2024-10-11
----------
- measured position of GPS trimble 2
- finalizing cruise report

2024-10-12
----------


2024-10-13
----------
