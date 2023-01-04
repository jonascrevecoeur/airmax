import requests
import json
import time
import pandas as pd
from datetime import datetime
from typing import Optional

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
                'series_id': series_id,
                'parameter_value': value_summed / measurement_count,
                'num_measurements': measurement_count
            })

    return pd.DataFrame(aggregated_measurements)

# Returns the average measurement over the last 3 hours
def get_recent_measurements(metadata: pd.DataFrame) -> pd.DataFrame:

    metadata['series_id'] = metadata['series_id'].astype(str)

    url = f"https://geo.irceline.be/sos/api/v1/timeseries/getData"
    
    # last 3 hours - ISO_8601 format https://en.wikipedia.org/wiki/ISO_8601#Time_intervals
    timespan = "PT3H/" + datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    body = {
        'timespan': timespan,
        'timeseries':  list(metadata['series_id'].unique())
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
        on='series_id')

    # filters the correct reference value
    measurements = measurements[
        (measurements['reference_value_lower'].isna()) |
        ((measurements['reference_value_lower'] <= measurements['parameter_value']) & (measurements['parameter_value'] < measurements['reference_value_upper']))
    ]

    return measurements
    

