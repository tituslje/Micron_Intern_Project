import pandas as pd
# import numpy as np  #keep first, might be useful
import seaborn as sns
import matplotlib.pyplot as plt
from autoscale_visualization import scale, trendline, outliers_json
from sieve_outlier_anova import get_anova_score, stats, get_outlier, remove_outlier
from ksm_plot_v1 import kernel_smooth
from jsonexport import exptppt
import logging
import datetime as dt
import click
import os
import json


@click.command()
@click.argument('csv_file')
# @click.option('--operation', required=True, type=click.Choice(['autoscale', 'porconv'], case_sensitive=False), help='Choose to autoscale visualization or porconv comparison')
# , type=click.Choice(['1250-51 SLIT RECESS WET ETCH WEIGHT::MeasurementData::Product::MASS::DELTA_MASS - RAW_WAFER (Mean)', 'FINAL FUNCT PROD::WaferData::npnC', 'FINAL FUNCT PROD::WaferData::npmD', 'FINAL FUNCT PROD::WaferData::npuZQ']), help='Choose your variable of interest')
# @click.option('--interest', required=True)
# interest leave as it is for a while, we may plan to just plot all interested variables wihtin the csv
@click.option('--ppt/--no-ppt', default=False, help='Do you want to export ppt?')
def main(csv_file, ppt):  # removed operation and interest option for now as it's not used

    interest_probes = ['FINAL FUNCT PROD::WaferData::npuZQ',
                       'FINAL FUNCT PROD::WaferData::npnC', 'FINAL FUNCT PROD::WaferData::npmD']
    probe = len(interest_probes)*2

    start = dt.datetime.now()

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('testing.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info('-' * 30)
    logger.info(f'run start: {start}')

    # create json for stats
    save_path = 'C:\\Users\\atatang\\Desktop\\MyAssistant-Visualizer\\json'
    file_name = 'stats.json'
    stats_json = os.path.join(save_path, file_name)

    with open(stats_json, 'w') as f:
        json.dump({"job_id": "1234"}, f)
        click.echo("stats.json created")

    # create json for ppt_details
    file_name = 'ppt_details.json'
    ppt_details_json = os.path.join(save_path, file_name)

    with open(ppt_details_json, 'w') as f:
        json.dump([{"title": "Plots from Probe/FD Data",
                    "template": "empty.pptx",
                    "image_dir": "C:\\Users\\atatang\\Desktop\\MyAssistant-Visualizer\\figures\\",
                    "home": "C:\\Users\\atatang\\Desktop\\MyAssistant-Visualizer\\",
                    "probe": probe},
                   {"title": "Probe Plots"}], f)
        click.echo("ppt_details.json created")

    for interest in interest_probes:
        # will update later
        # datetime = "5450-51 SLIT RECESS WET ETCH::RunWaferData::ProcessEndDateTime"
        datetime = "5450-51 SLIT RECESS WET ETCH::RunData::ProcessEndDateTime"

        # load data and remove NaN values, then sort them
        logger.info(f'reading csv file... {csv_file}')
        data = pd.read_csv(csv_file)
        data[datetime] = pd.to_datetime(data[datetime])
        logger.info(f'removing NA rows...')
        data = data.loc[data[datetime].notna()]
        data = data.loc[data[interest].notna()]

        # get por and conv
        por = data.loc[data["porconv"] == "por"]
        conv = data.loc[data["porconv"] == "conv"]
        por = por.sort_values(by=[datetime])
        conv = conv.sort_values(by=[datetime])

        # get stats of raw data, before removing outliers
        click.echo('POR stats before outlier removal: [Mean, Std, Median]')
        stats(por, interest, "before", "por")
        click.echo('CONV stats before outlier removal: [Mean, Std, Median]')
        stats(conv, interest, "before", "conv")

        # kernel smooth
        logger.info(f'kernel smoothing in progress...')
        y_kvp = kernel_smooth(por[datetime], por[interest], x_datetime=True)
        y_kvc = kernel_smooth(
            conv[datetime], conv[interest], x_datetime=True)

        end = dt.datetime.now()
        runtime = (end - start).seconds
        logger.info(f'prep data and kernel smooth: {runtime}')

        # append the smoothed value to a new column for both por and conv
        por['y_kvp'] = y_kvp
        conv['y_kvc'] = y_kvc

        # ### Autoscale Visualization ###
        # logger.info(f'autoscale visualization in progress...')
        # mean = data[datetime].mean()
        # std = data[datetime].std()
        # new = data.loc[abs(data[datetime] - mean) < 2*std]

        # min_date = new[datetime].min()
        # max_date = new[datetime].max()

        # por = por.loc[(por[datetime] >= min_date) &
        #               (por[datetime] <= max_date)]
        # conv = conv.loc[(conv[datetime] >= min_date) &
        #                 (conv[datetime] <= max_date)]

        # new = scale(new, interest)
        # plt.figure(figsize=(10, 10))
        # sns.set_theme()
        # scatter = sns.scatterplot(data=new, x=datetime, y=interest,
        #                           hue="porconv", palette=dict(por="orange", conv="blue"))
        # por_trend = trendline(por[datetime], por["y_kvp"], "por")
        # conv_trend = trendline(conv[datetime], conv["y_kvc"], "conv")
        # plt.savefig("autoscaled_Visualization.png")

        # end = dt.datetime.now()
        # runtime = (end - start).seconds
        # logger.info(f'autoscaled_visualization: {runtime}')

        # sieve outliers
        logger.info("outlier sieving in progress...")
        data = get_anova_score(data, interest)
        cleaned_data = remove_outlier(data)
        cleaned_por = cleaned_data.loc[cleaned_data["porconv"] == "por"]
        cleaned_conv = cleaned_data.loc[cleaned_data["porconv"] == "conv"]
        cleaned_por = cleaned_por.sort_values(by=[datetime])
        cleaned_conv = cleaned_conv.sort_values(by=[datetime])

        # pass a json data of wafer id and lot id later from this csv, do later
        outliers = get_outlier(data)
        outliers.to_csv("outliers_data.csv")
        outliers_json(outliers, interest[-4:])

        # stats after removing outliers
        click.echo('POR stats after outlier removal: [Mean, Std, Median]')
        stats(cleaned_por, interest, "after", "por")
        click.echo('CONV stats after outlier removal: [Mean, Std, Median]')
        stats(cleaned_conv, interest, "after", "conv")

        end = dt.datetime.now()
        runtime = (end - start).seconds
        logger.info(f'outliers sieving: {runtime}')

        # kernel smooth for cleaned data
        logger.info(f'kernel smoothing for cleaned data in progress...')
        y_kvp = kernel_smooth(
            cleaned_por[datetime], cleaned_por[interest], x_datetime=True)
        y_kvc = kernel_smooth(
            cleaned_conv[datetime], cleaned_conv[interest], x_datetime=True)

        end = dt.datetime.now()
        runtime = (end - start).seconds
        logger.info(f'kernel smoothing for cleaned data: {runtime}')

        # append the smoothed value to a new column for both cleaned por and conv
        cleaned_por['y_kvp'] = y_kvp
        cleaned_conv['y_kvc'] = y_kvc

        ### Autoscale Visualization ###
        logger.info(f'autoscale visualization for cleaned data in progress...')
        mean = cleaned_data[datetime].mean()
        std = cleaned_data[datetime].std()
        new = cleaned_data.loc[abs(cleaned_data[datetime] - mean) < 2*std]

        min_date = new[datetime].min()
        max_date = new[datetime].max()

        cleaned_por = cleaned_por.loc[(cleaned_por[datetime] >= min_date) &
                                      (cleaned_por[datetime] <= max_date)]
        cleaned_conv = cleaned_conv.loc[(cleaned_conv[datetime] >= min_date) &
                                        (cleaned_conv[datetime] <= max_date)]

        # new = scale(new, interest)
        plt.figure(figsize=(10, 10))
        sns.set_theme()
        scatter = sns.scatterplot(data=new, x=datetime, y=interest,
                                  hue="porconv", palette=dict(por="orange", conv="blue"))
        por_trend = trendline(
            cleaned_por[datetime], cleaned_por["y_kvp"], "por")
        conv_trend = trendline(
            cleaned_conv[datetime], cleaned_conv["y_kvc"], "conv")
        plt.savefig(
            "figures\\autoscaled_Visualization_no-outliers_"+interest[-4:]+".png")

        # create the json details
        with open(ppt_details_json, 'r') as f:
            load = json.load(f)
            load.append({"title": "autoscaled_Visualization_no-outliers_"+interest[-4:],
                        "header": "Por & Conv Outliers:"})
        with open(ppt_details_json, 'w') as f:
            json.dump(load, f, indent=4)

        end = dt.datetime.now()
        runtime = (end - start).seconds
        logger.info(f'autoscale visualization with no outliers: {runtime}')

        # zoom in y axis
        new = scale(new, interest)
        plt.figure(figsize=(10, 10))
        sns.set_theme()
        scatter = sns.scatterplot(data=new, x=datetime, y=interest,
                                  hue="porconv", palette=dict(por="orange", conv="blue"))
        por_trend = trendline(
            cleaned_por[datetime], cleaned_por["y_kvp"], "por")
        conv_trend = trendline(
            cleaned_conv[datetime], cleaned_conv["y_kvc"], "conv")
        plt.savefig(
            "figures/autoscaled_Visualization_no-outliers_zoomed-y_"+interest[-4:]+".png")

        # create the json details
        with open(ppt_details_json, 'r') as f:
            load = json.load(f)
            load.append({"title": "autoscaled_Visualization_no-outliers_zoomed-y_"+interest[-4:],
                        "header": "Por & Conv Outliers:"})
        with open(ppt_details_json, 'w') as f:
            json.dump(load, f, indent=4)

        end = dt.datetime.now()
        runtime = (end - start).seconds
        logger.info(
            f'autoscale visualization with no outliers zoomed y: {runtime}')

    if ppt == True:
        click.echo('PPT')
        exptppt('json\\ppt_details.json', outlier_json="json\\outliers.json",
                imagedir="C:\\Users\\atatang\\Desktop\\MyAssistant-Visualizer\\figures\\")
    else:
        print('Nothing')

    end = dt.datetime.now()
    runtime = (end - start).seconds
    logger.info(f'run end: {end}')
    logger.info(f'total runtime: {runtime}')


if __name__ == '__main__':
    main()
