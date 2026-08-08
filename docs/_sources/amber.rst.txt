AMBER Compatibility
===================

CliMaPan-Lab is built on `AMBER <https://github.com/a11to1n3/AMBER>`_ (PyPI package
``ambr``), an agent-based modeling framework with a columnar (Polars) agent backend.

**Required version:** ``ambr >= 0.4.7`` (Python ``>= 3.9``).

Pins are aligned in ``requirements.txt``, ``setup.py``, and ``pyproject.toml``.

Results API
-----------

``model.run()`` returns an AMBER ``RunResults`` mapping (dict-like):

.. code-block:: python

   from climapan_lab.model import EconModel
   from climapan_lab.base_params import economic_params

   params = economic_params.copy()
   params["steps"] = 45          # daily steps
   params["show_progress"] = False
   model = EconModel(params)
   results = model.run()

   # Polars frames
   model_df = results["model"]     # model-level time series
   agents_df = results["agents"]   # agent snapshot / history

   # Convert to pandas when needed
   pdf = model_df.to_pandas()

The high-level runner ``climapan_lab.run_sim.single_run`` wraps the same results in an
AgentPy-compatible object for legacy analysis code:

.. code-block:: python

   from climapan_lab.run_sim import single_run

   result = single_run(params, parent_folder="results", make_stats=True)
   pdf = result.variables.EconModel   # pandas DataFrame

Time steps and monthly recording
--------------------------------

* Simulation **steps are daily** (``steps=365`` ≈ one year).
* Macro indicators (``GDP``, ``UnemploymentRate``, ``Investment``, climate series, …)
  are recorded in ``EconModel.update()`` only on **month boundaries**
  (when the calendar day of ``tomorrow`` is ``1``).
* Short CI runs (1–5 steps) therefore often produce a model frame that only has
  the step index ``t``. Use **at least ~40 steps** (crossing a month end) to see
  economic metrics in ``results["model"]``.

Example start date: default ``start_date`` is ``1980-01-01``; the first monthly
record typically appears around step ~31 (end of January).

Execution modes (vectorized vs OOP)
-----------------------------------

AMBER supports:

* ``mode="vectorized"`` (default) — view / columnar execution path
* ``mode="oop"`` — per-agent object path

.. code-block:: python

   model = EconModel(params)
   results_v = model.cpu(mode="vectorized").run(mode="vectorized")
   results_o = model.cpu(mode="oop").run(mode="oop")  # new instance recommended

**CliMaPan verification (ambr 0.4.7):** ``EconModel`` implements a single
``step()`` method used by both modes. Side-by-side runs with the same seed
produced **bit-identical** model and agent frames (including climate-on runs).

There is no separate “vectorized economics” implementation in CliMaPan; NumPy
vectorization inside agent/firm logic is independent of AMBER’s mode flag.

AMBER 0.3 → 0.4 notes
---------------------

The following remain true under 0.4.7:

* ``Model.record(key, value)`` still works (deprecated alias of ``record_model``;
  removal planned for AMBER 1.0). Prefer ``record_model`` for new code.
* ``AgentList.select(...)`` still works (deprecated; prefer ``agents.where`` /
  mask indexing before AMBER 1.0).
* AMBER’s model seed no longer seeds process-global ``np.random``; CliMaPan calls
  ``np.random.seed(self.p.seed)`` in setup.
* ``update()`` is a pure hook; step advance and result finalization are owned by
  the runner. Calling ``super().update()`` remains a no-op and is safe.

Deprecation warnings in tests are expected until CliMaPan migrates call sites.

Integrity checks performed
--------------------------

Under **ambr 0.4.7** the following were exercised:

* Full ``pytest tests/`` (unit, integration, performance): all non-skipped tests pass
* ``tests/run_all_tests.py --fast``
* Determinism: same seed → same monthly GDP path
* Different seeds → diverging multi-month GDP paths
* Finite, non-negative GDP; bounded People / Gini on monthly samples
* BAU / CT / climate-on scenarios produce positive activity and expected columns
* Vectorized vs OOP end-result identity (see above)

CI does **not** currently force a month boundary, so it will not alone catch a
regression that drops monthly ``record`` metrics. Prefer a ≥40-step smoke test
when changing data collection.

Related docs
------------

* :doc:`calibration` — autocorrelation calibration pipeline and evaluation
* :doc:`installation` — dependency pins
* `CHANGELOG.md` — release notes for the AMBER floor bump
