"""
bioscout
~~~~~~~~

A package for the BioScout technical challenge.
"""

import importlib.metadata

# Import your modules here
from . import models
from .utils import *#read_csv_file, save_csv_file, merge_weather_data, get_na_rows, expand_weather_dataframe
from .utils.weather import (
    merge_weather_data,
    get_na_rows,
    expand_extra_information,
    # get_timezone_from_utc_offset,
    get_timezone_from_coordinates,
    expand_weather_dataframe,
)
#fix this later
__version__ = importlib.metadata.version(__package__)
__author__ = "Zach Milgate"
__email__ = "zach.milgate@example.com"
__description__ = "BioScout Technical Challenge Implementation"

# List all modules and specific functions/classes to be exposed
__all__ = [ 
    'models',
    'read_csv_file',
    'save_csv_file',
    'merge_weather_data',
    'get_na_rows',
    'identify_header',
    'combine_csv_files',
    'find_csv_files',
    'expand_extra_information',
    # 'get_timezone_from_utc_offset',
    'get_timezone_from_coordinates',
    'expand_weather_dataframe',
]