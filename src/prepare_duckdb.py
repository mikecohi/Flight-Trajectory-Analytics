"""Create DuckDB views for the flight trajectory analytics project."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "dataset"


def sql_path(path: Path) -> str:
    """Return a DuckDB-safe path literal."""
    return str(path).replace("\\", "/").replace("'", "''")


def create_views(connection: duckdb.DuckDBPyConnection) -> None:
    files = {
        "raw_flight_states": DATASET_DIR / "combined_csv_data.csv",
        "normal_flight_states": DATASET_DIR / "new_df.csv",
        "abnormal_flight_states": DATASET_DIR / "df_anormaly_flights.csv",
        "abnormal_selected_flights": DATASET_DIR / "anormal_flights.csv",
    }

    for table_name, file_path in files.items():
        if not file_path.exists():
            raise FileNotFoundError(f"Missing expected dataset: {file_path}")
        connection.execute(
            f"""
            CREATE OR REPLACE VIEW {table_name} AS
            SELECT *
            FROM read_csv_auto('{sql_path(file_path)}', ignore_errors = true)
            """
        )

    connection.execute(
        """
        CREATE OR REPLACE VIEW normal_flight_enriched AS
        SELECT
            *,
            to_timestamp("time") AS event_ts,
            date_trunc('hour', to_timestamp("time")) AS event_hour,
            date_trunc('day', to_timestamp("time")) AS event_day
        FROM normal_flight_states
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE VIEW abnormal_flight_enriched AS
        SELECT
            *,
            to_timestamp("time") AS event_ts,
            date_trunc('hour', to_timestamp("time")) AS event_hour,
            date_trunc('day', to_timestamp("time")) AS event_day
        FROM abnormal_flight_states
        """
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a DuckDB database with views over local flight CSV files."
    )
    parser.add_argument(
        "--db",
        default=str(PROJECT_ROOT / "flight_analytics.duckdb"),
        help="Output DuckDB database path.",
    )
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(db_path)) as connection:
        create_views(connection)
        tables = connection.execute("SHOW TABLES").fetchall()

    print(f"Created DuckDB views in {db_path}")
    print("Available tables/views:")
    for (table_name,) in tables:
        print(f"- {table_name}")


if __name__ == "__main__":
    main()
