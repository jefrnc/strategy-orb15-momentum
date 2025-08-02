#!/usr/bin/env python3
"""
Generate realistic sample market data for testing
Creates data that mimics Polygon API format
"""

import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class SampleDataGenerator:
    def __init__(self):
        self.sample_dir = "data/sample_polygon_data"
        os.makedirs(self.sample_dir, exist_ok=True)
        
        # Market characteristics
        self.symbols = ['NVDA', 'TSLA', 'AMD', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
        self.base_prices = {
            'NVDA': 475.0,
            'TSLA': 250.0,
            'AMD': 115.0,
            'AAPL': 180.0,
            'MSFT': 370.0,
            'GOOGL': 140.0,
            'AMZN': 155.0,
            'META': 470.0
        }
        
    def generate_minute_data(self, symbol: str, date: str) -> dict:
        """Generate realistic minute data for a symbol"""
        base_price = self.base_prices[symbol]
        
        # Parse date
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        
        # Generate trading day data (390 minutes from 9:30 to 16:00)
        data_points = []
        current_time = datetime.combine(date_obj, datetime.strptime("09:30", "%H:%M").time())
        
        # Pre-market gap
        gap_pct = np.random.normal(0, 0.02)  # +/- 2% gap on average
        opening_price = base_price * (1 + gap_pct)
        
        # Daily volatility
        daily_volatility = np.random.uniform(0.01, 0.03)  # 1-3% daily vol
        
        # Trend for the day
        daily_trend = np.random.choice([-1, 0, 1], p=[0.3, 0.4, 0.3])
        trend_strength = np.random.uniform(0.001, 0.003)
        
        current_price = opening_price
        
        # ORB period characteristics
        orb_high = opening_price
        orb_low = opening_price
        
        for minute in range(390):
            # Timestamp
            timestamp = int(current_time.timestamp() * 1000)
            
            # Price movement
            if minute < 15:  # ORB period - higher volatility
                volatility = daily_volatility * 2
                volume_multiplier = 3
            elif minute < 120:  # Morning session
                volatility = daily_volatility * 1.5
                volume_multiplier = 2
            elif minute < 240:  # Midday
                volatility = daily_volatility * 0.7
                volume_multiplier = 0.8
            else:  # Afternoon
                volatility = daily_volatility
                volume_multiplier = 1.2
            
            # Generate OHLC
            change = np.random.normal(daily_trend * trend_strength, volatility)
            
            open_price = current_price
            close_price = current_price * (1 + change)
            
            # High and low with realistic wicks
            wick_size = abs(change) * np.random.uniform(0.5, 2)
            high_price = max(open_price, close_price) + wick_size
            low_price = min(open_price, close_price) - wick_size
            
            # Volume (base 100k-500k shares per minute)
            base_volume = np.random.uniform(100000, 500000)
            volume = int(base_volume * volume_multiplier)
            
            # Update ORB levels
            if minute < 15:
                orb_high = max(orb_high, high_price)
                orb_low = min(orb_low, low_price)
            
            # Create potential breakout after ORB
            if minute == 20 and np.random.random() < 0.3:  # 30% chance of breakout
                if daily_trend > 0:
                    close_price = orb_high * 1.002  # Break above
                    high_price = close_price + volatility * base_price
            
            data_point = {
                "v": volume,
                "vw": (open_price + high_price + low_price + close_price) / 4,  # VWAP estimate
                "o": round(open_price, 2),
                "c": round(close_price, 2),
                "h": round(high_price, 2),
                "l": round(low_price, 2),
                "t": timestamp,
                "n": np.random.randint(100, 1000)  # Number of trades
            }
            
            data_points.append(data_point)
            
            # Update for next minute
            current_price = close_price
            current_time += timedelta(minutes=1)
        
        # Create Polygon-like response
        response = {
            "ticker": symbol,
            "queryCount": len(data_points),
            "resultsCount": len(data_points),
            "adjusted": True,
            "results": data_points,
            "status": "OK",
            "request_id": f"sample_{symbol}_{date}"
        }
        
        return response
    
    def generate_sample_month(self, year: int, month: int):
        """Generate sample data for first 5 days of a month"""
        print(f"Generating sample data for {year}-{month:02d}...")
        
        # Get first 5 trading days
        start_date = datetime(year, month, 1)
        trading_days = []
        current_date = start_date
        
        while len(trading_days) < 5:
            if current_date.weekday() < 5:  # Monday to Friday
                trading_days.append(current_date)
            current_date += timedelta(days=1)
            
            # Stop if we go to next month
            if current_date.month != month:
                break
        
        # Generate data for each symbol and day
        for symbol in self.symbols:
            for date in trading_days:
                date_str = date.strftime("%Y-%m-%d")
                data = self.generate_minute_data(symbol, date_str)
                
                # Save to file
                filename = f"{self.sample_dir}/{symbol}_{date_str}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f)
    
    def generate_full_year_sample(self, year: int):
        """Generate sample data for entire year"""
        for month in range(1, 13):
            self.generate_sample_month(year, month)
        
        print(f"\nSample data generated in {self.sample_dir}/")
        
        # Create a README for the sample data
        readme_content = f"""# Sample Polygon Data

This directory contains sample market data in Polygon API format for testing the ORB trading system.

## Data Format

Each file contains minute-by-minute OHLCV data for a specific symbol and date.

### File naming convention:
`SYMBOL_YYYY-MM-DD.json`

### Data structure:
```json
{{
  "ticker": "NVDA",
  "results": [
    {{
      "v": 250000,     // Volume
      "vw": 475.50,    // Volume weighted price
      "o": 475.00,     // Open
      "c": 476.25,     // Close  
      "h": 476.50,     // High
      "l": 474.75,     // Low
      "t": 1704379800000,  // Timestamp (ms)
      "n": 500         // Number of trades
    }}
  ]
}}
```

## Usage

1. Place these files in `data/sample_polygon_data/`
2. Run backtest with `--use-sample-data` flag
3. No API key required for sample data

## Symbols included:
- NVDA, TSLA, AMD, AAPL, MSFT, GOOGL, AMZN, META

## Time period:
- First 5 trading days of each month in {year}
- Full market hours (9:30 AM - 4:00 PM ET)

This data is synthetic and for testing purposes only.
"""
        
        with open(f"{self.sample_dir}/README.md", 'w') as f:
            f.write(readme_content)

def main():
    generator = SampleDataGenerator()
    
    # Generate sample data for 2024
    generator.generate_full_year_sample(2024)
    
    # Create zip archive
    import shutil
    shutil.make_archive('data/sample_polygon_data', 'zip', 'data/sample_polygon_data')
    print("Sample data archive created: data/sample_polygon_data.zip")

if __name__ == "__main__":
    main()