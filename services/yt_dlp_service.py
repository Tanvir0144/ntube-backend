import yt_dlp
from utils.helpers import build_ydl_opts

def _extract(url: str, opts: dict):
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)

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

def get_stream_links(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    info = _extract(url, build_ydl_opts(fmt="best"))
    streams = {}
    # Prefer muxed (video+audio)
    for f in info.get("formats", []):
        if not f.get("url"):
            continue
        vcodec = f.get("vcodec")
        acodec = f.get("acodec")
        note = f.get("format_note") or f.get("resolution") or f.get("format_id")
        if vcodec != "none" and acodec != "none" and note:
            # We only care about video streams here
            if "video" in f.get("format_note", "").lower() or vcodec != "none":
                if note not in streams:
                    streams[note] = f["url"]
            
        # Limit the number of streams to avoid too many options
        if len(streams) >= 6:
            break

    # Also add specific resolutions if not already captured
    for f in info.get("formats", []):
        if not f.get("url"):
            continue
        if f.get("ext") == "mp4": # Filter for mp4
            if f.get("height") == 720 and "720p" not in streams:
                streams["720p"] = f["url"]
            elif f.get("height") == 360 and "360p" not in streams:
                streams["360p"] = f["url"]

    # Best audio
    best_audio = next((f for f in info.get("formats", []) if f.get("vcodec") == "none" and f.get("acodec") != "none" and f.get("url")), None)
    if best_audio:
        streams["audio"] = best_audio["url"]
        
    # ✅ FIX: Return only the streams dictionary, not the title
    return streams

def get_download_link(video_id: str, kind: str = "video"):
    url = f"https://www.youtube.com/watch?v={video_id}"
    opts = build_ydl_opts(fmt=("bestaudio/best" if kind == "audio" else "best"))
    info = _extract(url, opts)
    return {"download_url": info.get("url")}
