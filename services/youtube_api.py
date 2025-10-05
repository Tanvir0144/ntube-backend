import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_KEY = os.getenv("YOUTUBE_API_KEY", "")
if not API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY missing in .env or environment")

youtube = build("youtube", "v3", developerKey=API_KEY, cache_discovery=False)

def _norm_item_snippet(it):
    snip = it["snippet"]
    return {
        "id": it["id"]["videoId"],
        "title": snip["title"],
        "thumbnail": snip["thumbnails"]["high"]["url"],
        "channel": snip["channelTitle"],
        "publishedAt": snip["publishedAt"],
    }

def yt_search(query: str, max_results: int = 20, page_token: str | None = None):
    try:
        res = youtube.search().list(
            q=query, part="snippet", type="video", maxResults=max_results,
            pageToken=page_token or None, safeSearch="none"
        ).execute()
        items = [_norm_item_snippet(it) for it in res.get("items", []) if it["id"].get("videoId")]
        return {"results": items, "nextPageToken": res.get("nextPageToken"), "prevPageToken": res.get("prevPageToken")}
    except HttpError as e:
        raise RuntimeError(f"Search error: {e}")

def yt_trending(region: str = "BD", max_results: int = 20, page_token: str | None = None):
    try:
        res = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            chart="mostPopular",
            regionCode=region,
            maxResults=max_results,
            pageToken=page_token or None,
        ).execute()
        items = [{
            "id": it["id"],
            "title": it["snippet"]["title"],
            "thumbnail": it["snippet"]["thumbnails"]["high"]["url"],
            "channel": it["snippet"]["channelTitle"],
            "publishedAt": it["snippet"]["publishedAt"],
            "views": it.get("statistics", {}).get("viewCount"),
        } for it in res.get("items", []) if it.get("id")]
        return {"region": region, "results": items, "nextPageToken": res.get("nextPageToken"), "prevPageToken": res.get("prevPageToken")}
    except HttpError as e:
        raise RuntimeError(f"Trending error: {e}")

def yt_related(video_id: str, max_results: int = 20, page_token: str | None = None):
    try:
        res = youtube.search().list(
            part="snippet",
            relatedToVideoId=video_id,
            type="video",
            maxResults=max_results,
            pageToken=page_token or None,
            safeSearch="none",
        ).execute()
        items = [_norm_item_snippet(it) for it in res.get("items", []) if it["id"].get("videoId")]
        return {"videoId": video_id, "results": items, "nextPageToken": res.get("nextPageToken"), "prevPageToken": res.get("prevPageToken")}
    except HttpError as e:
        raise RuntimeError(f"Related error: {e}")

def yt_suggest(q: str) -> list[str]:
    # Lightweight suggest: search titles → unique best-matching phrases
    res = youtube.search().list(q=q, part="snippet", type="video", maxResults=10, safeSearch="none").execute()
    titles = [it["snippet"]["title"] for it in res.get("items", [])]
    # Build simple suggestions list from titles + base variants
    base = q.strip()
    suffixes = [" tutorial", " bangla", " 2025", " best", " latest", " how to", " official", " review"]
    cand = [base + s for s in suffixes] + titles
    # unique keep order
    seen, out = set(), []
    for t in cand:
        k = t.strip()
        if k and k.lower() not in seen:
            seen.add(k.lower())
            out.append(k)
        if len(out) >= 12:
            break
    return out
