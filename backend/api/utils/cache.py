"""
Simple In-Memory Cache
Replaces Redis for FREE Azure deployment

Note: This is a basic in-memory cache that loses data on app restart.
For production with multiple instances, consider Azure Cache for Redis
or Azure Table Storage.
"""
import time
from typing import Any, Optional, Dict
from threading import Lock
import structlog

logger = structlog.get_logger()


class InMemoryCache:
    """
    Thread-safe in-memory cache with TTL support

    Features:
    - Thread-safe operations
    - TTL (time-to-live) support
    - LRU eviction when max size reached
    - Simple get/set/delete interface compatible with Redis

    Limitations:
    - Data lost on restart
    - Single instance only (doesn't work across multiple function instances)
    - No persistence
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize cache

        Args:
            max_size: Maximum number of items to store
            default_ttl: Default time-to-live in seconds
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._access_order: Dict[str, float] = {}  # For LRU

        logger.info("in_memory_cache_initialized", max_size=max_size, default_ttl=default_ttl)

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                return None

            item = self._cache[key]

            # Check if expired
            if item["expires_at"] and time.time() > item["expires_at"]:
                del self._cache[key]
                if key in self._access_order:
                    del self._access_order[key]
                return None

            # Update access time for LRU
            self._access_order[key] = time.time()

            return item["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)

        Returns:
            True if successful
        """
        with self._lock:
            # Evict if at max size
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()

            ttl = ttl if ttl is not None else self.default_ttl
            expires_at = time.time() + ttl if ttl > 0 else None

            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time()
            }

            self._access_order[key] = time.time()

            return True

    def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_order:
                    del self._access_order[key]
                return True
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache

        Args:
            key: Cache key

        Returns:
            True if key exists and not expired
        """
        return self.get(key) is not None

    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            logger.info("cache_cleared")

    def _evict_lru(self):
        """Evict least recently used item"""
        if not self._access_order:
            return

        # Find least recently accessed key
        lru_key = min(self._access_order, key=self._access_order.get)

        # Remove from cache
        if lru_key in self._cache:
            del self._cache[lru_key]
        if lru_key in self._access_order:
            del self._access_order[lru_key]

        logger.debug("cache_evicted_lru", key=lru_key)

    def cleanup_expired(self):
        """Remove all expired items"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, item in self._cache.items()
                if item["expires_at"] and current_time > item["expires_at"]
            ]

            for key in expired_keys:
                del self._cache[key]
                if key in self._access_order:
                    del self._access_order[key]

            if expired_keys:
                logger.info("cache_cleanup", expired_count=len(expired_keys))

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "utilization": len(self._cache) / self.max_size if self.max_size > 0 else 0
            }


# Singleton instance
_cache: Optional[InMemoryCache] = None


def get_cache() -> InMemoryCache:
    """
    Get or create the cache singleton

    Returns:
        InMemoryCache instance
    """
    global _cache

    if _cache is None:
        _cache = InMemoryCache(
            max_size=1000,  # Store up to 1000 items
            default_ttl=3600  # 1 hour default TTL
        )

    return _cache


# Helper functions for common cache patterns
def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    return get_cache().get(key)


def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in cache"""
    return get_cache().set(key, value, ttl)


def cache_delete(key: str) -> bool:
    """Delete key from cache"""
    return get_cache().delete(key)


def cache_clear():
    """Clear all cache"""
    get_cache().clear()


if __name__ == "__main__":
    # Test cache
    cache = get_cache()

    # Test basic operations
    cache.set("test_key", "test_value")
    print(f"Get: {cache.get('test_key')}")  # Should print: test_value

    # Test TTL
    cache.set("expire_key", "will_expire", ttl=1)
    print(f"Before expiry: {cache.get('expire_key')}")  # Should print: will_expire
    time.sleep(2)
    print(f"After expiry: {cache.get('expire_key')}")  # Should print: None

    # Test stats
    print(f"Stats: {cache.get_stats()}")

    print("✅ Cache tests passed!")
