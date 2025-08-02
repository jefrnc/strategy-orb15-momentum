#!/usr/bin/env python3
"""
Real Backtesting System with Polygon Data
Backtests ORB strategy month by month with fresh data downloads
"""

import os
import json
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass
import shutil

@dataclass
class BacktestTrade:
    """Individual trade result"""
    symbol: str
    entry_date: str
    entry_time: str
    entry_price: float
    exit_price: float
    exit_reason: str
    shares: int
    pnl: float
    hold_minutes: int
    stop_price: float
    target_price: float

class PolygonDataDownloader:
    """Download real market data from Polygon.io"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        self.cache_dir = "data/polygon_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def download_daily_bars(self, symbol: str, date_str: str) -> Optional[pd.DataFrame]:
        """Download 1-minute bars for a specific date"""
        cache_file = f"{self.cache_dir}/{symbol}_{date_str}.csv"
        
        # Check if already cached
        if os.path.exists(cache_file):
            print(f"📈 Loading cached data: {symbol} {date_str}")
            return pd.read_csv(cache_file, parse_dates=['timestamp'])
        
        # Download from Polygon
        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/minute/{date_str}/{date_str}"
        params = {
            'apikey': self.api_key,
            'adjusted': 'true',
            'sort': 'asc',
            'limit': 50000
        }
        
        try:
            print(f"🌐 Downloading: {symbol} {date_str}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK' or not data.get('results'):
                print(f"⚠️ No data for {symbol} on {date_str}")
                return None
            
            # Convert to DataFrame
            bars = []
            for bar in data['results']:
                bars.append({
                    'timestamp': pd.to_datetime(bar['t'], unit='ms'),
                    'open': bar['o'],
                    'high': bar['h'], 
                    'low': bar['l'],
                    'close': bar['c'],
                    'volume': bar['v']
                })
            
            df = pd.DataFrame(bars)
            
            # Filter to market hours only (9:30 AM - 4:00 PM ET)
            df = df[df['timestamp'].dt.time >= pd.Timestamp('09:30').time()]
            df = df[df['timestamp'].dt.time <= pd.Timestamp('16:00').time()]
            
            # Cache the data
            df.to_csv(cache_file, index=False)
            print(f"✅ Downloaded and cached: {symbol} {date_str} ({len(df)} bars)")
            
            time.sleep(0.2)  # Rate limiting
            return df
            
        except Exception as e:
            print(f"❌ Error downloading {symbol} {date_str}: {e}")
            return None

class ORBBacktester:
    """Real ORB strategy backtester"""
    
    def __init__(self, config_file: str = 'configs/orb_optimized_config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.trades = []
        self.daily_stats = []
        self.account_value = 100000  # Starting capital
        
        # Get API key from environment
        self.api_key = os.getenv('POLYGON_API_KEY')
        if not self.api_key:
            raise ValueError("POLYGON_API_KEY environment variable required")
        
        self.downloader = PolygonDataDownloader(self.api_key)
    
    def calculate_orb_levels(self, df: pd.DataFrame, orb_minutes: int = 15) -> Tuple[float, float]:
        """Calculate ORB high and low levels"""
        market_open = pd.Timestamp('09:30').time()
        orb_end = (pd.Timestamp('09:30') + pd.Timedelta(minutes=orb_minutes)).time()
        
        # Get ORB period bars
        orb_bars = df[
            (df['timestamp'].dt.time >= market_open) & 
            (df['timestamp'].dt.time <= orb_end)
        ].copy()
        
        if len(orb_bars) == 0:
            return None, None
        
        orb_high = orb_bars['high'].max()
        orb_low = orb_bars['low'].min()
        
        return orb_high, orb_low
    
    def calculate_position_size(self, entry_price: float, stop_price: float) -> int:
        """Calculate position size based on risk"""
        risk_pct = self.config['position_sizing']['base_risk_per_trade']
        risk_amount = self.account_value * risk_pct
        
        stop_distance = abs(entry_price - stop_price)
        if stop_distance == 0:
            return 0
        
        shares = int(risk_amount / stop_distance)
        
        # Apply maximum position size
        max_position_pct = self.config['position_sizing']['absolute_limits']['max_position_percentage']
        max_position_value = self.account_value * max_position_pct
        max_shares = int(max_position_value / entry_price)
        
        return min(shares, max_shares)
    
    def simulate_trade(self, symbol: str, df: pd.DataFrame, entry_time: pd.Timestamp, 
                      entry_price: float, stop_price: float, target_price: float) -> Optional[BacktestTrade]:
        """Simulate a single trade execution"""
        
        # Calculate position size
        shares = self.calculate_position_size(entry_price, stop_price)
        if shares < 1:
            return None
        
        # Find bars after entry
        future_bars = df[df['timestamp'] > entry_time].copy()
        if len(future_bars) == 0:
            return None
        
        # Check for stop loss or take profit
        for _, bar in future_bars.iterrows():
            # Check stop loss (price goes against us)
            if bar['low'] <= stop_price:
                exit_price = stop_price
                exit_reason = "STOP"
                hold_minutes = int((bar['timestamp'] - entry_time).total_seconds() / 60)
                break
            
            # Check take profit
            if bar['high'] >= target_price:
                exit_price = target_price
                exit_reason = "TARGET"
                hold_minutes = int((bar['timestamp'] - entry_time).total_seconds() / 60)
                break
        else:
            # No stop or target hit, exit at market close
            exit_price = future_bars.iloc[-1]['close']
            exit_reason = "TIME"
            hold_minutes = int((future_bars.iloc[-1]['timestamp'] - entry_time).total_seconds() / 60)
        
        # Calculate P&L
        pnl = (exit_price - entry_price) * shares
        
        # Apply commission (IBKR rates)
        commission = shares * 0.0035 + 0.35  # $0.0035 per share + $0.35 base
        pnl -= commission
        
        return BacktestTrade(
            symbol=symbol,
            entry_date=entry_time.strftime('%Y-%m-%d'),
            entry_time=entry_time.strftime('%H:%M'),
            entry_price=entry_price,
            exit_price=exit_price,
            exit_reason=exit_reason,
            shares=shares,
            pnl=pnl,
            hold_minutes=hold_minutes,
            stop_price=stop_price,
            target_price=target_price
        )
    
    def backtest_symbol_day(self, symbol: str, date_str: str) -> List[BacktestTrade]:
        """Backtest one symbol for one day"""
        df = self.downloader.download_daily_bars(symbol, date_str)
        if df is None or len(df) < 20:
            return []
        
        # Calculate ORB levels
        strategy = self.config['strategy_parameters']['beast_mode']
        orb_minutes = strategy['orb_minutes']
        orb_high, orb_low = self.calculate_orb_levels(df, orb_minutes)
        
        if orb_high is None or orb_low is None:
            return []
        
        trades = []
        
        # Look for breakout after ORB period
        orb_end_time = pd.Timestamp(f"{date_str} 09:30") + pd.Timedelta(minutes=orb_minutes)
        post_orb_bars = df[df['timestamp'] > orb_end_time].copy()
        
        for _, bar in post_orb_bars.iterrows():
            # Long breakout above ORB high
            if bar['high'] > orb_high and bar['close'] > orb_high:
                entry_price = orb_high * 1.001  # Small buffer above breakout
                
                # Calculate stop and target
                stop_loss_pct = strategy['stop_loss_pct']
                take_profit_pct = strategy['take_profit_pct']
                
                stop_price = entry_price * (1 + stop_loss_pct)  # stop_loss_pct is negative
                target_price = entry_price * (1 + take_profit_pct)
                
                # Simulate the trade
                trade = self.simulate_trade(
                    symbol, df, bar['timestamp'], 
                    entry_price, stop_price, target_price
                )
                
                if trade:
                    trades.append(trade)
                    break  # Only one trade per symbol per day
        
        return trades
    
    def get_trading_days(self, year: int, month: int) -> List[str]:
        """Get list of trading days for a month (exclude weekends)"""
        start_date = date(year, month, 1)
        
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        trading_days = []
        current_date = start_date
        
        while current_date <= end_date:
            # Exclude weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:
                trading_days.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        return trading_days
    
    def backtest_month(self, year: int, month: int) -> Dict:
        """Backtest a full month"""
        print(f"\n🗓️ BACKTESTING {year}-{month:02d}")
        print("=" * 50)
        
        # Clear cache for fresh data
        month_cache = f"{self.downloader.cache_dir}/*_{year}-{month:02d}-*.csv"
        os.system(f"rm -f {month_cache}")
        
        trading_days = self.get_trading_days(year, month)
        symbols = self.config['strategy_parameters']['beast_mode']['symbols']
        
        month_trades = []
        daily_pnl = []
        
        for day in trading_days:
            print(f"\n📅 Testing {day}")
            day_trades = []
            day_pnl = 0
            
            for symbol in symbols:
                symbol_trades = self.backtest_symbol_day(symbol, day)
                day_trades.extend(symbol_trades)
                day_pnl += sum(trade.pnl for trade in symbol_trades)
                
                if symbol_trades:
                    for trade in symbol_trades:
                        print(f"  💰 {trade.symbol}: {trade.exit_reason} P&L=${trade.pnl:.2f}")
            
            month_trades.extend(day_trades)
            daily_pnl.append(day_pnl)
            self.account_value += day_pnl
            
            print(f"  📊 Day P&L: ${day_pnl:.2f} | Account: ${self.account_value:.2f}")
        
        # Calculate month statistics
        total_trades = len(month_trades)
        winning_trades = len([t for t in month_trades if t.pnl > 0])
        total_pnl = sum(t.pnl for t in month_trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        month_stats = {
            'month': f"{year}-{month:02d}",
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'daily_pnl': daily_pnl,
            'trades': month_trades,
            'account_value': self.account_value
        }
        
        print(f"\n📈 MONTH SUMMARY:")
        print(f"   Trades: {total_trades}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Total P&L: ${total_pnl:.2f}")
        print(f"   Account Value: ${self.account_value:.2f}")
        
        return month_stats
    
    def run_full_backtest(self, start_month: int = 1, end_month: int = 7) -> Dict:
        """Run complete backtest for 2025"""
        print("🎯 STARTING REAL BACKTEST - 2025")
        print("=" * 60)
        print(f"💰 Starting Capital: ${self.account_value:,.2f}")
        print(f"📊 Strategy: {self.config.get('system_name', 'ORB_OPTIMIZED')}")
        
        all_results = {
            'months': [],
            'total_trades': 0,
            'total_pnl': 0,
            'final_account_value': 0,
            'overall_win_rate': 0,
            'monthly_returns': []
        }
        
        all_trades = []
        
        # Test each month
        for month in range(start_month, end_month + 1):
            month_result = self.backtest_month(2025, month)
            all_results['months'].append(month_result)
            all_trades.extend(month_result['trades'])
        
        # Calculate overall statistics
        all_results['total_trades'] = len(all_trades)
        all_results['total_pnl'] = sum(t.pnl for t in all_trades)
        all_results['final_account_value'] = self.account_value
        all_results['overall_win_rate'] = (
            len([t for t in all_trades if t.pnl > 0]) / len(all_trades) * 100
            if all_trades else 0
        )
        
        # Calculate monthly returns
        for month_result in all_results['months']:
            monthly_return = month_result['total_pnl'] / 100000 * 100  # Percentage
            all_results['monthly_returns'].append(monthly_return)
        
        # Save detailed results
        os.makedirs('data/backtest_results', exist_ok=True)
        
        with open('data/backtest_results/full_backtest_2025.json', 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        # Save trade details
        trades_df = pd.DataFrame([
            {
                'symbol': t.symbol,
                'entry_date': t.entry_date,
                'entry_time': t.entry_time,
                'entry_price': t.entry_price,
                'exit_price': t.exit_price,
                'exit_reason': t.exit_reason,
                'shares': t.shares,
                'pnl': t.pnl,
                'hold_minutes': t.hold_minutes
            } for t in all_trades
        ])
        
        trades_df.to_csv('data/backtest_results/trades_detail_2025.csv', index=False)
        
        return all_results

def main():
    """Run real backtesting"""
    
    # Check for API key
    if not os.getenv('POLYGON_API_KEY'):
        print("❌ ERROR: POLYGON_API_KEY environment variable required")
        print("Get your free API key at: https://polygon.io/")
        print("Set it in your .env file: POLYGON_API_KEY=your_key_here")
        return
    
    try:
        backtester = ORBBacktester()
        results = backtester.run_full_backtest(start_month=1, end_month=7)
        
        print("\n" + "="*60)
        print("🏆 FINAL BACKTEST RESULTS - 2025")
        print("="*60)
        print(f"📊 Total Trades: {results['total_trades']}")
        print(f"🎯 Win Rate: {results['overall_win_rate']:.1f}%")
        print(f"💰 Total P&L: ${results['total_pnl']:,.2f}")
        print(f"📈 Final Account: ${results['final_account_value']:,.2f}")
        print(f"📊 Total Return: {(results['final_account_value']/100000-1)*100:.1f}%")
        
        if results['monthly_returns']:
            avg_monthly = np.mean(results['monthly_returns'])
            annualized = avg_monthly * 12
            print(f"📈 Avg Monthly Return: {avg_monthly:.1f}%")
            print(f"🚀 Annualized Return: {annualized:.1f}%")
        
        print(f"\n📁 Results saved to: data/backtest_results/")
        
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        raise

if __name__ == "__main__":
    main()