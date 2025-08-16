"""
AI-powered SPY price prediction system using GPT-4/5.
Generates predictions for Open, Noon, 2PM, and Close prices based on market analysis.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import os
import logging

import pandas as pd
import yfinance as yf
from openai import OpenAI

from .config import settings
from .providers import default_provider
from .timezone_utils import ET, get_checkpoint_datetime
from .baseline_model import baseline_predictor

# Set up logging
logger = logging.getLogger(__name__)


# Prompt version for tracking changes
PROMPT_VERSION = "v3.0.0"  # Enhanced with comprehensive expert analysis, technical indicators, and regime detection


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
            logger.warning("OpenAI API key not configured - AI predictions unavailable")
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
        
        # Calculate additional technical indicators for enhanced analysis
        close_prices = hist['Close']
        
        # RSI (Relative Strength Index) - momentum oscillator
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = float(rsi.iloc[-1]) if len(rsi) > 0 and not pd.isna(rsi.iloc[-1]) else None
        
        # Moving averages for trend identification
        sma_20 = close_prices.rolling(window=20).mean().iloc[-1] if len(close_prices) >= 20 else None
        sma_50 = close_prices.rolling(window=50).mean().iloc[-1] if len(close_prices) >= 50 else None
        ema_9 = close_prices.ewm(span=9, adjust=False).mean().iloc[-1] if len(close_prices) >= 9 else None
        ema_21 = close_prices.ewm(span=21, adjust=False).mean().iloc[-1] if len(close_prices) >= 21 else None
        
        # MACD (Moving Average Convergence Divergence) - trend and momentum
        if len(close_prices) >= 26:
            ema_12 = close_prices.ewm(span=12, adjust=False).mean()
            ema_26 = close_prices.ewm(span=26, adjust=False).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_histogram = macd_line - signal_line
            current_macd = float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None
            current_signal = float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else None
            current_histogram = float(macd_histogram.iloc[-1]) if not pd.isna(macd_histogram.iloc[-1]) else None
        else:
            current_macd = current_signal = current_histogram = None
        
        # Bollinger Bands for volatility and potential breakouts
        if len(close_prices) >= 20:
            bb_middle = close_prices.rolling(window=20).mean()
            bb_std = close_prices.rolling(window=20).std()
            bb_upper = bb_middle + (bb_std * 2)
            bb_lower = bb_middle - (bb_std * 2)
            bb_width = ((bb_upper - bb_lower) / bb_middle).iloc[-1] if len(bb_middle) > 0 else None
            bb_position = ((close_prices.iloc[-1] - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])) if len(bb_upper) > 0 else None
        else:
            bb_width = bb_position = None
        
        # Volume analysis for institutional activity
        avg_volume_20 = hist['Volume'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else None
        volume_ratio = (hist['Volume'].iloc[-1] / avg_volume_20) if avg_volume_20 and avg_volume_20 > 0 else None
        
        # Support and Resistance levels
        recent_highs = hist['High'].tail(20) if len(hist) >= 20 else hist['High']
        recent_lows = hist['Low'].tail(20) if len(hist) >= 20 else hist['Low']
        resistance_levels = recent_highs.nlargest(3).tolist() if len(recent_highs) >= 3 else recent_highs.tolist()
        support_levels = recent_lows.nsmallest(3).tolist() if len(recent_lows) >= 3 else recent_lows.tolist()
        
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
            "technical_indicators": {
                "rsi": current_rsi,
                "sma_20": float(sma_20) if sma_20 is not None else None,
                "sma_50": float(sma_50) if sma_50 is not None else None,
                "ema_9": float(ema_9) if ema_9 is not None else None,
                "ema_21": float(ema_21) if ema_21 is not None else None,
                "macd": {
                    "macd_line": current_macd,
                    "signal_line": current_signal,
                    "histogram": current_histogram
                } if current_macd is not None else None,
                "bollinger_bands": {
                    "width": float(bb_width) if bb_width is not None else None,
                    "position": float(bb_position) if bb_position is not None else None  # 0=lower band, 1=upper band
                } if bb_width is not None else None,
                "volume_ratio": float(volume_ratio) if volume_ratio is not None else None
            },
            "support_resistance": {
                "resistance_levels": [float(x) for x in resistance_levels],
                "support_levels": [float(x) for x in support_levels]
            },
            "summary": f"SPY analysis for {target_date}: Pre-market {safe_format_price(pre_market_price)}, "
                      f"Previous close {safe_format_price(prev_close)}, {lookback_days}-day range {safe_format_price(recent_low)}-{safe_format_price(recent_high)}"
        }
        
        return context
    
    def _get_ai_predictions(self, context: Dict, target_date: date) -> List[PricePrediction]:
        """Use GPT-4/5 to generate price predictions."""
        
        system_prompt = """You are an elite quantitative trader and market microstructure expert specializing in SPY intraday price prediction.
