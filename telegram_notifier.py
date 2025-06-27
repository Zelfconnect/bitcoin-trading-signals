#!/usr/bin/env python3
"""
Telegram Notification Module
---------------------------
This module handles sending Telegram notifications for Bitcoin trading signals.
"""

import os
import json
import logging
import requests
import pytz
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("telegram_notifier.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TelegramNotifier")

class TelegramNotifier:
    """
    Class to handle Telegram notifications for trading signals.
    """
    
    def __init__(self, config_file: str = 'config/telegram_config.json'):
        """
        Initialize the Telegram notifier.
        
        Args:
            config_file (str): Path to Telegram configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.base_url = f"https://api.telegram.org/bot{self.config['bot_token']}"
        self.timeout = 30  # Request timeout in seconds
        
        # Setup Dutch timezone
        self.dutch_tz = pytz.timezone('Europe/Amsterdam')
        
        # Validate configuration
        self._validate_config()
        
        logger.info("Telegram notifier initialized")
    
    def _load_config(self) -> Dict:
        """
        Load Telegram configuration from file.
        
        Returns:
            dict: Telegram configuration
        """
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Check if config file exists
        if not os.path.exists(self.config_file):
            # Create default config
            default_config = {
                "bot_token": "YOUR_BOT_TOKEN",
                "chat_ids": [
                    "YOUR_CHAT_ID"  # Replace with actual chat IDs
                ],
                "test_mode": True  # Set to False in production
            }
            
            # Save default config
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info(f"Created default Telegram config at {self.config_file}")
            return default_config
        
        # Load existing config
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            logger.info(f"Loaded Telegram config from {self.config_file}")
            return config
        except Exception as e:
            logger.error(f"Error loading Telegram config: {e}")
            raise
    
    def _validate_config(self) -> None:
        """
        Validate the Telegram configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.config.get('bot_token') or self.config['bot_token'] == "YOUR_BOT_TOKEN":
            raise ValueError("Bot token not configured. Please set your bot token in the config file.")
        
        if not self.config.get('chat_ids') or self.config['chat_ids'] == ["YOUR_CHAT_ID"]:
            raise ValueError("Chat IDs not configured. Please set your chat IDs in the config file.")
        
        # Validate chat IDs format
        for chat_id in self.config['chat_ids']:
            if not isinstance(chat_id, (str, int)):
                raise ValueError(f"Invalid chat ID format: {chat_id}")
    
    def _test_bot_connection(self) -> bool:
        """
        Test the bot connection by calling getMe API.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/getMe",
                timeout=self.timeout
            )
            response.raise_for_status()
            bot_info = response.json()
            
            if bot_info.get('ok'):
                logger.info(f"Bot connection successful: {bot_info['result']['username']}")
                return True
            else:
                logger.error(f"Bot connection failed: {bot_info}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing bot connection: {e}")
            return False
    
    def send_message(self, message: str, chat_id: Optional[Union[str, int]] = None) -> bool:
        """
        Send a Telegram message.
        
        Args:
            message (str): Message content
            chat_id (str|int, optional): Chat ID to send to. If None, uses all configured chat IDs.
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.config["test_mode"]:
            logger.info(f"TEST MODE: Would send Telegram message: {message}")
            return True
        
        # Validate message length (Telegram limit is 4096 characters)
        if len(message) > 4096:
            logger.warning(f"Message too long ({len(message)} chars), truncating...")
            message = message[:4090] + "..."
        
        chat_ids = [chat_id] if chat_id else self.config["chat_ids"]
        
        if not chat_ids:
            logger.warning("No chat IDs configured for Telegram")
            return False
        
        success = True
        for chat_id in chat_ids:
            try:
                response = requests.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get('ok'):
                    logger.info(f"Sent message to chat {chat_id}")
                else:
                    logger.error(f"Failed to send message to chat {chat_id}: {result}")
                    success = False
                    
            except requests.exceptions.Timeout:
                logger.error(f"Timeout sending message to chat {chat_id}")
                success = False
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error sending message to chat {chat_id}: {e}")
                success = False
            except Exception as e:
                logger.error(f"Unexpected error sending message to chat {chat_id}: {e}")
                success = False
        
        return success
    
    def _get_dutch_time(self, timestamp=None):
        """
        Get current time in Dutch timezone or convert provided timestamp.
        
        Args:
            timestamp (datetime, optional): Timestamp to convert. If None, uses current time.
            
        Returns:
            datetime: Time in Amsterdam timezone
        """
        if timestamp is None:
            utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        else:
            if timestamp.tzinfo is None:
                utc_now = timestamp.replace(tzinfo=pytz.UTC)
            else:
                utc_now = timestamp.astimezone(pytz.UTC)
        
        return utc_now.astimezone(self.dutch_tz)
    
    def send_signal_notification(self, signal: Dict) -> bool:
        """
        Send a signal notification via Telegram.
        
        Args:
            signal (dict): Signal data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Format the signal as a Telegram message with HTML formatting
            signal_type = signal.get('type', 'N/A')
            signal_emoji = "🟢" if signal_type == "BUY" else "🔴" if signal_type == "SELL" else "⚪"
            quality = signal.get('quality', 'N/A')
            score = signal.get('score', 'N/A')
            
            # Quality emojis
            quality_emoji = {
                "VERY STRONG": "🔥🔥🔥",
                "STRONG": "🔥🔥", 
                "MODERATE": "🔥",
                "WEAK": "⚠️"
            }.get(quality, "")
            
            # Conditions met
            conditions = signal.get('conditions', [])
            conditions_text = "\n".join([f"✓ {cond}" for cond in conditions])
            
            # Handle timestamp and convert to Dutch time
            timestamp_str = signal.get('timestamp', datetime.now().isoformat())
            try:
                if isinstance(timestamp_str, str):
                    signal_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    signal_timestamp = timestamp_str
                
                dutch_time = self._get_dutch_time(signal_timestamp)
                formatted_time = dutch_time.strftime('%H:%M:%S')
                formatted_date = dutch_time.strftime('%d-%m-%Y')
                timezone_name = dutch_time.strftime('%Z')  # CET or CEST
                
                # Calculate optimal entry time (add 2-3 minutes for preparation)
                optimal_entry_time = dutch_time + timedelta(minutes=2)
                entry_time_str = optimal_entry_time.strftime('%H:%M')
                
            except Exception as e:
                logger.warning(f"Error parsing timestamp {timestamp_str}: {e}")
                dutch_time = self._get_dutch_time()
                formatted_time = dutch_time.strftime('%H:%M:%S')
                formatted_date = dutch_time.strftime('%d-%m-%Y')
                timezone_name = dutch_time.strftime('%Z')
                
                from datetime import timedelta
                optimal_entry_time = dutch_time + timedelta(minutes=2)
                entry_time_str = optimal_entry_time.strftime('%H:%M')
            
            # Determine trade action
            action_text = "📈 <b>CALL (UP)</b>" if signal_type == "BUY" else "📉 <b>PUT (DOWN)</b>"
            
            message = f"""
{signal_emoji} <b>SCALPING SIGNAL - {signal_type}</b> {quality_emoji}

