# FIXME: DELETE ME
import json
from typing import Optional

from .clients import twitch


def stream_exists(name: str) -> bool:
    return bool(twitch.users.translate_usernames_to_ids(name))


def get_user_id(user_name: str) -> Optional[str]:
    with open("data/nerodia.json", 'r') as f:
        data = json.load(f)

    if user_name in data["users"]:
        return data["users"][user_name]

    users = twitch.users.translate_usernames_to_ids(user_name)
    if not users:
        return None
    user = users[0]
    data["users"][user["name"]] = user['id']
    with open("data/nerodia.json", 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)
    return user['id']


def all_follows() -> list:
    with open("data/nerodia.json", 'r') as f:
        return json.load(f)["follows"]


def follow_stream(stream_name: str):
    with open("data/nerodia.json", 'r') as f:
        data = json.load(f)

    correct_casing = twitch.users.translate_usernames_to_ids(stream_name)

    data["follows"].append(correct_casing[0]["name"])
    with open("nerodia.json", 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)


def unfollow_stream(stream_name: str):
    with open("nerodia.json", 'r') as f:
        data = json.load(f)

    data["follows"].remove(stream_name)
    with open("nerodia.json", 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)
