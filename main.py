import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Load environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Example: "@yourchannel"

# Flask app for keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Service Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Check Membership", callback_data="check_membership")],
        [InlineKeyboardButton("Change Language", callback_data="lang_en")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Hello {user.first_name}! Welcome to the Service Bot.", reply_markup=reply_markup
    )

async def check_membership_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)

    if member.status not in ["left", "kicked"]:
        await query.edit_message_text("✅ You are a member! You can proceed.")
    else:
        await query.edit_message_text(
            f"❌ You are not a member! Please join: {CHANNEL_ID}"
        )

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]  # Example: lang_en
    await query.edit_message_text(f"Language changed to {lang.upper()}.")

async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.split("_")[1]  # Example: cat_services
    await query.edit_message_text(f"You selected category: {category}")

async def service_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    service_type = query.data.split("_")[1]
    await query.edit_message_text(f"You selected service: {service_type}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = update.message.photo[-1]
    file_id = photo_file.file_id
    await update.message.reply_text(f"Photo received! File ID: {file_id}")

async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Description received: {text}")

# --- Main Function ---
def main():
    # Create the Telegram bot application
    bot_app = Application.builder().token(TOKEN).build()

    # Register handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(check_membership_callback, pattern="check_membership"))
    bot_app.add_handler(CallbackQueryHandler(language_handler, pattern="lang_"))
    bot_app.add_handler(CallbackQueryHandler(category_handler, pattern="cat_"))
    bot_app.add_handler(CallbackQueryHandler(service_type_handler, pattern="service_|design_"))
    bot_app.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_photo))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description))

    # Start Flask in a separate thread
    Thread(target=run_flask).start()

    # Run the bot
    bot_app.run_polling()

if __name__ == "__main__":
    main()
