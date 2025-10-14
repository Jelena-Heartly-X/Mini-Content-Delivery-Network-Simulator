"""
Cache Replacement Policies for CDN
"""
from collections import OrderedDict, defaultdict
from abc import ABC, abstractmethod
import random

class CachePolicy(ABC):
    @abstractmethod
    def get(self, key):
        pass
    
    @abstractmethod
    def put(self, key, value):
        pass
    
    @abstractmethod
    def contains(self, key):
        pass
    
    @abstractmethod
    def get_stats(self):
        pass

class LRUCache(CachePolicy):
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        if key not in self.cache:
            self.misses += 1
            return None
        
        self.cache.move_to_end(key)
        self.hits += 1
        return self.cache[key]
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value
    
    def contains(self, key):
        return key in self.cache
    
    def get_stats(self):
        total = self.hits + self.misses
        hit_ratio = self.hits / total if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_ratio': hit_ratio,
            'size': len(self.cache),
            'capacity': self.capacity
        }

class LFUCache(CachePolicy):
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key -> (value, frequency)
        self.freq = defaultdict(OrderedDict)  # frequency -> OrderedDict of keys
        self.min_freq = 0
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        if key not in self.cache:
            self.misses += 1
            return None
        
        value, freq = self.cache[key]
        # Remove from current frequency
        del self.freq[freq][key]
        
        # Update frequency
        new_freq = freq + 1
        self.cache[key] = (value, new_freq)
        self.freq[new_freq][key] = None
        
        # Update min_freq if needed
        if not self.freq[self.min_freq]:
            self.min_freq += 1
        
        self.hits += 1
        return value
    
    def put(self, key, value):
        if self.capacity == 0:
            return
        
        if key in self.cache:
            # Update existing key
            _, freq = self.cache[key]
            del self.freq[freq][key]
            
            new_freq = freq + 1
            self.cache[key] = (value, new_freq)
            self.freq[new_freq][key] = None
            
            if not self.freq[self.min_freq]:
                self.min_freq += 1
        else:
            # New key
            if len(self.cache) >= self.capacity:
                # Evict least frequently used
                evict_key, _ = self.freq[self.min_freq].popitem(last=False)
                del self.cache[evict_key]
            
            self.cache[key] = (value, 1)
            self.freq[1][key] = None
            self.min_freq = 1
    
    def contains(self, key):
        return key in self.cache
    
    def get_stats(self):
        total = self.hits + self.misses
        hit_ratio = self.hits / total if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_ratio': hit_ratio,
            'size': len(self.cache),
            'capacity': self.capacity
        }

class FIFOCache(CachePolicy):
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        if key not in self.cache:
            self.misses += 1
            return None
        
        self.hits += 1
        return self.cache[key]
    
    def put(self, key, value):
        if key not in self.cache:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
            self.cache[key] = value
    
    def contains(self, key):
        return key in self.cache
    
    def get_stats(self):
        total = self.hits + self.misses
        hit_ratio = self.hits / total if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_ratio': hit_ratio,
            'size': len(self.cache),
            'capacity': self.capacity
        }

class RandomCache(CachePolicy):
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        if key not in self.cache:
            self.misses += 1
            return None
        
        self.hits += 1
        return self.cache[key]
    
    def put(self, key, value):
        if key not in self.cache:
            if len(self.cache) >= self.capacity:
                # Random eviction
                evict_key = random.choice(list(self.cache.keys()))
                del self.cache[evict_key]
            self.cache[key] = value
    
    def contains(self, key):
        return key in self.cache
    
    def get_stats(self):
        total = self.hits + self.misses
        hit_ratio = self.hits / total if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_ratio': hit_ratio,
            'size': len(self.cache),
            'capacity': self.capacity
        }