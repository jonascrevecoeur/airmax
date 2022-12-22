import base64
import json
import os
import boto3
from decimal import Decimal

# get reference to dynamodb
database = os.environ.get('database')
dynamodb = boto3.resource('dynamodb').Table(database) #type: ignore

def lambda_handler(event, context):
    
    succes = 0
    fail = 0
    
    for record in event['Records']:
        
        # Kinesis data is base64 encoded
        data = json.loads(base64.b64decode(record['kinesis']['data']).decode('utf-8'), parse_float=Decimal)
        
        try:
            dynamodb.put_item(Item = data)
            succes += 1
        except Exception as e:
            print(f"Failed writing record {data} to DynamoDB: {str(e)}")
            fail += 1
        
    return f'Successfully processed {succes} records, {fail} records failed'
