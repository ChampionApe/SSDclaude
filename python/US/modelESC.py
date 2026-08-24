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
    theta_{t0} = theta*  ->  p               the outer root here (phi is imposed, not calibrated)

where theta_{t0} is the design in FORCE at the baseline year on a freely simulated path -- chosen in 1990,
not in 2020 (leadedDesignAtT0). So the observed design is what the model's own political history delivers
by 2020, and the counterfactual tables, which are new paths read at 2020, have a baseline row that sits on
the datum. Everything after 2020 is then a prediction: as nu_t moves the design moves with it, and that
drift is the object of the exercise.

That target replaced thetaPolicy_{t0}(theta*) = theta* -- the choice MADE at 2020, which is the right
object only when the design is pinned as history through 2020 and the tables are read at 2050. The two
differ by one period of nu_t and by about 0.011 in theta at the calibrated point.

The approximation is in the inner block: (beta, omega) are calibrated on the path with theta held at
theta*, not on the endogenous-theta path. At the calibrated p those two paths agree at t0 by construction
and drift only later, so the error is second order -- but it is an error, not an identity, so solveLeaded
reports `targetDrift`, the distance the endogenous path lands from the (R, tau) targets it was calibrated
to. Read it before trusting a result: it is the diagnostic that says whether the fixed-point approximation
held at this parameter point, and it costs nothing.
"""
import numpy as np, pandas as pd
from scipy import optimize
from model import ModelUS
from policyESC import LeadedLOG, LeadedCRRA, LeadedCRRA2D, PermanentLOG, PermanentCRRA


class ModelESC(ModelUS):
    _defaultWedge = {'spec': None, 'phi': 0.5, 'p': 1.0}

    def __init__(self, *args, wedge = None, nθ = 41, nθCand = 121, nθCandCRRA = 13,
                 nθCandPerm = 21, nθ2D = 13, nθCand2D = 21, **kwargs):
        """ wedge: {'spec': None|'scale'|'flat', 'phi': float, 'p': float}. spec=None reproduces ModelUS
        exactly (Base.wedgeA/wedgeB are then the identity), which is what test_esc.py pins. """
        self._wedge0 = self._defaultWedge | (wedge or {})
        super().__init__(*args, **kwargs)
        self.ESC = LeadedLOG(self, nθ = nθ, nθCand = nθCand)
        self.ESCC = LeadedCRRA(self, nθCand = nθCandCRRA)
        self.ESCC2 = LeadedCRRA2D(self, nθ = nθ2D, nθCand = nθCand2D)
        self.ESCP = PermanentLOG(self, nθ = nθ, nθCand = nθCand)
        self.ESCPC = PermanentCRRA(self, nθCand = nθCandPerm)

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
        """ thetaPolicy_{t0}(theta*) -- the design the t0 electorate picks FOR t0+1, given theta* in force.

        This is not what calibrateWedge targets any more; leadedDesignAtT0 is. Kept because it is the
        object the pinned timing reports and what test_esc.py's separability checks are written against. """
        sols = self.ESC.solveBackward() if sols is None else sols
        return self.ESC.choiceAt(sols, self.t0Year, float(self.db['θ'].xs(self.t0Year)))

    def leadedDesignAtT0(self, sols = None):
        """ theta_{t0} on the FREELY simulated path -- the design in FORCE at the baseline year when the
        political choice binds from the first period of the horizon. What calibrateWedge targets, and
        what every counterfactual table reads.

        The distinction from leadedChoiceAtT0 is one period and it matters. theta_t is a state chosen at
        t-1, so the design in force in 2020 was picked in 1990 under nu_{1990}; the choice made in 2020
        binds in 2050. They coincide only if the policy function is time-invariant, and nu_t is not. At
        p = 0.4022 (scale, phi = 0.5, rho = 1) the two differ by 0.011 -- small, but enough to put the
        baseline row off the observed design in a table read at 2020, which is why the target moved here.

        Under LOG this is exactly thetaPolicy_{t0-1} evaluated anywhere: the policy has no state at all
        (test_esc.py measures it), so the inherited theta_{t0-1} drops out and simulate's forward sweep is
        a formality. It is written through simulate anyway, because that identity is a LOG fact and this
        method must stay right if it stops holding. """
        sols = self.ESC.solveBackward() if sols is None else sols
        θPath, _ = self.ESC.simulate(sols, float(self.db['θ'].xs(self.t0Year)), tPin = None)
        return float(θPath.xs(self.t0Year))

    def createCopyFromt0(self, t0):
        """ ModelUS.createCopyFromt0, with the leaded solver's horizon refreshed. self.ESC is deepcopied
        with everything else and its db/B/BG/BT already point at the copy's own objects, but its cached T
        would still describe the original horizon. """
        mt0 = super().createCopyFromt0(t0)
        mt0.ESC.T = mt0.ESCC.T = mt0.ESCC2.T = mt0.ESCP.T = mt0.ESCPC.T = mt0.T
        return mt0

    def _leadedGridChoice_CRRA(self, votePos, s0 = None, solveKwargs = None, name = ''):
        """ The design chosen by the electorate at position `votePos` for votePos+1, under CRRA, with the
        rest of the design path held at theta*.

        Holding theta at theta* away from the one candidate slot is not a shortcut AT THE CALIBRATED
        POINT: the target is precisely that the choice reproduces theta*, so at a converged p the held
        path IS the equilibrium path (up to the drift that time-varying nu_t induces later, which
        solveLeadedCRRA then reports). Away from the calibrated p it is a genuine approximation, and it
        only has to be good enough to locate the root.

        13 candidate solves rather than a full path iteration, which is what makes calibrating p under
        CRRA affordable at all. """
        θStar = float(self.db['θ'].xs(self.t0Year))
        Ws = np.empty(self.ESCC.nθCand)
        for k, cand in enumerate(self.ESCC.θCand):
            θTry = np.full(self.T, θStar)
            θTry[votePos+1] = cand
            try:
                Ws[k] = self.ESCC.W(self.ESCC.solveθPath(θTry, s0 = s0, **(solveKwargs or {})), votePos)
            except Exception:
                Ws[k] = -np.inf
        if not np.any(np.isfinite(Ws)):
            raise RuntimeError(f'{name or "_leadedGridChoice_CRRA"}: every candidate failed to solve.')
        return self.ESCC._argmax(self.ESCC.θCand, Ws)[0]

    def leadedChoiceAtT0_CRRA(self, s0 = None, solveKwargs = None):
        """ theta_{t0+1} chosen at t0 under CRRA -- the CRRA counterpart of leadedChoiceAtT0. """
        return self._leadedGridChoice_CRRA(self.db['t0'], s0, solveKwargs, 'leadedChoiceAtT0_CRRA')

    def leadedDesignAtT0_CRRA(self, s0 = None, solveKwargs = None):
        """ theta_{t0} under CRRA: the design in FORCE at the baseline year, chosen one period earlier.
        The CRRA counterpart of leadedDesignAtT0, and what calibrateWedge targets at rho != 1.

        Same 13-candidate cost as leadedChoiceAtT0_CRRA -- only the slot moves, from t0+1 to t0, and the
        objective from the t0 electorate's to the t0-1 one's. A full free-path iteration inside the outer
        root on p would be the exact object and is not affordable; this is the same approximation the
        calibration has always made, relocated one period. """
        pos = self.db['t0']
        if pos == 0:
            raise ValueError('leadedDesignAtT0_CRRA: t0 is the first period of the horizon, so the design '
                             'in force there is inherited, not chosen.')
        return self._leadedGridChoice_CRRA(pos-1, s0, solveKwargs, 'leadedDesignAtT0_CRRA')

    def solveLeaded2D(self, s0 = None, pinAtT0 = True, sols = None, verbose = False):
        """ The TRUE leaded CRRA equilibrium (LeadedCRRA2D): backward-solved 2-D policy functions, the
        simulated design/tax path, the exact economic equilibrium at that path, and the same targetDrift
        diagnostic the other solvers report. pinAtT0 as solveLeaded: the design is history up to and
        including t0 -- and here the pinning has to reach the RECURSION, not just the simulation, because
        τ_t responds to θ_{t+1} under CRRA (see LeadedCRRA2D's docstring). """
        θStar = float(self.db['θ'].xs(self.t0Year))
        pinPos = int(self.db['t0']) if pinAtT0 else None
        if sols is None:
            sols = self.ESCC2.solvePolicies(θStar, pinPos = pinPos, verbose = verbose)
        if s0 is None:
            s0 = self.ESCC2.s0FixedPoint(sols, θStar)
        θPath, τPath, sP, hP, ΓsP = self.ESCC2.simulate(sols, θStar, s0, pinPos = pinPos)
        ε = self.db['eps'].values.astype(float)
        sol = self.EE_CRRA_solve(τPath.values, θPath.values, ε, s0,
                                 x0 = np.concatenate([ΓsP, hP, sP]))
        report = self.EE_report(sol, τPath.values, θPath.values, ε, s0)
        t0 = self.t0Year
        drift = {'R': float(report['R'].xs(t0)) - float(self.db['R0']),
                 'τ': float(τPath.xs(t0)) - float(self.db['τ0'])}
        return {'sols': sols, 'θ': θPath, 'τ': τPath, 'sol': sol, 'report': report,
                'targetDrift': drift, 's0': s0}

    def leadedChoiceAtT0_2D(self, out = None, verbose = False):
        """ θPolicy_{t0}(s_{t0-1}, θ*) from the 2-D solver -- the exact counterpart of what
        leadedChoiceAtT0_CRRA approximates with a held-fixed future, evaluated at the pinned path's own
        state entering t0. Pass a solveLeaded2D return to reuse its recursion. """
        if out is None:
            out = self.solveLeaded2D(pinAtT0 = True, verbose = verbose)
        t0 = self.t0Year
        θStar = float(self.db['θ'].xs(t0))
        s_ = float(out['report']['s_'].xs(t0))
        return self.ESCC2.choiceAt(out['sols'], t0, s_, θStar)

    def solveLeadedCRRA(self, s0 = None, maxIter = 6, tol = 1e-3, verbose = True, solveKwargs = None,
                        pinAtT0 = False):
        """ The full CRRA design path (LeadedCRRA.solvePath) plus the same targetDrift diagnostic
        solveLeaded reports.

        pinAtT0 as solveLeaded, and the default is False here because the counterfactuals are new paths:
        the design is chosen from the first period the horizon allows, so theta_{t0} is an equilibrium
        outcome and can be read at 2020. True holds it at theta* through t0 -- the unanticipated-reform
        reading, kept as a diagnostic and as the object leadedChoiceAtT0_CRRA is the one-shot version of.
        """
        θStar = float(self.db['θ'].xs(self.t0Year))
        rec = self.ESCC.solvePath(θStar, pinPos = self.db['t0'] if pinAtT0 else 0, maxIter = maxIter,
                                  tol = tol, s0 = s0, verbose = verbose, solveKwargs = solveKwargs)
        t0 = self.t0Year
        rec['targetDrift'] = {'R': float(rec['out']['report']['R'].xs(t0)) - float(self.db['R0']),
                              'τ': float(rec['out']['τ'].xs(t0)) - float(self.db['τ0'])}
        return rec

    # ------------------------------------------------------------------ the permanent choice
    def predeterminedSiRatio(self, base = None, preferences = 'LOG'):
        """ s_{t0-1,i}/s_{t0-1} from the INCUMBENT equilibrium -- the ratio the permanent choice would hold
        fixed if the reform were unanticipated. The default timing is the anticipated one, which pins it at
        the CHOSEN design instead (PermanentLOG.solveFixedPoint); this is the diagnostic alternative, and
        the seed the fixed point starts from.

        Read off the baseline report at the period BEFORE t0: EE_report's 'si_s' is computed at vintage t
        and gives s_{t,i}/s_t, so the row at t0-1 is exactly what c_{2,t0}^i consumes. base: a solved
        solvePEE_* return; solved here if not supplied. """
        t0 = self.t0Year
        pos = self.db['t'].get_loc(t0)
        if pos == 0:
            raise ValueError('predeterminedSiRatio: t0 is the first period of the horizon, so there is no '
                             'predetermined ratio to read -- use initialState_solve instead.')
        if base is None:
            base = getattr(self, f'solvePEE_{preferences}')()
        return base['report']['si_s'].xs(self.db['t'][pos-1]).values.astype(float)

    def θPathPermanent(self, θ):
        """ The design path a permanent reform at t0 actually is: the INCUMBENT design before t0, theta
        from t0 on. Before t0 the design is exogenous -- the vote has not happened -- so applying the
        chosen theta over the whole horizon would report a counterfactual past.

        It does not change the choice: eq (EE:si_s) at vintage t0-1 depends on date-t0 policy alone, so
        the predetermined ratio is the same either way (checked in test_esc.py). It changes the reported
        path before t0, which is a different object. """
        out = self.db['θ'].values.astype(float).copy()
        out[self.db['t0']:] = float(θ)
        return out

    def solvePermanent(self, preferences = 'LOG', base = None, pinning = 'fixedPoint', diagnostics = True,
                       s0 = None, θCand = None, verbose = False):
        """ The permanent design chosen at t0, and the equilibrium it implies.

        pinning selects what s_{t0-1,i}/s_{t0-1} is held at while W_{t0} is maximised. It is a TIMING
        assumption, not a numerical setting -- see PermanentLOG's docstring:

          'fixedPoint' (default)  the vote is ANTICIPATED, so the savings made at t0-1 were made against
                                  the design that wins: theta* = argmax W(theta ; siRatio(theta*)).
          'incumbent'             the ratio from the incumbent equilibrium -- the UNANTICIPATED reform.
                                  Identical to 'fixedPoint' wherever the choice reproduces the incumbent
                                  design, which is what calibrateWedge targets.
          'moving'                recomputed at each candidate. The WRONG object under any timing: savings
                                  are sunk at the vote, and z_t = 0 is built holding the ratio fixed, so
                                  a moving ratio is inconsistent with the tau it is paired with. Exposed
                                  so the size of the error stays on the record. LOG only.

        diagnostics: also report the choice under the other two readings ('θIncumbent', 'θMoving').

        Returns {'θ', 'atBound', 'τ', 'sol', 'report', 'W', 'θCand', 'converged', ...}. """
        t0 = self.t0Year
        if base is None:
            base = getattr(self, f'solvePEE_{preferences}')()
        θInc = float(self.db['θ'].xs(t0))
        siInc = self.predeterminedSiRatio(base = base)
        if preferences == 'LOG':
            P, kw = self.ESCP, {'θCand': θCand}
        else:
            if s0 is None:
                s0 = float(base['report']['s_'].xs(t0))
            P, kw = self.ESCPC, {'θCand': θCand, 's0': s0, 'verbose': verbose}
        if pinning == 'fixedPoint':
            rec = P.solveFixedPoint(t0, θInc, **kw)
        elif pinning == 'incumbent':
            rec = P.solve(t0, siInc, **kw)
        elif pinning == 'moving':
            if preferences != 'LOG':
                raise NotImplementedError("solvePermanent: pinning='moving' is LOG only.")
            rec = self.ESCP.solve(t0, None, θCand = θCand)
        else:
            raise ValueError(f"solvePermanent: unknown pinning {pinning!r}.")
        rec.setdefault('converged', True)     # vacuously so for the two single-pass pinnings
        if diagnostics:
            kwInc = (kw | {'cache': rec['cache']}) if 'cache' in rec else kw   # CRRA: reuse the solves
            rec['θIncumbent'] = P.solve(t0, siInc, **kwInc)['θ']
            rec['θMoving'] = (self.ESCP.solve(t0, None, θCand = θCand)['θ']
                              if preferences == 'LOG' else np.nan)

        # the equilibrium at the chosen permanent design: incumbent before t0, chosen from t0 on
        θ = self.θPathPermanent(rec['θ'])
        ε = self.db['eps'].values.astype(float)
        θSave = self.db['θ'].values.astype(float).copy()
        try:
            self.db.update(self.adjPar('θ', θ))
            τ = (self.ESCP.τPath(θ) if preferences == 'LOG'
                 else self.solvePEE_CRRA(θ = θ, ε = ε)['τ'].values.astype(float))
            s0e = self.steadyState_LOG_solve(τ[self.B.tFirst], θ[self.B.tFirst], t = self.B.tFirst)['s']                   if preferences == 'LOG' else None
            sol = getattr(self, f'EE_{preferences}_solve')(τ, θ, ε, s0e)
            report = self.EE_report(sol, τ, θ, ε, s0e if s0e is not None else float(sol['s'].iloc[0]))
        finally:
            self.db.update(self.adjPar('θ', θSave))
        return rec | {'τ': pd.Series(τ, index = self.db['t']), 'sol': sol, 'report': report, 'θPath': θ}

    def permanentChoiceAtT0(self, preferences = 'LOG', base = None, verbose = False):
        """ The permanent choice evaluated at the INCUMBENT ratio -- what calibrateWedge's residual is
        built from, and deliberately not solvePermanent's fixed point.

        This is not a second convention. calibrateWedge asks for the p at which the electorate re-elects
        the system it has, i.e. choice(theta*) = theta*, and THAT EQUATION IS the fixed-point condition:
        a p where the incumbent-pinned choice reproduces the incumbent design is a p where the incumbent
        design IS the fixed point. So both readings have the same root, and this one reaches it with one
        pass per trial instead of an inner iteration. Verified against a scan run with solveFixedPoint
        in the loop (RESEARCH_LOG, 2026-08-24): identical p to 1e-9.

        What the two do NOT share is the residual away from the root, so a scan must not mix them. """
        t0 = self.t0Year
        if base is None:
            base = getattr(self, f'solvePEE_{preferences}')()
        siRatio_ = self.predeterminedSiRatio(base = base)
        if preferences == 'LOG':
            return self.ESCP.solve(t0, siRatio_)['θ']
        s0 = float(base['report']['s_'].xs(t0))
        return self.ESCPC.solve(t0, siRatio_, s0 = s0, verbose = verbose)['θ']

    # ------------------------------------------------------------------ calibrating the wedge
    def wedgeResidual(self, p, spec, phi, calKwargs = None, preferences = 'LOG'):
        """ (the equilibrium design at t0) - theta* at wedge parameter p, with (beta, omega) recalibrated
        to (R_{t0}, tau_{t0}) at that p. theta* is db['θ'] AFTER setWedge, so it moves with p under
        'flat'. preferences selects which solver evaluates the design.

        For the LEADED timings the target is the design in FORCE at t0 on a freely simulated path
        (leadedDesignAtT0), not the choice made at t0. That is the design the tables report, so it is the
        one the baseline has to reproduce; see leadedDesignAtT0 for the one-period distinction and what
        it costs. For the PERMANENT timings the choice at t0 IS the design at t0 -- the reform is dated
        t0 -- so those two entries are unchanged. """
        self.setWedge(spec = spec, phi = phi, p = float(p))
        self.calibrate(**(calKwargs or {}))
        θStar = float(self.db['θ'].xs(self.t0Year))
        design = {'LOG':      lambda: self.leadedDesignAtT0(),
                  'CRRA':     lambda: self.leadedDesignAtT0_CRRA(),
                  'permLOG':  lambda: self.permanentChoiceAtT0('LOG'),
                  'permCRRA': lambda: self.permanentChoiceAtT0('CRRA')}[preferences]()
        return design - θStar

    def calibrateWedge(self, spec = 'scale', phi = 0.5, bracket = (0.05, 3.0), nScan = 12,
                       calKwargs = None, xtol = 1e-6, verbose = True, preferences = 'LOG'):
        """ Calibrate p (phi imposed) so the equilibrium design at t0 is the observed one (wedgeResidual).

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
