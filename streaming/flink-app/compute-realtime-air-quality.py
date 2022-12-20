import os
import json
import sys
from pyflink.table import EnvironmentSettings, StreamTableEnvironment
from pyflink.table.types import DataTypes
from pyflink.table.window import Slide
from pyflink.table.expressions import col, lit, local_timestamp

# Setup
env_settings = EnvironmentSettings.in_streaming_mode()
table_env = StreamTableEnvironment.create(environment_settings=env_settings)
table_env.get_config().set_local_timezone("UTC")

REMOTE_APPLICATION_PROPERTIES_FILE_PATH =  "/etc/flink/application_properties.json"  
LOCAL_APPLICATION_PROPERTIES_FILE_PATH = "application_properties.json"

def get_application_properties(local: bool = False) -> dict:

    if local:
        filename = LOCAL_APPLICATION_PROPERTIES_FILE_PATH
    else:
        filename = REMOTE_APPLICATION_PROPERTIES_FILE_PATH

    if os.path.isfile(filename):
        with open(filename, "r") as file:
            contents = file.read()
            properties = json.loads(contents)
            return properties
    else: 
        raise Exception(f'Application file not found at {filename}')


def get_property_group(props: dict, property_group_id: str) -> dict:
    for prop in props:
        if prop["PropertyGroupId"] == property_group_id:
            return prop["PropertyMap"]

def create_input_table(table_name: str, stream_name: str, region: str) -> None:

    param = {
        'table_name': table_name,
        'stream_name': stream_name,
        'region': region
    }

    sql = """
        CREATE TABLE {table_name} (
            message_id VARCHAR(255),
            message_send_time_utc TIMESTAMP,
            measurement_time_utc TIMESTAMP,
            country_code VARCHAR(2),
            location VARCHAR(255),
            city VARCHAR(255),
            latitude DECIMAL(8, 6),
            longitude DECIMAL(9, 6), 
            source_type VARCHAR(255),
            source_name VARCHAR(255),
            parameter_name VARCHAR(255),
            parameter_value DOUBLE,
            parameter_unit VARCHAR(255),
            proctime AS PROCTIME()
        )
        PARTITIONED BY (parameter_name, city)
        WITH (
            'connector' = 'kinesis',
            'stream' = '{stream_name}',
            'aws.region' = '{region}',
            'scan.stream.initpos' = 'LATEST',
            'format' = 'json',
            'json.timestamp-format.standard' = 'SQL'
        ) 
    """.format(**param)

    table_env.execute_sql(sql)

def create_output_table(table_name: str, stream_name: str, region: str) -> None:

    param = {
        'table_name': table_name,
        'stream_name': stream_name,
        'region': region
    }

    sql = """
        CREATE TABLE {table_name} (
            parameter_name VARCHAR(255),
            city VARCHAR(255), 
            latitude DECIMAL(8, 6),
            longitude DECIMAL(9, 6),
            parameter_value DOUBLE,
            parameter_unit VARCHAR(255),
            num_measurements INTEGER,
            evaluation_time_utc TIMESTAMP
        )
        PARTITIONED BY (parameter_name, city)
        WITH (
            'connector' = 'kinesis',
            'stream' = '{stream_name}',
            'aws.region' = '{region}',
            'format' = 'json',
            'json.timestamp-format.standard' = 'SQL'
        ) 
    """.format(**param)

    table_env.execute_sql(sql)

def perform_sliding_window_aggregation(input_table_name:str):
    input_table = table_env.from_path(input_table_name)

    sliding_window_table = (
        input_table
            # remove measurements which are more than 3 hours old
            # prevents errors when old data is added
            .filter( 
                    col("measurement_time_utc") > (local_timestamp() - lit(3).hour)
            )
            # aggregate the data received in the last 3 hours every five minutes
            .window(
                Slide
                .over(lit(3).hours)
                .every(lit(5).minutes)
                .on(col('proctime'))
                .alias("three_hour_window")
            )
            .group_by(col("parameter_name"), col("city"), col("parameter_unit"), col("three_hour_window"))
            .select(
                col("parameter_name"),
                col("city"), 
                col("latitude").avg.cast(DataTypes.DECIMAL(8, 6)).alias("latitude"),
                col("longitude").avg.cast(DataTypes.DECIMAL(9, 6)).alias("longitude"),
                col("parameter_value").avg.alias("parameter_value"),
                col("parameter_unit"),
                lit(1).count.cast(DataTypes.INT(False)).alias("num_measurements"),
                col('three_hour_window').end.cast(DataTypes.TIMESTAMP(nullable=True)).alias('evaluation_time_utc')
            )
    )

    return sliding_window_table

def main(local: bool = False):

    if local:
        CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
        table_env.get_config().get_configuration().set_string(
            key = "pipeline.jars",
            value = "file:///" + CURRENT_DIR + "/lib/flink-sql-connector-kinesis-1.15.2.jar",
        )

    # tables
    input_table_name = "OpenAQInputStream"
    output_table_name = "AverageMeasurementOutputStream"

    properties = get_application_properties(local)

    input_property_map = get_property_group(properties, 'input')
    output_property_map = get_property_group(properties, 'output')

    create_input_table(
        table_name = input_table_name, 
        stream_name = input_property_map["input.stream.name"], 
        region = input_property_map["aws.region"]
        )

    create_output_table(
        table_name = output_table_name, 
        stream_name = output_property_map["output.stream.name"], 
        region = output_property_map["aws.region"]
        )

    sliding_window_table = perform_sliding_window_aggregation(input_table_name)
    table_env.create_temporary_view("sliding_window_table", sliding_window_table) 

    table_result = table_env.execute_sql(
        "INSERT INTO {0} SELECT * FROM {1}"
        .format(output_table_name, "sliding_window_table")
    )


if __name__ == "__main__":
    args = sys.argv

    if len(args) >= 2:
        local = args[1].lower() in ("yes", "true", "1", "local")
    else:
        local = False

    main(local)