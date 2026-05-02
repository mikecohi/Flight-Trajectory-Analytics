-- Traffic and flight behavior analysis.
-- These queries demonstrate aggregation, time bucketing, and window functions.

-- Hourly traffic volume.
SELECT
    event_hour,
    count(*) AS observations,
    count(DISTINCT icao24) AS unique_aircraft,
    count(DISTINCT callsign) AS unique_callsigns
FROM normal_flight_enriched
GROUP BY event_hour
ORDER BY event_hour;

-- Top aircraft/callsign pairs by observation count.
SELECT
    icao24,
    callsign,
    count(*) AS observations,
    min(event_ts) AS first_seen,
    max(event_ts) AS last_seen,
    round(avg(velocity), 2) AS avg_velocity,
    round(avg(geoaltitude), 2) AS avg_geoaltitude
FROM normal_flight_enriched
GROUP BY icao24, callsign
ORDER BY observations DESC
LIMIT 25;

-- Recreate flight segments using time gaps larger than 30 seconds.
WITH ordered AS (
    SELECT
        *,
        lag("time") OVER (
            PARTITION BY icao24, callsign
            ORDER BY "time"
        ) AS previous_time
    FROM normal_flight_enriched
),
segmented AS (
    SELECT
        *,
        sum(
            CASE
                WHEN previous_time IS NULL OR "time" - previous_time > 30 THEN 1
                ELSE 0
            END
        ) OVER (
            PARTITION BY icao24, callsign
            ORDER BY "time"
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS flight_segment_id
    FROM ordered
)
SELECT
    icao24,
    callsign,
    flight_segment_id,
    min(event_ts) AS segment_start,
    max(event_ts) AS segment_end,
    max("time") - min("time") AS duration_seconds,
    count(*) AS observations,
    round(avg(velocity), 2) AS avg_velocity,
    round(max(geoaltitude) - min(geoaltitude), 2) AS altitude_range
FROM segmented
GROUP BY icao24, callsign, flight_segment_id
HAVING count(*) >= 20
ORDER BY duration_seconds DESC
LIMIT 50;

-- Largest one-step altitude changes by aircraft.
WITH changes AS (
    SELECT
        icao24,
        callsign,
        event_ts,
        geoaltitude,
        geoaltitude - lag(geoaltitude) OVER (
            PARTITION BY icao24, callsign
            ORDER BY "time"
        ) AS altitude_change
    FROM normal_flight_enriched
    WHERE geoaltitude IS NOT NULL
)
SELECT *
FROM changes
WHERE altitude_change IS NOT NULL
ORDER BY abs(altitude_change) DESC
LIMIT 50;
