"""
Live trading preflight checks.

This module performs checks that must pass before live execution.

It does NOT sign or submit transactions.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PreflightResult:
    ready: bool
    reasons: tuple[str, ...]


def validate_live_preflight(
    live_trading,
    wallet_sol_balance,
    required_sol,
):
    """
    Validate whether the wallet is capable of proceeding.

    `required_sol` must come from the actual transaction/fee
    calculation rather than a hard-coded wallet reserve.
    """

    reasons = []

    if not live_trading:
        reasons.append(
            "LIVE_TRADING is disabled."
        )

    try:
        wallet_sol_balance = float(
            wallet_sol_balance
        )
    except (TypeError, ValueError):
        reasons.append(
            "Wallet SOL balance is invalid."
        )
        wallet_sol_balance = 0.0

    try:
        required_sol = float(
            required_sol
        )
    except (TypeError, ValueError):
        reasons.append(
            "Required SOL amount is invalid."
        )
        required_sol = float("inf")

    if wallet_sol_balance < required_sol:
        reasons.append(
            "Wallet does not have enough SOL for "
            "the required transaction cost."
        )

    return PreflightResult(
        ready=len(reasons) == 0,
        reasons=tuple(reasons),
    )
