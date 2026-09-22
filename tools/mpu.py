#!/usr/bin/python
"""
Logger for MPU sensor on Raspberry Pi.

Description
-----------
This script logs the measurements of the MPU6050 sensor on the Raspberry Pi.
It handles the communication with the sensor, retrieves the data, and writes
the measurement to a file at regular intervals. The script can run in test 
mode to verify the logging functionality without the sensor.

Logging
-------
The data is written to files with a timestamp in the filename. A new file is
created automatically once a file interval passed. The writing is performed 
with a buffer interval to limit file operations. The buffer intervals are a 
fraction of the file intervals. Logging begins once the next buffer interval 
starts. If the logger is restarted but the past file is still valid, the logger 
will append to the existing file.

Usage
-----
The following parameters should be specified from command line in this order:

- path
- interval
- buffer interval
- file interval

# logging to a given path with interval 0.1 s, buffer interval 10 s, file interval 60 s
python mpu.py /path/to/save/files 0.1 10 60
"""

import os
import math
import time
import sched
import sys

ADDRESS = 0x68  # I2C address

try:
    import smbus

    BUS = smbus.SMBus(1)
    BUS.write_byte_data(ADDRESS, 0x6B, 0)  # initialize MPU

except ImportError:
    print("No smbus module found. Make sure you run on Raspberry Pi.")
    BUS = None

SCHEDULER = sched.scheduler(time.time, time.sleep)

# scale factors of gyroscope and accelerometer
SCALE0_GYR = 131.0
SCALE1_GYR = 65.5
SCALE2_GYR = 32.8
SCALE3_GYR = 16.4

SCALE0_ACC = 16384.0
SCALE1_ACC = 8192.0
SCALE2_ACC = 4096.0
SCALE3_ACC = 2048.0

# logging
PATH = sys.argv[1]  # path to save files
INTERVAL = float(sys.argv[2])  # measurement interval [s]
BUFFER_INTERVAL = int(sys.argv[
    3
])  # buffer duration [s] - interval to write data to file
FILE_INTERVAL = int(sys.argv[
    4
])  # file duration [s] - interval to create a new file
HEADER_LINES = [
    "MPU6050\n",
    "time,gyr_x,gyr_y,gyr_z,acc_x,acc_y,acc_z,rot_x,rot_y,rot_z,temp,dur\n",
    "[YYYY-MM-DDTHH:MM:SS.f],[arcsec],[arcsec],[arcsec],[g],[g],[g],[\xb0],[\xb0],[\xb0],[\xb0C],[ms]\n",
]
LINE_FORMAT = "{},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.2f},{:.8f}\n"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def main():
    """
    Run MPU measurement and write regularly to file
    """

    assert (
        FILE_INTERVAL > BUFFER_INTERVAL
    ), "File interval must be larger than buffer interval."
    assert (
        FILE_INTERVAL % BUFFER_INTERVAL == 0
    ), "File interval must be a multiple of buffer interval."

    if BUS is None:
        print("Running in test mode.")
        run_logger(f_sensor=read_sensor_test)

    else:
        print("Starting logger.")
        run_logger(f_sensor=read_sensor)


