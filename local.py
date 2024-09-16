import asyncio
import os

os.environ["DYNAMODB_BOTTLES_TABLE"] = "Bottles"
os.environ["DYNAMODB_ADMINS_TABLE"] = "Admins"
os.environ["DYNAMODB_GIFS_TABLE"] = "Gifs"

os.environ["LOG_LEVEL"] = "INFO"

os.environ["TELEGRAM_BOT_TOKEN"] = ""

import app_logger

from bot import run_bot, add_handlers, run_polling

logger = app_logger.logger


def lambda_handler(event, context):
    logger.info(f"Received event: {event}")
    return asyncio.get_event_loop().run_until_complete(main(event, context))


def main():
    add_handlers()
    run_polling()

if __name__ == "__main__":
    main()
