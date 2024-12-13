"""
Image-related utility functions.
"""

import pandas as pd
from PIL import Image
from pathlib import Path
from typing import Union, List

def find_image_files(directory: Union[str, Path], extensions: List[str] = ['.jpg'], sort: bool = False) -> List[Path]:
    """
    Find all image files in a directory and its subdirectories.
    
    Args:
        directory: Path to directory to search
        extensions: List of file extensions to include (e.g. ['.jpg', '.png'])
    
    Returns:
        List of Path objects for all matching image files
    """
    
    if isinstance(directory, str):
        directory = Path(directory)
        
    image_files = []
    for ext in extensions:
        image_files.extend(directory.rglob(f'*{ext}'))
        
    return sorted(image_files, key=lambda x: int(x.name.split('.')[0])) if sort else image_files


def get_image_dimensions(image_paths: Union[str, List[str]], include_path: bool = False) -> pd.DataFrame:
    """
    Get width and height of images and store in DataFrame.
    
    Args:
        image_paths: Single path, list of paths
        include_path: Whether to include the image path in the DataFrame
    Returns:
        DataFrame with columns [image_path, image_width, image_height]
    """
    if isinstance(image_paths, str):
        image_paths = [image_paths]
    
    dimensions = []
    for path in image_paths:
        try:
            with Image.open(path) as img:
                width, height = img.size
                dimensions.append({
                    'file_number': str(path.stem.replace('.jpg', '')),
                    'image_width': width,
                    'image_height': height
                })
                if include_path:
                    dimensions[-1]['image_path'] = path
        except Exception as e:
            print(f"Error processing {path}: {str(e)}")
    
    return pd.DataFrame(dimensions)
