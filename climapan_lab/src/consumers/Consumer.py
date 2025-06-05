import copy
import math

import agentpy as ap
import numpy as np
import numpy.random as random

from ..utils import lognormal


class Consumer(ap.Agent):
    """A consumer agent"""

    def setup(self):

        # parameter
        self.consumptionSubsistenceLevel = (
            self.p.subsistenceLevelOfConsumption
        )  # physical good
        self.worker_additional_consumption = self.p.worker_additional_consumption
        self.owner_additional_consumption = self.p.owner_additional_consumption
        self.iD = self.p.bankID
        self.consumption_growth = self.p.consumption_growth
        self.employed = False
        self.reset()
        self.covidState = {
            "state": None,
            "t": None,
            "duration": None,
            "nextState": None,
        }

        self.deposit = 1500  # total wealth
        self.growth_factor = 1
        self.consumerType = None  # 4 (5) options after setup: workers, capitalists, green_energy_owners, brown_energy_owners, (None)

        # what else do I need

    # reborn inherit
    def reset(self):
        self.owner = False
        self.memoryLengthForUnemplymentRate = 5
        self.memoryLengthForEmplymentState = 10
        self.wage = self.p.minimumWage  # wage from firm
        self.income = 0  # income from all source
        self.div = 0  # capital income
        self.wealthList = [0]
        self.desired_consumption = self.consumptionSubsistenceLevel  # physical good
        self.consumption = 0  # value variable
        self.employmentStateStorage = [1]
        self.unemploymentRateStorage = [0]
        self.employed = False
        self.belongToFirm = None
        self.dead = False
        self.sickLeaves = []
        self.price = 0

    def desired_C(self):
        sick_reduction = self.p.sick_reduction
        sick = self.model.covidState
        base_consumption = self.consumptionSubsistenceLevel + np.min(
            [
                self.employed * self.worker_additional_consumption
                + self.owner * self.owner_additional_consumption,
                0.8 * self.deposit / self.price,
            ]
        )

        self.growth_factor *= 1 + self.consumption_growth
        self.desired_consumption = (
            self.growth_factor * base_consumption - sick_reduction * sick
        )
        # if sick == True:
        # print("sick reduction", sick, sick_reduction)

    def update_wealth(self):
        self.income = (
            self.deposit * self.iD
            + self.isWorker() * self.getWage()
            + self.owner * (self.p.minimumWage + self.getDiv())
        )
        # if self.owner: print("owner income", self.income)
        self.deposit += (
            self.income - self.consumption
        )  # consumption is value variable, updated in transaction
        self.wealthList.append(self.deposit)

    def receiveHiring(self, firmID):
        if self.getConsumerType() == "workers":
            self.setEmployment(True)
            self.setWage(self.p.minimumWage)
            self.belongToFirm = firmID
            self.updateMemoryAfterHiringFiring()

    def receiveFiring(self):
        if self.getConsumerType() == "workers":
            self.setEmployment(False)
            self.setWage()
            self.belongToFirm = None
            self.updateMemoryAfterHiringFiring()

    def updateMemoryAfterHiringFiring(self):
        if self.employed:
            self.employmentStateStorage.append(1.0)
        else:
            self.employmentStateStorage.append(0.0)

        if len(self.employmentStateStorage) > self.memoryLengthForEmplymentState:
            self.employmentStateStorage.pop(0)

    def updateMemory(self, unemplRate):
        self.unemploymentRateStorage.append(unemplRate)
        if len(self.unemploymentRateStorage) > self.memoryLengthForUnemplymentRate:
            self.unemploymentRateStorage.pop(0)

    # use to set level of consumption
    def setConsumption(self, value):
        self.consumption = value

    # use to retrieve level of consumption
    def getConsumption(self):
        return self.consumption

    def get_desired_consumption(self):
        return self.desired_consumption

    # use to adjust level of wealth
    def update_deposit(self, amount):
        self.deposit += amount

    # use to set level of wealth
    def set_deposit(self, deposit):
        self.deposit = deposit

    def wealth_loss(self, loss_percentage):
        self.deposit *= 1 - loss_percentage

    # use to retrieve level of wealth
    def get_deposit(self):
        return self.deposit

    def getEmploymentState(self):
        return self.employed and self.consumerType == "workers"

    def getUnemploymentState(self):
        return not self.employed and self.consumerType == "workers"

    def setEmployment(self, value):
        self.employed = value

    def isWorker(self):
        return self.consumerType == "workers"

    def getSumEmploymentState(self):
        return self.sumEmploymentState

    def getIdentity(self):
        return self.id

    def getFinancialDifficultyIndicator(self):
        return self.financialDifficultyIndicator

    def setWage(self, wage=None):
        if self.employed:
            if self.model.t < 32:
                self.wage = self.p.minimumWage * (1 + self.unemploymentRateStorage[-1])
            else:
                if wage > self.p.unemploymentDole:
                    self.wage = wage
                else:
                    self.wage = self.p.unemploymentDole
        else:
            self.wage = self.p.unemploymentDole

    def getIncome(self):
        return self.income

    def getWage(self):
        return self.wage

    def setConsumerType(self, consumerType):
        self.consumerType = consumerType

    def getConsumerType(self):
        return self.consumerType

    def getBelongToFirm(self):
        return self.belongToFirm

    def setDiv(self, div):
        if self.owner:
            self.div = div

    def getDiv(self):
        return self.div

    def gov_transfer(self, value):
        self.deposit += value

    def setAgeGroup(self, ageGroup):
        self.ageGroup = ageGroup

    def getAgeGroup(self):
        return self.ageGroup

    def setCovidState(self, state=None, time=None, duration=None, nextState=None):
        if state is not None and time is not None:
            self.covidState["state"] = state
            self.covidState["t"] = time
            self.covidState["duration"] = duration
            self.covidState["nextState"] = nextState
        elif state == "susceptible":
            self.covidState = {
                "state": "susceptible",
                "t": None,
                "duration": None,
                "nextState": None,
            }
        else:
            self.covidState = {
                "state": None,
                "t": None,
                "duration": None,
                "nextState": None,
            }

    def getCovidState(self):
        return self.covidState

    def getCovidStateAttr(self, attr):
        if attr in list(self.covidState.keys()):
            return self.covidState[attr]
        else:
            raise SyntaxError(
                "No such attribute. Please select from: state, t, duration, nextState"
            )

    def propagateContact(self, inf_f, inf_c, p_firm, p_community):
        if inf_f > 0 or inf_c > 0:
            p_infection = 1 - ((1 - p_firm) ** inf_f) * ((1 - p_community) ** inf_c)
            if np.random.rand() <= p_infection:
                self.setCovidState(
                    "exposed",
                    self.model.t,
                    lognormal(
                        self.p.T_susceptible_mild_mean, self.p.T_susceptible_mild_std
                    ),
                    "mild",
                )

    def _progressCovidExposedState(self):
        self.setSickLeaves(str(self.model.today))
        if self.getCovidStateAttr("duration") is None:
            if self.getAgeGroup() == "young":
                if np.random.rand() < self.p.p_exposed_mild_young:
                    self.setCovidState(
                        "exposed",
                        self.getCovidStateAttr("t"),
                        lognormal(
                            self.p.T_exposed_mild_mean, self.p.T_exposed_mild_std
                        ),
                        "mild",
                    )

                else:
                    self.setCovidState(
                        "infected non-sympotomatic",
                        self.getCovidStateAttr("t"),
                        lognormal(
                            self.p.T_nonsym_recovered_mean,
                            self.p.T_nonsym_recovered_std,
                        ),
                        "recovered",
                    )
            elif self.getAgeGroup() == "working":
                if np.random.rand() < self.p.p_exposed_mild_working:
                    self.setCovidState(
                        "exposed",
                        self.getCovidStateAttr("t"),
                        lognormal(
                            self.p.T_exposed_mild_mean, self.p.T_exposed_mild_std
                        ),
                        "mild",
                    )

                else:
                    self.setCovidState(
                        "infected non-sympotomatic",
                        self.getCovidStateAttr("t"),
                        lognormal(
                            self.p.T_nonsym_recovered_mean,
                            self.p.T_nonsym_recovered_std,
                        ),
                        "recovered",
                    )
            elif self.getAgeGroup() == "elderly":
                if np.random.rand() < self.p.p_exposed_mild_elderly:
                    self.setCovidState(
                        "exposed",
                        self.getCovidStateAttr("t"),
                        lognormal(
                            self.p.T_exposed_mild_mean, self.p.T_exposed_mild_std
                        ),
                        "mild",
                    )

                else:
                    self.setCovidState(
                        "infected non-sympotomatic",
                        self.getCovidStateAttr("t"),
                        lognormal(
                            self.p.T_nonsym_recovered_mean,
                            self.p.T_nonsym_recovered_std,
                        ),
                        "recovered",
                    )
        else:
            if self.model.t >= self.getCovidStateAttr("t") + self.getCovidStateAttr(
                "duration"
            ):
                self.setCovidState(self.getCovidStateAttr("nextState"), self.model.t)

    def _progressCovidInfectedNonsympotomaticState(self):
        self.setSickLeaves(str(self.model.today))
        if self.model.t >= self.getCovidStateAttr("t") + self.getCovidStateAttr(
            "duration"
        ):
            self.setCovidState(self.getCovidStateAttr("nextState"), self.model.t)

    def _progressCovidMildState(self):
        self.setSickLeaves(str(self.model.today))
        if self.getCovidStateAttr("duration") is None:
            if self.getAgeGroup() == "young":
                if np.random.rand() < self.p.p_mild_severe_young * (
                    (1 - self.p.p_vax) ** int(self.p.covid_settings == "VAX")
                ):
                    self.setCovidState(
                        "mild",
                        self.model.t,
                        lognormal(self.p.T_mild_severe_mean, self.p.T_mild_severe_std),
                        "severe",
                    )
                else:
                    self.setCovidState(
                        "infected non-sympotomatic",
                        self.model.t,
                        lognormal(
                            self.p.T_mild_recovered_mean, self.p.T_mild_recovered_std
                        ),
                        "recovered",
                    )
            elif self.getAgeGroup() == "working":
                if np.random.rand() < self.p.p_mild_severe_working * (
                    (1 - self.p.p_vax) ** int(self.p.covid_settings == "VAX")
                ):
                    self.setCovidState(
                        "mild",
                        self.model.t,
                        lognormal(self.p.T_mild_severe_mean, self.p.T_mild_severe_std),
                        "severe",
                    )
                else:
                    self.setCovidState(
                        "infected non-sympotomatic",
                        self.model.t,
                        lognormal(
                            self.p.T_mild_recovered_mean, self.p.T_mild_recovered_std
                        ),
                        "recovered",
                    )
            elif self.getAgeGroup() == "elderly":
                if np.random.rand() < self.p.p_mild_severe_elderly * (
                    (1 - self.p.p_vax) ** int(self.p.covid_settings == "VAX")
                ):
                    self.setCovidState(
                        "mild",
                        self.model.t,
                        lognormal(self.p.T_mild_severe_mean, self.p.T_mild_severe_std),
                        "severe",
                    )
                else:
                    self.setCovidState(
                        "infected non-sympotomatic",
                        self.model.t,
                        lognormal(
                            self.p.T_mild_recovered_mean, self.p.T_mild_recovered_std
                        ),
                        "recovered",
                    )
        else:
            if self.model.t >= self.getCovidStateAttr("t") + self.getCovidStateAttr(
                "duration"
            ):
                self.setCovidState(self.getCovidStateAttr("nextState"), self.model.t)

    def _progressCovidSevereState(self):
        self.setSickLeaves(str(self.model.today))
        if self.getCovidStateAttr("duration") is None:
            if self.getAgeGroup() == "young":
                if np.random.rand() < self.p.p_severe_critical_young:
                    self.setCovidState(
                        "severe",
                        self.model.t,
                        lognormal(
                            self.p.T_severe_critical_mean, self.p.T_severe_critical_std
                        ),
                        "critical",
                    )
                else:
                    self.setCovidState(
                        "severe",
                        self.model.t,
                        lognormal(
                            self.p.T_severe_recovered_mean,
                            self.p.T_severe_recovered_std,
                        ),
                        "recovered",
                    )
            elif self.getAgeGroup() == "working":
                if np.random.rand() < self.p.p_severe_critical_working:
                    self.setCovidState(
                        "severe",
                        self.model.t,
                        lognormal(
                            self.p.T_severe_critical_mean, self.p.T_severe_critical_std
                        ),
                        "critical",
                    )
                else:
                    self.setCovidState(
                        "severe",
                        self.model.t,
                        lognormal(
                            self.p.T_severe_recovered_mean,
                            self.p.T_severe_recovered_std,
                        ),
                        "recovered",
                    )
            elif self.getAgeGroup() == "elderly":
                if np.random.rand() < self.p.p_severe_critical_elderly:
                    self.setCovidState(
                        "severe",
                        self.model.t,
                        lognormal(
                            self.p.T_severe_critical_mean, self.p.T_severe_critical_std
                        ),
                        "critical",
                    )
                else:
                    self.setCovidState(
                        "severe",
                        self.model.t,
                        lognormal(
                            self.p.T_severe_recovered_mean,
                            self.p.T_severe_recovered_std,
                        ),
                        "recovered",
                    )
        else:
            if self.model.t >= self.getCovidStateAttr("t") + self.getCovidStateAttr(
                "duration"
            ):
                self.setCovidState(self.getCovidStateAttr("nextState"), self.model.t)

    def _progressCovidCriticalState(self):
        self.setSickLeaves(str(self.model.today))
        if self.getCovidStateAttr("duration") is None:
            if self.getAgeGroup() == "young":
                if np.random.rand() < self.p.p_critical_death_young:
                    self.setCovidState(
                        "critical",
                        self.model.t,
                        lognormal(
                            self.p.T_critical_death_mean, self.p.T_critical_death_std
                        ),
                        "dead",
                    )
                else:
                    self.setCovidState(
                        "critical",
                        self.model.t,
                        lognormal(
                            self.p.T_critical_recovered_mean,
                            self.p.T_critical_recovered_std,
                        ),
                        "recovered",
                    )
            elif self.getAgeGroup() == "working":
                if np.random.rand() < self.p.p_critical_death_working:
                    self.setCovidState(
                        "critical",
                        self.model.t,
                        lognormal(
                            self.p.T_critical_death_mean, self.p.T_critical_death_std
                        ),
                        "dead",
                    )
                else:
                    self.setCovidState(
                        "critical",
                        self.model.t,
                        lognormal(
                            self.p.T_critical_recovered_mean,
                            self.p.T_critical_recovered_std,
                        ),
                        "recovered",
                    )
            elif self.getAgeGroup() == "elderly":
                if np.random.rand() < self.p.p_critical_death_elderly:
                    self.setCovidState(
                        "critical",
                        self.model.t,
                        lognormal(
                            self.p.T_critical_death_mean, self.p.T_critical_death_std
                        ),
                        "dead",
                    )
                else:
                    self.setCovidState(
                        "critical",
                        self.model.t,
                        lognormal(
                            self.p.T_critical_recovered_mean,
                            self.p.T_critical_recovered_std,
                        ),
                        "recovered",
                    )
        else:
            if self.model.t >= self.getCovidStateAttr("t") + self.getCovidStateAttr(
                "duration"
            ):
                self.setCovidState(self.getCovidStateAttr("nextState"), self.model.t)

    def _progressCovidRecoveredState(self):
        if self.getAgeGroup() == "young":
            if np.random.rand() < self.p.p_recovered_immun_young:
                self.setCovidState("immunized", self.model.t, 180)
            else:
                self.setCovidState()
        elif self.getAgeGroup() == "working":
            if np.random.rand() < self.p.p_recovered_immun_working:
                self.setCovidState("immunized", self.model.t, 180)
            else:
                self.setCovidState()
        elif self.getAgeGroup() == "elderly":
            if np.random.rand() < self.p.p_recovered_immun_elderly:
                self.setCovidState("immunized", self.model.t, 180)
            else:
                self.setCovidState()

    def _progressCovidImmunizedState(self):
        if self.model.t >= self.getCovidStateAttr("t") + self.getCovidStateAttr(
            "duration"
        ):
            self.setCovidState()

    def _progressCovidDeadState(self):
        self.covid_death += 1
        self.reset()

    def progressCovid(self):
        if self.getCovidStateAttr("state") == "exposed":
            self._progressCovidExposedState()
        elif self.getCovidStateAttr("state") == "infected non-sympotomatic":
            self._progressCovidInfectedNonsympotomaticState()
        elif self.getCovidStateAttr("state") == "mild":
            self._progressCovidMildState()
        elif self.getCovidStateAttr("state") == "severe":
            self._progressCovidSevereState()
        elif self.getCovidStateAttr("state") == "critical":
            self._progressCovidCriticalState()
        elif self.getCovidStateAttr("state") == "recovered":
            self._progressCovidRecoveredState()
            self.resetSickLeaves()
        elif self.getCovidStateAttr("state") == "immunized":
            if np.random.rand() < self.p.p_mutation * (
                (1 - self.p.p_vax) ** int(self.p.covid_settings == "VAX")
            ):
                self.setCovidState("exposed", self.model.t)
            else:
                self._progressCovidImmunizedState()
        elif self.getCovidStateAttr("state") == "dead":
            self._progressCovidDeadState()

    def setSickLeaves(self, date):
        self.sickLeaves.append(date)

    def getSickLeaves(self):
        return self.sickLeaves

    def resetSickLeaves(self):
        self.sickLeaves = []

    def isDead(self):
        return self.dead

    def isEmployed(self):
        return self.employed

    def setObtainedCredit(self, obtainedCredit):
        self.obtainedCredit = obtainedCredit
        self.obtainedCreditList[-1] = np.sum([obtainedCredit])

    def getObtainedCredit(self):
        return self.obtainedCredit

    def setDead(self):
        self.deposit = 0
        self.div = 0
        self.wealthList = [0]
        self.desired_consumption = 0
        self.consumption = 0
        self.employed = False
        self.belongToFirm = None
        self.wage = 0
        self.income = 0
        self.dead = True
