#!/usr/bin/env python3
"""Test GPT-5 with low reasoning."""

import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Testing GPT-5 with LOW reasoning...")

# Very simple prompt
response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "user", "content": 'Output JSON: {"price": 637.50}'}
    ],
    reasoning_effort="low",
    max_completion_tokens=100
)

print(f"Response: '{response.choices[0].message.content}'")
if hasattr(response.usage, 'completion_tokens_details'):
    details = response.usage.completion_tokens_details
    print(f"Reasoning tokens: {details.reasoning_tokens}")
    print(f"Output tokens: {response.usage.completion_tokens - details.reasoning_tokens}")