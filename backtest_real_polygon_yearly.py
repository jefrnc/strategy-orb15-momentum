#!/usr/bin/env python3
"""
Real Polygon Data Backtesting - Full Year Analysis
Month-by-month backtesting with actual market data
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import requests
import time
from typing import Dict, List, Tuple
import argparse
import shutil

class RealPolygonBacktester:
    def __init__(self, api_key: str, config_path: str):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        self.config = self._load_config(config_path)
        self.cache_dir = "data/polygon_cache"
        self.results_dir = "data/yearly_backtest_results"
        
        # Create directories
        for dir_path in [self.cache_dir, self.results_dir]:
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
        self.monthly_results = defaultdict(dict)
        self.all_trades = []
        
    def _load_config(self, config_path: str) -> dict:
        """Load trading configuration"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def get_polygon_data(self, symbol: str, date: str, use_cache: bool = True) -> pd.DataFrame:
        """Fetch minute data from Polygon API"""
        cache_file = f"{self.cache_dir}/{symbol}_{date}.json"
        
        if use_cache and os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                data = json.load(f)
        else:
            # Fetch from Polygon
            url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}"
            params = {
                'apiKey': self.api_key,
                'adjusted': 'true',
                'sort': 'asc',
                'limit': 50000
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Cache the data
                with open(cache_file, 'w') as f:
                    json.dump(data, f)
                
                time.sleep(0.2)  # Rate limiting
            else:
                print(f"Error fetching {symbol} for {date}: {response.status_code}")
                return pd.DataFrame()
        
        # Convert to DataFrame
        if 'results' in data and data['results']:
            df = pd.DataFrame(data['results'])
            df['datetime'] = pd.to_datetime(df['t'], unit='ms')
            df['date'] = df['datetime'].dt.date
            df['time'] = df['datetime'].dt.time
            df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'}, inplace=True)
            return df[['datetime', 'date', 'time', 'open', 'high', 'low', 'close', 'volume']]
        
        return pd.DataFrame()
    
    def calculate_orb(self, df: pd.DataFrame, date: datetime.date) -> Tuple[float, float]:
        """Calculate Opening Range Breakout levels"""
        orb_start = datetime.combine(date, datetime.strptime("09:30", "%H:%M").time())
        orb_end = orb_start + timedelta(minutes=self.orb_minutes)
        
        orb_data = df[(df['datetime'] >= orb_start) & (df['datetime'] < orb_end)]
        
        if orb_data.empty:
            return None, None
        
        orb_high = orb_data['high'].max()
        orb_low = orb_data['low'].min()
        
        return orb_high, orb_low
    
    def simulate_trades(self, symbol: str, date: str, account_value: float) -> List[Dict]:
        """Simulate trades for a single day"""
        df = self.get_polygon_data(symbol, date)
        if df.empty:
            return []
        
        trades = []
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        
        # Calculate ORB
        orb_high, orb_low = self.calculate_orb(df, date_obj)
        if orb_high is None:
            return []
        
        # Trading window
        trade_start = datetime.combine(date_obj, datetime.strptime("09:35", "%H:%M").time())
        trade_end = datetime.combine(date_obj, datetime.strptime("11:30", "%H:%M").time())
        market_close = datetime.combine(date_obj, datetime.strptime("16:00", "%H:%M").time())
        
        # Filter trading window data
        trade_data = df[(df['datetime'] >= trade_start) & (df['datetime'] <= trade_end)]
        
        position_open = False
        entry_price = 0
        entry_time = None
        shares = 0
        
        for idx, row in trade_data.iterrows():
            if not position_open:
                # Check for breakout
                if row['close'] > orb_high * 1.001:  # 0.1% above ORB high
                    entry_price = row['close']
                    entry_time = row['datetime']
                    
                    # Calculate position size
                    risk_amount = account_value * self.position_risk
                    stop_distance = entry_price * abs(self.stop_loss_pct)
                    shares = int(risk_amount / stop_distance)
                    position_value = shares * entry_price
                    
                    # Apply position limits
                    max_position = account_value * 0.08  # 8% max for aggressive
                    if position_value > max_position:
                        shares = int(max_position / entry_price)
                    
                    position_open = True
            else:
                # Check exit conditions
                stop_price = entry_price * (1 + self.stop_loss_pct)
                target_price = entry_price * (1 + self.take_profit_pct)
                
                exit_price = None
                exit_reason = None
                
                if row['low'] <= stop_price:
                    exit_price = stop_price
                    exit_reason = "STOP"
                elif row['high'] >= target_price:
                    exit_price = target_price
                    exit_reason = "TARGET"
                
                if exit_price:
                    # Calculate P&L
                    gross_pnl = (exit_price - entry_price) * shares
                    commission = 0.0035 * shares * 2 + 0.70  # IBKR rates
                    net_pnl = gross_pnl - commission
                    
                    trade = {
                        'symbol': symbol,
                        'date': date,
                        'entry_time': entry_time.strftime('%H:%M'),
                        'exit_time': row['datetime'].strftime('%H:%M'),
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'shares': shares,
                        'gross_pnl': gross_pnl,
                        'commission': commission,
                        'net_pnl': net_pnl,
                        'exit_reason': exit_reason,
                        'hold_time': (row['datetime'] - entry_time).seconds / 60
                    }
                    
                    trades.append(trade)
                    position_open = False
                    break
        
        # Close at market close if still open
        if position_open:
            close_data = df[df['datetime'] <= market_close].iloc[-1]
            exit_price = close_data['close']
            
            gross_pnl = (exit_price - entry_price) * shares
            commission = 0.0035 * shares * 2 + 0.70
            net_pnl = gross_pnl - commission
            
            trade = {
                'symbol': symbol,
                'date': date,
                'entry_time': entry_time.strftime('%H:%M'),
                'exit_time': close_data['datetime'].strftime('%H:%M'),
                'entry_price': entry_price,
                'exit_price': exit_price,
                'shares': shares,
                'gross_pnl': gross_pnl,
                'commission': commission,
                'net_pnl': net_pnl,
                'exit_reason': "TIME",
                'hold_time': (close_data['datetime'] - entry_time).seconds / 60
            }
            
            trades.append(trade)
        
        return trades
    
    def backtest_month(self, year: int, month: int, starting_capital: float) -> Dict:
        """Backtest a single month"""
        print(f"\nBacktesting {year}-{month:02d}...")
        
        # Get trading days for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        account_value = starting_capital
        month_trades = []
        daily_pnl = []
        
        # Iterate through trading days
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday to Friday
                date_str = current_date.strftime("%Y-%m-%d")
                day_trades = []
                
                # Trade each symbol
                for symbol in self.symbols:
                    trades = self.simulate_trades(symbol, date_str, account_value)
                    day_trades.extend(trades)
                
                # Update account value
                day_pnl = sum(trade['net_pnl'] for trade in day_trades)
                account_value += day_pnl
                
                if day_trades:
                    daily_pnl.append(day_pnl)
                    month_trades.extend(day_trades)
                
                # Apply daily loss limit
                if day_pnl < -starting_capital * 0.05:  # 5% daily loss limit
                    print(f"  Daily loss limit hit on {date_str}: ${day_pnl:.2f}")
            
            current_date += timedelta(days=1)
        
        # Calculate monthly metrics
        if month_trades:
            wins = [t for t in month_trades if t['net_pnl'] > 0]
            losses = [t for t in month_trades if t['net_pnl'] <= 0]
            
            metrics = {
                'month': f"{year}-{month:02d}",
                'starting_capital': starting_capital,
                'ending_capital': account_value,
                'total_trades': len(month_trades),
                'winning_trades': len(wins),
                'losing_trades': len(losses),
                'win_rate': len(wins) / len(month_trades) * 100,
                'total_pnl': account_value - starting_capital,
                'return_pct': (account_value - starting_capital) / starting_capital * 100,
                'avg_win': np.mean([t['net_pnl'] for t in wins]) if wins else 0,
                'avg_loss': np.mean([t['net_pnl'] for t in losses]) if losses else 0,
                'largest_win': max([t['net_pnl'] for t in wins]) if wins else 0,
                'largest_loss': min([t['net_pnl'] for t in losses]) if losses else 0,
                'profit_factor': abs(sum(t['net_pnl'] for t in wins) / sum(t['net_pnl'] for t in losses)) if losses else 0,
                'sharpe_ratio': np.mean(daily_pnl) / np.std(daily_pnl) * np.sqrt(252) if len(daily_pnl) > 1 else 0,
                'trades': month_trades
            }
        else:
            metrics = {
                'month': f"{year}-{month:02d}",
                'starting_capital': starting_capital,
                'ending_capital': account_value,
                'total_trades': 0,
                'return_pct': 0
            }
        
        return metrics, account_value
    
    def run_yearly_backtest(self, start_year: int, start_month: int, end_year: int, end_month: int):
        """Run backtest for specified period"""
        initial_capital = 100000
        account_value = initial_capital
        
        current_year = start_year
        current_month = start_month
        
        while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
            # Clear cache for fresh data
            month_cache_pattern = f"{current_year}-{current_month:02d}"
            for cache_file in os.listdir(self.cache_dir):
                if month_cache_pattern in cache_file:
                    os.remove(os.path.join(self.cache_dir, cache_file))
            
            # Run monthly backtest
            month_metrics, account_value = self.backtest_month(current_year, current_month, account_value)
            self.monthly_results[f"{current_year}-{current_month:02d}"] = month_metrics
            self.all_trades.extend(month_metrics.get('trades', []))
            
            # Next month
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
        
        # Calculate YTD and overall metrics
        self._calculate_ytd_metrics(initial_capital, account_value)
        self._save_results()
    
    def _calculate_ytd_metrics(self, initial_capital: float, final_capital: float):
        """Calculate Year-to-Date metrics"""
        total_return = (final_capital - initial_capital) / initial_capital * 100
        
        # Group by year
        yearly_metrics = defaultdict(lambda: {
            'trades': 0,
            'pnl': 0,
            'wins': 0,
            'starting_capital': initial_capital
        })
        
        for month, metrics in self.monthly_results.items():
            year = month.split('-')[0]
            yearly_metrics[year]['trades'] += metrics.get('total_trades', 0)
            yearly_metrics[year]['pnl'] += metrics.get('total_pnl', 0)
            yearly_metrics[year]['wins'] += metrics.get('winning_trades', 0)
        
        # Calculate annual metrics
        for year, data in yearly_metrics.items():
            if data['trades'] > 0:
                data['win_rate'] = data['wins'] / data['trades'] * 100
                data['return_pct'] = data['pnl'] / data['starting_capital'] * 100
        
        self.ytd_metrics = {
            'total_return': total_return,
            'final_capital': final_capital,
            'yearly_breakdown': dict(yearly_metrics),
            'total_trades': len(self.all_trades)
        }
    
    def _save_results(self):
        """Save all results to files"""
        # Save monthly results
        monthly_file = f"{self.results_dir}/monthly_results.json"
        with open(monthly_file, 'w') as f:
            json.dump(self.monthly_results, f, indent=2, default=str)
        
        # Save YTD metrics
        ytd_file = f"{self.results_dir}/ytd_metrics.json"
        with open(ytd_file, 'w') as f:
            json.dump(self.ytd_metrics, f, indent=2)
        
        # Save trades CSV
        if self.all_trades:
            trades_df = pd.DataFrame(self.all_trades)
            trades_df.to_csv(f"{self.results_dir}/all_trades.csv", index=False)
        
        # Generate summary report
        self._generate_summary_report()
    
    def _generate_summary_report(self):
        """Generate markdown summary report"""
        report = f"""# 📊 Real Polygon Data Backtest Results

## 🎯 Overall Performance Summary

- **Total Return**: {self.ytd_metrics['total_return']:.2f}%
- **Final Account Value**: ${self.ytd_metrics['final_capital']:,.2f}
- **Total Trades**: {self.ytd_metrics['total_trades']}

## 📅 Monthly Breakdown

| Month | Trades | Win Rate | P&L | Return % | Account Value |
|-------|--------|----------|-----|----------|---------------|
"""
        
        for month, metrics in sorted(self.monthly_results.items()):
            if metrics.get('total_trades', 0) > 0:
                report += f"| {month} | {metrics['total_trades']} | {metrics['win_rate']:.1f}% | ${metrics['total_pnl']:,.2f} | {metrics['return_pct']:.2f}% | ${metrics['ending_capital']:,.2f} |\n"
        
        report += """
## 📈 Key Metrics

### Risk-Adjusted Performance
"""
        
        # Calculate overall Sharpe ratio
        monthly_returns = [m['return_pct'] for m in self.monthly_results.values() if 'return_pct' in m]
        if len(monthly_returns) > 1:
            sharpe = np.mean(monthly_returns) / np.std(monthly_returns) * np.sqrt(12)
            report += f"- **Sharpe Ratio**: {sharpe:.2f}\n"
        
        # Best/worst months
        best_month = max(self.monthly_results.items(), key=lambda x: x[1].get('return_pct', -999))
        worst_month = min(self.monthly_results.items(), key=lambda x: x[1].get('return_pct', 999))
        
        report += f"- **Best Month**: {best_month[0]} ({best_month[1]['return_pct']:.2f}%)\n"
        report += f"- **Worst Month**: {worst_month[0]} ({worst_month[1]['return_pct']:.2f}%)\n"
        
        # Save report
        with open(f"{self.results_dir}/backtest_summary.md", 'w') as f:
            f.write(report)
        
        print("\n" + report)

def main():
    parser = argparse.ArgumentParser(description='Real Polygon data backtesting')
    parser.add_argument('--start-year', type=int, default=2024, help='Start year')
    parser.add_argument('--start-month', type=int, default=1, help='Start month')
    parser.add_argument('--end-year', type=int, default=2024, help='End year')
    parser.add_argument('--end-month', type=int, default=12, help='End month')
    parser.add_argument('--config', default='configs/orb_aggressive_config.json', help='Config file')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = os.getenv('POLYGON_API_KEY')
    if not api_key:
        print("Error: POLYGON_API_KEY not set in environment")
        return
    
    # Run backtest
    backtester = RealPolygonBacktester(api_key, args.config)
    backtester.run_yearly_backtest(
        args.start_year,
        args.start_month,
        args.end_year,
        args.end_month
    )
    
    # Backtesting complete
    print("\nBacktesting complete. Results saved to data/yearly_backtest_results/")

if __name__ == "__main__":
    main()