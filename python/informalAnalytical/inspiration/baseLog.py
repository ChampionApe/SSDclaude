import numpy as np, pandas as pd
from pyDbs import is_iterable
def noneInit(x, fallBackValue):
    return fallBackValue if x is None else x

#######################################################################
##########                ANALYTICAL LOG MODEL              ###########
#######################################################################

class BaseLogA:
    """ Base methods for analytical, LOG model. """
    def __init__(self, m, t = None):
        self.m = m # associated Model class 
        self.db = m.db # main database
        self.t0 = self.db['t'][0] # first yearly index (used to avoid lagging outside t domains)
        self.t = t # current year

    def __call__(self, k, t = None):
        """ Return symbol 'k' from database. If t is not provided, rely on self.t attribute as backup. """
        return self.db[f'{k}'].xs(max(noneInit(t, self.t), self.t0))

    def get(self, k, t = None):
        """ return numpy version of __call__ method """
        s = self(k, t = t)
        return s.values if isinstance(s, (pd.Series, pd.DataFrame)) else s

    #######################################################################
    ##########                    0. Aux methods                     ###########
    #######################################################################
    # Political weights:
    def ω2i(self, t = None):
        """ Political weight on types 2i """
        return (self('pi[t-1]', t).mul(self('ω',t), axis = 0).mul(self('μi',t), axis = 0)).values
    def ω20(self, t = None):
        """ Political weight on types 20 """
        return self.get('p0[t-1]', t) * self.get('ω',t) * self.get('μ0',t)
    def ω1i(self, t = None):
        """ Political weight on types 1i """
        return self.get('μi',t)
    def ω10(self, t = None):
        """ Political weight on types 10 """
        return self.get('μ0',t)

    # Power functions:
    def power_s(self, t = None):
        """ α(1+ξ)/(1+αξ) """
        return self.get('α',t)*(1+self.get('ξ',t))/(1+self.get('α',t)*self.get('ξ',t))
    def power_h(self, t = None):
        """ αξ/(1+αξ) """
        return self.get('α',t)*self.get('ξ',t)/(1+self.get('α',t)*self.get('ξ',t))
    def power_p(self, t = None):
        """ ( α(1+ξ)/(1+αξ) )^2 """
        return self.power_s(t)**2

    # Auxiliary parameters over household types:
    def auxProd(self, t = None):
        """ ηi^(1+ξ)/Xi^ξ"""
        return (self('ηi', t).pow(1+self('ξ',t), axis = 0)/self('Xi',t).pow(self('ξ',t), axis = 0)).values
    def auxProd_(self, t = None):
        """ ηi^(1+ξ)/Xi^ξ - lagged t-1 """
        return (self('ηi[t-1]',t).pow(1+self('ξ[t-1]',t), axis = 0)/self('Xi[t-1]',t).pow(self('ξ[t-1]',t), axis = 0)).values
    def auxProd0(self, t = None):
        """ η0^(1+ξ)/X0^ξ"""
        return self.get('η0', t)**(1+self.get('ξ',t))/self.get('X0',t)**self.get('ξ',t)
    def auxInf0(self, t = None):
        """ ( η0^(1+ξ)/X0^ξ ) * ((1-α)/Γh^α)^((1+ξ)/(1+αξ)) / (1+ξ)"""
        return self.auxProd0(t)*((1-self.get('α',t))/self.get('Γh',t)**(self.get('α',t)))**((1+self.get('ξ',t))/(1+self.get('ξ',t)*self.get('α',t)))/(1+self.get('ξ',t))
    def auxForm1(self, t = None):
        """ ( (1-α)/α ) * p * θ/κ """
        return self.get('αr',t)*self.get('p',t)*self.get('θ[t+1]',t)/self.get('κ',t)


    def Γh(self, t = None):
        """ ∑i γi * ηi^(1+ξ)/Xi^ξ"""
        return (self('γi') * self.auxProd()).sum()
    def auxΓB1(self, Bi, t = None):
        """ ∑i γi * ηi^(1+ξ)/Xi^ξ * Bi/(1+Bi)"""
        return np.matmul((self('γi',t) * self.auxProd(t)).values, (Bi/(1+Bi)).T)
    def auxΓB2(self, Bi, t = None):
        """ ∑i γi * 1/(1+Bi)"""
        return np.matmul(self('γi',t).values, 1/(1+Bi.T))
    def auxΓB3(self, Bi, t = None):
        """ ∑i γi * ηi^(1+ξ)/Xi^ξ * (Bi/(1+Bi)^2)"""
        return np.matmul((self('γi',t) * self.auxProd(t)).values, (Bi/(1+Bi)**2).T)
    def auxΓB4(self, Bi, t = None):
        """ ∑i γi * (Bi/(1+Bi)^2)"""
        return np.matmul(self('γi',t).values, (Bi/(1+Bi)**2).T)

    # Auxiliary methods used for PEE conditions:
    def aux_PEE(self, v1i = None, v10 = None, v2i = None, v20 = None, τ = None, t = None):
        return self.interiorFOC_V1(np.matmul(v2i, self.get('γi[t-1]',t)*self.ω2i(t))+v20*self.get('γ0[t-1]',t)*self.ω20(t)+self.get('ν',t)*(np.matmul(v1i, self.get('γi',t)*self.ω1i(t))+v10*self.get('γ0',t)*self.ω10(t)), τ)

    def adjustFocMultiplicative_V1(self, z, x, l = 0, u = 1, kl = 10, ku = 10):
        """ Adjust FOC in a multiplicative way: z is the "original" marginal effect, x is the bounded variable """
        return z-abs(z)*(kl*(np.clip(x, None, l)-l)+ku*(np.clip(x,u,None)-u))
    def adjustFocMultiplicative_V2(self, z, x, l = 0, u = 1, kl = 10, ku = 10):
        """ Adjust FOC in a multiplicative way: z is the "original" marginal effect, x is the bounded variable """
        return z-(kl*(np.clip(x, None, l)-l)+ku*(np.clip(x,u,None)-u))

    def interiorFOC_V1(self, z, x, var = 'τ'):
        return self.adjustFocMultiplicative_V1(z, x, l = self.db[f'{var}_l'], u = self.db[f'{var}_u'], kl = self.db[f'k{var}_l'], ku = self.db[f'k{var}_u'])
    def interiorFOC_V2(self, z, x, var = 'τ'):
        return self.adjustFocMultiplicative_V2(z, x, l = self.db[f'{var}_l'], u = self.db[f'{var}_u'], kl = self.db[f'k{var}_l'], ku = self.db[f'k{var}_u'])

    #######################################################################
    ##########                    1. Simple defs                     ###########
    #######################################################################
    def R(self, s_ = None, h = None, t = None):
        return self.get('α',t) * (self.get('ν',t)*h/s_)**(1-self.get('α',t))
    def Bi(self, t = None, **kwargs):
        return self.get('βi',t)
    def Γs(self, Bi = None, τp = None, t = None):
        return (1/(1+self.get('ξ',t)))*self.auxΓB1(Bi, t = t)/(1+self.get('αr',t)*(self.get('p',t)*τp/self.get('κ',t))*(self.get('θ[t+1]',t)+self.auxΓB2(Bi, t = t)*(1-self.get('θ[t+1]',t))))

    # Savings and labor supply:
    def Θh_t(self, τ = None, τp = None, Γs = None, t = None):
        return self.get('Γh',t)**((1+self.get('ξ',t))/(1+self.get('α',t)*self.get('ξ',t))) * ((1-self.get('α',t))*(1-τ)/(self.get('Γh',t)-self.auxForm1(t) * τp * Γs))**(self.get('ξ',t)/(1+self.get('α',t)*self.get('ξ',t)))
    def Θs_t(self, Θh = None, Γs = None, t = None):
        return (Θh/self.get('Γh',t))**((1+self.get('ξ',t))/self.get('ξ',t)) * Γs
    def h_t(self, s_ = None, Θh = None, t = None):
        return Θh*(s_/self.get('ν',t))**self.power_h(t)
    def s_t(self, h = None, Γs = None, t = None):
        return (h/self.get('Γh',t))**((1+self.get('ξ',t))/self.get('ξ',t))*Γs

    def hFromΘh_t(self, s_ = None, Θh = None, t = None):
        return Θh * (s_/self.get('ν',t))**self.power_h(t)    

    def si_s(self, Bi = None, Γs = None, τp = None, t = None):
        """ Savings ratios si/s """
        return Bi*self.auxProd(t) /((1+Bi)*(1+self('ξ',t))*Γs)-self('αr',t)*τp*(self('p',t)/self('κ',t))*((1-self('θ[t+1]',t))/(1+Bi)+self('θ[t+1]',t)*self.auxProd(t)/self('Γh',t))

    #######################################################################
    ##########                2. Terminal state (FH)                 ###########
    #######################################################################

    def PEE_T(self, τBound = None, τ = None, dlnh_Dτ = None, si_s = None, Θh = None, t = None):
        v1i = self.PEE1i_T(dlnh_Dτ = dlnh_Dτ, t = t)
        v2i = self.PEE2i(τ = τBound, dlnh_Dτ = dlnh_Dτ, si_s = si_s, t = t)
        v20 = self.PEE20(τ = τBound, dlnh_Dτ = dlnh_Dτ, Θh = Θh, t = t)
        return self.aux_PEE(v1i = v1i, v10 = 0, v2i = v2i, v20 = v20, τ = τ, t = t)

    def Θh_T(self, τ = None, t = None):
        return self.get('Γh',t)**(1/(1+self.get('ξ',t)*self.get('α',t))) * ((1-self.get('α',t))*(1-τ))**(self.get('ξ',t)/(1+self.get('α',t)*self.get('ξ',t)))
    def h_T(self, s_ = None, τ = None, t = None):
        return self.Θh_T(τ = τ, t = t)*(s_/self.get('ν',t))**self.power_h(t)
    def c1i_T(self, h = None, t = None):
        return self.auxProd(t)*(h/self('Γh',t))**((1+self('ξ',t))/self('ξ',t))
    def c̃1i_T(self, h = None, t = None):
        return self.c1i_T(h = h, t = t)/(1+self('ξ',t))
    def PEE1i_T(self, dlnh_Dτ = None, t= None):
        return np.full(self.m.ni, dlnh_Dτ*(1+self.get('ξ',t))/self.get('ξ',t))

    #######################################################################
    ##########                3. Out of terminal state            ###########
    #######################################################################
    def PEE_t(self, τBound = None, τ  = None, si_s = None, Θh = None, dlnh_Dτ = None, t = None):
        v1i = self.PEE1i_t(dlnh_Dτ = dlnh_Dτ, t = t)
        v10 = self.PEE10_t(τ = τBound, t = t)
        v2i = self.PEE2i(τ = τBound, dlnh_Dτ = dlnh_Dτ, si_s = si_s, t = t)
        v20 = self.PEE20(τ = τBound, dlnh_Dτ = dlnh_Dτ, Θh = Θh, t = t)
        return self.aux_PEE(v1i = v1i, v10 = v10, v2i = v2i, v20 = v20, τ = τ, t =t)

    # General stuff:
    def dlnh_dτ(self, τ = None, t = None):
        """ ∂ln(h)/∂τ """
        return -self.get('ξ',t)/((1+self.get('ξ',t)*self.get('α',t))*(1-τ))

    # Types 2i
    def PEE2i(self, τ = None, dlnh_Dτ = None, si_s = None, t = None):
        return (1-self.get('α',t))*dlnh_Dτ+self.aux_c2i_coeff(t)/(si_s+τ * self.aux_c2i_coeff(t))
    def aux_c2i_coeff(self, t = None):
        return self.get('αr',t)*(self.get('p[t-1]',t)/self.get('κ[t-1]',t))*(1+self.get('θ',t)*(self.auxProd(noneInit(t,self.t)-1)/self.get('Γh[t-1]',t)-1))
    def c2i(self, τ = None, s_ = None, h = None, si_s = None,  t = None):
        return self.get('α',t)*(self.get('ν',t)/self.get('p[t-1]',t))*h**(1-self.get('α',t))*(s_/self.get('ν',t))**self.get('α',t)*(si_s + τ*self.aux_c2i_coeff(t))

    # Type 20:
    def PEE20(self, τ = None, Θh = None, dlnh_Dτ = None, t = None):
        return ((1-self.get('α',t))*self.get('ν',t)*self.get('eps',t)*Θh**(1-self.get('α',t)) /self.get('κ[t-1]',t)) * (1+(1-self.get('α',t))*τ*dlnh_Dτ)/self.Θc̃20(τ = τ, Θh = Θh, t = t)
    def Θc̃20(self, τ = None, Θh = None, t = None):
        return self.get('χ[t-1]',t)**(1+self.get('ξ[t-1]',t))*self.auxInf0(noneInit(t,self.t)-1)+(1-self.get('α',t))*self.get('ν',t)*self.get('eps',t)*τ *Θh**(1-self.get('α',t)) /self.get('κ[t-1]',t)
    def c̃20(self, τ = None, Θh = None, s_ = None, t = None):
        return self.Θc̃20(τ = τ, Θh = Θh, t = t)*(s_/self.get('ν',t))**self.power_s(t)

    # Types 1i
    def PEE1i_t(self, dlnh_Dτ = None, t = None):
        return ((1+self.get('ξ',t))/(self.get('ξ',t)))*dlnh_Dτ*(1+self.get('βi',t))

    # Types 10:
    def PEE10_t(self, τ = None, t = None):
        return -self.get('β0',t)*self.power_s(t)**2 / (self.get('α',t)*(1-τ))

    # Used in reporting (SS_report method in main)
    def backOutH(self, s = None, Γs = None, t = None):
        return (s/Γs)**(self.get('ξ',t)/(1+self.get('ξ',t)))*self.get('Γh',t)
    def backOutΘs(self, s_ = None, s = None, t = None):
        return s/((s_/self.get('ν',t))**self.power_s(t))


    #######################################################################
    ##########                4. Steady state methods                ###########
    #######################################################################
    def steadyState_Γs(self, τ, t = None):
        return self.Γs(Bi = self.get('βi',t), τp = τ, t = t)

    def steadyState_s(self, Γs, τ, t = None):
        """ Return steady state level of savings"""
        return self.get('Γh',t)**(1+self.get('ξ',t))*( ((1-self.get('α',t))*(1-τ)/(self.get('Γh',t)-self.auxForm1(t)*τ*Γs))**(1+self.get('ξ',t))* Γs**(1+self.get('α',t)*self.get('ξ',t))/self.get('ν',t)**(self.get('α',t)*(1+self.get('ξ',t))))**(1/(1-self.get('α',t)))

    #######################################################################
    ########            5. Calibration specific methods         ###########
    #######################################################################

    def calib_η0(self, τ = None, Θh = None, t = None):
        t = noneInit(t, self.db['t0'])
        return (self('zη0',t)/self('zx0',t)) * (1-self('α',t))*(1-τ)/(Θh**(self('α',t))* ((1-self('α',t))/self('Γh',t)**(self('α',t)))**(1/(1+self('ξ',t)*self.get('α',t))))
    def calib_X0(self, η0 = None, Θh = None, t = None):
        t = noneInit(t, self.db['t0'])
        return η0 * ((1-self('α',t))/self('Γh',t)**(self('α',t)))**(1/(1+self('ξ',t)*self('α',t))) / ((Θh*self('zx0',t))**(1/self('ξ',t)))
    def calib_savingsRate(self, s_ = None, s= None, h = None, t = None):
        t = noneInit(t, self.db['t0'])
        return s / ((1-self.get('α',t))*(s_/self.get('ν',t))**self.get('α',t) * h**(1-self.get('α',t)))

