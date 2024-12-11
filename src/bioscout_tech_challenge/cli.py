import logging

from pyapp import app
from pyapp.app import CliApplication, argument, CommandOptions
from bioscout_tech_challenge.utils.weather import flatten_weather_data, merge_weather_data, add_timezone_from_coordinates
from bioscout_tech_challenge.utils.file_operations import *
from bioscout_tech_challenge.default_settings import BioscoutTechChallengeSettings
from pyapp.conf import settings
from pathlib import Path
# Initialize the application with settings
APP = CliApplication(
    prog="bioscout-tech-challenge",
    description="Bioscout Tech Challenge CLI",
    application_settings="bioscout_tech_challenge.default_settings"
)

# Get settings instance
main = APP.dispatch

@APP.command
@argument(
    "-n",
    "--name",
    help_text="Choose what name to greet",
    default="Nick",
)
def hello(opts: CommandOptions):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    logger.info(f"Hello {opts.name}")

# Create the weather command group
weather_group = APP.create_command_group(
    "weather",
    help_text="Commands for processing weather data files",
)

@weather_group.command(name="flatten")
@argument(
    "-f",
    "--file",
    help_text="Path to the file to flatten",
    default=None,
)
@argument(
    "-o",
    "--output",
    help_text="Path to the output file default is the same as the input file/directory",
    default=None,
    type=Path,
)
@argument(
    "-d",
    "--directory",
    help_text="Path to the directory of files matching the prefix to flatten",
    default=None,
)
@argument(
    "-hd",
    "--header_detection",
    help_text="Whether to detect the header from the first file (default is True only when a directory is provided)",
    default=BioscoutTechChallengeSettings.HEADER_DETECTION,
    action="store_true",
)
@argument(
    "-c",
    "--combine",
    help_text="Whether to combine the files into a single file(default is False)",
    default=BioscoutTechChallengeSettings.COMBINE,
    # type=bool, 
    action="store_true",
)
@argument(
    "-s",
    "--source_column",
    help_text="Whether to add a column to the output file to store the source file information(default is False)",
    default=settings.DEBUG,
    action="store_true",
)
@argument(
    "-ss",
    "--sensor_schema",
    help_text="Path to the sensor schema file as a json",
    default=BioscoutTechChallengeSettings.SENSOR_SCHEMA,
    type=Path,
)
@argument(
    "-sep",
    "--separator",
    help_text="Separator for the csv file",
    default=BioscoutTechChallengeSettings.SEPARATOR,
)
def flatten_weather(opts: CommandOptions):
    """
    Flatten weather data from a CSV file or directory of CSV files.
    Extracts additional sensor data from the extra_information column and merges it with the weather data.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    # check if the user provided a file or directory
    if opts.directory:
        logger.info(f"Flattening directory {opts.directory}")
    elif opts.file:
        logger.info(f"Flattening file {opts.file}")
    else:
        logger.error("No file or directory provided")
        return
    if opts.directory:
        try:
            files = find_csv_files(
                opts.directory, 
                prefix=BioscoutTechChallengeSettings.PREFIX, 
                recursive=BioscoutTechChallengeSettings.RECURSIVE
            )
        except Exception as e:
            logger.error(e)
            return
    else:
        files = [Path(opts.file)]
    logger.debug(f"Files: {files}")

    total_missing_headers = 0
    header_locations = []
    # check if at least one file has a header
    for i,file in enumerate(files):
        header_locations.append(identify_header(file))
        if header_locations[-1] is None:
            logger.debug(f"No header detected in file {file}")
            total_missing_headers += 1
        else:
            logger.debug(f"Header detected in file {file}")
            header_location = i

    # if there are missing headers and no header was detected, error
    if total_missing_headers > 0 and header_locations.count(None) == len(files):
        logger.error("No header detected in any file")
        return
    elif total_missing_headers != 0:
        detect_header = True
        #swap the first file with the file that has the header
        files[0], files[header_location] = files[header_location], files[0]
    # read the sensor schema if it is provided
    logger.info(f"Reading sensor schema from {opts.sensor_schema}")
    if opts.sensor_schema and Path(opts.sensor_schema).exists():
        sensor_schema_json = read_json_file(opts.sensor_schema)
        sensor_schema = parse_sensor_schema(sensor_schema_json)
    else:
        logger.warning(f"Sensor schema file not provided or does not exist: {opts.sensor_schema}")
        logger.warning(f"Using default sensor schema")
        sensor_schema = {}
    if opts.output is None:
        if not (files[0].parent / BioscoutTechChallengeSettings.SUFFIX.replace('_', '')).exists():
            logger.warning(f"No {BioscoutTechChallengeSettings.SUFFIX.replace('_', '')} folder found in {files[0].parent}, making {BioscoutTechChallengeSettings.SUFFIX.replace('_', '')} folder")
            (files[0].parent / BioscoutTechChallengeSettings.SUFFIX.replace('_', '')).mkdir(parents=True, exist_ok=True)
        opts.output = files[0].parent / BioscoutTechChallengeSettings.SUFFIX.replace('_', '') 
    else:
        if opts.output.suffix and not opts.combine:
            logger.error("Cannot output multiple files into a single file if the output is a file")
            return               
        if opts.output.exists():
            if opts.output.is_file() and opts.combine:
                logger.warning(f"Output file {opts.output} already exists, overwriting it")
            elif opts.output.is_file() and not opts.combine and len(files) > 1:
                logger.error("Cannot output multiple files into a single file if the output is a file")
                return
        else:
            if opts.output.suffix:  # Check if the path has a file extension
                logger.warning(f"Output file {opts.output} does not exist, creating parent directories")
                opts.output.parent.mkdir(parents=True, exist_ok=True)
            else:
                logger.warning(f"Output folder {opts.output} does not exist, creating it")
                opts.output.mkdir(parents=True, exist_ok=True)

    logger.debug(f"Output: {opts.output}")
    # combine the files if the combine flag is set
    if opts.combine and len(files) > 1:
        df = combine_csv_files(files, detect_header=detect_header, add_source_column=opts.source_column)
        try:
            df = flatten_weather_data(df, **sensor_schema)
        except Exception as e:
            logger.error(f"Error flattening data: {e}")
            return
        if isinstance(opts.output, Path):
            output_filename = BioscoutTechChallengeSettings.PREFIX + BioscoutTechChallengeSettings.SUFFIX + '.csv'
            opts.output = opts.output / output_filename
        save_csv_file(df, opts.output)
    else:
        for i,file in enumerate(files):
            try:
                if i != 0 and header_locations[i] is None:
                    df = read_csv_file(file, header=header_locations[i],names=columns)
                else:
                    df = read_csv_file(file, header=header_locations[i])
                    columns = df.columns

                df = flatten_weather_data(df, **sensor_schema)
            except Exception as e:
                logger.error(f"Error flattening data of {file}: {e}")
                return
            if isinstance(opts.output, Path):
                output_filename = file.name.replace('.csv', '') + BioscoutTechChallengeSettings.SUFFIX + '.csv'
                save_csv_file(df, opts.output / output_filename)
            else:
                save_csv_file(df, opts.output)
    
    logger.info(f"Flattened {len(files)} files and saved to {opts.output}")

@weather_group.command(name="merge")
@argument(
    "--device_csv",
    help_text="Path to the device csv file",
    type=Path,
    required=True,
)
@argument(
    "-f",
    "--file",
    help_text="Path to the weather csv file to merge",
    type=Path,
    default=None,
)
@argument(
    "-d",
    "--directory",
    help_text="Path to the directory of weather files to merge",
    type=Path,
    default=None,
)
@argument(
    "-tz",
    "--timezone",
    help_text="Calculate the timezone of the device from the latitude and longitude",
    default=False,
    action="store_true",
)
@argument(
    "-o",
    "--output",
    help_text="Path to save merged files. If not provided, will save alongside input files",
    type=Path,
    default=None,
)
@argument(
    "-m",
    "--merge_column",
    help_text="Column to merge on (default: device_id)",
    type=str,
    default="device_id",
)
def merge_command(opts: CommandOptions):
    """
    Merge weather data with device information from a CSV file.
    Can merge either a single weather CSV file or an entire directory of weather files.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # Read device data
    try:
        device_df = read_csv_file(opts.device_csv)
        logger.info(f"Read device data from {opts.device_csv}")
    except Exception as e:
        logger.error(f"Error reading device data: {e}")
        return
    if opts.timezone:
        device_df = add_timezone_from_coordinates(device_df)

    # Determine input files
    if opts.directory:
        try:
            files = find_csv_files(
                opts.directory, 
                recursive=BioscoutTechChallengeSettings.RECURSIVE
            )
            logger.info(f"Found {len(files)} files in {opts.directory}")
        except Exception as e:
            logger.error(f"Error finding CSV files: {e}")
            return
    elif opts.file:
        files = [Path(opts.file)]
        logger.info(f"Using single file: {opts.file}")
    else:
        logger.error("No input file or directory provided")
        return
    print(opts.output)
    # Process each file
    for file in files:
        try:
            # Read weather data
            weather_df = read_csv_file(file)
            logger.debug(f"Read weather data from {file}")

            # Merge data
            merged_df = merge_weather_data(
                weather_df,
                device_df,
                merge_column=opts.merge_column
            )
            logger.debug(f"Merged data for {file}")

            # Determine output path
            if opts.output is None:
                output_file = file.parent / (file.stem + '_merged.csv')
            elif opts.output.is_dir():
                output_file = opts.output / (file.stem + '_merged.csv')
            else:
                output_file = opts.output

            # Create output directory if needed
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Save merged data
            save_csv_file(merged_df, output_file)
            logger.info(f"Saved merged data to {output_file}")

        except Exception as e:
            logger.error(f"Error processing file {file}: {e}")
            continue

