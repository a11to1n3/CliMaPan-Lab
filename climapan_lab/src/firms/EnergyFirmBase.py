import numpy as np
import copy
import numpy.random as random
import agentpy as ap
from collections import OrderedDict


class EnergyFirmBase(ap.Agent):

    """ A EnergyFirmBase agent """

    def setup(self):
        # Main Variables
        self.capital= 0
        self.deposit = 20000
        self.net_profit = 0
        self.useEnergy = "brown"

        #parameters
        self.iL = self.p.bankICB
        self.capital_growth_rate = self.p.capital_growth_rate
        self.capital_depreciation = self.p.depreciationRate
        self.base_price = 0
        self.energy_price_growth = 0
        self.div_ratio = self.p.energyOwnerProportionFromProfits

        # Transitory variables
        self.capital_tracking = []
        self.actual_production = 1000
        self.average_production_cost = 0

        self.loanList = [0, 0]
        self.loanContractRemainingTime = {}
        self.loanObtained = 0
        self.loan_demand = 0
        self.DTE = 0
        self.iF = 0

        self.depositList = [0, 0]
        self.sale_record = 0
        self.profits = 0
        self.ownerIncome = 0
        self.netWorth = 0

        self.countConsumers = 0
        self.tax = 0       
        self.carbonTax = 0
        self.energy_demand = 0 #equivalent to aggregate_demand for other firms

        self.carbon_tax_state = self.p.settings.find("CT") != -1
        self.brown_firm = self.useEnergy == 'brown'

        self.capital_investment = 0 #value variable
        self.capital_increase = 0 #physical variable
        self.capital_price = 1
        self.capital_value = self.capital * self.capital_price #value variable
        self.cost_of_capital = 0 #value variable
        self.capital_purchase = 0 #physical vaariable
        self.capital_demand = 0 #physical variable

    def calculate_input_demand(self):
        self.capital_demand = self.get_capital() * (self.capital_growth_rate + self.capital_depreciation)

    def production_budgeting(self):
        ''''''
        #checking if production can be financed, otherwise taking loan if possible
        #self.loan_demand = np.max([self.get_average_production_cost() * self.get_actual_production() - self.deposit, 0])
        self.loan_demand = np.max([self.get_average_production_cost() * self.get_actual_production() - self.deposit, 0])
        if self.loan_demand > 0:
            self.loanList.append(self.get_average_production_cost() * self.get_actual_production() - self.deposit)
        else:
            self.loanList.append(0)

    def produce(self):
        # Energy firm should fully satisfy consumption
        self.set_actual_production(5 + self.get_energy_demand())

    def calculate_average_production_cost(self):
        ## Capital Component
        #Need to default value of past periods to 0
        if len(self.capital_tracking) > self.p.capital_length:
            self.capital_tracking.pop(0)
        self.capital_tracking.append(np.sum(self.capital_investment))
        
        cost_of_capital = np.sum(self.capital_tracking) / self.p.capital_length
        ##Need to also store the price of capital together with the period so we can do multiplication
        self.average_production_cost = (cost_of_capital) / (self.get_actual_production())

    def price_setting(self):
        # Assuming fixed price
        self.price = self.price * (1 + self.energy_price_growth)

    def compute_net_profit(self, eps=1e-8):
        #function to calculate profit

        #determint loan payback
        self.progressPayback()

        #Calculating Profit
        self.profits = self.p.bankID * self.deposit + self.get_actual_production() * (self.getPrice() - self.get_average_production_cost()) + self.payback # - self.inn

        #Net Profit after Tax
        self.updateProfitsAfterTax(isC02Taxed=self.carbon_tax_state*self.brown_firm)
        self.updateDeposit(self.net_profit)
        
        #pay income to firm owner
        self.ownerIncome = np.max([0, self.net_profit * self.div_ratio])
        self.updateDeposit(-self.ownerIncome)

    def payLoan(self):
        if - self.payback > 0:
            payback = copy.copy(self.payback)
            for loan_id in [i for i in range(len(self.loanList)) if self.loanList[i] > 0]:
                if payback == 0:
                    break
                if - payback <= self.loanList[loan_id]:
                    self.loanList[loan_id] += np.sum(payback)
                    payback = 0
                else:
                    self.loanList[loan_id] = 0
                    payback += np.sum(self.loanList[loan_id])
                if self.loanList[loan_id] > 0 and self.loanContractRemainingTime[loan_id] <= 0:
                    self.bankrupt = True
                elif self.loanList[loan_id] > 0:
                    self.loanContractRemainingTime[loan_id] -= 1
                else:
                    self.loanContractRemainingTime.pop(loan_id)
        else:
            for loan_id in [i for i in range(len(self.loanList)) if self.loanList[i] > 0]:
                if self.loanList[loan_id] > 0 and self.loanContractRemainingTime[loan_id] <= 0:
                    self.bankrupt = True
                elif self.loanList[loan_id] > 0:
                    self.loanContractRemainingTime[loan_id] -= 1
                else:
                    self.loanContractRemainingTime.pop(loan_id)

    def updateProfitsAfterTax(self, isC02Taxed=False):
        carbonTax = copy.copy(self.carbonTax) if isC02Taxed else 0
        if self.profits > 0:
            self.net_profit = (1-self.p.taxRate)*self.profits - carbonTax
            self.setTax(self.p.taxRate*self.profits + carbonTax)
        else:
            self.net_profit = 1 * self.profits - carbonTax
            self.setTax(carbonTax)

    def adjustAccordingToBankState(self, obtainedCredit, eps=1e-8):
        '''Check bank _calculate_running_loan for the function'''

        ## Credit obtained via bank
        if obtainedCredit > 0 and len(self.loanContractRemainingTime) == 0:
            self.loanObtained = obtainedCredit
            self.loanList.append((np.sum([self.getLoan()])))

            if self.useEnergy == "green":
                self.loanContractRemainingTime[len(self.loanList) - 1] = self.p.greenLoanRepayPeriod
            else:
                self.loanContractRemainingTime[len(self.loanList) - 1] = self.p.brownLoanRepayPeriod
            
        ## Adjust deposit and networth
        self.updateDeposit(np.sum(obtainedCredit)) #updateDeposit with loan
        #print("update deposit", np.sum(obtainedCredit) + self.net_profit, np.sum(obtainedCredit))
        self.depositList[-1] = self.deposit
        self.netWorth = self.depositList[-1] - sum(self.loanList)

        ## Update other financial varaibles
        self.DTE = sum(self.loanList) / ((self.deposit + self.get_capital() * self.capital_price) - sum(self.loanList))
        self.iF = np.max([0,self.DTE/100])
        if self.DTE < 0:
            self.defaultProb = 1
        else:
            self.defaultProb = 1 - np.exp(-self.p.defaultProbAlpha * self.DTE)
        self.iL = np.max([0,self.p.bankICB * (1 + self.defaultProb)])

    def update_capital_value(self):
        ''''''
        # depreciation update
        self.set_capital(self.get_capital() * (1 - self.capital_depreciation))

        # reflect the purchase of new capital
        self.update_capital_increase(self.capital_growth)
        self.set_capital(self.get_capital() + self.get_capital_increase())

        # new value of capital
        self.capital_value = self.get_capital() * self.capital_price

    
    def get_actual_production(self):
        return self.actual_production

    def get_average_production_cost(self):
        return self.average_production_cost    

    def getPrice(self):
        return self.price
    
    def getNetProfit(self):
        return self.net_profit

    def update_capital_increase(self, value):
        self.capital_increase = np.max([0, value])

    def set_capital(self, capital):
        self.capital = capital

    def get_capital(self):
        return self.capital

    def get_capital_increase(self):
        return self.capital_increase
    
    def get_capital_demand(self):
        return self.capital_demand
    
    def set_capital_price(self, value):
        # firm will get this info when doing transaction, capital firm know their price
        self.capital_price = value
    
    def getIdentity(self):
        return self.id

    def getLoan(self):
        return self.loanObtained
    
    def getPrice(self):
        return self.price
    
    def setPrice(self, price):
        self.price = price
    
    def getOwnerIncome(self):
        return self.ownerIncome
    
    def getDeposit(self):
        return self.deposit
    
    def setDeposit(self, deposit):
        self.deposit = deposit

    def set_sale_record(self, sale):
        self.sale_record = sale

    def update_sale_record(self,value):
        self.sale_record += value
    
    def getNetWorth(self):
        return self.netWorth
    
    def getTax(self):
        return self.tax
    
    def setTax(self, tax):
        self.tax = tax

    def updateTax(self, value):
        self.tax += value
    
    def getUseEnergy(self):
        return self.useEnergy
    
    def getSoldProducts(self):
        return self.get_actual_production()

    def set_actual_production(self, actual_production):
        self.actual_production = actual_production

    def get_actual_production(self):
        return self.actual_production

    def set_capital_investment(self, capital_investment):
        self.capital_investment = capital_investment

    def get_capital_investment(self):
        return self.capital_investment

    def set_energy_demand(self, energy_demand):
        self.energy_demand = energy_demand

    def get_energy_demand(self):
        return self.energy_demand
    
    def updateDeposit(self, value):
        if value > 0:
            self.deposit += value
    
    def append2DepositList(self, deposit):
        self.depositList.append(deposit)

    def progressPayback(self):
        if len(self.loanContractRemainingTime) > 0:
            self.payback = self.iL * np.sum([self.loanList]) / (1 - (1 + self.iL)**(list(self.loanContractRemainingTime.values())[0]))
        else:
            self.payback = 0
        #print(0", self.payback)
        brown_firm_coefficient = self.brown_firm * self.p.climateZetaBrown * self.p.co2_price
        carbon_tax = brown_firm_coefficient * self.carbon_tax_state * self.get_actual_production()
        #print("energy production ", self.get_actual_production())
        self.setPrice(self.getPrice() + np.sum(carbon_tax / (self.get_actual_production())))
        self.payLoan()

        ## Update other financial variables
        self.DTE = sum(self.loanList) / ((self.deposit + self.get_capital() * self.capital_price) - sum(self.loanList))
        self.iF = np.max([0,self.DTE/100])
        if self.DTE < 0:
            self.defaultProb = 1
        else:
            self.defaultProb = 1 - np.exp(-self.p.defaultProbAlpha * self.DTE)
        self.iL = np.max([0,self.p.bankICB * (1 + self.defaultProb)])

    def update_capital_growth(self):
        self.capital_growth = self.capital_purchase