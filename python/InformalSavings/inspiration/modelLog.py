import numpy as np, pandas as pd
from scipy import optimize
from baseLog import BaseLog, BaseLog_Grid, BaseLog_Time
from pyDbs import SymMaps as sm
from auxFunctions import noneInit, defaultGrid
from modelLogA import ModelLogA
from policyLog import Log

class ModelLog(ModelLogA):
    # Override base classes
    _BaseClass = BaseLog
    _BaseGridClass = BaseLog_Grid
    _BaseTimeClass = BaseLog_Time
    _PolicyClass = Log

    # New convenience function
    def solvePEE(self, kwargsPOL = None, **kwargs):
        policy = self.POL(**noneInit(kwargsPOL, {}))
        return self.solveEEPol(policy, **kwargs), policy

    # New grids:
    def initGrids(self, **kwargs):
        dsol = self._solGridSettings
        self.solGrids = {'τ': defaultGrid('τ', dsol), 's0/s': np.linspace(dsol['s0/s_l'], dsol['s0/s_u'], dsol['s0/s_n'])}
        dstate = self._stateGridSettings | kwargs
        self.stateGrids = {'τ': np.linspace(dstate['τ_l'], dstate['τ_u'], dstate['τ_n']), 
                           's0/s[t-1]': np.linspace(dstate['s0/s[t-1]_l'],dstate['s0/s[t-1]_u'],dstate['s0/s[t-1]_n'])}
        self.db.update(dsol)

    @property
    def _solGridSettings(self):
        return {'kτ_l': 1e2, 'kτ_u': 1e2, 'τ_n': 101, 'τ_l': 1e-4, 'τ_u': 1-1e-4,
                's0/s_n': 101, 's0/s_l': 0, 's0/s_u': .75}
    @property
    def _stateGridSettings(self):
        return {'kτ_l': 1e2, 'kτ_u': 1e2, 'τ_n': 101, 'τ_l': 1e-4, 'τ_u': 1-1e-4,
                's0/s[t-1]_n': 101, 's0/s[t-1]_l': 0, 's0/s[t-1]_u': .75}

    ### STEADY STATE METHODS:
    def steadyState_report(self, *args, t = None, **kwargs):
        d = super().steadyState_report(*args, **kwargs)
        d['s0/s'] = self.BG.s0_s(B0 = self.BG.get('β0',t), Θs = d['Θs'], τp = d['τ'], t = t)
        return d

    def steadyStatePol(self, policyFunction, t = None):
        def fixedPoint(τ):
            steadyState = self.steadyStateScalar(τ, t = t)
            return τ-np.clip(policyFunction(steadyState['s0/s']), self.db['τ_l'], self.db['τ_u'])
        sol = optimize.root_scalar(fixedPoint, bracket = (1e-7, 1-1e-7))
        assert sol['converged'], f""" Couldn't identify steady state fixed point - consider grid implementation """
        return self.steadyStateScalar(sol['root'], t = t)

    ### ECONOMIC EQUILIBRIUM
    def solveEE(self, τ, s0 = None, s0_s = None, **kwargs):
        """ EE given τ vector """
        sol = super().solveEE(τ, s0 = s0)
        sol['s0/s'] = self.BT.FH_s0_s(Θs = sol['Θs'], τp = sol['τ[t+1]'])
        sol['s0/s[t-1]'] = np.insert(sol['s0/s'], 0, s0_s)
        [sol.__setitem__(k, pd.Series(sol[k], index = self.db['t'])) for k in ['s0/s[t-1]']];
        [sol.__setitem__(k, pd.Series(sol[k], index = self.db['txE'])) for k in ['s0/s']];
        return sol

    # PEE METHODS
    def solveEEPol(self, sols, s0 = None, s0_s = None, **kwargs):
        """ Solve for EE with sols containing dictionary with policy functions """
        if s0_s is None:
            t = self.db['t'][0]
            steadyState = self.steadyStatePol(sols[t]['τPolicy'], t = t)
            s0, s0_s = steadyState['s'], steadyState['s0/s'] # get steady state values of the states.
        ### Approximate solution:
        τ, states = self.POL.approximatePEE(sols, {'s0_s_': s0_s})
        return self.solveEE(τ.values, s0 = s0, s0_s = s0_s)

    ###  Reporting
    def reportAll(self, path):
        path['Bi'] = pd.DataFrame(self.BT.Bi(s_ = path['s[t-1]'].values, h = path['h'].values), index = self.db['t'], columns = self.db['i'])
        path['B0'] = pd.Series(self.BT.B0(s_ = path['s[t-1]'].values, h = path['h'].values), index = self.db['t'])
        path['R']  = pd.Series(self.BT.R(s_ = path['s[t-1]'].values, h = path['h'].values), index = self.db['t'])
        path['Γs[t-1]'] = pd.Series(np.insert(path['Γs'].values, 0, self.B.Γs(Bi = path['Bi'].values[0], τp = path['τ'].values[0], t = self.db['t'][0])), index = self.db['t'])
        path['si/s[t-1]'] = pd.DataFrame(self.BT.si_s(Bi = path['Bi'].values, Γs = path['Γs[t-1]'].values, τp = path['τ'].values), index = self.db['t'], columns = self.db['i'])
        self.reportCoefficients(path)
        self.reportLevels(path)
        self.reportUtils(path)
        return path

    def reportCoefficients(self, path):
        """ Return dictionary of solution"""
        [path.__setitem__(k, getattr(self.BT, f'FH_{k}')(path)) for k in ('Θhi','Θc̃1i','Θc2i', 'Θc2pi', 'Θc̃10','Θc20','Θc2p0')];
        return path
    def reportLevels(self, path):
        """ Assumes self.reportCoefficients has been run"""
        [path.__setitem__(k, getattr(self.BT, f'FH_{k}')(path)) for k in ('hi_h','c̃1i','c2i','c2pi','c̃10','c20','c2p0','sRate')];
    def reportUtils(self, path):
        """ Assumes self.reportLevels has been run - not yet implemented here ... """
        pass