def run_logger(f_sensor):
    """
    This runs the logger for the sensor data.

    Parameters
    ----------
    f_sensor : function
        Function to read sensor data.
    """

    start_time = (
        time.time() // BUFFER_INTERVAL + 1
    ) * BUFFER_INTERVAL  # future
    time_file = (start_time // FILE_INTERVAL) * FILE_INTERVAL  # past
    time_write = start_time + BUFFER_INTERVAL  # future
    log_buffer = []

    # write header to file if file does not exist
    if not os.path.exists(get_filename(time_file)):
        write(HEADER_LINES, get_filename(time_file))

    SCHEDULER.enterabs(
        time=start_time,
        priority=1,
        action=logger,
        argument=(
            start_time,
            log_buffer,
            f_sensor,
            time_file,
            time_write,
        ),
    )
    SCHEDULER.run()


def logger(start_time, log_buffer, f_sensor, time_file, time_write):
    """
    Log the sensor data and write the data to the file. A new file is created
    for every hour.

    Parameters
    ----------
    start_time : float
        Start time of the logger in seconds. This will be the reference time.
        All following readings are relative to this time using the interval
        constant.
    log_buffer : list
        List of log entries.
    f_sensor : function
        Function to read sensor data.
    time_file : float
        Time of file name in seconds.
    time_write : float
        Time of next writing in seconds.
    """

    current_time = time.time()

    log_buffer.append(f_sensor())

    # write data regularly
    if current_time >= time_write - INTERVAL:
        write(log_buffer, get_filename(time_file))
        log_buffer.clear()
        time_write += BUFFER_INTERVAL

    # write header to new file
    if current_time >= time_file + FILE_INTERVAL:
        time_file += FILE_INTERVAL
        write(HEADER_LINES, get_filename(time_file))

    SCHEDULER.enterabs(
        time=start_time + INTERVAL,
        priority=1,
        action=logger,
        argument=(
            start_time + INTERVAL,
            log_buffer,
            f_sensor,
            time_file,
            time_write,
        ),
    )


def write(log_buffer, file):
    """
    Write buffer to file.

    Parameters
    ----------
    log_buffer : list
        List of log entries.
    file : str
        Name of file to write to.
    """

    with open(file, mode="a") as f:
        f.writelines(log_buffer)


def get_filename(t):
    """
    Create filename with time stamp.
    """

    time_str = time.strftime("%Y%m%d_%H%M%S", time.gmtime(t))
    file = os.path.join(
        PATH,
        f"mpu_{time_str}.csv",
    )

    return file


def read_word(reg):  # reading values from register
    high = BUS.read_byte_data(ADDRESS, reg)
    low = BUS.read_byte_data(ADDRESS, reg + 1)
    value = (high << 8) + low

    if value >= 0x8000:
        return -((65535 - value) + 1)
    else:
        return value


def get_distance(a, b):
    return math.sqrt((a * a) + (b * b))


def get_y_rotation(x, y, z):
    radians = math.atan2(x, get_distance(y, z))
    return -math.degrees(radians)


def get_x_rotation(x, y, z):
    radians = math.atan2(y, get_distance(x, z))
    return math.degrees(radians)


def get_z_rotation(x, y, z):
    radians = math.atan2(z, get_distance(x, y))
    return math.degrees(radians)


def get_temperature():
    temp = read_word(0x41)
    return (temp / 340) + 36.53


def read_sensor():
    """
    Read sensor measurements
    """

    time1 = time.time()
    gyroscope_xout = read_word(0x43)  # reading gyroscope values
    gyroscope_yout = read_word(0x45)
    gyroscope_zout = read_word(0x47)
    acceleration_xout = read_word(0x3B)  # reading accelerometer values
    acceleration_yout = read_word(0x3D)
    acceleration_zout = read_word(0x3F)
    temperature = get_temperature()

    duration = (time.time() - time1) * 1000
    timestamp_s = time.strftime(TIME_FORMAT, time.gmtime(time1))
    time_fr = time1 - int(time1)
    timestamp_ms = str(int(time_fr * 1000)).zfill(3)
    timestamp = timestamp_s + "." + timestamp_ms

    gyroscope_xout_scaled = (
        gyroscope_xout / SCALE0_GYR
    )  # scaled gyroscope values
    gyroscope_yout_scaled = gyroscope_yout / SCALE0_GYR
    gyroscope_zout_scaled = gyroscope_zout / SCALE0_GYR

    acceleration_xout_scaled = (
        acceleration_xout / SCALE0_ACC
    )  # scaled accelerometer values
    acceleration_yout_scaled = acceleration_yout / SCALE0_ACC
    acceleration_zout_scaled = acceleration_zout / SCALE0_ACC

    rotation_x = get_x_rotation(
        acceleration_xout_scaled,
        acceleration_yout_scaled,
        acceleration_zout_scaled,
    )
    rotation_y = get_y_rotation(
        acceleration_xout_scaled,
        acceleration_yout_scaled,
        acceleration_zout_scaled,
    )
    rotation_z = get_z_rotation(
        acceleration_xout_scaled,
        acceleration_yout_scaled,
        acceleration_zout_scaled,
    )

    out = LINE_FORMAT.format(
        timestamp,
        gyroscope_xout_scaled,
        gyroscope_yout_scaled,
        gyroscope_zout_scaled,
        acceleration_xout_scaled,
        acceleration_yout_scaled,
        acceleration_zout_scaled,
        rotation_x,
        rotation_y,
        rotation_z,
        temperature,
        duration,
    )

    return out


def read_sensor_test():
    """
    Test of sensor measurement reading
    """

    time1 = time.time()
    duration = (time.time() - time1) * 1000
    timestamp_s = time.strftime(TIME_FORMAT, time.gmtime(time1))
    time_fr = time1 - int(time1)
    timestamp_ms = str(int(time_fr * 1000)).zfill(3)
    timestamp = timestamp_s + "." + timestamp_ms

    gyroscope_xout_scaled = 0
    gyroscope_yout_scaled = 1
    gyroscope_zout_scaled = 2
    acceleration_xout_scaled = -1
    acceleration_yout_scaled = -2
    acceleration_zout_scaled = -3
    rotation_x = 1
    rotation_y = 2
    rotation_z = 3
    temperature = 270.1

    out = LINE_FORMAT.format(
        timestamp,
        gyroscope_xout_scaled,
        gyroscope_yout_scaled,
        gyroscope_zout_scaled,
        acceleration_xout_scaled,
        acceleration_yout_scaled,
        acceleration_zout_scaled,
        rotation_x,
        rotation_y,
        rotation_z,
        temperature,
        duration,
    )

    return out


if __name__ == "__main__":
    main()