📊 <b>Signal Quality:</b> {quality} ({score})
💰 <b>Entry Price:</b> ${signal.get('price', 0):,.2f}
{action_text}

⏰ <b>TIMING INSTRUCTIONS:</b>
🇳🇱 <b>Signal Time:</b> {formatted_time} {timezone_name}
🚀 <b>ENTER TRADE AT:</b> {entry_time_str} Amsterdam
⏳ <b>Expiry:</b> {signal.get('expiry', '5 minutes')}
⚡ <b>You have ~2 minutes to prepare!</b>

💼 <b>Trade Details:</b>
🎯 <b>Target:</b> ${signal.get('take_profit', 0):,.2f} (+{((signal.get('take_profit', 0)/signal.get('price', 1))-1)*100:.1f}%)
🛑 <b>Stop Loss:</b> ${signal.get('stop_loss', 0):,.2f} (-{(1-(signal.get('stop_loss', 0)/signal.get('price', 1)))*100:.1f}%)
💼 <b>Position Size:</b> {signal.get('position_size', 0)*100:.1f}% of capital

📈 <b>Market Conditions Met:</b>
{conditions_text}

📊 <b>Key Indicators:</b>
• RSI: {signal.get('indicators', {}).get('rsi', 0):.1f}
• MACD: {signal.get('indicators', {}).get('macd', 0):.2f}
• BB Position: {signal.get('indicators', {}).get('bb_position', 'N/A')}
• Volume Ratio: {signal.get('indicators', {}).get('volume_ratio', 0):.1f}x avg

<b>📱 ACTION REQUIRED:</b>
1️⃣ Open your trading platform NOW
2️⃣ Navigate to Bitcoin options
3️⃣ Select {action_text} at {entry_time_str}
4️⃣ Set 5-minute expiry
5️⃣ Use recommended position size

<i>Professional scalping signal - Trade at your own risk.</i>
            """.strip()
            
            # Send the message
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error formatting signal notification: {e}")
            return False

if __name__ == "__main__":
    # Example usage
    try:
        notifier = TelegramNotifier()
        
        # Test bot connection
        if not notifier._test_bot_connection():
            print("Bot connection test failed. Please check your configuration.")
            exit(1)
        
        # Example signal
        example_signal = {
            "type": "BUY",
            "timestamp": datetime.now().isoformat(),
            "price": 50000.0,
            "expiry": "5 minutes",
            "stop_loss": 49500.0,
            "position_size": 0.02,
            "target": 50500.0,
            "conviction": "Strong",
            "signal_number": 1
        }
        
        # Send test notification
        success = notifier.send_signal_notification(example_signal)
        print(f"Test notification sent: {success}")
        
    except Exception as e:
        print(f"Error in test: {e}") 