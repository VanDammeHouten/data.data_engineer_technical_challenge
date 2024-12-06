import pandas as pd

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


