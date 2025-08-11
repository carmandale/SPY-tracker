from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Suggestion:
    tenor: str  # 0DTE, 1W, 1M
    strategy: str  # IC/IB
    short_delta: float
    long_delta: float
    min_credit: float
    rationale: str


def generate_suggestions(iv_rank: Optional[float] = None) -> List[Suggestion]:
    # Simple static rules MVP
    suggestions: List[Suggestion] = []

    suggestions.append(
        Suggestion(
            tenor="0DTE",
            strategy="Iron Condor",
            short_delta=0.12,
            long_delta=0.05,
            min_credit=0.2,
            rationale="Target ±10–15Δ, take >=$0.20 credit",
        )
    )
    suggestions.append(
        Suggestion(
            tenor="1W",
            strategy="Iron Condor",
            short_delta=0.18,
            long_delta=0.10,
            min_credit=0.5,
            rationale="Target ±15–20Δ, take >=$0.50 credit",
        )
    )
    suggestions.append(
        Suggestion(
            tenor="1M",
            strategy="Iron Condor",
            short_delta=0.22,
            long_delta=0.12,
            min_credit=1.2,
            rationale="Target ±20Δ, take >=$1.20 credit",
        )
    )
    return suggestions


