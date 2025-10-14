"""
Cache Manager for CDN
"""
from .policies import LRUCache, LFUCache, FIFOCache, RandomCache

class CacheManager:
    def __init__(self, policy='LRU', capacity=100):
        self.policy = policy
        self.capacity = capacity
        self.cache = self._create_cache(policy, capacity)
    
    def _create_cache(self, policy, capacity):
        """Create cache instance based on policy"""
        if policy == 'LRU':
            return LRUCache(capacity)
        elif policy == 'LFU':
            return LFUCache(capacity)
        elif policy == 'FIFO':
            return FIFOCache(capacity)
        elif policy == 'RANDOM':
            return RandomCache(capacity)
        else:
            return LRUCache(capacity)  # Default
    
    def get(self, key):
        """Get content from cache"""
        return self.cache.get(key)
    
    def put(self, key, value):
        """Put content into cache"""
        self.cache.put(key, value)
    
    def contains(self, key):
        """Check if content is in cache"""
        return self.cache.contains(key)
    
    def get_stats(self):
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def clear(self):
        """Clear the cache (create new instance)"""
        self.cache = self._create_cache(self.policy, self.capacity)