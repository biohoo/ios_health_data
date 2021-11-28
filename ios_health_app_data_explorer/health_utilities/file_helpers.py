import os
import datetime
from datetime import timedelta
import pandas as pd


def is_new_file(filename, days=2):
    """
    Based on the source file's modification date, determines if re-import of data is necessary.
    If you require re-import of data from an older file, manually setting the variable above is required.

    :argument
    """

    if filename.endswith('.zip'):
        print("Analyzing zip file in downloads...")

    if datetime.datetime.fromtimestamp(
        os.path.getatime(filename)
    ) > datetime.datetime.now() + timedelta(days=-days):

        print(f"The file is newer than {days} days.")
        print(str(datetime.datetime.fromtimestamp(os.path.getatime(filename))))

        return True

    print(f"Healthkit xml data not re-parsed.\nFile is older than {days} days.")
    return False


def parse_ios_data(file):
    """
    From exported iOS Health App xml, generates a parseable list of records that can be used as a foundation
    for graphing and human-readable exports.

    :param file:
    :return:
    """
    from xml.dom import minidom

    xmldoc = minidom.parse(file)
    recordlist = xmldoc.getElementsByTagName("Record")

    return recordlist
