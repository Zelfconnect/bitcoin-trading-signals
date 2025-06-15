# Bitcoin Futures Trading Signal Strategy

## Overview
This document outlines the comprehensive strategy for generating high-conviction Bitcoin futures trading signals for 1-minute expiry contracts on tofro.com. The system is designed to provide exactly 6 signals per day, with each signal aiming for a 1% profit target.

## Technical Indicator Combination

The strategy employs a multi-layered approach combining several technical indicators to generate high-conviction signals:

### Primary Indicators
1. **Relative Strength Index (RSI)** - Measures the speed and change of price movements
   - Overbought threshold: 70
   - Oversold threshold: 30
   - Timeframe: 1-minute and 5-minute for confirmation

2. **Bollinger Bands** - Volatility bands placed above and below a moving average
   - Period: 20
   - Standard Deviation: 2
   - Signal triggers when price touches or crosses bands

3. **Moving Average Convergence Divergence (MACD)** - Trend-following momentum indicator
   - Fast EMA: 12 periods
   - Slow EMA: 26 periods
   - Signal Line: 9-period EMA of MACD
   - Histogram: MACD - Signal Line

4. **Stochastic Oscillator** - Compares closing price to price range over a period
   - %K period: 14
   - %D period: 3
   - Overbought threshold: 80
   - Oversold threshold: 20

### Secondary Confirmation Indicators
1. **Volume Profile** - Analyzes trading volume at specific price levels
   - Used to identify support/resistance levels

2. **Ichimoku Cloud** - Provides multiple data points about momentum, support, and resistance
   - Used for trend confirmation

3. **Fibonacci Retracement Levels** - Identifies potential reversal levels
   - Used to set precise entry/exit points

## Signal Generation Rules

### Buy (Call) Signal Criteria
A high-conviction buy signal is generated when ALL of the following conditions are met:
1. RSI crosses above 30 from below (indicating potential reversal from oversold)
2. Price touches or crosses the lower Bollinger Band
3. MACD line crosses above the signal line
4. Stochastic %K crosses above %D while both are below 20
5. Volume shows increasing trend
6. Price is above the Ichimoku Cloud or crossing from below
7. Price is near a Fibonacci retracement level (38.2%, 50%, or 61.8%)

### Sell (Put) Signal Criteria
A high-conviction sell signal is generated when ALL of the following conditions are met:
1. RSI crosses below 70 from above (indicating potential reversal from overbought)
2. Price touches or crosses the upper Bollinger Band
3. MACD line crosses below the signal line
4. Stochastic %K crosses below %D while both are above 80
5. Volume shows increasing trend
6. Price is below the Ichimoku Cloud or crossing from above
7. Price is near a Fibonacci retracement level (38.2%, 50%, or 61.8%)

## Signal Strength Classification
Each signal is classified based on the number of confirming indicators:
- **Strong Signal**: All primary and at least 2 secondary indicators confirm
- **Moderate Signal**: All primary indicators confirm
- **Weak Signal**: Only some primary indicators confirm (these signals are not sent)

Only Strong and Moderate signals are considered "high-conviction" and will be sent to the user.

## Risk Management Components

### Position Sizing
- Base position size: 2% of total trading capital
- Adjusted based on signal strength:
  - Strong signal: 100% of base position size
  - Moderate signal: 75% of base position size

### Stop-Loss Recommendations
- Technical stop-loss: Placed at the nearest support/resistance level
- Time-based stop-loss: 30 seconds (half the contract duration)
- Volatility-based stop-loss: 1.5x Average True Range (ATR)

### Take-Profit Targets
- Primary target: 1% profit (as specified by user)
- Secondary target: 1.5% profit (optional extension if momentum is strong)

## Signal Distribution Schedule

To provide 6 signals per day, the system will analyze market conditions during the following time windows:

1. **Early Asian Session**: 00:00-02:00 UTC (1 signal)
2. **Late Asian Session**: 04:00-06:00 UTC (1 signal)
3. **European Session Opening**: 08:00-10:00 UTC (1 signal)
4. **European/US Overlap**: 14:00-16:00 UTC (1 signal)
5. **US Session**: 18:00-20:00 UTC (1 signal)
6. **Late US Session**: 22:00-00:00 UTC (1 signal)

These windows target periods of higher volatility and liquidity, which are optimal for short-term trading. The system will only generate signals during these windows, and will prioritize the highest-conviction signals within each window.

## Signal Delivery Format

Each signal will be delivered via SMS with the following information:

```
BITCOIN SIGNAL #[number]
Type: [BUY/SELL]
Time: [UTC timestamp]
Expiry: 1 minute
Target: +1%
Stop-Loss: [calculated level]
Position Size: [recommended percentage]
Conviction: [Strong/Moderate]
```

## Backtesting and Optimization

The strategy parameters will be optimized through:
1. Historical backtesting on 1-minute Bitcoin data
2. Parameter optimization using walk-forward analysis
3. Monte Carlo simulations to assess robustness

## Performance Metrics

The strategy will be evaluated based on:
1. Win rate (target: >60%)
2. Risk-reward ratio (target: >1.5)
3. Maximum drawdown (target: <15%)
4. Sharpe ratio (target: >1.5)
5. Profit factor (target: >1.3)

## Limitations and Considerations

1. **Market Conditions**: Strategy performance may vary in different market conditions (trending vs. ranging)
2. **Slippage**: 1-minute expiry contracts may experience significant slippage
3. **Signal Latency**: Time between signal generation and user action must be minimized
4. **Exchange Limitations**: tofro.com platform-specific limitations must be considered
