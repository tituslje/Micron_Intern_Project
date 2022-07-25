import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import seaborn as sns
import math

#read data, only the file that is read changes
#filename = str(input('Please enter csv file name: '))
master = pd.read_csv('FD Raw Data.csv')
master = master.iloc[1:,:]
master.sort_values('TimeStamp',ascending=True)

#distinguish data by their wafer ids, same code everytime
# waferids = list(set(list(master.loc[:,'WAFER_ID'])))
# final_df = pd.DataFrame()
# for wafer_id in waferids:
#     temp_df = master[master['WAFER_ID'] == wafer_id].copy()
#     rowcount = len(temp_df)
#     temp_df['rownum'] = range(rowcount)
#     final_df = pd.concat([final_df,temp_df],axis=0)

#get the average y-axis value
y_axis_data = [item for item in list(final_df['Arm1DIWFlow']) if not(math.isnan(item)) == True]
y_axis_data = [item for item in y_axis_data if item != 0]
avg_y = sum(list(y_axis_data))/len(list(y_axis_data))

#Scaling x-axis
xydata = final_df[['Arm1DIWFlow','rownum']]
#nandata = [item for item in list(final_df['Arm1DIWFlow']) if math.isnan(item) == True]
x_axis_data = []
#for nan in nandata:
for y,x in xydata.itertuples(index=False):
    if y != 0 and math.isnan(y) == False:
        if x != 0:
            x_axis_data.append(x)

x_axis_data = list(dict.fromkeys(x_axis_data))
indx = 0
for x in x_axis_data:
    if max(x_axis_data) - 10 <= x <= max(x_axis_data): #removing abnormally large values from the interval we want to zoom in on
        x_axis_data.remove(x)

print(x_axis_data)
x_min = min(x_axis_data)
x_max = max(x_axis_data)

#get the KDM/KEB codes to put in sns lineplot function
toollist = final_df['ToolName'].tolist()
KList = []
for tool in toollist:
    if 'KDM' in tool:
        KList.append('KDM')
    elif 'KEB' in tool:
        KList.append('KEB')

fig, (ax,ax2) = plt.subplots(2,1, gridspec_kw={'height_ratios':[8,1],'width_ratios':[10]},sharex=True)
ax.grid(True)
ax2.grid(True)

graph = sns.lineplot(x='rownum',y='Arm1DIWFlow',data=final_df,hue=KList,palette='magma',ax=ax,marker='o',ci=None)
graph = sns.lineplot(x='rownum',y='Arm1DIWFlow',data=final_df,hue=KList,palette='magma',ax=ax2,marker='o',ci=None)

y_min, y_max = ax.get_ylim()
ax.set_ylim(avg_y, y_max)  # outliers only
ax2.set_ylim(y_min, avg_y)  # most of the data
ax.set_xlim(x_min,x_max)
ax2.get_legend().remove()

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

plt.savefig('KDMKEB_broken.png',bbox_inches='tight')
