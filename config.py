import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

SOLANA_RPC_URL = os.getenv(
    "SOLANA_RPC_URL",
    "https://api.mainnet-beta.solana.com",
)

TRADE_AMOUNT_USD = float(
    os.getenv("TRADE_AMOUNT_USD", "0.10")
)

TAKE_PROFIT_MULTIPLE = float(
    os.getenv("TAKE_PROFIT_MULTIPLE", "10")
)

LIVE_TRADING = (
    os.getenv("LIVE_TRADING", "false").lower()
    == "true"
)

BOT_ENABLED = False