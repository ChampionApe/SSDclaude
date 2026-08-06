import numpy as np, pandas as pd
from scipy import optimize, interpolate
from auxFunctions import SolveGrid, refineGrid, noneInit, CustomLinInterp
import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)


class LogA: 
    """ 
    Identify Sequence of Policy Functions. Analytical, LOG model.
    
    The analytical LOG model does not involve identifying policy
    functions when pension characteristics (θ,ϵ) are fixed. In
    this case, the class returns the solution instead.
    """
    def __init__(self, m, style = 'Vector', **kwargs):
        self.m = m
        self.B  = m.B
        self.BG = m.BG
        self.BT = m.BT
        self.db = m.db
        # self.fInterp = interpolate.PchipInterpolator
        self.fInterp = CustomLinInterp
        self.fInterpND = interpolate.RegularGridInterpolator
        self.style = style
        self.x0 = self._x0 # passed to newton solver
        self.kwargs = self._kwargs | kwargs # passed to newton solver
        self.initGS() # initialize gridsearch class

    def adjust_t0(self, t0, namespace):
        """ 
        Update relevant structures from a new baseline year t0.
        Assumes that self.m and base classes are updated through
        self.m. namespace is the original namespace before slicing t0
        """
        self.x0 = self.x0[t0:] 

    def initGS(self):
        """
        One solve instance (structure is the same across solve states and years).
        Use self.settingsSG0 to refine grids when looping through time (creating solGrid0)
        Use self.settingsRG to refine grids (only required when solving via loops)
        """
        self.GS = SolveGrid(F = None, solGrids = self._solGrids, stateGrids = self._stateGrids, maxExpand = 5)
        self.settingsSG0 = self._settingsSG0
        # self.settingsRG  = self._settingsRG

    def get_solGrid0(self, solp = None):
        if self.BG.t == self.db['t'][-1]:
            return None
        elif self.BG.t == self.db['t'][-2]:
            return {k: refineGrid(self.GS.solGrids[k], solp[f'{k}_unbounded'], 
                                    self.settingsSG0['T_']['ΔL'][k], 
                                    self.settingsSG0['T_']['ΔU'][k]) for k in self.GS.solGrids}
        elif self.BG.t < self.db['t'][-2]:
            return {k: refineGrid(self.GS.solGrids[k], solp[f'{k}_unbounded'], 
                                    self.settingsSG0['t']['ΔL'][k], 
                                    self.settingsSG0['t']['ΔU'][k]) for k in self.GS.solGrids}


    @property
    def _settingsSG0(self):
        return {'T_': {'ΔL': {'τ': 25}, 'ΔU': {'τ': 1}},
                't' : {'ΔL': {'τ': 10}, 'ΔU': {'τ': 1}}}

    @property
    def _x0(self):
        return np.full(self.m.T, .2)
    @property
    def _kwargs(self):
        return {'update': True}
    @property
    def _solGrids(self):
        return {'τ': self.m.solGrids['τ']}
    @property
    def _stateGrids(self):
        return None

    def __call__(self, style = 'Vector', **kwargs):
        return getattr(self, f'solve{style}')(**(self.kwargs | kwargs))

    def solveRobust(self, update = True, **kwargs):
        try:
            return self.solveVector(update = update, **kwargs)
        except:
            return self.solveGSLoop(update = update, **kwargs)

    def solveGSLoop(self, update = True, **kwargs):
        sols = dict.fromkeys(self.db['t'])
        t = self.db['t'][-1]
        self.BG.t, self.B.t = t, t
        sols[t] = self.solveGSLoop_T(**kwargs)
        for t in self.db['t'][-2::-1]:
            self.BG.t, self.B.t = t, t
            sols[t] = self.solveGSLoop_t(sols[t+1], **kwargs)
        return self.report(self._extractSolGSLoop(sols), update = update)

    def _extractSolGSLoop(self, sols):
        return np.array([soli['τ_unbounded'] for soli in sols.values()])

    def solveGSLoop_t(self, solp, **kwargs):
        self.GS.update(F = lambda τ: self.objectiveGrid_t(τ, solp), solGrid0 = self.get_solGrid0(solp = solp))
        result = self.GS.solve()
        return self.report_t(result['x'][0])

    def solveGSLoop_T(self, **kwargs):
        self.GS.update(F = self.objectiveGrid_T, solGrid0 = self.get_solGrid0())
        result = self.GS.solve()
        return self.report_t(result['x'][0])

    def report_t(self, τ):
        sol = {'τ_unbounded': τ, 'τ':np.clip(τ, self.db['τ_l'], self.db['τ_u'])}
        sol['Γs'] = self.B.Γs(Bi = self.B.get('βi[t-1]'), τp = sol['τ'])
        return sol

    def objectiveGrid_T(self, τ):
        sol = self.funcOfτGrid_T(τ)
        return self.BG.PEE_T(τBound = sol['τ'], τ = sol['τ_unbounded'], si_s = sol['si/s'], Θh = sol['Θh'], dlnh_Dτ = sol['dln(h)/dτ'])

    def objectiveGrid_t(self, τ, solp):
        sol = self.funcOfτGrid_t(τ, solp)
        return self.BG.PEE_t(τBound = sol['τ'], τ = sol['τ_unbounded'], si_s = sol['si/s'], Θh = sol['Θh'], dlnh_Dτ = sol['dln(h)/dτ'])

    def funcOfτGrid_T(self, τ):
        sol = {'τ_unbounded': τ, 'τ': np.clip(τ, self.db['τ_l'], self.db['τ_u'])}
        sol['dln(h)/dτ'] = self.BG.dlnh_dτ(τ = sol['τ'])
        sol['Γs'] = self.BG.Γs(Bi = self.BG.get('βi[t-1]'), τp = sol['τ'])
        sol['Θh'] = self.BG.Θh_T(τ = sol['τ'])
        sol['si/s'] = self.BG.si_s(Bi = self.BG.get('βi[t-1]')[None,:], Γs = sol['Γs'], τp = sol['τ'])
        return sol

    def funcOfτGrid_t(self, τ, solp):
        sol = {'τ_unbounded': τ, 'τ': np.clip(τ, self.db['τ_l'], self.db['τ_u'])}
        sol['dln(h)/dτ'] = self.BG.dlnh_dτ(τ = sol['τ'])
        sol['Γs'] = self.BG.Γs(Bi = self.BG.get('βi[t-1]'), τp = sol['τ'])
        sol['Θh'] = self.BG.Θh_t(τ = sol['τ'], τp = solp['τ'], Γs = solp['Γs'])
        sol['si/s'] = self.BG.si_s(Bi = self.BG.get('βi[t-1]')[None,:], Γs = sol['Γs'], τp = sol['τ'])
        return sol

    def solveVector(self, x0 = None, update = True, **kwargs):
        sol = optimize.root(lambda τ: self.objectiveVector(τ), noneInit(x0, self.x0), **kwargs)
        assert sol['success'], f""" Couldn't identify PEE in LOG.solveVector"""
        return self.report(sol['x'], update = update)

    def objectiveVector(self, τ):
        sol = self.funcOfτVector(τ)
        return self.BT.FH_PEE(τBound = sol['τ'], τ = sol['τ_unbounded'], si_s = sol['si/s'], Θh = sol['Θh'], dlnh_Dτ = sol['dln(h)/dτ'])

    def funcOfτVector(self, τ):
        sol = {'τ_unbounded': τ, 'τ': np.clip(τ, self.db['τ_l'], self.db['τ_u'])}
        sol['τ[t+1]'] = self.m.leadSym(sol['τ'])
        sol['dln(h)/dτ'] = self.BT.dlnh_dτ(τ=sol['τ'])
        sol['Γs[t-1]'] = self.BT.FH_ΓsLagged(τ = sol['τ'])
        sol['Θh'] = self.BT.FH_Θh(τ = sol['τ'], τp = sol['τ[t+1]'], Γs = sol['Γs[t-1]'][1:])
        sol['si/s'] = self.BT.si_s(Bi = self.BT.get('βi[t-1]'), Γs = sol['Γs[t-1]'], τp = sol['τ'])
        return sol    

    def report(self, τ, update = True):
        sol = self.funcOfτVector(τ)
        if update:
            self.x0 = sol['τ_unbounded']
        return sol

    ### SOME UTILITIES THAT WE'LL USE IN VARIOUS EXTENSIONS OF THIS MODEL. 
    #   Added it here as several classes built on this relies on them.
    def _policyFunction1D(self, y, x, GS):
        return GS.fInterp(x, y, **GS.kwargsInterp)

    def _griddedGradient1D(self, y, x, s = 1e-4):
        sorted_indices = np.argsort(x)
        return interpolate.UnivariateSpline(x[sorted_indices], y[sorted_indices], s = s, k = 3).derivative()(x)

    # With splines instead:
    def _griddedGradient1D_griddedIdx_(self, y, griddedIdx, var = 'τ', s = 1e-4):
        df = pd.Series(y, index = griddedIdx).unstack(var)
        τIdx = np.clip(df.columns.to_numpy(), self.db[f'{var}_l'], self.db[f'{var}_u'])

        sorted_col_indices = np.argsort(τIdx)
        τIdx_sorted = τIdx[sorted_col_indices]
        df_sorted = df.iloc[:, sorted_col_indices]

        # Apply spline derivative to each row
        grad_array = np.array([
            interpolate.UnivariateSpline(τIdx_sorted, df_sorted.iloc[i].values, s=s, k=3).derivative()(τIdx_sorted)
            for i in range(len(df_sorted))
        ])

        # Restore original column order
        grad_array = grad_array[:, np.argsort(sorted_col_indices)]
        return pd.DataFrame(grad_array, index=df.index, columns=df.columns)

    def _griddedGradient1D_griddedIdx(self, y, griddedIdx, var = 'τ', order = 'F', s = 1e-4):
        return self._griddedGradient1D_griddedIdx_(y, griddedIdx, var = var, s = s).values.reshape(-1, order = order)
    
    def _griddedGradient1D_griddedIdx_sort(self, y, griddedIdx, var = 'τ', s = 1e-4):
        grad_df = self._griddedGradient1D_griddedIdx_(y, griddedIdx, var = var, s = s)
        grad_df = grad_df.stack().reorder_levels(griddedIdx.names).sort_index()
        return grad_df.values

    def _griddedGradient1D_griddedIdx_dropnan(self, y, griddedIdx, var = 'τ', order = 'F', s = 1e-4):
        """ Version where griddedIdx is not a cartesian product, 
        i.e. nan values are propagated when unstacking. This version 
        assumes the gridded index is sorted in a specific way. """
        df = pd.Series(y, index = griddedIdx).unstack(var)
        df.columns = np.clip(df.columns, self.db[f'{var}_l'], self.db[f'{var}_u'])
        size = df.shape[1]
        def _row(df, i):
            a = np.full(size, np.nan)
            si = df.iloc[i].dropna()
            a[~df.iloc[i,:].isna()] = interpolate.UnivariateSpline(si.index.values, si.values, s=s, k=3).derivative()(si.index.values)
            return a
        aFull = np.array([
            _row(df,i)
            for i in range(df.shape[0])
        ])
        aFull = aFull.reshape(-1, order = order)
        return aFull[~np.isnan(aFull)]

    def _griddedGradient2D(self, y, x, s = 1e-4):
        """ apply _griddedGradient columnwise on 2d array y, common x"""
        sorted_indices = np.argsort(x) 
        x_sorted, y_sorted = x[sorted_indices], y[sorted_indices, :]
        return np.array([
            interpolate.UnivariateSpline(x_sorted, y_sorted[:,i], s = s, k =3).derivative()(x)
            for i in range(y_sorted.shape[1])
        ]).T

    def _griddedGradient2D_griddedIdx(self, y, griddedIdx, var = 'τ', order = 'F', s = 1e-4):
        return np.column_stack([self._griddedGradient1D_griddedIdx(y[:,i], griddedIdx, var = var, order = order, s = s) for i in range(y.shape[1])])

    def _griddedGradient2D_griddedIdx_sort(self, y, griddedIdx, var = 'τ', s = 1e-4):
        return np.column_stack([self._griddedGradient1D_griddedIdx_sort(y[:,i], griddedIdx, var = var, s = s) for i in range(y.shape[1])])

    def _griddedGradient2D_griddedIdx_dropnan(self, y, griddedIdx, var = 'τ', order = 'F', s = 1e-4):
        return np.column_stack([self._griddedGradient1D_griddedIdx_dropnan(y[:,i], griddedIdx, var = var, order = order, s = s) for i in range(y.shape[1])])


