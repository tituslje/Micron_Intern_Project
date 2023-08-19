from math import sqrt
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sb
import json
import os

# Reference: https://www.real-statistics.com/one-way-analysis-of-variance-anova/outliers-anova/
# Reference: https://www.real-statistics.com/one-way-analysis-of-variance-anova/basic-concepts-anova/

# get the range where conv points exist


def x_conv_range(data, column):
    conv_data = data.loc[data["porconv"] == "conv"]
    min_date = conv_data[column].min()
    max_date = conv_data[column].max()

    x_scale_data = data.loc[(data[column] >=
                             min_date) & (data[column] <= max_date)]
    return x_scale_data

# obtain anova score for variable of interest


def get_anova_score(data, column):
    conv_before = data.loc[data["porconv"] == "conv"]
    por_before = data.loc[data["porconv"] == "por"]

    mean_conv_before = conv_before[column].mean()
    mean_por_before = por_before[column].mean()

    # calculate Sum of Squares within
    ss_conv = 0
    for i in conv_before[column]:
        ss_conv = ss_conv + (i-mean_conv_before)**2

    ss_por = 0
    for i in por_before[column]:
        ss_por = ss_por + (i-mean_por_before)**2

    ss_within = ss_conv + ss_por

    # calculate degree of freedom within
    k = 2  # k is no. of groups (our case, k is por and conv, k = 2)
    dof_within = len(data) - k

    # calculate Mean Square Within (ms)
    ms_within = ss_within/dof_within

    # standard error within
    std_w = sqrt(ms_within)

    anova_score = []
    count = 0
    for i in data[column]:
        if data.iloc[count]["porconv"] == "conv":
            anova_score.append(
                abs((data.iloc[count][column] - mean_conv_before)/std_w))
        else:
            anova_score.append(
                abs((data.iloc[count][column] - mean_por_before)/std_w))
        count += 1

    data["anova_score"] = anova_score
    return data

# obtain mean, std, and median of variable of interest in a list


def stats(data, column, when, type):
    save_path = 'C:\\Users\\tituslim\\exportcode\\'
    file_name = 'stats.json'
    completeName = os.path.join(save_path, file_name)
    with open(completeName, 'r') as f:
        load = json.load(f)
    stats = {}
    stats["Mean"] = data[column].mean()
    stats["Std"] = data[column].std()
    stats['Median'] = data[column].median()
    if type == "por":
        if when == "before":
            load["por_stats_before_" + column] = stats
        else:
            load["por_stats_after_" + column] = stats
    else:
        if when == "before":
            load["conv_stats_before_" + column] = stats
        else:
            load["conv_stats_after_" + column] = stats
    with open(completeName, 'w') as f:
        json.dump(load, f, indent=4)
    print(stats)

# extract outlier data from csv


def get_outlier(data):
    mean = data['anova_score'].mean()
    std = data['anova_score'].std()

    return data.loc[abs(data["anova_score"] - mean) > 3*std]

# remove outlier data from csv


def remove_outlier(data):
    mean = data['anova_score'].mean()
    std = data['anova_score'].std()

    return data.loc[abs(data["anova_score"] - mean) <= 3*std]

# convert outliers data to json (only top 10 outliers)


def outliers_to_json(data, column):
    save_path = 'C:\\Users\\tituslim\\exportcode\\'
    file_name = "outliers.json"
    completeName = os.path.join(save_path, file_name)
    with open(completeName, 'r') as f:
        load = json.load(f)
    data = data.sort_values(by=["anova_score"], ascending=False)
    data = data.loc[data["porconv"] == 'conv']
    data = data[:10]
    count = 0
    lot_wafer = {}
    for i in data.WaferId:
        if data.iloc[count]['LotId'] not in lot_wafer:
            lot_wafer[data.iloc[count]['LotId']] = [i]
        else:
            lot_wafer[data.iloc[count]['LotId']] += [i]
        count += 1
    load[column] = lot_wafer
    with open(completeName, 'w') as f:
        json.dump(load, f, indent=4)

# {
#   blabla,
#   npuZQ : { lot id : [waferid], lot id: [waferid]},
#   npfsd : { blbalba}
# }
