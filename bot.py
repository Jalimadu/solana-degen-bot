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

bot_enabled = False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 BOT STATUS\n\n"
        f"Bot: {'ON' if bot_enabled else 'OFF'}\n"
        f"Entry: ${TRADE_AMOUNT_USD:.2f}\n"
        f"Target: {TAKE_PROFIT_MULTIPLE:.0f}×\n"
        f"Live trading: {'ON' if LIVE_TRADING else 'OFF'}\n"
        "Scanner: OFF\n"
        "Paper trading: OFF"
    )


async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_enabled

    bot_enabled = True

    await update.message.reply_text(
        "🟢 Bot enabled.\n\n"
        "The trading engine is not active yet.\n"
        "No real trades will be executed."
    )


async def stopbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_enabled

    bot_enabled = False

    await update.message.reply_text(
        "🔴 Bot disabled.\n"
        "No new trades will be opened."
    )


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚙️ SETTINGS\n\n"
        f"Entry amount: ${TRADE_AMOUNT_USD:.2f}\n"
        f"Take profit: {TAKE_PROFIT_MULTIPLE:.0f}×\n"
        f"Live trading: {'ON' if LIVE_TRADING else 'OFF'}"
    )


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
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("status", status)
    )

    app.add_handler(
        CommandHandler("startbot", startbot)
    )

    app.add_handler(
        CommandHandler("stopbot", stopbot)
    )

    app.add_handler(
        CommandHandler("settings", settings)
    )

    print("🤖 Solana Degen Bot is running...")
    print("🔴 Live trading is disabled.")

    app.run_polling()


if __name__ == "__main__":
    main()