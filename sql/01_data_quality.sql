-- Data quality checks for aircraft state-vector data.
-- Run after sql/00_create_views.sql or after src/prepare_duckdb.py.

-- Row counts by table.
SELECT 'raw_flight_states' AS table_name, count(*) AS row_count FROM raw_flight_states
UNION ALL
SELECT 'normal_flight_states', count(*) FROM normal_flight_states
UNION ALL
SELECT 'abnormal_flight_states', count(*) FROM abnormal_flight_states
UNION ALL
SELECT 'abnormal_selected_flights', count(*) FROM abnormal_selected_flights;

-- Missing-value profile for key analysis fields.
SELECT
    count(*) AS total_rows,
    sum(CASE WHEN icao24 IS NULL OR trim(CAST(icao24 AS VARCHAR)) = '' THEN 1 ELSE 0 END) AS missing_icao24,
    sum(CASE WHEN callsign IS NULL OR trim(CAST(callsign AS VARCHAR)) = '' THEN 1 ELSE 0 END) AS missing_callsign,
    sum(CASE WHEN lat IS NULL THEN 1 ELSE 0 END) AS missing_lat,
    sum(CASE WHEN lon IS NULL THEN 1 ELSE 0 END) AS missing_lon,
    sum(CASE WHEN velocity IS NULL THEN 1 ELSE 0 END) AS missing_velocity,
    sum(CASE WHEN heading IS NULL THEN 1 ELSE 0 END) AS missing_heading,
    sum(CASE WHEN vertrate IS NULL THEN 1 ELSE 0 END) AS missing_vertical_rate,
    sum(CASE WHEN squawk IS NULL OR trim(CAST(squawk AS VARCHAR)) = '' THEN 1 ELSE 0 END) AS missing_squawk,
    sum(CASE WHEN baroaltitude IS NULL THEN 1 ELSE 0 END) AS missing_baroaltitude,
    sum(CASE WHEN geoaltitude IS NULL THEN 1 ELSE 0 END) AS missing_geoaltitude
FROM normal_flight_states;

-- Basic numeric ranges for sanity checking.
SELECT
    min(lat) AS min_lat,
    max(lat) AS max_lat,
    min(lon) AS min_lon,
    max(lon) AS max_lon,
    min(velocity) AS min_velocity,
    max(velocity) AS max_velocity,
    min(vertrate) AS min_vertical_rate,
    max(vertrate) AS max_vertical_rate,
    min(baroaltitude) AS min_baroaltitude,
    max(baroaltitude) AS max_baroaltitude,
    min(geoaltitude) AS min_geoaltitude,
    max(geoaltitude) AS max_geoaltitude
FROM normal_flight_states;

-- Duplicate check at the aircraft-time-position grain.
SELECT
    icao24,
    callsign,
    "time",
    lat,
    lon,
    count(*) AS duplicate_count
FROM normal_flight_states
GROUP BY icao24, callsign, "time", lat, lon
HAVING count(*) > 1
ORDER BY duplicate_count DESC
LIMIT 50;
