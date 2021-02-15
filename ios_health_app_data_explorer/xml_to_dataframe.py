import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import dateutil
import datetime
from xml.etree.ElementTree import ElementTree
from mpl_toolkits.mplot3d import Axes3D


from pandas.tseries import converter
converter.register()


re_parse_xml = True    #   So we're not re-parsing the original huge XML file...


'''
Remove all instances of "was user entered" metadata.
This falsely inputs '1' if this is true, and overwrites the subsequent 'value' nodes below...
'''
tree = ElementTree()
tree.parse('export.xml')

foos = tree.findall('Record')
for foo in foos:
  bars = foo.findall('MetadataEntry')
  for bar in bars:
    foo.remove(bar)
tree.write('export.xml')




def parse_xml_output_csv():
    def open_xml(file):
        with open(file) as f:
            result = f.read()
            return result



    xml_data = 'export.xml'

    xml_data = open_xml(xml_data)


    class XML2DataFrame:

        def __init__(self, xml_data):
            self.root = ET.XML(xml_data)

        def parse_root(self, root):
            print([self.parse_element(child) for child in iter(root)])
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
    xml_dataframe.to_csv('pandas_dataframe.csv')

if re_parse_xml:
    parse_xml_output_csv()



#   Read in formatted csv file and convert datetime column types
xml_dataframe = pd.read_csv('pandas_dataframe.csv')



pd.to_numeric(xml_dataframe['value'], errors='coerce')
pd.to_datetime(xml_dataframe['startDate'], errors='coerce')
pd.to_datetime(xml_dataframe['endDate'], errors='coerce')


#   Convert proportion of body fat to percentage.  Coerce to float.
xml_dataframe.loc[xml_dataframe['type'] == 'HKQuantityTypeIdentifierBodyFatPercentage', 'value'] = \
    xml_dataframe.loc[xml_dataframe['type'] == 'HKQuantityTypeIdentifierBodyFatPercentage', 'value'].astype(float).mul(100)



#   Selectors
body_fat = xml_dataframe['type'] == 'HKQuantityTypeIdentifierBodyFatPercentage'
weight = xml_dataframe['type'] == 'HKQuantityTypeIdentifierBodyMass'
muscle = xml_dataframe['type'] == 'HKQuantityTypeIdentifierLeanBodyMass'
distance = xml_dataframe['type'] == 'HKQuantityTypeIdentifierDistanceWalkingRunning'
flights = xml_dataframe['type'] == 'HKQuantityTypeIdentifierFlightsClimbed'
sleep = xml_dataframe['type'] == 'HKCategoryTypeIdentifierSleepAnalysis'


#   Slices
pd_body_fat = xml_dataframe[body_fat][['type','unit','value','startDate']]
pd_weight = xml_dataframe[weight][['type','unit','value','startDate']]
pd_muscle = xml_dataframe[muscle][['type','unit','value','startDate']]
pd_distance = xml_dataframe[distance][['type','unit','value','startDate']]
pd_flights = xml_dataframe[flights][['type','unit','value','startDate']]
pd_sleep = xml_dataframe[sleep][['type','unit','value','startDate','endDate']]

xml_dataframe['value'] = xml_dataframe['value'].convert_objects(convert_numeric=True)
xml_dataframe['startDate'] = xml_dataframe['startDate'].convert_objects(convert_dates=True)


print(xml_dataframe.dtypes)

pivoted = xml_dataframe.pivot_table(index='startDate', columns='type', values='value', aggfunc='mean')
pivoted = pivoted.reset_index()
pivoted.to_csv('pivoted.csv')


print(pivoted.dtypes)
'''
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(pivoted['startDate'], pivoted['HKQuantityTypeIdentifierBodyFatPercentage'], pivoted['HKQuantityTypeIdentifierLeanBodyMass'])

ax.set_xlabel('Date')
ax.set_ylabel('Body Fat %')
ax.set_zlabel('Muscle %')

plt.show()
'''
groups = xml_dataframe.groupby('type')

# Plot

def plot_this():

    fig, ax = plt.subplots()
    ax.margins(0.05) # Optional, just adds 5% padding to the autoscaling
    for name, group in groups:
        if name in ['HKQuantityTypeIdentifierBodyFatPercentage', 'HKQuantityTypeIdentifierBodyMass', 'HKQuantityTypeIdentifierLeanBodyMass']:
            ax.plot(group.startDate, group.value.astype(float), marker='.', linestyle='', ms=12, label=name)
    ax.legend()
    plt.show()

#plot_this()