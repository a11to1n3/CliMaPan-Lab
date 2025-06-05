# CliMaPan-Lab: Climate-Pandemic Economic Modeling Laboratory

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/your-username/CliMaPan-Lab/workflows/CI/badge.svg)](https://github.com/your-username/CliMaPan-Lab/actions)
[![Tests](https://github.com/your-username/CliMaPan-Lab/workflows/Tests/badge.svg)](https://github.com/your-username/CliMaPan-Lab/actions)

CliMaPan-Lab is an agent-based economic modeling framework for studying interactions between climate change, pandemic dynamics, and economic systems.

## Installation

```bash
# Install from source
git clone https://github.com/your-username/CliMaPan-Lab.git
cd CliMaPan-Lab
pip install -e .

# Or install directly from GitHub
pip install git+https://github.com/your-username/CliMaPan-Lab.git
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
  year={2024},
  url={https://github.com/your-username/CliMaPan-Lab}
}
```
