#!/home/rex/.venv/redis/bin/python

import os
import sys
import requests
import pprint

pp = pprint.PrettyPrinter(indent=2)

SECRET = os.getenv("TWITCH_WEBHOOK_SECRET")
COUNT = 10

if len(sys.argv) > 1:
    COUNT = int(sys.argv[1])

# write function:
# tell it url to request, and the number of elements to print out.
# function will return number of items printed out and the "next" element


def rexy_events(url="", requested=0):
    response = requests.get(url, headers={"Authorization": f"Token {SECRET}"})
    printed = 0
    for e in response.json()["results"]:
        if requested <= 0:
            return printed, response.json()["next"]
        else:
            if e["origin"] == "twitch":
                requested -= 1
                _type = e["event_type"]

                if _type == "point-redemption":
                    _title = e["event_data"]["reward"]["title"]
                    _username = e["event_data"]["user_name"]
                    print(f"{_username} {_type} {_title}")
                elif _type == "follow":
                    _username = e["event_data"]["user_name"]
                    print(f"{_type} event {_username}")
                elif _type == "update":
                    _title = e["event_data"]["title"]
                    print(f"stream {_type} {_title}")
                elif _type == "subscribe":
                    _user = e["event_data"]["data"]["message"]["user_name"]
                    _msg = e["event_data"]["data"]["message"]["sub_message"]["message"]
                    print(f"{_type} {_user} {_msg}")
                else:
                    pp.pprint(e)
                printed += 1
            else:
                print(e)
    return printed, response.json()["next"]


event_url = "http://localhost:8000/api/v1/twitch-events"

while COUNT > 0:
    if event_url is not None:
        printed, event_url = rexy_events(url=event_url, requested=COUNT)
    else:
        COUNT = -1
    COUNT -= printed

# response_id = response.json()["data"][0]["id"]


# docker exec tau_db_1 psql -U tau_db -d tau_db -t \
#   -c "select event_data from twitchevents_twitchevent
# order by created desc limit ${LIMIT}" \
#   | jq -s 'map({user: .user_login, followed:.followed_at})'
#  # | jq -r '.user_name +" -> "+ .title +" "+ .reward.title'
