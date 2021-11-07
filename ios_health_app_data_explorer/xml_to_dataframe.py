import xml.etree.ElementTree as ET
import pandas as pd
from xml.etree.ElementTree import ElementTree
from pandas.plotting import register_matplotlib_converters as register

register()

re_parse_xml = True  #   So we're not re-parsing the original huge XML file...

INPUT_FILE = "apple_health_export/export.xml"


def remove_user_entered_data(input_file=INPUT_FILE):
    """
    Remove all instances of "was user entered" metadata.
    This falsely inputs '1' if this is true, and overwrites the subsequent 'value' nodes below...
    """

    tree = ElementTree()
    tree.parse(input_file)

    xml_records = tree.findall("Record")

    for xml_record in xml_records:
        user_entries = xml_record.findall("MetadataEntry")
        for user_single_entry in user_entries:
            print(f"removing {user_single_entry.attrib}")
            xml_record.remove(user_single_entry)

    tree.write(input_file)


remove_user_entered_data()


def open_and_read_file(file):
    with open(file) as f:
        result = f.read()
        return result


def parse_xml_output_csv():

    xml_data = INPUT_FILE
    xml_data = open_and_read_file(xml_data)

    class XML2DataFrame:
        def __init__(self, xml_data):
            self.root = ET.XML(xml_data)

        def parse_root(self, root):
            return [self.parse_element(child) for child in iter(root)]

        def parse_element(self, element, parsed=None):
            if parsed is None:
                parsed = dict()
            for key in element.keys():
                parsed[key] = element.attrib.get(key)
            if element.text:
                parsed[element.tag] = element.text
            for child in list(element):
                self.parse_element(child, parsed)
            return parsed

        def process_data(self):
            structure_data = self.parse_root(self.root)
            return pd.DataFrame(structure_data)

    xml2df = XML2DataFrame(xml_data)
    xml_dataframe = xml2df.process_data()
    xml_dataframe.to_csv("pandas_dataframe.csv")


if re_parse_xml:
    parse_xml_output_csv()


#   Read in formatted csv file and convert datetime column types
xml_dataframe = pd.read_csv("pandas_dataframe.csv")

pd.to_numeric(xml_dataframe["value"], errors="coerce")
pd.to_datetime(xml_dataframe["startDate"], errors="coerce")
pd.to_datetime(xml_dataframe["endDate"], errors="coerce")


#   Convert proportion of body fat to percentage.  Coerce to float.
xml_dataframe.loc[
    xml_dataframe["type"] == "HKQuantityTypeIdentifierBodyFatPercentage", "value"
] = (
    xml_dataframe.loc[
        xml_dataframe["type"] == "HKQuantityTypeIdentifierBodyFatPercentage", "value"
    ]
    .astype(float)
    .mul(100)
)


#   Selectors
body_fat = xml_dataframe["type"] == "HKQuantityTypeIdentifierBodyFatPercentage"
weight = xml_dataframe["type"] == "HKQuantityTypeIdentifierBodyMass"
muscle = xml_dataframe["type"] == "HKQuantityTypeIdentifierLeanBodyMass"
distance = xml_dataframe["type"] == "HKQuantityTypeIdentifierDistanceWalkingRunning"
flights = xml_dataframe["type"] == "HKQuantityTypeIdentifierFlightsClimbed"
sleep = xml_dataframe["type"] == "HKCategoryTypeIdentifierSleepAnalysis"


#   Slices
pd_body_fat = xml_dataframe[body_fat][["type", "unit", "value", "startDate"]]
pd_weight = xml_dataframe[weight][["type", "unit", "value", "startDate"]]
pd_muscle = xml_dataframe[muscle][["type", "unit", "value", "startDate"]]
pd_distance = xml_dataframe[distance][["type", "unit", "value", "startDate"]]
pd_flights = xml_dataframe[flights][["type", "unit", "value", "startDate"]]
pd_sleep = xml_dataframe[sleep][["type", "unit", "value", "startDate", "endDate"]]
