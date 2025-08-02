#!/usr/bin/env python3
"""
Run REAL backtesting with Polygon.io historical data
NO synthetic data, NO hardcoded values, 100% authentic market data
"""

import os
import sys
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(
        description='Run authentic backtesting with real Polygon.io data'
    )
    parser.add_argument('--start-year', type=int, required=True,
                      help='Start year for backtest')
    parser.add_argument('--start-month', type=int, required=True,
                      help='Start month (1-12)')
    parser.add_argument('--end-year', type=int, required=True,
                      help='End year for backtest')
    parser.add_argument('--end-month', type=int, required=True,
                      help='End month (1-12)')
    parser.add_argument('--config', default='configs/orb_aggressive_config.json',
                      help='Configuration file to use')
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = os.getenv('POLYGON_API_KEY')
    if not api_key:
        print("❌ ERROR: POLYGON_API_KEY environment variable not set")
        print("\nTo run real backtesting, you need a Polygon.io API key:")
        print("1. Sign up at https://polygon.io")
        print("2. Get your API key")
        print("3. Set environment variable:")
        print("   export POLYGON_API_KEY=your_key_here")
        print("\n⚠️  This system does NOT work with synthetic data")
        print("⚠️  All results come from real market data only")
        sys.exit(1)
    
    # Validate dates
    current_year = datetime.now().year
    if args.start_year > current_year or args.end_year > current_year:
        print(f"❌ ERROR: Cannot backtest future dates (current year: {current_year})")
        sys.exit(1)
    
    if args.start_year < 2020:
        print("⚠️  WARNING: Data before 2020 may be limited or unavailable")
    
    # Import the real backtester
    try:
        from backtest_real_polygon_yearly import RealPolygonBacktester
    except ImportError:
        print("❌ ERROR: Missing backtest_real_polygon_yearly.py")
        print("This file is required for real backtesting")
        sys.exit(1)
    
    print("\n🚀 Starting REAL backtest with Polygon.io data")
    print("=" * 60)
    print(f"📅 Period: {args.start_year}/{args.start_month} to {args.end_year}/{args.end_month}")
    print(f"⚙️  Config: {args.config}")
    print(f"🔑 API Key: {'*' * 20}{api_key[-4:]}")
    print("=" * 60)
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("• This uses REAL market data - results reflect actual historical performance")
    print("• Performance will vary based on market conditions during test period")
    print("• Past performance does NOT guarantee future results")
    print("• Commission and slippage are included in calculations")
    print("\nFetching real market data... this may take several minutes\n")
    
    # Run the backtest
    backtester = RealPolygonBacktester(api_key, args.config)
    backtester.run_yearly_backtest(
        args.start_year,
        args.start_month,
        args.end_year,
        args.end_month
    )
    
    print("\n✅ Backtest complete!")
    print(f"📊 Results saved to: data/yearly_backtest_results/")
    print("\nFiles generated:")
    print("  • monthly_results.json - Monthly performance breakdown")
    print("  • ytd_metrics.json - Overall statistics")
    print("  • all_trades.csv - Individual trade details")
    print("  • backtest_summary.md - Human-readable report")
    print("\n⚠️  Remember: These are historical results. Future performance may differ.")

if __name__ == "__main__":
    main()