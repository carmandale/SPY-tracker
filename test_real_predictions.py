#!/usr/bin/env python3
"""Test REAL AI predictions with o1-mini."""

import os
import sys
from datetime import date

# Add backend to path
sys.path.append('/Users/dalecarman/Groove Jones Dropbox/Dale Carman/Projects/dev/SPY-tracker/backend')

from app.ai_predictor import ai_predictor

print("🤖 Testing REAL AI Predictions with o1-mini...")
print("=" * 50)

try:
    predictions = ai_predictor.generate_predictions(date.today())
    
    print(f"\n📊 Market Context:")
    print(f"   {predictions.market_context}")
    
    print(f"\n💰 Pre-market: ${predictions.pre_market_price:.2f}" if predictions.pre_market_price else "\n💰 Pre-market: Loading...")
    
    print(f"\n🎯 AI PREDICTIONS (REAL VALUES):")
    print("-" * 40)
    for p in predictions.predictions:
        print(f"  {p.checkpoint.upper():>8}: ${p.predicted_price:>7.2f} ({p.confidence:.0%})")
        print(f"           {p.reasoning}")
        print()
    
    # Calculate range
    prices = [p.predicted_price for p in predictions.predictions]
    print(f"📈 Predicted Range: ${min(prices):.2f} - ${max(prices):.2f}")
    print(f"📊 Predicted Mid: ${(min(prices) + max(prices))/2:.2f}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()