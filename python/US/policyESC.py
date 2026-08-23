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
from gridsearch import roots1d


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
    def objective(self, t, tLag, t1, τt, θt, θ1, cont, s_ = 1.):
        """ W_t over a mesh of (state theta_t, candidate theta1), all arguments flattened to (M,).

        cont: {'τ1': tau_{t+1}(theta1), 'θ2': theta_{t+2}(theta1), 'τ2': tau_{t+2}(theta2),
               'terminal1': whether t+1 is the terminal period} -- the continuation, already evaluated at
        theta1 by solveBackward. s_ = s_{t-1}; the argmax does not depend on it (module docstring), and it
        defaults to the appendix's own normalisation.

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
        Γs_ = BG.Γs(BG.get('βi', tLag), τt, θt, tLag)
        si_s_ = BG.si_s(BG.get('βi', tLag), τt, θt, Γs_, tLag)
        c2 = BG.c2i(h, s_, τt, θt, si_s_, t)
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
