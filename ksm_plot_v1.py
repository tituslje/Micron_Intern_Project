import pandas as pd
# import datetime as dt
# from datetime import date # library not used
import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec # library not used
import numpy as np
import seaborn as sns
# import math # library not used
import time
import matplotlib.dates as dt
# from kernelsmoothing import kernel_smooth


def kernel_smooth(x, y, x_datetime, bandwidth=None):
    x = np.array(x)
    y = np.array(y)

    # x = np.sort(x) # sorting is done twice, delete this one

    # sorting has been done before calling this func, no need to do twice
    if x_datetime:
        #x_time = x
        # x = pd.to_datetime(x) # assumes x can still be in string form
        # x = (x - x.min()).dt.total_seconds()/(3600*24) # convert to days from earliest date
        x = dt.date2num(x)
    # else: #no need for else
        # x_time = x #variable x_time is not used

    n = len(x)  # number of points

    if bandwidth is None:
        sigma = x.std()
        iqr = np.subtract(*np.percentile(x, [75, 25]))
        b = 1.06*min(sigma, iqr/1.34)*pow(len(x), -0.2)  # bandwidth
    else:
        b = bandwidth

    wgt = np.ones((n, n))

    wgt = (wgt*x).T
    ref = np.ones((n, n))*x

    # Calculate distances from all other points, then scale by bandwidth
    # Calculate guassian kernels
    wgt = np.exp((- 0.5 * np.power((wgt - ref) / b, 2)).astype(float))

    # Calculate sum of kernels to normalize weights
    kern_sum = np.sum(wgt, axis=1).reshape((n, 1))
    wgt = wgt * 1/kern_sum

    y_smoothed = np.matmul(wgt, y)

    return y_smoothed


def multiple_plot(df, x_axis=None):
    start = time.time()

    master = df
    cols = master.columns.to_list()
    if x_axis is None:
        exclude_list = ['StartLotKey', 'LotId', 'WaferId', 'WaferInstance', 'porconv'] + \
            [d for d in cols if 'Time' in d] + \
            [d for d in cols if ':Fab:' in d]
        x_datetime_cols = [d for d in cols if 'Time' in d]
        x_axis = x_datetime_cols[0]
        master[x_axis] = pd.to_datetime(master[x_axis])
        master = master.sort_values(x_axis, ascending=True)
    else:
        exclude_list = ['StartLotKey', 'LotId', 'WaferId',
                        'WaferInstance', 'porconv'] + [d for d in cols if ':Fab:' in d]
        x_axis = x_axis
        master = master.sort_values(x_axis, ascending=True)

    y_axis_cols = [d for d in cols if d not in exclude_list]

    por = master[master['porconv'] == 'por']
    conv = master[master['porconv'] == 'conv']

    for i in y_axis_cols:

        yaxis_name = i

        # First Kernel Smoothing for por data
        por = por[por[yaxis_name].notna()]
        por = por[por[x_axis].notna()]
        #por['days'] = pd.Series(por['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime']).dt.day
        y_ksvp = kernel_smooth(dt.date2num(np.sort(pd.to_datetime(
            por[x_axis]))), por[yaxis_name], x_datetime=True, bandwidth=None)

        # First Kernel Smoothing for conv data
        conv = conv[conv[yaxis_name].notna()]
        conv = conv[conv[x_axis].notna()]
        # conv['days'] = pd.Series(conv[x_axis]).dt.day
        y_ksvc = kernel_smooth(dt.date2num(np.sort(pd.to_datetime(
            conv[x_axis]))), conv[yaxis_name], x_datetime=True, bandwidth=None)

        # Plot Details
        fig, (ax, ax2) = plt.subplots(2, 1, gridspec_kw={
            'height_ratios': [1, 60], 'width_ratios': [10]}, sharex=True)
        ax.grid(True)
        ax2.grid(True)

        #graph = sns.scatterplot(x='5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime', y=yaxis_name,data=master,hue='porconv',ax=ax,ci=None)
        sns.scatterplot(x=x_axis, y=yaxis_name, data=master,
                        hue='porconv', ax=ax2, ci=None)
        ax2.plot(por[x_axis], y_ksvp, 'r', label='por')
        ax2.plot(conv[x_axis], y_ksvc, 'g', label='conv')

        # Broken-axis Method (to be replaced by z-score)
        ax.get_yaxis().set_visible(False)
        # ax.get_legend().remove()
        ax2.set_ylim(bottom=0, top=1)
        ax2.legend(bbox_to_anchor=(1, 1))

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
        ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **
                 kwargs)  # bottom-right diagonal

        plt.xticks(rotation=15)
        # plt.savefig(r"C:\Users\mdarmawan\Downloads\test_"+i+".png",bbox_inches='tight')
        plt.show()

    end = time.time()
    print('Runtime is: {} seconds'.format(str(end-start)))


