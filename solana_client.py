from solana.rpc.async_api import AsyncClient

from config import SOLANA_RPC_URL


async def get_client():
    return AsyncClient(SOLANA_RPC_URL)


async def get_sol_balance(wallet_address):
    client = await get_client()

    try:
        from solders.pubkey import Pubkey

        public_key = Pubkey.from_string(wallet_address)

        response = await client.get_balance(
            public_key
        )

        return response.value / 1_000_000_000

    finally:
        await client.close()