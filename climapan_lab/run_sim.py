"""
CliMaPan-Lab: Climate-Pandemic Economic Modeling Laboratory
Main Simulation Runner

This script runs the economic model simulations with various scenarios and settings.
Supports single runs, multiple runs, and sensitivity analysis.
"""

import argparse
import copy
import json
import os
import pickle
import warnings
from datetime import datetime
from itertools import product

import jaxabm.agentpy as ap
import numpy as np
import pandas as pd
from joblib import Parallel, delayed

warnings.filterwarnings("ignore")
from .base_params import economic_params as parameters
from .src.models import EconModel
from .src.utils import (
    plotBankSummary,
    plotClimateModuleEffects,
    plotConsumersSummary,
    plotConsumptionInflationSummary,
    plotCovidStatistics,
    plotEnergyFirmsDemands,
    plotGoodsFirmSalesSummary,
    plotGoodsFirmsDemandsSummary,
    plotGoodsFirmsProfitSummary,
    plotGoodsFirmWorkersSummary,
)

# Initialize global variables for variable extraction
varListNpy = []
varListCsv = []


def single_run(
    parameters, idx=0, parent_folder=None, make_stats=False, var_dict=None, args=None
):
    multi_params = False
    if len(parameters) == 2:
        multi_params = True
        varying_var = parameters[1]
        parameters = parameters[0]

    timestamp = datetime.timestamp(datetime.now())
    if multi_params:
        varying_params = "".join(
            [
                str(list(varying_var.keys())[i]) + str(list(varying_var.values())[i])
                for i in range(len(varying_var))
            ]
        )
    else:
        varying_params = None

    if (
        args
        and hasattr(args, "climateDamage")
        and args.climateDamage
        and parameters.get("climateShockMode") is not None
    ):
        shockModeList = parameters["climateShockMode"]
        if parent_folder:
            save_folder = os.path.abspath(
                f"./{parent_folder}/results_{parameters['settings']}_{parameters['covid_settings']}_{''.join(shockModeList)}"
            )
            if varying_params is not None:
                save_folder += f"_{varying_params}"
            save_folder += f"_{timestamp}"
        else:
            save_folder = os.path.abspath(
                f"./results/results_{parameters['settings']}_{parameters['covid_settings']}_{''.join(shockModeList)}"
            )
            if varying_params is not None:
                save_folder += f"_{varying_params}"
            save_folder += f"_{timestamp}"
    else:
        parameters["climateShockMode"] = None
        if parent_folder:
            save_folder = os.path.abspath(
                f"./{parent_folder}/results_{parameters['settings']}_{parameters['covid_settings']}"
            )
            if varying_params is not None:
                save_folder += f"_{varying_params}"
            save_folder += f"_{timestamp}"
        else:
            save_folder = os.path.abspath(
                f"./results/results_{parameters['settings']}_{parameters['covid_settings']}"
            )
            if varying_params is not None:
                save_folder += f"_{varying_params}"
            save_folder += f"_{timestamp}"

    model = EconModel(parameters)
    results = model.run()
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    if args and hasattr(args, "plot") and args.plot:
        print("Ploting the results ...")
        plotConsumersSummary(results, save_folder)
        plotConsumptionInflationSummary(results, save_folder)
        plotBankSummary(results, save_folder)
        plotGoodsFirmsProfitSummary(results, save_folder)
        plotGoodsFirmsDemandsSummary(results, save_folder)
        if parameters["energySectorFlag"]:
            plotEnergyFirmsDemands(results, save_folder)
        plotGoodsFirmWorkersSummary(results, save_folder)
        plotGoodsFirmSalesSummary(results, save_folder)
        if parameters["climateModuleFlag"]:
            plotClimateModuleEffects(results, save_folder)
        if parameters["covid_settings"]:
            plotCovidStatistics(results, save_folder)

    if varListNpy is not None and len(varListNpy) > 0:
        for var in varListNpy:
            if var in results.variables.EconModel.columns:
                saving_var = np.array(
                    [
                        i
                        for i in list(results.variables.EconModel[var.strip()].values)
                        if (i is not None)
                    ]
                )
                saving_var = np.array(
                    [[i] if "ndarray" in str(type(i)) else i for i in saving_var]
                )
                np.save(
                    f"{save_folder}/{''.join(var.strip().split(' '))}.npy",
                    np.array(
                        [
                            (
                                list(i)
                                if ("ndarray" in str(type(i)) and i.shape != ())
                                else i
                            )
                            for i in list(
                                results.variables.EconModel[var.strip()].values
                            )
                        ]
                    ),
                )
                results.variables.EconModel = results.variables.EconModel.drop(
                    columns=[var.strip()]
                )

    if varListCsv is not None and len(varListCsv) > 0:
        for var in varListCsv:
            if var in results.variables.EconModel.columns:
                varList = []
                for i in results.variables.EconModel[var].values:
                    if i is not None and "ndarray" in str(type(i)):
                        varList.append([i])
                    else:
                        varList.append(i)
                try:
                    pd.DataFrame(
                        [i for i in results.variables.EconModel[var].values]
                    ).to_csv(f"{save_folder}/{''.join(var.strip().split(' '))}.csv")
                except:
                    pass
    results.variables.EconModel.to_csv(
        f"{save_folder}/single_run.csv.gz", compression="gzip"
    )

    if make_stats and var_dict is not None:
        var_dict[idx] = results.variables.EconModel

    # with open(f'{save_folder}/model.pickle', 'wb') as handle:
    # pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(f"{save_folder}/params.txt", "w") as params_file:
        params_file.write(json.dumps(parameters))

    if multi_params:
        with open(f"{save_folder}/varying_params.txt", "w") as params_file:
            params_file.write(json.dumps(varying_var))

    return results


