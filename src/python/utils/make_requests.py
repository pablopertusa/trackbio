import xarray as xr
import copernicusmarine

def make_request_copernicus(dataset, output_name, start_time, end_time, max_latitude, min_latitude, max_longitude, min_longitude):
    copernicusmarine.subset( 
        dataset_id = dataset,
        minimum_longitude = min_longitude,
        maximum_longitude = max_longitude,
        minimum_latitude = min_latitude,
        maximum_latitude = max_latitude,
        start_datetime = start_time,
        end_datetime = end_time,
        minimum_depth = 0,
        maximum_depth = 1,
        output_filename = output_name,
        output_directory = "/home/pablo/Desktop/zird/2/proy/trackbio/data/copernicus/raw"
    )

def make_request_and_open_copernicus(dataset, output_name, start_time, end_time, max_latitude, min_latitude, max_longitude, min_longitude):
    copernicusmarine.subset( 
        dataset_id = dataset,
        minimum_longitude = min_longitude,
        maximum_longitude = max_longitude,
        minimum_latitude = min_latitude,
        maximum_latitude = max_latitude,
        start_datetime = start_time,
        end_datetime = end_time,
        minimum_depth = 0,
        maximum_depth = 1,
        output_filename = output_name,
        output_directory = "/home/pablo/Desktop/zird/2/proy/trackbio/data/copernicus/raw"
    )
    nc_file = xr.open_dataset(f'/home/pablo/Desktop/zird/2/proy/trackbio/data/copernicus/raw/{output_name}')
    return nc_file

def make_request_and_open_copernicus_with_variables(dataset, output_name, start_time, end_time, max_latitude, min_latitude, max_longitude, min_longitude, variables):
    copernicusmarine.subset( 
        dataset_id = dataset,
        variables = variables,
        minimum_longitude = min_longitude,
        maximum_longitude = max_longitude,
        minimum_latitude = min_latitude,
        maximum_latitude = max_latitude,
        start_datetime = start_time,
        end_datetime = end_time,
        minimum_depth = 0,
        maximum_depth = 1,
        output_filename = output_name,
        output_directory = "/home/pablo/Desktop/zird/2/proy/trackbio/data/copernicus/raw"
    )
    nc_file = xr.open_dataset(f'/home/pablo/Desktop/zird/2/proy/trackbio/data/copernicus/raw/{output_name}')
    return nc_file