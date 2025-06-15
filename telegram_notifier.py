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
from datetime import datetime
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
            
            timestamp_str = signal.get('timestamp', datetime.now().isoformat())
            try:
                formatted_time = datetime.fromisoformat(timestamp_str).strftime('%Y-%m-%d %H:%M:%S UTC')
            except:
                formatted_time = timestamp_str
            
            # Calculate recommended entry time (3 minutes from now)
            from datetime import timedelta
            import pytz
            
            # Get current time in UTC and Dutch timezone
            utc_now = datetime.now(pytz.UTC)
            dutch_tz = pytz.timezone('Europe/Amsterdam')
            dutch_now = utc_now.astimezone(dutch_tz)
            
            # Entry times
            entry_time_utc = utc_now + timedelta(minutes=3)
            entry_time_dutch = entry_time_utc.astimezone(dutch_tz)
            
            entry_time_str = f"{entry_time_dutch.strftime('%H:%M')} NL / {entry_time_utc.strftime('%H:%M')} UTC"
            
            message = f"""
{signal_emoji} <b>BITCOIN SIGNAL #{signal.get('signal_number', 'N/A')}</b>

📊 <b>Type:</b> {signal_type}
⏰ <b>Signal Time:</b> {dutch_now.strftime('%H:%M:%S')} Amsterdam
🚀 <b>ENTER TRADE AT:</b> {entry_time_str}
⏳ <b>Expiry:</b> {signal.get('expiry', '5 minutes')}
🎯 <b>Target:</b> +1%
🛑 <b>Stop-Loss:</b> ${signal.get('stop_loss', 0):.2f}
💰 <b>Position Size:</b> {signal.get('position_size', 0)*100:.1f}%
💪 <b>Conviction:</b> {signal.get('conviction', 'N/A')}

⚡ <b>You have 3 minutes to prepare your trade!</b>
💡 <i>Trade at your own risk. This is not financial advice.</i>
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