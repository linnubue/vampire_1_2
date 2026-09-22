"""
Band pass information of the microwave radiometers HATPRO, MiRAC-P, and the
passive channel of MiRAC-A.

Note: The polarizations of HATPRO and LHUMPRO are opposite during VAMPIRE, 
because the instruments layed on the side.

From https://github.com/nrisse/lizard/blob/main/lizard/readers/band_pass.py
"""

import xarray as xr


def create_band_pass():
    """
    Creates a band pass dataset for HATPRO, LHUMPRO, MiRAC-A, and a combination
    of HATPRO and LHUMPRO.

    Returns
    -------
    xr.Dataset of band pass data.
    """

    ds_bp_hatpro = xr.Dataset.from_dict(
        {
            "coords": {
                "channel": {
                    "dims": ("channel",),
                    "attrs": {"long_name": "channel number"},
                    "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                },
                "n_avg_freq": {
                    "dims": ("n_avg_freq",),
                    "attrs": {
                        "description": "Enumerating the frequencies, which are averaged."
                    },
                    "data": [1, 2, 3, 4],
                },
            },
            "attrs": {
                "title": "Pass band data for MW coefficient files",
                "instrument": "HATPRO",
                "platform": "unspecified",
                "history": "Created from RTTOV MW coefficient files",
                "citation": "source: https://nwp-saf.eumetsat.int/site/software/rttov/download/coefficients/spectral-response-functions/",
            },
            "dims": {"channel": 14, "n_avg_freq": 4},
            "data_vars": {
                "polarization": {
                    "dims": ("channel",),
                    "attrs": {
                        "standard_name": "polarization",
                        "long_name": "polarization",
                        "description": "Polarization of the channel",
                        "flag_meanings": "average_vertical_horizontal nominal_vertical_at_nadir_rotating nominal_horizontal_at_nadir_rotating vertical horizontal +45_minus_-45 left_circular_minus_right_circular uneven_mixture",
                        "flag_values": [0, 1, 2, 3, 4, 5, 6, 7],
                    },
                    "data": [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
                },
                "n_if_offsets": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "Number of intermediate frequency offsets",
                        "description": "0: one freq; 1: two freq; 2: four freq",
                    },
                    "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                },
                "bandwidth": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "bandwidth",
                        "standard_name": "bandwidth",
                        "units": "MHz",
                        "description": "Bandwith of each averaging frequency",
                    },
                    "data": [
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        600.0,
                        1000.0,
                        2000.0,
                    ],
                },
                "center_freq": {
                    "dims": ("channel",),
                    "attrs": {
                        "units": "GHz",
                        "description": "Center frequency of the channel",
                    },
                    "data": [
                        22.24,
                        23.04,
                        23.84,
                        25.44,
                        26.24,
                        27.84,
                        31.4,
                        51.26,
                        52.28,
                        53.86,
                        54.94,
                        56.66,
                        57.3,
                        58.0,
                    ],
                },
                "if_offset_1": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "first intermediate frequency offset",
                        "standard_name": "first_intermediate_frequency_offset",
                        "units": "GHz",
                        "description": "Offset of first intermediate frequency stage",
                    },
                    "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                },
                "if_offset_2": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "second intermediate frequency offset",
                        "standard_name": "second_intermediate_frequency_offset",
                        "units": "GHz",
                        "description": "Offset of second intermediate frequency stage",
                    },
                    "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                },
                "avg_freq": {
                    "dims": ("channel", "n_avg_freq"),
                    "attrs": {
                        "units": "GHz",
                        "description": "Frequencies, which are averaged.",
                    },
                    "data": [
                        [22.24, 22.24, 22.24, 22.24],
                        [23.04, 23.04, 23.04, 23.04],
                        [23.84, 23.84, 23.84, 23.84],
                        [25.44, 25.44, 25.44, 25.44],
                        [26.24, 26.24, 26.24, 26.24],
                        [27.84, 27.84, 27.84, 27.84],
                        [31.4, 31.4, 31.4, 31.4],
                        [51.26, 51.26, 51.26, 51.26],
                        [52.28, 52.28, 52.28, 52.28],
                        [53.86, 53.86, 53.86, 53.86],
                        [54.94, 54.94, 54.94, 54.94],
                        [56.66, 56.66, 56.66, 56.66],
                        [57.3, 57.3, 57.3, 57.3],
                        [58.0, 58.0, 58.0, 58.0],
                    ],
                },
                "label": {
                    "dims": ("channel",),
                    "attrs": {"description": "String label of channel"},
                    "data": [
                        "22.24 GHz",
                        "23.04 GHz",
                        "23.84 GHz",
                        "25.44 GHz",
                        "26.24 GHz",
                        "27.84 GHz",
                        "31.4 GHz",
                        "51.26 GHz",
                        "52.28 GHz",
                        "53.86 GHz",
                        "54.94 GHz",
                        "56.66 GHz",
                        "57.3 GHz",
                        "58 GHz",
                    ],
                },
                "label_pol": {
                    "dims": ("channel",),
                    "attrs": {
                        "description": "String label of channel with polarization."
                    },
                    "data": [
                        "22.24 (QV) GHz",
                        "23.04 (QV) GHz",
                        "23.84 (QV) GHz",
                        "25.44 (QV) GHz",
                        "26.24 (QV) GHz",
                        "27.84 (QV) GHz",
                        "31.4 (QV) GHz",
                        "51.26 (QH) GHz",
                        "52.28 (QH) GHz",
                        "53.86 (QH) GHz",
                        "54.94 (QH) GHz",
                        "56.66 (QH) GHz",
                        "57.3 (QH) GHz",
                        "58 (QH) GHz",
                    ],
                },
            },
        }
    )

    ds_bp_lhumpro = xr.Dataset.from_dict(
        {
            "coords": {
                "channel": {
                    "dims": ("channel",),
                    "attrs": {"long_name": "channel number"},
                    "data": [1, 2, 3, 4, 5, 6, 7, 8],
                },
                "n_avg_freq": {
                    "dims": ("n_avg_freq",),
                    "attrs": {
                        "description": "Enumerating the frequencies, which are averaged."
                    },
                    "data": [1, 2, 3, 4],
                },
            },
            "attrs": {
                "title": "Pass band data for MW coefficient files",
                "instrument": "MiRAC-P",
                "platform": "unspecified",
                "history": "Created from RTTOV MW coefficient files",
                "citation": "source: https://nwp-saf.eumetsat.int/site/software/rttov/download/coefficients/spectral-response-functions/",
            },
            "dims": {"channel": 8, "n_avg_freq": 4},
            "data_vars": {
                "polarization": {
                    "dims": ("channel",),
                    "attrs": {
                        "standard_name": "polarization",
                        "long_name": "polarization",
                        "description": "Polarization of the channel",
                        "flag_meanings": "average_vertical_horizontal nominal_vertical_at_nadir_rotating nominal_horizontal_at_nadir_rotating vertical horizontal +45_minus_-45 left_circular_minus_right_circular uneven_mixture",
                        "flag_values": [0, 1, 2, 3, 4, 5, 6, 7],
                    },
                    "data": [1, 1, 1, 1, 1, 1, 2, 2],
                },
                "n_if_offsets": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "Number of intermediate frequency offsets",
                        "description": "0: one freq; 1: two freq; 2: four freq",
                    },
                    "data": [1, 1, 1, 1, 1, 1, 0, 0],
                },
                "bandwidth": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "bandwidth",
                        "standard_name": "bandwidth",
                        "units": "MHz",
                        "description": "Bandwith of each averaging frequency",
                    },
                    "data": [
                        200.0,
                        200.0,
                        200.0,
                        400.0,
                        600.0,
                        1000.0,
                        4000.0,
                        4000.0,
                    ],
                },
                "center_freq": {
                    "dims": ("channel",),
                    "attrs": {
                        "units": "GHz",
                        "description": "Center frequency of the channel",
                    },
                    "data": [
                        183.31,
                        183.31,
                        183.31,
                        183.31,
                        183.31,
                        183.31,
                        243.0,
                        340.0,
                    ],
                },
                "if_offset_1": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "first intermediate frequency offset",
                        "standard_name": "first_intermediate_frequency_offset",
                        "units": "GHz",
                        "description": "Offset of first intermediate frequency stage",
                    },
                    "data": [0.6, 1.5, 2.5, 3.5, 5.0, 7.5, 0.0, 0.0],
                },
                "if_offset_2": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "second intermediate frequency offset",
                        "standard_name": "second_intermediate_frequency_offset",
                        "units": "GHz",
                        "description": "Offset of second intermediate frequency stage",
                    },
                    "data": [0, 0, 0, 0, 0, 0, 0, 0],
                },
                "avg_freq": {
                    "dims": ("channel", "n_avg_freq"),
                    "attrs": {
                        "units": "GHz",
                        "description": "Frequencies, which are averaged.",
                    },
                    "data": [
                        [182.71, 182.71, 183.91, 183.91],
                        [181.81, 181.81, 184.81, 184.81],
                        [180.81, 180.81, 185.81, 185.81],
                        [179.81, 179.81, 186.81, 186.81],
                        [178.31, 178.31, 188.31, 188.31],
                        [175.81, 175.81, 190.81, 190.81],
                        [243.0, 243.0, 243.0, 243.0],
                        [340.0, 340.0, 340.0, 340.0],
                    ],
                },
                "label": {
                    "dims": ("channel",),
                    "attrs": {"description": "String label of channel"},
                    "data": [
                        "183.31$\\pm$0.6 GHz",
                        "183.31$\\pm$1.5 GHz",
                        "183.31$\\pm$2.5 GHz",
                        "183.31$\\pm$3.5 GHz",
                        "183.31$\\pm$5 GHz",
                        "183.31$\\pm$7.5 GHz",
                        "243 GHz",
                        "340 GHz",
                    ],
                },
                "label_pol": {
                    "dims": ("channel",),
                    "attrs": {
                        "description": "String label of channel with polarization."
                    },
                    "data": [
                        "183.31$\\pm$0.6 (QV) GHz",
                        "183.31$\\pm$1.5 (QV) GHz",
                        "183.31$\\pm$2.5 (QV) GHz",
                        "183.31$\\pm$3.5 (QV) GHz",
                        "183.31$\\pm$5 (QV) GHz",
                        "183.31$\\pm$7.5 (QV) GHz",
                        "243 (QH) GHz",
                        "340 (QH) GHz",
                    ],
                },
            },
        }
    )

    ds_bp_mirac_a = xr.Dataset.from_dict(
        {
            "coords": {
                "channel": {
                    "dims": ("channel",),
                    "attrs": {"long_name": "channel number"},
                    "data": [1],
                },
                "n_avg_freq": {
                    "dims": ("n_avg_freq",),
                    "attrs": {
                        "description": "Enumerating the frequencies, which are averaged."
                    },
                    "data": [1, 2, 3, 4],
                },
            },
            "attrs": {
                "title": "Pass band data for MW coefficient files",
                "instrument": "MiRAC-A",
                "platform": "unspecified",
                "history": "Created from RTTOV MW coefficient files",
                "citation": "source: https://nwp-saf.eumetsat.int/site/software/rttov/download/coefficients/spectral-response-functions/",
            },
            "dims": {"channel": 1, "n_avg_freq": 4},
            "data_vars": {
                "polarization": {
                    "dims": ("channel",),
                    "attrs": {
                        "standard_name": "polarization",
                        "long_name": "polarization",
                        "description": "Polarization of the channel",
                        "flag_meanings": "average_vertical_horizontal nominal_vertical_at_nadir_rotating nominal_horizontal_at_nadir_rotating vertical horizontal +45_minus_-45 left_circular_minus_right_circular uneven_mixture",
                        "flag_values": [0, 1, 2, 3, 4, 5, 6, 7],
                    },
                    "data": [4],
                },
                "n_if_offsets": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "Number of intermediate frequency offsets",
                        "description": "0: one freq; 1: two freq; 2: four freq",
                    },
                    "data": [0],
                },
                "bandwidth": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "bandwidth",
                        "standard_name": "bandwidth",
                        "units": "MHz",
                        "description": "Bandwith of each averaging frequency",
                    },
                    "data": [2000.0],
                },
                "center_freq": {
                    "dims": ("channel",),
                    "attrs": {
                        "units": "GHz",
                        "description": "Center frequency of the channel",
                    },
                    "data": [89.0],
                },
                "if_offset_1": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "first intermediate frequency offset",
                        "standard_name": "first_intermediate_frequency_offset",
                        "units": "GHz",
                        "description": "Offset of first intermediate frequency stage",
                    },
                    "data": [0],
                },
                "if_offset_2": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "second intermediate frequency offset",
                        "standard_name": "second_intermediate_frequency_offset",
                        "units": "GHz",
                        "description": "Offset of second intermediate frequency stage",
                    },
                    "data": [0],
                },
                "avg_freq": {
                    "dims": ("channel", "n_avg_freq"),
                    "attrs": {
                        "units": "GHz",
                        "description": "Frequencies, which are averaged.",
                    },
                    "data": [[89.0, 89.0, 89.0, 89.0]],
                },
                "label": {
                    "dims": ("channel",),
                    "attrs": {"description": "String label of channel"},
                    "data": ["89 GHz"],
                },
                "label_pol": {
                    "dims": ("channel",),
                    "attrs": {
                        "description": "String label of channel with polarization."
                    },
                    "data": ["89 (H) GHz"],
                },
            },
        }
    )

    ds_bp_hatpro_lhumpro = xr.Dataset.from_dict(
        {
            "coords": {
                "channel": {
                    "dims": ("channel",),
                    "attrs": {"long_name": "channel number"},
                    "data": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                        9,
                        10,
                        11,
                        12,
                        13,
                        14,
                        15,
                        16,
                        17,
                        18,
                        19,
                        20,
                        21,
                        22,
                    ],
                },
                "n_avg_freq": {
                    "dims": ("n_avg_freq",),
                    "attrs": {
                        "description": "Enumerating the frequencies, which are averaged."
                    },
                    "data": [1, 2, 3, 4],
                },
            },
            "attrs": {
                "title": "Pass band data for MW coefficient files",
                "instrument": "HATPRO and MiRAC-P",
                "platform": "unspecified",
                "history": "Created from RTTOV MW coefficient files",
                "citation": "source: https://nwp-saf.eumetsat.int/site/software/rttov/download/coefficients/spectral-response-functions/",
            },
            "dims": {"channel": 22, "n_avg_freq": 4},
            "data_vars": {
                "polarization": {
                    "dims": ("channel",),
                    "attrs": {
                        "standard_name": "polarization",
                        "long_name": "polarization",
                        "description": "Polarization of the channel",
                        "flag_meanings": "average_vertical_horizontal nominal_vertical_at_nadir_rotating nominal_horizontal_at_nadir_rotating vertical horizontal +45_minus_-45 left_circular_minus_right_circular uneven_mixture",
                        "flag_values": [0, 1, 2, 3, 4, 5, 6, 7],
                    },
                    "data": [
                        1,
                        1,
                        1,
                        1,
                        1,
                        1,
                        1,
                        2,
                        2,
                        2,
                        2,
                        2,
                        2,
                        2,
                        1,
                        1,
                        1,
                        1,
                        1,
                        1,
                        2,
                        2,
                    ],
                },
                "n_if_offsets": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "Number of intermediate frequency offsets",
                        "description": "0: one freq; 1: two freq; 2: four freq",
                    },
                    "data": [
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        1,
                        1,
                        1,
                        1,
                        0,
                        0,
                    ],
                },
                "bandwidth": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "bandwidth",
                        "standard_name": "bandwidth",
                        "units": "MHz",
                        "description": "Bandwith of each averaging frequency",
                    },
                    "data": [
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        230.0,
                        600.0,
                        1000.0,
                        2000.0,
                        200.0,
                        200.0,
                        200.0,
                        400.0,
                        600.0,
                        1000.0,
                        4000.0,
                        4000.0,
                    ],
                },
                "center_freq": {
                    "dims": ("channel",),
                    "attrs": {
                        "units": "GHz",
                        "description": "Center frequency of the channel",
                    },
                    "data": [
                        22.24,
                        23.04,
                        23.84,
                        25.44,
                        26.24,
                        27.84,
                        31.4,
                        51.26,
                        52.28,
                        53.86,
                        54.94,
                        56.66,
                        57.3,
                        58.0,
                        183.31,
                        183.31,
                        183.31,
                        183.31,
                        183.31,
                        183.31,
                        243.0,
                        340.0,
                    ],
                },
                "if_offset_1": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "first intermediate frequency offset",
                        "standard_name": "first_intermediate_frequency_offset",
                        "units": "GHz",
                        "description": "Offset of first intermediate frequency stage",
                    },
                    "data": [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.6,
                        1.5,
                        2.5,
                        3.5,
                        5.0,
                        7.5,
                        0.0,
                        0.0,
                    ],
                },
                "if_offset_2": {
                    "dims": ("channel",),
                    "attrs": {
                        "long_name": "second intermediate frequency offset",
                        "standard_name": "second_intermediate_frequency_offset",
                        "units": "GHz",
                        "description": "Offset of second intermediate frequency stage",
                    },
                    "data": [
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                    ],
                },
                "avg_freq": {
                    "dims": ("channel", "n_avg_freq"),
                    "attrs": {
                        "units": "GHz",
                        "description": "Frequencies, which are averaged.",
                    },
                    "data": [
                        [22.24, 22.24, 22.24, 22.24],
                        [23.04, 23.04, 23.04, 23.04],
                        [23.84, 23.84, 23.84, 23.84],
                        [25.44, 25.44, 25.44, 25.44],
                        [26.24, 26.24, 26.24, 26.24],
                        [27.84, 27.84, 27.84, 27.84],
                        [31.4, 31.4, 31.4, 31.4],
                        [51.26, 51.26, 51.26, 51.26],
                        [52.28, 52.28, 52.28, 52.28],
                        [53.86, 53.86, 53.86, 53.86],
                        [54.94, 54.94, 54.94, 54.94],
                        [56.66, 56.66, 56.66, 56.66],
                        [57.3, 57.3, 57.3, 57.3],
                        [58.0, 58.0, 58.0, 58.0],
                        [182.71, 182.71, 183.91, 183.91],
                        [181.81, 181.81, 184.81, 184.81],
                        [180.81, 180.81, 185.81, 185.81],
                        [179.81, 179.81, 186.81, 186.81],
                        [178.31, 178.31, 188.31, 188.31],
                        [175.81, 175.81, 190.81, 190.81],
                        [243.0, 243.0, 243.0, 243.0],
                        [340.0, 340.0, 340.0, 340.0],
                    ],
                },
                "label": {
                    "dims": ("channel",),
                    "attrs": {"description": "String label of channel"},
                    "data": [
                        "22.24 GHz",
                        "23.04 GHz",
                        "23.84 GHz",
                        "25.44 GHz",
                        "26.24 GHz",
                        "27.84 GHz",
                        "31.4 GHz",
                        "51.26 GHz",
                        "52.28 GHz",
                        "53.86 GHz",
                        "54.94 GHz",
                        "56.66 GHz",
                        "57.3 GHz",
                        "58 GHz",
                        "183.31$\\pm$0.6 GHz",
                        "183.31$\\pm$1.5 GHz",
                        "183.31$\\pm$2.5 GHz",
                        "183.31$\\pm$3.5 GHz",
                        "183.31$\\pm$5 GHz",
                        "183.31$\\pm$7.5 GHz",
                        "243 GHz",
                        "340 GHz",
                    ],
                },
                "label_pol": {
                    "dims": ("channel",),
                    "attrs": {
                        "description": "String label of channel with polarization."
                    },
                    "data": [
                        "22.24 (QV) GHz",
                        "23.04 (QV) GHz",
                        "23.84 (QV) GHz",
                        "25.44 (QV) GHz",
                        "26.24 (QV) GHz",
                        "27.84 (QV) GHz",
                        "31.4 (QV) GHz",
                        "51.26 (QH) GHz",
                        "52.28 (QH) GHz",
                        "53.86 (QH) GHz",
                        "54.94 (QH) GHz",
                        "56.66 (QH) GHz",
                        "57.3 (QH) GHz",
                        "58 (QH) GHz",
                        "183.31$\\pm$0.6 (QV) GHz",
                        "183.31$\\pm$1.5 (QV) GHz",
                        "183.31$\\pm$2.5 (QV) GHz",
                        "183.31$\\pm$3.5 (QV) GHz",
                        "183.31$\\pm$5 (QV) GHz",
                        "183.31$\\pm$7.5 (QV) GHz",
                        "243 (QH) GHz",
                        "340 (QH) GHz",
                    ],
                },
            },
        }
    )

    return ds_bp_hatpro, ds_bp_lhumpro, ds_bp_mirac_a, ds_bp_hatpro_lhumpro
