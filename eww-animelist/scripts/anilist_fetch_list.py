import sys
import json
import requests

if len(sys.argv) < 2:
    raise SystemExit("Usage: python3 anilist_fetch_list.py <anilist_username>")

username = sys.argv[1]

QUERY = """
query ($userName: String) {
  MediaListCollection(userName: $userName, type: ANIME) {
    lists {
      name
      entries {
        status
        progress
        score
        media {
          id
          title { romaji english }
          episodes
          coverImage { medium }
        }
      }
    }
  }
}
"""

response = requests.post(
    "https://graphql.anilist.co",
    json={"query": QUERY, "variables": {"userName": username}},
    headers={"Content-Type": "application/json", "Accept": "application/json"},
)

if response.status_code != 200:
    print(response.status_code)
    print(response.text)
    raise SystemExit(
        "Request failed. If this user's list is private, a username-only "
        "lookup won't work and you'd need the OAuth flow instead."
    )

with open("../cache/anilist_list.json", "w") as f:
    json.dump(response.json(), f, indent=2)

<<<<<<< HEAD
print(f"Saved {username}'s anime list to ../cache/anilist_list.json")
=======
print(f"Saved {username}'s anime list to ../cache/anilist_list.json")
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
