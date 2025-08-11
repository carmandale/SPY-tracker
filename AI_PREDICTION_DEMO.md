# SPY TA Tracker - AI Prediction System

## 🤖 Advanced GPT-4/5 Price Prediction System

The SPY TA Tracker now includes sophisticated AI-powered price prediction using GPT-4/5 to analyze market conditions and predict 4 key intraday price points.

## System Architecture

### 1. **Real Market Data Integration**
- ✅ **Live SPY Data**: Uses yfinance for real-time SPY prices
- ✅ **Scheduled Capture**: Automated price logging at Open/Noon/2PM/Close
- ✅ **Historical Analysis**: 10-day price history for context
- ✅ **Technical Indicators**: Volatility, support/resistance levels

### 2. **AI Prediction Engine** (`ai_predictor.py`)
```python
# GPT-4/5 analyzes:
- Pre-market price movements
- 5-day price history and volatility  
- Technical support/resistance levels
- Volume patterns and market sentiment

# Generates predictions for:
- Market Open (9:30 AM EST): $580.50 (confidence: 0.75)
- Noon (12:00 PM EST): $582.25 (confidence: 0.70) 
- 2:00 PM (2:00 PM EST): $581.80 (confidence: 0.65)
- Market Close (4:00 PM EST): $583.10 (confidence: 0.72)
```

### 3. **Accuracy Tracking System**
- **Real-time Comparison**: AI predictions vs actual SPY prices
- **Performance Metrics**: Mean Absolute Error, accuracy rates
- **Confidence Calibration**: How well confidence scores match actual accuracy
- **Learning Feedback**: Continuous improvement based on results

## API Endpoints

### Generate AI Predictions
```bash
GET /ai/predictions/2025-08-11
```
Response:
```json
{
  "date": "2025-08-11",
  "market_context": "SPY analysis: Pre-market $579.50, Previous close $578.25, 5-day range $575.10-$582.40",
  "predictions": [
    {
      "checkpoint": "open",
      "predicted_price": 580.50,
      "confidence": 0.75,
      "reasoning": "Gap up on pre-market strength",
      "actual_price": 580.25,
      "prediction_error": 0.25
    }
  ],
  "accuracy_summary": {
    "mean_absolute_error": 0.68,
    "accuracy_rate": 0.75
  }
}
```

### Accuracy Analytics
```bash
GET /ai/accuracy
```
Response:
```json
{
  "overall_mae": 0.82,
  "checkpoint_performance": {
    "open": {"mean_absolute_error": 0.65, "accuracy_rate_1dollar": 0.85},
    "close": {"mean_absolute_error": 0.95, "accuracy_rate_1dollar": 0.70}
  },
  "confidence_calibration": {
    "high": {"mean_absolute_error": 0.55, "count": 12},
    "medium": {"mean_absolute_error": 0.88, "count": 8}
  }
}
```

### Complete System Demo
```bash
GET /ai/demo
```
Shows full workflow with explanations and next steps.

## Database Schema

### `ai_predictions` Table
```sql
- id: Primary key
- date: Trading date
- checkpoint: open|noon|twoPM|close  
- predicted_price: AI generated price
- confidence: 0.0 to 1.0 confidence score
- reasoning: Brief explanation of prediction logic
- market_context: Market conditions summary
- actual_price: Real SPY price (filled when available)
- prediction_error: |predicted - actual|
```

## Morning Workflow

1. **8:00 AM CST**: System gathers market context
   - Historical SPY data (last 10 days)
   - Pre-market price movements
   - Volatility calculations
   - Technical support/resistance levels

2. **GPT-4/5 Analysis**: AI processes data with prompt:
   ```
   "You are an expert SPY trader. Analyze these market conditions 
   and predict Open/Noon/2PM/Close prices with confidence scores..."
   ```

3. **Prediction Storage**: Save all predictions to database

4. **Real-time Tracking**: As actual prices come in:
   - Compare with AI predictions
   - Calculate prediction errors
   - Update accuracy metrics
   - Generate performance insights

## Setup Requirements

### Environment Variables
```bash
# Add to .env or .env.local
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Dependencies (already installed)
```python
openai>=1.0.0
yfinance>=0.2.65
```

## Usage Example

```python
from ai_predictor import ai_predictor
from datetime import date

# Generate predictions for today
predictions = ai_predictor.generate_predictions(date.today())

print(f"Market Context: {predictions.market_context}")
for pred in predictions.predictions:
    print(f"{pred.checkpoint}: ${pred.predicted_price:.2f} "
          f"(confidence: {pred.confidence:.1%})")
    print(f"  Reasoning: {pred.reasoning}")
```

## Key Features

### 🎯 **Precision Tracking**
- Track prediction accuracy down to the penny
- Separate performance metrics for each time checkpoint
- Confidence calibration analysis

### 🧠 **Advanced AI Analysis** 
- GPT-4/5 processes multiple market signals
- Considers technical levels, volatility, sentiment
- Provides reasoning for each prediction

### 📊 **Performance Analytics**
- Mean Absolute Error tracking
- Accuracy rate analysis (within $1.00)
- Confidence score validation
- Checkpoint-specific performance

### 🔄 **Continuous Learning**
- System learns from prediction accuracy
- Adapts to market conditions over time
- Feedback loop for model improvement

## Next Steps

1. **Add OpenAI API Key** to enable AI predictions
2. **Test the system** using the demo endpoints  
3. **Integrate with frontend** to show predictions vs reality
4. **Enable scheduling** for automatic morning predictions
5. **Add visualization** of accuracy trends over time

The system is designed to provide sophisticated market analysis while maintaining transparency about prediction confidence and accuracy. This enables data-driven trading decisions with clear performance tracking.

---

**Note**: This is a trading analysis tool only. All predictions are for educational/tracking purposes and should not be considered investment advice.