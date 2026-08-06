import numpy as np, pandas as pd, functools, scipy
from scipy import optimize
from copy import deepcopy
from symMaps import SimpleSys, Lag, Lead
from base import Base, BaseGrid, BaseTime
from policy import LOG, CRRA


class ModelInformalAnalytical:
    _BaseClass = Base
    _BaseGridClass = BaseGrid
    _BaseTimeClass = BaseTime
    _PolicyLogClass = LOG
    _PolicyCRRAClass = CRRA

    def __init__(self, nj = 4, T = 10, pars = None, **kwargs):
        """ Analytical model with informal households.
        
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
        - 's0' here is a *calibration target for the aggregate savings rate* (a ratio, e.g. 0.184 = 18.4%,
          matched at db['t0'] below) -- NOT the `s0` function argument used throughout EE_LOG_solve/
          EE_CRRA_solve/steadyState_*/policy.py (the *level* of savings at the pre-determined period before
          db['t'][0], i.e. docs' s_0).
        - 't0' here is the *index into db['t'] of the calibration baseline year* (e.g. 2010 in the real
          Argentina calibration; defaults to 2, an arbitrary early index) -- NOT self.B.tFirst (=db['t'][0],
          the model's first active/endogenous period, docs' t=1) and NOT the pre-determined period before
          the horizon (docs' t=0). All three are genuinely different things. """
        return {'τ0': .125, 'RR0': 0.678/0.803, 's0': 0.184, 'RRGroups': (1,2), 't0': 2}

    @property
    def default1Dparams(self):
        """ 1d vectors - defined over t """
        return {'α': .43, 'ν': 1, 'ξ' : .3, 'ρ': 1, 'ω': 1.25, 'α0': 1, 'χ': 1}
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
    # Style per numerical problem: (i) a residual method, (ii) a solve method returning just the core
    # solution ({'s','h','Γs','B'}), (iii) a shared report method expanding it via base.py. τ,θ,ε,s0
    # always explicit (never read from db).
    #
    # Timing (README's "Timing convention" for the full version): db['t'] (0..T-1) is the docs' t=1..T.
    # s0 (this section's argument, NOT db['s0'] -- an unrelated calibration target for the savings rate)
    # is the state before db['t'][0] (docs' t=0). Terminal period is db['t'][-1] (docs' t=T).
    #
    # Terminal-period convention: Γs/B/si_s report at natural length T-1 (no Γ_{s,T}/B_T^i -- no period
    # T+1 to look into); h/s stay length T (s_{T-1}=0 is a real terminal condition, not missing). Use
    # base.py's FH_* methods wherever a T-length quantity needs Γs/B/si_s alongside it.
    #
    # EE_LOG_solve/EE_CRRA_solve/EE_report return plain ndarrays internally, wrapping into pd.Series/
    # DataFrame only in the final return (_wrapVars, keyed off _t2vars/_txE2vars below) -- so the T-vs-T-1
    # domain is visible from the index rather than an array's bare length, declared once here rather than
    # per method. Not done inside base.py's own methods (incl. FH_*): those run inside EE_CRRA_solve's
    # root-finding loop, where pandas' per-call overhead would be pure cost.

    # Which pandas index a symbol reports over -- a fixed, once-per-model mapping.
    _t2vars = ('s', 'h', 's_', 'R', 'w', 'w0', 'hi', 'bbar', 'bi', 'b0',
               'c1i', 'tildec1i', 'c2i', 'tildec2i', 'c10', 'tildec10', 'c20', 'tildec20')
    _txE2vars = ('Γs', 'B', 'si_s')

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
        everything downstream of (s,h,Γs,B) is identical regardless of origin. Γs/B/si_s come back at
        length T-1; everything else (incl. 's_'=s_{t-1} and 'h_', backed out via §5's
        initialState_solve) is length T. """
        s, h, Γs, B = sol['s'].values, sol['h'].values, sol['Γs'].values, sol['B'].values
        s_ = np.append(s0, s[:-1])
        τ1, θ1 = self.leadSym(τ), self.leadSym(θ)
        init = self.initialState_solve(τ[self.B.tFirst], θ[self.B.tFirst])
        h_ = np.append(self.B.hFromS(s0, init['Γs'], self.B.tFirst), h[:-1])

        R, w, w0 = self.BT.R(s_, h), self.BT.w(s_, h), self.BT.w0(s_)
        hi = self.BT.hi(h)
        bbar = self.BT.bbar(τ, w, h, h_)
        bi = self.BT.bi(θ, bbar, h_)
        b0 = self.BT.b0(ε, bbar, h_)

        # si_s has no terminal-period counterpart at all (s_{T-1}=0 makes the ratio 0/0), so we pad with a
        # nonzero dummy purely to dodge the resulting divide-by-zero warning, then drop that entry (unlike
        # FH_c1i/FH_tildec1i's 0-padding, this dummy carries no economic meaning -- it's discarded, not used).
        B_dummy, Γs_dummy = np.vstack([B, np.ones((1, self.ni))]), np.append(Γs, 1)
        si_s = self.BT.si_s(B_dummy, τ1, θ1, Γs_dummy)[:-1]
        si_s_ = np.vstack([init['si_s'][None, :], si_s])

        c1i = self.BT.FH_c1i(h, s, B, τ1, θ1)
        tc1i = self.BT.FH_tildec1i(h, B, τ1, θ1, Γs)
        c2i = self.BT.c2i(h, s_, τ, θ, si_s_)
        tc2i = self.BT.tildec2i(h, s_, τ, θ, si_s_)
        c10, tc10 = self.BT.c10(s_), self.BT.tildec10(s_)
        c20, tc20 = self.BT.c20(h, s_, ε, τ), self.BT.tildec20(h, s_, ε, τ)

        return self._wrapVars({'s': s, 'h': h, 's_': s_, 'R': R, 'w': w, 'w0': w0, 'hi': hi, 'bbar': bbar, 'bi': bi, 'b0': b0,
                                'c1i': c1i, 'tildec1i': tc1i, 'c2i': c2i, 'tildec2i': tc2i,
                                'c10': c10, 'tildec10': tc10, 'c20': c20, 'tildec20': tc20,
                                'Γs': Γs, 'B': B, 'si_s': si_s})

    #######################################################################
    ##########   4. Steady state solve (docs §2.1, eq:steadystate_*)  ######
    #######################################################################
    # Steady state = fixed point s_t=s_{t-1}=s* under a *constant* policy (τ,θ), at db['t'][0]'s
    # parameters ("Initializing with steady state savings"). Default s0 for EE_LOG_solve/EE_CRRA_solve.
    # steadyState_report exposes {'Γs','B','s','h','Θs'}, shared by both LOG and CRRA (same Θh/Θs/
    # sSteadyState/h chain past Γs/B).
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
        recommendation). bounds default (0, 0.75): the doc notes Γs is practically always inside this
        range (e.g. exactly B/((1+B)(1+ξ)) when B is constant across types). """
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
    # βi exactly at ρ=1, so one method serves both cases) and si_s are pure functions of (τ,θ) and
    # primitives, never of the savings level. h_{-1} is the one exception that does need s0 (via
    # Base.hFromS) -- computed separately in EE_report, not bundled here.
    def initialState_solve(self, τ, θ, t = None, **kwargs):
        """ Identify Γ_{s,-1}, B_{-1}^i, s_{-1,i}/s_{-1} -- see §5 header. τ, θ: scalars, db['t'][0]'s own
        policy. kwargs passed to steadyState_CRRA_solve. Returns {'Γs','B','si_s'} -- no h_{-1} (needs the
        actual s0; see EE_report's Base.hFromS call). """
        t = self.B.tFirst if t is None else t
        ss = self.steadyState_CRRA_solve(τ, θ, t = t, **kwargs)
        Γs, B = ss['Γs'], ss['B']
        si_s = self.B.si_s(B, τ, θ, Γs, t)
        return {'Γs': Γs, 'B': B, 'si_s': si_s}

    #######################################################################
    ##########   6. Politico-economic equilibrium (PEE) solve, LOG    ######
    #######################################################################
    # End-to-end orchestrator: identify τ via policy.py's LOG class, then solve/report the full economic
    # equilibrium it implies. Deliberately thin -- all the actual work is delegated: self.LOG.solveVectorized
    # (no s0 needed, see policy.py) for τ, then EE_LOG_solve/EE_report (§3) for the equilibrium.
    def solvePEE_LOG(self, θ = None, ε = None, s0 = None, solver = 'Robust', **kwargs):
        """ Solve the LOG politico-economic equilibrium end to end. θ, ε: full length-T paths; default to
        db['θ']/db['eps']. s0: if None, the LOG steady state at db['t'][0], evaluated at the *solved*
        τ[db['t'][0]]. Returns {'policy','sol','report'}.

        solver picks which policy.py method identifies τ:
        - 'Robust'     (default) LOG.solveRobust -- gradient solve (alg:fast), falling back to the
                       backward grid search + warm-started gradient polish if it fails (e.g. a high
                       political weight ω moves the solution far from the constant-db['τ0'] guess).
        - 'Vectorized' LOG.solveVectorized alone. Fails loudly rather than falling back.
        - 'Backward'   LOG.solveBackward alone. Capped at grid resolution -- for diagnosing the FOC. """
        if θ is None:
            θ = self.db['θ'].values
        if ε is None:
            ε = self.db['eps'].values
        if solver not in ('Robust', 'Vectorized', 'Backward'):
            raise ValueError(f"solver must be 'Robust', 'Vectorized' or 'Backward', got {solver!r}.")
        policy = getattr(self.LOG, f'solve{solver}')(θ, ε, **kwargs)
        τ = policy['τ'].values
        if s0 is None:
            s0 = self.steadyState_LOG_solve(τ[self.B.tFirst], θ[self.B.tFirst], t = self.B.tFirst)['s']
        sol = self.EE_LOG_solve(τ, θ, ε, s0)
        report = self.EE_report(sol, τ, θ, ε, s0)
        return {'policy': policy, 'τ': policy['τ'], 'sol': sol, 'report': report}

    #######################################################################
    ##########   7. Politico-economic equilibrium (PEE) solve, CRRA   ######
    #######################################################################
    # solvePEE_LOG's s0 default doesn't survive to CRRA: it reads τ[db['t'][0]] off the *solved* τ path,
    # which only works because LOG's τ never depends on s. CRRA's τ_{tFirst}=τPolicy_{tFirst}(s0) is
    # itself a function of the state being determined, so "solve τ, then read off τ[tFirst]" is circular.
    # steadyStatePEE_CRRA replaces it.
    def steadyStatePEE_CRRA(self, sols, θ, t = None, bounds = None, tol = 1e-10, **kwargs):
        """ solvePEE_CRRA's default s0: the (τ*, s*) fixed point where τ* is both the constant-policy
        steady-state tax (self.steadyState_CRRA_solve) and what the solved policy function would choose
        at that steady state:
        Returns the full steady-state report ({'Γs','B','s','h','Θs'}), not just 's'. """
        t = self.B.tFirst if t is None else t
        θt = θ[t]                                            # scalar -- θ is the full length-T path here
        l, u = self.CRRA.GS['PEE']['gridSettings']['l'], self.CRRA.GS['PEE']['gridSettings']['u']
        bounds = (l, u) if bounds is None else bounds
        τPolicy = sols[t]['τPolicy']
        def residual(τ):
            s = self.steadyState_CRRA_solve(τ, θt, t = t)['s']
            return τ - np.clip(τPolicy(s), l, u)
        τStar = optimize.brentq(residual, *bounds, **kwargs)
        self._checkConverged(residual(τStar), tol = tol, name = 'steadyStatePEE_CRRA')
        return self.steadyState_CRRA_solve(τStar, θt, t = t)

    def solvePEE_CRRA(self, θ = None, ε = None, s0 = None, warmStart = True,
                      backwardKwargs = None, solveKwargs = None):
        """ Solve the CRRA politico-economic equilibrium end to end (docs §PEE/alg:CRRA:grid): identify
        the backward-solved policy functions (CRRA.solveBackward), forward-simulate the tax path they
        imply from an initial state (CRRA.approximatePEE), then solve the equilibrium given that
        path (EE_CRRA_solve/EE_report).

        θ, ε: full length-T paths, as solvePEE_LOG. s0: if None, steadyStatePEE_CRRA's fixed point.
        warmStart: build EE_CRRA_solve's x0 from the forward-simulated (Γs,h,s) path instead of its own
        default (a LOG closed-form proxy, exact only at ρ=1) -- scoped to this call only; passing
        solveKwargs={'x0': ...} overrides it regardless.

        Returns {'sols','τ','sol','report'}: sols is CRRA.solveBackward's {t: report dict} ; τ is
        the path fed to EE_CRRA_solve; sol/report are its usual outputs. ('τ'/'sol'/'report' are named
        to match solvePEE_LOG's return, so §8's calibration can drive either one interchangeably.) """
        if θ is None:
            θ = self.db['θ'].values
        if ε is None:
            ε = self.db['eps'].values
        sols = self.CRRA.solveBackward(θ, ε, **(backwardKwargs or {}))
        if s0 is None:
            s0 = self.steadyStatePEE_CRRA(sols, θ)['s']
        path = self.CRRA.approximatePEE(sols, s0)
        kwargs = dict(solveKwargs or {})
        if warmStart and 'x0' not in kwargs:
            kwargs['x0'] = np.concatenate([path['Γs'], path['h'], path['s']])
        sol = self.EE_CRRA_solve(path['τ'].values, θ, ε, s0, **kwargs)
        report = self.EE_report(sol, path['τ'].values, θ, ε, s0)
        return {'sols': sols, 'τ': path['τ'], 'sol': sol, 'report': report}

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
        general/terminal formulas alike. solveKwargs must not pin θ/ε: they need to stay at their None
        defaults so solvePEE_* re-reads db['θ']/db['eps'] after _calSetPars refreshes them (the channel
        through which β reaches ε/κ). """
        self._calSetPars(pars)
        out = getattr(self, f'solvePEE_{preferences}')(**(solveKwargs or {}))
        t0 = self.db['t'][self.db['t0']]
        rep, τ = out['report'], out['τ'].xs(t0)
        h, s, s_ = rep['h'].xs(t0), rep['s'].xs(t0), rep['s_'].xs(t0)
        Θh = self.B.ΘhFromH(h, s_, t0)
        η0 = self.B.calibrationη0(Θh, τ, t0)
        return {'sr': self.B.savingsRate(s, s_, h, t0), 'τ': τ, 'Θh': Θh,
                'η0': η0, 'X0': self.B.calibrationX0(η0, Θh, t0), 'PEE': out}

    def calibration_residual(self, x, preferences, solveKwargs = None):
        """ eq:calibration as a residual on the unbounded vector. sr/τ enter as level gaps (same O(0.1)
        magnitude); η0/X0 enter relatively (η0≈0.2, X0≈2.6 -- level gaps would let the root finder trade
        accuracy in one for the other). """
        pars = self._calFromX(x)
        d = self.calibration_report(pars, preferences, solveKwargs)
        return np.array([d['sr'] - self.db['s0'], d['τ'] - self.db['τ0'],
                         d['η0']/pars['η0'] - 1, d['X0']/pars['X0'] - 1])

    def calibrate(self, preferences = None, x0 = None, tol = 1e-8, update = True,
                  solveKwargs = None, **kwargs):
        """ Solve eq:calibration for (β,ω,η0,X0): one 4-D root, each evaluation a full PEE solve.
        preferences defaults to 'LOG' iff ρ=1 (CRRA's recursion divides by 1-1/ρ). x0 defaults to
        self.x0['calibration'] if cached, else db's current parameters. kwargs -> scipy.optimize.root.

        db is mutated as the search proceeds; restored to its entry state on any failure (a shallow copy
        suffices -- adjPar/updateAuxPars always rebind db keys rather than mutate in place). On success db
        is left holding the converged parameters and equilibrium. """
        if preferences is None:
            preferences = 'LOG' if self.db['ρ'].xs(self.db['t'][self.db['t0']]) == 1 else 'CRRA'
        if x0 is None:
            x0 = self.x0.get('calibration', self._calToX(self.calibrationPars))
        snapshot = dict(self.db)
        try:
            res = optimize.root(self.calibration_residual, x0, args = (preferences, solveKwargs), **kwargs)
            pars = self._calFromX(res.x)
            report = self.calibration_report(pars, preferences, solveKwargs)
            residual = np.array([report['sr'] - self.db['s0'], report['τ'] - self.db['τ0'],
                                 report['η0']/pars['η0'] - 1, report['X0']/pars['X0'] - 1])
            self._checkConverged(residual, tol = tol, name = 'calibrate', scipyRes = res)
        except Exception:
            self.db.clear() # self.B/BG/BT hold a reference to this dict, so restore in place
            self.db.update(snapshot)
            raise
        if update:
            self.x0['calibration'] = res.x
        return {'pars': pars, 'x': res.x, 'residual': residual, 'report': report, 'scipyRes': res}
