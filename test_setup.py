#!/usr/bin/env python3
"""
Test script to verify AI Analyst setup
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all dependencies are installed"""
    print("✓ Testing imports...")

    try:
        import flask
        print("  ✓ Flask")
    except ImportError:
        print("  ✗ Flask - run: pip install flask")
        return False

    try:
        import yfinance
        print("  ✓ yfinance")
    except ImportError:
        print("  ✗ yfinance - run: pip install yfinance")
        return False

    try:
        import pandas
        print("  ✓ pandas")
    except ImportError:
        print("  ✗ pandas - run: pip install pandas")
        return False

    try:
        import numpy
        print("  ✓ numpy")
    except ImportError:
        print("  ✗ numpy - run: pip install numpy")
        return False

    try:
        import talib
        print("  ✓ talib")
    except ImportError:
        print("  ✗ talib - run: pip install TA-Lib")
        return False

    try:
        import sklearn
        print("  ✓ scikit-learn")
    except ImportError:
        print("  ✗ scikit-learn - run: pip install scikit-learn")
        return False

    try:
        import google.generativeai
        print("  ✓ google-generativeai")
    except ImportError:
        print("  ✗ google-generativeai - run: pip install google-generativeai")
        return False

    return True

def test_api_keys():
    """Test if API keys are configured"""
    print("\n✓ Testing API keys...")

    from dotenv import load_dotenv
    load_dotenv()

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key != "your_gemini_api_key_here":
        print("  ✓ GEMINI_API_KEY configured")
    else:
        print("  ✗ GEMINI_API_KEY not configured - add to .env file")
        return False

    news_key = os.getenv("NEWS_API_KEY")
    if news_key and news_key != "your_newsapi_key_here":
        print("  ✓ NEWS_API_KEY configured")
    else:
        print("  ⚠ NEWS_API_KEY optional - sentiment analysis may be limited")

    return True

def test_data_fetcher():
    """Test data fetching"""
    print("\n✓ Testing data fetcher...")

    try:
        from data_fetcher import DataFetcher

        # Try to fetch AAPL data
        df = DataFetcher.fetch_stock_data("AAPL", period="1mo")
        if df is not None and not df.empty:
            print(f"  ✓ Successfully fetched AAPL data ({len(df)} rows)")
            return True
        else:
            print("  ✗ Failed to fetch data")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_technical_bot():
    """Test technical analysis bot"""
    print("\n✓ Testing technical analysis bot...")

    try:
        from data_fetcher import DataFetcher
        from technical_bot import TechnicalAnalysisBot

        df = DataFetcher.fetch_stock_data("AAPL", period="1y")
        bot = TechnicalAnalysisBot()
        result = bot.analyze(df, "AAPL")

        if result and "signal" in result:
            print(f"  ✓ Analysis complete: {result['signal']} (confidence: {result.get('confidence', 0):.2f})")
            return True
        else:
            print("  ✗ Analysis failed")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_ml_bot():
    """Test ML prediction bot"""
    print("\n✓ Testing ML prediction bot...")

    try:
        from data_fetcher import DataFetcher
        from ml_bot import MLPredictionBot

        df = DataFetcher.fetch_stock_data("AAPL", period="1y")
        bot = MLPredictionBot()
        result = bot.predict(df, "AAPL")

        if result and "signal" in result:
            print(f"  ✓ Prediction complete: {result['signal']}")
            return True
        else:
            print("  ✗ Prediction failed")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_sentiment_bot():
    """Test sentiment analysis bot"""
    print("\n✓ Testing sentiment bot...")

    try:
        from sentiment_bot import SentimentAnalysisBot

        bot = SentimentAnalysisBot()
        result = bot.analyze("AAPL")

        if result and "signal" in result:
            print(f"  ✓ Sentiment analysis complete: {result['signal']}")
            return True
        else:
            print("  ⚠ Sentiment analysis limited (API key may help)")
            return True
    except Exception as e:
        print(f"  ⚠ Warning: {e}")
        return True

def main():
    """Run all tests"""
    print("🤖 AI Analyst System Test\n" + "="*40)

    tests = [
        ("Imports", test_imports),
        ("API Keys", test_api_keys),
        ("Data Fetcher", test_data_fetcher),
        ("Technical Bot", test_technical_bot),
        ("ML Bot", test_ml_bot),
        ("Sentiment Bot", test_sentiment_bot),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name}: Unexpected error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*40)
    print("Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n✓ All tests passed! Ready to run: python app.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix issues above and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
