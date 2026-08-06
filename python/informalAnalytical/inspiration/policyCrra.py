import numpy as np, pandas as pd
from scipy import interpolate
from auxFunctions import SolveGrid, refineGrid, noneInit, CustomLinInterp
import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)

from policyLog import Log

class CrraA(Log):
    """ 
    Identify Sequence of Policy Functions. CRRA model with H2M
    informal households. The only relevant state variable is 
    aggregate savings s[t-1].
    """

    ### GRIDSETTING METHODS:
    def initGS(self):
        """
        'stateApprox_i': Identifies (s)(τ, s_) where s_ is a scalar (not a full state grid). 'PEE_i': Identify τ(s_) for this one gridpoint.
        'stateApprox': Identify (s)(τ,s_) where s_ is a full grid. 'PEE': Then, identify τ(s_) on grid. 
        """
        self.GS, solGrids, stateGrids = {}, self._solGrids, self._stateGrids
        # PEE states: 
        for x in ('PEE','PEE_i'):
            self.GS[x] = SolveGrid(F = None, solGrids = solGrids[x], stateGrids = stateGrids[x], fallback_to_nn=True)
            self.GS[x]._globalSolGrids = self.GS[x].solGrids.copy() # Use this to relaunch global grid search
            self.GS[x].fInterp = self.fInterp # specify preferred interpolator
            self.GS[x].kwargsInterp = {}
        for x in ('stateApprox','stateApprox_i'):
            self.GS[x] = SolveGrid(F = None, solGrids = solGrids[x], stateGrids = stateGrids[x], fallback_to_nn=False)
            self.GS[x].fInterp = self.fInterp # specify preferred interpolator
            self.GS[x].kwargsInterp = {}
        self.GS['stateApprox'].fInterpND = self.fInterpND
        self.GS['stateApprox'].kwargsInterpND = {'method': 'linear', 'bounds_error': False, 'fill_value': None}

    @property
    def _solGrids(self):
        return {'stateApprox':   {'s': self.m.solGrids['s']}, 'PEE':   {'τ': self.m.solGrids['τ']},
                'stateApprox_i': {'s': self.m.solGrids['s']}, 'PEE_i': {'τ': self.m.solGrids['τ']}}

    @property
    def _stateGrids(self):
        return {'stateApprox': {'τ': self.m.stateGrids['τ'], 's_': self.m.stateGrids['s[t-1]']},
                'stateApprox_i': {'τ': self.m.stateGrids['τ']},
                'PEE': {'s_': self.m.stateGrids['s[t-1]']},
                'PEE_i': None}

    ### Highlevel methods:
    def __call__(self, style = None, **kwargs):
        return self.solveGSLoop_i(**kwargs) # only one implementation for this class

    def approximatePEE(self, sols, states0):
        """ Solve for both τ, states, and labor supply. states0 = dict of initial level of variables. """ 
        τ, states = super().approximatePEE(sols, states0)
        h = pd.Series([sols[t]['hPolicy'](states.loc[t,:].values)[0] for t in sols], index = self.db['t'])
        return τ, states, h

    ### SOLVE STYLE GSLoop_t - loop through t, cartesian grid of states.
    def report_t(self, τ, s_, fStateApprox, solp):
        s = fStateApprox(np.column_stack([τ, s_]))
        τp = solp['τPolicy'](s)
        hp = solp['hPolicy'](s)
        sol = self.funcOfτ_i(τ, s, τp, hp, s_)
        sol['τPolicy'] = self._policyFunction1D(sol['τ'], sol['s[t-1]'], self.GS['PEE'])
        sol['hPolicy'] = self._policyFunction1D(sol['h'], sol['s[t-1]'], self.GS['PEE'])
        sol['statePolicy'] = lambda x, states, **kwargs: fStateApprox(np.concatenate([[x], states]))
        return sol

    def solveStateApprox(self, solp):
        """ Grid of s_, solp dict. Return policy function s(s[t-1], τ). """
        def Fobj(s = None, states = None):
            τp = solp['τPolicy'](s)
            hp = solp['hPolicy'](s)
            sol = self.funcOfStates_i(states['τ'], s, τp, hp)
            return self.BG.st_fromLevels(Θs = sol['Θs'], s_ = states['s_'])-s
        self.GS['stateApprox'].update(F = Fobj)
        result = self.GS['stateApprox'].solve()
        fGrid = pd.Series(result['x'], index = self.GS['stateApprox'].global_stateIdx).unstack('τ')
        solved_mask = (~fGrid.isna()).sum(axis=1) > 1 # demand at least two feasible solutions
        return self._policyFunctionND(result['x'], self.GS['stateApprox']), solved_mask

    def _smooth1D(self, x, y):
        """ Minimial smoothing out of gridded solutions """
        sorted_indices = np.argsort(x)
        return interpolate.UnivariateSpline(x[sorted_indices], y[sorted_indices], s = 1e-5, k =3)(x)

    ### SOLVE STYLE GSLoop_ti - loop through t, loop through i when solving on grid of states:
    def solveGSLoop_i(self, **kwargs):
        sols = dict.fromkeys(self.db['t'])
        t = self.db['t'][-1]
        self.BG.t, self.B.t = t, t
        sols[t] = self.solveGSLoop_T(**kwargs)
        for t in self.db['t'][-2::-1]:
            self.BG.t, self.B.t = t, t
            sols[t] = self.solveGSLoop_ti(sols[t+1], **kwargs)
        return sols

    def solveGSLoop_ti(self, solp):
        # Approximate endogenous state functions:
        fStateApprox, solved_mask = self.solveStateApprox(solp)
        # Set up solution structures - only solutions available for solved_mask:
        s_ = solved_mask.index[solved_mask].values
        τ = np.empty(len(s_), dtype = float)
        for i, state_vals in enumerate(s_):
            τ[i] = self.GSLoop_i(state_vals, fStateApprox, solp)
        solved_mask = ~np.isnan(τ)
        τ, s_ = τ[solved_mask], s_[solved_mask]
        τ = self._smooth1D(s_, τ)
        return self.report_t(τ, s_, fStateApprox, solp)

    # Solve for scalar s_:
    def GSLoop_i(self, s_, fStateApprox, solp, **kwargs):
        def fStateApprox_i(τ):
            return fStateApprox(np.column_stack([τ, np.full(len(τ), s_)]))
        self._updateFeasiblePEE_i(fStateApprox_i)
        def Fobj(τ = None):
            s = fStateApprox_i(τ)
            τp = solp['τPolicy'](s)
            hp = solp['hPolicy'](s)
            sol = self.funcOfτ_i(τ, s, τp, hp, s_)
            sol = self.getGriddedGradients_i(sol)
            return self.objectiveGrid_t(sol)
        self.GS['PEE_i'].update(F = Fobj)
        result = self.GS['PEE_i'].solve()
        return result['x']

    def _updateFeasiblePEE_i(self, fStateApprox):
        τ, state = self.GS['PEE_i']._globalSolGrids['τ'], self.GS['PEE'].stateGrids['s_'] # full grids
        statePredicted = fStateApprox(τ) # predicted state on full solution grid
        mask = (statePredicted > min(state)) & (statePredicted < max(state))
        # padded = np.pad(mask, (1,1), mode = 'constant', constant_values= False)
        # mask_extended = mask | padded[:-2] | padded[2:]
        mask_extended = mask # keep values just outside domain? Not a good idea with s, which can become negative in this case...
        self.GS['PEE_i'].update(solGrids = {'τ': τ[mask_extended]})

    def objectiveGrid_t(self, sol):
        return self.BG.PEE_t(τBound = sol['τ'], τ  = sol['τ_unbounded'], s_ = sol['s[t-1]'], h = sol['h'], si_s = sol['si/s'], Θh = sol['Θh'], 
                    dlnh_Dτ = sol['dln(h)/dτ'], ĉ1i = sol['ĉ1i'], dlnĉ1i_dτ = sol['dln(ĉ1i)/dτ'], c̃2p0 = sol['c̃20[t+1]'], dlnc̃2p0_dτ = sol['dln(c̃20[t+1])/dτ'])

    def funcOfτ_i(self, τ, s, τp, hp, s_):
        sol = self.funcOfStates_i(τ, s, τp, hp)
        sol['s[t-1]'] = s_
        sol['h'] = self.BG.h_t(s_ = sol['s[t-1]'], Θh = sol['Θh'])
        sol['R'] = self.BG.R(s_ = sol['s[t-1]'], h = sol['h'])
        sol['Bi']= self.BG.Bi(s_ = sol['s[t-1]'], h = sol['h'])
        sol['Γs']= self.BG.Γs(Bi = sol['Bi'], τp = sol['τ'])
        sol['si/s'] = self.BG.si_s(Bi = sol['Bi'], Γs = sol['Γs'], τp = sol['τ'])
        sol['ĉ1i']  = self.BG.ĉ1i_t(τp = sol['τ[t+1]'], h = sol['h'], Bip = sol['Bi[t+1]'], Γs = sol['Γs[t+1]'])
        sol['c̃20[t+1]'] = self.BG.c̃2p0_fromLevels(τp = sol['τ[t+1]'], hp = sol['h[t+1]'], s = sol['s'])
        return sol

    def funcOfStates_i(self, τ, s, τp, hp):
        sol = {'τ_unbounded': τ, 'τ': np.clip(τ, self.db['τ_l'], self.db['τ_u']),
                            'τ[t+1]': np.clip(τp, self.db['τ_l'], self.db['τ_u']),
               's'  : s, 'h[t+1]': hp}
        sol['R[t+1]'] = self.BG.R(s_ = sol['s'], h = sol['h[t+1]'], t = self.BG.t+1)
        sol['Bi[t+1]'] = self.BG.Bi(s_ = sol['s'], h = sol['h[t+1]'], t = self.BG.t+1)
        sol['Γs[t+1]'] = self.BG.Γs(Bi = sol['Bi[t+1]'], τp = sol['τ[t+1]'])
        sol['Θh'] = self.BG.Θh_t(τ = sol['τ'], τp = sol['τ[t+1]'], Γs = sol['Γs[t+1]'])
        sol['Θs'] = self.BG.Θs_t(Θh = sol['Θh'], Γs=sol['Γs[t+1]'])
        return sol

    def getGriddedGradients_i(self, sol):
        _x = sol['τ']
        sol['dln(h)/dτ'] = self._griddedGradient1D(np.log(sol['Θh']), _x)
        sol['dln(ĉ1i)/dτ'] = self._griddedGradient2D(np.log(sol['ĉ1i']), _x)
        sol['dln(c̃20[t+1])/dτ'] = self._griddedGradient1D(np.log(sol['c̃20[t+1]']), _x)
        return sol

    ### Terminal state - ALWAYS THE SAME SOLVE
    def solveGSLoop_T(self, **kwargs):
        def Fobj(τ = None, states = None):
            return self.objectiveGrid_T(τ = τ, s_ = states['s_'])
        self.GS['PEE'].update(F = Fobj, solGrids = self.GS['PEE']._globalSolGrids)
        result = self.GS['PEE'].solve()
        return self.report_T(result['x'])

    def funcOfτGrid_T(self, τ, s_):
        sol = {'τ_unbounded': τ, 'τ': np.clip(τ, self.db['τ_l'], self.db['τ_u']),
               's[t-1]'  : s_}
        sol['dln(h)/dτ'] = self.BG.dlnh_dτ(sol['τ'])
        sol['Θh'] = self.BG.Θh_T(τ = sol['τ'])
        sol['h']  = self.BG.h_T(s_ = sol['s[t-1]'], τ = sol['τ'])
        sol['Bi'] = self.BG.Bi(s_ = sol['s[t-1]'], h = sol['h'])
        sol['Γs'] = self.BG.Γs(Bi = sol['Bi'], τp = sol['τ'])
        sol['si/s'] = self.BG.si_s(Bi = sol['Bi'], Γs = sol['Γs'], τp = sol['τ'])
        return sol

    def objectiveGrid_T(self, τ=None, s_ = None):
        sol = self.funcOfτGrid_T(τ, s_)
        return self.BG.PEE_T(τBound = sol['τ'], τ = sol['τ_unbounded'], dlnh_Dτ = sol['dln(h)/dτ'], si_s = sol['si/s'], Θh = sol['Θh'], 
                             s_ = sol['s[t-1]'], h = sol['h'])


    def report_T(self, τ):
        solved_mask = ~np.isnan(τ)
        τ, s_ = τ[solved_mask], self.GS['PEE'].global_stateIdx.to_numpy()[solved_mask]
        sol = self.funcOfτGrid_T(τ, s_)
        sol['τPolicy'] = self._policyFunction1D(sol['τ'], sol['s[t-1]'], self.GS['PEE'])
        sol['hPolicy'] = self._policyFunction1D(sol['h'], sol['s[t-1]'], self.GS['PEE'])
        return sol

    def _policyFunctionND(self, y, GS):
        return GS.fInterpND(GS.stateGrids.values(), y.reshape(GS.state_shape), **GS.kwargsInterpND)

