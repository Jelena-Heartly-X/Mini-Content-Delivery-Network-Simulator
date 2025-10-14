"""
Streamlit Dashboard for CDN Simulator
"""
import streamlit as st
import sys
import os
import time
import matplotlib.pyplot as plt

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
    st.markdown("Interactive Content Delivery Network Simulation")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    num_requests = st.sidebar.slider("Number of Requests", 100, 1000, 500)
    cache_size = st.sidebar.slider("Cache Size (objects)", 50, 500, 100)
    selected_policy = st.sidebar.selectbox("Cache Policy", ["LRU", "LFU", "FIFO", "RANDOM"])
    
    if st.sidebar.button("🚀 Run Simulation", type="primary"):
        run_simulation(num_requests, selected_policy, cache_size)

def run_simulation(num_requests, cache_policy, cache_size):
    """Run simulation and display results in Streamlit"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Initialize components
    status_text.text("Creating network topology...")
    progress_bar.progress(20)
    
    network = NetworkTopology()
    G = network.create_realistic_network()
    
    # Network overview
    st.subheader("📡 Network Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    origin_servers = len([n for n in G.nodes if 'origin' in n])
    edge_servers = len([n for n in G.nodes if 'edge' in n])
    clients = len([n for n in G.nodes if 'client' in n])
    
    with col1:
        st.metric("Origin Servers", origin_servers)
    with col2:
        st.metric("Edge Servers", edge_servers)
    with col3:
        st.metric("Clients", clients)
    with col4:
        st.metric("Total Requests", num_requests)
    
    # Generate requests
    status_text.text("Generating requests...")
    progress_bar.progress(40)
    
    clients_list = [node for node in G.nodes if 'client' in node]
    request_gen = RequestGenerator()
    requests = request_gen.generate_requests(num_requests, clients_list)
    
    # Run simulation
    status_text.text(f"Running simulation with {cache_policy} policy...")
    progress_bar.progress(60)
    
    simulator = CDNSimulation(network, cache_policy=cache_policy, cache_size=cache_size)
    results = simulator.run_simulation(requests)
    
    # Display results
    status_text.text("Generating visualizations...")
    progress_bar.progress(80)
    
    st.subheader("📊 Simulation Results")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        hit_ratio = results.get('hit_ratio', 0) * 100
        st.metric("Cache Hit Ratio", f"{hit_ratio:.1f}%")
    with col2:
        st.metric("Average Latency", f"{results.get('avg_latency', 0):.1f} ms")
    with col3:
        st.metric("Origin Load", results.get('origin_requests', 0))
    with col4:
        bandwidth_saved = results.get('bandwidth_saved', 0) * 100
        st.metric("Bandwidth Saved", f"{bandwidth_saved:.1f}%")
    
    # Generate and display visualizations
    dashboard = CDNDashboard()
    
    # Network graph
    status_text.text("Creating network visualization...")
    st.subheader("🌍 Network Topology")
    fig = dashboard.plot_network_topology(network)
    st.pyplot(fig)
    
    # Cache performance
    status_text.text("Creating performance charts...")
    st.subheader("📈 Performance Metrics")
    
    # Create comparison data for the selected policy
    comparison_results = {cache_policy: results}
    fig2 = dashboard.plot_cache_comparison(comparison_results)
    st.pyplot(fig2)
    
    progress_bar.progress(100)
    status_text.text("✅ Simulation completed!")
    
    # Show detailed metrics
    st.subheader("📋 Detailed Metrics")
    st.json(results)

if __name__ == "__main__":
    main()