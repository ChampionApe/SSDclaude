r""" Endogenous system characteristics: the LEADED choice of theta (app:ESC, "Leaded choices of theta_t"),
under LOG (LeadedLOG) and CRRA (LeadedCRRA) preferences.

theta_{t+1} is chosen at t by the same probabilistic-voting objective that chooses tau_t, and is a STATE
at t+1. What makes the LOG case cheap is a property of the US model (no informal household), verified in
test_esc.py rather than assumed:

    z_t -- the FOC for tau_t -- depends on (tau_t, theta_t) ALONE.

theta_{t+1} enters z_t only through Theta_{h,t}, which reaches the FOC only through dv20 (the old informal
household), and that term carries weight gamma_0 = 0 here. So tau_t = tauPolicy_t(theta_t) is a STATIC
scalar problem, the two choices at t are separable, and the state is one-dimensional.

Two further properties, both MEASURED (test_esc.py) rather than assumed, and both specific to LOG:

  * the choice does not depend on s_{t-1} -- ln(s_{t-1}) enters every term of W_t additively, which is the
    appendix's own normalisation ("simply assume that s_{t-1} = 1");
  * the choice does not depend on theta_t EITHER. ln(h_t), ln(ctilde_{1,t}^i) and ln(R_{t+1}) are each
    additively separable in tau_t and theta_{t+1}, so W_t = A(tau_t) + B(theta_{t+1}); theta_t reaches W_t
    only through tau_t, so it cannot move the argmax. thetaPolicy_t comes back constant across the state
    grid to machine precision.

Under CRRA both fail: the powers do not separate. LeadedCRRA therefore solves the PATH rather than a
policy function -- see its own docstring for what that costs and how the residual state-dependence is
measured rather than hoped away.

THE OBJECTIVE, in both cases:

    W_t = sum_i gamma_{t-1,i} omega p_{t-1} mu_{t-1,i} v_{2,t}^i + nu_t sum_i gamma_{t,i} mu_{t,i} v_{1,t}^i

with (model_PEE.tex) v_1^i = (1+beta_i)ln(ctilde_1^i) + beta_i ln(R_{t+1}) and v_2^i = ln(c_2^i) under LOG,
and v_1^i = (1+B_{t+1}^i)(ctilde_1^i)^{1-1/rho}/(1-1/rho), v_2^i = (c_2^i)^{1-1/rho}/(1-1/rho) under CRRA.
The weights are Base.FOC's own, so the objective and the tau-FOC cannot be weighted differently.

WHY A GRID AND NOT A FOC. The whole point of the exercise is to find out whether the choice is interior,
so the solver must be able to return a corner as a corner. Both solvers evaluate W_t on a grid of
candidates, take the argmax, and refine it parabolically when interior; a corner is reported as such.
Differentiating W_t would buy speed and cost exactly the property being measured.
"""
import numpy as np, pandas as pd
from scipy import optimize
from gridsearch import roots1d, CartesianGrid, griddedInterp1D, griddedSmooth1D, griddedGradient1D
from policy import CRRA


class LeadedBase:
    """ What the LOG and CRRA leaded solvers share: the political weights, the zero-mass guard, and the
    corner-preserving argmax. """

    def weights(self, t):
        """ W_t's bloc weights: old_i = gamma_{t-1,i}*omega*p_{t-1}*mu_{t-1,i}, young_i = nu_t*gamma_{t,i}*mu_{t,i}.
        Exactly Base.FOC's combination. The informal blocs are absent: gamma_0 = 0 in this model. """
        old = self.BG.get('γi[t-1]', t) * self.BG.ω2i(t)
        young = float(self.BG.get('ν', t)) * self.BG.get('γi', t) * self.BG.ω1i(t)
        return old, young

    def _requireZeroMass(self):
        """ The whole design rests on gamma_0 = 0 (see LeadedLOG.z and the module header). Checked where
        it is relied on rather than asserted in a comment. """
        if float(np.max(np.abs(self.db['γ0'].values))) != 0.:
            raise NotImplementedError(
                'The leaded solvers require the zero-mass informal slot (gamma_0 = 0): with mass, z_t '
                'depends on theta_{t+1} through dv20 and tau_t/theta_{t+1} stop being separable.')

    @staticmethod
    def _argmax(x, y):
        """ argmax of y over the grid x, refined by the parabola through the three points around it when
        the maximum is interior. Returns (x*, atBound). A corner is returned AS a corner -- whether the
        choice is interior is the object of the exercise, so it must never be interpolated away. """
        k = int(np.argmax(y))
        if k == 0 or k == len(x)-1:
            return float(x[k]), True
        y0, y1, y2 = y[k-1], y[k], y[k+1]
        denom = y0 - 2*y1 + y2
        if denom == 0 or not np.isfinite(denom):
            return float(x[k]), False
        shift = float(np.clip(0.5*(y0 - y2)/denom, -1., 1.))     # in units of the grid step
        return float(x[k] + shift*(x[k+1]-x[k])), False


