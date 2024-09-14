import secrets

def generate_secret_token():
    """Generate a secure random secret token."""
    return secrets.token_hex(32)

def main():
    secret_token = generate_secret_token()
    print(f"Generated secret token: {secret_token}")

if __name__ == '__main__':
    main()