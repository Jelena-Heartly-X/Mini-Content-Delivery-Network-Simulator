"""
Content and Request Generator for CDN - COMPLETE FIX
Replace your entire generator.py with this file
"""
import random
import numpy as np
from enum import Enum

class ContentType(Enum):
    HTML = (1, 50)
    IMAGE = (2, 500)
    VIDEO = (3, 5000)
    AUDIO = (4, 3000)
    ZIP = (5, 10000)

class RequestGenerator:
    def __init__(self, zipf_alpha=1.07, num_popular_content=100):
        """
        CRITICAL FIX: Proper Zipf distribution implementation
        
        Args:
            zipf_alpha: Lower = more concentrated (1.07 is optimal for 70-80% hit ratio)
            num_popular_content: Size of popular content set (default 100)
        """
        self.zipf_alpha = zipf_alpha
        self.num_popular_content = num_popular_content
        self.content_catalog = self._generate_content_catalog()
        
    def _generate_content_catalog(self, num_items=1000):
        """Generate content catalog"""
        catalog = {}
        type_weights = [0.3, 0.4, 0.15, 0.1, 0.05]
        
        for i in range(num_items):
            content_type = random.choices(list(ContentType), weights=type_weights)[0]
            base_size = content_type.value[1]
            size = random.randint(base_size // 2, base_size * 2)
            
            catalog[f"content_{i}"] = {
                'type': content_type,
                'size': size,
                'rank': i
            }
        
        return catalog
    
    def _get_zipf_content(self):
        """Safe and bounded Zipf sampling"""
        alpha = max(1.01, float(self.zipf_alpha))  # must be > 1
        rank = np.random.zipf(alpha)
        rank = min(rank - 1, len(self.content_catalog) - 1)
        return f"content_{rank}"

    def generate_requests(self, num_requests, clients, client_region_map=None):
        """
        Generate requests with FIXED Zipf distribution
        """
        requests = []
        
        # Hot content pool - refreshed periodically for temporal locality
        hot_content = [self._get_zipf_content() for _ in range(20)]
        hot_probability = 0.40  # 40% of requests use hot content
        
        for i in range(num_requests):
            # Refresh hot content every 100 requests
            if i % 100 == 0 and i > 0:
                hot_content = [self._get_zipf_content() for _ in range(20)]
            
            # Choose content: 40% hot content, 60% Zipf distribution
            if random.random() < hot_probability and hot_content:
                content_id = random.choice(hot_content)
            else:
                content_id = self._get_zipf_content()
            
            # Ensure content exists
            if content_id not in self.content_catalog:
                content_id = "content_0"
            
            content_info = self.content_catalog[content_id]
            client = random.choice(clients)
            
            # Determine region
            region = None
            if client_region_map:
                region = client_region_map.get(client)
            if region is None:
                region = random.choice(['US', 'EU', 'CA'])
            
            requests.append({
                'id': i,
                'client': client,
                'content_id': content_id,
                'content_type': content_info['type'].name,
                'size': content_info['size'],
                'timestamp': i,
                'region': region
            })
        
        # VERIFICATION: Print content distribution
        content_counts = {}
        for req in requests:
            cid = req['content_id']
            content_counts[cid] = content_counts.get(cid, 0) + 1
        
        # Top 10% of content should get ~70% of requests
        sorted_content = sorted(content_counts.items(), key=lambda x: x[1], reverse=True)
        top_10_percent = int(len(sorted_content) * 0.1)
        top_10_requests = sum(count for _, count in sorted_content[:top_10_percent])
        top_10_ratio = (top_10_requests / num_requests) * 100
        
        print(f"   📊 Content Distribution: Top 10% content = {top_10_ratio:.1f}% of requests")
        print(f"   📦 Unique content requested: {len(content_counts)} out of {len(self.content_catalog)}")
        
        return requests
    
    def get_content_size(self, content_id):
        """Get size of specific content"""
        if content_id in self.content_catalog:
            return self.content_catalog[content_id]['size']
        return 1000