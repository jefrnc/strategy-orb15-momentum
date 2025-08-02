# 📦 Installation Guide

## Prerequisites

- **Python**: 3.8 or higher
- **Interactive Brokers**: TWS or IB Gateway installed
- **Operating System**: macOS, Linux, or Windows
- **Capital**: Minimum $50,000 recommended for aggressive mode

## 🚀 Quick Install

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ORB-15-Momentum.git
cd ORB-15-Momentum
```

### 2. Create Virtual Environment
```bash
python3 -m venv orb_env
source orb_env/bin/activate  # On Windows: orb_env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env file with your settings (NEVER commit this file)
```

### 5. Interactive Brokers Setup
1. Open TWS or IB Gateway
2. Navigate to: File → Global Configuration → API → Settings
3. Enable: "Enable ActiveX and Socket Clients"
4. Enable: "Download open orders on connection"
5. Set Socket Port: 7497 (paper) or 7496 (live)
6. Add Trusted IP: 127.0.0.1

## 🔧 Configuration

### Required Environment Variables (.env)
```bash
# Market Data API (Optional - for backtesting)
POLYGON_API_KEY=your_polygon_api_key_here  # Get free at polygon.io

# Interactive Brokers Connection
ORB_IBKR_PORT=7497  # 7497 for paper, 7496 for live
ORB_IBKR_CLIENT_ID=10
```

### Risk Profile Selection
The system defaults to **AGGRESSIVE MODE (25.7% annual return)**

To use different risk profiles:
```bash
# Conservative (10.3% annual)
python3 orb_trader.py --risk-profile conservative --mode paper

# Balanced (16.0% annual)
python3 orb_trader.py --risk-profile balanced --mode paper

# Growth (20.7% annual)
python3 orb_trader.py --risk-profile growth --mode paper
```

## ✅ Verify Installation

### Test Connection
```bash
python3 -c "from ib_insync import IB; print('✅ ib_insync installed successfully')"
```

### Test Configuration
```bash
python3 orb_trader.py --help
```

### Paper Trading Test
```bash
# Make sure IB Gateway/TWS is running on port 7497
python3 orb_trader.py --mode paper
```

## 🐛 Troubleshooting

### Connection Issues
- **Error**: "Failed to connect to IB"
  - Ensure TWS/Gateway is running
  - Check port settings (7497 for paper)
  - Verify API permissions are enabled

### Module Import Errors
- **Error**: "No module named 'ib_insync'"
  - Activate virtual environment: `source orb_env/bin/activate`
  - Reinstall: `pip install -r requirements.txt`

### Permission Errors
- **macOS/Linux**: Use `chmod +x trading_launcher_*.sh` for launcher scripts
- **Windows**: Run PowerShell as Administrator

## 📱 Stream Deck Setup (Optional)

1. Install Stream Deck software
2. Create new button
3. Action: "Open" → File/URL
4. Target: `/path/to/ORB-15-Momentum/trading_launcher_direct.sh`
5. Icon: Use provided icons in `assets/` directory (if available)

## 🔒 Security Best Practices

1. **Never commit .env files** - Always use .env.example as template
2. **Use paper trading first** - Validate for at least 30 days
3. **Keep API credentials secure** - Use environment variables only
4. **Regular updates** - Keep dependencies updated with `pip install --upgrade -r requirements.txt`

## 📞 Support

- **Documentation**: See README.md and RISK_PROFILES.md
- **Issues**: Open issue on GitHub
- **Community**: Join discussions on GitHub

---

**Ready to trade? Start with paper mode to validate the system!** 🚀