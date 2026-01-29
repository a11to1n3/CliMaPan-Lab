#!/usr/bin/env python3
"""
Benchmark Script: Original vs Optimized Parameters
Compares performance against Germany9122.csv using autocorrelation-based scoring.
"""

import os
import sys
import numpy as np
import pandas as pd
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from climapan_lab.src.models import EconModel
from climapan_lab.base_params import economic_params as original_params
from climapan_lab.optimized_params import optimized_params


# =============================================================================
# Scoring Utils
# =============================================================================

def compute_autocorrelation(series, max_lag=5):
    series = np.asarray(series, dtype=float)
    n = len(series)
    if n < max_lag + 2:
        return np.zeros(max_lag)
    
    mean = np.mean(series)
    var = np.var(series)
    
    if var < 1e-10:
        return np.zeros(max_lag)
    
    normalized = (series - mean) / np.sqrt(var)
    
    acf = []
    for lag in range(1, max_lag + 1):
        if lag < n:
            acf.append(np.mean(normalized[:-lag] * normalized[lag:]))
        else:
            acf.append(0)
    return np.array(acf)

def compute_statistics(series):
    series = np.asarray(series, dtype=float)
    n = len(series)
    if n < 3:
        return {'cv': 0, 'trend': 0, 'acf': np.zeros(5)}
    
    mean = np.mean(series)
    std = np.std(series)
    cv = std / (abs(mean) + 1e-10)
    
    x = np.arange(n)
    if std > 1e-10:
        slope = np.polyfit(x, series, 1)[0]
        trend = slope / (abs(mean) + 1e-10)
    else:
        trend = 0
    
    acf = compute_autocorrelation(series, max_lag=5)
    return {'cv': cv, 'trend': trend, 'acf': acf}

def compute_distance_score(target_df, sim_results, n_years):
    total_distance = 0.0
    n_metrics = 0
    
    for metric in ['GDP', 'UnemploymentRate', 'Investment', 'Climate C02']:
        if metric not in target_df.columns:
            continue
            
        target = target_df[metric].values[:n_years]
        sim = sim_results.get(metric, np.zeros(n_years))[:n_years]
        
        valid_mask = ~np.isnan(target)
        if not np.any(valid_mask):
            continue
            
        target_valid = target[valid_mask]
        sim_valid = sim[valid_mask] if len(sim) >= len(target) else sim[:len(target_valid)]
        
        if len(sim_valid) < 3 or len(target_valid) < 3:
            continue
            
        target_stats = compute_statistics(target_valid)
        sim_stats = compute_statistics(sim_valid)
        
        # Distance components
        acf_dist = np.mean((target_stats['acf'] - sim_stats['acf']) ** 2)
        cv_dist = (target_stats['cv'] - sim_stats['cv']) ** 2
        trend_dist = (target_stats['trend'] - sim_stats['trend']) ** 2
        
        # Weighted score (same as calibration)
        score = 0.6 * acf_dist + 0.25 * cv_dist + 0.15 * trend_dist
        
        total_distance += score
        n_metrics += 1
        
    return total_distance / max(n_metrics, 1) if n_metrics > 0 else float('inf')


# =============================================================================
# Runner
# =============================================================================

def run_simulation(params_override, n_years=10):
    steps = n_years * 365
    
    sim_params = original_params.copy()
    sim_params.update(params_override)
    sim_params['steps'] = steps
    sim_params['show_progress'] = False
    sim_params['climateModuleFlag'] = True
    
    print(f"  > Initializing model ({steps} steps)...")
    model = EconModel(sim_params)
    model.setup()
    
    print("  > Running simulation...")
    monthly_data = {
        'GDP': [], 'UnemploymentRate': [], 'Investment': [], 'Climate C02': []
    }
    
    # Run in chunks to show aliveness
    chunk_size = 365
    total_chunks = (steps + chunk_size - 1) // chunk_size
    
    for chunk in range(total_chunks):
        sys.stdout.write(f"\r    Progress: {chunk+1}/{total_chunks} years")
        sys.stdout.flush()
        
        start = chunk * chunk_size
        end = min((chunk + 1) * chunk_size, steps)
        
        for _ in range(end - start):
            model.step()
            model.update()
            
            # Record monthly
            if hasattr(model, 'GDP') and model.GDP > 0:
                monthly_data['GDP'].append(model.GDP)
            if hasattr(model, 'unemploymentRate'):
                monthly_data['UnemploymentRate'].append(model.unemploymentRate * 100)
            if hasattr(model, 'ksale'):
                monthly_data['Investment'].append(model.ksale)
            if hasattr(model, 'climateModule') and hasattr(model.climateModule, 'EM'):
                em = model.climateModule.EM
                val = em[-1] if len(em) > 0 else 0
                monthly_data['Climate C02'].append(val)
                
    print("\n  > Aggregating results...")
    
    # Aggregate yearly
    yearly_results = {}
    for key, vals in monthly_data.items():
        arr = np.array(vals)
        years = []
        n_months = len(arr)
        if n_months == 0:
            yearly_results[key] = np.zeros(n_years)
            continue
            
        for y in range(n_years):
            start_m = y * 12
            end_m = min((y+1)*12, n_months)
            if start_m < n_months:
                years.append(np.mean(arr[start_m:end_m]))
            else:
                years.append(0)
        yearly_results[key] = np.array(years)
        
    return yearly_results

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    n_years = 30
    data_path = os.path.join(os.path.dirname(__file__), 'climapan_lab/data/Germany9122.csv')
    
    print(f"Loading target data from {data_path}...")
    target_df = pd.read_csv(data_path).ffill().bfill()
    
    print(f"\n{'='*60}")
    print("BENCHMARK: Original vs Optimized Parameters")
    print(f"Simulation Length: {n_years} years")
    print(f"{'='*60}\n")
    
    # 1. Original
    print("1. Evaluating ORIGINAL parameters...")
    start_time = time.time()
    try:
        res_orig = run_simulation({}, n_years)
        score_orig = compute_distance_score(target_df, res_orig, n_years)
        print(f"  >> Score (Lower is better): {score_orig:.6f}")
        print(f"  >> Time: {time.time() - start_time:.1f}s")
    except Exception as e:
        print(f"  >> Error: {e}")
        score_orig = float('inf')
        
    print("-" * 60)
        
    # 2. Optimized
    print("2. Evaluating OPTIMIZED parameters...")
    start_time = time.time()
    try:
        res_opt = run_simulation(optimized_params, n_years)
        score_opt = compute_distance_score(target_df, res_opt, n_years)
        print(f"  >> Score (Lower is better): {score_opt:.6f}")
        print(f"  >> Time: {time.time() - start_time:.1f}s")
    except Exception as e:
        print(f"  >> Error: {e}")
        score_opt = float('inf')
        
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    print(f"Original Score:  {score_orig:.6f}")
    print(f"Optimized Score: {score_opt:.6f}")
    
    if score_opt < score_orig:
        imp = ((score_orig - score_opt) / score_orig) * 100
        print(f"\n✅ OPTIMIZED parameters improved fit by {imp:.1f}%!")
    else:
        print("\n❌ Optimized parameters did not improve fit.")
