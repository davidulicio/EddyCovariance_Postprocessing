# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 12:55:59 2024
Canopy Height Estimation
@author: David Trejo
"""
import numpy as np

def h_estimation(df, ustarmin=0.2, ustarmax=0.4, neutral=0.1):
    """
    Dynamic canopy height calculat     ion based on Pennypacker, S., Baldocchi, D.
    Seeing the Fields and Forests: Application of Surface-Layer Theory and
    Flux-Tower Data to Calculating Vegetation Canopy Height.
    Boundary-Layer Meteorol 158, 165–182 (2016).
    https://doi.org/10.1007/s10546-015-0090-0

    Parameters
    ----------
    df : DataFrame
        EddyPro's full output file read as a dataframe or smartflux results from
        Flux floder.
    ustarmin : float, optional
        Minimum ustar threshold. The default is 0.2.
    ustarmax : float, optional
        Maximum ustar threshold. The default is 0.4.
    neutral : float, optional
        Stabilty parameter threshold for neutral conditions. The default is 0.1.

    Returns
    -------
    h : Series
        Canopy height estimation 30-min timeseries.
    h : Series
        Canopy height estimation daily timeseries.

    """
    #dynamic canopy height
    df = df.astype(float, errors="ignore")
    umean = df.u_rot
    vmean = df.v_rot
    ustar = df["u*"]
    u = np.sqrt(umean**(2) + vmean**(2))
    sp = df["(z-d)/L"].abs()
    neutral_mask = sp <= neutral # Neutral conditions
    turbulence_mask = (ustar > ustarmin) * (ustar < ustarmax)
    mask = turbulence_mask * neutral_mask
    z = 7.1  # measurement height
    k = 0.4  # von Karman constant
    b = 0.6 + 0.1* np.exp(k * u / ustar)
    h = z / (b)
    h[~mask] = np.nan
    h_daily = h.resample("D").mean
    return h, h_daily