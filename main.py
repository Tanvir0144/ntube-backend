# ======================================================
# ✅ Auto-load environment variables safely from .env
# ======================================================
from dotenv import load_dotenv
import os, time, threading

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)
# ======================================================

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from services.youtube_api import yt_search, yt_trending, yt_related, yt_suggest
from services.yt_dlp_service import get_stream_links, get_download_link, get_video_info
from utils.cache import cache_get, cache_set, cache_stats, cache_cleanup_job
from utils.helpers import RateLimiter

# 🔧 App version
APP_VERSION = "3.2"

# 🚀 FastAPI App
app = FastAPI(title="NTUBE Ultra Backend", version=APP_VERSION)

# 🌍 CORS (Flutter/web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚡ Global rate limit: 60 req/min/IP
limiter = RateLimiter(rate=60, per_seconds=60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    if not limiter.allow(ip):
        raise HTTPException(status_code=429, detail="Too Many Requests")
    return await call_next(request)

# ♻️ Background cache cleanup thread
threading.Thread(target=cache_cleanup_job, daemon=True).start()

# 🏠 Root endpoint
@app.get("/")
def root():
    return {
        "message": "✅ NTUBE Ultra Backend OK",
        "version": APP_VERSION,
        "cache": cache_stats(),
    }

# 🔎 Search (YouTube API + pagination)
@app.get("/search")
def search(
    q: str = Query(..., min_length=1),
    max_results: int = Query(20, ge=1, le=50),
    page_token: str | None = None,
):
    try:
        key = f"search:{q}:{max_results}:{page_token or ''}"
        hit = cache_get(key)
        if hit:
            return hit
        data = yt_search(q, max_results=max_results, page_token=page_token)
        cache_set(key, data, ttl=600)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🏠 Trending (infinite scroll via pageToken)
@app.get("/trending")
def trending(
    region: str = os.getenv("REGION_CODE", "BD"),
    max_results: int = Query(20, ge=1, le=50),
    page_token: str | None = None,
):
    try:
        key = f"trending:{region}:{max_results}:{page_token or ''}"
        hit = cache_get(key)
        if hit:
            return hit
        data = yt_trending(region, max_results=max_results, page_token=page_token)
        cache_set(key, data, ttl=900)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔁 Related feed (YouTube-like “Up next”)
@app.get("/related")
def related(video_id: str, max_results: int = Query(20, ge=1, le=50), page_token: str | None = None):
    try:
        key = f"related:{video_id}:{max_results}:{page_token or ''}"
        hit = cache_get(key)
        if hit:
            return hit
        data = yt_related(video_id, max_results=max_results, page_token=page_token)
        cache_set(key, data, ttl=900)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✍️ Search suggestions (fast, cached)
@app.get("/suggest")
def suggest(q: str = Query(..., min_length=1)):
    try:
        key = f"suggest:{q}"
        hit = cache_get(key)
        if hit:
            return hit
        data = {"query": q, "suggestions": yt_suggest(q)}
        cache_set(key, data, ttl=1800)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ℹ️ Video info via yt-dlp
@app.get("/info")
def info(video_id: str):
    try:
        key = f"info:{video_id}"
        hit = cache_get(key)
        if hit:
            return hit
        data = get_video_info(video_id)
        cache_set(key, data, ttl=1800)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ▶️ Stream links (yt-dlp, cached)
@app.get("/stream")
def stream(video_id: str):
    try:
        key = f"stream:{video_id}"
        hit = cache_get(key)
        if hit:
            return hit
        data = get_stream_links(video_id)
        cache_set(key, data, ttl=600)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ⬇️ Download link (audio/video)
@app.get("/download")
def download(video_id: str, type: str = Query("video", pattern="^(video|audio)$")):
    try:
        return get_download_link(video_id, kind=type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ❤️ Health check (for Render / uptime monitor)
@app.api_route("/health", methods=["GET", "HEAD"])
def health(_: Request):
    return {"status": "ok", "ts": time.time(), "cache": cache_stats()}
