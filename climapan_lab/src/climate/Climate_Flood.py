import copy
import agentpy as ap
import numpy as np


class Climate(ap.Agent):
    def setup(self):
        #old for storm
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

        #new for flood
        self.flood_prob = 0 #flood probability at time t
        self.flood_severity = 0
        self.K_dam = 0
        self.P = 0 #flood precipitation

        self.climate_omega = self.p.climate_flood_omega
        self.delta = self.p.flood_delta
        self.psi_h = self.p.psi_h
        self.psi_f_g = self.p.psi_f_g
        self.psi_f_b = self.p.psi_f_b
        self.alpha_T = self.p.alpha_T
        self.alpha_P = self.p.alpha_P
        self.T_threshold = self.p.T_threshold
        self.p_threshold = self.p.P_threshold
        
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
        self.FS()
        self.flood_trigger()
    
    def FS(self):
        self.flood_severity = self.climate_omega * self.T + self.delta * self.P

    def climate_damage_household(self, S):
        return S - self.psi_h * self.flood_severity * S

    def climate_damage_firm(self, K, type):
        
        ###implement resilient investment - still required
        psi = self.psi_f_g ** (type == "green") * self.psi_f_b ** (type == "brown")
        K_dam = psi * self.flood_severity * K
        K -= K_dam
        return K
    

    def flood_trigger(self):
        self.flood_prob = 1 / (1 + np.exp(-self.alpha_T * (self.T - self.T_threshold) - self.alpha_P * (self.P - self.p_threshold)))

    def initGDP(self, GDP):
        self.GDP_t0 = GDP
        if self.p.verboseFlag:
            print("initial GDP", self.GDP_t0)
