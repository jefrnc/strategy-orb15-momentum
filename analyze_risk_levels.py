#!/usr/bin/env python3
"""
Risk Level Analysis - Test different position sizes for higher returns
Compares risk levels from 1.5% to 6% per trade
"""

import json
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple
from dataclasses import dataclass
import copy

@dataclass
class RiskAnalysisResult:
    """Results for a specific risk level"""
    risk_pct: float
    total_trades: int
    win_rate: float
    total_pnl: float
    total_return_pct: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    max_monthly_loss: float
    final_account_value: float
    largest_loss: float
    consecutive_losses: int

class RiskLevelAnalyzer:
    """Analyze different risk levels for ORB strategy"""
    
    def __init__(self):
        # Load base backtest results from CSV (more reliable)
        self.trades_df = pd.read_csv('data/backtest_results/realistic_trades_2025.csv')
        
        # Risk levels to test
        self.risk_levels = [1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]
        
    def scale_trade_results(self, original_trades: List[Dict], risk_multiplier: float) -> List[Dict]:
        """Scale trade results for different risk levels"""
        scaled_trades = []
        
        for trade in original_trades:
            scaled_trade = trade.copy()
            
            # Scale shares and P&L proportionally
            original_shares = trade['shares']
            scaled_shares = int(original_shares * risk_multiplier)
            
            # Recalculate P&L with new share count
            price_change = trade['exit_price'] - trade['entry_price']
            raw_pnl = price_change * scaled_shares
            
            # Add commission (IBKR rates)
            commission = scaled_shares * 0.0035 + 0.35
            scaled_pnl = raw_pnl - commission
            
            scaled_trade['shares'] = scaled_shares
            scaled_trade['pnl'] = scaled_pnl
            scaled_trades.append(scaled_trade)
        
        return scaled_trades
    
    def calculate_risk_metrics(self, trades: List[Dict], risk_pct: float) -> RiskAnalysisResult:
        """Calculate comprehensive risk metrics"""
        if not trades:
            return RiskAnalysisResult(
                risk_pct=risk_pct, total_trades=0, win_rate=0, total_pnl=0,
                total_return_pct=0, annualized_return=0, max_drawdown=0,
                sharpe_ratio=0, max_monthly_loss=0, final_account_value=100000,
                largest_loss=0, consecutive_losses=0
            )
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t['pnl'] > 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_pnl = sum(t['pnl'] for t in trades)
        final_account = 100000 + total_pnl
        total_return_pct = (total_pnl / 100000) * 100
        
        # Monthly analysis for advanced metrics
        monthly_pnl = {}
        for trade in trades:
            month_key = trade['entry_date'][:7]  # YYYY-MM
            if month_key not in monthly_pnl:
                monthly_pnl[month_key] = 0
            monthly_pnl[month_key] += trade['pnl']
        
        monthly_returns = []
        running_account = 100000
        max_drawdown = 0
        peak_value = 100000
        
        for month_pnl in monthly_pnl.values():
            monthly_return = (month_pnl / running_account) * 100
            monthly_returns.append(monthly_return)
            running_account += month_pnl
            
            # Track drawdown
            if running_account > peak_value:
                peak_value = running_account
            else:
                drawdown = ((peak_value - running_account) / peak_value) * 100
                max_drawdown = max(max_drawdown, drawdown)
        
        # Risk metrics
        avg_monthly_return = np.mean(monthly_returns) if monthly_returns else 0
        monthly_volatility = np.std(monthly_returns) if len(monthly_returns) > 1 else 0
        annualized_return = avg_monthly_return * 12
        sharpe_ratio = (avg_monthly_return / monthly_volatility) if monthly_volatility > 0 else 0
        max_monthly_loss = min(monthly_returns) if monthly_returns else 0
        
        # Loss analysis
        losses = [t['pnl'] for t in trades if t['pnl'] < 0]
        largest_loss = min(losses) if losses else 0
        
        # Consecutive losses
        max_consecutive = 0
        current_consecutive = 0
        for trade in trades:
            if trade['pnl'] < 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return RiskAnalysisResult(
            risk_pct=risk_pct,
            total_trades=total_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            total_return_pct=total_return_pct,
            annualized_return=annualized_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            max_monthly_loss=max_monthly_loss,
            final_account_value=final_account,
            largest_loss=largest_loss,
            consecutive_losses=max_consecutive
        )
    
    def analyze_all_risk_levels(self) -> Dict[float, RiskAnalysisResult]:
        """Analyze all risk levels"""
        print("🎯 ANÁLISIS DE NIVELES DE RIESGO")
        print("=" * 60)
        print("Comparando diferentes tamaños de posición para maximizar retornos")
        print()
        
        # Convert DataFrame to list of dicts
        base_trades = self.trades_df.to_dict('records')
        base_risk = 1.5  # Current risk level
        results = {}
        
        for risk_pct in self.risk_levels:
            print(f"📊 Analizando riesgo {risk_pct}% por trade...")
            
            # Calculate risk multiplier
            risk_multiplier = risk_pct / base_risk
            
            # Scale trades
            scaled_trades = self.scale_trade_results(base_trades, risk_multiplier)
            
            # Calculate metrics
            result = self.calculate_risk_metrics(scaled_trades, risk_pct)
            results[risk_pct] = result
            
            print(f"   Retorno anualizado: {result.annualized_return:.1f}%")
            print(f"   Máximo drawdown: {result.max_drawdown:.1f}%")
            print(f"   Sharpe ratio: {result.sharpe_ratio:.2f}")
            print()
        
        return results
    
    def generate_comparison_report(self, results: Dict[float, RiskAnalysisResult]) -> str:
        """Generate detailed comparison report"""
        report = []
        report.append("🎯 ANÁLISIS COMPLETO DE NIVELES DE RIESGO")
        report.append("=" * 70)
        report.append("")
        
        # Summary table
        report.append("📊 COMPARACIÓN DE RETORNOS VS RIESGO")
        report.append("-" * 70)
        report.append(f"{'Risk %':<8} {'Annual %':<10} {'Drawdown %':<12} {'Sharpe':<8} {'Final $':<12}")
        report.append("-" * 70)
        
        for risk_pct, result in results.items():
            report.append(f"{risk_pct:<8.1f} {result.annualized_return:<10.1f} "
                         f"{result.max_drawdown:<12.1f} {result.sharpe_ratio:<8.2f} "
                         f"${result.final_account_value:<11,.0f}")
        
        report.append("")
        
        # Best options analysis
        best_return = max(results.values(), key=lambda x: x.annualized_return)
        best_sharpe = max(results.values(), key=lambda x: x.sharpe_ratio)
        safest_option = min(results.values(), key=lambda x: x.max_drawdown)
        
        report.append("🏆 MEJORES OPCIONES POR CRITERIO")
        report.append("-" * 40)
        report.append(f"🚀 Mayor retorno: {best_return.risk_pct}% riesgo → {best_return.annualized_return:.1f}% anual")
        report.append(f"⚡ Mejor Sharpe: {best_sharpe.risk_pct}% riesgo → {best_sharpe.sharpe_ratio:.2f} ratio")
        report.append(f"🛡️ Más seguro: {safest_option.risk_pct}% riesgo → {safest_option.max_drawdown:.1f}% drawdown")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMENDACIONES ESTRATÉGICAS")
        report.append("-" * 40)
        
        # Conservative
        conservative = results[2.0]
        report.append(f"🛡️ CONSERVADOR (2.0% riesgo):")
        report.append(f"   • Retorno anualizado: {conservative.annualized_return:.1f}%")
        report.append(f"   • Máximo drawdown: {conservative.max_drawdown:.1f}%")
        report.append(f"   • Recomendado para: Capital principal, bajo estrés")
        report.append("")
        
        # Balanced
        balanced = results[3.0]
        report.append(f"⚖️ BALANCEADO (3.0% riesgo):")
        report.append(f"   • Retorno anualizado: {balanced.annualized_return:.1f}%")
        report.append(f"   • Máximo drawdown: {balanced.max_drawdown:.1f}%")
        report.append(f"   • Recomendado para: Crecimiento estable, tolerancia media")
        report.append("")
        
        # Aggressive
        aggressive = results[5.0]
        report.append(f"🔥 AGRESIVO (5.0% riesgo):")
        report.append(f"   • Retorno anualizado: {aggressive.annualized_return:.1f}%")
        report.append(f"   • Máximo drawdown: {aggressive.max_drawdown:.1f}%")
        report.append(f"   • Recomendado para: Crecimiento acelerado, alta tolerancia")
        report.append("")
        
        # Risk warnings
        report.append("⚠️ CONSIDERACIONES DE RIESGO")
        report.append("-" * 40)
        high_risk = results[6.0]
        report.append(f"• Riesgo 6%: Drawdown hasta {high_risk.max_drawdown:.1f}% posible")
        report.append(f"• Mayor volatilidad = mayor estrés emocional")
        report.append(f"• Pérdida máxima individual: ${high_risk.largest_loss:.0f}")
        report.append(f"• Rachas de pérdidas: hasta {high_risk.consecutive_losses} consecutivas")
        report.append("")
        
        return "\n".join(report)
    
    def create_risk_configs(self, results: Dict[float, RiskAnalysisResult]):
        """Create configuration files for different risk levels"""
        print("📝 Creando configuraciones para diferentes niveles de riesgo...")
        
        # Load base config
        with open('configs/orb_optimized_config.json', 'r') as f:
            base_config = json.load(f)
        
        configs_to_create = [
            (2.0, "Conservative", "Retorno estable con bajo riesgo"),
            (3.0, "Balanced", "Balance óptimo entre retorno y riesgo"),
            (4.0, "Growth", "Crecimiento acelerado con riesgo moderado"),
            (5.0, "Aggressive", "Máximo crecimiento con alto riesgo")
        ]
        
        for risk_pct, name, description in configs_to_create:
            result = results[risk_pct]
            config = copy.deepcopy(base_config)
            
            # Update config
            config['system_name'] = f"ORB_{name.upper()}_SYSTEM"
            config['description'] = f"{description} - {result.annualized_return:.1f}% retorno anualizado"
            config['position_sizing']['base_risk_per_trade'] = risk_pct / 100
            
            # Add performance expectations
            config['expected_performance'] = {
                'annualized_return_pct': result.annualized_return,
                'max_drawdown_pct': result.max_drawdown,
                'sharpe_ratio': result.sharpe_ratio,
                'win_rate_pct': result.win_rate,
                'risk_level': name.lower()
            }
            
            # Save config
            filename = f"configs/orb_{name.lower()}_config.json"
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"   ✅ {filename} - {result.annualized_return:.1f}% anual")

