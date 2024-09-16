from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CallbackContext, CommandHandler, filters
from telegram.helpers import escape_markdown

from database import bottle_names_list, gif_list, admin_list, admin_remove, gif_remove, bottle_remove, bottle_list, is_admin

import re


def escape_underscores(text: str) -> str:
    """Escape underscores by replacing them with a special placeholder."""
    return text.replace('_', '\\_')  # Replaces underscores with escaped versions


def unescape_underscores(text: str) -> str:
    """Unescape underscores by replacing '\\_' with '_'."""
    return text.replace('\\_', '_')


async def send_selection_message(update: Update, context: CallbackContext, item_names: list, item_ids: list, message: str, callback_data_prefix: str) -> None:
    if not item_names:
        await update.message.reply_text("No items available.")
        return

    # Escape underscores in item names
    escaped_item_names = [escape_underscores(item_name) for item_name in item_names]

    # Create inline keyboard buttons for each item with prefixed callback_data
    keyboard = [[InlineKeyboardButton(item_name, callback_data=f"{callback_data_prefix}_{item_name}_{item_id}")]
                for item_name, item_id in zip(escaped_item_names, item_ids)]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a message with the inline keyboard
    await update.message.reply_text(message, reply_markup=reply_markup)


async def handle_selection(update: Update, context: CallbackContext, item_type: str, process_function) -> bool:
    query = update.callback_query
    callback_items = query.data.split('_', 3)
    if len(callback_items) != 3:
        await query.answer()
        await query.edit_message_text(text="Invalid selection.")
        return False
    item_name = unescape_underscores(callback_items[1])
    item_id = callback_items[2]

    # Process the selected item using the provided function
    await process_function(update, item_id)

    # Acknowledge the callback query and send a response
    await query.answer()
    await query.edit_message_text(text=f"{item_type} '{item_name}' poistettu.")


async def process_bottle(update, bottle_id: str) -> None:
    # Implement the logic for processing a bottle selection
    # For example, remove the bottle from a database

    bottle_remove(bottle_id)

    # get the original message

    #update.message.reply_text(f"Pullo '{selected_bottle}' poistettu.")


async def process_gif(update, gif_id: str) -> None:
    # Implement the logic for processing a gif selection
    # For example, remove the gif from a database

    gif_remove(gif_id)

    #update.message.reply_text(f"Gif '{selected_gif}' poistettu.")


async def process_admin(update, admin_id: str) -> None:
    # Implement the logic for processing an admin selection
    # For example, remove the admin from a database

    admin_remove(admin_id)


async def bottle_remove_command(update: Update, context: CallbackContext) -> None:
    bottle_names, bottle_ids = bottle_list()

    if not bottle_names:
        await update.message.reply_text("Ei pulloja.")
        return
    await send_selection_message(update, context, bottle_names, bottle_ids, "Mikä pullo poistetaan?", "bottle")


async def handle_bottle_selection(update: Update, context: CallbackContext) -> None:
    removed = await handle_selection(update, context, "Pullo", process_bottle)


async def gif_remove_command(update: Update, context: CallbackContext) -> None:
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

    gif_names = [str(i+1) for i in range(length)]  # Replace with your function to list gifs
    await send_selection_message(update, context, gif_names, gif_ids, "Mikä gif poistetaan?", "gif")


async def handle_gif_selection(update: Update, context: CallbackContext) -> None:
    await handle_selection(update, context, "Gif", process_gif)


async def admin_remove_command(update: Update, context: CallbackContext) -> None:
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Ei oikeuksia.")
        return
    admins = admin_list()
    await send_selection_message(update, context, admins, admins, "Kuka admin poistetaan?", "admin")


async def handle_admin_selection(update: Update, context: CallbackContext) -> None:
    await handle_selection(update, context, "Admin", process_admin)


def register_callbacks(application):
    # Register command handlers

    application.add_handler(CommandHandler("pullo_remove", bottle_remove_command,filters=~filters.UpdateType.EDITED))
    application.add_handler(CommandHandler("gif_remove", gif_remove_command,filters=~filters.UpdateType.EDITED))
    application.add_handler(CommandHandler("admin_remove", admin_remove_command,filters=~filters.UpdateType.EDITED))

    # Register callback handlers
    application.add_handler(CallbackQueryHandler(handle_bottle_selection, pattern=r'^bottle_'))
    application.add_handler(CallbackQueryHandler(handle_gif_selection, pattern=r'^gif_'))
    application.add_handler(CallbackQueryHandler(handle_admin_selection, pattern=r'^admin_'))
