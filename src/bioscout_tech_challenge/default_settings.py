from pyapp.conf import Settings
import pathlib
DEBUG: bool = False
class BioscoutTechChallengeSettings(Settings):
    SENSOR_SCHEMA: str = pathlib.Path(__file__).parent / "sensor_schema.json"
    HEADER_DETECTION: bool = False
    COMBINE: bool = False
    ENCODING: str = 'utf-8'
    SEPARATOR: str = ','
    PREFIX: str = 'weather_data'
    RECURSIVE: bool = False
    SUFFIX: str = '_flattened'
