from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CallbackContext, CommandHandler

from database import bottle_names_list, gif_list, admin_list, admin_remove, gif_remove, bottle_remove, bottle_list


async def send_selection_message(update: Update, context: CallbackContext, item_names: list, item_ids: list, message: str, callback_data_prefix: str) -> None:
    if not item_names:
        await update.message.reply_text("No items available.")
        return

    # Create inline keyboard buttons for each item with prefixed callback_data
    keyboard = [[InlineKeyboardButton(item_name, callback_data=f"{callback_data_prefix}_{item_id}")]for item_name, item_id in zip(item_names, item_ids)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a message with the inline keyboard
    await update.message.reply_text(message, reply_markup=reply_markup)


async def handle_selection(update: Update, context: CallbackContext, item_type: str, process_function) -> bool:
    query = update.callback_query
    item_name = query.data.split('_', 1)[1]  # Extract item name from callback data
    item_id = query.data.split('_', 2)[2]  # Extract item id from callback data

    # Process the selected item using the provided function
    await process_function(update, item_name, item_id)

    # Acknowledge the callback query and send a response
    await query.answer()
    await query.edit_message_text(text=f"{item_type} '{item_name}' processed.")


async def process_bottle(update, bottle_name: str, bottle_id: str) -> None:
    # Implement the logic for processing a bottle selection
    # For example, remove the bottle from a database

    bottle_remove(bottle_id)

    # get the original message

    #update.message.reply_text(f"Pullo '{selected_bottle}' poistettu.")


async def process_gif(update, gif_name: str, gif_id: str) -> None:
    # Implement the logic for processing a gif selection
    # For example, remove the gif from a database

    gif_remove(gif_id)

    #update.message.reply_text(f"Gif '{selected_gif}' poistettu.")


async def process_admin(update, admin_name: str, admin_id: str) -> None:
    # Implement the logic for processing an admin selection
    # For example, remove the admin from a database

    admin_remove(admin_id)

    #update.message.reply_text(f"Admin '{selected_admin}' poistettu.")


async def bottle_remove_command(update: Update, context: CallbackContext) -> None:
    bottle_names, bottle_ids = bottle_names_list()

    if not bottle_names:
        await update.message.reply_text("Ei pulloja.")
        return
    await send_selection_message(update, context, bottle_names, bottle_ids, "Mikä pullo poistetaan?", "bottle")


async def handle_bottle_selection(update: Update, context: CallbackContext) -> None:
    removed = await handle_selection(update, context, "Pullo", process_bottle)
    #await update.message.reply_text("Pullo poistettu.")


async def gif_remove_command(update: Update, context: CallbackContext) -> None:
    gifs = gif_list()
    if not gifs:
        await update.message.reply_text("Ei giffejä.")
        return
    gifs = [i for i in range(1, len(gif_list() + 1))]  # Replace with your function to list gifs
    await send_selection_message(update, context, gifs, gifs, "Mikä gif poistetaan?", "gif")


async def handle_gif_selection(update: Update, context: CallbackContext) -> None:
    await handle_selection(update, context, "Gif", process_gif)


async def admin_remove_command(update: Update, context: CallbackContext) -> None:
    admins = admin_list()
    await send_selection_message(update, context, admins, admins, "Kuka admin poistetaan?", "admin")


async def handle_admin_selection(update: Update, context: CallbackContext) -> None:
    await handle_selection(update, context, "Admin", process_admin)


def register_callbacks(application):
    # Register command handlers

    application.add_handler(CommandHandler("pullo_remove", bottle_remove_command))
    application.add_handler(CommandHandler("gif_remove", gif_remove_command))
    application.add_handler(CommandHandler("admin_remove", admin_remove_command))

    # Register callback handlers
    application.add_handler(CallbackQueryHandler(handle_bottle_selection, pattern=r'^bottle_'))
    application.add_handler(CallbackQueryHandler(handle_gif_selection, pattern=r'^gif_'))
    application.add_handler(CallbackQueryHandler(handle_admin_selection, pattern=r'^admin_'))
