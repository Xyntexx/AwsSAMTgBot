import os
import random
import time
import uuid

import boto3

# Fetch environment variables for DynamoDB tables
DYNAMODB_BOTTLES_TABLE = os.environ.get("DYNAMODB_BOTTLES_TABLE")
DYNAMODB_ADMINS_TABLE = os.environ.get("DYNAMODB_ADMINS_TABLE")
DYNAMODB_GIFS_TABLE = os.environ.get("DYNAMODB_GIFS_TABLE")

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb")

# Initialize DynamoDB tables
bottles_table = dynamodb.Table(DYNAMODB_BOTTLES_TABLE)
admins_table = dynamodb.Table(DYNAMODB_ADMINS_TABLE)
gifs_table = dynamodb.Table(DYNAMODB_GIFS_TABLE)


# -------------------------------------
# GIF Functions
# -------------------------------------

def gif_random():
    """Fetches a random GIF from the DynamoDB table."""
    try:
        gifs = gifs_table.scan().get("Items", [])
        if not gifs:
            return None
        return random.choice(gifs)["file_id"]
    except Exception as e:
        print(f"Error fetching gifs: {e}")
        return None


def gif_list() -> tuple[list[str], list[str]]:
    """Lists all GIFs stored in the DynamoDB table."""
    try:
        gifs = gifs_table.scan().get("Items", [])
        if not gifs:
            return [], []
        return [gif["id"] for gif in gifs], [gif["file_id"] for gif in gifs]
    except Exception as e:
        print(f"Error fetching gifs: {e}")
        return [], []


def gif_add(file_id):
    """Adds a new GIF to the DynamoDB table."""
    # Generate a unique id for the GIF
    gif_id = str(uuid.uuid4())
    try:
        gifs_table.put_item(Item={"id": gif_id, "file_id": file_id})
        return True
    except Exception as e:
        print(f"Error adding GIF: {e}")
        return False


def gif_remove(gif_id):
    """Removes a GIF from the DynamoDB table by id."""
    try:
        gifs_table.delete_item(Key={"id": gif_id})
        return True
    except Exception as e:
        print(f"Error removing GIF: {e}")
        return False


# -------------------------------------
# Bottle Functions
# -------------------------------------

def bottle_random():
    """Fetches a random bottle name from the DynamoDB table."""
    try:
        bottles = bottles_table.scan().get("Items", [])
        if not bottles:
            return None
        return random.choice(bottles)["bottle_name"]
    except Exception as e:
        print(f"Error fetching bottles: {e}")
        return None


def bottle_list() -> tuple[list[str], list[str]]:
    """Lists all bottles stored in the DynamoDB table."""
    try:
        bottles = bottles_table.scan().get("Items", [])
        if not bottles:
            return [], []
        return [bottle["bottle_name"] for bottle in bottles], [bottle["id"] for bottle in bottles]
    except Exception as e:
        print(f"Error fetching bottles: {e}")
        return [], []


def bottle_names_list():
    """Lists all bottle names stored in the DynamoDB table."""
    try:
        bottles = bottles_table.scan().get("Items", [])
        if not bottles:
            return []
        return [bottle["bottle_name"] for bottle in bottles]
    except Exception as e:
        print(f"Error fetching bottles: {e}")
        return "Error fetching bottles."


def bottle_add(name, user_id):
    """Adds a new bottle to the DynamoDB table."""
    # Generate a unique id for the bottle
    bottle_id = str(uuid.uuid4())

    # Construct the item to insert into DynamoDB
    item = {
        'id': bottle_id,
        'bottle_name': name,
        'user_id': user_id,  # Track which user added the bottle
        'added_at': int(time.time())  # Store the timestamp of when it was added
    }

    try:
        bottles_table.put_item(Item=item)
        return f"Bottle '{name}' added."
    except Exception as e:
        print(f"Error adding bottle: {e}")
        return "Error adding bottle."


def bottle_remove(bottle_id):
    """Removes a bottle from the DynamoDB table by id."""
    try:
        bottles_table.delete_item(Key={"id": bottle_id})
        return f"Bottle with id '{bottle_id}' removed."
    except Exception as e:
        print(f"Error removing bottle: {e}")
        return "Error removing bottle."


# -------------------------------------
# Admin Functions
# -------------------------------------

def admin_list():
    """Lists all admins stored in the DynamoDB table."""
    try:
        admins = admins_table.scan().get("Items", [])
        if not admins:
            return []
        return [admin["id"] for admin in admins]
    except Exception as e:
        print(f"Error fetching admins: {e}")
        return []


def admin_add(user_id):
    """Adds a new admin to the DynamoDB table."""
    try:
        admins_table.put_item(Item={"id": str(user_id)})
        return True
    except Exception as e:
        print(f"Error adding admin: {e}")
        return False


def admin_remove(user_id):
    """Removes an admin from the DynamoDB table by user ID."""
    try:
        admins_table.delete_item(Key={"id": str(user_id)})
        return f"Admin '{user_id}' removed."
    except Exception as e:
        print(f"Error removing admin: {e}")
        return "Error removing admin."


def is_admin(user_id):
    """Checks if a user is an admin by looking them up in the DynamoDB table."""
    try:
        admin = admins_table.get_item(Key={"id": str(user_id)}).get("Item")
        return bool(admin)
    except Exception as e:
        print(f"Error checking admin: {e}")
        return False
