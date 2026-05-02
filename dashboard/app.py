"""Streamlit dashboard for flight trajectory analysis."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "flight_analytics.duckdb"
DATASET_DIR = PROJECT_ROOT / "dataset"


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    db_ready = DB_PATH.exists() and DB_PATH.stat().st_size > 0
    connection = duckdb.connect(str(DB_PATH), read_only=db_ready)
    if not db_ready:
        create_inline_views(connection)
    return connection


def sql_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def create_inline_views(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(
        f"""
        CREATE OR REPLACE VIEW normal_flight_states AS
        SELECT *
        FROM read_csv_auto('{sql_path(DATASET_DIR / "new_df.csv")}', ignore_errors = true)
        """
    )
    connection.execute(
        f"""
        CREATE OR REPLACE VIEW abnormal_selected_flights AS
        SELECT *
        FROM read_csv_auto('{sql_path(DATASET_DIR / "anormal_flights.csv")}', ignore_errors = true)
        """
    )


@st.cache_data(show_spinner=False)
def query_df(query: str) -> pd.DataFrame:
    return get_connection().execute(query).fetchdf()


st.set_page_config(page_title="Flight Trajectory Analytics", layout="wide")
st.title("Flight Trajectory Analytics")

st.caption(
    "Portfolio dashboard for aircraft state-vector profiling, abnormal flight review, "
    "and trajectory exploration."
)

counts = query_df(
    """
    SELECT 'Normal states' AS metric, count(*) AS value FROM normal_flight_states
    UNION ALL
    SELECT 'Abnormal selected states', count(*) FROM abnormal_selected_flights
    UNION ALL
    SELECT 'Normal aircraft', count(DISTINCT icao24) FROM normal_flight_states
    UNION ALL
    SELECT 'Normal callsigns', count(DISTINCT callsign) FROM normal_flight_states
    """
)

metric_cols = st.columns(len(counts))
for col, (_, row) in zip(metric_cols, counts.iterrows()):
    col.metric(row["metric"], f"{int(row['value']):,}")

tab_overview, tab_abnormal, tab_trajectory = st.tabs(
    ["Traffic Overview", "Abnormal Flights", "Trajectory Explorer"]
)

with tab_overview:
    st.subheader("Top Aircraft/Callsign Pairs")
    top_pairs = query_df(
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
        LIMIT 25
        """
    )
    st.dataframe(top_pairs, use_container_width=True, hide_index=True)

    fig = px.bar(
        top_pairs.head(15),
        x="callsign",
        y="observations",
        color="avg_geoaltitude",
        labels={"avg_geoaltitude": "Avg altitude"},
        title="Most Frequent Callsigns",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_abnormal:
    st.subheader("Selected Abnormal Flight Summary")
    abnormal_summary = query_df(
        """
        SELECT
            icao24,
            callsign,
            flight,
            count(*) AS observations,
            max("time") - min("time") AS duration_seconds,
            round(avg(velocity), 2) AS avg_velocity,
            round(max(velocity), 2) AS max_velocity,
            round(min(vertrate), 2) AS min_vertical_rate,
            round(max(vertrate), 2) AS max_vertical_rate,
            round(min(geoaltitude), 2) AS min_geoaltitude,
            round(max(geoaltitude), 2) AS max_geoaltitude
        FROM abnormal_selected_flights
        GROUP BY icao24, callsign, flight
        ORDER BY observations DESC
        """
    )
    st.dataframe(abnormal_summary, use_container_width=True, hide_index=True)

    fig = px.scatter(
        abnormal_summary,
        x="duration_seconds",
        y="observations",
        color="callsign",
        size="max_velocity",
        hover_data=["icao24", "flight", "min_vertical_rate", "max_vertical_rate"],
        title="Abnormal Flight Duration vs Observation Count",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_trajectory:
    st.subheader("Trajectory Explorer")
    abnormal_options = query_df(
        """
        SELECT DISTINCT icao24, callsign, flight
        FROM abnormal_selected_flights
        ORDER BY callsign, flight
        """
    )
    abnormal_options["label"] = (
        abnormal_options["callsign"].astype(str)
        + " | "
        + abnormal_options["icao24"].astype(str)
        + " | flight "
        + abnormal_options["flight"].astype(str)
    )

    selected_label = st.selectbox("Abnormal flight", abnormal_options["label"])
    selected = abnormal_options.loc[abnormal_options["label"] == selected_label].iloc[0]

    trajectory = query_df(
        f"""
        SELECT
            "time",
            lat,
            lon,
            velocity,
            heading,
            vertrate,
            geoaltitude,
            squawk
        FROM abnormal_selected_flights
        WHERE CAST(icao24 AS VARCHAR) = '{str(selected["icao24"]).replace("'", "''")}'
          AND CAST(callsign AS VARCHAR) = '{str(selected["callsign"]).replace("'", "''")}'
          AND flight = {int(selected["flight"])}
        ORDER BY "time"
        """
    )

    map_fig = px.line_mapbox(
        trajectory,
        lat="lat",
        lon="lon",
        color_discrete_sequence=["#d62728"],
        zoom=8,
        height=520,
        hover_data=["velocity", "heading", "vertrate", "geoaltitude", "squawk"],
        title="Selected Abnormal Flight Path",
    )
    map_fig.update_layout(mapbox_style="open-street-map", margin={"r": 0, "t": 50, "l": 0, "b": 0})
    st.plotly_chart(map_fig, use_container_width=True)

    altitude_fig = px.line(
        trajectory,
        x="time",
        y=["geoaltitude", "velocity", "vertrate"],
        title="Altitude, Velocity, and Vertical Rate Over Time",
    )
    st.plotly_chart(altitude_fig, use_container_width=True)
