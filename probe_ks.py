import pandas as pd
import datetime as dt
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import seaborn as sns
import math
import time
from kernelsmoothing import kernel_smooth

start = time.time()
#filename = str(input('Please enter csv file name: '))
master = pd.read_csv('Bad_data.csv')
#name = str(input('Y-Axis you wish to plot(Key in npmD for testing, otherwise last few unique letters): ')) #might not need to add in
master['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'] = pd.to_datetime(master['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'])
master = master.sort_values('5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime',ascending=True)
yaxis_name = 'FINAL FUNCT PROD::WaferData::npmD' #convenience

#Get an array of indexes+1 to deal with kernel_smooth input
#index_lst = list(master.index)
index_lst = []
master['indexnum'] = pd.Series([idx+1 for idx in index_lst])

master.insert(1,'indexnum',pd.Series(index_lst))

#lesser = master2[master2[yaxis_name] < 1]
por = master[master['porconv'] == 'por']
conv = master[master['porconv'] == 'conv']
#greater = master2[master2[yaxis_name] > 1]

#First Kernel Smoothing for por data
por = por[por[yaxis_name].notna()]
por = por[por['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'].notna()]
#por['days'] = pd.Series(por['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime']).dt.day
y_ksvp = kernel_smooth(por['indexnum'],por[yaxis_name],bandwidth=None)

#First Kernel Smoothing for conv data
#conv = conv[conv[yaxis_name].notna()]
#conv = conv[conv['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'].notna()]
#conv['days'] = pd.Series(conv['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime']).dt.day
#y_ksvc = kernel_smooth(conv['indexnum'],conv[yaxis_name],bandwidth=None)

#Plot Details
fig, (ax,ax2) = plt.subplots(2,1,gridspec_kw = {'height_ratios':[1,60],'width_ratios':[10]},sharex=True)
ax.grid(True)
ax2.grid(True)

#graph = sns.scatterplot(x='5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime', y=yaxis_name,data=master,hue='porconv',ax=ax,ci=None)
graph1 = sns.scatterplot(x='5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime', y=yaxis_name,data=master2,hue='porconv',ax=ax2,ci=None)
line1 = ax2.plot(por['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'],y_ksvp,'r',label='por')
#line2 = ax2.plot(conv['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'],y_ksvc,'g',label='conv')

#Broken-axis Method (to be replaced by z-score)
ax.get_yaxis().set_visible(False)
#ax.get_legend().remove()
ax2.set_ylim(bottom = 0, top = 1) 
ax2.legend(bbox_to_anchor=(1,1))

# hide the spines between ax and ax2
ax.spines['bottom'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax.xaxis.tick_top()
ax.tick_params(labeltop=False)  # don't put tick labels at the top
ax2.xaxis.tick_bottom()

d = .015  # how big to make the diagonal lines in axes coordinates
# arguments to pass to plot, just so we don't keep repeating them
kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
ax.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

plt.xticks(rotation=15)
plt.savefig('trial4.png',bbox_inches='tight')

end = time.time()
print('Runtime is: {} seconds'.format(str(end-start)))