class BaseLogA_Grid(BaseLogA):
    """ Base methods for analytical, LOG model - gridded inputs """

    # Simple defs:
    def Bi(self, t = None, **kwargs):
        return self.get('βi',t)[None,:]
    def si_s(self, Bi = None, Γs = None, τp = None, t = None):
        return Bi*self.auxProd(t) /((1+Bi)*(1+self('ξ',t))*Γs[:,None])-(self('αr',t)*τp*self('p',t)/self('κ',t))[:,None]*((1-self('θ[t+1]',t))/(1+Bi)+self('θ[t+1]',t)*self.auxProd(t)/self.get('Γh',t))

    # Terminal state:
    def c1i_T(self, h = None, t = None):
        return ((h/self('Γh',t))**((1+self('ξ',t))/self('ξ',t)))[:,None]*self.auxProd(t)[:,None].T
    def PEE1i_T(self, dlnh_Dτ = None, t= None):
        return np.tile(dlnh_Dτ[:,None]*(1+self.get('ξ',t))/self.get('ξ',t), self.m.ni)

    # Out of terminal state
    def c2i(self, τ = None, s_ = None, h = None, si_s = None,  t = None):
        return (self.get('α',t)*(self.get('ν',t)/self.get('p[t-1]',t))*h**(1-self.get('α',t))*(s_/self.get('ν',t))**self.get('α',t))[:,None]*(si_s + self.aux_c2i_coeff(t)*τ[:,None])
    def PEE2i(self, τ = None, dlnh_Dτ = None, si_s = None, t = None):
        return (1-self.get('α',t))*dlnh_Dτ[:,None]+self.aux_c2i_coeff(t)/(si_s+self.aux_c2i_coeff(t)*τ[:,None])
    def PEE1i_t(self, dlnh_Dτ = None, t = None):
        return ((1+self.get('ξ',t))/(self.get('ξ',t)))*dlnh_Dτ[:,None]*(1+self.get('βi',t)*self.power_s(t))