class CrraUSA(CrraA):
    """ 
    Identify Sequence of Policy Functions. Analytical, CRRA model.
    No informal households. Adjusts elements related to informal households,
    otherwise identical to CrraA class.
    """

    def objectiveGrid_t(self, sol):
        """ Removed references to type 0 elements in sol """
        return self.BG.PEE_t(τBound = sol['τ'], τ  = sol['τ_unbounded'], s_ = sol['s[t-1]'], h = sol['h'], si_s = sol['si/s'], Θh = sol['Θh'], 
                    dlnh_Dτ = sol['dln(h)/dτ'], ĉ1i = sol['ĉ1i'], dlnĉ1i_dτ = sol['dln(ĉ1i)/dτ'])

    def funcOfτ_i(self, τ, s, τp, hp, s_):
        """ Commented out the change compared to parent class"""
        sol = self.funcOfStates_i(τ, s, τp, hp)
        sol['s[t-1]'] = s_
        sol['h'] = self.BG.h_t(s_ = sol['s[t-1]'], Θh = sol['Θh'])
        sol['R'] = self.BG.R(s_ = sol['s[t-1]'], h = sol['h'])
        sol['Bi']= self.BG.Bi(s_ = sol['s[t-1]'], h = sol['h'])
        sol['Γs']= self.BG.Γs(Bi = sol['Bi'], τp = sol['τ'])
        sol['si/s'] = self.BG.si_s(Bi = sol['Bi'], Γs = sol['Γs'], τp = sol['τ'])
        sol['ĉ1i']  = self.BG.ĉ1i_t(τp = sol['τ[t+1]'], h = sol['h'], Bip = sol['Bi[t+1]'], Γs = sol['Γs[t+1]'])
        # sol['c̃20[t+1]'] = self.BG.c̃2p0_fromLevels(τp = sol['τ[t+1]'], hp = sol['h[t+1]'], s = sol['s'])
        return sol

    def getGriddedGradients_i(self, sol):
        """ Commented out the change compared to parent class"""
        _x = sol['τ']
        sol['dln(h)/dτ'] = self._griddedGradient1D(np.log(sol['Θh']), _x)
        sol['dln(ĉ1i)/dτ'] = self._griddedGradient2D(np.log(sol['ĉ1i']), _x)
        # sol['dln(c̃20[t+1])/dτ'] = self._griddedGradient1D(np.log(sol['c̃20[t+1]']), _x)
        return sol

