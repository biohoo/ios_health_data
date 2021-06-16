from datetime import timedelta
from xml.dom import minidom
import matplotlib.pyplot as plt
import pandas as pd

import ios_health_app_data_explorer.health_utilities.file_helpers as fh

'''Colors'''
DARK_BLUE = '#22336c'
LIGHT_BLUE = '#8899d2'
BLUE = '#3a55b4'

IOS_XML_FILE = 'export.xml'

'''Redefining a few iOS categories
NOTE: For the scale i'm using, 'lean' is technically 'muscle mass (lbs)'.
In healthcare, 'lean body mass' is total mass minus body fat mass.
'''

TypeID = {'Pedometer': 'HKQuantityTypeIdentifierDistanceWalkingRunning',
          'Weight': 'HKQuantityTypeIdentifierBodyMass',
          'Sleep': 'HKCategoryTypeIdentifierSleepAnalysis',
          'Flights': 'HKQuantityTypeIdentifierFlightsClimbed',
          'FatPercent':'HKQuantityTypeIdentifierBodyFatPercentage',
          'Lean':'HKQuantityTypeIdentifierLeanBodyMass'}


def parse_ios_data(file):
    '''
    From exported iOS Health App xml, generates a parseable list of records that can be used as a foundation
    for graphing and human-readable exports.

    :param file:
    :return:
    '''
    xmldoc = minidom.parse(file)
    recordlist = xmldoc.getElementsByTagName('Record')

    return recordlist


def output_weight(recordlist, figureNumber, plotThis=True):
    '''
    Generates weight data in lbs.

    :param recordlist:
    :param figureNumber:
    :param plotThis:
    :return:
    '''
    x, y = generate_iterable(recordlist, 'Weight', isDict=False)

    if plotThis:
        plt.figure(figureNumber)
        plt.scatter(x, y, c=y)

        plot_annotations(plt)
        plt.title('Weight (lbs) over Time')
        plt.savefig('Weight (lbs) over Time')
        plt.draw()

    return list(zip(x, y))

def output_fat(recordlist, figureNumber, plotThis=True):
    '''
    Generates body fat percentage data as a proportion (0 to 1).

    :param recordlist:
    :param figureNumber:
    :param plotThis:
    :return:
    '''
    x, y = generate_iterable(recordlist, 'FatPercent', isDict=False)

    if plotThis:
        plt.figure(figureNumber)
        plt.scatter(x, y, c=y)

        plot_annotations(plt)
        plt.title('Body Fat percent over Time')
        plt.savefig('Body Fat Percent Over Time')
        plt.draw()

    return list(zip(x, y))


def output_lean(recordlist, figureNumber, plotThis=True):
    '''
    Generates lean body mass in lbs.

    NOTE: This is a misnomer as the scale tracks Muscle Mass.
    Lean body mass is technically total mass - fat mass

    :param recordlist:
    :param figureNumber:
    :param plotThis:
    :return:
    '''
    x, y = generate_iterable(recordlist, 'Lean', isDict=False)

    if plotThis:
        plt.figure(figureNumber)
        plt.scatter(x, y, c=y)

        plot_annotations(plt)
        plt.title('Muscle Mass percent over Time')
        plt.savefig('Muscle Mass Percent Over Time', size=100)
        plt.draw()

    return list(zip(x, y))




def output_sleep(recordlist, figureNumber, plotThis=True):
    '''
    Generates sleep data.

    :param recordlist:
    :param figureNumber:
    :param plotThis:
    :return:
    '''
    x, y = generate_iterable(recordlist, 'Sleep', isDict=False, isSleep=True)

    if plotThis:
        plt.figure(figureNumber)
        plt.scatter(x, y, c=y)

        plot_annotations(plt)
        plt.title('Sleep over Time')
        plt.savefig('Sleep over Time')
        plt.draw()

    return list(zip(x, y))


