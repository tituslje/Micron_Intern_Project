# import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats


def scale(data, column):
    z = np.abs(stats.zscore(data[column]))
    data[column + "::z-score"] = z
    return data.loc[data[column + "::z-score"] <= 0.5]


def trendline(x, y, type):
    sns.set_theme()
    if type == "por":
        return sns.lineplot(x, y, color='red', legend="brief", label='por', sort=False)
    if type == "conv":
        return sns.lineplot(x, y, color='green', legend="brief", label='conv', sort=False)
