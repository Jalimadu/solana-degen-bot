"""
Trade Candidate

This module converts a scanner signal into a structured
trade candidate.

IMPORTANT:
    This module does NOT place trades.
    It does NOT load private keys.
    It does NOT sign transactions.
    It does NOT send transactions.
"""

from dataclasses import dataclass
from typing import Optional


ALLOWED_SIGNALS = {
    "SETUP",
    "STRONG SETUP",
}


@dataclass(frozen=True)
class TradeCandidate:
    """
    Immutable candidate produced by the scanner.

    This is an execution input, not an order.
    """

    token_address: str
    symbol: str
    name: str

    signal: str
    confidence: int

    liquidity_usd: float
    volume_5m_usd: float
    buy_pressure: Optional[float]

    reasons: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def is_trade_candidate(self) -> bool:
        """
        Return True only for executable signal classes.
        """

        return self.signal in ALLOWED_SIGNALS


def build_trade_candidate(
    token_address,
    overview,
    signal_data,
):
    """
    Convert scanner output into a TradeCandidate.

    Raises ValueError if the data is unsafe or incomplete.
    """

    address = str(
        token_address or ""
    ).strip()

    if not address:
        raise ValueError(
            "Trade candidate requires a token address."
        )

    signal = str(
        signal_data.get("signal", "")
    ).strip()

    if signal not in ALLOWED_SIGNALS:
        raise ValueError(
            f"Signal is not executable: {signal or 'missing'}"
        )

    confidence = int(
        signal_data.get("confidence", 0)
    )

    if confidence < 0 or confidence > 100:
        raise ValueError(
            "Signal confidence must be between 0 and 100."
        )

    liquidity = float(
        overview.get("liquidity", 0) or 0
    )

    volume_5m = float(
        overview.get("v5mUSD", 0) or 0
    )

    if liquidity < 0:
        raise ValueError(
            "Liquidity cannot be negative."
        )

    if volume_5m < 0:
        raise ValueError(
            "5m volume cannot be negative."
        )

    pressure = signal_data.get(
        "buy_pressure"
    )

    if pressure is not None:
        pressure = float(pressure)

        if pressure < 0 or pressure > 100:
            raise ValueError(
                "Buy pressure must be between 0 and 100."
            )

    reasons = tuple(
        str(item)
        for item in signal_data.get(
            "reasons",
            []
        )
    )

    warnings = tuple(
        str(item)
        for item in signal_data.get(
            "warnings",
            []
        )
    )

    return TradeCandidate(
        token_address=address,
        symbol=str(
            overview.get("symbol", "UNKNOWN")
        ),
        name=str(
            overview.get("name", "Unknown")
        ),
        signal=signal,
        confidence=confidence,
        liquidity_usd=liquidity,
        volume_5m_usd=volume_5m,
        buy_pressure=pressure,
        reasons=reasons,
        warnings=warnings,
    )
