#!/usr/bin/env python3
"""Test script to verify GPT-5 model configuration."""

import os
from openai import OpenAI

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ OPENAI_API_KEY not found")
    exit(1)

print(f"✅ API Key found: {api_key[:8]}...")

client = OpenAI(api_key=api_key)

# Test 1: Try GPT-5 with reasoning_effort
print("\n🧪 Test 1: GPT-5 with reasoning_effort='high'")
try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "user", "content": "What is 2+2? Reply with just the number."}
        ],
        reasoning_effort="high",
        max_completion_tokens=100
    )
    print(f"✅ GPT-5 works! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ GPT-5 failed: {e}")

# Test 2: Try o1-preview
print("\n🧪 Test 2: o1-preview (latest reasoning model)")
try:
    response = client.chat.completions.create(
        model="o1-preview",
        messages=[
            {"role": "user", "content": "What is 2+2? Reply with just the number."}
        ],
        max_completion_tokens=100
    )
    print(f"✅ o1-preview works! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ o1-preview failed: {e}")

# Test 3: Try o1-mini
print("\n🧪 Test 3: o1-mini (faster reasoning model)")
try:
    response = client.chat.completions.create(
        model="o1-mini",
        messages=[
            {"role": "user", "content": "What is 2+2? Reply with just the number."}
        ],
        max_completion_tokens=100
    )
    print(f"✅ o1-mini works! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ o1-mini failed: {e}")

# Test 4: Try GPT-4o
print("\n🧪 Test 4: GPT-4o (standard model)")
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "What is 2+2? Reply with just the number."}
        ],
        max_tokens=100
    )
    print(f"✅ GPT-4o works! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ GPT-4o failed: {e}")

print("\n📊 Summary:")
print("Based on these tests, use the working model in your configuration.")