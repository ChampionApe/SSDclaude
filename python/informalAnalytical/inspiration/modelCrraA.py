import numpy as np, pandas as pd
from scipy import optimize
from pyDbs import SymMaps as sm
from baseCrra import BaseCrraA, BaseCrraA_Grid, BaseCrraA_Time
from gridsearch.InterpRoots import _find_root_1d
from auxFunctions import noneInit, defaultGrid, polGrid
from modelLogA import ModelLogA
from policyCrra import CrraA


class ModelCrraA(ModelLogA):
    # Override base classes
    _BaseClass = BaseCrraA
    _BaseGridClass = BaseCrraA_Grid
    _BaseTimeClass = BaseCrraA_Time
    _PolicyClass = CrraA

    # New convenience function
    def solvePEE(self, kwargsPOL = None, **kwargs):
        policy = self.POL(**noneInit(kwargsPOL, {}))
        return self.solveEEPol(policy, **kwargs), policy

    # Add namespace for newton routine on stacked named symbols:
    def addNamespaces(self):
        super().addNamespaces()
        self.ns['EE'] = sm(symbols = {'h': self.db['t'], 's': self.db['txE'], 'Γs': self.db['txE']})
        self.ns['EE'].compile()

    @property
    def _x0(self):
        x0 = super()._x0
        x0['EE'] = np.full(self.ns['EE'].len, .2)
        return x0

    # New grids:
    def initGrids(self, **kwargs):
        dsol = self._solGridSettings
        self.solGrids = {'τ': defaultGrid('τ', dsol), 's': polGrid(dsol['s_l'], dsol['s_u'], dsol['s_n'], exp = dsol['s_exp'])}
        dstate = self._stateGridSettings | kwargs
        self.stateGrids = {'τ': np.linspace(dstate['τ_l'], dstate['τ_u'], dstate['τ_n']), 
                           's[t-1]': polGrid(dstate['s[t-1]_l'], dstate['s[t-1]_u'], dstate['s[t-1]_n'], exp = dstate['s[t-1]_exp'])}
        self.db.update(dsol)

    @property
    def _solGridSettings(self):
        return {'kτ_l': 1e2, 'kτ_u': 1e2, 'τ_n': 101, 'τ_l': 1e-4, 'τ_u': 1-1e-4,
                's_n': 101, 's_l': 1e-4, 's_u': .1, 's_exp': 2}
    @property
    def _stateGridSettings(self):
        return {'kτ_l': 1e2, 'kτ_u': 1e2, 'τ_n': 101, 'τ_l': 1e-4, 'τ_u': 1-1e-4,
                's[t-1]_n': 101, 's[t-1]_l': 1e-4, 's[t-1]_u': .1, 's[t-1]_exp': 2}

    # Steady state methods:
    def steadyStateScalar(self, τ, t = None, **kwargs):
        """ Note: This searches for solution for Γs in steady state; this is bounded << B/((1+B)*(1+ξ)), which should be well below 0.75  """
        sol = optimize.root_scalar(lambda x: self.B.steadyStateScalarEq(x, τ, t = t), bracket = (1e-16, 0.75), **kwargs)
        assert sol['converged'], f""" Couldn't identify steady state with τ = {τ}"""
        Bi = self.B.steadyState_Bi(sol['root'], τ, t = t)
        return self.steadyState_report(Bi, sol['root'], τ, t = t)

    def steadyStatePol(self, policyFunction, t = None):
        def fixedPoint(τ):
            steadyState = self.steadyStateScalar(τ, t = t)
            return τ-np.clip(policyFunction(steadyState['s']), self.db['τ_l'], self.db['τ_u'])
        sol = optimize.root_scalar(fixedPoint, bracket = (self.db['τ_l'], self.db['τ_u']))
        assert sol['converged'], f""" Couldn't identify steady state fixed point - consider grid implementation """
        return self.steadyStateScalar(sol['root'], t = t)

    # Economic equilibrium
    def solveEE(self, τ, s0 = None, update = True, **kwargs):
        """ Solve for economic equilibrium given τ """
        τ = np.clip(τ, self.db['τ_l'], self.db['τ_u']) # clip that
        if s0 is None:
            s0 = self.steadyStateScalar(τ[0], t = self.db['t'][0])['s']
        τp = self.leadSym(τ)
        sol = optimize.root(lambda x: self.EE_objective(x, τ, τp, s0), self.x0['EE'])
        assert self.checkOpt(sol), f""" Could not identify economic equilibrium."""
        if update:
            self.x0['EE'] = sol['x']
        d = self.ns['EE'].unloadSol(sol['x'])
        return self.EE_report(τ, d['s'].values, d['h'].values, s0)

    def EE_objective(self, x, τ, τp, s0):
        """ Γs, s are defined over txE. h defined over t. """
        Γs, h, s, = self(x, 'Γs', ns = 'EE'), self(x, 'h', ns = 'EE'), self(x, 's', ns = 'EE')
        s_ = np.insert(s, 0, s0)
        Θh = self.BT.FH_Θh(τ = τ, τp = τp, Γs = Γs)
        return np.hstack([self.BT.FH_h(Θh = Θh, s_ = s_)-h,
                          self.BT.FH_sFromH(h = h, Γs = Γs)-s,
                          self.BT.FH_Γs(s = s, h = h, τp = τp)-Γs])

    def EE_report(self, τ, s, h, s0):
        sol = {'τ': τ, 'τ[t+1]': self.leadSym(τ), 
               's': s, 's[t-1]': np.insert(s, 0, s0), 
               'h': h}
        sol['Γs'] = self.BT.FH_Γs(s = sol['s'], h = sol['h'], τp = sol['τ[t+1]'])
        sol['Θh'] = self.BT.FH_Θh(τ = sol['τ'], τp = sol['τ[t+1]'], Γs = sol['Γs'])
        sol['Θs'] = self.BT.FH_Θs(Θh = sol['Θh'], Γs = sol['Γs'])
        [sol.__setitem__(k, pd.Series(sol[k], index = self.db['t'])) for k in ('τ','τ[t+1]','Θh','s[t-1]','h')];
        [sol.__setitem__(k, pd.Series(sol[k], index = self.db['txE'])) for k in ('Γs','Θs','s')];
        return sol

    # PEE METHODS
    def solveEEPol(self, sols, s0 = None, **kwargs):
        """ Solve for EE with sols containing dictionary with policy functions """
        if s0 is None:
            t0 = self.db['t'][0]
            s0 = _find_root_1d(sols[t0]['s[t-1]'], sols[t0]['s']-sols[t0]['s[t-1]'])[0] # fixed point s0 in first period
            # s0 = self.steadyStatePol(sols[t]['τPolicy'], t = t)['s'] # alternative - solves fixed point problem with policy function assuming steady state
        ### Approximate solution:
        τ, states, h = self.POL.approximatePEE(sols, {'s_': s0})
        return self.EE_report(τ.values, states['s_'].values[1:], h.values, s0)

    