"""Tests for API endpoints."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from db.models import CryptoPrice

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def sample_crypto_price():
    """Create a sample CryptoPrice object."""
    price = CryptoPrice(
        id=1,
        symbol="BTC",
        name="Bitcoin",
        price_usd=50000.0,
        market_cap=1000000000000,
        volume_24h=50000000000,
        price_change_24h=2.5,
        last_updated=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    return price


class TestHealthEndpoint:
    """Test cases for health check endpoint."""

    @patch("api.routes.check_db_connection")
    def test_health_check_success(self, mock_check_db):
        """Test successful health check."""
        mock_check_db.return_value = True

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "healthy"
        assert "timestamp" in data

    @patch("api.routes.check_db_connection")
    def test_health_check_db_unhealthy(self, mock_check_db):
        """Test health check with unhealthy database."""
        mock_check_db.return_value = False

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "unhealthy"


class TestPricesEndpoint:
    """Test cases for prices list endpoint."""

    @patch("api.routes.get_db")
    def test_get_prices_success(self, mock_get_db, mock_db_session, sample_crypto_price):
        """Test successful retrieval of prices."""
        mock_query = MagicMock()
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = [sample_crypto_price]

        mock_db_session.query.return_value = mock_query
        mock_get_db.return_value = iter([mock_db_session])

        response = client.get("/api/v1/prices")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert len(data["data"]) == 1
        assert data["data"][0]["symbol"] == "BTC"

    @patch("api.routes.get_db")
    def test_get_prices_with_symbol_filter(
        self, mock_get_db, mock_db_session, sample_crypto_price
    ):
        """Test retrieval of prices with symbol filter."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = [sample_crypto_price]

        mock_db_session.query.return_value = mock_query
        mock_get_db.return_value = iter([mock_db_session])

        response = client.get("/api/v1/prices?symbol=BTC")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["symbol"] == "BTC"

    @patch("api.routes.get_db")
    def test_get_prices_with_pagination(self, mock_get_db, mock_db_session, sample_crypto_price):
        """Test retrieval of prices with pagination."""
        mock_query = MagicMock()
        mock_query.count.return_value = 50
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = [sample_crypto_price]

        mock_db_session.query.return_value = mock_query
        mock_get_db.return_value = iter([mock_db_session])

        response = client.get("/api/v1/prices?page=2&per_page=20")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["per_page"] == 20
        assert data["total"] == 50

    @patch("api.routes.get_db")
    def test_get_prices_database_error(self, mock_get_db, mock_db_session):
        """Test handling of database errors."""
        mock_db_session.query.side_effect = Exception("Database error")
        mock_get_db.return_value = iter([mock_db_session])

        response = client.get("/api/v1/prices")

        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


class TestPriceBySymbolEndpoint:
    """Test cases for price by symbol endpoint."""

    @patch("api.routes.get_db")
    def test_get_price_by_symbol_success(self, mock_get_db, mock_db_session, sample_crypto_price):
        """Test successful retrieval of price by symbol."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = sample_crypto_price

        mock_db_session.query.return_value = mock_query
        mock_get_db.return_value = iter([mock_db_session])

        response = client.get("/api/v1/prices/BTC")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "BTC"
        assert data["name"] == "Bitcoin"
        assert data["price_usd"] == 50000.0

    @patch("api.routes.get_db")
    def test_get_price_by_symbol_not_found(self, mock_get_db, mock_db_session):
        """Test retrieval of non-existent symbol."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None

        mock_db_session.query.return_value = mock_query
        mock_get_db.return_value = iter([mock_db_session])

        response = client.get("/api/v1/prices/INVALID")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch("api.routes.get_db")
    def test_get_price_by_symbol_database_error(self, mock_get_db, mock_db_session):
        """Test handling of database errors."""
        mock_db_session.query.side_effect = Exception("Database error")
        mock_get_db.return_value = iter([mock_db_session])

        response = client.get("/api/v1/prices/BTC")

        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
