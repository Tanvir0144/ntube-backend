import os
import yt_dlp

# ✅ Helper for yt_dlp configuration
def build_ydl_opts(fmt="best", skip_download=False):
    opts = {
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "source_address": "0.0.0.0",
        "extract_flat": False,
        "format": fmt,
        "skip_download": skip_download,
    }

    # ✅ Use local cookie file to prevent 429 errors
    cookies_path = os.path.join(os.path.dirname(__file__), "..", "youtube.com_cookies.txt")
    if os.path.exists(cookies_path):
        opts["cookiefile"] = cookies_path
        print("🍪 Using cookies.txt for yt-dlp session")

    return opts


# ✅ Core extractor
def _extract(url: str, opts: dict):
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)


# ℹ️ Get video info
def get_video_info(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    info = _extract(url, build_ydl_opts(skip_download=True))
    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "uploader": info.get("uploader") or info.get("channel"),
    }


# ▶️ Get stream links (video/audio)
def get_stream_links(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    info = _extract(url, build_ydl_opts(fmt="best"))
    streams = {}

    # ✅ Prefer muxed (video+audio)
    for f in info.get("formats", []):
        if not f.get("url"):
            continue
        vcodec = f.get("vcodec")
        acodec = f.get("acodec")
        note = f.get("format_note") or f.get("resolution") or f.get("format_id")
        if vcodec != "none" and acodec != "none" and note:
            if note not in streams:
                streams[note] = f["url"]
        if len(streams) >= 6:
            break

    # 🎵 Best audio-only stream
    best_audio = next(
        (f for f in info.get("formats", []) if f.get("vcodec") == "none" and f.get("acodec") != "none" and f.get("url")),
        None
    )
    if best_audio:
        streams["audio"] = best_audio["url"]

    return {"title": info.get("title"), "streams": streams}


# ⬇️ Direct download URL
def get_download_link(video_id: str, kind: str = "video"):
    url = f"https://www.youtube.com/watch?v={video_id}"
    opts = build_ydl_opts(fmt=("bestaudio/best" if kind == "audio" else "best"))
    info = _extract(url, opts)
    return {"download_url": info.get("url")}
