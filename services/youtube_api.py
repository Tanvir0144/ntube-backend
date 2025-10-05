import os
import requests
from dotenv import load_dotenv

# ✅ Load environment variables (for local + Render)
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
REGION_CODE = os.getenv("REGION_CODE", "BD").strip()
COOKIES_B64 = os.getenv("COOKIES_B64", "").strip()

if not YOUTUBE_API_KEY:
    print("⚠️ [WARN] YOUTUBE_API_KEY not found in environment!")
    raise RuntimeError("YOUTUBE_API_KEY missing in .env or environment")

# -------------------------------
# 🌎 YouTube Data API base
# -------------------------------
BASE_URL = "https://www.googleapis.com/youtube/v3"

# 🔍 Search videos
def yt_search(q, max_results=20, page_token=None):
    params = {
        "part": "snippet",
        "q": q,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }
    if page_token:
        params["pageToken"] = page_token
    res = requests.get(f"{BASE_URL}/search", params=params)
    res.raise_for_status()
    return res.json()

# 🔥 Trending videos
def yt_trending(region="BD", max_results=20, page_token=None):
    params = {
        "part": "snippet,contentDetails,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }
    if page_token:
        params["pageToken"] = page_token
    res = requests.get(f"{BASE_URL}/videos", params=params)
    res.raise_for_status()
    return res.json()

# 🎬 Related videos
def yt_related(video_id, max_results=20, page_token=None):
    params = {
        "part": "snippet",
        "type": "video",
        "relatedToVideoId": video_id,
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }
    if page_token:
        params["pageToken"] = page_token
    res = requests.get(f"{BASE_URL}/search", params=params)
    res.raise_for_status()
    return res.json()

# 💡 Search suggestion (simple)
def yt_suggest(query):
    try:
        from urllib.parse import quote
        url = f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={quote(query)}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()[1]
    except Exception as e:
        print(f"[yt_suggest] Error: {e}")
    return []
