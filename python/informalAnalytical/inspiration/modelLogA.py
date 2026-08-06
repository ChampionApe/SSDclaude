import numpy as np, pandas as pd, functools, scipy
from scipy import optimize
from copy import deepcopy
from pyDbs import SymMaps as sm, adj
from baseLog import BaseLogA, BaseLogA_Grid, BaseLogA_Time
from auxFunctions import noneInit, defaultGrid, checkOpt
from policyLog import LogA

class ModelLogA:
    # Define the base classes used by this model variant
    _BaseClass = BaseLogA
    _BaseGridClass = BaseLogA_Grid
    _BaseTimeClass = BaseLogA_Time
    _PolicyClass = LogA

    def __init__(self, nj = 4, T = 10, pars = None, gridkwargs = None, ftol = None):
        """ Analytical model with informal households """
        self.nj, self.T = nj, T
        self.ni = self.nj-1
        self.addProperty('paramsFromFuncs', ['αr','Γh','θ','eps','κ'])
        self.db = {}
        self.parTypes = self._parTypes.copy()
        self.initIdxs() # add relevant pandas indices to database
        self.addNamespaces() # aux classes that help nagivate stacked vectors + lag/lead symbols.
        self.x0 = self._x0 # dictionary with initial values used in various numerical problems.
        self.B = self._BaseClass(self) # Class used for scalar computations
        self.BG = self._BaseGridClass(self)  # Class used for vectorized computations across states
        self.BT = self._BaseTimeClass(self)  # Class used for vectorized computations across time
        self.initPars(pars = pars) # add parameters and targets
        self.initProductivity()
        self.updateAuxPars()
        self.initGrids(**noneInit(gridkwargs, {}))
        self.POL = self._PolicyClass(self)
        self.ftol = noneInit(ftol, 1e-5)

    #######################################################################
    ##########                0. Convenience functions          ###########
    #######################################################################
    def solvePEE(self, kwargsPOL = None, **kwargs):
        policy = self.POL(**noneInit(kwargsPOL, {}))
        return self.solveEE(policy['τ'], **kwargs), policy

    #######################################################################
    ##########                0.1. Auxiliary methods            ###########
    #######################################################################
    def checkOpt(self, sol, ftol = None):
        return checkOpt(sol, ftol = noneInit(ftol, self.ftol))

    # Some basic methods for navigating symbols:
    def leadSym(self, symbol, lead = -1, opt = None, ns = 'exo'):
        if isinstance(symbol, pd.Series):
            return self.ns[ns].getShift(symbol, lead, opt = noneInit(opt, {'useLoc':'nn'}))
        elif isinstance(symbol, pd.DataFrame):
            return self.ns[ns].getShift(symbol.stack(), lead, opt = noneInit(opt, {'useLoc': 'nn'})).unstack()
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
        return {'τ0': .125, 'RR0': 0.678/0.803, 's0': 0.184, 'RRGroups': (1,2), 't0': 2}
    @property
    def default1Dparams(self):
        return {'α': .43, 'ν': 1, 'ξ' : .3, 'ρ': 1, 'ω': 1.25, 'α0': 1, 'χ': 1}
    @property
    def default2Dparams(self):
        return {'γj': np.full(self.nj, 1/self.ni)} | {k: np.full(self.nj, 1) for k in ('pj','μj','Xj','ηj','zxj','zηj','βj')}
    @property
    def aux2DParams(self):
        return [f"{k[:-1]}i" for k in self.default2Dparams]
    @property
    def aux1DParams(self):
        return [f"{k[:-1]}0" for k in self.default2Dparams]

    def addProperty(self, key, value):
        """ default dynamic property method """
        setattr(self, f'_{key}', value)
        setattr(type(self), key, property(fget = lambda self: getattr(self, f'_{key}'), fset = lambda self, value: setattr(self, f'_{key}', value)))

    def __setstate__(self, state):
        self.__dict__.update(state)
        value = getattr(self, '_paramsFromFuncs', getattr(self, '_paramFromFuncs', None))
        if value is not None:
            self.addProperty('paramsFromFuncs', value)

    ### Methods to compute auxiliary parameters used throughout the code:
    @property
    def aux_αr(self):
        return (1-self.db['α'])/self.db['α']
    @property
    def aux_θ(self):
        return pd.Series(self.getθ(), index = self.db['t'])
    @property
    def aux_eps(self):
        return pd.Series(self.getEps(), index = self.db['t'])
    @property
    def aux_κ(self):
        return (self.db['p']+self.db['eps[t+1]']*self.db['γ0']*self.db['p0'])*(1+self.db['γ0'])/(1+self.db['γ0[t+1]'])
    @property
    def aux_p(self):
        return (self.db['γi'] * self.db['pi']).sum(axis=1)
    @property
    def aux_Γh(self):
        return self.BT.Γh()

    def addNamespaces(self):
        self.ns = {}
        self.ns['exo'] = sm(symbols = (dict.fromkeys(self.default1Dparams, self.db['t']) |
                                       dict.fromkeys(self.default2Dparams, self.db['tj'])| 
                                       dict.fromkeys(self.aux1DParams, self.db['t']) |
                                       dict.fromkeys(self.aux2DParams, self.db['ti']) |
                                       dict.fromkeys(self.paramsFromFuncs, self.db['t'])))
        [ns.compile() for ns in self.ns.values()];

    @property
    def _x0(self):
        return {}

    #######################################################################
    ##########             1. Initialize methods                ###########
    #######################################################################

    def createCopyFromt0(self, t0):
        """ Return a copy of Model instance 'm' with time starting from t0 """
        mt0 = deepcopy(self)
        mt0.T = self.T-t0
        for k,v in self.db.items():
            if isinstance(v, (pd.Series, pd.DataFrame, pd.Index)):
                mt0.db[k] = adj.rc_pd(v, self.db['t'][t0:])
            elif isinstance(v, np.ndarray):
                mt0.db[k] = self.db[k][t0:]
        mt0.addNamespaces() # reset definition of namespaces
        [baseIns.__setattr__('t0', mt0.db['t'][0]) for baseIns in (mt0.B, mt0.BG, mt0.BT)];
        mt0.x0 = self._x0CopyFromt0(mt0)
        mt0.POL.adjust_t0(t0, self.ns)
        return mt0

    def _x0CopyFromt0(self, mt0):
        return {k: self._x0i_CopyFromt0(k, mt0) for k in self.x0}
    def _x0i_CopyFromt0(self, k, mt0):
        if k in self.ns:
            return np.hstack([adj.rc_pd(self.ns[k].get(self.x0[k], s), mt0.db['t']) for s in self.ns[k].symbols])
        else:
            return mt0.x0[k]

    def initIdxs(self):
        self.db['t'] = pd.Index(range(self.T), name = 't')
        self.db['txE'] = pd.Index(range(self.T-1), name = 't') # Time index without terminal period
        self.db['j'] = pd.Index(range(self.nj), name = 'j')
        self.db['i'] = self.db['j'][1:]
        self.db['u'] = self.db['j'][0:1]
        self.db['tj'] = pd.MultiIndex.from_product([self.db['t'], self.db['j']])
        self.db['ti'] = pd.MultiIndex.from_product([self.db['t'], self.db['i']])

    def initPars(self, pars = None):
        self.db.update(self.defaultParameters) # default parameters and targets
        self.addDefaultHeterogeneity # default heterogeneity
        [self.db.update(self.adjPar(k,v)) for k,v in noneInit(pars, {}).items()];

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

    # Initialzie grids
    def initGrids(self, **kwargs):
        d = self._gridSettings | kwargs
        self.solGrids = {'τ': defaultGrid('τ', d)}
        self.db.update(d)

    @property
    def _gridSettings(self):
        return {'kτ_l': 10, 'kτ_u': 10, 'τ_n': 101, 'τ_l': 1e-4, 'τ_u': 1-1e-4}

    ### Methods used to navigate 0D/1D/2D parameters including lags/leads - and how to update full dimension
    ### parameters based on fewer dimensions. 
    @property
    def defaultParameters(self):
        return functools.reduce(lambda x,y: x|y, [self.adjPar(k,v) for k,v in self.default0DParams.items()] + [self.adjPar(k,v) for k,v in self.default1Dparams.items()])
    @property
    def addDefaultHeterogeneity(self):
        [self.db.update(self.adjPar(k,v)) for k,v in self.default2Dparams.items()]; 
        # return functools.reduce(lambda x,y: x|y, [self.adjPar(k,v) for k,v in self.default2Dparams.items()])
    def updateAuxPars(self):
        [self.db.update(self.addLeadAndLags(k, getattr(self, f'aux_{k}'))) for k in self.paramsFromFuncs]

    def adjPar(self, k, vals, t = None):
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
        return β * self.db['pj']
    def simpleβinv(self):
        return self.db['βj'].iloc[0,0]/self.db['pj'].iloc[0,0]
    def adjpj(self, k, vals, t = None):
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
    ##########            2. Simple calibration methods            ###########
    #######################################################################
    # Note: These two methods are specific to Argentina, these may be changed in other subclasses.

    def getθ(self):
        i,ii = self.db['RRGroups'][0], self.db['RRGroups'][1]
        ξ= self.db['ξ'].xs(self.db['t0'])
        h1,h2 = (self.db['Γh']*self.db['Xi'][i]**ξ/self.db['ηi'][i]**(1+ξ)).xs(self.db['t0']), (self.db['Γh']*self.db['Xi'][ii]**ξ/self.db['ηi'][ii]**(1+ξ)).xs(self.db['t0'])
        return (self.db['RR0']*h1-h2)/(1-h2-self.db['RR0']*(1-h1))
    def getEps(self, coverageRate = 0.7):
        return coverageRate * (1-self.db['θ'].xs(self.db['t0'])+self.db['θ'].xs(self.db['t0'])*self.B.auxProd(self.db['t0'])[1]) * (self.simpleβinv()**(5/30)*9.45/14.45+self.simpleβinv()**(10/30)*12.55/22.55)/2

    #######################################################################
    ##########                3. Steady state methods           ###########
    #######################################################################
    def steadyStateScalar(self, τ, t = None):
        return self.steadyState_report(self.B.get('βi',t), self.B.steadyState_Γs(τ, t = t), τ, t = t)

    def steadyState_report(self, Bi, Γs, τ, t = None):
        d = {'Bi': Bi, 'Γs': Γs, 'τ': τ, 's': np.nan_to_num(self.B.steadyState_s(Γs, τ, t = t), nan = 0)}
        d['h'] = self.BG.backOutH(s = d['s'], Γs = d['Γs'], t = t)
        d['Θs']= self.BG.backOutΘs(s_ = d['s'], s = d['s'], t = t)
        return d

    #######################################################################
    ########                4. Economic Eq. analysis            ###########
    #######################################################################
    def solveEE(self, τ, s0 = None, **kwargs):
        """ Reporting function given τ """
        τ = np.clip(τ, self.db['τ_l'], self.db['τ_u'])
        if s0 is None:
            s0 = self.steadyStateScalar(τ[0], t = self.db['t'][0])['s']
        sol = {'τ': τ, 'τ[t+1]': self.leadSym(τ)}
        sol['Γs'] = self.BT.FH_Γs(τp = sol['τ[t+1]'])
        sol['Θh'] = self.BT.FH_Θh(τ = sol['τ'], τp = sol['τ[t+1]'], Γs = sol['Γs'])
        sol['Θs'] = self.BT.FH_Θs(Θh = sol['Θh'], Γs = sol['Γs'])
        sol['s']  = self.BT.FH_s(Θs = sol['Θs'], s0 = s0)
        sol['s[t-1]'] = np.insert(sol['s'], 0, s0)
        sol['h']  = self.BT.FH_h(Θh = sol['Θh'], s_ = sol['s[t-1]'])
        [sol.__setitem__(k, pd.Series(sol[k], index = self.db['t'])) for k in ('τ','τ[t+1]','Θh','s[t-1]','h')];
        [sol.__setitem__(k, pd.Series(sol[k], index = self.db['txE'])) for k in ('Γs','Θs','s')];
        return sol

    #######################################################################
    ##########                    5. PEE methods                ###########
    #######################################################################
    # Currently None...

    #######################################################################
    ##########                    6. Calibration                ###########
    #######################################################################
    # Depends on model and implementation
    def calibrateUpdateParameters(self, x):
        self.db.update(self.adjPar('β', x[0])) # update beta estimate - this makes sure that entire β matrix and subcomponents are updated
        self.db.update(self.adjPar('ω', x[1])) # update omega estimate.
        ηj = self.db['ηj'].iloc[0].values.copy()
        ηj[0] = x[2]
        self.db.update(self.adjPar('ηj',ηj))
        Xj = self.db['Xj'].iloc[0].values.copy()
        Xj[0] = x[3]
        self.db.update(self.adjPar('Xj',Xj))
        self.updateAuxPars() # update auxiliary parameters

    def calibrateGetx0(self):
        return np.hstack([self.simpleβinv(), self.db['ω'].xs(self.db['t0']), self.db['η0'].xs(self.db['t0']), self.db['X0'].xs(self.db['t0'])])

    def calibrate(self, x0 = None, ftol = None, **kwargs):
        sol = optimize.root(lambda x: self.calibrate_objective(x), noneInit(x0, self.calibrateGetx0()), **kwargs)
        assert self.checkOpt(sol, ftol), f""" Couldn't calibrate model """
        return sol['x']

    def calibrate_objective(self, x, **kwargs):
        self.calibrateUpdateParameters(x)
        path, _ = self.solvePEE(**kwargs)
        η0 = self.B.calib_η0(τ = path['τ'].xs(self.db['t0']), Θh = path['Θh'].xs(self.db['t0']))
        return np.hstack([path['τ'].xs(self.db['t0'])-self.db['τ0'],
                          self.B.calib_savingsRate(s_ = path['s[t-1]'].xs(self.db['t0']), s = path['s'].xs(self.db['t0']), h = path['h'].xs(self.db['t0']))-self.db['s0'],
                          η0-x[2],
                          self.B.calib_X0(η0 = η0, Θh = path['Θh'].xs(self.db['t0']))-x[3]])    

    #######################################################################
    ##########                    7. Reporting                  ###########
    #######################################################################
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
        [path.__setitem__(k, getattr(self.BT, f'FH_{k}')(path)) for k in ('Θhi','Θc̃1i','Θc2i', 'Θc2pi', 'Θc̃10','Θc̃20','Θc̃2p0')];
        return path
    def reportLevels(self, path):
        """ Assumes self.FH_reportCoefficients has been run"""
        [path.__setitem__(k, getattr(self.BT, f'FH_{k}')(path)) for k in ('hi_h','c̃1i','c2i','c2pi','c̃10','c̃20','c̃2p0', 'sRate')];
    def reportUtils(self, path):
        """ Assumes self.FH_reportLevels has been run - not yet implemented here ... """
        pass
