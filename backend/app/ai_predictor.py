"""
AI-powered SPY price prediction system using GPT-4/5.
Generates predictions for Open, Noon, 2PM, and Close prices based on market analysis.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import os

import yfinance as yf
from openai import OpenAI

from .config import settings
from .providers import default_provider


@dataclass
class PricePrediction:
    """Single price prediction with confidence and reasoning."""
    checkpoint: str  # "open", "noon", "twoPM", "close"
    predicted_price: float
    confidence: float  # 0.0 to 1.0
    reasoning: str


@dataclass
class DayPredictions:
    """Complete set of predictions for a trading day."""
    date: date
    predictions: List[PricePrediction]
    market_context: str
    pre_market_price: Optional[float] = None
    created_at: Optional[datetime] = None


class AIPredictor:
    """GPT-4/5 powered SPY price predictor."""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.symbol = settings.symbol
    
    def generate_predictions(self, target_date: date) -> DayPredictions:
        """Generate AI predictions for a specific trading day."""
        
        # Gather market context
        context = self._gather_market_context(target_date)
        
        # Generate predictions using GPT-4/5
        predictions = self._get_ai_predictions(context, target_date)
        
        return DayPredictions(
            date=target_date,
            predictions=predictions,
            market_context=context["summary"],
            pre_market_price=context.get("pre_market_price"),
            created_at=datetime.now()
        )
    
    def _gather_market_context(self, target_date: date) -> Dict:
        """Gather comprehensive market context for AI analysis."""
        
        # Get historical SPY data (last 10 trading days)
        spy = yf.Ticker(self.symbol)
        end_date = target_date
        start_date = target_date - timedelta(days=15)  # Buffer for weekends
        
        hist = spy.history(start=start_date, end=end_date, interval="1d")
        
        # Get pre-market price if available
        pre_market_price = default_provider.get_price(self.symbol)
        
        # Calculate key technical levels
        recent_high = hist['High'].tail(5).max()
        recent_low = hist['Low'].tail(5).min()
        prev_close = hist['Close'].iloc[-1] if len(hist) > 0 else None
        
        # Calculate volatility indicators
        returns = hist['Close'].pct_change().dropna()
        volatility = returns.std() * (252 ** 0.5) if len(returns) > 1 else 0
        
        context = {
            "target_date": target_date.isoformat(),
            "pre_market_price": pre_market_price,
            "previous_close": float(prev_close) if prev_close else None,
            "recent_high": float(recent_high),
            "recent_low": float(recent_low),
            "annualized_volatility": float(volatility),
            "recent_prices": [
                {
                    "date": idx.strftime("%Y-%m-%d"),
                    "open": float(row.Open),
                    "high": float(row.High),
                    "low": float(row.Low),
                    "close": float(row.Close),
                    "volume": int(row.Volume)
                }
                for idx, row in hist.tail(5).iterrows()
            ],
            "summary": f"SPY analysis for {target_date}: Pre-market ${pre_market_price:.2f}, "
                      f"Previous close ${prev_close:.2f}, 5-day range ${recent_low:.2f}-${recent_high:.2f}"
        }
        
        return context
    
    def _get_ai_predictions(self, context: Dict, target_date: date) -> List[PricePrediction]:
        """Use GPT-4/5 to generate price predictions."""
        
        system_prompt = """You are an expert SPY (S&P 500 ETF) trader with advanced reasoning capabilities. 
Use deep analytical thinking to predict 4 key intraday price points.

Apply sophisticated analysis considering:
- Multi-timeframe technical patterns and momentum
- Market microstructure and institutional flows  
- Volatility regime analysis and mean reversion tendencies
- Cross-asset correlations and macro factors
- Order flow dynamics and support/resistance levels

You must respond with valid JSON containing predictions for:
- open: Market open price (9:30 AM EST)
- noon: Midday price (12:00 PM EST) 
- twoPM: Afternoon price (2:00 PM EST)
- close: Market close price (4:00 PM EST)

For each prediction, provide:
- predicted_price: Your price prediction (float)
- confidence: Your confidence level 0.0-1.0 (float) 
- reasoning: Brief explanation (string, max 100 chars)

Use your advanced reasoning to identify subtle patterns and provide highly calibrated predictions."""

        user_prompt = f"""Analyze SPY for {target_date.strftime('%Y-%m-%d')}:

MARKET DATA:
- Pre-market price: ${context['pre_market_price']:.2f}
- Previous close: ${context['previous_close']:.2f}
- 5-day high/low: ${context['recent_high']:.2f}/${context['recent_low']:.2f}
- Annualized volatility: {context['annualized_volatility']:.1%}

