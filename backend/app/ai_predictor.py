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
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key and self.api_key != 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx':
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            print("⚠️  OpenAI API key not configured - AI predictions unavailable")
        self.symbol = settings.symbol
    
    def generate_predictions(self, target_date: date, lookback_days: int = 5) -> DayPredictions:
        """Generate AI predictions for a specific trading day."""
        
        # Gather market context
        context = self._gather_market_context(target_date, lookback_days=lookback_days)
        
        # Generate predictions using GPT-4/5
        predictions = self._get_ai_predictions(context, target_date)
        # Prefer rich AI analysis when available; fall back to concise summary
        analysis_text = getattr(self, "last_analysis", None) or context["summary"]

        return DayPredictions(
            date=target_date,
            predictions=predictions,
            market_context=analysis_text,
            pre_market_price=context.get("pre_market_price"),
            created_at=datetime.now()
        )
    
    def _gather_market_context(self, target_date: date, lookback_days: int = 5) -> Dict:
        """Gather comprehensive market context for AI analysis."""
        
        # Get historical SPY data (last N trading days)
        spy = yf.Ticker(self.symbol)
        end_date = target_date
        # Multiply by 3 to buffer weekends/holidays
        start_date = target_date - timedelta(days=lookback_days * 3)
        
        hist = spy.history(start=start_date, end=end_date, interval="1d")
        
        # Get pre-market price if available
        pre_market_price = default_provider.get_price(self.symbol)
        
        # Calculate key technical levels
        recent_high = hist['High'].tail(lookback_days).max()
        recent_low = hist['Low'].tail(lookback_days).min()
        prev_close = hist['Close'].iloc[-1] if len(hist) > 0 else None
        
        # Calculate volatility indicators
        returns = hist['Close'].pct_change().dropna()
        volatility = returns.std() * (252 ** 0.5) if len(returns) > 1 else 0
        
        def safe_format_price(value, fallback="N/A"):
            if value is None:
                return fallback
            try:
                return f"${float(value):.2f}"
            except (ValueError, TypeError):
                return fallback

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
                for idx, row in hist.tail(lookback_days).iterrows()
            ],
            "summary": f"SPY analysis for {target_date}: Pre-market {safe_format_price(pre_market_price)}, "
                      f"Previous close {safe_format_price(prev_close)}, {lookback_days}-day range {safe_format_price(recent_low)}-{safe_format_price(recent_high)}"
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

        # Safely format context values to handle None values
        def safe_format_price(value, fallback="N/A"):
            if value is None:
                return fallback
            try:
                return f"${float(value):.2f}"
            except (ValueError, TypeError):
                return fallback
        
        def safe_format_percent(value, fallback="N/A"):
            if value is None:
                return fallback
            try:
                return f"{float(value):.1%}"
            except (ValueError, TypeError):
                return fallback

        user_prompt = f"""Analyze SPY for {target_date.strftime('%Y-%m-%d')}:

MARKET DATA:
- Pre-market price: {safe_format_price(context.get('pre_market_price'))}
- Previous close: {safe_format_price(context.get('previous_close'))}
- 5-day high/low: {safe_format_price(context.get('recent_high'))}/{safe_format_price(context.get('recent_low'))}
- Annualized volatility: {safe_format_percent(context.get('annualized_volatility'))}

RECENT PRICE HISTORY:
{json.dumps(context.get('recent_prices', []), indent=2)}

Provide predictions in this exact JSON format:
{{
  "analysis": "Your detailed market analysis explaining your reasoning, patterns identified, and key factors considered",
  "open": {{"predicted_price": 580.50, "confidence": 0.75, "reasoning": "Gap up on pre-market strength"}},
  "noon": {{"predicted_price": 582.25, "confidence": 0.70, "reasoning": "Continued momentum into lunch"}},
  "twoPM": {{"predicted_price": 581.80, "confidence": 0.65, "reasoning": "Slight pullback on profit taking"}},
  "close": {{"predicted_price": 583.10, "confidence": 0.72, "reasoning": "End of day buying interest"}}
}}"""

        try:
            # Use Chat Completions like your working service, with JSON mode + fallback
            from .config import settings
            model = settings.openai_model
            max_tokens = settings.openai_max_completion_tokens
            reasoning_effort = settings.openai_reasoning_effort

            print(f"🤖 Using {model} (chat.completions) for SPY predictions...")

            try:
                api_params = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an expert SPY trader. Always respond with valid JSON only."},
                        {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"},
                    ],
                    "max_completion_tokens": max_tokens,
                    "response_format": {"type": "json_object"},
                }
                if model.startswith("gpt-5"):
                    api_params["reasoning_effort"] = reasoning_effort
                response = self.client.chat.completions.create(**api_params)
            except Exception as format_error:
                # Fallback without response_format
                fallback_params = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an expert SPY trader. Always respond with valid JSON only."},
                        {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"},
                    ],
                    "max_completion_tokens": max_tokens,
                }
                if model.startswith("gpt-5"):
                    fallback_params["reasoning_effort"] = reasoning_effort
                response = self.client.chat.completions.create(**fallback_params)

            # Token usage logging (best-effort)
            try:
                u = response.usage
                print("📊 Token Usage:")
                print(f"   - prompt: {getattr(u, 'prompt_tokens', None)}")
                print(f"   - completion: {getattr(u, 'completion_tokens', None)}")
                print(f"   - total: {getattr(u, 'total_tokens', None)}")
            except Exception:
                pass

            raw_content = None
            # Prefer tool JSON if tool-choosing happened, else message.content
            if response and getattr(response.choices[0].message, "refusal", None):
                # If refusal, force fallback
                raw_content = None
            else:
                raw_content = response.choices[0].message.content
            if not raw_content:
                raise ValueError("No content from Chat Completions API")

            # Remove markdown code fences if present
            if raw_content.startswith("```"):
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
                raw_content = '\n'.join(json_lines) or raw_content

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