"""
CDN Simulation Engine - OPTIMIZED
"""
import random
from collections import defaultdict
from ..cache.manager import CacheManager

class CDNSimulation:
    def __init__(self, network, cache_policy='LRU', cache_size=100):
        self.network = network
        self.cache_policy = cache_policy
        self.cache_size = cache_size
        self.edge_servers = self._initialize_edge_servers()
        self.metrics = self._initialize_metrics()
        self.requests_processed = []
        
        # Optimization: Pre-compute client to edge mappings
        self.client_edge_map = self._precompute_client_edge_mapping()
    
    def _initialize_edge_servers(self):
        """Initialize edge servers with caches"""
        edge_servers = {}
        edge_nodes = [n for n in self.network.G.nodes 
                     if self.network.G.nodes[n].get('type') == 'edge']
        
        for server_id in edge_nodes:
            edge_servers[server_id] = {
                'cache': CacheManager(self.cache_policy, self.cache_size),
                'load': 0,
                'location': self.network.G.nodes[server_id].get('location', 'Unknown'),
                'region': self.network.G.nodes[server_id].get('region', None)
            }
        
        return edge_servers
    
    def _initialize_metrics(self):
        """Initialize metrics collection"""
        return {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_latency': 0,
            'origin_requests': 0,
            'bandwidth_saved': 0,  # in KB
            'server_loads': defaultdict(int),
            'content_served': defaultdict(int),
            'hit_latencies': [],  # Track hit latencies
            'miss_latencies': []  # Track miss latencies
        }
    
    def _precompute_client_edge_mapping(self):
        """Pre-compute nearest edge servers for each client"""
        mapping = {}
        clients = [n for n in self.network.G.nodes 
                  if self.network.G.nodes[n].get('type') == 'client']
        
        for client in clients:
            mapping[client] = self.network.find_nearest_edge_server(client)
        
        return mapping
    
    def find_nearest_edge_server(self, client_node):
        """Find nearest edge server (using pre-computed mapping)"""
        return self.client_edge_map.get(client_node)
    
    def process_request(self, request):
        """Process a single request - OPTIMIZED"""
        client = request['client']
        content_id = request['content_id']
        content_size = request['size']
        region = request.get('region', None)
        
        # Find nearest edge server (fast lookup)
        edge_server_id = self.find_nearest_edge_server(client)
        
        if not edge_server_id:
            # No edge server available
            latency = 1000
            self.metrics['total_requests'] += 1
            self.metrics['total_latency'] += latency
            self.metrics['miss_latencies'].append(latency)
            return latency
        
        edge_server = self.edge_servers[edge_server_id]
        
        # Update server load
        self.metrics['server_loads'][edge_server_id] += 1
        edge_server['load'] += 1
        
        # Check cache (OPTIMIZED: contains is faster than get for checking)
        if edge_server['cache'].contains(content_id):
            # CACHE HIT - serve from edge
            latency = self.network.get_latency(client, edge_server_id)
            
            # Update the cache (for LRU/LFU policies to track access)
            edge_server['cache'].get(content_id)
            
            self.metrics['cache_hits'] += 1
            self.metrics['bandwidth_saved'] += content_size
            self.metrics['content_served'][content_id] += 1
            self.metrics['hit_latencies'].append(latency)
            
        else:
            # CACHE MISS - fetch from origin
            origin_server = self.network.find_origin_server(client_region=region)
            
            # Calculate round-trip latency: client → edge → origin → edge → client
            # Optimized: Only client→edge once (assuming edge caches response)
            client_to_edge = self.network.get_latency(client, edge_server_id)
            edge_to_origin = self.network.get_latency(edge_server_id, origin_server)
            
            # Total latency: request to edge + fetch from origin + response
            latency = client_to_edge + edge_to_origin + client_to_edge
            
            # Cache the content at the edge for future requests
            edge_server['cache'].put(content_id, content_size)
            
            self.metrics['cache_misses'] += 1
            self.metrics['origin_requests'] += 1
            self.metrics['content_served'][content_id] += 1
            self.metrics['miss_latencies'].append(latency)
        
        self.metrics['total_requests'] += 1
        self.metrics['total_latency'] += latency
        
        # Store request for analysis
        self.requests_processed.append(request)
        
        return latency
    
    def run_simulation(self, requests):
        """Run simulation with given requests"""
        print(f"   Processing {len(requests)} requests with {self.cache_policy} policy...")
        
        # Reset metrics for new simulation
        self.metrics = self._initialize_metrics()
        self.requests_processed = []
        
        # Process requests in batches for better progress reporting
        batch_size = 100
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i+batch_size]
            
            for request in batch:
                self.process_request(request)
            
            # Progress indicator
            if (i + batch_size) % 500 == 0 or i + batch_size >= len(requests):
                processed = min(i + batch_size, len(requests))
                print(f"     Processed {processed}/{len(requests)} requests")
        
        return self.get_metrics()
    
    def get_metrics(self):
        """Get comprehensive metrics with additional statistics"""
        total_requests = self.metrics['total_requests']
        
        if total_requests == 0:
            return {
                'policy': self.cache_policy,
                'hit_ratio': 0,
                'avg_latency': 0,
                'median_latency': 0,
                'p95_latency': 0,
                'p99_latency': 0,
                'avg_hit_latency': 0,
                'avg_miss_latency': 0,
                'origin_requests': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'total_requests': 0,
                'bandwidth_saved': 0,
                'server_loads': {},
                'total_bandwidth_saved_kb': 0,
                'cache_efficiency': 0
            }
        
        hit_ratio = self.metrics['cache_hits'] / total_requests
        avg_latency = self.metrics['total_latency'] / total_requests
        
        # Calculate percentile latencies
        all_latencies = self.metrics['hit_latencies'] + self.metrics['miss_latencies']
        all_latencies.sort()
        
        median_latency = all_latencies[len(all_latencies)//2] if all_latencies else 0
        p95_idx = int(len(all_latencies) * 0.95)
        p99_idx = int(len(all_latencies) * 0.99)
        p95_latency = all_latencies[p95_idx] if p95_idx < len(all_latencies) else 0
        p99_latency = all_latencies[p99_idx] if p99_idx < len(all_latencies) else 0
        
        # Average latencies for hits vs misses
        avg_hit_latency = (sum(self.metrics['hit_latencies']) / len(self.metrics['hit_latencies']) 
                          if self.metrics['hit_latencies'] else 0)
        avg_miss_latency = (sum(self.metrics['miss_latencies']) / len(self.metrics['miss_latencies']) 
                           if self.metrics['miss_latencies'] else 0)
        
        # Calculate bandwidth saving percentage
        total_bandwidth = sum(req['size'] for req in self.requests_processed)
        bandwidth_saved_ratio = (self.metrics['bandwidth_saved'] / total_bandwidth 
                                if total_bandwidth > 0 else 0)
        
        # Cache efficiency: ratio of hits to cache size
        cache_efficiency = (self.metrics['cache_hits'] / self.cache_size 
                          if self.cache_size > 0 else 0)
        
        return {
            'policy': self.cache_policy,
            'hit_ratio': hit_ratio,
            'avg_latency': avg_latency,
            'median_latency': median_latency,
            'p95_latency': p95_latency,
            'p99_latency': p99_latency,
            'avg_hit_latency': avg_hit_latency,
            'avg_miss_latency': avg_miss_latency,
            'origin_requests': self.metrics['origin_requests'],
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'total_requests': total_requests,
            'bandwidth_saved': bandwidth_saved_ratio,
            'server_loads': dict(self.metrics['server_loads']),
            'total_bandwidth_saved_kb': self.metrics['bandwidth_saved'],
            'cache_efficiency': cache_efficiency
        }