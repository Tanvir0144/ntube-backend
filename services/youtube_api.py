import os
import requests
from dotenv import load_dotenv

# ✅ Load .env values (Render + Local)
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
REGION_CODE = os.getenv("REGION_CODE", "BD").strip()

if not YOUTUBE_API_KEY:
    print("⚠️ [WARN] YOUTUBE_API_KEY not found!")
    raise RuntimeError("YOUTUBE_API_KEY missing in .env or environment")

# 🌎 Base URL
BASE_URL = "https://www.googleapis.com/youtube/v3"

# 🔍 Search videos
def yt_search(q, max_results=20, page_token=None):
    params = {
        "part": "snippet",
        "q": q,
        "type": "video",
        "maxResults": max_results,
        "regionCode": REGION_CODE,
        "safeSearch": "none",
        "key": YOUTUBE_API_KEY,
    }
    if page_token:
        params["pageToken"] = page_token
    res = requests.get(f"{BASE_URL}/search", params=params, timeout=10)
    res.raise_for_status()
    return res.json()

# 🔥 Trending videos
def yt_trending(region="BD", max_results=20, page_token=None):
    params = {
        "part": "snippet,contentDetails,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results,
        "safeSearch": "none",
        "key": YOUTUBE_API_KEY,
    }
    if page_token:
        params["pageToken"] = page_token
    res = requests.get(f"{BASE_URL}/videos", params=params, timeout=10)
    res.raise_for_status()
    return res.json()

# 🎬 Related videos (✅ FIXED 400 Error)
def yt_related(video_id, max_results=20, page_token=None):
    params = {
        "part": "snippet",
        "type": "video",
        "relatedToVideoId": video_id,
        "maxResults": max_results,
        "safeSearch": "none",
        "key": YOUTUBE_API_KEY,
    }
    if page_token:
        params["pageToken"] = page_token
    try:
        res = requests.get(f"{BASE_URL}/search", params=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ [YouTubeAPI] Related videos fetch failed: {e}")
        return {"results": []}

# 💡 Search suggestions (for autocomplete)
def yt_suggest(query):
    from urllib.parse import quote
    try:
        url = f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={quote(query)}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()[1]
    except Exception as e:
        print(f"⚠️ [yt_suggest] {e}")
    return []
