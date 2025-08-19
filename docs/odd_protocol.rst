ODD+D Protocol Documentation for CliMaPan-Lab
============================================

This document provides a comprehensive Overview, Design concepts, and Details (ODD) protocol with Decision logic extensions (ODD+D) for the CliMaPan-Lab agent-based model.

**Authors:** Paola D'Orazio, Anh-Duy Pham, Son Hong Nguyen

Overview
--------

Purpose
~~~~~~~

The CliMaPan Lab model simulates macro-financial and socio-environmental effects arising from compound climate and pandemic risks. It integrates epidemiological (SEIR-based), climate (FUND-based), and macroeconomic modules in an agent-based setting to investigate feedback loops, sectoral vulnerabilities, and systemic fragility. The model supports scenario analysis and policy design under deep uncertainty.

Entities, State Variables, and Scales
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Agent types include:

- **Households** (workers, capitalists, energy owners): health state, income, consumption rule, deposits
- **Firms** (consumption, capital, energy): capital stock, productivity, cash reserves, debt
- **Banks**: equity, loans, deposits, capital ratio
- **Government**: budget, taxation rules, activation thresholds for fiscal/health policies
- **Climate and Epidemic Modules**: systemic variables (e.g., temperature, infection states)

**Time scale:** daily steps with monthly economic blocks

**Space:** single-country closed economy (Germany for calibration)

Process Overview and Scheduling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each step executes the following (monthly):

1. Income generation, epidemic transmission, mortality updates
2. Household consumption, savings update
3. Firm production, investment, pricing, credit demand
4. Bank loan allocation, interest pricing
5. Government policy application (e.g., taxes, lockdowns)
6. Update climate indicators (emissions, temperature)

Temporal Granularity
^^^^^^^^^^^^^^^^^^^

The simulation advances in daily steps. COVID transmission, health-state progression, and contact generation run daily.

Stopping Condition
^^^^^^^^^^^^^^^^^^

The simulation runs for a fixed horizon of T days (or M months). No early stopping conditions are used.

Design Concepts (ODD core + ODD+D extensions)
----------------------------------------------

- **Basic Principles**: Post-Keynesian ABM with feedbacks between health, climate, and macro-financial states
- **Emergence**: Systemic crises, sectoral shocks, environmental degradation from micro-decisions
- **Adaptation**: Rule-of-thumb adjustments based on past performance
- **Objectives**: Agents pursue satisficing behavior (not optimization)
- **Learning**: Bounded adaptation; no machine learning or optimization
- **Prediction**: Agents use lagged observations to forecast demand/income
- **Sensing**: Local observations; no perfect foresight
- **Interaction**: Markets (goods, labor, credit, energy), epidemics via network links
- **Stochasticity**: Storm shocks, epidemic states, productivity, firm exit
- **Collectives**: Sector aggregates; no group-level decision-making
- **Observation**: Outputs include GDP, credit volumes, infection rates, emissions
- **Uncertainty Representation**: All stochastic draws use NumPy pseudo random number generator. Runs are reproducible via the parameter ``seed``. Monte Carlo and parameter sweeps are orchestrated from ``run_sim.py``

Decision Logic (ODD+D Extension)
---------------------------------

This section formalizes the decision rules of agents as required by the ODD+D protocol.

Households
~~~~~~~~~~

**Consumption:**

.. math::

   C^*_h = \bar{C}_x + \alpha Y_h \quad \text{(healthy)} \quad \text{and} \quad C^*_h = \psi C^*_h \quad \text{(if sick)}

**Savings update:**

.. math::

   D_{h,t} = D_{h,t-1}(1+i_d) + Y_{h,t} - C_{h,t}

Firms
~~~~~

**Production and credit demand:**

.. math::

   Q_{f,t} &= f(E_{f,t}, L_{f,t}, K_{f,t}) \\
   \text{If } R_{f,t} < \text{costs} &\Rightarrow \text{apply for loan } L_{f,t} = \max(0, \text{gap})

**Default condition:**

.. math::

   NW_{f,t} < 0 \Rightarrow \text{exit and replacement}

Exit and Replacement
^^^^^^^^^^^^^^^^^^^

Firms with negative net worth or failed loan schedules are marked bankrupt, cleared of outstanding loans, and immediately replaced with new firm while retains current capital. Replacement may switch energy type to preserve sectoral diversity (brown/green share constraints).

Banks
~~~~~

**Credit rule:**

.. math::

   \sum \zeta_{x,t} L_{x,t} \leq \gamma E_{B,t} \quad \text{(capital adequacy)}

**Interest rate:**

.. math::

   i_{x,t} = (1 + \zeta_{x,t})i_{CB} \quad \text{with } i_D < i_{CB} < i_x

Government
~~~~~~~~~~

Rules:

- Lockdowns triggered if infection > θ_I
- Transfers triggered if unemployment > θ_U  
- Emissions taxed if policy active

Pandemic Module
~~~~~~~~~~~~~~~

