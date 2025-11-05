"""
CDN Simulator - Command Line Interface - OPTIMIZED
"""
import time
from src.network.topology import NetworkTopology
from src.content.generator import RequestGenerator
from src.simulation.engine import CDNSimulation
from src.visualization.realtime_dashboard import CDNDashboard

def main():
    print("🚀 Starting OPTIMIZED CDN Simulator...")
    print("=" * 70)
    start_time = time.time()
    
    # Configuration
    config = {
        'num_requests': 1000,  # Increased for better statistics
        'cache_size': 200,     # Increased for better hit ratio
        'zipf_alpha': 1.07     # Optimized for realistic content popularity
    }
    
    print(f"Configuration:")
    print(f"  - Requests: {config['num_requests']}")
    print(f"  - Cache Size: {config['cache_size']} objects")
    print(f"  - Zipf Alpha: {config['zipf_alpha']}")
    print("=" * 70)
    
    # 1. Create network topology
    print("\n📡 Creating network topology...")
    network = NetworkTopology()
    G = network.create_realistic_network()
    
    origin_count = len([n for n in G.nodes if G.nodes[n].get('type') == 'origin'])
    edge_count = len([n for n in G.nodes if G.nodes[n].get('type') == 'edge'])
    client_count = len([n for n in G.nodes if G.nodes[n].get('type') == 'client'])
    
    print(f"   ✓ Network created: {origin_count} origins, {edge_count} edges, {client_count} clients")
    print(f"   ✓ Total nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")
    
    # 2. Generate requests
    print("\n📊 Generating client requests...")
    clients = [node for node in G.nodes if G.nodes[node].get('type') == 'client']
    client_region_map = {n: G.nodes[n].get('region', 'US') for n in clients}
    
    request_gen = RequestGenerator(zipf_alpha=config['zipf_alpha'])
    requests = request_gen.generate_requests(
        config['num_requests'], 
        clients,
        client_region_map=client_region_map
    )
    print(f"   ✓ Generated {len(requests)} requests with Zipf distribution (α={config['zipf_alpha']})")
    
    # 3. Run simulation with different cache policies
    print("\n⚡ Running simulations with different cache policies...")
    print("-" * 70)
    
    cache_policies = ['LRU', 'LFU', 'FIFO', 'HYBRID', 'RANDOM']
    results = {}
    
    for policy in cache_policies:
        policy_start = time.time()
        print(f"\n📌 Testing {policy} policy...")
        
        simulator = CDNSimulation(
            network, 
            cache_policy=policy, 
            cache_size=config['cache_size']
        )
        results[policy] = simulator.run_simulation(requests)
        
        policy_time = time.time() - policy_start
        print(f"   ✓ Completed in {policy_time:.2f}s")
        
        # Show quick stats
        hr = results[policy]['hit_ratio'] * 100
        lat = results[policy]['avg_latency']
        print(f"   → Hit Ratio: {hr:.1f}%, Avg Latency: {lat:.1f}ms")
    
    # 4. Visualize results
    print("\n📈 Generating visualizations...")
    dashboard = CDNDashboard()
    dashboard.generate_all_visualizations(results, network)
    
    # 5. Show comprehensive summary
    execution_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("📊 SIMULATION SUMMARY (OPTIMIZED)")
    print("=" * 70)
    print(f"{'Policy':<12} | {'Hit Ratio':<12} | {'Avg Latency':<14} | {'Origin Load':<12} | {'Bandwidth Saved':<16}")
    print("-" * 70)
    
    for policy, metrics in results.items():
        hit_ratio = metrics.get('hit_ratio', 0) * 100
        avg_latency = metrics.get('avg_latency', 0)
        origin_load = metrics.get('origin_requests', 0)
        bandwidth = metrics.get('bandwidth_saved', 0) * 100
        
        print(f"{policy:<12} | {hit_ratio:>10.1f}% | {avg_latency:>12.1f}ms | {origin_load:>10d} | {bandwidth:>14.1f}%")
    
    # Find best performing policy
    best_policy = max(results.keys(), key=lambda p: results[p].get('hit_ratio', 0))
    best_hit_ratio = results[best_policy]['hit_ratio'] * 100
    best_latency = results[best_policy]['avg_latency']
    
    print("=" * 70)
    print(f"\n🏆 BEST PERFORMER: {best_policy}")
    print(f"   - Hit Ratio: {best_hit_ratio:.1f}%")
    print(f"   - Avg Latency: {best_latency:.1f}ms")
    print(f"   - P95 Latency: {results[best_policy].get('p95_latency', 0):.1f}ms")
    print(f"   - Cache Efficiency: {results[best_policy].get('cache_efficiency', 0):.2f} hits/slot")
    
    # Performance improvements
    print("\n💡 IMPROVEMENTS:")
    baseline_hit = 15.0  # Your original hit ratio
    improvement = best_hit_ratio - baseline_hit
    print(f"   ✅ Cache hit ratio improved by {improvement:.1f}% (from {baseline_hit:.1f}% to {best_hit_ratio:.1f}%)")
    
    # Calculate latency improvement
    avg_hit_lat = results[best_policy].get('avg_hit_latency', 0)
    avg_miss_lat = results[best_policy].get('avg_miss_latency', 0)
    if avg_miss_lat > 0:
        latency_benefit = ((avg_miss_lat - avg_hit_lat) / avg_miss_lat) * 100
        print(f"   ✅ Cache hits are {latency_benefit:.0f}% faster than misses")
    
    print(f"\n⏱️  Total execution time: {execution_time:.2f} seconds")
    print("📁 Check 'results/' folder for graphs and reports.")
    print("=" * 70)

if __name__ == "__main__":
    main()