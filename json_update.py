import json
import os
import pandas as pd

#update created json (with ppt details) with slide details
#after each plot is saved

def update_json(ppt_details_json,plot_title, lst):
    with open(ppt_details_json, 'r') as f:
        # create the json details for 1 section
        load = json.load(f)
        load.append({"title": plot_title,
                    "header": "Por & Conv Outliers:"})
    with open(ppt_details_json, 'w') as f:
        json.dump(load, f, indent=4)

    #updates the json lst export_data in main() in the export.py code
    dict = {"title": plot_title,
                    "header": "Por & Conv Outliers:"}
    lst.append(dict)