## Realtime monitoring of Belgian air quality using data of OpenAQ

This repository contains several components created when investigating the feasibility of using data of OpenAQ for monitoring the Belgian air quality in realtime.

## Components

- Data flows:
  - [Processing of the OpenAQ data using MariaDB](batch-processing/)
  - [Processing of the OpenAQ data using AWS Kinesis](streaming/)
  - [Ingestion of the OpenAQ data into MariaDB and Kinesis](lambda-ingestion)
- Analyses:
  - [Analysis of the ingested data using R](data-analysis/)
- POC application:
  - [Streamilt application showing realtime air quality using data of IRCELINE](streamlit/)

## Getting started

See the readme files in the subdirectories for instructions to set up your development environment for each of the components.

