import xarray as xr
import pandas as pd
import numpy as np
import yaml
import os



def convert_csv_to_netcdf(config):
    """
    Converts CSV files to NetCDF format based on a given configuration.

    Args:
        config (dict): Configuration dictionary containing input paths as a list, output path, and global attributes.
    """

    # Get the list of input CSV files from the configuration
    data_files = config.get('input_path', {})

    # Loop through each CSV file in the input path
    for data_file in data_files:

        # Read the CSV file into a pandas DataFrame, specifying column names
        df = pd.read_csv(
            data_file,
            header=None,  # CSV has no header
            names=[
                'timestamp', 'latitude', 'longitude', 'true_wind_speed', 'true_wind_direction',
                'air_temperature', 'air_humidity', 'dew_point', 'immediate_air_pressure',
                'average_air_pressure_for_last_minute', 'sea_level_air_pressure'
            ]  # Assigning column names for the data
        )

        # Creating an xarray Dataset from the DataFrame
        # Defining coordinates (time) and data variables (other columns)
        ds = xr.Dataset(
            coords={
                'time': df['timestamp'],
            },
            data_vars={
                'latitude': ('time', df['latitude'].values),
                'longitude': ('time', df['longitude'].values),
                'true_wind_speed': ('time', df['true_wind_speed'].values),
                'true_wind_direction': ('time', df['true_wind_direction'].values.astype(str('int32'))),
                'air_temperature': ('time', df['air_temperature'].values),
                'air_humidity': ('time', df['air_humidity'].values.astype(str('int32'))),
                'dew_point': ('time', df['dew_point'].values),
                'immediate_air_pressure': ('time', df['immediate_air_pressure'].values),
                'average_air_pressure_for_last_minute': ('time', df['average_air_pressure_for_last_minute'].values),
                'sea_level_air_pressure': ('time', df['sea_level_air_pressure'].values),
            }
        )

        # Adding std names for each variable
        ds["latitude"].attrs["standard_name"] = "latitude"
        ds["longitude"].attrs["standard_name"] = "longitude"
        ds["true_wind_speed"].attrs["standard_name"] = "wind_speed"
        ds["true_wind_direction"].attrs["standard_name"] = "wind_from_direction"
        ds["air_temperature"].attrs["standard_name"] = "air_temperature"
        ds["air_humidity"].attrs["standard_name"] = "humidity_mixing_ratio"
        ds["dew_point"].attrs["standard_name"] = "dew_point_temperature"
        ds["immediate_air_pressure"].attrs["standard_name"] = "air_pressure"
        ds["average_air_pressure_for_last_minute"].attrs["standard_name"] = "tendency_of_air_pressure"
        ds["sea_level_air_pressure"].attrs["standard_name"] = "air_pressure_at_mean_sea_level"

        # Adding units for each variable
        ds["latitude"].attrs["units"] = "degree_north"
        ds["longitude"].attrs["units"] = "degree_east"
        ds["true_wind_speed"].attrs["units"] = "m s-1"
        ds["true_wind_direction"].attrs["units"] = "degrees"
        ds["air_temperature"].attrs["units"] = "degree_Celsius"
        ds["air_humidity"].attrs["units"] = "percent"
        ds["dew_point"].attrs["units"] = "degree_Celsius"
        ds["immediate_air_pressure"].attrs["units"] = "hPa"
        ds["average_air_pressure_for_last_minute"].attrs["units"] = "hPa s-1"
        ds["sea_level_air_pressure"].attrs["units"] = "hPa"
        ds["time"].attrs["units"] = "seconds since 1970-01-01 00:00:00"

        # Adding long names for each variable
        for key, value in ds.data_vars.items():
            ds[key].attrs['long_name'] = str(key)
            print(ds[f'{key}'].attrs['long_name'])

        # Adding featureType and title
        ds.attrs['title'] = str(os.path.splitext(os.path.basename(data_file))[0])  # Use the file name (without extension) as the title
        
        # Adding spatial and temporal coverage metadata
        ds.attrs['geospatial_lat_min'] = np.nanmin(ds['latitude'])
        ds.attrs['geospatial_lat_max'] = np.nanmax(ds['latitude'])
        ds.attrs['geospatial_lon_min'] = np.nanmin(ds['longitude'])
        ds.attrs['geospatial_lon_max'] = np.nanmax(ds['longitude'])
        ds.attrs['time_coverage_start'] = np.nanmin(ds['time'])
        ds.attrs['time_coverage_end'] = np.nanmax(ds['time'])
        ds.attrs['date_created'] = str(np.datetime64('today', 'D'))  # Record the creation date

        # Adding ACDD global attributes specified in the configuration
        global_attributes = config.get('global_attributes', {})
        for key, values in global_attributes.items():
            if values:
                ds.attrs[key] = values

        # Saving the dataset to a NetCDF file
        netcdf_file = f"{str(os.path.splitext(os.path.basename(data_file))[0])}.nc"

        output_path = config.get('output_path', {})[0]

        #Adding attribute history
        ds.attrs['history'] = f"{np.datetime64('now')} {os.getlogin()} {os.path.basename(__file__)} -input {os.path.basename(data_file)} -output {netcdf_file}"

        ds.to_netcdf(output_path + '/' + netcdf_file)
        print(f"NetCDF file '{output_path + netcdf_file}' created successfully!")
        
        for i, k in ds.attrs.items():
            print(f'{i} : {k} \n')

        print('-----------------------------------------------------')


if __name__ == "__main__":

    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    convert_csv_to_netcdf(config)