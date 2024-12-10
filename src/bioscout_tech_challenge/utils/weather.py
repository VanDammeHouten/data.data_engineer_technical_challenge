"""
Weather-related utility functions.
"""

__all__ = [
    'merge_weather_data',
    'get_na_rows',
    'expand_extra_information',
    'expand_weather_dataframe',
    'get_timezone_from_coordinates',
    'flatten_weather_data',
    'add_sensor_units',
    'add_timezone_from_coordinates',
    'check_timestamp_match',
    'filter_weather_data',
    'apply_single_filter'
]

import pandas as pd
import json
import ast
import numpy as np
from timezonefinder import TimezoneFinder

def merge_weather_data(
    data_df: pd.DataFrame,
    devices_df: pd.DataFrame,
    merge_column: str = 'device_id',
    how: str = 'left',
) -> pd.DataFrame:
    """
    Merge two weather-related DataFrames on a common column.

    Args:
        data_df (pd.DataFrame): First weather DataFrame
        devices_df (pd.DataFrame): Second weather DataFrame
        merge_column (str): Column name to merge on
        how (str): Type of merge to perform ('inner', 'outer', 'left', 'right')

    Returns:
        pd.DataFrame: Merged DataFrame
    """


    # Validate inputs
    if merge_column not in data_df.columns or merge_column not in devices_df.columns:
        raise ValueError(f"Merge column '{merge_column}' not found in both DataFrames")

    # Perform merge
    merged_df = pd.merge(
        data_df,
        devices_df,
        on=merge_column,
        how=how,
    )

    return merged_df


def get_na_rows(df: pd.DataFrame, column: str, merge_column: str="device_id" ) -> pd.DataFrame:
    """
    Return rows from DataFrame where specified column contains NA values.
    Includes row number and device_id in the output.

    Args:
        df (pd.DataFrame): Input DataFrame
        column (str): Column name to check for NA values
        merge_column (str: Column name that merge was performed on

    Returns:
        pd.DataFrame: DataFrame containing row number, device_id, and rows where specified column is NA
    """
    # Validate input
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    if merge_column not in df.columns:
        raise ValueError(f"Column '{merge_column}' not found in DataFrame")

    # Get rows where column is NA and reset index to get row numbers
    na_rows = df[df[column].isna()].reset_index()
    
    # Select only relevant columns
    return na_rows[[column, merge_column]]


def expand_extra_information(
    row: pd.Series, 
    sensor_schema: dict[str, list[str]] = {},
    extra_information_column: str = 'extra_information', 
    dropped_columns: list[str] = ['pressure', 'voc', 'date_measured', 'extra_information'],
    unique_columns: list[str] = ['Timestamp', 'IotID']
) -> pd.DataFrame:
    """
    Expands a single row into multiple rows by parsing the JSON data in the extra_information column.
    Designed to be used with pandas apply function.

    Args:
        row (pd.Series): Single row from DataFrame containing JSON data in extra_information column

    Returns:
        pd.DataFrame: DataFrame with the row expanded based on the JSON data structure
    """
    # Parse the JSON data from extra_information column
    try:
        json_str = row[extra_information_column]
        cleaned_str = json_str.replace("'", '"')  # Replace single quotes with double quotes
        json_data = json.loads(cleaned_str)
    except (json.JSONDecodeError, KeyError):
        # Raise an error if the JSON parsing fails this is a placeholder for now
        raise ValueError(f"Failed to parse JSON data from column '{extra_information_column}'")
    
    # Drop columns
    row_dropped = row.drop(labels=dropped_columns)

    # Test timestamp
    timestamp = pd.to_datetime(json_data['Timestamp'])
    if timestamp != pd.to_datetime(row['date_measured']):
        raise ValueError(f"Timestamp in extra_information column does not match timestamp in date_measured column")


    # Find the timezone from the latitude and longitude
    timezone_coord = get_timezone_from_coordinates(row['latitude'], row['longitude'])
    # Find the timezone from the UTC offset (Not implemented yet)
    # timezone_utc = get_timezone_from_utc_offset(row['utc_offset_in_hours'])
    
    # Compare the two timezones ( Need to implement timezone from UTC offset)
    # if timezone_coord != timezone_utc:
    #     raise ValueError(f"Timezone from coordinates does not match timezone from UTC offset")
    # else:
    row_dropped['timezone'] = timezone_coord
    if row_dropped['timestamp'].exists():
        row_dropped['timestamp'] = row_dropped['timestamp'].dt.tz_localize(row_dropped['timezone'])
    else:
        row_dropped['timestamp'] = row_dropped['timestamp'].astype(str)
    for key in unique_columns:
        if key in json_data:
            # Convert to lowercase to match the expected column names
            row_dropped[key.lower()] = json_data[key]    # Create copies of the row for each JSON entry
    
    expanded_rows = []
    # iterate over sensor types ignoring the unique columns
    for key, value in json_data.items():
        if key not in unique_columns and isinstance(value, list):
            for reading in value:
                new_row = row_dropped.copy()
                new_row['sensor_type'] = sensor_schema[key][0]
                new_row['sensor_device'] = reading['Sensor']
                new_row['sensor_value'] = reading['Value']
                new_row['sensor_units'] = sensor_schema[key][1]            

                if 'SampleTimeLength' in reading:
                    new_row['sample_time_length'] = reading['SampleTimeLength']
                else:
                    new_row['sample_time_length'] = -1

                expanded_rows.append(new_row)
        
    return pd.DataFrame(expanded_rows)


