-- Abnormal flight and emergency-code analysis.

-- Emergency/special squawk codes in normal data.
SELECT
    try_cast(squawk AS INTEGER) AS squawk_code,
    CASE try_cast(squawk AS INTEGER)
        WHEN 7500 THEN 'Hijacking or unlawful interference'
        WHEN 7600 THEN 'Radio communication failure'
        WHEN 7700 THEN 'General emergency'
        ELSE 'Other'
    END AS squawk_meaning,
    count(*) AS observations,
    count(DISTINCT icao24) AS unique_aircraft,
    count(DISTINCT callsign) AS unique_callsigns
FROM normal_flight_states
WHERE try_cast(squawk AS INTEGER) IN (7500, 7600, 7700)
GROUP BY squawk_code, squawk_meaning
ORDER BY observations DESC;

-- Abnormal selected flights summary.
SELECT
    icao24,
    callsign,
    flight,
    min(to_timestamp("time")) AS start_time,
    max(to_timestamp("time")) AS end_time,
    max("time") - min("time") AS duration_seconds,
    count(*) AS observations,
    round(avg(velocity), 2) AS avg_velocity,
    round(max(velocity), 2) AS max_velocity,
    round(min(vertrate), 2) AS min_vertical_rate,
    round(max(vertrate), 2) AS max_vertical_rate,
    round(min(geoaltitude), 2) AS min_geoaltitude,
    round(max(geoaltitude), 2) AS max_geoaltitude
FROM abnormal_selected_flights
GROUP BY icao24, callsign, flight
ORDER BY observations DESC;

-- Potential outliers based on velocity and vertical rate.
SELECT
    icao24,
    callsign,
    to_timestamp("time") AS event_ts,
    lat,
    lon,
    velocity,
    vertrate,
    geoaltitude,
    squawk
FROM normal_flight_states
WHERE velocity > 350
   OR vertrate < -50
   OR vertrate > 50
ORDER BY abs(coalesce(vertrate, 0)) DESC, velocity DESC
LIMIT 100;

-- Consecutive-point movement flags using window functions.
WITH movement AS (
    SELECT
        icao24,
        callsign,
        "time",
        to_timestamp("time") AS event_ts,
        lat,
        lon,
        velocity,
        geoaltitude,
        lat - lag(lat) OVER (
            PARTITION BY icao24, callsign
            ORDER BY "time"
        ) AS lat_delta,
        lon - lag(lon) OVER (
            PARTITION BY icao24, callsign
            ORDER BY "time"
        ) AS lon_delta,
        velocity - lag(velocity) OVER (
            PARTITION BY icao24, callsign
            ORDER BY "time"
        ) AS velocity_delta,
        geoaltitude - lag(geoaltitude) OVER (
            PARTITION BY icao24, callsign
            ORDER BY "time"
        ) AS altitude_delta
    FROM normal_flight_states
)
SELECT *
FROM movement
WHERE abs(coalesce(velocity_delta, 0)) > 100
   OR abs(coalesce(altitude_delta, 0)) > 1000
   OR abs(coalesce(lat_delta, 0)) > 0.2
   OR abs(coalesce(lon_delta, 0)) > 0.2
ORDER BY abs(coalesce(velocity_delta, 0)) DESC, abs(coalesce(altitude_delta, 0)) DESC
LIMIT 100;
