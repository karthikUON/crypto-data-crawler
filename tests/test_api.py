"""Tests for API endpoints."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api.main import app
from db.database import get_db
from db.models import CryptoPrice


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

    def test_health_check_success(self):
        """Test successful health check."""
        from unittest.mock import patch

        with patch("api.routes.check_db_connection", return_value=True):
            client = TestClient(app)
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "healthy"
            assert "timestamp" in data

    def test_health_check_db_unhealthy(self):
        """Test health check with unhealthy database."""
        from unittest.mock import patch

        with patch("api.routes.check_db_connection", return_value=False):
            client = TestClient(app)
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "unhealthy"


class TestPricesEndpoint:
    """Test cases for prices list endpoint."""

    def test_get_prices_success(self, sample_crypto_price):
        """Test successful retrieval of prices."""
        mock_db_session = MagicMock()
        mock_query = MagicMock()
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = [sample_crypto_price]
        mock_db_session.query.return_value = mock_query

        def override_get_db():
            try:
                yield mock_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)

        response = client.get("/api/v1/prices")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert len(data["data"]) == 1
        assert data["data"][0]["symbol"] == "BTC"

        app.dependency_overrides = {}

    def test_get_prices_with_symbol_filter(self, sample_crypto_price):
        """Test retrieval of prices with symbol filter."""
        mock_db_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = [sample_crypto_price]
        mock_db_session.query.return_value = mock_query

        def override_get_db():
            try:
                yield mock_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)

        response = client.get("/api/v1/prices?symbol=BTC")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["symbol"] == "BTC"

        app.dependency_overrides = {}

    def test_get_prices_with_pagination(self, sample_crypto_price):
        """Test retrieval of prices with pagination."""
        mock_db_session = MagicMock()
        mock_query = MagicMock()
        mock_query.count.return_value = 50
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = [sample_crypto_price]
        mock_db_session.query.return_value = mock_query

        def override_get_db():
            try:
                yield mock_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)

        response = client.get("/api/v1/prices?page=2&per_page=20")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["per_page"] == 20
        assert data["total"] == 50

        app.dependency_overrides = {}

    def test_get_prices_database_error(self):
        """Test handling of database errors."""
        mock_db_session = MagicMock()
        mock_db_session.query.side_effect = Exception("Database error")

        def override_get_db():
            try:
                yield mock_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)

        response = client.get("/api/v1/prices")

        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

        app.dependency_overrides = {}


class TestPriceBySymbolEndpoint:
    """Test cases for price by symbol endpoint."""

    def test_get_price_by_symbol_success(self, sample_crypto_price):
        """Test successful retrieval of price by symbol."""
        mock_db_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = sample_crypto_price
        mock_db_session.query.return_value = mock_query

        def override_get_db():
            try:
                yield mock_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)

        response = client.get("/api/v1/prices/BTC")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "BTC"
        assert data["name"] == "Bitcoin"
        assert data["price_usd"] == 50000.0

        app.dependency_overrides = {}

    def test_get_price_by_symbol_not_found(self):
        """Test retrieval of non-existent symbol."""
        mock_db_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query

        def override_get_db():
            try:
                yield mock_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)

        response = client.get("/api/v1/prices/INVALID")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

        app.dependency_overrides = {}

    def test_get_price_by_symbol_database_error(self):
        """Test handling of database errors."""
        mock_db_session = MagicMock()
        mock_db_session.query.side_effect = Exception("Database error")

        def override_get_db():
            try:
                yield mock_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)

        response = client.get("/api/v1/prices/BTC")

        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

        app.dependency_overrides = {}
