#!/usr/bin/env python3
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    print("Please make sure you have a .env file with: GEMINI_API_KEY=your_actual_key")
    exit(1)

print(f"🔑 API Key found: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)

    # List available models
    print("📋 Checking available models...")
    models = genai.list_models()

    if not models:
        print("❌ No models found. Possible issues:")
        print("   - API key is invalid")
        print("   - API key doesn't have proper permissions")
        print("   - Regional restrictions")
        exit(1)

    print("✅ Available models:")
    for model in models:
        methods = model.supported_generation_methods
        if 'generateContent' in methods:
            print(f"   ✅ {model.name} - supports generateContent")
        else:
            print(f"   ❌ {model.name} - no generateContent")

    # Test with a simple prompt
    print("\n🧪 Testing model with simple prompt...")
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say 'Hello World'")
        print(f"✅ Test successful: {response.text}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

except Exception as e:
    print(f"❌ Configuration error: {e}")