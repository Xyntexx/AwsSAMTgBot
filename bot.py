import asyncio

import app_logger
import json

from telegram.ext import Application, MessageHandler, ContextTypes, filters, CommandHandler, CallbackContext, CallbackQueryHandler
from telegram import Update, ForceReply, InlineKeyboardMarkup, KeyboardButtonRequestUsers, helpers, User, KeyboardButton, ReplyKeyboardMarkup

from database import *

import remove_commands

logger = app_logger.logger

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# --- Telegram Bot ---
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

DOUBLE_CHANCE = 0.1

# Admin commands and their expected parameters
ADMIN_COMMANDS = [
    "gif",
]

# Centralized command responses for non-admin commands
START_MESSAGE = "Hei! Komennolla /spin voit pyöräyttää onnenpyörää."
HELP_MESSAGE = """Komennot:
/spin - Pyöräytä onnenpyörää
/pullo_list - Listaa lisätyt pullot
/pullo_add - Lisää pullo
/pullo_remove - Poista pullo
Apua: https://paihdelinkki.fi/mista-apua/"""

GIF_ADD_MESSAGE = helpers.escape_markdown("Lisää giffi vastaamalla tähän viestiin", 2)
BOTTLE_ADD_MESSAGE = helpers.escape_markdown("Mikä pullo lisätään? Vastaa tähän viestiin", 2)
ADMIN_ADD_MESSAGE = helpers.escape_markdown("Lisää admin", 2)


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
    message1 = await update.message.reply_text("Pyöräytetään...", disable_notification=True)
    message2 = None
    if gif:
        message2 = await update.message.reply_animation(gif, disable_notification=True)
    # send bot is typing action
    await update.message.reply_chat_action("typing")
    # wait 5 seconds
    await asyncio.sleep(3)
    # delete the sent gif
    await message1.delete()
    if message2:
        await message2.delete()

    bottle = bottle_random()

    mention = user.mention_markdown_v2(name=user.first_name)

    response = helpers.escape_markdown(f"Ei pulloja. Lisää komennolla /pullo_add", 2)
    if bottle:
        if is_double:
            response = f"*{helpers.escape_markdown(f"Tuplashotti pullosta {bottle}!!!", 2)}*"
        else:
            response = helpers.escape_markdown(f"Shotti pullosta {bottle}!", 2)

    await update.message.reply_text(f"{mention} {response}", parse_mode="MarkdownV2")


async def bottle_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bottles = "\n".join(bottle_names_list())
    await update.message.reply_text(bottles)


async def admin_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Ei oikeuksia.")
        return
    admins = admin_list()
    if not admins:
        await update.message.reply_text("Ei admineja.")
        return
    admins = "\n".join(admin_list())
    await update.message.reply_text(admins)


async def gif_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Ei oikeuksia.")
        return
    gif_ids, file_ids = gif_list()
    if not gif_ids:
        await update.message.reply_text("Ei giffejä.")
        return
    length = len(gif_ids)
    for i in range(length):
        await update.message.reply_text(f"{i + 1}")
        await update.message.reply_animation(file_ids[i])


user_data = {}


async def bottle_add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user: User = update.effective_user
    user_id = user.id

    mention = user.mention_markdown_v2(name=user.first_name)
    initial_message = await update.message.reply_text(f"{mention} {BOTTLE_ADD_MESSAGE}", reply_markup=ForceReply(selective=True), parse_mode="MarkdownV2")

    if user_id in user_data:
        # Delete the previous ForceReply message
        await update.message.chat.delete_message(user_data[user_id]["initial_message_id"])
    # Store the user state and message ID to delete later
    user_data[user_id] = {
        "state": "awaiting_bottle_name",
        "initial_message_id": initial_message.message_id
    }


async def gif_add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Ei oikeuksia.")
        return
    user = update.effective_user
    user_id = update.message.from_user.id

    mention = user.mention_markdown_v2(name=user.first_name)
    initial_message = await update.message.reply_text(f"{mention} {GIF_ADD_MESSAGE}", reply_markup=ForceReply(selective=True), parse_mode="MarkdownV2")

    if user_id in user_data:
        # Delete the previous ForceReply message
        await update.message.chat.delete_message(user_data[user_id]["initial_message_id"])
    # Store the user state and message ID to delete later
    user_data[user_id] = {
        "state": "awaiting_gif_url",
        "initial_message_id": initial_message.message_id
    }


