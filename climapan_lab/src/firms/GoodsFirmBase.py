import copy
from collections import OrderedDict

import agentpy as ap
import numpy as np
import numpy.random as random
from scipy.optimize import minimize

from ..utils import days_in_month


class GoodsFirmBase(ap.Agent):
    """A GoodsFirmBase agent"""

    def setup(self):

        # Main variables
        self.workersList = []
        self.wages = {}
        self.price = 0
        self.capital = 0
        self.energy = 0
        self.deposit = 0
        self.equity = 0
        self.net_profit = 0
        self.non_loan = 0

        # parameter
        self.iL = self.p.bankICB
        self.beta_capital = self.p.beta_capital
        self.beta_labour = self.p.beta_labour
        self.beta_energy = self.p.beta_energy
        self.eta_production = self.p.ETA_PRODUCTION
        self.rho_labour = self.p.rho_labour
        self.rho_energy = self.p.rho_energy
        self.capital_growth_rate = self.p.capital_growth_rate
        self.carbon_tax_state = self.p.settings.find("CT") != -1
        self.div_ratio = self.p.ownerProportionFromProfits
        self.capital_depreciation = self.p.depreciationRate
        self.wage_factor = 1 / (1 + self.p.wageAdjustmentRate)

        # Transitory variables
        self.wage_bill = 0
        self.unitWageBill = self.p.unemploymentDole
        self.capital_tracking = []
        self.actual_production = 0  # 10
        self.planned_production = 0
        self.average_production_cost = 0
        self.labour_demand = 0
        self.aggregate_demand = 0
        self.priceList = [1]

        self.capital_investment = 0  # value variable
        self.capital_increase = 0  # physical variable
        self.capital_price = 1
        self.capital_value = self.capital * self.capital_price  # value variable
        self.cost_of_capital = 0  # value variable
        self.capital_purchase = 0  # physical vaariable
        self.capital_demand = 0  # physical variable
        self.capital_growth = 0  # physical variable

        self.useEnergy = None
        self.brown_firm = self.useEnergy == "brown"
        self.firmDataWriter = []

        self.loanObtained = 0
        self.loan_demand = 0
        self.loanList = [0, 0]
        self.loanContractRemainingTime = {}
        self.DTE = 0
        self.iF = 0
        self.reserve_ratio = self.p.reserve_ratio

        self.depositList = [0, 0]
        self.sale_record = 0
        self.profits = 0
        self.fix_cost = 0
        self.ownerIncome = 0
        self.netWorth = 0
        self.countConsumers = 0
        self.countWorkers = 0
        self.carbonTax = 0
        self.defaultProb = 0
        self.bankrupt = False
        self.lockdown = False
        self.lockdownList = []
        self.payback = 0
        self.profit_margin = 0
        self.consumersList = self.model.consumer_agents
        self.sickList = self.model.consumer_agents
        self.tax = 0
        self.soldProducts = 1
        self.workersList = []
        [
            self.workersList.append(aConsumer.id)
            for aConsumer in self.model.aliveConsumers
            if aConsumer.consumerType == "workers"
            and aConsumer.getBelongToFirm() == self.id
            and aConsumer.getCovidStateAttr("state") != "dead"
        ]
        for aConsumer in self.model.aliveConsumers:
            if aConsumer.getIdentity() in self.workersList:
                self.wages[aConsumer.getIdentity()] = aConsumer.getWage()

    def bankrupt_reset(self):
        print("firm get bankrupt!!!", self.id)
        self.netWorth = 0
        self.loanObtained = 0
        self.loanList = [0, 0]
        self.loanContractRemainingTime = {}
        self.payback = 0
        self.bankrupt = False
        self.DTE = 0
        self.deposit = 0
        self.depositList = [0, 0]
        self.fiscal = 0
        self.brown_firm = self.useEnergy == "brown"

    def production_function(self, inputs):
        # Define consumer goods production function
        capital_input, labour_input, energy_input = inputs
        production = (
            self.beta_capital * (capital_input) ** self.eta_production
            + self.beta_labour * (labour_input * self.rho_labour) ** self.eta_production
            + self.beta_energy * (energy_input * self.rho_energy) ** self.eta_production
        ) ** (1 / self.eta_production)
        return production

    def production_budgeting(self):
        """"""
        # print("capital stock", self.capital, self.capital_increase, self.capital_growth)
        # checking if production can be financed, otherwise taking loan if possible
        self.loan_demand = np.max(
            [
                self.get_average_production_cost() * self.planned_production
                - self.deposit * (1 - self.reserve_ratio),
                self.get_average_production_cost() * self.planned_production * 0.2,
            ]
        )
        # self.loan_demand = np.max([self.get_average_production_cost() * self.planned_production, 0])
        if self.loan_demand > 0:
            pass
        else:
            self.loanList.append(0)

            data = [self.getSoldProducts(), self.wage_bill, len(self.workersList)]
            self.firmDataWriter.append(data)

    def calculate_average_production_cost(self):
        # function to derive production cost
        ## Wage Component
        self.calculate_all_wages()
        mean_wage = np.mean(
            list(
                self.consumersList.select(
                    self.consumersList.consumerType == "workers"
                ).getWage()
            )
        )
        # it is probably best to just sum the wage instead of taking average and multiply with number of labour

        ## Energy Component
        energy_price = (
            self.model.brownEFirm[-1].getPrice()
            if self.brown_firm
            else self.model.greenEFirm[-1].getPrice()
        )
        energy_cost = self.get_energy() * energy_price
        # print("energy break down: ", self.id, self.getUseEnergy(), self.get_energy(), energy_price)

        ## Capital Component
        # Need to default value of past periods to 0
        if len(self.capital_tracking) > self.p.capital_length:
            self.capital_tracking.pop(0)
        self.capital_tracking.append(np.sum(self.capital_investment))

        cost_of_capital = np.sum(self.capital_tracking) / self.p.capital_length
        self.cost_of_capital = cost_of_capital
        ##Need to also store the price of capital together with the period so we can do multiplication

        self.average_production_cost = (
            mean_wage * self.getNumberOfLabours() + energy_cost + cost_of_capital
        ) / (self.get_actual_production())
        # print(self.id, " cost of each type: ", self.getUseEnergy(), " wage ", mean_wage * self.getNumberOfLabours(),
        #      " energy ", energy_cost,
        #      " capital ", cost_of_capital, "-", self.capital_price,
        #      " production ", self.get_actual_production())

        self.fix_cost = mean_wage * self.getNumberOfLabours() + cost_of_capital

    def get_actual_production(self):
        return self.actual_production

    def getNumberOfLabours(self):
        return len(self.workersList)

    def update_actual_production(self, value):
        self.actual_production += value

    def getPrice(self):
        return self.price

    def getNetProfit(self):
        return self.net_profit

    def getIdentity(self):
        return self.id

    def getLoan(self):
        return self.loanObtained

    def payLoan(self):
        if -self.payback > 0:
            payback = copy.copy(self.payback)
            for loan_id in [
                i for i in range(len(self.loanList)) if self.loanList[i] > 0
            ]:
                if payback == 0:
                    break
                if -payback <= self.loanList[loan_id]:
                    self.loanList[loan_id] += np.sum(payback)
                    payback = 0
                else:
                    self.loanList[loan_id] = 0
                    payback += np.sum(self.loanList[loan_id])
                if (
                    self.loanList[loan_id] > 0
                    and self.loanContractRemainingTime[loan_id] <= 0
                ):
                    self.bankrupt = True
                elif self.loanList[loan_id] > 0:
                    self.loanContractRemainingTime[loan_id] -= 1
                else:
                    self.loanContractRemainingTime.pop(loan_id)
        else:
            for loan_id in [
                i for i in range(len(self.loanList)) if self.loanList[i] > 0
            ]:
                if (
                    self.loanList[loan_id] > 0
                    and self.loanContractRemainingTime[loan_id] <= 0
                ):
                    self.bankrupt = True
                elif self.loanList[loan_id] > 0:
                    self.loanContractRemainingTime[loan_id] -= 1
                else:
                    self.loanContractRemainingTime.pop(loan_id)

    def updateProfitsAfterTax(self, isC02Taxed=False):
        carbonTax = copy.copy(self.carbonTax) if isC02Taxed else 0
        if self.profits > 0:
            self.net_profit = (1 - self.p.taxRate) * self.profits - carbonTax
            self.updateTax(self.p.taxRate * self.profits + carbonTax)
        else:
            self.net_profit = 1 * self.profits - carbonTax
            self.updateTax(carbonTax)

    def adjustAccordingToBankState(self, obtainedCredit, eps=1e-8):
        """Check bank _calculate_running_loan for the function"""
        ## Credit obtained via bank
        # if obtainedCredit > 0 and len(self.loanContractRemainingTime) == 0:
        if obtainedCredit > 0:
            self.loanObtained = obtainedCredit
            self.loanList.append(np.sum([self.getLoan()]))

            if self.useEnergy == "green":
                self.loanContractRemainingTime[len(self.loanList) - 1] = (
                    self.p.greenLoanRepayPeriod
                )
            else:
                self.loanContractRemainingTime[len(self.loanList) - 1] = (
                    self.p.brownLoanRepayPeriod
                )

        ## Adjust deposit and networth
        self.updateDeposit(np.sum(obtainedCredit))  # adjust deposit if loan is granted
        self.depositList[-1] = self.deposit
        self.netWorth = self.depositList[-1] - sum(self.loanList)

        ## Update other financial variables
        self.DTE = sum(self.loanList) / (self.netWorth + 1e-8)
        self.iF = np.max([0, self.DTE / 100])
        if self.DTE < 0:
            self.defaultProb = 1
        else:
            self.defaultProb = 1 - np.exp(-self.p.defaultProbAlpha * self.DTE)
        # print("default Prob: ", self.defaultProb)
        self.iL = np.max([0, self.p.bankICB * (1 + self.defaultProb)])

        data = [self.soldProducts, self.wage_bill, len(self.workersList)]
        self.firmDataWriter.append(data)

    def update_capital_value(self):
        """"""
        # depreciation update
        self.set_capital(self.get_capital() * (1 - self.capital_depreciation))

        # reflect the purchase of new capital
        self.update_capital_increase(np.sum(self.capital_growth))
        self.set_capital(self.get_capital() + self.get_capital_increase())

        # new value of capital
        self.capital_value = self.get_capital() * self.capital_price

    def setBankruptcy(self):
        if self.getBankrupt() == True or self.getNetWorth() < 0:
            self.model.bankrupt_count += 1
            self.non_loan = np.sum([self.loanList])
            if "ConsumerGoods" in str(self):
                self.model.numCSFirmBankrupt += 1
                if (
                    np.sum(self.model.csfirm_agents.getUseEnergy() == "brown") > 2
                    and np.sum(self.model.csfirm_agents.getUseEnergy() == "green") > 2
                ):
                    if np.random.rand() < 0.5:
                        for wid in self.workersList:
                            self.model.aliveConsumers.select(
                                self.model.aliveConsumers.getIdentity() == wid
                            ).receiveFiring()
                        self.useEnergyType("brown")
                        self.bankrupt_reset()
                    else:
                        for wid in self.workersList:
                            self.model.aliveConsumers.select(
                                self.model.aliveConsumers.getIdentity() == wid
                            ).receiveFiring()
                        self.useEnergyType("green")
                        self.bankrupt_reset()
                elif np.sum(self.model.csfirm_agents.getUseEnergy() == "brown") <= 2:
                    for wid in self.workersList:
                        self.model.aliveConsumers.select(
                            self.model.aliveConsumers.getIdentity() == wid
                        ).receiveFiring()
                    self.useEnergyType("brown")
                    self.bankrupt_reset()
                elif np.sum(self.model.csfirm_agents.getUseEnergy() == "green") <= 2:
                    for wid in self.workersList:
                        self.model.aliveConsumers.select(
                            self.model.aliveConsumers.getIdentity() == wid
                        ).receiveFiring()
                    self.useEnergyType("green")
                    self.bankrupt_reset()
            elif "CapitalGoods" in str(self):
                self.model.numCPFirmBankrupt += 1
                if (
                    np.sum(self.model.cpfirm_agents.getUseEnergy() == "brown") > 1
                    and np.sum(self.model.cpfirm_agents.getUseEnergy() == "green") > 1
                ):
                    if np.random.rand() < 0.5:
                        for wid in self.workersList:
                            self.model.aliveConsumers.select(
                                self.model.aliveConsumers.getIdentity() == wid
                            ).receiveFiring()
                        self.useEnergyType("brown")
                        self.bankrupt_reset()
                    else:
                        for wid in self.workersList:
                            self.model.aliveConsumers.select(
                                self.model.aliveConsumers.getIdentity() == wid
                            ).receiveFiring()
                        self.useEnergyType("green")
                        self.bankrupt_reset()
                elif np.sum(self.model.cpfirm_agents.getUseEnergy() == "brown") <= 1:
                    for wid in self.workersList:
                        self.model.aliveConsumers.select(
                            self.model.aliveConsumers.getIdentity() == wid
                        ).receiveFiring()
                    self.useEnergyType("brown")
                    self.bankrupt_reset()
                elif np.sum(self.model.cpfirm_agents.getUseEnergy() == "green") <= 1:
                    for wid in self.workersList:
                        self.model.aliveConsumers.select(
                            self.model.aliveConsumers.getIdentity() == wid
                        ).receiveFiring()
                    self.useEnergyType("green")
                    self.bankrupt_reset()

    def calculate_all_wages(self):
        # Initialize the total wage bill and calculate the number of days in the current month
        self.wage_bill = 0
        self.wage_factor *= 1 + self.p.wageAdjustmentRate
        # Loop through all consumers and calculate wages for each
        for aConsumer in self.consumersList:
            # Retrieve commonly used values
            self.daysInMonth = days_in_month(
                int(str(self.model.today).split("-")[1]),
                int(str(self.model.today).split("-")[0]),
            )
            days = self.daysInMonth
            sick_leaves = aConsumer.getSickLeaves()
            lockdown_days = len(self.lockdownList)
            unemployment_dole = self.p.unemploymentDole
            pandemic_transfer = self.p.pandemicWageTransfer

            # Check if the consumer's identity is not in the workersList (i.e., not an active worker)
            if aConsumer.getIdentity() not in self.workersList:
                continue

            # If the consumer's identity is not in the wages dictionary, add it and set the initial wage
            if aConsumer.getIdentity() not in self.wages:
                self.wages[aConsumer.id] = aConsumer.getWage()

            wages = self.wages[aConsumer.id]
            # print("wage paid", wages)
            # Wage Setting
            if aConsumer.getEmploymentState():
                if self.model.t < 32:
                    wage = (wages / days) * (days - len(sick_leaves)) + (
                        unemployment_dole / days
                    ) * len(sick_leaves)
                    if self.lockdown:
                        wage = (wages / days) * (
                            days - lockdown_days
                        ) + pandemic_transfer * lockdown_days

                else:
                    wage = (wages / days) * (days - len(sick_leaves)) + (
                        unemployment_dole / days
                    ) * len(sick_leaves)
                    if self.lockdown:
                        wage = (wages / days) * (
                            days - lockdown_days
                        ) + pandemic_transfer * lockdown_days

                wage = (
                    wages
                    / (1 - self.p.incomeTaxRate)
                    * self.wage_factor
                    * (1 - self.p.incomeTaxRate)
                )

                # Update the consumer's wage
                aConsumer.setWage(wage)
                self.updateTax(wage * self.p.incomeTaxRate)
                # Update the total wage bill for this time step
                self.wage_bill += np.sum(
                    aConsumer.getWage() - (unemployment_dole / days) * len(sick_leaves)
                )

    def get_aggregate_demand(self):
        return self.aggregate_demand

    def set_aggregate_demand(self, value):
        self.aggregate_demand = value

    def update_aggregate_demand(self, value):
        self.aggregate_demand += value

    def optimize_energy(self, labour, capital):
        energy = (1 / self.rho_energy) * (
            (
                self.planned_production**self.eta_production
                - (self.beta_labour * (self.rho_labour * labour) ** self.eta_production)
                - (self.beta_capital * (capital) ** self.eta_production)
            )
            / self.beta_energy
        ) ** (1 / self.eta_production)
        if (
            (
                self.planned_production**self.eta_production
                - (self.beta_labour * (self.rho_labour * labour) ** self.eta_production)
                - (self.beta_capital * (capital) ** self.eta_production)
            )
            / self.beta_energy
        ) < 0:
            energy = 0
        return energy

    def set_energy(self, value):
        self.set_energy = value

    def get_energy(self):
        return self.energy

    def set_capital(self, capital):
        self.capital = capital

    def get_capital(self):
        return self.capital

    def set_actual_production(self, actual_production):
        self.actual_production = actual_production

    def get_actual_production(self):
        return self.actual_production

    def set_capital_investment(self, capital_investment):
        self.capital_investment = capital_investment

    def get_capital_investment(self):
        return self.capital_investment

    def setSoldProducts(self, soldProducts):
        self.soldProducts = np.sum(soldProducts)

    def updateSoldProducts(self, soldProducts):
        self.soldProducts += np.sum(soldProducts)

    def getSoldProducts(self):
        return self.soldProducts

    def setPrice(self, price):
        self.price = price

    def getPrice(self):
        return self.price

    def useEnergyType(self, energyType):
        self.useEnergy = energyType

    def getUseEnergy(self):
        return self.useEnergy

    def gov_transfer(self, value):
        self.updateDeposit(value)
        self.depositList[-1] = self.deposit
        self.netWorth += self.depositList[-1]
        self.model.government_agents.expenditure += value

    def getBankrupt(self):
        return self.bankrupt

    def getDeposit(self):
        return self.deposit

    def set_sale_record(self, sale):
        self.sale_record = sale

    def update_sale_record(self, value):
        self.sale_record += value

    def getNetWorth(self):
        return self.netWorth

    def getTax(self):
        return self.tax

    def setTax(self, tax):
        self.tax = tax

    def updateTax(self, value):
        self.tax += value

    def updateDeposit(self, value):
        self.deposit += value

    def append2DepositList(self, deposit):
        self.depositList.append(deposit)

    def get_average_production_cost(self):
        return self.average_production_cost

    def update_capital_increase(self, value):
        self.capital_increase = np.max([0, value])

    def get_capital_increase(self):
        return self.capital_increase

    def get_capital_demand(self):
        return self.capital_demand

    def set_capital_price(self, value):
        # firm will get this info when doing transaction, capital firm know their price
        self.capital_price = value

    def fire(self):
        # function for firm to fire workers
        for (
            id
        ) in (
            self.workersList
        ):  # this line require an update mechanic to fire worker since the worker list shrink as we fire
            worker = self.model.aliveConsumers.select(
                self.model.aliveConsumers.getIdentity() == id
            )
            worker.receiveFiring()
            self.workersList.remove(id)

    def setLockDown(self):
        self.lockdown = True
        self.lockdownList.append(self.model.today)

    def unsetLockDown(self):
        self.lockdown = False

    def resetLockDown(self):
        self.lockdownList = []

    def getOwnerIncome(self):
        return self.ownerIncome

    def progressPayback(self, eps=1e-8):
        if len(self.loanContractRemainingTime) > 0:
            self.payback = (
                self.iL
                * np.sum([self.loanList])
                / (
                    1
                    - (1 + self.iL)
                    ** (list(self.loanContractRemainingTime.values())[0])
                )
            )
        else:
            self.payback = 0

        if self.p.verboseFlag:
            print("payback value", self.payback)
        brown_firm_coefficient = (
            self.brown_firm * self.p.climateZetaBrown * self.p.co2_price
        )
        carbon_tax = (
            brown_firm_coefficient
            * self.carbon_tax_state
            * self.get_actual_production()
        )
        self.setPrice(
            self.getPrice() + np.sum(carbon_tax / (self.get_actual_production()))
        )
        self.payLoan()

        ## Update other financial variables
        self.DTE = sum(self.loanList) / (self.netWorth + eps)
        self.iF = np.max([0, self.DTE / 100])
        # print("default probability factor", self.DTE)
        if self.DTE < 0:
            self.defaultProb = 1
        else:
            self.defaultProb = 1 - np.exp(-self.p.defaultProbAlpha * self.DTE)
        self.iL = np.max([0, self.p.bankICB * (1 + self.defaultProb)])
        # print("default Prob: ", self.defaultProb, " ", self.DTE)

    def reset_non_loan(self):
        self.non_loan = 0
