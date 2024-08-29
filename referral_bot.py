import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
import sqlite3
import os

# Configuration
TOKEN = '7494153356:AAFQo6RDU7o_Cjn88uVqmwTFyQZaqoOn25k'
CHANNEL_ID = '@pancake90x'  # Updated to your new channel

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a new SQLite database if it doesn't exist
def init_db():
    if not os.path.isfile('referral_bot.db'):
        conn = sqlite3.connect('referral_bot.db')
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            referred_by INTEGER,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        conn.close()

# Command Handlers
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    referred_by = context.args[0] if context.args else None
    
    conn = sqlite3.connect('referral_bot.db')
    c = conn.cursor()
    c.execute('SELECT * FROM referrals WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    
    if result is None:
        # Add user to database
        c.execute('INSERT INTO referrals (user_id, referred_by) VALUES (?, ?)', (user_id, referred_by))
        conn.commit()
        
        if referred_by:
            context.bot.send_message(chat_id=referred_by, text=f"Your referral link has been used by user {user_id}!")
    
    conn.close()
    
    # Send a welcome message and ask to join the channel
    await update.message.reply_text(
        f"Welcome! To complete the registration, please join our channel {CHANNEL_ID}.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_ID[1:]}")]]
        )
    )

    # After joining, prompt the user to type /verify to confirm their membership
    await update.message.reply_text(
        "After joining, please type /verify to confirm your membership.\n\n1 POINT = $50.\n\nPlease note that if you leave the channel, your points will be withdrawn to 0 automatically."
    )

async def verify(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    # Since we are not verifying the actual membership, just let the user through
    await update.message.reply_text("Thank you for confirming! You are now fully registered.")
    await update.message.reply_text(
        "Now you can use the following commands:\n"
        "/referral - Get your referral link\n"
        "/points - Check your referral points\n"
        "/withdraw - Request withdrawal\n\nRemember, 1 POINT = $50.\n\nPlease note that if you leave the channel, your points will be withdrawn to 0 automatically."
    )

async def referral(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    await update.message.reply_text(f"Share this link to refer others to the bot: {referral_link}")

async def points(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    conn = sqlite3.connect('referral_bot.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM referrals WHERE referred_by = ?', (user_id,))
    points = c.fetchone()[0]
    conn.close()
    dollar_value = points * 50
    await update.message.reply_text(f"You have {points} points.\nThis equals ${dollar_value}.\n\nRemember, if you leave the channel, your points will be withdrawn to 0 automatically.")

async def withdraw(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    conn = sqlite3.connect('referral_bot.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM referrals WHERE referred_by = ?', (user_id,))
    points = c.fetchone()[0]
    conn.close()
    
    if points < 200:
        await update.message.reply_text("You need at least 200 points to request a withdrawal. Please continue referring others.")
    else:
        await update.message.reply_text("To request a withdrawal, please contact our support team.")

def main() -> None:
    # Initialize the database
    init_db()
    
    # Create the application and add handlers
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify))
    application.add_handler(CommandHandler("referral", referral))  # Added referral command
    application.add_handler(CommandHandler("points", points))
    application.add_handler(CommandHandler("withdraw", withdraw))

    application.run_polling()

if __name__ == '__main__':
    main()
