# Bitcoin Trading Signal System - Dutch Configuration

## 🇳🇱 System Logic Overview for Dutch Traders

### ⏰ Trading Schedule (Amsterdam Time)
The system is configured to respect your preferred trading hours:
- **Morning Session**: 08:00 - 11:00
- **Evening Session**: 17:00 - 19:00

### 📱 Signal Delivery Timeline

#### Example Morning Signal:
```
09:27 Amsterdam - You receive Telegram notification
09:30 Amsterdam - You place the trade (5-minute expiry)
09:35 Amsterdam - Option expires
```

#### Example Evening Signal:
```
18:27 Amsterdam - You receive Telegram notification
18:30 Amsterdam - You place the trade (5-minute expiry)
18:35 Amsterdam - Option expires
```

### 📊 Complete Signal Flow

1. **Data Collection** (Continuous)
   - Fetches latest 100 Bitcoin price candles
   - Updates every minute

2. **Signal Generation** (At scheduled times)
   - **Morning**: 09:27, 09:57, 10:27
   - **Evening**: 18:27, 18:57, 19:27
   
3. **Technical Analysis**
   - RSI (14-period) - Overbought/Oversold
   - MACD - Momentum shifts
   - Bollinger Bands - Volatility breakouts
   - Stochastic - Reversal points
   - Ichimoku Cloud - Trend confirmation

4. **Signal Criteria**
   - Requires 3+ indicators to align
   - Strong signals need 4+ indicators
   - Maximum 6 signals per day

5. **Risk Management**
   - Position size: 0.5-2% based on volatility
   - Stop-loss: 1.5x ATR from entry
   - Target: 1% profit (for 5-minute expiry)

### 💬 Telegram Message Format

```
🟢 BITCOIN SIGNAL #3

📊 Type: BUY
⏰ Signal Time: 09:27:15 Amsterdam
🚀 ENTER TRADE AT: 09:30 NL / 07:30 UTC
⏳ Expiry: 5 minutes
🎯 Target: +1%
🛑 Stop-Loss: $65,432.00
💰 Position Size: 1.5%
💪 Conviction: Strong

⚡ You have 3 minutes to prepare your trade!
💡 Trade at your own risk. This is not financial advice.
```

### 🔄 Daily Signal Distribution

**Maximum 6 signals per day:**
- Morning: Up to 3 signals
- Evening: Up to 3 signals

**Signal Times (Amsterdam):**
- 09:27 → Trade at 09:30 → Expires 09:35
- 09:57 → Trade at 10:00 → Expires 10:05
- 10:27 → Trade at 10:30 → Expires 10:35
- 18:27 → Trade at 18:30 → Expires 18:35
- 18:57 → Trade at 19:00 → Expires 19:05
- 19:27 → Trade at 19:30 → Expires 19:35

### 🌍 Timezone Handling

The system automatically handles:
- **CET** (Winter): UTC+1
- **CEST** (Summer): UTC+2

All times shown in Telegram will be in Amsterdam local time with UTC reference.

### ⚙️ Technical Implementation

1. **Scheduler** runs in UTC but calculates Dutch local times
2. **Signal Generator** checks if current UTC hour falls within allowed windows
3. **Telegram Notifier** converts all times to Amsterdam timezone for display
4. **3-minute advance notice** gives you time to:
   - Review the signal
   - Check market conditions
   - Prepare your trade
   - Enter at the optimal 5-minute mark

### 🎯 Why These Specific Times?

**Morning (08:00-11:00)**:
- European markets fully open
- Good liquidity
- Clear trends forming

**Evening (17:00-19:00)**:
- US markets active
- European/US overlap
- High volatility periods

### 🚀 Deployment on Railway

When deployed, the system will:
1. Run 24/7 but only generate signals during your windows
2. Automatically adjust for daylight saving time
3. Send clear, actionable signals to your Telegram
4. Maintain signal quality with max 6 per day limit

Your trading system is now perfectly configured for Dutch timezone with 5-minute expiry options! 