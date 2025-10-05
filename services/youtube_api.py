import os
import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException, HTTPError, Timeout

# ======================================================
# ✅ Load environment variables (safe for local + Render)
# ======================================================
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
REGION_CODE = os.getenv("REGION_CODE", "BD").strip()

if not YOUTUBE_API_KEY:
    raise RuntimeError("❌ Missing YOUTUBE_API_KEY in .env")

# 🌍 YouTube Data API base
BASE_URL = "https://www.googleapis.com/youtube/v3"


# ------------------------------------------------------
# 🔧 Helper: Safe request wrapper with retry + graceful fallback
# ------------------------------------------------------
def safe_request(url, params, retries=2):
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            return r.json()
        except HTTPError as e:
            print(f"⚠️ [YouTubeAPI] HTTP Error: {e} (Attempt {attempt+1}/{retries})")
        except Timeout:
            print(f"⚠️ [YouTubeAPI] Timeout — retrying ({attempt+1}/{retries})...")
        except RequestException as e:
            print(f"⚠️ [YouTubeAPI] Network error: {e}")
    return {"error": "Failed to fetch data from YouTube API"}


# ------------------------------------------------------
# 🔍 1️⃣ Search Videos
# ------------------------------------------------------
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

    data = safe_request(f"{BASE_URL}/search", params)
    if "error" in data:
        return {"results": [], "nextPageToken": None, "error": data["error"]}

    videos = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        videos.append({
            "id": item["id"].get("videoId", ""),
            "title": snippet.get("title", "No Title"),
            "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
            "channel": snippet.get("channelTitle", "Unknown Channel"),
            "duration": "N/A",
        })
    return {"results": videos, "nextPageToken": data.get("nextPageToken")}


# ------------------------------------------------------
# 🔥 2️⃣ Trending Videos
# ------------------------------------------------------
def yt_trending(region="BD", max_results=20, page_token=None):
    params = {
        "part": "snippet,contentDetails,statistics",
        "chart": "mostPopular",
        "regionCode": region or REGION_CODE,
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }
    if page_token:
        params["pageToken"] = page_token

    data = safe_request(f"{BASE_URL}/videos", params)
    if "error" in data:
        return {"trending": [], "nextPageToken": None, "error": data["error"]}

    videos = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        videos.append({
            "id": item.get("id", ""),
            "title": snippet.get("title", "No Title"),
            "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
            "channel": snippet.get("channelTitle", "Unknown Channel"),
            "duration": item.get("contentDetails", {}).get("duration", "N/A"),
            "views": item.get("statistics", {}).get("viewCount", "0"),
        })
    return {"trending": videos, "nextPageToken": data.get("nextPageToken")}


# ------------------------------------------------------
# 🔁 3️⃣ Related Videos
# ------------------------------------------------------
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

    data = safe_request(f"{BASE_URL}/search", params)
    if "error" in data:
        return {"related": [], "nextPageToken": None, "error": data["error"]}

    videos = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        videos.append({
            "id": item["id"].get("videoId", ""),
            "title": snippet.get("title", "No Title"),
            "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
            "channel": snippet.get("channelTitle", "Unknown Channel"),
            "duration": "N/A",
        })
    return {"related": videos, "nextPageToken": data.get("nextPageToken")}


# ------------------------------------------------------
# 💡 4️⃣ Search Suggestions (no API key required)
# ------------------------------------------------------
def yt_suggest(query):
    try:
        from urllib.parse import quote
        url = f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={quote(query)}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()[1]
    except Exception as e:
        print(f"⚠️ [yt_suggest] {e}")
    return []
