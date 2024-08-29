import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import psycopg2
import os

# Configuration
TOKEN = '7298768595:AAFEa7ojD-hevC5dRQXOWEEv2eMhfNmDQXY'
CHANNEL_ID = '@pancake90x'

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.environ['DATABASE_URL']

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Create a new database table if it doesn't exist
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS referrals (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        referred_by BIGINT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

# Command Handlers
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    referred_by = context.args[0] if context.args else None
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM referrals WHERE user_id = %s', (user_id,))
    result = c.fetchone()
    
    if result is None:
        # Add user to database
        c.execute('INSERT INTO referrals (user_id, referred_by) VALUES (%s, %s)', (user_id, referred_by))
        conn.commit()
        
        if referred_by:
            context.bot.send_message(chat_id=referred_by, text=f"Your referral link has been used by user {user_id}!")
    
    conn.close()
    
    # Send a welcome message and ask to join the channel
    await update.message.reply_text(
        f"🚀 Welcome aboard! To finalize your registration, join our channel {CHANNEL_ID}. 💸 For every referral, you'll earn $50! Dive into the biggest referral program sponsored by PancakeWhales Pump Group and unlock weekly earnings up to 800X from their channel! Don't miss out—join now and start earning big! 🚀💰",
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
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM referrals WHERE referred_by = %s', (user_id,))
    points = c.fetchone()[0]
    conn.close()
    dollar_value = points * 50
    await update.message.reply_text(f"You have {points} points.\nThis equals ${dollar_value}.\n\nRemember, if you leave the channel, your points will be withdrawn to 0 automatically.Also we will detect bots account if you are sending bots your points will be automatically reset to 0")

async def withdraw(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM referrals WHERE referred_by = %s', (user_id,))
    points = c.fetchone()[0]
    conn.close()
    
    if points < 200:
        await update.message.reply_text("You need at least 200 points to request a withdrawal. Please continue referring others.")
    else:
        await update.message.reply_text("To request a withdrawal, please contact our support team.")

async def stats(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    # Only allow the user with ID 5607989288 to access this command
    if user_id != 5607989288:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Total number of users
    c.execute('SELECT COUNT(*) FROM referrals')
    total_users = c.fetchone()[0]
    
    # Number of users who have referred others
    c.execute('SELECT COUNT(DISTINCT referred_by) FROM referrals WHERE referred_by IS NOT NULL')
    referring_users = c.fetchone()[0]
    
    # Example of sending the stats
    await update.message.reply_text(
        f"Total users: {total_users}\nUsers who have referred others: {referring_users}"
    )
    
    conn.close()

def main() -> None:
    # Initialize the database
    init_db()
    
    # Create the application and add handlers
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify))
    application.add_handler(CommandHandler("referral", referral))
    application.add_handler(CommandHandler("points", points))
    application.add_handler(CommandHandler("withdraw", withdraw))
    application.add_handler(CommandHandler("stats", stats))  # Hidden command for stats, accessible only by user 5607989288

    application.run_polling()

if __name__ == '__main__':
    main()