class Crra(CrraA):

    ### Highlevel methods:
    def __call__(self, style = None, **kwargs):
        return self.solveGSLoop(**kwargs) # only one implementation for this class

    #######################################################################
    ##########              1. Structure                        ########### 
    #######################################################################

    def initGS(self):
        """ 
        'stateApprox': Identify economic equilibrium function (s, s0/s)(τ,s[t-1]). This becomes a rather big problem --> apply adaptive gridsearch.
        'PEE': Given economic  equilibrium function, identify τ(s[t-1], s0/s[t-1]).  
        """
        self.GS, solGrids, stateGrids = {}, self._solGrids, self._stateGrids
        # State approximation:
        self.GS['stateApprox'] = SolveGrid(
                F = None, 
                solGrids = solGrids['stateApprox'], 
                stateGrids = stateGrids['stateApprox'], 
                ΔL = {('s', 'τ'): 5, ('s', 's_'): 4, ('s0_s', 'τ'): 2, ('s0_s', 's_'): 5},
                ΔU = {('s', 'τ'): 2, ('s', 's_'): 4, ('s0_s', 'τ'): 5, ('s0_s', 's_'): 5}, 
                maxExpand = 0,
                fallback_to_nn = False
                )
        self.GS['stateApprox'].fInterp = self.fInterp
        self.GS['stateApprox'].fInterpND = self.fInterpND
        self.GS['stateApprox'].kwargsInterp = {}
        self.GS['stateApprox'].kwargsInterpND = {'method': 'linear', 'bounds_error': False, 'fill_value': None}

        # PEE:
        self.GS['PEE'] = SolveGrid(F = None, solGrids = solGrids['PEE'], stateGrids = stateGrids['PEE'], fallback_to_nn=False)
        self.GS['PEE']._globalSolGrids = self.GS['PEE'].solGrids.copy()
        self.GS['PEE']._globalStateGrids = self.GS['PEE'].stateGrids.copy() 
        self.GS['PEE'].fInterp = self.fInterp
        self.GS['PEE'].fInterpND = self.fInterpND
        self.GS['PEE'].kwargsInterp = {}
        self.GS['PEE'].kwargsInterpND = {'method': 'linear', 'bounds_error': False, 'fill_value': None}

    @property
    def _solGrids(self):
        return {'stateApprox':   {'s': self.m.solGrids['s'], 's0_s': self.m.solGrids['s0/s']}, 
                'PEE':   {'τ': self.m.solGrids['τ']}}

    @property
    def _stateGrids(self):
        return {'stateApprox': {'τ': self.m.stateGrids['τ'], 's_': self.m.stateGrids['s[t-1]']},
                'PEE': {'s_': self.m.stateGrids['s[t-1]'], 's0_s_': self.m.stateGrids['s0/s[t-1]']}}
    
    #######################################################################
    ##########              2. Solve t<T                        ########### 
    #######################################################################
    def solveGSLoop(self, **kwargs):
        sols = dict.fromkeys(self.db['t'])
        t = self.db['t'][-1]
        self.BG.t, self.B.t = t, t
        sols[t] = self.solveGSLoop_T(**kwargs)
        for t in self.db['t'][-2::-1]:
            self.BG.t, self.B.t = t, t
            sols[t] = self.solveGSLoop_t(sols[t+1], **kwargs)
        return sols

    def solveGSLoop_t(self, solp):
        """
        Identification of the policy function in t occurs in several steps:
        1.  Create approximation of endogenous states in current year. 
            Returns a dictionary with states as function of current choices
            and past states. In this case, we get functions s[t](τ[t], s[t-1])
            and s0/s[t](τ[t], s[t-1]). 
        2.  Define subset of global grids that return feasible PEE solutions.
            This is done by approximating states on global grids of τ and pre-
            determined states and evaluating if they fall outside state domains.
        3.  Solve for τ by (i) computing the political first order condition on 
            the grid of feasible PEE. (ii) simply input nan for infeasible com-
            binations. Pass gridded objective to gridsearch class and identify.
        4.  Given PEE choices of τ on the grid of predetermined states t-1,
            store relevant blocks, including the state approximation functions. 

        The outcome is passed through the reporting function to create dictionary
        with solutions.                    
        """
        # Approximate endogenous state functions:
        fStateApprox, solved_mask_states = self.solveStateApprox_t(solp) 
        # If there are state values that we cannot solve for, remove them from states:
        if any((~solved_mask_states)):
            self.GS['PEE'].update(stateGrids = self.GS['PEE']._globalStateGrids.copy() | {'s_': solved_mask_states.index[solved_mask_states].to_numpy()})

        # Set up dictionary with vectors of solution variables + states:
        d = self.GS['PEE'].get_levels(idx = self.GS['PEE'].combined_gridsND) 
                 
        # Set up dictionary with approximated states in t, i.e. s[t] and s0/s[t]:
        states = {k: fStateApprox[k](np.column_stack([d['τ'], d['s_']])) for k in fStateApprox}
        # Only look at 'feasible' equilibria, i.e. where the approximate states fall within grid bounds:
        feasible_mask = np.column_stack([(states[k]>=min(self.GS['stateApprox'].solGrids[k])) & (states[k]<=max(self.GS['stateApprox'].solGrids[k])) for k in states]).all(axis=1)
        # Objective:
        def Fobj(**kwargs):
            obj = np.full(len(feasible_mask), np.nan)
            states_int = {k: states[k][feasible_mask] for k in states}
            states2D = np.column_stack([v for v in states_int.values()])
            d_int = {k: v[feasible_mask] for k,v in d.items()}
            τp = solp['τPolicy'](states2D)
            hp = solp['hPolicy'](states2D)
            sol = self.funcOfτ_i(τp = τp, hp = hp, **(d_int | states_int))
            sol = self.getGriddedGradients(sol, gridND = self.GS['PEE'].combined_gridsND[feasible_mask])
            obj[feasible_mask] = self.objectiveGrid_t(sol)
            return obj
        # Solve:
        self.GS['PEE'].update(F = Fobj)
        result = self.GS['PEE'].solve()

        # Only keep solutions where at least one state solves:
        z2D = result['x'].reshape(tuple(len(v) for v in self.GS['PEE'].stateGrids.values()))
        keepCols = ~np.isnan(z2D).all(axis=0)
        keepRows = ~np.isnan(z2D).all(axis=1)
        z2D = z2D[np.ix_(keepRows,keepCols)]
        self.GS['PEE'].update(stateGrids = {'s_': self.GS['PEE'].stateGrids['s_'][keepRows], 's0_s_': self.GS['PEE'].stateGrids['s0_s_'][keepCols]})
        
        # Smooth out small kinks (with robust fallback candidates for s):
        τ = self._smooth2D_robust(z2D.reshape(-1), self.GS['PEE'])
        states = self.GS['PEE'].get_levels() # states
        return self.report_t(τ = τ, fStateApprox = fStateApprox, solp = solp, **states)

    def report_t(self, τ = None, s_ = None, s0_s_ = None, fStateApprox = None, solp = None):
        states_t = {k: fStateApprox[k](np.column_stack([τ, s_])) for k in fStateApprox}
        states2D = np.column_stack([v for v in states_t.values()])
        τp = solp['τPolicy'](states2D)
        hp = solp['hPolicy'](states2D)
        sol = self.funcOfτ_i(τ = τ, τp = τp, hp = hp, s_ = s_, s0_s_ = s0_s_, **states_t)
        sol['τPolicy'] = self._policyFunctionND(sol['τ'], self.GS['PEE'])
        sol['hPolicy'] = self._policyFunctionND(sol['h'], self.GS['PEE'])
        # What states are actually used to access the state approximation:
        relevantStates_int = [self.GS['PEE'].state_names.index(k) for k in self.GS['PEE'].state_names if k in self.GS['stateApprox'].state_names] 
        sol['statePolicy'] = lambda x, states, **kwargs: np.column_stack([fStateApprox[k](np.concatenate([[x], states[...,relevantStates_int]]))
                                                                          for k in fStateApprox])
        return sol

    def funcOfτ_i(self, τ = None, s = None, s0_s = None, τp = None, hp = None, s_ = None, s0_s_ = None):
        sol = self.funcOfStates_i(τ, s, s0_s, τp, hp)
        sol['s[t-1]'] = s_
        sol['s0/s[t-1]'] = s0_s_
        sol['h'] = self.BG.h_t(s_ = sol['s[t-1]'], Θh = sol['Θh'])
        sol['R'] = self.BG.R(s_ = sol['s[t-1]'], h = sol['h'])
        sol['Bi']= self.BG.Bi(s_ = sol['s[t-1]'], h = sol['h'])
        sol['Γs']= self.BG.Γs(Bi = sol['Bi'], τp = sol['τ'])
        sol['si/s'] = self.BG.si_s(Bi = sol['Bi'], Γs = sol['Γs'], τp = sol['τ'])
        sol['ĉ1i']  = self.BG.ĉ1i_t(τp = sol['τ[t+1]'], h = sol['h'], Bip = sol['Bi[t+1]'], Γs = sol['Γs[t+1]'])
        sol['ĉ10']  = self.BG.ĉ10_t(τp = sol['τ[t+1]'], s_ = sol['s[t-1]'], B0p = sol['B0[t+1]'], Θs = sol['Θs'])
        return sol

    def objectiveGrid_t(self, sol):
        return self.BG.PEE_t(τBound = sol['τ'], τ  = sol['τ_unbounded'], s_ = sol['s[t-1]'], h = sol['h'], si_s = sol['si/s'], s0_s = sol['s0/s[t-1]'],
                    dlnh_Dτ = sol['dln(h)/dτ'], ĉ1i = sol['ĉ1i'], dlnĉ1i_dτ = sol['dln(ĉ1i)/dτ'], ĉ10 = sol['ĉ10'], dlnĉ10_dτ = sol['dln(ĉ10)/dτ'])

    ### State approximation:
    def solveStateApprox_t(self, solp):
        """ Grid of s_, s0_s_, solp dict. Return policy functions s(s[t-1], τ) and s0/s(s[t-1], τ)"""
        result = self._solveStateApprox_t(solp)
        df = self.GS['stateApprox'].flatten_solution(result['x'], as_dataframe=True)
        # policies = {k: self._policyFunctionND(df[k].to_numpy(), self.GS['stateApprox']) for k in df.columns}
        policies = {k: self._policyFunction2Dclean(df[k], self.GS['stateApprox']) for k in df.columns}
        nSolved = df.dropna().iloc[:,0].groupby([k for k in df.index.names if k != 'τ']).count() #
        solved_mask = nSolved > 1
        return policies, solved_mask

    def _solveStateApprox_t(self, solp):
        def Fobj(s = None, s0_s = None, states = None):
            τp = solp['τPolicy'](np.column_stack([s, s0_s]))
            hp = solp['hPolicy'](np.column_stack([s, s0_s]))
            sol = self.funcOfStates_i(states['τ'], s, s0_s, τp, hp)
            return np.column_stack([self.BG.st_fromLevels(Θs = sol['Θs'], s_ = states['s_'])-s, 
                                    self.BG.s0_s(B0 = sol['B0[t+1]'], Θs = sol['Θs'], τp = sol['τ[t+1]'])-s0_s])
        self.GS['stateApprox'].update(F = Fobj)
        return self.GS['stateApprox'].solve()
   
    def funcOfStates_i(self, τ, s, s0_s, τp, hp):
        sol = super().funcOfStates_i(τ, s, τp, hp)
        sol['s0/s'] = s0_s
        sol['B0[t+1]'] = self.BG.B0(s_ = sol['s'], h = sol['h[t+1]'], t = self.BG.t+1)
        return sol

    ### Auxiliary methods:   
    def _estimateRefinement_stateApprox(self, result, **kwargs):
        """ Estimate ΔL, ΔU for searching over the grids when identifying stateApprox """
        return self.GS['stateApprox'].estimate_refinement_from_full_solution(result['x'], **kwargs)

    def _smooth2D(self, f, GS, s = 1e-5, nan_threshold = 0.4):
        x, y = tuple(GS.stateGrids.values())
        z2D = f.reshape(len(x), len(y))

        state_vals = GS.get_levels()
        state_arrays = tuple(state_vals.values())
        state_points = GS.get_levels_stacked()

        nan_mask = np.isnan(z2D)
        n_nan = nan_mask.sum()
        if n_nan == 0:
            spline = interpolate.RectBivariateSpline(x, y, z2D, s=s, kx=3, ky=3)
            return spline.ev(*state_arrays)

        elif n_nan / len(f) < nan_threshold:
            # Fill NaNs on the full grid, then fit spline on the full grid.
            z_filled = self._fillNaN2D(z2D, x, y)
            spline = interpolate.RectBivariateSpline(x, y, z_filled, s=s, kx=3, ky=3)
            return spline.ev(*state_arrays)

        else:
            solved_mask = ~np.isnan(f)
            z_solved = f[solved_mask]
            state_points_solved = state_points[solved_mask]
            rbf = interpolate.RBFInterpolator(
                state_points_solved,
                z_solved,
                kernel = 'thin_plate_spline',
                smoothing = s,
                degree = 1
            )
            return rbf(state_points)

    def _smooth2D_eval(self, f, GS, s, nan_threshold = 0.4, maxIter = 3):
        """Smooth with given s and return (smoothed_array, maxdist, rmse) on observed points."""
        x, y = tuple(GS.stateGrids.values())
        z2D = f.reshape(len(x), len(y))
        obs = ~np.isnan(z2D)
        for i in range(maxIter):
            try:
                smooth = self._smooth2D(f, GS, s = s, nan_threshold = nan_threshold)
                break
            except ValueError:
                s = s*10
        diff = smooth.reshape(len(x), len(y))[obs] - z2D[obs]
        return smooth, np.max(np.abs(diff)), np.sqrt(np.mean(diff ** 2))

    def _smooth2D_robust(self, f, GS, s_default = 1e-5, s_backups = (5e-4, 1e-3),
                        nan_threshold = 0.4, maxdist_tol = 0.05):
        """Apply 2D smoothing, falling back to backup candidates when default produces large errors."""
        smooth_def, maxdist_def, rmse_def = self._smooth2D_eval(f, GS, s_default, nan_threshold)
        if maxdist_def < maxdist_tol:
            return smooth_def

        # Default failed tolerance — evaluate backups
        results = {s_default: (smooth_def, maxdist_def, rmse_def)}
        for s in s_backups:
            results[s] = self._smooth2D_eval(f, GS, s, nan_threshold)

        has_nan = np.isnan(f).any()
        if not has_nan:
            # No NaN: pick candidate with lowest maxdist
            s_chosen = min(results, key = lambda s: results[s][1])
        else:
            # NaN case: prefer below-tolerance candidates with lowest RMSE
            below_tol = {s: r for s, r in results.items() if r[1] < maxdist_tol}
            if below_tol:
                s_chosen = min(below_tol, key = lambda s: below_tol[s][2])
            else:
                s_chosen = min(results, key = lambda s: results[s][1])

        return results[s_chosen][0]

    def _fillNaN2D(self, z_2d, x_grid, y_grid, n_extrap = 4, method = 'pchip'):
        """Fill NaNs using auto-calibrated mixing of row-first and column-first edge extrapolation."""
        z0 = np.asarray(z_2d, dtype = float)
        nan0 = np.isnan(z0)
        if not nan0.any():
            return z0.copy()

        def extrapolate_edge(grid_known, vals_known, grid_target):
            if len(vals_known) < 2:
                return None
            if method == 'pchip':
                try:
                    return interpolate.PchipInterpolator(grid_known, vals_known, extrapolate = True)(grid_target)
                except Exception:
                    pass
            coef = np.polyfit(grid_known, vals_known, 1)
            return np.polyval(coef, grid_target)

        def fill_once_axis(z_in, axis):
            z = z_in.copy()
            grid = y_grid if axis == 1 else x_grid
            n_outer = z.shape[0] if axis == 1 else z.shape[1]
            k_min = 2
            for idx in range(n_outer):
                line = z[idx, :] if axis == 1 else z[:, idx]
                nan_line = np.isnan(line)
                if not nan_line.any():
                    continue
                valid_idx = np.where(~nan_line)[0]
                if len(valid_idx) < 2:
                    continue
                k = min(max(k_min, n_extrap), len(valid_idx))
                miss_idx = np.where(nan_line)[0]

                left = miss_idx[miss_idx < valid_idx[0]]
                if len(left):
                    pred = extrapolate_edge(grid[valid_idx[:k]], line[valid_idx[:k]], grid[left])
                    if pred is not None:
                        if axis == 1:
                            z[idx, left] = pred
                        else:
                            z[left, idx] = pred

                right = miss_idx[miss_idx > valid_idx[-1]]
                if len(right):
                    pred = extrapolate_edge(grid[valid_idx[-k:]], line[valid_idx[-k:]], grid[right])
                    if pred is not None:
                        if axis == 1:
                            z[idx, right] = pred
                        else:
                            z[right, idx] = pred
            return z

        def blend(z_rc, z_cr, alpha):
            out = z0.copy()
            rc_ok, cr_ok = ~np.isnan(z_rc), ~np.isnan(z_cr)
            both = nan0 & rc_ok & cr_ok
            out[both] = alpha * z_rc[both] + (1 - alpha) * z_cr[both]
            out[nan0 & rc_ok & ~cr_ok] = z_rc[nan0 & rc_ok & ~cr_ok]
            out[nan0 & ~rc_ok & cr_ok] = z_cr[nan0 & ~rc_ok & cr_ok]
            return out

        def estimate_alpha(n_alpha = 21):
            obs = ~nan0
            adj = np.zeros_like(obs, dtype = bool)
            for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                src_i = slice(max(0, -di), z0.shape[0] - max(0, di))
                src_j = slice(max(0, -dj), z0.shape[1] - max(0, dj))
                dst_i = slice(max(0, di), z0.shape[0] - max(0, -di))
                dst_j = slice(max(0, dj), z0.shape[1] - max(0, -dj))
                adj[dst_i, dst_j] |= nan0[src_i, src_j]

            points = np.argwhere(obs & adj)
            if len(points) < 4:
                return 0.5

            sel = np.linspace(0, len(points) - 1, min(200, len(points)), dtype = int)
            pts = points[sel]
            rows, cols = pts[:, 0], pts[:, 1]

            z_masked = z0.copy()
            truth = z0[rows, cols]
            z_masked[rows, cols] = np.nan

            z_rc_cv = fill_once_axis(fill_once_axis(z_masked, axis = 1), axis = 0)
            z_cr_cv = fill_once_axis(fill_once_axis(z_masked, axis = 0), axis = 1)

            rc = z_rc_cv[rows, cols]
            cr = z_cr_cv[rows, cols]
            only_rc = np.isnan(cr) & ~np.isnan(rc)
            only_cr = np.isnan(rc) & ~np.isnan(cr)
            both = ~np.isnan(rc) & ~np.isnan(cr)

            best_alpha, best_rmse = 0.5, np.inf
            for alpha in np.linspace(0.0, 1.0, n_alpha):
                pred = np.full_like(truth, np.nan)
                pred[only_rc] = rc[only_rc]
                pred[only_cr] = cr[only_cr]
                pred[both] = alpha * rc[both] + (1 - alpha) * cr[both]
                ok = ~np.isnan(pred)
                if ok.any():
                    rmse = np.sqrt(np.mean((pred[ok] - truth[ok]) ** 2))
                    if rmse < best_rmse:
                        best_rmse, best_alpha = rmse, alpha
            return best_alpha

        z_rc = fill_once_axis(fill_once_axis(z0, axis = 1), axis = 0)
        z_cr = fill_once_axis(fill_once_axis(z0, axis = 0), axis = 1)
        return blend(z_rc, z_cr, estimate_alpha())

    def getGriddedGradients(self, sol, gridND = None):
        if gridND is None:
            _x = sol['τ']
            _method1D = self._griddedGradient1D
            _method2D = self._griddedGradient2D
        else:
            _x = gridND
            _method1D = self._griddedGradient1D_griddedIdx_dropnan
            _method2D = self._griddedGradient2D_griddedIdx_dropnan
        sol['dln(h)/dτ'] = _method1D(np.log(sol['Θh']), _x)
        sol['dln(ĉ1i)/dτ'] = _method2D(np.log(sol['ĉ1i']), _x)
        sol['dln(ĉ10)/dτ'] = _method1D(np.log(sol['ĉ10']), _x)
        return sol

    #######################################################################
    ##########              3. Solve terminal T                 ########### 
    #######################################################################

    def solveGSLoop_T(self, **kwargs):
        def Fobj(τ = None, states = None):
            return self.objectiveGrid_T(τ = τ, s_ = states['s_'], s0_s_ = states['s0_s_'])
        self.GS['PEE'].update(F = Fobj, solGrids = self.GS['PEE']._globalSolGrids)
        result = self.GS['PEE'].solve()
        return self.report_T(result['x'])

    def funcOfτGrid_T(self, τ, s_, s0_s_):
        sol = {'τ_unbounded': τ, 'τ': np.clip(τ, self.db['τ_l'], self.db['τ_u']),
               's[t-1]'  : s_,
               's0/s[t-1]': s0_s_}
        sol['dln(h)/dτ'] = self.BG.dlnh_dτ(sol['τ'])
        sol['h']  = self.BG.h_T(s_ = sol['s[t-1]'], τ = sol['τ'])
        sol['Bi'] = self.BG.Bi(s_ = sol['s[t-1]'], h = sol['h'])
        sol['Γs'] = self.BG.Γs(Bi = sol['Bi'], τp = sol['τ'])
        sol['si/s'] = self.BG.si_s(Bi = sol['Bi'], Γs = sol['Γs'], τp = sol['τ'])
        return sol

    def objectiveGrid_T(self, τ=None, s_ = None, s0_s_ = None):
        sol = self.funcOfτGrid_T(τ, s_, s0_s_)
        return self.BG.PEE_T(τBound = sol['τ'], τ = sol['τ_unbounded'], dlnh_Dτ = sol['dln(h)/dτ'], si_s = sol['si/s'], s_ = sol['s[t-1]'], h = sol['h'], s0_s = sol['s0/s[t-1]'])

    def report_T(self, τ):
        solved_mask = ~np.isnan(τ)
        τ = τ[solved_mask]
        _s_vals = self.GS['PEE'].get_levels()
        s_ = _s_vals['s_'][solved_mask]
        s0_s_ = _s_vals['s0_s_'][solved_mask]
        sol = self.funcOfτGrid_T(τ, s_, s0_s_)
        sol['τPolicy'] = self._policyFunctionND(sol['τ'], self.GS['PEE'])
        sol['hPolicy'] = self._policyFunctionND(sol['h'], self.GS['PEE'])
        return sol

    def _policyFunction2Dclean(self, s, GS):
        """ start by removing columns/rows entirely with nan, then fill in NaN values using extrapolation techniques,
         then return interpolation function on the clean grid. """
        df = s.dropna().unstack()
        z2D, x, y = df.values, df.index.to_numpy(), df.columns.to_numpy()
        z2D = self._fillNaN2D(z2D, x, y)
        return GS.fInterpND((x,y), z2D, **GS.kwargsInterpND)