class LogUSA(LogA):
    """ 
    Identify Sequence of Policy Functions. Analytical, LOG model.
    No informal households.
    
    The analytical LOG model does not involve identifying policy
    functions when pension characteristics (θ,ϵ) are fixed. In
    this case, the class returns the solution instead.
    """

    def objectiveVector(self, τ):
        sol = self.funcOfτVector(τ)
        return self.BT.FH_PEE(τBound = sol['τ'], τ = sol['τ_unbounded'], si_s = sol['si/s'], dlnh_Dτ = sol['dln(h)/dτ'])

    def objectiveGrid_T(self, τ):
        sol = self.funcOfτGrid_T(τ)
        return self.BG.PEE_T(τBound = sol['τ'], τ = sol['τ_unbounded'], si_s = sol['si/s'], dlnh_Dτ = sol['dln(h)/dτ'])

    def objectiveGrid_t(self, τ, solp):
        sol = self.funcOfτGrid_t(τ, solp)
        return self.BG.PEE_t(τBound = sol['τ'], τ = sol['τ_unbounded'], si_s = sol['si/s'], dlnh_Dτ = sol['dln(h)/dτ'])

class Log(LogA):
    """ 
    Identify Sequence of Policy Functions. LOG model with informal
    savings.

    When pension characteristics are fixed (θ, ϵ), the LOG model 
    identifies a sequence of policy functions witn informal savings
    relative to aggregate savings as the key state variable.
    """

    ### GRIDSETTING METHODS:
    def initGS(self):
        """ 
        'stateApprox': Instance to help identify state function: (s0}/s)(τ). 'PEE': Identify τ on grid of states. 
        """
        self.GS, solGrids, stateGrids = {}, self._solGrids, self._stateGrids
        # PEE state: Store global grids so we can restore them after subsetting along the way.
        self.GS['PEE'] = SolveGrid(F = None, solGrids = solGrids['PEE'], stateGrids = stateGrids['PEE'], fallback_to_nn=True)
        self.GS['PEE']._globalSolGrids = self.GS['PEE'].solGrids.copy() # Use this to relaunch global grid search
        self.GS['PEE'].fInterp = self.fInterp # specify preferred interpolator
        self.GS['PEE'].kwargsInterp = {}

        # State approximation:        
        self.GS['stateApprox'] = SolveGrid(F = None, solGrids = solGrids['stateApprox'], stateGrids = stateGrids['stateApprox'], fallback_to_nn=False)
        self.GS['stateApprox'].fInterp = self.fInterp # specify preferred interpolator
        self.GS['stateApprox'].kwargsInterp = {} # kwargs to add to interpolator

    @property
    def _solGrids(self):
        return {'stateApprox': {'s0_s': self.m.solGrids['s0/s']}, 'PEE': {'τ': self.m.solGrids['τ']}}

    @property
    def _stateGrids(self):
        return {'stateApprox': {'τ': self.m.stateGrids['τ']}, 'PEE': {'s0_s_': self.m.stateGrids['s0/s[t-1]']}}

    def vectorPolicy(self, sols, policy = 'τPolicy'):
        return lambda x: np.array([sols[t][policy](x[i]) for i,t in enumerate(sols.keys())], dtype = float)

    def __call__(self, style = None, **kwargs):
        return self.solveGSLoop(**kwargs) # only one implementation for this class

    def solveGSLoop(self, **kwargs):
        sols = dict.fromkeys(self.db['t'])
        t = self.db['t'][-1]
        self.BG.t, self.B.t = t, t
        sols[t] = self.solveGSLoop_T(**kwargs)
        for t in self.db['t'][-2::-1]:
            self.BG.t, self.B.t = t, t
            sols[t] = self.solveGSLoop_t(sols[t+1], **kwargs)
        return sols

    def approximatePEE(self, sols, states0):
        """ Approximate τ from sols and states0 = dict of initial levels of state variables """
        τ = pd.Series(None, index = self.db['t'], dtype = float)
        states = pd.DataFrame(None, index = self.db['t'], columns = self.GS['PEE'].state_names, dtype = float)
        # Initial state - add levels to states dataframe:
        t0 = self.db['t'][0]
        states.loc[t0,:] = tuple(states0.values())
        for t in self.db['t'][:-1]:
            τ.loc[t] = np.clip(sols[t]['τPolicy'](states.loc[t,:].values), self.db['τ_l'], self.db['τ_u']) # solve τ[t](states[t-1])
            states.loc[t+1,:] = sols[t]['statePolicy'](τ.loc[t], states = states.loc[t,:].values) # solve states[t](τ[t])
        # Terminal state - add policy, no states:
        tE = self.db['t'][-1]
        τ.loc[tE] = np.clip(sols[tE]['τPolicy'](states.loc[tE,:].values), self.db['τ_l'], self.db['τ_u'])
        return τ, states

    ### Non-terminal state:
    def solveGSLoop_t(self, solp, **kwargs):
        fStateApprox = self.solveStateApprox_t(solp) # returns gridded interpolant (s0/s)(τ)
        fPolicy = solp['τPolicy'] # policy function τ[t+1]/(s0/s) identified in t+1
        self._updateFeasiblePEE(fStateApprox) 
        def Fobj(τ = None, states = None):
            s0_s = fStateApprox(τ) # approximate (s0/s)(τ)
            τp = fPolicy(s0_s) # approximate τ[t+1](s0/s)
            sol = self.funcOfτ_t(τ, s0_s, τp, states['s0_s_'], gridND = self.GS['PEE'].combined_gridsND)
            return self.objectiveGrid_t(sol)
        self.GS['PEE'].update(F = Fobj)
        result = self.GS['PEE'].solve()
        return self.report_t(result['x'], fStateApprox, fPolicy)

    def _updateFeasiblePEE(self, fStateApprox):
        τ, state = self.GS['PEE']._globalSolGrids['τ'], self.GS['PEE'].stateGrids['s0_s_']
        statePredicted = fStateApprox(τ) # predicted state on full solution grid
        mask = (statePredicted > min(state)) & (statePredicted < max(state))
        padded = np.pad(mask, (1,1), mode = 'constant', constant_values= False)
        mask_extended = mask | padded[:-2] | padded[2:]
        self.GS['PEE'].update(solGrids = {'τ': τ[mask_extended]})

    def report_t(self, τ, fStateApprox, fPolicy):
        solved_mask = ~np.isnan(τ)
        τ, s0_s_ = τ[solved_mask], self.GS['PEE'].global_stateIdx.to_numpy()[solved_mask]
        s0_s = fStateApprox(τ)
        τp   = fPolicy(s0_s)
        sol = self.funcOfτ_t(τ, s0_s, τp, s0_s_)
        sol['τPolicy'] = self._policyFunction1D(sol['τ'], sol['s0/s[t-1]'], self.GS['PEE'])
        sol['statePolicy'] = lambda x, **kwargs: fStateApprox(x)
        return sol

    def objectiveGrid_t(self, sol):
        return self.BG.PEE_t(τBound = sol['τ'], τ = sol['τ_unbounded'], τp = sol['τ[t+1]'], Γs = sol['Γs[t+1]'], Bip = self.BG.get('βi')[None,:], B0p = self.BG.get('β0'), si_s = sol['si/s'], s0_s = sol['s0/s[t-1]'], Θs = sol['Θs'],
                             dlnh_Dτ = sol['dln(h)/dτ'], dlns_Dτ = sol['dln(s)/dτ'], dlnΓs_Dτ = sol['dln(Γs)/dτ'], dlnhp_Dlns = sol['dln(h[t+1])/dln(s)'], dτp_dτ = sol['dτ[t+1]/dτ'])


    def funcOfτ_t(self, τ, s0_s, τp, s0_s_, gridND = None):
        sol = self.funcOfStates_t(τ, s0_s, τp)
        sol['s0/s[t-1]'] = s0_s_ # gridded value
        sol['Γs'] = self.BG.Γs(Bi = self.BG.get('βi[t-1]'), τp = sol['τ'])
        sol['si/s'] = self.BG.si_s(Bi = self.BG.get('βi[t-1]')[None,:], Γs = sol['Γs'], τp = sol['τ'])
        sol = self.getGriddedGradients(sol, gridND = gridND)
        return sol

    def getGriddedGradients(self, sol, gridND = None):
        if gridND is None:
            _x = sol['τ']
            _method = self._griddedGradient1D
        else:
            _x = gridND
            _method = self._griddedGradient1D_griddedIdx
        sol['dln(h)/dτ'] = _method(np.log(sol['Θh']), _x)
        sol['dln(s)/dτ'] = _method(np.log(sol['Θs']), _x)
        sol['dln(Γs)/dτ'] = _method(np.log(sol['Γs[t+1]']), _x)
        sol['dτ[t+1]/dτ'] = _method(sol['τ[t+1]'], _x)
        sol['dln(h[t+1])/dln(s)'] = self.BG.power_h()
        return sol
        
    # Solve state approximation:
    def solveStateApprox_t(self, solp, **kwargs):
        """ Return dict with s0/s, τ for PEE approximation"""
        def Fobj(s0_s = None, states = None):
            τp = solp['τPolicy'](s0_s) # query future policy rates from approximation
            sol = self.funcOfStates_t(states['τ'], s0_s, τp) # collect in dict
            return self.BG.s0_s(B0 = self.BG.get('β0'), Θs = sol['Θs'], τp = sol['τ[t+1]']) - s0_s
        self.GS['stateApprox'].update(F = Fobj)
        result = self.GS['stateApprox'].solve()
        s0_s, τ = result['x'], self.GS['stateApprox'].stateGrids['τ']
        solved_mask = ~np.isnan(result['x'])
        return self._policyFunction1D(s0_s[solved_mask], τ[solved_mask], self.GS['stateApprox'])        

    def funcOfStates_t(self, τ, s0_s, τp):
        sol = {'τ_unbounded': τ, 'τ': np.clip(τ, self.db['τ_l'], self.db['τ_u']),
                            'τ[t+1]': np.clip(τp, self.db['τ_l'], self.db['τ_u']),
               's0/s'  : s0_s}
        sol['Γs[t+1]'] = self.BG.Γs(Bi = self.BG.get('βi')[None,:], τp = sol['τ[t+1]'])
        sol['Θh'] = self.BG.Θh_t(τ = sol['τ'], τp = sol['τ[t+1]'], Γs = sol['Γs[t+1]'])
        sol['Θs'] = self.BG.Θs_t(Θh = sol['Θh'], Γs = sol['Γs[t+1]'])
        return sol

    ### Terminal state:
    def solveGSLoop_T(self, **kwargs):
        def Fobj(τ = None, states = None):
            return self.objectiveGrid_T(τ = τ, s0_s_ = states['s0_s_'])
        self.GS['PEE'].update(F = Fobj, solGrids = self.GS['PEE']._globalSolGrids)
        result = self.GS['PEE'].solve()
        return self.report_T(result['x'])

    def funcOfτGrid_T(self, τ, s0_s_):
        sol = {'τ_unbounded': τ, 'τ': np.clip(τ, self.db['τ_l'], self.db['τ_u']),
               's0/s[t-1]'  : s0_s_}
        sol['dln(h)/dτ'] = self.BG.dlnh_dτ(sol['τ'])
        sol['Γs'] = self.BG.Γs(Bi = self.BG.get('βi[t-1]'), τp = sol['τ'])
        sol['si/s'] = self.BG.si_s(Bi = self.BG.get('βi[t-1]')[None,:], Γs = sol['Γs'], τp = sol['τ'])
        return sol

    def objectiveGrid_T(self, τ=None, s0_s_ = None):
        sol = self.funcOfτGrid_T(τ, s0_s_)
        return self.BG.PEE_T(τBound = sol['τ'], τ = sol['τ_unbounded'], dlnh_Dτ = sol['dln(h)/dτ'], si_s = sol['si/s'], s0_s = sol['s0/s[t-1]'])

    def report_T(self, τ):
        solved_mask = ~np.isnan(τ)
        τ, s0_s_ = τ[solved_mask], self.GS['PEE'].global_stateIdx.to_numpy()[solved_mask]
        sol = self.funcOfτGrid_T(τ, s0_s_)
        sol['τPolicy'] = self._policyFunction1D(sol['τ'], sol['s0/s[t-1]'], self.GS['PEE'])
        return sol

