# HIAA Climate Data Pipeline

## Overview

This project implements a **production-oriented ETL pipeline** that extracts hourly climate observations for the **latest available full day** from the ECCC GeoMet API and loads them into an existing SQLite table.

The pipeline retrieves the complete set of hourly observations for a given day and performs the following steps:

1. **Extract** hourly climate observations for a specific date from the GeoMet API
2. **Transform** the data to match the schema of the target database
3. **Load** the processed records into the SQLite table `hiaa_geomet_hourly`

The solution is designed with production principles in mind: **automation, reproducibility, observability, and maintainability**.

---

## Project Structure

```
hiaa-climate-pipeline
│
├── config/
│   └── .env
│
├── db/
│   └── yhz_db.sqlite
│
├── logs/
│   └── pipeline.log.example
│
├── pipeline/
│   ├── __init__.py
│   ├── extract.py
│   ├── load.py
│   ├── transform.py
│   └── main.py
│
├── requirements.txt
├── run_pipeline.sh
├── Dockerfile
├── README.md
└── .gitignore
```

### Description

| Component              | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| `extract.py`           | Fetch data from the GeoMet API             |
| `transform.py`         | Normalize API response to database schema  |
| `load.py`              | Insert records into SQLite                 |
| `main.py`              | Pipeline orchestration                     |
| `run_pipeline.sh`      | Automation wrapper for scheduled execution |
| `.env`                 | Runtime configuration                      |
| `pipeline.log.example` | Example log output                         |

---

## API Analysis and Design Decisions

The pipeline extracts data from the GeoMet hourly climate API:

```
https://api.weather.gc.ca/collections/climate-hourly/items
```

During development the API behavior was analyzed using manual testing tools such as Postman.

Several design decisions were made to ensure reliable and predictable extraction.

---

### Explicit Query Parameters

Although the API provides default values for some parameters, explicit values are used to avoid dependency on undocumented or changing defaults.

| Parameter                    | Purpose                                                                    |
| ---------------------------- | -------------------------------------------------------------------------- |
| `CLIMATE_IDENTIFIER=8202251` | Halifax Stanfield International Airport station                            |
| `LOCAL_DATE`                 | Retrieve observations for a specific day based on the station's local time |
| `limit=30`                   | Maximum records returned                                                   |
| `f=json`                     | JSON response format                                                       |
| `skipGeometry=true`          | Reduce unnecessary geometry payload                                        |

Example request:

```
https://api.weather.gc.ca/collections/climate-hourly/items
?f=json
&CLIMATE_IDENTIFIER=8202251
&LOCAL_DATE=YYYY-MM-DD
&limit=30
&skipGeometry=true
```

A day contains **24 hourly observations**, therefore `limit=30` safely guarantees all daily records are returned in a single request.

---

### LOCAL_DATE vs UTC_DATE

The GeoMet API supports filtering observations using `LOCAL_DATE` or `UTC_DATE`.

During testing it was observed that using `UTC_DATE` returns observations for a **24-hour UTC window** rather than a single local calendar day for the station.

For example, querying:

```
UTC_DATE = 2026-03-07
```

returns observations covering:

```
2026-03-07 00:00 UTC → 2026-03-07 23:00 UTC
```

For the Halifax station (Atlantic Time), this corresponds approximately to:

```
2026-03-06 20:00 local → 2026-03-07 19:00 local
```

This means the dataset spans **two local calendar days**, which does not represent a complete local day of observations.

Using `LOCAL_DATE` instead returns the correct full day of observations for the station:

```
2026-03-07 00:00 local → 2026-03-07 23:00 local
```

This produces the expected **24 hourly records for a single day**.

During testing it was also observed that the API may delay publishing the previous day's complete dataset for several hours after midnight. Because of this behavior, the automation schedule was designed to run later in the day to ensure the dataset is fully available.

---

## Handling Missing or NULL Values

The API occasionally returns `NULL` for numeric values such as humidex, precipitation, or windchill.

During transformation these values are normalized:

```
NULL → 0
```

This ensures compatibility with the database schema.

---

## Duplicate Protection

The pipeline checks whether data for the target date already exists before inserting new records.

This prevents duplicate ingestion if the pipeline runs multiple times for the same day.

Example log message:

```
WARNING | pipeline.load | Data for 2026-03-05 already exists in database. Skipping insert.
```

---

## Logging

The pipeline uses Python's built-in logging framework to record execution details.

Logs capture key events such as:

