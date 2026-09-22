r"""
This logs COM two ports that stream data of the Polarstern GPS receiver and 
an instrument measuring roll, pitch, and yaw. One file is created per hour 
and named after the beginning of the hour. The file is written every 10 s to 
reduce amount of disk writes. The GPS data is provided with 1 Hz and the angular
data with 20 Hz frequency.

Some things are not yet implemented:

- file headers. When converting the data to netcdf, get file headers from this script
- it is unclear which in which order roll and pitch are provided

Usage
-----
GPS logging: 

C:\Users\mirac\AppData\Local\Programs\Python\Python312\python.exe C:\Users\mirac\Documents\vampire\log_ship.py --stream gps --output-dir C:\Users\mirac\Documents\vampire\data\ship\gps --interval 0.9 --start-line PSSVT --n-char 19

Angles logging: 

C:\Users\mirac\AppData\Local\Programs\Python\Python312\python.exe C:\Users\mirac\Documents\vampire\log_ship.py --stream angles --output-dir C:\Users\mirac\Documents\vampire\data\ship\angles --interval 0.04 --start-line PRDID --n-char 30

COM port setup
--------------

COM1: angles
COM2: gps

Description GPS
---------------

The following describes the information of the GPS. The
GPS data block follows National Marine Electronics Association (NMEA) data 
communication. See also https://aprs.gids.nl/nmea/. We extract some information
from these blocks:

- GPGGA
  - Latitude
  - Longitude
  - Altitude
  - Geoid separation
- GPRMC
  - Speed (knots)
  - Date
- GPZDA
  - Time

This is an explanation of a single block:

    $GPGGA,132340,7908.501,N,00830.620,E,2,9,1,48.6,M,19.8,M,,,,*57
    $GPGLL,7908.501,N,00830.620,E,13:23:40,A,,*20
    $GPRMC,132340,A,7908.501,N,00830.620,E,11.3,337.9,12082024,0.0,A,*66
    $GPVTG,337.9,T,,M,11.3,N,,K,A*1E
    $GPZDA,132340.00,12, 8,2024,00,00*7E
    $HEHDT,337.7,M*36
    $PSDPT,339.4,0.0,*62
    $PSSVT,1483.19*56

$GPGGA (Global Positioning System Fix Data)

    Time: 132340 - Time of fix (HHMMSS in UTC).
    Latitude: 7908.501,N - Latitude (79deg 08.501' North).
    Longitude: 00830.620,E - Longitude (8deg 30.620' East).
    Fix Quality: 2 - GPS fix quality (2 = DGPS fix).
    Satellites: 9 - Number of satellites being tracked.
    HDOP: 1 - Horizontal dilution of precision.
    Altitude: 48.6,M - Altitude (48.6 meters above mean sea level).
    Geoid Separation: 19.8,M - Height of geoid above WGS84 ellipsoid (19.8 meters).
    DGPS Station ID: ,,, - Not provided (optional).
    Checksum: *57 - Data integrity checksum.

$GPGLL (Geographic Position - Latitude/Longitude)

    Latitude: 7908.501,N - Latitude (79deg 08.501' North).
    Longitude: 00830.620,E - Longitude (8deg 30.620' East).
    Time: 13:23:40 - Time of position fix (HHMMSS in UTC).
    Data Status: A - Data status (A = Valid).
    Checksum: *20 - Data integrity checksum.

$GPRMC (Recommended Minimum Navigation Information)

    Time: 132340 - Time of fix (HHMMSS in UTC).
    Status: A - Status of the fix (A = Valid).
    Latitude: 7908.501,N - Latitude (79deg 08.501' North).
    Longitude: 00830.620,E - Longitude (8deg 30.620' East).
    Speed: 11.3 - Speed over ground (11.3 knots).
    Course: 337.9 - Track angle (337.9deg true).
    Date: 12082024 - Date of fix (12th August 2024).
    Magnetic Variation: 0.0 - Magnetic variation (0.0deg).
    Mode: A - Mode indicator (A = Autonomous).
    Checksum: *66 - Data integrity checksum.

$GPVTG (Course Over Ground and Ground Speed)

    Course (True): 337.9,T - Track angle in degrees (337.9deg true).
    Course (Magnetic): ,M - Track angle in degrees (empty).
    Speed (Knots): 11.3,N - Speed over ground (11.3 knots).
    Speed (Km/h): ,K - Speed over ground (empty).
    Mode: A - Mode indicator (A = Autonomous).
    Checksum: *1E - Data integrity checksum.

$GPZDA (Time and Date)

    Time: 132340.00 - Time of fix (HHMMSS.SS in UTC).
    Day: 12 - Day of month.
    Month: 8 - Month.
    Year: 2024 - Year.
    Local Time Offset: 00,00 - Local time zone offset from UTC (hours, minutes).
    Checksum: *7E - Data integrity checksum.

$HEHDT (Heading - True)

    Heading: 337.7,M - Heading in degrees (337.7deg magnetic).
    Checksum: *36 - Data integrity checksum.

$PSDPT (Depth)

    Depth: 339.4 - Depth in meters.
    Transducer Offset: 0.0 - Offset from transducer in meters.
    Checksum: *62 - Data integrity checksum.

$PSSVT (Speed or Velocity)

    Speed/Velocity: 1483.19 - Speed or velocity (exact interpretation depends on device).
    Checksum: *56 - Data integrity checksum.

Description angles
------------------

The following describes the angular information. We use all information on 
angles from this device rather than the GPS:

- PRDID
  - Pitch
  - Roll
  - Heading

This is an explanation of a single line:

$PRDID,+0.03,+0.32,+338.63*5D

$PRDID (Custom sentence from a device reporting pitch, roll, and heading)

    Pitch: +0.03 - The pitch angle in degrees
    Roll: +0.32 - The roll angle in degrees
    Heading: +338.63 - The heading (yaw) angle in degrees
    Checksum: *5D - Data integrity checksum
"""

