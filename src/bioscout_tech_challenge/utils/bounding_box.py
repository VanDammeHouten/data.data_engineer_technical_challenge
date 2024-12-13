"""
Bounding box utility functions.
"""
from typing import List
import pandas as pd
from ..models import BoundingBox

def df_to_bounding_boxes(
    df: pd.DataFrame,
    method: str = 'direct',
    columns: list = None,
    file_name: str = None
) -> List[BoundingBox]:
    """
    Convert DataFrame rows to BoundingBox objects using specified creation method.
    
    Args:
        df: DataFrame with box coordinates
        method: Creation method ('direct', 'centroid', or 'absolute')
        columns: List of column names in order required for the method
        file_name: Name of the file the boxes are from (optional)
    Column orders:
        direct: [x, y, width, height]
        centroid: [center_x, center_y, width, height]
        absolute: [x_min, y_min, x_max, y_max]
    """
    boxes = []
    
    # Default column names for each method
    default_columns = {
        'direct': ['x', 'y', 'width', 'height'],
        'centroid': ['x_center_normalised', 'y_center_normalised', 'width_normalised', 'height_normalised'],
        'absolute': ['x_min', 'y_min', 'x_max', 'y_max','image_width','image_height']
    }
    
    # Use provided columns or defaults
    cols = columns or default_columns[method]

    # Validate column count
    expected_counts = {'direct': 4, 'centroid': 4, 'absolute': 6}
    if len(cols) != expected_counts[method]:
        raise ValueError(f"Method '{method}' requires {expected_counts[method]} columns, got {len(cols)}")
    # Add the file name to the columns if it is provided
    if file_name is not None:
        cols.append(file_name)
    for row in df[cols].itertuples():
        # row[0] is the index, actual values start from row[1]
        if method == 'direct':
            box = BoundingBox(
                x=row[1],
                y=row[2],
                width=row[3],
                height=row[4],
                name=row[5] if len(cols) == 5 else None
            )
            
        elif method == 'centroid':
            box = BoundingBox.from_centroid(
                x=row[1],
                y=row[2],
                width=row[3],
                height=row[4],
                name=row[5] if len(cols) == 5 else None
            )
            
        elif method == 'absolute':

                
            box = BoundingBox.from_absolute_coordinates(
                x_min=row[1],
                y_min=row[2],
                x_max=row[3],
                y_max=row[4],
                image_width=row[5],
                image_height=row[6],
                name=row[7] if len(cols) == 7 else None
            )
            
        boxes.append(box)
        
    return boxes