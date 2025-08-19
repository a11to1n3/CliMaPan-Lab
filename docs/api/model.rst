Economic Model
==============

The main economic model class that orchestrates the agent-based simulation with comprehensive 
inline documentation explaining the simulation flow and component interactions.

.. currentmodule:: climapan_lab.src.models

.. autoclass:: EconModel
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Model Architecture
------------------

The EconModel follows a well-documented daily timestep approach with monthly economic cycles:

* **Daily Steps**: Each model step represents one day with COVID progression
* **Monthly Cycles**: Economic activities (production, hiring, sales) occur monthly
* **Climate Integration**: Step-by-step climate dynamics with emissions, temperature, and shocks
* **Pandemic Dynamics**: SEIR-like disease progression with age-group specific transitions

Model Components
----------------

The EconModel integrates several key components with detailed documentation:

* **Agents**: Consumers, firms, banks, government with comprehensive lifecycle documentation
* **Climate Module**: Environmental effects and climate policies with detailed step-by-step dynamics
* **COVID Module**: Pandemic dynamics and interventions with SEIR progression
* **Economic Mechanisms**: Markets, pricing, employment with clear implementation details

Key Methods
-----------

.. automethod:: EconModel.__init__
.. automethod:: EconModel.setup
.. automethod:: EconModel.step
.. automethod:: EconModel.run 