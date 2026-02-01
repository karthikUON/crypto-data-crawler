"""Tests for crawler module (parser, retry handler, crawler)."""

import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

from crawler.fetch_prices import CryptoCrawler
from crawler.parser import DataParser
from crawler.retry_handler import RetryHandler


class TestDataParser:
    """Test cases for DataParser."""

    def test_parse_crypto_data_success(self):
        """Test successful parsing of cryptocurrency data."""
        raw_data = [
            {
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 50000.0,
                "market_cap": 1000000000000,
                "total_volume": 50000000000,
                "price_change_percentage_24h": 2.5,
                "last_updated": "2026-02-01T08:00:00Z",
            },
            {
                "symbol": "eth",
                "name": "Ethereum",
                "current_price": 3000.0,
                "market_cap": 400000000000,
                "total_volume": 20000000000,
                "price_change_percentage_24h": -1.2,
                "last_updated": "2026-02-01T08:00:00Z",
            },
        ]

        parser = DataParser()
        result = parser.parse_crypto_data(raw_data)

        assert len(result) == 2
        assert result[0]["symbol"] == "BTC"
        assert result[0]["name"] == "Bitcoin"
        assert result[0]["price_usd"] == 50000.0
        assert result[1]["symbol"] == "ETH"
        assert result[1]["name"] == "Ethereum"

    def test_parse_crypto_data_missing_required_field(self):
        """Test parsing with missing required field."""
        raw_data = [
            {
                "symbol": "btc",
                "name": "Bitcoin",
                # Missing current_price
            }
        ]

        parser = DataParser()
        result = parser.parse_crypto_data(raw_data)

        # Should skip invalid item
        assert len(result) == 0

    def test_parse_crypto_data_invalid_type(self):
        """Test parsing with invalid data type."""
        parser = DataParser()

        with pytest.raises(ValueError, match="Expected raw_data to be a list"):
            parser.parse_crypto_data("not a list")  # type: ignore

    def test_safe_int_conversion(self):
        """Test safe integer conversion."""
        assert DataParser._safe_int(123) == 123
        assert DataParser._safe_int("456") == 456
        assert DataParser._safe_int(None) is None
        assert DataParser._safe_int("invalid") is None

    def test_safe_float_conversion(self):
        """Test safe float conversion."""
        assert DataParser._safe_float(12.34) == 12.34
        assert DataParser._safe_float("56.78") == 56.78
        assert DataParser._safe_float(None) is None
        assert DataParser._safe_float("invalid") is None


class TestRetryHandler:
    """Test cases for RetryHandler."""

    def test_execute_with_retry_success_first_attempt(self):
        """Test successful execution on first attempt."""
        handler = RetryHandler(max_retries=3)
        func = MagicMock(return_value="success")

        result = handler.execute_with_retry(func, "test_operation")

        assert result == "success"
        assert func.call_count == 1

    def test_execute_with_retry_success_after_failures(self):
        """Test successful execution after some failures."""
        handler = RetryHandler(max_retries=3, backoff_factor=0.1)
        func = MagicMock(side_effect=[Exception("error1"), Exception("error2"), "success"])

        result = handler.execute_with_retry(func, "test_operation")

        assert result == "success"
        assert func.call_count == 3

    def test_execute_with_retry_all_attempts_fail(self):
        """Test when all retry attempts fail."""
        handler = RetryHandler(max_retries=2, backoff_factor=0.1)
        func = MagicMock(side_effect=Exception("persistent error"))

        with pytest.raises(Exception, match="persistent error"):
            handler.execute_with_retry(func, "test_operation")

        assert func.call_count == 3  # 1 initial + 2 retries

    def test_exponential_backoff(self):
        """Test exponential backoff timing."""
        handler = RetryHandler(max_retries=3, backoff_factor=2.0)
        func = MagicMock(side_effect=[Exception("error"), Exception("error"), "success"])

        start_time = time.time()
        handler.execute_with_retry(func, "test_operation")
        elapsed_time = time.time() - start_time

        # Should have waited approximately 1s (2^0) + 2s (2^1) = 3s
        assert elapsed_time >= 2.5  # Allow some tolerance


class TestCryptoCrawler:
    """Test cases for CryptoCrawler."""

    @patch("crawler.fetch_prices.requests.get")
    def test_fetch_crypto_data_success(self, mock_get):
        """Test successful fetching of cryptocurrency data."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 50000.0,
                "market_cap": 1000000000000,
                "total_volume": 50000000000,
                "price_change_percentage_24h": 2.5,
                "last_updated": "2026-02-01T08:00:00Z",
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        crawler = CryptoCrawler()
        result = crawler.fetch_crypto_data()

        assert len(result) == 1
        assert result[0]["symbol"] == "BTC"
        assert result[0]["price_usd"] == 50000.0
        mock_get.assert_called_once()

    @patch("crawler.fetch_prices.requests.get")
    def test_fetch_crypto_data_api_error(self, mock_get):
        """Test handling of API errors."""
        mock_get.side_effect = requests.RequestException("API Error")

        crawler = CryptoCrawler()

        with pytest.raises(requests.RequestException):
            crawler.fetch_crypto_data()

    @patch("crawler.fetch_prices.SessionLocal")
    def test_save_to_database_success(self, mock_session_local):
        """Test successful saving to database."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        crypto_data = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price_usd": 50000.0,
                "market_cap": 1000000000000,
                "volume_24h": 50000000000,
                "price_change_24h": 2.5,
                "last_updated": datetime.utcnow(),
            }
        ]

        crawler = CryptoCrawler()
        crawler.save_to_database(crypto_data)

        mock_db.add.assert_called()
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("crawler.fetch_prices.SessionLocal")
    def test_save_to_database_error(self, mock_session_local):
        """Test handling of database errors."""
        mock_db = MagicMock()
        mock_db.commit.side_effect = Exception("Database error")
        mock_session_local.return_value = mock_db

        crypto_data = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price_usd": 50000.0,
                "market_cap": 1000000000000,
                "volume_24h": 50000000000,
                "price_change_24h": 2.5,
                "last_updated": datetime.utcnow(),
            }
        ]

        crawler = CryptoCrawler()

        with pytest.raises(Exception, match="Database error"):
            crawler.save_to_database(crypto_data)

        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()
