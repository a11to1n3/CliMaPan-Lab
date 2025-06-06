Climate Module
==============

The CliMaPan-Lab climate module simulates environmental effects and their economic impacts. This module has been streamlined to focus on two main climate damage mechanisms plus an option to disable climate effects entirely.

Climate Damage Types
--------------------

AggPop (Aggregate Population)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aggregate population-level climate damage affects the entire economy uniformly:

- **Description**: Climate shocks impact all economic agents equally
- **Use case**: Modeling economy-wide climate effects
- **Implementation**: Uniform damage multipliers applied across all sectors

.. code-block:: python

   params['climateModuleFlag'] = True
   params['climateShockMode'] = 'AggPop'

Idiosyncratic
~~~~~~~~~~~~~

Individual-level climate damage with heterogeneous effects:

- **Description**: Climate shocks vary across individual agents and sectors
- **Use case**: Modeling differential climate vulnerability
- **Implementation**: Varied damage based on agent characteristics

.. code-block:: python

   params['climateModuleFlag'] = True
   params['climateShockMode'] = 'Idiosyncratic'

None
~~~~

Disables climate damage effects while maintaining other climate calculations:

- **Description**: No economic damage from climate shocks
- **Use case**: Baseline scenarios without climate impacts
- **Implementation**: Climate module tracks emissions but applies no damage

.. code-block:: python

   params['climateModuleFlag'] = True
   params['climateShockMode'] = 'None'

Climate Parameters
------------------

Key climate-related parameters:

.. code-block:: python

   # Enable/disable climate module
   'climateModuleFlag': True,
   
   # Climate damage type
   'climateShockMode': 'AggPop',  # or 'Idiosyncratic' or 'None'
   
   # Climate shock timing
   'climate_shock_start': 120,  # months until shocks activate
   
   # Emission intensities
   'climateZetaGreen': 0.01,    # green energy emission intensity
   'climateZetaBrown': 0.5,     # brown energy emission intensity
   
   # Climate sensitivity parameters
   'climateSensitivity': 6.90625,
   'climateT0': 0,              # initial temperature
   
   # Damage parameters
   'climateAlpha_d': 0.05,      # benchmark damage
   'climateSigma_d': 0.9,       # storm sensitivity
   'psi_h': 0.1,                # household damage parameter
   'psi_f_g': 0.15,             # green firm damage parameter
   'psi_f_b': 0.25,             # brown firm damage parameter

Climate Variables
-----------------

The climate module tracks several key variables:

- **CO2 Emissions**: Total and sectoral emissions
- **CO2 Concentration**: Atmospheric concentration levels
- **Temperature**: Global temperature anomaly
- **Radiative Forcing**: Climate forcing effects
- **Climate Damage**: Economic damage from climate effects

Command Line Usage
------------------

Use the climate damage options via command line:

.. code-block:: bash

   # Run with aggregate population damage
   climapan-run --climateDamage AggPop --settings CT
   
   # Run with idiosyncratic damage
   climapan-run --climateDamage Idiosyncratic --settings CTRa
   
   # Run without climate damage
   climapan-run --climateDamage None --settings BAU

Integration with Economic Scenarios
-----------------------------------

Climate damage works with all economic scenarios:

Carbon Tax Scenarios
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Carbon tax with aggregate climate damage
   params = {
       'settings': 'CT',
       'climateModuleFlag': True,
       'climateShockMode': 'AggPop',
       'co2_tax': 0.05
   }

   # Carbon tax with revenue recycling and idiosyncratic damage
   params = {
       'settings': 'CTRa', 
       'climateModuleFlag': True,
       'climateShockMode': 'Idiosyncratic',
       'co2_tax': 0.03
   }

COVID-Climate Interactions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Combined pandemic and climate scenario
   params = {
       'settings': 'CT',
       'covid_settings': 'LOCK',
       'climateModuleFlag': True,
       'climateShockMode': 'AggPop'
   }

Historical Context
------------------

.. note::
   Previous versions of CliMaPan-Lab included flood-specific climate damage mechanisms. 
   These have been removed and consolidated into the more flexible AggPop and 
   Idiosyncratic damage types, which can represent various climate impacts including 
   floods, droughts, storms, and other climate events.

Best Practices
--------------

1. **Start with AggPop**: For initial explorations, use aggregate damage for simplicity
2. **Use Idiosyncratic for detailed analysis**: When studying inequality effects
3. **Calibrate carefully**: Climate parameters should be calibrated to real-world data
4. **Consider interactions**: Climate effects interact with other policies and shocks
5. **Validate results**: Compare outputs with and without climate effects

Example Analysis
----------------

.. code-block:: python

   import matplotlib.pyplot as plt
   from climapan_lab.model import EconModel
   from climapan_lab.base_params import economic_params

   # Run scenarios with different climate damage types
   scenarios = ['None', 'AggPop', 'Idiosyncratic']
   results = {}
   
   for scenario in scenarios:
       params = economic_params.copy()
       params['climateModuleFlag'] = True
       params['climateShockMode'] = scenario
       params['settings'] = 'CT'
       params['steps'] = 240
       
       model = EconModel(params)
       results[scenario] = model.run()
   
   # Compare GDP trajectories
   plt.figure(figsize=(10, 6))
   for scenario, result in results.items():
       df = result.variables.EconModel
       plt.plot(df['GDP'], label=f'Climate Damage: {scenario}')
   
   plt.title('GDP Under Different Climate Damage Scenarios')
   plt.xlabel('Time Steps (Months)')
   plt.ylabel('GDP')
   plt.legend()
   plt.show() 