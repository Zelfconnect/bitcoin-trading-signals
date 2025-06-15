#!/usr/bin/env python3
"""
Main Application
---------------
This is the main entry point for the Bitcoin Trading Signal System.
"""

import os
import time
import logging
import argparse
import schedule
from datetime import datetime
from data_collector import BitcoinDataCollector
from indicators import TechnicalIndicators
from signal_generator import SignalGenerator
from telegram_notifier import TelegramNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bitcoin_signals.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BitcoinSignals")

class BitcoinSignalSystem:
    """
    Main class for the Bitcoin Trading Signal System.
    """
    
    def __init__(self, config=None):
        """
        Initialize the Bitcoin Signal System.
        
        Args:
            config (dict, optional): Configuration parameters
        """
        self.config = config or {}
        
        # Create necessary directories
        os.makedirs('data', exist_ok=True)
        os.makedirs('signals', exist_ok=True)
        os.makedirs('config', exist_ok=True)
        
        # Initialize components
        self.data_collector = BitcoinDataCollector()
        self.signal_generator = SignalGenerator()
        self.telegram_notifier = TelegramNotifier()
        
        logger.info("Bitcoin Signal System initialized")
    
    def check_for_signals(self):
        """
        Check for trading signals and send notifications.
        """
        logger.info("Checking for trading signals")
        
        try:
            # Fetch latest data
            data = self.data_collector.fetch_latest_data(limit=100)
            
            # Generate signal
            signal = self.signal_generator.generate_signal(data)
            
            # Send notification if signal generated
            if signal:
                self.signal_generator.save_signal(signal)
                self.telegram_notifier.send_signal_notification(signal)
                logger.info(f"Generated and sent {signal['type']} signal")
            else:
                logger.info("No signal generated")
                
        except Exception as e:
            logger.error(f"Error checking for signals: {e}")
    
    def schedule_signal_checks(self):
        """
        Schedule signal checks for Dutch timezone preferences.
        Morning: 08:00-11:00 CET/CEST
        Evening: 17:00-19:00 CET/CEST
        
        Note: Schedule uses UTC times, so we adjust:
        - CET = UTC+1 (winter)
        - CEST = UTC+2 (summer)
        Using UTC times for year-round consistency.
        """
        # Morning signals (08:00-11:00 Dutch time = 06:00-09:00 UTC winter / 07:00-10:00 UTC summer)
        # Using 07:00-10:00 UTC to work in both seasons
        schedule.every().day.at("07:27").do(self.check_for_signals)  # 09:27 Dutch summer / 08:27 Dutch winter
        schedule.every().day.at("07:57").do(self.check_for_signals)  # 09:57 Dutch summer / 08:57 Dutch winter
        schedule.every().day.at("08:27").do(self.check_for_signals)  # 10:27 Dutch summer / 09:27 Dutch winter
        
        # Evening signals (17:00-19:00 Dutch time = 15:00-17:00 UTC winter / 16:00-18:00 UTC summer)
        # Using 16:00-18:00 UTC to work in both seasons
        schedule.every().day.at("16:27").do(self.check_for_signals)  # 18:27 Dutch summer / 17:27 Dutch winter
        schedule.every().day.at("16:57").do(self.check_for_signals)  # 18:57 Dutch summer / 17:57 Dutch winter
        schedule.every().day.at("17:27").do(self.check_for_signals)  # 19:27 Dutch summer / 18:27 Dutch winter
        
        logger.info("Signal checks scheduled for Dutch timezone (08:00-11:00 & 17:00-19:00 local time)")
    
    def run(self):
        """
        Run the Bitcoin Signal System.
        """
        logger.info("Starting Bitcoin Signal System")
        
        # Schedule signal checks
        self.schedule_signal_checks()
        
        # Run continuously
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Bitcoin Signal System stopped by user")
        except Exception as e:
            logger.error(f"Error in Bitcoin Signal System: {e}")
            raise

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description='Bitcoin Trading Signal System')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--backtest', action='store_true', help='Run backtesting')
    parser.add_argument('--check-now', action='store_true', help='Check for signals immediately')
    args = parser.parse_args()
    
    system = BitcoinSignalSystem()
    
    if args.test:
        logger.info("Running in test mode")
        system.check_for_signals()
    elif args.backtest:
        logger.info("Running backtesting")
        # This would call a backtesting module
        print("Backtesting not implemented yet")
    elif args.check_now:
        logger.info("Checking for signals immediately")
        system.check_for_signals()
    else:
        system.run()

if __name__ == "__main__":
    main()
