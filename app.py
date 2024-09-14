import json
import os
import random
import boto3
import requests

# Environment variables
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DYNAMODB_BOTTLES_TABLE = os.environ.get('DYNAMODB_BOTTLES_TABLE')
DYNAMODB_ADMINS_TABLE = os.environ.get('DYNAMODB_ADMINS_TABLE')
DYNAMODB_GIFS_TABLE = os.environ.get('DYNAMODB_GIFS_TABLE')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"

# DynamoDB clients
dynamodb = boto3.resource('dynamodb')
bottles_table = dynamodb.Table(DYNAMODB_BOTTLES_TABLE)
admins_table = dynamodb.Table(DYNAMODB_ADMINS_TABLE)
gifs_table = dynamodb.Table(DYNAMODB_GIFS_TABLE)


def lambda_handler(event, context):
    # Parse the incoming update from Telegram
    body = json.loads(event['body'])
    message = body.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')

    # Get the user ID to check if they are an admin
    user_id = message.get('from', {}).get('id')
    is_admin = check_if_admin(user_id)

    # Handle commands
    if text.startswith('/start'):
        send_help_message(chat_id, is_admin)

    elif text.startswith('/pyorayta') or text.startswith('/spin'):
        handle_pyorayta(chat_id)

    elif text.startswith('/bottle'):
        handle_bottle_command(chat_id, text)

    elif text.startswith('/admin'):
        handle_admin_command(chat_id, text, is_admin)

    elif text.startswith('/gif'):
        handle_gif_command(chat_id, text, is_admin)

    return {
        'statusCode': 200,
        'body': json.dumps({'status': 'ok'})
    }


def check_if_admin(user_id):
    response = admins_table.get_item(Key={'id': str(user_id)})
    return 'Item' in response


def send_help_message(chat_id, is_admin):
    if is_admin:
        help_text = (
            "/start - Show this help message\n"
            "/pyorayta - Spin the wheel\n"
            "/bottle [lisää|poista|lista|add|remove|list] - Manage bottles\n"
            "/admin [lisää|poista|lista|add|remove|list] - Manage admins\n"
            "/gif [lisää|poista|lista|add|remove|list] - Manage GIFs"
        )
    else:
        help_text = (
            "/start - Show this help message\n"
            "/pyorayta - Spin the wheel\n"
        )
    send_message(chat_id, help_text)


def handle_pyorayta(chat_id):
    # Get a random GIF from DynamoDB
    response = gifs_table.scan()
    items = response.get('Items', [])

    if items:
        gif_url = random.choice(items).get('url')
        send_message(chat_id, gif_url)
    else:
        send_message(chat_id, "No GIFs saved.")


def handle_bottle_command(chat_id, text):
    # Handle bottle-related commands
    # Placeholder for actual bottle command handling logic
    send_message(chat_id, "Bottle command received.")


def handle_admin_command(chat_id, text, is_admin):
    if is_admin:
        # Handle admin-related commands
        # Placeholder for actual admin command handling logic
        send_message(chat_id, "Admin command received.")
    else:
        send_message(chat_id, "You are not authorized to use admin commands.")


def handle_gif_command(chat_id, text, is_admin):
    if is_admin:
        # Handle GIF-related commands
        # Placeholder for actual GIF command handling logic
        send_message(chat_id, "GIF command received.")
    else:
        send_message(chat_id, "You are not authorized to use GIF commands.")


def send_message(chat_id, text):
    url = TELEGRAM_API_URL + 'sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    return response.json()
