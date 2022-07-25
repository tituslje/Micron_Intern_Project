import pandas as pd
import datetime as dt
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import seaborn as sns
import math
import time
from kernelsmoothing import fast_kernel_smooth, kernel_smooth
from scale_sieve import x_scale

#filename = str(input('Please enter csv file name: '))
master = pd.read_csv('Bad_data.csv')
#name = str(input('Y-Axis you wish to plot(Key in npmD for testing, otherwise last few unique letters): ')) #might not need to add in
master['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'] = pd.to_datetime(master['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'])
master.sort_values('5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime',ascending=True)

yaxis_name = 'FINAL FUNCT PROD::WaferData::npmD' #convenience

#Scaling y-axis (used to break the graph into 2 parts)
#y_axis_data = [item for item in list(master[yaxis_name]) if not(math.isnan(item)) == True]
#y_axis_data = [item for item in y_axis_data if item != 0]
#avg_y = sum(list(y_axis_data))/len(list(y_axis_data))

master2 = master.copy()
#lesser = master2[master2[yaxis_name] < 1]
por = master2[master2['porconv'] == 'por']
conv = master2[master2['porconv'] == 'conv']
#greater = master2[master2[yaxis_name] > 1]

#Kernel Smoothing for por data
por = por[por[yaxis_name].notna()]
por = por[por['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'].notna()]
x_kvp, y_kvp = fast_kernel_smooth(por['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'],por[yaxis_name],n_order=15,x_datetime=True) #returns 2 lists, x and y

#Kernel Smoothing for conv data
conv = conv[conv[yaxis_name].notna()]
conv = conv[conv['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'].notna()]
x_kvc, y_kvc = fast_kernel_smooth(conv['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'],conv[yaxis_name],n_order=15,x_datetime=True) #returns 2 lists, x and y

#Loading figure and axes + subplot sizes
fig, (ax,ax2) = plt.subplots(2,1,gridspec_kw = {'height_ratios':[1,60],'width_ratios':[10]},sharex=True)
ax.grid(True)
ax2.grid(True)

#graph = sns.scatterplot(x='5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime', y=yaxis_name,data=master,hue='porconv',ax=ax,ci=None)
graph1 = sns.scatterplot(x='5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime', y=yaxis_name,data=master2,hue='porconv',ax=ax2,ci=None)
line1 = ax2.plot(x_kvp,y_kvp,'r',label='por')
line2 = ax2.plot(x_kvc,y_kvc,'g',label='conv')

#Broken-axis Method
#y_min, y_max = ax.get_ylim()
#ax.set_ylim(master2[yaxis_name].max(), y_max)  # outliers only
ax.get_yaxis().set_visible(False)
#ax.get_legend().remove()
#Q1 = np.percentile(master2[yaxis_name],25,method='midpoint')
#Q3 = np.percentile(master2[yaxis_name],75,method='midpoint')
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
plt.savefig('trial2.png',bbox_inches='tight')
