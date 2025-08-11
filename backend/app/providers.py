from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

import yfinance as yf


class PriceProvider(ABC):
    @abstractmethod
    def get_price(self, symbol: str) -> Optional[float]:
        raise NotImplementedError


class YFinanceProvider(PriceProvider):
    def get_price(self, symbol: str) -> Optional[float]:
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.fast_info.last_price
            if price is None:
                hist = ticker.history(period="1d", interval="1m")
                if hist is not None and len(hist) > 0:
                    price = float(hist["Close"].iloc[-1])
            return float(price) if price is not None else None
        except Exception:
            return None


default_provider = YFinanceProvider()


