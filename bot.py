import asyncio
import os

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from config import (
    TELEGRAM_BOT_TOKEN,
    TAKE_PROFIT_MULTIPLE,
    LIVE_TRADING,
)

from scanner.launches import run_scanner
from scanner.watchlist import size as watchlist_size

from trading.settings import (
    HARD_MAX_OPEN_POSITIONS,
    HARD_MAX_SLIPPAGE_PERCENT,
    HARD_MAX_TRADE_USD,
    settings_summary,
    update_setting,
)


# ============================================================
# BOT STATE
# ============================================================

bot_enabled = False
scanner_task = None


# ============================================================
# ADMIN
# ============================================================

def get_admin_id():
    value = os.getenv(
        "TELEGRAM_ADMIN_ID",
        "",
    ).strip()

    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        return None


def is_admin(update: Update):
    admin_id = get_admin_id()

    if admin_id is None:
        return False

    if update.effective_user is None:
        return False

    return update.effective_user.id == admin_id


async def require_admin(update: Update):
    if is_admin(update):
        return True

    await update.message.reply_text(
        "🔒 Admin access required.\n\n"
        "Use /myid to see your Telegram ID.\n"
        "Then configure TELEGRAM_ADMIN_ID."
    )

    return False


# ============================================================
# START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🤖 SOLANA DEGEN BOT\n\n"
        "System: ONLINE\n"
        f"Target: {TAKE_PROFIT_MULTIPLE:.0f}×\n"
        f"Live trading: "
        f"{'ON' if LIVE_TRADING else 'OFF'}\n\n"
        "Commands:\n"
        "/status\n"
        "/startbot\n"
        "/stopbot\n"
        "/settings\n"
        "/myid\n\n"
        "Trading controls:\n"
        "/settrade <USD>\n"
        "/setmaxtrade <USD>\n"
        "/setpositions <number>\n"
        "/setslippage <percent>\n"
        "/setliquidity <USD>\n"
        "/setfeebuffer <SOL>"
    )


# ============================================================
# MY ID
# ============================================================

async def myid(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_user is None:
        return

    await update.message.reply_text(
        "🆔 Your Telegram ID:\n\n"
        f"{update.effective_user.id}"
    )


# ============================================================
# STATUS
# ============================================================

async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    scanner_running = (
        scanner_task is not None
        and not scanner_task.done()
    )

    await update.message.reply_text(
        "📊 BOT STATUS\n\n"
        f"Bot: {'ON' if bot_enabled else 'OFF'}\n"
        f"Live trading: "
        f"{'ON' if LIVE_TRADING else 'OFF'}\n"
        f"Scanner: {'ON' if scanner_running else 'OFF'}\n"
        "Paper trading: OFF\n"
        f"Watchlist: {watchlist_size()}\n\n"
        "⚙️ TRADING SETTINGS\n"
        f"{settings_summary()}"
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

    bot_enabled = True

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

def settings_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔄 Refresh",
                    callback_data="settings_refresh",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📖 Commands",
                    callback_data="settings_help",
                ),
            ],
        ]
    )


async def settings(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "⚙️ TRADING SETTINGS\n\n"
        f"{settings_summary()}\n\n"
        "Change values with:\n\n"
        "/settrade 0.10\n"
        "/setmaxtrade 0.10\n"
        "/setpositions 3\n"
        "/setslippage 5\n"
        "/setliquidity 1000\n"
        "/setfeebuffer 0.0001\n\n"
        f"Hard maximum trade: "
        f"${HARD_MAX_TRADE_USD:.2f}\n"
        f"Hard maximum positions: "
        f"{HARD_MAX_OPEN_POSITIONS}\n"
        f"Hard maximum slippage: "
        f"{HARD_MAX_SLIPPAGE_PERCENT:.1f}%\n\n"
        f"Live trading: "
        f"{'ON' if LIVE_TRADING else 'OFF'}",
        reply_markup=settings_keyboard(),
    )


