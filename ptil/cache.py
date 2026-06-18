from collections import OrderedDict
from typing import Optional, Any, List
from dataclasses import dataclass, field
import time


@dataclass
class CacheEntry:
    value: Any
    expiry: float


class LRUCache:
    def __init__(self, capacity: int = 512, ttl_seconds: int = 3600):
        self._capacity = capacity
        self._ttl = ttl_seconds
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        entry = self._cache[key]
        if time.time() > entry.expiry:
            del self._cache[key]
            return None
        self._cache.move_to_end(key)
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        if len(self._cache) >= self._capacity:
            self._cache.popitem(last=False)
        self._cache[key] = CacheEntry(value, time.time() + (ttl or self._ttl))
        self._cache.move_to_end(key)

    def invalidate(self, key: str):
        self._cache.pop(key, None)

    def clear(self):
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)

    def keys(self) -> List[str]:
        return list(self._cache.keys())
