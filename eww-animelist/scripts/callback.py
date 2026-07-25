import os
import json
from flask import Flask, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "..", "cache")

app = Flask(__name__)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")

    with open(os.path.join(CACHE_DIR, "oauth.json"), "r") as f:
        oauth = json.load(f)

    if state != oauth["state"]:
        return "State mismatch"

    with open(os.path.join(CACHE_DIR, "code.txt"), "w") as f:
        f.write(code)

    print("Code saved!")
    return "Login successful, close this window."

app.run(host="localhost", port=8000)
