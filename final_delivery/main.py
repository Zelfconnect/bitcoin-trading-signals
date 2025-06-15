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
from sms_notifier import SMSNotifier

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
        self.sms_notifier = SMSNotifier()
        
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
                self.sms_notifier.send_signal_notification(signal)
                logger.info(f"Generated and sent {signal['type']} signal")
            else:
                logger.info("No signal generated")
                
        except Exception as e:
            logger.error(f"Error checking for signals: {e}")
    
    def schedule_signal_checks(self):
        """
        Schedule signal checks according to the defined time windows.
        """
        # Schedule checks for each time window
        # Early Asian Session: 00:00-02:00 UTC
        schedule.every().day.at("00:30").do(self.check_for_signals)
        schedule.every().day.at("01:30").do(self.check_for_signals)
        
        # Late Asian Session: 04:00-06:00 UTC
        schedule.every().day.at("04:30").do(self.check_for_signals)
        schedule.every().day.at("05:30").do(self.check_for_signals)
        
        # European Session Opening: 08:00-10:00 UTC
        schedule.every().day.at("08:30").do(self.check_for_signals)
        schedule.every().day.at("09:30").do(self.check_for_signals)
        
        # European/US Overlap: 14:00-16:00 UTC
        schedule.every().day.at("14:30").do(self.check_for_signals)
        schedule.every().day.at("15:30").do(self.check_for_signals)
        
        # US Session: 18:00-20:00 UTC
        schedule.every().day.at("18:30").do(self.check_for_signals)
        schedule.every().day.at("19:30").do(self.check_for_signals)
        
        # Late US Session: 22:00-00:00 UTC
        schedule.every().day.at("22:30").do(self.check_for_signals)
        schedule.every().day.at("23:30").do(self.check_for_signals)
        
        logger.info("Signal checks scheduled")
    
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
