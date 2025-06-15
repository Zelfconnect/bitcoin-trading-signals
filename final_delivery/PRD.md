# Product Requirements Document (PRD)
# Bitcoin Futures Trading Signal System

## 1. Introduction

### 1.1 Purpose
This document outlines the requirements for a Bitcoin futures trading signal system designed to generate high-conviction buy (call) and sell (put) signals for 1-minute expiry futures contracts on tofro.com.

### 1.2 Scope
The system will monitor Bitcoin price movements, apply technical analysis, generate trading signals, and deliver them via SMS to the user. It aims to provide 6 signals per day with a target of 1% profit per trade.

### 1.3 Definitions
- **Signal**: A buy (call) or sell (put) recommendation for Bitcoin futures
- **Expiry**: The time at which a futures contract expires (1 minute in this case)
- **High-conviction**: Signals with strong technical confirmation across multiple indicators
- **tofro.com**: The target trading platform for executing the signals

## 2. Product Overview

### 2.1 Product Perspective
The Bitcoin Futures Trading Signal System is a standalone application that integrates with cryptocurrency data sources and SMS delivery services. It operates independently of the trading platform (tofro.com) where trades will be executed.

### 2.2 User Characteristics
The primary user is an intraday Bitcoin futures trader who:
- Trades on tofro.com
- Uses leverage for amplified returns
- Focuses on short-term (1-minute) contracts
- Targets approximately 1% profit per trade
- Requires high-conviction signals to minimize false positives

### 2.3 Operating Environment
- Python 3.x runtime environment
- Internet connectivity for data retrieval and SMS delivery
- Continuous operation during trading hours
- Ability to run on cloud servers or local machines

## 3. Functional Requirements

### 3.1 Data Collection
- **FR1.1**: Retrieve real-time Bitcoin price data at 1-minute intervals
- **FR1.2**: Support multiple data sources (Binance, CryptoCompare, CoinGecko)
- **FR1.3**: Implement fallback mechanisms if primary data source is unavailable
- **FR1.4**: Store historical data for backtesting and analysis

### 3.2 Technical Analysis
- **FR2.1**: Calculate primary technical indicators (RSI, MACD, Bollinger Bands, Stochastic)
- **FR2.2**: Calculate secondary confirmation indicators (Volume, Ichimoku, Fibonacci)
- **FR2.3**: Identify potential entry points based on indicator combinations
- **FR2.4**: Classify signal strength as "Strong" or "Moderate"

### 3.3 Signal Generation
- **FR3.1**: Generate exactly 6 signals per day during optimal trading windows
- **FR3.2**: Apply strict criteria to ensure high-conviction signals
- **FR3.3**: Include risk management parameters with each signal
- **FR3.4**: Avoid generating signals outside designated time windows
- **FR3.5**: Prioritize "Strong" signals over "Moderate" signals

### 3.4 Risk Management
- **FR4.1**: Calculate appropriate position size for each trade (base: 2% of capital)
- **FR4.2**: Determine technical stop-loss levels using ATR
- **FR4.3**: Set profit targets at 1% (primary) and 1.5% (secondary)
- **FR4.4**: Adjust position size based on signal strength

### 3.5 Notification System
- **FR5.1**: Format signals into clear, actionable SMS messages
- **FR5.2**: Deliver signals via SMS a few minutes before optimal entry time
- **FR5.3**: Include all necessary trade information (direction, price, stop-loss, target)
- **FR5.4**: Track daily signal count to avoid exceeding 6 signals per day

### 3.6 System Operation
- **FR6.1**: Run continuously during designated trading windows
- **FR6.2**: Automatically restart after errors or interruptions
- **FR6.3**: Log all system activities and signal generations
- **FR6.4**: Support configuration changes without system restart

## 4. Non-Functional Requirements

### 4.1 Performance
- **NFR1.1**: Process price data and generate signals within 5 seconds
- **NFR1.2**: Deliver SMS notifications within 30 seconds of signal generation
- **NFR1.3**: Support continuous operation with minimal resource usage
- **NFR1.4**: Handle data processing for at least 30 days of historical data

### 4.2 Reliability
- **NFR2.1**: Achieve 99.9% uptime during trading windows
- **NFR2.2**: Implement error handling for all external API calls
- **NFR2.3**: Provide fallback mechanisms for data sources and SMS delivery
- **NFR2.4**: Maintain accurate signal timing even under high system load

### 4.3 Security
- **NFR3.1**: Secure storage of API keys and credentials
- **NFR3.2**: Encrypt sensitive configuration data
- **NFR3.3**: Implement access controls for system configuration
- **NFR3.4**: Protect user phone number and trading preferences

