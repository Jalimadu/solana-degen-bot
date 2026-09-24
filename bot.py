import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import (
    TELEGRAM_BOT_TOKEN,
    TRADE_AMOUNT_USD,
    TAKE_PROFIT_MULTIPLE,
    LIVE_TRADING,
)

from scanner.launches import run_scanner
from scanner.watchlist import size as watchlist_size


# ============================================================
# BOT STATE
# ============================================================

bot_enabled = False
scanner_task = None


# ============================================================
# START COMMAND
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🤖 SOLANA DEGEN BOT\n\n"
        "System: ONLINE\n"
        f"Entry: ${TRADE_AMOUNT_USD:.2f}\n"
        f"Target: {TAKE_PROFIT_MULTIPLE:.0f}×\n"
        f"Live trading: {'ON' if LIVE_TRADING else 'OFF'}\n\n"
        "Commands:\n"
        "/status\n"
        "/startbot\n"
        "/stopbot\n"
        "/settings"
    )


# ============================================================
# STATUS
# ============================================================

async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    global bot_enabled
    global scanner_task

    scanner_running = (
        scanner_task is not None
        and not scanner_task.done()
    )

    await update.message.reply_text(
        "📊 BOT STATUS\n\n"
        f"Bot: {'ON' if bot_enabled else 'OFF'}\n"
        f"Entry: ${TRADE_AMOUNT_USD:.2f}\n"
        f"Target: {TAKE_PROFIT_MULTIPLE:.0f}×\n"
        f"Live trading: {'ON' if LIVE_TRADING else 'OFF'}\n"
        f"Scanner: {'ON' if scanner_running else 'OFF'}\n"
        "Paper trading: OFF\n"
        f"Watchlist: {watchlist_size()}"
    )


# ============================================================
# START SCANNER
# ============================================================

async def startbot(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    global bot_enabled
    global scanner_task

    # --------------------------------------------------------
    # CHECK IF ALREADY RUNNING
    # --------------------------------------------------------

    if (
        scanner_task is not None
        and not scanner_task.done()
    ):
        bot_enabled = True

        await update.message.reply_text(
            "🟢 Bot is already running.\n\n"
            "Scanner: ON\n"
            f"Watchlist: {watchlist_size()}\n"
            f"Live trading: "
            f"{'ON' if LIVE_TRADING else 'OFF'}"
        )

        return

    # --------------------------------------------------------
    # ENABLE BOT
    # --------------------------------------------------------

    bot_enabled = True

    # --------------------------------------------------------
    # START SCANNER AS BACKGROUND TASK
    # --------------------------------------------------------

    scanner_task = asyncio.create_task(
        run_scanner()
    )

    await update.message.reply_text(
        "🟢 Bot enabled.\n\n"
        "🔎 Scanner: ON\n"
        "📡 New-token discovery: ON\n"
        "📈 Momentum tracking: ON\n"
        f"🔴 Live trading: "
        f"{'ON' if LIVE_TRADING else 'OFF'}"
    )


# ============================================================
# STOP SCANNER
# ============================================================

async def stopbot(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    global bot_enabled
    global scanner_task

    bot_enabled = False

    # --------------------------------------------------------
    # STOP SCANNER TASK
    # --------------------------------------------------------

    if (
        scanner_task is not None
        and not scanner_task.done()
    ):
        scanner_task.cancel()

        try:
            await scanner_task

        except asyncio.CancelledError:
            pass

    scanner_task = None

    await update.message.reply_text(
        "🔴 Bot disabled.\n\n"
        "Scanner: OFF\n"
        "No new scans will be started.\n"
        "No real trades will be executed."
    )


# ============================================================
# SETTINGS
# ============================================================

async def settings(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "⚙️ SETTINGS\n\n"
        f"Entry amount: ${TRADE_AMOUNT_USD:.2f}\n"
        f"Take profit: {TAKE_PROFIT_MULTIPLE:.0f}×\n"
        f"Live trading: "
        f"{'ON' if LIVE_TRADING else 'OFF'}\n"
        f"Watchlist: {watchlist_size()}"
    )


# ============================================================
# APPLICATION
# ============================================================

def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing."
        )

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    app.add_handler(
        CommandHandler(
            "status",
            status,
        )
    )

    app.add_handler(
        CommandHandler(
            "startbot",
            startbot,
        )
    )

    app.add_handler(
        CommandHandler(
            "stopbot",
            stopbot,
        )
    )

    app.add_handler(
        CommandHandler(
            "settings",
            settings,
        )
    )

    print(
        "🤖 Solana Degen Bot is running..."
    )

    print(
        "🔴 Live trading is disabled."
    )

    try:
        app.run_polling(close_loop=False)
    finally:
        if scanner_task is not None and not scanner_task.done():
            scanner_task.cancel()
            try:
                asyncio.get_event_loop().run_until_complete(scanner_task)
            except asyncio.CancelledError:
                pass


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
