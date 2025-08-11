#!/usr/bin/env python3
"""Test GPT-5 with different approaches to get output."""

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Testing GPT-5 output methods...\n")

# Test 1: Simple request without reasoning_effort
print("Test 1: GPT-5 without reasoning_effort")
try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "user", "content": "What is 2+2? Reply with just the number."}
        ],
        max_completion_tokens=100
    )
    print(f"Response: '{response.choices[0].message.content}'")
    print(f"Finish reason: {response.choices[0].finish_reason}")
    print(f"Usage: {response.usage}\n")
except Exception as e:
    print(f"Failed: {e}\n")

# Test 2: With reasoning_effort=low
print("Test 2: GPT-5 with reasoning_effort='low'")
try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "user", "content": "What is 2+2? Reply with just the number."}
        ],
        reasoning_effort="low",
        max_completion_tokens=100
    )
    print(f"Response: '{response.choices[0].message.content}'")
    print(f"Finish reason: {response.choices[0].finish_reason}")
    print(f"Usage: {response.usage}\n")
except Exception as e:
    print(f"Failed: {e}\n")

# Test 3: With reasoning_effort=medium
print("Test 3: GPT-5 with reasoning_effort='medium'")
try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "user", "content": "What is 2+2? Reply with just the number."}
        ],
        reasoning_effort="medium",
        max_completion_tokens=100
    )
    print(f"Response: '{response.choices[0].message.content}'")
    print(f"Finish reason: {response.choices[0].finish_reason}")
    print(f"Usage: {response.usage}\n")
except Exception as e:
    print(f"Failed: {e}\n")

# Test 4: Asking for JSON directly
print("Test 4: GPT-5 JSON request with high reasoning")
try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "user", "content": 'Output this exact JSON: {"result": 4}'}
        ],
        reasoning_effort="high",
        max_completion_tokens=2000
    )
    print(f"Response: '{response.choices[0].message.content}'")
    print(f"Finish reason: {response.choices[0].finish_reason}")
    if hasattr(response.usage, 'completion_tokens_details'):
        details = response.usage.completion_tokens_details
        print(f"Reasoning tokens: {details.reasoning_tokens}")
        print(f"Output tokens: {response.usage.completion_tokens - details.reasoning_tokens}\n")
except Exception as e:
    print(f"Failed: {e}\n")

# Test 5: Check if we need to access a different field
print("Test 5: Exploring response structure")
try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "user", "content": "Say 'hello'"}
        ],
        reasoning_effort="high",
        max_completion_tokens=2000
    )
    print(f"Response content: '{response.choices[0].message.content}'")
    print(f"Response object dir: {[x for x in dir(response.choices[0].message) if not x.startswith('_')]}")
    print(f"Full message: {response.choices[0].message}")
except Exception as e:
    print(f"Failed: {e}\n")