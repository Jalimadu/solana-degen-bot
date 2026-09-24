"""
Trading Configuration

Centralized safety limits for the trading system.

IMPORTANT:
    LIVE_TRADING defaults to False.
    No module should bypass these settings.
"""

import os

from dotenv import load_dotenv


load_dotenv()


LIVE_TRADING = (
    os.getenv(
        "LIVE_TRADING",
        "false",
    ).strip().lower()
    == "true"
)


MAX_TRADE_USD = float(
    os.getenv(
        "MAX_TRADE_USD",
        "1.00",
    )
)


MAX_SLIPPAGE_PERCENT = float(
    os.getenv(
        "MAX_SLIPPAGE_PERCENT",
        "5.0",
    )
)


MIN_LIQUIDITY_USD = float(
    os.getenv(
        "MIN_LIQUIDITY_USD",
        "1000.0",
    )
)


MIN_SOL_RESERVE = float(
    os.getenv(
        "MIN_SOL_RESERVE",
        "0.01",
    )
)


MAX_OPEN_POSITIONS = int(
    os.getenv(
        "MAX_OPEN_POSITIONS",
        "3",
    )
)


def trading_status():
    """
    Return a safe summary of trading configuration.

    Never exposes private keys or secrets.
    """

    return {
        "live_trading": LIVE_TRADING,
        "max_trade_usd": MAX_TRADE_USD,
        "max_slippage_percent": MAX_SLIPPAGE_PERCENT,
        "min_liquidity_usd": MIN_LIQUIDITY_USD,
        "min_sol_reserve": MIN_SOL_RESERVE,
        "max_open_positions": MAX_OPEN_POSITIONS,
    }
