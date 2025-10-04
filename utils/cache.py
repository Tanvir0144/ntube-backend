import time, threading

_CACHE: dict[str, dict] = {}
_DEFAULT_TTL = 600
_LIMIT = 800  # generous for 2-year scale on free tier

def cache_get(key: str):
    it = _CACHE.get(key)
    if not it: return None
    if it["exp"] < time.time():
        _CACHE.pop(key, None)
        return None
    return it["val"]

def cache_set(key: str, val, ttl: int = _DEFAULT_TTL):
    # Evict if over limit (oldest 10%)
    if len(_CACHE) >= _LIMIT:
        for k, _ in sorted(_CACHE.items(), key=lambda x: x[1]["exp"])[: max(1, _LIMIT // 10)]:
            _CACHE.pop(k, None)
    _CACHE[key] = {"val": val, "exp": time.time() + ttl}

def cache_stats():
    alive = sum(1 for v in _CACHE.values() if v["exp"] >= time.time())
    return {"size": len(_CACHE), "alive": alive, "limit": _LIMIT, "ttl_default": _DEFAULT_TTL}

def cache_cleanup_job():
    while True:
        now = time.time()
        expired = [k for k, v in _CACHE.items() if v["exp"] < now]
        for k in expired:
            _CACHE.pop(k, None)
        time.sleep(60)
