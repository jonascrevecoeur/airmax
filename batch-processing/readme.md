# Batch processing

These files explore the feasibility of processing the OpenAQ data in batches in a MariaDB database for monitoring the current air quality in Belgian cities.

## Setting up your development environment
To get this project up and running, make sure you have the following installed:
* Python 3
* PIP
* Docker (for local testing)

Create a virtual environment for this project. You can run this command in the terminal from the current folder `batch-processing` to install the required packages.
```
pip install -r requirements.txt
```

## Setting up your local test database
New features can be tested on a local database running as a docker container. 

Run the following command in this folder to create or start your database
```
docker-compose up
```

This will setup:

- MariaDB database on port 3306
- Adminer on port 8080

The first time you create the database, the scripts in the directory `queries/initialization/` are run in alphabetical order to initialize the database.  

To reset the database and test new initialization scripts add the option `-V`
```
docker-compose up -V
```
This recreates volumes used by the containers.

Connect to the database locally by logging in using adminer on
```
http://localhost:8080
```
with:

- host: db
- user: root
- password: password
- database: openaq

## Generating streaming test data





