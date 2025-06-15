#!/usr/bin/env python3
"""
Bitcoin Price Data Collector
----------------------------
This module fetches historical and real-time Bitcoin price data for the signal generation system.
"""

import os
import time
import json
import datetime
import pandas as pd
import numpy as np
import ccxt
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BitcoinDataCollector")

class BitcoinDataCollector:
    """
    Class to collect Bitcoin price data from various exchanges.
    """
    
    def __init__(self, exchange_id='binance', symbol='BTC/USDT', timeframe='1m', data_dir='data'):
        """
        Initialize the data collector.
        
        Args:
            exchange_id (str): Exchange ID (default: 'binance')
            symbol (str): Trading pair symbol (default: 'BTC/USDT')
            timeframe (str): Candle timeframe (default: '1m')
            data_dir (str): Directory to store data (default: 'data')
        """
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.timeframe = timeframe
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        # Initialize exchange
        try:
            exchange_class = getattr(ccxt, exchange_id)
            self.exchange = exchange_class({
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',  # Use futures market
                }
            })
            logger.info(f"Successfully initialized {exchange_id} exchange")
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {e}")
            raise
    
    def fetch_historical_data(self, start_date, end_date=None):
        """
        Fetch historical OHLCV data for the specified period.
        
        Args:
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format. Defaults to current date.
            
        Returns:
            pandas.DataFrame: DataFrame with OHLCV data
        """
        if end_date is None:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
            
        start_timestamp = int(datetime.datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
        end_timestamp = int(datetime.datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
        
        logger.info(f"Fetching historical data from {start_date} to {end_date}")
        
        all_candles = []
        current_timestamp = start_timestamp
        
        try:
            while current_timestamp < end_timestamp:
                logger.info(f"Fetching data batch from timestamp {current_timestamp}")
                candles = self.exchange.fetch_ohlcv(
                    symbol=self.symbol,
                    timeframe=self.timeframe,
                    since=current_timestamp,
                    limit=1000  # Most exchanges limit to 1000 candles per request
                )
                
                if not candles:
                    break
                    
                all_candles.extend(candles)
                
                # Update timestamp for next batch
                current_timestamp = candles[-1][0] + 1
                
                # Respect rate limits
                time.sleep(self.exchange.rateLimit / 1000)
                
            # Convert to DataFrame
            df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Save to file
            filename = f"{self.data_dir}/historical_{self.symbol.replace('/', '_')}_{self.timeframe}_{start_date}_{end_date}.csv"
            df.to_csv(filename)
            logger.info(f"Saved historical data to {filename}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            raise
    
    def fetch_latest_data(self, limit=100):
        """
        Fetch the latest OHLCV data.
        
        Args:
            limit (int): Number of candles to fetch (default: 100)
            
        Returns:
            pandas.DataFrame: DataFrame with OHLCV data
        """
        try:
            logger.info(f"Fetching latest {limit} candles")
            candles = self.exchange.fetch_ohlcv(
                symbol=self.symbol,
                timeframe=self.timeframe,
                limit=limit
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Save to file
            current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.data_dir}/latest_{self.symbol.replace('/', '_')}_{self.timeframe}_{current_time}.csv"
            df.to_csv(filename)
            logger.info(f"Saved latest data to {filename}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching latest data: {e}")
            raise
    
    def stream_real_time_data(self, callback=None, interval=60):
        """
        Stream real-time data at specified intervals.
        
        Args:
            callback (callable, optional): Function to call with new data
            interval (int): Update interval in seconds (default: 60)
        """
        logger.info(f"Starting real-time data stream with {interval}s interval")
        
        try:
            while True:
                # Fetch latest candle
                candles = self.exchange.fetch_ohlcv(
                    symbol=self.symbol,
                    timeframe=self.timeframe,
                    limit=1
                )
                
                if candles:
                    candle = candles[0]
                    timestamp = pd.to_datetime(candle[0], unit='ms')
                    data = {
                        'timestamp': timestamp,
                        'open': candle[1],
                        'high': candle[2],
                        'low': candle[3],
                        'close': candle[4],
                        'volume': candle[5]
                    }
                    
                    logger.info(f"New data: {timestamp} - Close: {data['close']}")
                    
                    # Save to file
                    with open(f"{self.data_dir}/realtime_data.json", 'w') as f:
                        json.dump({
                            'timestamp': timestamp.isoformat(),
                            'data': {k: float(v) for k, v in data.items() if k != 'timestamp'}
                        }, f)
                    
                    # Call callback if provided
                    if callback and callable(callback):
                        callback(data)
                
                # Wait for next update
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Data streaming stopped by user")
        except Exception as e:
            logger.error(f"Error in data streaming: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    collector = BitcoinDataCollector()
    
    # Fetch one week of historical data
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    
    historical_data = collector.fetch_historical_data(start_date, end_date)
    print(f"Fetched {len(historical_data)} historical candles")
    
    # Fetch latest data
    latest_data = collector.fetch_latest_data(limit=100)
    print(f"Fetched {len(latest_data)} latest candles")
