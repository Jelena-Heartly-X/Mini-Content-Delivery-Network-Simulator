"""
Visualization dashboard for CDN simulator
"""
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import numpy as np
import os

class CDNDashboard:
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        self.colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        
        # Create results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
    
    def plot_network_topology(self, network):
        """Plot network topology"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        G = network.G
        
        # Define node colors and sizes based on type
        node_colors = []
        node_sizes = []
        
        for node in G.nodes():
            node_type = G.nodes[node].get('type', 'client')
            if node_type == 'origin':
                node_colors.append('#FF6B6B')  # Red for origins
                node_sizes.append(800)
            elif node_type == 'edge':
                node_colors.append('#4ECDC4')  # Teal for edges
                node_sizes.append(500)
            else:  # client
                node_colors.append('#45B7D1')  # Blue for clients
                node_sizes.append(200)
        
        # Use spring layout for better visualization
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Draw the network
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, 
                              alpha=0.9, ax=ax)
        nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='gray', ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
        
        # Draw edge labels (latency)
        edge_labels = {(u, v): f"{d['latency']}ms" 
                      for u, v, d in G.edges(data=True) if 'latency' in d}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
        
        ax.set_title("CDN Network Topology", fontsize=16, fontweight='bold')
        ax.axis('off')
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B', 
                      markersize=10, label='Origin Servers'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4', 
                      markersize=10, label='Edge Servers'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#45B7D1', 
                      markersize=10, label='Clients')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.savefig('results/network_topology.png', dpi=300, bbox_inches='tight')
        return fig
    
    def plot_cache_comparison(self, results_dict):
        """Compare cache policies performance"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        policies = list(results_dict.keys())
        hit_ratios = [results_dict[p].get('hit_ratio', 0) * 100 for p in policies]
        avg_latencies = [results_dict[p].get('avg_latency', 0) for p in policies]
        origin_requests = [results_dict[p].get('origin_requests', 0) for p in policies]
        bandwidth_saved = [results_dict[p].get('bandwidth_saved', 0) * 100 for p in policies]
        
        # Plot 1: Hit Ratios
        bars1 = ax1.bar(policies, hit_ratios, color=self.colors[:len(policies)], alpha=0.8)
        ax1.set_title('Cache Hit Ratio by Policy', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Hit Ratio (%)')
        ax1.set_ylim(0, 100)
        self._add_value_labels(ax1, bars1)
        
        # Plot 2: Average Latency
        bars2 = ax2.bar(policies, avg_latencies, color=self.colors[:len(policies)], alpha=0.8)
        ax2.set_title('Average Latency by Policy', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Latency (ms)')
        self._add_value_labels(ax2, bars2)
        
        # Plot 3: Origin Server Load
        bars3 = ax3.bar(policies, origin_requests, color=self.colors[:len(policies)], alpha=0.8)
        ax3.set_title('Origin Server Requests', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Number of Requests')
        self._add_value_labels(ax3, bars3)
        
        # Plot 4: Bandwidth Saved
        bars4 = ax4.bar(policies, bandwidth_saved, color=self.colors[:len(policies)], alpha=0.8)
        ax4.set_title('Bandwidth Saved', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Bandwidth Saved (%)')
        ax4.set_ylim(0, 100)
        self._add_value_labels(ax4, bars4)
        
        plt.tight_layout()
        plt.savefig('results/cache_comparison.png', dpi=300, bbox_inches='tight')
        return fig
    
    def plot_latency_distribution(self, results_dict):
        """Plot latency distribution across policies"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        policies = list(results_dict.keys())
        latencies = [results_dict[p].get('avg_latency', 0) for p in policies]
        
        bars = ax.bar(policies, latencies, color=self.colors[:len(policies)], alpha=0.8)
        ax.set_title('Average Latency Distribution', fontsize=16, fontweight='bold')
        ax.set_ylabel('Latency (ms)')
        ax.set_xlabel('Cache Policy')
        
        self._add_value_labels(ax, bars)
        
        plt.tight_layout()
        plt.savefig('results/latency_distribution.png', dpi=300, bbox_inches='tight')
        return fig
    
    def plot_server_load_distribution(self, results_dict):
        """Plot load distribution across edge servers"""
        # Take first policy's server loads
        first_policy = list(results_dict.keys())[0]
        server_loads = results_dict[first_policy].get('server_loads', {})
        
        if not server_loads:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        servers = list(server_loads.keys())
        loads = list(server_loads.values())
        
        bars = ax.bar(servers, loads, color='skyblue', alpha=0.8)
        ax.set_title('Load Distribution Across Edge Servers', fontsize=16, fontweight='bold')
        ax.set_ylabel('Number of Requests')
        ax.set_xlabel('Edge Servers')
        plt.xticks(rotation=45, ha='right')
        
        self._add_value_labels(ax, bars)
        
        plt.tight_layout()
        plt.savefig('results/server_load_distribution.png', dpi=300, bbox_inches='tight')
        return fig
    
    def _add_value_labels(self, ax, bars):
        """Add value labels on bars"""
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                   f'{height:.1f}', ha='center', va='bottom')
    
    def generate_all_visualizations(self, results_dict, network):
        """Generate all visualizations"""
        print("   Generating network topology...")
        self.plot_network_topology(network)
        
        print("   Generating cache comparison...")
        self.plot_cache_comparison(results_dict)
        
        print("   Generating latency distribution...")
        self.plot_latency_distribution(results_dict)
        
        print("   Generating server load distribution...")
        self.plot_server_load_distribution(results_dict)
        
        print("   All visualizations saved to 'results/' folder")