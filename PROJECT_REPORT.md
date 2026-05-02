# Flight Trajectory Analytics Project Report

This report documents what was built in this project, how the project is organized, and how another student or recruiter can recreate the work from scratch.

## 1. Project Overview

The project analyzes aircraft trajectory data around Hartsfield-Jackson Atlanta International Airport (ATL). It started as a final course project for Data Analysis and Visualization and was later upgraded into a portfolio-ready data analyst project.

The project uses OpenSky-style aircraft state-vector data to:

- Clean and profile large flight telemetry CSV files.
- Analyze missing values, data types, traffic volume, aircraft/callsign frequency, and abnormal flight behavior.
- Detect suspicious trajectories using velocity, vertical-rate, altitude, and squawk-code rules.
- Visualize normal and abnormal flight paths.
- Compare RNN, LSTM, and GRU models for short-term trajectory prediction.
- Add SQL analysis and a Streamlit dashboard so the project demonstrates practical data analyst skills.

## 2. Dataset

The local dataset is stored in `dataset/`.

| File | Rows | Purpose |
| --- | ---: | --- |
| `combined_csv_data.csv` | 23,530,652 | Raw combined aircraft state-vector data |
| `new_df.csv` | 8,952,853 | Cleaned normal-flight dataset |
| `df_anormaly_flights.csv` | 6,361 | Abnormal-flight records |
| `anormal_flights.csv` | 1,836 | Selected abnormal trajectories |

Important columns:

- `time`: Unix timestamp.
- `icao24`: unique aircraft transponder address.
- `callsign`: aircraft callsign or registration.
- `lat`, `lon`: aircraft position.
- `velocity`: ground speed.
- `heading`: direction of travel.
- `vertrate`: vertical rate.
- `squawk`: transponder code.
- `baroaltitude`, `geoaltitude`: altitude values.

Special squawk codes:

- `7500`: hijacking or unlawful interference.
- `7600`: radio communication failure.
- `7700`: general emergency.

## 3. Final Project Structure

```text
.
|-- dashboard/
|   `-- app.py
|-- dataset/
|   |-- README.md
|   |-- combined_csv_data.csv
|   |-- new_df.csv
|   |-- df_anormaly_flights.csv
|   `-- anormal_flights.csv
|-- reports/
|   `-- data_profile.md
|-- source/
|   |-- EDA-and-PreProcessing.ipynb
|   |-- model_normal.ipynb
|   |-- model_anormal-OPT366.ipynb
|   `-- model_anormal-N550AA.ipynb
|-- sql/
|   |-- 00_create_views.sql
|   |-- 01_data_quality.sql
|   |-- 02_traffic_analysis.sql
|   `-- 03_anomaly_detection.sql
|-- src/
|   |-- prepare_duckdb.py
|   `-- data_profile.py
|-- README.md
|-- PROJECT_REPORT.md
|-- requirements.txt
|-- requirements-ml.txt
`-- run_dashboard.ps1
```

## 4. What Was Done

### 4.1 Original Notebook Work

The original course work is inside `source/`.

`EDA-and-PreProcessing.ipynb`:

- Loaded raw flight CSV data.
- Checked data types and mixed-type columns.
- Standardized boolean and numeric columns.
- Measured missing values.
- Removed records without useful flight identifiers.
- Investigated missing `squawk` values.
- Created correlation matrices and boxplots.
- Detected suspicious flights using outlier rules.
- Visualized flight paths in 2D and 3D.

`model_normal.ipynb`:

- Loaded the cleaned normal-flight dataset.
- Segmented flights using time gaps greater than 30 seconds.
- Selected a representative normal flight.
- Scaled trajectory features.
- Converted the trajectory into time-window sequences.
- Trained RNN, LSTM, and GRU models.
- Predicted future `lat`, `lon`, and `geoaltitude`.
- Compared model errors.

`model_anormal-OPT366.ipynb` and `model_anormal-N550AA.ipynb`:

- Loaded abnormal-flight data.
- Selected abnormal/emergency-related flights.
- Repeated sequence modeling with RNN, LSTM, and GRU.
- Compared predicted and actual abnormal trajectories.

### 4.2 Portfolio Upgrade Work

The project was upgraded to make it stronger for a data analyst CV.

Added documentation:

- `README.md`: high-level project summary, dataset description, stack, commands, and portfolio highlights.
- `dataset/README.md`: explains why full CSV files should not be committed to GitHub.
- `PROJECT_REPORT.md`: this detailed implementation report.

Added SQL layer:

- `sql/00_create_views.sql`: creates DuckDB views over the CSV files.
- `sql/01_data_quality.sql`: checks row counts, missing values, numeric ranges, and duplicates.
- `sql/02_traffic_analysis.sql`: analyzes traffic volume, top aircraft, flight segments, and altitude changes.
- `sql/03_anomaly_detection.sql`: detects emergency squawk codes and suspicious movement patterns.

Added Python utilities:

- `src/prepare_duckdb.py`: creates `flight_analytics.duckdb` with reusable views over the CSV files.
- `src/data_profile.py`: generates `reports/data_profile.md` from DuckDB queries.

Added dashboard:

- `dashboard/app.py`: Streamlit dashboard with traffic overview, abnormal flight summary, and trajectory explorer.
- `run_dashboard.ps1`: Windows launcher for the dashboard.

Improved dependency setup:

- `requirements.txt`: core data analyst dependencies.
- `requirements-ml.txt`: optional deep learning dependencies for rerunning the model notebooks.

## 5. How To Build This Project From Scratch

### Step 1: Create The Folder

```powershell
mkdir flight-trajectory-analysis
cd flight-trajectory-analysis
```

Create folders:

```powershell
mkdir dataset source sql src dashboard reports
```

### Step 2: Add The Dataset

Place the CSV files in `dataset/`:

```text
dataset/combined_csv_data.csv
dataset/new_df.csv
dataset/df_anormaly_flights.csv
dataset/anormal_flights.csv
```

If publishing to GitHub, do not commit the large CSV files. Keep only `dataset/README.md` or a small sample dataset.

### Step 3: Create The Python Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For this machine, Anaconda was also used because it already had `pandas`, `streamlit`, and `plotly`. DuckDB was installed into Anaconda with:

```powershell
C:\Users\quynh\anaconda3\python.exe -m pip install duckdb
```

### Step 4: Create DuckDB Views

Use `src/prepare_duckdb.py`.

Main idea:

```python
import duckdb

