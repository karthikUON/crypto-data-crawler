-- Initialize database schema for crypto prices

-- Create crypto_prices table
CREATE TABLE IF NOT EXISTS crypto_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price_usd NUMERIC(20, 8) NOT NULL,
    market_cap BIGINT,
    volume_24h BIGINT,
    price_change_24h NUMERIC(10, 2),
    last_updated TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_symbol ON crypto_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_last_updated ON crypto_prices(last_updated);
CREATE INDEX IF NOT EXISTS idx_symbol_last_updated ON crypto_prices(symbol, last_updated);

-- Add comments
COMMENT ON TABLE crypto_prices IS 'Stores cryptocurrency price data from CoinGecko API';
COMMENT ON COLUMN crypto_prices.symbol IS 'Cryptocurrency symbol (e.g., BTC, ETH)';
COMMENT ON COLUMN crypto_prices.name IS 'Full cryptocurrency name';
COMMENT ON COLUMN crypto_prices.price_usd IS 'Current price in USD';
COMMENT ON COLUMN crypto_prices.market_cap IS 'Market capitalization';
COMMENT ON COLUMN crypto_prices.volume_24h IS '24-hour trading volume';
COMMENT ON COLUMN crypto_prices.price_change_24h IS '24-hour price change percentage';
COMMENT ON COLUMN crypto_prices.last_updated IS 'When the price data was last updated by the API';
COMMENT ON COLUMN crypto_prices.created_at IS 'When the record was inserted into the database';