class LeadedLOG(LeadedBase):
    """ Sequence of policy functions (tauPolicy_t, thetaPolicy_t) over the state theta_t, LOG case.

    The state grid is kept even though thetaPolicy_t is measurably constant along it (module docstring):
    it costs almost nothing, it is what MAKES that property measurable, and it stops being true the moment
    anything breaks the log separability. """

    def __init__(self, m, nθ = 41, nθCand = 121, **kwargs):
        self.m = m
        self.B, self.BG, self.BT = m.B, m.BG, m.BT
        self.db = m.db
        self.ni, self.T = m.ni, m.T
        self.nθ, self.nθCand = nθ, nθCand
        self.θGrid = np.linspace(0., 1., nθ)          # the state grid, and where policies are tabulated
        self.θCand = np.linspace(0., 1., nθCand)      # candidates searched over
        self.kwargs = kwargs

    # ------------------------------------------------------------------ tau given theta
    def z(self, t, τ, θ, tLag, terminal):
        """ The LOG political FOC z_t at (tau, theta), both broadcastable to a common shape (M,). Thin
        wrapper over LOG.stateGrid/focGrid -- the SAME code path solvePEE_LOG uses, so the leaded solver
        cannot drift from the exogenous-theta one.

        (tau_{t+1}, theta_{t+1}) are passed as (tau, theta) rather than their true values, and that is
        SOUND rather than approximate: they enter stateGrid only through the LEVEL of Theta_{h,t}, which
        reaches the FOC only through dv20 -- the old informal household -- whose weight is gamma_{t-1,0},
        exactly zero in this model. The placeholder keeps that term finite (0*NaN would poison the whole
        FOC, README's "zero-mass slot"). test_esc.py drives the placeholder over the whole unit square and
        asserts z_t does not move; if the informal type is ever given mass, that test fails and this
        shortcut has to go. """
        τ = np.atleast_1d(np.asarray(τ, dtype = float))
        θ = np.broadcast_to(np.asarray(θ, dtype = float), τ.shape)
        d = self.m.LOG.stateGrid(τ, t, θ, tLag, terminal, τ1 = τ, θ1 = θ)
        return self.m.LOG.focGrid(d, t, θ, float(self.db['eps'].xs(t)), terminal)

    def τOfθ(self, t, θ, tLag, terminal, tol = 0.0, polish = True):
        """ tauPolicy_t evaluated on a vector of states theta (shape (K,)): for each, the maximiser of the
        political objective among {l, u} and the downward crossings of z_t (roots1d.selectMax, as
        LOG.solveBackward_t). Vectorised over the (theta, tau) mesh in one z() call -- z_t is elementwise
        in both arguments, so the flattened mesh costs one evaluation, not K.

        polish: brentq the selected interior crossing to solver tolerance inside one grid cell. The grid
        selection alone is only O(spacing^2) accurate (~1e-4 at the default n), and tau_{t0} is a
        CALIBRATION TARGET matched at 1e-8 -- without this the wedge calibration would chase grid noise.
        Corners are never polished: z_t != 0 there is the correct answer, not a residual.

        Returns (tau, atBound, nMax), each (K,). """
        θ = np.atleast_1d(np.asarray(θ, dtype = float))
        τGrid = self.m.LOG.GS['PEE']['solGrids']['τ']
        K, M = θ.size, τGrid.size
        τMesh = np.tile(τGrid, K)                      # (K*M,)
        θMesh = np.repeat(θ, M)                        # (K*M,)
        zz = self.z(t, τMesh, θMesh, tLag, terminal).reshape(K, M)
        τ = np.empty(K); atBound = np.empty(K, dtype = bool); nMax = np.empty(K, dtype = int)
        for k in range(K):
            sel = roots1d.selectMax(τGrid, zz[k], tol = tol)
            τ[k], atBound[k], nMax[k] = sel['x'], bool(sel['atBound']), int(sel['nMax'])
            if polish and not atBound[k]:
                τ[k] = self._polish(t, τ[k], θ[k], tLag, terminal, τGrid)
        return τ, atBound, nMax

    def _polish(self, t, τ, θt, tLag, terminal, τGrid):
        """ Sharpen one interior crossing to solver tolerance. Brackets by the grid cell containing it and
        widens by whole cells if the selection sat on a node; returns the unpolished value if no sign
        change can be bracketed (which selectMax's own tolerance can allow at a tangential crossing). """
        step = τGrid[1] - τGrid[0]
        f = lambda x: float(self.z(t, x, θt, tLag, terminal)[0])
        for k in (1, 2, 4):
            a, b = max(τ - k*step, τGrid[0]), min(τ + k*step, τGrid[-1])
            fa, fb = f(a), f(b)
            if np.isfinite(fa) and np.isfinite(fb) and fa*fb < 0:
                return float(optimize.brentq(f, a, b, xtol = 1e-12, rtol = 8.9e-16))
        return float(τ)

    def τAt(self, t, θt):
        """ tauPolicy_t(theta_t) at ONE state, solved rather than interpolated. simulate() uses this: the
        policy function is tabulated on self.θGrid and interpolating it back costs O(spacing^2), which at
        the default grid is ~5e-6 in tau -- invisible next to any economic effect, but tau_{t0} is a
        calibration target matched at 1e-8, so the realised path should not carry avoidable grid error. """
        tIdx = self.db['t']
        pos = tIdx.get_loc(t)
        tLag = tIdx[pos-1] if pos > 0 else self.B.tFirst
        τ, _, _ = self.τOfθ(t, np.atleast_1d(θt), tLag, terminal = (t == tIdx[-1]))
        return float(τ[0])

    # ------------------------------------------------------------------ the objective
    def objective(self, t, tLag, t1, τt, θt, θ1, cont, s_ = 1., siRatio_ = None):
        """ W_t over a mesh of (state theta_t, candidate theta1), all arguments flattened to (M,).

        cont: {'τ1': tau_{t+1}(theta1), 'θ2': theta_{t+2}(theta1), 'τ2': tau_{t+2}(theta2),
               'terminal1': whether t+1 is the terminal period} -- the continuation, already evaluated at
        theta1 by solveBackward. s_ = s_{t-1}; the argmax does not depend on it (module docstring), and it
        defaults to the appendix's own normalisation.

        siRatio_: s_{t-1,i}/s_{t-1}, shape (ni,) or (M,ni). None (the leaded default) recomputes it from
        the candidate (tau_t, theta_t), matching LOG.stateGrid. PermanentLOG passes it explicitly, because
        there theta_t is the object being chosen and letting the predetermined state move with it would
        fold a channel into the choice that the policy maker takes as given (see base.dlnc2i_dτ).

        Returns (W, parts) with W shape (M,). """
        BG = self.BG
        βi, βi1 = BG.get('βi', t), BG.get('βi', t1)
        τ1 = cont['τ1']

        # --- period t equilibrium at the candidate
        Γs = BG.Γs(βi, τ1, θ1, t)
        Θh = BG.Θh(τt, τ1, θ1, Γs, t)
        h = BG.h(Θh, s_, t)
        s = BG.s(BG.Θs(Θh, Γs, t), s_, t)

        # --- period t+1, needed only for R_{t+1}
        if cont['terminal1']:
            Θh1 = BG.ΘhTerminal(τ1, t1)
        else:
            Γs1 = BG.Γs(βi1, cont['τ2'], cont['θ2'], t1)
            Θh1 = BG.Θh(τ1, cont['τ2'], cont['θ2'], Γs1, t1)
        h1 = BG.h(Θh1, s, t1)
        R1 = BG.Rlead(s, h1, t)

        # --- indirect utilities. The old: c_{2,t}^i at the predetermined s_{t-1,i}/s_{t-1}, a function of
        # (tau_t, theta_t) -- NOT of theta1, so it shifts W_t's level without touching the argmax.
        # Computed exactly anyway: it costs nothing and makes W_t the actual objective.
        if siRatio_ is None:
            Γs_ = BG.Γs(BG.get('βi', tLag), τt, θt, tLag)
            siRatio_ = BG.si_s(BG.get('βi', tLag), τt, θt, Γs_, tLag)
        c2 = BG.c2i(h, s_, τt, θt, siRatio_, t)
        tc1 = BG.tildec1i(h, βi, τ1, θ1, Γs, t)

        v2 = np.log(c2)
        v1 = (1+βi)*np.log(tc1) + βi*np.log(R1)[:, None]
        old, young = self.weights(t)
        W = (old*v2).sum(axis = -1) + (young*v1).sum(axis = -1)
        return W, {'h': h, 's': s, 'R1': R1, 'Γs': Γs, 'Θh': Θh}

    # ------------------------------------------------------------------ one period
    def solveBackward_t(self, t, tLag, t1, cont, terminal1):
        """ One period of the recursion: tauPolicy_t on the state grid, then thetaPolicy_t by maximising
        W_t over self.θCand at each state node.

        cont: {'τPolicy1': callable theta1 -> tau_{t+1}, 'θPolicy1': callable or None (None iff t+1 is
        terminal), 'τPolicy2': callable theta2 -> tau_{t+2} or None}. """
        τState, atBoundτ, nMaxτ = self.τOfθ(t, self.θGrid, tLag, terminal = False)

        K, C = self.nθ, self.nθCand
        θtM = np.repeat(self.θGrid, C)                 # (K*C,)
        τtM = np.repeat(τState, C)
        θ1M = np.tile(self.θCand, K)

        τ1 = cont['τPolicy1'](θ1M)
        if terminal1:
            θ2 = τ2 = None
        else:
            θ2 = cont['θPolicy1'](θ1M)
            τ2 = cont['τPolicy2'](θ2)
        W, parts = self.objective(t, tLag, t1, τtM, θtM, θ1M,
                                  {'τ1': τ1, 'θ2': θ2, 'τ2': τ2, 'terminal1': terminal1})
        W = W.reshape(K, C)

        θNext = np.empty(K); atBoundθ = np.empty(K, dtype = bool)
        for k in range(K):
            θNext[k], atBoundθ[k] = self._argmax(self.θCand, W[k])
        return {'θGrid': self.θGrid.copy(), 'τ': τState, 'θNext': θNext,
                'atBoundτ': atBoundτ, 'nMaxτ': nMaxτ, 'atBoundθ': atBoundθ, 'W': W,
                'stateSpread': float(θNext.max() - θNext.min())}

    # ------------------------------------------------------------------ the recursion
    def solveBackward(self, tol = 0.0):
        """ The whole sequence of policy functions, backwards from the terminal period.

        The terminal period T-1 has no theta_T to choose and its tau uses the terminal FOC (beta = 0, as
        LOG.solveBackward_t's `terminal`). Period T-2 is the first with a theta choice, and its
        continuation reaches only into T-1, whose Theta_h is the terminal formula.

        Returns {t: report}. Interpolation between grid nodes is piecewise linear (np.interp) throughout
        -- notes/crossCuttingFindings.md #4/#5: this module's lineage has been bitten by adaptive knots
        and by cubic overshoot in exactly this role, and a policy function about to be maximised over must
        not carry interpolation wiggles. """
        self._requireZeroMass()
        tIdx = self.db['t']
        sols = {}
        with self.BG.cacheParams():
            tT = tIdx[-1]
            posT = tIdx.get_loc(tT)
            tLagT = tIdx[posT-1] if posT > 0 else self.B.tFirst
            τT, atBoundτT, nMaxτT = self.τOfθ(tT, self.θGrid, tLagT, terminal = True)
            sols[tT] = {'θGrid': self.θGrid.copy(), 'τ': τT, 'θNext': None,
                        'atBoundτ': atBoundτT, 'nMaxτ': nMaxτT, 'atBoundθ': None, 'terminal': True}

            for pos in range(len(tIdx)-2, -1, -1):
                t, t1 = tIdx[pos], tIdx[pos+1]
                tLag = tIdx[pos-1] if pos > 0 else self.B.tFirst
                terminal1 = (t1 == tIdx[-1])
                s1 = sols[t1]
                cont = {'τPolicy1': self._interp(s1['θGrid'], s1['τ']),
                        'θPolicy1': None if terminal1 else self._interp(s1['θGrid'], s1['θNext']),
                        'τPolicy2': None}
                if not terminal1:
                    s2 = sols[tIdx[pos+2]]
                    cont['τPolicy2'] = self._interp(s2['θGrid'], s2['τ'])
                sols[t] = self.solveBackward_t(t, tLag, t1, cont, terminal1) | {'terminal': False}
        return sols

    @staticmethod
    def _interp(x, y):
        """ Piecewise-linear interpolant, clamped outside [x0, xN] (np.interp's own default). """
        return lambda q: np.interp(q, x, y)

    # ------------------------------------------------------------------ forward simulation
    def simulate(self, sols, θ0, tPin = None):
        """ The equilibrium paths of theta and tau implied by the policy functions, from an inherited
        design theta = theta0.

        theta_t is the STATE at t (chosen at t-1), so theta[pos+1] = thetaPolicy_t(theta[pos]) and
        tau[pos] = tauPolicy_t(theta[pos]).

        tPin: hold theta at theta0 for every period up to AND INCLUDING this one, letting the choice bind
        only from tPin onward -- i.e. the design is history (data) until tPin and a political outcome
        after it. That is the timing the wedge calibration targets (thetaPolicy_{tPin}(theta0) = theta0),
        and it makes the baseline and endogenous paths agree exactly up to tPin, which is what lets the
        two be compared at tPin at all. None = the choice binds from the first period. """
        tIdx = self.db['t']
        θ = np.empty(len(tIdx)); τ = np.empty(len(tIdx))
        θ[0] = θ0
        pin = None if tPin is None else tIdx.get_loc(tPin)
        for pos, t in enumerate(tIdx):
            if pin is not None and pos <= pin:
                θ[pos] = θ0
            s = sols[t]
            τ[pos] = self.τAt(t, θ[pos])
            if pos < len(tIdx)-1:
                θ[pos+1] = np.interp(θ[pos], s['θGrid'], s['θNext'])
        return pd.Series(θ, index = tIdx), pd.Series(τ, index = tIdx)

    def choiceAt(self, sols, t, θt):
        """ thetaPolicy_t(theta_t) at one state -- what the calibration of the wedge targets. """
        s = sols[t]
        return float(np.interp(θt, s['θGrid'], s['θNext']))


