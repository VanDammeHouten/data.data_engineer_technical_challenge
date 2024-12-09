"""
BioScout Technical Challenge
~~~~~~~~~~~~~~~~~~~~~~~~~~

A package for processing and analyzing weather and sensor data.
"""

from .utils import (
    read_csv_file,
    save_csv_file,
    identify_header,
    combine_csv_files,
    find_csv_files,
    read_json_file,
    merge_weather_data,
    get_na_rows,
    expand_extra_information,
    # get_timezone_from_utc_offset,
    get_timezone_from_coordinates,
    expand_weather_dataframe,
    flatten_weather_data,
    add_sensor_units,
    check_timestamp_match,
    add_timezone_from_coordinates,
    parse_sensor_schema,
)
#fix this later
# __version__ = importlib.metadata.version(__package__)
__author__ = "Zach Milgate"
__email__ = "zach.milgate@example.com"
__description__ = "BioScout Technical Challenge Implementation"

# List all modules and specific functions/classes to be exposed
__all__ = [ 
    'models',
    'read_csv_file',
    'save_csv_file',
    'identify_header',
    'combine_csv_files',
    'find_csv_files',
    'read_json_file',
    'merge_weather_data',
    'get_na_rows',
    'expand_extra_information',
    # 'get_timezone_from_utc_offset',
    'get_timezone_from_coordinates',
    'expand_weather_dataframe',
    'flatten_weather_data',
    'add_sensor_units',
    'check_timestamp_match',
    'add_timezone_from_coordinates',
    'parse_sensor_schema',
]