def output_pedometer(recordlist, figureNumber, plotThis=True):
    '''
    Generates pedometer data.

    :param record_list:
    :param figureNumber:
    :param plotThis:
    :return:
    '''

    Dict = generate_iterable(recordlist, TypeIndex='Pedometer', isDict=True)
    summed_dict = {key: sum(value) for key, value in Dict.items()}

    if plotThis:
        plot_dictionary(figureNumber, 'Pedometer (miles) over Time', summed_dict)

    return summed_dict


def output_flights(record_list, figure_number, plotThis=True):
    '''
    Generates altimeter data.

    :param record_list:
    :param figure_number:
    :param plotThis:
    :return:
    '''

    Dict = generate_iterable(record_list, TypeIndex='Flights', isDict=True)

    summedDict = {key: sum(value) for key, value in Dict.items()}

    if plotThis:
        plot_dictionary(figure_number, 'Altimeter (flights of stairs) over Time', summedDict)

    return summedDict


def plot_dictionary(figureNumber, title, dictionary):
    '''
    Generates a plot from dictionary data points.

    :param figureNumber:
    :param title:
    :param dictionary:
    :return:
    '''

    fig = plt.figure()
    axis = fig.add_subplot(int('21'+str(figureNumber)))
    DictToList = [(key, value) for key, value in dictionary.items()]
    axis.plot([i[0] for i in DictToList], [i[1] for i in DictToList])
    plot_annotations(fig)
    axis.title(title)
    
    plt.savefig(title)


def generate_iterable(recordlist, TypeIndex, isDict=True, isSleep=False):
    '''
    Produces either a dictionary or list of data points from the record of interest.

    Type Index refers to the category of data desired from the iOS health export.

    Since the sleep record is a list, this is treated separately.

    :param recordlist:
    :param TypeIndex:
    :param isDict:
    :param isSleep:
    :return:
    '''

    if isDict:

        Dict = {}

        for s in recordlist:

            if s.attributes['type'].value == TypeID[TypeIndex]:

                dateTime = s.attributes['startDate'].value
                date, time = dateTime.split(' ')[0:2]

                Datum = float(s.attributes['value'].value)

                try:
                    # append
                    Dict[pd.to_datetime(date)].append(Datum)

                except:
                    # produce new
                    Dict[pd.to_datetime(date)] = [Datum]
        return Dict


    elif isSleep:
        x = []
        y = []

        for s in recordlist:
            if s.attributes['type'].value == TypeID[TypeIndex]:
                startDate = s.attributes['startDate'].value
                endDate = s.attributes['endDate'].value

                difference = pd.to_datetime(endDate) - pd.to_datetime(startDate)
                difference = difference.seconds / 60

                x.append(pd.to_datetime(startDate))
                y.append(difference)

        return (x, y)

    else:
        x = []
        y = []

        for s in recordlist:
            if s.attributes['type'].value == TypeID[TypeIndex]:
                dateTime = s.attributes['startDate'].value
                date, time = dateTime.split(' ')[0:2]

                x.append(pd.to_datetime(dateTime))
                y.append(float(s.attributes['value'].value))

        return (x, y)


def plot_annotations(plot):
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
                   '1/8/2018':'Diet/Exercise\n Improvement / \nFood Tracking',
                   '4/1/2021':'(Restart) Diet\n and food tracking\n after pandemic'
                   }

    for date, annotation in annotations.items():
        plot.text(pd.to_datetime(date) + timedelta(days=10), y_max * 0.80, annotation, rotation=90)
        plot.axvline(x=pd.to_datetime(date))


def output_csv(func_name, title='Title Here'):
    '''
    Produces a csv file from information in a single type of event.

    :param func_name:
    :param title:
    :return:
    '''


    open(title + '.csv', 'w').close()  # Clear data in existing file

    with open(title + ".csv", 'a') as f:

        if type(func_name) == dict:
            f.write('Date,Value\n')
            for key, value in func_name.items():
                f.write('%s,%s\n' % (key, value))
        elif type(func_name) == list:
            f.write('Date,Value\n')
            for x, y in func_name:
                f.write('%s,%s\n' % (x, y))


