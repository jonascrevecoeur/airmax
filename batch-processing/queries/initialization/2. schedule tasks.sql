SET GLOBAL event_scheduler = ON;

DELIMITER @@;
CREATE EVENT aggregate-records
ON SCHEDULE EVERY 5 MINUTE
DO 
BEGIN
    START TRANSACTION;
    truncate openaq.current_air_quality;

    insert into openaq.current_air_quality
        (city, latitude, longitude, parameter_name, parameter_value, parameter_unit,
        num_measurements, evaluation_time_utc)
    select
        city,
        avg(latitude) as latitude,
        avg(longitude) as longitude,
        parameter_name,
        avg(parameter_value) as parameter_value,
        parameter_unit,
        count(*) as num_measurements,
        utc_time() as evaluation_time_utc
    from openaq.raw
    where measurement_time_utc > date_sub(utc_time(), INTERVAL 3 HOUR)
    group by parameter_name, city, parameter_unit;

    COMMIT;
END
@@;
DELIMITER ;
