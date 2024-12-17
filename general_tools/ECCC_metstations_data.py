# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 10:59:20 2024
Functions to download data met data from ECCC met stations
@author: david

"""
import pandas as pd
import numpy as np


def canadian_stations(PATH, lon, lat, d=50):
    """
    Returns the station IDs and names of the Canadian Meteorological stations
    close to the given coordinates. It will return all the stations in the given 
    distance.

    Parameters
    ----------
    PATH : str
        Directory of the climate-stations.csv file.
    lon : float
        Longitude in decimal degrees.
    lat : float
        Latitude in decimal degrees.
    d : float
        Distance in [km] from the coordinates in which to find met stations.
        Default is 50 km.

    Returns
    -------
    stns_info : Tuple
        Tuple with the stations ids and names (ids, names).

    """
    from numpy import cos, arcsin, sqrt
    df = pd.read_csv(PATH+"climate-stations.csv")
    lats = df.y
    lons = df.x
    stsid = df.STN_ID
    stsname = df.STATION_NAME
    lon = float(lon)
    lat = float(lat)   
    d = float(d)
    p = 0.017453292519943295
    hav = 0.5 - cos((lats-lat)*p)/2 + cos(lat*p)*cos(lats*p) * (1-cos((lons-lon)*p)) / 2
    distance = 12742 * arcsin(sqrt(hav))
    mask = np.where(distance < d)[0]
    ids = stsid[mask]
    names = stsname[mask]
    stns_info = (ids, names)
    return stns_info


def get_met_data(years, months, stn_id):
    """
    Given years, months and a station id it will download all the data from 
    that met station in a hourly resolution. It will output the data and another
    dataframe downscaled to 30-min and linear interpolated to match the eddy
    covariance data.
  
    Parameters
    ----------
    years : list, array
        Years of the data.
    months : list or array
        Months of the data.
    stn_id : float, int or str
        Station ID using ECCC convention.

    Returns
    -------
    df : TYPE
        DESCRIPTION.
    df2 : TYPE
        DESCRIPTION.

    """
    import requests
    import io
    df = []
    stn_id = str(int(stn_id))
    for iyear in range(len(years)):
        year = str(int(years[iyear]))
        for imonth in range(len(months)):
            month = str(int(months[imonth]))
            url = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID="+stn_id+"&Year="+year+"&Month="+month+"&Day=14&timeframe=1&submit=%20Download+Data"
            response = requests.get(url, timeout=20)
            if response.ok:
                df.append(pd.read_csv(io.StringIO(response.content.decode('utf-8'))))
    df = pd.concat(df)
    df = df.drop(columns=df.filter(regex="Flag"))
    df.index = pd.DatetimeIndex(df['Date/Time (LST)'])
    # df = pd.to_numeric(df, errors='coerce')
    df = df.apply(pd.to_numeric, errors='coerce')
    no_data = df.columns[df.isna().sum()==len(df)].to_list()
    no_data.extend(["Longitude (x)", "Latitude (y)", "Climate ID",
                    "Year", "Month", "Day"])
    df = df.drop(columns=no_data).resample("1h").mean()
    df2 = df.resample("30min").mean().interpolate(method="time")
    df2 = df2.bfill(); df2 = df2.ffill() 
    return df, df2