def single_plot(x, y, x_axis, y_axis, porconv, x_datetime):
    start = time.time()

    master = pd.DataFrame()
    master[x_axis] = x
    master[y_axis] = y
    master['porconv'] = porconv
    if x_datetime is None:
        master[x_axis] = pd.to_datetime(master[x_axis])
        master = master.sort_values(x_axis, ascending=True)
    else:
        x_axis = x_axis
        master = master.sort_values(x_axis, ascending=True)

    por = master[master['porconv'] == 'por']
    conv = master[master['porconv'] == 'conv']

    yaxis_name = y_axis

    # First Kernel Smoothing for por data
    por = por[por[yaxis_name].notna()]
    por = por[por[x_axis].notna()]
    #por['days'] = pd.Series(por['5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime']).dt.day
    y_ksvp = kernel_smooth(dt.date2num(np.sort(pd.to_datetime(
        por[x_axis]))), por[yaxis_name], x_datetime=True, bandwidth=None)

    # First Kernel Smoothing for conv data
    conv = conv[conv[yaxis_name].notna()]
    conv = conv[conv[x_axis].notna()]
    # conv['days'] = pd.Series(conv[x_axis]).dt.day
    y_ksvc = kernel_smooth(dt.date2num(np.sort(pd.to_datetime(
        conv[x_axis]))), conv[yaxis_name], x_datetime=True, bandwidth=None)

    # Plot Details
    fig, (ax, ax2) = plt.subplots(2, 1, gridspec_kw={
        'height_ratios': [1, 60], 'width_ratios': [10]}, sharex=True)
    ax.grid(True)
    ax2.grid(True)

    #graph = sns.scatterplot(x='5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime', y=yaxis_name,data=master,hue='porconv',ax=ax,ci=None)
    sns.scatterplot(x=x_axis, y=yaxis_name, data=master,
                    hue='porconv', ax=ax2, ci=None)
    ax2.plot(por[x_axis], y_ksvp, 'r', label='por')
    ax2.plot(conv[x_axis], y_ksvc, 'g', label='conv')

    # Broken-axis Method (to be replaced by z-score)
    ax.get_yaxis().set_visible(False)
    # ax.get_legend().remove()
    ax2.set_ylim(bottom=0, top=1)
    ax2.legend(bbox_to_anchor=(1, 1))

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
    # plt.savefig(r"C:\Users\mdarmawan\Downloads\test_"+i+".png",bbox_inches='tight')
    plt.show()

    end = time.time()
    print('Runtime is: {} seconds'.format(str(end-start)))


def plot_endpoint(df, x_axis=None):
    start = time.time()

    master = df
    cols = master.columns.to_list()
    if x_axis is None:
        exclude_list = ['StartLotKey', 'LotId', 'WaferId', 'WaferInstance', 'porconv'] + \
            [d for d in cols if 'Time' in d] + \
            [d for d in cols if ':Fab:' in d]
        x_datetime_cols = [d for d in cols if 'Time' in d]
        x_axis = x_datetime_cols[0]
        master[x_axis] = pd.to_datetime(master[x_axis])
        master = master.sort_values(x_axis, ascending=True)
    else:
        exclude_list = ['StartLotKey', 'LotId', 'WaferId',
                        'WaferInstance', 'porconv'] + [d for d in cols if ':Fab:' in d]
        x_axis = x_axis
        master = master.sort_values(x_axis, ascending=True)

    y_axis_cols = [d for d in cols if d not in exclude_list]

    # por = master[master['porconv'] == 'por']
    # conv = master[master['porconv'] == 'conv']

    for i in y_axis_cols:
        single_plot()

    end = time.time()
    print('Runtime is: {} seconds'.format(str(end-start)))
