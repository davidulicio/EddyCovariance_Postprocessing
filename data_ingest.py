# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 10:22:50 2024

@author: David Trejo

Data ingest
Functions to read and filter data
"""

import numpy as np
import pandas as pd

#%% data reading functions


def df_fulloutput(PATH):
    """
    Reads the EddyPro fullout file and return a dataframe of the data and their
    units.

    Parameters
    ----------
    PATH : str
        String of the directory to the file.
    FILENAME_FULL : str
        Filename.

    Returns
    -------
    full : DataFrame
        DataFrame of the fulloutput data with the datetime as index .
    units : Series
        Series of the units of each variable as given by EddyPro.

    """
    # Reading of fulloutput file
    full = pd.read_csv(PATH, skiprows=([0]),
                       low_memory=False)
    units = full.iloc[0][3:]; full = full[1:]
    # Indexing
    full.index = pd.DatetimeIndex(full.date.astype(str) +' '+ full.time.astype(str))
    # Droping columns and changing data to float
    full = full.drop(columns=['filename', 'date', 'time']).astype(float)
    full[full==-9999] = np.nan
    # 30-min data consistency and sorting
    full = full.resample('30min').mean()
    return full, units


def df_biomet(PATH):
    """
    Reads the biomet data coming from a CSI datalogger. It can read multiple
    files if the filename is given with a string + *.

    Parameters
    ----------
    PATH : str
        String of the directory to the file.
    FILENAME_BIOMET : str
        Filename, it can read multiple files if the filename uses an *.

    Returns
    -------
    df : DataFrame
        DataFrame of the biomet data with the datetime as index.
    units : Series
        Series of the units of each variable.

    """
    import glob
    df = []
    # Lists all the files with silimar filenames
    FILENAMES = glob.glob(PATH)
    for filename in FILENAMES:
        dfo = pd.read_csv(filename, skiprows=[0])
        units = dfo.iloc[0]; dfo = dfo[2:]
        df.append(dfo)
    # Concatenates all the files
    df = pd.concat(df)
    # Indexing
    df.index = pd.DatetimeIndex(df.TIMESTAMP)
    # Droping columns and changing data to float
    df = df.drop(columns=["TIMESTAMP"]).astype(float, errors="ignore")
    df[df==-9999] = np.nan
    # Droping columns with no data
    no_data = df.columns[df.isna().sum()==len(df)].to_list()
    df = df.drop(columns=no_data)
    units = units.drop(columns=no_data)
    # 30-min data consistency and sorting
    df = df.resample("30min").mean()
    return df, units


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
    df = pd.read_csv(PATH)
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
    df = df.drop(columns=no_data)
    df = df.resample("30min").mean().interpolate(method="time")
    df = df.bfill(); df = df.ffill() 
    return df


    
def var_reading(varname, data, boolean):
    """
    Reads variables from a dataframe and turns non valid data into NaN.

    Parameters
    ----------
    varname : str
        Column name of the variable.
    data : DataFrame
        Pandas DataFrame that includes the variable to read.
    boolean : Boolean
        True if the variable is convertible into a float.

    Returns
    -------
    var : array
        Data of the variable desired.

    """
    if boolean:
        var = np.float64(data[varname])
        var[var<-9998] = np.nan
    else:
        var = np.data[varname]
    return var



