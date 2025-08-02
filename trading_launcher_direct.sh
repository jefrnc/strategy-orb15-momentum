#!/bin/bash

# Direct ORB Optimized Trading Launcher for Stream Deck
# Launches optimized system immediately in paper trading mode

osascript -e 'tell application "Terminal"
    activate
    set newTab to do script "cd /Users/Joseph/repos/ORB-15-Momentum && source /Users/Joseph/repos/ORB-15-Momentum/orb_env/bin/activate && echo \"🔥 ORB AGGRESSIVE MODE Starting...\" && echo \"⚠️  5% Position Risk - High Risk Mode\" && echo \"═══════════════════════════════════\" && echo \"Performance depends on market conditions\" && python3 /Users/Joseph/repos/ORB-15-Momentum/orb_trader.py --mode paper"
    set current settings of newTab to settings set "Pro"
end tell'