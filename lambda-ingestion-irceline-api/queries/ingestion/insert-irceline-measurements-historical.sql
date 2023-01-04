insert into openaq.irceline_measurements_historical (
    measurement_fetch_time_utc,
    series_id,
    location_id,
    location_name,
    latitude,
    longitude,
    parameter_name,
    parameter_value,
    num_measurements,
    reference_value_lower,
    reference_value_upper,
    reference_color 
)
values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)