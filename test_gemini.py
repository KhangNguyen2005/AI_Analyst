#!/usr/bin/env python3
"""Test Gemini API connection and functionality"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

print("=" * 60)
print("GEMINI API TEST SUITE")
print("=" * 60)

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("FAILED: No GEMINI_API_KEY in .env file")
    exit(1)

print(f"OK - API Key found: {api_key[:20]}...")

# Test 1: Configure
print("\n[TEST 1] Configuring Gemini...")
try:
    genai.configure(api_key=api_key)
    print("OK - Configuration successful")
except Exception as e:
    print(f"FAILED - Configuration failed: {e}")
    exit(1)

# Test 2: Create model
print("\n[TEST 2] Creating model instance...")
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    print("OK - Model created: gemini-2.5-flash")
except Exception as e:
    print(f"FAILED - Model creation failed: {e}")
    exit(1)

# Test 3: Simple API call
print("\n[TEST 3] Making simple API call...")
try:
    response = model.generate_content("What is 2+2?")
    print(f"OK - API call successful!")
    print(f"  Response: {response.text[:80]}...")
except Exception as e:
    print(f"FAILED - API call failed: {type(e).__name__}")
    print(f"  Error: {str(e)}")

# Test 4: JSON response test
print("\n[TEST 4] Testing JSON response (like AI Synthesizer)...")
try:
    prompt = """Respond ONLY with valid JSON. No markdown, no code blocks.
{
    "signal": "BUY",
    "confidence": 85,
    "reasoning": "Test response"
}"""
    response = model.generate_content(prompt)
    print(f"OK - JSON test response received")
    print(f"  Response preview: {response.text[:100]}...")
    
    # Try to parse JSON
    try:
        data = json.loads(response.text)
        print(f"OK - JSON parsed successfully: signal={data.get('signal')}")
    except json.JSONDecodeError as je:
        print(f"FAILED - JSON parsing failed: {je}")
        
except Exception as e:
    print(f"FAILED - JSON test failed: {type(e).__name__}")
    print(f"  Error: {str(e)}")

# Test 5: Financial analysis test
print("\n[TEST 5] Financial analysis test (AAPL mock)...")
try:
    finance_prompt = """You are a financial analyst. Analyze this data:
Symbol: AAPL
Current Price: $285
Technical Signal: BUY
Sentiment: POSITIVE
ML Score: 0.78

Respond with ONLY a JSON object:
{
    "signal": "BUY or SELL or NEUTRAL",
    "confidence": 0-100,
    "action_summary": "brief summary"
}"""
    
    response = model.generate_content(finance_prompt)
    print(f"OK - Finance test API call successful!")
    print(f"  Response: {response.text[:120]}...")
except Exception as e:
    print(f"FAILED - Finance test failed: {type(e).__name__}")
    print(f"  Error: {str(e)}")

print("\n" + "=" * 60)
print("TEST SUITE COMPLETE")
print("=" * 60)
