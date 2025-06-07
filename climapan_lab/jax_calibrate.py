"""Simple calibration interface using JaxABM's ModelCalibrator."""

from jaxabm.analysis import ModelCalibrator, ModelConfig

from .base_params import economic_params
from .src.models import EconModel


def model_factory(params=None, config: ModelConfig | None = None):
    params_dict = economic_params.copy()
    if params:
        params_dict.update(params)
    seed = params_dict.get("seed", 0)
    if config is not None:
        seed = config.seed
    return EconModel(parameters=params_dict, seed=seed)


def run_calibration():
    initial_params = {"wageAdjustmentRate": economic_params["wageAdjustmentRate"]}
    target_metrics = {"UnemploymentRate": 0.05}
    param_bounds = {"wageAdjustmentRate": (0.0001, 0.01)}

    calibrator = ModelCalibrator(
        model_factory=model_factory,
        initial_params=initial_params,
        target_metrics=target_metrics,
        param_bounds=param_bounds,
        evaluation_steps=200,
        max_iterations=10,
    )

    best_params = calibrator.calibrate(verbose=True)
    print("Best parameters:", best_params)


if __name__ == "__main__":
    run_calibration()
