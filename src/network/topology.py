"""
Network Topology for CDN Simulator - OPTIMIZED
"""
import networkx as nx
import random

class NetworkTopology:
    def __init__(self):
        self.G = nx.Graph()
        self.latency_cache = {}  # Cache shortest path calculations
    
    def create_realistic_network(self):
        """Create a realistic CDN network with origins, edges, and clients"""
        
        # Add origin servers (increased capacity)
        self.G.add_node('origin_ny', type='origin', location='New York', capacity=10000, region='US')
        self.G.add_node('origin_lon', type='origin', location='London', capacity=10000, region='EU')
        
        # Add edge servers with better distribution
        edge_servers = [
            # US East
            ('edge_bos', 'Boston', 200, 'US'),
            ('edge_atl', 'Atlanta', 200, 'US'),
            ('edge_mia', 'Miami', 200, 'US'),
            
            # US Central
            ('edge_chi', 'Chicago', 200, 'US'),
            ('edge_dal', 'Dallas', 200, 'US'),
            ('edge_den', 'Denver', 200, 'US'),
            
            # US West
            ('edge_la', 'Los Angeles', 200, 'US'),
            ('edge_sf', 'San Francisco', 200, 'US'),
            ('edge_sea', 'Seattle', 200, 'US'),
            ('edge_phx', 'Phoenix', 200, 'US'),
            
            # Canada
            ('edge_tor', 'Toronto', 200, 'CA'),
            ('edge_van', 'Vancouver', 200, 'CA'),
        ]
        
        for server_id, location, capacity, region in edge_servers:
            self.G.add_node(server_id, type='edge', location=location, capacity=capacity, region=region)
        
        # Add clients with realistic distribution
        client_configs = [
            # US clients (70% of total)
            *[('NY', 'US') for _ in range(6)],
            *[('CA', 'US') for _ in range(5)],
            *[('TX', 'US') for _ in range(3)],
            *[('FL', 'US') for _ in range(2)],
            *[('IL', 'US') for _ in range(2)],
            # Canada clients (20%)
            *[('ON', 'CA') for _ in range(2)],
            *[('BC', 'CA') for _ in range(2)],
            # EU clients (10%)
            *[('GB', 'EU') for _ in range(2)],
        ]
        
        for i, (loc_code, region) in enumerate(client_configs[:20]):
            client_id = f'client_{i}'
            self.G.add_node(client_id, type='client', location=loc_code, region=region)
        
        # Add connections with optimized latencies
        self._add_connections()
        
        return self.G
    
    def _add_connections(self):
        """Add edges with realistic and optimized latency values"""
        
        # Origin to Edge connections (lower latencies for better performance)
        connections = [
            # From NY Origin (US East coast - very low latency)
            ('origin_ny', 'edge_bos', 3), ('origin_ny', 'edge_atl', 10),
            ('origin_ny', 'edge_mia', 15), ('origin_ny', 'edge_tor', 8),
            
            # US Central (medium latency from NY)
            ('origin_ny', 'edge_chi', 12), ('origin_ny', 'edge_dal', 18),
            ('origin_ny', 'edge_den', 22),
            
            # US West (higher latency from NY)
            ('origin_ny', 'edge_la', 35), ('origin_ny', 'edge_sf', 40),
            ('origin_ny', 'edge_sea', 45), ('origin_ny', 'edge_phx', 32),
            ('origin_ny', 'edge_van', 50),
            
            # From London Origin (lower latency to EU/East Coast)
            ('origin_lon', 'edge_bos', 65), ('origin_lon', 'edge_tor', 70),
            ('origin_lon', 'edge_chi', 80), ('origin_lon', 'edge_van', 85),
            
            # Edge server interconnections (create mesh for redundancy)
            # East Coast mesh
            ('edge_bos', 'edge_atl', 10), ('edge_atl', 'edge_mia', 8),
            ('edge_bos', 'edge_tor', 7),
            
            # Central mesh
            ('edge_chi', 'edge_dal', 12), ('edge_dal', 'edge_den', 10),
            ('edge_chi', 'edge_den', 15),
            
            # West Coast mesh
            ('edge_la', 'edge_sf', 6), ('edge_sf', 'edge_sea', 12),
            ('edge_la', 'edge_phx', 7), ('edge_sea', 'edge_van', 10),
            
            # Cross-region connections
            ('edge_chi', 'edge_sf', 25), ('edge_dal', 'edge_la', 18),
            ('edge_den', 'edge_sea', 16), ('edge_atl', 'edge_dal', 14),
        ]
        
        for src, dst, latency in connections:
            if src in self.G.nodes and dst in self.G.nodes:
                self.G.add_edge(src, dst, latency=latency, bandwidth=10000)
        
        # Connect clients to edges (OPTIMIZED: each client connects to 2-3 nearby edges)
        clients = [n for n in self.G.nodes if self.G.nodes[n].get('type') == 'client']
        edge_servers = [n for n in self.G.nodes if self.G.nodes[n].get('type') == 'edge']
        
        for client in clients:
            client_region = self.G.nodes[client].get('region', 'US')
            
            # Find edges in same region
            regional_edges = [e for e in edge_servers 
                            if self.G.nodes[e].get('region') == client_region]
            
            if not regional_edges:
                regional_edges = edge_servers
            
            # Connect to 2-3 edges for redundancy and load balancing
            num_connections = min(3, len(regional_edges))
            connected_edges = random.sample(regional_edges, num_connections)
            
            for edge in connected_edges:
                # Very low latency within same region
                if self.G.nodes[edge].get('region') == client_region:
                    base_latency = random.randint(2, 8)  # 2-8ms within region
                else:
                    base_latency = random.randint(30, 60)  # 30-60ms cross-region
                
                self.G.add_edge(client, edge, latency=base_latency, bandwidth=1000)
    
    def get_latency(self, node1, node2):
        """Get latency between two nodes (with caching for performance)"""
        # Check cache first
        cache_key = tuple(sorted([node1, node2]))
        if cache_key in self.latency_cache:
            return self.latency_cache[cache_key]
        
        try:
            if self.G.has_edge(node1, node2):
                latency = self.G.edges[node1, node2]['latency']
            else:
                # Use shortest path
                try:
                    path = nx.shortest_path(self.G, node1, node2, weight='latency')
                    latency = sum(self.G.edges[path[i], path[i+1]]['latency'] 
                                for i in range(len(path)-1))
                except nx.NetworkXNoPath:
                    latency = 100  # Fallback
            
            # Cache the result
            self.latency_cache[cache_key] = latency
            return latency
            
        except Exception:
            return 100
    
    def find_nearest_edge_server(self, client_node):
        """Find the nearest edge server for a client (OPTIMIZED)"""
        edge_servers = [n for n in self.G.nodes if self.G.nodes[n].get('type') == 'edge']
        
        if not edge_servers:
            return None
        
        # Prefer directly connected edges (lowest latency)
        direct_neighbors = [n for n in self.G.neighbors(client_node) 
                          if self.G.nodes[n].get('type') == 'edge']
        
        if direct_neighbors:
            # Return the directly connected edge with lowest latency
            return min(direct_neighbors, 
                      key=lambda s: self.G.edges[client_node, s]['latency'])
        
        # Fallback: find nearest edge server
        nearest_server = min(edge_servers, 
                           key=lambda server: self.get_latency(client_node, server))
        return nearest_server
    
    def find_origin_server(self, content_location='NY', client_region=None):
        """
        Find appropriate origin server based on client region.
        Optimized to prefer geographically closer origins.
        """
        if client_region is not None:
            region = client_region.upper()
            if region in ['US', 'NA', 'CA']:
                return 'origin_ny'
            if region in ['EU', 'GB', 'UK']:
                return 'origin_lon'
            return 'origin_ny'  # Default to NY for unknown regions
        
        # Fallback
        if content_location in ['US', 'NY', 'NA', 'CA']:
            return 'origin_ny'
        else:
            return 'origin_lon'
    
    def clear_cache(self):
        """Clear the latency cache (useful for testing)"""
        self.latency_cache.clear()