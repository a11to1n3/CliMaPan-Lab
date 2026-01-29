#!/usr/bin/env python3
"""
Plot Benchmark: Original vs Optimized Parameters
Generates plots comparing ACF and CV against Target Data.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from climapan_lab.src.models import EconModel
from climapan_lab.base_params import economic_params as original_params
from climapan_lab.optimized_params import optimized_params

# Set style
plt.style.use('ggplot')
sns.set_context("paper")

# =============================================================================
# Utils
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

def compute_cv(series):
    series = np.asarray(series, dtype=float)
    if len(series) < 2: return 0.0
    mean = np.mean(series)
    std = np.std(series)
    return std / (abs(mean) + 1e-10)

def run_simulation(params_override, n_years=30):
    steps = n_years * 365
    
    sim_params = original_params.copy()
    sim_params.update(params_override)
    sim_params['steps'] = steps
    sim_params['show_progress'] = True  # Show progress for this script
    sim_params['climateModuleFlag'] = True
    
    print(f"Running simulation ({n_years} years)...")
    model = EconModel(sim_params)
    model.setup()
    
    monthly_data = {
        'GDP': [], 'UnemploymentRate': [], 'Investment': [], 'Climate C02': []
    }
    
    # Run loop
    for step in range(steps):
        model.step()
        model.update()
        
        # Simple progress bar
        if step % 3650 == 0:
            print(f"  Year {step//365 + 1}/{n_years}")

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
    
    print("1. Loading Target Data...")
    target_df = pd.read_csv(data_path).ffill().bfill()
    target_data = {}
    for col in ['GDP', 'UnemploymentRate', 'Investment', 'Climate C02']:
        if col in target_df.columns:
            target_data[col] = target_df[col].values[:n_years]

    print("\n2. Running Original Parameters...")
    orig_results = run_simulation({}, n_years)
    
    print("\n3. Running Optimized Parameters...")
    opt_results = run_simulation(optimized_params, n_years)
    
    print("\n4. Generating Plots...")
    
    metrics = ['GDP', 'UnemploymentRate', 'Investment', 'Climate C02']
    
    # Prepare Data for Plotting
    plot_data = [] # List of dicts for DataFrame
    
    # CV Data
    cv_rows = []
    
    # ACF Data
    acf_data = {'Metric': [], 'Source': [], 'Lag': [], 'ACF': []}
    
    for m in metrics:
        # Target
        t_vals = target_data.get(m, np.zeros(n_years))
        t_cv = compute_cv(t_vals)
        t_acf = compute_autocorrelation(t_vals)
        
        cv_rows.append({'Metric': m, 'Source': 'Target', 'CV': t_cv})
        for i, val in enumerate(t_acf):
            acf_data['Metric'].append(m)
            acf_data['Source'].append('Target')
            acf_data['Lag'].append(i+1)
            acf_data['ACF'].append(val)
            
        # Original
        o_vals = orig_results.get(m, np.zeros(n_years))
        o_cv = compute_cv(o_vals)
        o_acf = compute_autocorrelation(o_vals)
        
        cv_rows.append({'Metric': m, 'Source': 'Original', 'CV': o_cv})
        for i, val in enumerate(o_acf):
            acf_data['Metric'].append(m)
            acf_data['Source'].append('Original')
            acf_data['Lag'].append(i+1)
            acf_data['ACF'].append(val)
            
        # Optimized
        opt_vals = opt_results.get(m, np.zeros(n_years))
        opt_cv = compute_cv(opt_vals)
        opt_acf = compute_autocorrelation(opt_vals)
        
        cv_rows.append({'Metric': m, 'Source': 'Optimized', 'CV': opt_cv})
        for i, val in enumerate(opt_acf):
            acf_data['Metric'].append(m)
            acf_data['Source'].append('Optimized')
            acf_data['Lag'].append(i+1)
            acf_data['ACF'].append(val)
            
    df_cv = pd.DataFrame(cv_rows)
    df_acf = pd.DataFrame(acf_data)
    
    # Create Figure
    fig = plt.figure(figsize=(15, 12))
    gs = fig.add_gridspec(len(metrics), 2)
    
    colors = {'Target': 'black', 'Original': 'red', 'Optimized': 'green'}
    
    for i, m in enumerate(metrics):
        # 1. ACF Plot (Line)
        ax_acf = fig.add_subplot(gs[i, 0])
        subset_acf = df_acf[df_acf['Metric'] == m]
        
        sns.lineplot(data=subset_acf, x='Lag', y='ACF', hue='Source', 
                     palette=colors, marker='o', ax=ax_acf, linewidth=2)
        
        ax_acf.set_title(f"{m} - Autocorrelation (ACF)")
        ax_acf.set_ylim(-0.5, 1.1)
        ax_acf.set_xticks(range(1, 6))
        
        # 2. CV Plot (Bar)
        ax_cv = fig.add_subplot(gs[i, 1])
        subset_cv = df_cv[df_cv['Metric'] == m]
        
        sns.barplot(data=subset_cv, x='Metric', y='CV', hue='Source', 
                    palette=colors, ax=ax_cv)
        
        ax_cv.set_title(f"{m} - Coefficient of Variation (CV)")
        ax_cv.set_xlabel("")
        
        # Add values on bars
        for container in ax_cv.containers:
            ax_cv.bar_label(container, fmt='%.2f')

    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), 'benchmark_comparison.png')
    plt.savefig(output_path, dpi=150)
    print(f"\n✅ Plot saved to: {output_path}")

