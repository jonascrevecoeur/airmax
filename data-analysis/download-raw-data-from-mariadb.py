import sys
import os
import time
import random
import string
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
import pymysql
import pandas as pd

def connect_to_database() -> pymysql.connections.Connection:

    load_dotenv()

    rds_host  = os.environ.get('DB_HOSTNAME')
    name = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')

    try:
        connection = pymysql.connect(
            host=rds_host, 
            user=name, 
            passwd=password, 
            connect_timeout=5
        )
    except pymysql.Error as e:
        print(f"Error connecting to MariaDB. {e}")
        raise 

    return connection

def download_data(destination:Optional[str] = None) -> None:
    
    connection = connect_to_database()

    data = pd.read_sql("select * from openaq.raw", connection) # type: ignore
    data.to_csv(destination, index=False)

    connection.close()

if __name__ == "__main__":
    args = sys.argv

    if len(args) > 1:
        destination = args[1]
    else:
        print("Saving data to data/openaq_raw.csv")
        destination = "data/openaq_raw.csv"

    download_data(destination)
