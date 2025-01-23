# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 10:22:58 2024

@author: david
"""

from canopy_height_estimation import h_estimation
from ECCC_metstations_data import *
import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt

#%% data reading
# PATH = "U:/Sites/UQAM_1/Flux/"
# FILENAMES = glob.glob(PATH+"2024-*")
# df = []
# for filename in FILENAMES:
#     try:
#         dfo = pd.read_csv(filename, sep="\t")
#         units = dfo.iloc[0]; dfo = dfo[2:]
#         df.append(dfo)
#     except pd.errors.EmptyDataError:
#         pass
# df = pd.concat(df);
# df.index = pd.DatetimeIndex(df.date.astype(str)+" "+df.time.astype(str))
# df = df.drop(columns=["date", "time", "filename", "DATAH", "DOY"])
# df = df.astype(float)
# df[df==9999.99] = np.nan; df[df==-9999] = np.nan
#%% full output
FILE = "C:/Projects/UQAM/Sites/UQAM_1/EP_Output/20241125/eddypro_UQAM1_NOV_full_output_2024-11-28T060456_adv.csv"
df = pd.read_csv(FILE, skiprows=[0])
units = df.loc[0]; df = df[1:]
df.index = pd.DatetimeIndex(df.date.astype(str) + " " + df.time.astype(str))
no_data = df.columns[df.isna().sum()==len(df)].to_list()
no_data.extend(["filename", "date", "time"])
df = df.drop(columns=no_data)
units = units.drop(columns=no_data)
df = df.astype(float)
df[df==-9999] = np.nan; df[df==9999.99] = np.nan
df = df.resample("30min").mean()
#%% variables
# ws = biomet.WS
umean = df.u_rot
vmean = df.v_rot
ustar = df["u*"]
u = np.sqrt(umean**(2) + vmean**(2))
# u = ws

sp = df["(z-d)/L"].abs()
neutral_mask = sp<=0.1 # Neutral conditions
turbulence_mask = (ustar > 0.2) * (ustar < 0.4)
direction = df.wind_dir > 200
mask = turbulence_mask * neutral_mask #* direction
z = 7.1  # measurement height
k = 0.4
b = 0.6 + 0.1* np.exp(k * u / ustar)
h = z / (b)
h[~mask] = np.nan
#%%
h2, h2_daily = h_estimation(df)
#%%
# plt.figure()
# plt.plot(h)
# plt.plot(h2, alpha=0.5)
# plt.show()

#%% Get data from near meteorological stations
ids, names = canadian_stations(-72.6850, 46.1645)
print(names)
met_data = []
for stn_id in ids:
    met = get_met_data(years=[x for x in range(df.index.year.min(), df.index.year.max()+1, 1)],
                              months=[x for x in range(1,13,1)],
                              stn_id=stn_id)
    met_data.append(met[0])
met_data = pd.concat(met_data, axis=1)
print("The columns kept for biomet gapfilling are:")
print(met_data.columns.unique())
