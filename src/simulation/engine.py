"""
CDN Simulation Engine
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
        self.requests_processed = []  # Store processed requests for metrics
    
    def _initialize_edge_servers(self):
        """Initialize edge servers with caches"""
        edge_servers = {}
        edge_nodes = [n for n in self.network.G.nodes if self.network.G.nodes[n].get('type') == 'edge']
        
        for server_id in edge_nodes:
            edge_servers[server_id] = {
                'cache': CacheManager(self.cache_policy, self.cache_size),
                'load': 0,
                'location': self.network.G.nodes[server_id].get('location', 'Unknown')
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
            'content_served': defaultdict(int)
        }
    
    def find_nearest_edge_server(self, client_node):
        """Find nearest edge server for a client"""
        return self.network.find_nearest_edge_server(client_node)
    
    def process_request(self, request):
        """Process a single request"""
        client = request['client']
        content_id = request['content_id']
        content_size = request['size']
        
        # Find nearest edge server
        edge_server_id = self.find_nearest_edge_server(client)
        
        if not edge_server_id:
            return 1000  # High latency if no server found
        
        edge_server = self.edge_servers[edge_server_id]
        
        # Update server load
        self.metrics['server_loads'][edge_server_id] += 1
        edge_server['load'] += 1
        
        # Check cache
        if edge_server['cache'].contains(content_id):
            # Cache hit
            latency = self.network.get_latency(client, edge_server_id)
            self.metrics['cache_hits'] += 1
            self.metrics['bandwidth_saved'] += content_size
            self.metrics['content_served'][content_id] += 1
        else:
            # Cache miss - fetch from origin
            origin_server = self.network.find_origin_server()
            
            # Latency: client → edge → origin → edge → client
            client_to_edge = self.network.get_latency(client, edge_server_id)
            edge_to_origin = self.network.get_latency(edge_server_id, origin_server)
            origin_to_edge = self.network.get_latency(origin_server, edge_server_id)
            edge_to_client = self.network.get_latency(edge_server_id, client)
            
            latency = client_to_edge + edge_to_origin + origin_to_edge + edge_to_client
            
            # Cache the content
            edge_server['cache'].put(content_id, content_size)
            
            self.metrics['cache_misses'] += 1
            self.metrics['origin_requests'] += 1
            self.metrics['content_served'][content_id] += 1
        
        self.metrics['total_requests'] += 1
        self.metrics['total_latency'] += latency
        
        # Store the request for later metrics calculation
        self.requests_processed.append(request)
        
        return latency
    
    def run_simulation(self, requests):
        """Run simulation with given requests"""
        print(f"   Processing {len(requests)} requests with {self.cache_policy} policy...")
        
        # Reset metrics for new simulation
        self.metrics = self._initialize_metrics()
        self.requests_processed = []
        
        for i, request in enumerate(requests):
            latency = self.process_request(request)
            
            # Progress indicator for CLI
            if (i + 1) % 100 == 0:
                print(f"     Processed {i + 1}/{len(requests)} requests")
        
        return self.get_metrics()
    
    def get_metrics(self):
        """Get comprehensive metrics"""
        total_requests = self.metrics['total_requests']
        
        if total_requests == 0:
            return {
                'policy': self.cache_policy,
                'hit_ratio': 0,
                'avg_latency': 0,
                'origin_requests': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'total_requests': 0,
                'bandwidth_saved': 0,
                'server_loads': {},
                'total_bandwidth_saved_kb': 0
            }
        
        hit_ratio = self.metrics['cache_hits'] / total_requests
        avg_latency = self.metrics['total_latency'] / total_requests
        
        # Calculate bandwidth saving percentage
        total_bandwidth = sum(req['size'] for req in self.requests_processed)
        bandwidth_saved_ratio = self.metrics['bandwidth_saved'] / total_bandwidth if total_bandwidth > 0 else 0
        
        return {
            'policy': self.cache_policy,
            'hit_ratio': hit_ratio,
            'avg_latency': avg_latency,
            'origin_requests': self.metrics['origin_requests'],
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'total_requests': total_requests,
            'bandwidth_saved': bandwidth_saved_ratio,
            'server_loads': dict(self.metrics['server_loads']),
            'total_bandwidth_saved_kb': self.metrics['bandwidth_saved']
        }