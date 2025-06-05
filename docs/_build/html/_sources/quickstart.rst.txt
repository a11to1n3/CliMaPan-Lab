Quick Start Guide
=================

This guide will help you run your first CliMaPan-Lab simulation in just a few minutes.

Basic Simulation
----------------

Here's how to run a basic simulation with default parameters:

.. code-block:: python

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
   print(f"Final Unemployment Rate: {df['unemployment_rate'].iloc[-1]}")

Running Different Scenarios
----------------------------

Business as Usual (BAU)
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   params = economic_params.copy()
   params['settings'] = 'BAU'
   params['steps'] = 120
   
   model = EconModel(params)
   results = model.run()

Carbon Tax Scenario
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   params = economic_params.copy()
   params['settings'] = 'CT'  # Carbon Tax
   params['co2_tax'] = 0.05
   params['climateModuleFlag'] = True
   params['steps'] = 120
   
   model = EconModel(params)
   results = model.run()

Pandemic Scenario
~~~~~~~~~~~~~~~~~

.. code-block:: python

   params = economic_params.copy()
   params['covid_settings'] = 'LOCK'  # Lockdown
   params['lockdown_scale'] = 0.7
   params['steps'] = 120
   
   model = EconModel(params)
   results = model.run()

Combined Climate and Pandemic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   params = economic_params.copy()
   params['settings'] = 'CT'
   params['covid_settings'] = 'DIST'  # Social distancing
   params['climateModuleFlag'] = True
   params['co2_tax'] = 0.03
   params['steps'] = 120
   
   model = EconModel(params)
   results = model.run()

Command Line Interface
----------------------

You can also run simulations from the command line:

Basic Run
~~~~~~~~~

.. code-block:: bash

   climapan-run --settings BAU

With Visualization
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   climapan-run --settings CT --plot

Multiple Runs
~~~~~~~~~~~~~

.. code-block:: bash

   climapan-run --noOfRuns 5 --settings BAU

Custom Parameters
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   climapan-run --settings CT --steps 240 --plot

Analyzing Results
-----------------

The simulation results are stored in a pandas DataFrame:

.. code-block:: python

   # Run simulation
   model = EconModel(params)
   results = model.run()
   
   # Get main variables
   df = results.variables.EconModel
   
   # Key economic indicators
   print("Key Economic Indicators:")
   print(f"Initial GDP: {df['GDP'].iloc[0]:.2f}")
   print(f"Final GDP: {df['GDP'].iloc[-1]:.2f}")
   print(f"GDP Growth: {((df['GDP'].iloc[-1] / df['GDP'].iloc[0]) - 1) * 100:.2f}%")
   
   # Environmental indicators (if climate module enabled)
   if 'climateModuleFlag' in params and params['climateModuleFlag']:
       print(f"Final CO2 Emissions: {df['total_emissions'].iloc[-1]:.2f}")
   
   # Labor market
   print(f"Final Unemployment Rate: {df['unemployment_rate'].iloc[-1]:.2f}%")

Basic Visualization
-------------------

Create simple plots of key variables:

.. code-block:: python

   import matplotlib.pyplot as plt
   
   # Run simulation
   model = EconModel(params)
   results = model.run()
   df = results.variables.EconModel
   
   # Create subplots
   fig, axes = plt.subplots(2, 2, figsize=(12, 8))
   
   # GDP over time
   axes[0, 0].plot(df['GDP'])
   axes[0, 0].set_title('GDP Over Time')
   axes[0, 0].set_ylabel('GDP')
   
   # Unemployment rate
   axes[0, 1].plot(df['unemployment_rate'])
   axes[0, 1].set_title('Unemployment Rate')
   axes[0, 1].set_ylabel('Rate (%)')
   
   # Inflation
   axes[1, 0].plot(df['inflation'])
   axes[1, 0].set_title('Inflation Rate')
   axes[1, 0].set_ylabel('Rate (%)')
   
   # If climate module is enabled
   if 'total_emissions' in df.columns:
       axes[1, 1].plot(df['total_emissions'])
       axes[1, 1].set_title('CO2 Emissions')
       axes[1, 1].set_ylabel('Emissions')
   else:
       axes[1, 1].text(0.5, 0.5, 'Climate module\nnot enabled', 
                      ha='center', va='center', transform=axes[1, 1].transAxes)
   
   plt.tight_layout()
   plt.show()

Key Parameters
--------------

Here are the most important parameters to understand:

Economic Settings
~~~~~~~~~~~~~~~~~

* **'BAU'** - Business as Usual (baseline scenario)
* **'CT'** - Carbon Tax
* **'CTRa', 'CTRb', 'CTRc', 'CTRd'** - Carbon Tax with different recycling mechanisms

COVID Settings
~~~~~~~~~~~~~~

* **None** - No pandemic effects
* **'BAU'** - Basic pandemic scenario
* **'DIST'** - Social distancing measures
* **'LOCK'** - Lockdown measures
* **'VAX'** - Vaccination scenario

Climate Settings
~~~~~~~~~~~~~~~~

* **climateModuleFlag** - Enable/disable climate module
* **co2_tax** - Carbon tax rate (e.g., 0.05 for 5%)

Simulation Settings
~~~~~~~~~~~~~~~~~~~

* **steps** - Number of time steps (monthly, e.g., 120 = 10 years)
* **seed** - Random seed for reproducibility

Next Steps
----------

* Read the :doc:`user_guide/model_overview` for detailed model explanation
* Explore :doc:`examples/index` for more complex scenarios
* Check the :doc:`api/index` for complete API documentation
* Learn about :doc:`user_guide/parameters` for advanced parameter tuning 