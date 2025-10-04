import os, base64

def _decode_cookies_to_file() -> str | None:
    b64 = os.getenv("COOKIES_B64")
    if not b64: return None
    try:
        data = base64.b64decode(b64).decode("utf-8")
        with open("cookies.txt", "w", encoding="utf-8") as f:
            f.write(data)
        return "cookies.txt"
    except Exception as e:
        print("Cookie decode error:", e)
        return None

def build_ydl_opts(fmt: str | None = None, skip_download: bool = False):
    opts = {
        "quiet": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "retries": 3,
        "extractor_retries": 2,
        "cachedir": False,
        "source_address": "0.0.0.0",
    }
    if fmt: opts["format"] = fmt
    if skip_download: opts["skip_download"] = True
    cookiefile = _decode_cookies_to_file()
    if cookiefile: opts["cookiefile"] = cookiefile
    return opts

# Token-bucket limiter
class RateLimiter:
    def __init__(self, rate: int, per_seconds: int):
        self.rate = rate
        self.per = per_seconds
        self.bucket = {}  # ip -> (tokens, last_ts)

    def allow(self, ip: str) -> bool:
        import time
        now = time.time()
        tokens, last = self.bucket.get(ip, (self.rate, now))
        tokens = min(self.rate, tokens + (now - last) * (self.rate / self.per))
        if tokens < 1:
            self.bucket[ip] = (tokens, now)
            return False
        tokens -= 1
        self.bucket[ip] = (tokens, now)
        return True
