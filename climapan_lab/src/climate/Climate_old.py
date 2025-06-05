import copy
import agentpy as ap
import numpy as np


class Climate(ap.Agent):
    def setup(self):
        self.climate_shock_start = self.p.climate_shock_start
        self.zeta_g = self.p.climateZetaGreen,
        self.zeta_b = self.p.climateZetaBrown,
        self.alpha_c = self.p.climateAlpha_conc
        self.beta_c = self.p.climateBeta_conc
        self.conc_t0 = self.p.climateConc_t0
        self.conc_t = copy.copy(self.conc_t0)
        self.conc_pre = self.p.climateConc_pre
        self.gammaRF = self.p.climateGammaRF
        self.CS = self.p.climateSensitivity
        # Calculate e-folding time
        self.phi = np.max([self.p.climateAlpha_phi + self.p.climateBeta_phiL*self.CS + self.p.climateBeta_phiQ*self.CS**2, 1])
        self.EM = 0
        self.step_EM = 0
        self.T = self.p.climateT0
        self.T_list = [self.T]
        self.alpha_d = self.p.climateAlpha_d
        self.sigma_d = self.p.climateSigma_d
        self.eps_etd = self.p.climateEps_etd
        self.gamma_etd = self.p.climateGamma_etd
        self.beta_d = self.p.climateBeta_d
        self.eps_etm = self.p.climateEps_etm
        self.gamma_etm = self.p.climateGamnma_etm
        self.RF = 0
        self.ETD = 0
        self.ETM = 0
        self.CO2 = self.EM + self.p.CO2_offset
        self.shockHappens = False
    
    def initGDP(self, GDP):
        self.GDP_t0 = GDP
        if self.p.verboseFlag:
            print("initial GDP", self.GDP_t0)

    def initAggregatedIncome(self):
        self.aggregatedIncome_t0 = np.sum(list(self.model.aliveConsumers.income)) + np.sum(list(self.model.aliveConsumers.wage))
    
    def progress(self, list_firm):
        # Calculate emission at time t
        self.workers_t = 0
        self.step_EM = 0
        if (self.model.t >= self.model.fiscalDate) and self.p.covid_settings and self.p.settings == "S3MOD" and self.model.fiscal_count <3:
            """for firm in list_firm:
                if firm.getUseEnergy() == 'green':
                    firm.update_actual_production(self.p.lumpSum / firm.getPrice())"""
            self.EM += self.p.climateZetaGreen * 1500
        for firm in list_firm:
            if firm.getUseEnergy() == 'green':
                self.EM += (np.sum(self.p.climateZetaGreen * firm.actual_production))
                self.step_EM += (np.sum(self.p.climateZetaGreen * firm.actual_production))
            else:
                self.EM += (self.p.climateZetaBrown * firm.actual_production)
                self.step_EM += (np.sum(self.p.climateZetaBrown * firm.actual_production))
            try:
                self.workers_t += np.sum(firm.getNumberOfLabours())
            except:
                pass
        
        # Calculate C02 concentration at time t
        self.CO2 = (np.log10(self.p.climateZetaBeta * self.EM) / np.log10(np.log10(self.p.climateZetaBeta * self.EM)*1e9 + (self.p.CO2_offset))) * 1e9 + self.p.CO2_offset
        self.conc_t  += np.sum(self.alpha_c * self.CO2)
        self.conc_t -= np.sum(self.beta_c * (self.conc_t - self.conc_pre))

        # Calculate radiative forcing
        self.RF = self.gammaRF*np.log10(self.conc_t / self.conc_t0)
        
        # Calculate temperature
        self.T = (1 - (1/self.phi))*self.T + (1/self.phi)*(self.CS/(5.35*np.log(2)))*self.RF
        self.T_list.append(self.T)
        #print(self.climate_shock_start)
        if self.model.month_no > self.climate_shock_start:
            #print((self.T - self.T_list[-12]) / self.T_list[-12], self.T)
            if (self.T - self.T_list[-self.climate_shock_start]) / self.T_list[-self.climate_shock_start] > 20:
                if self.p.climateShockMode == "AggPop":
                    self._induce_aggregate_population_climate_shock()
                    self.shockHappens = True
                elif self.p.climateShockMode == "Idiosyncratic":
                    self._induce_idiosyncratic_climate_shock()
                    self.shockHappens = True


    def _induce_aggregate_population_climate_shock(self):
        aliveConsumers = self.model.aliveConsumers.select(self.model.aliveConsumers.isDead() != True)
        aggregatedIncome = np.sum(list(self.model.aliveConsumers.getIncome())) + np.sum(list(self.model.aliveConsumers.getWage()))
        self.PM = self.p.currentMortality \
                    *len(aliveConsumers) \
                    *(aggregatedIncome/self.aggregatedIncome_t0)**self.eps_etd \
                    *((1 + self.sigma_d*self.T)**self.p.climateWindSpeed)


    def _induce_idiosyncratic_climate_shock(self):
        omega = 1 / (1 - 0.0028*self.T**2)
        self.aliveConsumersPostShock = omega * len(self.model.aliveConsumers.select(self.model.aliveConsumers.isDead() != True and self.model.aliveConsumers.isEmployed()))


    def process_aggregate_damage(self):
        #print(self.GDP_t1)
        self.ETD = self.alpha_d*self.model.GDP*((self.model.GDP/self.GDP_t0)**self.eps_etd)*self.sigma_d*((self.conc_t/self.conc_t0)**self.gamma_etd - 1)
        self.ETM = self.beta_d*self.workers_t*((self.model.GDP/self.GDP_t0)**self.eps_etd)*self.sigma_d*((self.conc_t/self.conc_t0)**self.gamma_etm - 1)

    def getPM(self):
        return self.PM
    
    def getAliveConsumersPostShock(self):
        return self.aliveConsumersPostShock