"""
Streamlit Dashboard for CDN Simulator - COMPLETE FIX
Replace your entire app.py with this file
"""
import streamlit as st
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.network.topology import NetworkTopology
from src.content.generator import RequestGenerator
from src.simulation.engine import CDNSimulation
from src.visualization.realtime_dashboard import CDNDashboard

def main():
    st.set_page_config(
        page_title="CDN Simulator Dashboard",
        page_icon="🌐",
        layout="wide"
    )
    
    st.title("🌐 CDN Simulator Dashboard")
    st.markdown("Interactive Content Delivery Network Simulation with Enhanced Performance")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    num_requests = st.sidebar.slider("Number of Requests", 500, 5000, 1000, step=100)
    cache_size = st.sidebar.slider("Cache Size (objects)", 100, 1000, 300, step=50)
    selected_policy = st.sidebar.selectbox(
        "Cache Policy", 
        ["LRU", "LFU", "FIFO", "RANDOM"]
    )
    
    # Advanced settings
    with st.sidebar.expander("Advanced Settings"):
        zipf_alpha = st.slider(
            "Zipf Alpha (Content Popularity)", 
            0.8, 1.5, 1.07, 0.01,
            help="Lower = more concentrated. 1.07 is optimal for realistic CDN (70-80% hit ratio)"
        )

    if st.sidebar.button("Run Simulation", type="primary"):
        run_simulation(num_requests, selected_policy, cache_size, zipf_alpha)

def run_simulation(num_requests, cache_policy, cache_size, zipf_alpha):
    """Run simulation and display results"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Initialize components
    status_text.text("Creating network topology...")
    progress_bar.progress(10)
    
    network = NetworkTopology()
    G = network.create_realistic_network()
    
    # Network overview
    st.subheader("Network Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    origin_servers = len([n for n in G.nodes if G.nodes[n].get('type') == 'origin'])
    edge_servers = len([n for n in G.nodes if G.nodes[n].get('type') == 'edge'])
    clients = len([n for n in G.nodes if G.nodes[n].get('type') == 'client'])
    
    with col1:
        st.metric("Origin Servers", origin_servers)
    with col2:
        st.metric("Edge Servers", edge_servers)
    with col3:
        st.metric("Clients", clients)
    with col4:
        st.metric("Total Requests", num_requests)
    
    progress_bar.progress(25)
    status_text.text(f"Generating {num_requests} requests (α={zipf_alpha:.2f})...")
    
    # Build clients list and region map
    clients_list = [n for n in G.nodes if G.nodes[n].get('type') == 'client']
    client_region_map = {n: G.nodes[n].get('region', 'US') for n in clients_list}
    
    # CRITICAL: Use the fixed RequestGenerator with proper Zipf
    request_gen = RequestGenerator(zipf_alpha=zipf_alpha)
    requests = request_gen.generate_requests(num_requests, clients_list, client_region_map=client_region_map)
    
    # Verify content distribution
    content_counts = {}
    for req in requests:
        cid = req['content_id']
        content_counts[cid] = content_counts.get(cid, 0) + 1
    
    unique_content = len(content_counts)
    sorted_counts = sorted(content_counts.values(), reverse=True)
    top_10_content = sorted_counts[:max(1, len(sorted_counts)//10)]
    top_10_percentage = (sum(top_10_content) / num_requests) * 100
    
    st.info(f"Generated {num_requests} requests | "
            f"Unique content: {unique_content} | "
            f"Top 10% content: {top_10_percentage:.1f}% of requests")
    
    progress_bar.progress(50)
    
    # Run simulation
    simulator = CDNSimulation(network, cache_policy=cache_policy, cache_size=cache_size)
    results = simulator.run_simulation(requests)
    
    progress_bar.progress(80)
    
    # Display results
    st.subheader("Simulation Results")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    hit_ratio = results.get('hit_ratio', 0) * 100
    baseline_hit_ratio = 15.0  # Your original performance
    improvement = hit_ratio - baseline_hit_ratio
    
    with col1:
        st.metric(
            "Cache Hit Ratio", 
            f"{hit_ratio:.1f}%"
        )
    with col2:
        avg_latency = results.get('avg_latency', 0)
        st.metric("Average Latency", f"{avg_latency:.1f} ms")
    with col3:
        st.metric("Origin Load", results.get('origin_requests', 0))
    with col4:
        bandwidth_saved = results.get('bandwidth_saved', 0) * 100
        st.metric("Bandwidth Saved", f"{bandwidth_saved:.1f}%")
    
    # Performance breakdown
    st.subheader("Performance Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Median Latency", f"{results.get('median_latency', 0):.1f} ms")
    with col2:
        st.metric("P95 Latency", f"{results.get('p95_latency', 0):.1f} ms")
    with col3:
        st.metric("Avg Hit Latency", f"{results.get('avg_hit_latency', 0):.1f} ms")
    with col4:
        st.metric("Avg Miss Latency", f"{results.get('avg_miss_latency', 0):.1f} ms")
    
    # Performance insight
    avg_hit_lat = results.get('avg_hit_latency', 0)
    avg_miss_lat = results.get('avg_miss_latency', 0)
    if avg_miss_lat > 0:
        speedup = ((avg_miss_lat - avg_hit_lat) / avg_miss_lat) * 100
        st.success(f"Cache hits are **{speedup:.0f}% faster** than cache misses!")
    
    # Recommendations based on results
    st.subheader("Performance Analysis")
    
    if hit_ratio >= 70:
        st.success(f"**Excellent Performance!** Hit ratio of {hit_ratio:.1f}% is optimal for a CDN.")
    elif hit_ratio >= 50:
        st.warning(f"**Good, but can improve.** Hit ratio is {hit_ratio:.1f}%. Try:\n"
                   f"- Increase cache size to {cache_size * 2}\n"
                   f"- Lower Zipf alpha to {max(0.8, zipf_alpha - 0.1):.2f}")
    else:
        st.error(f"**Low hit ratio ({hit_ratio:.1f}%).** Issues:\n"
                 f"- Cache size too small (try {cache_size * 3})\n"
                 f"- Content distribution not concentrated enough (try α=1.0)\n"
                 f"- Not enough requests for statistics (try 2000+)")
    
    # Generate visualizations
    dashboard = CDNDashboard()
    
    st.subheader("Network Topology")
    fig = dashboard.plot_network_topology(network)
    st.pyplot(fig)
    
    st.subheader("Performance Metrics")
    comparison_results = {cache_policy: results}
    fig2 = dashboard.plot_cache_comparison(comparison_results)
    st.pyplot(fig2)
    
    progress_bar.progress(100)    
    # Detailed metrics
    with st.expander("View Detailed Metrics"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.json({
                'Policy': results['policy'],
                'Cache Hit Ratio': f"{results['hit_ratio']*100:.2f}%",
                'Cache Hits': results['cache_hits'],
                'Cache Misses': results['cache_misses'],
                'Total Requests': results['total_requests'],
            })
        
        with col2:
            st.json({
                'Avg Latency': f"{results['avg_latency']:.2f} ms",
                'Median Latency': f"{results['median_latency']:.2f} ms",
                'P95 Latency': f"{results['p95_latency']:.2f} ms",
                'Origin Requests': results['origin_requests'],
                'Bandwidth Saved': f"{results['bandwidth_saved']*100:.2f}%",
            })

if __name__ == "__main__":
    main()