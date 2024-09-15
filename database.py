# Get environment variables
import os
import random

import boto3

DYNAMODB_BOTTLES_TABLE = os.environ.get("DYNAMODB_BOTTLES_TABLE")
DYNAMODB_ADMINS_TABLE = os.environ.get("DYNAMODB_ADMINS_TABLE")
DYNAMODB_GIFS_TABLE = os.environ.get("DYNAMODB_GIFS_TABLE")

dynamodb = boto3.resource("dynamodb")
bottles_table = dynamodb.Table(DYNAMODB_BOTTLES_TABLE)
admins_table = dynamodb.Table(DYNAMODB_ADMINS_TABLE)
gifs_table = dynamodb.Table(DYNAMODB_GIFS_TABLE)


def gif_random():
    try:
        gifs = gifs_table.scan().get("Items", [])
        if not gifs:
            return
        return random.choice(gifs)["url"]
    except Exception as e:
        print(f"Error fetching gifs: {e}")
        return None


def gif_list():
    try:
        gifs = gifs_table.scan().get("Items", [])
        if not gifs:
            return "No gifs saved."
        return "\n".join([gif["url"] for gif in gifs])
    except Exception as e:
        print(f"Error fetching gifs: {e}")
        return "Error fetching gifs."


def gif_add(url):
    try:
        gifs_table.put_item(Item={"url": url})
        return f"Gif '{url}' added."
    except Exception as e:
        print(f"Error adding gif: {e}")
        return "Error adding gif."


def gif_remove(url):
    try:
        gifs_table.delete_item(Key={"url": url})
        return f"Gif '{url}' removed."
    except Exception as e:
        print(f"Error removing gif: {e}")
        return "Error removing gif."


def bottle_random():
    try:
        bottles = bottles_table.scan().get("Items", [])
        if not bottles:
            return
        return random.choice(bottles)["name"]
    except Exception as e:
        print(f"Error fetching bottles: {e}")
        return None


def bottle_list():
    try:
        bottles = bottles_table.scan().get("Items", [])
        if not bottles:
            return "No bottles saved."
        return "\n".join([bottle["name"] for bottle in bottles])
    except Exception as e:
        print(f"Error fetching bottles: {e}")
        return "Error fetching bottles."


def bottle_add(name):
    try:
        bottles_table.put_item(Item={"name": name})
        return f"Bottle '{name}' added."
    except Exception as e:
        print(f"Error adding bottle: {e}")
        return "Error adding bottle."


def bottle_remove(name):
    try:
        bottles_table.delete_item(Key={"name": name})
        return f"Bottle '{name}' removed."
    except Exception as e:
        print(f"Error removing bottle: {e}")
        return "Error removing bottle."


def admin_list():
    try:
        admins = admins_table.scan().get("Items", [])
        if not admins:
            return "No admins saved."
        return "\n".join([admin["id"] for admin in admins])
    except Exception as e:
        print(f"Error fetching admins: {e}")
        return "Error fetching admins."


def admin_add(user_id):
    try:
        admins_table.put_item(Item={"id": user_id})
        return f"Admin '{user_id}' added."
    except Exception as e:
        print(f"Error adding admin: {e}")
        return "Error adding admin."


def admin_remove(user_id):
    try:
        admins_table.delete_item(Key={"id": user_id})
        return f"Admin '{user_id}' removed."
    except Exception as e:
        print(f"Error removing admin: {e}")
        return "Error removing admin."


def is_admin(user_id):
    try:
        admin = admins_table.get_item(Key={"id": user_id}).get("Item")
        return bool(admin)
    except Exception as e:
        print(f"Error checking admin: {e}")
        return False