def expand_weather_dataframe(df: pd.DataFrame, 
                           sensor_schema: dict[str, list[str]] = {},
                           **kwargs) -> pd.DataFrame:
    """
    Expands the extra information JSON column for every row in a dataframe.
    
    Args:
        df (pd.DataFrame): Input dataframe containing weather data
        extra_information_column (str): Name of column containing JSON data
        dropped_columns (list): List of columns to drop from expanded data
        sensor_schema (dict): Dictionary mapping sensor types to (name, units) tuples
        **kwargs: Additional keyword arguments to pass to expand_extra_information
            
    Returns:
        pd.DataFrame: Expanded dataframe with JSON data flattened into columns
        
    Raises:
        ValueError: If JSON parsing fails for any row
    """
    # Initialize empty list to store expanded rows
    expanded_dfs = []
    
    # Iterate through each row and expand
    for _, row in df.iterrows():
        try:
            expanded_df = expand_extra_information(row,
                                                 sensor_schema=sensor_schema,
                                                 **kwargs)
            expanded_dfs.append(expanded_df)
        except ValueError as e:
            # Log error and continue
            print(f"Error expanding row: {e}")
            continue
            
    # Concatenate all expanded dataframes
    if expanded_dfs:
        return pd.concat(expanded_dfs, ignore_index=True)
    else:
        return pd.DataFrame()  # Return empty dataframe if no rows were successfully expanded




def get_timezone_from_coordinates(lat: float, lon: float) -> str:
    """
    Get timezone string from latitude and longitude coordinates.
    
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
            
    Returns:
        str: Timezone string (e.g. 'Australia/Sydney')
            
    Raises:
        ValueError: If timezone cannot be determined from coordinates
    """
    from timezonefinder import TimezoneFinder
        
    # Initialize TimezoneFinder
    tf = TimezoneFinder()
        
    # Get timezone string from coordinates
    timezone_str = tf.timezone_at(lat=float(lat), lng=float(lon))
        
    if timezone_str is None:
        raise ValueError(f"Could not determine timezone for coordinates: {lat}, {lon}")
            
    return timezone_str




# Add these constants before the new function
DEFAULT_SENSOR_TYPES = [
    'VOCs', 'Pressure', 'Humidity', 'Temperature', 
    'WindSpeed', 'WindDirection', 'Rainfall'
]
DEFAULT_META_COLUMNS = ['IotID', 'Timestamp']
DEFAULT_COLUMN_MAPPING = {
    'Value': 'sensor_value',
    'Sensor': 'sensor_device',
    'IotID': 'iotid',
    'SampleTimeLength': 'sample_time_length',
    'Timestamp': 'timestamp',
}
DEFAULT_COLUMN_TYPES = {
    "sensor_units": "str",
    "timezone": "str",
    "sensor_type": "str",
    "sensor_device": "str",
    "sensor_value": "float",
    "sample_time_length": "int",
    "timestamp": "datetime",
}
DEFAULT_COLUMNS_TO_DROP = ['extra_information', 'pressure', 'voc']

