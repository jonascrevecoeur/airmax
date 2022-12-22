# Lambda ingestion

This lambda function ingests OpenAQ measurements from SQS into a MariaDB database and a Kinesis Data Stream. This design is only intended for initial testing and development as pushing to two destinations using a single lambda function can result in duplicate entries in the first destination stream as the second one encounters an error.

## Environmental variables

This lambda function depends on the following environmental variables:

- DB_HOSTNAME: Host address of the MariaDB database
- DB_PASSWORD: Password of the MariaDB database - TODO: Move this to a secret in the Secrets Manager
- DB_USERNAME: Role of the user profile for the MariaDB database
- stream_name: Name of Amazon Kinesis Data Stream to which the data is pushed
- send_to_kinesis: boolean - indicates whether data should be send to kinesis
- send_to_mariadb: boolean - indicates whether data should be send to MariaDB