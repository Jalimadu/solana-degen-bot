import asyncio
import os
import sys

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from solana_client import get_sol_balance


async def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python tools/check_wallet.py "
            "<SOLANA_PUBLIC_ADDRESS>"
        )
        return

    address = sys.argv[1].strip()

    if not address:
        print("Wallet address cannot be empty.")
        return

    try:
        balance = await get_sol_balance(address)

        print("Wallet:", address)
        print(f"SOL balance: {balance:.9f} SOL")

    except Exception as exc:
        print("Wallet check failed:", exc)


if __name__ == "__main__":
    asyncio.run(main())
