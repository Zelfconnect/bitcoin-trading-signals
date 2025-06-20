#!/usr/bin/env python3
"""
Signal Generator Module
----------------------
This module implements the signal generation logic for the Bitcoin trading system.
"""

import os
import time
import json
import datetime
import pandas as pd
import numpy as np
import logging
from data_collector import BitcoinDataCollector
from indicators import TechnicalIndicators

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("signal_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SignalGenerator")

class SignalGenerator:
    """
    Class to generate trading signals based on technical indicators.
    """
    
    def __init__(self, data_dir='data', signal_dir='signals'):
        """
        Initialize the signal generator.
        
        Args:
            data_dir (str): Directory with price data (default: 'data')
            signal_dir (str): Directory to store signals (default: 'signals')
        """
        self.data_dir = data_dir
        self.signal_dir = signal_dir
        
        # Create signal directory if it doesn't exist
        if not os.path.exists(signal_dir):
            os.makedirs(signal_dir)
            
        # Initialize data collector
        self.data_collector = BitcoinDataCollector(data_dir=data_dir)
        
        # Initialize signal count for the day
        self.daily_signal_count = 0
        self.last_signal_date = None
        
        logger.info("Signal generator initialized")
    
    def check_buy_signal(self, data):
        """
        Check if a buy (call) signal should be generated.
        
        Args:
            data (pandas.DataFrame): DataFrame with price and indicator data
            
        Returns:
            bool: True if buy signal, False otherwise
        """
        # Get the latest data point
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Primary indicators check
        rsi_condition = previous['rsi'] < 30 and latest['rsi'] > 30
        bb_condition = latest['close'] <= latest['bb_lower']
        macd_condition = previous['macd'] < previous['macd_signal'] and latest['macd'] > latest['macd_signal']
        stoch_condition = (previous['stoch_k'] < previous['stoch_d'] and latest['stoch_k'] > latest['stoch_d'] and 
                          latest['stoch_k'] < 20 and latest['stoch_d'] < 20)
        
        # Volume check
        volume_increasing = latest['volume'] > data['volume'].rolling(window=5).mean().iloc[-1]
        
        # Ichimoku check
        ichimoku_condition = latest['close'] > latest['ichimoku_span_a'] or (
            previous['close'] < previous['ichimoku_span_a'] and latest['close'] > latest['ichimoku_span_a']
        )
        
        # Fibonacci check - simplified for implementation
        # In a real system, this would check if price is near a Fibonacci level
        fib_levels = TechnicalIndicators.calculate_fibonacci_retracement(data)
        close_price = latest['close']
        
        # Handle different return types (Series or ndarray)
        if hasattr(fib_levels, 'values'):
            fib_values = fib_levels.values
        else:
            fib_values = fib_levels
            
        fib_condition = any(abs(close_price - level) / close_price < 0.01 for level in fib_values)
        
        # Primary signal conditions
        primary_conditions = rsi_condition and bb_condition and macd_condition and stoch_condition
        
        # Secondary confirmation conditions
        secondary_conditions = [volume_increasing, ichimoku_condition, fib_condition]
        secondary_count = sum(secondary_conditions)
        
        # Signal strength classification
        if primary_conditions and secondary_count >= 2:
            signal_strength = "Strong"
            return True, signal_strength
        elif primary_conditions:
            signal_strength = "Moderate"
            return True, signal_strength
        else:
            return False, None
    
    def check_sell_signal(self, data):
        """
        Check if a sell (put) signal should be generated.
        
        Args:
            data (pandas.DataFrame): DataFrame with price and indicator data
            
        Returns:
            bool: True if sell signal, False otherwise
        """
        # Get the latest data point
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Primary indicators check
        rsi_condition = previous['rsi'] > 70 and latest['rsi'] < 70
        bb_condition = latest['close'] >= latest['bb_upper']
        macd_condition = previous['macd'] > previous['macd_signal'] and latest['macd'] < latest['macd_signal']
        stoch_condition = (previous['stoch_k'] > previous['stoch_d'] and latest['stoch_k'] < latest['stoch_d'] and 
                          latest['stoch_k'] > 80 and latest['stoch_d'] > 80)
        
        # Volume check
        volume_increasing = latest['volume'] > data['volume'].rolling(window=5).mean().iloc[-1]
        
        # Ichimoku check
        ichimoku_condition = latest['close'] < latest['ichimoku_span_a'] or (
            previous['close'] > previous['ichimoku_span_a'] and latest['close'] < latest['ichimoku_span_a']
        )
        
        # Fibonacci check - simplified for implementation
        # In a real system, this would check if price is near a Fibonacci level
        fib_levels = TechnicalIndicators.calculate_fibonacci_retracement(data)
        close_price = latest['close']
        
        # Handle different return types (Series or ndarray)
        if hasattr(fib_levels, 'values'):
            fib_values = fib_levels.values
        else:
            fib_values = fib_levels
            
        fib_condition = any(abs(close_price - level) / close_price < 0.01 for level in fib_values)
        
        # Primary signal conditions
        primary_conditions = rsi_condition and bb_condition and macd_condition and stoch_condition
        
        # Secondary confirmation conditions
        secondary_conditions = [volume_increasing, ichimoku_condition, fib_condition]
        secondary_count = sum(secondary_conditions)
        
        # Signal strength classification
        if primary_conditions and secondary_count >= 2:
            signal_strength = "Strong"
            return True, signal_strength
        elif primary_conditions:
            signal_strength = "Moderate"
            return True, signal_strength
        else:
            return False, None
    
    def calculate_risk_management(self, data, signal_type):
        """
        Calculate risk management parameters for a signal.
        
        Args:
            data (pandas.DataFrame): DataFrame with price and indicator data
            signal_type (str): 'BUY' or 'SELL'
            
        Returns:
            dict: Risk management parameters
        """
        latest = data.iloc[-1]
        
        # Calculate stop-loss
        atr = latest['atr']
        close_price = latest['close']
        
        if signal_type == 'BUY':
            technical_stop = close_price - (1.5 * atr)  # 1.5x ATR for volatility-based stop-loss
        else:  # SELL
            technical_stop = close_price + (1.5 * atr)
        
        # Position sizing
        base_position_size = 0.02  # 2% of capital
        
        # Adjust based on signal strength
        if signal_type == 'BUY':
            _, signal_strength = self.check_buy_signal(data)
        else:  # SELL
            _, signal_strength = self.check_sell_signal(data)
        
        if signal_strength == "Strong":
            adjusted_position_size = base_position_size
        else:  # Moderate
            adjusted_position_size = base_position_size * 0.75
        
        # Take-profit targets
        primary_target = close_price * (1.01 if signal_type == 'BUY' else 0.99)  # 1% profit
        secondary_target = close_price * (1.015 if signal_type == 'BUY' else 0.985)  # 1.5% profit
        
        return {
            'stop_loss': technical_stop,
            'position_size': adjusted_position_size,
            'primary_target': primary_target,
            'secondary_target': secondary_target,
            'signal_strength': signal_strength
        }
    
    def generate_signal(self, data):
        """
        Generate a trading signal based on the latest data.
        
        Args:
            data (pandas.DataFrame): DataFrame with price and indicator data
            
        Returns:
            dict: Signal data or None if no signal
        """
        # Check if we've already sent 6 signals today
        current_date = datetime.datetime.now().date()
        if self.last_signal_date != current_date:
            self.daily_signal_count = 0
            self.last_signal_date = current_date
        
        if self.daily_signal_count >= 6:
            logger.info("Maximum daily signal count reached (6)")
            return None
        
        # MODIFIED: Expanded time windows to cover more hours for better signal generation
        # Early morning: 03:00-12:00 UTC (04:00-13:00 Dutch time)
        # Extended evening: 15:00-20:00 UTC (16:00-21:00 Dutch time)  
        # Late night: 22:00-03:00 UTC (23:00-04:00 Dutch time) for active traders
        current_hour = datetime.datetime.utcnow().hour
        time_windows = [
            (3, 12),   # Early morning: 04:00-13:00 Dutch time
            (15, 20),  # Extended evening: 16:00-21:00 Dutch time
            (22, 24),  # Late night part 1: 23:00-00:00 Dutch time
            (0, 3)     # Late night part 2: 01:00-04:00 Dutch time (extended)
        ]
        
        in_time_window = False
        for start, end in time_windows:
            if start <= current_hour < end:
                in_time_window = True
                break
        
        if not in_time_window:
            logger.info(f"Current UTC hour {current_hour} is outside extended trading windows")
            return None
        
        # Add indicators to data
        data_with_indicators = TechnicalIndicators.add_all_indicators(data)
        
        # MODIFIED: More flexible signal generation - use scoring system instead of requiring ALL conditions
        buy_score = self._calculate_buy_score(data_with_indicators)
        sell_score = self._calculate_sell_score(data_with_indicators)
        
        # Generate signal if score is high enough (threshold: 2 out of 5 conditions for testing)
        if buy_score >= 2 and buy_score > sell_score:
            signal_type = "BUY"
            risk_params = self.calculate_risk_management(data_with_indicators, signal_type)
            
            # Determine strength based on score
            if buy_score >= 4:
                strength = "Strong"
            else:
                strength = "Moderate"
            
            signal = {
                'type': signal_type,
                'timestamp': datetime.datetime.now().isoformat(),
                'price': data_with_indicators['close'].iloc[-1],
                'expiry': '5 minutes',
                'stop_loss': risk_params['stop_loss'],
                'position_size': risk_params['position_size'],
                'target': risk_params['primary_target'],
                'conviction': strength,
                'score': f"{buy_score}/5"
            }
            
            self.daily_signal_count += 1
            logger.info(f"Generated BUY signal with score {buy_score}/5 ({self.daily_signal_count}/6 for today)")
            
            return signal
            
        elif sell_score >= 2 and sell_score > buy_score:
            signal_type = "SELL"
            risk_params = self.calculate_risk_management(data_with_indicators, signal_type)
            
            # Determine strength based on score
            if sell_score >= 4:
                strength = "Strong"
            else:
                strength = "Moderate"
            
            signal = {
                'type': signal_type,
                'timestamp': datetime.datetime.now().isoformat(),
                'price': data_with_indicators['close'].iloc[-1],
                'expiry': '5 minutes',
                'stop_loss': risk_params['stop_loss'],
                'position_size': risk_params['position_size'],
                'target': risk_params['primary_target'],
                'conviction': strength,
                'score': f"{sell_score}/5"
            }
            
            self.daily_signal_count += 1
            logger.info(f"Generated SELL signal with score {sell_score}/5 ({self.daily_signal_count}/6 for today)")
            
            return signal
        
        logger.info(f"No signal generated (buy_score: {buy_score}, sell_score: {sell_score})")
        return None
    
    def _calculate_buy_score(self, data):
        """Calculate buy signal score (0-5) based on multiple conditions."""
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        score = 0
        
        # 1. RSI oversold recovery (more flexible)
        if latest['rsi'] < 40 and latest['rsi'] > previous['rsi']:  # RSI improving from oversold
            score += 1
            
        # 2. Price near or below Bollinger Lower Band
        if latest['close'] <= latest['bb_lower'] * 1.01:  # Within 1% of lower band
            score += 1
            
        # 3. MACD improvement (more flexible)
        if latest['macd'] > previous['macd']:  # MACD improving
            score += 1
            
        # 4. Stochastic oversold (more flexible)
        if latest['stoch_k'] < 30 and latest['stoch_k'] > previous['stoch_k']:  # Improving from oversold
            score += 1
            
        # 5. Volume confirmation
        volume_avg = data['volume'].rolling(window=10).mean().iloc[-1]
        if latest['volume'] > volume_avg * 1.2:  # Volume 20% above average
            score += 1
            
        return score
    
    def _calculate_sell_score(self, data):
        """Calculate sell signal score (0-5) based on multiple conditions."""
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        score = 0
        
        # 1. RSI overbought decline (more flexible)
        if latest['rsi'] > 60 and latest['rsi'] < previous['rsi']:  # RSI declining from overbought
            score += 1
            
        # 2. Price near or above Bollinger Upper Band
        if latest['close'] >= latest['bb_upper'] * 0.99:  # Within 1% of upper band
            score += 1
            
        # 3. MACD deterioration (more flexible)
        if latest['macd'] < previous['macd']:  # MACD declining
            score += 1
            
        # 4. Stochastic overbought (more flexible)
        if latest['stoch_k'] > 70 and latest['stoch_k'] < previous['stoch_k']:  # Declining from overbought
            score += 1
            
        # 5. Volume confirmation
        volume_avg = data['volume'].rolling(window=10).mean().iloc[-1]
        if latest['volume'] > volume_avg * 1.2:  # Volume 20% above average
            score += 1
            
        return score
    
    def format_sms_message(self, signal):
        """
        Format a signal as an SMS message.
        
        Args:
            signal (dict): Signal data
            
        Returns:
            str: Formatted SMS message
        """
        return f"""
BITCOIN SIGNAL #{self.daily_signal_count}
Type: {signal['type']}
Time: {signal['timestamp']}
Expiry: {signal['expiry']}
Target: +1%
Stop-Loss: {signal['stop_loss']:.2f}
Position Size: {signal['position_size']*100:.1f}%
Conviction: {signal['conviction']}
        """.strip()
    
    def save_signal(self, signal):
        """
        Save a signal to file.
        
        Args:
            signal (dict): Signal data
        """
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.signal_dir}/signal_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(signal, f, indent=2)
            
        logger.info(f"Saved signal to {filename}")
        
        # Also save SMS format
        sms_filename = f"{self.signal_dir}/sms_{timestamp}.txt"
        with open(sms_filename, 'w') as f:
            f.write(self.format_sms_message(signal))
            
        logger.info(f"Saved SMS format to {sms_filename}")
    
    def run_signal_generation(self, interval=60):
        """
        Run continuous signal generation.
        
        Args:
            interval (int): Update interval in seconds (default: 60)
        """
        logger.info(f"Starting signal generation with {interval}s interval")
        
        try:
            while True:
                # Fetch latest data
                data = self.data_collector.fetch_latest_data(limit=100)
                
                # Generate signal
                signal = self.generate_signal(data)
                
                # Save and send signal if generated
                if signal:
                    self.save_signal(signal)
                    # In a real system, this would send the SMS
                    # self.send_sms(self.format_sms_message(signal))
                
                # Wait for next update
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Signal generation stopped by user")
        except Exception as e:
            logger.error(f"Error in signal generation: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    generator = SignalGenerator()
    
    # Fetch some data for testing
    data = generator.data_collector.fetch_latest_data(limit=100)
    
    # Generate a signal
    signal = generator.generate_signal(data)
    
    if signal:
        print("Signal generated:")
        print(json.dumps(signal, indent=2))
        
        print("\nSMS format:")
        print(generator.format_sms_message(signal))
    else:
        print("No signal generated")
