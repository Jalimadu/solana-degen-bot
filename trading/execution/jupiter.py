"""
Jupiter execution client.

This module obtains swap orders from Jupiter.

It does NOT automatically sign or send transactions.
"""

from dataclasses import dataclass

import aiohttp

from trading.execution.config import (
    JUPITER_API_KEY,
    JUPITER_BASE_URL,
)


@dataclass(frozen=True)
class JupiterOrder:
    request_id: str
    raw: dict

    @property
    def transaction(self):
        return self.raw.get("transaction")

    @property
    def input_amount(self):
        return self.raw.get("inAmount")

    @property
    def output_amount(self):
        return self.raw.get("outAmount")

    @property
    def price_impact(self):
        return self.raw.get("priceImpact")


class JupiterError(RuntimeError):
    """Raised when Jupiter rejects or cannot process a request."""


class JupiterClient:

    def __init__(self):
        self.base_url = JUPITER_BASE_URL

    def _headers(self):
        headers = {
            "Accept": "application/json",
        }

        if JUPITER_API_KEY:
            headers["x-api-key"] = JUPITER_API_KEY

        return headers

    async def get_order(
        self,
        input_mint,
        output_mint,
        amount,
        taker,
    ):
        """
        Request a Jupiter order.

        No transaction is signed or submitted here.
        """

        url = (
            f"{self.base_url}/ultra/v1/order"
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
                        f"Jupiter order request failed "
                        f"({response.status}): {body[:500]}"
                    )

                try:
                    data = await response.json()
                except Exception as exc:
                    raise JupiterError(
                        "Jupiter returned invalid JSON."
                    ) from exc

        request_id = data.get(
            "requestId",
            "",
        )

        if not request_id:
            raise JupiterError(
                "Jupiter response did not contain requestId."
            )

        return JupiterOrder(
            request_id=request_id,
            raw=data,
        )