class BaseLogA_Time(BaseLogA):
    def __init__(self, m, ts = 'FH'):
        super().__init__(m)
        self.ts = ts # terminal state 

    def __call__(self, k, t = None):
        try:
            return self.db[k] if t is None else self.db[k].loc[t]
        except KeyError:
            return self.db[k].loc[np.clip(t, self.t0, None)]

    def get(self, k, t = None):
        s = self(k, t = t)
        return s.values if isinstance(s, (pd.Series, pd.DataFrame)) else s

    # Aux methods: Identical to base implementation, except first dimension = time
    def Γh(self, t = None):
        return (self('γi',t) * self.auxProd(t)).sum(axis=1)
    def auxΓB1(self, Bi, t = None):
        return ((self('γi',t) * self.auxProd(t)).values * (Bi/(1+Bi))).sum(axis=-1)
    def auxΓB2(self, Bi, t = None):
        return (self.get('γi',t) * (1/(1+Bi))).sum(axis=-1)
    def auxΓB3(self, Bi, t = None):
        return ((self('γi',t) * self.auxProd(t)).values * (Bi/(1+Bi)**2)).sum(axis=-1)
    def auxΓB4(self, Bi, t = None):
        return (self.get('γi',t)*Bi/(1+Bi)**2).sum(axis=-1)

    def aux_PEE(self, v1i = None, v10 = None, v2i = None, v20 = None, τ = None, t = None):
        return self.interiorFOC_V1( (v2i*self.get('γi[t-1]',t)*self.ω2i(t)).sum(axis=-1)+v20*self.get('γ0[t-1]',t)*self.ω20(t)+self.get('ν',t)*((v1i * self.get('γi',t)*self.ω1i(t)).sum(axis=-1)+v10*self.get('γ0',t)*self.ω10(t)), τ)

    # Simple defs:
    def B0(self, t = None, **kwargs):
        return self.get('β0',t)
    def si_s(self, Bi = None, Γs = None, τp = None, t = None):
        return Bi*self.auxProd(t) /((1+Bi)*(1+self.get('ξ',t)[:,None])*Γs[:,None])-(self.get('αr',t)*τp*self.get('p',t)/self.get('κ',t))[:,None]*((1-self.get('θ[t+1]',t)[:,None])/(1+Bi)+self.get('θ[t+1]',t)[:,None]*self.auxProd(t)/self.get('Γh',t)[:,None])

    # terminal state:
    def PEE1i_T(self, dlnh_Dτ = None, t = None):
        return np.tile((dlnh_Dτ * (1+self.get('ξ',t))/self.get('ξ',t))[:,None], self.m.ni)
    def Θc̃1i_T(self, Θh = None, t = None): 
        return ((Θh/self.get('Γh',t))**((1+self.get('ξ',t))/self.get('ξ',t))/(1+self.get('ξ',t)))[:,None] * self.auxProd(t)

    # Out of terminal state:
    def aux_c2i_coeff(self, t = None):
        return (self.get('αr',t)*self.get('p[t-1]',t)/self.get('κ[t-1]',t))[:,None]*(1+self.get('θ',t)[:,None]*(self.auxProd(t)/self.get('Γh[t-1]',t)[:,None]-1))
    def PEE2i(self, τ = None, dlnh_Dτ = None, si_s = None, t = None):
        return ((1-self.get('α',t))*dlnh_Dτ)[:,None]+self.aux_c2i_coeff(t)/(si_s+self.aux_c2i_coeff(t)*τ[:,None])
    def PEE1i_t(self, dlnh_Dτ = None, t = None):
        return (1+self.get('βi',t)*self.power_s(t)[:,None]) * ((1+self.get('ξ',t))*dlnh_Dτ/self.get('ξ',t))[:,None]
    # Used in reporting:
    def Θc̃1i_t(self, Θh = None, Γs = None, Bip = None, τp = None, t = None):
        return ((Θh/self.get('Γh',t))**((1+self.get('ξ',t))/self.get('ξ',t)))[:,None]*(self.auxProd(t)/(1+self.get('ξ',t)[:,None])+(Γs*self.get('αr',t)* self.get('p',t)*τp*(1-self.get('θ[t+1]',t))/self.get('κ',t))[:,None])/(1+Bip)
    def Θc2i(self, τ = None, Θh = None, si_s = None, t = None):
        return (self.get('α',t)*self.get('ν',t)*Θh**(1-self.get('α',t))/self.get('p[t-1]',t))[:,None] * (si_s + (self.get('αr',t)*self.get('p[t-1]',t)*τ/self.get('κ[t-1]',t))[:,None]*(1+self.get('θ',t)[:,None]*(self.auxProd_(t)/self.get('Γh[t-1]',t)[:,None]-1)))
    def Θc2pi_t(self, τp = None, Θhp = None, Θs = None, si_s = None, t = None):
        return ((Θs/self.get('ν[t+1]',t))**self.power_s(t)*self.get('α[t+1]',t)*self.get('ν[t+1]',t)*Θhp**(1-self.get('α[t+1]',t))/self.get('p',t))[:,None] * (si_s+(self.get('αr[t+1]',t)*self.get('p',t)*τp/self.get('κ',t))[:,None]*(1+self.get('θ[t+1]',t)[:,None]*(self.auxProd(t)/self.get('Γh',t)[:,None]-1)))
    def Θc̃10(self, t = None):
        return self.auxInf0(t)
    def Θc̃2p0(self, τp = None, Θhp = None, t = None):
        return self.get('χ',t)**(1+self.get('ξ',t))*self.auxInf0(t)+(1-self.get('α[t+1]',t))*self.get('ν[t+1]',t)*self.get('eps[t+1]',t)*τp *Θhp**(1-self.get('α[t+1]',t)) /self.get('κ',t)


    #######################################################################
    ##########                4. Finite horizon methods         ###########
    #######################################################################
    def FH_ΓsLagged(self, τ = None):
        return self.Γs(Bi = self.get('βi[t-1]'), τp = τ)
    def FH_Γs(self, τp = None):
        return self.Γs(Bi = self.get('βi[t-1]',self.db['txE']), τp = τp[:-1], t = self.db['txE'])
    def FH_Θh(self, τ = None, τp = None, Γs = None):
        return np.hstack([self.Θh_t(τ = τ[:-1], τp = τp[:-1], Γs = Γs, t = self.db['txE']), self.Θh_T(τ = τ[-1], t = self.db['t'][-1])])
    def FH_Θs(self, Θh = None, Γs = None):
        return self.Θs_t(Θh[:-1], Γs = Γs, t = self.db['txE'])
    def FH_s(self, Θs = None, s0 = None):
        s = np.empty(self.m.T-1)
        s[0] = Θs[0]*(s0/self.get('ν',self.t0))**(self.power_s(self.t0))
        for t in range(1, self.m.T-1):
            s[t] = Θs[t]*(s[t-1]/self.get('ν',self.db['t'][t]))**(self.power_s(self.db['t'][t]))
        return s
    def FH_h(self, Θh = None, s_ = None):
        return Θh * (s_/self.get('ν'))**self.power_h()
    def FH_BackOutΘs(self, s_ = None, s = None):
        return s/((s_[:-1]/self.get('ν',t = self.db['txE']))**self.power_s(self.db['txE']))
    def FH_BackOutΘh(self, s_ = None, h = None):
        return h/((s_/self('ν'))**self.power_h())

    def FH_PEE(self, τBound = None, τ = None, si_s = None, Θh = None, dlnh_Dτ = None):
        return np.hstack([self.PEE_t(τBound = τBound[:-1], τ = τ[:-1], si_s = si_s[:-1], Θh = Θh[:-1], dlnh_Dτ = dlnh_Dτ[:-1], t = self.db['txE']),
                          self.PEE_T(τBound = τBound[-1:], τ = τ[-1:], si_s = si_s[-1:], Θh = Θh[-1:], dlnh_Dτ = dlnh_Dτ[-1:], t = self.db['t'][-1:])])


    ### REPORTING METHODS - relies on dictionary of solution structure, returns pandas objects
    def FH_Θhi(self, sd):
        return pd.DataFrame((self.get('ηi')/self.get('Xi'))**(self.get('ξ')[:,None]) / self.get('Γh')[:,None], index = self.db['t'], columns = self.db['i'])
    def FH_Θc̃1i(self, sd):
        return pd.DataFrame(np.vstack([self.Θc̃1i_t(Θh = sd['Θh'].values[:-1], Γs = sd['Γs'].values, Bip = sd['Bi'].values[1:,], τp = sd['τ[t+1]'].values[:-1], t = self.db['txE']), 
                                       self.Θc̃1i_T(Θh = sd['Θh'].values[-1:], t = self.db['t'][-1:])]), index = self.db['t'], columns = self.db['i'])
    def FH_Θc2i(self, sd):
        return pd.DataFrame(self.Θc2i(τ = sd['τ'].values, Θh = sd['Θh'].values, si_s = sd['si/s[t-1]'].values), index = self.db['t'], columns = self.db['i'])
    def FH_Θc2pi(self, sd):
        return pd.DataFrame(self.Θc2pi_t(τp = sd['τ'].values[1:], Θhp = sd['Θh'].values[1:], Θs = sd['Θs'].values, si_s = sd['si/s[t-1]'].values[1:], t = self.db['txE']), index = self.db['txE'], columns = self.db['i'])
    def FH_Θc̃10(self, sd):
        return pd.Series(self.Θc̃10(t = self.db['t']), index = self.db['t'])
    def FH_Θc̃20(self, sd):
        return pd.Series(self.Θc̃20(τ = sd['τ'].values, Θh = sd['Θh'].values, t = self.db['t']), index = self.db['t'])
    def FH_Θc̃2p0(self, sd):
        return pd.Series(self.Θc̃2p0(τp = sd['τ'].values[1:], Θhp = sd['Θh'].values[1:], t = self.db['txE']), index = self.db['txE'])

    # Reporting methods for "levels" - relies on dictionary solution structure, return pandas objects
    def FH_hi_h(self, sd):
        return pd.DataFrame(self.auxProd()/self.get('Γh')[:,None], index = self.db['t'], columns = self.db['i'])
    def FH_c̃1i(self, sd):
        return sd['Θc̃1i'].mul((sd['s[t-1]']/self.get('ν'))**self.power_s(),axis=0)
    def FH_c2i(self, sd):
        return sd['Θc2i'].mul((sd['s[t-1]']/self.get('ν'))**self.power_s(), axis = 0)
    def FH_c2pi(self, sd):
        return sd['Θc2pi'].mul((sd['s[t-1]'].iloc[:-1]/self.get('ν', t = self.db['txE']))**self.power_p(t = self.db['txE']), axis = 0)
    def FH_c̃10(self, sd):
        return sd['Θc̃10']*((sd['s[t-1]']/self.get('ν'))**self.power_s())
    def FH_c̃20(self, sd):
        return sd['Θc̃20']*((sd['s[t-1]']/self.get('ν'))**self.power_s())
    def FH_c̃2p0(self, sd):
        return sd['Θc̃2p0']*((sd['s[t-1]'].iloc[:-1]/self.get('ν',t=self.db['txE']))**self.power_p(t = self.db['txE']))
    def FH_sRate(self, sd, t = None, **kwargs):
        t = noneInit(t, self.db['txE'])
        return sd['s'] / ((1-self.get('α',t))*(sd['s[t-1]'].loc[t]/self.get('ν',t))**self.get('α',t) * sd['h'].loc[t] **(1-self.get('α',t)))


