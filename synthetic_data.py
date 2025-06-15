#!/usr/bin/env python3
"""
Synthetic Data Generator
-----------------------
This module generates synthetic Bitcoin price data for testing and backtesting.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("synthetic_data.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SyntheticDataGenerator")

class SyntheticDataGenerator:
    """
    Class to generate synthetic Bitcoin price data.
    """
    
    def __init__(self, data_dir='data/synthetic'):
        """
        Initialize the synthetic data generator.
        
        Args:
            data_dir (str): Directory to store synthetic data (default: 'data/synthetic')
        """
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        logger.info("Synthetic data generator initialized")
    
    def generate_random_walk(self, start_price=50000, volatility=0.001, days=30, interval_minutes=1):
        """
        Generate synthetic price data using random walk.
        
        Args:
            start_price (float): Starting price (default: 50000)
            volatility (float): Price volatility (default: 0.001)
            days (int): Number of days to generate (default: 30)
            interval_minutes (int): Time interval in minutes (default: 1)
            
        Returns:
            pandas.DataFrame: DataFrame with synthetic OHLCV data
        """
        logger.info(f"Generating {days} days of synthetic data with {interval_minutes}-minute intervals")
        
        # Calculate number of intervals
        intervals = int(days * 24 * 60 / interval_minutes)
        
        # Generate timestamps
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        timestamps = [start_date + timedelta(minutes=i*interval_minutes) for i in range(intervals)]
        
        # Generate price data using random walk
        np.random.seed(42)  # For reproducibility
        returns = np.random.normal(0, volatility, intervals)
        price_factors = np.cumprod(1 + returns)
        closes = start_price * price_factors
        
        # Generate OHLCV data
        data = []
        for i in range(intervals):
            # Add some randomness to open, high, low
            if i == 0:
                open_price = start_price
            else:
                open_price = closes[i-1]
            
            close_price = closes[i]
            
            # High and low with some randomness
            price_range = abs(close_price - open_price) + (close_price * 0.001)
            high_price = max(open_price, close_price) + (price_range * np.random.random())
            low_price = min(open_price, close_price) - (price_range * np.random.random())
            
            # Volume with some correlation to price change
            volume = abs(close_price - open_price) * 10 * (1 + np.random.random())
            
            data.append({
                'timestamp': timestamps[i],
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        # Save to file
        filename = f"{self.data_dir}/synthetic_BTC_USDT_1m_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv"
        df.to_csv(filename)
        logger.info(f"Saved synthetic data to {filename}")
        
        return df
    
    def generate_realistic_price_action(self, start_price=50000, days=30, interval_minutes=1):
        """
        Generate more realistic synthetic price data with trends, volatility clusters, and patterns.
        
        Args:
            start_price (float): Starting price (default: 50000)
            days (int): Number of days to generate (default: 30)
            interval_minutes (int): Time interval in minutes (default: 1)
            
        Returns:
            pandas.DataFrame: DataFrame with synthetic OHLCV data
        """
        logger.info(f"Generating {days} days of realistic synthetic data with {interval_minutes}-minute intervals")
        
        # Calculate number of intervals
        intervals = int(days * 24 * 60 / interval_minutes)
        
        # Generate timestamps
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        timestamps = [start_date + timedelta(minutes=i*interval_minutes) for i in range(intervals)]
        
        # Parameters for price generation
        trend_strength = 0.0001  # Slight upward bias
        base_volatility = 0.001
        volatility_cluster_factor = 2.0
        
        # Generate price data with trends and volatility clusters
        np.random.seed(42)  # For reproducibility
        
        # Initialize arrays
        volatilities = np.ones(intervals) * base_volatility
        returns = np.zeros(intervals)
        closes = np.zeros(intervals)
        closes[0] = start_price
        
        # Generate volatility clusters
        for i in range(1, intervals):
            # Randomly increase volatility for clusters
            if np.random.random() < 0.01:  # 1% chance of volatility cluster
                volatilities[i:i+100] = base_volatility * volatility_cluster_factor
        
        # Generate returns with trends
        for i in range(1, intervals):
            # Add trend component
            trend = trend_strength * (1 + np.sin(i / 1000))
            
            # Add random component with current volatility
            random_component = np.random.normal(0, volatilities[i])
            
            # Combine for final return
            returns[i] = trend + random_component
            
            # Calculate price
            closes[i] = closes[i-1] * (1 + returns[i])
        
        # Generate OHLCV data
        data = []
        for i in range(intervals):
            # Add some randomness to open, high, low
            if i == 0:
                open_price = start_price
            else:
                open_price = closes[i-1]
            
            close_price = closes[i]
            
            # High and low with some randomness
            price_range = abs(close_price - open_price) + (close_price * volatilities[i])
            high_price = max(open_price, close_price) + (price_range * np.random.random())
            low_price = min(open_price, close_price) - (price_range * np.random.random())
            
            # Volume with correlation to price change and volatility
            volume = abs(close_price - open_price) * 10 * (1 + volatilities[i] * 100) * (1 + np.random.random())
            
            data.append({
                'timestamp': timestamps[i],
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        # Save to file
        filename = f"{self.data_dir}/realistic_BTC_USDT_1m_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv"
        df.to_csv(filename)
        logger.info(f"Saved realistic synthetic data to {filename}")
        
        return df
    
    def plot_synthetic_data(self, df, title="Synthetic Bitcoin Price Data"):
        """
        Plot synthetic price data.
        
        Args:
            df (pandas.DataFrame): DataFrame with synthetic price data
            title (str): Plot title
            
        Returns:
            str: Path to saved plot file
        """
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
        
        # Plot price
        ax1.plot(df.index, df['close'], label='Close Price', color='black')
        
        # Plot volume
        ax2.bar(df.index, df['volume'], color='blue', alpha=0.5)
        
        # Set titles and labels
        ax1.set_title(title)
        ax1.set_ylabel('Price (USDT)')
        ax1.grid(True)
        
        ax2.set_title('Volume')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Volume')
        ax2.grid(True)
        
        # Format x-axis
        fig.autofmt_xdate()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.data_dir}/synthetic_data_plot_{timestamp}.png"
        plt.savefig(filename)
        
        logger.info(f"Saved plot to {filename}")
        
        return filename

if __name__ == "__main__":
    # Example usage
    generator = SyntheticDataGenerator()
    
    # Generate random walk data
    random_walk_data = generator.generate_random_walk(days=30)
    generator.plot_synthetic_data(random_walk_data, "Random Walk Bitcoin Price Data")
    
    # Generate more realistic data
    realistic_data = generator.generate_realistic_price_action(days=30)
    generator.plot_synthetic_data(realistic_data, "Realistic Bitcoin Price Data")
    
    print(f"Generated {len(random_walk_data)} random walk data points")
    print(f"Generated {len(realistic_data)} realistic data points")
