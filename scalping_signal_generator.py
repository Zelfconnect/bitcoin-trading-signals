#!/usr/bin/env python3
"""
Scalping Signal Generator Module
--------------------------------
Professional scalping signal generator that focuses on market conditions, not time.
Only generates signals when multiple strong conditions align.
"""

import os
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
        logging.FileHandler("scalping_signals.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ScalpingSignalGenerator")

class ScalpingSignalGenerator:
    """
    Professional scalping signal generator with strict entry conditions.
    """
    
    def __init__(self, data_dir='data', signal_dir='signals'):
        self.data_dir = data_dir
        self.signal_dir = signal_dir
        
        # Create directories
        os.makedirs(signal_dir, exist_ok=True)
        
        # Initialize data collector
        self.data_collector = BitcoinDataCollector(data_dir=data_dir)
        
        # Track last signal time to avoid overtrading
        self.last_signal_time = None
        self.min_time_between_signals = 300  # 5 minutes minimum between signals
        
        # Track recent signals for win/loss analysis
        self.recent_signals = []
        self.max_recent_signals = 20
        
        logger.info("Scalping Signal Generator initialized")
    
    def check_scalping_conditions_buy(self, data):
        """
        Check for high-probability BUY scalping opportunities.
        Requires multiple confirmations across different timeframes and indicators.
        """
        if len(data) < 100:
            return False, 0, []
        
        latest = data.iloc[-1]
        conditions_met = []
        
        # 1. MOMENTUM REVERSAL - RSI bounce from oversold
        rsi_reversal = False
        if latest['rsi'] < 35:  # Currently oversold
            # Check if RSI is starting to turn up
            rsi_slope = (latest['rsi'] - data['rsi'].iloc[-3]) / 2
            if rsi_slope > 0.5:  # RSI improving
                rsi_reversal = True
                conditions_met.append("RSI reversal from oversold")
        
        # 2. BOLLINGER BAND SQUEEZE & BOUNCE
        bb_squeeze = False
        bb_width = latest['bb_upper'] - latest['bb_lower']
        avg_bb_width = (data['bb_upper'] - data['bb_lower']).rolling(20).mean().iloc[-1]
        
        if bb_width < avg_bb_width * 0.7:  # Bands are squeezed
            if latest['close'] <= latest['bb_lower'] * 1.002:  # Price at lower band
                # Check for bounce pattern
                if data['close'].iloc[-2] < data['bb_lower'].iloc[-2] and latest['close'] > data['close'].iloc[-2]:
                    bb_squeeze = True
                    conditions_met.append("Bollinger Band squeeze bounce")
        
        # 3. VOLUME SPIKE - Smart money entering
        volume_spike = False
        current_volume = latest['volume']
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        
        if current_volume > avg_volume * 1.5:  # 50% above average
            # Check if price is holding despite selling
            if latest['close'] > data['close'].iloc[-3]:
                volume_spike = True
                conditions_met.append("Volume spike with price support")
        
        # 4. MACD MOMENTUM SHIFT
        macd_shift = False
        macd_histogram = latest['macd'] - latest['macd_signal']
        prev_histogram = data['macd'].iloc[-2] - data['macd_signal'].iloc[-2]
        
        if macd_histogram > prev_histogram and prev_histogram < 0:  # Histogram improving from negative
            if abs(macd_histogram) < abs(prev_histogram):  # Momentum shifting
                macd_shift = True
                conditions_met.append("MACD momentum shift")
        
        # 5. SUPPORT LEVEL BOUNCE
        support_bounce = False
        # Find recent support levels (local minima)
        recent_lows = data['low'].rolling(10).min()
        support_levels = recent_lows.unique()[-3:]  # Last 3 support levels
        
        for support in support_levels:
            if abs(latest['low'] - support) / support < 0.002:  # Within 0.2% of support
                if latest['close'] > latest['open']:  # Bullish candle at support
                    support_bounce = True
                    conditions_met.append(f"Support bounce at {support:.2f}")
                    break
        
        # 6. STOCHASTIC OVERSOLD REVERSAL
        stoch_reversal = False
        if latest['stoch_k'] < 20 and latest['stoch_d'] < 20:  # Both oversold
            if latest['stoch_k'] > latest['stoch_d'] and data['stoch_k'].iloc[-2] <= data['stoch_d'].iloc[-2]:
                stoch_reversal = True
                conditions_met.append("Stochastic oversold crossover")
        
        # 7. PRICE ACTION - Bullish reversal patterns
        price_pattern = False
        # Hammer pattern
        body = abs(latest['close'] - latest['open'])
        lower_wick = latest['open'] - latest['low'] if latest['close'] > latest['open'] else latest['close'] - latest['low']
        
        if lower_wick > body * 2 and latest['close'] > latest['open']:  # Bullish hammer
            price_pattern = True
            conditions_met.append("Bullish hammer pattern")
        
        # Calculate total score
        conditions = [rsi_reversal, bb_squeeze, volume_spike, macd_shift, 
                     support_bounce, stoch_reversal, price_pattern]
        score = sum(conditions)
        
        # Require at least 4 conditions for a signal
        return score >= 4, score, conditions_met
    
    def check_scalping_conditions_sell(self, data):
        """
        Check for high-probability SELL scalping opportunities.
        """
        if len(data) < 100:
            return False, 0, []
        
        latest = data.iloc[-1]
        conditions_met = []
        
        # 1. MOMENTUM EXHAUSTION - RSI decline from overbought
        rsi_exhaustion = False
        if latest['rsi'] > 65:  # Currently overbought
            # Check if RSI is starting to turn down
            rsi_slope = (latest['rsi'] - data['rsi'].iloc[-3]) / 2
            if rsi_slope < -0.5:  # RSI declining
                rsi_exhaustion = True
                conditions_met.append("RSI exhaustion from overbought")
        
        # 2. BOLLINGER BAND REJECTION
        bb_rejection = False
        if latest['close'] >= latest['bb_upper'] * 0.998:  # Price at upper band
            # Check for rejection pattern
            if data['high'].iloc[-2] > data['bb_upper'].iloc[-2] and latest['close'] < data['close'].iloc[-2]:
                bb_rejection = True
                conditions_met.append("Bollinger Band upper rejection")
        
        # 3. VOLUME SPIKE ON SELLING
        volume_selling = False
        current_volume = latest['volume']
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        
        if current_volume > avg_volume * 1.5:  # 50% above average
            # Check if price is falling with volume
            if latest['close'] < data['close'].iloc[-3]:
                volume_selling = True
                conditions_met.append("High volume selling pressure")
        
        # 4. MACD BEARISH CROSSOVER
        macd_bearish = False
        macd_histogram = latest['macd'] - latest['macd_signal']
        prev_histogram = data['macd'].iloc[-2] - data['macd_signal'].iloc[-2]
        
        if macd_histogram < prev_histogram and prev_histogram > 0:  # Histogram declining from positive
            if latest['macd'] < latest['macd_signal']:  # Bearish crossover
                macd_bearish = True
                conditions_met.append("MACD bearish crossover")
        
        # 5. RESISTANCE LEVEL REJECTION
        resistance_rejection = False
        # Find recent resistance levels (local maxima)
        recent_highs = data['high'].rolling(10).max()
        resistance_levels = recent_highs.unique()[-3:]  # Last 3 resistance levels
        
        for resistance in resistance_levels:
            if abs(latest['high'] - resistance) / resistance < 0.002:  # Within 0.2% of resistance
                if latest['close'] < latest['open']:  # Bearish candle at resistance
                    resistance_rejection = True
                    conditions_met.append(f"Resistance rejection at {resistance:.2f}")
                    break
        
        # 6. STOCHASTIC OVERBOUGHT REVERSAL
        stoch_overbought = False
        if latest['stoch_k'] > 80 and latest['stoch_d'] > 80:  # Both overbought
            if latest['stoch_k'] < latest['stoch_d'] and data['stoch_k'].iloc[-2] >= data['stoch_d'].iloc[-2]:
                stoch_overbought = True
                conditions_met.append("Stochastic overbought crossunder")
        
        # 7. PRICE ACTION - Bearish reversal patterns
        price_pattern = False
        # Shooting star pattern
        body = abs(latest['close'] - latest['open'])
        upper_wick = latest['high'] - latest['close'] if latest['close'] < latest['open'] else latest['high'] - latest['open']
        
        if upper_wick > body * 2 and latest['close'] < latest['open']:  # Bearish shooting star
            price_pattern = True
            conditions_met.append("Bearish shooting star pattern")
        
        # Calculate total score
        conditions = [rsi_exhaustion, bb_rejection, volume_selling, macd_bearish,
                     resistance_rejection, stoch_overbought, price_pattern]
        score = sum(conditions)
        
        # Require at least 4 conditions for a signal
        return score >= 4, score, conditions_met
    
    def calculate_signal_quality(self, score, conditions_met):
        """
        Determine signal quality based on score and conditions.
        """
        if score >= 6:
            return "VERY STRONG", 0.03  # 3% position size
        elif score >= 5:
            return "STRONG", 0.02  # 2% position size
        elif score >= 4:
            return "MODERATE", 0.01  # 1% position size
        else:
            return "WEAK", 0.005  # 0.5% position size
    
    def can_generate_signal(self):
        """
        Check if enough time has passed since last signal.
        """
        if self.last_signal_time is None:
            return True
        
        time_since_last = (datetime.datetime.now() - self.last_signal_time).total_seconds()
        return time_since_last >= self.min_time_between_signals
    
    def generate_scalping_signal(self, data):
        """
        Generate a scalping signal based on strict market conditions.
        """
        if not self.can_generate_signal():
            logger.info("Too soon since last signal, waiting...")
            return None
        
        # Add all indicators
        data_with_indicators = TechnicalIndicators.add_all_indicators(data)
        
        # Check both buy and sell conditions
        buy_signal, buy_score, buy_conditions = self.check_scalping_conditions_buy(data_with_indicators)
        sell_signal, sell_score, sell_conditions = self.check_scalping_conditions_sell(data_with_indicators)
        
        # Only generate signal if conditions are strong
        if buy_signal and buy_score > sell_score:
            quality, position_size = self.calculate_signal_quality(buy_score, buy_conditions)
            
            signal = {
                'type': 'BUY',
                'timestamp': datetime.datetime.now().isoformat(),
                'price': data_with_indicators['close'].iloc[-1],
                'score': f"{buy_score}/7",
                'quality': quality,
                'conditions': buy_conditions,
                'position_size': position_size,
                'stop_loss': data_with_indicators['close'].iloc[-1] * 0.995,  # 0.5% stop
                'take_profit': data_with_indicators['close'].iloc[-1] * 1.01,  # 1% target
                'expiry': '5 minutes',
                'indicators': {
                    'rsi': float(data_with_indicators['rsi'].iloc[-1]),
                    'macd': float(data_with_indicators['macd'].iloc[-1]),
                    'bb_position': 'lower' if data_with_indicators['close'].iloc[-1] < data_with_indicators['bb_lower'].iloc[-1] else 'middle',
                    'volume_ratio': float(data_with_indicators['volume'].iloc[-1] / data_with_indicators['volume'].rolling(20).mean().iloc[-1])
                }
            }
            
            self.last_signal_time = datetime.datetime.now()
            logger.info(f"Generated BUY signal with score {buy_score}/7 - {quality}")
            return signal
            
        elif sell_signal and sell_score > buy_score:
            quality, position_size = self.calculate_signal_quality(sell_score, sell_conditions)
            
            signal = {
                'type': 'SELL',
                'timestamp': datetime.datetime.now().isoformat(),
                'price': data_with_indicators['close'].iloc[-1],
                'score': f"{sell_score}/7",
                'quality': quality,
                'conditions': sell_conditions,
                'position_size': position_size,
                'stop_loss': data_with_indicators['close'].iloc[-1] * 1.005,  # 0.5% stop
                'take_profit': data_with_indicators['close'].iloc[-1] * 0.99,  # 1% target
                'expiry': '5 minutes',
                'indicators': {
                    'rsi': float(data_with_indicators['rsi'].iloc[-1]),
                    'macd': float(data_with_indicators['macd'].iloc[-1]),
                    'bb_position': 'upper' if data_with_indicators['close'].iloc[-1] > data_with_indicators['bb_upper'].iloc[-1] else 'middle',
                    'volume_ratio': float(data_with_indicators['volume'].iloc[-1] / data_with_indicators['volume'].rolling(20).mean().iloc[-1])
                }
            }
            
            self.last_signal_time = datetime.datetime.now()
            logger.info(f"Generated SELL signal with score {sell_score}/7 - {quality}")
            return signal
        
        logger.debug(f"No signal: BUY score={buy_score}, SELL score={sell_score}")
        return None
    
    def save_signal(self, signal):
        """
        Save signal with detailed information.
        """
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.signal_dir}/scalping_signal_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(signal, f, indent=2)
        
        # Track recent signals
        self.recent_signals.append(signal)
        if len(self.recent_signals) > self.max_recent_signals:
            self.recent_signals.pop(0)
        
        logger.info(f"Saved scalping signal to {filename}") 