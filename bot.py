# bot.py
import logging
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import config

# Set up logging
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    conn = sqlite3.connect('referral_bot.db')
    return conn

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        'Welcome! Use /referral to get your referral link.\n'
        'Use /points to check your points.\n'
        'Use /withdraw to withdraw points.'
    )

async def referral(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    referral_link = f'tg://resolve?domain={context.bot.username}&start={user_id}'
    await update.message.reply_text(f'Your referral link: {referral_link}')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

async def points(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT points FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    points = result[0] if result else 0
    conn.close()
    await update.message.reply_text(f'You have {points} points.')

async def withdraw(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT points FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    points = result[0] if result else 0
    if points > 0:
        c.execute('UPDATE users SET points = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
        await update.message.reply_text(f'You have successfully withdrawn {points} points.')
    else:
        await update.message.reply_text('You have no points to withdraw.')
    conn.close()

async def join_channel(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    chat_member = await context.bot.get_chat_member(config.CHANNEL_ID, user_id)
    if chat_member.status in ['member', 'administrator', 'creator']:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('UPDATE users SET joined_channel = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        await update.message.reply_text('You have joined the channel!')
    else:
        await update.message.reply_text('You must join the channel to participate in the referral program.')

def main() -> None:
    application = Application.builder().token(config.BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("referral", referral))
    application.add_handler(CommandHandler("points", points))
    application.add_handler(CommandHandler("withdraw", withdraw))
    application.add_handler(CommandHandler("join_channel", join_channel))
    application.run_polling()

if __name__ == '__main__':
    main()
