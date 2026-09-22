"""
Calculates emissivity at the surface and converts H- and V-pol to QH- and 
QV-pol.
"""

import numpy as np


def calc_emissivity(tb, td, ts):
    """
    Compute emissivity, neglecting distance between radiometer and surface.

    tb = e * ts + (1 - e) td

    Parameters
    ----------
    tb : np.ndarray
        Upwelling Tb.
    td : np.ndarray
        Downwelling Tb.
    ts : np.ndarray
        Surface temperature.
    """

    e = (tb - td) / (ts - td)

    return e


def vh2qv(v, h, scan_ang, angle_deg=True):
    """
    Vertical and horizontal polarization to quasi-vertical polarization.

    Parameters
    ----------
    v : np.ndarray
        Vertically-polarized radiation.
    h : np.ndarray
        Horizontally-polarized radiation.
    scan_ang : np.ndarray
        Scan angle.
    angle_deg : bool
        Angle unit in degrees.
    """

    if angle_deg:
        scan_ang = np.deg2rad(scan_ang)

    qv = v * np.cos(scan_ang) ** 2 + h * np.sin(scan_ang) ** 2

    return qv


def vh2qh(v, h, scan_ang, angle_deg=True):
    """
    Vertical and horizontal polarization to quasi-horizontal polarization.

    Parameters
    ----------
    v : np.ndarray
        Vertically-polarized radiation.
    h : np.ndarray
        Horizontally-polarized radiation.
    scan_ang : np.ndarray
        Scan angle.
    angle_deg : bool
        Angle unit in degrees.
    """

    if angle_deg:
        scan_ang = np.deg2rad(scan_ang)

    qh = h * np.cos(scan_ang) ** 2 + v * np.sin(scan_ang) ** 2

    return qh
