"""
Reads timestamp from FLIR .seq binary files and writes them to a csv file. This
is needed, because the png 16-bit format does not contain time information.
The idea is taken from https://flirpy.readthedocs.io/, but the library does 
not work with the .seq files from the FLIR A315 camera.

Description
-----------
The time of each FLIR image of a .seq sequence is given in seconds since 1970
(unix time) and milliseconds. The time is stored in the binary file as a 
sequence of bytes. The seconds are stored as long integers (len=4) and 
milliseconds are stored as short integers (len=2). The following shows the
conversion to binary for a given unix time and millisecond.

>>> struct.pack("i", 1724330541)
b"-2\xc7f"

>>> struct.pack("h", 628)
b"t\x02"

The second and millisecond locations in the binary file are indicated by a
unique start sequence.

Usage
-----
>>> python flir_time.py /in/path /out/path/
"""

import argparse
import csv
import os
import struct
import pdb
from glob import glob

from tqdm import tqdm

START_SEQUENCE = b"\x80?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
SIZE_START = len(START_SEQUENCE)
SIZE_SEC = 4
SIZE_MS = 2


def main(path_in, path_out):
    """
    Extracts times from all binary files in a directory.
    """

    files = glob(os.path.join(path_in, "*.seq"))
    for file in tqdm(files):
        process(file, path_out, skip_existing=True)


def process(file, path_out, skip_existing=False):
    """
    Extract times from FLIR binary file.
    """

    outfile = os.path.join(
        path_out, os.path.basename(file.replace(".seq", "_times.csv"))
    )
    
    if skip_existing and os.path.isfile(outfile):
        return

    data = read_binary(file)
    lst_sec, lst_ms = find_times(data)

    print(f"{file}: Found {len(lst_sec)} timestamps.")

    # create output filename
    write_result(file=outfile, lst_sec=lst_sec, lst_ms=lst_ms)


def read_binary(file):
    """
    Reads binary file
    """

    with open(file, "rb") as f:
        data = f.read()

    return data


def find_times(data):
    """
    Extracts seconds and milliseconds from binary FLIR .seq file.

    This function searches for a specific start sequence in a binary data stream
    and extracts the timestamp information that follows it. The timestamp consists
    of seconds and milliseconds, both of which are unpacked from their respective
    byte representations. The function processes the binary data in chunks,
    skipping a fixed number of bytes after each match to optimize performance.

    Parameters
    ----------
    data : bytes
        The binary data from which to extract the timestamps. This should be
        the entire contents of the binary file read in as bytes.

    Returns
    -------
    lst_sec : list of int
        A list of extracted seconds as integers.
    lst_ms : list of int
        A list of extracted milliseconds as integers.

    Notes
    -----
    - The function looks for a predefined start sequence (`START_SEQUENCE`) in the
      binary data to locate each timestamp.
    - The number of bytes to skip (`n_skip`) after each match is a fixed value to
      enhance performance by reducing the search space for subsequent matches.
    """

    lst_sec = []
    lst_ms = []

    i = 0
    n_skip = 140000
    while True:
        i = data.find(START_SEQUENCE, i)

        if i == -1:
            break
        else:
            i0 = i + SIZE_START
            sec_byte = data[i0 : i0 + SIZE_SEC]
            ms_byte = data[i0 + SIZE_SEC : i0 + SIZE_SEC + SIZE_MS]

            lst_sec.append(struct.unpack("i", sec_byte)[0])
            lst_ms.append(struct.unpack("h", ms_byte)[0])

            i += n_skip

    return lst_sec, lst_ms


def write_result(file, lst_sec, lst_ms):
    """
    Write resulting seconds and milliseconds to csv file.
    """

    with open(file, "w") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerows(zip(lst_sec, lst_ms))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract times from all binary files in a directory."
    )
    parser.add_argument(
        "path_in", help="The input directory containing .seq files."
    )
    parser.add_argument(
        "path_out", help="The output directory to save processed files."
    )

    args = parser.parse_args()
    main(args.path_in, args.path_out)
