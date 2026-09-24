"""
Trade Execution Safety

This module validates whether a trade is allowed to proceed.

IMPORTANT:
    This module does NOT sign transactions.
    This module does NOT send transactions.
    This module does NOT load private keys.
    This module does NOT execute swaps.
"""

from dataclasses import dataclass

from trading.settings import load_settings


@dataclass(frozen=True)
class SafetyConfig:
    """
    Runtime safety limits.
    """

    max_trade_usd: float
    max_slippage_percent: float
    min_liquidity_usd: float
    sol_fee_buffer: float
    max_open_positions: int


@dataclass(frozen=True)
class SafetyResult:
    """
    Result of a safety validation.
    """

    allowed: bool
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


def get_safety_config():
    """
    Build safety configuration from persistent settings.
    """

    settings = load_settings()

    return SafetyConfig(
        max_trade_usd=settings.max_trade_usd,
        max_slippage_percent=settings.max_slippage_percent,
        min_liquidity_usd=settings.min_liquidity_usd,
        sol_fee_buffer=settings.sol_fee_buffer,
        max_open_positions=settings.max_open_positions,
    )


def validate_trade(
    candidate,
    trade_amount_usd,
    slippage_percent,
    wallet_sol_balance,
    open_positions,
    config=None,
):
    """
    Validate a trade candidate against execution safety limits.

    This function never executes a trade.
    """

    if config is None:
        config = get_safety_config()

    reasons = []
    warnings = []

    # --------------------------------------------------------
    # Candidate
    # --------------------------------------------------------

    if not candidate.is_trade_candidate:
        reasons.append(
            "Candidate signal is not executable."
        )

    # --------------------------------------------------------
    # Trade amount
    # --------------------------------------------------------

    try:
        trade_amount_usd = float(
            trade_amount_usd
        )
    except (TypeError, ValueError):
        reasons.append(
            "Trade amount is invalid."
        )
        trade_amount_usd = 0

    if trade_amount_usd <= 0:
        reasons.append(
            "Trade amount must be greater than zero."
        )

    if trade_amount_usd > config.max_trade_usd:
        reasons.append(
            f"Trade amount exceeds maximum "
            f"of ${config.max_trade_usd:.2f}."
        )

    # --------------------------------------------------------
    # Slippage
    # --------------------------------------------------------

    try:
        slippage_percent = float(
            slippage_percent
        )
    except (TypeError, ValueError):
        reasons.append(
            "Slippage value is invalid."
        )
        slippage_percent = 0

    if slippage_percent < 0:
        reasons.append(
            "Slippage cannot be negative."
        )

    if slippage_percent > config.max_slippage_percent:
        reasons.append(
            f"Slippage exceeds maximum "
            f"of {config.max_slippage_percent:.2f}%."
        )

    # --------------------------------------------------------
    # Liquidity
    # --------------------------------------------------------

    if (
        candidate.liquidity_usd
        < config.min_liquidity_usd
    ):
        reasons.append(
            f"Liquidity is below minimum "
            f"of ${config.min_liquidity_usd:.2f}."
        )

    # --------------------------------------------------------
    # SOL fee buffer
    # --------------------------------------------------------

    try:
        wallet_sol_balance = float(
            wallet_sol_balance
        )
    except (TypeError, ValueError):
        reasons.append(
            "Wallet SOL balance is invalid."
        )
        wallet_sol_balance = 0

    if wallet_sol_balance < config.sol_fee_buffer:
        reasons.append(
            f"Wallet SOL balance is below "
            f"the configured SOL fee buffer "
            f"of {config.sol_fee_buffer:.6f} SOL."
        )

    # --------------------------------------------------------
    # Open positions
    # --------------------------------------------------------

    try:
        open_positions = int(
            open_positions
        )
    except (TypeError, ValueError):
        reasons.append(
            "Open position count is invalid."
        )
        open_positions = 0

    if open_positions < 0:
        reasons.append(
            "Open position count cannot be negative."
        )

    if open_positions >= config.max_open_positions:
        reasons.append(
            f"Maximum open positions "
            f"({config.max_open_positions}) "
            f"has been reached."
        )

    # --------------------------------------------------------
    # Candidate warnings
    # --------------------------------------------------------

    if candidate.warnings:
        warnings.extend(
            candidate.warnings
        )

    # --------------------------------------------------------
    # Final decision
    # --------------------------------------------------------

    allowed = len(reasons) == 0

    return SafetyResult(
        allowed=allowed,
        reasons=tuple(reasons),
        warnings=tuple(warnings),
    )
