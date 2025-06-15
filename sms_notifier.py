#!/usr/bin/env python3
"""
SMS Notification Module
----------------------
This module handles sending SMS notifications for Bitcoin trading signals.
"""

import os
import json
import logging
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sms_notifier.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SMSNotifier")

class SMSNotifier:
    """
    Class to handle SMS notifications for trading signals.
    """
    
    def __init__(self, config_file='config/sms_config.json'):
        """
        Initialize the SMS notifier.
        
        Args:
            config_file (str): Path to SMS configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        
        logger.info("SMS notifier initialized")
    
    def _load_config(self):
        """
        Load SMS configuration from file.
        
        Returns:
            dict: SMS configuration
        """
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Check if config file exists
        if not os.path.exists(self.config_file):
            # Create default config
            default_config = {
                "sms_service": "twilio",  # Can be "twilio", "nexmo", etc.
                "twilio": {
                    "account_sid": "YOUR_ACCOUNT_SID",
                    "auth_token": "YOUR_AUTH_TOKEN",
                    "from_number": "YOUR_TWILIO_NUMBER"
                },
                "nexmo": {
                    "api_key": "YOUR_API_KEY",
                    "api_secret": "YOUR_API_SECRET",
                    "from_number": "YOUR_NEXMO_NUMBER"
                },
                "recipient_numbers": [
                    "+1234567890"  # Replace with actual recipient numbers
                ],
                "test_mode": True  # Set to False in production
            }
            
            # Save default config
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info(f"Created default SMS config at {self.config_file}")
            return default_config
        
        # Load existing config
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            logger.info(f"Loaded SMS config from {self.config_file}")
            return config
        except Exception as e:
            logger.error(f"Error loading SMS config: {e}")
            raise
    
    def send_sms(self, message, recipient=None):
        """
        Send an SMS notification.
        
        Args:
            message (str): Message content
            recipient (str, optional): Recipient phone number. If None, uses all configured recipients.
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.config["test_mode"]:
            logger.info(f"TEST MODE: Would send SMS: {message}")
            return True
        
        recipients = [recipient] if recipient else self.config["recipient_numbers"]
        
        if not recipients:
            logger.warning("No recipients configured for SMS")
            return False
        
        sms_service = self.config.get("sms_service", "twilio")
        
        if sms_service == "twilio":
            return self._send_twilio_sms(message, recipients)
        elif sms_service == "nexmo":
            return self._send_nexmo_sms(message, recipients)
        else:
            logger.error(f"Unsupported SMS service: {sms_service}")
            return False
    
    def _send_twilio_sms(self, message, recipients):
        """
        Send SMS using Twilio.
        
        Args:
            message (str): Message content
            recipients (list): List of recipient phone numbers
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from twilio.rest import Client
            
            twilio_config = self.config.get("twilio", {})
            account_sid = twilio_config.get("account_sid")
            auth_token = twilio_config.get("auth_token")
            from_number = twilio_config.get("from_number")
            
            if not all([account_sid, auth_token, from_number]):
                logger.error("Incomplete Twilio configuration")
                return False
            
            client = Client(account_sid, auth_token)
            
            success = True
            for recipient in recipients:
                try:
                    sms = client.messages.create(
                        body=message,
                        from_=from_number,
                        to=recipient
                    )
                    logger.info(f"Sent SMS to {recipient} (SID: {sms.sid})")
                except Exception as e:
                    logger.error(f"Error sending SMS to {recipient}: {e}")
                    success = False
            
            return success
        except ImportError:
            logger.error("Twilio package not installed. Run: pip install twilio")
            return False
        except Exception as e:
            logger.error(f"Error in Twilio SMS sending: {e}")
            return False
    
    def _send_nexmo_sms(self, message, recipients):
        """
        Send SMS using Nexmo/Vonage.
        
        Args:
            message (str): Message content
            recipients (list): List of recipient phone numbers
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import vonage
            
            nexmo_config = self.config.get("nexmo", {})
            api_key = nexmo_config.get("api_key")
            api_secret = nexmo_config.get("api_secret")
            from_number = nexmo_config.get("from_number")
            
            if not all([api_key, api_secret, from_number]):
                logger.error("Incomplete Nexmo configuration")
                return False
            
            client = vonage.Client(key=api_key, secret=api_secret)
            sms = vonage.Sms(client)
            
            success = True
            for recipient in recipients:
                try:
                    response = sms.send_message({
                        'from': from_number,
                        'to': recipient,
                        'text': message
                    })
                    
                    if response["messages"][0]["status"] == "0":
                        logger.info(f"Sent SMS to {recipient} (ID: {response['messages'][0]['message-id']})")
                    else:
                        logger.error(f"Error sending SMS to {recipient}: {response['messages'][0]['error-text']}")
                        success = False
                except Exception as e:
                    logger.error(f"Error sending SMS to {recipient}: {e}")
                    success = False
            
            return success
        except ImportError:
            logger.error("Vonage package not installed. Run: pip install vonage")
            return False
        except Exception as e:
            logger.error(f"Error in Nexmo SMS sending: {e}")
            return False
    
    def send_signal_notification(self, signal):
        """
        Send a signal notification via SMS.
        
        Args:
            signal (dict): Signal data
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Format the signal as an SMS message
        message = f"""
BITCOIN SIGNAL #{signal.get('signal_number', 'N/A')}
Type: {signal.get('type', 'N/A')}
Time: {datetime.fromisoformat(signal.get('timestamp', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M:%S UTC')}
Expiry: {signal.get('expiry', '1 minute')}
Target: +1%
Stop-Loss: {signal.get('stop_loss', 0):.2f}
Position Size: {signal.get('position_size', 0)*100:.1f}%
Conviction: {signal.get('conviction', 'N/A')}
        """.strip()
        
        # Send the SMS
        return self.send_sms(message)

if __name__ == "__main__":
    # Example usage
    notifier = SMSNotifier()
    
    # Example signal
    example_signal = {
        "type": "BUY",
        "timestamp": datetime.now().isoformat(),
        "price": 50000.0,
        "expiry": "1 minute",
        "stop_loss": 49500.0,
        "position_size": 0.02,
        "target": 50500.0,
        "conviction": "Strong",
        "signal_number": 1
    }
    
    # Send test notification
    notifier.send_signal_notification(example_signal)
