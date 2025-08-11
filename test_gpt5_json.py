#!/usr/bin/env python3
"""Test GPT-5 JSON response for SPY predictions."""

import os
import json
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

print("Testing GPT-5 JSON response...")

system_prompt = """You are an expert SPY trader. Respond with valid JSON containing predictions."""

user_prompt = """Analyze SPY and provide predictions in this exact JSON format:
{
  "open": {"predicted_price": 580.50, "confidence": 0.75, "reasoning": "Gap up expected"},
  "noon": {"predicted_price": 582.25, "confidence": 0.70, "reasoning": "Momentum continues"},
  "twoPM": {"predicted_price": 581.80, "confidence": 0.65, "reasoning": "Afternoon pullback"},
  "close": {"predicted_price": 583.10, "confidence": 0.72, "reasoning": "End of day buying"}
}"""

try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        reasoning_effort="high",
        max_completion_tokens=1000
    )
    
    raw_response = response.choices[0].message.content
    print(f"\n📝 Raw response:\n{raw_response}\n")
    
    # Try to parse as JSON
    try:
        data = json.loads(raw_response)
        print("✅ Successfully parsed as JSON!")
        print(f"📊 Parsed data: {json.dumps(data, indent=2)}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print("Response is not valid JSON format")
        
except Exception as e:
    print(f"❌ API call failed: {e}")