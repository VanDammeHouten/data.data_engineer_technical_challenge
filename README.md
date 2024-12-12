
# Submission

The submission to the solution is under the branch `submission`. It contains the following files:

- `README.md`: This file contains the solution to the problem.
- `src/`: This directory contains the source code for the solution.
- `tests/`: This directory contains the test cases for the solution.
- `notebooks/`: This directory contains the jupyter notebooks for the solution.

The solution assumes copying of the data directory to the root of the repository.

## How to install the solution

To run the solution, please follow the steps below:

1. Clone the repository with `git clone https://github.com/VanDammeHouten/data.data_engineer_technical_challenge.git -b submission`
2. Navigate to the root of the repository
3. Run the `poetry install` command to install the dependencies within a virtual environment with python>=3.12
4. Copy the data directory to the root of the repository `cp -R data/ data.data_engineering_challenge/data`
5. Confirm running `bioscout-tech-challenge --help` to see the available commands addition of weather should be present
6. Confirm running `bioscout-tech-challenge weather --help` to see the available commands for the weather data and that the flatten, merge and filter commands are present.

## How to run the solution
### 1. Pre-Process Weather Data
The exploration of the weather data is done in the `notebooks/exploration.ipynb` notebook. This work leads to the development of the flatten and merge commands of the bioscout-tech-challenge cli tool. These commands will be used to pre-process the weather data for the visualisation and analysis tasks.

### 2. Visualise Weather Data & Provide Insights
The visualisation of the weather data is done in the `notebooks/visualisation.ipynb` notebook. This work leads to the development of the filter command of the bioscout-tech-challenge cli tool.  Before running this notebook the following bash commands should be run to flatten and merge the weather data:
```bash
bioscout-tech-challenge weather flatten --combine --directory=data/tables/weather_data
bioscout-tech-challenge weather merge -tz \
--file=data/tables/weather_data/flattened/weather_data_flattened.csv \
--device_csv=data/tables/weather_data/weather_devices.csv \
--output=data/tables/weather_data/output/exploration_data_output.csv
```

The filter command can be run to remove and tag the weather data identified within the `notebooks/visualisation.ipynb` notebook. This is not required for the solution to work, but it is a useful to apply the insights from the visualisation to the weather data for future analysis.
```bash
bioscout-tech-challenge weather filter \
--config=data/filters/weather_filters.json \
--file=data/tables/weather_data/output/exploration_data_output.csv \
--output=data/tables/weather_data/output/filtered_data_output.csv
```

### 3. Explore Imagery & Bounding Boxes
The exploration of the imagery and bounding boxes is done in the `notebooks/imagery_exploration.ipynb` notebook. This work leads to the development of the bounding box commands of the bioscout-tech-challenge cli tool. These commands will be used to explore the imagery and bounding boxes for the analysis task.


## Future Work

- Add more tests to the bioscout-tech-challenge package specifically for the utils module
- Implement checks for the pyapp cli
- Add different output formats for the cli including connecting to a database through the pyapp settings module
- Implement ablitity to change the output of the logging module and the logging level