- **Infection Dynamics:** An extension based on a stochastic SEIR process with network transmission
- **Transmission Probability:** Infection occurs when a susceptible household is connected to an infected individual in the network
- **Health States:** Susceptible, Non-Symptomatic, Mild, Severe, Critical, Recovered, Dead. Mortality won't remove the agent from the model
- **Behavioral Adjustments:** Infected households reduce consumption and labor supply according to parameters ψ (consumption) and sick leave rules
- **Uncertainty:** Stochastic variation in infection outcomes (random draws for exposure, recovery, and mortality)

Bounded Rationality and Uncertainty
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All agents operate under heuristic rules, use partial information, and adjust reactively. No intertemporal optimization.

Details
-------

Initialization
~~~~~~~~~~~~~~

Firms, households, and bank parameters are drawn from stylized distributions. Initial states (e.g., equity, productivity, infection status) are randomized within bounds. Simulation burn-in of 3 years used.

Input Data
~~~~~~~~~~

Macroeconomic indicators (GDP, CPI, labor share) and emissions data from IMF and World Bank. Climate parameters follow FUND model calibration.

Submodels
~~~~~~~~~

- **Households**: Rule-of-thumb consumption, epidemic status adjustment
- **Firms**: Adaptive demand forecasting, CES production, credit constraints
- **Banks**: Risk-weighted credit rationing, threshold-based interest markup
- **Government**: Fiscal responses, emissions regulation toggles
- **Epidemic Module**: Networked SEIR model by age and severity class
- **Climate Module**: CO2 accumulation, temperature forcing, storm mortality

Appendices
----------

Appendix A: Parameter Overview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Key Model Parameters
   :header-rows: 1
   :widths: 15 35 15 15 20

   * - Symbol
     - Description
     - Unit
     - Value
     - Source
   * - α
     - Marginal propensity to consume
     - --
     - 0.6
     - Calibrated
   * - C̄_x
     - Minimum consumption
     - $
     - 400
     - Stylized
   * - ψ
     - Sick consumption reduction
     - --
     - 0.8
     - Assumed
   * - δ_k
     - Capital depreciation rate
     - % per month
     - 20
     - Calibrated
   * - γ
     - Capital buffer ratio
     - --
     - 0.08
     - Regulation
   * - ζ_{x,t}
     - Default probability
     - --
     - [0.01–0.25]
     - Endogenous
   * - θ_I
     - Lockdown infection threshold
     - %
     - 3.0
     - Assumed
   * - θ_U
     - Transfer unemployment threshold
     - %
     - 8.0
     - Assumed

Appendix B: Simulation Configuration and Modularity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Model Configuration
^^^^^^^^^^^^^^^^^^^

The model is modular. Users can activate or deactivate key modules via Boolean flags in the configuration file:

- ``epidemic_module = TRUE``: Activates SEIR network-based epidemic simulation
- ``climate_module = TRUE``: Activates climate damage and temperature dynamics
- ``policy_rules = FLEX``: Enables adaptive fiscal responses to shocks

Shock Dynamics and Event Handling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Climate shocks (e.g., AggPop or Idiosyncratic) are triggered when temperature crosses stochastic thresholds. Epidemic outbreaks emerge endogenously when infection rates exceed calibrated baseline levels. Both shocks include duration and severity components that influence mortality, income, and production.

Appendix C: Epidemic Network Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The epidemic module uses a fixed random network:

- **Topology**: Random Poisson distribution with mean degree calibrated to pre-pandemic contact data
- **Static Structure**: Network remains constant across simulation but varies across Monte Carlo runs
- **Link Type**: Only intra-firm links are assumed for transmission; no inter-firm spread

Appendix D: Model Limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- No international spillovers or trade channels
- Monetary policy is exogenous and does not respond to macro conditions
- Climate policy limited to carbon tax; no green subsidies or ETS
- Health sector capacity and vaccination policies are abstracted
- Firms are homogeneous within sectors; no firm-level innovation or upgrading
- The population is demographically static; no births or migration

Appendix E: Output Format and Data Export
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The model records all relevant micro- and macroeconomic variables monthly in CSV format:

- ``macro_summary.csv``: GDP, unemployment, inflation, emissions, infection rate
- ``firm_panel.csv``: firm-level balance sheets, output, credit usage
- ``household_panel.csv``: income, consumption, deposits, health state
- ``shock_log.csv``: timing and type of shocks (pandemic, climate)

Each file is time-stamped and supports multi-run aggregation via companion Python scripts.

Acronyms and Abbreviations
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Summary of acronyms and abbreviations
   :header-rows: 1
   :widths: 20 80

   * - Acronym
     - Meaning
   * - COV
     - Baseline COVID scenario
   * - DIST
     - Social distancing intervention
   * - VAX
     - Vaccination intervention
   * - LOCK
     - Lockdown intervention
   * - NPI
     - Non-pharmaceutical intervention (include social distancing, vaccination, and lockdown)
   * - AggPop
     - Aggregate Population Shock
   * - Idio
     - Idiosyncratic Shock
   * - S1
     - Baseline scenario
   * - S2
     - COVID baseline only
   * - S3
     - Climate shock only
   * - S4
     - Combined pandemic and climate shock