import sys
import json
import time
import random
import string
from datetime import datetime, timedelta

import boto3
import numpy as np

def generate_random_string(length:int) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def generate_random_record() -> dict:

    city = random.choice(['Genk', 'Diepenbeek', 'Leuven', 'Antwerpen', 'Hasselt', 'Brussel', 'Gent', 'Landen'])

    record = {
        'message_id': generate_random_string(6),
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

    return {'Data': json.dumps(record), 'PartitionKey': record['parameter_name'] + '|' + record['city']}

def generate_data(stream_name:str, frequency_per_minute:int) -> None:
    
    kinesis_client=boto3.client('kinesis')

    # send records in batches of 20. Frequency_per_minute is reached by waiting
    # ((20 * 60) /frequency_per_minute) seconds between each batch
    # This ignores the computation time required to send the records
    time_between_batches = (60 * 20) /frequency_per_minute 

    print("Start data generation")
    num_batches_send = 0
    while(True):
        records = [generate_random_record() for idx in range(20)]
        response = kinesis_client.put_records(StreamName=stream_name, Records=records)
        num_batches_send += 1

        if(num_batches_send % 50 == 0):
            print(f"{num_batches_send * 20} records send")

        time.sleep(time_between_batches)

if __name__ == "__main__":
    args = sys.argv

    if len(args) > 1:
        stream_name = args[1]
    else:
        print("Missing required first argument: stream_name")
        sys.exit()

    if len(args) > 2:
        frequency = int(args[2]) 
    else:
        print("Missing argument frequency. Inserting 100 records / minute.")
        frequency = 100

    generate_data(stream_name, frequency)



