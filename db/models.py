"""SQLAlchemy database models."""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CryptoPrice(Base):
    """Model for storing cryptocurrency price data."""

    __tablename__ = "crypto_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    price_usd = Column(Numeric(20, 8), nullable=False)
    market_cap = Column(BigInteger, nullable=True)
    volume_24h = Column(BigInteger, nullable=True)
    price_change_24h = Column(Numeric(10, 2), nullable=True)
    last_updated = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of CryptoPrice."""
        return (
            f"<CryptoPrice(symbol={self.symbol}, name={self.name}, "
            f"price_usd={self.price_usd}, last_updated={self.last_updated})>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "name": self.name,
            "price_usd": float(self.price_usd) if self.price_usd else None,
            "market_cap": self.market_cap,
            "volume_24h": self.volume_24h,
            "price_change_24h": float(self.price_change_24h) if self.price_change_24h else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