* pipeline start and completion
* number of records retrieved
* duplicate detection
* API or runtime errors

An example log file is included in the repository:

```
logs/pipeline.log.example
```

The example contains `INFO`, `WARNING`, and `ERROR` log entries.
An intentional error was generated during testing by temporarily modifying the API endpoint to demonstrate error logging behavior.

---

## Handling Missing Records

The pipeline does **not enforce a strict check for exactly 24 records**.

This is intentional. In production environments data sources may occasionally contain missing or corrupted records. Instead of failing the pipeline, available data is still inserted so the pipeline remains resilient.

---

## Automation and Scheduling

Automation is implemented using the `run_pipeline.sh` script or Docker container rather than embedding scheduling logic directly in the code. This keeps the pipeline **decoupled from its execution environment**.

The script:

1. Determines the previous day's date
2. Runs the pipeline for that date

---

### Suggested Scheduling Design

Initial analysis suggested running the pipeline around **05:00 UTC**, assuming the previous day's data would be available after local midnight.

However, testing showed the API sometimes delays publishing the previous day's observations even after the local day changes.

To ensure the dataset is consistently available, the pipeline is scheduled to run at:

```
23:00 UTC
```

At this time all Canadian time zones are still within the same day and the previous day's observations are reliably available from the API.

The pipeline subtracts one day from the current date to fetch the correct dataset.

---

## Quick Start

The following steps describe how to set up and run the pipeline on a clean Linux environment.

---

### 1. Install System Dependencies

Ensure the following tools are available:

* Python 3
* pip
* Git
* SQLite (for verification)

Example installation on Ubuntu:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git sqlite3 -y
```

---

### 2. Clone the Repository

```bash
git clone https://github.com/saini10/hiaa-climate-pipeline.git
cd hiaa-climate-pipeline
```

---

### 3. Create and Activate Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Pipeline

The pipeline can be executed in two ways.

### Option A: Run Manually

Run the pipeline by providing a target date.

```
python -m pipeline.main --date YYYY-MM-DD
```

Example:

```
python -m pipeline.main --date 2026-03-05
```

The `--date` parameter allows manual execution for a specific day.
This is useful for testing, backfilling historical data, or re-processing a failed run.

---

### Option B: Run Using the Helper Script

Make the script executable:

```
chmod +x run_pipeline.sh
```

Run the pipeline:

```
./run_pipeline.sh
```

The script automatically calculates the previous day's date and runs the pipeline.

> **Note**
> If the script is executed **early in the UTC day**, it is possible that the records for the specified climate identifier are not yet available from the API. In that case, the pipeline may log a message similar to:
>
> ```
> INFO | __main__ | Extracted 0 records
> ```
>
> This is **normal and expected behavior**. When the pipeline is scheduled to run later in the day (for example **23:00 UTC**), the records are  available and the pipeline will process them normally.

---

## Verify Results

Open the SQLite database:

```
sqlite3 db/yhz_db.sqlite
```

The database included in the repository contains the schema but no records. 
All development and testing data was removed so the pipeline execution can be observed clearly when run.

Example queries:

```
SELECT COUNT(*) FROM hiaa_geomet_hourly;
```

```
SELECT * FROM hiaa_geomet_hourly LIMIT 10;
```

Exit SQLite:

```
.exit
```

---

## Schedule the Pipeline with Cron (Example)

Open the cron configuration:

```
crontab -e
```

Example job:

```
0 23 * * * /path/to/hiaa-climate-pipeline/run_pipeline.sh
```

This runs the pipeline daily at **23:00 UTC**, ensuring the previous day's dataset is available from the API.

---

## Run Using Docker (Optional)

Build the Docker image:

```
docker build -t hiaa-climate-pipeline .
```

Run the container:

```
docker run --rm hiaa-climate-pipeline
```

The container implementation is intentionally simple and focuses on providing a clean execution environment. Persistent storage configuration was not included due to the scope and time constraints of this assessment.

---

## Testing

The pipeline was tested on a clean **Ubuntu Linux environment (AWS EC2 instance)** using the Quick Start steps described above. This ensures the setup instructions are reproducible in a fresh environment.

## Summary

This project demonstrates a production-oriented ETL pipeline for ingesting hourly climate observations from the GeoMet API and loading them into an SQLite database.

The implementation incorporates practical engineering considerations such as API behavior analysis, duplicate protection, resilient data handling, automated scheduling, structured logging, and reproducible execution using scripts and Docker.
