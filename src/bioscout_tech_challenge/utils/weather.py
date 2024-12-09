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

DEFAULT_COLUMNS_TO_DROP = ['extra_information', 'pressure', 'voc']

def flatten_weather_data(
    weather_df: pd.DataFrame,
    sensor_types: list[str] = DEFAULT_SENSOR_TYPES,
    meta_columns: list[str] = DEFAULT_META_COLUMNS,
    column_mapping: dict = DEFAULT_COLUMN_MAPPING,
    columns_to_drop: list[str] = DEFAULT_COLUMNS_TO_DROP,
    sensor_units: dict = {}
) -> pd.DataFrame:
    """
    Flattens the extra_information JSON column in weather data into separate rows for each sensor reading.
    
    Args:
        weather_df: Weather dataframe containing extra_information column
        sensor_types: List of sensor types to extract. 
            Defaults to common weather sensors (temperature, pressure, etc.)
        meta_columns: List of metadata columns to include from the JSON. 
            Defaults to ['IotID', 'Timestamp']
        column_mapping: Dictionary to map original column names to new names.
            Defaults to mapping Value->sensor_value, Sensor->sensor_device, IotID->iotid
        columns_to_drop: List of columns to drop from the output.
            Defaults to ['extra_information', 'pressure', 'voc']
            
    Returns:
        Flattened dataframe with sensor readings as separate rows
    """
    # Validate required columns
    required_columns = {'extra_information', 'weather_reading_id'}
    missing_columns = required_columns - set(weather_df.columns)
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")
    
    
    # Convert JSON strings to Python dictionaries
    fixed = weather_df['extra_information'].apply(ast.literal_eval).tolist()
    
    # Process each sensor type
    sensor_dfs = []
    for sensor_type in sensor_types:
        try:
            df = pd.json_normalize(
                fixed,
                record_path=[sensor_type],
                meta=meta_columns
            )
            df['sensor_type'] = sensor_type.lower().rstrip('s')
            
            # Create repeated weather_reading_id array
            readings_per_row = df.shape[0] // weather_df.shape[0]
            weather_ids = np.repeat(weather_df['weather_reading_id'].values, readings_per_row)
            df['weather_reading_id'] = weather_ids
            sensor_dfs.append(df)
        except KeyError:
            print(f"Warning: {sensor_type} not found in some records")

    if not sensor_dfs:
        raise ValueError("No sensor data was successfully processed")

    # Combine all sensor dataframes
    combined_sensors = pd.concat(sensor_dfs, ignore_index=True)
    # Rename columns using provided mapping
    combined_sensors = combined_sensors.rename(columns=column_mapping)
    
    # Merge with original weather dataframe
    final_df = weather_df.merge(
        combined_sensors,
        on=['weather_reading_id'],
        how='left'
    )
    # Replace NaN values in sample_time_length with -1
    final_df['sample_time_length'] = final_df['sample_time_length'].fillna(-1)
    if sensor_units:
        final_df = add_sensor_units(final_df, sensor_units)
    # After the final merge, optionally drop the extra_information column
    final_df = final_df.drop(columns=columns_to_drop)
    
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





