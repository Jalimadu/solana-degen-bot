"""
Jupiter Swap V2 client.

Quote/order retrieval is separated from signing and execution.
"""

from dataclasses import dataclass

import aiohttp

from trading.execution.config import (
    JUPITER_API_KEY,
    JUPITER_BASE_URL,
)


class JupiterError(RuntimeError):
    pass


@dataclass(frozen=True)
class JupiterOrder:
    request_id: str
    transaction: str | None
    input_mint: str
    output_mint: str
    input_amount: int
    output_amount: int
    router: str
    mode: str
    fee_bps: int
    fee_mint: str
    raw: dict


class JupiterClient:

    def __init__(self):
        self.base_url = JUPITER_BASE_URL

    def _headers(self):
        if not JUPITER_API_KEY:
            raise JupiterError(
                "JUPITER_API_KEY is not configured."
            )

        return {
            "Accept": "application/json",
            "x-api-key": JUPITER_API_KEY,
        }

    async def get_order(
        self,
        input_mint,
        output_mint,
        amount,
        taker,
    ):
        """
        Get a Jupiter Swap V2 order.

        This does not sign or execute anything.
        """

        if int(amount) <= 0:
            raise JupiterError(
                "Order amount must be greater than zero."
            )

        if not taker:
            raise JupiterError(
                "Taker wallet address is required."
            )

        url = (
            f"{self.base_url}/swap/v2/order"
        )

        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(int(amount)),
            "taker": taker,
        }

        timeout = aiohttp.ClientTimeout(
            total=15
        )

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(
                url,
                params=params,
                headers=self._headers(),
            ) as response:

                body = await response.text()

                if response.status != 200:
                    raise JupiterError(
                        f"Jupiter order failed "
                        f"({response.status}): "
                        f"{body[:500]}"
                    )

                try:
                    data = await response.json()
                except Exception as exc:
                    raise JupiterError(
                        "Jupiter returned invalid JSON."
                    ) from exc

        request_id = data.get("requestId", "")

        if not request_id:
            raise JupiterError(
                "Jupiter response has no requestId."
            )

        transaction = data.get("transaction")

        # An empty transaction means Jupiter could quote
        # the trade but could not construct an executable swap.
        if transaction == "":
            raise JupiterError(
                "Jupiter returned no executable transaction: "
                f"{data.get('errorCode')} "
                f"{data.get('errorMessage', '')}"
            )

        return JupiterOrder(
            request_id=request_id,
            transaction=transaction,
            input_mint=data.get(
                "inputMint",
                input_mint,
            ),
            output_mint=data.get(
                "outputMint",
                output_mint,
            ),
            input_amount=int(
                data.get("inAmount", amount)
            ),
            output_amount=int(
                data.get("outAmount", 0)
            ),
            router=data.get(
                "router",
                "",
            ),
            mode=data.get(
                "mode",
                "",
            ),
            fee_bps=int(
                data.get("feeBps", 0)
            ),
            fee_mint=data.get(
                "feeMint",
                "",
            ),
            raw=data,
        )

    async def execute(
        self,
        signed_transaction_base64,
        request_id,
    ):
        """
        Submit a signed transaction to Jupiter.

        The caller must explicitly enable live trading.
        """

        if not signed_transaction_base64:
            raise JupiterError(
                "Signed transaction is empty."
            )

        if not request_id:
            raise JupiterError(
                "requestId is required."
            )

        url = (
            f"{self.base_url}/swap/v2/execute"
        )

        payload = {
            "signedTransaction":
                signed_transaction_base64,
            "requestId": request_id,
        }

        timeout = aiohttp.ClientTimeout(
            total=30
        )

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.post(
                url,
                json=payload,
                headers={
                    **self._headers(),
                    "Content-Type":
                        "application/json",
                },
            ) as response:

                body = await response.text()

                if response.status != 200:
                    raise JupiterError(
                        f"Jupiter execute failed "
                        f"({response.status}): "
                        f"{body[:500]}"
                    )

                try:
                    return await response.json()
                except Exception as exc:
                    raise JupiterError(
                        "Jupiter returned invalid "
                        "execution JSON."
                    ) from exc
