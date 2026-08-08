Contributing to CliMaPan-Lab
============================

We welcome contributions to CliMaPan-Lab! This guide will help you get started.

Development Setup
-----------------

1. Fork the repository on GitHub
2. Clone your fork locally:

.. code-block:: bash

   git clone https://github.com/YOUR_USERNAME/CliMaPan-Lab.git
   cd CliMaPan-Lab

3. Install in development mode:

.. code-block:: bash

   pip install -e ".[dev]"

4. Install pre-commit hooks:

.. code-block:: bash

   pre-commit install

Running Tests
-------------

Run the full test suite:

.. code-block:: bash

   cd tests
   python run_all_tests.py

Run specific test categories:

.. code-block:: bash

   python -m pytest test_basic_functionality.py -v
   python -m pytest test_model_components.py -v

Code Style
----------

We use several tools to maintain code quality:

* **Black** for code formatting
* **isort** for import sorting
* **flake8** for linting

Run formatting checks:

.. code-block:: bash

   black --check .
   isort --check-only .
   flake8 .

Fix formatting issues:

.. code-block:: bash

   black .
   isort .

Submitting Changes
------------------

1. Create a new branch for your feature:

.. code-block:: bash

   git checkout -b feature-name

2. Make your changes and add tests
3. Run the test suite to ensure everything works
4. Commit your changes with a descriptive message
5. Push to your fork and create a pull request

Documentation
-------------

Documentation is built with Sphinx. To build locally:

.. code-block:: bash

   cd docs
   make html

The documentation will be available in ``docs/_build/html/``.

Reporting Issues
----------------

Please use the GitHub issue tracker to report bugs or request features.
Include as much detail as possible:

* Python version
* Operating system
* Complete error traceback
* Minimal example to reproduce the issue 