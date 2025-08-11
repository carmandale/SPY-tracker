#!/usr/bin/env python3
"""Debug GPT-5 output issue."""

import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Testing GPT-5 with market prediction task...")
print("=" * 50)

# Simple market prediction prompt
system_prompt = """You are a SPY price predictor. Respond with JSON only."""

user_prompt = """Predict SPY prices for today. Current price: $637.

Output this exact JSON format:
{
  "open": {"predicted_price": 637.50, "confidence": 0.75, "reasoning": "slight gap up"},
  "noon": {"predicted_price": 638.00, "confidence": 0.70, "reasoning": "momentum"},
  "twoPM": {"predicted_price": 637.75, "confidence": 0.65, "reasoning": "pullback"},
  "close": {"predicted_price": 638.50, "confidence": 0.72, "reasoning": "end rally"}
}"""

try:
    print("\n1. Testing with high reasoning, 800 tokens...")
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        reasoning_effort="high",
        max_completion_tokens=800
    )
    
    content = response.choices[0].message.content
    print(f"Response content: {content}")
    
    if hasattr(response.usage, 'completion_tokens_details'):
        details = response.usage.completion_tokens_details
        print(f"Reasoning tokens: {details.reasoning_tokens}")
        print(f"Output tokens: {response.usage.completion_tokens - details.reasoning_tokens}")
    
    if content:
        try:
            data = json.loads(content)
            print(f"✅ Successfully parsed JSON!")
            print(f"Predicted open: ${data['open']['predicted_price']}")
        except:
            print(f"❌ Failed to parse JSON")
    else:
        print(f"❌ No content returned!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n2. Testing with medium reasoning...")
try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        reasoning_effort="medium",
        max_completion_tokens=500
    )
    
    content = response.choices[0].message.content
    print(f"Response content: {content}")
    if content:
        print("✅ Got output with medium reasoning!")
    else:
        print("❌ Still no output")
        
except Exception as e:
    print(f"Error: {e}")