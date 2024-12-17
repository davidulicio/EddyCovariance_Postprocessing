# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 09:50:25 2024
Data screening functions
@author: David Trejo Cancino
"""
import numpy as np
import configparser
import pandas as pd
#%% Filtering data functions

def biomet_physical_values(PATH, df):
    import ast
    # Read the biomet inifile
    config = configparser.ConfigParser()
    config.read(PATH)
    sections = config.sections()
    df2 = pd.DataFrame()
    for section in sections:
        metadata = config[section]
        inputvarname = metadata["inputfilename"]
        variablename = metadata["variablename"]
        try: 
            var = df[inputvarname]
            # Read min and max values of the variable
            minmax = np.float64(metadata["minmax"][1:-1].split(","))
            # Create a boolean mask for values outside the interval
            mask = (var < minmax[0]) | (var > minmax[1])
            # Convert to nan data outside the limits
            # df[inputvarname][mask] = np.nan
            var[mask] = np.nan
            # Rename column to Ameriflux standard format
            # df = df.rename(columns={inputvarname: variablename})
            df2[variablename] = var
        except KeyError:
            print("Variable " + inputvarname+" is not available in the dataset")
            pass
    return df2


def dependencies_qc(variable, min_val, max_val):
    """
    Returns a boolean array where "1" or True corresponds to the data to delete.

    Parameters
    ----------
    variable : array or Series
        Variable that is another variable is going to depend on.
    min_val : float or int
        Minimum physical value.
    max_val : float or int
        Maximum physical value.

    Returns
    -------
    valid : Boolean array
        Mask of the valid data dependending on the given variable.

    """
    boolean = np.zeros_like(variable)
    boolean[variable>max_val] = 1; boolean[variable<min_val] = 1
    boolean = boolean==1
    return boolean


def quality_screening(variable, min_val, max_val, date_exclusions,
                      dependencies, foken_flags):
    """
    Returns filtered data of the variable desired using folken_flags, 
    physical possible values, dependencies and date exclusion.

    Parameters
    ----------
    variable : array
        Variable to screen.
    min_val : float
        Minimal possible value.
    max_val : float
        Maximal possible value.
    date_exclusions : boolean array or float
        Dates which are going to be filtered from the sample. If float it does
        not apply the filter.
    dependencies : boolean array or float
        Boolean array where false implies wrong data from the dependency variable
        thus wrong data of the desired variable. If float it does not apply the
        filter.
    foken_flags : array or float
        Flux quality flags for micrometeorological tests using Mauder and Foken
        (2004) policy. If float, it does not apply the filter.

    Returns
    -------
    variable : array
        Filtered variable.

    """
    variable = np.copy(variable)
    variable[variable>max_val] = np.nan; variable[variable<min_val] = np.nan
    variable[date_exclusions] = np.nan
    variable[~np.isfinite(variable)] = np.nan
    variable[dependencies] = np.nan
    try:
        float(date_exclusions)
        pass
    except TypeError:
        variable[date_exclusions] = np.nan
    try:
        float(foken_flags)
        pass
    except TypeError:
        variable[foken_flags==2] = np.nan
    return variable