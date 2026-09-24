"""
Controlled Jupiter Swap V2 execution.

This module is the only component allowed to sign/execute swaps.

LIVE_TRADING must explicitly be true before execution.
"""

import base64
import os

from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

from trading.execution.config import (
    LIVE_TRADING,
)
from trading.execution.jupiter import (
    JupiterClient,
    JupiterOrder,
)
from trading.execution.result import (
    ExecutionResult,
)


class ExecutionBlocked(RuntimeError):
    pass


class ExecutionError(RuntimeError):
    pass


def load_trading_keypair(private_key=None):
    """
    Load the trading key only when explicitly requested.
    """

    if private_key is None:
        private_key = os.getenv(
            "SOLANA_PRIVATE_KEY",
            "",
        ).strip()

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


def sign_order(
    order: JupiterOrder,
    keypair,
):
    """
    Sign the Jupiter v0 transaction locally.

    Nothing is sent to the network.
    """

    if not order.transaction:
        raise ExecutionError(
            "Jupiter order has no transaction."
        )

    try:
        raw = base64.b64decode(
            order.transaction
        )

        transaction = (
            VersionedTransaction.from_bytes(raw)
        )

        transaction.sign([keypair])

        return base64.b64encode(
            bytes(transaction)
        ).decode("ascii")

    except Exception as exc:
        raise ExecutionError(
            f"Transaction signing failed: {exc}"
        ) from exc


async def execute_order(
    order: JupiterOrder,
    keypair=None,
):
    """
    Sign and execute a Jupiter order.

    This function is locked unless LIVE_TRADING=true.
    """

    if not LIVE_TRADING:
        raise ExecutionBlocked(
            "LIVE_TRADING=false. "
            "Transaction execution is disabled."
        )

    if keypair is None:
        keypair = load_trading_keypair()

    signed_transaction = sign_order(
        order,
        keypair,
    )

    client = JupiterClient()

    result = await client.execute(
        signed_transaction_base64=
            signed_transaction,
        request_id=order.request_id,
    )

    status = result.get(
        "status",
        "Failed",
    )

    signature = result.get(
        "signature",
        "",
    )

    if status != "Success":
        raise ExecutionError(
            "Jupiter execution failed: "
            f"{result}"
        )

    return ExecutionResult(
        success=True,
        signature=signature,
        input_amount=int(
            result.get(
                "totalInputAmount",
                order.input_amount,
            )
        ),
        output_amount=int(
            result.get(
                "totalOutputAmount",
                order.output_amount,
            )
        ),
        message="Swap confirmed by Jupiter.",
    )