@weather_group.command(name="filter")
@argument(
    "-f",
    "--file",
    help_text="Path to the weather csv file to filter",
    default=None,
    type=Path,
)
@argument(
    "-o",
    "--output",
    help_text="Path to the output file",
    default=None,
    type=Path,
)
@argument(
    "-d",
    "--directory",
    help_text="Path to the directory of weather files to filter",
    default=None,
    type=Path,
)
@argument(
    "-ff",
    "--filter_file", 
    help_text="Path to the filter file json containing columns and values to filter on",
    default=None,
    type=Path,
    required=True
)
@argument(
    "-t",
    "--tag",
    help_text="Name of the column to add when tagging rows. If not provided, matching rows will be removed",
    default=None,
)
def filter_weather(opts: CommandOptions):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Check inputs
    if opts.directory:
        logger.info(f"Filtering files in directory {opts.directory}")
        try:
            files = find_csv_files(opts.directory, recursive=BioscoutTechChallengeSettings.RECURSIVE)
        except Exception as e:
            logger.error(f"Error finding CSV files: {e}")
            return
    elif opts.file:
        logger.info(f"Filtering file {opts.file}")
        files = [Path(opts.file)]
    else:
        logger.error("No input file or directory provided")
        return

    # Read filter file
    try:
        filter_config = read_json_file(opts.filter_file)
    except Exception as e:
        logger.error(f"Error reading filter file: {e}")
        return

    # Process each file
    for file in files:
        try:
            data_df = read_csv_file(file)
            modified_df = data_df.copy()
            
            # Apply removal filters
            if "remove_filters" in filter_config:
                for filter_group in filter_config["remove_filters"]:
                    for filter_condition in filter_group["filters"]:
                        matching_idx = apply_single_filter(modified_df, filter_condition)
                        modified_df = modified_df.drop(matching_idx)
                        logger.info(f"Removed {len(matching_idx)} rows using filter '{filter_group['name']}'")
            
            # Apply tagging filters
            if "tag_filters" in filter_config:
                for filter_group in filter_config["tag_filters"]:
                    tag_column = filter_group["tag"]
                    # Initialize tag column if it doesn't exist
                    if tag_column not in modified_df.columns:
                        modified_df[tag_column] = False
                    
                    for filter_condition in filter_group["filters"]:
                        matching_idx = apply_single_filter(modified_df, filter_condition)
                        modified_df.loc[matching_idx, tag_column] = True
                        logger.info(f"Tagged {len(matching_idx)} rows with '{tag_column}' using filter '{filter_group['name']}'")
            
            # Save output
            if opts.output is None:
                outputfile = file.parent / (file.name.replace('.csv', '') + '_filtered.csv')
            elif opts.output.is_dir():
                outputfile = opts.output / (file.name.replace('.csv', '') + '_filtered.csv')
            else:
                outputfile = opts.output
                
            save_csv_file(modified_df, outputfile)
            logger.info(f"Saved filtered data to {outputfile}")
            
        except Exception as e:
            logger.error(f"Error processing file {file}: {e}")
            continue
