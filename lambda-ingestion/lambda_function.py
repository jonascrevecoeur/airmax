import json
import os
import sys
import datetime
import boto3

from dotenv import load_dotenv
import pymysql

load_dotenv()

# share database_connection between calls to lambda_handler
database_connection = None
kinesis_client=boto3.client('kinesis')

# read the MariaDB query template
with open("insert-raw-record-many.sql", 'r') as f:
    sql = f.read()

def connect_to_database() -> None:
    global database_connection

    try:
        # NOTE: Should request access to AWS Secrets Manager, to move DB_PASSWORD to a secret
        database_connection = pymysql.connect(
            user = os.environ.get('DB_USERNAME'),
            password = os.environ.get('DB_PASSWORD'),
            host = os.environ.get('DB_HOSTNAME'),
            port = 3306,
            connect_timeout=5
        )
    except pymysql.Error as e:
        print(f"Error connecting to MariaDB. {e}")
        raise

def format_datetime(datetime_str:str) -> str:
    return (datetime.datetime
        .strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        .strftime("%Y-%m-%d %H:%M:%S.0")
    )

def format_record(record: dict) -> dict:

    return {
        'message_id':record["MessageId"],
        'message_send_time_utc':format_datetime(record["Timestamp"]),
        'measurement_time_utc':format_datetime(record["MessageAttributes"]["date_utc"]["Value"]),
        'country_code':record["MessageAttributes"]["country"]["Value"],
        'location':record["MessageAttributes"]["location"]["Value"],
        'city':record["MessageAttributes"]["city"]["Value"],
        'latitude':record["MessageAttributes"]["latitude"]["Value"],
        'longitude':record["MessageAttributes"]["longitude"]["Value"],
        'source_type':record["MessageAttributes"]["sourceType"]["Value"],
        'source_name':record["MessageAttributes"]["sourceName"]["Value"],
        'parameter_name':record["MessageAttributes"]["parameter"]["Value"],
        'parameter_unit':record["MessageAttributes"]["unit"]["Value"],
        'parameter_value':float(record["MessageAttributes"]["value"]["Value"])
    }


# For testing purpose only 
# Sending to multiple streams without checks might result in duplicate data in case of errors
def lambda_handler(event, context):
    
    if (database_connection == None) or (not database_connection.open):
        print("Connect to MariaDB")
        connect_to_database()

    records = [format_record(record) for record in event["Records"]]
    
    # send to kinesis
    records_kinesis = [{'Data': json.dumps(record), 'PartitionKey': record['parameter_name'] + '|' + record['city']} for record in records]
    response = kinesis_client.put_records(StreamName=os.environ.get('stream_name'), Records=records_kinesis)
    
    # send to mariadb
    records_mariadb = [tuple(record.values()) for record in records]
    print(records_mariadb)
    cursor = database_connection.cursor()
    cursor.executemany(sql, records_mariadb)
    database_connection.commit()
    cursor.close()