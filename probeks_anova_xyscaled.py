from cmath import nan
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import seaborn as sns
import math
import time
from kernelsmoothing import fast_kernel_smooth
from scale_sieve import x_scale
from scipy import stats

master = pd.read_csv('Bad_data.csv')
master['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'] = pd.to_datetime(
    master['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'])

yaxis_name = 'FINAL FUNCT PROD::WaferData::npmD'  # convenience

master = master.loc[master["5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime"].notna()]
master = master.loc[master[yaxis_name].notna()]
z = np.abs(stats.zscore(master[yaxis_name]))
master['z-score'] = z

master2 = master.copy()

master = x_scale(
    master, '5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime')

mean = master[yaxis_name].mean()
std = master[yaxis_name].std()

# Kernel Smoothing for por data
por = master2.loc[master2["porconv"] == "por"]
conv = master2.loc[master2["porconv"] == "conv"]
x_kvp, y_kvp = fast_kernel_smooth(por['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'],
                                  por[yaxis_name], n_order=100, x_datetime=True)  # returns 2 lists, x and y
x_kvc, y_kvc = fast_kernel_smooth(conv['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'],
                                  conv[yaxis_name], n_order=100, x_datetime=True)  # returns 2 lists, x and y


scaled_y = master.loc[master['z-score'] <= 1]

plt.figure(figsize=(10, 10))
sns.set_theme()
graph = sns.scatterplot(data=scaled_y, x='5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime',
                        y=yaxis_name, hue="porconv", palette=dict(por="orange", conv="blue"))
por_line = sns.lineplot(x_kvp, y_kvp, color='red',
                        legend="brief", label="por")
conv_line = sns.lineplot(x_kvc, y_kvc, color='green',
                         legend="brief", label="conv")
plt.savefig('new_plot.png')