import pytest
import pandas as pd
from pathlib import Path
import json
import tempfile
from bioscout_tech_challenge.cli import filter_weather
from pyapp.app import CommandOptions

@pytest.fixture
def sample_weather_data():
    """Create a sample weather DataFrame for testing."""
    return pd.DataFrame({
        'device_id': [255, 280, 285, 290, 290],
        'timestamp': ['2024-11-06', '2024-11-06', '2024-11-21', '2024-11-22', '2024-11-07'],
        'sensor_type': ['temperature', 'temperature', 'rainfall', 'rainfall', 'rainfall'],
        'sensor_device': ['Generic', 'Generic', 'OpticalRainGauge', 'OpticalRainGauge', 'OpticalRainGauge'],
        'value': [20.5, 22.0, 0.5, 0.0, 1.0]
    })

@pytest.fixture
def filter_config():
    """Create a sample filter configuration."""
    return {
        "remove_filters": [
            {
                "name": "remove_prototype_devices",
                "description": "Remove sensor readings from prototype devices",
                "filters": [
                    {
                        "device_id": 255
                    }
                ]
            },
            {
                "name": "remove_calibration_data",
                "description": "Remove calibration data from devices",
                "filters": [
                    {
                        "device_id": {"min": 280, "max": 291},
                        "timestamp": {"min": "2024-11-05", "max": "2024-11-08"}
                    }
                ]
            }
        ],
        "tag_filters": [
            {
                "name": "optical_device_malfunction",
                "description": "Tag optical devices that have malfunctioned",
                "tag": "OpticalRainGauge_malfunction",
                "filters": [
                    {
                        "device_id": 290,
                        "timestamp": {"min": "2024-11-20", "max": "2024-11-23"},
                        "sensor_type": "rainfall",
                        "sensor_device": "OpticalRainGauge"
                    }
                ]
            }
        ]
    }

@pytest.fixture
def temp_csv_file(sample_weather_data):
    """Create a temporary CSV file with sample data."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        sample_weather_data.to_csv(tmp.name, index=False)
        return Path(tmp.name)

@pytest.fixture
def temp_filter_file(filter_config):
    """Create a temporary JSON file with filter configuration."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        json.dump(filter_config, tmp)
        return Path(tmp.name)

def test_remove_filters(temp_csv_file, temp_filter_file):
    """Test that removal filters work correctly."""
    # Create command options
    opts = CommandOptions()
    opts.file = temp_csv_file
    opts.filter_file = temp_filter_file
    opts.output = None

    # Run filter_weather
    filter_weather(opts)

    # Read the output file
    output_file = temp_csv_file.parent / (temp_csv_file.stem + '_filtered.csv')
    result_df = pd.read_csv(output_file)

    # Check that prototype device (255) was removed
    assert 255 not in result_df['device_id'].values

    # Check that calibration data was removed
    calibration_mask = (
        (result_df['device_id'].between(280, 291)) & 
        (pd.to_datetime(result_df['timestamp']).dt.date.between(
            pd.to_datetime('2024-11-05').date(),
            pd.to_datetime('2024-11-08').date()
        ))
    )
    assert not calibration_mask.any()

def test_tag_filters(temp_csv_file, temp_filter_file):
    """Test that tagging filters work correctly."""
    # Create command options
    opts = CommandOptions()
    opts.file = temp_csv_file
    opts.filter_file = temp_filter_file
    opts.output = None

    # Run filter_weather
    filter_weather(opts)

    # Read the output file
    output_file = temp_csv_file.parent / (temp_csv_file.stem + '_filtered.csv')
    result_df = pd.read_csv(output_file)

    # Check that OpticalRainGauge_malfunction tag was added
    assert 'OpticalRainGauge_malfunction' in result_df.columns

    # Check that correct rows were tagged
    malfunction_mask = (
        (result_df['device_id'] == 290) & 
        (pd.to_datetime(result_df['timestamp']).dt.date.between(
            pd.to_datetime('2024-11-20').date(),
            pd.to_datetime('2024-11-23').date()
        )) &
        (result_df['sensor_type'] == 'rainfall') &
        (result_df['sensor_device'] == 'OpticalRainGauge')
    )
    assert result_df.loc[malfunction_mask, 'OpticalRainGauge_malfunction'].all()
    assert not result_df.loc[~malfunction_mask, 'OpticalRainGauge_malfunction'].any()

def test_invalid_filter_file(temp_csv_file):
    """Test handling of invalid filter file."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        tmp.write(b'invalid json')
        invalid_filter_file = Path(tmp.name)

    opts = CommandOptions()
    opts.file = temp_csv_file
    opts.filter_file = invalid_filter_file
    opts.output = None

    # Should not raise an exception but log an error
    filter_weather(opts)

def test_missing_input_file(temp_filter_file):
    """Test handling of missing input file."""
    opts = CommandOptions()
    opts.file = Path('nonexistent.csv')
    opts.filter_file = temp_filter_file
    opts.output = None

    # Should not raise an exception but log an error
    filter_weather(opts)

@pytest.fixture(autouse=True)
def cleanup_temp_files(temp_csv_file, temp_filter_file):
    """Clean up temporary files after tests."""
    yield
    temp_csv_file.unlink(missing_ok=True)
    temp_filter_file.unlink(missing_ok=True)
    # Also clean up filtered output file
    output_file = temp_csv_file.parent / (temp_csv_file.stem + '_filtered.csv')
    output_file.unlink(missing_ok=True)
