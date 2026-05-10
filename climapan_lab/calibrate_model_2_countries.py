#!/usr/bin/env python3
"""
Dual-Country Model Calibration Script for CliMaPan-Lab using Bayesian Optimization

Calibrates model parameters against a 2-country dataset using AUTOCORRELATION-BASED matching.
This matches the dynamics/patterns of time series rather than absolute values.
"""

import json
import os
import sys
import time
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from climapan_lab.base_params import economic_params as parameters
from climapan_lab.src.models import EconModel

# =============================================================================
# Load Target Data
# =============================================================================


def load_target_data(filepath: str = None) -> pd.DataFrame:
    """Load target data for 2 countries."""
    if filepath is None:
        # Update this to the actual CSV containing your 2-country data
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data", "TwoCountriesData.csv"
        )

    try:
        df = pd.read_csv(filepath)
        df = df.ffill().bfill()
        print(f"Loaded target data: {len(df)} years")
        print(f"Columns: {list(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"WARNING: Target data not found at {filepath}.")
        print("Please ensure your dual-country CSV exists or update the filepath.")
        return pd.DataFrame()


# =============================================================================
# Autocorrelation Functions
# =============================================================================


def compute_autocorrelation(series: np.ndarray, max_lag: int = 5) -> np.ndarray:
    """Compute autocorrelation for a time series up to max_lag."""
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


def compute_statistics(series: np.ndarray) -> Dict[str, float]:
    """Compute key statistics of a time series."""
    series = np.asarray(series, dtype=float)
    n = len(series)

    if n < 3:
        return {"mean": 0, "std": 0, "cv": 0, "trend": 0, "acf": np.zeros(5)}

    mean = np.mean(series)
    std = np.std(series)
    cv = std / (abs(mean) + 1e-10)  # Coefficient of variation

    # Trend (normalized slope)
    x = np.arange(n)
    if std > 1e-10:
        slope = np.polyfit(x, series, 1)[0]
        trend = slope / (abs(mean) + 1e-10)
    else:
        trend = 0

    acf = compute_autocorrelation(series, max_lag=5)

    return {"mean": mean, "std": std, "cv": cv, "trend": trend, "acf": acf}


# =============================================================================
# Parameter Space
# =============================================================================

# Define parameters for both countries. You may have shared parameters or distinct ones.
PARAM_SPACE = {
    # Shared or Country A parameters
    "wageAdjustmentRate": (0.0001, 0.01),
    "depreciationRate": (0.1, 0.4),
    "rho_labour": (40, 120),
    # Country B parameters (if explicit in your model setup)
    # "countryB_wageAdjustmentRate": (0.0001, 0.01),
    # "countryB_depreciationRate": (0.1, 0.4),
}


# =============================================================================
# Simulation Runner
# =============================================================================


def run_simulation(params: dict, n_years: int = 10) -> dict:
    """Run simulation and return yearly aggregated metrics for both countries."""
    steps = n_years * 365

    sim_params = parameters.copy()
    sim_params.update(params)
    sim_params["steps"] = steps
    sim_params["show_progress"] = False

    model = EconModel(sim_params)
    model.setup()

    # Dictionary to collect monthly data for 2 countries
    monthly_metrics = {
        "CountryA_GDP": [],
        "CountryB_GDP": [],
        "CountryA_Unemployment": [],
        "CountryB_Unemployment": [],
        # Add more if needed: "CountryA_Investment": [], "CountryB_Investment": [],
    }

    for step in range(steps):
        model.step()
        model.update()

        # Update these according to how your model exposes Country A and Country B variables
        # Assuming you have model.countryA_GDP, model.countryB_GDP, etc.
        if hasattr(model, "countryA_GDP"):
            monthly_metrics["CountryA_GDP"].append(model.countryA_GDP)
        if hasattr(model, "countryB_GDP"):
            monthly_metrics["CountryB_GDP"].append(model.countryB_GDP)

        if hasattr(model, "countryA_unemploymentRate"):
            monthly_metrics["CountryA_Unemployment"].append(
                model.countryA_unemploymentRate * 100
            )
        if hasattr(model, "countryB_unemploymentRate"):
            monthly_metrics["CountryB_Unemployment"].append(
                model.countryB_unemploymentRate * 100
            )

    def yearly_aggregate(monthly_data: list, n_years: int) -> np.ndarray:
        if not monthly_data:
            return np.zeros(n_years)
        arr = np.array(monthly_data)
        n_months = len(arr)
        years = []
        for y in range(n_years):
            start = y * 12
            end = min((y + 1) * 12, n_months)
            if start < n_months:
                years.append(np.mean(arr[start:end]))
            else:
                years.append(0)
        return np.array(years)

    # Convert collected monthly metrics to yearly aggregations
    yearly_results = {
        key: yearly_aggregate(values, n_years)
        for key, values in monthly_metrics.items()
    }

    return yearly_results


# =============================================================================
# Autocorrelation-Based Objective Function
# =============================================================================


def objective_function(
    params: dict, target_data: pd.DataFrame, n_years: int = 10
) -> float:
    """
    Compute autocorrelation-based distance between simulation and target for 2 countries.
    """
    try:
        sim_results = run_simulation(params, n_years)
        total_distance = 0.0
        n_metrics = 0

        # Define the exact column names expected in your Target CSV
        target_metrics = [
            "CountryA_GDP",
            "CountryB_GDP",
            "CountryA_Unemployment",
            "CountryB_Unemployment",
        ]

        for metric in target_metrics:
            if metric not in target_data.columns:
                continue

            target = target_data[metric].values[:n_years]
            sim = sim_results.get(metric, np.zeros(n_years))[:n_years]

            valid_mask = ~np.isnan(target)
            if not np.any(valid_mask):
                continue

            target_valid = target[valid_mask]
            sim_valid = (
                sim[valid_mask] if len(sim) >= len(target) else sim[: len(target_valid)]
            )

            if len(sim_valid) < 3 or len(target_valid) < 3:
                continue

            target_stats = compute_statistics(target_valid)
            sim_stats = compute_statistics(sim_valid)

            acf_distance = np.mean((target_stats["acf"] - sim_stats["acf"]) ** 2)
            cv_distance = (target_stats["cv"] - sim_stats["cv"]) ** 2
            trend_distance = (target_stats["trend"] - sim_stats["trend"]) ** 2

            metric_distance = (
                0.6 * acf_distance + 0.25 * cv_distance + 0.15 * trend_distance
            )

            total_distance += metric_distance
            n_metrics += 1

        return total_distance / max(n_metrics, 1)

    except Exception as e:
        print(f"Error in objective: {e}")
        return float("inf")


# =============================================================================
# Bayesian Optimization
# =============================================================================


def monte_carlo_optimization(
    target_data: pd.DataFrame,
    n_calls: int = 100,
    n_years: int = 10,
    seed: int = 42,
) -> list:
    """Perform Monte Carlo random sampling for model calibration."""
    np.random.seed(seed)

    print(f"\n{'='*60}")
    print(f"Autocorrelation-Based Monte Carlo Calibration")
    print(f"  Total trials: {n_calls}")
    print(f"  Years per trial: {n_years}")
    print(f"  Parameters: {len(PARAM_SPACE)}")
    print(f"  Objective: ACF + CV + Trend matching (lower is better)")
    print(f"{'='*60}\n")

    results = []
    start_time = time.time()

    def sample_random() -> dict:
        params = {}
        for name, (low, high) in PARAM_SPACE.items():
            if low > 0 and high / low > 100:
                # Log-uniform for parameters spanning multiple orders of magnitude
                params[name] = np.exp(np.random.uniform(np.log(low), np.log(high)))
            else:
                # Uniform for others
                params[name] = np.random.uniform(low, high)
        return params

    for i in range(n_calls):
        params = sample_random()
        phase = "monte_carlo"

        trial_start = time.time()
        objective = objective_function(params, target_data, n_years)
        trial_time = time.time() - trial_start

        results.append(
            {
                "params": params,
                "objective": objective if objective != float("inf") else 1e6,
                "time": trial_time,
                "phase": phase,
            }
        )

        best_obj = min(r["objective"] for r in results)
        print(
            f"[{i+1}/{n_calls}] Score: {objective:.6f} | Best: {best_obj:.6f} | {trial_time:.1f}s"
        )

    total_time = time.time() - start_time

    results.sort(key=lambda x: x["objective"])

    print(f"\n{'='*60}")
    print(f"Optimization Complete!")
    print(f"  Total time: {total_time:.1f}s")
    print(f"  Best Score: {results[0]['objective']:.6f}")
    print(f"{'='*60}\n")

    return results


def save_results(results: list, output_path: str):
    """Save calibration results to JSON."""
    serializable_results = []
    for r in results[:10]:
        serializable_results.append(
            {
                "params": {k: float(v) for k, v in r["params"].items()},
                "objective": (
                    float(r["objective"]) if r["objective"] != float("inf") else 1e10
                ),
                "time": float(r["time"]),
                "phase": r.get("phase", "unknown"),
            }
        )

    with open(output_path, "w") as f:
        json.dump(serializable_results, f, indent=2)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    target_data = load_target_data()

    if target_data.empty:
        print("Exiting due to missing target data.")
        sys.exit(1)

    print("\nTarget Data Statistics:")
    print("-" * 40)
    # Match the metrics from dual target lists
    target_metrics = [
        "CountryA_GDP",
        "CountryB_GDP",
        "CountryA_Unemployment",
        "CountryB_Unemployment",
    ]
    for col in target_metrics:
        if col in target_data.columns:
            stats = compute_statistics(target_data[col].values)
            print(f"{col}:")
            print(f"  CV: {stats['cv']:.4f}")
            print(f"  Trend: {stats['trend']:.4f}")
            print(f"  ACF[1-3]: {stats['acf'][:3]}")

    results = monte_carlo_optimization(
        target_data=target_data,
        n_calls=100,  # Number of MC trials
        n_years=30,  # Number of years to simulate matching target length
        seed=42,
    )

    print("\n" + "=" * 60)
    print("Best Parameters Found:")
    print("=" * 60)
    for k, v in sorted(results[0]["params"].items()):
        print(f"  {k}: {v:.6f}")

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "calibration_results_2_countries.json",
    )
    save_results(results, output_path)
    print(f"Results JSON saved to: {output_path}")

    best_params_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "optimized_params_2_countries.py"
    )
    with open(best_params_path, "w") as f:
        f.write(
            "# Optimized Multi-Country parameters from Autocorrelation-Based Monte Carlo calibration\n"
        )
        f.write("optimized_params = {\n")
        for k, v in sorted(results[0]["params"].items()):
            f.write(f"    '{k}': {v},\n")
        f.write("}\n")
    print(f"Best params saved to: {best_params_path}")
