import os

from dotenv import load_dotenv
from solders.keypair import Keypair

from solana_client import get_sol_balance


load_dotenv()


def get_private_key():
    private_key = os.getenv("SOLANA_PRIVATE_KEY")

    if not private_key:
        raise RuntimeError(
            "SOLANA_PRIVATE_KEY is not configured."
        )

    return private_key.strip()


def get_keypair():
    private_key = get_private_key()

    try:
        return Keypair.from_base58_string(
            private_key
        )
    except Exception as exc:
        raise RuntimeError(
            "SOLANA_PRIVATE_KEY is invalid."
        ) from exc


def get_public_address():
    keypair = get_keypair()

    return str(keypair.pubkey())


async def get_wallet_balance():
    address = get_public_address()

    return await get_sol_balance(address)