class LeadedCRRA(LeadedBase):
    r""" The leaded choice under CRRA, solved as a PATH rather than as a policy function.

    Under CRRA neither LOG simplification survives: v = c^{1-1/rho}/(1-1/rho) does not turn products into
    sums, so W_t is not additively separable in (tau_t, theta_{t+1}) and s_{t-1} does not drop out. The
    honest Markov object is a policy function over the two-dimensional state (s_{t-1}, theta_t), i.e. a
    2-D version of policy.py's CRRA grid. This class does something cheaper and says exactly what it
    assumes:

        Iterate on the equilibrium PATH {theta_t}. At each t, evaluate W_t over a grid of candidate
        theta_{t+1}, re-solving the WHOLE CRRA equilibrium (model.solvePEE_CRRA, unchanged) for each
        candidate while holding theta_{t+2}, ... at the current iterate. Take the argmax, sweep forward,
        repeat until the path stops moving.

    WHAT THAT ASSUMES. Holding theta_{t+2} fixed while theta_{t+1} varies is exactly right if the choice
    at t+1 does not respond to the design it inherits. Under LOG that is not an approximation at all --
    thetaPolicy is provably constant in theta_t (module docstring). Under CRRA it is an approximation, and
    stateSensitivity() measures it directly: it re-runs the t+1 choice at two different theta_{t+1} and
    reports how far the response moves. Report that number alongside any result from this class; if it is
    not small, the 2-D grid is required and this shortcut is not good enough.

    Re-solving for each candidate is also what makes the envelope logic right: tau_t is re-optimised at
    every candidate, so its own response to theta_{t+1} contributes nothing to first order, and W_t is
    evaluated at the equilibrium tau rather than at a stale one. """

    def __init__(self, m, nθCand = 13, **kwargs):
        self.m = m
        self.B, self.BG, self.BT = m.B, m.BG, m.BT
        self.db = m.db
        self.ni, self.T = m.ni, m.T
        self.nθCand = nθCand
        self.θCand = np.linspace(0., 1., nθCand)
        self.kwargs = kwargs

    # ------------------------------------------------------------------ one equilibrium
    def solveθPath(self, θ, s0 = None, **kwargs):
        """ The CRRA politico-economic equilibrium at a GIVEN design path (model.solvePEE_CRRA, which
        already accepts a time-varying theta -- CRRA.solveBackward indexes theta[pos] per period). """
        ε = self.db['eps'].values.astype(float)
        return self.m.solvePEE_CRRA(θ = np.asarray(θ, dtype = float), ε = ε, s0 = s0, **kwargs)

    def W(self, out, pos):
        """ W_t at position `pos` of a solved equilibrium (solveθPath's return). CRRA indirect utilities,
        same blocs and weights as the LOG case. """
        t = self.db['t'][pos]
        rep = out['report']
        ρ = float(self.BG.get('ρ', t))
        q = 1 - 1/ρ
        c1 = rep['tildec1i'].xs(t).values.astype(float)
        c2 = rep['c2i'].xs(t).values.astype(float)
        B = rep['B'].xs(t).values.astype(float)
        v1 = (1+B)*c1**q/q
        v2 = c2**q/q
        old, young = self.weights(t)
        return float((old*v2).sum() + (young*v1).sum())

    # ------------------------------------------------------------------ the path iteration
    def solvePath(self, θ0, pinPos = 0, maxIter = 6, tol = 1e-4, s0 = None, verbose = True,
                  solveKwargs = None):
        """ Iterate the design path to a fixed point.

        theta[pos] for pos <= pinPos is held at theta0 (the inherited design -- history, not a choice, as
        LeadedLOG.simulate's tPin). Positions pinPos+1 .. T-1 are chosen, swept forward, Gauss-Seidel
        (each choice sees the updated earlier entries and the previous iterate's later ones).

        Returns {'θ', 'out', 'iterations', 'converged', 'atBound', 'history', 'step'}. """
        self._requireZeroMass()
        kw = dict(solveKwargs or {})
        T = len(self.db['t'])
        θ = np.full(T, float(θ0))
        history = [θ.copy()]
        atBound = np.zeros(T, dtype = bool)
        step = np.inf
        for it in range(maxIter):
            θNew = θ.copy()
            for pos in range(pinPos, T-1):
                Ws = np.empty(self.nθCand)
                for k, cand in enumerate(self.θCand):
                    θTry = θNew.copy()
                    θTry[pos+1] = cand
                    try:
                        Ws[k] = self.W(self.solveθPath(θTry, s0 = s0, **kw), pos)
                    except Exception:
                        Ws[k] = -np.inf        # an infeasible candidate is not a maximiser
                if not np.any(np.isfinite(Ws)):
                    raise RuntimeError(f'LeadedCRRA: every candidate failed to solve at pos={pos}.')
                θNew[pos+1], atBound[pos+1] = self._argmax(self.θCand, Ws)
            step = float(np.max(np.abs(θNew - θ)))
            θ = θNew
            history.append(θ.copy())
            if verbose:
                print('    iter {}: max|dθ|={:.5f}  θ={}'.format(
                    it, step, ' '.join('{:.4f}'.format(x) for x in θ[:6])))
            if step < tol:
                break
        out = self.solveθPath(θ, s0 = s0, **kw)
        return {'θ': pd.Series(θ, index = self.db['t']), 'out': out, 'iterations': it+1,
                'converged': step < tol, 'atBound': atBound, 'history': history, 'step': step}

    # ------------------------------------------------------------------ the assumption, measured
    def stateSensitivity(self, θ, pos, δ = 0.05, s0 = None, solveKwargs = None):
        """ How much the choice at pos+1 responds to the design it inherits -- the quantity solvePath
        assumes away (see the class docstring). Perturbs theta_{pos+1} by +/-delta, re-optimises
        theta_{pos+2} at each, and returns d(theta_{pos+2})/d(theta_{pos+1}).

        Zero under LOG by the separability argument; whatever it is under CRRA is the error term of the
        path iteration, and belongs in the write-up next to the result. """
        kw = dict(solveKwargs or {})
        θ = np.asarray(θ, dtype = float)
        got = {}
        for s, lab in ((-δ, 'lo'), (+δ, 'hi')):
            θP = θ.copy()
            θP[pos+1] = float(np.clip(θ[pos+1] + s, 0., 1.))
            Ws = np.empty(self.nθCand)
            for k, cand in enumerate(self.θCand):
                θTry = θP.copy()
                θTry[pos+2] = cand
                try:
                    Ws[k] = self.W(self.solveθPath(θTry, s0 = s0, **kw), pos+1)
                except Exception:
                    Ws[k] = -np.inf
            got[lab] = (self._argmax(self.θCand, Ws)[0], θP[pos+1])
        (chLo, θLo), (chHi, θHi) = got['lo'], got['hi']
        slope = (chHi - chLo)/(θHi - θLo) if θHi != θLo else np.nan
        return {'slope': float(slope), 'choiceLo': chLo, 'choiceHi': chHi, 'θLo': θLo, 'θHi': θHi}


