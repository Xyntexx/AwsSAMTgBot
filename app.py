import json
import os
import requests
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
bottles_table = dynamodb.Table(os.environ['DYNAMODB_BOTTLES_TABLE'])
admins_table = dynamodb.Table(os.environ['DYNAMODB_ADMINS_TABLE'])
gifs_table = dynamodb.Table(os.environ['DYNAMODB_GIFS_TABLE'])

# Get the Telegram bot token from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    message = body.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')

    response_text = handle_commands(text)

    send_message(chat_id, response_text)

    return {
        'statusCode': 200,
        'body': json.dumps({'status': 'success'})
    }

def handle_commands(text):
    if text.startswith('/start'):
        return "Welcome to the bot! Use /help to see available commands."

    if text.startswith('/help'):
        return help_text()

    if text.startswith('/pyöräytä'):
        return "Pyöräytä command received."

    if text.startswith('/pullo'):
        return handle_pullo_command(text)

    if text.startswith('/admin'):
        return handle_admin_command(text)

    if text.startswith('/gif'):
        return handle_gif_command(text)

    return "Unknown command. Use /help to see available commands."

def help_text():
    return (
        "Here are the commands you can use:\n"
        "/start - Start the bot and see a welcome message.\n"
        "/help - Display this help message.\n"
        "/pyöräytä - Example command for demonstration.\n"
        "/pullo [lisää|poista|lista|add|remove|list] - Manage bottles.\n"
        "/admin [lisää|poista|lista|add|remove|list] - Manage admins.\n"
        "/gif [lisää|poista|lista|add|remove|list] - Manage GIFs."
    )

def handle_pullo_command(text):
    action = get_action_from_command(text)
    if action == 'add':
        return add_to_dynamodb(bottles_table, text)
    elif action == 'remove':
        return remove_from_dynamodb(bottles_table, text)
    elif action == 'list':
        return list_from_dynamodb(bottles_table)
    else:
        return "Invalid pullo command. Use /pullo [lisää|poista|lista|add|remove|list]."

def handle_admin_command(text):
    action = get_action_from_command(text)
    if action == 'add':
        return add_to_dynamodb(admins_table, text)
    elif action == 'remove':
        return remove_from_dynamodb(admins_table, text)
    elif action == 'list':
        return list_from_dynamodb(admins_table)
    else:
        return "Invalid admin command. Use /admin [lisää|poista|lista|add|remove|list]."

def handle_gif_command(text):
    action = get_action_from_command(text)
    if action == 'add':
        return add_to_dynamodb(gifs_table, text)
    elif action == 'remove':
        return remove_from_dynamodb(gifs_table, text)
    elif action == 'list':
        return list_from_dynamodb(gifs_table)
    else:
        return "Invalid gif command. Use /gif [lisää|poista|lista|add|remove|list]."

def get_action_from_command(text):
    if 'lisää' in text or 'add' in text:
        return 'add'
    elif 'poista' in text or 'remove' in text:
        return 'remove'
    elif 'lista' in text or 'list' in text:
        return 'list'
    return None

def add_to_dynamodb(table, text):
    item_id = extract_id_from_command(text)
    try:
        table.put_item(Item={'id': item_id})
        return f"Item with ID {item_id} added."
    except ClientError as e:
        return f"Error adding item: {e.response['Error']['Message']}"

def remove_from_dynamodb(table, text):
    item_id = extract_id_from_command(text)
    try:
        table.delete_item(Key={'id': item_id})
        return f"Item with ID {item_id} removed."
    except ClientError as e:
        return f"Error removing item: {e.response['Error']['Message']}"

def list_from_dynamodb(table):
    try:
        response = table.scan()
        items = response.get('Items', [])
        if items:
            return json.dumps(items, indent=4)
        else:
            return "No items found."
    except ClientError as e:
        return f"Error listing items: {e.response['Error']['Message']}"

def extract_id_from_command(text):
    parts = text.split(' ')
    return parts[1] if len(parts) > 1 else 'unknown'

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=payload)
