import time
from typing import Optional, Any

class CacheService:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, max_size: int = 100):
        self._cache = {}
        self._access_times = {}
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        if time.time() > expiry:
            self._delete(key)
            return None
        
        self._access_times[key] = time.time()
        return value
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        if len(self._cache) >= self.max_size:
            self._evict_lru()
        
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)
        self._access_times[key] = time.time()
    
    def _delete(self, key: str):
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
    
    def _evict_lru(self):
        if not self._access_times:
            return
        
        lru_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        self._delete(lru_key)
    
    def clear(self):
        self._cache.clear()
        self._access_times.clear()