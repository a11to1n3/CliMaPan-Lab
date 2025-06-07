Installation
============

Requirements
------------

* Python 3.8 or higher
* pip package manager

Dependencies
------------

CliMaPan-Lab requires the following Python packages:

Core Dependencies
~~~~~~~~~~~~~~~~~

* **numpy** (>=1.21.0) - Numerical computing
* **pandas** (>=1.3.0) - Data manipulation and analysis
* **matplotlib** (>=3.5.0) - Plotting and visualization
* **jaxabm** (>=0.1.0) - Agent-based modeling framework
* **scikit-learn** (>=1.0.0) - Machine learning utilities
* **scipy** (>=1.7.0) - Scientific computing
* **joblib** (>=1.1.0) - Parallel computing
* **salib** (>=1.4.0) - Sensitivity analysis
* **networkx** (>=2.6.0) - Network analysis
* **pathos** (>=0.2.8) - Parallel processing
* **dill** (>=0.3.4) - Serialization
* **h5py** (>=3.7.0) - HDF5 file handling
* **statsmodels** (>=0.13.0) - Statistical analysis utilities
* **plotly** (>=5.0) - Interactive plotting

Installation Methods
--------------------

Install from Source (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/a11to1n3/CliMaPan-Lab.git
   cd CliMaPan-Lab
   pip install -e .

This method is recommended for development and to get the latest features.

Install from GitHub
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install git+https://github.com/a11to1n3/CliMaPan-Lab.git

Install in Development Mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For developers who want to contribute to the project:

.. code-block:: bash

   git clone https://github.com/a11to1n3/CliMaPan-Lab.git
   cd CliMaPan-Lab
   pip install -e ".[dev]"

This installs additional development dependencies including testing and documentation tools.

Virtual Environment (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's recommended to install CliMaPan-Lab in a virtual environment:

.. code-block:: bash

   python -m venv climapan_env
   source climapan_env/bin/activate  # On Windows: climapan_env\Scripts\activate
   pip install git+https://github.com/a11to1n3/CliMaPan-Lab.git

Verify Installation
-------------------

To verify that CliMaPan-Lab is installed correctly:

.. code-block:: python

   import climapan_lab
   print(f"CliMaPan-Lab version: {climapan_lab.__version__}")

   # Test basic functionality
   from climapan_lab.model import EconModel
   from climapan_lab.base_params import economic_params
   
   print("Installation successful!")

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import Error: No module named 'jaxabm'**

This usually means the dependencies weren't installed properly. Try:

.. code-block:: bash

   pip install -r requirements.txt

**Permission Error during installation**

Use the ``--user`` flag:

.. code-block:: bash

   pip install --user git+https://github.com/a11to1n3/CliMaPan-Lab.git

**Installation fails on Windows**

Some scientific packages require compilation. Install from conda-forge:

.. code-block:: bash

   conda install -c conda-forge numpy pandas matplotlib scipy
   pip install git+https://github.com/a11to1n3/CliMaPan-Lab.git

System-specific Notes
~~~~~~~~~~~~~~~~~~~~~

**macOS**

You may need to install Xcode command line tools:

.. code-block:: bash

   xcode-select --install

**Linux**

You may need to install development headers:

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt-get install python3-dev build-essential
   
   # CentOS/RHEL
   sudo yum install python3-devel gcc gcc-c++

**Windows**

Consider using Anaconda or Miniconda for easier dependency management. 