Economic Agents
===============

CliMaPan-Lab includes several types of economic agents with comprehensive inline documentation 
explaining their behavior, state management, and lifecycle within the simulation.

Consumers
---------

The Consumer agent represents households/individuals with detailed lifecycle documentation 
covering income sources, consumption decisions, wealth management, employment status, 
and epidemiological state progression.

Key Features:
* **Income Management**: Wages, dividends, interest, and transfers
* **Consumption Decisions**: Based on wealth and subsistence needs
* **Employment Dynamics**: Hiring, firing, and firm attachment
* **COVID Progression**: SEIR-like disease dynamics by age group
* **Climate Effects**: Wealth impacts from climate shocks

.. currentmodule:: climapan_lab.src.consumers

.. autoclass:: Consumer
   :members:
   :undoc-members:
   :show-inheritance:

Firms
-----

All firm types inherit from GoodsFirmBase which provides comprehensive documentation 
covering the monthly production lifecycle, financial management, labor relations, 
and policy interactions.

Firm Lifecycle (Monthly):
1. **Planning**: Set production targets and budget requirements
2. **Hiring**: Labor market participation and wage calculation
3. **Production**: Physical production function execution
4. **Sales**: Market transactions and price setting
5. **Settlement**: Cost accounting, profit calculation, capital updates
6. **Taxes/Dividends**: Policy compliance and owner income distribution

Consumer Goods Firms
~~~~~~~~~~~~~~~~~~~~

Produce final consumption goods with demand-driven production planning.

.. currentmodule:: climapan_lab.src.firms

.. autoclass:: ConsumerGoodsFirm
   :members:
   :undoc-members:
   :show-inheritance:

Capital Goods Firms
~~~~~~~~~~~~~~~~~~~

Produce capital equipment for other firms with investment-driven demand.

.. autoclass:: CapitalGoodsFirm
   :members:
   :undoc-members:
   :show-inheritance:

Energy Firms
~~~~~~~~~~~~

Provide energy inputs to production with environmental impact differentiation.

.. autoclass:: GreenEnergyFirm
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: BrownEnergyFirm
   :members:
   :undoc-members:
   :show-inheritance:

Banks
-----

.. currentmodule:: climapan_lab.src.banks

.. autoclass:: Bank
   :members:
   :undoc-members:
   :show-inheritance:

Government
----------

.. currentmodule:: climapan_lab.src.governments

.. autoclass:: Government
   :members:
   :undoc-members:
   :show-inheritance:

Climate Module
--------------

The Climate module provides comprehensive step-by-step documentation of climate dynamics 
including emissions tracking, CO₂ concentration updates, temperature changes, and 
economic impact calculations.

Climate Process (Monthly):
1. **Emissions Aggregation**: Collect and scale emissions from all firms
2. **Carbon Cycle Update**: CO₂ concentration with accumulation and mean-reversion
3. **Temperature Dynamics**: Radiative forcing and e-folding temperature updates
4. **Shock Detection**: Climate threshold monitoring and trigger activation
5. **Damage Calculation**: Economic and mortality impact assessment

Shock Types:
* **Aggregate Population**: Population-level mortality impacts
* **Idiosyncratic**: Individual-level survival calculations

.. currentmodule:: climapan_lab.src.climate

.. autoclass:: Climate
   :members:
   :undoc-members:
   :show-inheritance: 