# Flight Trajectory Analysis and Prediction

Portfolio version of a final project for a Data Analysis and Visualization course. The project analyzes aircraft state-vector data around Hartsfield-Jackson Atlanta International Airport (ATL), identifies abnormal trajectories, and compares sequence models for short-term flight trajectory prediction.

## Project Goal

Air traffic systems need reliable short-term trajectory information to monitor aircraft movement, detect abnormal behavior, and support safer airspace operations. This project uses historical flight data to:

- Clean and profile large aircraft telemetry datasets.
- Explore traffic patterns, missing data, altitude/velocity distributions, and abnormal squawk codes.
- Segment raw state vectors into flight trajectories.
- Visualize normal and suspicious flights in 2D and 3D.
- Train RNN, LSTM, and GRU models to predict latitude, longitude, and altitude.

## Dataset

The data follows the OpenSky state-vector format and contains observations around ATL airport.

| File | Rows | Description |
| --- | ---: | --- |
| `dataset/combined_csv_data.csv` | 23,530,652 | Raw combined state-vector data |
| `dataset/new_df.csv` | 8,952,853 | Cleaned normal-flight dataset |
| `dataset/df_anormaly_flights.csv` | 6,361 | Abnormal-flight dataset |
| `dataset/anormal_flights.csv` | 1,836 | Selected abnormal flight trajectories |

Main fields include `time`, `icao24`, `callsign`, `lat`, `lon`, `velocity`, `heading`, `vertrate`, `squawk`, `baroaltitude`, and `geoaltitude`.

## Repository Structure

```text
.
|-- dashboard/                 # Streamlit dashboard for portfolio demo
|-- dataset/                   # Local CSV datasets
|-- reports/                   # Generated markdown/data reports
|-- source/                    # Original course notebooks
|-- sql/                       # SQL analytics queries using DuckDB
|-- src/                       # Reproducible Python utilities
`-- requirements.txt
```

## Technical Stack

- Python: pandas, NumPy, scikit-learn, Keras/TensorFlow
- SQL: DuckDB analytical queries over large CSV files
- Visualization: Matplotlib, Seaborn, Plotly, Streamlit
- Machine learning: RNN, LSTM, GRU sequence models

## Key Analysis Questions

- How complete and reliable are the aircraft state-vector records?
- Which aircraft or callsigns dominate the dataset?
- How does traffic volume vary by hour, day, and flight segment?
- Which flights contain abnormal squawk codes such as `7500`, `7600`, or `7700`?
- Which trajectories have unusual velocity, vertical-rate, or altitude-change behavior?
- How accurately can sequence models predict future position and altitude?

## How To Run

Create an environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The original deep learning notebooks need heavier optional packages:

```powershell
pip install -r requirements-ml.txt
```

Create a DuckDB database from the CSV files:

```powershell
python src\prepare_duckdb.py --db flight_analytics.duckdb
```

Run SQL analysis from the project root:

```powershell
duckdb flight_analytics.duckdb -init sql\01_data_quality.sql
duckdb flight_analytics.duckdb -init sql\02_traffic_analysis.sql
duckdb flight_analytics.duckdb -init sql\03_anomaly_detection.sql
```

Generate a compact markdown profile:

```powershell
python src\data_profile.py --db flight_analytics.duckdb --output reports\data_profile.md
```

Launch the dashboard:

```powershell
streamlit run dashboard\app.py
```

On this Windows machine, the project also includes a convenience launcher:

```powershell
.\run_dashboard.ps1
```

## Notebook Summary

- `source/EDA-and-PreProcessing.ipynb`: data type normalization, missing-value analysis, null handling, correlation matrix, boxplots, abnormal flight detection, and trajectory visualization.
- `source/model_normal.ipynb`: sequence modeling for a normal flight using RNN, LSTM, and GRU.
- `source/model_anormal-OPT366.ipynb`: sequence modeling for an abnormal flight associated with squawk `7600`.
- `source/model_anormal-N550AA.ipynb`: sequence modeling for an abnormal flight associated with squawk `7500`.


## Portfolio Highlights

- Processed and profiled 23M+ aircraft telemetry records.
- Used SQL window functions to detect time gaps, velocity changes, altitude changes, and abnormal squawk events.
- Built Python preprocessing and visualization notebooks for aviation trajectory analysis.
- Compared RNN, LSTM, and GRU models for short-term trajectory forecasting.
- Added a reproducible SQL/Python workflow and Streamlit dashboard for recruiter review.

