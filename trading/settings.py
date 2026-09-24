"""
Persistent Trading Settings

Stores user-configurable trading settings locally.

IMPORTANT:
    This module never loads or stores private keys.
    LIVE_TRADING remains controlled by the existing .env setting.
"""

import json
import os
import tempfile
from dataclasses import asdict, dataclass


SETTINGS_FILE = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    ".trading_settings.json",
)


# ============================================================
# HARD SAFETY CEILINGS
# ============================================================

HARD_MAX_TRADE_USD = 0.60
HARD_MAX_SLIPPAGE_PERCENT = 10.0
HARD_MAX_OPEN_POSITIONS = 10

MIN_ALLOWED_TRADE_USD = 0.01
MIN_ALLOWED_SLIPPAGE_PERCENT = 0.1
MIN_ALLOWED_OPEN_POSITIONS = 1
MIN_ALLOWED_LIQUIDITY_USD = 100.0

# No fixed 0.01 SOL reserve.
# This is only a configurable fee/safety buffer.
DEFAULT_SOL_FEE_BUFFER = 0.0001


@dataclass
class TradingSettings:
    """
    Runtime trading settings.
    """

    trade_amount_usd: float = 0.10
    max_trade_usd: float = 0.10
    max_open_positions: int = 3
    max_slippage_percent: float = 5.0
    min_liquidity_usd: float = 1000.0
    sol_fee_buffer: float = DEFAULT_SOL_FEE_BUFFER


def _default_settings():
    return TradingSettings()


def load_settings():
    """
    Load persistent settings.

    If the settings file does not exist or is invalid,
    return safe defaults.
    """

    defaults = _default_settings()

    if not os.path.exists(SETTINGS_FILE):
        return defaults

    try:
        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return TradingSettings(
            trade_amount_usd=float(
                data.get(
                    "trade_amount_usd",
                    defaults.trade_amount_usd,
                )
            ),
            max_trade_usd=float(
                data.get(
                    "max_trade_usd",
                    defaults.max_trade_usd,
                )
            ),
            max_open_positions=int(
                data.get(
                    "max_open_positions",
                    defaults.max_open_positions,
                )
            ),
            max_slippage_percent=float(
                data.get(
                    "max_slippage_percent",
                    defaults.max_slippage_percent,
                )
            ),
            min_liquidity_usd=float(
                data.get(
                    "min_liquidity_usd",
                    defaults.min_liquidity_usd,
                )
            ),
            sol_fee_buffer=float(
                data.get(
                    "sol_fee_buffer",
                    defaults.sol_fee_buffer,
                )
            ),
        )

    except (
        OSError,
        ValueError,
        TypeError,
        json.JSONDecodeError,
    ):
        return defaults


def save_settings(settings):
    """
    Atomically save settings to disk.
    """

    directory = os.path.dirname(
        SETTINGS_FILE
    )

    os.makedirs(
        directory,
        exist_ok=True,
    )

    fd, temporary_file = tempfile.mkstemp(
        prefix=".trading_settings.",
        suffix=".tmp",
        dir=directory,
        text=True,
    )

    try:
        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                asdict(settings),
                file,
                indent=2,
            )
            file.write("\n")

        os.replace(
            temporary_file,
            SETTINGS_FILE,
        )

    finally:
        if os.path.exists(temporary_file):
            os.remove(temporary_file)


def validate_settings(settings):
    """
    Validate settings against hard safety boundaries.

    Raises ValueError when a setting is unsafe.
    """

    if not (
        MIN_ALLOWED_TRADE_USD
        <= settings.trade_amount_usd
        <= HARD_MAX_TRADE_USD
    ):
        raise ValueError(
            f"Trade amount must be between "
            f"${MIN_ALLOWED_TRADE_USD:.2f} and "
            f"${HARD_MAX_TRADE_USD:.2f}."
        )

    if not (
        MIN_ALLOWED_TRADE_USD
        <= settings.max_trade_usd
        <= HARD_MAX_TRADE_USD
    ):
        raise ValueError(
            f"Maximum trade must be between "
            f"${MIN_ALLOWED_TRADE_USD:.2f} and "
            f"${HARD_MAX_TRADE_USD:.2f}."
        )

    if settings.trade_amount_usd > settings.max_trade_usd:
        raise ValueError(
            "Trade amount cannot exceed maximum trade."
        )

    if not (
        MIN_ALLOWED_OPEN_POSITIONS
        <= settings.max_open_positions
        <= HARD_MAX_OPEN_POSITIONS
    ):
        raise ValueError(
            f"Maximum positions must be between "
            f"{MIN_ALLOWED_OPEN_POSITIONS} and "
            f"{HARD_MAX_OPEN_POSITIONS}."
        )

    if not (
        MIN_ALLOWED_SLIPPAGE_PERCENT
        <= settings.max_slippage_percent
        <= HARD_MAX_SLIPPAGE_PERCENT
    ):
        raise ValueError(
            f"Maximum slippage must be between "
            f"{MIN_ALLOWED_SLIPPAGE_PERCENT:.1f}% and "
            f"{HARD_MAX_SLIPPAGE_PERCENT:.1f}%."
        )

    if settings.min_liquidity_usd < MIN_ALLOWED_LIQUIDITY_USD:
        raise ValueError(
            f"Minimum liquidity cannot be below "
            f"${MIN_ALLOWED_LIQUIDITY_USD:.2f}."
        )

    if settings.sol_fee_buffer < 0:
        raise ValueError(
            "SOL fee buffer cannot be negative."
        )


def update_setting(name, value):
    """
    Update one setting safely and persist it.
    """

    settings = load_settings()

    if name == "trade_amount_usd":
        settings.trade_amount_usd = float(value)

    elif name == "max_trade_usd":
        settings.max_trade_usd = float(value)

    elif name == "max_open_positions":
        settings.max_open_positions = int(value)

    elif name == "max_slippage_percent":
        settings.max_slippage_percent = float(value)

    elif name == "min_liquidity_usd":
        settings.min_liquidity_usd = float(value)

    elif name == "sol_fee_buffer":
        settings.sol_fee_buffer = float(value)

    else:
        raise ValueError(
            f"Unknown setting: {name}"
        )

    validate_settings(settings)
    save_settings(settings)

    return settings


def settings_summary():
    settings = load_settings()

    return (
        f"💵 Trade amount: "
        f"${settings.trade_amount_usd:.2f}\n"
        f"🛑 Max trade: "
        f"${settings.max_trade_usd:.2f}\n"
        f"📊 Max positions: "
        f"{settings.max_open_positions}\n"
        f"📉 Max slippage: "
        f"{settings.max_slippage_percent:.1f}%\n"
        f"💧 Min liquidity: "
        f"${settings.min_liquidity_usd:.2f}\n"
        f"⛽ SOL fee buffer: "
        f"{settings.sol_fee_buffer:.6f} SOL"
    )
