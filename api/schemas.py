"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CryptoPriceBase(BaseModel):
    """Base schema for cryptocurrency price."""

    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")
    name: str = Field(..., description="Full cryptocurrency name")
    price_usd: float = Field(..., description="Current price in USD")
    market_cap: Optional[int] = Field(None, description="Market capitalization")
    volume_24h: Optional[int] = Field(None, description="24-hour trading volume")
    price_change_24h: Optional[float] = Field(None, description="24-hour price change percentage")
    last_updated: datetime = Field(..., description="When the price was last updated")


class CryptoPriceResponse(CryptoPriceBase):
    """Schema for cryptocurrency price response."""

    id: int = Field(..., description="Database record ID")
    created_at: datetime = Field(..., description="When the record was created")

    class Config:
        """Pydantic config."""

        from_attributes = True


class CryptoPriceListResponse(BaseModel):
    """Schema for paginated cryptocurrency price list response."""

    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    data: List[CryptoPriceResponse] = Field(..., description="List of cryptocurrency prices")


class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(..., description="Service status")
    database: str = Field(..., description="Database connection status")
    timestamp: datetime = Field(..., description="Current timestamp")
