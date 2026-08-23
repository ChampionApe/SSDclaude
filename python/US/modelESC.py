r""" ModelESC: the US model with a deadweight wedge on redistributive benefits AND the leaded political
choice of theta (app:ESC). The "A+B" combination.

    m = ModelESC(pars = ..., wedge = {'spec': 'scale', 'phi': 0.5, 'p': 0.4}, **kwargs)
    m.calibrate()                       # (beta, omega) as ModelUS, with the wedge installed
    out = m.solveLeaded()               # the sequence of policy functions + the equilibrium path
    rec = m.calibrateWedge()            # p such that the leaded choice reproduces the observed design

TWO SPECS, and they differ in more than a formula (Base.wedgeA/wedgeB):

    'scale'   b^i = f(theta)[theta*eta_i*h_i + (1-theta)h]*bbar     the appendix's live spec
    'flat'    b^i = [theta*eta_i*h_i + (1-theta)f(theta)h]*bbar     MGE's variant

Under 'scale' f cancels out of the OECD replacement-rate ratio that identifies theta, so theta is the same
number as in the exogenous-theta model. Under 'flat' it does NOT cancel: the same RR0 datum implies a
different theta for every p, so theta and the wedge are jointly identified and getTheta becomes a scalar
root. That is why the calibration below targets the DATUM (RR0, through theta*(p)) rather than the number
0.738 -- see notes/crossCuttingFindings.md #9, which is exactly this trap in its earlier incarnation.

THE CALIBRATION, and what is approximate about it. Three targets, three parameters:

    R_{t0}, tau_{t0}     ->  beta, omega     ModelUS.calibrate, wedge installed, theta EXOGENOUS at theta*
    thetaPolicy_{t0}(theta*) = theta*  ->  p   the outer root here (phi is imposed, not calibrated)

so the observed design is a fixed point of the leaded choice at the baseline year: in 2020 the electorate
re-elects the system it has. Everything after 2020 is then a prediction -- as nu_t moves, the fixed point
moves with it, and that drift is the object of the exercise.

The approximation is in the inner block: (beta, omega) are calibrated on the path with theta held at
theta*, not on the endogenous-theta path. At the calibrated p those two paths agree at t0 and at t0+1 by
construction and drift only later, so the error is second order -- but it is an error, not an identity, so
solveLeaded reports `targetDrift`, the distance the endogenous path lands from the (R, tau) targets it was
calibrated to. Read it before trusting a result: it is the diagnostic that says whether the fixed-point
approximation held at this parameter point, and it costs nothing.
"""
import numpy as np, pandas as pd
from scipy import optimize
from model import ModelUS
from policyESC import LeadedLOG, LeadedCRRA