async def settings_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    await query.answer()

    if query.data == "settings_refresh":
        await query.edit_message_text(
            "⚙️ TRADING SETTINGS\n\n"
            f"{settings_summary()}\n\n"
            f"Live trading: "
            f"{'ON' if LIVE_TRADING else 'OFF'}",
            reply_markup=settings_keyboard(),
        )

    elif query.data == "settings_help":
        await query.edit_message_text(
            "📖 TRADING CONTROL COMMANDS\n\n"
            "/settrade 0.10\n"
            "Changes the actual trade amount.\n\n"
            "/setmaxtrade 0.10\n"
            "Changes the maximum allowed trade.\n\n"
            "/setpositions 3\n"
            "Changes maximum simultaneous positions.\n\n"
            "/setslippage 5\n"
            "Changes maximum slippage.\n\n"
            "/setliquidity 1000\n"
            "Changes minimum liquidity.\n\n"
            "/setfeebuffer 0.0001\n"
            "Changes SOL fee buffer.\n\n"
            "All setting changes are admin-only."
        )


# ============================================================
# SETTING HELPER
# ============================================================

async def change_setting(
    update: Update,
    setting_name,
    label,
):
    if not await require_admin(update):
        return

    if not update.message:
        return

    if len(update.message.text.split()) != 2:
        await update.message.reply_text(
            f"Usage:\n"
            f"/{label[0]} <value>"
        )
        return

    value = update.message.text.split()[1]

    try:
        settings = update_setting(
            setting_name,
            value,
        )

    except (
        ValueError,
        TypeError,
    ) as exc:
        await update.message.reply_text(
            f"❌ Setting rejected.\n\n{exc}"
        )
        return

    await update.message.reply_text(
        "✅ Setting updated.\n\n"
        f"{settings_summary()}"
    )


# ============================================================
# SET TRADE AMOUNT
# ============================================================

async def settrade(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await change_setting(
        update,
        "trade_amount_usd",
        "settrade",
    )


# ============================================================
# SET MAX TRADE
# ============================================================

async def setmaxtrade(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await change_setting(
        update,
        "max_trade_usd",
        "setmaxtrade",
    )


# ============================================================
# SET POSITIONS
# ============================================================

async def setpositions(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await change_setting(
        update,
        "max_open_positions",
        "setpositions",
    )


# ============================================================
# SET SLIPPAGE
# ============================================================

async def setslippage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await change_setting(
        update,
        "max_slippage_percent",
        "setslippage",
    )


# ============================================================
# SET LIQUIDITY
# ============================================================

async def setliquidity(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await change_setting(
        update,
        "min_liquidity_usd",
        "setliquidity",
    )


# ============================================================
# SET SOL FEE BUFFER
# ============================================================

async def setfeebuffer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await change_setting(
        update,
        "sol_fee_buffer",
        "setfeebuffer",
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

    app.add_handler(
        CommandHandler(
            "myid",
            myid,
        )
    )

    app.add_handler(
        CommandHandler(
            "settrade",
            settrade,
        )
    )

    app.add_handler(
        CommandHandler(
            "setmaxtrade",
            setmaxtrade,
        )
    )

    app.add_handler(
        CommandHandler(
            "setpositions",
            setpositions,
        )
    )

    app.add_handler(
        CommandHandler(
            "setslippage",
            setslippage,
        )
    )

    app.add_handler(
        CommandHandler(
            "setliquidity",
            setliquidity,
        )
    )

    app.add_handler(
        CommandHandler(
            "setfeebuffer",
            setfeebuffer,
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            settings_callback,
        )
    )

    print(
        "🤖 Solana Degen Bot is running..."
    )

    print(
        "🔴 Live trading is disabled."
    )

    try:
        app.run_polling(
            close_loop=False
        )

    finally:
        if (
            scanner_task is not None
            and not scanner_task.done()
        ):
            scanner_task.cancel()

            try:
                asyncio.get_event_loop().run_until_complete(
                    scanner_task
                )

            except asyncio.CancelledError:
                pass


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
