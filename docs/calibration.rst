Model Calibration
=================

CliMaPan-Lab calibrates selected economic and climate parameters against German
macro time series using an **autocorrelation-oriented** distance (dynamics and
relative variability), not absolute level matching.

Entry points
------------

* Script: ``climapan_lab/calibrate_model.py``
* Target data: ``climapan_lab/data/Germany9122.csv``
  (columns: ``GDP``, ``UnemploymentRate``, ``Investment``, ``Climate C02``)
* Best parameters: ``climapan_lab/optimized_params.py``
* Trial log: ``climapan_lab/calibration_results.json``
* Evaluation snapshot (ambr 0.4.7): ``climapan_lab/calibration_eval_ambr047.json``

How a trial works
-----------------

1. Sample or propose a parameter vector from ``PARAM_SPACE`` in
   ``calibrate_model.py``.
2. Run ``run_simulation(params, n_years)``:

   * ``steps = n_years * 365`` (daily steps)
   * default agent scale from ``climapan_lab/src/params.py`` (e.g. 5000 consumers)
   * climate module enabled for calibration runs
3. Aggregate monthly recorded series to **yearly** means (12 monthly points per
   year when recording is complete).
4. Score against the first ``n_years`` of Germany data.

Objective (lower is better)
---------------------------

For each available metric (``GDP``, ``UnemploymentRate``, ``Investment``,
``Climate C02``):

.. code-block:: text

   metric_distance = 0.6 * ACF_MSE + 0.25 * CV_distance + 0.15 * trend_distance

* **ACF**: MSE of autocorrelation lags 1…``max_lag`` (default 5)
* **CV**: squared difference of coefficients of variation
* **Trend**: squared difference of normalized linear slopes

The total objective is the mean of metric distances. Absolute means/levels are
**not** part of the loss by design.

Bayesian search
---------------

``bayesian_optimization`` uses a simple surrogate acquisition (distance-weighted
mean minus exploration term) after ``n_initial`` random samples. Defaults in
code:

* ``n_calls=30``, ``n_initial=10``, ``n_years=5``, ``seed=42``

A full trial at production scale is expensive (~8–9 minutes per evaluation on a
laptop-class CPU with 5000 agents and 5 years).

Historical search note: ``calibration_results.json`` currently contains only
**10** trials (tight objective cluster ~0.170–0.174). Treat published
``optimized_params`` as a **candidate**, not a fully explored optimum.

Evaluation under ambr 0.4.7
---------------------------

Re-scored configurations at ``n_years=5`` (full agent scale):

.. list-table::
   :header-rows: 1
   :widths: 40 20 40

   * - Configuration
     - Objective
     - Notes
   * - ``optimized_params``
     - **0.00690**
     - Best among tested sets
   * - baseline defaults
     - 0.01440
     - No PARAM_SPACE overrides
   * - random sample
     - 0.01765
     - Seeded random in PARAM_SPACE
   * - PARAM_SPACE midpoint
     - 0.02354
     - Worst among tested

Optimized parameters still **beat** baseline and random under the current
metric. Absolute numbers are not comparable to the historical 0.17 cluster
without replaying the same AMBER / recording stack (metric series and ACF
behavior can change when monthly collection is healthy).

Known limitations
-----------------

ACF inert for short horizons
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``compute_autocorrelation`` returns all zeros when
``len(series) < max_lag + 2``. With default ``n_years=5`` and ``max_lag=5``,
**every ACF distance is zero**. The optimizer effectively only matches **CV** and
**trend**. Fix options:

* set ``max_lag = min(5, n // 2 - 1)`` (or similar), and/or
* calibrate with longer series (e.g. ``n_years >= 10``).

Scale and unit mismatches
~~~~~~~~~~~~~~~~~~~~~~~~~

These do not enter the loss as levels, but they matter for interpretation:

* **GDP**: sim yearly means ~1e7 vs Germany ~1e12 (orders of magnitude)
* **UnemploymentRate**: sim ~0.04 (fraction) vs data ~5–9 (percent points)
* **Climate C02**: sim ~1e10 vs data ~0.9 (different definition/units)

Unemployment dynamics
~~~~~~~~~~~~~~~~~~~~~

In evaluated 5-year runs, simulated unemployment was nearly **constant** across
years and parameter draws, so it cannot reproduce German U dynamics.

Running calibration
-------------------

.. code-block:: bash

   # From repo root (long-running)
   python -m climapan_lab.calibrate_model

Or import and call ``bayesian_optimization`` / ``objective_function`` from
``climapan_lab.calibrate_model``. Prefer reducing ``n_years`` and agent counts
only for smoke tests; production scores should use the default scale for
comparability with ``optimized_params``.

Recommended follow-ups
----------------------

1. Fix ACF length gate so lags are informative at the chosen ``n_years``.
2. Align units (unemployment percent, climate variable definition).
3. Re-run a larger search (more random + bayesian trials, longer horizon).
4. Add a regression test that asserts finite yearly GDP for ``n_years>=2`` under
   a reduced agent count for CI time budgets.

See also
--------

* :doc:`amber` — results API, monthly recording, mode verification
* ``climapan_lab/optimized_params.py`` — current best vector
* ``climapan_lab/calibration_eval_ambr047.json`` — detailed re-score dump