class ModelESC(ModelUS):
    _defaultWedge = {'spec': None, 'phi': 0.5, 'p': 1.0}

    def __init__(self, *args, wedge = None, nθ = 41, nθCand = 121, nθCandCRRA = 13, **kwargs):
        """ wedge: {'spec': None|'scale'|'flat', 'phi': float, 'p': float}. spec=None reproduces ModelUS
        exactly (Base.wedgeA/wedgeB are then the identity), which is what test_esc.py pins. """
        self._wedge0 = self._defaultWedge | (wedge or {})
        super().__init__(*args, **kwargs)
        self.ESC = LeadedLOG(self, nθ = nθ, nθCand = nθCand)
        self.ESCC = LeadedCRRA(self, nθCand = nθCandCRRA)

    def initPars(self, pars = None):
        """ Write the wedge parameters BEFORE the parent fills db: updateAuxPars runs inside the parent's
        __init__ and re-derives theta through getθ, which is wedge-aware under 'flat'. """
        self.db.update({'wedgeSpec': self._wedge0['spec'], 'wedgePhi': self._wedge0['phi'],
                        'wedgeP': self._wedge0['p']})
        super().initPars(pars = pars)

    # ------------------------------------------------------------------ wedge parameters
    @property
    def wedge(self):
        return {'spec': self.db['wedgeSpec'], 'phi': self.db['wedgePhi'], 'p': self.db['wedgeP']}

    def setWedge(self, spec = None, phi = None, p = None, update = True):
        """ Install wedge parameters and refresh the auxiliary ones. `update` re-derives theta (and Γh,
        eps, kappa) -- necessary under 'flat', where theta is a function of p, and harmless under 'scale'.
        Pass update=False only if you are about to overwrite db['θ'] yourself. """
        if spec is not None:
            self.db['wedgeSpec'] = None if spec == 'none' else spec
        if phi is not None:
            self.db['wedgePhi'] = float(phi)
        if p is not None:
            self.db['wedgeP'] = float(p)
        if update:
            self.updateAuxPars()
        return self.wedge

    # ------------------------------------------------------------------ theta identification
    def getθ(self):
        """ theta from the OECD replacement-rate ratio (eq in Quant.tex), wedge-aware.

        The datum pins the RATIO of the benefit formula's two coefficients, B/A = (1-RR0)/(RR0*h1-h2),
        and nothing else -- so the parent's closed form already delivers it as (1-theta)/theta. Under
        'scale' A/B carry a common f(theta) which cancels there, and theta is unchanged. Under 'flat'
        B/A = (1-theta)f(theta)/theta and theta is the root of that in (0,1).

        The root is bracketed by a scan rather than handed straight to brentq: (1-x)/x is decreasing and
        f(x) increasing, so the product need not be monotone, and a silently-picked second root would be
        a different calibration wearing the same number. """
        θ = super().getθ()
        if self.db.get('wedgeSpec') != 'flat':
            return θ
        if not (0. < θ < 1.):
            raise ValueError(f'getθ: the no-wedge inversion gives θ={θ}, outside (0,1); B/A is not identified.')
        r = (1-θ)/θ
        g = lambda x: (1-x)*self.B.fWedge(x)/x - r
        grid = np.linspace(1e-6, 1-1e-9, 2001)
        v = g(grid)
        sign = np.where(np.diff(np.sign(v)) != 0)[0]
        if len(sign) == 0:
            raise ValueError(f'getθ: no root of (1-θ)f(θ)/θ = {r:.6g} on (0,1) at {self.wedge}.')
        if len(sign) > 1:
            raise ValueError(f'getθ: {len(sign)} roots of (1-θ)f(θ)/θ = {r:.6g} on (0,1) at {self.wedge}; '
                             'the wedge shape makes θ ambiguous at this (φ,p).')
        k = sign[0]
        return float(optimize.brentq(g, grid[k], grid[k+1], xtol = 1e-14))

    # ------------------------------------------------------------------ the leaded solve
    @property
    def t0Year(self):
        """ The db['t'] label of the calibration baseline year (db['t0'] is its POSITION -- see
        ModelUS.default0DParams). """
        return self.db['t'][self.db['t0']]

    def solveLeaded(self, s0 = None, pinAtT0 = True, sols = None, ε = None):
        """ Solve the leaded politico-economic equilibrium end to end.

        pinAtT0: hold theta at its calibrated value up to and including t0, so the political choice binds
        from t0 onward (LeadedLOG.simulate's tPin) -- the timing calibrateWedge targets. False lets the
        choice bind from the first period of the horizon, which makes theta_{t0} a prediction rather than
        the datum, and is only what you want for a diagnostic.

        Returns {'sols', 'θ', 'τ', 'sol', 'report', 'targetDrift'} -- the same keys solvePEE_LOG returns
        plus the design path and the fixed-point diagnostic (see the module docstring). """
        sols = self.ESC.solveBackward() if sols is None else sols
        t0 = self.t0Year
        θ0 = float(self.db['θ'].xs(t0))
        θPath, τPath = self.ESC.simulate(sols, θ0, tPin = t0 if pinAtT0 else None)
        ε = self.db['eps'].values if ε is None else ε
        θ, τ = θPath.values, τPath.values
        if s0 is None:
            s0 = self.steadyState_LOG_solve(τ[self.B.tFirst], θ[self.B.tFirst], t = self.B.tFirst)['s']
        sol = self.EE_LOG_solve(τ, θ, ε, s0)
        report = self.EE_report(sol, τ, θ, ε, s0)
        drift = {'R': float(report['R'].xs(t0)) - float(self.db['R0']),
                 'τ': float(τPath.xs(t0)) - float(self.db['τ0'])}
        return {'sols': sols, 'θ': θPath, 'τ': τPath, 'sol': sol, 'report': report,
                'targetDrift': drift}

    def leadedChoiceAtT0(self, sols = None):
        """ thetaPolicy_{t0}(theta*) -- what calibrateWedge drives onto theta*. """
        sols = self.ESC.solveBackward() if sols is None else sols
        return self.ESC.choiceAt(sols, self.t0Year, float(self.db['θ'].xs(self.t0Year)))

    def createCopyFromt0(self, t0):
        """ ModelUS.createCopyFromt0, with the leaded solver's horizon refreshed. self.ESC is deepcopied
        with everything else and its db/B/BG/BT already point at the copy's own objects, but its cached T
        would still describe the original horizon. """
        mt0 = super().createCopyFromt0(t0)
        mt0.ESC.T = mt0.ESCC.T = mt0.T
        return mt0

    def leadedChoiceAtT0_CRRA(self, s0 = None, solveKwargs = None):
        """ theta_{t0+1} chosen at t0 under CRRA, with the rest of the design path held at theta*.

        This is the CRRA counterpart of leadedChoiceAtT0 and it is what calibrateWedge targets when
        preferences='CRRA'. Holding theta_{t0+2}, ... at theta* is not a shortcut AT THE CALIBRATED POINT:
        the target is precisely that the choice reproduces theta*, so at a converged p the held path IS
        the equilibrium path (up to the drift that time-varying nu_t induces later, which solveLeadedCRRA
        then reports). Away from the calibrated p it is a genuine approximation, and it only has to be
        good enough to locate the root.

        13 candidate solves rather than a full path iteration, which is what makes calibrating p under
        CRRA affordable at all. """
        θStar = float(self.db['θ'].xs(self.t0Year))
        pos = self.db['t0']
        Ws = np.empty(self.ESCC.nθCand)
        for k, cand in enumerate(self.ESCC.θCand):
            θTry = np.full(self.T, θStar)
            θTry[pos+1] = cand
            try:
                Ws[k] = self.ESCC.W(self.ESCC.solveθPath(θTry, s0 = s0, **(solveKwargs or {})), pos)
            except Exception:
                Ws[k] = -np.inf
        if not np.any(np.isfinite(Ws)):
            raise RuntimeError('leadedChoiceAtT0_CRRA: every candidate failed to solve.')
        return self.ESCC._argmax(self.ESCC.θCand, Ws)[0]

    def solveLeadedCRRA(self, s0 = None, maxIter = 6, tol = 1e-3, verbose = True, solveKwargs = None):
        """ The full CRRA design path (LeadedCRRA.solvePath), pinned at theta* up to and including t0, plus
        the same targetDrift diagnostic solveLeaded reports. """
        θStar = float(self.db['θ'].xs(self.t0Year))
        rec = self.ESCC.solvePath(θStar, pinPos = self.db['t0'], maxIter = maxIter, tol = tol,
                                  s0 = s0, verbose = verbose, solveKwargs = solveKwargs)
        t0 = self.t0Year
        rec['targetDrift'] = {'R': float(rec['out']['report']['R'].xs(t0)) - float(self.db['R0']),
                              'τ': float(rec['out']['τ'].xs(t0)) - float(self.db['τ0'])}
        return rec

    # ------------------------------------------------------------------ calibrating the wedge
    def wedgeResidual(self, p, spec, phi, calKwargs = None, preferences = 'LOG'):
        """ (the leaded choice at t0) - theta* at wedge parameter p, with (beta, omega) recalibrated to
        (R_{t0}, tau_{t0}) at that p. theta* is db['θ'] AFTER setWedge, so it moves with p under 'flat'.
        preferences selects which leaded solver evaluates the choice. """
        self.setWedge(spec = spec, phi = phi, p = float(p))
        self.calibrate(**(calKwargs or {}))
        θStar = float(self.db['θ'].xs(self.t0Year))
        choice = self.leadedChoiceAtT0() if preferences == 'LOG' else self.leadedChoiceAtT0_CRRA()
        return choice - θStar

    def calibrateWedge(self, spec = 'scale', phi = 0.5, bracket = (0.05, 3.0), nScan = 12,
                       calKwargs = None, xtol = 1e-6, verbose = True, preferences = 'LOG'):
        """ Calibrate p (phi imposed) so the leaded choice reproduces the observed design at t0.

        Scans `bracket` on a log grid for a sign change before bracketing, because the residual is NOT
        guaranteed monotone in p and, more importantly, is FLAT AT A CORNER: wherever the choice is at
        theta = 0 or 1 the residual does not move with p at all, and a root finder handed such a bracket
        would report a spurious convergence at whichever endpoint it happened to test. The scan reports
        what it saw, so a run that fails to find an interior crossing says so rather than returning a
        number. Returns {'p', 'residual', 'scan', 'converged', 'wedge', 'θ'}. """
        grid = np.exp(np.linspace(np.log(bracket[0]), np.log(bracket[1]), nScan))
        scan = []
        for p in grid:
            try:
                r = self.wedgeResidual(p, spec, phi, calKwargs, preferences)
            except Exception as e:                   # a failed inner calibration is a datum, not a stop
                r = np.nan
                if verbose:
                    print(f'    p={p:.4f}: inner solve failed ({type(e).__name__}: {e})')
            scan.append({'p': float(p), 'residual': float(r),
                         'θ': float(self.db['θ'].xs(self.t0Year))})
            if verbose and np.isfinite(r):
                print(f"    p={p:.4f}: θ*={scan[-1]['θ']:.4f}  choice-θ* = {r:+.5f}")
        v = np.array([s['residual'] for s in scan])
        ok = np.isfinite(v)
        idx = [k for k in range(len(v)-1) if ok[k] and ok[k+1] and v[k]*v[k+1] < 0]
        if not idx:
            return {'p': np.nan, 'residual': np.nan, 'scan': scan, 'converged': False,
                    'wedge': self.wedge, 'θ': np.nan,
                    'message': 'no sign change in the scanned bracket -- the choice never crosses θ*'}
        k = idx[0]
        f = lambda p: self.wedgeResidual(p, spec, phi, calKwargs, preferences)
        p = optimize.brentq(f, grid[k], grid[k+1], xtol = xtol)
        res = self.wedgeResidual(p, spec, phi, calKwargs, preferences)  # leaves db at the calibrated point
        return {'p': float(p), 'residual': float(res), 'scan': scan, 'converged': abs(res) < 1e-4,
                'wedge': self.wedge, 'θ': float(self.db['θ'].xs(self.t0Year)),
                'message': 'calibrated'}
