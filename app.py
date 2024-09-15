import asyncio
import app_logger

from bot import run_bot, add_handlers

logger = app_logger.logger


def lambda_handler(event, context):
    logger.info(f"Received event: {event}")
    return asyncio.get_event_loop().run_until_complete(main(event, context))


async def main(event, context):
    add_handlers()

    try:
        await run_bot(event, context)

        return {
            'statusCode': 200,
            'body': 'Success'
        }

    except Exception as exc:
        logger.error(f"Error processing request: {exc}")
        return {
            'statusCode': 500,
            'body': 'Failure'
        }
