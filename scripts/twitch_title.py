#!/home/rex/.venv/redis/bin/python

import os
import requests

SECRET = os.getenv("TWITCH_WEBHOOK_SECRET")

try:
    import gnureadline as readline
except ImportError:
    import readline

response = requests.get(
    "http://localhost:8000/api/twitch/helix/users",
    headers={"Authorization": f"Token {SECRET}"},
)
response_id = response.json()["data"][0]["id"]

response = requests.get(
    f"http://localhost:8000/api/twitch/helix/channels?broadcaster_id={response_id}",
    headers={"Authorization": f"Token {SECRET}"},
)
response_title = response.json()["data"][0]["title"]

# Use the tab key for completion
readline.parse_and_bind("tab: complete")

# prefill with previous title
readline.set_startup_hook(lambda: readline.insert_text(response_title))

# Prompt the user for text
chat_text = input("> ")

response = requests.patch(
    f"http://localhost:8000/api/twitch/helix/channels?broadcaster_id={response_id}",
    headers={"Authorization": f"Token {SECRET}"},
    data=[("title", chat_text)],
)
