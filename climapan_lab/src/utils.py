"""
CliMaPan-Lab: Climate-Pandemic Economic Modeling Laboratory
Utility Functions and Plotting

This module contains utility functions for data processing, statistical calculations,
and visualization of simulation results.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from .params import parameters
import math
import random


def listToArray(x):
    return np.array(x)


def leap_year(year):
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    if year % 4 == 0:
        return True
    return False


def days_in_month(month, year):
    if month in {1, 3, 5, 7, 8, 10, 12}:
        return 31
    if month == 2:
        if leap_year(year):
            return 29
        return 28
    return 30


def _merge_edgelist(p1, p2, mapping, offset=0):
    """Helper function to convert lists to arrays and optionally map arrays"""
    p1 = np.array(p1, dtype=np.int32)
    p2 = np.array(p2, dtype=np.int32)
    if mapping is not None:
        mapping = np.array(mapping, dtype=np.int32)
        p1 = mapping[p1] - offset
        p2 = mapping[p2] - offset
    output = dict(p1=p1, p2=p2)
    return output


def gini(x, eps=1e-8):
    # Mean absolute difference
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # Relative mean absolute difference
    rmad = mad / (np.mean(x) + eps)
    # Gini coefficient
    g = 0.5 * rmad
    return g


def plotConsumersSummary(results, saveFolder):
    plt.figure(figsize=(36, 27))
    plt.subplots_adjust(hspace=0.5)

    ax1 = plt.subplot2grid((6, 2), (5, 0))
    ax1.margins(0.1)
    ax1.plot(
        [
            (
                results.variables.EconModel["Gini"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Gini"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
            and not np.isnan(
                results.variables.EconModel["Gini"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
        ]
    )
    ax1.set_ylabel("Gini")
    ax1.set_xlabel("Year")

    ax1 = plt.subplot2grid((6, 2), (5, 1))
    ax1.margins(0.1)
    ax1.hist(
        np.array([np.sum(i) for i in results.variables.EconModel["Wage"]])
        + results.variables.EconModel["Owners Income"],
        1000,
    )
    ax1.set_ylabel("Density")
    ax1.set_xlabel("Wage")

    ax1 = plt.subplot2grid((6, 2), (4, 0))
    ax1.margins(0.1)
    ax1.plot(
        [
            (
                results.variables.EconModel["UnemploymentRate"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            * 100
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["UnemploymentRate"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
            and not np.isnan(
                results.variables.EconModel["UnemploymentRate"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
        ]
    )
    ax1.set_ylabel("Unemployment Rate (%)")
    ax1.set_xlabel("Year")

    ax2 = plt.subplot2grid((6, 2), (1, 0))
    ax2.margins(0.1)
    # ax2.plot([(results.variables.EconModel['Available Income'][results.variables.EconModel['BankDataWriter'].keys()[i]].sum()) for i in range(50,len(results.variables.EconModel['BankDataWriter']))], label = "Available Income")
    ax2.plot(
        [
            np.sum(
                results.variables.EconModel["UnemplDole"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["UnemplDole"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Unempl Dole",
    )
    ax2.plot(
        [
            np.sum(
                results.variables.EconModel["Owners Income"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Owners Income"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Owners Income",
    )
    ax2.plot(
        [
            np.sum(
                results.variables.EconModel["Wage"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Wage"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Wage",
    )
    ax2.set_ylabel("Available Income")
    ax2.set_xlabel("Year")
    ax2.legend()

    ax2 = plt.subplot2grid((6, 2), (1, 1))
    ax2.margins(0.1)
    data = []
    # data.append([(results.variables.EconModel['Available Income'][results.variables.EconModel['BankDataWriter'].keys()[i]].sum()) for i in range(50,len(results.variables.EconModel['BankDataWriter']))])
    data.append(
        [
            np.sum(
                np.array(
                    (
                        results.variables.EconModel["UnemplDole"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                    )
                )
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["UnemplDole"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            np.sum(
                np.array(
                    (
                        results.variables.EconModel["Owners Income"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                    )
                )
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Owners Income"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            np.sum(
                np.sum(
                    np.array(
                        (
                            results.variables.EconModel["Wage"][
                                results.variables.EconModel["BankDataWriter"].keys()[i]
                            ]
                        )
                    )
                )
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Wage"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.boxplot(data)
    ax2.set_ylabel("Available Income")

    ax2 = plt.subplot2grid((6, 2), (2, 0))
    ax2.margins(0.1)
    ax2.plot(
        [
            (
                results.variables.EconModel["Wage"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Wage"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Wage",
    )
    ax2.set_ylabel("Wage")
    ax2.set_xlabel("Year")
    ax2.legend()

    ax2 = plt.subplot2grid((6, 2), (2, 1))
    ax2.margins(0.1)
    data = []
    data.append(
        [
            np.sum(
                np.sum(
                    np.array(
                        (
                            results.variables.EconModel["Wage"][
                                results.variables.EconModel["BankDataWriter"].keys()[i]
                            ]
                        )
                    )
                )
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Wage"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.boxplot(data)
    ax2.set_ylabel("Wage")

    ax3 = plt.subplot2grid((6, 2), (3, 0))
    ax3.margins(0.1)
    ax3.plot(
        [
            (
                results.variables.EconModel["New Credit Asked"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["New Credit Asked"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="New Credit Asked",
    )
    ax3.plot(
        [
            (
                results.variables.EconModel["Obtained Credit"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Obtained Credit"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Obtained Credit",
    )
    ax3.set_ylabel("New Credit Asked vs Obtained Credit")
    ax3.set_xlabel("Year")
    ax3.legend()

    ax3 = plt.subplot2grid((6, 2), (3, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["New Credit Asked"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["New Credit Asked"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            (
                results.variables.EconModel["Obtained Credit"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Obtained Credit"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.boxplot(data)
    ax3.set_ylabel("New Credit Asked vs Obtained Credit")

    ax5 = plt.subplot2grid((6, 2), (0, 0))
    ax5.margins(0.1)
    ax5.plot(
        [
            (
                results.variables.EconModel["Wealth"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Wealth"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax5.set_ylabel("Wealth")
    ax5.set_xlabel("Year")

    ax3 = plt.subplot2grid((6, 2), (0, 1))
    ax5.margins(0.1)
    ax5.boxplot(
        [
            (
                results.variables.EconModel["Wealth"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Wealth"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax5.set_ylabel("Wealth")

    if os.path.isdir(saveFolder):
        plt.savefig(f"{saveFolder}/ConsumerSummaryPlot.png")
    else:
        os.mkdir(saveFolder)
        plt.savefig(f"{saveFolder}/ConsumerSummaryPlot.png")


def plotConsumptionInflationSummary(results, saveFolder):
    plt.figure(figsize=(36, 27))
    plt.subplots_adjust(hspace=0.5)

    ax5 = plt.subplot2grid((5, 2), (0, 0))
    ax5.margins(0.1)
    ax5.plot(
        [
            (
                results.variables.EconModel["Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "capitalists"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Capitalists",
    )
    ax5.plot(
        [
            (
                results.variables.EconModel["Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "green_energy_owners"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Green Energy Owners",
    )
    ax5.plot(
        [
            (
                results.variables.EconModel["Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "brown_energy_owners"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Brown Energy Owners",
    )
    ax5.plot(
        [
            (
                results.variables.EconModel["Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "workers"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Workers",
    )
    ax5.set_ylabel("Consumption")
    ax5.set_xlabel("Year")
    ax5.legend()

    ax5 = plt.subplot2grid((5, 2), (0, 1))
    ax5.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "capitalists"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            (
                results.variables.EconModel["Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "green_energy_owners"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            (
                results.variables.EconModel["Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "brown_energy_owners"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            (
                results.variables.EconModel["Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "workers"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax5.boxplot(data)
    ax5.set_ylabel("Consumption")

    ax1 = plt.subplot2grid((5, 2), (1, 0))
    ax1.margins(0.1)
    ax1.plot(
        [
            (
                results.variables.EconModel["Gini Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Gini Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
            and not np.isnan(
                results.variables.EconModel["Gini Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
        ]
    )
    ax1.set_ylabel("Gini Consumption")
    ax1.set_xlabel("Year")

    ax5 = plt.subplot2grid((5, 2), (2, 0))
    ax5.margins(0.1)
    ax5.plot(
        [
            (
                results.variables.EconModel["Desired Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "capitalists"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Desired Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Capitalists",
    )
    ax5.plot(
        [
            (
                results.variables.EconModel["Desired Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "green_energy_owners"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Desired Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Green Energy Owners",
    )
    ax5.plot(
        [
            (
                results.variables.EconModel["Desired Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "brown_energy_owners"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Desired Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Brown Energy Owners",
    )
    ax5.plot(
        [
            (
                results.variables.EconModel["Desired Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "workers"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Desired Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Workers",
    )
    ax5.set_ylabel("Desired Consumption")
    ax5.set_xlabel("Year")
    ax5.legend()

    ax5 = plt.subplot2grid((5, 2), (2, 1))
    ax5.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["Desired Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "capitalists"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Desired Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            (
                results.variables.EconModel["Desired Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "green_energy_owners"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Desired Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            (
                results.variables.EconModel["Desired Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "brown_energy_owners"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Desired Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            (
                results.variables.EconModel["Desired Consumption"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][
                    np.argwhere(
                        results.variables.EconModel["Consumer Type"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                        == "workers"
                    )
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Desired Consumption"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax5.boxplot(data)
    ax5.set_ylabel("Desired Consumption")

    ax5 = plt.subplot2grid((5, 2), (3, 0))
    ax5.margins(0.1)
    ax5.plot(
        [
            (
                results.variables.EconModel["Expected Inflation Rate"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Expected Inflation Rate"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="expectedInflationRate",
    )
    ax5.set_ylabel("expectedInflationRate")
    ax5.set_xlabel("Year")
    ax5.legend()

    ax5 = plt.subplot2grid((5, 2), (3, 1))
    ax5.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["Expected Inflation Rate"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Expected Inflation Rate"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax5.boxplot(data)
    ax5.set_ylabel("expectedInflationRate")

    ax5 = plt.subplot2grid((5, 2), (4, 0))
    ax5.margins(0.1)
    ax5.plot(
        [
            (
                results.variables.EconModel["Inflation Rate"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Inflation Rate"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="inflationRate",
    )
    ax5.set_ylabel("inflationRate")
    ax5.set_xlabel("Year")
    ax5.legend()

    ax5 = plt.subplot2grid((5, 2), (4, 1))
    ax5.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["Inflation Rate"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Inflation Rate"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax5.boxplot(data)
    ax5.set_ylabel("inflationRate")

    if os.path.isdir(saveFolder):
        plt.savefig(f"{saveFolder}/ConsumptionInflationSummary.png")
    else:
        os.mkdir(saveFolder)
        plt.savefig(f"{saveFolder}/ConsumptionInflationSummary.png")


def plotBankSummary(results, saveFolder, eps=1e-8):
    plt.figure(figsize=(36, 27))
    plt.subplots_adjust(hspace=0.5)

    ax1 = plt.subplot2grid((9, 2), (0, 0))
    ax1.margins(0.1)
    ax1.plot(
        [
            (
                results.variables.EconModel["Bank totalLoanSupply"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Bank totalLoanSupply"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Total Loan Supply",
    )
    ax1.plot(
        [
            (
                results.variables.EconModel["Bank Loan Demands"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Bank Loan Demands"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Loan Demand",
    )
    ax1.set_ylabel("Bank Total Loan Supply vs Loan Demand")
    ax1.set_xlabel("Year")
    ax1.legend()

    ax1 = plt.subplot2grid((9, 2), (1, 0))
    ax1.margins(0.1)
    ax1.plot(
        [
            (
                results.variables.EconModel["Bank iL"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
                * 100
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Bank iL"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Bank Debt to Equity",
    )
    ax1.plot(
        [
            1.5
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Bank iL"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax1.set_ylabel("Bank Debt to Equity")
    ax1.set_xlabel("Year")

    ax3 = plt.subplot2grid((9, 2), (7, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["Bank iL"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
                * 100
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Bank iL"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Bank Debt to Equity")

    ax2 = plt.subplot2grid((9, 2), (2, 0))
    ax2.margins(0.1)
    ax2.plot(
        [
            (
                results.variables.EconModel["Bank Equity"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Bank Equity"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.set_ylabel("Bank Equity")
    ax2.set_xlabel("Year")
    ax2.legend()

    ax3 = plt.subplot2grid((9, 2), (2, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["Bank Equity"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Bank Equity"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Bank Equity")

    ax2 = plt.subplot2grid((9, 2), (3, 0))
    ax2.margins(0.1)
    ax2.plot(
        [
            (
                results.variables.EconModel["Bank Deposits"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Bank Deposits"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.set_ylabel("Bank Deposits")
    ax2.set_xlabel("Year")
    ax2.legend()

    ax3 = plt.subplot2grid((9, 2), (3, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["Bank Deposits"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Bank Deposits"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Bank Deposits")

    ax2 = plt.subplot2grid((9, 2), (4, 0))
    ax2.margins(0.1)
    ax2.plot(
        [
            (
                results.variables.EconModel["Consumer iL"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Consumer iL"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Consumer iL",
    )
    for j in range(len(results.variables.EconModel["CS iL"][0])):
        ax2.plot(
            [
                (
                    results.variables.EconModel["CS iL"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][j]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS iL"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ],
            label=f"CS {j} iL",
        )
    for j in range(len(results.variables.EconModel["CP iL"][0])):
        ax2.plot(
            [
                (
                    results.variables.EconModel["CP iL"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][j]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP iL"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ],
            label=f"CP {j} iL",
        )
    ax2.set_ylabel("iL")
    ax2.set_xlabel("Year")
    ax2.legend()

    ax3 = plt.subplot2grid((9, 2), (4, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["Consumer iL"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Consumer iL"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    for j in range(len(results.variables.EconModel["CS iL"][0])):
        data.append(
            [
                (
                    results.variables.EconModel["CS iL"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][j]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS iL"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    for j in range(len(results.variables.EconModel["CP iL"][0])):
        data.append(
            [
                (
                    results.variables.EconModel["CP iL"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][j]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP iL"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    ax3.boxplot(data)
    ax3.set_ylabel("iL")

    ax2 = plt.subplot2grid((9, 2), (5, 0))
    ax2.margins(0.1)
    ax2.plot(
        [
            (
                results.variables.EconModel["Consumer iH"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Consumer iH"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Consumer iH",
    )
    for j in range(len(results.variables.EconModel["CS iF"][0])):
        ax2.plot(
            [
                (
                    results.variables.EconModel["CS iF"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][j]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS iF"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ],
            label=f"CS {j} iF",
        )
    for j in range(len(results.variables.EconModel["CP iF"][0])):
        ax2.plot(
            [
                (
                    results.variables.EconModel["CP iF"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][j]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP iF"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ],
            label=f"CP {j} iF",
        )
    ax2.set_ylabel("iF/iH")
    ax2.set_xlabel("Year")
    ax2.legend()

    ax3 = plt.subplot2grid((9, 2), (5, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["Consumer iH"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Consumer iH"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    for j in range(len(results.variables.EconModel["CS iF"][0])):
        data.append(
            [
                (
                    results.variables.EconModel["CS iF"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][j]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS iF"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    for j in range(len(results.variables.EconModel["CP iF"][0])):
        data.append(
            [
                (
                    results.variables.EconModel["CP iF"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][j]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP iF"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    ax3.boxplot(data)
    ax3.set_ylabel("iF/iH")

    ax2 = plt.subplot2grid((9, 2), (6, 0))
    ax2.margins(0.1)
    ax2.plot(
        [
            (
                results.variables.EconModel["CS Num Bankrupt"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Num Bankrupt"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="CS Num Bankrupt",
    )
    ax2.plot(
        [
            (
                results.variables.EconModel["CP Num Bankrupt"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Num Bankrupt"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="CP Num Bankrupt",
    )
    ax2.set_ylabel("Number of Bankrupt Goods Firms")
    ax2.set_xlabel("Year")
    ax2.legend()

    ax3 = plt.subplot2grid((9, 2), (6, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["CS Num Bankrupt"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Num Bankrupt"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            (
                results.variables.EconModel["CP Num Bankrupt"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Num Bankrupt"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Number of Bankrupt Goods Firms")

    ax2 = plt.subplot2grid((9, 2), (7, 0))
    ax2.margins(0.1)
    ax2.plot(
        [
            (
                results.variables.EconModel["Bank Loan Over Equity"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Bank Loan Over Equity"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Bank Leverage",
    )
    ax2.plot(
        [
            0.5
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Bank Loan Over Equity"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.set_ylabel("Bank Leverage")
    ax2.set_xlabel("Year")
    ax2.legend()

    ax3 = plt.subplot2grid((9, 2), (7, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["Bank Loan Over Equity"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Bank Loan Over Equity"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Bank Leverage")

    ax2 = plt.subplot2grid((9, 2), (8, 0))
    ax2.margins(0.1)
    ax2.plot(
        [
            (
                results.variables.EconModel["GDP"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
                - results.variables.EconModel["GDP"][
                    results.variables.EconModel["BankDataWriter"].keys()[i - 1]
                ].sum()
            )
            * 100
            / (
                results.variables.EconModel["GDP"][
                    results.variables.EconModel["BankDataWriter"].keys()[i - 1]
                ].sum()
                + eps
            )
            for i in range(51, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["GDP"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
            and results.variables.EconModel["GDP"][
                results.variables.EconModel["BankDataWriter"].keys()[i - 1]
            ]
            is not None
        ]
    )
    ax2.set_ylabel("GDP Increase")
    ax2.set_xlabel("Year")
    ax2.legend()

    ax3 = plt.subplot2grid((9, 2), (8, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["GDP"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
                - results.variables.EconModel["GDP"][
                    results.variables.EconModel["BankDataWriter"].keys()[i - 1]
                ].sum()
            )
            * 100
            / (
                results.variables.EconModel["GDP"][
                    results.variables.EconModel["BankDataWriter"].keys()[i - 1]
                ].sum()
                + eps
            )
            for i in range(51, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["GDP"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
            and results.variables.EconModel["GDP"][
                results.variables.EconModel["BankDataWriter"].keys()[i - 1]
            ]
            is not None
        ]
    )
    ax3.boxplot(data)
    ax3.set_ylabel("GDP Increase")

    if os.path.isdir(saveFolder):
        plt.savefig(f"{saveFolder}/BankSummary.png")
    else:
        os.mkdir(saveFolder)
        plt.savefig(f"{saveFolder}/BankSummary.png")


def plotGoodsFirmsProfitSummary(results, saveFolder):
    plt.figure(figsize=(36, 27))
    plt.subplots_adjust(hspace=0.5)

    ax1 = plt.subplot2grid((5, 2), (0, 0))
    ax1.margins(0.1)
    ax1.plot(
        [
            (
                results.variables.EconModel["CS Net Profits"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Net Profits"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax1.set_ylabel("Consumer Goods Firms Net Profits")
    ax1.set_xlabel("Year")

    ax1 = plt.subplot2grid((5, 2), (1, 0))
    ax1.margins(0.1)
    ax1.plot(
        [
            (
                results.variables.EconModel["CP Net Profits"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Net Profits"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax1.set_ylabel("Capital Goods Firms Net Profits")
    ax1.set_xlabel("Year")

    ax2 = plt.subplot2grid((5, 2), (2, 0))
    ax2.margins(0.1)
    ax2.plot(
        [
            (
                results.variables.EconModel["CS Loan Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Loan Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="ConsumptionGoods Loan Demand",
    )
    ax2.plot(
        [
            (
                results.variables.EconModel["CS Loan Obtained"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Loan Obtained"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="ConsumptionGoods Loan Obtained",
    )
    ax2.plot(
        [
            (
                results.variables.EconModel["CP Loan Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Loan Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="CapitalGoods Loan Demand",
    )
    ax2.plot(
        [
            (
                results.variables.EconModel["CP Loan Obtained"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Loan Obtained"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="CapitalGoods Loan Obtained",
    )
    ax2.set_ylabel("Loans")
    ax2.set_xlabel("Year")
    ax2.legend()

    ax3 = plt.subplot2grid((5, 2), (3, 0))
    ax3.margins(0.1)
    ax3.plot(
        [
            (
                results.variables.EconModel["CS Firm Loans"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Firm Loans"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.set_ylabel("Consumer Goods Firms Loans")
    ax3.set_xlabel("Year")

    ax3 = plt.subplot2grid((5, 2), (4, 0))
    ax3.margins(0.1)
    ax3.plot(
        [
            (
                results.variables.EconModel["CP Firm Loans"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].sum()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Firm Loans"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.set_ylabel("Capital Goods Firms Loans")
    ax3.set_xlabel("Year")

    ax1 = plt.subplot2grid((5, 2), (0, 1))
    ax1.margins(0.1)
    data = []
    [
        data.append(
            [
                (
                    results.variables.EconModel["CS Net Profits"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][j]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS Net Profits"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
        for j in range(len(results.variables.EconModel["CS Net Profits"][0]))
    ]
    ax1.boxplot(data)
    ax1.set_ylabel("Consumer Goods Firms Net Profits")

    ax1 = plt.subplot2grid((5, 2), (1, 1))
    ax1.margins(0.1)
    data = []
    [
        data.append(
            [
                (
                    results.variables.EconModel["CP Net Profits"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][j]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP Net Profits"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
        for j in range(len(results.variables.EconModel["CP Net Profits"][0]))
    ]
    ax1.boxplot(data)
    ax1.set_ylabel("Capital Goods Firms Net Profits")

    ax3 = plt.subplot2grid((5, 2), (3, 1))
    ax3.margins(0.1)
    data = []
    [
        data.append(
            [
                (
                    results.variables.EconModel["CS Firm Loans"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][j]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS Firm Loans"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
        for j in range(len(results.variables.EconModel["CS Firm Loans"][0]))
    ]
    ax3.boxplot(data)
    ax3.set_ylabel("Consumer Goods Firms Loans")

    ax3 = plt.subplot2grid((5, 2), (4, 1))
    ax3.margins(0.1)
    data = []
    [
        data.append(
            [
                (
                    results.variables.EconModel["CP Firm Loans"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][j]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP Firm Loans"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
        for j in range(len(results.variables.EconModel["CP Firm Loans"][0]))
    ]
    ax3.boxplot(data)
    ax3.set_ylabel("Capital Goods Firms Loans")

    if os.path.isdir(saveFolder):
        plt.savefig(f"{saveFolder}/GoodsFirmsProfitSummary.png")
    else:
        os.mkdir(saveFolder)
        plt.savefig(f"{saveFolder}/GoodsFirmsProfitSummary.png")


def plotGoodsFirmsDemandsSummary(results, saveFolder):
    plt.figure(figsize=(36, 27))
    plt.subplots_adjust(hspace=0.5)

    ax1 = plt.subplot2grid((8, 2), (0, 0))
    ax1.margins(0.1)
    lines = ax1.plot(
        [
            (
                results.variables.EconModel["CS Labour Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Labour Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax1.set_ylabel("Consumer Goods Firms Labour Demand")
    ax1.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Consumer Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CS Labour Demand"][0]))
        ],
    )

    ax3 = plt.subplot2grid((8, 2), (1, 0))
    ax3.margins(0.1)
    lines = ax3.plot(
        [
            (
                results.variables.EconModel["CS Capital Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Capital Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.set_ylabel("Consumer Goods Capital Demand")
    ax3.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Consumer Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CS Capital Demand"][0]))
        ],
    )

    ax3 = plt.subplot2grid((8, 2), (2, 0))
    ax3.margins(0.1)
    lines = ax3.plot(
        [
            (
                results.variables.EconModel["CS Capital"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Capital"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.set_ylabel("Consumer Goods Capital")
    ax3.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Consumer Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CS Capital"][0]))
        ],
    )

    ax3 = plt.subplot2grid((8, 2), (3, 0))
    ax3.margins(0.1)
    lines = ax3.plot(
        [
            (
                results.variables.EconModel["CS Demand Forecast"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].squeeze()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Demand Forecast"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.set_ylabel("Consumer Goods Forecast Demand")
    ax3.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Consumer Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CS Demand Forecast"][0]))
        ],
    )

    ax1 = plt.subplot2grid((8, 2), (4, 0))
    ax1.margins(0.1)
    lines = ax1.plot(
        [
            (
                results.variables.EconModel["CP Labour Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Labour Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax1.set_ylabel("Capital Goods Firms Labour Demand")
    ax1.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Capital Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CP Labour Demand"][0]))
        ],
    )

    ax3 = plt.subplot2grid((8, 2), (5, 0))
    ax3.margins(0.1)
    lines = ax3.plot(
        [
            (
                results.variables.EconModel["CP Capital Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Capital Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.set_ylabel("Capital Goods Capital Demand")
    ax3.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Capital Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CP Capital Demand"][0]))
        ],
    )

    ax3 = plt.subplot2grid((8, 2), (6, 0))
    ax3.margins(0.1)
    lines = ax3.plot(
        [
            (
                results.variables.EconModel["CP Capital"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Capital"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.set_ylabel("Capital Goods Capital")
    ax3.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Capital Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CP Capital"][0]))
        ],
    )

    ax3 = plt.subplot2grid((8, 2), (7, 0))
    ax3.margins(0.1)
    lines = ax3.plot(
        [
            (
                results.variables.EconModel["CP Demand Forecast"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ].squeeze()
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Demand Forecast"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.set_ylabel("Capital Goods Forecast Demand")
    plt.legend(
        lines,
        [
            f"Capital Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CP Demand Forecast"][0]))
        ],
    )

    ax1 = plt.subplot2grid((8, 2), (0, 1))
    ax1.margins(0.1)
    data = np.array(
        [
            (
                results.variables.EconModel["CS Labour Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Labour Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax1.boxplot(data)
    ax1.set_ylabel("Consumer Goods Firms Labour Demand")

    ax3 = plt.subplot2grid((8, 2), (1, 1))
    ax3.margins(0.1)
    ax3.boxplot(
        np.array(
            [
                (
                    results.variables.EconModel["CS Capital Demand"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS Capital Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.set_ylabel("Consumer Goods Capital Demand")

    ax3 = plt.subplot2grid((8, 2), (2, 1))
    ax3.margins(0.1)
    ax3.boxplot(
        np.array(
            [
                (
                    results.variables.EconModel["CS Capital"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS Capital"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.set_ylabel("Consumer Goods Capital")

    ax3 = plt.subplot2grid((8, 2), (3, 1))
    ax3.margins(0.1)
    ax3.boxplot(
        np.array(
            [
                (
                    results.variables.EconModel["CS Demand Forecast"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ].squeeze()
                )
                for i in range(
                    50, len(results.variables.EconModel["BankDataWriter"]) - 50
                )
                if results.variables.EconModel["CS Demand Forecast"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.set_ylabel("Consumer Goods Forecast Demand")

    ax1 = plt.subplot2grid((8, 2), (4, 1))
    ax1.margins(0.1)
    ax1.boxplot(
        np.array(
            [
                (
                    results.variables.EconModel["CP Labour Demand"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP Labour Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax1.set_ylabel("Capital Goods Firms Labour Demand")

    ax3 = plt.subplot2grid((8, 2), (5, 1))
    ax3.margins(0.1)
    ax3.boxplot(
        np.array(
            [
                (
                    results.variables.EconModel["CP Capital Demand"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP Capital Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.set_ylabel("Capital Goods Capital Demand")

    ax3 = plt.subplot2grid((8, 2), (6, 1))
    ax3.margins(0.1)
    ax3.boxplot(
        np.array(
            [
                (
                    results.variables.EconModel["CP Capital"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP Capital"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.set_ylabel("Capital Goods Capital")

    ax3 = plt.subplot2grid((8, 2), (7, 1))
    ax3.margins(0.1)
    ax3.boxplot(
        np.array(
            [
                (
                    results.variables.EconModel["CP Demand Forecast"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ].squeeze()
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP Demand Forecast"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.set_ylabel("Capital Goods Forecast Demand")

    if os.path.isdir(saveFolder):
        plt.savefig(f"{saveFolder}/GoodsFirmsDemandsSummary.png")
    else:
        os.mkdir(saveFolder)
        plt.savefig(f"{saveFolder}/GoodsFirmsDemandsSummary.png")


def plotEnergyFirmsDemands(results, saveFolder):
    plt.figure(figsize=(36, 27))
    plt.subplots_adjust(hspace=0.5)

    ax3 = plt.subplot(521)
    ax3.margins(0.1)
    ax3.plot(
        [
            (
                results.variables.EconModel["GE Labour Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["GE Labour Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Green Energy",
    )
    ax3.plot(
        [
            (
                results.variables.EconModel["BE Labour Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["BE Labour Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Brown Energy",
    )
    ax3.set_ylabel("Electricity Labour Demand")
    ax3.set_xlabel("Year")
    ax3.legend()

    ax3 = plt.subplot(523)
    ax3.margins(0.1)
    ax3.plot(
        [
            (
                results.variables.EconModel["GE Demand Forecast"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][0]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["GE Demand Forecast"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Green Energy",
    )
    ax3.plot(
        [
            (
                results.variables.EconModel["BE Demand Forecast"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][0]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["BE Demand Forecast"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Brown Energy",
    )
    ax3.set_ylabel("Electricity Demand Forecast")
    ax3.set_xlabel("Year")
    ax3.legend()

    ax3 = plt.subplot(525)
    ax3.margins(0.1)
    ax3.plot(
        [
            (
                results.variables.EconModel["GE Price"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["GE Price"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Green Energy",
    )
    ax3.plot(
        [
            (
                results.variables.EconModel["BE Price"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["BE Price"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Brown Energy",
    )
    ax3.set_ylabel("Electricity Price")
    ax3.set_xlabel("Year")
    ax3.legend()

    ax3 = plt.subplot(527)
    ax3.margins(0.1)
    ax3.plot(
        [
            (
                results.variables.EconModel["GE Capital"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["GE Capital"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Green Capital",
    )
    ax3.plot(
        [
            (
                results.variables.EconModel["BE Capital"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["BE Capital"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Brown Capital",
    )
    ax3.plot(
        [
            (
                results.variables.EconModel["GE Capital Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["GE Capital Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Green Capital Demand",
    )
    ax3.plot(
        [
            (
                results.variables.EconModel["BE Capital Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["BE Capital Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Brown Capital Demand",
    )
    ax3.set_ylabel("Electricity Capital")
    ax3.set_xlabel("Year")
    ax3.legend()

    ax3 = plt.subplot(522)
    ax3.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["GE Labour Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][0]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["GE Labour Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            (
                results.variables.EconModel["BE Labour Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][0]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["BE Labour Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Electricity Labour Demand")

    ax3 = plt.subplot(524)
    ax3.margins(0.1)
    data = []
    data.append(
        np.array(
            [
                (
                    results.variables.EconModel["GE Demand Forecast"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][0]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["GE Demand Forecast"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    data.append(
        np.array(
            [
                (
                    results.variables.EconModel["BE Demand Forecast"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][0]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["BE Demand Forecast"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Electricity Demand Forecast")

    ax3 = plt.subplot(526)
    ax3.margins(0.1)
    data = []
    data.append(
        np.array(
            [
                (
                    results.variables.EconModel["GE Price"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][0]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["GE Price"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    data.append(
        np.array(
            [
                (
                    results.variables.EconModel["BE Price"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][0]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["BE Price"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Electricity Price")

    ax3 = plt.subplot(528)
    ax3.margins(0.1)
    data = []
    data.append(
        np.array(
            [
                (
                    results.variables.EconModel["GE Capital"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][0]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["GE Capital"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    data.append(
        np.array(
            [
                (
                    results.variables.EconModel["BE Capital"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][0]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["BE Capital"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    data.append(
        np.array(
            [
                (
                    results.variables.EconModel["GE Capital Demand"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][0]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["GE Capital Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    data.append(
        np.array(
            [
                (
                    results.variables.EconModel["BE Capital Demand"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][0]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["BE Capital Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Electricity Capital")

    if os.path.isdir(saveFolder):
        plt.savefig(f"{saveFolder}/EnergyFirmsDemands.png")
    else:
        os.mkdir(saveFolder)
        plt.savefig(f"{saveFolder}/EnergyFirmsDemands.png")


def plotGoodsFirmWorkersSummary(results, saveFolder):
    plt.figure(figsize=(36, 27))
    plt.subplots_adjust(hspace=0.5)

    ax1 = plt.subplot(421)
    ax1.margins(0.1)
    lines = ax1.plot(
        [
            (
                results.variables.EconModel["CS Number of Workers"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Number of Workers"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax1.set_ylabel("Consumer Goods Firms Number of Workers")
    ax1.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Consumer Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CS Labour Demand"][0]))
        ],
    )

    ax1 = plt.subplot(425)
    ax1.margins(0.1)
    lines = ax1.plot(
        [
            (
                results.variables.EconModel["CP Number of Workers"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Number of Workers"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax1.set_ylabel("Capital Goods Firms Number of Workers")
    ax1.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Capital Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CP Capital"][0]))
        ],
    )

    ax2 = plt.subplot(423)
    ax2.margins(0.1)
    lines = ax2.plot(
        [
            (
                results.variables.EconModel["CS Number of Consumers"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Number of Consumers"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.set_ylabel("Consumer Goods Firms Number of Consumers")
    ax2.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Consumer Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CS Labour Demand"][0]))
        ],
    )

    ax3 = plt.subplot(427)
    ax3.margins(0.1)
    lines = ax3.plot(
        [
            (
                results.variables.EconModel["CP Number of Consumers"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Number of Consumers"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.set_ylabel("Capital Goods Firms Number of Consumers")
    ax3.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Capital Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CP Capital"][0]))
        ],
    )

    ax1 = plt.subplot(422)
    ax1.margins(0.1)
    ax1.boxplot(
        np.array(
            [
                (
                    results.variables.EconModel["CS Number of Workers"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS Number of Workers"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax1.set_ylabel("Consumer Goods Firms Number of Workers")

    ax1 = plt.subplot(426)
    ax1.margins(0.1)
    ax1.boxplot(
        np.array(
            [
                (
                    results.variables.EconModel["CP Number of Workers"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP Number of Workers"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax1.set_ylabel("Capital Goods Firms Number of Workers")

    ax2 = plt.subplot(424)
    ax2.margins(0.1)
    ax2.boxplot(
        np.array(
            [
                (
                    results.variables.EconModel["CS Number of Consumers"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS Number of Consumers"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax2.set_ylabel("Consumer Goods Firms Number of Consumers")

    ax3 = plt.subplot(428)
    ax3.margins(0.1)
    ax3.boxplot(
        np.array(
            [
                (
                    results.variables.EconModel["CP Number of Consumers"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP Number of Consumers"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.set_ylabel("Capital Goods Firms Number of Consumers")

    if os.path.isdir(saveFolder):
        plt.savefig(f"{saveFolder}/GoodsFirmWorkersSummary.png")
    else:
        os.mkdir(saveFolder)
        plt.savefig(f"{saveFolder}/GoodsFirmWorkersSummary.png")


def plotGoodsFirmSalesSummary(results, saveFolder):
    plt.figure(figsize=(56, 27))
    plt.subplots_adjust(hspace=0.5)

    ax1 = plt.subplot2grid((10, 2), (0, 0))
    ax1.margins(0.1)
    lines = ax1.plot(
        [
            (
                results.variables.EconModel["CS Price"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Price"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax1.set_ylabel("Consumer Goods Firms Price")
    ax1.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Consumer Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CS Labour Demand"][0]))
        ],
    )

    ax1 = plt.subplot2grid((10, 2), (1, 0))
    ax1.margins(0.1)
    lines = ax1.plot(
        [
            (
                results.variables.EconModel["CP Price"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Price"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax1.set_ylabel("Capital Goods Firms Price")
    ax1.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Capital Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CP Capital"][0]))
        ],
    )

    ax2 = plt.subplot2grid((10, 2), (2, 0))
    ax2.margins(0.1)
    lines = ax2.plot(
        [
            (
                results.variables.EconModel["CS Sold Products"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Sold Products"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.set_ylabel("Consumer Goods Firms Sold Products")
    ax2.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Consumer Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CS Labour Demand"][0]))
        ],
    )

    ax3 = plt.subplot2grid((10, 2), (3, 0))
    ax3.margins(0.1)
    lines = ax3.plot(
        [
            (
                results.variables.EconModel["CP Sold Products"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Sold Products"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.set_ylabel("Capital Goods Firms Sold Products")
    ax3.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Capital Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CP Capital"][0]))
        ],
    )

    ax2 = plt.subplot2grid((10, 2), (4, 0))
    ax2.margins(0.1)
    lines = ax2.plot(
        [
            (
                results.variables.EconModel["CS Inventory"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Inventory"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.set_ylabel("Consumer Goods Firms Inventory")
    ax2.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Consumer Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CS Labour Demand"][0]))
        ],
    )

    ax2 = plt.subplot2grid((10, 2), (5, 0))
    ax2.margins(0.1)
    lines = ax2.plot(
        [
            (
                results.variables.EconModel["CP Inventory"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Inventory"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.set_ylabel("Capital Goods Firms Inventory")
    ax2.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Capital Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CS Labour Demand"][0]))
        ],
    )

    ax2 = plt.subplot2grid((10, 2), (6, 0))
    ax2.margins(0.1)
    lines = ax2.plot(
        [
            (
                results.variables.EconModel["CS Energy Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Energy Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.set_ylabel("Consumer Goods Firms Energy Demand")
    ax2.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Consumer Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CS Energy Demand"][0]))
        ],
    )

    ax2 = plt.subplot2grid((10, 2), (7, 0))
    ax2.margins(0.1)
    lines = ax2.plot(
        [
            (
                results.variables.EconModel["CP Energy Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Energy Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.set_ylabel("Capital Goods Firms Energy Demand")
    ax2.set_xlabel("Year")
    plt.legend(
        lines,
        [
            f"Capital Goods Firm no.{i+1}"
            for i in range(len(results.variables.EconModel["CP Energy Demand"][0]))
        ],
    )

    ax2 = plt.subplot2grid((10, 2), (8, 0))
    ax2.margins(0.1)
    lines = ax2.plot(
        [
            (
                np.sum(
                    results.variables.EconModel["CS V Cost"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS V Cost"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="VC",
    )
    lines = ax2.plot(
        [
            (
                np.sum(
                    results.variables.EconModel["CS U Cost"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS U Cost"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="UC",
    )
    lines = ax2.plot(
        [
            (
                np.sum(
                    results.variables.EconModel["CS Q Cost"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Q Cost"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="QC",
    )
    ax2.set_ylabel("Consumer Goods Firms Costs")
    ax2.set_xlabel("Year")
    plt.legend()

    ax2 = plt.subplot2grid((10, 2), (8, 0))
    ax2.margins(0.1)
    lines = ax2.plot(
        [
            (
                np.sum(
                    results.variables.EconModel["CP V Cost"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP V Cost"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="VC",
    )
    lines = ax2.plot(
        [
            (
                np.sum(
                    results.variables.EconModel["CP U Cost"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                )
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP U Cost"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="UC",
    )
    # lines=ax2.plot([(np.sum(results.variables.EconModel['CP Q Cost'][results.variables.EconModel['BankDataWriter'].keys()[i]])) for i in range(50,len(results.variables.EconModel['BankDataWriter'])) if results.variables.EconModel['Expected Inflation Rate'][results.variables.EconModel['BankDataWriter'].keys()[i]] is not None], label='QC')
    ax2.set_ylabel("Capital Goods Firms Costs")
    ax2.set_xlabel("Year")
    plt.legend()

    ax1 = plt.subplot2grid((10, 2), (0, 1))
    ax1.margins(0.1)
    data = np.array(
        [
            (
                results.variables.EconModel["CS Price"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Price"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    for d in data:
        ax1.boxplot(data)
    ax1.set_ylabel("Consumer Goods Firms Price")

    ax1 = plt.subplot2grid((10, 2), (1, 1))
    ax1.margins(0.1)
    data = np.array(
        [
            (
                results.variables.EconModel["CP Price"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Price"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    for d in data:
        ax1.boxplot(data)
    ax1.set_ylabel("Capital Goods Firms Price")

    ax2 = plt.subplot2grid((10, 2), (2, 1))
    ax2.margins(0.1)
    data = np.array(
        [
            (
                results.variables.EconModel["CS Sold Products"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Sold Products"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    for d in data:
        ax2.boxplot(data)
    ax2.set_ylabel("Consumer Goods Firms Sold Products")

    ax3 = plt.subplot2grid((10, 2), (3, 1))
    ax3.margins(0.1)
    data = np.array(
        [
            (
                results.variables.EconModel["CP Sold Products"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Sold Products"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Capital Goods Firms Sold Products")

    ax2 = plt.subplot2grid((10, 2), (4, 1))
    ax2.margins(0.1)
    data = np.array(
        [
            (
                results.variables.EconModel["CS Inventory"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Inventory"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.boxplot(data)
    ax2.set_ylabel("Consumer Goods Firms Inventory")

    ax2 = plt.subplot2grid((10, 2), (5, 1))
    ax2.margins(0.1)
    data = np.array(
        [
            (
                results.variables.EconModel["CP Inventory"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Inventory"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.boxplot(data)
    ax2.set_ylabel("Capital Goods Firms Inventory")

    ax2 = plt.subplot2grid((10, 2), (6, 1))
    ax2.margins(0.1)
    data = np.array(
        [
            (
                results.variables.EconModel["CS Energy Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CS Energy Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.boxplot(data)
    ax2.set_ylabel("Consumer Goods Firms Energy Demand")

    ax2 = plt.subplot2grid((10, 2), (7, 1))
    ax2.margins(0.1)
    data = np.array(
        [
            (
                results.variables.EconModel["CP Energy Demand"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["CP Energy Demand"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax2.boxplot(data)
    ax2.set_ylabel("Capital Goods Firms Energy Demand")

    ax2 = plt.subplot2grid((10, 2), (8, 1))
    ax2.margins(0.1)
    data = []
    data.append(
        np.array(
            [
                (
                    np.sum(
                        results.variables.EconModel["CS V Cost"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                    )
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS V Cost"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    data.append(
        np.array(
            [
                (
                    np.sum(
                        results.variables.EconModel["CS U Cost"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                    )
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS U Cost"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    data.append(
        np.array(
            [
                (
                    np.sum(
                        results.variables.EconModel["CS Q Cost"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                    )
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS Q Cost"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax2.boxplot(data)
    ax2.set_ylabel("Consumer Goods Firms Costs")

    ax2 = plt.subplot2grid((10, 2), (9, 1))
    ax2.margins(0.1)
    data = []
    data.append(
        np.array(
            [
                (
                    np.sum(
                        results.variables.EconModel["CP V Cost"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                    )
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CP V Cost"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    data.append(
        np.array(
            [
                (
                    np.sum(
                        results.variables.EconModel["CP U Cost"][
                            results.variables.EconModel["BankDataWriter"].keys()[i]
                        ]
                    )
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["CS U Cost"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    # data.append(np.array([(np.sum(results.variables.EconModel['CP Q Cost'][results.variables.EconModel['BankDataWriter'].keys()[i]])) for i in range(50,len(results.variables.EconModel['BankDataWriter'])) if results.variables.EconModel['Expected Inflation Rate'][results.variables.EconModel['BankDataWriter'].keys()[i]] is not None]))
    ax2.boxplot(data)
    ax2.set_ylabel("Capital Goods Firms Costs")

    if os.path.isdir(saveFolder):
        plt.savefig(f"{saveFolder}/GoodsFirmSalesSummary.png")
    else:
        os.mkdir(saveFolder)
        plt.savefig(f"{saveFolder}/GoodsFirmSalesSummary.png")


def plotClimateModuleEffects(results, saveFolder):
    plt.figure(figsize=(36, 27))
    plt.subplots_adjust(hspace=0.5)

    ax3 = plt.subplot2grid((10, 2), (0, 0))
    ax3.margins(0.1)
    ax3.plot(
        [
            (
                results.variables.EconModel["Climate C02 Taxes"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Climate C02 Taxes"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Climate C02 Taxes",
    )
    ax3.set_ylabel("Climate C02 Taxes")
    ax3.set_xlabel("Year")
    ax3.legend()

    ax3 = plt.subplot2grid((10, 2), (1, 0))
    ax3.margins(0.1)
    ax3.plot(
        [
            (
                results.variables.EconModel["Climate C02"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            / 1e9
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Climate C02"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Climate C02 (GtCO2)",
    )
    ax3.set_ylabel("Climate C02")
    ax3.set_xlabel("Year")
    ax3.legend()

    ax3 = plt.subplot2grid((10, 2), (2, 0))
    ax3.margins(0.1)
    ax3.plot(
        [
            (
                results.variables.EconModel["Climate Radiative Forcing"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][0]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Climate Radiative Forcing"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Climate Radiative Forcing",
    )
    ax3.set_ylabel("Climate Radiative Forcing")
    ax3.set_xlabel("Year")
    ax3.legend()

    ax3 = plt.subplot2grid((10, 2), (3, 0))
    ax3.margins(0.1)
    ax3.plot(
        [
            (
                results.variables.EconModel["Climate Temperature"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Climate Temperature"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Climate Temperature",
    )
    ax3.set_ylabel("Climate Temperature")
    ax3.set_xlabel("Year")
    ax3.legend()

    ax3 = plt.subplot2grid((10, 2), (4, 0))
    ax3.margins(0.1)
    ax3.plot(
        [
            (
                results.variables.EconModel["Climate ETD"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Climate ETD"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Climate ETD",
    )
    ax3.plot(
        [
            (
                results.variables.EconModel["Climate ETM"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Climate ETM"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Climate ETM",
    )
    ax3.set_ylabel("Climate Aggregate Damage")
    ax3.set_xlabel("Year")
    ax3.legend()

    ax3 = plt.subplot2grid((10, 2), (0, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["Climate C02 Taxes"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Climate C02 Taxes"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Climate C02 Taxes")

    ax3 = plt.subplot2grid((10, 2), (1, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        [
            (
                results.variables.EconModel["Climate C02 Concentration"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ][0]
                / 1e9
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Climate C02 Concentration"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Climate C02 Concentration")

    ax3 = plt.subplot2grid((10, 2), (2, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        np.array(
            [
                (
                    results.variables.EconModel["Climate Radiative Forcing"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][0]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["Climate Radiative Forcing"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Climate Radiative Forcing")

    ax3 = plt.subplot2grid((10, 2), (3, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        np.array(
            [
                (
                    results.variables.EconModel["Climate Temperature"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][0]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["Climate Temperature"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Climate Temperature")

    ax3 = plt.subplot2grid((10, 2), (4, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        np.array(
            [
                (
                    results.variables.EconModel["Climate ETD"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ][0]
                )
                for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
                if results.variables.EconModel["Climate ETD"][
                    results.variables.EconModel["BankDataWriter"].keys()[i]
                ]
                is not None
            ]
        )
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Climate Aggregate Damage")

    if os.path.isdir(saveFolder):
        plt.savefig(f"{saveFolder}/ClimateModule.png")
    else:
        os.mkdir(saveFolder)
        plt.savefig(f"{saveFolder}/ClimateModule.png")


def plotCovidStatistics(results, saveFolder):

    plt.figure(figsize=(36, 27))
    plt.subplots_adjust(hspace=0.5)

    ax3 = plt.subplot2grid((2, 2), (0, 0))
    ax3.margins(0.1)
    ax3.plot(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == None
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Normal",
    )
    ax3.plot(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "susceptible"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Susceptible",
    )
    ax3.plot(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "mild"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Mild",
    )
    ax3.plot(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "infected non-sympotomatic"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Infected non-sympotomatic",
    )
    ax3.plot(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "severe"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Severe",
    )
    ax3.plot(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "critical"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Critical",
    )
    ax3.plot(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "dead"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Dead",
    )
    ax3.plot(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "recovered"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Recovered",
    )
    ax3.plot(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "immunized"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ],
        label="Immunized",
    )
    ax3.set_ylabel("Covid State Over Time (Days)")
    ax3.set_xlabel("Day")
    ax3.legend()

    ax3 = plt.subplot2grid((2, 2), (0, 1))
    ax3.margins(0.1)
    data = []
    data.append(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == None
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "susceptible"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "mild"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "infected non-sympotomatic"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "severe"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "critical"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "dead"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "recovered"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    data.append(
        [
            len(
                [
                    state
                    for state in results.variables.EconModel["Covid State"][
                        results.variables.EconModel["BankDataWriter"].keys()[i]
                    ]
                    if state == "immunized"
                ]
            )
            for i in range(50, len(results.variables.EconModel["BankDataWriter"]))
            if results.variables.EconModel["Covid State"][
                results.variables.EconModel["BankDataWriter"].keys()[i]
            ]
            is not None
        ]
    )
    ax3.boxplot(data)
    ax3.set_ylabel("Covid State Over Time")

    if os.path.isdir(saveFolder):
        plt.savefig(f"{saveFolder}/CovidStat.png")
    else:
        os.mkdir(saveFolder)
        plt.savefig(f"{saveFolder}/CovidStat.png")


def lognormal(mu, sigma):
    mean = math.log(mu**2 / math.sqrt(sigma + mu**2))
    std = math.sqrt(math.log(sigma / mu**2 + 1))
    y = np.random.lognormal(mean, std)
    return y


def normal(mu, sigma):
    mean = mu
    std = math.sqrt(sigma)
    y = np.random.normal(mean, std)
    return y


### Unused functions:


def setSignalToFirmForHiring(self):
    self.signalToFirmForHiring = (
        self.p.signalParameterOfProductivity * self.productivity
        + self.p.signalParameterOfRandomComponent
        * (random.random() - 0.5)
        * self.p.productivityParetoPositionParameter
        + self.desiredEConsumption * self.p.EnergyToProductivity
    )


def getSignalToFirmForHiring(self):
    return self.signalToFirmForHiring
