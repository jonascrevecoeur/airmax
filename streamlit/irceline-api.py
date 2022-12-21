import requests
import json
import time
import pandas as pd

def list_timeseries() -> dict:
        
    url = "https://geo.irceline.be/sos/api/v1/timeseries"

    response = requests.get(url)
    response.raise_for_status()

    return json.loads(response.content)

def _parse_timeseries_metadata(metadata:dict) -> dict:

    core = {
        'series-id': metadata['id'],
        'location-id': metadata['station']['properties']['id'],
        'location-name': metadata['station']['properties']['label'],
        'longitude': metadata['station']['geometry']['coordinates'][0],
        'latitude': metadata['station']['geometry']['coordinates'][1],
        'phenomenon': metadata['parameters']['phenomenon']['label'],
    }

    if 'statusIntervals' in metadata:

        reference_values = [{
            'reference-value-lower': float(interval['lower']),
            'reference-value-upper': float(interval['upper']),
            'reference-value-color': interval['color']
        } for interval in metadata['statusIntervals']]

    else:

        reference_values = [{
            'reference-value-lower': None,
            'reference-value-upper': None,
            'reference-value-color': "#888888"
        }]

    return [
        {**core, **reference_value} for reference_value in reference_values
    ]

# Returns a list with one dict per reference category
def get_timeries_metadata(id:str) -> list:

    url = f"https://geo.irceline.be/sos/api/v1/timeseries/{id}"

    response = requests.get(url)
    response.raise_for_status()

    return _parse_timeseries_metadata(json.loads(response.content))

# There is no convenient API endpoint to get all metadata of the timeseries 
# Collect it once and save it in a csv for future use
def collect_and_store_metadata_as_csv(filename: str) -> None:
    timeseries = list_timeseries()

    collected_metadata = []
    for idx, series in enumerate(timeseries):
        metadata = get_timeries_metadata(series['id'])
        collected_metadata.extend(metadata)

        if idx % 10 == 0:
            print(f"processed {idx}/{len(timeseries)} points")

        # limit the number of requests per minute
        time.sleep(2)

    pd.DataFrame(collected_metadata).to_csv(filename, index=None)