### 4.4 Usability
- **NFR4.1**: Provide clear, concise SMS notifications
- **NFR4.2**: Include all necessary information for trade execution
- **NFR4.3**: Format messages consistently for easy reading
- **NFR4.4**: Deliver signals with sufficient time for user action

### 4.5 Maintainability
- **NFR5.1**: Modular code structure for easy updates
- **NFR5.2**: Comprehensive documentation of all components
- **NFR5.3**: Configurable parameters without code changes
- **NFR5.4**: Detailed logging for troubleshooting

## 5. System Architecture

### 5.1 Component Overview
1. **Data Collection Module**
   - Interfaces with cryptocurrency data APIs
   - Handles data normalization and storage
   - Implements fallback mechanisms

2. **Technical Indicators Module**
   - Calculates all required technical indicators
   - Provides indicator values to signal generation module
   - Supports customizable indicator parameters

3. **Signal Generation Module**
   - Applies trading logic to technical indicators
   - Identifies high-conviction trading opportunities
   - Classifies signals by strength

4. **Risk Management Module**
   - Calculates position sizing
   - Determines stop-loss levels
   - Sets profit targets

5. **Notification Module**
   - Formats signal information
   - Delivers SMS notifications
   - Tracks daily signal count

6. **Main Application**
   - Orchestrates all components
   - Manages system lifecycle
   - Handles configuration and logging

### 5.2 Data Flow
1. Data Collection → Technical Indicators → Signal Generation → Risk Management → Notification
2. Configuration → All Modules
3. All Modules → Logging

### 5.3 External Interfaces
1. **Cryptocurrency Data APIs**
   - Binance, CryptoCompare, CoinGecko
   - Real-time and historical price data

2. **SMS Gateway**
   - SMS delivery service (Twilio, Nexmo/Vonage)
   - Message formatting and delivery

## 6. Implementation Considerations

### 6.1 Development Tools
- Python 3.x programming language
- pandas, numpy for data processing
- matplotlib for visualization (development/testing)
- requests for API communication
- SMS gateway client libraries

### 6.2 Testing Requirements
- Unit tests for all modules
- Integration tests for component interactions
- Backtesting with historical data
- Synthetic data testing for edge cases

### 6.3 Deployment Considerations
- Cloud server or local machine deployment
- Continuous operation requirements
- Monitoring and alerting
- Backup and recovery procedures

### 6.4 Future Enhancements
- Machine learning for signal optimization
- Web interface for configuration and monitoring
- Additional trading pairs beyond Bitcoin
- Support for different expiry timeframes
- Performance analytics dashboard

## 7. Acceptance Criteria

### 7.1 Minimum Viable Product
- Successfully retrieves Bitcoin price data
- Calculates all specified technical indicators
- Generates signals based on defined criteria
- Delivers signals via SMS
- Operates continuously during trading windows
- Limits to 6 signals per day

### 7.2 Success Metrics
- Signal accuracy (win rate)
- Average profit per signal
- System reliability and uptime
- Timely signal delivery
- User satisfaction with signal quality

## 8. Timeline and Milestones

### 8.1 Development Phases
1. **Phase 1**: Data collection and technical indicators
2. **Phase 2**: Signal generation and risk management
3. **Phase 3**: Notification system and integration
4. **Phase 4**: Testing and optimization
5. **Phase 5**: Deployment and monitoring

### 8.2 Key Milestones
- Data collection module completion
- Technical indicator implementation
- Signal generation logic validation
- End-to-end system testing
- Production deployment

## 9. Appendices

### 9.1 Technical Indicator Specifications
- **RSI**: Settings, thresholds, and interpretation
- **MACD**: Fast/slow periods, signal line, crossover conditions
- **Bollinger Bands**: Period, standard deviation, conditions
- **Stochastic Oscillator**: %K, %D periods, thresholds
- **Volume Profile**: Calculation method and interpretation
- **Ichimoku Cloud**: Component periods and signal conditions
- **Fibonacci Retracement**: Calculation and level significance

### 9.2 Signal Generation Logic
- Detailed conditions for buy signals
- Detailed conditions for sell signals
- Signal strength classification criteria
- Conflict resolution between indicators

### 9.3 Time Window Specifications
1. Early Asian Session: 00:00-02:00 UTC
2. Late Asian Session: 04:00-06:00 UTC
3. European Session Opening: 08:00-10:00 UTC
4. European/US Overlap: 14:00-16:00 UTC
5. US Session: 18:00-20:00 UTC
6. Late US Session: 22:00-00:00 UTC

### 9.4 SMS Format Template
```
BITCOIN SIGNAL #[count]
Type: [BUY/SELL]
Time: [timestamp]
Expiry: 1 minute
Target: +1%
Stop-Loss: [level]
Position Size: [percentage]%
Conviction: [Strong/Moderate]
```
