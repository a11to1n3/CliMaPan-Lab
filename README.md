# CliMaPan-Lab: Climate-Pandemic Economic Modeling Laboratory

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/a11to1n3/CliMaPan-Lab/workflows/Tests/badge.svg)](https://github.com/a11to1n3/CliMaPan-Lab/actions)

CliMaPan-Lab is an agent-based economic modeling framework for studying interactions between climate change, pandemic dynamics, and economic systems.

## Installation

```bash
# Install from source
git clone https://github.com/a11to1n3/CliMaPan-Lab.git
cd CliMaPan-Lab
pip install -e .

# Or install directly from GitHub
pip install git+https://github.com/a11to1n3/CliMaPan-Lab.git
```

## Quick Start

```python
from climapan_lab.model import EconModel
from climapan_lab.base_params import economic_params

# Create model with default parameters
params = economic_params.copy()
params['steps'] = 120  # 10 years (monthly steps)

# Run simulation
model = EconModel(params)
results = model.run()

# Access results
df = results.variables.EconModel
print(f"Final GDP: {df['GDP'].iloc[-1]}")
```

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
- **Simulation Length**: Set `steps` (monthly time steps)

## Model Features

- **Agents**: Consumers, firms, banks, government
- **Climate Integration**: Climate shocks and economic impacts
- **Pandemic Dynamics**: COVID-19 effects on economic activity
- **Policy Analysis**: Carbon taxes, fiscal policies
- **Flexible Scenarios**: Various economic and environmental conditions

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

CliMaPan-Lab includes a comprehensive test suite with 60+ tests across 5 categories:

```bash
# Run all tests
cd tests
python run_all_tests.py

# Run fast tests (excludes performance tests)
python run_all_tests.py --fast

# Run specific test categories
python -m pytest test_basic_functionality.py -v
python -m pytest test_model_components.py -v
python -m pytest test_integration.py -v
python -m pytest test_examples.py -v
python -m pytest test_performance.py -v
```

### Test Categories
- **Basic Functionality**: Model creation, parameter validation
- **Model Components**: Agent behavior, climate/COVID scenarios
- **Integration**: End-to-end workflows, multi-scenario analysis
- **Examples**: Script validation, import testing
- **Performance**: Benchmarking, memory efficiency, scaling

## CI/CD

The project uses GitHub Actions for automated testing and quality assurance:

- **CI**: Quick checks on every commit (syntax, formatting, basic tests)
- **Tests**: Comprehensive testing on Python 3.8-3.11
- **Security**: Weekly security and dependency audits
- **Release**: Automated releases on version tags

For more details, see [`.github/README.md`](.github/README.md).

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Citation

```bibtex
@software{climapan_lab,
  title={CliMaPan-Lab: Climate-Pandemic Economic Modeling Laboratory},
  author={D'Orazio, Paola and Pham, Anh-Duy and Nguyen, Hong Son},
  year={2024},
  url={https://github.com/your-username/CliMaPan-Lab}
}
```
