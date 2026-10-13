#!/usr/bin/env python3
"""List available Gemini models"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("✗ No GEMINI_API_KEY found")
    exit(1)

genai.configure(api_key=api_key)

print("=" * 60)
print("AVAILABLE GEMINI MODELS")
print("=" * 60)

try:
    models = genai.list_models()
    print(f"\nTotal models available: {len(list(models))}\n")
    
    # Re-fetch since list_models is a generator
    for model in genai.list_models():
        model_name = model.name.split('/')[-1]
        supported_methods = model.supported_generation_methods
        
        if 'generateContent' in supported_methods:
            print(f"✓ {model_name}")
            print(f"  Methods: {supported_methods}")
            print()
            
except Exception as e:
    print(f"Error listing models: {e}")
