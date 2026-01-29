#!/usr/bin/env python3
"""
Stratified Benchmark Script for CliMaPan-Lab
Compares runtime and core statistics across multiple configurations.

Experiment Design:
- 10 seeds × 4 durations (5, 10, 20, 30 years) WITHOUT covid
- 10 seeds × 33 years WITH covid (covid starts year 30, lasts 1 year)

Statistics Collected:
- Runtime (seconds)
- Total GDP (sum over all time steps)
- Unemployment Rate (mean over all time steps)
- Investment (sum over all time steps)
- Climate CO2 (final value)
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from climapan_lab.src.models import EconModel
from climapan_lab.base_params import economic_params


# =============================================================================
# Configuration
# =============================================================================

SEEDS = list(range(42, 52))  # 10 seeds: 42, 43, ..., 51
DURATIONS_NO_COVID = [5, 10, 20, 30]  # years
DURATION_COVID = 33  # years
COVID_START_YEAR = 30  # Year when covid starts
COVID_DURATION_DAYS = 365  # 1 year


# =============================================================================
# Runner
# =============================================================================

def run_single_experiment(seed: int, n_years: int, covid_enabled: bool) -> dict:
    """Run a single experiment and return results."""
    n_days = n_years * 365
    
    params = economic_params.copy()
    params['seed'] = seed
    params['steps'] = n_days
    params['show_progress'] = False
    params['climateModuleFlag'] = True
    
    # Covid configuration
    if covid_enabled:
        params['covidFlag'] = True
        params['covidStartDay'] = COVID_START_YEAR * 365
        params['covidDuration'] = COVID_DURATION_DAYS
    else:
        params['covidFlag'] = False
    
    # Initialize model
    model = EconModel(params)
    model.setup()
    
    # Track statistics
    gdp_values = []
    unemployment_values = []
    investment_values = []
    co2_values = []
    
    # Run simulation
    start_time = time.time()
    
    for step in range(n_days):
        model.step()
        model.update()
        
        # Collect metrics
        if hasattr(model, 'GDP') and model.GDP > 0:
            gdp_values.append(model.GDP)
        if hasattr(model, 'unemploymentRate'):
            unemployment_values.append(model.unemploymentRate * 100)
        if hasattr(model, 'ksale'):
            investment_values.append(model.ksale)
        if hasattr(model, 'climateModule') and hasattr(model.climateModule, 'EM'):
            if len(model.climateModule.EM) > 0:
                co2_values.append(model.climateModule.EM[-1])
    
    duration = time.time() - start_time
    
    # Aggregate results
    return {
        'seed': seed,
        'n_years': n_years,
        'covid': covid_enabled,
        'runtime': duration,
        'total_gdp': sum(gdp_values) if gdp_values else 0,
        'mean_unemployment': np.mean(unemployment_values) if unemployment_values else 0,
        'total_investment': sum(investment_values) if investment_values else 0,
        'final_co2': co2_values[-1] if co2_values else 0,
    }


def run_stratified_benchmark():
    """Run the full stratified benchmark experiment."""
    results = []
    
    total_runs = len(SEEDS) * len(DURATIONS_NO_COVID) + len(SEEDS)
    current_run = 0
    
    print(f"Starting Stratified Benchmark")
    print(f"  Seeds: {len(SEEDS)}")
    print(f"  No-Covid Durations: {DURATIONS_NO_COVID}")
    print(f"  Covid Duration: {DURATION_COVID} years")
    print(f"  Total Runs: {total_runs}")
    print("=" * 60)
    
    # 1. No-Covid experiments
    for n_years in DURATIONS_NO_COVID:
        print(f"\n[NO COVID] {n_years} years:")
        for seed in SEEDS:
            current_run += 1
            print(f"  Run {current_run}/{total_runs}: seed={seed}...", end=" ", flush=True)
            
            result = run_single_experiment(seed, n_years, covid_enabled=False)
            results.append(result)
            
            print(f"{result['runtime']:.2f}s")
    
    # 2. Covid experiments
    print(f"\n[WITH COVID] {DURATION_COVID} years (covid starts year {COVID_START_YEAR}):")
    for seed in SEEDS:
        current_run += 1
        print(f"  Run {current_run}/{total_runs}: seed={seed}...", end=" ", flush=True)
        
        result = run_single_experiment(seed, DURATION_COVID, covid_enabled=True)
        results.append(result)
        
        print(f"{result['runtime']:.2f}s")
    
    return results


def save_results(results: list, output_path: str):
    """Save results to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")


def print_summary(results: list):
    """Print summary statistics."""
    df = pd.DataFrame(results)
    
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    
    # Group by (n_years, covid)
    for covid in [False, True]:
        subset = df[df['covid'] == covid]
        covid_label = "WITH COVID" if covid else "NO COVID"
        
        print(f"\n{covid_label}:")
        
        for n_years in subset['n_years'].unique():
            year_subset = subset[subset['n_years'] == n_years]
            
            print(f"\n  {n_years} years (n={len(year_subset)}):")
            print(f"    Runtime:      {year_subset['runtime'].mean():.2f}s ± {year_subset['runtime'].std():.2f}s")
            print(f"    Total GDP:    {year_subset['total_gdp'].mean():.2e} ± {year_subset['total_gdp'].std():.2e}")
            print(f"    Unemployment: {year_subset['mean_unemployment'].mean():.2f}% ± {year_subset['mean_unemployment'].std():.2f}%")
            print(f"    Investment:   {year_subset['total_investment'].mean():.2e} ± {year_subset['total_investment'].std():.2e}")
            print(f"    Final CO2:    {year_subset['final_co2'].mean():.4f} ± {year_subset['final_co2'].std():.4f}")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Detect engine (check if ambr is used)
    try:
        import ambr
        engine = "AMBER"
    except ImportError:
        engine = "AgentPy"
    
    print(f"Engine: {engine}")
    
    # Run benchmark
    results = run_stratified_benchmark()
    
    # Save results
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"benchmark_results_{engine.lower()}_{timestamp}.json"
    )
    save_results(results, output_path)
    
    # Print summary
    print_summary(results)
    
    print(f"\n✅ Benchmark complete for {engine}")