def main():
    """Run risk level analysis"""
    print("🚀 Iniciando análisis de niveles de riesgo...")
    
    analyzer = RiskLevelAnalyzer()
    results = analyzer.analyze_all_risk_levels()
    
    # Generate report
    report = analyzer.generate_comparison_report(results)
    print(report)
    
    # Save detailed results
    os.makedirs('data/risk_analysis', exist_ok=True)
    
    # Save numerical results
    results_data = {}
    for risk_pct, result in results.items():
        results_data[str(risk_pct)] = {
            'risk_pct': result.risk_pct,
            'annualized_return': result.annualized_return,
            'max_drawdown': result.max_drawdown,
            'sharpe_ratio': result.sharpe_ratio,
            'total_return_pct': result.total_return_pct,
            'win_rate': result.win_rate,
            'final_account_value': result.final_account_value,
            'largest_loss': result.largest_loss,
            'consecutive_losses': result.consecutive_losses
        }
    
    with open('data/risk_analysis/risk_levels_comparison.json', 'w') as f:
        json.dump(results_data, f, indent=2)
    
    # Save report
    with open('data/risk_analysis/risk_analysis_report.txt', 'w') as f:
        f.write(report)
    
    # Create configuration files
    analyzer.create_risk_configs(results)
    
    print("\n" + "="*60)
    print("📁 RESULTADOS GUARDADOS:")
    print("• data/risk_analysis/risk_levels_comparison.json")
    print("• data/risk_analysis/risk_analysis_report.txt") 
    print("• configs/orb_[conservative|balanced|growth|aggressive]_config.json")
    print("\n✅ ANÁLISIS COMPLETO TERMINADO")
    
    return results

if __name__ == "__main__":
    main()