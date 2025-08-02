#!/usr/bin/env python3
"""
ORB Trading System - Opening Range Breakout Strategy

Professional algorithmic trading system for Interactive Brokers.
Optimized for consistent returns with controlled risk management.

Features:
- Dynamic position sizing based on volatility and performance
- Automated risk management with circuit breakers
- Real-time market data integration
- Comprehensive trade logging and analytics
"""

import asyncio
import json
import logging
import os
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ib_insync import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/orb_optimized.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class OptimizedPosition:
    """Optimized position with dynamic risk management"""
    symbol: str
    entry_price: float
    stop_price: float
    target_price: float
    position_size: float
    shares: int
    entry_time: datetime
    risk_amount: float
    expected_reward: float
    volatility_factor: float


class ORBOptimizedTrader:
    """🎯 ORB Optimized Trading System - Final Implementation"""
    
    def __init__(self, config_file: str = 'configs/orb_aggressive_config.json', risk_profile: str = 'aggressive'):
        # Auto-select config based on risk profile
        if risk_profile:
            config_map = {
                'conservative': 'configs/orb_conservative_config.json',
                'balanced': 'configs/orb_balanced_config.json', 
                'growth': 'configs/orb_growth_config.json',
                'aggressive': 'configs/orb_aggressive_config.json'
            }
            if risk_profile in config_map:
                config_file = config_map[risk_profile]
        
        self.config = self._load_config(config_file)
        self.risk_profile = risk_profile or 'aggressive'
        self.ib = IB()
        self.account_value = 100000  # Default, will be updated from IB
        self.positions = {}
        self.daily_pnl = 0
        self.trade_count = 0
        self.consecutive_losses = 0
        self.daily_trades = 0
        self.current_drawdown = 0
        self.max_drawdown = 0
        self.vix_level = 20  # Default, will be updated
        
        # Performance tracking
        self.performance_metrics = {
            'daily_returns': [],
            'win_rate': 0,
            'total_trades': 0,
            'winning_trades': 0
        }
        
        # Create necessary directories
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data/trades', exist_ok=True)
        
        self.show_optimized_banner()
        
    def show_optimized_banner(self):
        """Show optimized system banner"""
        risk_info = {
            'conservative': {'risk': '2.0%', 'desc': 'Low Risk'},
            'balanced': {'risk': '3.0%', 'desc': 'Balanced Risk'},
            'growth': {'risk': '4.0%', 'desc': 'Growth Focus'},
            'aggressive': {'risk': '5.0%', 'desc': 'High Risk Mode'},
            'optimized': {'risk': '1.5%', 'desc': 'Original Strategy'}
        }
        
        info = risk_info.get(self.risk_profile, risk_info['aggressive'])
        
        print("🎯" + "="*70 + "🎯")
        print("                 ORB TRADING SYSTEM")
        print("🎯" + "="*70 + "🎯")
        print(f"🏆 PROFILE: {info['desc']}")
        print(f"⚡ Position Risk: {info['risk']} per trade")
        print("📊 Performance varies with market conditions")
        print(f"🔥 Strategy: 15min ORB, 5.6:1 R/R")
        if self.risk_profile == 'aggressive':
            print("🚀 MODO AGRESIVO: Máximas ganancias activadas")
        print()
        
    def _load_config(self, config_file: str) -> dict:
        """Load optimized configuration"""
        if not os.path.exists(config_file):
            logger.error(f"Config file not found: {config_file}")
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        logger.info(f"✅ Loaded optimized config: {config.get('system_name', 'ORB_OPTIMIZED')}")
        return config
    
    async def connect(self):
        """Connect to IB and update account information"""
        try:
            port = self.config['connection_settings']['ib_connection']['paper_port']
            await self.ib.connectAsync('127.0.0.1', port, clientId=10)
            
            # Get account value
            await asyncio.sleep(1)
            account_summary = self.ib.accountSummary()
            for item in account_summary:
                if item.tag == 'NetLiquidation':
                    self.account_value = float(item.value)
                    break
            
            logger.info(f"✅ Connected to IB - Account Value: ${self.account_value:,.2f}")
            
            # Subscribe to events
            self.ib.orderStatusEvent += self.on_order_status
            self.ib.execDetailsEvent += self.on_execution
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to IB: {e}")
            return False
    
    def calculate_position_size(self, symbol: str, entry_price: float, stop_price: float) -> Tuple[float, int]:
        """Calculate optimized position size based on dynamic rules"""
        
        # Base risk per trade
        base_risk_pct = self.config['position_sizing']['base_risk_per_trade']
        base_risk_amount = self.account_value * base_risk_pct
        
        # Volatility adjustment
        vix_adjustments = self.config['position_sizing']['volatility_adjustments']
        if self.vix_level < 20:
            vol_multiplier = vix_adjustments['vix_below_20']
        elif self.vix_level <= 30:
            vol_multiplier = vix_adjustments['vix_20_to_30']
        elif self.vix_level <= 40:
            vol_multiplier = vix_adjustments['vix_30_to_40']
        else:
            vol_multiplier = vix_adjustments['vix_above_40']
        
        # Performance adjustment
        perf_multiplier = 1.0
        if len(self.performance_metrics['daily_returns']) >= 5:
            recent_returns = self.performance_metrics['daily_returns'][-5:]
            avg_return = np.mean(recent_returns)
            if avg_return > 0.02:  # Good performance
                perf_multiplier = 1.1
            elif avg_return < -0.01:  # Poor performance
                perf_multiplier = 0.8
        
        # Consecutive loss adjustment
        if self.consecutive_losses >= 2:
            perf_multiplier *= 0.7
        elif self.consecutive_losses >= 3:
            perf_multiplier *= 0.5
        
        # Calculate final risk amount
        adjusted_risk = base_risk_amount * vol_multiplier * perf_multiplier
        
        # Calculate position size
        stop_distance = abs(entry_price - stop_price)
        shares = int(adjusted_risk / stop_distance)
        position_value = shares * entry_price
        
        # Apply maximum limits
        max_position_pct = self.config['position_sizing']['absolute_limits']['max_position_percentage']
        max_position_value = self.account_value * max_position_pct
        
        if position_value > max_position_value:
            shares = int(max_position_value / entry_price)
            position_value = shares * entry_price
        
        # Minimum position check
        min_position = self.config['position_sizing']['absolute_limits']['min_position_size']
        if position_value < min_position and shares > 0:
            shares = max(1, int(min_position / entry_price))
            position_value = shares * entry_price
        
        logger.info(f"📊 Position sizing for {symbol}:")
        logger.info(f"   Base risk: ${base_risk_amount:.2f}")
        logger.info(f"   Vol multiplier: {vol_multiplier:.2f} (VIX: {self.vix_level:.1f})")
        logger.info(f"   Perf multiplier: {perf_multiplier:.2f}")
        logger.info(f"   Final position: {shares} shares (${position_value:.2f})")
        
        return position_value, shares
    
    def check_risk_limits(self) -> bool:
        """Check if trading is allowed based on risk limits"""
        
        # Daily loss limit check
        daily_limits = self.config['risk_management']['loss_limits']['daily']
        daily_loss_pct = abs(self.daily_pnl) / self.account_value
        
        if daily_loss_pct >= daily_limits['tier_3_stop_trading']:
            logger.warning(f"🛑 Daily loss limit reached: {daily_loss_pct:.1%}")
            return False
        
        # Consecutive loss check
        max_consecutive = self.config['risk_management']['consecutive_loss_protection']['max_consecutive_losses']
        if self.consecutive_losses >= max_consecutive:
            logger.warning(f"🛑 Consecutive loss limit reached: {self.consecutive_losses}")
            return False
        
        # Maximum positions check
        active_strategy = 'beast_mode'  # Default to beast mode
        max_positions = self.config['strategy_parameters'][active_strategy]['max_simultaneous_positions']
        if len(self.positions) >= max_positions:
            logger.info(f"⚠️ Maximum positions reached: {len(self.positions)}/{max_positions}")
            return False
        
        # Daily trade limit check
        max_daily_trades = self.config['strategy_parameters'][active_strategy]['max_daily_trades']
        if self.daily_trades >= max_daily_trades:
            logger.info(f"⚠️ Daily trade limit reached: {self.daily_trades}/{max_daily_trades}")
            return False
        
        return True
    
    def check_market_conditions(self) -> bool:
        """Check if market conditions allow trading"""
        
        # VIX-based filters
        no_trading_conditions = self.config['market_condition_filters']['no_trading_conditions']
        
        if self.vix_level > 45 and 'vix_above_45' in no_trading_conditions:
            logger.warning(f"🛑 VIX too high for trading: {self.vix_level:.1f}")
            return False
        
        # Time-based filters
        current_time = datetime.now().time()
        market_open = time(9, 30)
        if current_time < time(9, 45) and 'market_open_first_15_minutes' in no_trading_conditions:
            return False
        
        if current_time > time(15, 30) and 'market_close_last_30_minutes' in no_trading_conditions:
            return False
        
        return True
    
    async def scan_for_opportunities(self) -> List[str]:
        """Scan for ORB opportunities in configured symbols"""
        
        active_strategy = 'beast_mode'  # Default strategy
        symbols = self.config['strategy_parameters'][active_strategy]['symbols']
        
        opportunities = []
        
        for symbol in symbols:
            if symbol in self.positions:
                continue  # Already have position
                
            try:
                # Get recent bars for ORB calculation
                contract = Stock(symbol, 'SMART', 'USD')
                orb_minutes = self.config['strategy_parameters'][active_strategy]['orb_minutes']
                
                bars = await self.ib.reqHistoricalDataAsync(
                    contract,
                    endDateTime='',
                    durationStr='1 D',
                    barSizeSetting='1 min',
                    whatToShow='TRADES',
                    useRTH=True
                )
                
                if bars and len(bars) >= orb_minutes:
                    # Calculate ORB levels
                    df = util.df(bars)
                    orb_bars = df.head(orb_minutes)
                    orb_high = orb_bars['high'].max()
                    orb_low = orb_bars['low'].min()
                    
                    # Check current price vs ORB levels
                    current_price = bars[-1].close
                    
                    # Check for breakout (simplified logic)
                    if current_price > orb_high * 1.001:  # Small buffer for noise
                        opportunities.append(symbol)
                        logger.info(f"🎯 ORB breakout detected: {symbol} @ ${current_price:.2f} (ORB High: ${orb_high:.2f})")
                
            except Exception as e:
                logger.warning(f"Error scanning {symbol}: {e}")
                continue
        
        return opportunities
    
    async def enter_position(self, symbol: str):
        """Enter optimized position with risk management"""
        
        if not self.check_risk_limits() or not self.check_market_conditions():
            return
        
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            ticker = self.ib.reqMktData(contract, '', False, False)
            await asyncio.sleep(0.5)  # Allow price to update
            
            if not ticker.last:
                logger.warning(f"No price data for {symbol}")
                return
            
            entry_price = ticker.last
            
            # Calculate levels based on strategy
            active_strategy = 'beast_mode'
            stop_loss_pct = self.config['strategy_parameters'][active_strategy]['stop_loss_pct']
            take_profit_pct = self.config['strategy_parameters'][active_strategy]['take_profit_pct']
            
            stop_price = entry_price * (1 + stop_loss_pct)  # stop_loss_pct is negative
            target_price = entry_price * (1 + take_profit_pct)
            
            # Calculate position size
            position_value, shares = self.calculate_position_size(symbol, entry_price, stop_price)
            
            if shares < 1:
                logger.warning(f"Position size too small for {symbol}")
                return
            
            # Create market order
            order = MarketOrder('BUY', shares)
            trade = self.ib.placeOrder(contract, order)
            
            # Store position info
            position = OptimizedPosition(
                symbol=symbol,
                entry_price=entry_price,
                stop_price=stop_price,
                target_price=target_price,
                position_size=position_value,
                shares=shares,
                entry_time=datetime.now(),
                risk_amount=abs(shares * (entry_price - stop_price)),
                expected_reward=shares * (target_price - entry_price),
                volatility_factor=self.vix_level / 20.0
            )
            
            self.positions[symbol] = {
                'position': position,
                'entry_trade': trade,
                'stop_order': None,
                'target_order': None
            }
            
            self.daily_trades += 1
            
            logger.info(f"🎯 ENTERED {symbol}: {shares} shares @ ${entry_price:.2f}")
            logger.info(f"   Stop: ${stop_price:.2f} | Target: ${target_price:.2f}")
            logger.info(f"   Risk: ${position.risk_amount:.2f} | Reward: ${position.expected_reward:.2f}")
            logger.info(f"   R/R Ratio: {position.expected_reward/position.risk_amount:.1f}:1")
            
            # Create bracket orders
            await self.create_bracket_orders(symbol, contract, position)
            
        except Exception as e:
            logger.error(f"Error entering position {symbol}: {e}")
    
    async def create_bracket_orders(self, symbol: str, contract: Contract, position: OptimizedPosition):
        """Create stop loss and take profit orders"""
        try:
            # Stop loss order
            stop_order = StopOrder('SELL', position.shares, position.stop_price)
            stop_trade = self.ib.placeOrder(contract, stop_order)
            
            # Take profit order  
            target_order = LimitOrder('SELL', position.shares, position.target_price)
            target_trade = self.ib.placeOrder(contract, target_order)
            
            # Update position with orders
            self.positions[symbol]['stop_order'] = stop_trade
            self.positions[symbol]['target_order'] = target_trade
            
            logger.info(f"✅ Bracket orders created for {symbol}")
            
        except Exception as e:
            logger.error(f"Error creating bracket orders for {symbol}: {e}")
    
    def on_order_status(self, trade: Trade):
        """Handle order status updates"""
        if trade.orderStatus.status == 'Filled':
            symbol = trade.contract.symbol
            
            logger.info(f"✅ Order filled: {symbol} "
                       f"{trade.order.action} {trade.orderStatus.filled} "
                       f"@ ${trade.orderStatus.avgFillPrice:.2f}")
    
    def on_execution(self, trade: Trade, fill: Fill):
        """Handle trade executions and P&L calculation"""
        symbol = trade.contract.symbol
        
        if symbol in self.positions:
            position_info = self.positions[symbol]
            position = position_info['position']
            
            # Check if this is an exit
            if (trade == position_info.get('stop_order') or 
                trade == position_info.get('target_order')):
                
                # Calculate P&L
                entry_price = position.entry_price
                exit_price = fill.execution.avgPrice
                shares = position.shares
                
                pnl = (exit_price - entry_price) * shares
                self.daily_pnl += pnl
                
                # Update performance metrics
                self.performance_metrics['total_trades'] += 1
                if pnl > 0:
                    self.performance_metrics['winning_trades'] += 1
                    self.consecutive_losses = 0
                else:
                    self.consecutive_losses += 1
                
                # Update win rate
                self.performance_metrics['win_rate'] = (
                    self.performance_metrics['winning_trades'] / 
                    self.performance_metrics['total_trades']
                )
                
                # Determine exit reason
                exit_reason = "TARGET" if trade == position_info.get('target_order') else "STOP"
                
                logger.info(f"💰 CLOSED {symbol} ({exit_reason}): P&L = ${pnl:.2f}")
                logger.info(f"   Daily P&L: ${self.daily_pnl:.2f}")
                logger.info(f"   Win Rate: {self.performance_metrics['win_rate']:.1%}")
                logger.info(f"   Consecutive Losses: {self.consecutive_losses}")
                
                # Cancel remaining order
                remaining_order = (position_info.get('target_order') if exit_reason == "STOP" 
                                 else position_info.get('stop_order'))
                if remaining_order:
                    try:
                        self.ib.cancelOrder(remaining_order.order)
                    except:
                        pass
                
                # Remove position
                del self.positions[symbol]
                
                # Save trade data
                self.save_trade_data(position, exit_price, pnl, exit_reason)
    
    def save_trade_data(self, position: OptimizedPosition, exit_price: float, pnl: float, exit_reason: str):
        """Save trade data for analysis"""
        trade_data = {
            'timestamp': datetime.now().isoformat(),
            'symbol': position.symbol,
            'entry_price': position.entry_price,
            'exit_price': exit_price,
            'stop_price': position.stop_price,
            'target_price': position.target_price,
            'shares': position.shares,
            'position_size': position.position_size,
            'pnl': pnl,
            'exit_reason': exit_reason,
            'hold_time_minutes': (datetime.now() - position.entry_time).total_seconds() / 60,
            'vix_level': position.volatility_factor * 20,
            'risk_amount': position.risk_amount,
            'expected_reward': position.expected_reward
        }
        
        # Save to daily file
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"data/trades/trades_{date_str}.json"
        
        # Load existing data or create new
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                trades = json.load(f)
        else:
            trades = []
        
        trades.append(trade_data)
        
        with open(filename, 'w') as f:
            json.dump(trades, f, indent=2)
    
    async def update_vix(self):
        """Update VIX level for volatility adjustments"""
        try:
            # In production, would get real VIX data
            # For now, simulate based on market conditions
            self.vix_level = np.random.normal(22, 5)  # Simplified simulation
            self.vix_level = max(10, min(50, self.vix_level))  # Clamp between 10-50
            
        except Exception as e:
            logger.warning(f"Error updating VIX: {e}")
    
    async def daily_reset(self):
        """Reset daily counters and limits"""
        # Save daily performance
        daily_return = self.daily_pnl / self.account_value
        self.performance_metrics['daily_returns'].append(daily_return)
        
        # Keep only last 30 days
        if len(self.performance_metrics['daily_returns']) > 30:
            self.performance_metrics['daily_returns'] = self.performance_metrics['daily_returns'][-30:]
        
        logger.info(f"📊 Daily Summary:")
        logger.info(f"   P&L: ${self.daily_pnl:.2f} ({daily_return:.2%})")
        logger.info(f"   Trades: {self.daily_trades}")
        logger.info(f"   Win Rate: {self.performance_metrics['win_rate']:.1%}")
        
        # Reset daily counters
        self.daily_pnl = 0
        self.daily_trades = 0
    
    async def run(self):
        """Main trading loop"""
        logger.info("🚀 Starting ORB Optimized Trader")
        
        if not await self.connect():
            return
        
        try:
            last_scan_time = datetime.now() - timedelta(minutes=5)
            last_day = datetime.now().date()
            
            while True:
                current_time = datetime.now()
                market_open = time(9, 30)
                market_close = time(16, 0)
                
                # Daily reset check
                if current_time.date() != last_day:
                    await self.daily_reset()
                    last_day = current_time.date()
                
                # Market hours check
                if current_time.time() < market_open:
                    logger.info("⏰ Waiting for market open...")
                    await asyncio.sleep(60)
                    continue
                
                if current_time.time() > market_close:
                    logger.info("🔔 Market closed")
                    break
                
                # Update market conditions
                await self.update_vix()
                
                # Scan for opportunities (every 5 minutes)
                if (current_time - last_scan_time).total_seconds() >= 300:
                    if self.check_market_conditions():
                        opportunities = await self.scan_for_opportunities()
                        
                        for symbol in opportunities:
                            if self.check_risk_limits():
                                await self.enter_position(symbol)
                            else:
                                break
                    
                    last_scan_time = current_time
                
                # Sleep before next iteration
                await asyncio.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("⏹️ Shutting down...")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up on shutdown"""
        logger.info("🧹 Cleaning up...")
        
        # Cancel any pending orders
        for symbol, position_info in self.positions.items():
            try:
                if position_info.get('stop_order'):
                    self.ib.cancelOrder(position_info['stop_order'].order)
                if position_info.get('target_order'):
                    self.ib.cancelOrder(position_info['target_order'].order)
            except:
                pass
        
        # Final daily summary
        await self.daily_reset()
        
        self.ib.disconnect()
        logger.info("✅ Cleanup complete")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ORB Trading System with Risk Profiles')
    parser.add_argument('--config', default='configs/orb_aggressive_config.json',
                       help='Configuration file path')
    parser.add_argument('--mode', choices=['paper', 'live'], default='paper',
                       help='Trading mode')
    parser.add_argument('--risk-profile', choices=['conservative', 'balanced', 'growth', 'aggressive'],
                       help='Risk profile (overrides config file)')
    
    args = parser.parse_args()
    
    # Risk profile information
    risk_info = {
        'conservative': {'risk': '2.0%'},
        'balanced': {'risk': '3.0%'},
        'growth': {'risk': '4.0%'},
        'aggressive': {'risk': '5.0%'}
    }
    
    print("🎯 ORB TRADING SYSTEM")
    print("=" * 50)
    if args.risk_profile:
        info = risk_info[args.risk_profile]
        print(f"🏆 Risk Profile: {args.risk_profile.upper()}")
        print(f"⚡ Position Risk: {info['risk']} per trade")
        print("📊 Performance depends on market conditions")
    else:
        print("🏆 Configuration: AGGRESSIVE MODE (Default)")
        print("⚡ Position Risk: 5.0% per trade")
        print("📊 Performance depends on market conditions")
    print(f"📊 Mode: {args.mode.upper()}")
    print()
    
    if args.mode == 'live':
        print("⚠️ WARNING: LIVE TRADING MODE")
        if args.risk_profile in ['growth', 'aggressive']:
            print(f"⚠️ HIGH RISK PROFILE: {args.risk_profile.upper()}")
            print("This will use larger position sizes!")
        response = input("Continue with real money? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled by user")
            return
    
    try:
        trader = ORBOptimizedTrader(args.config, args.risk_profile)
        asyncio.run(trader.run())
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        raise


if __name__ == "__main__":
    main()