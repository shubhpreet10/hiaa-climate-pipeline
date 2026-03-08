import os
import sqlite3
import logging
from dotenv import load_dotenv

load_dotenv("config/.env")

logger = logging.getLogger(__name__)


INSERT_QUERY = """
INSERT INTO hiaa_geomet_hourly (
    climate_identifier,
    local_date,
    temp,
    dew_point_temp,
    humidex,
    precip_amount,
    relative_humidity,
    station_pressure,
    visibility,
    weather_eng_desc,
    windchill,
    wind_direction,
    wind_speed,
    insert_time
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def data_exists(cursor, date_value: str) -> bool:
    """
    Check if records already exist for the given LOCAL_DATE.
    """

    query = """
    SELECT COUNT(*)
    FROM hiaa_geomet_hourly
    WHERE date(local_date) = ?
    """

    cursor.execute(query, (date_value,))
    count = cursor.fetchone()[0]

    return count > 0


def load_rows(rows: list):
    """
    Load transformed rows into the SQLite database.

    Args:
        rows (list): List of transformed row dictionaries.
    """

    if not rows:
        logger.warning("No rows to load")
        return

    db_path = os.getenv("DB_PATH")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Extract date portion (YYYY-MM-DD)
        date_value = rows[0]["local_date"][:10]

        # Duplicate check
        if data_exists(cursor, date_value):
            logger.warning(
                f"Data for {date_value} already exists in database. Skipping insert."
            )
            return

        # Prepare values for insertion
        values = [
            (
                row["climate_identifier"],
                row["local_date"],
                row["temp"],
                row["dew_point_temp"],
                row["humidex"],
                row["precip_amount"],
                row["relative_humidity"],
                row["station_pressure"],
                row["visibility"],
                row["weather_eng_desc"],
                row["windchill"],
                row["wind_direction"],
                row["wind_speed"],
                row["insert_time"],
            )
            for row in rows
        ]

        cursor.executemany(INSERT_QUERY, values)

        conn.commit()

        logger.info(f"Inserted {len(rows)} records for date {date_value}")

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise

    finally:
        conn.close()