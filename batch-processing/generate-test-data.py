import sys
import os
import time
import random
import string
from datetime import datetime, timedelta

import pymysql
from mariadb.constants.ERR import ER_DUP_ENTRY
from dotenv import load_dotenv
import numpy as np

def connect_to_database(settings_file:str = None) -> pymysql.connections.Connection:

    if settings_file is None: 
        rds_host  = "localhost"
        name = "root"
        password = "password"
        db_name = "openaq"
    else:
        load_dotenv(settings_file)

        rds_host  = os.environ.get('DB_HOSTNAME')
        name = os.environ.get('DB_USERNAME')
        password = os.environ.get('DB_PASSWORD')
        db_name = os.environ.get('DB_DATABASE')

    try:
        connection = pymysql.connect(
            host=rds_host, 
            user=name, 
            passwd=password, 
            db=db_name, 
            connect_timeout=5
        )
    except pymysql.Error as e:
        print(f"Error connecting to MariaDB. {e}")
        raise 

    return connection

def generate_random_string(length:int) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def generate_random_record() -> dict:

    city = random.choice(['Genk', 'Diepenbeek', 'Leuven', 'Antwerpen', 'Hasselt', 'Brussel', 'Gent', 'Landen'])

    record = {
        'message_id': generate_random_string(10),
        'message_send_time_utc': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.0"),
        'measurement_time_utc': (datetime.utcnow() + timedelta(minutes=-np.exp(np.random.normal(1, 1)))).strftime("%Y-%m-%d %H:%M:%S.0"),
        'country_code': 'BE',
        'location': city,
        'city': city,
        'latitude': 0,
        'longitude': 1,
        'source_type': random.choice(['Government', 'Community']),
        'source_name': generate_random_string(3),
        'parameter_name': 'pm25',
        'parameter_unit': 'so³',
        'parameter_value': np.exp(np.random.normal(0, 1))
    }

    return record

def generate_data(frequency_per_minute:int, settings_file:str = None) -> None:
    
    connection = connect_to_database(settings_file)
    cursor = connection.cursor()
    
    # read the insert query template
    with open("queries/ingestion/insert-raw-record-many.sql", 'r') as f:
        sql = f.read()

    # send records in batches of 20. Frequency_per_minute is reached by waiting
    # ((20 * 60) /frequency_per_minute) seconds between each batch
    # This ignores the computation time required to send the records
    time_between_batches = (60 * 20) /frequency_per_minute 

    print("Start data generation")
    num_batches_send = 0
    while(True):
        records = [tuple(generate_random_record().values()) for i in range(20)]
        
        cursor.executemany(sql, records)
        
        connection.commit()
        num_batches_send += 1

        if(num_batches_send % 50 == 0):
            print(f"{num_batches_send * 20} records send")

        time.sleep(time_between_batches)

    # script will never reach this point, but useful when executing in interactive mode
    connection.close()

if __name__ == "__main__":
    args = sys.argv

    if len(args) > 1:
        frequency = int(args[1]) 
    else:
        print("Missing argument frequency. Inserting 100 records / minute.")
        frequency = 100

    if len(args) > 2:
        settings_file = args[2] 
    else:
        settings_file = None

    generate_data(frequency, settings_file)



