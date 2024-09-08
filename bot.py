import subprocess
import os
import logging
import asyncio
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext
from datetime import datetime
import server
from config import TOKEN, AUTHORIZED_USERS, EXCLUSIVE, USE_PROXIES

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Replace 'YOUR_CHANNEL_USERNAME' with your channel's username (without @)
CHANNEL_USERNAME = '@your_channel_username'

# Check if the user is part of the Telegram channel
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    
    # Check if user is in the channel
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome back! You are already a member of the channel.")
            # Sending bot command instructions after membership check
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="The Commands are:\n*/cube*\n*/train*\n*/merge*\n*/twerk*\n*/poly*\n*/trim*\n*/cafe*\n*/zoo*\n*/tile*\n*/fluff*\n*/stone*\n*/all*\nThese will generate 4 keys for their respective games\\. /fluff will generate 8 keys\\.",
                parse_mode='MARKDOWNV2'
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You can also set how many keys are generated\\. For example, */cube 8* will generate *EIGHT* keys for the cube game\\.",
                parse_mode='MARKDOWNV2'
            )
        else:
            await update.message.reply_text(f"You need to join the channel {CHANNEL_USERNAME} to use this bot.")
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        await update.message.reply_text(f"You need to join the channel {CHANNEL_USERNAME} to use this bot.")

# Game handler function
async def game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, chosen_game: int, all: bool, delay=0):
    if EXCLUSIVE and update.effective_chat.id not in AUTHORIZED_USERS:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Clone this bot from zeedtek telegram channel.",
            parse_mode='MARKDOWNV2'
        )
        with open(f'{os.path.dirname(__file__)}/unauthorized', 'a') as file:
            unauthorized_message = f"Unauthorized User: {update.effective_chat.first_name} - {update.effective_chat.username}: {update.effective_chat.id}"
            server.logger.warning(unauthorized_message)
            file.write(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} {unauthorized_message}\n")
        return

    # Delay for the /all command
    await asyncio.sleep(delay)
    server.logger.info(f"Delay for {delay} seconds")

    server.logger.info(f"Generating for client: {update.effective_chat.first_name} - {update.effective_chat.username}: {update.effective_chat.id}")
    if not all:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🐹🔑")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Generating\\.\\.\\.", parse_mode='MARKDOWNV2')
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"This will only take a moment , follow Updates channel while you wait @zeedtek\\.\\.\\.", parse_mode='MARKDOWNV2')

    if server.GAMES[chosen_game]['name'] == "Fluff Crusade":
        no_of_keys = 8
    else:
        no_of_keys = int(context.args[0]) if context.args else 4
    
    key_count = 0
    async for key in server.run(chosen_game=chosen_game, no_of_keys=no_of_keys, use_proxies=USE_PROXIES):
        formatted_key = f"`{key}`"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{key_count + 1}\\. {formatted_key}", parse_mode='MARKDOWNV2')
        server.logger.info(f"Message sent to client: {update.effective_chat.first_name} - {update.effective_chat.username}: {update.effective_chat.id}")
        key_count += 1

# Define the command functions for each game
async def cube(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=1, all=all)

async def train(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=2, all=all)

async def merge(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=3, all=all)

async def twerk(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=4, all=all)

async def poly(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=5, all=all)

async def trim(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=6, all=all)

async def zoo(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=7, all=all)

async def tile(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=8, all=all)

async def fluff(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=9, all=all)

async def stone(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=10, all=all)

# Command for generating all games
async def all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if EXCLUSIVE and update.effective_chat.id not in AUTHORIZED_USERS:
        return
    
    server.logger.info(f"Generating ALL GAMES for client: {update.effective_chat.first_name} - {update.effective_chat.username}: {update.effective_chat.id}")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="🐹")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Currently generating for all games\\.\\.\\.", parse_mode='MARKDOWNV2')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Come back in about 5\\-10 minutes\\.", parse_mode='MARKDOWNV2')

    # Wait a certain number of seconds between each game
    tasks = [game_handler(update, context, i + 1, True, i * 30) for i in range(len(server.GAMES))]
    await asyncio.gather(*tasks)

# Main entry point to start the bot
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    logger.info("Server is running. Awaiting users...")

    # Add command handlers
    application.add_handler(CommandHandler('start', start, block=False))
    application.add_handler(CommandHandler('cube', cube, block=False))
    application.add_handler(CommandHandler('train', train, block=False))
    application.add_handler(CommandHandler('merge', merge, block=False))
    application.add_handler(CommandHandler('twerk', twerk, block=False))
    application.add_handler(CommandHandler('poly', poly, block=False))
    application.add_handler(CommandHandler('trim', trim, block=False))
    application.add_handler(CommandHandler('zoo', zoo, block=False))
    application.add_handler(CommandHandler('tile', tile, block=False))
    application.add_handler(CommandHandler('fluff', fluff, block=False))
    application.add_handler(CommandHandler('stone', stone, block=False))
    application.add_handler(CommandHandler('all', all, block=False))

    # Start polling to handle updates
    application.run_polling()
