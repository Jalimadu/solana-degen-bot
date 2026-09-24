"""
Execution configuration.

Live trading remains disabled unless LIVE_TRADING=true is explicitly
configured in the environment.
"""

import os

from dotenv import load_dotenv


load_dotenv()


LIVE_TRADING = (
    os.getenv("LIVE_TRADING", "false")
    .strip()
    .lower()
    == "true"
)

JUPITER_API_KEY = os.getenv(
    "JUPITER_API_KEY",
    "",
).strip()

JUPITER_BASE_URL = os.getenv(
    "JUPITER_BASE_URL",
    "https://api.jup.ag",
).rstrip("/")

SOL_MINT = (
    "So11111111111111111111111111111111111111112"
)

USDC_MINT = (
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
)

# Never allow the execution layer to use more than this percentage
# of the configured trade amount without explicit code changes.
MAX_EXECUTION_MULTIPLIER = 1.0


def execution_status():
    return {
        "live_trading": LIVE_TRADING,
        "jupiter_api_configured": bool(JUPITER_API_KEY),
        "jupiter_base_url": JUPITER_BASE_URL,
        "max_execution_multiplier": MAX_EXECUTION_MULTIPLIER,
    }
