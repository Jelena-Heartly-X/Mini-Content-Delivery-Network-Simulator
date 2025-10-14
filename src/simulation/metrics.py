"""
Metrics collection and analysis for CDN simulation
"""
import json
import pandas as pd
from datetime import datetime

class MetricsCollector:
    def __init__(self):
        self.metrics_history = []
    
    def record_simulation(self, results, config):
        """Record simulation results"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'results': results
        }
        self.metrics_history.append(record)
    
    def generate_report(self, results_dict):
        """Generate comprehensive report for multiple policies"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'detailed_metrics': results_dict
        }
        
        # Find best performing policy
        best_policy = max(results_dict.keys(), 
                         key=lambda p: results_dict[p].get('hit_ratio', 0))
        
        report['summary'] = {
            'best_policy': best_policy,
            'best_hit_ratio': results_dict[best_policy].get('hit_ratio', 0),
            'total_simulations': len(results_dict)
        }
        
        return report
    
    def save_to_json(self, results_dict, filename=None):
        """Save metrics to JSON file"""
        if filename is None:
            filename = f"results/metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.generate_report(results_dict)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename
    
    def save_to_csv(self, results_dict, filename=None):
        """Save metrics to CSV file"""
        if filename is None:
            filename = f"results/metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Flatten results for CSV
        rows = []
        for policy, metrics in results_dict.items():
            row = {
                'policy': policy,
                'hit_ratio': metrics.get('hit_ratio', 0),
                'avg_latency': metrics.get('avg_latency', 0),
                'origin_requests': metrics.get('origin_requests', 0),
                'cache_hits': metrics.get('cache_hits', 0),
                'cache_misses': metrics.get('cache_misses', 0),
                'total_requests': metrics.get('total_requests', 0),
                'bandwidth_saved': metrics.get('bandwidth_saved', 0)
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        
        return filename