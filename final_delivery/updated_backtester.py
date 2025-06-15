#!/usr/bin/env python3
"""
Updated Backtester Module
------------------------
This module implements backtesting functionality for the Bitcoin trading signal system
using the alternative data source.
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging
from alt_data_source import AlternativeDataCollector
from indicators import TechnicalIndicators
from signal_generator import SignalGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backtest.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Backtester")

class Backtester:
    """
    Class to backtest the Bitcoin trading signal strategy.
    """
    
    def __init__(self, data_dir='data', results_dir='backtest_results', data_source='cryptocompare'):
        """
        Initialize the backtester.
        
        Args:
            data_dir (str): Directory with price data (default: 'data')
            results_dir (str): Directory to store backtest results (default: 'backtest_results')
            data_source (str): Data source to use (default: 'cryptocompare')
        """
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.data_source = data_source
        
        # Create results directory if it doesn't exist
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            
        # Initialize components
        self.data_collector = AlternativeDataCollector(data_source=data_source, data_dir=data_dir)
        self.signal_generator = SignalGenerator(data_dir=data_dir)
        
        logger.info(f"Backtester initialized with {data_source} data source")
    
    def load_historical_data(self, start_date, end_date=None):
        """
        Load historical data for backtesting.
        
        Args:
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format
            
        Returns:
            pandas.DataFrame: DataFrame with historical data
        """
        try:
            # Try to fetch from data source
            data = self.data_collector.fetch_historical_data(start_date, end_date)
            logger.info(f"Loaded historical data from {start_date} to {end_date}")
            return data
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            
            # Check if we have cached data
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
                
            filename = f"{self.data_dir}/historical_BTC_USDT_1m_{start_date}_{end_date}.csv"
            
            if os.path.exists(filename):
                logger.info(f"Loading cached data from {filename}")
                return pd.read_csv(filename, index_col='timestamp', parse_dates=True)
            else:
                raise
    
    def run_backtest(self, data, initial_capital=10000.0):
        """
        Run backtest on historical data.
        
        Args:
            data (pandas.DataFrame): DataFrame with historical price data
            initial_capital (float): Initial capital for backtesting
            
        Returns:
            tuple: (results_df, performance_metrics)
        """
        logger.info(f"Running backtest with {len(data)} data points")
        
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
        Calculate performance metrics from backtest results.
        
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
        Plot backtest results.
        
        Args:
            results_df (pandas.DataFrame): DataFrame with backtest results
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
        ax1.set_title('Bitcoin Price and Trading Signals')
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
        filename = f"{self.results_dir}/backtest_results_{timestamp}.png"
        plt.savefig(filename)
        
        # Save metrics to file
        metrics_file = f"{self.results_dir}/backtest_metrics_{timestamp}.json"
        with open(metrics_file, 'w') as f:
            json.dump(performance_metrics, f, indent=2)
        
        logger.info(f"Saved backtest results to {filename} and {metrics_file}")
        
        return filename
    
    def run_parameter_optimization(self, data, parameter_grid):
        """
        Run parameter optimization using grid search.
        
        Args:
            data (pandas.DataFrame): DataFrame with historical price data
            parameter_grid (dict): Dictionary of parameter ranges to test
            
        Returns:
            tuple: (best_params, best_metrics)
        """
        logger.info("Running parameter optimization")
        
        best_metrics = None
        best_params = None
        
        # TODO: Implement grid search for parameter optimization
        
        return best_params, best_metrics

if __name__ == "__main__":
    # Example usage
    backtester = Backtester(data_source='cryptocompare')
    
    # Load one week of historical data
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    try:
        data = backtester.load_historical_data(start_date, end_date)
        
        # Run backtest
        results, trades, metrics = backtester.run_backtest(data)
        
        # Plot results
        plot_file = backtester.plot_results(results, trades, metrics)
        
        print(f"Backtest completed. Results saved to {plot_file}")
        print("\nPerformance Metrics:")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")
    except Exception as e:
        logger.error(f"Error in backtesting: {e}")
