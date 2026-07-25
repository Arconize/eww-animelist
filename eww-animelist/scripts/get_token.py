import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "..", "cache")

<<<<<<< HEAD
client_id = "9dd3de08b2d374a415acec85cb88fe49"
client_secret = "8930dd66db0bc023d372e57192f264d53b4d9f6c616a5b006bea85052cfa110e"
=======
client_id = "c118a6140671b5d99d4d01c7ba8e8cf3"
client_secret = "12086c66bb1e77f5e75d9807e9e2f8e067af7d13b05c5ebd0aaafe085be7b9d5"
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d

with open(os.path.join(CACHE_DIR, "code.txt"), "r") as f:
    code = f.read().strip()

with open(os.path.join(CACHE_DIR, "oauth.json"), "r") as f:
    oauth = json.load(f)

code_verifier = oauth["code_verifier"]

print("CLIENT:", client_id)
print("VERIFIER:", code_verifier)
print("REDIRECT:", "http://localhost:8000/callback")
print("CODE:", code[:40])

response = requests.post(
    "https://myanimelist.net/v1/oauth2/token",
    data={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:8000/callback",
        "code_verifier": code_verifier,
    },
    headers={
        "Content-Type": "application/x-www-form-urlencoded"
    }
)

print(response.status_code)

if response.status_code == 200:
    token_data = response.json()
    token_path = os.path.join(CACHE_DIR, "token.json")
    with open(token_path, "w") as f:
        json.dump(token_data, f, indent=2)
    print(f"Token saved to {token_path}")
else:
    print(response.text)
    raise SystemExit("Failed to get token, aborting.")