import os
import argparse
import serial
import sched
import time
from datetime import datetime

BAUD_RATE = 9600
TIMEOUT = 1  # timeout in seconds


# Function to create a new filename every hour
def generate_filename():
    return os.path.join(
        output_dir, datetime.now().strftime(f"shipstream_{stream}_%Y%m%d_%H.txt")
    )


# Function to log data from both ports
def log_data(ser, scheduler, log_interval, extract_fun, start_line, n_char):
    global current_file, last_write_time

    data_lst = None
    data_exists = False
    try:
        data_lst = extract_fun(ser)
        data_exists = True
    except Exception as e:
        print(e)
        print("Go to sentence start")
        to_sentence_start(ser, start_line, n_char)
        data_exists = False

    # Check if it's time to write data to file
    if time.time() - last_write_time >= log_interval and data_exists:
        data_line = (",").join(data_lst)
        data_line = f"{datetime.now().isoformat()},{data_line}"
        print(data_line)
        with open(current_file, "a") as f:
            f.write(data_line + "\n")
        last_write_time = time.time()

    # Reschedule the logging function
    scheduler.enter(
        log_interval,
        1,
        log_data,
        (ser, scheduler, log_interval, extract_fun, start_line, n_char),
    )


# Function to manage creating a new log file every hour
def manage_new_file(scheduler):
    global current_file

    current_file = generate_filename()

    # Reschedule the file management function for the next hour
    scheduler.enter(3600, 1, manage_new_file, (scheduler,))


def extract_ang_string(ser):
    """
    Extract data from angles string.

    Parameters
    ----------
    in_string : str
        The angles string. E.g.
        $PRDID,+0.03,+0.32,+338.63*5D
    """
	
    data = ser.readline().decode("utf-8").strip()
    #line = data.split(",")
    #data_lst = [
    #    line[1],  # pitch
    #    line[2],  # roll
    #    line[3].split("*")[0],  # heading
    #]
	
    #return data_lst
    return [data]