class Interp2D:
    """ A policy table over the 2-D state (s_, θ): piecewise-linear and linearly EXTRAPOLATING along s
    (griddedInterp1D per θ column, NaN nodes dropped per column), piecewise-linear and clamped along θ
    (the θ grid spans the whole unit interval, so no θ query can leave it). Linear throughout on purpose
    -- notes/crossCuttingFindings.md #4/#5: an object feeding an argmax or a numerical derivative must
    not carry interpolation wiggles. A column with fewer than two finite nodes evaluates to NaN. """

    def __init__(self, sGrid, θGrid, tab):
        """ tab: (ns, nθ) values on (sGrid, θGrid). """
        self.θGrid = np.asarray(θGrid, dtype = float)
        sGrid = np.asarray(sGrid, dtype = float)
        self.cols = []
        for k in range(tab.shape[1]):
            col = np.asarray(tab[:, k], dtype = float)
            ok = np.isfinite(col)
            self.cols.append(griddedInterp1D(sGrid[ok], col[ok]) if ok.sum() >= 2 else None)

    def __call__(self, s, θ):
        s, θ = np.broadcast_arrays(np.asarray(s, dtype = float), np.asarray(θ, dtype = float))
        shape = s.shape
        sf, θf = s.reshape(-1), θ.reshape(-1)
        gθ = self.θGrid
        j = np.clip(np.searchsorted(gθ, θf) - 1, 0, len(gθ) - 2)
        w = np.clip((θf - gθ[j])/(gθ[j+1] - gθ[j]), 0., 1.)
        V = np.stack([np.full_like(sf, np.nan) if c is None else np.asarray(c(sf), dtype = float)
                      for c in self.cols], axis = 1)
        idx = np.arange(len(sf))
        return ((1 - w)*V[idx, j] + w*V[idx, j+1]).reshape(shape)