#######################################################################
##########                US VERSION - ANALYTICAL LOG            ###########
#######################################################################

class BaseLogUSA(BaseLogA): 
    """ Base methods for LOG, US model (no informal).
        Note: These methods do not remove methods related to the informal households.
        They only remove the informal part for the important functions that are called. """
    
    def aux_PEE(self, v1i = None, v2i = None, τ = None, t = None):
        return self.interiorFOC_V1(np.matmul(v2i, self.get('γi[t-1]',t)*self.ω2i(t))+self.get('ν',t)*np.matmul(v1i, self.get('γi',t)*self.ω1i(t)), τ)

    def PEE_T(self, τBound = None, τ = None, dlnh_Dτ = None, si_s = None, t = None):
        v1i = self.PEE1i_T(dlnh_Dτ = dlnh_Dτ, t = t)
        v2i = self.PEE2i(τ = τBound, dlnh_Dτ = dlnh_Dτ, si_s = si_s, t = t)
        return self.aux_PEE(v1i = v1i, v2i = v2i, τ = τ, t = t)

    def PEE_t(self, τBound = None, τ  = None, si_s = None, dlnh_Dτ = None, t = None):
        v1i = self.PEE1i_t(dlnh_Dτ = dlnh_Dτ, t = t)
        v2i = self.PEE2i(τ = τBound, dlnh_Dτ = dlnh_Dτ, si_s = si_s, t = t)
        return self.aux_PEE(v1i = v1i, v2i = v2i, τ = τ, t =t)