async def handle_user_response(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_response = update.message.text

    # Check if the user is in the process of adding a bottle
    if user_id not in user_data:
        return
    state = user_data[user_id]["state"]
    if state == "awaiting_bottle_name":
        # Check if the user is responding to the ForceReply message
        if not update.message.reply_to_message or update.message.reply_to_message.message_id != user_data[user_id]["initial_message_id"]:
            return

        # Check if the user response is empty
        if not user_response or not user_response.strip():
            return
        bottle_name = user_response.strip()

        # Add the bottle to your list or database here
        # Example: append to a list (replace this with your actual implementation)
        bottle_add(bottle_name, user_id)

        # Get the initial message ID from user_data
        initial_message_id = user_data[user_id]["initial_message_id"]

        # Delete the initial question message
        await update.message.chat.delete_message(initial_message_id)

        # Inform the user that the bottle has been added
        await update.message.reply_text(f"Pullo '{bottle_name}' lisätty.")

        # Clear user state
        del user_data[user_id]

    elif state == "awaiting_gif_url":
        # Check if the user is responding to the ForceReply message
        if not update.message.reply_to_message or update.message.reply_to_message.message_id != user_data[user_id]["initial_message_id"]:
            return

        # Check if the user sent an animation
        if not update.message.animation:
            return
        file_id = update.message.animation.file_id

        # Add the gif to your list or database here
        # Example: append to a list (replace this with your actual implementation)
        gif_add(file_id)

        # Get the initial message ID from user_data
        initial_message_id = user_data[user_id]["initial_message_id"]

        # Delete the initial question message
        await update.message.chat.delete_message(initial_message_id)

        # Inform the user that the gif has been added
        await update.message.reply_text(f"Giffi lisätty.")

        # Clear user state
        del user_data[user_id]

    elif state == "awaiting_admin_user":
        # Check if the request is valid
        if not update.message.users_shared.users:
            return
        admin_user_id = update.message.users_shared.users[0].user_id

        # Perform the admin add operation
        ret = admin_add(admin_user_id)

        # Get the initial message ID from user_data
        initial_message_id = user_data[user_id]["initial_message_id"]

        # Delete the initial question message
        await update.message.chat.delete_message(initial_message_id)

        if not ret:
            await update.message.reply_text(f"Admin ei lisätty.")
        else:
            # Inform the user that the gif has been added
            await update.message.reply_text(f"Admin lisätty.")

        # Clear user state
        del user_data[user_id]


async def admin_add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Ei oikeuksia.")
        return
    # Create a KeyboardButtonRequestUser object
    # Create a Signed 32-bit identifier of the request
    # Store the request in the admin_user_requests dictionary
    user_id = update.message.from_user.id
    request_id = random.randint(-2_147_483_648, 2_147_483_647)
    user_request = KeyboardButtonRequestUsers(request_id, user_is_bot=False)
    button = KeyboardButton("Lisää admin", request_users=user_request)
    keyboard = [[button]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, selective=True, resize_keyboard=True)
    message = await update.message.reply_text(ADMIN_ADD_MESSAGE, reply_markup=reply_markup, parse_mode="MarkdownV2")
    message_id = message.message_id
    user_data[user_id] = {
        "state": "awaiting_admin_user",
        "initial_message_id": message_id,
        "request_id": request_id,
    }


def add_handlers():
    # Add conversation, command, and any other handlers
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start, filters=~filters.UpdateType.EDITED))
    application.add_handler(CommandHandler("help", help_command, filters=~filters.UpdateType.EDITED))
    application.add_handler(CommandHandler("spin", spin_command, filters=~filters.UpdateType.EDITED))
    application.add_handler(CommandHandler("pullo_list", bottle_list_command, filters=~filters.UpdateType.EDITED))
    application.add_handler(CommandHandler("pullo_add", bottle_add_command, filters=~filters.UpdateType.EDITED))
    application.add_handler(CommandHandler("admin_list", admin_list_command, filters=~filters.UpdateType.EDITED))
    application.add_handler(CommandHandler("admin_add", admin_add_command, filters=~filters.UpdateType.EDITED))
    application.add_handler(CommandHandler("gif_list", gif_list_command, filters=~filters.UpdateType.EDITED))
    application.add_handler(CommandHandler("gif_add", gif_add_command, filters=~filters.UpdateType.EDITED))

    remove_commands.register_callbacks(application)

    # add handler for messages that are replies to our messages
    application.add_handler(MessageHandler(~filters.COMMAND & ~filters.UpdateType.EDITED, handle_user_response))


async def run_bot(event, context):
    await application.initialize()
    logger.info(f"Bot started")
    await application.process_update(
        Update.de_json(json.loads(event["body"]), application.bot)
    )


def run_polling():
    logger.info(f"Bot starting in polling mode")
    application.run_polling()