RECENT PRICE HISTORY:
{json.dumps(context['recent_prices'], indent=2)}

Provide predictions in this exact JSON format:
{{
  "analysis": "Your detailed market analysis explaining your reasoning, patterns identified, and key factors considered",
  "open": {{"predicted_price": 580.50, "confidence": 0.75, "reasoning": "Gap up on pre-market strength"}},
  "noon": {{"predicted_price": 582.25, "confidence": 0.70, "reasoning": "Continued momentum into lunch"}},
  "twoPM": {{"predicted_price": 581.80, "confidence": 0.65, "reasoning": "Slight pullback on profit taking"}},
  "close": {{"predicted_price": 583.10, "confidence": 0.72, "reasoning": "End of day buying interest"}}
}}"""

        try:
            # Use exact pattern from working AI assessment service
            model = "gpt-5"
            temperature = 0.3
            max_tokens = 2000
            reasoning_effort = "high"
            
            print(f"🤖 Using {model} for SPY predictions...")
            
            # Note: response_format might not be supported on all models
            # Try with response_format first, fall back if not supported
            try:
                # Prepare API parameters - EXACTLY like working file
                api_params = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "response_format": {"type": "json_object"}
                }
                
                # Add reasoning effort for GPT-5 models
                if model.startswith('gpt-5'):
                    api_params["reasoning_effort"] = reasoning_effort
                
                response = self.client.chat.completions.create(**api_params)
            except Exception as format_error:
                if "response_format" in str(format_error):
                    # Retry without response_format parameter but keep reasoning
                    fallback_params = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                    
                    # Add reasoning effort for GPT-5 models
                    if model.startswith('gpt-5'):
                        fallback_params["reasoning_effort"] = reasoning_effort
                    
                    response = self.client.chat.completions.create(**fallback_params)
                else:
                    raise format_error
            
            # Report token usage
            if hasattr(response, 'usage'):
                print(f"📊 GPT-5 Token Usage Report:")
                print(f"   - Prompt tokens: {response.usage.prompt_tokens}")
                print(f"   - Completion tokens: {response.usage.completion_tokens}")
                if hasattr(response.usage, 'completion_tokens_details'):
                    details = response.usage.completion_tokens_details
                    reasoning_tokens = getattr(details, 'reasoning_tokens', 0)
                    output_tokens = response.usage.completion_tokens - reasoning_tokens
                    print(f"   - Reasoning tokens: {reasoning_tokens}")
                    print(f"   - Output tokens: {output_tokens}")
                print(f"   - Total tokens: {response.usage.total_tokens}")
            
            # Parse the JSON response
            raw_content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if raw_content.startswith("```"):
                # Extract JSON from markdown code block
                lines = raw_content.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.startswith("```json"):
                        in_json = True
                        continue
                    elif line.startswith("```"):
                        in_json = False
                        continue
                    elif in_json:
                        json_lines.append(line)
                raw_content = '\n'.join(json_lines)
            
            prediction_data = json.loads(raw_content)
            
            # Extract analysis if present
            analysis = prediction_data.pop("analysis", "No detailed analysis provided")
            print(f"📝 Analysis extracted: {analysis[:100]}..." if len(analysis) > 100 else f"📝 Analysis: {analysis}")
            
            # Convert to PricePrediction objects
            predictions = []
            for checkpoint, data in prediction_data.items():
                predictions.append(PricePrediction(
                    checkpoint=checkpoint,
                    predicted_price=float(data["predicted_price"]),
                    confidence=float(data["confidence"]),
                    reasoning=data["reasoning"]
                ))
            
            # Store the full analysis in context for later use
            self.last_analysis = analysis
            
            return predictions
            
        except Exception as e:
            # Fallback to simple predictions if AI fails
            print(f"❌ AI prediction failed: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_predictions(context)
    
    def _fallback_predictions(self, context: Dict) -> List[PricePrediction]:
        """Simple fallback predictions if AI service fails."""
        base_price = context.get('pre_market_price') or context.get('previous_close', 580.0)
        
        return [
            PricePrediction("open", base_price * 1.001, 0.5, "Fallback: slight gap"),
            PricePrediction("noon", base_price * 1.002, 0.4, "Fallback: minor drift"),
            PricePrediction("twoPM", base_price * 1.001, 0.4, "Fallback: consolidation"),
            PricePrediction("close", base_price * 1.003, 0.5, "Fallback: end of day")
        ]


# Global instance
ai_predictor = AIPredictor()