def multi_run(overall_dict, i, save_folder):
    print(f"Processing run number {i-60+1}")
    parameters["seed"] = i

    process_save_path = os.path.join(os.path.abspath(f"{save_folder}"), f"run_{i-60}")
    if not os.path.exists(process_save_path):
        os.makedirs(process_save_path)

    model = EconModel(parameters)
    results = model.run()

    if args and hasattr(args, "plot") and args.plot:
        print("Ploting the results ...")
        plotConsumersSummary(results, process_save_path)
        plotConsumptionInflationSummary(results, process_save_path)
        plotBankSummary(results, process_save_path)
        plotGoodsFirmsProfitSummary(results, process_save_path)
        plotGoodsFirmsDemandsSummary(results, process_save_path)
        if parameters["energySectorFlag"]:
            plotEnergyFirmsDemands(results, process_save_path)
        plotGoodsFirmWorkersSummary(results, process_save_path)
        plotGoodsFirmSalesSummary(results, process_save_path)
        if parameters["climateModuleFlag"]:
            plotClimateModuleEffects(results, process_save_path)

    if varListNpy is not None and len(varListNpy) > 0:
        for var in varListNpy:
            if var in results.variables.EconModel.columns:
                saving_var = np.array(
                    [
                        i
                        for i in list(results.variables.EconModel[var.strip()].values)
                        if (i is not None)
                    ]
                )
                saving_var = np.array(
                    [[i] if "ndarray" in str(type(i)) else i for i in saving_var]
                )
                np.save(
                    f"{process_save_path}/{''.join(var.strip().split(' '))}.npy",
                    saving_var,
                )
                results.variables.EconModel = results.variables.EconModel.drop(
                    columns=[var.strip()]
                )

    if varListCsv is not None and len(varListCsv) > 0:
        for var in varListCsv:
            if var in results.variables.EconModel.columns:
                varList = []
                for i in results.variables.EconModel[var].values:
                    if i is not None and "ndarray" in str(type(i)):
                        varList.append([i])
                    else:
                        varList.append(i)

                pd.DataFrame(
                    [i for i in results.variables.EconModel[var].values]
                ).to_csv(f"{process_save_path}/{''.join(var.strip().split(' '))}.csv")

    with open(f"{process_save_path}/model_run_{i-60}.pickle", "wb") as handle:
        pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)
    overall_dict[f"Run_0{i-60}"] = results.variables.EconModel


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--noOfRuns", type=int, default=1, help="an integer for number of runs"
    )
    parser.add_argument(
        "-s",
        "--settings",
        type=str,
        default="BAU",
        help="situation settings: BAU, CT, CTRa, CTRb, CTRc, CTRd",
    )
    parser.add_argument(
        "-c",
        "--covidSettings",
        type=str,
        default=None,
        help="situation settings: BAU, DIST, LOCK, VAX",
    )
    parser.add_argument(
        "-d",
        "--climateDamage",
        type=str,
        default="AggPop",
        help="Climate damage type: AggPop, Idiosyncratic, or None",
    )
    parser.add_argument(
        "-l",
        "--extractedVarListPathNpy",
        default=None,
        help="extractedVarListPathNpy is the list of variables to be extracted to separate numpy files",
    )
    parser.add_argument(
        "-v",
        "--extractedVarListPathCsv",
        default=None,
        help="extractedVarListPathCsv is the list of variables to be extracted to separate csv files",
    )
    parser.add_argument("-p", "--plot", action="store_true", help="(bool) plot or not")
    args = parser.parse_args()

    if args.settings:
        parameters["settings"] = args.settings.strip()

    if args.covidSettings:
        parameters["covid_settings"] = args.covidSettings.strip()

    if (
        args.extractedVarListPathNpy is not None
        and os.path.exists(args.extractedVarListPathNpy.strip())
        and args.extractedVarListPathNpy.strip().endswith(".txt")
    ):
        file = args.extractedVarListPathNpy.strip()
        varListNpy = []
        with open(file) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                varListNpy.append(line.strip())
    else:
        varListNpy = []

    if (
        args.extractedVarListPathCsv is not None
        and os.path.exists(args.extractedVarListPathCsv.strip())
        and args.extractedVarListPathCsv.strip().endswith(".txt")
    ):
        file = args.extractedVarListPathCsv.strip()
        varListCsv = []
        with open(file) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                varListCsv.append(line.strip())
    else:
        varListCsv = []

    if args.noOfRuns == 1:
        print("Start simulating ...")
        print(args.climateDamage)
        count = 0
        for i in parameters:
            if type(parameters[i]) == list:
                count += 1
                break

        if count == 0:
            single_run(parameters)
        else:
            print("Enter Multi-params mode.")
            parameters_combinations = []
            count = 0
            list_of_varying_parameters = {}
            values_of_varying_parameters = {}
            for name in parameters:
                if type(parameters[name]) == list:
                    list_of_varying_parameters[count] = name
                    values_of_varying_parameters[name] = parameters[name]
                    parameters_combinations.append(parameters[name])
                    count += 1

            list_parameters_combinations = list(product(*parameters_combinations))
            print(
                f"Given parameter list will be split into {len(list_parameters_combinations)} variants"
            )

            parameters_combinations = []
            for parameter_vars in list_parameters_combinations:
                vaying_dict = {}
                for i in range(len(parameter_vars)):
                    params_copy = copy.deepcopy(parameters)
                    params_copy[list_of_varying_parameters[i]] = parameter_vars[i]
                    vaying_dict[list_of_varying_parameters[i]] = parameter_vars[i]
                parameters_combinations.append([params_copy, vaying_dict])

            timestamp = datetime.timestamp(datetime.now())
            parent_folder = f"./results/result_multi_{timestamp}"
            if not os.path.exists(parent_folder):
                os.makedirs(parent_folder)

            var_dict = {}

            Parallel(n_jobs=-1, prefer="threads")(
                [
                    delayed(single_run)(
                        params,
                        idx,
                        parent_folder=parent_folder,
                        make_stats=True,
                        var_dict=var_dict,
                    )
                    for idx, params in enumerate(parameters_combinations)
                ]
            )

            with open(f"{parent_folder}/params.txt", "w") as params_file:
                params_file.write(json.dumps(parameters))

        print("Finished.")

    elif args.noOfRuns > 1:
        print(f"Start simulating with {args.noOfRuns} runs ...")
        count = 0
        for i in parameters:
            if type(parameters[i]) == list:
                count += 1

        if count == 0:
            overall_dict = {}
            timestamp = datetime.timestamp(datetime.now())
            if args.climateDamage:
                save_folder = f"./results/multi_run_results_{parameters['settings']}_{parameters['covid_settings']}_CLIMATE_{timestamp}"
            else:
                parameters["climateShockMode"] = None
                save_folder = f"./results/multi_run_results_{parameters['settings']}_{parameters['covid_settings']}_{timestamp}"
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            Parallel(n_jobs=-1, prefer="threads")(
                [
                    delayed(multi_run)(overall_dict, i, save_folder)
                    for i in range(60, 60 + args.noOfRuns)
                ]
            )

            result = pd.concat(overall_dict)
            result = result.rename(columns={"Unnamed: 0": "RunNo"})

            result.to_csv(f"{save_folder}/multi_runs.csv.gz", compression="gzip")
        else:
            print("Multi-params setting for multi-run is not currently supported!")

        with open(f"{save_folder}/params.txt", "w") as params_file:
            params_file.write(json.dumps(parameters))

        print("Finished.")


