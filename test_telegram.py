#!/usr/bin/env python3

from telegram_notifier import TelegramNotifier
from datetime import datetime

# Create test signal
test_signal = {
    'type': 'BUY',
    'timestamp': datetime.now().isoformat(),
    'price': 107500.0,
    'score': '5/7',
    'quality': 'STRONG',
    'conditions': [
        'RSI reversal from oversold', 
        'Bollinger Band squeeze bounce', 
        'Volume spike with price support', 
        'MACD momentum shift', 
        'Support bounce at 107450.00'
    ],
    'position_size': 0.02,
    'stop_loss': 106975.0,
    'take_profit': 108575.0,
    'expiry': '5 minutes',
    'indicators': {
        'rsi': 32.5,
        'macd': -2.1,
        'bb_position': 'lower',
        'volume_ratio': 1.8
    }
}

print("Testing Telegram notification...")

# Test the notification
notifier = TelegramNotifier()
success = notifier.send_signal_notification(test_signal)
print(f'BUY signal notification sent: {success}')

# Test SELL signal too
test_signal['type'] = 'SELL'
test_signal['quality'] = 'VERY STRONG'
test_signal['score'] = '6/7'
test_signal['conditions'] = [
    'RSI exhaustion from overbought',
    'Bollinger Band upper rejection', 
    'High volume selling pressure',
    'MACD bearish crossover',
    'Resistance rejection at 107950.00',
    'Stochastic overbought crossunder'
]
test_signal['indicators']['rsi'] = 78.2
test_signal['indicators']['bb_position'] = 'upper'

success2 = notifier.send_signal_notification(test_signal)
print(f'SELL signal notification sent: {success2}') 