Your analysis combines institutional order flow patterns, technical indicators, regime detection, and behavioral finance insights.

Your expertise includes:
1. **Technical Analysis Mastery**: RSI divergences, MACD crossovers, Bollinger Band squeezes, moving average confluences
2. **Market Microstructure**: Opening auction dynamics, VWAP magnetism, MOC imbalances, dark pool activity patterns
3. **Regime Detection**: Trending vs mean-reverting environments, volatility regime shifts, risk-on/risk-off transitions
4. **Intraday Patterns**: Morning gap dynamics, lunch hour behavior, power hour accumulation, end-of-day positioning
5. **Cross-Asset Analysis**: VIX-SPY correlation, futures-cash basis, sector rotation signals, bond-equity dynamics
6. **Behavioral Factors**: Options expiry effects, weekly/monthly patterns, sentiment extremes, positioning squeezes

Analyze the provided data with institutional-grade sophistication:
- Identify the current market regime (trend-following, mean-reverting, volatile)
- Detect any technical pattern completions or breakouts
- Consider support/resistance levels and their likely strength
- Factor in any divergences between price and technical indicators
- Account for volume patterns and potential liquidity events
- Assess the probability of gap fills, trend continuations, or reversals

Provide predictions with:
- predicted_price: Precise price prediction based on your analysis
- confidence: Calibrated confidence (0.0-1.0) reflecting prediction certainty
- reasoning: Concise expert rationale (max 100 chars) highlighting the key driver
- interval_low/high: 68% confidence interval (1-sigma) adjusted for regime volatility

Your predictions should reflect the nuanced understanding of an experienced trader who can synthesize multiple signals into actionable insights."""

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

        # Format technical indicators safely
        tech_indicators = context.get('technical_indicators', {})
        rsi_str = f"{tech_indicators.get('rsi'):.1f}" if tech_indicators.get('rsi') is not None else "N/A"
        sma20_str = f"${tech_indicators.get('sma_20'):.2f}" if tech_indicators.get('sma_20') is not None else "N/A"
        sma50_str = f"${tech_indicators.get('sma_50'):.2f}" if tech_indicators.get('sma_50') is not None else "N/A"
        
        macd_str = "N/A"
        if tech_indicators.get('macd'):
            macd_data = tech_indicators['macd']
            if macd_data.get('macd_line') is not None:
                macd_str = f"MACD: {macd_data['macd_line']:.3f}, Signal: {macd_data['signal_line']:.3f}, Hist: {macd_data['histogram']:.3f}"
        
        bb_str = "N/A"
        if tech_indicators.get('bollinger_bands'):
            bb_data = tech_indicators['bollinger_bands']
            if bb_data.get('position') is not None:
                bb_str = f"Position: {bb_data['position']:.1%}, Width: {bb_data['width']:.3f}"
        
        volume_str = f"{tech_indicators.get('volume_ratio'):.1f}x avg" if tech_indicators.get('volume_ratio') is not None else "N/A"
        
        support_resistance = context.get('support_resistance', {})
        resistance_str = ", ".join([f"${x:.2f}" for x in support_resistance.get('resistance_levels', [])][:3]) or "N/A"
        support_str = ", ".join([f"${x:.2f}" for x in support_resistance.get('support_levels', [])][:3]) or "N/A"
        
        user_prompt = f"""Analyze SPY for {target_date.strftime('%Y-%m-%d')}:

MARKET DATA:
- Pre-market price: {safe_format_price(context.get('pre_market_price'))}
- Previous close: {safe_format_price(context.get('previous_close'))}
- 5-day high/low: {safe_format_price(context.get('recent_high'))}/{safe_format_price(context.get('recent_low'))}
- Annualized volatility: {safe_format_percent(context.get('annualized_volatility'))}
- 14-day ATR: {safe_format_price(context.get('atr_14day'))}
- VIX: {vix_str}
- ES Futures: {es_str}