class BaseLogUSA_Grid(BaseLogA_Grid):
    def aux_PEE(self, v1i = None, v2i = None, τ = None, t = None):
        return self.interiorFOC_V1(np.matmul(v2i, self.get('γi[t-1]',t)*self.ω2i(t))+self.get('ν',t)*np.matmul(v1i, self.get('γi',t)*self.ω1i(t)), τ)

    def PEE_T(self, τBound = None, τ = None, dlnh_Dτ = None, si_s = None, t = None):
        v1i = self.PEE1i_T(dlnh_Dτ = dlnh_Dτ, t = t)
        v2i = self.PEE2i(τ = τBound, dlnh_Dτ = dlnh_Dτ, si_s = si_s, t = t)
        return self.aux_PEE(v1i = v1i, v2i = v2i, τ = τ, t = t)

    def PEE_t(self, τBound = None, τ  = None, si_s = None, dlnh_Dτ = None, t = None):
        v1i = self.PEE1i_t(dlnh_Dτ = dlnh_Dτ, t = t)
        v2i = self.PEE2i(τ = τBound, dlnh_Dτ = dlnh_Dτ, si_s = si_s, t = t)
        return self.aux_PEE(v1i = v1i, v2i = v2i, τ = τ, t =t)

class BaseLogUSA_Time(BaseLogA_Time):

    def aux_PEE(self, v1i = None, v2i = None, τ = None, t = None):
        return self.interiorFOC_V1( (v2i*self.get('γi[t-1]',t)*self.ω2i(t)).sum(axis=-1)+self.get('ν',t)*(v1i * self.get('γi',t)*self.ω1i(t)).sum(axis=-1), τ)

    def PEE_T(self, τBound = None, τ = None, dlnh_Dτ = None, si_s = None, t = None):
        v1i = self.PEE1i_T(dlnh_Dτ = dlnh_Dτ, t = t)
        v2i = self.PEE2i(τ = τBound, dlnh_Dτ = dlnh_Dτ, si_s = si_s, t = t)
        return self.aux_PEE(v1i = v1i, v2i = v2i, τ = τ, t = t)

    def PEE_t(self, τBound = None, τ  = None, si_s = None, dlnh_Dτ = None, t = None):
        v1i = self.PEE1i_t(dlnh_Dτ = dlnh_Dτ, t = t)
        v2i = self.PEE2i(τ = τBound, dlnh_Dτ = dlnh_Dτ, si_s = si_s, t = t)
        return self.aux_PEE(v1i = v1i, v2i = v2i, τ = τ, t =t)

    def FH_PEE(self, τBound = None, τ = None, si_s = None, dlnh_Dτ = None):
        return np.hstack([self.PEE_t(τBound = τBound[:-1], τ = τ[:-1], si_s = si_s[:-1], dlnh_Dτ = dlnh_Dτ[:-1], t = self.db['txE']),
                          self.PEE_T(τBound = τBound[-1:], τ = τ[-1:], si_s = si_s[-1:], dlnh_Dτ = dlnh_Dτ[-1:], t = self.db['t'][-1:])])

