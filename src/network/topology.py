"""
Network Topology for CDN Simulator
"""
import networkx as nx
import random

class NetworkTopology:
    def __init__(self):
        self.G = nx.Graph()
    
    def create_realistic_network(self):
        """Create a realistic CDN network with origins, edges, and clients"""
        
        # Add origin servers
        self.G.add_node('origin_ny', type='origin', location='New York', capacity=1000)
        self.G.add_node('origin_lon', type='origin', location='London', capacity=1000)
        
        # Add edge servers
        edge_servers = [
            ('edge_bos', 'Boston', 100),
            ('edge_chi', 'Chicago', 100),
            ('edge_la', 'Los Angeles', 100),
            ('edge_sf', 'San Francisco', 100),
            ('edge_mia', 'Miami', 100),
            ('edge_sea', 'Seattle', 100),
            ('edge_dal', 'Dallas', 100),
            ('edge_atl', 'Atlanta', 100),
            ('edge_den', 'Denver', 100),
            ('edge_phx', 'Phoenix', 100),
            ('edge_tor', 'Toronto', 100),
            ('edge_van', 'Vancouver', 100)
        ]
        
        for server_id, location, capacity in edge_servers:
            self.G.add_node(server_id, type='edge', location=location, capacity=capacity)
        
        # Add clients (20 clients)
        for i in range(20):
            client_id = f'client_{i}'
            location = random.choice(['NY', 'CA', 'TX', 'FL', 'IL', 'WA', 'GA', 'CO', 'AZ', 'MA'])
            self.G.add_node(client_id, type='client', location=location)
        
        # Add connections with realistic latencies (in milliseconds)
        self._add_connections()
        
        return self.G
    
    def _add_connections(self):
        """Add edges with realistic latency values"""
        
        # Origin to Edge connections
        connections = [
            # From NY Origin
            ('origin_ny', 'edge_bos', 5), ('origin_ny', 'edge_chi', 15),
            ('origin_ny', 'edge_atl', 20), ('origin_ny', 'edge_tor', 10),
            ('origin_ny', 'edge_mia', 25), ('origin_ny', 'edge_la', 45),
            ('origin_ny', 'edge_sf', 50), ('origin_ny', 'edge_sea', 60),
            ('origin_ny', 'edge_dal', 25), ('origin_ny', 'edge_den', 30),
            ('origin_ny', 'edge_phx', 40), ('origin_ny', 'edge_van', 65),
            
            # From London Origin
            ('origin_lon', 'edge_bos', 80), ('origin_lon', 'edge_tor', 85),
            ('origin_lon', 'edge_nyc', 90),
            
            # Edge server interconnections
            ('edge_bos', 'edge_nyc', 5), ('edge_chi', 'edge_nyc', 15),
            ('edge_la', 'edge_sf', 8), ('edge_sea', 'edge_sf', 15),
            ('edge_chi', 'edge_dal', 18), ('edge_atl', 'edge_mia', 12),
            ('edge_den', 'edge_phx', 15), ('edge_chi', 'edge_den', 25),
        ]
        
        for src, dst, latency in connections:
            if src in self.G.nodes and dst in self.G.nodes:
                self.G.add_edge(src, dst, latency=latency, bandwidth=1000)
        
        # Connect each client to 1-2 edge servers
        clients = [n for n in self.G.nodes if self.G.nodes[n].get('type') == 'client']
        edge_servers = [n for n in self.G.nodes if self.G.nodes[n].get('type') == 'edge']
        
        for client in clients:
            # Connect to 1-2 random edge servers
            num_connections = random.randint(1, 2)
            connected_edges = random.sample(edge_servers, num_connections)
            
            for edge in connected_edges:
                latency = random.randint(5, 50)  # Client to edge latency
                self.G.add_edge(client, edge, latency=latency, bandwidth=100)
        
    def get_latency(self, node1, node2):
        """Get latency between two nodes"""
        try:
            if self.G.has_edge(node1, node2):
                return self.G.edges[node1, node2]['latency']
            else:
                # Return high latency for no direct connection
                return 100
        except:
            return 100
    
    def find_nearest_edge_server(self, client_node):
        """Find the nearest edge server for a client"""
        edge_servers = [n for n in self.G.nodes if self.G.nodes[n].get('type') == 'edge']
        
        if not edge_servers:
            return None
        
        # Find edge server with minimum latency
        nearest_server = min(edge_servers, 
                        key=lambda server: self.get_latency(client_node, server))
        return nearest_server
        
    def find_origin_server(self, content_location='NY'):
        """Find appropriate origin server based on content location"""
        if content_location in ['US', 'NY']:
            return 'origin_ny'
        else:
            return 'origin_lon'