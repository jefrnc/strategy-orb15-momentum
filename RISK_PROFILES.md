# 📊 Risk Profiles Documentation

## ⚠️ IMPORTANT
All performance metrics must be generated from YOUR OWN backtesting with real Polygon.io historical data. Past performance does not guarantee future results.

## 🎯 Available Risk Profiles

The ORB Trading System offers multiple risk profiles to suit different trading styles and risk tolerances:

### 1. Conservative (2% Risk)
- **Position Risk**: 2% per trade
- **Target Audience**: Risk-averse traders
- **Focus**: Capital preservation
- **Recommended for**: Beginners

### 2. Balanced (3% Risk)
- **Position Risk**: 3% per trade
- **Target Audience**: Moderate risk tolerance
- **Focus**: Steady growth
- **Recommended for**: Experienced traders

### 3. Growth (4% Risk)
- **Position Risk**: 4% per trade
- **Target Audience**: Growth-oriented traders
- **Focus**: Higher returns with managed risk
- **Recommended for**: Experienced traders with larger accounts

### 4. Aggressive (5% Risk) - DEFAULT
- **Position Risk**: 5% per trade
- **Target Audience**: High risk tolerance
- **Focus**: Maximum returns
- **Recommended for**: Very experienced traders only
- **⚠️ WARNING**: High risk of significant losses

## 📐 Position Sizing Formula

```
Position Size = (Account Value × Risk %) / Stop Distance
```

Example:
- Account: $100,000
- Risk: 5% = $5,000
- Stop Distance: $1.00
- Position Size: 5,000 shares

## 🛡️ Risk Management Features

### Daily Loss Limits
- Conservative: 2% daily max loss
- Balanced: 3% daily max loss
- Growth: 4% daily max loss
- Aggressive: 5% daily max loss

### Circuit Breakers
- Consecutive loss protection
- Volatility-based position reduction
- Market condition filters
- Automatic daily stop

## 💻 Usage

### Command Line
```bash
# Conservative
python3 orb_trader.py --risk-profile conservative --mode paper

# Balanced
python3 orb_trader.py --risk-profile balanced --mode paper

# Growth
python3 orb_trader.py --risk-profile growth --mode paper

# Aggressive (Default)
python3 orb_trader.py --mode paper
```

### Configuration Files
- `configs/orb_conservative_config.json`
- `configs/orb_balanced_config.json`
- `configs/orb_growth_config.json`
- `configs/orb_aggressive_config.json`

## ⚠️ Risk Warnings

### CRITICAL CONSIDERATIONS
1. **Higher risk = Higher potential losses**
2. **5% risk can lead to 50%+ drawdowns**
3. **Always start with paper trading**
4. **Validate each profile for 30-60 days minimum**
5. **Past performance varies by market conditions**

### Account Size Recommendations
- Conservative: $25,000+ minimum
- Balanced: $30,000+ minimum
- Growth: $40,000+ minimum
- Aggressive: $50,000+ minimum

## 📊 Expected Outcomes

**IMPORTANT**: Actual returns depend on:
- Market conditions
- Strategy execution
- Timing of trades
- Symbol selection
- Overall market trends

**You must run your own backtests** to determine expected performance for your specific parameters and time period.

## 🔄 Switching Profiles

To change risk profiles:
1. Stop current trading
2. Update configuration
3. Paper trade new profile for validation
4. Only go live after successful validation

## 📝 Final Notes

- **Default is AGGRESSIVE**: Be aware of high risk
- **Start Conservative**: Work your way up
- **Monitor Daily**: Higher risk requires more attention
- **Have an Exit Plan**: Know when to stop if losing

Remember: The market can take away profits faster than it gives them. Always trade within your risk tolerance and never risk money you cannot afford to lose.