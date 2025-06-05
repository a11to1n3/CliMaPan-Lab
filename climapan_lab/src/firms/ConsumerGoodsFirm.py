import numpy as np
import copy
import agentpy as ap
import numpy.random as random
from collections import OrderedDict
from .GoodsFirmBase import GoodsFirmBase
from ..utils import days_in_month
from scipy.optimize import minimize

class ConsumerGoodsFirm(GoodsFirmBase):

    """ A ConsumerGoodsFirm agent """
    def setup(self):
        super().setup()

        # Main variables
        self.wages = {}
        self.price = 0
        self.capital = 10000
        self.labour = 0
        self.equity = 0

        #parameter
        self.beta_capital = self.p.beta_capital
        self.beta_labour = self.p.beta_labour
        self.beta_energy = self.p.beta_energy
        self.eta_production = self.p.ETA_PRODUCTION
        self.rho_labour = self.p.rho_labour
        self.rho_energy = self.p.rho_energy
        self.capital_growth_rate = self.p.capital_growth_rate
        self.mark_up = self.p.mark_up_factor
        self.mark_up_adjustment = self.p.mark_up_adjustment
        self.mark_up_alpha = self.p.mark_up_alpha
        self.mark_up_beta = self.p.mark_up_beta
        self.carbon_tax_state = self.p.settings.find("CT") != -1
        self.div_ratio = self.p.ownerProportionFromProfits
        self.capital_depreciation = self.p.depreciationRate
        self.forecast_discount_factor = self.p.forecast_discount_factor

        #transitory variables
        self.actual_production = 0
        self.planned_production = 1100
        self.utilization = 0
        self.labour_demand = 0
        self.aggregate_demand = 0
        self.energy = 0
        self.brown_firm = self.useEnergy == 'brown'
        self.capital_investment = 0 #value variable
        self.capital_increase = 616 #physical variable
        self.capital_price = 0
        self.capital_value = self.capital * self.capital_price #value variable
        self.cost_of_capital = 0 #value variable
        self.capital_purchase = 0 #physical vaariable
        self.capital_demand = self.capital * (self.capital_growth_rate + self.capital_depreciation) #physical variable
        self.average_production_cost = 0
        self.market_share = 1/self.p.csf_agents
        self.market_shareList = []

    def prepareForecast(self):
        ''''''
        '''if self.model.t > 31:
            print("total sale", self.model.total_good)
            self.market_share = self.getSoldProducts() / self.model.total_good

        self.market_shareList.append(self.market_share)'''
        self.set_aggregate_demand(0)
        self.soldProducts = 0
        self.consumersList = self.model.aliveConsumers.select(self.model.aliveConsumers.getCovidStateAttr('state') != 'dead' and self.model.aliveConsumers.getAgeGroup() == 'working')
        #market share
  

    def calculate_input_demand(self):
        ''''''
        beta = self.forecast_discount_factor
        #This function is used to calculate all inputs and related demands
        self.old_demand = self.get_aggregate_demand()
        self.planned_production = (beta* self.sale_record + (1 - beta) * self.get_aggregate_demand())
        self.utilization = self.sale_record / self.old_demand
        self.labour_demand = 0.8 * self.model.num_worker / self.p.csf_agents
        self.energy = self.optimize_energy(self.labour_demand, self.capital)
        self.capital_demand = self.get_capital() * (self.capital_growth_rate + self.capital_depreciation)
        #print("good firm capital demand", self.capital_demand, self.capital, self.capital* (1 - self.capital_depreciation) +self.capital_demand)

    def produce(self):
        #This function is to calculate the actual production value based on the inputs of current period
        #Check production function in GoodsFirmBase 

        aggSickLeaves = np.sum([len(aConsumer.getSickLeaves()) for aConsumer in self.consumersList if aConsumer.getBelongToFirm() == self.id])
        if self.p.verboseFlag:
            print("sick leave", aggSickLeaves)
        sick_ratio = np.min([1, np.max([0, aggSickLeaves / (30 * len(self.workersList))])])
        if self.p.verboseFlag:
            print("sick ratio", sick_ratio)

        labour_input = self.labour_demand
        capital_input = self.get_capital()
        energy_input = self.get_energy()
        #print("input", labour_input, capital_input, energy_input)
        #print("energy type", self.useEnergy)


        production_value = self.production_function((capital_input, labour_input, energy_input)) * (1 - sick_ratio)
        #print("production value", production_value, self.planned_production)
        self.set_actual_production(production_value)

    def price_setting(self):
        '''Function to set price base on mark up over cost'''

        ## calculate cost
        self.calculate_average_production_cost()

        ## set price
        energy_price = self.model.brownEFirm[-1].getPrice() if self.brown_firm else self.model.greenEFirm[-1].getPrice()
        self.price = self.get_average_production_cost() * (1 + self.mark_up * (self.mark_up_alpha + self.mark_up_beta * self.utilization))
        #print("price ", self.price, self.id, self.getUseEnergy(), energy_price, " utilization: ", self.utilization, self.profits)
        self.priceList.append(np.sum([self.getPrice()]))

    def compute_net_profit(self, eps=1e-8):
        #function to calculate profit
        # Wage component
        if self.wage_bill > 0:
            self.unitWageBill = self.wage_bill / (self.getNumberOfLabours())
        else:
            self.unitWageBill = 0 ##if firm demand 0 labour it means it shut down?
        
        self.countWorkers = self.getNumberOfLabours()

        if self.p.verboseFlag:
            print(f"Number of workers in Capital Goods Firm no. {self.id - self.p.c_agents - self.p.csf_agents - 1 - 1} is {self.countWorkers}")

        #determint loan payback
        self.progressPayback()

        #printint firm report
        if self.p.verboseFlag:
            print()
            print("Activity Report for firm", self.id, ":")
            print("........................................")

        #Calculating Profit
        if self.p.verboseFlag:
            print("loan payback", self.payback, self.deposit, self.get_average_production_cost() * self.get_actual_production())

        self.profits = self.p.bankID * self.deposit + self.getSoldProducts()*self.getPrice() - self.get_average_production_cost() * self.get_actual_production() + self.payback # - self.inn
        self.profit_margin = (self.getSoldProducts()*self.getPrice() - self.get_average_production_cost() * self.get_actual_production()) / (self.getSoldProducts()*self.getPrice())
        #Net Profit after Tax
        self.updateProfitsAfterTax(isC02Taxed=self.carbon_tax_state*self.brown_firm)
        #pay income to firm owner
        self.ownerIncome = np.max([0, self.net_profit * self.div_ratio])
        if self.p.verboseFlag:
            print("deposit before", self.deposit)
        self.updateDeposit(self.net_profit-self.ownerIncome)
        if self.p.verboseFlag:
            print("deposit after", self.deposit)
            print("networth", self.netWorth)
            print("production and sale", self.actual_production, self.sale_record)
            print("profit", self.profits, self.net_profit)
            print("owner income", self.ownerIncome, "deposit", self.deposit, "total cost", self.get_average_production_cost() * self.get_actual_production())
            print("DTE", self.DTE)
            print("loan list", sum(self.loanList), self.loanList, "loan demand", self.loan_demand, "loan granted", self.loanObtained)

    def update_capital_growth(self):
        self.capital_growth = self.capital_purchase
        #print("consumer capital growth", self.capital_growth)
        #for consumer firm, capital growth is what they purchase

