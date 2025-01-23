# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 09:50:25 2024
Data screening functions
@author: David Trejo Cancino
"""
import numpy as np
import yaml
import pandas as pd
#%% Filtering data functions

def physical_range(yaml, df):
    """
    Filter extreme values using the limits defined in the YAML configuration file

    Parameters
    ----------
    yaml : dict
        Dictionary from the YAML configuration file.
    df : DataFrame
        DataFrame of the data to be filter.

    Returns
    -------
    df2 : DataFrame
        DataFrame with the data already filtered using the extreme limits.

    """
    # Read sections of the yaml file
    sections = yaml.keys()
    # filter data in a loop for every section and rename to Ameriflux format
    df2 = pd.DataFrame()
    for section in sections:
        metadata = yaml[section]
        inputvarname = metadata["inputFileName"]
        variablename = metadata["variableName"]
        try: 
            var = df[inputvarname].copy()
            # Read min and max values of the variable
            minmax = np.float64(metadata["minMax"])
            # Create a boolean mask for values outside the interval
            mask = (var < minmax[0]) | (var > minmax[1])
            # Convert to nan data outside the limits
            # df[inputvarname][mask] = np.nan
            var[mask] = np.nan
            # Rename column to Ameriflux standard format
            df2[variablename] = var
        except KeyError:
            print("Variable " + inputvarname+" is not available in the dataset")
            pass
    return df2


def dependencies_filtering(biomet_yaml, df):
    """
    Read the dependencies of a variable and propagate the dependencies' nan values
    to the variable.

    Parameters
    ----------
    biomet_yaml : dict
        Dictionary from the YAML configuration file.
    df : DataFrame
        DataFrame of the data to be filtered.

    Returns
    -------
    df3 : DataFrame
        DataFrame of the data already filtered using the dependencies.

    """
    sections = biomet_yaml.keys()
    df3 = df.copy(deep=True)
    for section in sections:
        metadata = biomet_yaml[section]
        variablename = metadata["variableName"]
        # try:
        mask = np.zeros_like(df[variablename]) == 1 # Mask of Falses
        try:
            dep = biomet_yaml[variablename]["dependent"]
            # In each loop the non valid data is propagated to the mask as Trues
            try:
                for dependency in dep:
                    mask = mask + df[dependency].isna()
                # If one of the dependencies is nan (due to lack of data or previous
                # removal) then the nan values is propagated to the variable
            except TypeError:
                pass  # If the dependency feature does not have a variable, then it is omitted
                
            df3.loc[mask, variablename] = np.nan
        except KeyError:
            pass  # If the variable doesn't have the dependecies feature, it is skipped
    return df3
    
    
    
    
    # sections = biomet_yaml.keys()
    # df2 = df.copy(deep=True)
    # for section in sections:
    #     metadata = biomet_yaml[section]
    #     variablename = metadata["variableName"]
    #     # try:
    #     mask = np.zeros_like(df2[variablename]) == 1 # Mask of Falses
    #     try:
    #         dep = biomet_yaml[variablename]["dependent"]
    #         # In each loop the non valid data is propagated to the mask as Trues
    #         try:
    #             for dependency in dep:
    #                 mask = mask + df2[dependency].isna()
    #                 print(dependency)
    #             # If one of the dependencies is nan (due to lack of data or previous
    #             # removal) then the nan values is propagated to the variable
    #         except TypeError:
    #             pass  # If the dependency feature does not have a variable, then it is omitted
                
    #         df2.loc[mask, variablename] = np.nan
    #     except KeyError:
    #         pass  # If the variable doesn't have the dependecies feature, it is skipped
    #     return df2
    
    
    
    
    # sections = biomet_yaml.keys()
    # df2 = biomet2.copy()
    # for section in sections:
    #     metadata = biomet_yaml[section]
    #     variablename = metadata["variableName"]
    #     try:
    #         dep = biomet_yaml[variablename]["dependent"]
    #         mask = np.zeros_like(biomet2[variablename]) == 1 # Mask of Falses
    #         try:
    #             # In each loop the non valid data is propagated to the mask as Trues
    #             for dependency in dep:
    #                 mask = mask + biomet2[dependency].isna()
    #         except TypeError:
    #             pass  # If the variable doesn't have dependecies it is skipped
    #         # If one of the dependencies is nan (due to lack of data or previous
    #         # removal) then the nan values is propagated to the variable
    #         df2.loc[mask, variablename] = np.nan
    #     except KeyError:
    #         pass # Skip variables that do not include the dependent feature



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