def extract_gps_string(ser):
    """
    Extract data from GPS string. This reads all eight lines

    Parameters
    ----------
    in_string : str
        The GPS string. E.g.
        $GPGGA,132340,7908.501,N,00830.620,E,2,9,1,48.6,M,19.8,M,,,,*57
        $GPGLL,7908.501,N,00830.620,E,13:23:40,A,,*20
        $GPRMC,132340,A,7908.501,N,00830.620,E,11.3,337.9,12082024,0.0,A,*66
        $GPVTG,337.9,T,,M,11.3,N,,K,A*1E
        $GPZDA,132340.00,12, 8,2024,00,00*7E
        $HEHDT,337.7,M*36
        $PSDPT,339.4,0.0,*62
        $PSSVT,1483.19*56
    """

    data = ""
    for i in range(8):
        data += ser.readline().decode("utf-8").strip()
        data += "\n"
    data = data.strip()
    sentences = data.split("\n")
    line_gga = sentences[0].split(",")
    line_rmc = sentences[2].split(",")
    line_zda = sentences[4].split(",")
    data_lst = [
        line_rmc[9],  # date
        line_zda[1],  # time
        line_gga[2],  # latitude
        line_gga[3],  # latitude direction
        line_gga[4],  # longitude
        line_gga[5],  # longitude direction
        line_gga[9],  # altitude
        line_gga[11],  # geoid separation
        line_rmc[7],  # speed
    ]

    return data_lst


def to_sentence_start(ser, start_line, n_char):
    """
    This reads the serial ser until a new message begins. This can be used
    to find the start of a message. Provide any marker string, ideally the
    beginning of the last line of a message.

    For gps: to_sentence_start(ser=ser, start_line="PSSVT", n_char=19)
    For angles: to_sentence_start(ser=ser, start_line="PRDID", n_char=30)

    Parameters
    ----------
    ser : serial.Serial
        Serial ser.
    start_line : str
        Start identified of the last sentence of a message
    n_char : int
        Length of the last sentence of a message
    """

    start_line = "$" + start_line
    line = " " * len(start_line)
    while line != start_line:
        try:
            line += ser.read(1).decode("utf-8")
            line = line[1:]
        except UnicodeDecodeError as err:
            pass
        print(line, start_line)
    skip = ser.read(n_char - len(start_line)).decode("utf-8")


if __name__ == "__main__":

    # make log interval and output directory to argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream", type=str, choices=["angles", "gps"])
    parser.add_argument("--output-dir", type=str)
    parser.add_argument("--interval", type=float)
    parser.add_argument("--start-line", type=str)
    parser.add_argument("--n-char", type=int)
    args = parser.parse_args()

    stream = args.stream
    output_dir = args.output_dir

    # Setup serial ports (replace with your actual ser settings)
    if stream == "angles":
        ser = serial.Serial("COM1", BAUD_RATE, timeout=TIMEOUT)
        extract_fun = extract_ang_string

    elif stream == "gps":
        ser = serial.Serial("COM2", BAUD_RATE, timeout=TIMEOUT)
        extract_fun = extract_gps_string

    # Initialize scheduler
    scheduler = sched.scheduler(time.time, time.sleep)

    # Initial filename setup and logging variables
    current_file = generate_filename()
    last_write_time = time.time()

    # Start logging data
    scheduler.enter(
        0,
        1,
        log_data,
        (ser, scheduler, args.interval, extract_fun, args.start_line, args.n_char),
    )

    # Schedule file creation every hour
    scheduler.enter(3600, 1, manage_new_file, (scheduler,))

    # go to sentence start
    to_sentence_start(ser, args.start_line, args.n_char)

    # Start the scheduler
    scheduler.run()
