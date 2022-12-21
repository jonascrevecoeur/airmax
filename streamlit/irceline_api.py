import requests
import json
import time
import pandas as pd
from datetime import datetime

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

# TODO: Checking data quality when parsing measurements
# -99.99 appears to be a placeholder for a failed measurement, but there might be other values used in this way
def _parse_measurements(measurements:dict) -> pd.DataFrame:

    aggregated_measurements = []    
    for series_id, data in measurements.items():
        value_summed = 0
        measurement_count = 0
        for measurement in data['values']:
            if (measurement['value'] is not None) and (not measurement['value'] == -99.99):
                value_summed += measurement['value']
                measurement_count += 1
        
        if measurement_count > 0:
            aggregated_measurements.append({
                'series-id': series_id,
                'measurement': value_summed / measurement_count,
                'num-measurements': measurement_count
            })

    return pd.DataFrame(aggregated_measurements)

# Returns the average measurement over the last 3 hours
def get_recent_measurements(metadata_file: str) -> pd.DataFrame:

    metadata = pd.read_csv(metadata_file)
    metadata['series-id'] = metadata['series-id'].astype(str)

    url = f"https://geo.irceline.be/sos/api/v1/timeseries/getData"
    
    # last 3 hours - ISO_8601 format https://en.wikipedia.org/wiki/ISO_8601#Time_intervals
    timespan = "PT3H/" + datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    body = {
        'timespan': timespan,
        'timeseries': list(metadata['series-id'].unique())
    }

    response = requests.post(
        url=url, 
        json=body,
        headers={'Accept': 'application/json'}
        )
    response.raise_for_status()

    measurements = pd.merge(
        left=_parse_measurements(json.loads(response.content)),
        right=metadata,
        how='left',
        on='series-id')

    # filters the correct reference value
    measurements = measurements[
        (measurements['reference-value-lower'].isna()) |
        ((measurements['reference-value-lower'] <= measurements['measurement']) & (measurements['measurement'] < measurements['reference-value-upper']))
    ]

    return measurements
    

