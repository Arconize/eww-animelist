import os
import json
import argparse
<<<<<<< HEAD
import time
=======
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "..", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
CLIENT_ID = "9dd3de08b2d374a415acec85cb88fe49"
CLIENT_SECRET = "8930dd66db0bc023d372e57192f264d53b4d9f6c616a5b006bea85052cfa110e"
TOKEN_FILE = os.path.join(CACHE_DIR, "token.json")
SEEN_FILE = os.path.join(CACHE_DIR, "seen_episodes.json")
OUTPUT_FILE = os.path.join(CACHE_DIR, "anime_widget.json")
ANILIST_LIST_FILE = os.path.join(CACHE_DIR, "anilist_list.json")  # [NEW]
CORNER_RADIUS = 10
def refresh_access_token():
    with open(TOKEN_FILE) as f:
        tok = json.load(f)
    resp = requests.post("https://myanimelist.net/v1/oauth2/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": tok["refresh_token"],
    })
    resp.raise_for_status()
    new_tok = resp.json()
    with open(TOKEN_FILE, "w") as f:
        json.dump(new_tok, f)
    return new_tok["access_token"]
def get_watching_list(access_token):
    url = "https://api.myanimelist.net/v2/users/@me/animelist"
    params = {
        "status": "watching",
        "fields": "alternative_titles,main_picture,list_status",
        "limit": 100,
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json()["data"]
def get_anilist_info(mal_id):
    query = """
    query ($id: Int) {
      Media(idMal: $id, type: ANIME) {
        title { romaji english }
        coverImage { large }
        status
        episodes
<<<<<<< HEAD
        averageScore
=======
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
        nextAiringEpisode { airingAt episode timeUntilAiring }
      }
    }
    """
<<<<<<< HEAD
    try:  # [NEW] AniList can rate-limit/reset the connection mid-loop
        r = requests.post(
            "https://graphql.anilist.co",
            json={"query": query, "variables": {"id": mal_id}},
            timeout=15,
        )
    except requests.exceptions.RequestException:  # [NEW]
        return None  # [NEW]
    finally:
        time.sleep(1)  # [NEW] stay well under AniList's ~30 req/min limit
=======
    r = requests.post(
        "https://graphql.anilist.co",
        json={"query": query, "variables": {"id": mal_id}},
    )
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
    if r.status_code != 200:
        return None
    return r.json().get("data", {}).get("Media")
# [NEW] same lookup, but by AniList's own media id instead of a MAL id
def get_anilist_info_by_id(anilist_id):
    query = """
    query ($id: Int) {
      Media(id: $id, type: ANIME) {
        title { romaji english }
        coverImage { large }
        status
        episodes
<<<<<<< HEAD
        averageScore
=======
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
        nextAiringEpisode { airingAt episode timeUntilAiring }
      }
    }
    """
<<<<<<< HEAD
    try:  # [NEW] AniList can rate-limit/reset the connection mid-loop
        r = requests.post(
            "https://graphql.anilist.co",
            json={"query": query, "variables": {"id": anilist_id}},
            timeout=15,
        )
    except requests.exceptions.RequestException:  # [NEW]
        return None  # [NEW]
    finally:
        time.sleep(1)  # [NEW] stay well under AniList's ~30 req/min limit
=======
    r = requests.post(
        "https://graphql.anilist.co",
        json={"query": query, "variables": {"id": anilist_id}},
    )
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
    if r.status_code != 200:
        return None
    return r.json().get("data", {}).get("Media")
# [NEW] reads the file anilist_fetch_list.py already wrote, no network needed
def get_anilist_watching_list():
    with open(ANILIST_LIST_FILE) as f:
        data = json.load(f)
    entries = []
    for lst in data["data"]["MediaListCollection"]["lists"]:
        for entry in lst["entries"]:
            if entry.get("status") == "CURRENT":
                entries.append(entry)
    return entries
def format_countdown(seconds):
    if seconds <= 0:
        return "Released"
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    if days > 0:
        return f"{days}d {hours:02}h {minutes:02}m"
    elif hours > 0:
        return f"{hours}h {minutes:02}m"
    else:
        return f"{minutes}m"
<<<<<<< HEAD
# [NEW] fraction (0-100) of the way through the current airing gap, for the progress bar
def compute_progress_pct(seconds_left, typical_interval=7 * 24 * 3600):
    if seconds_left is None:
        return 0
    elapsed = typical_interval - seconds_left
    pct = round((elapsed / typical_interval) * 100)
    return max(0, min(100, pct))
=======
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
def notify(title, episode):
    os.system(f'notify-send "🎬 {title}" "قسمت {episode} پخش شد!"')
    os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga &')
def download_cover(url, mal_id, radius=CORNER_RADIUS):
    covers_dir = os.path.join(CACHE_DIR, "covers")
    os.makedirs(covers_dir, exist_ok=True)
    # .png, since rounded corners need real transparency (jpg can't do alpha)
    path = os.path.join(covers_dir, f"{mal_id}.png")
    if not os.path.exists(path):
        r = requests.get(url)
        r.raise_for_status()
        tmp = os.path.join(covers_dir, f"{mal_id}_tmp.jpg")
        with open(tmp, "wb") as f:
            f.write(r.content)
        img = Image.open(tmp).convert("RGBA").resize((60, 80))
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
        img.putalpha(mask)
        img.save(path, "PNG")
        os.remove(tmp)
    return path
# [NEW]
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--source", choices=["mal", "anilist"], default="mal")
    p.add_argument("--username")
    return p.parse_args()
# [NEW] AniList path — separate from the MyAnimeList flow below
def main_anilist():
    entries = get_anilist_watching_list()
    seen = {}
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            seen = json.load(f)
    output = []
    for entry in entries:
        media = entry["media"]
        anilist_id = media["id"]
        title = media["title"].get("english") or media["title"].get("romaji")
        cover_url = media["coverImage"]["medium"]
        watched = entry.get("progress", 0)
        cover_path = download_cover(cover_url, anilist_id)
        info = get_anilist_info_by_id(anilist_id)
        if not info:
            continue
        next_ep = info.get("nextAiringEpisode")
        if next_ep:
            seconds_left = next_ep["timeUntilAiring"]
            episode_num = next_ep["episode"]
            countdown = format_countdown(seconds_left)
<<<<<<< HEAD
            progress_pct = compute_progress_pct(seconds_left)  # [NEW]
=======
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
            if seconds_left <= 0 and seen.get(str(anilist_id)) != episode_num:
                notify(title, episode_num)
                seen[str(anilist_id)] = episode_num
        elif info.get("status") == "FINISHED" and info.get("episodes"):
            episode_num = info["episodes"]
            countdown = "Finished"
<<<<<<< HEAD
            progress_pct = 100  # [NEW]
        else:
            episode_num = "?"
            countdown = "N/A"
            progress_pct = 0  # [NEW]
=======
        else:
            episode_num = "?"
            countdown = "N/A"
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
        output.append({
            "title": title,
            "cover": cover_path,
            "next_episode": episode_num,
            "watched": watched,
            "countdown": countdown,
<<<<<<< HEAD
            "progress_pct": progress_pct,          # [NEW]
            "my_score": entry.get("score") or 0,     # [NEW]
            "overall_score": round((info.get("averageScore") or 0) / 10, 1),  # [NEW]
            "url": f"https://anilist.co/anime/{anilist_id}",  # [NEW]
=======
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
        })
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
def main():
    args = parse_args()  # [NEW]
    if args.source == "anilist":  # [NEW]
        main_anilist()            # [NEW]
        return                    # [NEW]
#    os.system("rm ~/.config/eww/eww-amimelist/cache/covers/*")
    access_token = refresh_access_token()
    watching = get_watching_list(access_token)
    seen = {}
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            seen = json.load(f)
    output = []
    for item in watching:
        node = item["node"]
        mal_id = node["id"]
        title = node["alternative_titles"].get("en") or node["title"]
        cover_url = node["main_picture"]["large"]
        watched = item.get("list_status", {}).get("num_episodes_watched", 0)
        cover_path = download_cover(cover_url, mal_id)
        info = get_anilist_info(mal_id)
        if not info:
            continue
        next_ep = info.get("nextAiringEpisode")
        if next_ep:
            seconds_left = next_ep["timeUntilAiring"]
            episode_num = next_ep["episode"]
            countdown = format_countdown(seconds_left)
<<<<<<< HEAD
            progress_pct = compute_progress_pct(seconds_left)  # [NEW]
=======
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
            if seconds_left <= 0 and seen.get(str(mal_id)) != episode_num:
                notify(title, episode_num)
                seen[str(mal_id)] = episode_num
        elif info.get("status") == "FINISHED" and info.get("episodes"):
            episode_num = info["episodes"]
            countdown = "Finished"
<<<<<<< HEAD
            progress_pct = 100  # [NEW]
        else:
            episode_num = "?"
            countdown = "N/A"
            progress_pct = 0  # [NEW]
=======
        else:
            episode_num = "?"
            countdown = "N/A"
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
        output.append({
            "title": title,
            "cover": cover_path,
            "next_episode": episode_num,
            "watched": watched,
            "countdown": countdown,
<<<<<<< HEAD
            "progress_pct": progress_pct,  # [NEW]
            "my_score": item.get("list_status", {}).get("score") or 0,  # [NEW]
            "overall_score": round((info.get("averageScore") or 0) / 10, 1),  # [NEW]
            "url": f"https://myanimelist.net/anime/{mal_id}",  # [NEW]
=======
>>>>>>> e50ba7b1b60aea4547d1ec577ce85ef9c1cd3c5d
        })
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
if __name__ == "__main__":
    main()
