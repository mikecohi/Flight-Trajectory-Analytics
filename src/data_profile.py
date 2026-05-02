"""Generate a compact markdown data profile from the DuckDB views."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def fetch_markdown_table(
    connection: duckdb.DuckDBPyConnection, query: str, limit: int | None = None
) -> str:
    if limit is not None:
        query = f"SELECT * FROM ({query}) AS q LIMIT {limit}"
    result = connection.execute(query)
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()

    if not rows:
        return "_No rows returned._\n"

    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join("" if value is None else str(value) for value in row) + " |")
    return "\n".join([header, separator, *body]) + "\n"


def generate_profile(connection: duckdb.DuckDBPyConnection) -> str:
    sections = [
        "# Flight Dataset Profile",
        "",
        "Generated from the local DuckDB views.",
        "",
        "## Row Counts",
        fetch_markdown_table(
            connection,
            """
            SELECT 'raw_flight_states' AS table_name, count(*) AS row_count FROM raw_flight_states
            UNION ALL
            SELECT 'normal_flight_states', count(*) FROM normal_flight_states
            UNION ALL
            SELECT 'abnormal_flight_states', count(*) FROM abnormal_flight_states
            UNION ALL
            SELECT 'abnormal_selected_flights', count(*) FROM abnormal_selected_flights
            """,
        ),
        "## Missing Values In Normal Flight Data",
        fetch_markdown_table(
            connection,
            """
            SELECT
                count(*) AS total_rows,
                sum(CASE WHEN callsign IS NULL OR trim(CAST(callsign AS VARCHAR)) = '' THEN 1 ELSE 0 END) AS missing_callsign,
                sum(CASE WHEN lat IS NULL THEN 1 ELSE 0 END) AS missing_lat,
                sum(CASE WHEN lon IS NULL THEN 1 ELSE 0 END) AS missing_lon,
                sum(CASE WHEN velocity IS NULL THEN 1 ELSE 0 END) AS missing_velocity,
                sum(CASE WHEN heading IS NULL THEN 1 ELSE 0 END) AS missing_heading,
                sum(CASE WHEN vertrate IS NULL THEN 1 ELSE 0 END) AS missing_vertical_rate,
                sum(CASE WHEN squawk IS NULL OR trim(CAST(squawk AS VARCHAR)) = '' THEN 1 ELSE 0 END) AS missing_squawk,
                sum(CASE WHEN geoaltitude IS NULL THEN 1 ELSE 0 END) AS missing_geoaltitude
            FROM normal_flight_states
            """,
        ),
        "## Top Aircraft/Callsign Pairs",
        fetch_markdown_table(
            connection,
            """
            SELECT
                icao24,
                callsign,
                count(*) AS observations,
                round(avg(velocity), 2) AS avg_velocity,
                round(avg(geoaltitude), 2) AS avg_geoaltitude
            FROM normal_flight_states
            GROUP BY icao24, callsign
            ORDER BY observations DESC
            """,
            limit=10,
        ),
        "## Abnormal Selected Flights",
        fetch_markdown_table(
            connection,
            """
            SELECT
                icao24,
                callsign,
                flight,
                count(*) AS observations,
                max("time") - min("time") AS duration_seconds,
                round(avg(velocity), 2) AS avg_velocity,
                round(max(velocity), 2) AS max_velocity,
                round(min(geoaltitude), 2) AS min_geoaltitude,
                round(max(geoaltitude), 2) AS max_geoaltitude
            FROM abnormal_selected_flights
            GROUP BY icao24, callsign, flight
            ORDER BY observations DESC
            """,
            limit=20,
        ),
    ]
    return "\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a markdown data profile.")
    parser.add_argument(
        "--db",
        default=str(PROJECT_ROOT / "flight_analytics.duckdb"),
        help="DuckDB database created by src/prepare_duckdb.py.",
    )
    parser.add_argument(
        "--output",
        default=str(PROJECT_ROOT / "reports" / "data_profile.md"),
        help="Markdown output path.",
    )
    args = parser.parse_args()

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(Path(args.db).resolve()), read_only=True) as connection:
        profile = generate_profile(connection)

    output_path.write_text(profile, encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
