"""
Test suite for image-related utility functions.
"""

import pytest
import pandas as pd
from pathlib import Path
from bioscout_tech_challenge.utils.image import (
    get_image_dimensions,
        get_directory_image_dimensions,
        add_image_dimensions
)

def test_get_image_dimensions():
    # Create test image
    test_image_path = 'test_image.jpg'
    with Image.new('RGB', (100, 200)) as img:
        img.save(test_image_path)
    
    try:
        # Test single image
        df = get_image_dimensions(test_image_path)
        assert df.shape == (1, 3)
        assert df.iloc[0]['image_width'] == 100
        assert df.iloc[0]['image_height'] == 200
        
        # Test list of images
        df = get_image_dimensions([test_image_path])
        assert df.shape == (1, 3)

        #Test multiple images
        df = get_image_dimensions([test_image_path, test_image_path])
        assert df.shape == (2, 3)
        assert df.iloc[0]['image_width'] == 100
        assert df.iloc[1]['image_height'] == 200

        #Test invalid image
        with pytest.raises(Exception):
            get_image_dimensions('invalid_image.jpg')
    
    finally:
        # Cleanup
        Path(test_image_path).unlink()
