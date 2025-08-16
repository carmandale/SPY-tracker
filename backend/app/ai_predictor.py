"""
AI-powered SPY price prediction system using GPT-4/5.
Generates predictions for Open, Noon, 2PM, and Close prices based on market analysis.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import os

import pandas as pd
import yfinance as yf
from openai import OpenAI

from .config import settings
from .providers import default_provider
from .timezone_utils import ET, get_checkpoint_datetime
from .baseline_model import baseline_predictor


# Prompt version for tracking changes
PROMPT_VERSION = "v2.0.0"  # Added prompt versioning, improved analysis


@dataclass
class PricePrediction:
    """Single price prediction with confidence and reasoning."""
    checkpoint: str  # "open", "noon", "twoPM", "close"
    predicted_price: float
    confidence: float  # 0.0 to 1.0
    reasoning: str
    interval_low: Optional[float] = None
    interval_high: Optional[float] = None
    source: str = "llm"
    model: Optional[str] = None
    prompt_version: Optional[str] = None


@dataclass
class DayPredictions:
    """Complete set of predictions for a trading day."""
    date: date
    predictions: List[PricePrediction]
    market_context: str
    pre_market_price: Optional[float] = None
    created_at: Optional[datetime] = None
    sentiment: Optional[Dict[str, Any]] = None


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
            created_at=datetime.now(),
            sentiment=getattr(self, "last_sentiment", None),
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
        
        # Calculate ATR (Average True Range)
        high_low = hist['High'] - hist['Low']
        high_close = abs(hist['High'] - hist['Close'].shift())
        low_close = abs(hist['Low'] - hist['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=14).mean().iloc[-1] if len(true_range) >= 14 else None
        
        # Get VIX data if available
        try:
            vix = yf.Ticker("^VIX")
            vix_hist = vix.history(start=start_date, end=end_date, interval="1d")
            vix_close = float(vix_hist['Close'].iloc[-1]) if len(vix_hist) > 0 else None
            vix_change = float(vix_hist['Close'].iloc[-1] - vix_hist['Close'].iloc[-2]) if len(vix_hist) > 1 else None
        except Exception:
            vix_close = None
            vix_change = None
        
        # Get ES futures data if available
        try:
            es = yf.Ticker("ES=F")
            es_hist = es.history(start=start_date, end=end_date, interval="1d")
            es_close = float(es_hist['Close'].iloc[-1]) if len(es_hist) > 0 else None
            es_change = float(es_hist['Close'].iloc[-1] - es_hist['Close'].iloc[-2]) if len(es_hist) > 1 else None
        except Exception:
            es_close = None
            es_change = None
        
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
            "atr_14day": float(atr) if atr is not None else None,
            "vix": {
                "close": vix_close,
                "change": vix_change
            } if vix_close is not None else None,
            "es_futures": {
                "close": es_close,
                "change": es_change
            } if es_close is not None else None,
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
- open: Market open price (9:30 AM ET)
- noon: Midday price (12:00 PM ET) 
- twoPM: Afternoon price (2:00 PM ET)
- close: Market close price (4:00 PM ET)

For each prediction, provide:
- predicted_price: Your price prediction (float)
- confidence: Your confidence level 0.0-1.0 (float) 
- reasoning: Brief explanation (string, max 100 chars)
- interval_low: Lower bound of 68% confidence interval (float)
- interval_high: Upper bound of 68% confidence interval (float)

Use your advanced reasoning to identify subtle patterns and provide highly calibrated predictions.
The confidence intervals should reflect a 68% probability (1-sigma) that the actual price will fall within that range.
Calibrate your intervals based on the provided volatility metrics."""

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

        # Format VIX and ES futures data if available
        vix_str = "N/A"
        if context.get('vix') and context['vix'].get('close') is not None:
            vix_close = context['vix']['close']
            vix_change = context['vix'].get('change')
            if vix_change is not None:
                vix_str = f"{vix_close:.2f} ({vix_change:+.2f})"
            else:
                vix_str = f"{vix_close:.2f}"
        
        es_str = "N/A"
        if context.get('es_futures') and context['es_futures'].get('close') is not None:
            es_close = context['es_futures']['close']
            es_change = context['es_futures'].get('change')
            if es_change is not None:
                es_str = f"{es_close:.2f} ({es_change:+.2f})"
            else:
                es_str = f"{es_close:.2f}"

        user_prompt = f"""Analyze SPY for {target_date.strftime('%Y-%m-%d')}:

MARKET DATA:
- Pre-market price: {safe_format_price(context.get('pre_market_price'))}
- Previous close: {safe_format_price(context.get('previous_close'))}
- 5-day high/low: {safe_format_price(context.get('recent_high'))}/{safe_format_price(context.get('recent_low'))}
- Annualized volatility: {safe_format_percent(context.get('annualized_volatility'))}
- 14-day ATR: {safe_format_price(context.get('atr_14day'))}
- VIX: {vix_str}
- ES Futures: {es_str}

RECENT PRICE HISTORY:
{json.dumps(context.get('recent_prices', []), indent=2)}

CHECKPOINT TIMES (All Eastern Time):
- open: 9:30 AM ET
- noon: 12:00 PM ET
- twoPM: 2:00 PM ET
- close: 4:00 PM ET

Provide predictions in this exact JSON format:
{{
  "analysis": "Your detailed market analysis explaining your reasoning, patterns identified, and key factors considered",
  "sentiment": {{"direction": "bullish|bearish|neutral", "confidence": 0.0, "regime": "range-bound|trend|volatile", "factors": ["factor1", "factor2"]}},
  "open": {{"predicted_price": 580.50, "confidence": 0.75, "reasoning": "Gap up on pre-market strength", "interval_low": 579.50, "interval_high": 581.50}},
  "noon": {{"predicted_price": 582.25, "confidence": 0.70, "reasoning": "Continued momentum into lunch", "interval_low": 580.75, "interval_high": 583.75}},
  "twoPM": {{"predicted_price": 581.80, "confidence": 0.65, "reasoning": "Slight pullback on profit taking", "interval_low": 580.00, "interval_high": 583.60}},
  "close": {{"predicted_price": 583.10, "confidence": 0.72, "reasoning": "End of day buying interest", "interval_low": 581.30, "interval_high": 584.90}}
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
            sentiment = prediction_data.pop("sentiment", None)
            print(f"📝 Analysis extracted: {analysis[:100]}..." if len(analysis) > 100 else f"📝 Analysis: {analysis}")

            # Convert to PricePrediction objects
            predictions = []
            for checkpoint, data in prediction_data.items():
                # Extract interval data with fallbacks
                interval_low = data.get("interval_low")
                interval_high = data.get("interval_high")
                
                # If intervals not provided, generate them based on confidence
                if interval_low is None or interval_high is None:
                    price = float(data["predicted_price"])
                    confidence = float(data["confidence"])
                    # Lower confidence = wider interval
                    width = (1.0 - confidence) * price * 0.02  # 2% at confidence=0
                    interval_low = price - width
                    interval_high = price + width
                
                predictions.append(PricePrediction(
                    checkpoint=checkpoint,
                    predicted_price=float(data["predicted_price"]),
                    confidence=float(data["confidence"]),
                    reasoning=data["reasoning"],
                    interval_low=float(interval_low),
                    interval_high=float(interval_high),
                    source="llm",
                    model=model,
                    prompt_version=PROMPT_VERSION
                ))

            self.last_analysis = analysis
            self.last_sentiment = sentiment if isinstance(sentiment, dict) else None
            return predictions
            
        except Exception as e:
            # Fallback to improved baseline predictions if AI fails
            print(f"❌ AI prediction failed: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_predictions(context)
    
    def _fallback_predictions(self, context: Dict) -> List[PricePrediction]:
        """Improved fallback predictions using baseline model if AI service fails."""
        try:
            # Use the baseline model for fallback predictions
            pre_market_price = context.get('pre_market_price')
            previous_close = context.get('previous_close')
            target_date = datetime.fromisoformat(context.get('target_date')).date()
            
            # Get predictions from baseline model
            baseline_preds = baseline_predictor.predict(
                target_date=target_date,
                pre_market_price=pre_market_price,
                previous_close=previous_close
            )
            
            # Convert to PricePrediction objects
            return [
                PricePrediction(
                    checkpoint=pred["checkpoint"],
                    predicted_price=pred["predicted_price"],
                    confidence=pred["confidence"],
                    reasoning=pred["reasoning"],
                    interval_low=pred["interval_low"],
                    interval_high=pred["interval_high"],
                    source="baseline",
                    model="baseline_statistical",
                    prompt_version="baseline_v1.0"
                )
                for pred in baseline_preds
            ]
        except Exception as e:
            # If even the baseline model fails, use a very simple fallback
            print(f"❌ Baseline fallback also failed: {e}")
            
            # Ultra-simple fallback
            base_price = context.get('pre_market_price') or context.get('previous_close', 580.0)
            volatility = context.get('annualized_volatility', 0.15) / 252**0.5  # Daily vol
            
            # Simple width calculation
            width = base_price * volatility
            
            return [
                PricePrediction("open", base_price * 1.001, 0.5, "Emergency fallback: slight gap", 
                               base_price * 0.998, base_price * 1.004, "emergency"),
                PricePrediction("noon", base_price * 1.002, 0.4, "Emergency fallback: minor drift", 
                               base_price * 0.997, base_price * 1.007, "emergency"),
                PricePrediction("twoPM", base_price * 1.001, 0.4, "Emergency fallback: consolidation", 
                               base_price * 0.996, base_price * 1.006, "emergency"),
                PricePrediction("close", base_price * 1.003, 0.5, "Emergency fallback: end of day", 
                               base_price * 0.995, base_price * 1.011, "emergency")
            ]


# Global instance
ai_predictor = AIPredictor()

