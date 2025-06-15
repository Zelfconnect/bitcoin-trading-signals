#!/usr/bin/env python3
"""
Test With Synthetic Data
-----------------------
This module tests the Bitcoin trading signal system using synthetic data.
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging
from indicators import TechnicalIndicators
from signal_generator import SignalGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_synthetic.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SyntheticTester")

class SyntheticTester:
    """
    Class to test the Bitcoin trading signal system using synthetic data.
    """
    
    def __init__(self, data_dir='data/synthetic', results_dir='test_results'):
        """
        Initialize the synthetic tester.
        
        Args:
            data_dir (str): Directory with synthetic data (default: 'data/synthetic')
            results_dir (str): Directory to store test results (default: 'test_results')
        """
        self.data_dir = data_dir
        self.results_dir = results_dir
        
        # Create results directory if it doesn't exist
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            
        # Initialize signal generator
        self.signal_generator = SignalGenerator(data_dir=data_dir)
        
        logger.info("Synthetic tester initialized")
    
    def load_synthetic_data(self, filename=None):
        """
        Load synthetic data for testing.
        
        Args:
            filename (str, optional): Specific filename to load
            
        Returns:
            pandas.DataFrame: DataFrame with synthetic data
        """
        try:
            if filename:
                full_path = os.path.join(self.data_dir, filename)
            else:
                # Find the most recent synthetic data file
                files = [f for f in os.listdir(self.data_dir) if f.startswith('synthetic_') and f.endswith('.csv')]
                if not files:
                    raise FileNotFoundError("No synthetic data files found")
                
                # Sort by modification time (newest first)
                files.sort(key=lambda x: os.path.getmtime(os.path.join(self.data_dir, x)), reverse=True)
                full_path = os.path.join(self.data_dir, files[0])
            
            logger.info(f"Loading synthetic data from {full_path}")
            df = pd.read_csv(full_path, index_col='timestamp', parse_dates=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading synthetic data: {e}")
            raise
    
    def run_backtest(self, data, initial_capital=10000.0):
        """
        Run backtest on synthetic data.
        
        Args:
            data (pandas.DataFrame): DataFrame with synthetic price data
            initial_capital (float): Initial capital for backtesting
            
        Returns:
            tuple: (results_df, trades, performance_metrics)
        """
        logger.info(f"Running backtest with {len(data)} synthetic data points")
        
        # Add indicators
        data_with_indicators = TechnicalIndicators.add_all_indicators(data)
        
        # Initialize results
        results = []
        capital = initial_capital
        position = None
        trades = []
        
        # Set up time windows for signal generation (6 per day)
        time_windows = [
            (0, 2),    # Early Asian Session
            (4, 6),    # Late Asian Session
            (8, 10),   # European Session Opening
            (14, 16),  # European/US Overlap
            (18, 20),  # US Session
            (22, 0)    # Late US Session
        ]
        
        # Track daily signal count
        current_date = None
        daily_signal_count = 0
        
        # Process each data point
        for i in range(100, len(data_with_indicators)):  # Start after warmup period
            current_row = data_with_indicators.iloc[i]
            timestamp = data_with_indicators.index[i]
            
            # Check if we're in a new day
            if current_date != timestamp.date():
                current_date = timestamp.date()
                daily_signal_count = 0
            
            # Check if we're in a signal generation time window
            in_time_window = False
            current_hour = timestamp.hour
            for start, end in time_windows:
                if start <= current_hour < end or (start == 22 and (current_hour >= 22 or current_hour < 0)):
                    in_time_window = True
                    break
            
            # Skip if not in time window or already have 6 signals today
            if not in_time_window or daily_signal_count >= 6:
                continue
            
            # Check for signals
            window_data = data_with_indicators.iloc[i-100:i+1]
            
            # Check for buy signal
            buy_signal, buy_strength = self.signal_generator.check_buy_signal(window_data)
            
            # Check for sell signal
            sell_signal, sell_strength = self.signal_generator.check_sell_signal(window_data)
            
            # Execute trades based on signals
            if position is None:  # No active position
                if buy_signal and (not sell_signal or buy_strength == "Strong"):
                    # Generate buy signal
                    risk_params = self.signal_generator.calculate_risk_management(window_data, "BUY")
                    
                    # Calculate position size
                    position_size = capital * risk_params['position_size']
                    entry_price = current_row['close']
                    stop_loss = risk_params['stop_loss']
                    target = risk_params['primary_target']
                    
                    # Open position
                    position = {
                        'type': 'BUY',
                        'entry_time': timestamp,
                        'entry_price': entry_price,
                        'size': position_size,
                        'stop_loss': stop_loss,
                        'target': target,
                        'strength': risk_params['signal_strength']
                    }
                    
                    daily_signal_count += 1
                    logger.info(f"BUY signal at {timestamp} - Price: {entry_price}")
                    
                elif sell_signal and (not buy_signal or sell_strength == "Strong"):
                    # Generate sell signal
                    risk_params = self.signal_generator.calculate_risk_management(window_data, "SELL")
                    
                    # Calculate position size
                    position_size = capital * risk_params['position_size']
                    entry_price = current_row['close']
                    stop_loss = risk_params['stop_loss']
                    target = risk_params['primary_target']
                    
                    # Open position
                    position = {
                        'type': 'SELL',
                        'entry_time': timestamp,
                        'entry_price': entry_price,
                        'size': position_size,
                        'stop_loss': stop_loss,
                        'target': target,
                        'strength': risk_params['signal_strength']
                    }
                    
                    daily_signal_count += 1
                    logger.info(f"SELL signal at {timestamp} - Price: {entry_price}")
            
            elif position is not None:  # Active position
                # Check if 1 minute has passed (contract expiry)
                if timestamp >= position['entry_time'] + timedelta(minutes=1):
                    # Close position at current price
                    exit_price = current_row['close']
                    
                    # Calculate profit/loss
                    if position['type'] == 'BUY':
                        pnl = (exit_price - position['entry_price']) / position['entry_price'] * position['size']
                    else:  # SELL
                        pnl = (position['entry_price'] - exit_price) / position['entry_price'] * position['size']
                    
                    # Update capital
                    capital += pnl
                    
                    # Record trade
                    trade = {
                        'type': position['type'],
                        'entry_time': position['entry_time'],
                        'entry_price': position['entry_price'],
                        'exit_time': timestamp,
                        'exit_price': exit_price,
                        'size': position['size'],
                        'pnl': pnl,
                        'pnl_percent': pnl / position['size'] * 100,
                        'strength': position['strength']
                    }
                    trades.append(trade)
                    
                    logger.info(f"Closed {position['type']} position at {timestamp} - P&L: {pnl:.2f} ({trade['pnl_percent']:.2f}%)")
                    
                    # Reset position
                    position = None
            
            # Record results
            results.append({
                'timestamp': timestamp,
                'close': current_row['close'],
                'capital': capital,
                'position': position['type'] if position else None
            })
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(results)
        results_df.set_index('timestamp', inplace=True)
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(trades, initial_capital)
        
        return results_df, trades, performance_metrics
    
    def _calculate_performance_metrics(self, trades, initial_capital):
        """
        Calculate performance metrics from test results.
        
        Args:
            trades (list): List of trade dictionaries
            initial_capital (float): Initial capital
            
        Returns:
            dict: Performance metrics
        """
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'total_return': 0,
                'annualized_return': 0
            }
        
        # Calculate basic metrics
        total_trades = len(trades)
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        avg_profit = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        total_profit = sum([t['pnl'] for t in winning_trades]) if winning_trades else 0
        total_loss = sum([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        profit_factor = abs(total_profit / total_loss) if total_loss != 0 else float('inf')
        
        # Calculate equity curve
        equity_curve = [initial_capital]
        for trade in trades:
            equity_curve.append(equity_curve[-1] + trade['pnl'])
        
        # Calculate drawdown
        max_equity = initial_capital
        drawdowns = []
        
        for equity in equity_curve:
            if equity > max_equity:
                max_equity = equity
            drawdown = (max_equity - equity) / max_equity
            drawdowns.append(drawdown)
        
        max_drawdown = max(drawdowns) if drawdowns else 0
        
        # Calculate returns
        total_return = (equity_curve[-1] - initial_capital) / initial_capital
        
        # Calculate Sharpe ratio (simplified)
        returns = np.diff(equity_curve) / np.array(equity_curve[:-1])
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 0 and np.std(returns) > 0 else 0
        
        # Calculate annualized return (assuming 252 trading days)
        if trades:
            first_trade_date = trades[0]['entry_time']
            last_trade_date = trades[-1]['exit_time']
            trading_days = (last_trade_date - first_trade_date).days / 365 * 252
            
            if trading_days > 0:
                annualized_return = (1 + total_return) ** (252 / trading_days) - 1
            else:
                annualized_return = 0
        else:
            annualized_return = 0
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'total_return': total_return,
            'annualized_return': annualized_return
        }
    
    def plot_results(self, results_df, trades, performance_metrics):
        """
        Plot test results.
        
        Args:
            results_df (pandas.DataFrame): DataFrame with test results
            trades (list): List of trade dictionaries
            performance_metrics (dict): Performance metrics
            
        Returns:
            str: Path to saved plot file
        """
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1]})
        
        # Plot price
        ax1.plot(results_df.index, results_df['close'], label='BTC/USDT', color='black', alpha=0.7)
        
        # Plot buy and sell signals
        for trade in trades:
            if trade['type'] == 'BUY':
                ax1.scatter(trade['entry_time'], trade['entry_price'], marker='^', color='green', s=100)
                ax1.scatter(trade['exit_time'], trade['exit_price'], marker='o', color='blue', s=50)
            else:  # SELL
                ax1.scatter(trade['entry_time'], trade['entry_price'], marker='v', color='red', s=100)
                ax1.scatter(trade['exit_time'], trade['exit_price'], marker='o', color='blue', s=50)
        
        # Plot equity curve
        ax2.plot(results_df.index, results_df['capital'], label='Capital', color='blue')
        
        # Set titles and labels
        ax1.set_title('Bitcoin Price and Trading Signals (Synthetic Data)')
        ax1.set_ylabel('Price (USDT)')
        ax1.legend()
        ax1.grid(True)
        
        ax2.set_title('Equity Curve')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Capital (USDT)')
        ax2.grid(True)
        
        # Add performance metrics as text
        metrics_text = (
            f"Total Trades: {performance_metrics['total_trades']}\n"
            f"Win Rate: {performance_metrics['win_rate']:.2%}\n"
            f"Profit Factor: {performance_metrics['profit_factor']:.2f}\n"
            f"Max Drawdown: {performance_metrics['max_drawdown']:.2%}\n"
            f"Sharpe Ratio: {performance_metrics['sharpe_ratio']:.2f}\n"
            f"Total Return: {performance_metrics['total_return']:.2%}\n"
            f"Annualized Return: {performance_metrics['annualized_return']:.2%}"
        )
        
        fig.text(0.01, 0.01, metrics_text, fontsize=10, verticalalignment='bottom')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.results_dir}/test_results_{timestamp}.png"
        plt.savefig(filename)
        
        # Save metrics to file
        metrics_file = f"{self.results_dir}/test_metrics_{timestamp}.json"
        with open(metrics_file, 'w') as f:
            json.dump(performance_metrics, f, indent=2)
        
        logger.info(f"Saved test results to {filename} and {metrics_file}")
        
        return filename
    
    def analyze_signal_distribution(self, trades):
        """
        Analyze the distribution of signals throughout the day.
        
        Args:
            trades (list): List of trade dictionaries
            
        Returns:
            dict: Signal distribution analysis
        """
        if not trades:
            return {
                'signals_per_day': 0,
                'hour_distribution': {},
                'day_distribution': {},
                'strength_distribution': {}
            }
        
        # Extract timestamps and signal strengths
        timestamps = [trade['entry_time'] for trade in trades]
        strengths = [trade['strength'] for trade in trades]
        
        # Count signals per day
        days = set([ts.date() for ts in timestamps])
        signals_per_day = len(timestamps) / len(days) if days else 0
        
        # Count signals per hour
        hour_distribution = {}
        for ts in timestamps:
            hour = ts.hour
            hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
        
        # Count signals per day of week
        day_distribution = {}
        for ts in timestamps:
            day = ts.strftime('%A')  # Day name
            day_distribution[day] = day_distribution.get(day, 0) + 1
        
        # Count signals by strength
        strength_distribution = {}
        for strength in strengths:
            strength_distribution[strength] = strength_distribution.get(strength, 0) + 1
        
        return {
            'signals_per_day': signals_per_day,
            'hour_distribution': hour_distribution,
            'day_distribution': day_distribution,
            'strength_distribution': strength_distribution
        }
    
    def analyze_performance_by_time(self, trades):
        """
        Analyze performance by time of day.
        
        Args:
            trades (list): List of trade dictionaries
            
        Returns:
            dict: Performance by time analysis
        """
        if not trades:
            return {
                'hour_performance': {},
                'day_performance': {}
            }
        
        # Initialize performance by hour
        hour_performance = {}
        for hour in range(24):
            hour_performance[hour] = {
                'count': 0,
                'win_count': 0,
                'win_rate': 0,
                'avg_pnl': 0
            }
        
        # Initialize performance by day
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_performance = {}
        for day in days:
            day_performance[day] = {
                'count': 0,
                'win_count': 0,
                'win_rate': 0,
                'avg_pnl': 0
            }
        
        # Analyze trades
        for trade in trades:
            # Hour analysis
            hour = trade['entry_time'].hour
            hour_performance[hour]['count'] += 1
            if trade['pnl'] > 0:
                hour_performance[hour]['win_count'] += 1
            hour_performance[hour]['avg_pnl'] += trade['pnl']
            
            # Day analysis
            day = trade['entry_time'].strftime('%A')
            day_performance[day]['count'] += 1
            if trade['pnl'] > 0:
                day_performance[day]['win_count'] += 1
            day_performance[day]['avg_pnl'] += trade['pnl']
        
        # Calculate averages and win rates
        for hour, perf in hour_performance.items():
            if perf['count'] > 0:
                perf['win_rate'] = perf['win_count'] / perf['count']
                perf['avg_pnl'] = perf['avg_pnl'] / perf['count']
        
        for day, perf in day_performance.items():
            if perf['count'] > 0:
                perf['win_rate'] = perf['win_count'] / perf['count']
                perf['avg_pnl'] = perf['avg_pnl'] / perf['count']
        
        return {
            'hour_performance': hour_performance,
            'day_performance': day_performance
        }
    
    def generate_test_report(self, performance_metrics, signal_distribution, time_performance):
        """
        Generate a comprehensive test report.
        
        Args:
            performance_metrics (dict): Performance metrics
            signal_distribution (dict): Signal distribution analysis
            time_performance (dict): Performance by time analysis
            
        Returns:
            str: Path to saved report file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.results_dir}/test_report_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write("# Bitcoin Trading Signal System - Test Report\n\n")
            f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            f.write("## Performance Metrics\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            for key, value in performance_metrics.items():
                if isinstance(value, float):
                    if key in ['win_rate', 'total_return', 'annualized_return', 'max_drawdown']:
                        f.write(f"| {key.replace('_', ' ').title()} | {value:.2%} |\n")
                    else:
                        f.write(f"| {key.replace('_', ' ').title()} | {value:.4f} |\n")
                else:
                    f.write(f"| {key.replace('_', ' ').title()} | {value} |\n")
            
            f.write("\n## Signal Distribution\n\n")
            f.write(f"Average Signals Per Day: {signal_distribution['signals_per_day']:.2f}\n\n")
            
            f.write("### Distribution by Hour\n\n")
            f.write("| Hour | Count |\n")
            f.write("|------|-------|\n")
            for hour in sorted(signal_distribution['hour_distribution'].keys()):
                count = signal_distribution['hour_distribution'][hour]
                f.write(f"| {hour:02d}:00 | {count} |\n")
            
            f.write("\n### Distribution by Day\n\n")
            f.write("| Day | Count |\n")
            f.write("|-----|-------|\n")
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                count = signal_distribution['day_distribution'].get(day, 0)
                f.write(f"| {day} | {count} |\n")
            
            f.write("\n### Distribution by Signal Strength\n\n")
            f.write("| Strength | Count |\n")
            f.write("|----------|-------|\n")
            for strength, count in signal_distribution['strength_distribution'].items():
                f.write(f"| {strength} | {count} |\n")
            
            f.write("\n## Performance by Time\n\n")
            
            f.write("### Performance by Hour\n\n")
            f.write("| Hour | Count | Win Rate | Avg P&L |\n")
            f.write("|------|-------|----------|--------|\n")
            for hour in sorted(time_performance['hour_performance'].keys()):
                perf = time_performance['hour_performance'][hour]
                if perf['count'] > 0:
                    f.write(f"| {hour:02d}:00 | {perf['count']} | {perf['win_rate']:.2%} | {perf['avg_pnl']:.2f} |\n")
            
            f.write("\n### Performance by Day\n\n")
            f.write("| Day | Count | Win Rate | Avg P&L |\n")
            f.write("|-----|-------|----------|--------|\n")
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                perf = time_performance['day_performance'].get(day, {'count': 0, 'win_rate': 0, 'avg_pnl': 0})
                if perf['count'] > 0:
                    f.write(f"| {day} | {perf['count']} | {perf['win_rate']:.2%} | {perf['avg_pnl']:.2f} |\n")
            
            f.write("\n## Conclusion\n\n")
            
            # Generate conclusion based on performance
            win_rate = performance_metrics['win_rate']
            profit_factor = performance_metrics['profit_factor']
            total_return = performance_metrics['total_return']
            
            if win_rate >= 0.6 and profit_factor >= 1.5 and total_return > 0.1:
                conclusion = "The trading signal system demonstrates strong performance with a high win rate and good profit factor. The system is generating consistent profits and appears to be robust."
            elif win_rate >= 0.5 and profit_factor >= 1.2 and total_return > 0:
                conclusion = "The trading signal system shows moderate performance with an acceptable win rate and profit factor. The system is profitable but could benefit from further optimization."
            else:
                conclusion = "The trading signal system shows suboptimal performance. Further optimization and refinement are recommended before deployment."
            
            f.write(conclusion)
        
        logger.info(f"Generated test report: {filename}")
        
        return filename

if __name__ == "__main__":
    # Example usage
    tester = SyntheticTester()
    
    # Load synthetic data
    data = tester.load_synthetic_data()
    
    # Run backtest
    results, trades, metrics = tester.run_backtest(data)
    
    # Plot results
    plot_file = tester.plot_results(results, trades, metrics)
    
    # Analyze signal distribution
    signal_distribution = tester.analyze_signal_distribution(trades)
    
    # Analyze performance by time
    time_performance = tester.analyze_performance_by_time(trades)
    
    # Generate test report
    report_file = tester.generate_test_report(metrics, signal_distribution, time_performance)
    
    print(f"Test completed. Results saved to {plot_file}")
    print(f"Test report generated: {report_file}")
    print("\nPerformance Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")
