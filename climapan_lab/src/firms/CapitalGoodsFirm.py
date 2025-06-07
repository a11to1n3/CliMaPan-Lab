import copy
from collections import OrderedDict

import jaxabm.agentpy as ap
import numpy as np
import numpy.random as random
from scipy.optimize import minimize

from ..param_dict import ParamDict
from ..utils import days_in_month
from .GoodsFirmBase import GoodsFirmBase


class CapitalGoodsFirm(GoodsFirmBase):
    """A CapitalGoodsFirm agent"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.p = ParamDict(self.p)

    def setup(self):
        super().setup()

        # Main variables
        self.wages = {}
        self.price = 1
        self.capital = 0
        self.labour = 0
        self.equity = 0
        self.deposit = 10000

        # parameter
        self.beta_capital = self.p.beta_capital_K
        self.beta_labour = self.p.beta_labour_K
        self.beta_energy = self.p.beta_energy_K
        self.eta_production = self.p.ETA_PRODUCTION_CAPITAL
        self.rho_labour = self.p.rho_labour_K
        self.rho_energy = self.p.rho_energy_K
        # self.capital_multiplier = self.p.capital_multiplier #currently not use
        self.capital_growth_rate = self.p.capital_growth_rate
        self.mark_up = self.p.mark_up_factor
        self.mark_up_alpha = self.p.mark_up_alpha
        self.mark_up_beta = self.p.mark_up_beta
        self.carbon_tax_state = self.p.settings.find("CT") != -1
        self.div_ratio = self.p.ownerProportionFromProfits
        self.capital_depreciation = self.p.depreciationRate
        self.forecast_discount_factor = self.p.forecast_discount_factor

        # transitory variables
        self.actual_production = 0
        self.planned_production = 1500
        self.labour_demand = 0
        self.aggregate_demand = 20000
        self.energy = 0
        self.brown_firm = self.useEnergy == "brown"
        self.capital_investment = 0  # value variable
        self.capital_increase = 165  # physical variable
        self.capital_price = self.price
        self.capital_value = self.capital * self.capital_price  # value variable
        self.cost_of_capital = 0  # value variable
        self.average_production_cost = 0

        if self.brown_firm:
            self.capital = 5000
        else:
            self.capital = 4200

    def prepareForecast(self):
        """"""
        self.set_aggregate_demand(0)
        self.soldProducts = 0
        state_ok = self.model.aliveConsumers.getCovidStateAttr("state") != "dead"
        working = self.model.aliveConsumers.getAgeGroup() == "working"
        self.consumersList = self.model.aliveConsumers.select(state_ok & working)

    def calculate_input_demand(self):
        """"""
        beta = self.forecast_discount_factor
        # This function is used to calculate all inputs and related demands
        self.planned_production = (
            beta * self.sale_record + (1 - beta) * self.get_aggregate_demand()
        ) + self.capital_increase
        # print("capital planned production", self.planned_production)
        self.labour_demand = 0.15 * self.model.num_worker / self.p.cpf_agents
        self.energy = self.optimize_energy(self.labour_demand, self.capital)
        # print("capital input", self.energy, self.labour_demand, self.capital)

    def produce(self):
        # This function is to calculate the actual production value based on the inputs of current period
        # Check production function in GoodsFirmBase
        # print("worker list", len(self.workersList), self.getNumberOfLabours())
        aggSickLeaves = np.sum(
            [
                len(aConsumer.getSickLeaves())
                for aConsumer in self.consumersList
                if aConsumer.getBelongToFirm() == self.id
            ]
        )
        # print("sick leave", aggSickLeaves)
        sick_ratio = np.min(
            [1, np.max([0, aggSickLeaves / (720 * len(self.workersList))])]
        )
        # print("sick ratio", sick_ratio)

        labour_input = self.labour_demand
        capital_input = self.get_capital()
        energy_input = self.get_energy()
        if self.p.verboseFlag:
            print(
                "capital input",
                self.get_energy(),
                self.labour_demand,
                self.get_capital(),
            )
        production_value = self.production_function(
            (capital_input, labour_input, energy_input)
        ) * (1 - sick_ratio)
        # print("capital production value")
        self.set_actual_production(
            production_value - self.capital_increase
        )  # capital firm automatically take away the capital they need for own expansion
        # print("\ndemand", self.planned_production,"net capital production", self.get_actual_production(), self.capital_increase, "total capital", self.capital)

    def price_setting(self):
        """Function to set price base on mark up over cost"""

        ## calculate cost
        self.calculate_average_production_cost()

        ## set price
        self.price = self.get_average_production_cost() * (1 + self.mark_up)
        self.set_capital_price(
            self.price
        )  # for capital firm, capital price is their own price (basically net zero)
        self.priceList.append(np.sum([self.getPrice()]))

    def compute_net_profit(self, eps=1e-8):
        # function to calculate profit
        # Wage component
        if self.wage_bill > 0:
            self.unitWageBill = self.wage_bill / (self.getNumberOfLabours() + eps)
        else:
            self.unitWageBill = 0  ##if firm demand 0 labour it means it shut down?

        self.countWorkers = self.getNumberOfLabours()

        if self.p.verboseFlag:
            print(
                f"Number of workers in Capital Goods Firm no. {self.id - self.p.c_agents - self.p.csf_agents - 1 - 1} is {self.countWorkers}"
            )

        # determint loan payback
        self.progressPayback()

        # Calculating Profit
        self.profits = (
            self.p.bankID * self.deposit
            + self.getSoldProducts() * self.getPrice()
            - self.get_average_production_cost() * self.get_actual_production()
            + self.payback
        )  # - self.inn
        # Net Profit after Tax
        self.updateProfitsAfterTax(isC02Taxed=self.carbon_tax_state * self.brown_firm)
        # pay income to firm owner
        self.ownerIncome = np.max([0, self.net_profit])
        self.updateDeposit(self.net_profit - self.ownerIncome)

    def update_capital_growth(self):
        self.capital_growth = self.get_capital() * (
            self.capital_growth_rate + self.capital_depreciation
        )
        # for capital firm, capital growth is what they produce inhouse
