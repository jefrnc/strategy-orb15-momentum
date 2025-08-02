#!/usr/bin/env python3
"""
Backtest using sample data - no API key required
Perfect for testing and validation
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backtest_real_polygon_yearly import RealPolygonBacktester

class SampleDataBacktester(RealPolygonBacktester):
    """Backtester that uses local sample data instead of API"""
    
    def __init__(self, config_path: str):
        # Initialize without API key
        self.api_key = "SAMPLE_DATA_MODE"
        self.base_url = "https://api.polygon.io"
        self.config = self._load_config(config_path)
        self.cache_dir = "data/polygon_cache"
        self.sample_dir = "data/sample_polygon_data"
        self.results_dir = "data/sample_backtest_results"
        
        # Create directories
        for dir_path in [self.cache_dir, self.sample_dir, self.results_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Trading parameters from config
        # Use scalping mode parameters from aggressive config
        strategy_params = self.config['strategy_parameters']['scalping_mode']
        self.symbols = strategy_params['symbols']
        self.position_risk = self.config['position_sizing']['base_risk_per_trade']
        self.stop_loss_pct = strategy_params['stop_loss_pct']
        self.take_profit_pct = strategy_params['take_profit_pct']
        self.orb_minutes = strategy_params['orb_minutes']
        self.max_daily_trades = strategy_params['max_daily_trades']
        self.max_simultaneous_positions = strategy_params['max_simultaneous_positions']
        
        # Results storage
        from collections import defaultdict
        self.monthly_results = defaultdict(dict)
        self.all_trades = []
    
    def get_polygon_data(self, symbol: str, date: str, use_cache: bool = True) -> pd.DataFrame:
        """Load data from sample files instead of API"""
        sample_file = f"{self.sample_dir}/{symbol}_{date}.json"
        
        if os.path.exists(sample_file):
            with open(sample_file, 'r') as f:
                data = json.load(f)
            
            # Convert to DataFrame
            if 'results' in data and data['results']:
                df = pd.DataFrame(data['results'])
                df['datetime'] = pd.to_datetime(df['t'], unit='ms')
                df['date'] = df['datetime'].dt.date
                df['time'] = df['datetime'].dt.time
                df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'}, inplace=True)
                return df[['datetime', 'date', 'time', 'open', 'high', 'low', 'close', 'volume']]
        
        return pd.DataFrame()

def main():
    """Run backtest with sample data"""
    print("🚀 Running backtest with sample data...")
    print("No API key required!\n")
    
    # Check if sample data exists
    if not os.path.exists("data/sample_polygon_data"):
        print("⚠️  Sample data not found. Generating...")
        os.system("python3 generate_sample_data.py")
    
    # Run backtest
    config_path = "configs/orb_aggressive_config.json"
    backtester = SampleDataBacktester(config_path)
    
    # Backtest full year 2024
    backtester.run_yearly_backtest(2024, 1, 2024, 12)
    
    print("\n✅ Backtest complete!")
    print(f"Results saved to: {backtester.results_dir}/")
    print("\nFiles created:")
    print("- monthly_results.json")
    print("- ytd_metrics.json") 
    print("- all_trades.csv")
    print("- backtest_summary.md")

if __name__ == "__main__":
    main()