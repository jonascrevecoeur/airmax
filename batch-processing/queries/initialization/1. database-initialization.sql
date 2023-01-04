CREATE DATABASE openaq;

drop table if exists openaq.raw;
CREATE TABLE openaq.raw (
    row mediumint primary key auto_increment,
    message_id varchar(255) unique,
    message_send_time_utc datetime,
    measurement_time_utc datetime,
    country_code varchar(2),
    location varchar(255),
    city varchar(255),
    latitude decimal(8,6),
    longitude decimal(9,6),
    source_type varchar(255),
    source_name varchar(255),
    parameter_name varchar(255),
    parameter_value double,
    parameter_unit varchar(255)
);

drop table if exists openaq.current_air_quality;
CREATE TABLE openaq.current_air_quality (
    parameter_name varchar(255),
    city varchar(255),
    latitude decimal(8,6),
    longitude decimal(9,6),
    parameter_value double,
    parameter_unit varchar(255),
    num_measurements int,
    evaluation_time_utc datetime
);

drop table if exists openaq.irceline_measurements_historical ;
CREATE TABLE openaq.irceline_measurements_historical (
  measurement_fetch_time_utc datetime, 
  series_id int,
  location_id int,
  location_name varchar(255),
  latitude decimal(8,6),
  longitude decimal(9,6),
  parameter_name varchar(255),
  parameter_value double,
  num_measurements int,
  reference_value_lower double null,
  reference_value_upper double null,
  reference_color varchar(255)  
);

drop table if exists openaq.irceline_measurements_current;
CREATE TABLE openaq.irceline_measurements_current (
  measurement_fetch_time_utc datetime, 
  series_id int,
  location_id int,
  location_name varchar(255),
  latitude decimal(8,6),
  longitude decimal(9,6),
  parameter_name varchar(255),
  parameter_value double,
  num_measurements int,
  reference_value_lower double null,
  reference_value_upper double null,
  reference_color varchar(255)  
);

drop table if exists openaq.irceline_sensor_metadata;
CREATE TABLE openaq.irceline_sensor_metadata (
  series_id int,
  location_id int,
  location_name varchar(255),
  latitude decimal(8,6),
  longitude decimal(9,6),
  parameter_name varchar(255),
  reference_value_lower double null,
  reference_value_upper double null,
  reference_color varchar(255)  
);