def main():
    """Main function for console script entry point."""
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--noOfRuns", type=int, default=1, help="an integer for number of runs"
    )
    parser.add_argument(
        "-s",
        "--settings",
        type=str,
        default="BAU",
        help="situation settings: BAU, CT, CTRa, CTRb, CTRc, CTRd",
    )
    parser.add_argument(
        "-c",
        "--covidSettings",
        type=str,
        default=None,
        help="situation settings: BAU, DIST, LOCK, VAX",
    )
    parser.add_argument(
        "-d",
        "--climateDamage",
        type=str,
        default="AggPop",
        help="Climate damage type: AggPop, Idiosyncratic, or None",
    )
    parser.add_argument(
        "-l",
        "--extractedVarListPathNpy",
        default=None,
        help="extractedVarListPathNpy is the list of variables to be extracted to separate numpy files",
    )
    parser.add_argument(
        "-v",
        "--extractedVarListPathCsv",
        default=None,
        help="extractedVarListPathCsv is the list of variables to be extracted to separate csv files",
    )
    parser.add_argument("-p", "--plot", action="store_true", help="(bool) plot or not")

    # Set global args for the existing code to use
    global args
    args = parser.parse_args()

    # Run the main simulation logic (copying from __main__ block)
    if args.settings:
        parameters["settings"] = args.settings.strip()

    if args.covidSettings:
        parameters["covid_settings"] = args.covidSettings.strip()

    # Handle variable extraction lists
    varListNpy = []
    varListCsv = []

    if (
        args.extractedVarListPathNpy is not None
        and os.path.exists(args.extractedVarListPathNpy.strip())
        and args.extractedVarListPathNpy.strip().endswith(".txt")
    ):
        file = args.extractedVarListPathNpy.strip()
        with open(file) as f:
            varListNpy = [line.strip() for line in f.readlines()]

    if (
        args.extractedVarListPathCsv is not None
        and os.path.exists(args.extractedVarListPathCsv.strip())
        and args.extractedVarListPathCsv.strip().endswith(".txt")
    ):
        file = args.extractedVarListPathCsv.strip()
        with open(file) as f:
            varListCsv = [line.strip() for line in f.readlines()]

    # Set global variables for existing functions to use
    globals()["varListNpy"] = varListNpy
    globals()["varListCsv"] = varListCsv

    # Run simulation logic
    if args.noOfRuns == 1:
        print("Start simulating ...")
        print(args.climateDamage)
        count = 0
        for i in parameters:
            if type(parameters[i]) == list:
                count += 1
                break

        if count == 0:
            single_run(parameters)
        else:
            print("Enter Multi-params mode.")
            parameters_combinations = []
            count = 0
            list_of_varying_parameters = {}
            values_of_varying_parameters = {}
            for name in parameters:
                if type(parameters[name]) == list:
                    list_of_varying_parameters[count] = name
                    values_of_varying_parameters[name] = parameters[name]
                    parameters_combinations.append(parameters[name])
                    count += 1

            list_parameters_combinations = list(product(*parameters_combinations))
            print(
                f"Given parameter list will be split into {len(list_parameters_combinations)} variants"
            )

            parameters_combinations = []
            for parameter_vars in list_parameters_combinations:
                vaying_dict = {}
                for i in range(len(parameter_vars)):
                    params_copy = copy.deepcopy(parameters)
                    params_copy[list_of_varying_parameters[i]] = parameter_vars[i]
                    vaying_dict[list_of_varying_parameters[i]] = parameter_vars[i]
                parameters_combinations.append([params_copy, vaying_dict])

            timestamp = datetime.timestamp(datetime.now())
            parent_folder = f"./results/result_multi_{timestamp}"
            if not os.path.exists(parent_folder):
                os.makedirs(parent_folder)

            var_dict = {}

            Parallel(n_jobs=-1, prefer="threads")(
                [
                    delayed(single_run)(
                        params,
                        idx,
                        parent_folder=parent_folder,
                        make_stats=True,
                        var_dict=var_dict,
                    )
                    for idx, params in enumerate(parameters_combinations)
                ]
            )

            with open(f"{parent_folder}/params.txt", "w") as params_file:
                params_file.write(json.dumps(parameters))

        print("Finished.")

    elif args.noOfRuns > 1:
        print(f"Start simulating with {args.noOfRuns} runs ...")
        count = 0
        for i in parameters:
            if type(parameters[i]) == list:
                count += 1

        if count == 0:
            overall_dict = {}
            timestamp = datetime.timestamp(datetime.now())
            if args.climateDamage:
                save_folder = f"./results/multi_run_results_{parameters['settings']}_{parameters['covid_settings']}_CLIMATE_{timestamp}"
            else:
                parameters["climateShockMode"] = None
                save_folder = f"./results/multi_run_results_{parameters['settings']}_{parameters['covid_settings']}_{timestamp}"
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            Parallel(n_jobs=-1, prefer="threads")(
                [
                    delayed(multi_run)(overall_dict, i, save_folder)
                    for i in range(60, 60 + args.noOfRuns)
                ]
            )

            result = pd.concat(overall_dict)
            result = result.rename(columns={"Unnamed: 0": "RunNo"})

            result.to_csv(f"{save_folder}/multi_runs.csv.gz", compression="gzip")
        else:
            print("Multi-params setting for multi-run is not currently supported!")

        with open(f"{save_folder}/params.txt", "w") as params_file:
            params_file.write(json.dumps(parameters))

        print("Finished.")
