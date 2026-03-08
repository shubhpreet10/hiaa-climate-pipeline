import logging
import os
import argparse
from datetime import datetime

from pipeline.extract import fetch_climate_data
from pipeline.transform import transform_features
from pipeline.load import load_rows


LOG_FILE = "logs/pipeline.log"


def setup_logging():
    """
    Configure logging for the pipeline.
    Logs are written to both console and file.
    """

    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )


def validate_date(local_date: str):
    """
    Validate that the provided date follows YYYY-MM-DD format.
    """
    try:
        datetime.strptime(local_date, "%Y-%m-%d")
    except ValueError:
        raise SystemExit("Invalid date. Use format YYYY-MM-DD")


def main():

    parser = argparse.ArgumentParser(description="HIAA Climate Data Pipeline")
    parser.add_argument(
        "--date",
        required=True,
        help="LOCAL_DATE for extraction in YYYY-MM-DD format"
    )

    args = parser.parse_args()
    target_date = args.date

    validate_date(target_date)

    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Pipeline started")

    try:
        # ---------------------
        # Extract
        # ---------------------
        features = fetch_climate_data(target_date)
        logger.info(f"Extracted {len(features)} records")

        if not features:
            logger.warning("No features returned from API. Pipeline exiting.")
            return

        # ---------------------
        # Transform
        # ---------------------
        rows = transform_features(features)
        logger.info(f"Transformed {len(rows)} records")

        # ---------------------
        # Load
        # ---------------------
        load_rows(rows)

    except Exception:
        logger.exception("Pipeline failed")
        raise

    logger.info("Pipeline finished successfully")


if __name__ == "__main__":
    main()