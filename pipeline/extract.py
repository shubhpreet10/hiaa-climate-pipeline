import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv("config/.env")

logger = logging.getLogger(__name__)


def build_request_params(local_date: str) -> dict:
    """
    Build query parameters for the API request.
    """
    return {
        "f": os.getenv("FORMAT"),
        "CLIMATE_IDENTIFIER": os.getenv("CLIMATE_IDENTIFIER"),
        "LOCAL_DATE": local_date,
        "limit": os.getenv("LIMIT"),
        "skipGeometry": os.getenv("SKIP_GEOMETRY")
    }


def fetch_climate_data(local_date: str) -> list:
    """
    Extract hourly climate data from the Geomet API.

    Args:
        local_date (str): Date in YYYY-MM-DD format.

    Returns:
        list: List of feature objects from the API response.
    """

    endpoint = os.getenv("API_ENDPOINT")
    timeout = int(os.getenv("REQUEST_TIMEOUT", 30))

    params = build_request_params(local_date)

    logger.info(f"Starting extraction for LOCAL_DATE={local_date}")

    try:
        response = requests.get(endpoint, params=params, timeout=timeout)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise

    data = response.json()
    features = data.get("features", [])

    if not features:
        logger.warning(f"No data returned for LOCAL_DATE={local_date}")
        return []

    logger.info(f"Successfully retrieved {len(features)} records")

    return features