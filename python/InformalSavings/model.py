import numpy as np, pandas as pd, functools, scipy, time
from scipy import optimize
from copy import deepcopy
from symMaps import SimpleSys, Lag, Lead
from gridsearch import continuation
from base import Base, BaseGrid, BaseTime
from policy import LOG, CRRA


def _shiftT(idx, t0, tName):
    """ Row-wise: subtract t0 from the `tName` axis/level of a pandas Index/MultiIndex, leaving any
    other level's values untouched. """
    if isinstance(idx, pd.MultiIndex):
        arrays = [idx.get_level_values(n) - t0 if n == tName else idx.get_level_values(n) for n in idx.names]
        return pd.MultiIndex.from_arrays(arrays, names = idx.names)
    return idx - t0


def _sliceDb(db, t0, tName = 't'):
    """ Restrict every db entry indexed (wholly or via one level) by `tName` to periods from t0 onward,
    AND renumber that axis back to 0-based (subtract t0), mutating db IN PLACE.

    Renumbering (not just restricting) is required, not cosmetic: model.py's EE_LOG_solve/
    EE_CRRA_solve/EE_report/initialState_solve index the plain ndarrays a caller passes in (τ, θ, ε)
    positionally via self.B.tFirst (e.g. `τ[self.B.tFirst]`), which is only correct when db['t'] is the
    native 0-based range() a fresh instance's initIdxs() builds -- so tFirst must come back out as 0 on
    the copy. Correspondingly, a caller's own τ/θ/ε arrays for the copy must themselves start at
    position 0 = the original t0 (i.e. sliced off the front) -- solvePEE_LOG/CRRA's own θ=None/ε=None
    defaults already get this for free, since db['θ']/db['eps'] are sliced+renumbered here too.

    createCopyFromt0 relies on self.B/self.BG/self.BT/self.LOG/self.CRRA all sharing the same dict
    object post-deepcopy -- rebinding db to a fresh dict here would silently orphan that aliasing, so
    this mutates the existing dict's entries in place rather than returning a new one. Scalars,
    type-indexed (j/i/u) objects, and eigenvector-calibration arrays pass through unchanged. Covers
    db['t']/db['txE'] (plain Index), db['tj']/db['ti'] (MultiIndex), and every 1D/2D parameter plus its
    [t+1]/[t-1] siblings (Series/DataFrame) in one pass. """
    for k, v in db.items():
        if isinstance(v, pd.MultiIndex):
            if tName in v.names:
                db[k] = _shiftT(v[v.get_level_values(tName) >= t0], t0, tName)
        elif isinstance(v, pd.Index):
            if v.name == tName:
                db[k] = v[v >= t0] - t0
        elif isinstance(v, (pd.Series, pd.DataFrame)):
            idx = v.index
            if isinstance(idx, pd.MultiIndex):
                if tName in idx.names:
                    sub = v[idx.get_level_values(tName) >= t0]
                    db[k] = sub.set_axis(_shiftT(sub.index, t0, tName))
            elif idx.name == tName:
                sub = v[idx >= t0]
                db[k] = sub.set_axis(sub.index - t0)