TECHNICAL INDICATORS:
- RSI (14): {rsi_str}
- SMA (20): {sma20_str}
- SMA (50): {sma50_str}
- {macd_str}
- Bollinger Bands: {bb_str}
- Volume: {volume_str}

KEY LEVELS:
- Resistance: {resistance_str}
- Support: {support_str}

RECENT PRICE HISTORY:
{json.dumps(context.get('recent_prices', []), indent=2)}

CHECKPOINT TIMES (All Eastern Time):
- open: 9:30 AM ET
- noon: 12:00 PM ET
- twoPM: 2:00 PM ET
- close: 4:00 PM ET

Provide predictions in this exact JSON format:
{{
  "analysis": "Your comprehensive expert analysis including: 1) Market regime identification, 2) Key technical patterns observed, 3) Institutional flow insights, 4) Critical levels to watch, 5) Primary risk factors",
  "sentiment": {{
    "direction": "bullish|bearish|neutral",
    "confidence": 0.0,
    "regime": "trending|range-bound|volatile|breakout|reversal",
    "momentum": "accelerating|steady|decelerating|exhausted",
    "factors": ["specific factor 1", "specific factor 2", "specific factor 3"]
  }},
  "key_dynamics": {{
    "opening_bias": "gap_up|gap_down|flat|inside_range",
    "intraday_pattern": "trend_day|range_day|reversal_day|choppy",
    "volume_profile": "accumulation|distribution|neutral|light",
    "risk_events": ["event1", "event2"]
  }},
  "open": {{"predicted_price": 580.50, "confidence": 0.75, "reasoning": "Gap up on overnight futures strength", "interval_low": 579.50, "interval_high": 581.50}},
  "noon": {{"predicted_price": 582.25, "confidence": 0.70, "reasoning": "VWAP magnetism with buying pressure", "interval_low": 580.75, "interval_high": 583.75}},
  "twoPM": {{"predicted_price": 581.80, "confidence": 0.65, "reasoning": "Consolidation near resistance level", "interval_low": 580.00, "interval_high": 583.60}},
  "close": {{"predicted_price": 583.10, "confidence": 0.72, "reasoning": "MOC imbalance buy-side bias", "interval_low": 581.30, "interval_high": 584.90}}
}}"""

        try:
            # Use Chat Completions like your working service, with JSON mode + fallback
            from .config import settings
            model = settings.openai_model
            max_tokens = settings.openai_max_completion_tokens
            reasoning_effort = settings.openai_reasoning_effort

            logger.info(f"Using {model} (chat.completions) for SPY predictions")

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
                logger.debug(f"Token usage - prompt: {getattr(u, 'prompt_tokens', None)}, "
                           f"completion: {getattr(u, 'completion_tokens', None)}, "
                           f"total: {getattr(u, 'total_tokens', None)}")
            except Exception as e:
                logger.debug(f"Could not log token usage: {e}")

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

            # Extract enhanced analysis fields
            analysis = prediction_data.pop("analysis", "No detailed analysis provided")
            sentiment = prediction_data.pop("sentiment", None)
            key_dynamics = prediction_data.pop("key_dynamics", None)
            
            # Store enhanced sentiment with additional fields if provided
            if sentiment and isinstance(sentiment, dict):
                # Merge key_dynamics into sentiment for comprehensive view
                if key_dynamics and isinstance(key_dynamics, dict):
                    sentiment["dynamics"] = key_dynamics
                self.last_sentiment = sentiment
            else:
                self.last_sentiment = None
            
            logger.debug(f"Analysis extracted: {analysis[:100]}..." if len(analysis) > 100 else f"Analysis: {analysis}")
            if sentiment:
                logger.debug(f"Sentiment: {sentiment.get('direction', 'N/A')}, Regime: {sentiment.get('regime', 'N/A')}")

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
            logger.error(f"AI prediction failed: {e}", exc_info=True)
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
            logger.error(f"Baseline fallback also failed: {e}", exc_info=True)
            
            # Ultra-simple fallback - use actual market data or raise error
            base_price = context.get('pre_market_price') or context.get('previous_close')
            if not base_price:
                logger.critical("Cannot generate predictions without base price data")
                raise ValueError("Cannot generate predictions without base price data")
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

