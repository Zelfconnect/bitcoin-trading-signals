#!/usr/bin/env python3
"""
Alternative Data Source Module
-----------------------------
This module provides alternative data sources for Bitcoin price data.
"""

import os
import time
import json
import datetime
import pandas as pd
import numpy as np
import requests
import logging
import csv
from io import StringIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("alt_data_source.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AlternativeDataSource")

class CryptoCompareDataSource:
    """
    Class to collect Bitcoin price data from CryptoCompare API.
    """
    
    def __init__(self, data_dir='data'):
        """
        Initialize the data source.
        
        Args:
            data_dir (str): Directory to store data (default: 'data')
        """
        self.data_dir = data_dir
        self.base_url = "https://min-api.cryptocompare.com/data"
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        logger.info("CryptoCompare data source initialized")
    
    def fetch_historical_minute_data(self, symbol='BTC', to_symbol='USDT', limit=2000, to_ts=None):
        """
        Fetch historical minute OHLCV data.
        
        Args:
            symbol (str): Trading symbol (default: 'BTC')
            to_symbol (str): Quote currency (default: 'USDT')
            limit (int): Number of data points to fetch (max 2000)
            to_ts (int, optional): End timestamp in seconds
            
        Returns:
            pandas.DataFrame: DataFrame with OHLCV data
        """
        endpoint = f"{self.base_url}/histominute"
        
        params = {
            'fsym': symbol,
            'tsym': to_symbol,
            'limit': min(limit, 2000),  # API limit is 2000
            'aggregate': 1
        }
        
        if to_ts:
            params['toTs'] = to_ts
        
        try:
            logger.info(f"Fetching historical minute data for {symbol}/{to_symbol}")
            response = requests.get(endpoint, params=params)
            data = response.json()
            
            if data.get('Response') == 'Error':
                logger.error(f"API error: {data.get('Message')}")
                raise Exception(data.get('Message'))
            
            # Convert to DataFrame
            df = pd.DataFrame(data['Data'])
            df['timestamp'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('timestamp', inplace=True)
            
            # Rename columns to match our standard format
            df.rename(columns={
                'time': 'unix_time',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volumefrom': 'volume'
            }, inplace=True)
            
            # Keep only needed columns
            df = df[['unix_time', 'open', 'high', 'low', 'close', 'volume']]
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical minute data: {e}")
            raise
    
    def fetch_historical_data(self, start_date, end_date=None, symbol='BTC', to_symbol='USDT'):
        """
        Fetch historical OHLCV data for the specified period.
        
        Args:
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format. Defaults to current date.
            symbol (str): Trading symbol (default: 'BTC')
            to_symbol (str): Quote currency (default: 'USDT')
            
        Returns:
            pandas.DataFrame: DataFrame with OHLCV data
        """
        if end_date is None:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
            
        start_timestamp = int(datetime.datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_timestamp = int(datetime.datetime.strptime(end_date, '%Y-%m-%d').timestamp())
        
        logger.info(f"Fetching historical data from {start_date} to {end_date}")
        
        all_data = []
        current_timestamp = end_timestamp
        
        try:
            while current_timestamp > start_timestamp:
                logger.info(f"Fetching data batch with end timestamp {current_timestamp}")
                df = self.fetch_historical_minute_data(
                    symbol=symbol,
                    to_symbol=to_symbol,
                    limit=2000,
                    to_ts=current_timestamp
                )
                
                if df.empty:
                    break
                    
                all_data.append(df)
                
                # Update timestamp for next batch (oldest timestamp in current batch minus 1)
                current_timestamp = df['unix_time'].min() - 1
                
                # Respect rate limits
                time.sleep(0.5)
            
            # Combine all data
            if all_data:
                combined_df = pd.concat(all_data)
                combined_df = combined_df[~combined_df.index.duplicated(keep='first')]
                combined_df.sort_index(inplace=True)
                
                # Filter by date range
                combined_df = combined_df[(combined_df.index >= pd.Timestamp(start_date)) & 
                                         (combined_df.index <= pd.Timestamp(end_date) + pd.Timedelta(days=1))]
                
                # Save to file
                filename = f"{self.data_dir}/historical_{symbol}_{to_symbol}_1m_{start_date}_{end_date}.csv"
                combined_df.to_csv(filename)
                logger.info(f"Saved historical data to {filename}")
                
                return combined_df
            else:
                logger.warning("No data retrieved")
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            raise
    
    def fetch_latest_data(self, limit=100, symbol='BTC', to_symbol='USDT'):
        """
        Fetch the latest OHLCV data.
        
        Args:
            limit (int): Number of candles to fetch (default: 100)
            symbol (str): Trading symbol (default: 'BTC')
            to_symbol (str): Quote currency (default: 'USDT')
            
        Returns:
            pandas.DataFrame: DataFrame with OHLCV data
        """
        try:
            logger.info(f"Fetching latest {limit} candles for {symbol}/{to_symbol}")
            df = self.fetch_historical_minute_data(
                symbol=symbol,
                to_symbol=to_symbol,
                limit=limit
            )
            
            # Save to file
            current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.data_dir}/latest_{symbol}_{to_symbol}_1m_{current_time}.csv"
            df.to_csv(filename)
            logger.info(f"Saved latest data to {filename}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching latest data: {e}")
            raise
    
    def get_current_price(self, symbol='BTC', to_symbol='USDT'):
        """
        Get current price for a symbol.
        
        Args:
            symbol (str): Trading symbol (default: 'BTC')
            to_symbol (str): Quote currency (default: 'USDT')
            
        Returns:
            float: Current price
        """
        endpoint = f"{self.base_url}/price"
        
        params = {
            'fsym': symbol,
            'tsyms': to_symbol
        }
        
        try:
            response = requests.get(endpoint, params=params)
            data = response.json()
            
            if to_symbol in data:
                price = float(data[to_symbol])
                logger.info(f"Current {symbol}/{to_symbol} price: {price}")
                return price
            else:
                logger.error(f"Price data not found for {symbol}/{to_symbol}")
                raise Exception(f"Price data not found for {symbol}/{to_symbol}")
            
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            raise

class CoinGeckoDataSource:
    """
    Class to collect Bitcoin price data from CoinGecko API.
    """
    
    def __init__(self, data_dir='data'):
        """
        Initialize the data source.
        
        Args:
            data_dir (str): Directory to store data (default: 'data')
        """
        self.data_dir = data_dir
        self.base_url = "https://api.coingecko.com/api/v3"
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        logger.info("CoinGecko data source initialized")
    
    def get_coin_id(self, symbol):
        """
        Get coin ID from symbol.
        
        Args:
            symbol (str): Coin symbol (e.g., 'BTC')
            
        Returns:
            str: Coin ID
        """
        symbol = symbol.lower()
        
        # Common mappings
        mappings = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'usdt': 'tether',
            'bnb': 'binancecoin'
        }
        
        if symbol in mappings:
            return mappings[symbol]
        
        # Fetch from API if not in common mappings
        try:
            response = requests.get(f"{self.base_url}/coins/list")
            coins = response.json()
            
            for coin in coins:
                if coin['symbol'].lower() == symbol:
                    return coin['id']
            
            logger.error(f"Coin ID not found for symbol {symbol}")
            raise Exception(f"Coin ID not found for symbol {symbol}")
            
        except Exception as e:
            logger.error(f"Error getting coin ID: {e}")
            raise
    
    def fetch_historical_data(self, start_date, end_date=None, symbol='BTC', to_symbol='USD'):
        """
        Fetch historical OHLCV data for the specified period.
        
        Args:
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format. Defaults to current date.
            symbol (str): Trading symbol (default: 'BTC')
            to_symbol (str): Quote currency (default: 'USD')
            
        Returns:
            pandas.DataFrame: DataFrame with OHLCV data
        """
        if end_date is None:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
            
        start_timestamp = int(datetime.datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_timestamp = int(datetime.datetime.strptime(end_date, '%Y-%m-%d').timestamp() + 86400)  # Add one day
        
        logger.info(f"Fetching historical data from {start_date} to {end_date}")
        
        try:
            coin_id = self.get_coin_id(symbol)
            vs_currency = to_symbol.lower()
            
            endpoint = f"{self.base_url}/coins/{coin_id}/market_chart/range"
            
            params = {
                'vs_currency': vs_currency,
                'from': start_timestamp,
                'to': end_timestamp
            }
            
            response = requests.get(endpoint, params=params)
            data = response.json()
            
            # Process price data
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            
            if not prices:
                logger.warning("No price data retrieved")
                return pd.DataFrame()
            
            # Create DataFrame
            df_prices = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df_prices['timestamp'] = pd.to_datetime(df_prices['timestamp'], unit='ms')
            
            df_volumes = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
            df_volumes['timestamp'] = pd.to_datetime(df_volumes['timestamp'], unit='ms')
            
            # Merge price and volume data
            df = pd.merge(df_prices, df_volumes, on='timestamp', how='outer')
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            # Resample to 1-minute intervals and forward fill
            df = df.resample('1min').ffill()
            
            # Create OHLCV format (approximation since CoinGecko only provides close prices)
            result_df = pd.DataFrame(index=df.index)
            result_df['close'] = df['price']
            result_df['open'] = df['price'].shift(1)
            result_df['high'] = df['price']
            result_df['low'] = df['price']
            result_df['volume'] = df['volume']
            
            # Fill NaN values in first row
            result_df['open'].fillna(result_df['close'], inplace=True)
            
            # Save to file
            filename = f"{self.data_dir}/historical_{symbol}_{to_symbol}_1m_{start_date}_{end_date}.csv"
            result_df.to_csv(filename)
            logger.info(f"Saved historical data to {filename}")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            raise
    
    def fetch_latest_data(self, days=1, symbol='BTC', to_symbol='USD'):
        """
        Fetch the latest OHLCV data.
        
        Args:
            days (int): Number of days of data to fetch (default: 1)
            symbol (str): Trading symbol (default: 'BTC')
            to_symbol (str): Quote currency (default: 'USD')
            
        Returns:
            pandas.DataFrame: DataFrame with OHLCV data
        """
        try:
            logger.info(f"Fetching latest {days} days of data for {symbol}/{to_symbol}")
            
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
            
            df = self.fetch_historical_data(
                start_date=start_date,
                end_date=end_date,
                symbol=symbol,
                to_symbol=to_symbol
            )
            
            # Get the most recent data points
            latest_df = df.tail(100)  # Get last 100 minutes
            
            # Save to file
            current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.data_dir}/latest_{symbol}_{to_symbol}_1m_{current_time}.csv"
            latest_df.to_csv(filename)
            logger.info(f"Saved latest data to {filename}")
            
            return latest_df
            
        except Exception as e:
            logger.error(f"Error fetching latest data: {e}")
            raise
    
    def get_current_price(self, symbol='BTC', to_symbol='USD'):
        """
        Get current price for a symbol.
        
        Args:
            symbol (str): Trading symbol (default: 'BTC')
            to_symbol (str): Quote currency (default: 'USD')
            
        Returns:
            float: Current price
        """
        try:
            coin_id = self.get_coin_id(symbol)
            vs_currency = to_symbol.lower()
            
            endpoint = f"{self.base_url}/simple/price"
            
            params = {
                'ids': coin_id,
                'vs_currencies': vs_currency
            }
            
            response = requests.get(endpoint, params=params)
            data = response.json()
            
            if coin_id in data and vs_currency in data[coin_id]:
                price = float(data[coin_id][vs_currency])
                logger.info(f"Current {symbol}/{to_symbol} price: {price}")
                return price
            else:
                logger.error(f"Price data not found for {symbol}/{to_symbol}")
                raise Exception(f"Price data not found for {symbol}/{to_symbol}")
            
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            raise

