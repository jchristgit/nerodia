import json

from poller import client


def get_user_id(user_name: str) -> int:
    with open("nerodia.json", 'r') as f:
        data = json.load(f)

    if user_name in data["users"]:
        return data["users"][user_name]

    user_id = client.users.translate_usernames_to_ids([user_name])[0]
    data["users"][user_name] = user_id
    with open("nerodia.json", 'r') as f:
        json.dump(data, f, sort_keys=True, indent=4)
    return user_id


def all_follows() -> list:
    with open("nerodia.json", 'r') as f:
        return json.load(f)["follows"]


def follow_stream(stream_name: str):
    with open("nerodia.json", 'r') as f:
        data = json.load(f)
        data["follows"].append(stream_name)
        json.dump(data, f, sort_keys=True, indent=4)


def unfollow_stream(stream_name: str):
    with open("nerodia.json", 'r') as f:
        data = json.load(f)
        data["follows"].remove(stream_name)
        json.dump(data, f, sort_keys=True, indent=4)
