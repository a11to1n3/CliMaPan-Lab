Changelog
=========

Version 0.0.2 (2024-12-05)
---------------------------

**Breaking Changes:**

* Removed flood-specific climate damage mechanisms
* Deleted Climate_Flood.py module and related parameters
* Cleaned up legacy Bank_revise*.py and Climate_old.py files

**Climate Module Updates:**

* Streamlined climate damage to three options: AggPop, Idiosyncratic, None
* Updated default climate damage from "Flood" to "AggPop" 
* Removed flood parameters: climate_flood_omega, flood_delta
* Enhanced climate documentation with comprehensive usage guide

**Documentation:**

* Added dedicated climate module documentation
* Updated quickstart guide with current climate damage options
* Enhanced CLI documentation with accurate parameter descriptions
* Added climate damage examples and best practices

**Codebase Cleanup:**

* Removed unused revision files (Bank_revise*.py)
* Removed outdated backup files (Climate_old.py)
* Simplified climate shock implementation in models.py
* Updated result folder naming from "FLOOD" to "CLIMATE"

Version 0.0.1 (2024-12-05)
---------------------------

Initial release of CliMaPan-Lab.

**Features:**

* Agent-based economic modeling framework
* Climate change integration
* Pandemic dynamics modeling
* Multiple policy scenarios (Carbon tax, COVID interventions)
* Comprehensive test suite (60+ tests)
* Command-line interface
* Visualization utilities
* Full API documentation

**Agents:**

* Consumers with adaptive behavior
* Consumer goods firms
* Capital goods firms
* Green and brown energy firms
* Banks with lending mechanisms
* Government with fiscal policies

**Modules:**

* Climate module with environmental impacts
* COVID module with pandemic effects
* Economic interactions and markets
* Parameter management system

**Testing:**

* Basic functionality tests
* Model component tests
* Integration workflow tests
* Example script validation
* Performance and scalability tests 