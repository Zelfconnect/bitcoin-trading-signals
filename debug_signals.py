#!/usr/bin/env python3
"""
Debug Signal Generation
-----------------------
Test script to debug why signals are not being generated.
"""

import datetime
from data_collector import BitcoinDataCollector
from signal_generator import SignalGenerator
from indicators import TechnicalIndicators

def debug_signal_generation():
    """Debug the signal generation process."""
    print("=== DEBUGGING SIGNAL GENERATION ===\n")
    
    # Check current time
    current_utc = datetime.datetime.utcnow()
    current_hour = current_utc.hour
    print(f"1. Current UTC time: {current_utc}")
    print(f"   Current UTC hour: {current_hour}")
    
    # Check updated time windows
    time_windows = [
        (3, 12),   # Early morning: 04:00-13:00 Dutch time
        (15, 20),  # Extended evening: 16:00-21:00 Dutch time
        (22, 24),  # Late night part 1: 23:00-00:00 Dutch time
        (0, 3)     # Late night part 2: 01:00-04:00 Dutch time (extended)
    ]
    in_time_window = False
    for start, end in time_windows:
        if start <= current_hour < end:
            in_time_window = True
            print(f"   ✅ Inside trading window: {start}:00-{end}:00 UTC")
            break
    
    if not in_time_window:
        print(f"   ❌ Outside trading windows: {time_windows}")
        print("   Extended Dutch time windows: 07:00-13:00, 16:00-21:00, 23:00-03:00")
    
    print()
    
    # Test data collection
    print("2. Testing data collection...")
    try:
        data_collector = BitcoinDataCollector()
        data = data_collector.fetch_latest_data(limit=100)
        print(f"   ✅ Data collected: {len(data)} rows")
        print(f"   Latest price: ${data['close'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"   ❌ Data collection failed: {e}")
        return
    
    print()
    
    # Test indicators
    print("3. Testing indicators...")
    try:
        data_with_indicators = TechnicalIndicators.add_all_indicators(data)
        print(f"   ✅ Indicators added successfully")
        
        # Show latest indicator values
        latest = data_with_indicators.iloc[-1]
        previous = data_with_indicators.iloc[-2]
        print(f"   RSI: {latest['rsi']:.2f} (prev: {previous['rsi']:.2f})")
        print(f"   MACD: {latest['macd']:.4f} (prev: {previous['macd']:.4f})")
        print(f"   BB Lower: ${latest['bb_lower']:.2f}")
        print(f"   BB Upper: ${latest['bb_upper']:.2f}")
        print(f"   Stoch %K: {latest['stoch_k']:.2f} (prev: {previous['stoch_k']:.2f})")
        print(f"   Stoch %D: {latest['stoch_d']:.2f}")
        
    except Exception as e:
        print(f"   ❌ Indicators calculation failed: {e}")
        return
    
    print()
    
    # Test signal generation
    print("4. Testing NEW scoring system...")
    try:
        signal_generator = SignalGenerator()
        
        # Test new scoring system
        buy_score = signal_generator._calculate_buy_score(data_with_indicators)
        sell_score = signal_generator._calculate_sell_score(data_with_indicators)
        
        print(f"   Buy score: {buy_score}/5")
        print(f"   Sell score: {sell_score}/5")
        
        # Show detailed scoring breakdown
        print("\n   Buy scoring breakdown:")
        print(f"   - RSI improving from oversold (<40): {latest['rsi'] < 40 and latest['rsi'] > previous['rsi']} (RSI: {latest['rsi']:.2f})")
        print(f"   - Price near BB lower (≤101% of lower): {latest['close'] <= latest['bb_lower'] * 1.01} (price: ${latest['close']:.2f}, lower: ${latest['bb_lower']:.2f})")
        print(f"   - MACD improving: {latest['macd'] > previous['macd']} (curr: {latest['macd']:.4f}, prev: {previous['macd']:.4f})")
        print(f"   - Stoch improving from oversold: {latest['stoch_k'] < 30 and latest['stoch_k'] > previous['stoch_k']} (curr: {latest['stoch_k']:.2f}, prev: {previous['stoch_k']:.2f})")
        
        volume_avg = data_with_indicators['volume'].rolling(window=10).mean().iloc[-1]
        volume_condition = latest['volume'] > volume_avg * 1.2
        print(f"   - Volume above average: {volume_condition} (curr: {latest['volume']:.0f}, avg*1.2: {volume_avg*1.2:.0f})")
        
        # Try to generate actual signal
        signal = signal_generator.generate_signal(data)
        if signal:
            print(f"\n   ✅ Signal generated: {signal['type']} at ${signal['price']:.2f} (score: {signal['score']})")
        else:
            print(f"\n   ❌ No signal generated (need score ≥2 and buy_score > sell_score)")
            
    except Exception as e:
        print(f"   ❌ Signal generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_signal_generation() 