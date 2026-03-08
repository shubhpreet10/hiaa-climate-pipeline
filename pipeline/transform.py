import logging
from datetime import datetime

logger = logging.getLogger(__name__)


NUMERIC_FIELDS = [
    "TEMP",
    "DEW_POINT_TEMP",
    "HUMIDEX",
    "PRECIP_AMOUNT",
    "RELATIVE_HUMIDITY",
    "STATION_PRESSURE",
    "VISIBILITY",
    "WINDCHILL",
    "WIND_DIRECTION",
    "WIND_SPEED",
]


def normalize_numeric(value):
    """
    Convert None/NA numeric values to 0.
    """
    if value is None:
        return 0
    return value


def transform_features(features: list) -> list:
    """
    Transform API features into rows matching the database schema.

    Args:
        features (list): Raw feature list from the API.

    Returns:
        list: List of transformed rows ready for database insertion.
    """

    rows = []
    insert_time = datetime.utcnow().isoformat()

    for feature in features:
        props = feature.get("properties", {})

        row = {
            "climate_identifier": props.get("CLIMATE_IDENTIFIER"),
            "local_date": props.get("LOCAL_DATE"),
            "temp": normalize_numeric(props.get("TEMP")),
            "dew_point_temp": normalize_numeric(props.get("DEW_POINT_TEMP")),
            "humidex": normalize_numeric(props.get("HUMIDEX")),
            "precip_amount": normalize_numeric(props.get("PRECIP_AMOUNT")),
            "relative_humidity": normalize_numeric(props.get("RELATIVE_HUMIDITY")),
            "station_pressure": normalize_numeric(props.get("STATION_PRESSURE")),
            "visibility": normalize_numeric(props.get("VISIBILITY")),
            "weather_eng_desc": props.get("WEATHER_ENG_DESC"),
            "windchill": normalize_numeric(props.get("WINDCHILL")),
            "wind_direction": normalize_numeric(props.get("WIND_DIRECTION")),
            "wind_speed": normalize_numeric(props.get("WIND_SPEED")),
            "insert_time": insert_time,
        }

        rows.append(row)

    logger.info(f"Transformed {len(rows)} records")

    return rows