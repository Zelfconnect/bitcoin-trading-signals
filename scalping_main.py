#!/usr/bin/env python3
"""
Scalping Main Application
------------------------
Continuous market monitoring for high-probability scalping signals.
No time-based triggers - only market condition based signals.
"""

import os
import time
import logging
import argparse
from datetime import datetime
from data_collector import BitcoinDataCollector
from scalping_signal_generator import ScalpingSignalGenerator
from telegram_notifier import TelegramNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scalping_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ScalpingSystem")

class ScalpingSystem:
    """
    Professional scalping system with continuous market monitoring.
    """
    
    def __init__(self, check_interval=30):
        """
        Initialize the scalping system.
        
        Args:
            check_interval (int): Seconds between market condition checks (default: 30)
        """
        self.check_interval = check_interval
        
        # Create necessary directories
        os.makedirs('data', exist_ok=True)
        os.makedirs('signals', exist_ok=True)
        os.makedirs('config', exist_ok=True)
        
        # Initialize components
        self.data_collector = BitcoinDataCollector()
        self.signal_generator = ScalpingSignalGenerator()
        self.telegram_notifier = TelegramNotifier()
        
        # Track statistics
        self.signals_sent_today = 0
        self.last_signal_date = None
        self.consecutive_losses = 0
        self.max_daily_signals = 10  # Reasonable limit to prevent overtrading
        
        logger.info(f"Scalping System initialized - checking every {check_interval} seconds")
    
    def format_telegram_message(self, signal):
        """
        Format signal for Telegram notification with all relevant details.
        """
        direction_emoji = "🟢" if signal['type'] == 'BUY' else "🔴"
        quality_emoji = {
            "VERY STRONG": "🔥🔥🔥",
            "STRONG": "🔥🔥",
            "MODERATE": "🔥",
            "WEAK": "⚠️"
        }.get(signal['quality'], "")
        
        conditions_text = "\n".join([f"✓ {cond}" for cond in signal['conditions']])
        
        message = f"""
{direction_emoji} **SCALPING SIGNAL - {signal['type']}** {quality_emoji}

📊 **Signal Quality**: {signal['quality']} ({signal['score']})
💰 **Entry Price**: ${signal['price']:,.2f}
🎯 **Target**: ${signal['take_profit']:,.2f} (+{((signal['take_profit']/signal['price'])-1)*100:.1f}%)
🛑 **Stop Loss**: ${signal['stop_loss']:,.2f} (-{(1-(signal['stop_loss']/signal['price']))*100:.1f}%)
⏱️ **Expiry**: {signal['expiry']}
💼 **Position Size**: {signal['position_size']*100:.1f}% of capital

📈 **Market Conditions Met**:
{conditions_text}

📊 **Key Indicators**:
• RSI: {signal['indicators']['rsi']:.1f}
• MACD: {signal['indicators']['macd']:.2f}
• BB Position: {signal['indicators']['bb_position']}
• Volume Ratio: {signal['indicators']['volume_ratio']:.1f}x avg

⚡ **Action**: Enter {signal['type']} position NOW
⏰ **Time**: {datetime.now().strftime('%H:%M:%S')}

_Signal #{self.signals_sent_today + 1} today_
        """
        
        return message.strip()
    
    def check_market_conditions(self):
        """
        Check current market conditions for scalping opportunities.
        """
        try:
            # Reset daily counter if new day
            current_date = datetime.now().date()
            if self.last_signal_date != current_date:
                self.signals_sent_today = 0
                self.last_signal_date = current_date
                self.consecutive_losses = 0
                logger.info("New trading day - counters reset")
            
            # Check daily limit
            if self.signals_sent_today >= self.max_daily_signals:
                logger.info(f"Daily signal limit reached ({self.max_daily_signals})")
                return
            
            # Stop if too many consecutive losses (circuit breaker)
            if self.consecutive_losses >= 3:
                logger.warning("Circuit breaker activated - 3 consecutive losses")
                return
            
            # Fetch latest market data
            logger.debug("Fetching latest market data...")
            data = self.data_collector.fetch_latest_data(limit=100)
            
            # Check for scalping signal
            signal = self.signal_generator.generate_scalping_signal(data)
            
            if signal:
                # Save signal
                self.signal_generator.save_signal(signal)
                
                # Send Telegram notification
                message = self.format_telegram_message(signal)
                self.telegram_notifier.send_signal_notification({
                    'message': message,
                    'parse_mode': 'Markdown'
                })
                
                self.signals_sent_today += 1
                logger.info(f"Sent {signal['type']} signal #{self.signals_sent_today} - {signal['quality']} quality")
                
                # Log signal details for analysis
                logger.info(f"Signal conditions: {', '.join(signal['conditions'])}")
                logger.info(f"Entry: ${signal['price']:,.2f}, Target: ${signal['take_profit']:,.2f}, Stop: ${signal['stop_loss']:,.2f}")
            else:
                logger.debug("No scalping opportunity detected")
                
        except Exception as e:
            logger.error(f"Error checking market conditions: {e}")
            # Don't crash the system - continue monitoring
    
    def run_continuous_monitoring(self):
        """
        Run continuous market monitoring for scalping opportunities.
        """
        logger.info("Starting continuous scalping monitor...")
        logger.info(f"Maximum {self.max_daily_signals} signals per day")
        logger.info(f"Minimum 5 minutes between signals")
        logger.info("Monitoring for high-probability setups only...")
        
        try:
            while True:
                self.check_market_conditions()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Scalping system stopped by user")
        except Exception as e:
            logger.error(f"Critical error in scalping system: {e}")
            raise
    
    def test_current_conditions(self):
        """
        Test current market conditions and show analysis.
        """
        logger.info("Testing current market conditions...")
        
        try:
            # Fetch data
            data = self.data_collector.fetch_latest_data(limit=100)
            
            # Add indicators
            from indicators import TechnicalIndicators
            data_with_indicators = TechnicalIndicators.add_all_indicators(data)
            
            # Check conditions
            buy_signal, buy_score, buy_conditions = self.signal_generator.check_scalping_conditions_buy(data_with_indicators)
            sell_signal, sell_score, sell_conditions = self.signal_generator.check_scalping_conditions_sell(data_with_indicators)
            
            latest = data_with_indicators.iloc[-1]
            
            print("\n" + "="*60)
            print("CURRENT MARKET ANALYSIS")
            print("="*60)
            print(f"Bitcoin Price: ${latest['close']:,.2f}")
            print(f"RSI: {latest['rsi']:.1f}")
            print(f"MACD: {latest['macd']:.2f}")
            print(f"Stochastic K/D: {latest['stoch_k']:.1f}/{latest['stoch_d']:.1f}")
            print(f"Volume Ratio: {latest['volume']/data_with_indicators['volume'].rolling(20).mean().iloc[-1]:.2f}x")
            
            print("\n" + "-"*60)
            print(f"BUY Signal Score: {buy_score}/7")
            if buy_conditions:
                print("BUY Conditions Met:")
                for cond in buy_conditions:
                    print(f"  ✓ {cond}")
            else:
                print("No BUY conditions met")
            
            print("\n" + "-"*60)
            print(f"SELL Signal Score: {sell_score}/7")
            if sell_conditions:
                print("SELL Conditions Met:")
                for cond in sell_conditions:
                    print(f"  ✓ {cond}")
            else:
                print("No SELL conditions met")
            
            print("\n" + "-"*60)
            if buy_score >= 4 or sell_score >= 4:
                print("🔥 SIGNAL WOULD BE GENERATED!")
                signal_type = "BUY" if buy_score > sell_score else "SELL"
                print(f"Signal Type: {signal_type}")
                print(f"Signal Score: {max(buy_score, sell_score)}/7")
            else:
                print("❌ No signal - conditions not strong enough")
                print(f"Need at least 4/7 conditions (currently BUY:{buy_score}, SELL:{sell_score})")
            
            print("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"Error in test: {e}")

def main():
    """
    Main entry point for scalping system.
    """
    parser = argparse.ArgumentParser(description='Professional Bitcoin Scalping System')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds (default: 30)')
    parser.add_argument('--test', action='store_true', help='Test current market conditions')
    parser.add_argument('--check-now', action='store_true', help='Check for signal immediately')
    args = parser.parse_args()
    
    system = ScalpingSystem(check_interval=args.interval)
    
    if args.test:
        system.test_current_conditions()
    elif args.check_now:
        logger.info("Checking for scalping signal immediately...")
        system.check_market_conditions()
    else:
        system.run_continuous_monitoring()

if __name__ == "__main__":
    main() 