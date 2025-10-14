"""
CDN Simulator - Command Line Interface
"""
import time
from src.network.topology import NetworkTopology
from src.content.generator import RequestGenerator
from src.simulation.engine import CDNSimulation
from src.visualization.realtime_dashboard import CDNDashboard

def main():
    print("🚀 Starting CDN Simulator...")
    start_time = time.time()
    
    # Configuration
    config = {
        'num_requests': 500,
        'cache_size': 100
    }
    
    # 1. Create network topology
    print("📡 Creating network topology...")
    network = NetworkTopology()
    G = network.create_realistic_network()
    
    # 2. Generate requests
    print("📊 Generating client requests...")
    clients = [node for node in G.nodes if 'client' in node]
    request_gen = RequestGenerator()
    requests = request_gen.generate_requests(config['num_requests'], clients)
    
    # 3. Run simulation with different cache policies
    print("⚡ Running simulations with different cache policies...")
    cache_policies = ['LRU', 'LFU', 'FIFO', 'RANDOM']
    results = {}
    
    for policy in cache_policies:
        print(f"   Testing {policy} policy...")
        simulator = CDNSimulation(network, cache_policy=policy, cache_size=config['cache_size'])
        results[policy] = simulator.run_simulation(requests)
    
    # 4. Visualize results
    print("📈 Generating visualizations...")
    dashboard = CDNDashboard()
    dashboard.generate_all_visualizations(results, network)
    
    # 5. Show summary
    execution_time = time.time() - start_time
    print("\n📊 SIMULATION SUMMARY")
    print("=" * 60)
    for policy, metrics in results.items():
        hit_ratio = metrics.get('hit_ratio', 0) * 100
        avg_latency = metrics.get('avg_latency', 0)
        origin_load = metrics.get('origin_requests', 0)
        print(f"{policy:8} | Hit Ratio: {hit_ratio:5.1f}% | Avg Latency: {avg_latency:5.1f}ms | Origin Load: {origin_load:3d}")
    
    print(f"\n✅ Simulation completed in {execution_time:.2f} seconds!")
    print("📁 Check 'results/' folder for graphs and reports.")

if __name__ == "__main__":
    main()