"""
Trade Execution Safety

This module validates whether a trade is allowed to proceed.

IMPORTANT:
    This module does NOT sign transactions.
    This module does NOT send transactions.
    This module does NOT load private keys.
    This module does NOT execute swaps.

It only performs safety checks.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyConfig:
    """
    Hard limits for trade execution.
    """

    max_trade_usd: float = 1.00
    max_slippage_percent: float = 5.0
    min_liquidity_usd: float = 1_000.0
    min_sol_reserve: float = 0.01
    max_open_positions: int = 3


@dataclass(frozen=True)
class SafetyResult:
    """
    Result of a safety validation.
    """

    allowed: bool
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


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

    Returns SafetyResult.

    This function never executes a trade.
    """

    if config is None:
        config = SafetyConfig()

    reasons = []
    warnings = []

    # --------------------------------------------------------
    # Candidate validation
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
    # Wallet SOL reserve
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

    if wallet_sol_balance < config.min_sol_reserve:
        reasons.append(
            f"Wallet SOL balance is below "
            f"the required reserve of "
            f"{config.min_sol_reserve:.4f} SOL."
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

    if (
        open_positions
        >= config.max_open_positions
    ):
        reasons.append(
            f"Maximum open positions "
            f"({config.max_open_positions}) "
            f"has been reached."
        )

    # --------------------------------------------------------
    # Warnings
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