class LeadedCRRA2D(CRRA, LeadedBase):
    r""" The TRUE leaded choice under CRRA: a sequence of policy functions over the two-dimensional state
    (s_{t-1}, θ_t), identified by backward iteration -- the "honest Markov object" LeadedCRRA's docstring
    names and does not compute. No path iteration and no held-fixed future: the choice of θ_{t+1} at t
    sees continuation policies τ_{t+1}(s_t, θ_{t+1}) and h_{t+1}(s_t, θ_{t+1}) that already embed the
    choice at t+1 responding to the design it inherits.

    STRUCTURE, per period t (mirrors policy.CRRA's alg:CRRA:grid with one extra layer):

      1. For every (τ_t, s_{t-1}, θ_{t+1}-candidate): resolve the equilibrium state s_t (the same fixed
         point as the exogenous solver -- _rootS -- with the continuation read off 2-D interpolants).
      2. z_t on that grid. Everything except the old formal households' dv2i is independent of the
         inherited design θ_t (θ_t enters only through the benefit split of the CURRENT old), so the
         grid carries no θ_t axis: dv2i alone is recomputed per θ_t node, with the numerical
         τ-derivatives (the expensive splines) shared across all of them.
      3. τ*(s_, θ_t, θ1): selectMax along τ, per state and candidate -- the same corner/multiplicity
         handling as everywhere else in this lineage.
      4. W_t at the selected τ* (young: Σ γμν(1+B_{t+1})c̃_1^{1-1/ρ}/(1-1/ρ) = Σ young·hatc1iPow/q; old:
         Σ γωpμ c_2^{1-1/ρ}/q), argmax over θ1 with parabolic refinement (LeadedBase._argmax), corners
         preserved. τ at the refined θ1 by linear interpolation along the candidate axis.
      5. Tabulate τ/θNext/s/h/Γs at the chosen policies, smooth τ along s with PINNED knots
         (crossCuttingFindings #5), rebuild the tables' interpolants for period t-1.

    The recursion is DIRECT -- terminal condition plus one backward pass -- so unlike LeadedCRRA's path
    iteration it needs no warm start and no convergence tolerance; the path iteration is kept as the
    cheap cross-check (validated against this class, not the other way around).

    PINNING (the timing the wedge calibration targets) is built into the recursion rather than only the
    simulation: for positions pos < pinPos the choice of θ_{pos+1} is FORCED to θPin (the candidate grid
    collapses to that one point), because under CRRA τ_t genuinely depends on θ_{t+1} -- pinning only at
    simulation time would evaluate τ off the pinned continuation. Under LOG the distinction vanishes,
    which is why LeadedLOG can pin in simulate() alone.

    Grid settings are borrowed from the model's exogenous solver (self.GS = m.CRRA.GS at solve time), so
    a driver that tunes m.CRRA.initGS(...) tunes this class with it. """

    def __init__(self, m, nθ = 13, nθCand = 21, **kwargs):
        super().__init__(m, **kwargs)
        self.nθ, self.nθCand = nθ, nθCand
        self.θGrid = np.linspace(0., 1., nθ)
        self.θCand = np.linspace(0., 1., nθCand)

    # ------------------------------------------------------------------ the one genuine override
    def stateApprox_t(self, τ, s, t, θ1, solp):
        """ CRRA.stateApprox_t with a 2-D continuation: solp's τPolicy/hPolicy take (s_t, θ_{t+1}) and
        θ1 is a flat array over the mesh rather than a scalar. Everything downstream broadcasts. """
        BG = self.BG
        τ1, h1 = solp['τPolicy'](s, θ1), solp['hPolicy'](s, θ1)
        B1 = BG.B(s, h1, t)
        Γs = BG.Γs(B1, τ1, θ1, t)
        Θh = BG.Θh(τ, τ1, θ1, Γs, t)
        Θs = BG.Θs(Θh, Γs, t)
        return {'τ1': τ1, 'h1': h1, 'B1': B1, 'Γs': Γs, 'Θh': Θh, 'Θs': Θs}

    # ------------------------------------------------------------------ state fixed point on the grid
    def _solveStateGrid(self, τGrid, s_Grid, θ1Grid, sCand, t, sol1):
        """ s_t over the (τ, s_, θ1) product, flat in C-order. Θs is evaluated on (τ, sCand, θ1) once and
        broadcast across s_ (only the residual's (s_/ν)^σ factor involves it), exactly as the parent's
        solveStateApprox_t broadcasts across its 1-D state. """
        gA = CartesianGrid(τ = τGrid, s = sCand, θ1 = θ1Grid)
        Θs = gA.reshape(self.stateApprox_t(gA.flat['τ'], gA.flat['s'], t, gA.flat['θ1'], sol1)['Θs'])
        nτ, nsC, nθ1 = Θs.shape
        ns_ = len(s_Grid)
        big = np.ascontiguousarray(np.broadcast_to(Θs.transpose(1, 0, 2)[:, :, None, :],
                                                   (nsC, nτ, ns_, nθ1))).reshape(nsC, -1)
        s_flat = np.ascontiguousarray(np.broadcast_to(s_Grid[None, :, None],
                                                      (nτ, ns_, nθ1))).reshape(-1)
        return self._rootS(big, sCand, s_flat, t)

    # ------------------------------------------------------------------ economics at resolved states
    def _econCore(self, τ, s, s_, θ1, t, tLag, t1, ε, ε1, sol1):
        """ stateGrid_t minus its θ_t block (Γs_/si_s_/c2i live in _zAtθ/_Wgrid instead): everything the
        FOC and the objective need that does NOT depend on the inherited design. Flat arrays throughout. """
        BG = self.BG
        self._requireCRRA(t)
        d = self.stateApprox_t(τ, s, t, θ1, sol1)
        d['τ'], d['s'], d['s_'] = τ, s, s_
        d['h'] = BG.h(d['Θh'], s_, t)
        d['B'] = BG.B(s_, d['h'], tLag)
        d['hatc1iPow'] = BG.hatc1iPow(d['h'], d['B1'], d['τ1'], θ1, d['Γs'], t)
        d['lnhatc1i'] = BG.lnhatc1i(d['h'], d['B1'], d['τ1'], θ1, d['Γs'], t)
        d['tc20'] = BG.tildec20(d['h'], s_, ε, τ, t)
        d['tc20_1'] = BG.tildec20(d['h1'], s, ε1, d['τ1'], t1)
        return d

    def _focParts(self, d, g, t, ε):
        """ The θ_t-independent pieces of focGrid_t, including every numerical τ-derivative -- computed
        once and shared across the θ_t loop (the splines dominate the period's cost). """
        BG, τ, τGrid = self.BG, d['τ'], g.values('τ')
        p = 1 - 1/BG.get('ρ', t)
        grad = lambda y: griddedGradient1D(τGrid, g.reshape(y)).reshape(np.shape(y))
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            dlnh = grad(np.log(d['h']))
            dv1i = d['hatc1iPow'] * grad(d['lnhatc1i'])
            dv10 = BG.get('β0', t) * d['tc20_1']**p * grad(np.log(d['tc20_1']))
            dv20 = d['tc20']**p * BG.dlnc20_dτ(dlnh, τ, ε, d['Θh'], t)
        return {'p': p, 'dlnh': dlnh, 'dv1i': dv1i, 'dv10': dv10, 'dv20': dv20}

    def _zAtθ(self, d, parts, θt, t, tLag):
        """ z_t at one inherited design θt: only dv2i moves (see the class docstring), everything else is
        read from parts. """
        BG, τ = self.BG, d['τ']
        Γs_ = BG.Γs(d['B'], τ, θt, tLag)
        si_s_ = BG.si_s(d['B'], τ, θt, Γs_, tLag)
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            c2i = BG.c2i(d['h'], d['s_'], τ, θt, si_s_, t)
            dv2i = c2i**parts['p'] * BG.dlnc2i_dτ(parts['dlnh'], τ, θt, si_s_, t)
        return BG.FOC(parts['dv1i'], parts['dv10'], dv2i, parts['dv20'], t)

    def _econAt(self, τF, s_F, θtF, θ1F, sCand, t, tLag, t1, ε, ε1, sol1):
        """ Re-solve the state fixed point and evaluate (W, s, h, Γs) at ARBITRARY flat points
        (τ, s_, θt, θ1) -- used at the selected τ* (step 4) and at the final smoothed tables (step 5),
        where τ no longer sits on the grid. """
        BG = self.BG
        N, nsC = τF.size, len(sCand)
        τR = np.ascontiguousarray(np.broadcast_to(τF, (nsC, N))).reshape(-1)
        θ1R = np.ascontiguousarray(np.broadcast_to(θ1F, (nsC, N))).reshape(-1)
        sR = np.ascontiguousarray(np.broadcast_to(sCand[:, None], (nsC, N))).reshape(-1)
        Θs = self.stateApprox_t(τR, sR, t, θ1R, sol1)['Θs'].reshape(nsC, N)
        sPt, nR = self._rootS(Θs, sCand, s_F, t)
        d = self._econCore(τF, sPt, s_F, θ1F, t, tLag, t1, ε, ε1, sol1)
        q = float(1 - 1/self.BG.get('ρ', t))
        old, young = self.weights(t)
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            Γs_ = BG.Γs(d['B'], τF, θtF, tLag)
            si_s_ = BG.si_s(d['B'], τF, θtF, Γs_, tLag)
            c2 = BG.c2i(d['h'], s_F, τF, θtF, si_s_, t)
            W = (young*d['hatc1iPow']).sum(axis = -1)/q + (old*c2**q).sum(axis = -1)/q
        return {'W': W, 's': sPt, 'h': d['h'], 'Γs': d['Γs'], 'nRoots': nR}

    # ------------------------------------------------------------------ one period
    def solveBackward_t2D(self, sol1, t, tLag, t1, ε, ε1, sGrid, sCand, θ1Grid, choose):
        """ One period of the recursion (steps 1-5 of the class docstring). θ1Grid: the candidate grid
        for θ_{t+1}; a pinned period passes the single forced value and choose = False. Returns the
        period dict with (ns, nθ) tables and their Interp2D interpolants. """
        τGrid = self.GS['PEE']['solGrids']['τ']
        nθ, ns_, nθ1 = self.nθ, len(sGrid), len(θ1Grid)
        g = CartesianGrid(τ = τGrid, s_ = sGrid, θ1 = θ1Grid)
        with self.BG.cacheParams():
            s, nRoots = self._solveStateGrid(τGrid, sGrid, θ1Grid, sCand, t, sol1)
            d = self._econCore(g.flat['τ'], s, g.flat['s_'], g.flat['θ1'], t, tLag, t1, ε, ε1, sol1)
            parts = self._focParts(d, g, t, ε)

            τStar = np.empty((nθ, ns_, nθ1))
            atBoundτ = np.zeros((nθ, ns_, nθ1), dtype = bool)
            for it, θt in enumerate(self.θGrid):
                sel = roots1d.selectMaxND(g, self._zAtθ(d, parts, θt, t, tLag), 'τ')
                τStar[it], atBoundτ[it] = sel['x'], sel['atBound']

            # --- W at the selected τ*, per (θt, s_, θ1)
            θtF = np.repeat(self.θGrid, ns_*nθ1)
            s_F = np.tile(np.repeat(sGrid, nθ1), nθ)
            θ1F = np.tile(θ1Grid, nθ*ns_)
            at = self._econAt(τStar.reshape(-1), s_F, θtF, θ1F, sCand, t, tLag, t1, ε, ε1, sol1)
            W = at['W'].reshape(nθ, ns_, nθ1)

            # --- the choice
            θNext = np.full((nθ, ns_), np.nan)
            atBoundθ = np.zeros((nθ, ns_), dtype = bool)
            τSel = np.full((nθ, ns_), np.nan)
            if choose:
                Wm = np.where(np.isfinite(W), W, -np.inf)
                for it in range(nθ):
                    for j in range(ns_):
                        if not np.any(np.isfinite(W[it, j])):
                            continue
                        θNext[it, j], atBoundθ[it, j] = self._argmax(θ1Grid, Wm[it, j])
                        τSel[it, j] = np.interp(θNext[it, j], θ1Grid, τStar[it, j])
            else:
                θNext[:] = θ1Grid[0]
                τSel = τStar[:, :, 0].copy()

            # --- smooth τ along s per θt column (pinned knots, #5), then retabulate the equilibrium at
            # the final (τ, θNext) so the tables the previous period interpolates are self-consistent.
            knots = self.GS['PEE']['gridSettings']['smoothKnots']
            τTab = griddedSmooth1D(sGrid, τSel.T, s = 1e-5, knots = knots)     # (ns, nθ)
            θTab = θNext.T                                                     # (ns, nθ)
            fin = self._econAt(τTab.T.reshape(-1), np.tile(sGrid, nθ), np.repeat(self.θGrid, ns_),
                               θTab.T.reshape(-1), sCand, t, tLag, t1, ε, ε1, sol1)
            sTab, hTab = fin['s'].reshape(nθ, ns_).T, fin['h'].reshape(nθ, ns_).T
            ΓsTab = fin['Γs'].reshape(nθ, ns_).T

        return {'sGrid': sGrid, 'θGrid': self.θGrid.copy(), 'θ1Grid': np.asarray(θ1Grid, dtype = float),
                'τ': τTab, 'θNext': θTab, 's': sTab, 'h': hTab, 'Γs': ΓsTab,
                'τStar3': τStar, 'W': W, 'atBoundτ': atBoundτ, 'atBoundθ': atBoundθ.T,
                'choose': choose, 'terminal': False,
                'θSpread_s': np.nan if not choose else float(np.nanmax(θTab, axis = 0).max()
                                                            - np.nanmin(θTab, axis = 0).min()),
                'τPolicy': Interp2D(sGrid, self.θGrid, τTab),
                'hPolicy': Interp2D(sGrid, self.θGrid, hTab),
                'sPolicy': Interp2D(sGrid, self.θGrid, sTab),
                'ΓsPolicy': Interp2D(sGrid, self.θGrid, ΓsTab),
                'θPolicy': Interp2D(sGrid, self.θGrid, θTab)}

    def solveTerminal2D(self, ε, sGrid, t, tLag):
        """ The terminal period has no design to choose -- θ_T is its state. One inherited (closed-form)
        CRRA.solveTerminal per θ node, stacked into 2-D tables. """
        ns_ = len(sGrid)
        τTab = np.empty((ns_, self.nθ)); hTab = np.empty((ns_, self.nθ))
        for k, θ in enumerate(self.θGrid):
            rep = self.solveTerminal(float(θ), ε, t = t, sGrid = sGrid)
            τTab[:, k], hTab[:, k] = rep['τ'].values, rep['h'].values
        return {'sGrid': sGrid, 'θGrid': self.θGrid.copy(), 'τ': τTab, 'h': hTab,
                'θNext': None, 'terminal': True, 'choose': False,
                'τPolicy': Interp2D(sGrid, self.θGrid, τTab),
                'hPolicy': Interp2D(sGrid, self.θGrid, hTab)}

    # ------------------------------------------------------------------ the recursion
    def solvePolicies(self, θPin, pinPos = None, sGrid = None, verbose = False):
        """ The whole sequence of 2-D policy functions, backwards from the terminal period.

        θPin: the inherited design -- the value forced on pinned periods AND the reference the default
        state grid is sized at. pinPos: positions pos < pinPos have the choice of θ_{pos+1} forced to
        θPin (the design is history until pinPos, a political outcome from pinPos on -- LeadedCRRA
        .solvePath's own convention); None = every period chooses. Returns {t: period dict}. """
        self._requireZeroMass()
        self.GS = self.m.CRRA.GS                     # borrow the driver-tuned grid settings
        tIdx = self.db['t']
        ε = self.db['eps'].values.astype(float)
        if sGrid is None:
            sGrid = self.defaultSGrid(float(θPin), tIdx[-1], n = self.GS['PEE']['gridSettings']['ns'])
        sGrid = np.asarray(sGrid, dtype = float)

        posT = len(tIdx) - 1
        tT = tIdx[-1]
        tLagT = tIdx[posT-1] if posT > 0 else self.B.tFirst
        sols = {tT: self.solveTerminal2D(ε[posT], sGrid, tT, tLagT)}
        import time as _time
        for pos in range(posT-1, -1, -1):
            t, t1 = tIdx[pos], tIdx[pos+1]
            tLag = tIdx[pos-1] if pos > 0 else self.B.tFirst
            choose = (pinPos is None) or (pos >= pinPos)
            θ1Grid = self.θCand if choose else np.array([float(θPin)])
            tic = _time.time()
            sols[t] = self.solveBackward_t2D(sols[t1], t, tLag, t1, ε[pos], ε[pos+1],
                                             sGrid, sGrid, θ1Grid, choose)
            if verbose:
                print('    t={}: {}  [{:.1f}s]'.format(
                    t, 'choice' if choose else 'pinned', _time.time() - tic))
        return sols

    # ------------------------------------------------------------------ forward simulation
    def s0FixedPoint(self, sols, θ0):
        """ The stationary state of the FIRST period's transition at the inherited design -- the CRRA2D
        counterpart of the steady-state seed the other solvers use for s0. """
        tIdx = self.db['t']
        f = lambda s: float(sols[tIdx[0]]['sPolicy'](s, θ0)) - s
        sg = sols[tIdx[0]]['sGrid']
        a, b = float(sg[0]), float(sg[-1])
        fa, fb = f(a), f(b)
        if np.isfinite(fa) and np.isfinite(fb) and fa*fb < 0:
            return float(optimize.brentq(f, a, b, xtol = 1e-12))
        s = 0.5*(a+b)                                # fall back to iteration from the grid's middle
        for _ in range(200):
            sNew = float(sols[tIdx[0]]['sPolicy'](s, θ0))
            if abs(sNew - s) < 1e-12:
                break
            s = sNew
        return s

    def simulate(self, sols, θ0, s0, pinPos = None):
        """ The equilibrium paths implied by the policy functions, from inherited design θ0 and initial
        state s0. Pinning here only overrides the REALISED θ; a pinned recursion (solvePolicies' pinPos)
        already tabulated its policies at the forced design, so passing the same pinPos twice is
        consistent, and passing it here alone is the LOG-style approximation. Returns (θ, τ, s, h, Γs)
        -- the last three length T-1, for EE_CRRA_solve's warm start. """
        tIdx = self.db['t']
        T = len(tIdx)
        θ = np.empty(T); τ = np.empty(T)
        sPath = np.empty(T-1); hPath = np.empty(T-1); ΓsPath = np.empty(T-1)
        θ[0] = float(θ0)
        s_ = float(s0)
        for pos, t in enumerate(tIdx):
            sol = sols[t]
            τ[pos] = float(sol['τPolicy'](s_, θ[pos]))
            if pos < T-1:
                nxt = float(sol['θPolicy'](s_, θ[pos]))
                θ[pos+1] = float(θ0) if (pinPos is not None and pos < pinPos) else nxt
                hPath[pos] = float(sol['hPolicy'](s_, θ[pos]))
                ΓsPath[pos] = float(sol['ΓsPolicy'](s_, θ[pos]))
                s_ = float(sol['sPolicy'](s_, θ[pos]))
                sPath[pos] = s_
        return (pd.Series(θ, index = tIdx), pd.Series(τ, index = tIdx), sPath, hPath, ΓsPath)

    def choiceAt(self, sols, t, s_, θt):
        """ θPolicy_t(s_, θ_t) at one state. """
        return float(sols[t]['θPolicy'](s_, θt))


