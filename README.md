# Bitcoin Trading Signal System

This document provides a comprehensive guide to the Bitcoin Trading Signal System, designed to generate high-conviction buy (call) and sell (put) signals for 5-minute expiry Bitcoin futures contracts on tofro.com. The system incorporates advanced technical indicators, a machine learning filter, and robust risk management features to optimize signal accuracy and profitability.

## Table of Contents

1.  [System Overview](#system-overview)
2.  [Features](#features)
3.  [Installation](#installation)
4.  [Configuration](#configuration)
5.  [Usage](#usage)
6.  [System Architecture](#system-architecture)
7.  [Development with Cursor](#development-with-cursor)
8.  [Troubleshooting](#troubleshooting)
9.  [Future Enhancements](#future-enhancements)

## 1. System Overview

The Bitcoin Trading Signal System is an automated solution for generating actionable trading signals. It is specifically tailored for intraday trading with 5-minute expiry futures contracts, aiming for high accuracy and consistent profitability. The system sends signals via Telegram, providing all necessary information for trade execution.

## 2. Features

*   **High-Accuracy Signals**: Utilizes a combination of optimized technical indicators and a machine learning filter to generate high-conviction buy/sell signals.
*   **5-Minute Timeframe Optimization**: All components are specifically tuned for 5-minute Bitcoin price data, aligning with 5-minute expiry contracts.
*   **Risk Management**: Includes dynamic position sizing, adaptive stop-loss, and take-profit levels to manage trade risk effectively.
*   **Telegram Notifications**: Delivers trading signals directly to your Telegram chat, typically 2 minutes before the optimal entry time.
*   **Configurable Parameters**: Easily adjust signal generation, ML filter, and risk management parameters to suit your trading style.
*   **Modular Design**: A well-structured codebase facilitates easy understanding, modification, and extension.
*   **Comprehensive Backtesting Framework**: Allows for rigorous testing and optimization of the trading strategy against historical data.

## 3. Installation

To set up the Bitcoin Trading Signal System, follow these steps:

1.  **Clone the Repository (if applicable)**: If you received this as a Git repository, clone it to your local machine:
    ```bash
    git clone <repository_url>
    cd bitcoin_trading_signals
    ```
    If you received a ZIP file, extract it to your desired location.

2.  **Create a Virtual Environment (Recommended)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file will be generated or should be present in the package. If not, you may need to install common data science and trading libraries such as `pandas`, `numpy`, `scikit-learn`, `ta-lib` (if used), `requests`, etc.)*

## 4. Configuration

The system\'s behavior is controlled by configuration files located in the `config/` directory. You will find:

*   `signal_config.json`: Parameters for technical indicators and signal generation logic.
*   `ml_config.json`: Settings for the machine learning filter, including model paths and confidence thresholds.
*   `risk_config.json`: Rules for position sizing, stop-loss, and take-profit levels.
*   `backtest_config.json`: Parameters for backtesting, such as initial capital, date ranges, and data source.

**Key Configuration Steps**:

1.  **Telegram Bot Setup**: 
    * Create a new Telegram bot using [@BotFather](https://t.me/botfather) and get your bot token
    * Start a chat with your bot and get your chat ID (you can use [@userinfobot](https://t.me/userinfobot) to get your ID)
    * Open `config/telegram_config.json` and replace the placeholder values:
      ```json
      {
          "bot_token": "YOUR_BOT_TOKEN",
          "chat_ids": ["YOUR_CHAT_ID"],
          "test_mode": false
      }
      ```

2.  **Data Source Configuration**: In `backtest_config.json` (and potentially `data_collector.py`), specify your preferred data source (e.g., Binance, CryptoCompare, CoinGecko). Ensure you have the necessary API keys or access if required by the chosen data source.

3.  **Parameter Adjustment**: Review the `signal_config.json`, `ml_config.json`, and `risk_config.json` files. The system has been tuned for high accuracy, but you may adjust parameters further based on your risk tolerance and desired signal frequency. Refer to the `parameter_adjustment_recommendations.md` for guidance.

## 5. Usage

To run the Bitcoin Trading Signal System:

1.  **Activate Virtual Environment** (if not already active):
    ```bash
    source venv/bin/activate
    ```

2.  **Run the Main Application**:
    ```bash
    python main.py
    ```
    The system will start monitoring Bitcoin price movements, generate signals, and send Telegram notifications during optimal trading windows.

3.  **Run Backtesting**:
    To evaluate the strategy\'s performance, use the backtesting script:
    ```bash
    python run_backtest.py
    ```
    Backtest results will be saved in the `test_results/` directory.

4.  **Parameter Tuning (Optional)**:
    To optimize system parameters for desired signal frequency and accuracy:
    ```bash
    python parameter_tuning.py
    ```
    This script will generate recommendations for optimal parameters.

## 6. System Architecture

The system is organized into several modular components:

*   `data_collector_5m.py`: Handles fetching and processing 5-minute Bitcoin price data from various sources.
*   `indicators_5m.py`: Implements and calculates various technical indicators (RSI, MACD, Bollinger Bands, Ichimoku Cloud, Fibonacci Retracements, etc.) optimized for the 5-minute timeframe.
*   `signal_generator_5m.py`: Contains the core trading logic, combining technical indicator analysis with predefined rules to generate buy/sell signals.
*   `ml_filter_5m.py`: Incorporates a machine learning model to filter out low-conviction signals and enhance overall accuracy.
*   `risk_manager_5m.py`: Manages position sizing, stop-loss, and take-profit levels based on market volatility and risk-reward principles.
*   `telegram_notifier.py`: Responsible for formatting and sending trading signals via Telegram.
*   `backtester_5m.py`: A comprehensive module for backtesting the trading strategy against historical data, evaluating performance metrics.
*   `main.py`: The main entry point for the live signal generation system.
*   `run_backtest.py`: Script to initiate the backtesting process.
*   `parameter_tuning.py`: Script for optimizing system parameters.
*   `config/`: Directory containing JSON configuration files for signals, ML, risk, and backtesting.

## 7. Development with Cursor

This project is structured to facilitate easy development and modification using Cursor. Here are some tips:

*   **Project Navigation**: Use Cursor\'s file explorer to navigate through the modular codebase. Each file is self-contained and focuses on a specific aspect of the system.
*   **Code Understanding**: Leverage Cursor\'s AI capabilities for code explanations, refactoring suggestions, and identifying potential areas for improvement.
*   **Debugging**: Utilize Cursor\'s integrated debugger to step through the code, inspect variables, and understand the flow of execution, especially during backtesting or signal generation.
*   **Experimentation**: Easily modify parameters in the `config/` files or directly in the Python scripts to experiment with different strategies. Use the `run_backtest.py` script to quickly evaluate changes.
*   **New Features**: When adding new indicators, ML models, or risk management rules, create new functions or modules following the existing modular structure.

## 8. Troubleshooting

*   **No Signals Generated**: 
    *   Check `signal_config.json` and `ml_config.json` for overly restrictive parameters. Refer to `parameter_adjustment_recommendations.md`.
    *   Ensure `main_5m.py` is running and has access to real-time data.
    *   Verify data source connectivity in `data_collector_5m.py`.
*   **Backtesting Errors**: 
    *   Ensure all dependencies are installed (`pip install -r requirements.txt`).
    *   Check `backtest_config.json` for correct date ranges and data source settings.
    *   Review console output for specific error messages (e.g., `KeyError`, `ValueError`).
*   **Telegram Not Sent**: 
    *   Verify Telegram bot credentials in `telegram_config.json`.
    *   Check your Telegram app for delivery issues.
    *   Ensure your chat ID is correctly configured.

## 9. Future Enhancements

Here are some potential areas for future development and enhancement:

*   **Real-time Data Integration**: Implement more robust real-time data streaming for lower latency signal generation.
*   **Additional ML Models**: Explore more advanced machine learning models (e.g., deep learning, reinforcement learning) for signal prediction and optimization.
*   **Automated Trading Integration**: Integrate directly with exchange APIs for automated trade execution (use with extreme caution and thorough testing).
*   **Web Interface**: Develop a simple web-based dashboard for monitoring signals, system status, and performance metrics.
*   **Multi-Asset Support**: Extend the system to support trading signals for other cryptocurrencies or assets.
*   **News Sentiment Analysis**: Incorporate external data sources like news sentiment to enhance signal accuracy.