#######################################################################
##########            LOG VERSION - INFORMAL SAVINGS            ###########
#######################################################################

class BaseLog(BaseLogA):
    """ Base methods for LOG model with informal savings """
    # New auxiliary methods
    def auxInf1(self, t = None):
        """ ((1-α)/(αr0)) * p0 * ϵ[t+1]/κ """
        return (self.get('αr[t+1]',t)/self.get('α0[t+1]',t))*self.get('p0',t)*self.get('eps[t+1]',t)/self.get('κ',t)
    def auxInf1_(self, t = None):
        """ Lagged version of auxInf1 """
        return (self.get('αr',t)/self.get('α0',t))*self.get('p0[t-1]',t)*self.get('eps',t)/self.get('κ[t-1]',t)

    # Types 20:
    def PEE20(self, τ = None, dlnh_Dτ = None, s0_s = None, t = None):
        return (1-self.get('α',t))*dlnh_Dτ+self.aux_c20_coeff(t)/(s0_s+τ*self.aux_c20_coeff(t))

    def s0_s(self, B0 = None, Θs = None, τp = None, t = None):
        return (1/(1+B0))*(B0*self.auxInf0(t)/Θs-τp*self.auxInf1(t))
    def aux_c20_coeff(self, t = None):
        return (self.get('αr',t)/self.get('α0',t))*(self.get('p0[t-1]',t)*self.get('eps',t))/self.get('κ[t-1]',t)
    def c20(self, τ = None, s_ = None, h = None, s0_s = None, t = None):
        return self.get('α0',t)*self.get('α',t)*(self.get('ν',t)/self.get('p0[t-1]',t))*(s_/self.get('ν',t))**self.get('α',t)*h**(1-self.get('α',t))*(s0_s+τ*self.aux_c20_coeff(t))

    # Types 2i - unchanged ...
    # Types 10:
    def dlnĉ10_dτ(self, τp = None, Θs = None, dlns_Dτ = None, dτp_dτ = None, t = None):
        return self.auxInf1(t)*Θs *(dτp_dτ+τp*dlns_Dτ)/(self.auxInf0(t)+τp * self.auxInf1(t) * Θs)
    def PEE10_t(self, τp = None, B0p = None, Θs = None, dlns_Dτ = None, dlnhp_Dlns = None, dτp_dτ = None, t = None):
        return (1+B0p)*self.dlnĉ10_dτ(τp = τp, Θs = Θs, dlns_Dτ = dlns_Dτ, dτp_dτ = dτp_dτ, t = t)+B0p*(1-self.get('α',t))*(dlnhp_Dlns-1)*dlns_Dτ

    # Types 1i:
    def dlnĉ1i_dτ(self, τp = None, Γs = None, dlnh_Dτ = None, dlnΓs_Dτ = None, dτp_dτ=None, t = None):
        k = self.get('αr',t)*self.get('p',t)*(1-self.get('θ[t+1]',t))*Γs/self.get('κ',t)
        return dlnh_Dτ*(1+self.get('ξ',t))/self.get('ξ',t)+(k*(dτp_dτ+τp*dlnΓs_Dτ))/(self.auxProd(t)/(1+self.get('ξ',t))+(τp*k))
    def PEE1i_t(self, τp = None, Γs = None, Bip = None, dlnh_Dτ = None, dlns_Dτ = None, dlnΓs_Dτ = None, dlnhp_Dlns = None, dτp_dτ = None, t = None):
        return self.dlnĉ1i_dτ(τp = τp, Γs = Γs, dlnh_Dτ = dlnh_Dτ, dlnΓs_Dτ = dlnΓs_Dτ, dτp_dτ = dτp_dτ, t = t)*(1+Bip)+Bip*(1-self.get('α',t))*(dlnhp_Dlns-1)*dlns_Dτ

    # PEE:
    def PEE_T(self, τBound = None, τ = None, dlnh_Dτ = None, si_s = None, s0_s = None, t = None):
        v1i = self.PEE1i_T(dlnh_Dτ = dlnh_Dτ, t = t)
        v2i = self.PEE2i(τ = τBound, dlnh_Dτ = dlnh_Dτ, si_s = si_s, t = t)
        v20 = self.PEE20(τ = τBound, dlnh_Dτ = dlnh_Dτ, s0_s = s0_s, t = t)
        return self.aux_PEE(v1i = v1i, v10 = 0, v2i = v2i, v20 = v20, τ = τ, t = t)

    def PEE_t(self, τBound = None, τ  = None, τp = None, Γs = None, Bip = None, B0p = None, si_s = None, s0_s = None, Θs = None,
                    dlnh_Dτ = None, dlns_Dτ = None, dlnΓs_Dτ = None, dlnhp_Dlns = None, dτp_dτ = None, t = None):
        v1i = self.PEE1i_t(τp = τp, Γs = Γs, Bip = Bip, dlnh_Dτ = dlnh_Dτ, dlns_Dτ = dlns_Dτ, dlnΓs_Dτ = dlnΓs_Dτ, dlnhp_Dlns = dlnhp_Dlns, dτp_dτ = dτp_dτ, t = t)
        v10 = self.PEE10_t(τp = τp, B0p = B0p, Θs = Θs, dlns_Dτ = dlns_Dτ, dlnhp_Dlns = dlnhp_Dlns, dτp_dτ = dτp_dτ, t = t)
        v2i = self.PEE2i(τ = τBound, dlnh_Dτ = dlnh_Dτ, si_s = si_s, t = t)
        v20 = self.PEE20(τ = τBound, dlnh_Dτ = dlnh_Dτ, s0_s = s0_s, t = t)
        return self.aux_PEE(v1i = v1i, v10 = v10, v2i = v2i, v20 = v20, τ = τ)

