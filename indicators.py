#!/usr/bin/env python3
"""
Technical Indicators Module
--------------------------
This module implements the technical indicators used in the Bitcoin trading signal system.
"""

import numpy as np
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("indicators.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TechnicalIndicators")

class TechnicalIndicators:
    """
    Class to calculate various technical indicators for the signal generation system.
    """
    
    @staticmethod
    def calculate_rsi(data, period=14):
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            data (pandas.DataFrame): DataFrame with price data
            period (int): RSI period (default: 14)
            
        Returns:
            pandas.Series: RSI values
        """
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(data, period=20, std_dev=2):
        """
        Calculate Bollinger Bands.
        
        Args:
            data (pandas.DataFrame): DataFrame with price data
            period (int): Moving average period (default: 20)
            std_dev (int): Number of standard deviations (default: 2)
            
        Returns:
            tuple: (middle_band, upper_band, lower_band)
        """
        middle_band = data['close'].rolling(window=period).mean()
        rolling_std = data['close'].rolling(window=period).std()
        
        upper_band = middle_band + (rolling_std * std_dev)
        lower_band = middle_band - (rolling_std * std_dev)
        
        return middle_band, upper_band, lower_band
    
    @staticmethod
    def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
        """
        Calculate Moving Average Convergence Divergence (MACD).
        
        Args:
            data (pandas.DataFrame): DataFrame with price data
            fast_period (int): Fast EMA period (default: 12)
            slow_period (int): Slow EMA period (default: 26)
            signal_period (int): Signal line period (default: 9)
            
        Returns:
            tuple: (macd_line, signal_line, histogram)
        """
        fast_ema = data['close'].ewm(span=fast_period, adjust=False).mean()
        slow_ema = data['close'].ewm(span=slow_period, adjust=False).mean()
        
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_stochastic(data, k_period=14, d_period=3):
        """
        Calculate Stochastic Oscillator.
        
        Args:
            data (pandas.DataFrame): DataFrame with price data
            k_period (int): %K period (default: 14)
            d_period (int): %D period (default: 3)
            
        Returns:
            tuple: (stoch_k, stoch_d)
        """
        low_min = data['low'].rolling(window=k_period).min()
        high_max = data['high'].rolling(window=k_period).max()
        
        stoch_k = 100 * ((data['close'] - low_min) / (high_max - low_min))
        stoch_d = stoch_k.rolling(window=d_period).mean()
        
        return stoch_k, stoch_d
    
    @staticmethod
    def calculate_volume_profile(data, price_bins=10):
        """
        Calculate Volume Profile.
        
        Args:
            data (pandas.DataFrame): DataFrame with price data
            price_bins (int): Number of price bins (default: 10)
            
        Returns:
            pandas.DataFrame: Volume profile data
        """
        min_price = data['low'].min()
        max_price = data['high'].max()
        
        # Create price bins
        bins = np.linspace(min_price, max_price, price_bins + 1)
        
        # Calculate volume for each price bin
        volume_profile = pd.DataFrame(index=range(len(bins) - 1))
        volume_profile['price_low'] = bins[:-1]
        volume_profile['price_high'] = bins[1:]
        volume_profile['volume'] = 0
        
        for i in range(len(data)):
            for j in range(len(bins) - 1):
                if data['low'].iloc[i] <= bins[j+1] and data['high'].iloc[i] >= bins[j]:
                    volume_profile.loc[j, 'volume'] += data['volume'].iloc[i]
        
        # Calculate support/resistance levels
        volume_profile['is_support_resistance'] = volume_profile['volume'] > volume_profile['volume'].mean()
        
        return volume_profile
    
    @staticmethod
    def calculate_ichimoku_cloud(data, conversion_period=9, base_period=26, lagging_span_period=52, displacement=26):
        """
        Calculate Ichimoku Cloud.
        
        Args:
            data (pandas.DataFrame): DataFrame with price data
            conversion_period (int): Conversion line period (default: 9)
            base_period (int): Base line period (default: 26)
            lagging_span_period (int): Lagging span period (default: 52)
            displacement (int): Displacement period (default: 26)
            
        Returns:
            tuple: (conversion_line, base_line, leading_span_a, leading_span_b, lagging_span)
        """
        # Conversion Line (Tenkan-sen)
        high_conversion = data['high'].rolling(window=conversion_period).max()
        low_conversion = data['low'].rolling(window=conversion_period).min()
        conversion_line = (high_conversion + low_conversion) / 2
        
        # Base Line (Kijun-sen)
        high_base = data['high'].rolling(window=base_period).max()
        low_base = data['low'].rolling(window=base_period).min()
        base_line = (high_base + low_base) / 2
        
        # Leading Span A (Senkou Span A)
        leading_span_a = ((conversion_line + base_line) / 2).shift(displacement)
        
        # Leading Span B (Senkou Span B)
        high_lagging = data['high'].rolling(window=lagging_span_period).max()
        low_lagging = data['low'].rolling(window=lagging_span_period).min()
        leading_span_b = ((high_lagging + low_lagging) / 2).shift(displacement)
        
        # Lagging Span (Chikou Span)
        lagging_span = data['close'].shift(-displacement)
        
        return conversion_line, base_line, leading_span_a, leading_span_b, lagging_span
    
    @staticmethod
    def calculate_fibonacci_retracement(data, window=100):
        """
        Calculate Fibonacci Retracement levels.
        
        Args:
            data (pandas.DataFrame): DataFrame with price data
            window (int): Window size for high/low calculation (default: 100)
            
        Returns:
            pandas.DataFrame: Fibonacci retracement levels
        """
        # Find swing high and swing low in the window
        high = data['high'].rolling(window=window).max().iloc[-1]
        low = data['low'].rolling(window=window).min().iloc[-1]
        
        # Calculate Fibonacci levels
        diff = high - low
        levels = {
            '0.0': low,
            '0.236': low + 0.236 * diff,
            '0.382': low + 0.382 * diff,
            '0.5': low + 0.5 * diff,
            '0.618': low + 0.618 * diff,
            '0.786': low + 0.786 * diff,
            '1.0': high
        }
        
        return pd.Series(levels)
    
    @staticmethod
    def calculate_atr(data, period=14):
        """
        Calculate Average True Range (ATR).
        
        Args:
            data (pandas.DataFrame): DataFrame with price data
            period (int): ATR period (default: 14)
            
        Returns:
            pandas.Series: ATR values
        """
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def add_all_indicators(data):
        """
        Add all technical indicators to the data.
        
        Args:
            data (pandas.DataFrame): DataFrame with OHLCV data
            
        Returns:
            pandas.DataFrame: DataFrame with added indicators
        """
        logger.info("Calculating all technical indicators")
        
        # Make a copy to avoid modifying the original
        df = data.copy()
        
        # RSI
        df['rsi'] = TechnicalIndicators.calculate_rsi(df)
        df['rsi_5m'] = TechnicalIndicators.calculate_rsi(df, period=5)
        
        # Bollinger Bands
        df['bb_middle'], df['bb_upper'], df['bb_lower'] = TechnicalIndicators.calculate_bollinger_bands(df)
        
        # MACD
        df['macd'], df['macd_signal'], df['macd_hist'] = TechnicalIndicators.calculate_macd(df)
        
        # Stochastic Oscillator
        df['stoch_k'], df['stoch_d'] = TechnicalIndicators.calculate_stochastic(df)
        
        # ATR for volatility-based stop-loss
        df['atr'] = TechnicalIndicators.calculate_atr(df)
        
        # Ichimoku Cloud
        df['ichimoku_conversion'], df['ichimoku_base'], df['ichimoku_span_a'], df['ichimoku_span_b'], df['ichimoku_lagging'] = TechnicalIndicators.calculate_ichimoku_cloud(df)
        
        logger.info("All indicators calculated successfully")
        
        return df
