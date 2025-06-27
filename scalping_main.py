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
from datetime import datetime, timedelta
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
            check_interval (int): How often to check market conditions (seconds)
        """
        self.check_interval = check_interval
        self.max_daily_signals = 8  # Maximum signals per day
        self.signals_sent_today = 0
        self.last_signal_date = None
        self.consecutive_losses = 0
        self.circuit_breaker_notified = False  # Track if circuit breaker notification sent
        self.signal_history = []  # Store completed signals
        self.active_signals = []  # Store active signals for tracking
        
        # Initialize components
        self.data_collector = BitcoinDataCollector()
        self.signal_generator = ScalpingSignalGenerator()
        self.telegram_notifier = TelegramNotifier()
        
        # Create necessary directories
        os.makedirs('data', exist_ok=True)
        os.makedirs('signals', exist_ok=True)
        os.makedirs('config', exist_ok=True)
        
        logger.info(f"Scalping system initialized with {check_interval}s check interval")
    
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
    
    def check_signal_outcomes(self):
        """
        Check the outcome of active signals and update consecutive losses.
        """
        if not self.active_signals:
            return
        
        # Get current price
        try:
            current_data = self.data_collector.fetch_latest_data(limit=1)
            current_price = current_data['close'].iloc[-1]
            current_time = datetime.now()
        except Exception as e:
            logger.error(f"Error fetching current price for outcome check: {e}")
            return
        
        signals_to_remove = []
        
        for signal in self.active_signals:
            signal_time = datetime.fromisoformat(signal['timestamp'])
            time_elapsed = (current_time - signal_time).total_seconds()
            
            # Check if signal has expired (5 minutes for binary options)
            if time_elapsed >= 300:  # 5 minutes
                outcome = None
                
                if signal['type'] == 'BUY':
                    # For BUY: win if price went up
                    if current_price >= signal['take_profit']:
                        outcome = 'WIN'
                    elif current_price <= signal['stop_loss']:
                        outcome = 'LOSS'
                    else:
                        # Check if price is higher than entry
                        outcome = 'WIN' if current_price > signal['price'] else 'LOSS'
                else:  # SELL
                    # For SELL: win if price went down
                    if current_price <= signal['take_profit']:
                        outcome = 'WIN'
                    elif current_price >= signal['stop_loss']:
                        outcome = 'LOSS'
                    else:
                        # Check if price is lower than entry
                        outcome = 'WIN' if current_price < signal['price'] else 'LOSS'
                
                # Update consecutive losses
                if outcome == 'LOSS':
                    self.consecutive_losses += 1
                    logger.warning(f"Signal LOSS - consecutive losses: {self.consecutive_losses}")
                    
                    # Send loss notification
                    loss_message = f"❌ <b>SIGNAL OUTCOME - LOSS</b>\n\n"
                    loss_message += f"Signal: {signal['type']} at ${signal['price']:,.2f}\n"
                    loss_message += f"Current: ${current_price:,.2f}\n"
                    loss_message += f"Result: {((current_price/signal['price'])-1)*100:+.2f}%\n"
                    loss_message += f"Consecutive Losses: {self.consecutive_losses}/3"
                    
                    self.telegram_notifier.send_message(loss_message)
                else:  # WIN
                    self.consecutive_losses = 0  # Reset on win
                    logger.info(f"Signal WIN - consecutive losses reset to 0")
                    
                    # Send win notification
                    win_message = f"✅ <b>SIGNAL OUTCOME - WIN</b>\n\n"
                    win_message += f"Signal: {signal['type']} at ${signal['price']:,.2f}\n"
                    win_message += f"Current: ${current_price:,.2f}\n"
                    win_message += f"Result: {((current_price/signal['price'])-1)*100:+.2f}%"
                    
                    self.telegram_notifier.send_message(win_message)
                
                # Add outcome to signal and move to history
                signal['outcome'] = outcome
                signal['outcome_price'] = current_price
                signal['outcome_time'] = current_time.isoformat()
                self.signal_history.append(signal)
                signals_to_remove.append(signal)
                
                logger.info(f"Signal outcome: {outcome} - Entry: ${signal['price']:,.2f}, Exit: ${current_price:,.2f}")
        
        # Remove processed signals from active list
        for signal in signals_to_remove:
            self.active_signals.remove(signal)
    
    def check_market_conditions(self):
        """
        Check current market conditions for scalping opportunities.
        """
        try:
            # First check outcomes of any active signals
            self.check_signal_outcomes()
            
            # Reset daily counter if new day
            current_date = datetime.now().date()
            if self.last_signal_date != current_date:
                self.signals_sent_today = 0
                self.last_signal_date = current_date
                self.consecutive_losses = 0
                self.circuit_breaker_notified = False  # Reset circuit breaker notification
                logger.info("New trading day - counters reset")
            
            # Check daily limit
            if self.signals_sent_today >= self.max_daily_signals:
                logger.info(f"Daily signal limit reached ({self.max_daily_signals})")
                return
            
            # Stop if too many consecutive losses (circuit breaker)
            if self.consecutive_losses >= 3:
                if not self.circuit_breaker_notified:
                    logger.warning("Circuit breaker activated - 3 consecutive losses")
                    
                    # Send circuit breaker notification only once
                    cb_message = "🛑 <b>CIRCUIT BREAKER ACTIVATED</b>\n\n"
                    cb_message += "3 consecutive losses detected.\n"
                    cb_message += "Trading suspended for safety.\n"
                    cb_message += "Manual review recommended.\n\n"
                    cb_message += "<i>System will resume on next trading day.</i>"
                    
                    self.telegram_notifier.send_message(cb_message)
                    self.circuit_breaker_notified = True
                    logger.info("Circuit breaker notification sent - no more notifications until reset")
                else:
                    logger.debug("Circuit breaker active - notification already sent")
                return
            
            # Fetch latest market data
            logger.debug("Fetching latest market data...")
            data = self.data_collector.fetch_latest_data(limit=100)
            
            # Check for scalping signal
            signal = self.signal_generator.generate_scalping_signal(data)
            
            if signal:
                # Add to active signals for tracking
                self.active_signals.append(signal)
                
                # Save signal
                self.signal_generator.save_signal(signal)
                
                # Send Telegram notification
                success = self.telegram_notifier.send_signal_notification(signal)
                
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
    
    def get_performance_stats(self):
        """
        Calculate and return performance statistics.
        """
        if not self.signal_history:
            return "No completed signals yet."
        
        wins = sum(1 for s in self.signal_history if s.get('outcome') == 'WIN')
        losses = sum(1 for s in self.signal_history if s.get('outcome') == 'LOSS')
        total = len(self.signal_history)
        
        win_rate = (wins / total * 100) if total > 0 else 0
        
        stats = f"📊 **Performance Stats**\n"
        stats += f"Total Signals: {total}\n"
        stats += f"Wins: {wins} ({win_rate:.1f}%)\n"
        stats += f"Losses: {losses}\n"
        stats += f"Current Streak: {self.consecutive_losses} losses"
        
        return stats
    
    def run_continuous_monitoring(self):
        """
        Run continuous market monitoring for scalping opportunities.
        """
        logger.info("Starting continuous scalping monitor...")
        logger.info(f"Maximum {self.max_daily_signals} signals per day")
        logger.info(f"Minimum 5 minutes between signals")
        logger.info("Monitoring for high-probability setups only...")
        logger.info("Circuit breaker will activate after 3 consecutive losses")
        
        try:
            while True:
                self.check_market_conditions()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Scalping system stopped by user")
            
            # Show final performance stats
            print("\n" + "="*60)
            print(self.get_performance_stats())
            print("="*60)
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
            
            print("\n" + "-"*60)
            print(f"Circuit Breaker Status: {self.consecutive_losses}/3 losses")
            print(f"Active Signals: {len(self.active_signals)}")
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