import numpy as np
import numpy.random as random
from collections import OrderedDict
import agentpy as ap
import copy
import pandas as pd


class Bank(ap.Agent):
    """A bank agent"""

    def setup(self):
        self.loans = 0
        self.numberOfUnemployed = 0
        self.numberOfEmployed = 0
        self.bankDataWriter = []
        self.iD = 0.0001
        self.iCB = self.p.bankICB
        self.profit = 0
        self.actualSuppliedLoan = 0
        self.totalLoanSupply = 0
        self.totalLoanDemands = 0
        self.deposits = 0
        self.equities = 0
        self.DTE = 0
        self.equity = 0
        self.NPL = 0
        self.gamma = self.p.gamma
        self.reserve = self.p.bankResInit

    def agentAssign(self):
        # short out agents without loan_demand > 0
        # updateConsumerList = self.model.consumer_agents.select(self.model.consumer_agents.newCreditAsked > 0)
        updateCSFList = self.model.csfirm_agents.select(
            self.model.csfirm_agents.loan_demand > 0
        )
        updateCPList = self.model.cpfirm_agents.select(
            self.model.cpfirm_agents.loan_demand > 0
        )

        self.orderedAgentsInterestsRaw = np.argsort(
            np.concatenate(
                [
                    updateCSFList.defaultProb,
                    updateCPList.defaultProb,
                    self.model.greenEFirm.defaultProb,
                    self.model.brownEFirm.defaultProb,
                ]
            )
        )
        self.orderedAgentsInterests = np.concatenate(
            [
                updateCSFList.id,
                updateCPList.id,
                self.model.greenEFirm.id,
                self.model.brownEFirm.id,
            ]
        )[self.orderedAgentsInterestsRaw]

    def _calculate_consumer_networth(self, agent):
        """
        This internal function of the Bank class is used to represent the demands
        between consumer agents and the bank

        ---
        Args:
            agent: The target consumer agent
        ---
        Returns:
        """

        if agent.getCovidStateAttr("state") != "dead":
            self.deposits += np.sum(agent.wealthList[-1])
            # self.loans += agent.obtainedCreditList[-1]
            self.profit += -np.sum(self.p.bankID * agent.get_deposit())

    def _calculate_firm_networth(self, agent):
        """
        This internal function of the Bank class is used to represent the demands
        between firm agents and the bank

        ---
        Args:
            agent: The target firm agent
        ---
        Returns:
        """

        self.totalLoanDemands += np.sum(agent.loan_demand)
        self.profit += agent.iL * np.sum(agent.loanList)
        self.deposits += np.sum(agent.depositList[-1])
        self.loans += np.sum(agent.loanList)
        self.totalBankruptFraction += np.sum(agent.defaultProb * np.sum(agent.loanList))

    def _calculate_running_loan(self, agent_id):
        """
        This internal function of the Bank class is used to represent the demands
        between agents and the bank

        ---
        Args:
            agent_id: The target agent id
        ---
        Returns:
        """
        # print("bank start")
        agent = self.agentList.select(self.agentList.getIdentity() == agent_id)
        bankruptFraction = agent.defaultProb * np.sum(agent.loanList[0])

        L_CAR = 0
        # print("loan supply", self.totalLoanSupply)
        if (
            bankruptFraction <= self.totalLoanSupply
            and self.runningLoan <= self.totalLoanSupply
        ):
            # print("bank state 2")
            L_CAR = np.sum([agent.loan_demand])
        agent.adjustAccordingToBankState(L_CAR)
        self.runningLoan += L_CAR

    def sommaW(self, eps=1e-8):
        """
        This internal function of the Bank class is used to propagate the main functions of the bank
        """

        # Demands and Transactions
        # [self._calculate_wealth(agent) for agent in self.model.consumer_agents]
        [
            self._calculate_consumer_networth(agent)
            for agent in self.model.aliveConsumers
        ]
        [self._calculate_firm_networth(agent) for agent in self.model.cpfirm_agents]
        self._calculate_firm_networth(self.model.greenEFirm[0])
        self._calculate_firm_networth(self.model.brownEFirm[0])

        # Calculate Bank statistics

        self.equities = self.reserve + self.loans - self.deposits
        self.equity = self.profit + self.equities
        # print("bank deposit", self.deposits, self.profit)
        self.totalLoanSupply = (
            1 - self.gamma
        ) * self.equity - self.totalBankruptFraction
        # self.totalLoanSupply = self.gamma * self.equity - self.totalBankruptFraction
        # print("bank statistic", " non-reserve equity", self.equity, " bankrupt fraction", self.totalBankruptFraction)
        self.DTE = self.deposits / (self.equity + eps)
        self.agentAssign()
        self.runningLoan = 0
        list(map(self._calculate_running_loan, self.orderedAgentsInterests))
        # print("current loan", self.runningLoan)
        self.actualSuppliedLoan += np.sum(self.runningLoan)

    def reset_bank(self):

        # Reset temporary variables
        self.agentList = (
            self.model.csfirm_agents
            + self.model.cpfirm_agents
            + self.model.greenEFirm
            + self.model.brownEFirm
        )
        self.numberOfUnemployed = sum(
            np.array(self.model.aliveConsumers.getEmploymentState() == 0)
            * np.array(
                (
                    self.model.aliveConsumers.consumerType == "workers"
                    and self.model.aliveConsumers.getCovidStateAttr("state") != "dead"
                )
            )
        )
        self.numberOfEmployed = sum(
            np.array(self.model.aliveConsumers.getEmploymentState() == 1)
            * np.array(
                (
                    self.model.aliveConsumers.consumerType == "workers"
                    and self.model.aliveConsumers.getCovidStateAttr("state") != "dead"
                )
            )
        )
        self.profit = 0
        self.totalLoanDemands = 0
        self.equities = 0
        self.actualSuppliedLoan = 0
        self.totalBankruptFraction = 0
        self.deposits = 0
        self.loans = 0
        self.NPL = 0
