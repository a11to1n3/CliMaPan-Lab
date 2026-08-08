# CliMaPan-Lab: Climate-Pandemic Economic Modeling Laboratory

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![ambr ≥0.4.7](https://img.shields.io/badge/ambr-%3E%3D0.4.7-green.svg)](https://pypi.org/project/ambr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/a11to1n3/CliMaPan-Lab/workflows/Tests/badge.svg)](https://github.com/a11to1n3/CliMaPan-Lab/actions)

CliMaPan-Lab is an agent-based economic modeling framework for studying interactions between climate change, pandemic dynamics, and economic systems. It runs on **[AMBER](https://github.com/a11to1n3/AMBER)** (`ambr≥0.4.7`).

## Installation

**Requirements:** Python **≥3.9**, `ambr≥0.4.7` (and other deps in `requirements.txt`).

```bash
# Install from PyPI (Recommended)
pip install climapan-lab

# Install from source
git clone https://github.com/a11to1n3/CliMaPan-Lab.git
cd CliMaPan-Lab
pip install -e .

# Or install directly from GitHub
pip install git+https://github.com/a11to1n3/CliMaPan-Lab.git
```

Confirm the stack:

```bash
python -c "import ambr; print('ambr', ambr.__version__)"  # expect 0.4.7+
```

## Quick Start

Time steps are **daily**. Macro indicators (`GDP`, unemployment, investment, climate series, …) are **recorded on month boundaries** only—use enough steps to cross at least one month (e.g. `steps ≥ 40`).

```python
from climapan_lab.model import EconModel
from climapan_lab.base_params import economic_params

params = economic_params.copy()
params["steps"] = 120              # ~4 months of daily steps
params["show_progress"] = False
# Optional for interactive runs: params["c_agents"] = 200

model = EconModel(params)
results = model.run()              # AMBER RunResults (dict-like)

# Polars model frame → pandas
df = results["model"].to_pandas()
gdp = df["GDP"].dropna()
print(f"Monthly GDP observations: {len(gdp)}")
if len(gdp):
    print(f"Last recorded GDP: {gdp.iloc[-1]}")
```

`climapan_lab.run_sim.single_run` wraps the same output for legacy AgentPy-style access (`result.variables.EconModel` as pandas).

### Example Script

```bash
python climapan_lab/examples/simple_example.py
```

### Command Line Interface

#### Basic Usage

```bash
# Basic simulation
climapan-run --settings BAU

# With carbon tax
climapan-run --settings CT --plot

# Multiple runs
climapan-run --noOfRuns 5

# Help
climapan-run --help
```

#### Complete Command Line Arguments

The `run_sim` script supports the following arguments:

| Argument | Short | Type | Default | Description |
|----------|-------|------|---------|-------------|
| `--noOfRuns` | `-n` | int | 1 | Number of simulation runs to execute |
| `--settings` | `-s` | str | "BAU" | Economic scenario: `BAU`, `CT`, `CTRa`, `CTRb`, `CTRc`, `CTRd` |
| `--covidSettings` | `-c` | str | None | COVID scenario: `BAU`, `DIST`, `LOCK`, `VAX` |
| `--climateDamage` | `-d` | str | "AggPop" | Climate damage type: `AggPop`, `Idiosyncratic`, or `None` |
| `--extractedVarListPathNpy` | `-l` | str | None | Path to text file with variables to extract as numpy files |
| `--extractedVarListPathCsv` | `-v` | str | None | Path to text file with variables to extract as CSV files |
| `--plot` | `-p` | flag | False | Generate plots of simulation results |

#### Advanced Examples

```bash
# Single run with carbon tax and plotting
climapan-run -s CT -p

# Multiple runs with COVID lockdown scenario
climapan-run -n 10 -s BAU -c LOCK

# Full scenario with climate damage and plotting
climapan-run -s CTRa -c VAX -d AggPop -p

# Extract specific variables to separate files
climapan-run -s CT -l variables_list.txt -v output_vars.txt -p

# Complex multi-parameter scenario
climapan-run -n 5 -s CTRb -c DIST -d Idiosyncratic -p

# Scenario without climate damage
climapan-run -s CT -c BAU -d None -p
```

#### Scenario Descriptions

**Economic Settings (`--settings`)**:
- `BAU`: Business as usual (baseline scenario)
- `CT`: Carbon tax implementation
- `CTRa`: Carbon tax with revenue recycling option A
- `CTRb`: Carbon tax with revenue recycling option B  
- `CTRc`: Carbon tax with revenue recycling option C
- `CTRd`: Carbon tax with revenue recycling option D

**COVID Settings (`--covidSettings`)**:
- `BAU`: COVID baseline scenario
- `DIST`: Social distancing measures
- `LOCK`: Lockdown implementation
- `VAX`: Vaccination rollout scenario

**Climate Damage Settings (`--climateDamage`)**:
- `AggPop`: Aggregate population-level climate damage
- `Idiosyncratic`: Individual-level climate damage variation
- `None`: No climate damage effects

#### Variable Extraction

To extract specific model variables to separate files, create a text file with variable names (one per line):

```bash
# variables_list.txt
GDP
UnemploymentRate
InflationRate
Consumption
Wage
TotalTaxes
BankDataWriter
```

Then use:
```bash
climapan-run -s CT -l variables_list.txt -v variables_list.txt -p
```

## Key Parameters

- **Economic Settings**: `'BAU'`, `'CT'`, `'CTRa'`, `'CTRb'`, `'CTRc'`, `'CTRd'`
- **COVID Settings**: `None`, `'BAU'`, `'DIST'`, `'LOCK'`, `'VAX'`
- **Climate Module**: Enable/disable with `climateModuleFlag`
- **Simulation Length**: Set `steps` (**daily** time steps; metrics recorded monthly)
- **Seed**: `seed` — CliMaPan also seeds process-global `np.random` for reproducibility

## Model Features

- **Agents**: Consumers, firms, banks, government with comprehensive lifecycle documentation
- **AMBER backend**: Columnar Polars agent store (`ambr≥0.4.7`)
- **Climate Integration**: Climate shocks and economic impacts with detailed step-by-step dynamics
- **Pandemic Dynamics**: COVID-19 effects on economic activity with SEIR-like progression
- **Policy Analysis**: Carbon taxes, fiscal policies with clear implementation details
- **Calibration**: Autocorrelation-oriented matching to German macro series
- **Flexible Scenarios**: Various economic and environmental conditions
- **Well-Documented Codebase**: Extensive inline documentation explaining agent behavior, simulation flow, and component interactions

## AMBER compatibility & verification

| Topic | Status (ambr **0.4.7**) |
|--------|-------------------------|
| Dependency floor | `ambr>=0.4.7` in `requirements.txt`, `setup.py`, `pyproject.toml` |
| Results API | `results["model"]` / `results["agents"]` (Polars); `single_run` → AgentPy-style wrapper |
| Monthly metrics | Recorded when calendar day of `tomorrow` is `1` |
| **Vectorized vs OOP modes** | **Identical end results** for `EconModel` (same seed; full model + agent frames) |
| Automated tests | Full `pytest tests/` + `run_all_tests.py --fast` pass |
| Deprecations (until AMBER 1.0) | `Model.record`, `AgentList.select` still work; prefer `record_model` / `agents.where` later |

Optional mode selection (defaults to vectorized):

```python
model = EconModel(params)
results = model.cpu(mode="vectorized").run(mode="vectorized")
# or: model.cpu(mode="oop").run(mode="oop")
```

CliMaPan implements a single `step()` used by both AMBER modes—there is no separate vectorized economics path that can diverge.

More detail: [docs/amber.rst](docs/amber.rst).

## Calibration

Script: `climapan_lab/calibrate_model.py`  
Target: `climapan_lab/data/Germany9122.csv`  
Best params: `climapan_lab/optimized_params.py`  
Trial log: `climapan_lab/calibration_results.json`

**Objective** (lower is better): mean over metrics of  
`0.6·ACF_MSE + 0.25·CV_distance + 0.15·trend_distance`  
(absolute GDP levels are **not** matched by design).

**Re-score under ambr 0.4.7** (`n_years=5`, full agent scale):

| Configuration | Objective |
|---------------|-----------|
| `optimized_params` | **0.00690** (best) |
| baseline defaults | 0.01440 |
| random sample | 0.01765 |
| PARAM_SPACE midpoint | 0.02354 |

### Known limitations

1. **ACF is inert for 5-year runs** — `compute_autocorrelation` returns zeros when `n < max_lag+2` (default lag 5). With `n_years=5`, only CV + trend matter.
2. **Scale / units** — sim GDP ≪ German GDP; unemployment is ~fraction vs data in percent points; climate CO₂ series use different scales/definitions.
3. **Unemployment dynamics** — nearly flat in evaluated runs.
4. **Historical search** in `calibration_results.json` is thin (10 trials); treat optimized params as a candidate.

Full write-up: [docs/calibration.rst](docs/calibration.rst).  
Machine-readable re-score: `climapan_lab/calibration_eval_ambr047.json`.

## Example Scenarios

```python
# Carbon tax scenario
params['settings'] = 'CT'
params['co2_tax'] = 0.05
params['climateModuleFlag'] = True

# Pandemic lockdown scenario  
params['covid_settings'] = 'LOCK'
params['lockdown_scale'] = 0.7

# Business as usual
params['settings'] = 'BAU'
params['covid_settings'] = None
```

## Testing

```bash
# Full suite
python -m pytest tests/ -v

# Fast custom runner (excludes heavy stress paths)
cd tests && python run_all_tests.py --fast

# By module
python -m pytest tests/test_basic_functionality.py -v
python -m pytest tests/test_model_components.py -v
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_examples.py -v
python -m pytest tests/test_performance.py -v
```

### Test categories
- **Basic functionality** — model creation, short runs, parameters
- **Model components** — agents, climate/COVID/scenario toggles, data collection
- **Integration** — end-to-end `single_run`, multi-scenario, CLI
- **Examples** — imports and path hygiene
- **Performance** — scaling and timing budgets

**Tip:** CI runs are short (few steps) and may only assert a non-empty results frame. To verify monthly metrics (e.g. `GDP`), run ≥ ~40 steps so a month boundary is crossed.

## Documentation

| Doc | Content |
|-----|---------|
| [docs/installation.rst](docs/installation.rst) | Install & dependencies |
| [docs/quickstart.rst](docs/quickstart.rst) | First simulation |
| [docs/amber.rst](docs/amber.rst) | AMBER API, recording, vectorized/OOP verification |
| [docs/calibration.rst](docs/calibration.rst) | Calibration pipeline & evaluation |
| [docs/climate.rst](docs/climate.rst) | Climate module |
| [docs/odd_protocol.rst](docs/odd_protocol.rst) | ODD+D model description |
| [CHANGELOG.md](CHANGELOG.md) | Release history |

Build Sphinx HTML (optional):

```bash
cd docs && make html
```

## CI/CD

GitHub Actions:

- **CI** — quick checks on every commit
- **Tests** — matrix on **Python 3.9–3.12** (`ambr` from `requirements.txt`)
- **Security** — dependency audits
- **Release** — version tags

See [`.github/README.md`](.github/README.md) if present for workflow details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Citation

```bibtex
@article{d2025climapan,
  title={CliMaPan-Lab: An open-source Python framework for agent-based macroeconomic simulation of climate-and pandemic-related systemic risks},
  author={D’Orazio, Paola and Pham, Anh-Duy and Nguyen, Son Hong},
  journal={SoftwareX},
  volume={32},
  pages={102408},
  year={2025},
  publisher={Elsevier}
}
```
