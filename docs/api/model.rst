Economic Model
==============

The main economic model class that orchestrates the agent-based simulation.

.. currentmodule:: climapan_lab.src.models

.. autoclass:: EconModel
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Model Components
----------------

The EconModel integrates several key components:

* **Agents**: Consumers, firms, banks, government
* **Climate Module**: Environmental effects and climate policies
* **COVID Module**: Pandemic dynamics and interventions
* **Economic Mechanisms**: Markets, pricing, employment

Key Methods
-----------

.. automethod:: EconModel.__init__
.. automethod:: EconModel.setup
.. automethod:: EconModel.step
.. automethod:: EconModel.run 