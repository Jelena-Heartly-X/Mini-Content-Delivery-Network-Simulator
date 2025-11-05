"""
Cache Manager for CDN
"""
from threading import Lock
from .policies import LRUCache, LFUCache, FIFOCache, RandomCache
from collections import defaultdict, OrderedDict
import time

class CacheManager:
    def __init__(self, policy='LRU', capacity=100):
        self.policy = str(policy).upper()
        self.capacity = int(capacity)
        self.lock = Lock()
        self.cache = self._create_cache(self.policy, self.capacity)
    
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
        elif policy == 'HYBRID':
            return HybridCache(capacity)
        else:
            return LRUCache(capacity)  # Default
    
    def get(self, key):
        """Get content from cache"""
        with self.lock:
            return self.cache.get(key)
    
    def put(self, key, value):
        """Put content into cache"""
        with self.lock:
            self.cache.put(key, value)
    
    def contains(self, key):
        """Check if content is in cache"""
        with self.lock:
            return self.cache.contains(key)
    
    def get_stats(self):
        """Get cache statistics"""
        with self.lock:
            return self.cache.get_stats()
    
    def clear(self):
        """Clear the cache (create new instance)"""
        with self.lock:
            self.cache = self._create_cache(self.policy, self.capacity)


# -------------------------
# Hybrid Cache Implementation
# -------------------------
class HybridCache:
    """
    Simple LFU+LRU hybrid:
    - track frequency for LFU behavior
    - maintain recency order via OrderedDict for LRU tie-breaking
    - on eviction prefer low-frequency items; if multiple, evict least recent among them
    """
    def __init__(self, capacity):
        self.capacity = int(capacity)
        self.store = {}  # key -> value
        self.freq = defaultdict(int)  # key -> freq
        self.recency = OrderedDict()  # key order: oldest -> newest
        self.hits = 0
        self.misses = 0

    def _evict_one(self):
        # Find minimum frequency among keys
        if not self.store:
            return
        min_freq = min(self.freq[k] for k in self.store.keys())
        # collect keys with min_freq
        candidates = [k for k in self.store.keys() if self.freq[k] == min_freq]
        # pick the least recently used among candidates (recency is OrderedDict)
        for key in self.recency:
            if key in candidates:
                victim = key
                break
        # remove victim
        if victim in self.store:
            del self.store[victim]
        if victim in self.freq:
            del self.freq[victim]
        if victim in self.recency:
            self.recency.pop(victim, None)

    def get(self, key):
        if key not in self.store:
            self.misses += 1
            return None
        # hit
        self.hits += 1
        self.freq[key] += 1
        # move to newest in recency
        self.recency.pop(key, None)
        self.recency[key] = True
        return self.store[key]

    def put(self, key, value):
        if key in self.store:
            # update existing
            self.store[key] = value
            self.freq[key] += 1
            # promote recency
            self.recency.pop(key, None)
            self.recency[key] = True
            return

        if self.capacity == 0:
            return

        if len(self.store) >= self.capacity:
            self._evict_one()

        # insert new item
        self.store[key] = value
        self.freq[key] = 1
        self.recency[key] = True

    def contains(self, key):
        return key in self.store

    def get_stats(self):
        total = self.hits + self.misses
        hit_ratio = (self.hits / total) if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_ratio': hit_ratio,
            'size': len(self.store),
            'capacity': self.capacity
        }
