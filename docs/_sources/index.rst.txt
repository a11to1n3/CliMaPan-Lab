CliMaPan-Lab Documentation
==========================

.. image:: https://img.shields.io/badge/python-3.9+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.9+

.. image:: https://img.shields.io/badge/ambr-%3E%3D0.4.7-green.svg
   :target: https://pypi.org/project/ambr/
   :alt: ambr >= 0.4.7

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

.. image:: https://github.com/a11to1n3/CliMaPan-Lab/workflows/CI/badge.svg
   :target: https://github.com/a11to1n3/CliMaPan-Lab/actions
   :alt: CI Status

Welcome to CliMaPan-Lab
-----------------------

CliMaPan-Lab is a comprehensive agent-based economic modeling framework that integrates 
climate change and pandemic dynamics. This documentation provides detailed information 
about installation, usage, API reference, and examples.

**Runtime:** Python ≥ 3.9 and AMBER (``ambr``) ≥ 0.4.7.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   climate
   amber
   calibration

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index

.. toctree::
   :maxdepth: 2
   :caption: Model Documentation

   odd_protocol

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog
   license

Key Features
------------

* **Agent-Based Modeling**: Comprehensive economic agents including consumers, firms, banks, and government
* **AMBER backend**: Columnar agent store (Polars) via ``ambr>=0.4.7``; vectorized and OOP modes yield identical end results for this model
* **Climate Integration**: Climate shocks and economic impacts modeling with detailed step-by-step dynamics
* **Pandemic Dynamics**: COVID-19 effects on economic activity with SEIR-like disease progression
* **Policy Analysis**: Carbon taxes, fiscal policies, and intervention scenarios
* **Calibration**: Autocorrelation-oriented matching to German macro series (see :doc:`calibration`)
* **Flexible Scenarios**: Various economic and environmental conditions
* **Comprehensive Testing**: 50+ automated tests across unit, integration, and performance suites

Quick Links
-----------

* :doc:`installation` - Get started with installing CliMaPan-Lab
* :doc:`quickstart` - Run your first simulation
* :doc:`amber` - AMBER results API, monthly recording, mode verification
* :doc:`calibration` - Calibration pipeline and evaluation notes
* :doc:`api/index` - Complete API documentation

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 