connection = duckdb.connect("flight_analytics.duckdb")
connection.execute("""
CREATE OR REPLACE VIEW normal_flight_states AS
SELECT *
FROM read_csv_auto('dataset/new_df.csv', ignore_errors = true)
""")
```

In the project, the script creates views for:

- `raw_flight_states`
- `normal_flight_states`
- `abnormal_flight_states`
- `abnormal_selected_flights`
- `normal_flight_enriched`
- `abnormal_flight_enriched`

Run:

```powershell
python src\prepare_duckdb.py --db flight_analytics.duckdb
```

### Step 5: Write SQL Data Quality Queries

Create `sql/01_data_quality.sql`.

Useful checks:

- Count rows by table.
- Count missing values by column.
- Check minimum and maximum values.
- Detect duplicate records.

Example:

```sql
SELECT
    count(*) AS total_rows,
    sum(CASE WHEN callsign IS NULL OR trim(CAST(callsign AS VARCHAR)) = '' THEN 1 ELSE 0 END) AS missing_callsign,
    sum(CASE WHEN lat IS NULL THEN 1 ELSE 0 END) AS missing_lat,
    sum(CASE WHEN lon IS NULL THEN 1 ELSE 0 END) AS missing_lon
FROM normal_flight_states;
```

### Step 6: Write SQL Traffic Analysis Queries

Create `sql/02_traffic_analysis.sql`.

Important analysis:

- Hourly traffic volume.
- Top aircraft/callsign pairs.
- Flight segmentation using time gaps.
- Altitude-change analysis.

Flight segmentation logic:

```sql
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
        ) AS flight_segment_id
    FROM ordered
)
SELECT *
FROM segmented;
```

This demonstrates SQL window functions, which are important for data analyst roles.

### Step 7: Write SQL Anomaly Detection Queries

Create `sql/03_anomaly_detection.sql`.

Detect emergency squawk codes:

```sql
SELECT
    try_cast(squawk AS INTEGER) AS squawk_code,
    count(*) AS observations,
    count(DISTINCT icao24) AS unique_aircraft