class PermanentLOG(LeadedLOG):
    r""" The PERMANENT choice of theta (app:ESC, "Permanent choice of theta"), LOG case.

    At the reform date t0 the electorate chooses a theta expected to hold forever: theta_t = theta for
    every t >= t0. It therefore enters THREE channels at once, where the leaded choice enters one:

        the sequential channel   theta_{t0} re-splits the CURRENT retirees' benefits (the appendix's
                                 E_{2,t}^{i,theta}), which is what corners the sequential choice at zero;
        the leaded channel       theta_{t0+1} moves h_{t0}, hence every period-t0 quantity;
        the continuation         theta_{t0+k} moves tau_{t0+k} and the whole future path.

    TWO THINGS MAKE THIS CHEAPER THAN THE APPENDIX'S RECIPE, and both are worth stating because they are
    not obvious from the write-up, which proposes a two-dimensional grid over (tau_{t0}, theta).

    1. THE JOINT CHOICE CONCENTRATES. dW/dtau = 0 is the ordinary tau first-order condition evaluated at
       theta_t = theta -- the permanent choice adds nothing to it, since theta is not a function of tau.
       So the optimal tau at any candidate theta is just tauPolicy_{t0}(theta), already available, and what
       is left is a ONE-dimensional maximisation over theta. The 2-D grid is not wrong, only redundant.

    2. tau_t FOR t > t0 IS THE ORDINARY PEE AT CONSTANT theta. Nothing about the continuation is special:
       once theta is fixed forever, later periods face exactly the exogenous-theta problem tauPolicy
       already solves. There is no recursion to run.

    THE ONE THING THAT MUST NOT BE GOT WRONG. s_{t0-1,i}/s_{t0-1} is a PREDETERMINED state, and here theta
    enters it (through theta_{t0}) in a way it never does in the leaded problem. Savings at t0-1 are SUNK
    when the vote is taken at t0: a voter comparing two candidates does not get a different s_{t0-1,i}
    under each. So the ratio is one number, passed in as an argument, and never recomputed per candidate --
    the same error base.dlnc2i_dτ's docstring forbids for tau. Letting it move is worth 0.13 in theta, and
    is also internally inconsistent with the tau it is paired with: si_s depends on tau_t0 as well as
    theta_t0, while tau_t0 comes from z_t = 0, which is BUILT holding the ratio fixed. It would break the
    concentration argument above.

    WHICH number it is pinned at is a separate question, and it is the timing that answers it. The vote is
    ANTICIPATED: households arrive at t0 knowing a design will be chosen, so the savings they made at t0-1
    were made against the design that actually wins. Rational expectations therefore make the choice a
    FIXED POINT -- solveFixedPoint below -- and not the incumbent's ratio, which is the unanticipated
    reading. The two coincide exactly wherever the chosen design equals the incumbent one, which is what
    the wedge calibration targets, so the calibrated p is the same under both; they separate only away
    from it. ModelESC.solvePermanent exposes all three readings and reports the gaps. """

    def τPath(self, θ, tFrom = None):
        """ tau_t for every t >= tFrom given a design path: the ordinary PEE, period by period, since z_t
        depends on (tau_t, theta_t) alone -- so a design that is one number before t0 and another from t0
        on needs no more work than a constant one. theta: scalar (constant) or a length-T path. Periods
        before tFrom are left NaN -- they are not part of this experiment and must not be read. """
        tIdx = self.db['t']
        θPath = np.full(len(tIdx), float(θ)) if np.isscalar(θ) else np.asarray(θ, dtype = float)
        out = np.full(len(tIdx), np.nan)
        start = 0 if tFrom is None else tIdx.get_loc(tFrom)
        for pos, t in enumerate(tIdx):
            if pos >= start:
                out[pos] = self.τAt(t, θPath[pos])
        return out

    def siRatioAt(self, t0, θ):
        """ s_{t0-1,i}/s_{t0-1} implied by a permanent design theta in force from t0 onward, shape (ni,).

        Eq (EE:si_s) at vintage t0-1 is a function of DATE-t0 policy alone, so the kinked path the reform
        actually is -- the incumbent design before t0, theta from t0 -- gives the same ratio as a constant
        theta path, and the fixed point below stays a scalar problem. Verified against the solved baseline
        report in test_esc.py. """
        tIdx = self.db['t']
        tLag = tIdx[tIdx.get_loc(t0)-1]
        τ0, θv = np.atleast_1d(self.τAt(t0, float(θ))), np.atleast_1d(float(θ))
        with self.BG.cacheParams():
            β_ = self.BG.get('βi', tLag)
            Γs_ = self.BG.Γs(β_, τ0, θv, tLag)
            return np.asarray(self.BG.si_s(β_, τ0, θv, Γs_, tLag), dtype = float).ravel()

    def objectiveOverθ(self, t0, siRatio_, θCand = None, s_ = 1.):
        """ W_{t0} over a grid of candidate permanent designs, fully vectorised.

        siRatio_: the pinned predetermined state, shape (ni,). See the class docstring for why it is an
        argument rather than something recomputed here. """
        th = self.θCand if θCand is None else np.asarray(θCand, dtype = float)
        tIdx = self.db['t']
        pos = tIdx.get_loc(t0)
        tLag = tIdx[pos-1] if pos > 0 else self.B.tFirst
        t1 = tIdx[pos+1]
        terminal1 = (t1 == tIdx[-1])

        τ0, _, _ = self.τOfθ(t0, th, tLag, terminal = False)
        τ1, _, _ = self.τOfθ(t1, th, t0, terminal = terminal1)
        if terminal1:
            τ2 = None
        else:
            t2 = tIdx[pos+2]
            τ2, _, _ = self.τOfθ(t2, th, t1, terminal = (t2 == tIdx[-1]))
        cont = {'τ1': τ1, 'θ2': th, 'τ2': τ2, 'terminal1': terminal1}
        W, parts = self.objective(t0, tLag, t1, τ0, th, th, cont, s_ = s_, siRatio_ = siRatio_)
        return {'θ': th, 'W': W, 'τ0': τ0, 'τ1': τ1, 'parts': parts}

    def solve(self, t0, siRatio_, θCand = None, s_ = 1.):
        """ The permanent design chosen at t0, given the predetermined s_{t0-1,i}/s_{t0-1}.

        nTurning counts sign changes in the gradient of W over the candidate grid, so a multi-peaked
        objective is visible rather than silently resolved by argmax. """
        self._requireZeroMass()
        with self.BG.cacheParams():
            d = self.objectiveOverθ(t0, siRatio_, θCand = θCand, s_ = s_)
        thStar, atBound = self._argmax(d['θ'], d['W'])
        turns = int(np.sum(np.diff(np.sign(np.diff(d['W']))) != 0))
        return {'θ': thStar, 'atBound': atBound, 'W': d['W'], 'θCand': d['θ'],
                'τAtChoice': float(np.interp(thStar, d['θ'], d['τ0'])), 'nTurning': turns}

    def solveFixedPoint(self, t0, θ0, θCand = None, s_ = 1., tol = 1e-9, maxIter = 50):
        """ The permanent design under the ANTICIPATED vote (the class docstring's timing):

            theta* = argmax_theta W_{t0}( theta ; siRatio(theta*) ),

        solved as a best response on the predetermined ratio. theta0 seeds it -- the incumbent design is
        the natural seed, and wherever the wedge is calibrated it is already the fixed point, so the
        iteration costs one extra pass and confirms it.

        `converged` is REPORTED, not asserted: this is a best response and not a contraction, so a cycle
        has to be visible rather than hidden behind a maxIter. 'iterates' carries the whole sequence. """
        θ, hist = float(θ0), [float(θ0)]
        with self.BG.cacheParams():
            for _ in range(maxIter):
                rec = self.solve(t0, self.siRatioAt(t0, θ), θCand = θCand, s_ = s_)
                hist.append(rec['θ'])
                done = abs(rec['θ'] - θ) < tol
                θ = rec['θ']
                if done:
                    break
            return rec | {'iterates': np.array(hist), 'converged': done,
                          'siRatio': self.siRatioAt(t0, θ)}


