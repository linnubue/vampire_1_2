# VAMPIRE
code and documentation 

This repository contains code and documentation for the VAMPIRE projects o
Polarstern cruises PS144 and PS149 with similar instrument setups.

The repository contains the code that is used during the cruise and for
data processing as described in the corresponding VAMPIRE data paper.

Jupyter notebooks provide examples and interactive plots.

## Installation

Install the package as editable for development:

`pip install --editable .`

## Requirements

The required Python packages are listed in the pyprojects.toml file. Additionally,
PAMTRA, SMRT, and MWRpy are needed for some modules. These packages might
have additional requirements not listed yet (e.g. ephem, timezonefinder).

Specific requirement to read EXIF data from images:

- libimage-exiftool-perl (needed to read exif data of images)

Radiative transfer models for atmosphere and snow/ice:

- [PAMTRA](https://github.com/igmk/pamtra)
- [SMRT](https://github.com/smrt-model/smrt)

Processing of microwave radiometer data.

- [MWRpy](https://github.com/actris-cloudnet/mwrpy)
