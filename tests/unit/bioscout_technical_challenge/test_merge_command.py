# Standard library imports
import tempfile
from pathlib import Path

# Third-party imports
import pytest
import pandas as pd
from pyapp.app import CommandOptions

# Local imports
from bioscout_tech_challenge.cli import merge_command

@pytest.fixture
def sample_weather_data():
    """Create a sample weather DataFrame for testing."""
    return pd.DataFrame({
        'device_id': [1, 1, 2, 2],
        'timestamp': ['2024-01-01', '2024-01-02', '2024-01-01', '2024-01-02'],
        'temperature': [20.5, 21.0, 19.5, 20.0],
        'humidity': [45, 48, 50, 52]
    })

@pytest.fixture
def sample_device_data():
    """Create a sample device DataFrame for testing."""
    return pd.DataFrame({
        'device_id': [1, 2],
        'latitude': [-33.865143, -33.865143],
        'longitude': [151.209900, 151.209900],
        'location': ['Sydney', 'Sydney']
    })

@pytest.fixture
def temp_csv_files(sample_weather_data, sample_device_data):
    """Create temporary CSV files with sample data."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as weather_tmp:
        sample_weather_data.to_csv(weather_tmp.name, index=False)
        weather_path = Path(weather_tmp.name)
        
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as device_tmp:
        sample_device_data.to_csv(device_tmp.name, index=False)
        device_path = Path(device_tmp.name)
        
    return weather_path, device_path

def test_merge_command_basic(temp_csv_files):
    """Test basic merge functionality."""
    weather_file, device_file = temp_csv_files
    
    try:
        # Create command options
        opts = CommandOptions()
        opts.device_csv = device_file
        opts.file = weather_file
        opts.directory = None
        opts.timezone = False
        opts.output = None
        opts.merge_column = "device_id"

        # Run merge command
        merge_command(opts)

        # Read the output file
        output_file = weather_file.parent / (weather_file.stem + '_merged.csv')
        result_df = pd.read_csv(output_file)

        # Verify merge results
        assert len(result_df) == 4  # Should maintain all weather records
        assert 'latitude' in result_df.columns  # Should include device info
        assert 'longitude' in result_df.columns
        assert 'location' in result_df.columns

    finally:
        # Cleanup
        weather_file.unlink(missing_ok=True)
        device_file.unlink(missing_ok=True)
        output_file = weather_file.parent / (weather_file.stem + '_merged.csv')
        output_file.unlink(missing_ok=True) 