FROM normal_flight_states
WHERE try_cast(squawk AS INTEGER) IN (7500, 7600, 7700)
GROUP BY squawk_code;
```

Detect suspicious movement:

- very high velocity,
- very large vertical rate,
- large altitude changes,
- large position jumps.

### Step 8: Generate A Markdown Data Profile

Use `src/data_profile.py`.

The script:

- connects to DuckDB,
- runs summary queries,
- converts query results to markdown tables,
- writes `reports/data_profile.md`.

Run:

```powershell
python src\data_profile.py --db flight_analytics.duckdb --output reports\data_profile.md
```

Generated examples:

- row counts,
- missing-value summary,
- top aircraft/callsign pairs,
- abnormal selected flight summary.

### Step 9: Build The Dashboard

Create `dashboard/app.py` with Streamlit.

Main dashboard sections:

- `Traffic Overview`: top aircraft/callsign pairs and observation counts.
- `Abnormal Flights`: summary of suspicious flights.
- `Trajectory Explorer`: map and time-series charts for selected abnormal flights.

Important implementation detail:

```python
db_ready = DB_PATH.exists() and DB_PATH.stat().st_size > 0
connection = duckdb.connect(str(DB_PATH), read_only=db_ready)
```

The dashboard opens the existing DuckDB database in read-only mode. This avoids database locking while other scripts read the same database.

Run:

```powershell
streamlit run dashboard\app.py
```

Or on this Windows setup:

```powershell
.\run_dashboard.ps1
```

### Step 10: Add Documentation

Write a strong `README.md` with:

- project goal,
- dataset description,
- repository structure,
- technical stack,
- commands to run,
- notebook summary,
- portfolio highlights,
- CV bullet.

Add `.gitignore` to avoid committing:

- `.venv/`,
- `__pycache__/`,
- large CSV files,
- DuckDB database files,
- generated reports.

## 6. How The Main Code Works

### `src/prepare_duckdb.py`

Purpose: create reusable DuckDB views over CSV files.

Key functions:

- `sql_path(path)`: converts Windows paths into DuckDB-safe paths.
- `create_views(connection)`: creates views for raw, normal, abnormal, and enriched data.
- `main()`: parses CLI arguments and writes the database.

Why DuckDB:

- It can query large CSV files directly.
- It supports SQL window functions.
- It is easier than loading 23M+ rows into pandas.
- It is good for a portfolio because it shows SQL skill on real data.

### `src/data_profile.py`

Purpose: generate a readable markdown report from SQL queries.

Key functions:

- `fetch_markdown_table()`: runs a query and formats the result as a markdown table.
- `generate_profile()`: defines all profiling sections.
- `main()`: writes the final report file.

### `dashboard/app.py`

Purpose: provide an interactive dashboard.

Main techniques:

- `st.cache_resource`: caches the DuckDB connection.
- `st.cache_data`: caches query results.
- `st.tabs`: separates dashboard pages.
- Plotly charts for bar charts, scatter charts, map lines, and time-series charts.

Dashboard pages:

- traffic summary,
- abnormal-flight summary,
- trajectory explorer.

## 7. Current Verified Results

The project was run successfully with:

```powershell
python src\prepare_duckdb.py --db flight_analytics.duckdb
python src\data_profile.py --db flight_analytics.duckdb --output reports\data_profile.md
.\run_dashboard.ps1
```

Verified outputs:

- DuckDB database created successfully.
- `reports/data_profile.md` generated successfully.
- Streamlit dashboard started successfully.
- Dashboard available at `http://localhost:8501`.
- Streamlit health check returned `200 ok`.

Some profile results:

- raw states: 23,530,652 rows,
- normal states: 8,952,853 rows,
- abnormal states: 6,361 rows,
- selected abnormal states: 1,836 rows.

Top abnormal selected callsigns by observations:

- `N739E`: 435 observations,
- `N550AA`: 397 observations,
- `OPT366`: 345 observations.

## 8. Recommended Future Improvements

To make the project stronger:

- Add screenshots of the Streamlit dashboard to `README.md`.
- Add a small sample dataset for GitHub users.
- Add model evaluation tables with MAE/RMSE in real-world units.
- Convert notebooks into cleaner Python training scripts.
- Add tests for SQL query outputs and Python utilities.
- Add a Power BI or Tableau version for data analyst applications.
- Add geospatial distance features such as Haversine distance.
- Add flight phase detection: takeoff, cruise, landing.

## 9. CV Section

LaTeX resume section:

```latex
\resumeProjectHeading
{\textbf{Flight Trajectory Analytics and Prediction} $|$ \emph{Python, SQL, DuckDB, Streamlit, Plotly, scikit-learn, Keras}} {}
\resumeItemListStart
    \resumeItem{Processed and profiled 23M+ OpenSky-style aircraft state-vector records using Python and DuckDB SQL, identifying missing values, abnormal squawk codes, and suspicious flight movement patterns.}
    \resumeItem{Developed SQL analytics queries with aggregations and window functions to analyze traffic volume, segment flight trajectories, rank aircraft/callsign activity, and detect abnormal altitude or velocity changes.}
    \resumeItem{Built a Streamlit and Plotly dashboard to visualize traffic summaries, abnormal flights, trajectory maps, and altitude/velocity trends for selected aircraft.}
    \resumeItem{Compared RNN, LSTM, and GRU sequence models for short-term flight trajectory prediction of latitude, longitude, and altitude.}
\resumeItemListEnd
```