class PermanentCRRA(LeadedBase):
    r""" The permanent choice under CRRA.

    Simpler than LeadedCRRA, not harder: a permanent theta means a CONSTANT design path, so each candidate
    is one ordinary solvePEE_CRRA call and there is no path to iterate. PermanentLOG's concentration
    argument carries over unchanged -- tau is whatever the CRRA politico-economic equilibrium delivers at
    that design -- so the whole problem is a one-dimensional grid search over theta.

    s_{t0-1,i}/s_{t0-1} is pinned for the same reason as in the LOG case, and here it must come from a
    SOLVED equilibrium: under CRRA it is not a closed form. That is why the candidate solves are cached
    (_grid) rather than folded into the maximisation -- the anticipated-vote fixed point re-weights the
    same equilibria against a different pinned ratio, so it costs iterations of arithmetic rather than
    iterations of solvePEE_CRRA. """

    def __init__(self, m, nθCand = 21, **kwargs):
        self.m = m
        self.B, self.BG, self.BT = m.B, m.BG, m.BT
        self.db = m.db
        self.ni, self.T = m.ni, m.T
        self.nθCand = nθCand
        self.θCand = np.linspace(0., 1., nθCand)
        self.kwargs = kwargs

    def _grid(self, t0, ths, s0 = None, solveKwargs = None, verbose = True):
        """ One ordinary CRRA equilibrium per candidate permanent design, reduced to what W needs.

        db['theta'] is written for each candidate, not just passed to the solver: Base.ΓsCap and the
        CRRA steady-state bracket read it from db, and leaving them on the incumbent design while the
        solver used a candidate would be silently inconsistent (shocks.shockTheta's own warning). It is
        restored in a finally block, so a failed candidate cannot leave db on the wrong design.

        'si' is each candidate's OWN s_{t0-1,i}/s_{t0-1}. W never uses it -- solveFixedPoint does, to
        find the ratio the anticipated vote implies. Failed candidates keep ok=False and NaN rows. """
        self._requireZeroMass()
        t = self.db['t'][self.db['t'].get_loc(t0)]
        ε = self.db['eps'].values.astype(float)
        n = len(ths)
        c = {'θ': ths, 'ok': np.zeros(n, dtype = bool), 'τ': np.full(n, np.nan),
             'h': np.full(n, np.nan), 's_': np.full(n, np.nan),
             'c1': np.full((n, self.ni), np.nan), 'B': np.full((n, self.ni), np.nan),
             'si': np.full((n, self.ni), np.nan)}
        thSave = self.db['θ'].values.astype(float).copy()
        try:
            for k, cand in enumerate(ths):
                self.db.update(self.m.adjPar('θ', float(cand)))
                try:
                    out = self.m.solvePEE_CRRA(θ = np.full(self.T, float(cand)), ε = ε, s0 = s0,
                                               **(solveKwargs or {}))
                    rep = out['report']
                    tPrev = self.db['t'][self.db['t'].get_loc(t0)-1]
                    c['c1'][k] = rep['tildec1i'].xs(t).values.astype(float)
                    c['B'][k] = rep['B'].xs(t).values.astype(float)
                    c['si'][k] = rep['si_s'].xs(tPrev).values.astype(float)
                    c['h'][k], c['s_'][k] = float(rep['h'].xs(t)), float(rep['s_'].xs(t))
                    c['τ'][k] = float(out['τ'].xs(t0))
                    c['ok'][k] = True
                except Exception as e:
                    if verbose:
                        print('      theta={:.3f}: failed ({}: {})'.format(cand, type(e).__name__, e))
        finally:
            self.db.update(self.m.adjPar('θ', thSave))
        if not c['ok'].any():
            raise RuntimeError('PermanentCRRA: every candidate failed to solve.')
        return c

    def W(self, cache, siRatio_, t0):
        """ W_{t0} at every cached candidate, with c_{2,t0}^i rebuilt at the PINNED predetermined ratio
        rather than read off each candidate's own report, whose si_s moved with the candidate.

        Evaluated with db back on the incumbent design, which is safe because c2i takes theta explicitly
        and nothing in its chain reads db['θ'] -- wedgeA/wedgeB are functions of the argument. """
        t = self.db['t'][self.db['t'].get_loc(t0)]
        q = 1 - 1/float(self.BG.get('ρ', t))
        old, young = self.weights(t)
        out = np.full(len(cache['θ']), -np.inf)
        with self.BG.cacheParams():
            for k in np.flatnonzero(cache['ok']):
                c2 = np.asarray(self.BG.c2i(cache['h'][k], cache['s_'][k], cache['τ'][k],
                                            float(cache['θ'][k]), siRatio_, t), dtype = float)
                v1 = (1+cache['B'][k])*cache['c1'][k]**q/q
                out[k] = float((old*(c2**q/q)).sum() + (young*v1).sum())
        return out

    def solve(self, t0, siRatio_, s0 = None, θCand = None, solveKwargs = None, verbose = True,
              cache = None):
        """ Grid-search the permanent design under CRRA at a given pinned ratio. One full solvePEE_CRRA
        per candidate, unless a cache from a previous _grid call is supplied. """
        ths = self.θCand if θCand is None else np.asarray(θCand, dtype = float)
        if cache is None:
            cache = self._grid(t0, ths, s0 = s0, solveKwargs = solveKwargs, verbose = verbose)
        Ws = self.W(cache, siRatio_, t0)
        thStar, atBound = self._argmax(cache['θ'], Ws)
        ok = cache['ok']
        return {'θ': thStar, 'atBound': atBound, 'W': Ws, 'θCand': cache['θ'], 'cache': cache,
                'τAtChoice': float(np.interp(thStar, cache['θ'][ok], cache['τ'][ok]))}

    def solveFixedPoint(self, t0, θ0, s0 = None, θCand = None, solveKwargs = None, verbose = True,
                        tol = 1e-6, maxIter = 50):
        """ PermanentLOG.solveFixedPoint's timing under CRRA: theta* = argmax W(theta ; siRatio(theta*)).

        The candidate equilibria are solved ONCE and the iteration re-weights them, so the fixed point
        costs no extra solvePEE_CRRA calls. siRatio(theta) is interpolated linearly across candidates --
        the same piecewise-linear rule the rest of the module uses, and for the same reason: an object
        feeding an argmax must not carry interpolation artefacts.

        tol is looser than the LOG version's (1e-6 against 1e-9) because each candidate here is a numerical
        equilibrium solve, not a closed form. """
        ths = self.θCand if θCand is None else np.asarray(θCand, dtype = float)
        cache = self._grid(t0, ths, s0 = s0, solveKwargs = solveKwargs, verbose = verbose)
        ok = cache['ok']
        siOf = lambda x: np.array([np.interp(x, cache['θ'][ok], cache['si'][ok, i])
                                   for i in range(self.ni)])
        θ, hist = float(θ0), [float(θ0)]
        for _ in range(maxIter):
            rec = self.solve(t0, siOf(θ), θCand = ths, cache = cache)
            hist.append(rec['θ'])
            done = abs(rec['θ'] - θ) < tol
            θ = rec['θ']
            if done:
                break
        return rec | {'iterates': np.array(hist), 'converged': done, 'siRatio': siOf(θ)}
