Changelog
=========

Version 0.0.4 (2025-08-19)
---------------------------

**Major Documentation Enhancement:**

* Added comprehensive ODD+D Protocol documentation following established standards for agent-based models
* Created formal model specification with mathematical formalization of agent decision rules
* Added detailed parameter tables with values and sources
* Documented model limitations and assumptions for transparency
* Added output format specifications and acronym reference

**Code Quality & Standards:**

* Applied comprehensive Black formatting to entire codebase (58 files reformatted)
* Major documentation overhaul with comprehensive inline documentation:

  - Climate Module: Detailed step-by-step climate dynamics documentation
  - Consumer Agent: Complete lifecycle and state management documentation
  - Economic Model: Full simulation flow and component interaction documentation
  - Firm Base Classes: Comprehensive production, finance, and lifecycle documentation
  - Main Runner: Enhanced script-level documentation with feature descriptions

* Improved code organization with better separation of concerns
* Standardized coding conventions following Python best practices

**Project Metadata:**

* Updated contact email to institutional address: anh-duy.pham@uni-wuerzburg.de
* Enhanced project metadata with correct repository URLs and documentation links
* Updated version references across all configuration files

**Package Installation:**

* Fixed setup.py dependencies to include all packages from requirements.txt
* Updated pyproject.toml with complete dependency list
* Ensured consistent package installation across different installation methods

Version 0.0.3 (2025-07-21)
---------------------------

**Performance Improvements:**

* Fixed infinite loop bug in EconModel.setup() that caused tests to hang
* Optimized integration tests to complete in ~4 seconds
* Reduced test parameters for faster CI/CD execution

**Bug Fixes:**

* Fixed missing return statement in single_run() function
* Fixed variable scope issues with varListNpy and varListCsv
* Fixed firm energy type assignment to prevent infinite loops

Version 0.0.2 (2025-07-20)
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

Version 0.0.1 (2025-07-15)
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