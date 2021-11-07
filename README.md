# iOS Health Data

Reads in the iPhone health app .xml export and graphs selected categories such as body fat, weight, steps, sleep.

## Processing the data

First run
>parse_health_and_visualize.py

which will grab any exported iOS Health exports from your *Downloads* folder, and
store them into current working directory.

## Visualization

From the resulting process, visualize 

> full_output.pickle

using jupyter notebook.

