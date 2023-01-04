import json
import os
import sys
import datetime
import math

import irceline_api as irceline_api

from dotenv import load_dotenv
import pymysql
import pandas as pd

load_dotenv()

def connect_to_database() -> pymysql.connections.Connection:
    load_dotenv()

    try:
        database_connection = pymysql.connect(
            user = os.environ.get('user'),
            password = os.environ.get('password'), # type: ignore
            host = os.environ.get('host'),
            port = 3306,
            connect_timeout = 5
        )

        return database_connection
    except pymysql.Error as e:
        print(f"Error connecting to MariaDB. {e}")
        raise

def format_record(record: dict) -> tuple:

    return tuple({
        'measurement_fetch_time_utc': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.0"),
        'series_id': int(record['series_id']),
        'location_id': record['location_id'],
        'location_name': record['location_name'],
        'latitude': record['latitude'],
        'longitude': record['longitude'],
        'parameter_name': record['parameter_name'],
        'parameter_value': record['parameter_value'],
        'num_measurements': record['num_measurements'],
        'reference_value_lower': None if math.isnan(record['reference_value_lower']) else record['reference_value_lower'],
        'reference_value_upper': None if math.isnan(record['reference_value_upper']) else record['reference_value_upper'],
        'reference_color': record['reference_color'],
        
    }.values())

def lambda_handler(event, context):
    
    connection = connect_to_database()
    cursor = connection.cursor()

    metadata = pd.read_sql_query('select * from openaq.irceline_sensor_metadata', connection) # type: ignore
    measurements =  irceline_api.get_recent_measurements(metadata)

    with open("queries/ingestion/insert-irceline-measurements-historical.sql", 'r') as f:
        sql_historical = f.read()

    with open("queries/ingestion/insert-irceline-measurements-current.sql", 'r') as f:
        sql_current = f.read()

    records = [format_record(record) for record in measurements.to_dict(orient='records')]

    cursor.executemany(sql_historical, records)
    cursor.execute('truncate openaq.irceline_measurements_current')
    cursor.executemany(sql_current, records)

    connection.commit() 

    cursor.close()
    connection.close()