import copy
from collections import OrderedDict

import jaxabm.agentpy as ap
import numpy as np
import numpy.random as random

from ..param_dict import ParamDict
from .EnergyFirmBase import EnergyFirmBase


class GreenEnergyFirm(EnergyFirmBase):
    """A GreenEnergyFirm agent"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.p = ParamDict(self.p)

    def setup(self):
        super().setup()
        # self.price = random.randint(6,10)
        self.price = self.p.base_green_energy_price
        self.capital = 50000
        self.capital_increase = 25000
        self.capital_demand = self.capital * (
            self.capital_growth_rate + self.capital_depreciation
        )
        self.useEnergy = "green"
        self.defaultProb = 0
        self.base_price = self.p.base_green_energy_price
        self.energy_price_growth = self.p.energy_price_growth
        self.brown_firm = self.useEnergy == "brown"
