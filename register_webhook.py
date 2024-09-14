import requests

# Constants
TELEGRAM_API_URL = 'https://api.telegram.org/bot{}/setWebhook'


def register_webhook(telegram_bot_token, webhook_url, secret_token):
    """Register the webhook with Telegram."""
    # Construct the webhook URL including the secret token as a query parameter
    full_webhook_url = f'{webhook_url}?secret_token={secret_token}'

    # Prepare the payload for the Telegram API request
    payload = {
        'url': full_webhook_url
    }

    # Make the request to set the webhook
    response = requests.post(TELEGRAM_API_URL.format(telegram_bot_token), json=payload)

    if response.status_code == 200:
        result = response.json()
        if result.get('ok'):
            print('Webhook registered successfully.')
        else:
            print('Failed to register webhook:', result.get('description'))
    else:
        print('Error registering webhook:', response.status_code, response.text)


def main():
    # Input Telegram bot token and secret token from the user
    telegram_bot_token = input("Enter your Telegram bot token: ").strip()
    webhook_url = input("Enter your webhook URL: ").strip()
    secret_token = input("Enter your secret token: ").strip()

    # Register the webhook with Telegram
    register_webhook(telegram_bot_token, webhook_url, secret_token)


if __name__ == '__main__':
    main()
