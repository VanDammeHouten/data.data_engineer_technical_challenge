"""
Test suite for image-related utility functions.
"""

# Standard library imports first
import pytest
from pathlib import Path

# Third-party imports second
import pandas as pd
from PIL import Image
from pyapp.app import CommandOptions  # if needed

# Local imports last
from bioscout_tech_challenge.utils.image import get_image_dimensions

def test_get_image_dimensions():
    # Create test image
    test_image_path = Path('test_image.jpg')
    with Image.new('RGB', (100, 200)) as img:
        img.save(test_image_path)
    
    try:
        # Test single image
        df = get_image_dimensions([test_image_path])
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

        #Test invalid image - should return empty DataFrame
        invalid_df = get_image_dimensions('invalid_image.jpg')
        assert len(invalid_df) == 0
    
    finally:
        # Cleanup
        test_image_path.unlink()
