insert into openaq.raw (
    message_id,
    message_send_time_utc,
    measurement_time_utc,
    country_code,
    location,
    city,
    latitude,
    longitude,
    source_type,
    source_name,
    parameter_name,
    parameter_unit,
    parameter_value
)
values (?,?,?,?,?,?,?,?,?,?,?,?,?)