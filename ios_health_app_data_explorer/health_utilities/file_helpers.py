import os
import datetime
from datetime import timedelta
import pandas as pd


def is_new_file(days=2, filename='export.xml'):
    '''
    Based on the source file's modification date, determines if re-import of data is necessary.
    If you require re-import of data from an older file, manually setting the variable above is required.

    :argument
    '''

    if datetime.datetime.fromtimestamp(os.path.getmtime('export.xml')) > datetime.datetime.now() + timedelta(days=-days):
        print(f'The file is newer than {days} days.  Re-importing data.')
        print(str(datetime.datetime.fromtimestamp(os.path.getmtime(filename))))

        return True

    print(f'Healthkit xml data not re-parsed.\nFile is older than {days} days.  Relying on csv data.')
    return False




def parse_ios_data(file):
    '''
    From exported iOS Health App xml, generates a parseable list of records that can be used as a foundation
    for graphing and human-readable exports.

    :param file:
    :return:
    '''
    from xml.dom import minidom

    xmldoc = minidom.parse(file)
    recordlist = xmldoc.getElementsByTagName('Record')

    return recordlist
