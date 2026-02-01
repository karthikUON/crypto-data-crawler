"""Main crawler for fetching cryptocurrency prices from CoinGecko API."""

import logging
import sys
import time
from typing import List

import requests
from sqlalchemy.orm import Session

from crawler.config import settings
from crawler.parser import DataParser
from crawler.retry_handler import retry_handler
from db.database import SessionLocal, init_db
from db.models import CryptoPrice

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


class CryptoCrawler:
    """Cryptocurrency data crawler that fetches prices from CoinGecko API."""

    def __init__(self):
        """Initialize the crawler."""
        self.api_url = f"{settings.crypto_api_url}/coins/markets"
        self.parser = DataParser()

    def fetch_crypto_data(self) -> List[dict]:
        """
        Fetch cryptocurrency data from CoinGecko API.

        Returns:
            List of cryptocurrency data

        Raises:
            requests.RequestException: If API request fails
        """
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": settings.top_n_cryptos,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h",
        }

        logger.info(f"Fetching top {settings.top_n_cryptos} cryptocurrencies from CoinGecko API")

        def _fetch():
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        raw_data = retry_handler.execute_with_retry(_fetch, "CoinGecko API fetch")
        return self.parser.parse_crypto_data(raw_data)

    def save_to_database(self, crypto_data: List[dict]) -> None:
        """
        Save cryptocurrency data to the database.

        Args:
            crypto_data: List of normalized cryptocurrency data
        """
        db: Session = SessionLocal()
        try:
            saved_count = 0
            for data in crypto_data:
                crypto_price = CryptoPrice(**data)
                db.add(crypto_price)
                saved_count += 1

            db.commit()
            logger.info(f"Successfully saved {saved_count} cryptocurrency prices to database")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save data to database: {e}")
            raise
        finally:
            db.close()

    def run_once(self) -> None:
        """Run the crawler once to fetch and save cryptocurrency data."""
        try:
            logger.info("Starting cryptocurrency data fetch...")
            crypto_data = self.fetch_crypto_data()
            self.save_to_database(crypto_data)
            logger.info("Cryptocurrency data fetch completed successfully")
        except Exception as e:
            logger.error(f"Crawler run failed: {e}")
            raise

    def run_continuous(self) -> None:
        """Run the crawler continuously at specified intervals."""
        logger.info(f"Starting continuous crawler (interval: {settings.crawler_interval}s)")

        while True:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"Error in crawler iteration: {e}")

            logger.info(f"Waiting {settings.crawler_interval} seconds before next fetch...")
            time.sleep(settings.crawler_interval)


def main(continuous: bool = False) -> None:
    """
    Main entry point for the crawler.

    Args:
        continuous: If True, run continuously. If False, run once.
    """
    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Create and run crawler
    crawler = CryptoCrawler()

    if continuous:
        crawler.run_continuous()
    else:
        crawler.run_once()


if __name__ == "__main__":
    # Check command line arguments
    continuous_mode = "--continuous" in sys.argv
    main(continuous=continuous_mode)