class ModelInformalSavings:
    _BaseClass = Base
    _BaseGridClass = BaseGrid
    _BaseTimeClass = BaseTime
    _PolicyLogClass = LOG
    _PolicyCRRAClass = CRRA

    def __init__(self, nj = 4, T = 10, pars = None, **kwargs):
        """ Model with informal households.
        
        Parameters
        ----------
        nj: Integer - number of household types.
        T : Integer - years.
        
        db : dict
            Keys = Variable names (string).
            Values = Data either stored as scalars, pandas series, or numpy arrays.        
        """
        self.nj, self.T = nj, T
        self.ni = self.nj-1
        self.db = {} # dictionary database
        self.x0 = {} # cache of last-used/default initial guesses for numerical problems, keyed by problem name
        self.addProperty('paramsFromFuncs', ['Γh','θ','eps','κ']) # list of auxiliary parameters to be recalculated when deep parameters are updated
        self.parTypes = self._parTypes.copy() # Mapping of parameter names to dimensions
        self.initIdxs() # Initialize relevant pandas indices
        self.addNamespaces() # aux classes that help nagivate stacked vectors + lag/lead symbols.
        self.B = self._BaseClass(self) # Class used for scalar computations
        self.BG = self._BaseGridClass(self)  # Class used for vectorized computations across states
        self.BT = self._BaseTimeClass(self)  # Class used for vectorized computations across time
        self.initPars(pars = pars)
        self.initProductivity()
        self.updateAuxPars()
        self.LOG = self._PolicyLogClass(self) 
        self.CRRA = self._PolicyCRRAClass(self)

    #######################################################################
    ##########                0.1. Auxiliary methods            ###########
    #######################################################################

    # Some basic methods for navigating symbols:
    def leadSym(self, symbol, lead = -1, opt = None, ns = 'exo'):
        """ 'lead' uses the same sign convention as Lag.series' 'lag' argument, i.e. result.loc[t] = symbol.loc[t-lead].
        bfill = 'ss' clamps the out-of-domain boundary period to the nearest in-domain value (replaces the old useLoc='nn' behavior). """
        o = {'bfill': 'ss'} if opt is None else opt
        if isinstance(symbol, pd.Series):
            return Lag.series(symbol, lead, **o)
        elif isinstance(symbol, pd.DataFrame):
            return Lag.series(symbol.stack(), lead, **o).unstack()
        elif isinstance(symbol, np.ndarray):
            if symbol.ndim == 1:
                return np.hstack([symbol[1:], symbol[-1]])
            elif symbol.ndim == 2:
                return np.vstack([symbol[1:], symbol[-1]])

    def __call__(self, x, name, ns = 'exo', **kwargs):
        return self.ns[ns](x, name, **kwargs)

    def get(self, x, name, ns = 'exo'):
        return self.ns[ns].get(x, name)

    ### Specify parameter structure - what parameters are 1D, 2D - what auxiliary parameters do we have and how do we recompute them? 
    @property
    def _parTypes(self):
        return {'0D': list(self.default0DParams), '1D': list(self.default1Dparams)+self.aux1DParams+self.paramsFromFuncs, '2D': list(self.default2Dparams)+self.aux2DParams}
    @property
    def default0DParams(self):
        """ scalars. NOTE two names here collide (in spelling only) with unrelated timing concepts used
        throughout §3/§4 -- see README's "Timing convention":
        - 's0' here is the *aggregate savings rate* at db['t0'] (a ratio, e.g. 0.184 = 18.4%). It was the
          target that identified β until 2026-08-24 and is now REPORTED ONLY -- 'KY0' replaced it, see
          calibration_report. It is NOT the `s0` function argument used throughout EE_LOG_solve/
          EE_CRRA_solve/steadyState_*/policy.py (the *level* of savings at the pre-determined period before
          db['t'][0], i.e. docs' s_0).
        - 't0' here is the *index into db['t'] of the calibration baseline year* (e.g. 2010 in the real
          Argentina calibration; defaults to 2, an arbitrary early index) -- NOT self.B.tFirst (=db['t'][0],
          the model's first active/endogenous period, docs' t=1) and NOT the pre-determined period before
          the horizon (docs' t=0). All three are genuinely different things.

        'KY0' is the capital-output ratio target (eq:calibration:KY), in ANNUAL output units, and
        'yearsPerPeriod' is what puts it there -- the model period is 30 years (docs, model_calibration),
        a convention that until now lived only in the documentation. The default 3.2313 is Argentina's
        ratio in 2010 from Penn World Table 11.0 -- the calibration year, where every other target in
        eq:calibration is also measured. data/argentina_calibrationTargets.csv is the record,
        python/paper/dataTargets.py rebuilds it, and the same file carries the 1980-2010 mean (3.6606,
        13% higher) as the sensitivity that choice costs. """
        return {'τ0': .125, 'RR0': 0.678/0.803, 's0': 0.184, 'KY0': 3.2313, 'yearsPerPeriod': 30,
                'RRGroups': (1,2), 't0': 2}

    @property
    def default1Dparams(self):
        """ 1d vectors - defined over t """
        return {'α': .43, 'ν': 1, 'ξ' : .3, 'ρ': 1, 'ω': 1.25, 'χR': 1}
    @property
    def default2Dparams(self):
        """ 2d matrices - defined over (t, j)"""
        return {'γj': np.full(self.nj, 1/self.ni)} | {k: np.full(self.nj, 1) for k in ('pj','μj','Xj','ηj','zxj','zηj','βj')}
    @property
    def aux2DParams(self):
        """ 2d matrices - defined over (t, i)"""
        return [f"{k[:-1]}i" for k in self.default2Dparams]
    @property
    def aux1DParams(self):
        """ 1d vectors - defined over t """
        return [f"{k[:-1]}0" for k in self.default2Dparams]

    ### Methods to compute auxiliary parameters used throughout the code:
    @property
    def aux_θ(self):
        return pd.Series(self.getθ(), index = self.db['t'])
    @property
    def aux_eps(self):
        return pd.Series(self.getEps(), index = self.db['t'])
    @property
    def aux_κ(self):
        return self.BT.κ(self.db['eps[t+1]'])
    @property
    def aux_p(self):
        return (self.db['γi'] * self.db['pi']).sum(axis=1)
    @property
    def aux_Γh(self):
        return self.BT.Γh()

    def addProperty(self, key, value):
        """ default dynamic property method """
        setattr(self, f'_{key}', value)
        setattr(type(self), key, property(fget = lambda self: getattr(self, f'_{key}'), fset = lambda self, value: setattr(self, f'_{key}', value)))

    def __setstate__(self, state):
        self.__dict__.update(state)
        value = getattr(self, '_paramsFromFuncs', getattr(self, '_paramFromFuncs', None))
        if value is not None:
            self.addProperty('paramsFromFuncs', value)

    def initIdxs(self):
        self.db['t'] = pd.Index(range(self.T), name = 't')
        self.db['txE'] = pd.Index(range(self.T-1), name = 't') # Time index without terminal period
        self.db['j'] = pd.Index(range(self.nj), name = 'j')
        self.db['i'] = self.db['j'][1:]
        self.db['u'] = self.db['j'][0:1]
        self.db['tj'] = pd.MultiIndex.from_product([self.db['t'], self.db['j']])
        self.db['ti'] = pd.MultiIndex.from_product([self.db['t'], self.db['i']])

    def addNamespaces(self):
        self.ns = {}
        self.ns['exo'] = SimpleSys(v = (dict.fromkeys(self.default1Dparams, self.db['t']) |
                                       dict.fromkeys(self.default2Dparams, self.db['tj'])|
                                       dict.fromkeys(self.aux1DParams, self.db['t']) |
                                       dict.fromkeys(self.aux2DParams, self.db['ti']) |
                                       dict.fromkeys(self.paramsFromFuncs, self.db['t'])))
        # One namespace per numerical problem (§3): here just for stacking/unstacking EE_CRRA's unknown
        # vector x=(Γs,h,s) (all txE-domain) -- NOT used for its x0()/db-array machinery (that's tied to
        # symMaps' own SimpleDB, not our plain-dict self.db), only for __call__/get/unloadSol's name<->
        # position mapping, so this coexists cleanly with keeping solution objects out of self.db.
        self.ns['EE_CRRA'] = SimpleSys(v = dict.fromkeys(('Γs', 'h', 's'), self.db['txE']))
        [ns.compile() for ns in self.ns.values()];

    def initPars(self, pars = None):
        self.db.update(self.defaultParameters) # default parameters and targets
        self.addDefaultHeterogeneity # default heterogeneity
        if pars is not None:
            [self.db.update(self.adjPar(k,v)) for k,v in pars.items()];

    ### Methods used to navigate 0D/1D/2D parameters including lags/leads - and how to update full dimension parameters based inputs with fewer dimensions. 
    @property
    def defaultParameters(self):
        """ Return full dictionary and default values
        and with dimensions broadcasted to appropriate dimensions for 0D/1D """
        return functools.reduce(lambda x,y: x|y, [self.adjPar(k,v) for k,v in self.default0DParams.items()] + [self.adjPar(k,v) for k,v in self.default1Dparams.items()])
    @property
    def addDefaultHeterogeneity(self):
        """ Return dictionary with defautlt values 
        and with dimensions broadcasted to appropriate dimensions for 2D. """
        [self.db.update(self.adjPar(k,v)) for k,v in self.default2Dparams.items()]; 

    def updateAuxPars(self):
        [self.db.update(self.addLeadAndLags(k, getattr(self, f'aux_{k}'))) for k in self.paramsFromFuncs]

    def adjPar(self, k, vals, t = None):
        """ Default methods for adjusting different parameter types. """
        if k == 'β':
            return self.adj2Dj_ll('βj', self.simpleβ(vals), t = t)
        elif k == 'pj':
            return self.adjpj('pj', vals, t = t)
        elif k in self.parTypes['0D']:
            return {k: vals}
        elif k in self.parTypes['1D']:
            return self.adj1D_ll(k, vals, t = t)
        elif k in self.aux2DParams:
            return self.adj2Di_ll(k, vals, t = t)
        elif k in self.parTypes['2D']:
            return self.adj2Dj_ll(k, vals, t = t)
        else:
            return {k:vals}
    def simpleβ(self, β):
        """ Override full βj with scalar """
        return β * self.db['pj']
    def simpleβinv(self):
        """ Get scalar β from full dataframe (assumes constant across t,j) """
        return self.db['βj'].iloc[0,0]/self.db['pj'].iloc[0,0]
    def adjpj(self, k, vals, t = None):
        """ Specialized method for p - we have to enforce constant p across pi"""
        d = self.adjDf_tj(k,vals,t=t)
        d['p'] = (self.db['γi'] * d['pi']).sum(axis=1)
        return self.addLeadAndLags(d)

    def adj1D_ll(self, k, vals, t = None):
        return self.addLeadAndLags(k, self.adjVec_t(k, vals, t = t))
    def adj2Dj_ll(self, k , vals, t = None):
        return self.addLeadAndLags(self.adjDf_tj(k, vals ,t = t))
    def adj2Di_ll(self, k , vals, t = None):
        return self.addLeadAndLags(self.adjDf_ti(k, vals ,t = t))

    def addLeadAndLags(self, k, s = None):
        if isinstance(k, dict):
            return functools.reduce(lambda x,y: x|y, [self.addLeadAndLags(i,v) for i,v in k.items()])
        else:
            return {k: s, f'{k}[t+1]': self.leadSym(s, lead = {'t':-1} if isinstance(s, pd.DataFrame) else -1), f'{k}[t-1]': self.leadSym(s, lead = {'t': 1} if isinstance(s, pd.DataFrame) else  1)}

    def adjVec_t(self, k, vals, t = None):
        if t is None:
            return pd.Series(vals, index = self.db['t'])
        else:
            x = self.db[k]
            x.loc[t] = vals
            return x
    def adjDf_ti(self, k, vals, t = None):
        if np.isscalar(vals):
            xi = pd.DataFrame(vals, index = self.db['t'], columns = self.db['i'])
        elif vals.ndim == 1:
            if t is None: 
                xi = pd.DataFrame(np.tile(vals, (self.T,1)), index = self.db['t'], columns = self.db['i'])
            else:
                xi = self.db[k]
                k.loc[t] = vals
        else:
            xi = pd.DataFrame(vals, index = self.db['t'], columns = self.db['i'])
        return {f'{k[:-1]}j': pd.concat([self.db[f'{k[:-1]}0'], xi], axis = 1), k: xi}
    def adjDf_tj(self, k, vals, t = None):
        if np.isscalar(vals):
            xj = pd.DataFrame(vals, index = self.db['t'], columns = self.db['j'])
        elif vals.ndim == 1:
            if t is None:
                xj =  pd.DataFrame(np.tile(vals, (self.T, 1)), index = self.db['t'], columns = self.db['j'])
            else:
                xj = self.db[k]
                xj.loc[t] = vals
        else:
            xj = pd.DataFrame(vals, index = self.db['t'], columns = self.db['j'])
        return {k: xj, f'{k[:-1]}i': xj[self.db['i']], f'{k[:-1]}0': xj[0]}



    #######################################################################
    ##########            2. Simple calibration methods         ###########
    #######################################################################

    def getθ(self):
        """ Target relative replacement ratios for θ """
        i,ii = self.db['RRGroups'][0], self.db['RRGroups'][1]
        ξ= self.db['ξ'].xs(self.db['t0'])
        h1,h2 = (self.db['Γh']*self.db['Xi'][i]**ξ/self.db['ηi'][i]**(1+ξ)).xs(self.db['t0']), (self.db['Γh']*self.db['Xi'][ii]**ξ/self.db['ηi'][ii]**(1+ξ)).xs(self.db['t0'])
        return (self.db['RR0']*h1-h2)/(1-h2-self.db['RR0']*(1-h1))
    def getEps(self, coverageRate = 0.7):
        """ Target ϵ for argentina pre-reform """
        return coverageRate * (1-self.db['θ'].xs(self.db['t0'])+self.db['θ'].xs(self.db['t0'])*self.B.auxProd(self.db['t0'])[1]) * (self.simpleβinv()**(5/30)*9.45/14.45+self.simpleβinv()**(10/30)*12.55/22.55)/2

    # Initialize productivity distribution:
    def initProductivity(self):
        """Get ηi, Xi based on data on relative income/labor supply."""
        # i. ηj, Xj stuff:
        self.addEigenVectors()
        ηi = self.getηi()
        η0 = 0.3 * ηi[0] * self.db['zη0'].xs(self.db['t0'])/self.db['zηi'].xs(self.db['t0'])[1] # initial guess for η0 based on the rest of the vector
        self.db.update(self.adjPar('ηj', np.hstack([η0,ηi])))
        xj = self.db['zxj'].xs(self.db['t0'])
        yx = np.hstack([self.db['yx'][0]*xj[0]/xj[1], self.db['yx']]) # inital guess for yx vector.
        self.db.update(self.adjPar('Xj', self.db['ηj'].values/(np.tile(yx, (self.T,1))**(1/self.db['ξ'].values.reshape(self.T,1)))))

    def addEigenVectors(self):
        valx, vecx = scipy.sparse.linalg.eigs(self.db['zxi'].xs(self.db['t0']).values.reshape(self.ni,1) * self.db['γi'].xs(self.db['t0']).values.reshape(1, self.ni), k = 1)
        valη, vecη = scipy.sparse.linalg.eigs(self.db['zηi'].xs(self.db['t0']).values.reshape(self.ni,1) * self.db['γi'].xs(self.db['t0']).values.reshape(1, self.ni), k = 1)
        self.db['yx'], self.db['yη'] = abs(np.real(vecx)).reshape(self.ni), abs(np.real(vecη).reshape(self.ni))
    def getηi(self):
        return self.db['yη']/(self.db['yx']*sum(self.db['γi'].xs(self.db['t0']).values*self.db['yη']))
    def getXi(self):
        return self.db['ηi']/self.db['yx']**(1/self.db['ξ'])

    #######################################################################
    ##########   3. Economic equilibrium (EE) solve, given policy   ########
    #######################################################################
    # See README's "Timing convention" for db['t']/s0/db['t'][-1] vs. the docs' t=0..T, and the module
    # overview's "The one structural consequence" for what's unchanged from informalAnalytical here. One
    # implementation note not in the README: EE_LOG_solve/EE_CRRA_solve/EE_report return plain ndarrays
    # internally, wrapping into pd.Series/DataFrame only in the final return (_wrapVars, keyed off
    # _t2vars/_txE2vars below) -- not done inside base.py's own methods (incl. FH_*), since those run
    # inside EE_CRRA_solve's root-finding loop where pandas' per-call overhead would be pure cost.

    # Which pandas index a symbol reports over -- a fixed, once-per-model mapping.
    _t2vars = ('s', 'h', 's_', 'R', 'R0', 'w', 'w0', 'hi', 'h0', 'bbar', 'bi', 'b0',
               'c1i', 'tildec1i', 'c2i', 'tildec2i', 'c10', 'tildec10', 'c20', 'tildec20')
    _txE2vars = ('Γs', 'B', 'B0', 'si_s', 'ι')

    def _wrapEE(self, x, idx):
        """ Wrap an EE_* result as pd.Series (1D) or pd.DataFrame (2D, columns=db['i']) indexed by idx
        (db['t'] for T-length, db['txE'] for T-1-length quantities). """
        return pd.DataFrame(x, index = idx, columns = self.db['i']) if x.ndim == 2 else pd.Series(x, index = idx)

    def _wrapVars(self, d):
        """ Wrap {name: raw ndarray} into pd.Series/DataFrame via _wrapEE, looking up each name's index
        (db['t'] vs db['txE']) from _t2vars/_txE2vars. Any name in neither is a bug -- fails loudly
        rather than silently mis-indexing a symbol someone forgot to register. """
        t, txE = self.db['t'], self.db['txE']
        def idx(k):
            if k in self._t2vars: return t
            elif k in self._txE2vars: return txE
            else: raise KeyError(f"'{k}' is not registered in _t2vars/_txE2vars -- add it there.")
        return {k: self._wrapEE(v, idx(k)) for k, v in d.items()}

    def _checkConverged(self, residual, tol = 1e-8, name = '', scipyRes = None):
        """ Verify convergence via the actual residual norm rather than trusting a solver's own success
        flag (scipy's res.success behaves inconsistently across methods -- treat as informational only).
        scipyRes: optional OptimizeResult, included in the error message for diagnostic context. Not
        scipy-specific (just needs a residual array), so it generalizes to any numerical problem here. """
        maxResid = np.max(np.abs(residual))
        if not (maxResid <= tol):  # not `maxResid > tol`: NaN comparisons are always False either way, so
                                    # that form would silently let a NaN residual pass as "converged".
            scipyInfo = f" (scipy success={scipyRes.success}, message={scipyRes.message!r})" if scipyRes is not None else ""
            raise RuntimeError(f"{name} did not converge: max|residual|={maxResid:.3e} > tol={tol:.1e}{scipyInfo}")
        return maxResid

    def EE_LOG_solve(self, τ, θ, ε, s0 = None):
        """ Closed-form economic equilibrium given LOG preferences (ρ=1, so B_{t+1}^i=β_{t,i} is a pure
        primitive -- no root-finding). τ, θ, ε: full length-T policy paths. s0: the state before db['t'][0]
        (docs' s_0); defaults to the LOG steady state at db['t'][0]'s (τ,θ) (§4's steadyState_LOG_solve).
        Γs/Θh/Θs are fully exogenous given β; the only genuine recursion is s_t (nonlinear in s_{t-1}), so
        that's the only loop -- h then follows in one vectorized FH_h call. Returns {'s','h','Γs','B'}
        (Γs/B length T-1, h/s length T). No self.x0 caching -- closed-form, nothing to warm-start. """
        if s0 is None:
            s0 = self.steadyState_LOG_solve(τ[self.B.tFirst], θ[self.B.tFirst], t = self.B.tFirst)['s']
        τ1, θ1 = self.leadSym(τ), self.leadSym(θ)
        Γs_full = self.BT.Γs(self.db['βi'].values, τ1, θ1)
        Θh_full = self.BT.Θh(τ, τ1, θ1, Γs_full)
        Θh_full[-1] = self.BT.ΘhTerminal(τ)[-1]
        Θs = self.BT.Θs(Θh_full, Γs_full)
        ν, powerS = self.db['ν'].values, self.BT.power_s()
        s = np.empty(self.T)
        s_ = s0
        for i in range(self.T-1):
            s[i] = Θs[i] * (s_/ν[i])**powerS[i]
            s_ = s[i]
        s[-1] = 0
        s_lag = np.append(s0, s[:-1])
        h = self.BT.FH_h(τ, τ1, θ1, Γs_full[:-1], s_lag)
        return self._wrapVars({'s': s, 'h': h, 'Γs': Γs_full[:-1], 'B': self.db['βi'].values[:-1]})

    def defaultX0_EE_CRRA(self, τ, θ, ε, s0):
        """ Fallback initial guess for EE_CRRA_solve when neither an explicit x0 nor a cached
        self.x0['EE_CRRA'] is available: the LOG closed-form (Γs,h,s) path, txE-sliced and stacked into
        the layout EE_CRRA_residual expects -- cheap, and exact at ρ=1. """
        nx = self.T - 1
        sol = self.EE_LOG_solve(τ, θ, ε, s0)
        return np.concatenate([sol['Γs'].values, sol['h'].values[:nx], sol['s'].values[:nx]])

    def EE_CRRA_residual(self, x, τ, θ, ε, s0):
        """ Residual for the CRRA economic equilibrium. Unknowns are the full (Γs_t, h_t, s_t) triple for
        t=0..T-2 (nx=T-1 each, 3*nx total, matching the docs' square system) -- evaluated fully vectorized
        via self.BT with zero Python loops, since each defining equation (auxiliary:h, auxiliary:sFromH,
        auxiliary:Gammas) only checks *consistency* of the candidate. Extraction uses self.ns['EE_CRRA']
        rather than hardcoded slicing. Uses __call__ (raw ndarray), not .get(): this runs inside the
        root-finder's hot loop. Returns the stacked (Γs_resid, h_resid, s_resid), length 3*nx. """
        nx = self.T - 1
        ns = self.ns['EE_CRRA']
        Γs_u, h_u, s_u = ns(x, 'Γs'), ns(x, 'h'), ns(x, 's')
        τ1, θ1 = self.leadSym(τ), self.leadSym(θ)

        s_lag = np.append(s0, s_u)          # s_{t-1}, t=0..T-1
        Γs_pad = np.append(Γs_u, 0)         # dummy -- sFromH's terminal-index output discarded by [:nx]
        s_full = np.append(s_u, 0) 

        h_full = self.BT.FH_h(τ, τ1, θ1, Γs_u, s_lag)
        h_resid = h_u - h_full[:nx]
        s_resid = s_u - self.BT.sFromH(h_full, Γs_pad)[:nx]

        h_lead = np.append(h_full[1:], h_full[-1])                   # h_{t+1}, only [:nx] used
        with np.errstate(divide = 'ignore', invalid = 'ignore'): # s_full[-1]=0 makes B's terminal entry inf/nan; discarded by [:nx] below
            Γs_new = self.BT.Γs(self.BT.B(s_full, h_lead), τ1, θ1)
        Γs_resid = Γs_u - Γs_new[:nx]

        return np.concatenate([Γs_resid, h_resid, s_resid])

    def EE_CRRA_solve(self, τ, θ, ε, s0 = None, x0 = None, update = True, tol = 1e-8, **kwargs):
        """ Root-find the CRRA economic equilibrium. s0: state before db['t'][0] (docs' s_0); defaults to
        the CRRA steady state at db['t'][0]'s (τ,θ) (§4's steadyState_CRRA_solve). x0 defaults to
        self.x0.get('EE_CRRA'), else defaultX0_EE_CRRA. update: cache the solved x for warm-starting later
        calls. Returns {'s','h','Γs','B'} (Γs/B length T-1, h/s length T -- h/s need the FH_h/terminal-
        append reconstruction below since the solver only searches their txE-domain values). """
        if s0 is None:
            s0 = self.steadyState_CRRA_solve(τ[self.B.tFirst], θ[self.B.tFirst], t = self.B.tFirst)['s']
        nx = self.T - 1
        ns = self.ns['EE_CRRA']
        if x0 is None:
            x0 = self.x0.get('EE_CRRA', self.defaultX0_EE_CRRA(τ, θ, ε, s0))
        res = optimize.root(self.EE_CRRA_residual, x0, args = (τ, θ, ε, s0), **kwargs)
        self._checkConverged(res.fun, tol = tol, name = 'EE_CRRA_solve', scipyRes = res)
        if update:
            self.x0['EE_CRRA'] = res.x
        Γs_u, h_u, s_u = ns(res.x, 'Γs'), ns(res.x, 'h'), ns(res.x, 's')
        τ1, θ1 = self.leadSym(τ), self.leadSym(θ)
        s_lag = np.append(s0, s_u)
        s = np.append(s_u, 0)
        h = self.BT.FH_h(τ, τ1, θ1, Γs_u, s_lag)
        h_lead = np.append(h[1:], h[-1])
        with np.errstate(divide = 'ignore', invalid = 'ignore'): # s[-1]=0 makes B's terminal entry inf/nan; discarded below
            B_full = self.BT.B(s, h_lead)
        return self._wrapVars({'s': s, 'h': h, 'Γs': Γs_u, 'B': B_full[:-1]})

    def EE_report(self, sol, τ, θ, ε, s0):
        """ Expand a solved {'s','h','Γs','B'} dict (from either solver) into the full set of equilibrium
        objects via base.py, vectorized over the whole time path (self.BT) -- shared by both since
        everything downstream of (s,h,Γs,B) is identical regardless of origin. Γs/B/B0/si_s/ι come back at
        length T-1; everything else (incl. 's_'=s_{t-1} and 'h_', backed out via §5's
        initialState_solve) is length T.

        B0/ι are computed here rather than returned by the solvers: informal savings never enter the
        formal capital stock, so ι_t is a closed-form read-off of the solved core (s,h,Γs,B), not part of
        the root problem. """
        s, h, Γs, B = sol['s'].values, sol['h'].values, sol['Γs'].values, sol['B'].values
        s_ = np.append(s0, s[:-1])
        τ1, θ1, ε1 = self.leadSym(τ), self.leadSym(θ), self.leadSym(ε)
        init = self.initialState_solve(τ[self.B.tFirst], θ[self.B.tFirst], ε[self.B.tFirst])
        h_ = np.append(self.B.hFromS(s0, init['Γs'], self.B.tFirst), h[:-1])

        R, R0 = self.BT.R(s_, h), self.BT.R0(s_, h)
        w, w0 = self.BT.w(s_, h), self.BT.w0(s_)
        hi, hh0 = self.BT.hi(h), self.BT.h0(s_)
        bbar = self.BT.bbar(τ, w, h, h_)
        bi = self.BT.bi(θ, bbar, h_)
        b0 = self.BT.b0(ε, bbar, h_)

        # B_T^i/B_T^0 are genuinely undefined (s_{T-1}=0 -> R_T=inf); the terminal entry is discarded below.
        h_lead = np.append(h[1:], h[-1])
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            B0 = self.BT.B0(s, h_lead)[:-1]

        # si_s/ι have no terminal-period counterpart at all (s_{T-1}=0 makes both ratios 0/0), so we pad
        # with nonzero dummies purely to dodge the resulting divide-by-zero warning, then drop that entry
        # (unlike FH_c1i/FH_c10's 0-padding, these dummies carry no economic meaning -- they are discarded).
        B_dummy, Γs_dummy = np.vstack([B, np.ones((1, self.ni))]), np.append(Γs, 1)
        si_s = self.BT.si_s(B_dummy, τ1, θ1, Γs_dummy)[:-1]
        si_s_ = np.vstack([init['si_s'][None, :], si_s])
        Θs_dummy = self.BT.Θs(self.BT.ΘhFromH(h, s_), Γs_dummy)
        ι = self.BT.s0_s(np.append(B0, 1), Θs_dummy, τ1, ε1)[:-1]
        ι_ = np.append(init['ι'], ι)

        c1i = self.BT.FH_c1i(h, s, B, τ1, θ1)
        tc1i = self.BT.FH_tildec1i(h, B, τ1, θ1, Γs)
        c2i = self.BT.c2i(h, s_, τ, θ, si_s_)
        tc2i = self.BT.tildec2i(h, s_, τ, θ, si_s_)
        c10 = self.BT.FH_c10(s_, s, B0, τ1, ε1)
        tc10 = self.BT.FH_tildec10(s_, s, B0, τ1, ε1)
        c20, tc20 = self.BT.c20(h, s_, ε, τ, ι_), self.BT.tildec20(h, s_, ε, τ, ι_)

        return self._wrapVars({'s': s, 'h': h, 's_': s_, 'R': R, 'R0': R0, 'w': w, 'w0': w0, 'hi': hi, 'h0': hh0,
                                'bbar': bbar, 'bi': bi, 'b0': b0,
                                'c1i': c1i, 'tildec1i': tc1i, 'c2i': c2i, 'tildec2i': tc2i,
                                'c10': c10, 'tildec10': tc10, 'c20': c20, 'tildec20': tc20,
                                'Γs': Γs, 'B': B, 'B0': B0, 'si_s': si_s, 'ι': ι})

    #######################################################################
    ##########   4. Steady state solve (docs §2.1, eq:steadystate_*)  ######
    #######################################################################
    # Fixed point s_t=s_{t-1}=s* under a constant (τ,θ) at db['t'][0]'s parameters. Default s0 source for
    # EE_LOG_solve/EE_CRRA_solve. Unchanged from informalAnalytical (informal savings never enter Γs/Θh).
    def steadyState_LOG_solve(self, τ, θ, t = None):
        """ Closed-form steady state given LOG preferences (ρ=1, so B^i=β_i is a pure primitive -- no
        root-finding, matching EE_LOG_solve). τ, θ: constant steady-state policy (scalars). """
        t = self.B.tFirst if t is None else t
        B = self.B.get('βi', t)
        Γs = self.B.Γs(B, τ, θ, t)
        return self.steadyState_report(Γs, B, τ, θ, t)

    def steadyState_CRRA_residual(self, Γs, τ, θ, t = None):
        """ Residual for the CRRA steady state (eq:steadystate_CRRA:Gammas): Γs is a steady state iff it
        reproduces itself through self.B.Γs once B^i is made consistent with it via self.B.BSteadyState.
        Scalar in/out, matching scipy.optimize.brentq's signature. """
        return Γs - self.B.Γs(self.B.BSteadyState(Γs, τ, θ, t), τ, θ, t)

    def steadyState_CRRA_solve(self, τ, θ, t = None, bounds = (1e-6, 0.75), tol = 1e-11, **kwargs):
        """ Root-find the CRRA steady state Γs via brentq (bounded scalar search, per the doc's own
        recommendation). The doc suggests (0, 0.9) on the grounds that Γs = B/((1+B)(1+ξ)) exactly when B
        is constant across types; 0.75 is tightened from that, and is not a doc value. """
        t = self.B.tFirst if t is None else t
        Γs = optimize.brentq(self.steadyState_CRRA_residual, *bounds, args = (τ, θ, t), **kwargs)
        self._checkConverged(self.steadyState_CRRA_residual(Γs, τ, θ, t), tol = tol, name = 'steadyState_CRRA_solve')
        B = self.B.BSteadyState(Γs, τ, θ, t)
        return self.steadyState_report(Γs, B, τ, θ, t)

    def steadyState_report(self, Γs, B, τ, θ, t = None):
        """ Expand a solved (Γs, B) pair into the full steady-state core: Θh/Θs (at constant
        τ_t=τ_{t+1}=τ, θ_{t+1}=θ), then s*/h* -- closed-form regardless of LOG vs. CRRA, since Γs/B
        already encode whichever preference case produced them. """
        t = self.B.tFirst if t is None else t
        Θh = self.B.Θh(τ, τ, θ, Γs, t)
        Θs = self.B.Θs(Θh, Γs, t)
        s = self.B.sSteadyState(Θs, t)
        h = self.B.h(Θh, s, t)
        return {'Γs': Γs, 'B': B, 's': s, 'h': h, 'Θs': Θs}

    #######################################################################
    ##########   5. Initial (pre-determined) state (docs' t=0)        ######
    #######################################################################
    # Identifies h_{-1}/s_{-1,i}/s_{-1} -- the generation already old at db['t'][0], per the docs' own
    # fallback ("the pre-defined state we take as given, or identify using some steady state assumption").
    #
    #
    # initialState_solve does NOT take s0: Γs/B (steadyState_CRRA_solve -- collapses to LOG's closed-form
    # βi exactly at ρ=1, so one method serves both cases), si_s and ι are pure functions of (τ,θ,ε) and
    # primitives, never of the savings level. h_{-1} is the one exception that does need s0 (via
    # Base.hFromS) -- computed separately in EE_report, not bundled here.
    def initialState_solve(self, τ, θ, ε, t = None, **kwargs):
        """ Identify Γ_{s,-1}, B_{-1}^i, B_{-1}^0, s_{-1,i}/s_{-1}, ι_{-1} -- see §5 header. τ, θ, ε:
        scalars, db['t'][0]'s own policy. kwargs passed to steadyState_CRRA_solve. Returns
        {'Γs','B','B0','si_s','ι','s'} -- no h_{-1} (needs the actual s0; see EE_report's Base.hFromS
        call). 's' is the steady-state savings LEVEL at the same constant policy (docs
        eq:initialState:s): not part of the pre-determined state proper, but §6's initial fixed point
        needs both at the same τ, so it is passed through here rather than re-solved. """
        t = self.B.tFirst if t is None else t
        ss = self.steadyState_CRRA_solve(τ, θ, t = t, **kwargs)
        Γs, B = ss['Γs'], ss['B']
        B0 = self.B.B0SteadyState(Γs, τ, θ, t)
        si_s = self.B.si_s(B, τ, θ, Γs, t)
        ι = self.B.s0_s(B0, ss['Θs'], τ, ε, t)
        return {'Γs': Γs, 'B': B, 'B0': B0, 'si_s': si_s, 'ι': ι, 's': ss['s']}


    #######################################################################
    ##########   6. The initial state of the path (docs §PEEpath)     ######
    #######################################################################
    # policy.py identifies policy FUNCTIONS, not a path: each period returns τ_t as a function of the
    # state inherited from t-1. Turning that into an equilibrium takes two steps, both shared by LOG and
    # CRRA -- pin the state entering the first period (here), then walk the functions forward
    # (policy.py's approximatePEE). §7's solvePEE_* then re-solve the economic equilibrium EXACTLY at the
    # resulting τ: the simulation supplies the tax path and a warm start, never the reported allocation.

    def initialStatePEE(self, sols, θ, ε, preferences, t = None, τGrid = None, tol = 1e-10, **kwargs):
        """ Docs eq:initialFixedPoint: the scalar fixed point pinning the state that enters db['t'][0].

        Under the steady-state assumption of §5, the generation already old in the first active period
        behaved as if it had always faced the policy it meets there -- so (ι_0, s_0) are functions of τ_1
        alone (§5's initialState_solve). But τ_1 is itself what the solved policy function chooses at that
        state, which is what makes this a fixed point rather than a substitution.

        The search runs over τ_1, not over the states: τ_1 has known bounds [l,u], whereas a bracket for
        ι_0 or s_0 would have to come from the same steady-state map being inverted.

        It is a grid scan followed by brentq on the bracketing cell, NOT brentq on [l,u], and the
        difference is not stylistic. The residual is NaN wherever (s_0,ι_0) leaves the state grids the
        policy functions were solved on -- past which τPolicy extrapolates, so a crossing there is an
        artefact of the extrapolation rather than an equilibrium. That region is real and adjacent: as
        τ→1 formal savings collapse and ι_0 = s_0^0/s_0 diverges (ι_0 ~ 5e3 at τ=u on the Argentina
        calibration), and the extrapolated τPolicy that comes back is then clipped to u -- which plants
        an EXACT root at the upper bracket end, since the residual there is u - u = 0. brentq accepts
        that bracket and returns the endpoint, i.e. the degenerate steady state, without ever looking
        inside. Scanning first also reports genuine multiplicity instead of silently picking one.

        sols: policy.py's {t: report}. θ, ε: full length-T paths. preferences: 'LOG'/'CRRA' -- selects the
        policy class (its τ grid, and the arity of τPolicy). Under LOG, s_0 is not a political state at
        all and drops out of the residual; it is read off at the converged τ_1 to report levels. τGrid:
        the scan grid, defaulting to the policy class's own 𝒯. kwargs -> brentq.

        Returns {'τ','s','ι','residual','nRoots'}; the lowest root is taken when nRoots > 1. """
        if preferences not in ('LOG', 'CRRA'):
            raise ValueError(f"preferences must be 'LOG' or 'CRRA', got {preferences!r}.")
        t = self.B.tFirst if t is None else t
        isLOG = preferences == 'LOG'
        pol = getattr(self, preferences)
        settings = pol.GS['PEE']['gridSettings']
        l, u = settings['l'], settings['u']
        τPolicy = sols[t]['τPolicy']
        sGrid, ιGrid = (None if isLOG else sols[t]['s_']), sols[t]['ι_']
        τGrid = pol.GS['PEE']['solGrids']['τ'] if τGrid is None else np.asarray(τGrid)

        def state(τ):
            """ (s_0, ι_0) at a constant policy τ. ι_0 comes from initialState_solve, so the state walked
            from is exactly the ι_{-1} EE_report will later report. s_0 follows each preference case's own
            steady state, matching EE_LOG_solve/EE_CRRA_solve's own s0 defaults. """
            init = self.initialState_solve(τ, θ[t], ε[t], t = t)
            s = self.steadyState_LOG_solve(τ, θ[t], t = t)['s'] if isLOG else init['s']
            return s, init['ι']

        def residual(τ):
            s, ι = state(τ)
            if not (ιGrid[0] <= ι <= ιGrid[-1]) or (not isLOG and not (sGrid[0] <= s <= sGrid[-1])):
                return np.nan                      # extrapolated policy -- see the docstring
            return τ - np.clip(float(τPolicy(ι) if isLOG else τPolicy(s, ι)), l, u)

        r = np.array([residual(τ) for τ in τGrid])
        cross = np.isfinite(r[:-1]) & np.isfinite(r[1:]) & (np.sign(r[:-1]) != np.sign(r[1:]))
        if not cross.any():
            raise RuntimeError(
                f"initialStatePEE ({preferences}): eq:initialFixedPoint has no sign change on 𝒯 at a τ_1 "
                f"whose implied (s_0,ι_0) stays inside the state grids ({int(np.isfinite(r).sum())} of "
                f"{len(τGrid)} nodes admit one; residual ∈ [{np.nanmin(r):.3e}, {np.nanmax(r):.3e}]). "
                "Either the state grids are too narrow for the steady states 𝒯 implies, or no constant "
                "policy reproduces itself through the first period's policy function.")
        i = int(np.flatnonzero(cross)[0])
        τStar = optimize.brentq(residual, τGrid[i], τGrid[i + 1], **kwargs)
        res = residual(τStar)
        self._checkConverged(res, tol = tol, name = f'initialStatePEE ({preferences})')
        s, ι = state(τStar)
        return {'τ': τStar, 's': s, 'ι': ι, 'residual': res, 'nRoots': int(cross.sum())}

    #######################################################################
    ##########   7. Politico-economic equilibrium (PEE) solve         ######
    #######################################################################
    # End-to-end orchestrators, deliberately thin: policy functions (policy.py's solveBackward), initial
    # state (§6), forward walk (policy.py's approximatePEE), exact equilibrium at the resulting τ (§3).
    # The last step is not a polish -- the simulated allocation inherits both the grid resolution and the
    # interpolation error and satisfies the equilibrium conditions only approximately (docs §PEEpath,
    # "The simulated path is never reported directly"). Both return the same keys, so §8's calibration
    # drives either interchangeably.

    def solvePEE_LOG(self, θ = None, ε = None, s0 = None, ι0 = None,
                     backwardKwargs = None, pathKwargs = None):
        """ Solve the LOG politico-economic equilibrium end to end. θ, ε: full length-T paths; default to
        db['θ']/db['eps']. ι0: the political state entering db['t'][0]; defaults to §6's fixed point. s0:
        only a level under LOG (it is not a political state), so it may be left to the steady state at the
        walked τ_1 even when ι0 is given. backwardKwargs -> LOG.solveBackward, pathKwargs ->
        LOG.approximatePEE (strict=False to inspect a path that leaves 𝒮_0 instead of raising;
        exact=False to walk the reported state interpolants rather than re-solving the transition).

        Returns {'sols','path','init','τ','sol','report'}. Everything reported comes from the exact
        closed-form re-solve; 'path' is kept for the docs' grid diagnostic -- its simulated ι against
        report['ι'], which is the one error the first order condition residual cannot see. 'init' is §6's
        own dict (None when ι0 was supplied): it carries nRoots, the branch diagnostic §8 has to watch,
        since a calibration that steps between branches of eq:initialFixedPoint shows up as a
        discontinuous outer residual rather than as an error. """
        θ = self.db['θ'].values if θ is None else θ
        ε = self.db['eps'].values if ε is None else ε
        sols = self.LOG.solveBackward(θ, ε, **(backwardKwargs or {}))
        init = None
        if ι0 is None:
            init = self.initialStatePEE(sols, θ, ε, 'LOG')
            ι0 = init['ι']
            s0 = init['s'] if s0 is None else s0
        path = self.LOG.approximatePEE(sols, θ, ε, ι0, **(pathKwargs or {}))
        τ = path['τ'].values
        if s0 is None:
            s0 = self.steadyState_LOG_solve(τ[self.B.tFirst], θ[self.B.tFirst], t = self.B.tFirst)['s']
        sol = self.EE_LOG_solve(τ, θ, ε, s0)
        report = self.EE_report(sol, τ, θ, ε, s0)
        return {'sols': sols, 'path': path, 'init': init, 'τ': path['τ'], 'sol': sol, 'report': report}

    def solvePEE_CRRA(self, θ = None, ε = None, s0 = None, ι0 = None, warmStart = True,
                      backwardKwargs = None, pathKwargs = None, solveKwargs = None):
        """ Solve the CRRA politico-economic equilibrium end to end. As solvePEE_LOG, with both states
        walked forward and the exact step a root-find rather than a closed form. s0/ι0 default jointly to
        §6's fixed point -- unlike the LOG case s_0 IS a political state here, so it enters the residual.

        warmStart: build EE_CRRA_solve's x0 from the simulated (Γ_{s,t}, h_t, s_t) rather than its own
        default (the LOG closed form, exact only at ρ=1) -- scoped to this call, and overridden by
        solveKwargs={'x0': ...}. 'init' is reported for the same reason as in solvePEE_LOG. """
        θ = self.db['θ'].values if θ is None else θ
        ε = self.db['eps'].values if ε is None else ε
        sols = self.CRRA.solveBackward(θ, ε, **(backwardKwargs or {}))
        init = None
        if s0 is None or ι0 is None:
            init = self.initialStatePEE(sols, θ, ε, 'CRRA')
            s0 = init['s'] if s0 is None else s0
            ι0 = init['ι'] if ι0 is None else ι0
        path = self.CRRA.approximatePEE(sols, θ, ε, s0, ι0, **(pathKwargs or {}))
        τ = path['τ'].values
        kwargs = dict(solveKwargs or {})
        if warmStart and 'x0' not in kwargs:
            kwargs['x0'] = np.concatenate([path['Γs'], path['h'], path['s']])
        sol = self.EE_CRRA_solve(τ, θ, ε, s0, **kwargs)
        report = self.EE_report(sol, τ, θ, ε, s0)
        return {'sols': sols, 'path': path, 'init': init, 'τ': path['τ'], 'sol': sol, 'report': report}

    #######################################################################
    ##########   8. Calibration (docs §calibration, eq:calibration)   ######
    #######################################################################
    # Nested fixed point: outer root over (β,ω,η0,X0) against eq:calibration's four targets; each residual
    # evaluation refreshes the auxiliary parameters and re-solves the whole PEE (inner loop). ηi/Xi/θ are
    # NOT here -- fixed once in §2, independent of (β,ω,η0,X0).

    _calPars = ('β', 'ω', 'η0', 'X0')
    # Unbounded reparameterization below: finite upper bound -> logit, infinite -> log. Only positivity is
    # enforced -- β is NOT capped at 1 (simpleβ sets βj=β·p_j, the actual discount factor; the Argentina
    # savings-rate target needs β≈1.3, and a (0,1) cap makes the search stall on the bound rather than fail).
    _calBounds = {k: (0., np.inf) for k in _calPars}

    # Per-solver overrides for the outer root, merged under the caller's kwargs by calibrate. Deliberately
    # EMPTY: both solvers now run at scipy's own finite-difference step.
    #
    # It held {'CRRA': {'options': {'eps': 1e-4}}} until 2026-08-19. That existed for one reason -- at
    # ρ=1.1, 45x45, the η0 column of the Jacobian came out at 5.13 against a resolved 0.99, and one
    # corrupted column is enough to derail the Newton direction. The corruption was the adaptive-knot
    # smoother's residual jumps being straddled at that particular step, not a property of the residual, so
    # smoothKnots removed it at source: re-measured at the converged ρ=0.7 and ρ=0.9 points, every column
    # is flat to 0.01% from 1.5e-8 through 1e-4 and within 0.6% at 1e-2. Calibrating at each candidate from
    # a common start then converges in the same evaluation count (12 at ρ=0.9, 14 at ρ=0.7) to the same
    # parameters to 3.7e-10, with scipy's default reaching the TIGHTEST final residual of the three -- so a
    # larger step is now a small accuracy cost with no benefit to trade against it.
    #
    # Kept as an empty dict rather than deleted: the per-solver hook is the right place for the next such
    # finding, and an empty one records that the split between LOG and CRRA was retracted on evidence
    # rather than never considered. deviations note items 11+13, now one finding.
    _calOuterKwargs = {}

    @property
    def calibrationPars(self):
        """ (β,ω,η0,X0) as db currently holds them. Inverse of _calSetPars. """
        t0 = self.db['t'][self.db['t0']]
        return {'β': self.simpleβinv(), 'ω': self.db['ω'].xs(t0),
                'η0': self.db['η0'].xs(t0), 'X0': self.db['X0'].xs(t0)}

    def _calToX(self, pars):
        """ Calibration-parameter dict -> unbounded search vector. """
        def f(k):
            l, u = self._calBounds[k]
            v = pars[k]
            return np.log(v-l) if np.isinf(u) else np.log((v-l)/(u-v))
        return np.array([f(k) for k in self._calPars])

    def _calFromX(self, x):
        """ Inverse of _calToX. """
        def f(k, xi):
            l, u = self._calBounds[k]
            return l+np.exp(xi) if np.isinf(u) else l+(u-l)/(1+np.exp(-xi))
        return {k: f(k, xi) for k, xi in zip(self._calPars, x)}

    def _calSetPars(self, pars):
        """ Write (β,ω,η0,X0) into db and refresh dependent auxiliary parameters (eps via β, κ via eps).
        η0/X0 go in via the full ηj/Xj frames, not db['η0']/db['X0'] alone -- adjPar would otherwise leave
        column 0 of ηj/Xj stale. """
        self.db.update(self.adjPar('β', pars['β']))
        self.db.update(self.adjPar('ω', pars['ω']))
        for k, v in (('ηj', pars['η0']), ('Xj', pars['X0'])):
            df = self.db[k].copy()
            df[df.columns[0]] = v
            self.db.update(self.adjPar(k, df.values))
        self.updateAuxPars()

    def calibration_report(self, pars, preferences, solveKwargs = None):
        """ Install `pars`, solve the PEE, evaluate eq:calibration's four target quantities at db['t0'].
        Θh is recovered from the solved (h,s_) via Base.ΘhFromH -- one expression covers LOG/CRRA and the
        general/terminal formulas alike. The savings rate comes back too: it is no longer targeted (KY
        replaced it, 2026-08-24) but it is what the paper's tables report and what every result before
        that date was fitted to. solveKwargs must not pin θ/ε: they need to stay at their None
        defaults so solvePEE_* re-reads db['θ']/db['eps'] after _calSetPars refreshes them (the channel
        through which β reaches ε/κ). """
        self._calSetPars(pars)
        out = getattr(self, f'solvePEE_{preferences}')(**(solveKwargs or {}))
        t0 = self.db['t'][self.db['t0']]
        rep, τ = out['report'], out['τ'].xs(t0)
        h, s, s_ = rep['h'].xs(t0), rep['s'].xs(t0), rep['s_'].xs(t0)
        Θh = self.B.ΘhFromH(h, s_, t0)
        η0 = self.B.calibrationη0(Θh, τ, t0)
        return {'KY': self.B.capitalOutputRatio(s_, h, t0), 'τ': τ, 'Θh': Θh,
                'sr': self.B.savingsRate(s, s_, h, t0),
                'η0': η0, 'X0': self.B.calibrationX0(η0, Θh, t0), 'PEE': out}

    def _calResidual(self, report, pars):
        """ eq:calibration's four targets as a residual on an already-evaluated calibration_report. One
        entry per element of _calPars, same order.

        KY enters relatively and τ as a level gap, so the two carry the same O(0.1) magnitude and the root
        finder cannot trade accuracy in one for the other -- the same form the US arm uses for its R
        target, and the reason KY cannot be a level gap: it is O(3.6) against τ's O(0.1). η0/X0 are
        relative because a relative gap is the natural form for a self-consistency condition; at the
        calibrated point they are O(0.3-0.4), so that choice is close to immaterial either way. The two
        are in any case nearly solved by substitution -- see README §8.1 on their 0.00%/0.02% spread
        over ρ.

        Split out so a change of targets happens in exactly one place: `calibrate` re-forms the residual
        at the converged point and the two must not be able to drift apart. """
        return np.array([report['KY']/self.db['KY0'] - 1, report['τ'] - self.db['τ0'],
                         report['η0']/pars['η0'] - 1, report['X0']/pars['X0'] - 1])

    def calibration_residual(self, x, preferences, solveKwargs = None):
        """ eq:calibration as a residual on the unbounded vector -- one full PEE solve per evaluation. """
        pars = self._calFromX(x)
        return self._calResidual(self.calibration_report(pars, preferences, solveKwargs), pars)

    def calibrate(self, preferences = None, x0 = None, tol = 1e-6, update = True,
                  solveKwargs = None, **kwargs):
        """ Solve eq:calibration for (β,ω,η0,X0): one 4-D root, each evaluation a full PEE solve.
        preferences defaults to 'LOG' iff ρ=1 (CRRA's recursion divides by 1-1/ρ). x0 defaults to
        self.x0['calibration'] if cached, else db's current parameters. kwargs -> scipy.optimize.root,
        merged over _calOuterKwargs[preferences] (the caller wins on any top-level key, so passing
        options={...} replaces a per-solver default rather than merging into it). That dict is currently
        empty -- both solvers run at scipy's own finite-difference step; see it for the measurement that
        retired the CRRA override.

        tol is looser than the inner solves' (EE 1e-8, steady state 1e-11) on purpose: those are exact
        root problems, whereas eq:calibration's targets are read off a path that reached them through two
        grid searches and a chain of interpolants, so the residual is only meaningful down to what the
        grids resolve. There is a floor on how far this may be relaxed, and it is not far below 1e-6:
        the inner grid resolves the outer answer to ~1e-4 in the parameters and no better, measured by
        refining it at fixed parameters (deviations note item 12); a tol at that scale would be reading
        grid noise as a root.

        db is mutated as the search proceeds; restored to its entry state on any failure (a shallow copy
        suffices -- adjPar/updateAuxPars always rebind db keys rather than mutate in place). On success db
        is left holding the converged parameters and equilibrium. """
        if preferences is None:
            preferences = 'LOG' if self.db['ρ'].xs(self.db['t'][self.db['t0']]) == 1 else 'CRRA'
        if x0 is None:
            x0 = self.x0.get('calibration', self._calToX(self.calibrationPars))
        kwargs = self._calOuterKwargs.get(preferences, {}) | kwargs   # caller wins, per top-level key
        snapshot = dict(self.db)
        try:
            res = optimize.root(self.calibration_residual, x0, args = (preferences, solveKwargs), **kwargs)
            pars = self._calFromX(res.x)
            report = self.calibration_report(pars, preferences, solveKwargs)
            residual = self._calResidual(report, pars)
            self._checkConverged(residual, tol = tol, name = 'calibrate', scipyRes = res)
        except Exception:
            self.db.clear() # self.B/BG/BT hold a reference to this dict, so restore in place
            self.db.update(snapshot)
            raise
        if update:
            self.x0['calibration'] = res.x
        return {'pars': pars, 'x': res.x, 'residual': residual, 'report': report, 'scipyRes': res}

    #######################################################################
    ##########   8.1. Calibration over a grid of parameter values    ######
    #######################################################################
    # A calibration costs ~26 PEE solves, so a grid of them is bought one warm start at a time. The
    # continuation logic (visit order, extrapolation, step-halving) is model-agnostic and lives in
    # gridsearch.continuation; what is here is only the part that knows what a calibration *is*.

    def _calPreferences(self):
        """ Which solver eq:calibration's inner loop uses at db's current ρ. Mirrors calibrate's own
        default -- CRRA's recursion divides by 1-1/ρ and its guard refuses ρ=1 -- and is needed separately
        because the *grid settings* have to be installed on that solver before calibrate is called. """
        return 'LOG' if self.db['ρ'].xs(self.db['t'][self.db['t0']]) == 1 else 'CRRA'

    @staticmethod
    def _calGridSettings(gridSettings, preferences):
        """ Resolve calibratePoint's gridSettings for the solver actually in use. A flat dict applies to
        whichever solver runs; a dict keyed by 'LOG'/'CRRA' selects per solver, which is what a march
        across ρ generally wants -- only the CRRA calibration needs a grid finer than its own PEE default
        (README, "The CRRA calibration needs a finer inner grid than the CRRA solve"), and imposing that
        number on the LOG solver silently moves it off its documented default of nι=50 instead. """
        if gridSettings and set(gridSettings) & {'LOG', 'CRRA'}:
            return gridSettings.get(preferences)
        return gridSettings

    def _calVerify(self, x, preferences, policy, verify, gridSettings):
        """ Re-evaluate the outer residual at the converged x on a finer inner grid, and restore the
        working grid afterwards. Returns max|residual|, or NaN if the refined solve fails.

        This is the one diagnostic that separates a converged calibration from a *correct* one: the outer
        root can settle on a point that is displaced rather than merely imprecise, and the symptom is that
        refining the inner grid at fixed parameters leaves the residual on a plateau instead of decaying.

        Read the LEVEL across points, not the shape within one: the rung at the calibration's own grid is
        ~1e-12 by construction, so any within-point sequence starts by rising. Deviations item 17 measured
        the level this now sits at -- 2e-5..1e-4 at nι=ns=45, which is also the floor of what the outer
        answer is determined to, so a point an order of magnitude above that is the one to look at.
        Recorded per point rather than asserted: 45 has no standing at every ρ. """
        try:
            policy.initGS((gridSettings or {}) | verify)
            return float(np.max(np.abs(self.calibration_residual(x, preferences))))
        except Exception:
            return np.nan
        finally:
            policy.initGS(gridSettings)

    @staticmethod
    def _calOccupancy(policy, pee, seedPad = (0.5, 2.0)):
        """ Fraction of each state grid's nodes that lie in the region the dynamics actually reach, seeded
        from the solved path's own range widened by seedPad (policy.reachableBox/gridOccupancy -- free,
        they only re-read what the solve stored).

        Recorded, never acted on, exactly like verifyResidual: a grid that is too narrow announces itself
        (states outside it are reported infeasible, never clipped), but one that is too WIDE is silent and
        merely spends its resolution where no path goes. This is the column that makes that visible, and
        the input to an offline retune of the grid RULE -- see policy.py's grid-placement diagnostics on
        why the retune must not be automatic. Returns {} rather than raising: a diagnostic must never be
        the reason a calibration fails. """
        try:
            rep = pee['report']
            seed = {}
            for name, key in (('ι', 'ι'), ('s', 's_')):
                if key in rep:
                    v = np.asarray(rep[key], dtype = float)
                    v = v[np.isfinite(v) & (v > 0)]
                    if v.size:
                        seed[name] = (seedPad[0]*v.min(), seedPad[1]*v.max())
            box = policy.reachableBox(pee['sols'], seed = seed)
            occ = policy.gridOccupancy(pee['sols'], box or {})
            return {f'occupancy{k}': round(v['frac'], 4) for k, v in occ.items()}
        except Exception:
            return {}

    def calibratePoint(self, value, x0 = None, par = 'ρ', gridSettings = None, verify = None,
                       calKwargs = None):
        """ Set db[par] = value, then calibrate there. Returns one flat record: the calibrated parameters,
        the unbounded x (which is what seeds the next point -- see calibrateGrid), max|residual|, the four
        target quantities, and the diagnostics a sweep has to be readable by afterwards (ι at t0, the
        initial fixed point's nRoots, scipy's nfev, wall time, and the inner grid actually used).

        x0 is the *unbounded* vector, not a parameter dict. gridSettings -> the active policy's initGS and
        verify -> _calVerify's refined settings (None to skip), both flat or keyed by 'LOG'/'CRRA' (see
        _calGridSettings -- keyed is what a march over ρ normally wants). db is left holding the converged
        point, which is deliberate: it is the next point's inner warm start. """
        self.db.update(self.adjPar(par, value))
        preferences = self._calPreferences()
        policy = getattr(self, preferences)
        settings = self._calGridSettings(gridSettings, preferences)
        policy.initGS(settings)
        tStart = time.time()
        cal = self.calibrate(preferences = preferences, x0 = x0, **(calKwargs or {}))
        elapsed = time.time()-tStart
        t0 = self.db['t'][self.db['t0']]
        rep, init = cal['report'], cal['report']['PEE']['init']
        rec = {par: float(value), 'preferences': preferences, 'x': cal['x'], 'time': elapsed,
               'residual': float(np.max(np.abs(cal['residual']))),
               'KY': float(rep['KY']), 'sr': float(rep['sr']), 'τ': float(rep['τ']),
               'ι': float(rep['PEE']['report']['ι'].xs(t0)),
               'nfev': int(getattr(cal['scipyRes'], 'nfev', -1)),
               'nRoots': None if init is None else int(init['nRoots']),
               'gridSettings': dict(policy.GS['PEE']['gridSettings'])}
        rec.update({k: float(v) for k, v in cal['pars'].items()})
        rec.update(self._calOccupancy(policy, cal['report']['PEE']))
        verifySettings = self._calGridSettings(verify, preferences) if verify else None
        if verifySettings:
            rec['verifyResidual'] = self._calVerify(cal['x'], preferences, policy, verifySettings, settings)
        return rec

    def calibrateGrid(self, grid, par = 'ρ', anchor = 1.0, gridSettings = None, verify = None,
                      x0 = None, degree = 1, maxHalvings = 2, onPoint = None, calKwargs = None,
                      **kwargs):
        """ Calibrate at every value of `grid`, marching outward from `anchor` (gridsearch.continuation's
        marchGrid -- see it for the extrapolation and failure-recovery contract; kwargs pass through).

        anchor defaults to ρ=1, which is the point of the default: it is the only value where the LOG
        solver applies, so it is both the cheapest calibration on the grid and the only one that needs no
        warm start at all. Every other point is seeded from its neighbours in the *unbounded* coordinate,
        where extrapolation cannot step a positivity-constrained parameter across its bound.

        The march runs on this one instance, so each point also inherits db's converged parameters as its
        inner warm start; that is separate from, and additional to, the extrapolated x0.

        onPoint(record) fires after every point including failures -- pass a writer here, since a sweep
        this long is one crash away from losing everything solved so far. """
        def solve(value, xStart):
            return self.calibratePoint(value, x0 = xStart, par = par, gridSettings = gridSettings,
                                       verify = verify, calKwargs = calKwargs)
        return continuation.marchGrid(grid, solve, x0 = x0, anchor = anchor, degree = degree,
                                      maxHalvings = maxHalvings, onPoint = onPoint, **kwargs)

    #######################################################################
    ##########   9. Model copies for shock experiments (docs' t0)     ######
    #######################################################################
    # createCopyFromt0 produces a new, independent model instance whose horizon is restricted to
    # db['t'] >= t0 -- for "unexpected shock" experiments: solve the baseline PEE over the full horizon,
    # build the copy, then re-solve PEE on it with (s0, ι0) (stateAtT0) read off the baseline's own
    # report at t0. The copy's own db['t'] is renumbered to start at 0 again (see _sliceDb's docstring
    # for why -- model.py's own EE_LOG_solve/EE_CRRA_solve/EE_report/initialState_solve index a caller's
    # τ/θ/ε ndarrays positionally via self.B.tFirst, which only works when tFirst is 0), so
    # self.B.tFirst on the copy is 0, not t0 -- the original calendar year t0 is not retained anywhere
    # on the copy. State seeding is deliberately NOT done here -- s0/ι0 stay explicit arguments to
    # solvePEE_LOG/solvePEE_CRRA on the copy, exactly as for any other instance; see stateAtT0.
    def createCopyFromt0(self, t0):
        """ Return an independent copy of this model with its time horizon restricted to db['t'] >= t0
        and renumbered to start at 0 (db['t'] runs 0..T-t0-1 on the copy, not t0..T-1).
        Warm-start caches (self.x0, self.LOG.x0, self.CRRA.x0) are cleared (stale/wrong length for the
        new horizon); self.LOG.GS/self.CRRA.GS (state-space grids, not time-indexed) are left as-is.
        db['t0'] (the calibration-baseline-year *position* -- unrelated to this t0; see
        default0DParams' docstring) is shifted by -t0 if the calibration year still falls inside the new
        horizon, else set to None: a stale position would otherwise silently resolve to the wrong year
        rather than failing loudly. Recalibrating a copy needs a caller-supplied db['t0']. """
        if t0 not in self.db['t']:
            raise ValueError(f"t0={t0!r} is not in db['t'] (={list(self.db['t'])}).")
        mt0 = deepcopy(self)
        _sliceDb(mt0.db, t0)
        mt0.T = len(mt0.db['t'])
        for baseIns in (mt0.B, mt0.BG, mt0.BT):
            baseIns.tFirst = mt0.db['t'][0]
        mt0.LOG.T = mt0.CRRA.T = mt0.T
        mt0.x0, mt0.LOG.x0, mt0.CRRA.x0 = {}, {}, {}
        mt0.addNamespaces()
        mt0.db['t0'] = (self.db['t0'] - t0) if (self.db['t0'] is not None and self.db['t0'] >= t0) else None
        return mt0

    def stateAtT0(self, report, t0, init = None):
        """ The state (s0, ι0) entering t0 in an already-solved report (solvePEE_LOG/solvePEE_CRRA's
        'report'), for seeding createCopyFromt0(t0)'s own solvePEE_LOG(s0=,ι0=)/solvePEE_CRRA(s0=,ι0=).

        ι is reported on the txE domain as ι_t for t=0..T-2 (_txE2vars), NOT lagged like s_ -- so the
        state entering t0 is report['ι'].xs(t0-1), except at t0 == db['t'][0] itself, where t0-1 has no
        entry and the value is instead the model's own initial-state proxy, init['ι'] (pass the 'init'
        key already returned by solvePEE_LOG/CRRA rather than recomputing it). """
        s0 = report['s_'].xs(t0)
        ι0 = init['ι'] if t0 == self.db['t'][0] else report['ι'].xs(t0 - 1)
        return {'s0': s0, 'ι0': ι0}
