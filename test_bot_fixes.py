#!/usr/bin/env python3
"""Test the fixes for Technical and ML bots"""

from technical_bot import TechnicalAnalysisBot
from ml_bot import MLPredictionBot
from data_fetcher import DataFetcher
import warnings

warnings.filterwarnings('ignore')

print("=" * 60)
print("TESTING BOT FIXES")
print("=" * 60)

# Test Technical Bot
print("\n[TEST 1] Technical Bot - Array Dimension Fix")
print("-" * 60)
try:
    bot = TechnicalAnalysisBot()
    df = DataFetcher.fetch_stock_data('AAPL', period='6mo', interval='1d')
    
    if df is not None and len(df) > 0:
        result = bot.analyze(df, 'AAPL')
        print(f"OK - Technical analysis completed")
        print(f"  Symbol: {result['symbol']}")
        print(f"  Signal: {result['signal']}")
        print(f"  Confidence: {result['confidence']:.2%}")
    else:
        print("FAILED - No data available")
except Exception as e:
    print(f"FAILED - {type(e).__name__}: {e}")

# Test ML Bot
print("\n[TEST 2] ML Bot - DataFrame Assignment Fix")
print("-" * 60)
try:
    bot = MLPredictionBot()
    df = DataFetcher.fetch_stock_data('MSFT', period='6mo', interval='1d')
    
    if df is not None and len(df) > 0:
        model = bot.train_model(df, 'MSFT')
        if model is not None:
            print(f"OK - ML model trained successfully")
            print(f"  Model type: {type(model).__name__}")
        else:
            print("FAILED - Model returned None")
    else:
        print("FAILED - No data available")
except Exception as e:
    print(f"FAILED - {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nConclusion:")
print("OK - If both tests show OK, the fixes are working!")
print("OK - App should now run without Technical Bot or ML Bot errors")
