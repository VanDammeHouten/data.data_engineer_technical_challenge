"""
File operation utility functions.
"""

__all__ = [
    'read_csv_file',
    'save_csv_file',
    'find_csv_files',
    'identify_header',
    'combine_csv_files',
    'read_json_file',
    'parse_sensor_schema'
]

import pandas as pd
import json
from typing import Optional, Union
from pathlib import Path




def read_csv_file(
    file_path: Union[str, Path],
    separator: str = ',',
    header: bool = 'infer',
    **kwargs
) -> Optional[pd.DataFrame]:
    """
    Safely read a CSV file into a pandas DataFrame
    
    Args:
        file_path: Path to the CSV file
        separator: Column separator (default: comma)
        header: Whether to use the header from the file (default: 'infer')
            
    Returns:
        DataFrame if successful, None if failed
    """
    # Try reading first few rows to detect column types
    try:
        dtypes = pd.read_csv(
            file_path,
            sep=separator,
            header=header,
            nrows=5,
            **kwargs
        ).dtypes
        kwargs['dtype'] = {col: str(dtype) for col, dtype in dtypes.items()}
    except Exception as e:
        print(f"Warning: Could not pre-detect column types: {str(e)}")
    try:
        df = pd.read_csv(
            file_path,
            sep=separator,
            header=header,
            **kwargs
        )
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except pd.errors.EmptyDataError:
        print(f"Error: File is empty at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        return None


# for testing and comparison
def save_csv_file(
    df: pd.DataFrame,
    file_path: Union[str, Path],
    encoding: str = 'utf-8',
    separator: str = ',',
    index: bool = False
) -> bool:
    """
    Safely save a DataFrame to CSV
    
    Args:
        df: DataFrame to save
        file_path: Path where to save the CSV
        encoding: File encoding (default: utf-8)
        separator: Column separator (default: comma)
        index: Whether to save the index (default: False)
        
    Returns:
        bool: True if successful, False if failed
    """
    try:
        df.to_csv(
            file_path,
            encoding=encoding,
            sep=separator,
            index=index
        )
        return True
    except Exception as e:
        print(f"Error saving CSV: {str(e)}")
        return False


def identify_header(
    path: Union[str, Path],
    n: int = 5,
    th: float = 0.9
) -> bool:
    """
    Determine if a CSV file has a header row by comparing data types
    of the first n rows when read with and without a header.
    
    Args:
        path: Path to the CSV file
        n: Number of rows to analyze (default: 5)
        th: Similarity threshold for dtypes comparison (default: 0.9)
        
    Returns:
        bool: True if header likely exists, False if no header likely
    """
    try:
        # Read first n rows assuming there is a header
        df1 = pd.read_csv(path, header='infer', nrows=n)
        # Read first n rows assuming no header
        df2 = pd.read_csv(path, header=None, nrows=n)
        
        # Compare data types between both readings
        # If very similar, likely no header (all data rows)
        sim = (df1.dtypes.values == df2.dtypes.values).mean()
        
        return 'infer' if sim < th else None
    except Exception as e:
        print(f"Error analyzing CSV header: {str(e)}")
        return 'infer'  # Default to infer if analysis fails


def combine_csv_files(
    file_paths: list[Union[str, Path]],
    add_source_column: bool = True,
    detect_header: bool = True,
    **kwargs
) -> Optional[pd.DataFrame]:
    """
    Combine multiple CSV files into a single DataFrame, adding a column to track the source file.
    
    Args:
        file_paths: List of paths to CSV files
        add_source_column: Whether to add a column to track the source file, column name: 'source_file' (default: True)
        detect_header: Whether to detect the header from the first file (default: True)
        **kwargs: Additional arguments passed to read_csv_file
        
    Returns:
        DataFrame containing all files' data if successful, None if failed
    """
    header_names = None
    try:
        # Initialize empty list to store DataFrames
        dfs = []
        
        for file_path in file_paths:
            # Read each CSV file
            use_header = identify_header(file_path)

            if detect_header:
                df = read_csv_file(file_path, header=use_header,  **kwargs)
                header_names = list(df.columns)
                detect_header = False
            elif header_names is None:
                df = read_csv_file(file_path, header='infer',  **kwargs)
            else:
                df = read_csv_file(file_path, header=None, names=header_names,  **kwargs)
            if df is not None:
                # Add source column with file name
                if add_source_column:
                    df['source_file'] = Path(file_path).name
                dfs.append(df)
            else:
                print(f"Skipping {file_path} due to read error")
        
        if not dfs:
            print("No valid CSV files were read")
            return None
            
        # Combine all DataFrames
        return pd.concat(dfs, ignore_index=True)
        
    except Exception as e:
        print(f"Error combining CSV files: {str(e)}")
        return None


def find_csv_files(
    folder_path: Union[str, Path],
    prefix: Optional[str] = None,
    recursive: bool = False,
    sort: bool = False
) -> list[Path]:
    """
    Find all CSV files in a folder, optionally filtering by prefix.
    
    Args:
        folder_path: Path to the folder to search
        prefix: Optional prefix to filter files (default: None)
        recursive: Whether to search in subfolders (default: False)
        
    Returns:
        list[Path]: List of paths to matching CSV files
        
    Raises:
        Exception: If an error occurs while searching for CSV files
    """
    try:
        # Convert to Path object and resolve any relative paths
        folder = Path(folder_path).resolve()
        
        if not folder.is_dir():
            raise NotADirectoryError(f"'{folder}' is not a valid directory")
        
        # Set up pattern matching
        pattern = "*.csv"
        if recursive:
            pattern = "**/" + pattern
        
        # Get all CSV files
        csv_files = [p for p in folder.glob(pattern)]
        
        # Filter by prefix if specified
        if prefix:
            csv_files = [p for p in csv_files if p.name.startswith(prefix)]
            
        return sorted(csv_files, key=lambda x: int(x.name.split('.')[0])) if sort else csv_files
        
    except Exception as e:
        raise Exception(f"Error searching for CSV files: {str(e)}")


def read_json_file(file_path: Union[str, Path]) -> dict:
    """
    Read and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file to read
        
    Returns:
        dict: Parsed JSON data as a dictionary
        
    Raises:
        FileNotFoundError: If file does not exist
        JSONDecodeError: If file contains invalid JSON
    """
    try:
        # Convert to Path object and resolve path
        path = Path(file_path).resolve()
        
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")
            
        # Read and parse JSON
        with open(path, 'r') as f:
            return json.load(f)
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {str(e)}")
        return {}
    except Exception as e:
        print(f"Error reading JSON file: {str(e)}")
        return {}

def parse_sensor_schema(sensor_schema: dict) -> dict:
    """
    Parse the sensor schema into a dictionary
    """

    kwargs = {}
    for key, value in sensor_schema.items():
        kwargs[key] = value
    return kwargs