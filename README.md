# 🔥 ORB Trading System

**Professional algorithmic trading system for Interactive Brokers**

⚠️ **IMPORTANT**: This system requires real market data from Polygon.io for backtesting. All performance metrics must be generated from your own backtests with actual historical data.

## 🎯 Strategy Overview

### Core Strategy: Opening Range Breakout (ORB)
- **ORB Period**: Configurable (5-15 minutes)
- **Trading Window**: Morning session focus
- **Position Type**: Long only (breakout above ORB high)
- **Markets**: Large cap stocks (NVDA, TSLA, AMD, AAPL, MSFT, GOOGL, AMZN, META)

### Risk Management
- **Position Sizing**: Risk-based (configurable 1-5% per trade)
- **Stop Loss**: ATR-based or percentage
- **Take Profit**: Multiple R targets
- **Circuit Breakers**: Daily loss limits and drawdown protection

## 📋 System Requirements

### Software Dependencies
```bash
pip install -r requirements.txt
```

### Core Requirements
- **Python**: 3.8+
- **Interactive Brokers**: TWS or IB Gateway
- **Market Data**: Polygon.io API key (required for backtesting)
- **API Libraries**: ib_insync, pandas, numpy

### Configuration
- **Paper Trading**: Port 7497 (default)
- **Live Trading**: Port 7496
- **API Permissions**: Enable in TWS/Gateway settings

## 🚀 Quick Start

### 1. Setup
```bash
# Clone repository
git clone https://github.com/yourusername/ORB-15-Momentum.git
cd ORB-15-Momentum

# Create virtual environment
python3 -m venv orb_env
source orb_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Polygon API key
```

### 2. Paper Trading
```bash
# Start with paper trading (REQUIRED before live trading)
python3 orb_trader.py --mode paper
```

### 3. Risk Profiles
```bash
# Conservative (1% risk)
python3 orb_trader.py --risk-profile conservative --mode paper

# Balanced (2% risk)
python3 orb_trader.py --risk-profile balanced --mode paper

# Growth (3% risk)
python3 orb_trader.py --risk-profile growth --mode paper

# Aggressive (5% risk) - NOT RECOMMENDED for beginners
python3 orb_trader.py --risk-profile aggressive --mode paper
```

## 📊 Backtesting with Real Data

### IMPORTANT: Real Data Required
This system does NOT include historical market data. You must use your own Polygon.io API key to fetch real market data for backtesting.

### Running Real Backtests
```bash
# Set your Polygon API key
export POLYGON_API_KEY=your_polygon_api_key_here

# Run backtest for specific period
python3 backtest_real_polygon_yearly.py --start-year 2024 --start-month 1 --end-year 2024 --end-month 12

# Results will be saved to data/yearly_backtest_results/
```

### Backtest Output
- `monthly_results.json` - Month-by-month performance
- `ytd_metrics.json` - Year-to-date statistics
- `all_trades.csv` - Individual trade details
- `backtest_summary.md` - Performance report

## ⚠️ Risk Disclaimers

### CRITICAL WARNINGS
1. **Paper Trade First**: Minimum 30-60 days paper trading required
2. **No Performance Guarantees**: Past results do not predict future performance
3. **Real Money Risk**: You can lose your entire investment
4. **Your Own Analysis**: Run your own backtests with real data
5. **Start Small**: Begin with conservative position sizing (1%)

### Trading Risks
- Market volatility can cause significant losses
- Technical failures can result in missed exits
- Slippage and commissions reduce profits
- Strategy may underperform in certain market conditions

## ⚙️ Configuration Files

### Strategy Parameters
Configure your strategy in `configs/orb_config.json`:
- ORB period length
- Stop loss and take profit levels
- Position sizing rules
- Trading time windows
- Symbol selection

### Risk Profiles Available
- `orb_conservative_config.json` - 1% risk per trade
- `orb_balanced_config.json` - 2% risk per trade
- `orb_growth_config.json` - 3% risk per trade
- `orb_aggressive_config.json` - 5% risk per trade (HIGH RISK)

## 🔧 Technical Features

### Real-Time Execution
- Market order entries
- Stop-loss and profit target brackets
- Position monitoring
- Automatic end-of-day exits

### Risk Controls
- Maximum daily loss limits
- Position size constraints
- Consecutive loss protection
- Volatility-based adjustments

## 📝 Important Notes

### Before Trading
1. **Validate with YOUR data**: Run extensive backtests using your Polygon.io API
2. **Paper trade extensively**: Minimum 30-60 days recommended
3. **Start conservative**: Use 1% risk until proven profitable
4. **Monitor carefully**: Watch for strategy degradation
5. **Have an exit plan**: Know when to stop if strategy fails

### Best Practices
- Keep detailed trade logs
- Review performance weekly
- Adjust parameters based on market conditions
- Never trade money you can't afford to lose
- Consider tax implications of frequent trading

## 🛠️ Troubleshooting

### Connection Issues
- Verify TWS/Gateway is running
- Check port settings (7497 paper, 7496 live)
- Ensure API permissions enabled

### Data Issues
- Confirm Polygon API key is valid
- Check rate limits aren't exceeded
- Verify market hours for data requests

## 📄 License

MIT License - See LICENSE file for details

## ⚠️ FINAL WARNING

**This is experimental software for educational purposes. Trading involves substantial risk of loss. The developers are not responsible for any financial losses. There are no guarantees of profitability. Always start with paper trading and never risk money you cannot afford to lose.**

---

*Remember: Successful trading requires discipline, proper risk management, and continuous learning. This is a tool, not a magic money maker.*