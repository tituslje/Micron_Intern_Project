import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import seaborn as sns
import math

master = pd.read_csv('Bad_Data.csv')

#distinguish data by wafer ids
waferids = list(set(list(master.loc[:,'WaferId'])))
final_df = pd.DataFrame()
for wafer_id in waferids:
    temp_df = master[master['WaferId'] == wafer_id].copy()
    final_df = pd.concat([final_df,temp_df],axis=0)

xyaxes = final_df.copy()
xyaxes['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'] = pd.to_datetime(xyaxes['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime'])

y_axis_data = [item for item in list(xyaxes['FINAL FUNCT PROD::WaferData::npnC']) if not(math.isnan(item)) == True]
y_axis_data = [item for item in y_axis_data if item != 0]
avg_y = sum(list(y_axis_data))/len(list(y_axis_data))

#Scaling x-axis
#Need to find a reliable way to scale (since the x-axis is now datetime format)

fig, (ax,ax2) = plt.subplots(2,1,gridspec_kw={'height_ratios':[1,15]},sharex=True)
ax.grid(True)
ax2.grid(True)

#crude plotting of trend using lines
graph1 = sns.lineplot(x='5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime', y='FINAL FUNCT PROD::WaferData::npnC',data=xyaxes,hue='porconv',marker='o',ax=ax,ci=None)
graph2 = sns.lineplot(x='5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime', y='FINAL FUNCT PROD::WaferData::npnC',data=xyaxes,hue='porconv',marker='o',ax=ax2,ci=None)

y_min, y_max = ax.get_ylim()
ax.set_ylim(avg_y, y_max)  # outliers only
ax2.set_ylim(y_min, avg_y)  # most of the data
ax.get_yaxis().set_visible(False)
ax2.set_ylim(bottom=0.) #Set minimum y axis value to be 0 (Yield loss will almost always be > 0)
ax2.set_ylim(top=1) #Set maximum y axis value to be 1 since most points of focus are within 0 and 1.
#ax2.get_yaxis().set_visible(False)
#ax.set_xlim(x_min,x_max)
ax.get_legend().remove()

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
plt.savefig('npnC.png',bbox_inches='tight')