class BaseLog_Grid(BaseLog, BaseLogA_Grid):
    """ Base methods for LOG model - gridded inputs """

    # Gridded versions of BaseLog methods where relevant:
    def dlnĉ1i_dτ(self, τp = None, Γs = None, dlnh_Dτ = None, dlnΓs_Dτ = None, dτp_dτ=None, t = None):
        k = self.get('αr',t)*self.get('p',t)*(1-self.get('θ[t+1]',t))*Γs/self.get('κ',t)
        return dlnh_Dτ[:,None]*(1+self.get('ξ',t))/self.get('ξ',t)+(k*(dτp_dτ+τp*dlnΓs_Dτ))[:,None]/(self.auxProd(t)/(1+self.get('ξ',t))+(τp*k)[:,None])
    def PEE1i_t(self, τp = None, Γs = None, Bip = None, dlnh_Dτ = None, dlns_Dτ = None, dlnΓs_Dτ = None, dlnhp_Dlns = None, dτp_dτ = None, t = None):
        return self.dlnĉ1i_dτ(τp = τp, Γs = Γs, dlnh_Dτ = dlnh_Dτ, dlnΓs_Dτ = dlnΓs_Dτ, dτp_dτ = dτp_dτ, t = t)*(1+Bip)+Bip*(1-self.get('α',t))*((dlnhp_Dlns-1)*dlns_Dτ)[:,None]

