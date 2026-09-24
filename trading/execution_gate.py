"""
Execution Safety Gate

This module is the final authorization boundary before trade execution.

IMPORTANT:
    This module does NOT sign transactions.
    This module does NOT send transactions.
    This module does NOT load private keys.
    This module does NOT execute swaps.

Every future execution path should pass through this gate first.
"""

from dataclasses import dataclass

from trading.safety import (
    SafetyResult,
    validate_trade,
)
from trading.execution.emergency import (
    is_emergency_stop_active,
)


@dataclass(frozen=True)
class ExecutionAuthorization:
    """
    Final authorization result for a potential trade.
    """

    authorized: bool
    safety: SafetyResult


def authorize_trade(
    candidate,
    trade_amount_usd,
    slippage_percent,
    wallet_sol_balance,
    open_positions,
    config=None,
):
    """
    Authorize a trade candidate for the next execution stage.

    This function only validates and authorizes.
    It never executes a transaction.

    A trade is authorized only when every safety check passes.
    """

    safety_result = validate_trade(
        candidate=candidate,
        trade_amount_usd=trade_amount_usd,
        slippage_percent=slippage_percent,
        wallet_sol_balance=wallet_sol_balance,
        open_positions=open_positions,
        config=config,
    )

    if is_emergency_stop_active():
        safety_result = SafetyResult(
            allowed=False,
            reasons=safety_result.reasons + (
                "Emergency stop is active.",
            ),
            warnings=safety_result.warnings,
        )

    return ExecutionAuthorization(
        authorized=safety_result.allowed,
        safety=safety_result,
    )


def require_authorization(
    candidate,
    trade_amount_usd,
    slippage_percent,
    wallet_sol_balance,
    open_positions,
    config=None,
):
    """
    Run the execution safety gate and raise an error if blocked.

    This is intended for future execution code.

    It still does NOT execute a trade.
    """

    authorization = authorize_trade(
        candidate=candidate,
        trade_amount_usd=trade_amount_usd,
        slippage_percent=slippage_percent,
        wallet_sol_balance=wallet_sol_balance,
        open_positions=open_positions,
        config=config,
    )

    if not authorization.authorized:
        reason_text = "; ".join(
            authorization.safety.reasons
        )

        raise PermissionError(
            f"Trade blocked by execution safety gate: "
            f"{reason_text}"
        )

    return authorization
