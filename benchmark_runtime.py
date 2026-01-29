#!/usr/bin/env python3
"""
Benchmark Runtime Script
Measures execution time of the model (setup + N steps).
Agnostic to underlying engine (AMBER vs AgentPy).
"""

import time
import numpy as np
import sys
import os

# Add parent dir
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from climapan_lab.src.models import EconModel
from climapan_lab.base_params import economic_params

def benchmark(n_runs=5, n_days=365):
    print(f"Benchmarking Runtime ({n_runs} runs, {n_days} days/run)...")
    
    times = []
    
    for i in range(n_runs):
        params = economic_params.copy()
        params['steps'] = n_days
        params['show_progress'] = False
        params['climateModuleFlag'] = False # Disable climate module for pure agent speed test
        
        start_time = time.time()
        
        # Initialize
        model = EconModel(params)
        model.setup()
        
        # Run
        for _ in range(n_days):
            model.step()
            model.update()
            
        duration = time.time() - start_time
        times.append(duration)
        print(f"  Run {i+1}: {duration:.4f}s")
        
    mean_time = np.mean(times)
    std_time = np.std(times)
    
    print("\nResults:")
    print(f"  Mean: {mean_time:.4f}s")
    print(f"  Std:  {std_time:.4f}s")
    print(f"  Rate: {n_days / mean_time:.1f} steps/sec")
    
    return mean_time, std_time

if __name__ == "__main__":
    benchmark(n_runs=5, n_days=365)
