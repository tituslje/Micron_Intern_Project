# Welcome and Acknowledgements

Welcome to this space, where I showcase what I and my fellow mentors have done throughout the space of Summer 2022 at Micron!

For the sake of data confidentiality, some references are changed and I was not able to obtain the entire code back from the company. However, I will still provide a concise explanation of what is the mission objective, what we had done and the intended results!

A big thank you to everyone who made it possible:
1. The PEE WET team at Micron Fab 10N for your warm encouragement during the course of my internship
2. Supervisor **Ong Hui Ting** for warmly welcoming me and integrating me into the team!
3. Mentor **Darren Lou Wei Hao** for your commitment to giving me as best a mentorship as you can despite your busy schedule
4. Fellow intern **Andrew Tatang** for contributing to the statistics portion and being my best buddy during the 3 months while coding
5. A special shoutout to the software engineer folks at PEE WET, for helping to construct the kernel smoothing code found in **ksm_plot_v1.py**.  
6. Other people who I did not name, but participated in the project in one way or another!

To begin, do read the requirements.txt file before using the source code files! A good habit will be to use a virtual environment for version control as well.

**Note: Current Python source code set is not optimized for any CSV file format, only the format that I and Andrew worked on back at Micron. Future updates coming soon by Fall 2023, so stay tuned!***

Without further ado, the next few sections will cover the project's brief mission objective, the key deliverables and the intended outcome!

## Project Mission Objective

My mentor Darren's vision: To create a centralised website acting as a source of data collection and storage for the entire fab in future. The value in this is faster data retrieval, potentially saving 240 man-hours per month in future.

I second his vision. In this world where data is getting bigger and bigger, the question of how to store and collect data in an efficient manner becomes an ever-changing goalpost. In addition, how to make sense of big data and all the intricate relationships becomes a question that never has a definite answer, there is only a most correct answer up to a certain point in time before a new technological breakthrough is made (my opinion and interest).

### Key Deliverables

Most of the forework has already been completed before I came in, so the task for us is to:
1. Develop a program to make data retrieval presentable in the form of a PowerPoint, the workflow will be as such:
   -- Process data from a CSV file containing cleaned and processed data.
   -- Calculate relevant statistics and make relevant line trends from data collected
   -- Present all data in an organised manner, all encapsulated in a PowerPoint file.

As for myself, I mainly contributed the data visualisation and presentation techniques covered in files **main.py**, **autoscale_visualisation.py**, **ksm_plot_v1.py** and **export_funcs.py** using matplotlib, pandas and numpy. 

In addition, I also assisted Andrew Tatang in the statistics portion outlined in files **sieve_outlier_anova.py**, with the relevant knowledge acquired from my Economics background (LETS GO US).

## Detailed Code Description and Project Outcome (Outputs)

This Python script has five source code files, namely:
1. **main.py** containing the entire script's main function (data manipulation --> statistics calculation --> data visualisation --> data presentation (PPT)).
2. **autoscale_visualisation.py** containing code for data visualisation and some data manipulation (scaling by z score)
3. **sieve_outlier_anova.py** that sieves out all data anomalies per data group using the ANOVA statistic.
4. **ksm_plot_v1.py** containing code for kernel smoothing of line plots to make nicer trendlines.
5. **export_funcs.py** which covers the functions of exporting the data plots and outlier (data anomalies) statistics data to a PowerPoint file which is generated in the main code.

In summary, the Python script uses the Click library to create a command-line application. It has a main function that processes data from a CSV file and creates a PowerPoint presentation if specified. Here's a concise summary:

**Functionality:**
The script processes data from a CSV file, applies outlier detection, performs kernel smoothing, and generates PowerPoint slides with data visualizations. It supports two modes: data processing without creating a presentation (`--no-ppt` option) and data processing with presentation creation (`--ppt` option).

**Inputs:**
- Command-line arguments:
  - `csv_file`: Path to the input CSV file containing data.
- Command-line options:
  - `--ppt`: Flag indicating whether to create a PowerPoint presentation (default: False).
  
**Outputs:**
- If `--ppt` is specified:
  - Creates a PowerPoint presentation.
  - Generates slides with data visualizations, trends, and outlier information.
- If `--no-ppt` is specified:
  - Processes the data from the CSV file.
  - Performs outlier detection and data processing.
  - Generates statistical information.

**Note: Current python source code set is not optimized for any csv file format, only the format that I and Andrew worked on back at Micron. Future updates coming soon by Fall 2023, so stay tuned!***

# Thank you for reading, and Stay Tuned for updates!

If you would like to suggest improvements or pathways that this code can take, do contact Titus at tituslje99@gmail.com. Enquiries will also be much appreciated!
