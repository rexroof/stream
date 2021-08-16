#!/home/rex/.venv/redis/bin/python

import redis
import docker
import json
import subprocess

try:
    import gnureadline as readline
except ImportError:
    import readline

# find my redis port.
client = docker.APIClient(base_url="unix://var/run/docker.sock")
port_data = client.inspect_container("bot-redis")["NetworkSettings"]["Ports"]
redis_port = port_data["6379/tcp"][0]["HostPort"]
r = redis.Redis(host="localhost", port=redis_port, db=0)

points = json.loads(r.get("points"))

OPTIONS = [k for k, v in points.items()]


class SimpleCompleter:
    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text,
            # so build a match list.
            if text:
                self.matches = [
                    s for s in self.options if s and s.startswith(text.lower())
                ]
            else:
                self.matches = self.options[:]

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        return response


# Register the completer function
readline.set_completer(SimpleCompleter(OPTIONS).complete)

# Use the tab key for completion
readline.parse_and_bind("tab: complete")

# Prompt the user for text
chat_text = input("> ")


subprocess.run(["/home/rex/bin/chat-window.sh", "send", chat_text])
