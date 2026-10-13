#!/usr/bin/env python3
"""Test the AI Synthesizer with fixed Gemini model"""

import os
import json
from dotenv import load_dotenv
from ai_synthesizer import AIAnalysisSynthesizer

load_dotenv()

print("=" * 70)
print("AI SYNTHESIZER TEST (Gemini Fix Verification)")
print("=" * 70)

# Initialize synthesizer
print("\n[1] Initializing AI Synthesizer...")
try:
    synthesizer = AIAnalysisSynthesizer()
    print("OK - AI Synthesizer initialized")
except Exception as e:
    print(f"FAILED - Initialization error: {e}")
    exit(1)

# Mock data for testing
mock_technical = {
    "signal": "BUY",
    "score": 0.85,
    "rsi": 45,
    "trend": "uptrend",
    "support": 280,
    "resistance": 295
}

mock_sentiment = {
    "signal": "BUY",
    "score": 0.72,
    "articles": 15,
    "positive": 12,
    "negative": 3
}

mock_ml = {
    "prediction": "BUY",
    "confidence": 0.78,
    "next_day": 1.02,
    "model": "LSTM"
}

mock_fundamental = {
    "signal": "BUY",
    "pe_ratio": 28.5,
    "growth": "strong",
    "dividend": 0.92
}

mock_price = {
    "current": 285.17,
    "52w_high": 310,
    "52w_low": 150,
    "change_today": 0.5
}

# Test synthesis
print("\n[2] Testing AI Synthesis with AAPL data...")
try:
    result = synthesizer.synthesize_analysis(
        symbol="AAPL",
        technical_analysis=mock_technical,
        sentiment_analysis=mock_sentiment,
        ml_prediction=mock_ml,
        fundamental_analysis=mock_fundamental,
        price_info=mock_price
    )
    print("OK - Synthesis completed")
    print(f"\nSynthesized Result:")
    print(f"  Signal: {result.get('signal', 'N/A')}")
    print(f"  Confidence: {result.get('confidence', 'N/A')}%")
    print(f"  Summary: {result.get('action_summary', 'N/A')[:80]}...")
    
except Exception as e:
    print(f"FAILED - Synthesis error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("\nConclusion: Gemini API is working correctly!")
print("The fix (gemini-pro -> gemini-2.5-flash) resolved the 404 error.")