class AlternativeDataCollector:
    """
    Class to collect Bitcoin price data from alternative sources.
    """
    
    def __init__(self, data_source='cryptocompare', data_dir='data'):
        """
        Initialize the data collector.
        
        Args:
            data_source (str): Data source to use (default: 'cryptocompare')
            data_dir (str): Directory to store data (default: 'data')
        """
        self.data_dir = data_dir
        self.data_source_name = data_source.lower()
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        # Initialize data source
        if self.data_source_name == 'cryptocompare':
            self.data_source = CryptoCompareDataSource(data_dir=data_dir)
        elif self.data_source_name == 'coingecko':
            self.data_source = CoinGeckoDataSource(data_dir=data_dir)
        else:
            raise ValueError(f"Unsupported data source: {data_source}")
            
        logger.info(f"Alternative data collector initialized with {data_source} data source")
    
    def fetch_historical_data(self, start_date, end_date=None, symbol='BTC', to_symbol='USDT'):
        """
        Fetch historical OHLCV data for the specified period.
        
        Args:
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format. Defaults to current date.
            symbol (str): Trading symbol (default: 'BTC')
            to_symbol (str): Quote currency (default: 'USDT')
            
        Returns:
            pandas.DataFrame: DataFrame with OHLCV data
        """
        return self.data_source.fetch_historical_data(
            start_date=start_date,
            end_date=end_date,
            symbol=symbol,
            to_symbol=to_symbol
        )
    
    def fetch_latest_data(self, limit=100, symbol='BTC', to_symbol='USDT'):
        """
        Fetch the latest OHLCV data.
        
        Args:
            limit (int): Number of data points to fetch (default: 100)
            symbol (str): Trading symbol (default: 'BTC')
            to_symbol (str): Quote currency (default: 'USDT')
            
        Returns:
            pandas.DataFrame: DataFrame with OHLCV data
        """
        if self.data_source_name == 'cryptocompare':
            return self.data_source.fetch_latest_data(
                limit=limit,
                symbol=symbol,
                to_symbol=to_symbol
            )
        elif self.data_source_name == 'coingecko':
            # CoinGecko doesn't support direct limit, so we fetch by days and take the last 'limit' points
            days = max(1, limit // 1440)  # Convert minutes to days, minimum 1 day
            df = self.data_source.fetch_latest_data(
                days=days,
                symbol=symbol,
                to_symbol=to_symbol
            )
            return df.tail(limit)
    
    def get_current_price(self, symbol='BTC', to_symbol='USDT'):
        """
        Get current price for a symbol.
        
        Args:
            symbol (str): Trading symbol (default: 'BTC')
            to_symbol (str): Quote currency (default: 'USDT')
            
        Returns:
            float: Current price
        """
        return self.data_source.get_current_price(
            symbol=symbol,
            to_symbol=to_symbol
        )

if __name__ == "__main__":
    # Example usage
    collector = AlternativeDataCollector(data_source='cryptocompare')
    
    # Fetch one day of historical data
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    historical_data = collector.fetch_historical_data(start_date, end_date)
    print(f"Fetched {len(historical_data)} historical data points")
    
    # Fetch latest data
    latest_data = collector.fetch_latest_data(limit=60)
    print(f"Fetched {len(latest_data)} latest data points")
    
    # Get current price
    current_price = collector.get_current_price()
    print(f"Current BTC/USDT price: {current_price}")
