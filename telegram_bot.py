"""
telegram_bot.py
================
Portfolio Example — "Develop a Custom Telegram or Discord Bot in Python"
By: juitindev @ GitHub | Fiverr

Scenario:
    A client wants a Telegram bot for their small online store that:
    - Lets customers check order status by order ID
    - Shows today's deals
    - Handles unknown messages gracefully
    - Logs all interactions

Setup:
    pip install python-telegram-bot
    Set BOT_TOKEN in .env or replace directly below
"""

import logging
import os
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# ── Config ─────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Mock database
ORDERS = {
    "ORD001": {"status": "Shipped",    "item": "Wireless Mouse",    "eta": "Mar 24"},
    "ORD002": {"status": "Processing", "item": "Mechanical Keyboard","eta": "Mar 26"},
    "ORD003": {"status": "Delivered",  "item": "USB-C Hub",         "eta": "Delivered"},
}

DEALS = [
    ("Wireless Mouse",     "$29.99", "30% OFF"),
    ("USB-C Hub",          "$19.99", "20% OFF"),
    ("Laptop Stand",       "$24.99", "15% OFF"),
]

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ── Handlers ───────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Hi {name}! Welcome to TechStore Bot.\n\n"
        "Here's what I can do:\n"
        "📦 /order <ID>  — Check your order status\n"
        "🔥 /deals       — Today's best deals\n"
        "ℹ️ /help        — Show this menu"
    )
    logger.info(f"User {update.effective_user.id} started the bot")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Available Commands*\n\n"
        "/order ORD001 — Track your order\n"
        "/deals        — See today's deals\n"
        "/start        — Back to main menu",
        parse_mode="Markdown"
    )


async def check_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide an order ID.\nExample: /order ORD001"
        )
        return

    order_id = context.args[0].upper()
    order = ORDERS.get(order_id)

    if order:
        status_emoji = {"Shipped": "🚚", "Processing": "⚙️", "Delivered": "✅"}.get(order["status"], "📦")
        await update.message.reply_text(
            f"*Order {order_id}*\n\n"
            f"{status_emoji} Status : {order['status']}\n"
            f"📦 Item   : {order['item']}\n"
            f"📅 ETA    : {order['eta']}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"❌ Order *{order_id}* not found.\n"
            "Please check your order ID and try again.",
            parse_mode="Markdown"
        )

    logger.info(f"Order check: {order_id} by user {update.effective_user.id}")


async def deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%B %d")
    msg = f"🔥 *Today's Deals — {today}*\n\n"
    for item, price, discount in DEALS:
        msg += f"• {item}\n  {price}  `{discount}`\n\n"
    msg += "DM us to order! 🛒"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤔 I didn't understand that.\nType /help to see what I can do!"
    )


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_cmd))
    app.add_handler(CommandHandler("order", check_order))
    app.add_handler(CommandHandler("deals", deals))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    print("🤖 Bot is running... Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
