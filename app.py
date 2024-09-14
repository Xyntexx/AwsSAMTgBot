import os
import json
import boto3
import requests
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage"


def lambda_handler(event, context):
    # Parse the Telegram message
    body = json.loads(event['body'])

    chat_id = body['message']['chat']['id']
    message_text = body['message']['text']
    message_id = str(body['message']['message_id'])

    # Save the message to DynamoDB
    try:
        table.put_item(
            Item={
                'MessageId': message_id,
                'ChatId': str(chat_id),
                'MessageText': message_text
            }
        )
    except ClientError as e:
        print(f"Error saving message: {e.response['Error']['Message']}")

    # Respond to the user
    reply_text = f"You said: {message_text}"
    send_message(chat_id, reply_text)

    return {
        'statusCode': 200,
        'body': json.dumps('Message processed successfully!')
    }


def send_message(chat_id, text):
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
