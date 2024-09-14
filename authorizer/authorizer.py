import os

# Retrieve the secret token from environment variables
SECRET_TOKEN = os.environ.get('SECRET_TOKEN')


def lambda_handler(event, context):
    # Extract the token from the request headers
    token = event['headers'].get('X-Telegram-Bot-Api-Secret-Token')

    # Check if the token matches the expected secret token
    if token == SECRET_TOKEN:
        return {
            'principalId': 'user',
            'policyDocument': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': 'execute-api:Invoke',
                        'Effect': 'Allow',
                        'Resource': event['methodArn']
                    }
                ]
            }
        }
    else:
        return {
            'principalId': 'user',
            'policyDocument': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': 'execute-api:Invoke',
                        'Effect': 'Deny',
                        'Resource': event['methodArn']
                    }
                ]
            }
        }
