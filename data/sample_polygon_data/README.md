# Sample Polygon Data

This directory contains sample market data in Polygon API format for testing the ORB trading system.

## Data Format

Each file contains minute-by-minute OHLCV data for a specific symbol and date.

### File naming convention:
`SYMBOL_YYYY-MM-DD.json`

### Data structure:
```json
{
  "ticker": "NVDA",
  "results": [
    {
      "v": 250000,     // Volume
      "vw": 475.50,    // Volume weighted price
      "o": 475.00,     // Open
      "c": 476.25,     // Close  
      "h": 476.50,     // High
      "l": 474.75,     // Low
      "t": 1704379800000,  // Timestamp (ms)
      "n": 500         // Number of trades
    }
  ]
}
```

## Usage

1. Place these files in `data/sample_polygon_data/`
2. Run backtest with `--use-sample-data` flag
3. No API key required for sample data

## Symbols included:
- NVDA, TSLA, AMD, AAPL, MSFT, GOOGL, AMZN, META

## Time period:
- First 5 trading days of each month in 2024
- Full market hours (9:30 AM - 4:00 PM ET)

This data is synthetic and for testing purposes only.
