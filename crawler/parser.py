"""Data parser and normalizer for cryptocurrency data."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DataParser:
    """Parses and normalizes cryptocurrency data from API responses."""

    @staticmethod
    def parse_crypto_data(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse and normalize cryptocurrency data from API response.

        Args:
            raw_data: Raw data from CoinGecko API

        Returns:
            List of normalized cryptocurrency records

        Raises:
            ValueError: If data is invalid or missing required fields
        """
        if not isinstance(raw_data, list):
            raise ValueError("Expected raw_data to be a list")

        normalized_data = []

        for item in raw_data:
            try:
                record = DataParser._parse_single_crypto(item)
                normalized_data.append(record)
            except Exception as e:
                logger.warning(f"Failed to parse crypto item: {e}. Item: {item}")
                continue

        logger.info(f"Successfully parsed {len(normalized_data)} crypto records")
        return normalized_data

    @staticmethod
    def _parse_single_crypto(item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a single cryptocurrency item.

        Args:
            item: Single cryptocurrency item from API

        Returns:
            Normalized cryptocurrency record

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ["symbol", "name", "current_price"]
        for field in required_fields:
            if field not in item:
                raise ValueError(f"Missing required field: {field}")

        # Extract and normalize data
        symbol = str(item["symbol"]).upper()
        name = str(item["name"])
        price_usd = float(item["current_price"])
        market_cap = DataParser._safe_int(item.get("market_cap"))
        volume_24h = DataParser._safe_int(item.get("total_volume"))
        price_change_24h = DataParser._safe_float(item.get("price_change_percentage_24h"))

        # Parse last_updated timestamp
        last_updated_str = item.get("last_updated")
        if last_updated_str:
            try:
                last_updated = datetime.fromisoformat(last_updated_str.replace("Z", "+00:00"))
            except Exception:
                last_updated = datetime.utcnow()
        else:
            last_updated = datetime.utcnow()

        return {
            "symbol": symbol,
            "name": name,
            "price_usd": price_usd,
            "market_cap": market_cap,
            "volume_24h": volume_24h,
            "price_change_24h": price_change_24h,
            "last_updated": last_updated,
        }

    @staticmethod
    def _safe_int(value: Optional[Any]) -> Optional[int]:
        """Safely convert value to int or return None."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_float(value: Optional[Any]) -> Optional[float]:
        """Safely convert value to float or return None."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
