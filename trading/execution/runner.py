"""
Controlled transaction execution.

This is the only module allowed to submit a Jupiter transaction.

All callers must first pass the execution safety gate.
"""

import base64

from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

from trading.execution.config import LIVE_TRADING
from trading.execution.jupiter import JupiterClient


class ExecutionBlocked(RuntimeError):
    """Raised when live execution is disabled."""


class ExecutionError(RuntimeError):
    """Raised when transaction execution fails."""


def load_trading_keypair(private_key):
    if not private_key:
        raise ExecutionError(
            "SOLANA_PRIVATE_KEY is not configured."
        )

    try:
        return Keypair.from_base58_string(
            private_key
        )
    except Exception as exc:
        raise ExecutionError(
            "SOLANA_PRIVATE_KEY is invalid."
        ) from exc


async def execute_jupiter_order(
    order,
    keypair,
):
    """
    Sign and submit a Jupiter transaction.

    This function refuses to operate unless LIVE_TRADING=true.
    """

    if not LIVE_TRADING:
        raise ExecutionBlocked(
            "Live trading is disabled. "
            "Set LIVE_TRADING=true only after "
            "simulation and safety testing."
        )

    if not order.transaction:
        raise ExecutionError(
            "Jupiter order contains no transaction."
        )

    try:
        raw_transaction = base64.b64decode(
            order.transaction
        )

        transaction = VersionedTransaction.from_bytes(
            raw_transaction
        )

        message = transaction.message

        signed_transaction = VersionedTransaction(
            message,
            [keypair],
        )

        return signed_transaction

    except Exception as exc:
        raise ExecutionError(
            f"Failed to sign Jupiter transaction: {exc}"
        ) from exc