class BaseLog_Time(BaseLog, BaseLogA_Time):
    """ Base methods for LOG model - vectors over t """

    # Used in reporting:
    def Θc̃10_T(self, t = None):
        return self.auxInf0(t)    
    def Θc̃10_t(self, B0p = None, τp = None, t = None):
        return (self.auxInf0(t)+self.auxInf1(t)*τp)/(1+B0p)
    def Θc20(self, τ = None, Θh = None, s0_s = None, t = None):
        return (self.get('α',t)*self.get('α0',t)*self.get('ν',t)/self.get('p0[t-1]',t))*Θh**(1-self.get('α',t))*(s0_s+self.auxInf1_(t)*τ)
    def Θc2p0(self, τp = None, Θhp = None, Θs = None, s0_s = None, t = None):
        return ((Θs/self.get('ν[t+1]',t))**self.power_s(t)*self.get('α[t+1]',t)*self.get('α0[t+1]',t)*self.get('ν[t+1]',t)/self.get('p0',t))*Θhp**(1-self.get('α[t+1]',t))*(s0_s+self.auxInf1(t)*τp)


    # FH methods that are different with informal savings:
    def FH_s0_s(self, Θs = None, τp = None):
        return self.s0_s(B0 = self.get('β0', t = self.db['txE']), Θs = Θs, τp = τp[:-1], t = self.db['txE'])

    def FH_Θc̃10(self, sd):
        return pd.Series(np.hstack([self.Θc̃10_t(B0p = sd['B0'].values[1:], τp = sd['τ'].values[1:], t = self.db['txE']),
                                    self.Θc̃10_T(t = self.db['t'][-1:])]), index = self.db['t'])
    def FH_Θc20(self, sd):
        return pd.Series(self.Θc20(τ = sd['τ'].values, Θh = sd['Θh'].values, s0_s = sd['s0/s[t-1]'].values), index = self.db['t'])
    def FH_Θc2p0(self, sd):
        return pd.Series(self.Θc2p0(τp = sd['τ'].values[1:], Θhp = sd['Θh'].values[1:], Θs = sd['Θs'].values, s0_s = sd['s0/s[t-1]'].values[1:], t = self.db['txE']), index = self.db['txE'])
    def FH_c̃10(self, sd):
        return sd['Θc̃10']*((sd['s[t-1]']/self.get('ν'))**self.power_s())
    def FH_c20(self, sd):
        return sd['Θc20']*((sd['s[t-1]']/self.get('ν'))**self.power_s())
    def FH_c2p0(self, sd):
        return sd['Θc2p0']*((sd['s[t-1]'].iloc[:-1]/self.get('ν',t=self.db['txE']))**self.power_p(t = self.db['txE']))
