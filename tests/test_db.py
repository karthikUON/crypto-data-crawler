"""Tests for database models and operations."""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base, CryptoPrice


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)


class TestCryptoPriceModel:
    """Test cases for CryptoPrice model."""

    def test_create_crypto_price(self, db_session):
        """Test creating a CryptoPrice record."""
        crypto_price = CryptoPrice(
            symbol="BTC",
            name="Bitcoin",
            price_usd=50000.0,
            market_cap=1000000000000,
            volume_24h=50000000000,
            price_change_24h=2.5,
            last_updated=datetime.utcnow(),
        )

        db_session.add(crypto_price)
        db_session.commit()

        # Verify record was created
        assert crypto_price.id is not None
        assert crypto_price.symbol == "BTC"
        assert crypto_price.name == "Bitcoin"
        assert crypto_price.price_usd == 50000.0

    def test_query_crypto_price(self, db_session):
        """Test querying CryptoPrice records."""
        # Create multiple records
        crypto1 = CryptoPrice(
            symbol="BTC",
            name="Bitcoin",
            price_usd=50000.0,
            market_cap=1000000000000,
            volume_24h=50000000000,
            price_change_24h=2.5,
            last_updated=datetime.utcnow(),
        )
        crypto2 = CryptoPrice(
            symbol="ETH",
            name="Ethereum",
            price_usd=3000.0,
            market_cap=400000000000,
            volume_24h=20000000000,
            price_change_24h=-1.2,
            last_updated=datetime.utcnow(),
        )

        db_session.add_all([crypto1, crypto2])
        db_session.commit()

        # Query all records
        all_prices = db_session.query(CryptoPrice).all()
        assert len(all_prices) == 2

        # Query by symbol
        btc_price = db_session.query(CryptoPrice).filter(CryptoPrice.symbol == "BTC").first()
        assert btc_price is not None
        assert btc_price.name == "Bitcoin"

    def test_crypto_price_to_dict(self, db_session):
        """Test converting CryptoPrice to dictionary."""
        crypto_price = CryptoPrice(
            symbol="BTC",
            name="Bitcoin",
            price_usd=50000.0,
            market_cap=1000000000000,
            volume_24h=50000000000,
            price_change_24h=2.5,
            last_updated=datetime.utcnow(),
        )

        db_session.add(crypto_price)
        db_session.commit()

        price_dict = crypto_price.to_dict()

        assert price_dict["symbol"] == "BTC"
        assert price_dict["name"] == "Bitcoin"
        assert price_dict["price_usd"] == 50000.0
        assert price_dict["market_cap"] == 1000000000000
        assert "last_updated" in price_dict
        assert "created_at" in price_dict

    def test_crypto_price_repr(self, db_session):
        """Test string representation of CryptoPrice."""
        crypto_price = CryptoPrice(
            symbol="BTC",
            name="Bitcoin",
            price_usd=50000.0,
            market_cap=1000000000000,
            volume_24h=50000000000,
            price_change_24h=2.5,
            last_updated=datetime.utcnow(),
        )

        repr_str = repr(crypto_price)
        assert "BTC" in repr_str
        assert "Bitcoin" in repr_str
        assert "50000" in repr_str

    def test_crypto_price_nullable_fields(self, db_session):
        """Test CryptoPrice with nullable fields."""
        crypto_price = CryptoPrice(
            symbol="BTC",
            name="Bitcoin",
            price_usd=50000.0,
            market_cap=None,
            volume_24h=None,
            price_change_24h=None,
            last_updated=datetime.utcnow(),
        )

        db_session.add(crypto_price)
        db_session.commit()

        # Verify record was created with null values
        assert crypto_price.id is not None
        assert crypto_price.market_cap is None
        assert crypto_price.volume_24h is None
        assert crypto_price.price_change_24h is None

    def test_multiple_price_updates(self, db_session):
        """Test storing multiple price updates for the same symbol."""
        # Simulate multiple price updates over time
        now = datetime.utcnow()

        crypto1 = CryptoPrice(
            symbol="BTC",
            name="Bitcoin",
            price_usd=50000.0,
            market_cap=1000000000000,
            volume_24h=50000000000,
            price_change_24h=2.5,
            last_updated=now,
        )

        crypto2 = CryptoPrice(
            symbol="BTC",
            name="Bitcoin",
            price_usd=51000.0,
            market_cap=1020000000000,
            volume_24h=52000000000,
            price_change_24h=4.0,
            last_updated=now,
        )

        db_session.add_all([crypto1, crypto2])
        db_session.commit()

        # Query all BTC prices
        btc_prices = (
            db_session.query(CryptoPrice).filter(CryptoPrice.symbol == "BTC").all()
        )
        assert len(btc_prices) == 2
