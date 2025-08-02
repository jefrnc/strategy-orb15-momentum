#!/bin/bash

# ORB-15 Momentum Trading Launcher
# Enhanced launcher with environment checks and multiple options

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project paths
PROJECT_DIR="/Users/Joseph/repos/ORB-15-Momentum"
VENV_NAME="orb_env"
LOG_DIR="$PROJECT_DIR/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    print_message $RED "Error: Project directory not found at $PROJECT_DIR"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/$VENV_NAME" ]; then
    print_message $YELLOW "Virtual environment not found. Creating it now..."
    cd "$PROJECT_DIR"
    python3 -m venv $VENV_NAME
    source $VENV_NAME/bin/activate
    pip install -r requirements.txt
else
    print_message $GREEN "Virtual environment found."
fi

# Get command line argument for which script to run
SCRIPT_CHOICE=${1:-"menu"}

# Function to launch a script
launch_script() {
    local script_name=$1
    local script_desc=$2
    
    osascript -e "tell application \"Terminal\"
        activate
        set newTab to do script \"cd $PROJECT_DIR && source $VENV_NAME/bin/activate && echo '🚀 Launching $script_desc...' && python3 $script_name\"
        set current settings of newTab to settings set \"Pro\"
    end tell"
}

# Menu function
show_menu() {
    clear
    print_message $GREEN "═══════════════════════════════════════"
    print_message $GREEN "   🔥 ORB AGGRESSIVE SYSTEM LAUNCHER    "
    print_message $GREEN "═══════════════════════════════════════"
    echo ""
    print_message $YELLOW "🚀 MODO AGRESIVO POR DEFECTO (25.7% annual, 5% risk)"
    echo ""
    echo "Select an option:"
    echo "1) 🔥 Aggressive Mode (Paper) - DEFAULT (25.7% return)"
    echo "2) 🔥 Aggressive Mode (Live) - DEFAULT (25.7% return)"
    echo "3) 🛡️ Conservative Mode (10.3% return, 2% risk)"
    echo "4) ⚖️ Balanced Mode (16.0% return, 3% risk)"
    echo "5) 🚀 Growth Mode (20.7% return, 4% risk)"
    echo "6) 🔧 Advanced Options (Custom configs)"
    echo "7) 🧹 Clean Logs"
    echo "8) 📁 Open Terminal in Project"
    echo "0) Exit"
    echo ""
    read -p "Enter your choice [0-8]: " choice
    
    case $choice in
        1) launch_script "orb_trader.py --mode paper" "🔥 AGGRESSIVE MODE (Default - 25.7% return)";;
        2) print_message $YELLOW "⚠️ WARNING: AGGRESSIVE LIVE TRADING with real money!"
           print_message $YELLOW "25.7% return mode with 5% position risk!"
           read -p "Type 'BEAST' to proceed with aggressive live trading: " confirm
           if [ "$confirm" = "BEAST" ]; then
               launch_script "orb_trader.py --mode live" "🔥 AGGRESSIVE LIVE TRADING"
           else
               print_message $RED "Aggressive live trading cancelled"
               sleep 2
               show_menu
           fi;;
        3) launch_script "orb_trader.py --risk-profile conservative --mode paper" "Conservative Mode (10.3% return)";;
        4) launch_script "orb_trader.py --risk-profile balanced --mode paper" "Balanced Mode (16.0% return)";;
        5) launch_script "orb_trader.py --risk-profile growth --mode paper" "Growth Mode (20.7% return)";;
        6) print_message $GREEN "Advanced configuration options:"
           echo "  - Custom config files in configs/ directory"
           echo "  - Manual risk profile selection"
           echo "  - Original optimized mode available"
           read -p "Press Enter to continue..." dummy
           show_menu;;
        7) rm -rf logs/*.log && print_message $GREEN "Logs cleaned!" && sleep 1 && show_menu;;
        8) osascript -e "tell application \"Terminal\"
            activate
            do script \"cd $PROJECT_DIR && source $VENV_NAME/bin/activate && clear && echo '🔥 ORB AGGRESSIVE ENVIRONMENT ACTIVATED' && echo '════════════════════════════════════' && echo '' && echo 'DEFAULT: Aggressive Mode (25.7% annual return)' && echo '  python orb_trader.py --mode paper     # AGGRESSIVE (Default)' && echo '  python orb_trader.py --mode live      # AGGRESSIVE Live' && echo '' && echo 'Other Risk Profiles:' && echo '  python orb_trader.py --risk-profile conservative  # 10.3% return' && echo '  python orb_trader.py --risk-profile balanced      # 16.0% return' && echo '  python orb_trader.py --risk-profile growth        # 20.7% return' && echo ''\"
        end tell";;
        0) exit 0;;
        *) print_message $RED "Invalid option. Please try again."
           sleep 2
           show_menu;;
    esac
}

# Direct launch based on argument
case $SCRIPT_CHOICE in
    "paper")
        launch_script "orb_trader.py --mode paper" "ORB System (Paper)"
        ;;
    "live")
        launch_script "orb_trader.py --mode live" "ORB System (Live)"
        ;;
    "menu"|*)
        show_menu
        ;;
esac