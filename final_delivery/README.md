# Bitcoin Futures Trading Signal System

## Overview

This system generates high-conviction buy (call) and sell (put) signals for Bitcoin futures trading with 1-minute expiry contracts on tofro.com. It's designed to deliver 6 signals per day with a target of 1% profit per trade.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Features](#features)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Development with Cursor](#development-with-cursor)
7. [Customization Guide](#customization-guide)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)
11. [API Reference](#api-reference)
12. [Future Enhancements](#future-enhancements)

## System Architecture

The system consists of several modular components:

```
Bitcoin Trading Signal System
├── Data Collection Module
│   ├── Real-time price data
│   ├── Historical data
│   └── Multiple data sources
├── Technical Indicators Module
│   ├── Primary indicators
│   └── Secondary confirmation indicators
├── Signal Generation Module
│   ├── Trading logic
│   └── Signal strength classification
├── Risk Management Module
│   ├── Position sizing
│   └── Stop-loss calculation
├── Notification Module
│   └── SMS formatting and delivery
└── Main Application
    ├── Component orchestration
    └── Scheduling
```

## Features

- **High-Conviction Signals**: Combines multiple technical indicators for reliable signals
- **Optimal Timing**: 6 signals per day during strategic market windows
- **Risk Management**: Position sizing and stop-loss recommendations
- **SMS Delivery**: Clear, actionable trading instructions
- **Multiple Data Sources**: Binance, CryptoCompare, CoinGecko with fallback options
- **Synthetic Data**: For testing and development without API access
- **Comprehensive Testing**: Backtesting and performance metrics

## Installation

### Prerequisites

- Python 3.8+
- pip package manager
- Internet connection
- SMS gateway account (Twilio, Nexmo/Vonage)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bitcoin-trading-signals.git
   cd bitcoin-trading-signals
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create configuration directories:
   ```bash
   mkdir -p data config signals test_results
   ```

## Configuration

### Data Sources

Edit `config/data_sources.json`:

```json
{
  "primary_source": "cryptocompare",
  "fallback_source": "coingecko",
  "api_keys": {
    "binance": "YOUR_BINANCE_API_KEY",
    "cryptocompare": "YOUR_CRYPTOCOMPARE_API_KEY"
  }
}
```

### SMS Configuration

Edit `config/sms_config.json`:

```json
{
  "provider": "twilio",
  "account_sid": "YOUR_TWILIO_SID",
  "auth_token": "YOUR_TWILIO_TOKEN",
  "from_number": "+1234567890",
  "to_number": "+1987654321"
}
```

### Trading Parameters

Edit `config/trading_params.json`:

```json
{
  "max_daily_signals": 6,
  "base_position_size": 0.02,
  "profit_target": 0.01,
  "secondary_target": 0.015,
  "atr_multiplier": 1.5
}
```

## Usage

### Running the System

Start the main application:

```bash
python main.py
```

This will:
1. Initialize all components
2. Begin monitoring Bitcoin price data
3. Generate signals during trading windows
4. Send SMS notifications when signals are triggered

### Command-line Options

```bash
python main.py --config custom_config.json --verbose --log-level DEBUG
```

### Monitoring

Check the logs in `logs/trading_signals.log` for system activity.

## Development with Cursor

This project is structured for efficient development with [Cursor](https://cursor.sh/), an AI-powered code editor. Here's how to make the most of it:

### Project Setup in Cursor

1. Open Cursor and select "Open Folder"
2. Navigate to the bitcoin-trading-signals directory
3. The project structure will be automatically recognized

### Key Files for Development

- **Entry Points**:
  - `main.py`: Main application entry point
  - `test_with_synthetic_data.py`: Testing entry point

- **Core Logic**:
  - `signal_generator.py`: Signal generation algorithms
  - `indicators.py`: Technical indicator implementations

- **Configuration**:
  - Files in the `config/` directory

### Using Cursor AI Features

1. **Code Explanation**: Select any code block and use Cursor's "Explain" feature to understand its purpose and functionality

2. **Function Enhancement**: Use Cursor to suggest improvements to existing functions:
   ```python
   # Example: Enhance the check_buy_signal function
   def check_buy_signal(self, data):
       # Select this function and ask Cursor to optimize it
   ```

3. **New Feature Implementation**: Describe the feature in comments and let Cursor generate implementation:
   ```python
   # TODO: Implement machine learning-based signal optimization that:
   # 1. Analyzes historical signal performance
   # 2. Adjusts indicator weights based on success rate
   # 3. Gradually improves signal quality over time
   ```

4. **Bug Fixing**: When encountering errors, paste the stack trace and ask Cursor to suggest fixes

5. **Documentation Generation**: Use Cursor to generate or improve docstrings and comments

### Recommended Development Workflow

1. Start with understanding the existing code structure
2. Make small, incremental changes to one module at a time
3. Run tests after each significant change
4. Use version control to track your modifications

## Customization Guide

### Adjusting Technical Indicators

Modify parameters in `indicators.py`:

```python
# Example: Change RSI parameters
def calculate_rsi(data, period=14):  # Change period from default 14
    # Implementation
```

### Modifying Signal Criteria

Edit signal conditions in `signal_generator.py`:

```python
# Example: Adjust RSI thresholds
rsi_condition = previous['rsi'] < 25 and latest['rsi'] > 25  # Changed from 30
```

### Adding New Indicators

1. Implement the indicator calculation in `indicators.py`
2. Add it to the `add_all_indicators` method
3. Incorporate it into signal logic in `signal_generator.py`

### Changing Time Windows

Modify the time windows in `main.py`:

```python
time_windows = [
    (0, 2),    # Early Asian Session
    (4, 6),    # Late Asian Session
    # Add or modify windows here
]
```

## Testing

### Running Tests

```bash
# Run backtesting with historical data
python backtester.py

# Test with synthetic data
python test_with_synthetic_data.py

# Run unit tests
python -m unittest discover tests
```

### Generating Synthetic Data

```bash
python synthetic_data.py --days 30 --output data/synthetic/
```

### Analyzing Results

Test results are saved in the `test_results/` directory:
- Performance metrics (JSON)
- Visualization plots (PNG)
- Detailed reports (MD)

## Deployment

### Local Deployment

Run as a background service:

```bash
nohup python main.py > trading.log 2>&1 &
```

### Cloud Deployment

1. **AWS EC2**:
   - Launch an EC2 instance
   - Install dependencies
   - Run as a systemd service

2. **Docker**:
   ```bash
   docker build -t bitcoin-signals .
   docker run -d bitcoin-signals
   ```

### Monitoring and Maintenance

- Set up monitoring with CloudWatch or similar
- Implement regular log rotation
- Create backup procedures for configuration and data

## Troubleshooting

### Common Issues

1. **Data Source Connection Failures**:
   - Check API keys
   - Verify internet connection
   - Ensure data source is operational

2. **No Signals Generated**:
   - Check if criteria are too restrictive
   - Verify time windows are correct
   - Ensure data is being processed correctly

3. **SMS Delivery Issues**:
   - Validate SMS provider credentials
   - Check phone number format
   - Verify SMS provider account status

### Logging

Adjust log level in `config/logging.json`:

```json
{
  "level": "INFO",  # Change to DEBUG for more details
  "file": "logs/trading_signals.log",
  "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}
```

## API Reference

### Data Collection Module

```python
# Fetch latest data
data = data_collector.fetch_latest_data(limit=100)

# Fetch historical data
historical_data = data_collector.fetch_historical_data(
    start_date="2023-01-01", 
    end_date="2023-01-31"
)
```

### Technical Indicators Module

```python
# Add all indicators to data
data_with_indicators = TechnicalIndicators.add_all_indicators(data)

# Calculate specific indicator
rsi = TechnicalIndicators.calculate_rsi(data, period=14)
```

### Signal Generator Module

```python
# Check for buy signal
buy_signal, strength = signal_generator.check_buy_signal(data)

# Generate signal
signal = signal_generator.generate_signal(data)
```

### SMS Notification Module

```python
# Format signal as SMS
sms_text = sms_notifier.format_message(signal)

# Send SMS
sms_notifier.send_sms(sms_text)
```

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**:
   - Signal optimization using historical performance
   - Adaptive parameter tuning
   - Market regime detection

2. **Web Dashboard**:
   - Real-time signal monitoring
   - Performance analytics
   - Configuration interface

3. **Extended Asset Support**:
   - Additional cryptocurrencies
   - Traditional market assets
   - Correlation-based signals

4. **Advanced Risk Management**:
   - Portfolio-level position sizing
   - Dynamic risk adjustment
   - Drawdown protection

### Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Technical indicator implementations inspired by TA-Lib
- Synthetic data generation based on research by [Author Name]
- Trading strategy concepts from [Source]