def summarize_attributes(recordlist):
    '''
    Generates the number of records of each type in stdout.

    :param recordlist: list
    :return: None
    '''

    attribute_dict = {}

    for s in recordlist:
        attribute = s.attributes['type'].value

        try:
            attribute_dict[attribute] += 1
        except:
            attribute_dict[attribute] = 1

    open('summary.csv', 'w').close()  # Clear data in existing file
    with open('summary.csv','a') as f:
        f.write('Category,Count\n')
        for key, value in attribute_dict.items():
            statement = '%s,%s' % (key, value)
            print(statement)
            f.write(statement+'\n')


def graph_workout_progress():
    fat = pd.read_csv('output_fat.csv')
    weight = pd.read_csv('output_weight.csv')
    lean = pd.read_csv('output_lean.csv')

    aggregate = weight.join(fat.set_index('Date'), lsuffix='_Weight', rsuffix='_Fat', on='Date')
    aggregate = aggregate.join(lean.set_index('Date'), rsuffix='_Lean', lsuffix='_Lean', on='Date')
    aggregate['Date'] = pd.to_datetime(aggregate['Date'])
    aggregate.columns = ['Date', 'Weight', 'Fat', 'Lean']
    aggregate['Lean'] = (aggregate['Lean'] / aggregate['Weight']) * 100  # Convert to percentage of weight.

    def make_patch_spines_invisible(ax):
        ax.set_frame_on(True)
        ax.patch.set_visible(False)
        for sp in ax.spines.values():
            sp.set_visible(False)

    fig, ax1 = plt.subplots()
    fig.subplots_adjust(right=0.75)
    plt.title('Workout Progress')
    plt.xticks(rotation='45')
    ax1.plot(aggregate['Date'], aggregate['Weight'], '.', color=LIGHT_BLUE)
    ax1.set_xlabel('Date')

    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_ylabel('Weight (lbs)', color=LIGHT_BLUE)
    ax1.tick_params('y', colors=LIGHT_BLUE)

    '''body fat axis'''

    ax2 = ax1.twinx()
    ax2.plot(aggregate['Date'], aggregate['Fat'] * 100, 'o', color=DARK_BLUE, alpha=0.5)
    ax2.set_ylabel('Body Fat (%)', color=DARK_BLUE)
    ax2.tick_params('y', colors=DARK_BLUE)

    ax3 = ax1.twinx()
    # Offset the right spine of par2.  The ticks and label have already been
    # placed on the right by twinx above.
    ax3.spines["right"].set_position(("axes", 1.2))
    # Having been created by twinx, par2 has its frame off, so the line of its
    # detached spine is invisible.  First, activate the frame but make the patch
    # and spines invisible.
    make_patch_spines_invisible(ax3)
    # Second, show the right spine.
    ax3.spines["right"].set_visible(True)

    '''muscle mass axis'''

    ax3.plot(aggregate['Date'], aggregate['Lean'], 'o', color='Red')
    ax3.set_ylabel('Lean (%)', color='Red')
    ax3.tick_params('y', colors='Red')

    plt.savefig('Workout Progress')
    plt.show()




re_import_data = fh.is_new_file()


if __name__ == '__main__':

    if re_import_data == True:

        #   Return raw data and summarize count of records.
        data = parse_ios_data(IOS_XML_FILE)
        summarize_attributes(data)

        #   Export csv files from these functions, naming the files according to the function names.
        for f in [output_weight, output_fat, output_flights, output_pedometer, output_sleep, output_lean]:
            output_csv(f(data,1,plotThis=False),title=str(f.__name__))

        #   Plot these functions.
        figureCounter = 1
        for f in [output_weight, output_fat]:
            f(data, figureCounter)
            figureCounter += 1



    graph_workout_progress()
