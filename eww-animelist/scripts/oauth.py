import os
import secrets
import hashlib
import base64
import webbrowser
import json
from urllib.parse import urlencode
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "..", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

load_dotenv()

<<<<<<< HEAD
client_id = "9dd3de08b2d374a415acec85cb88fe49"
=======
client_id = "c118a6140671b5d99d4d01c7ba8e8cf3"
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d

code_verifier = secrets.token_urlsafe(64)
code_challenge = code_verifier  # MAL فقط از plain پشتیبانی می‌کند

state = secrets.token_urlsafe(16)

with open(os.path.join(CACHE_DIR, "oauth.json"), "w") as f:
    json.dump({
        "state": state,
        "code_verifier": code_verifier
    }, f)

params = {
    "response_type": "code",
    "client_id": client_id,
    "redirect_uri": "http://localhost:8000/callback",
    "state": state,
    "code_challenge": code_challenge,
    "code_challenge_method": "plain",
}

url = "https://myanimelist.net/v1/oauth2/authorize?" + urlencode(params)

print("VERIFIER:", code_verifier)
print("CHALLENGE:", code_challenge)
print(url)

webbrowser.open(url)
