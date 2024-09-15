import asyncio

import app_logger
import json
import os

from telegram.ext import Application, MessageHandler, ContextTypes, filters, CommandHandler
from telegram import Update, ForceReply

from database import *

logger = app_logger.get_logger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# --- Telegram Bot ---
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

DOUBLE_CHANCE = 0.1

# Command aliases to avoid duplicate output
COMMAND_ALIASES = {
    "spin": ["pyöräytä", "pyorayta"],
    "bottle": ["pullo"],
    "help": ["ohje", "h"],
    "add": ["lisää", "lisaa"],
    "remove": ["poista"],
    "list": ["lista"]
}

# Admin commands and their expected parameters
ADMIN_COMMANDS = [
    "gif",
]

# Centralized command responses for non-admin commands
START_MESSAGE = "Hei! Komennolla /spin voit pyöräyttää onnenpyörää."
HELP_MESSAGE = """Komennot:
/spin - Pyöräytä onnenpyörää
/pullo_list - Listaa lisätyt pullot
/pullo_add [nimi] - Lisää pullo
/pullo_remove [nimi] - Poista pullo"""


# Define command handlers.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(START_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(HELP_MESSAGE)


async def spin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    is_double = random.random() < DOUBLE_CHANCE
    user = update.effective_user
    # send a random gif
    gif = gif_random()
    message1 = await update.message.reply_text("Pyöräytetään...")
    message2 = None
    if gif:
        message2 = await update.message.reply_text(gif)
    else:
        message2 = await update.message.reply_text("No gifs saved.")
    # send bot is typing action
    await update.message.reply_chat_action("typing")
    # wait 5 seconds
    await asyncio.sleep(5)
    # delete the sent gif
    await message1.delete()
    await message2.delete()

    bottle = bottle_random()
    response = f"{user.mention_html()} Ei pulloja. Lisää komennolla /pullo lisää [nimi]."
    if bottle:
        if is_double:
            response = f"{user.mention_html()} Tuplashotti pullosta {bottle}!!!"
        else:
            response = f"{user.mention_html()} Shotti pullosta {bottle}!"

    await update.message.reply_text(response, reply_markup=ForceReply(selective=True))


async def bottle_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bottles = bottle_list()
    await update.message.reply_text(bottles)


async def bottle_add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = " ".join(context.args)
    response = bottle_add(name)
    await update.message.reply_text(response)


async def bottle_remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = " ".join(context.args)
    response = bottle_remove(name)
    await update.message.reply_text(response)


async def bottle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # parse what subcommand is being called
    subcommand = context.args[0]
    if subcommand in COMMAND_ALIASES["list"]:
        await bottle_list_command(update, context)
    elif subcommand in COMMAND_ALIASES["add"]:
        await bottle_add_command(update, context)
    elif subcommand in COMMAND_ALIASES["remove"]:
        await bottle_remove_command(update, context)
    else:
        await update.message.reply_text("Komennot: list, add, remove")


async def admin_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    admins = admin_list()
    await update.message.reply_text(admins)


async def admin_add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = context.args[0]
    response = admin_add(user_id)
    await update.message.reply_text(response)


async def admin_remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = context.args[0]
    response = admin_remove(user_id)
    await update.message.reply_text(response)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # parse what subcommand is being called
    subcommand = context.args[0]
    if subcommand in COMMAND_ALIASES["list"]:
        await admin_list_command(update, context)
    elif subcommand in COMMAND_ALIASES["add"]:
        await admin_add_command(update, context)
    elif subcommand in COMMAND_ALIASES["remove"]:
        await admin_remove_command(update, context)
    else:
        await update.message.reply_text("Komennot: list, add, remove")


async def gif_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    gifs = gif_list()
    await update.message.reply_text(gifs)


async def gif_add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = context.args[0]
    response = gif_add(url)
    await update.message.reply_text(response)


async def gif_remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = context.args[0]
    response = gif_remove(url)
    await update.message.reply_text(response)


async def gif_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # parse what subcommand is being called
    subcommand = context.args[0]
    if subcommand in COMMAND_ALIASES["list"]:
        await gif_list_command(update, context)
    elif subcommand in COMMAND_ALIASES["add"]:
        await gif_add_command(update, context)
    elif subcommand in COMMAND_ALIASES["remove"]:
        await gif_remove_command(update, context)
    else:
        await update.message.reply_text("Komennot: list, add, remove")


def add_handlers():
    # Add conversation, command, and any other handlers
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("spin", spin_command))
    application.add_handler(CommandHandler("pyorayta", spin_command))
    application.add_handler(CommandHandler("pullo", bottle_command))
    application.add_handler(CommandHandler("pullo_list", bottle_list_command))
    application.add_handler(CommandHandler("pullo_lista", bottle_list_command))
    application.add_handler(CommandHandler("pullo_add", bottle_add_command))
    application.add_handler(CommandHandler("pullo_lisaa", bottle_add_command))
    application.add_handler(CommandHandler("pullo_remove", bottle_remove_command))
    application.add_handler(CommandHandler("pullo_poista", bottle_remove_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("admin_list", admin_list_command))
    application.add_handler(CommandHandler("admin_lista", admin_list_command))
    application.add_handler(CommandHandler("admin_add", admin_add_command))
    application.add_handler(CommandHandler("admin_lisaa", admin_add_command))
    application.add_handler(CommandHandler("admin_remove", admin_remove_command))
    application.add_handler(CommandHandler("admin_poista", admin_remove_command))
    application.add_handler(CommandHandler("gif", gif_command))
    application.add_handler(CommandHandler("gif_list", gif_list_command))
    application.add_handler(CommandHandler("gif_lista", gif_list_command))
    application.add_handler(CommandHandler("gif_add", gif_add_command))
    application.add_handler(CommandHandler("gif_lisaa", gif_add_command))
    application.add_handler(CommandHandler("gif_remove", gif_remove_command))
    application.add_handler(CommandHandler("gif_poista", gif_remove_command))


async def run_bot(event, context):
    await application.initialize()
    logger.info(f"Bot started")
    await application.process_update(
        Update.de_json(json.loads(event["body"]), application.bot)
    )
