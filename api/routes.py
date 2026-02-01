"""API routes for cryptocurrency data."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from api.schemas import CryptoPriceListResponse, CryptoPriceResponse, HealthResponse
from db.database import check_db_connection, get_db
from db.models import CryptoPrice

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status including database connection status
    """
    db_status = "healthy" if check_db_connection() else "unhealthy"

    return HealthResponse(status="healthy", database=db_status, timestamp=datetime.utcnow())


@router.get("/api/v1/prices", response_model=CryptoPriceListResponse, tags=["Cryptocurrency"])
async def get_prices(
    symbol: Optional[str] = Query(None, description="Filter by cryptocurrency symbol"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get list of cryptocurrency prices with pagination.

    Args:
        symbol: Optional filter by cryptocurrency symbol
        page: Page number (starts from 1)
        per_page: Number of items per page (max 100)
        db: Database session

    Returns:
        Paginated list of cryptocurrency prices
    """
    try:
        # Build query
        query = db.query(CryptoPrice)

        # Apply symbol filter if provided
        if symbol:
            query = query.filter(CryptoPrice.symbol == symbol.upper())

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        offset = (page - 1) * per_page
        prices = query.order_by(desc(CryptoPrice.last_updated)).limit(per_page).offset(offset).all()

        # Convert to response models
        price_responses = [CryptoPriceResponse.model_validate(price) for price in prices]

        return CryptoPriceListResponse(
            total=total, page=page, per_page=per_page, data=price_responses
        )

    except Exception as e:
        logger.error(f"Error fetching prices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/v1/prices/{symbol}", response_model=CryptoPriceResponse, tags=["Cryptocurrency"])
async def get_price_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """
    Get the latest price for a specific cryptocurrency.

    Args:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH)
        db: Database session

    Returns:
        Latest cryptocurrency price data

    Raises:
        HTTPException: If cryptocurrency not found
    """
    try:
        # Query for the latest price of the given symbol
        price = (
            db.query(CryptoPrice)
            .filter(CryptoPrice.symbol == symbol.upper())
            .order_by(desc(CryptoPrice.last_updated))
            .first()
        )

        if not price:
            raise HTTPException(
                status_code=404, detail=f"Cryptocurrency with symbol '{symbol}' not found"
            )

        return CryptoPriceResponse.model_validate(price)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
