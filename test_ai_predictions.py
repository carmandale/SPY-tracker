#!/usr/bin/env python3
"""
Simple test script to demonstrate GPT-4 powered SPY predictions.
This shows the AI system working with real OpenAI API calls.
"""

import os
import sys
import json
from datetime import date, datetime

# Add backend to path
sys.path.append('/Users/dalecarman/Groove Jones Dropbox/Dale Carman/Projects/dev/SPY-tracker/backend')

from app.ai_predictor import AIPredictor
import yfinance as yf

def test_ai_predictions():
    """Test the AI prediction system with real OpenAI API."""
    
    print("🤖 SPY TA Tracker - AI Prediction System Test")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("Please add your OpenAI API key to .env file")
        return
    
    print(f"✅ OpenAI API key found: {api_key[:8]}...")
    
    # Test real SPY data fetch
    print("\n📊 Testing Real SPY Data Fetch...")
    spy = yf.Ticker("SPY")
    try:
        current_price = spy.fast_info.last_price
        print(f"✅ Current SPY price: ${current_price:.2f}")
        
        # Get recent history
        hist = spy.history(period="5d")
        print(f"✅ 5-day price range: ${hist['Low'].min():.2f} - ${hist['High'].max():.2f}")
        
    except Exception as e:
        print(f"❌ Error fetching SPY data: {e}")
        return
    
    # Test AI prediction generation
    print("\n🧠 Testing GPT-4 Prediction Generation...")
    try:
        predictor = AIPredictor()
        target_date = date.today()
        
        print(f"📅 Generating predictions for: {target_date}")
        print("🔄 Calling OpenAI GPT-4...")
        
        predictions = predictor.generate_predictions(target_date)
        
        print("✅ AI predictions generated successfully!")
        print(f"\n🎯 Market Context: {predictions.market_context}")
        print(f"📈 Pre-market Price: ${predictions.pre_market_price:.2f}")
        
        print(f"\n🤖 GPT-4 Predictions:")
        print("-" * 40)
        
        for pred in predictions.predictions:
            confidence_bar = "█" * int(pred.confidence * 10)
            print(f"  {pred.checkpoint.upper():>8}: ${pred.predicted_price:>7.2f} "
                  f"({pred.confidence:.1%}) {confidence_bar}")
            print(f"           Reasoning: {pred.reasoning}")
            print()
        
        return predictions
        
    except Exception as e:
        print(f"❌ Error generating AI predictions: {e}")
        print(f"Error details: {type(e).__name__}: {str(e)}")
        return None

def compare_with_mock_actual(predictions):
    """Demonstrate accuracy comparison with mock actual prices."""
    if not predictions:
        return
        
    print("\n📊 Accuracy Analysis Demo")
    print("=" * 30)
    
    # Mock some actual prices for demonstration
    mock_actuals = {
        "open": predictions.pre_market_price * 1.002,  # Small gap up
        "noon": predictions.pre_market_price * 1.004,   # Continued rise
        "twoPM": predictions.pre_market_price * 1.003,  # Slight pullback
        "close": predictions.pre_market_price * 1.005   # End higher
    }
    
    total_error = 0
    accurate_predictions = 0
    
    print("Prediction vs 'Actual' Comparison:")
    print("-" * 40)
    
    for pred in predictions.predictions:
        actual = mock_actuals.get(pred.checkpoint)
        if actual:
            error = abs(pred.predicted_price - actual)
            total_error += error
            is_accurate = error <= 1.0
            if is_accurate:
                accurate_predictions += 1
            
            status = "✅ GOOD" if is_accurate else "❌ MISS"
            print(f"  {pred.checkpoint.upper():>8}: Pred ${pred.predicted_price:>7.2f} | "
                  f"Actual ${actual:>7.2f} | Error ${error:>5.2f} | {status}")
    
    mae = total_error / len(predictions.predictions)
    accuracy = accurate_predictions / len(predictions.predictions)
    
    print(f"\n📈 Performance Metrics:")
    print(f"  Mean Absolute Error: ${mae:.2f}")
    print(f"  Accuracy Rate (±$1): {accuracy:.1%}")
    print(f"  Predictions within $1: {accurate_predictions}/{len(predictions.predictions)}")

if __name__ == "__main__":
    predictions = test_ai_predictions()
    if predictions:
        compare_with_mock_actual(predictions)
        print("\n🎉 AI Prediction System Test Complete!")
        print("\nThis demonstrates:")
        print("• Real SPY data fetching via yfinance")
        print("• GPT-4 powered market analysis")
        print("• Confidence-scored price predictions")
        print("• Accuracy tracking capabilities")
    else:
        print("\n❌ AI Prediction System Test Failed")
        print("Check your OpenAI API key and internet connection")