def process_sensor_data(
    fixed_json: list,
    sensor_type: str,
    meta_columns: list[str],
    weather_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Process data for a single sensor type from JSON data.
    
    Args:
        fixed_json: List of parsed JSON dictionaries
        sensor_type: Type of sensor to process
        meta_columns: List of metadata columns to include
        weather_df: Original weather dataframe for IDs
        
    Returns:
        DataFrame containing processed sensor data
    """
    df = pd.json_normalize(
        fixed_json,
        record_path=[sensor_type], 
        meta=meta_columns
    )
    df['sensor_type'] = sensor_type.lower().rstrip('s')
    
    readings_per_row = df.shape[0] // weather_df.shape[0]
    weather_ids = np.repeat(weather_df['weather_reading_id'].values, readings_per_row)
    df['weather_reading_id'] = weather_ids
    
    return df

def validate_input_df(weather_df: pd.DataFrame) -> None:
    """
    Validate that required columns exist in input dataframe.
    
    Args:
        weather_df: Weather dataframe to validate
        
    Raises:
        KeyError: If required columns are missing
    """
    required_columns = {'extra_information', 'weather_reading_id'} 
    missing_columns = required_columns - set(weather_df.columns)
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")
def fix_json_strings(json_strings: list) -> list:
    """
    Fix and parse JSON strings that may have encoding issues.
    
    Args:
        json_strings: List of JSON strings to fix
        
    Returns:
        List of parsed JSON dictionaries
    """
    fixed = []
    for json_str in json_strings:
        if isinstance(json_str, str):
            # Fix common encoding issues
            json_str = json_str.replace("'", '"')
            json_str = json_str.replace('None', 'null')
            json_str = json_str.replace('True', 'true')
            json_str = json_str.replace('False', 'false')
            
            try:
                fixed.append(json.loads(json_str))
            except json.JSONDecodeError:
                # If JSON parsing fails, try literal eval as fallback
                try:
                    fixed.append(ast.literal_eval(json_str))
                except:
                    fixed.append({})
        else:
            fixed.append(json_str)
    return fixed

def convert_data_types(df: pd.DataFrame, column_dtypes: dict[str, str]) -> pd.DataFrame:
    """
    Convert DataFrame columns to specified data types.
    
    Args:
        df: DataFrame to convert
        column_dtypes: Dictionary mapping column names to their desired data types.
            Valid dtypes include: 'int64', 'float64', 'string', 'datetime64[ns]'
            
    Returns:
        DataFrame with converted data types
    """
    for column, dtype in column_dtypes.items():
        if column in df.columns:
            try:
                if dtype in ['datetime', 'datetime64', 'datetime64[ns]']:
                    df[column] = pd.to_datetime(df[column], errors='coerce')
                elif dtype in ['int', 'int64']:
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                elif dtype in ['float', 'float64']:
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                elif dtype in ['str', 'string']:
                    df[column] = df[column].astype('|S') 
            except Exception as e:
                print(f"Warning: Could not convert {column} to {dtype}: {e}")
    return df

def flatten_weather_data(
    weather_df: pd.DataFrame,
    sensor_types: list[str] = DEFAULT_SENSOR_TYPES,
    meta_columns: list[str] = DEFAULT_META_COLUMNS,
    column_mapping: dict = DEFAULT_COLUMN_MAPPING,
    columns_to_drop: list[str] = DEFAULT_COLUMNS_TO_DROP,
    sensor_units: dict = {},
    column_types: dict = DEFAULT_COLUMN_TYPES
) -> pd.DataFrame:
    """
    Flattens the extra_information JSON column in weather data into separate rows for each sensor reading.
    """
    try:
        validate_input_df(weather_df)
    except KeyError as e:
        logger.error(f"Missing required columns: {e}")
        return
    
    # Parse JSON data
    fixed_json = weather_df['extra_information'].apply(ast.literal_eval).tolist()
    
    # Process each sensor type
    sensor_dfs = []
    for sensor_type in sensor_types:
        try:
            df = process_sensor_data(fixed_json, sensor_type, meta_columns, weather_df)
            sensor_dfs.append(df)
        except KeyError:
            print(f"Warning: {sensor_type} not found in some records")

    if not sensor_dfs:
        raise ValueError("No sensor data was successfully processed")

    # Combine and process dataframes
    combined_sensors = pd.concat(sensor_dfs, ignore_index=True)
    
    # Rename columns using provided mapping
    combined_sensors = combined_sensors.rename(columns=column_mapping)
    
    # Merge with original weather dataframe
    final_df = weather_df.merge(
        combined_sensors,
        on=['weather_reading_id'],
        how='left'
    )
    
    # Drop unnecessary columns
    final_df = final_df.drop(columns=columns_to_drop)
    
    # Handle special cases
    if 'sample_time_length' in final_df.columns:
        final_df['sample_time_length'] = final_df['sample_time_length'].fillna(-1)
    
    if sensor_units:
        final_df = add_sensor_units(final_df, sensor_units)

    # Convert data types
    final_df = convert_data_types(final_df, column_types)
    return final_df

def add_sensor_units(df: pd.DataFrame, sensor_units: dict) -> pd.DataFrame:
    """
    Add a sensor_units column to the DataFrame based on the sensor scheme.

    Args:
        df (pd.DataFrame): Input DataFrame containing sensor readings
        sensor_units (dict): Dictionary mapping sensor types to their units
                            e.g. {'temperature': '°C', 'humidity': '%'}

    Returns:
        pd.DataFrame: DataFrame with added sensor_units column
    """
    # Map sensor types to their units directly on original dataframe
    df['sensor_units'] = df['sensor_type'].map(sensor_units)
    # set to string
    df['sensor_units'] = df['sensor_units'].astype(str)
    return df

def add_timezone_from_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a timezone column to the DataFrame based on latitude and longitude coordinates.

    Args:
        df (pd.DataFrame): Input DataFrame containing latitude and longitude columns

    Returns:
        pd.DataFrame: DataFrame with added timezone column

    Raises:
        ValueError: If latitude or longitude columns are missing from the DataFrame
    """
    # Verify required columns exist
    required_cols = ['latitude', 'longitude'] 
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Apply timezone lookup to each row using existing get_timezone_from_coordinates function
    df['timezone'] = df.apply(
        lambda row: get_timezone_from_coordinates(row['latitude'], row['longitude']), 
        axis=1
    )
    # set to string
    df['timezone'] = df['timezone'].astype(str)

    return df

def check_timestamp_match(df: pd.DataFrame,
                         date_measured_col: str = 'date_measured',
                         timestamp_col: str = 'timestamp') -> list[int]:
    """
    Check if timestamps in two columns match across a DataFrame and return indices of mismatched rows.

    Args:
        df (pd.DataFrame): DataFrame containing the timestamp columns
        date_measured_col (str, optional): Name of the date_measured column. Defaults to 'date_measured'.
        timestamp_col (str, optional): Name of the timestamp column to compare against. Defaults to 'timestamp'.

    Returns:
        list[int]: List of row indices where timestamps don't match between columns

    Raises:
        ValueError: If either column name is not found in the DataFrame
    """
    if date_measured_col not in df.columns or timestamp_col not in df.columns:
        raise ValueError(f"One or both column names not found in DataFrame: {date_measured_col}, {timestamp_col}")
    
    try:
        # Convert both columns to datetime
        date_measured = pd.to_datetime(df[date_measured_col])
        timestamp = pd.to_datetime(df[timestamp_col])
        
        # Find indices where timestamps don't match
        mismatch_mask = date_measured != timestamp
        mismatched_indices = df.index[mismatch_mask].tolist()
        
        return mismatched_indices
    except (TypeError, ValueError) as e:
        raise ValueError(f"Error converting timestamps: {str(e)}")

def apply_single_filter(df: pd.DataFrame, filter_dict: dict) -> pd.Index:
    """
    Apply a single set of filter criteria and return matching indices.
    
    Args:
        df (pd.DataFrame): DataFrame to filter
        filter_dict (dict): Dictionary of filter criteria
            
    Returns:
        pd.Index: Index of rows matching all criteria
    """
    valid_idx = pd.Series(True, index=df.index)
    
    for col, criteria in filter_dict.items():
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame")
            
        if isinstance(criteria, dict):
            if 'min' in criteria:
                if col == 'timestamp':
                    # Convert both to datetime for timestamp comparisons
                    df_dates = pd.to_datetime(df[col]).dt.date
                    min_date = pd.to_datetime(criteria['min']).date()
                    valid_idx &= df_dates >= min_date
                else:
                    valid_idx &= df[col] >= criteria['min']
                    
            if 'max' in criteria:
                if col == 'timestamp':
                    # Convert both to datetime for timestamp comparisons
                    df_dates = pd.to_datetime(df[col]).dt.date
                    max_date = pd.to_datetime(criteria['max']).date()
                    valid_idx &= df_dates <= max_date
                else:
                    valid_idx &= df[col] <= criteria['max']
        else:
            valid_idx &= (df[col] == criteria)
    return df.index[valid_idx]

def filter_weather_data(df: pd.DataFrame, filter_dict: dict) -> pd.Index:
    """
    Get indices of rows matching any of the filter criteria sets.
    
    Args:
        df (pd.DataFrame): DataFrame to filter
        filter_dict (dict): Dictionary containing a list of filter criteria under 'filters' key
            
    Returns:
        pd.Index: Index of rows matching any of the filter sets
        
    Example filter_dict:
    {
        "filters": [
            {
                "device_id": "255",
                "timestamp": {
                    "min": "2023-11-05"
                }
            },
            {
                "sensor_type": "temperature",
                "sensor_value": {
                    "min": 20,
                    "max": 25
                }
            }
        ]
    }
    """
    if 'filters' not in filter_dict:
        # If no filters list is provided, treat the entire dict as a single filter
        return apply_single_filter(df, filter_dict)
        
    # Apply each filter set independently and combine indices
    matching_indices = []
    for filter_set in filter_dict['filters']:
        indices = apply_single_filter(df, filter_set)
        matching_indices.append(indices)
    
    # Combine all matching indices (union for OR operation)
    if matching_indices:
        return pd.Index(set().union(*matching_indices))
    return pd.Index([])




