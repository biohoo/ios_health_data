from datetime import timedelta
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from pathlib import Path
import os

import ios_health_app_data_explorer.health_utilities.file_helpers as fh
import unzip_and_move_ios_health as uzip


DOWNLOADS_EXTRACT = str(Path.home() / "Downloads/export.zip")
OUTPUT_PICKLE = "full_output.pickle"
IOS_XML_FILE = 'apple_health_export/export.xml'
WIDTH, HEIGHT = (15,9)

if not os.path.exists(DOWNLOADS_EXTRACT):
    print("Unable to find downloaded .zip file.  Reverting to stored export.xml data.")
else:
    if fh.is_new_file(DOWNLOADS_EXTRACT):
        print('Unzipping from downloads and exporting to current working directory.')
        uzip.extract_and_move_healthkit_data()

def plot_annotations(plot, start_date="2000"):
    '''
    Life events to add to the plots
    Also converts the spacing of the text to be spaced according to the timedelta days parameter.

    INPUT: the plot to annotate
    '''



    y_min, y_max = plot.ylim()

    annotations = {'7/20/2012': 'Moved to California',
                   '11/1/2012': 'Downey',
                   '9/1/2014': 'Koreatown',
                   '9/1/2015': 'Culver City',
                   '9/11/2016': 'Married',
                   '7/20/2017': 'Westlake Village',
                   '1/8/2018':'Diet',
                   '4/1/2021':'Diet'
                   }

    for date, annotation in annotations.items():
        if pd.to_datetime(date) > datetime.datetime.strptime(start_date, "%Y"):
            plot.text(pd.to_datetime(date) + timedelta(days=10), y_max * 0.90, annotation, rotation=90)
            plot.axvline(x=pd.to_datetime(date))

def weight_plot(dataframe, feature='HKQuantityTypeIdentifierBodyMass'):
    f, ax = plt.subplots(figsize=(WIDTH, HEIGHT))
    sns.despine(f, left=True, bottom=True)
    sns.scatterplot(x="start_date", y="value",
                    hue="weight_class",
                    hue_order=['Underweight','Athletic', 'Healthy','Overweight','Obese'],
                    palette=sns.color_palette("hls", 5),
                    linewidth=0,
                    data=dataframe[dataframe['type'] == feature], ax=ax)

    plt.title('Weight over Time')
    plt.xlabel('Date')
    plt.ylabel('Weight (lbs)')
    plt.xticks(rotation=45)
    plot_annotations(plt)
    plt.savefig("plots/weight_plot.png")


def body_fat_plot(dataframe, feature='HKQuantityTypeIdentifierBodyFatPercentage'):
    f, ax = plt.subplots(figsize=(WIDTH, HEIGHT))
    sns.despine(f, left=True, bottom=True)
    sns.scatterplot(x="start_date", y="value",
                    hue='value',
                    palette=sns.color_palette("coolwarm", as_cmap=True),
                    linewidth=0,
                    data=dataframe[dataframe['type'] == feature], ax=ax)

    plt.title('Body Fat Percentage over Time')
    plt.xlabel('Date')
    plt.ylabel('Body Fat Percentage')
    plt.xticks(rotation=45)
    plot_annotations(plt, start_date="2016")
    plt.savefig("plots/body_fat_plot.png")

def heart_rate_boxplot(dataframe, feature='HKQuantityTypeIdentifierHeartRate'):
    f, ax = plt.subplots(figsize=(WIDTH, HEIGHT))
    dataframe['month_year'] = pd.to_datetime(dataframe['start_date']).dt.to_period('Y') # 'M' for month, 'Y' for year...
    sns.violinplot(x="month_year", y="value",
                data=dataframe[dataframe['type'] == feature])

    plt.title('Annual Heart Rate')
    plt.xlabel('Date')
    plt.ylabel('Heart Rate')
    plt.xticks(rotation=45)
    plt.savefig("plots/heart_rate_boxplot.png")

def body_fat_boxplot(dataframe, feature='HKQuantityTypeIdentifierBodyFatPercentage'):
    f, ax = plt.subplots(figsize=(WIDTH, HEIGHT))
    dataframe['month_year'] = pd.to_datetime(dataframe['start_date']).dt.to_period(
        'Y')  # 'M' for month, 'Y' for year...
    sns.violinplot(x="month_year", y="value",
                data=dataframe[dataframe['type'] == feature])

    plt.title('Annual Body Fat Percentage')
    plt.xlabel('Date')
    plt.ylabel('Body Fat Percentage')
    plt.xticks(rotation=45)
    plt.savefig("plots/body_fat_boxplot.png")


def generate_all_plots(dataframe):
    heart_rate_boxplot(dataframe)
    body_fat_boxplot(dataframe)
    body_fat_plot(dataframe)
    weight_plot(dataframe)


    plt.show()


def parse_full_file():
    record_list = fh.parse_ios_data(IOS_XML_FILE)

    df = pd.DataFrame(columns=['type', 'start_date', 'value'])
    for record in record_list:
        type = record.attributes['type'].value
        start_date = record.attributes['startDate'].value
        value = record.attributes['value'].value

        if type in ['HKQuantityTypeIdentifierBodyMass',
                    'HKQuantityTypeIdentifierHeartRate',
                    'HKQuantityTypeIdentifierBodyFatPercentage',
                    'HKQuantityTypeIdentifierBodyMassIndex',
                    'HKQuantityTypeIdentifierBloodPressureSystolic',
                    'HKQuantityTypeIdentifierBloodPressureDiastolic'
                    ]:

            to_append = [type, start_date, value]
            a_series = pd.Series(to_append, index=df.columns)
            df = df.append(a_series, ignore_index=True)
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['value'] = df['value'].astype(float)
    criteria = [df['value'].between(0, 110),
                df['value'].between(110, 125),
                df['value'].between(125, 145),
                df['value'].between(145, 170),
                df['value'].between(170, 250)
                ]
    values = ['Underweight', 'Athletic', 'Healthy', 'Overweight', 'Obese']
    df['weight_class'] = np.select(criteria, values, 0)
    weight_plot(df)
    df.to_pickle(OUTPUT_PICKLE)


if __name__ == '__main__':

    if fh.is_new_file(days=4, filename=IOS_XML_FILE):
        parse_full_file()

    df = pd.read_pickle(OUTPUT_PICKLE)
    generate_all_plots(df)
    df.to_csv('test_output.csv')
