"""
Content and Request Generator for CDN
"""
import random
import numpy as np
from enum import Enum

class ContentType(Enum):
    HTML = (1, 50)      # ID, typical size in KB
    IMAGE = (2, 500)
    VIDEO = (3, 5000)
    AUDIO = (4, 3000)
    ZIP = (5, 10000)

class RequestGenerator:
    def __init__(self, zipf_alpha=1.2):
        self.zipf_alpha = zipf_alpha
        self.content_catalog = self._generate_content_catalog()
    
    def _generate_content_catalog(self, num_items=1000):
        """Generate content catalog with realistic distribution"""
        catalog = {}
        
        # Content type distribution
        type_weights = [0.3, 0.4, 0.15, 0.1, 0.05]  # HTML, IMAGE, VIDEO, AUDIO, ZIP
        
        for i in range(num_items):
            content_type = random.choices(
                list(ContentType), 
                weights=type_weights
            )[0]
            
            # Size variation ±50%
            base_size = content_type.value[1]
            size = random.randint(base_size // 2, base_size * 2)
            
            catalog[f"content_{i}"] = {
                'type': content_type,
                'size': size,  # in KB
                'popularity': np.random.zipf(self.zipf_alpha)
            }
        
        return catalog
    
    def _get_zipf_content(self):
        """Get content ID based on Zipf distribution"""
        # Simple Zipf-like distribution
        popular_contents = list(self.content_catalog.keys())[:100]  # Top 100 popular
        less_popular = list(self.content_catalog.keys())[100:500]   # Medium popularity
        rare_contents = list(self.content_catalog.keys())[500:]     # Rare content
        
        # Weighted selection
        choice = random.random()
        if choice < 0.7:  # 70% chance for popular content
            return random.choice(popular_contents)
        elif choice < 0.9:  # 20% chance for medium popularity
            return random.choice(less_popular)
        else:  # 10% chance for rare content
            return random.choice(rare_contents)
    
    def generate_requests(self, num_requests, clients):
        """Generate synthetic requests"""
        requests = []
        
        for i in range(num_requests):
            client = random.choice(clients)
            content_id = self._get_zipf_content()
            content_info = self.content_catalog[content_id]
            
            requests.append({
                'id': i,
                'client': client,
                'content_id': content_id,
                'content_type': content_info['type'].name,
                'size': content_info['size'],  # in KB
                'timestamp': i  # Simple timestamp simulation
            })
        
        return requests
    
    def get_content_size(self, content_id):
        """Get size of specific content"""
        if content_id in self.content_catalog:
            return self.content_catalog[content_id]['size']
        return 1000  # Default size in KB