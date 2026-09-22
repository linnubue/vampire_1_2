"""
This is a module to familiarize with COM port signals.
"""

import serial
import sys
import time

port = str(sys.argv[1])
baud_rate = int(sys.argv[2])
timeout = float(sys.argv[3])

ser = serial.Serial(port, baud_rate, timeout=timeout)

# get everything
time.sleep(0.1)
s = ser.read(ser.in_waiting)
print(s, len(s))

n_char = 30  # number of line characters including new line (two characters \r\n)

# this finds the start of a message and discards the end of a previous message
# provide the start identifier of the last sentence of a message
start_line = "$PRDID"
line = "      "
while line != start_line:
    try:
        char = ser.read(1).decode("utf-8").strip()
        line += char
        line = line[len(char):]
        print(line, len(line), start_line)
    except UnicodeDecodeError as err:
        pass
    time.sleep(0.05)
skip = ser.read(n_char - len(start_line)).decode("utf-8")

while True:
    line = ser.read(ser.in_waiting).decode("utf-8").strip()
    print(int(time.time()*100), line, len(line))
    time.sleep(1)
