-- Run from the project root.
-- This file creates reusable DuckDB views over the local CSV files.

CREATE OR REPLACE VIEW raw_flight_states AS
SELECT *
FROM read_csv_auto('dataset/combined_csv_data.csv', ignore_errors = true);

CREATE OR REPLACE VIEW normal_flight_states AS
SELECT *
FROM read_csv_auto('dataset/new_df.csv', ignore_errors = true);

CREATE OR REPLACE VIEW abnormal_flight_states AS
SELECT *
FROM read_csv_auto('dataset/df_anormaly_flights.csv', ignore_errors = true);

CREATE OR REPLACE VIEW abnormal_selected_flights AS
SELECT *
FROM read_csv_auto('dataset/anormal_flights.csv', ignore_errors = true);

CREATE OR REPLACE VIEW normal_flight_enriched AS
SELECT
    *,
    to_timestamp("time") AS event_ts,
    date_trunc('hour', to_timestamp("time")) AS event_hour,
    date_trunc('day', to_timestamp("time")) AS event_day
FROM normal_flight_states;

CREATE OR REPLACE VIEW abnormal_flight_enriched AS
SELECT
    *,
    to_timestamp("time") AS event_ts,
    date_trunc('hour', to_timestamp("time")) AS event_hour,
    date_trunc('day', to_timestamp("time")) AS event_day
FROM abnormal_flight_states;
