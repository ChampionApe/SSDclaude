import numpy as np, pandas as pd
from scipy import optimize, interpolate
from gridsearch import (robustRoot, roots1d, CartesianGrid, griddedInterp1D,
                        griddedSmooth1D, griddedGradient1D)


def multiplicitySummary(sols, keys = ('nEq', 'nCand', 'fallback')):
    """ One dict over a {t: period dict} solution: the largest number of equilibria at any state, the
    largest candidate count, the number of states where more than one equilibrium passed the test and
    where none did (num_robustroot.tex, eq:equilibriumTest), and the periods concerned. `keys` names the
    per-period entries. Periods without them and -1 entries (the legacy rule) are skipped. """
    kEq, kCand, kFb = keys
    out = {'nEqMax': 0, 'nCandMax': 0, 'nStatesMultiple': 0, 'nFallback': 0,
           'periodsMultiple': [], 'periodsFallback': []}
    for t, rep in sols.items():
        if not isinstance(rep, dict) or rep.get(kEq) is None:
            continue
        nEq, nCand = np.asarray(rep[kEq]), np.asarray(rep[kCand])
        fb = np.asarray(rep[kFb], dtype = bool)
        if nEq.size == 0 or (nEq < 0).all():
            continue
        out['nEqMax'] = max(out['nEqMax'], int(nEq.max()))
        out['nCandMax'] = max(out['nCandMax'], int(nCand.max()))
        nm, nf = int((nEq > 1).sum()), int(fb.sum())
        out['nStatesMultiple'] += nm
        out['nFallback'] += nf
        if nm:
            out['periodsMultiple'].append(t)
        if nf:
            out['periodsFallback'].append(t)
    return out


def _interpAtCand(x, Y, cand):
    """ roots1d.interpAlong(x, Y, cand) for Y (M, N) and cand (K, N), except that a candidate sitting
    exactly on a node takes that node's value. interpAlong weights the next node by zero there, and 0·NaN
    is NaN: the upper end of a feasible sub-grid bordering an infeasible node would lose its value. """
    out = roots1d.interpAlong(x, Y, cand)
    c = np.where(np.isfinite(cand), cand, x[0])
    j = np.clip(np.searchsorted(x, c), 0, x.size - 1)
    n = np.broadcast_to(np.arange(cand.shape[1]), cand.shape)
    return np.where(np.isfinite(cand) & (x[j] == c), Y[j, n], out)


def _retireeLevel(w, c2, p):
    """ Σ_i w_i υ(c_{2,t}^i), υ(c) = c^p/p with p = 1-1/ρ, and ln c at p = 0 (ρ = 1, where the CRRA
    terminal period is solved too and c^p/p is undefined). c2: (..., ni). """
    return (w*np.log(c2)).sum(axis = -1) if p == 0 else (w*c2**p).sum(axis = -1)/p


class LOG:
    """
    Identify Sequence of Policy Functions.
    Informal Analytical, LOG model.

    The analytical LOG model does not involve identifying policy
    functions when pension characteristics (θ,ϵ) are fixed.
    """
    # 'legacy' reinstates the integral criterion (roots1d.selectMax), for comparisons only. A class
    # attribute, so that an instance unpickled from before it existed selects by the frozen rule too.
    selection = 'frozen'

    def __init__(self, m, style = 'Vector', grid = None, **kwargs):
        self.m = m
        self.B  = m.B # refer to base class
        self.BG = m.BG # refer to basegrid class
        self.BT = m.BT # refer to basetime class
        self.db = m.db # refer to main database
        self.ni, self.T = m.ni, m.T # copied locally so solves don't need to keep reaching into self.m
        self.style = style
        self.x0 = {} # own cache of last-used/default initial guesses, keyed by problem name -- separate
                      # from self.m.x0 (model.py's EE_* cache)
        self.kwargs = self._kwargs | kwargs # passed to newton solver
        self.initGS(grid)

    @property
    def _kwargs(self):
        return {'update': True}

    #######################################################################
    ##########   Named grid-problem structure (self.GS)                ####
    #######################################################################
    # See README's "Named grid-problem structure" for the design (why one dict per named problem, why
    # CRRA extends 'PEE' rather than adding a second name, why stateGrids['s_'] is a settable override
    # slot and not a cache).
    def initGS(self, grid = None):
        """ LOG's only named problem, 'PEE': solGrids={'τ': ...} from this entry's own gridSettings
        (_gridSettings' defaults, overridable via `grid`), no state. CRRA.initGS extends this entry. """
        settings = self._gridSettings | (grid or {})
        τGrid = np.linspace(settings['l'], settings['u'], settings['n'])
        self.GS = {'PEE': {'solGrids': {'τ': τGrid}, 'stateGrids': None, 'gridSettings': settings}}

    @property
    def _gridSettings(self):
        """ Defaults for solveBackward (docs alg:gridsearch). l/u: interior bounds -- u<1 strictly, since
        z_t carries a 1/(1-τ_t) factor and diverges at τ=1. n: nodes spanning [l,u]. Δl/Δu: nodes
        below/above the previous period's solution the refinement window spans -- kept separate since a
        monotone-in-t policy path can be solved with far fewer evaluations by making them asymmetric. """
        return {'l': 1e-4, 'u': 1-1e-4, 'n': 101, 'Δl': 10, 'Δu': 10}

    #######################################################################
    ##########   solveVectorized (docs alg:fast, "Gradient-based       ####
    ##########   roots for the politico-economic equilibrium with      ####
    ##########   log preferences")                                     ####
    #######################################################################
    # "Barely an algorithm" per the doc -- no fallback, presumes the FOC is well-behaved. Bounded-root
    # reparameterization (gridsearch.robustRoot): stateVectorized (candidate τ̃ -> economic-object dict,
    # mirroring EE_LOG_solve/EE_report) -> focVectorized (dict -> z_t via Base.FOC) -> reportVectorized
    # (converged result -> bounded τ + diagnostics; no EE solve here, that's model.py's job).
    #
    # No s0 anywhere, deliberately: LOG's B^i=β_i is a pure primitive (never a function of s/h, unlike
    # CRRA's B(s,h1)), so Γs/Θh/si_s never depend on the savings level (docs' "no endogenous states",
    # §PEELOG). si_s_'s first entry (generation already old at db['t'][0]) comes from
    # model.py's initialState_solve, which itself needs no s0.

    def stateVectorized(self, τtilde, θ, ε, l = 0, u = 1):
        """ Build the dict of economic objects the LOG political FOC (eq:fast) needs at a candidate
        *unbounded* tax path τtilde (length T). θ, ε: full paths, as model.py's EE_LOG_solve. l, u:
        bounds for gridsearch.robustRoot.clip -- τ is only ever evaluated inside [l,u]. """
        d = {'τtilde': τtilde, 'τ': robustRoot.clip(τtilde, l, u), 'θ': θ, 'ε': ε}
        d['τ1'], d['θ1'] = self.m.leadSym(d['τ']), self.m.leadSym(θ)
        d['βi'], d['β0'] = self.db['βi'].values, self.db['β0'].values

        # Γs/Θh: identical construction to EE_LOG_solve (B^i=β_i at ρ=1, terminal ΘhTerminal at t=T-1).
        d['Γs'] = self.BT.Γs(d['βi'], d['τ1'], d['θ1'])
        Θh = self.BT.Θh(d['τ'], d['τ1'], d['θ1'], d['Γs'])
        Θh[-1] = self.BT.ΘhTerminal(d['τ'])[-1]
        d['Θh'] = Θh

        # si_s_[t] = s_{t-1,i}/s_{t-1}: undefined at t'=T-1 (drop the meaningless last entry), then shift
        # forward one period. db['t'][0]'s entry comes from initialState_solve (model.py §5), not this
        # period's own si_s formula -- the generation already old at the pre-determined period before
        # the horizon, identified from db['t'][0]'s own (τ,θ) alone.
        si_s = self.BT.si_s(d['βi'], d['τ1'], d['θ1'], d['Γs'])[:-1]
        tFirst = self.m.B.tFirst
        init = self.m.initialState_solve(d['τ'][tFirst], θ[tFirst])
        d['si_s_'] = np.vstack([init['si_s'][None, :], si_s])
        return d

    def focVectorized(self, d):
        """ Evaluate the LOG political FOC z_t (eq:fast) from a state dict (see stateVectorized): young
        (FH_dv1i_LOG/FH_dv10_LOG) and old (dv2i_dτ_LOG/dv20_dτ_LOG) marginal utilities via Base.FOC. """
        τ, θ, ε = d['τ'], d['θ'], d['ε']
        dv1i = self.BT.FH_dv1i_LOG(d['βi'], τ)
        dv10 = self.BT.FH_dv10_LOG(d['β0'], τ)
        dv2i = self.BT.dv2i_dτ_LOG(τ, θ, d['si_s_'])
        dv20 = self.BT.dv20_dτ_LOG(τ, ε, d['Θh'])
        return self.BT.FOC(dv1i, dv10, dv2i, dv20)

    def reportVectorized(self, res, l = 0, u = 1, tol = 1e-8):
        """ Package a solveVectorized result: check convergence (self.m._checkConverged -- max|residual|,
        not scipy's own res.success), return the bounded policy τ=clip(τ̃,l,u) + solver diagnostics. """
        maxResid = self.m._checkConverged(res.fun, tol = tol, name = 'LOG.solveVectorized', scipyRes = res)
        τ = robustRoot.clip(res.x, l, u)
        return {'τ': pd.Series(τ, index = self.db['t']),
                'maxResid': maxResid, 'success': res.success, 'message': res.message}

    def solveVectorized(self, θ, ε, x0 = None, l = 0, u = 1, a0 = 1, a1 = 1, tol = 1e-8, update = True, **kwargs):
        """ Solve the stacked LOG political FOC (eq:fast) for the whole tax path at once, via the
        bounded-root reparameterization (gridsearch.robustRoot, eq:root). x0: defaults to a cached
        self.x0['vectorized'] warm-start, else the constant db['τ0'] path. update: cache the solved τ̃ on
        convergence. Returns just τ + solver diagnostics (see reportVectorized). """
        if x0 is None:
            x0 = self.x0.get('vectorized', np.full(self.T, self.db['τ0']))

        def residual(τtilde):
            z = self.focVectorized(self.stateVectorized(τtilde, θ, ε, l, u))
            return z - np.abs(z)*robustRoot.penalty(τtilde, l, u, a0, a1)

        # scipy calls `residual` many times (Newton step + finite-difference Jacobian); cache db reads
        # for the solve (base.py's cacheParams). self.BT, not self.BG: this works through BaseTime.
        with self.BT.cacheParams():
            res = optimize.root(residual, x0, **kwargs)
        if update:
            self.x0['vectorized'] = res.x
        return self.reportVectorized(res, l, u, tol = tol)

    #######################################################################
    ##########   solveBackward (docs alg:gridsearch, "Iterative grid   ####
    ##########   search with initial boundary check")                  ####
    #######################################################################
    # Rests on a structural property solveVectorized doesn't exploit: no term of z_t depends on any
    # *lag* of τ (young terms depend on τ_t alone; dv2i's si_s_ is closed-form in τ_t; only dv20's Θh
    # reaches forward to τ_{t+1}). Hence z_t = z_t(τ_t, τ_{t+1}), z_{T-1} = z_{T-1}(τ_{T-1}) -- the
    # T-dimensional simultaneous root is triangular, solved exactly by backward recursion over *scalar*
    # problems, with no initial-guess dependence.
    #
    # Corners and multiplicity are resolved by gridsearch.roots1d.selectMaxFrozen (docs eq:candidates,
    # eq:equilibriumTest): every crossing of z_t and both ends of 𝒯 are candidates, each tested and ranked
    # on the objective at the savings shares it implies (objectiveFrozen). Does NOT use robustRoot's
    # extended grid -- that exists for a *root*-finder; the corners are candidates on the same footing as
    # the crossings.
    #
    # As in solveVectorized, no s0 anywhere: under LOG the whole FOC is independent of the savings level.

    def stateGrid(self, τ, t, θ, tLag, terminal, τ1 = None, θ1 = None):
        """ Economic objects the FOC needs at one period t, over a *grid* of candidate τ_t (shape (M,)),
        given the already-solved τ_{t+1}. Runs through self.BG (db sliced to one year, grid-valued args).

        Γ_{s,t} is a scalar here (depends on τ_{t+1}/θ_{t+1}/primitives, never candidate τ_t); Γ_{s,t-1}
        (feeding si_s_ below) IS grid-valued.

        tLag: the actual db['t'] label of the period before t -- explicit, not `t-1`, since db['t'] need
        not be a literal integer range. At t=tFirst there is no period before it; solveBackward passes
        tLag=tFirst, matching Base.__call__'s own clamp and model.py's initialState_solve proxy. No
        initialState_solve call here: under LOG its Γs root-find collapses to B^i=β_i anyway, and it's
        scalar-only so couldn't be evaluated over the grid. """
        BG = self.BG
        Θh = BG.ΘhTerminal(τ, t) if terminal else BG.Θh(τ, τ1, θ1, BG.Γs(BG.get('βi', t), τ1, θ1, t), t)
        βi_ = BG.get('βi', tLag)
        Γs_ = BG.Γs(βi_, τ, θ, tLag)
        return {'τ': τ, 'Θh': Θh, 'si_s_': BG.si_s(βi_, τ, θ, Γs_, tLag)}

    def focGrid(self, d, t, θ, ε, terminal):
        """ Evaluate z_t (eq:fast) over the grid of candidate τ_t in a stateGrid dict. Returns (M,). The
        terminal period passes β=β0=0 (matching how the doc derives eq:terminalPEELOG from the general
        formulas with β_{T,j}=0), rather than a separate formula. """
        BG, τ = self.BG, d['τ']
        β  = np.zeros(self.ni) if terminal else BG.get('βi', t)
        β0 = 0.0 if terminal else BG.get('β0', t)
        return BG.FOC(BG.dv1i_dτ_LOG(β, τ, t), BG.dv10_dτ_LOG(β0, τ, t),
                      BG.dv2i_dτ_LOG(τ, θ, d['si_s_'], t), BG.dv20_dτ_LOG(τ, ε, d['Θh'], t), t)

    #######################################################################
    ##########   Selection among tax candidates at frozen shares       ####
    ##########   (num_robustroot.tex, eq:candidates / eq:equilibriumTest) #
    #######################################################################
    # z_t substitutes the formal savings shares consistent with every node, which is what makes its root
    # the equilibrium -- and what makes z_t the derivative of no single objective. The candidates (every
    # crossing plus the corners) are therefore tested and ranked on W_t evaluated at the shares each
    # candidate implies, held fixed along the whole grid (roots1d.selectMaxFrozen). The informal blocs'
    # terms carry no formal shares and are the same at every candidate.
    def _oldFormalWeights(self, t):
        """ (ni,) weights of the formal retirees' term in W_t, exactly as Base.FOC applies them to dv2i. """
        return self.BG.get('γi[t-1]', t) * self.BG.ω2i(t)

    def objectiveFrozen(self, cand, τGrid, d, θ, t, ε, tLag, terminal):
        """ W_t(τ; D) on τGrid at the formal savings shares D frozen at each candidate tax, up to a
        constant common to a column -- the callback of roots1d.selectMaxFrozen (eq:objectiveProfile).
        d: a stateGrid dict over the τ-first mesh of τGrid and the N columns (flat length M·N); cand:
        (K, N) candidate taxes, NaN-padded; θ: the design in force, scalar or (N,) per column. Returns
        (K, M, N).

        It is z_t (focGrid) re-evaluated along the grid with d['si_s_'] replaced by the frozen shares and
        integrated in τ (roots1d.cumtrapzColumns), plus the formal retirees' level Σ_i w_i ln c_{2,t}^i at
        the first feasible node and the frozen shares; the young's and the informal retirees' levels
        there are common to the column and drop out. The frozen shares are Eq EE:si_s at vintage t-1 at
        the candidate's own tax (exact under LOG, where B = β). c_{2,t}^i is evaluated at h = s_ = 1:
        its outer factor is common to the column and drops out with the rest. """
        BG = self.BG
        cand = np.asarray(cand, dtype = float)
        K, N = cand.shape
        M = τGrid.size
        θc = np.broadcast_to(np.asarray(θ, dtype = float), (N,))
        # the shares each candidate implies: Eq EE:si_s at vintage t-1, at the candidate's own tax
        cF, θF = cand.reshape(-1), np.broadcast_to(θc[None, :], (K, N)).reshape(-1)
        ok = np.isfinite(cF)
        D = np.full((K*N, self.ni), np.nan)
        if ok.any():
            βi_ = BG.get('βi', tLag)
            Γs_ = BG.Γs(βi_, cF[ok], θF[ok], tLag)
            D[ok] = BG.si_s(βi_, cF[ok], θF[ok], Γs_, tLag)
        θB = np.broadcast_to(θc[None, :], (M, N)).reshape(-1)
        oldW = self._oldFormalWeights(t)
        n = np.arange(N)
        W = np.full((K, M, N), np.nan)
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            for k in range(K):
                Dk = np.broadcast_to(D[k*N:(k+1)*N][None, :, :], (M, N, self.ni)).reshape(-1, self.ni)
                zk = np.asarray(self.focGrid(d | {'si_s_': Dk}, t, θB, ε, terminal), dtype = float).reshape(M, N)
                Lk = (oldW*np.log(BG.c2i(1., 1., d['τ'], θB, Dk, t))).sum(axis = -1).reshape(M, N)
                fin = np.isfinite(zk)
                first = np.where(fin.any(axis = 0), fin.argmax(axis = 0), 0)
                W[k] = roots1d.cumtrapzColumns(τGrid, zk) + Lk[first, n][None, :]
        return W

    def _select(self, x, z, frozen, tol = 0.0):
        """ roots1d.selectMaxFrozen, or the integral criterion roots1d.selectMax when self.selection ==
        'legacy' (kept for row-by-row comparisons; the counts are then -1 and W NaN). """
        if self.selection == 'legacy':
            sel = roots1d.selectMax(x, z, tol = tol)
            shape = np.shape(sel['x'])
            return sel | {'nCand': np.full(shape, -1), 'nEq': np.full(shape, -1),
                          'fallback': np.zeros(shape, dtype = bool), 'W': np.full(shape, np.nan)}
        return roots1d.selectMaxFrozen(x, z, frozen, tol = tol)

    def _selectND(self, g, z, name, frozen, tol = 0.0):
        """ _select over a CartesianGrid (roots1d.selectMaxFrozenND / selectMaxND). """
        if self.selection == 'legacy':
            sel = roots1d.selectMaxND(g, z, name, tol = tol)
            shape = g.stateShape(name)
            return sel | {'nCand': np.full(shape, -1), 'nEq': np.full(shape, -1),
                          'fallback': np.zeros(shape, dtype = bool), 'W': np.full(shape, np.nan)}
        return roots1d.selectMaxFrozenND(g, z, name, frozen, tol = tol)

    def solveBackward_t(self, t, θ, ε, tLag, terminal, τ1 = None, θ1 = None,
                        Δl = None, Δu = None, maxExpand = 8, tol = 0.0):
        """ Solve the scalar problem for one period: refine the grid around τ_{t+1}, evaluate z_t,
        select among the candidates (steps 1-3 of alg:gridsearch, eq:equilibriumTest). Terminal period
        searches the full grid.

        The expansion step guards the refinement window: if the selection sits on a window edge that
        isn't a global-grid edge, the window may have excluded the true maximum, so the binding side is
        doubled and the period re-solved (nodes are not cached across expansions -- z_t is closed-form
        and cheap; that changes for CRRA, where z needs numerical derivatives).

        Returns {'τ', 'z', 'nMax', 'nCand', 'nEq', 'fallback', 'atBound', 'expansions', 'windowed'} --
        'nCand'/'nEq' the candidates tested and the equilibria among them ('nEq' > 1 means the selection
        rule bound), 'fallback' that no candidate passed the equilibrium test and the integral
        criterion's choice is returned, 'atBound' a legitimate corner solution (z_t(τ_t)!=0 there is
        correct, not a failure), 'windowed' that the expansion budget ran out still stuck on an edge. A
        window only sees the candidates inside it; pass Δl = Δu = n for the full candidate count
        (solveRobust's check does). """
        τGrid = self.GS['PEE']['solGrids']['τ']
        n = τGrid.size
        if terminal:
            lo, hi, dl, du = 0, n, None, None
        else:
            centre = int(np.searchsorted(τGrid, τ1))
            dl = self.GS['PEE']['gridSettings']['Δl'] if Δl is None else Δl
            du = self.GS['PEE']['gridSettings']['Δu'] if Δu is None else Δu

        for k in range(maxExpand + 1):
            if not terminal:
                lo, hi = max(centre - dl, 0), min(centre + du + 1, n)
            g = τGrid[lo:hi]
            d = self.stateGrid(g, t, θ, tLag, terminal, τ1, θ1)
            z = self.focGrid(d, t, θ, ε, terminal)
            frozen = lambda cand, g = g, d = d: self.objectiveFrozen(cand, g, d, θ, t, ε, tLag, terminal)
            sel = self._select(g, z, frozen, tol = tol)
            τ = sel['x']
            atLo, atHi = (lo > 0) and (τ <= g[0]), (hi < n) and (τ >= g[-1])
            if not (atLo or atHi):
                break
            dl = max(2*dl, 1) if atLo else dl
            du = max(2*du, 1) if atHi else du
        return {'τ': τ, 'z': float(np.interp(τ, g, z)), 'nMax': int(sel['nMax']),
                'nCand': int(sel['nCand']), 'nEq': int(sel['nEq']), 'fallback': bool(sel['fallback']),
                'atBound': bool(sel['atBound']), 'expansions': k, 'windowed': bool(atLo or atHi)}

    def solveBackward(self, θ, ε, Δl = None, Δu = None, maxExpand = 8, tol = 0.0, update = True):
        """ Solve the whole tax path by backward recursion over scalar grid searches (docs alg:gridsearch).
        No x0/s0 needed -- self-starting from the terminal period.

        Returns {'τ', 'maxResid', 'success', 'message', 'diagnostics', 'multiplicity'}, the first four
        matching reportVectorized's keys; 'multiplicity' is multiplicitySummary over the per-period
        diagnostics. 'maxResid' = max|z_t| over *interior* selections only (a corner's z_t!=0 is correct,
        not a residual), and only as accurate as the grid (~O(spacing^2)) -- no self._checkConverged call
        here; use solveRobust to polish to solver tolerance.

        Loops over db['t']'s actual values (not range(self.T)), since it need not be a literal integer
        range; tLag is resolved via tIdx.get_loc(t) (position within the Index), which works for any
        ordered index. """
        tIdx = self.db['t']
        τ = np.empty(len(tIdx))
        diagnostics = {}
        τNext = θNext = None
        # Parameters dominate one grid evaluation's cost (base.py's cacheParams); nothing here writes to
        # db, so the whole recursion runs inside one cache block.
        with self.BG.cacheParams():
            for t in tIdx[::-1]:
                pos = tIdx.get_loc(t)
                terminal = (t == tIdx[-1])
                tLag = tIdx[pos - 1] if pos > 0 else self.B.tFirst
                d = self.solveBackward_t(t, θ[pos], ε[pos], tLag, terminal, τ1 = τNext, θ1 = θNext,
                                         Δl = Δl, Δu = Δu, maxExpand = maxExpand, tol = tol)
                τ[pos], diagnostics[t] = d['τ'], d
                τNext, θNext = d['τ'], θ[pos]
        if update:
            self.x0['vectorized'] = τ.copy() # a valid warm start for solveVectorized: τ is interior, so
                                              # robustRoot.clip(τ) = τ and the reparameterization is inert
        interior = [d['z'] for d in diagnostics.values() if not d['atBound']]
        maxResid = max((abs(z) for z in interior), default = 0.0)
        stuck = [k for k, d in diagnostics.items() if d['windowed']]
        multiple = [k for k, d in diagnostics.items() if d['nEq'] > 1]
        fallback = [k for k, d in diagnostics.items() if d['fallback']]
        legacyMultiple = [k for k, d in diagnostics.items() if d['nEq'] < 0 and d['nMax'] > 1]
        msgs = ([f"refinement window still binding at t={stuck} after maxExpand={maxExpand}"] if stuck else []) + \
               ([f"several equilibria at t={multiple}; selected by the political objective (num_robustroot.tex)"] if multiple else []) + \
               ([f"no candidate passed the equilibrium test at t={fallback}; integral criterion used"] if fallback else []) + \
               ([f"multiple interior maxima at t={legacyMultiple}; selected by the integral criterion"] if legacyMultiple else [])
        return {'τ': pd.Series(τ, index = tIdx), 'maxResid': maxResid, 'success': not stuck,
                'message': '; '.join(msgs) if msgs else 'grid search completed', 'diagnostics': diagnostics,
                'multiplicity': multiplicitySummary(diagnostics)}

    def solveRobust(self, θ, ε, tol = 1e-8, gridkwargs = None, check = True, **kwargs):
        """ Practical entry point: the cheap gradient solve, checked against the grid search.
        1. solveVectorized -- cheap, exact, but it can fail (e.g. a high political weight ω moves the
           solution far from the constant-db['τ0'] starting guess) and it reports one root with no view
           of the others.
        2. solveBackward on the full grid, which applies the selection rule of num_robustroot.tex and
           reports the candidate and equilibrium counts. With check = True it runs on every solve: when
           the gradient solve converged to the selected equilibrium (within one grid cell) that solution
           is returned unchanged, with the counts attached under 'multiplicity'; otherwise the grid
           selection is polished by a warm-started solveVectorized and returned instead. check = False
           runs the grid only as a fallback, and a gradient solution then carries no counts.
        3. If the polish fails, the grid solution is returned, flagged.
        Only RuntimeError is caught (the specific error self.m._checkConverged raises) -- a bare `except`
        would swallow genuine bugs and misreport them as "didn't converge". """
        try:
            fast = self.solveVectorized(θ, ε, tol = tol, **kwargs)
        except RuntimeError:
            fast = None
        if fast is not None and not check:
            return fast
        gk = dict(gridkwargs or {})
        if check:
            n = self.GS['PEE']['solGrids']['τ'].size
            gk = {'Δl': n, 'Δu': n} | gk                     # the full grid: a window hides candidates
        grid = self.solveBackward(θ, ε, update = fast is None, **gk)   # keep the gradient warm start
        gap = np.nan
        if fast is not None:
            cell = float(np.max(np.diff(self.GS['PEE']['solGrids']['τ'])))
            gap = float(np.max(np.abs(fast['τ'].values - grid['τ'].values)))
            if gap <= cell:
                return fast | {'multiplicity': grid['multiplicity'], 'gridMessage': grid['message']}
        try:
            polished = self.solveVectorized(θ, ε, x0 = grid['τ'].values, tol = tol,
                                            **{k: v for k, v in kwargs.items() if k != 'x0'})
        except RuntimeError as e:
            return grid | {'success': False,
                           'message': f"{grid['message']}; gradient polish failed ({e}) -- returning grid solution"}
        note = '' if fast is None else f'; the cold-started gradient solve sat {gap:.3g} from the selected equilibrium and was replaced'
        return polished | {'message': f"solveVectorized converged after grid warm start ({grid['message']}){note}",
                           'multiplicity': grid['multiplicity']}


class CRRA(LOG):
    """
    Identify Sequence of Policy Functions. CRRA model with H2M informal households. The only relevant
    state variable is aggregate savings s[t-1] (docs §PEE).

    Terminal period (t=T-1, docs' t=T) is closed-form -- see solveTerminal, docs eq:terminalPEECRRA: each
    dv/dτ term is (consumption level)^{1-1/ρ} times the same log-derivative already implemented for LOG
    (dv1i_dτ_LOG/dv2i_dτ_LOG/dv20_dτ_LOG compute dln(c)/dτ; CRRA's chain rule gives
    d[c^{1-1/ρ}/(1-1/ρ)]/dτ = c^{1-1/ρ}·dln(c)/dτ exactly). So the terminal period needs no numerical
    differentiation -- unlike t<T, where Θh_t depends on the endogenous τ_{t+1} and has no closed form.

    The one genuinely new ingredient: B_T^i is Base.B(s_{T-1}, h_T), not the LOG primitive β_i -- so the
    terminal problem is z_T(τ_T, s_{T-1}), solved on the whole (τ, s_) Cartesian grid at once
    (gridsearch.CartesianGrid + roots1d.selectMaxFrozenND), with LOG's selection rule applied per state.
    Evaluating the whole grid is the cheap design, not just the simple one: base.py's cacheParams()
    profiling showed grid-evaluation cost is dominated by per-call db overhead and flat in grid size.

    Verified: at ρ=1, Bi collapses to β_i regardless of (s_,h) and every c^{1-1/ρ} weight collapses to
    c^0=1, so solveTerminal's τ(s_) is then exactly (not approximately) state-independent and matches
    LOG.solveBackward_t(terminal=True) at every s_.
    """

    def initGS(self, grid = None):
        """ Extends LOG's 'PEE' entry (not a separate name) with the state grid CRRA's political problem
        has. 's_' starts unset (see self.GS's header comment for why). Also adds solGrids['s'] (docs'
        𝒮'): the grid of *candidate* s_t values the t<T fixed point is searched over -- kept separate
        from stateGrids['s_'] (docs' 𝒮, the predetermined states solved *at*) since the accuracy of the
        state approximation is governed by 's' alone and may warrant finer spacing. Unset -> the state
        grid. """
        super().initGS(grid)
        self.GS['PEE']['stateGrids'] = {'s_': None}
        self.GS['PEE']['solGrids']['s'] = None

    def stateGrid_T(self, τ, s_, θ, ε, t, tLag):
        """ Closed-form terminal-period economic objects, over grids of candidate τ_T and s_ = s_{T-1}.
        Θh/h/tc1i/c2i/tc20 all use T's own primitives (base.py's own internal [t-1] shifts reach tLag
        where needed); only Bi (=B_T^i, discount factor of the generation OLD at T) and what depends on
        it (Γs_, si_s_) need tLag passed explicitly -- matching LOG.stateGrid's βi_/Γs_/si_s_.

        Unlike LOG (B^i=β_i, a primitive), CRRA's Bi = Base.B(s_, h, tLag) genuinely depends on s_ --
        this is what makes s_ a state of the political problem, not just a reporting variable. """
        BG = self.BG
        Θh = BG.ΘhTerminal(τ, t)
        h = BG.h(Θh, s_, t)
        Bi = BG.B(s_, h, tLag)
        Γs_ = BG.Γs(Bi, τ, θ, tLag)
        si_s_ = BG.si_s(Bi, τ, θ, Γs_, tLag)
        zB, zΓs = np.zeros_like(Bi), np.zeros_like(Γs_) # terminal collapse of tildec1i, as FH_tildec1i does
        tc1i = BG.tildec1i(h, zB, τ, θ, zΓs, t)
        c2i = BG.c2i(h, s_, τ, θ, si_s_, t)
        tc20 = BG.tildec20(h, s_, ε, τ, t)
        return {'τ': τ, 's_': s_, 'Θh': Θh, 'h': h, 'Bi': Bi, 'Γs_': Γs_, 'si_s_': si_s_,
                'tc1i': tc1i, 'c2i': c2i, 'tc20': tc20}

    def focGrid_T(self, d, θ, ε, t):
        """ z_T (docs eq:terminalPEECRRA) over a stateGrid_T dict -- each term is (consumption
        level)^{1-1/ρ} times the LOG log-derivative (see class docstring). Young informal's term is
        identically zero regardless of ρ (matches LOG's terminal dv10=0), so written directly. """
        BG, τ = self.BG, d['τ']
        p = 1 - 1/BG.get('ρ', t)
        dv1i = d['tc1i']**p * BG.dv1i_dτ_LOG(np.zeros(self.ni), τ, t)
        dv10 = np.zeros_like(τ)
        dv2i = d['c2i']**p * BG.dv2i_dτ_LOG(τ, θ, d['si_s_'], t)
        dv20 = d['tc20']**p * BG.dv20_dτ_LOG(τ, ε, d['Θh'], t)
        return BG.FOC(dv1i, dv10, dv2i, dv20, t)

    def defaultSGrid(self, θ, t = None, n = 50):
        """ Default grid of candidate s_{T-1} states (docs §PEE "Grids"): small positive lower bound
        (s_{T-1}=0 makes Rlead/Bi/si_s undefined) and u_s = 1.25×s*(τ=0) via steadyState_CRRA_solve. """
        t = self.db['t'][-1] if t is None else t
        sMax = self.m.steadyState_CRRA_solve(0.0, θ, t = t)['s']
        return np.linspace(1e-4, 1.25*sMax, n)

    def solveTerminal(self, θ, ε, t = None, tol = 0.0, sGrid = None):
        """ Terminal-period τ_T(s_{T-1}) over a grid of states, via one fully vectorized evaluation of
        the whole (τ, s_) grid -- no numerical derivatives, no per-state loop.

        Grids come from self.GS['PEE']: 'τ' from solGrids['τ']; 's_' from stateGrids['s_'] if set, else a
        fresh defaultSGrid(θ, t) (never cached back -- see self.GS's header comment). sGrid overrides
        both, and is how solveBackward pins one shared state grid across every period.

        Corner/multiplicity handling is LOG's selection rule (eq:candidates, eq:equilibriumTest), applied
        once per state via _selectND with objectiveFrozen at the terminal period. No self.x0/warm start
        needed -- closed-form, self-starting at every state simultaneously.

        Returns report_T's full solution dict plus the per-state 'nMax'/'atBound'/'nCand'/'nEq'/
        'fallback' diagnostics. """
        tIdx = self.db['t']
        t = tIdx[-1] if t is None else t
        pos = tIdx.get_loc(t)
        tLag = tIdx[pos - 1] if pos > 0 else self.B.tFirst
        τGrid = self.GS['PEE']['solGrids']['τ']
        if sGrid is None:
            sGrid = self.GS['PEE']['stateGrids']['s_']
        if sGrid is None:
            sGrid = self.defaultSGrid(θ, t)

        g = CartesianGrid(τ = τGrid, s_ = sGrid)
        with self.BG.cacheParams():
            d = self.stateGrid_T(g.flat['τ'], g.flat['s_'], θ, ε, t, tLag)
            z = self.focGrid_T(d, θ, ε, t)
            frozen = lambda cand: self.objectiveFrozen(cand, g, d, None, θ, t, tLag, ε = ε, terminal = True)
            sel = self._selectND(g, z, 'τ', frozen, tol = tol)
        report = self.report_T(sGrid, sel['x'], θ, ε, t, tLag)
        report['nMax'], report['atBound'] = sel['nMax'], sel['atBound']
        report['nCand'], report['nEq'], report['fallback'] = sel['nCand'], sel['nEq'], sel['fallback']
        return report

    # ------------------------------------------------------------------ W_t at frozen shares (CRRA)
    def objectiveFrozen(self, cand, g, d, parts, θ, t, tLag, ε = None, terminal = False):
        """ W_t(τ; D) over the grid g (τ its first axis) at formal shares frozen at each column's
        candidates, up to a column constant -- the callback of roots1d.selectMaxFrozenND
        (eq:objectiveProfile). d: the grid dict (stateGrid_T / stateGrid_t) with 'h', 's_', 'τ' flat
        over g; parts: focParts_t(d) at t < T, None at T (pass ε and terminal = True there); θ: the
        design in force, scalar or flat over g (constant along τ within a column). Returns (K, M, N) in
        g.asColumns order.

        It is z_t re-evaluated with the formal retirees' shares frozen (zAtShares at t < T, focGrid_T at
        T) and integrated in τ (roots1d.cumtrapzColumns), plus Σ_i w_i (c_{2,t}^i)^{1-1/ρ}/(1-1/ρ) (ln c
        at ρ = 1, _retireeLevel) at the first feasible node and the frozen shares; the young's and the
        informal retirees' levels there are common to the column and drop out. Integrating the condition
        rather than reading utility levels keeps the smoothed numerical derivatives z_t carries at t < T
        (finding #18). The frozen shares are Eq EE:si_s at vintage t-1 at the candidate's own tax and the
        hours there, B_t(s_{t-1}, h_t) with h interpolated linearly along τ (_interpAtCand). Cells where
        z_t is infeasible stay NaN. """
        BG = self.BG
        if g.axis('τ') != 0:
            raise ValueError('objectiveFrozen expects τ as the first axis of the grid.')
        τGrid = g.values('τ')
        M = τGrid.size
        cand = np.asarray(cand, dtype = float)
        K, N = cand.shape
        hF, s_F = np.asarray(d['h'], dtype = float), np.asarray(d['s_'], dtype = float)
        θF = np.broadcast_to(np.asarray(θ, dtype = float), (M*N,))
        hG, s_G, θG = hF.reshape(M, N), s_F.reshape(M, N), θF.reshape(M, N)
        # the shares each candidate implies, at its own tax and the hours there
        hc = _interpAtCand(τGrid, hG, cand)                                # (K, N)
        cF = cand.reshape(-1)
        hcF = hc.reshape(-1)
        scF = np.broadcast_to(s_G[0][None, :], (K, N)).reshape(-1)
        θcF = np.broadcast_to(θG[0][None, :], (K, N)).reshape(-1)
        ok = np.isfinite(cF) & np.isfinite(hcF)
        D = np.full((K*N, self.ni), np.nan)
        if ok.any():
            with np.errstate(divide = 'ignore', invalid = 'ignore'):
                Bc = BG.B(scF[ok], hcF[ok], tLag)
                Γc = BG.Γs(Bc, cF[ok], θcF[ok], tLag)
                D[ok] = BG.si_s(Bc, cF[ok], θcF[ok], Γc, tLag)
        p = 1 - 1/float(BG.get('ρ', t))
        oldW = self._oldFormalWeights(t)
        n = np.arange(N)
        W = np.full((K, M, N), np.nan)
        θz = θ if np.ndim(θ) == 0 else θF
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            for k in range(K):
                Dk = np.broadcast_to(D[k*N:(k+1)*N][None, :, :], (M, N, self.ni)).reshape(-1, self.ni)
                c2k = BG.c2i(hF, s_F, d['τ'], θz, Dk, t)
                if terminal:
                    zk = self.focGrid_T(d | {'si_s_': Dk, 'c2i': c2k}, θz, ε, t)
                else:
                    zk = self.zAtShares(d, parts, θz, Dk, t)
                zk = np.asarray(zk, dtype = float).reshape(M, N)
                Lk = _retireeLevel(oldW, c2k, p).reshape(M, N)
                fin = np.isfinite(zk)
                first = np.where(fin.any(axis = 0), fin.argmax(axis = 0), 0)
                W[k] = roots1d.cumtrapzColumns(τGrid, zk) + Lk[first, n][None, :]
        return W

    def report_T(self, sGrid, τ, θ, ε, t, tLag):
        """ Expand a solved τ(s_{T-1}) into the full terminal solution dict, evaluated along the SOLVED
        path: stateGrid_T makes no assumption about where τ came from, only that it matches s_'s shape,
        so this is the same method called again with different inputs -- no new economic content.

        Also builds τ_T(s_{T-1})/h_T(s_{T-1}) as callables (gridsearch.griddedInterp1D) for the t<T
        recursion: the next period's stateGrid calls solp['τPolicy'](s)/solp['hPolicy'](s) at whatever
        *endogenous* continuation state a candidate implies, which need not land on sGrid's own nodes --
        why griddedInterp1D extrapolates rather than clamps.

        Returns stateGrid_T's dict with 'τ'/'h' wrapped as pd.Series indexed by sGrid; everything else
        stays a raw ndarray. """
        d = self.stateGrid_T(τ, sGrid, θ, ε, t, tLag)
        d['τPolicy'] = griddedInterp1D(sGrid, τ)
        d['hPolicy'] = griddedInterp1D(sGrid, d['h'])
        d['τ'] = pd.Series(τ, index = sGrid)
        d['h'] = pd.Series(d['h'], index = sGrid)
        return d

    #######################################################################
    ##########   t < T: backward recursion (docs alg:CRRA:grid)        ####
    #######################################################################
    # For t<T, Θ_{h,t} depends on the endogenous continuation τ_{t+1} (a function of the state s_t that
    # τ_t helps determine), so two things change from the terminal period:
    #
    # (i) The economic equilibrium at t is a fixed point in s_t (docs eq:stateResidual), not a closed
    #     form -- a ROOT problem (any crossing solves, roots1d.allRoots), not the maximisation the
    #     political FOC needs. None of Θ_{s,t}'s inputs depend on s_{t-1} (only the residual's explicit
    #     (s_{t-1}/ν)^σ factor does), so the expensive forward pass is 2D over (τ,s), and every s_{t-1}
    #     follows by broadcasting (_rootS/solveStateApprox_t).
    #
    # (ii) Three log-derivatives are numerical along τ (d ln h_t, d ln ĉ_{1,t}^i, d ln c̃_{2,t+1}^0).
    #      dln(c_{2,t}^i)/dτ_t must come from base.py's dlnc2i_dτ instead -- s_{t-1,i}/s_{t-1} varies
    #      along the grid but the policy maker takes it as predetermined, so a grid derivative would fold
    #      in a channel that doesn't belong in the FOC (docs §PEE footnote -- a correctness issue, not
    #      precision). dln(c̃_{2,t}^0) could go either way; closed form used for consistency.
    #
    # Infeasibility is first-class here (unlike at T): for a given s_{t-1}, the implied s_t leaves the
    # grid once τ_t is extreme enough. Those cells stay NaN through to the selection, which treats each
    # state over its own feasible sub-grid.

    def _requireCRRA(self, t):
        """ Guard the t<T path against ρ=1, before anything evaluates base.py's hatc1i (whose exponent
        1/(1-1/ρ) divides by zero there) -- a directed error rather than a silently propagating inf.
        ρ=1 is not a gap: it's exactly what policy.py's LOG class solves in closed form. """
        ρ = self.BG.get('ρ', t)
        if np.isclose(ρ, 1):
            raise ValueError(f"CRRA's t<T solve requires ρ != 1 (got ρ={ρ}): the ĉ1i fold (base.py's "
                             "hatc1i) has no ρ=1 counterpart, since υ_1i is then (1+B)ln(c̃1i) rather "
                             "than a power of any single level. Use the LOG class, which solves ρ=1 "
                             "in closed form.")

    def stateApprox_t(self, τ, s, t, θ1, solp):
        """ Forward pass of docs eq:stateApprox, on candidate pairs (τ_t, s_t) -- a function of (τ_t,
        s_t) and the continuation policies only, *not* of s_{t-1} (what keeps the fixed point 2D).
        solp: the already-solved t+1 dict, read only through its τPolicy/hPolicy interpolants, evaluated
        at candidate s_t values that need not be grid nodes (why they extrapolate rather than clamp). """
        BG = self.BG
        τ1, h1 = solp['τPolicy'](s), solp['hPolicy'](s)
        B1 = BG.B(s, h1, t)                     # B_{t+1}^i(s_t, h_{t+1}), at t's own vintage
        Γs = BG.Γs(B1, τ1, θ1, t)
        Θh = BG.Θh(τ, τ1, θ1, Γs, t)
        Θs = BG.Θs(Θh, Γs, t)
        return {'τ1': τ1, 'h1': h1, 'B1': B1, 'Γs': Γs, 'Θh': Θh, 'Θs': Θs}

    def _rootS(self, Θs, sGrid, s_, t):
        """ Solve docs eq:stateResidual for s_t, one column per predetermined state. Θs: (M,N), M =
        len(sGrid), Θ_{s,t} at each candidate s_t (rows) for each column's own (τ_t,s_{t-1}) pair.
        Returns ((N,) roots, (N,) root counts); NaN where no equilibrium lies inside sGrid -- the
        feasibility signal everything downstream keys off. Count>1 means genuinely multiple equilibria;
        the lowest is taken and the count reported rather than silently picking one. """
        ν, σ = self.BG.get('ν', t), self.BG.power_s(t)
        resid = Θs * ((s_/ν)**σ)[None, :] - sGrid[:, None]
        r = roots1d.allRoots(sGrid, resid, kind = 'any')
        if r.ndim == 1:
            r = r[:, None]
        n = (~np.isnan(r)).sum(axis = 0)
        return (r[0] if r.shape[0] else np.full(len(s_), np.nan)), n

    def solveStateApprox_t(self, τGrid, sGrid, s_Grid, t, θ1, solp):
        """ Step 1 of docs alg:CRRA:grid: s_t(τ_t, s_{t-1}) on the whole (τ, s_) grid, plus root counts.
        Evaluates stateApprox_t once on the 2D grid (τ,s), then broadcasts Θ_{s,t} across s_Grid rather
        than re-evaluating -- the cost is independent of how finely the state grid is resolved. Returns
        (Mτ, Ns_)-shaped arrays. """
        g = CartesianGrid(τ = τGrid, s = sGrid)
        d = self.stateApprox_t(g.flat['τ'], g.flat['s'], t, θ1, solp)
        Θs = g.asColumns(d['Θs'], 's')                       # (Ms, Mτ)
        nS_ = len(s_Grid)
        # Column order below is C-order over (τ, s_), matching the reshape at the end.
        sSol, nRoots = self._rootS(np.repeat(Θs, nS_, axis = 1), sGrid, np.tile(s_Grid, len(τGrid)), t)
        return sSol.reshape(len(τGrid), nS_), nRoots.reshape(len(τGrid), nS_)

    def stateGrid_t(self, τ, s, s_, t, tLag, t1, θ, θ1, ε, ε1, solp):
        """ Step 2 of docs alg:CRRA:grid: every economic object the t<T FOC needs, given the
        already-resolved s_t. t/tLag split as stateGrid_T's: only B_t^i (generation old at t) and what
        depends on it (Γs_, si_s_) use tLag; forward-looking objects come from stateApprox_t at t, and
        c̃_{2,t+1}^0 at t1=t+1 (the generation young at t, consuming when old). """
        BG = self.BG
        self._requireCRRA(t)                                 # before hatc1i below, not after
        d = self.stateApprox_t(τ, s, t, θ1, solp)
        d['τ'], d['s'], d['s_'] = τ, s, s_
        d['h'] = BG.h(d['Θh'], s_, t)
        d['B'] = BG.B(s_, d['h'], tLag)                      # B_t^i, generation old at t
        d['Γs_'] = BG.Γs(d['B'], τ, θ, tLag)
        d['si_s_'] = BG.si_s(d['B'], τ, θ, d['Γs_'], tLag)
        # ĉ_{1,t}^i carried as its (1-1/ρ) power and its log, never as the level (base.py's hatc1iPow/
        # lnhatc1i -- the literal level overflows as ρ approaches 1).
        d['hatc1iPow'] = BG.hatc1iPow(d['h'], d['B1'], d['τ1'], θ1, d['Γs'], t)
        d['lnhatc1i'] = BG.lnhatc1i(d['h'], d['B1'], d['τ1'], θ1, d['Γs'], t)
        d['c2i'] = BG.c2i(d['h'], s_, τ, θ, d['si_s_'], t)
        d['tc20'] = BG.tildec20(d['h'], s_, ε, τ, t)
        d['tc20_1'] = BG.tildec20(d['h1'], s, ε1, d['τ1'], t1)   # c̃_{2,t+1}^0
        return d

    def focGrid_t(self, d, g, t, θ, ε):
        """ Step 3 of docs alg:CRRA:grid: z_t on the (τ, s_) grid in a stateGrid_t dict. g: the
        CartesianGrid the dict's flat arrays live on (τ as its first axis) -- numerical derivatives run
        along τ *within each state*, so flat vectors are viewed as (Mτ,Ns_) before differentiating and
        flattened back after. griddedGradient1D passes NaN through, so infeasible cells stay infeasible
        rather than contaminating a spline fit. See the §header comment for which derivatives are
        numerical vs. closed-form. It is zAtShares at the consistent shares d['si_s_']: focParts_t holds
        everything that does not involve them, so the selection rule can re-evaluate z_t at frozen shares
        without redoing the splines. """
        return self.zAtShares(d, self.focParts_t(d, g, t, ε), θ, d['si_s_'], t)

    def focParts_t(self, d, g, t, ε):
        """ The terms of z_t that do not involve the formal retirees' shares, including every numerical
        τ-derivative (the splines dominate a period's cost): {'p', 'dlnh', 'dv1i', 'dv10', 'dv20'},
        flat over g. Computed once per period and shared by focGrid_t and objectiveFrozen. """
        BG, τ, τGrid = self.BG, d['τ'], g.values('τ')
        p = 1 - 1/BG.get('ρ', t)                             # ρ=1 already refused by stateGrid_t upstream
        grad = lambda y: griddedGradient1D(τGrid, g.reshape(y)).reshape(np.shape(y))
        dln = lambda x: grad(np.log(x))
        dlnh = dln(d['h'])
        dv1i = d['hatc1iPow'] * grad(d['lnhatc1i'])          # already a log; differentiate it directly
        dv10 = BG.get('β0', t) * d['tc20_1']**p * dln(d['tc20_1'])
        dv20 = d['tc20']**p * BG.dlnc20_dτ(dlnh, τ, ε, d['Θh'], t)
        return {'p': p, 'dlnh': dlnh, 'dv1i': dv1i, 'dv10': dv10, 'dv20': dv20}

    def zAtShares(self, d, parts, θ, si_s_, t):
        """ z_t with the formal retirees' term rebuilt at the shares si_s_ (flat (M·N, ni)) -- c_{2,t}^i
        (Eq EE:ci) and the closed-form dln(c_{2,t}^i)/dτ_t (base.dlnc2i_dτ, which holds the shares
        fixed) -- and every other term from parts (focParts_t). zAtShares(d, parts, θ, d['si_s_'], t) is
        the consistent z_t, bitwise focGrid_t. """
        BG, τ = self.BG, d['τ']
        c2i = BG.c2i(d['h'], d['s_'], τ, θ, si_s_, t)
        dv2i = c2i**parts['p'] * BG.dlnc2i_dτ(parts['dlnh'], τ, θ, si_s_, t)
        return BG.FOC(parts['dv1i'], parts['dv10'], dv2i, parts['dv20'], t)

    def solveBackward_t(self, solp, t, tLag, t1, θ, θ1, ε, ε1, sGrid, sCandGrid, tol = 0.0, smooth = 1e-5):
        """ One period of the backward recursion (steps 1-4 of docs alg:CRRA:grid), returning the same
        kind of dict as solveTerminal. The selection is LOG's rule per state (eq:equilibriumTest), the
        frozen objective built from the same focParts_t as z_t. smooth: passed to griddedSmooth1D for the
        selected τ_t(s_{t-1}) before interpolation -- the profile inherits small kinks from the
        continuation interpolants, amplified by the next period's numerical derivatives; pass 0 to
        disable. """
        τGrid = self.GS['PEE']['solGrids']['τ']
        with self.BG.cacheParams():
            sSol, nRoots = self.solveStateApprox_t(τGrid, sCandGrid, sGrid, t, θ1, solp)
            g = CartesianGrid(τ = τGrid, s_ = sGrid)
            d = self.stateGrid_t(g.flat['τ'], sSol.reshape(-1), g.flat['s_'],
                                 t, tLag, t1, θ, θ1, ε, ε1, solp)
            parts = self.focParts_t(d, g, t, ε)
            z = self.zAtShares(d, parts, θ, d['si_s_'], t)        # = focGrid_t, splines done once
            frozen = lambda cand: self.objectiveFrozen(cand, g, d, parts, θ, t, tLag)
            sel = self._selectND(g, z, 'τ', frozen, tol = tol)

            τ = sel['x']
            if smooth:
                ok = ~np.isnan(τ)
                τ = np.where(ok, griddedSmooth1D(sGrid, np.where(ok, τ, np.nan), s = smooth), np.nan)
            report = self.report_t(sGrid, τ, sCandGrid, t, tLag, t1, θ, θ1, ε, ε1, solp)
        report['nMax'], report['atBound'] = sel['nMax'], sel['atBound']
        report['nCand'], report['nEq'], report['fallback'] = sel['nCand'], sel['nEq'], sel['fallback']
        report['nRoots'], report['feasible'] = nRoots, ~np.isnan(sSol)
        return report

    def report_t(self, sGrid, τ, sCandGrid, t, tLag, t1, θ, θ1, ε, ε1, solp):
        """ Step 4 of docs alg:CRRA:grid, t<T counterpart of report_T: re-solve the state fixed point at
        the *selected* τ_t(s_{t-1}) (the selected τ generally falls between grid nodes, so its s_t must
        be re-solved, not read off solveStateApprox_t's grid -- cheap here since it's only
        len(sCandGrid) x len(sGrid)), expand into the full solution dict, and build the
        τ_t/h_t/s_t/Γ_{s,t} interpolants the previous period will call (sPolicy/ΓsPolicy alongside
        τPolicy/hPolicy -- no new economic content, since d['s']/d['Γs'] are already the equilibrium
        values at each node). These feed model.py's CRRA.approximatePEE: sPolicy steps s_{t-1}->s_t, and
        ΓsPolicy/hPolicy/s together make a CRRA-consistent warm start for EE_CRRA_solve. """
        nS, nC = len(sGrid), len(sCandGrid)
        τ2 = np.broadcast_to(τ, (nC, nS))
        s2 = np.broadcast_to(sCandGrid[:, None], (nC, nS))
        Θs = self.stateApprox_t(τ2.reshape(-1), s2.reshape(-1), t, θ1, solp)['Θs'].reshape(nC, nS)
        s, nRoots = self._rootS(Θs, sCandGrid, sGrid, t)

        d = self.stateGrid_t(τ, s, sGrid, t, tLag, t1, θ, θ1, ε, ε1, solp)
        ok = ~np.isnan(τ) & ~np.isnan(s)
        d['τPolicy'] = griddedInterp1D(sGrid[ok], τ[ok])
        d['hPolicy'] = griddedInterp1D(sGrid[ok], d['h'][ok])
        d['sPolicy'] = griddedInterp1D(sGrid[ok], s[ok])
        d['ΓsPolicy'] = griddedInterp1D(sGrid[ok], d['Γs'][ok])
        d['τ'] = pd.Series(τ, index = sGrid)
        d['h'] = pd.Series(d['h'], index = sGrid)
        d['s'] = pd.Series(s, index = sGrid)
        return d

    def approximatePEE(self, sols, s0):
        """ Forward-simulate the tax path τ_t(s_{t-1}) implied by the backward-solved policy functions,
        from an initial state s0 -- turns "a sequence of policy functions" into "one actual path". No new
        state-transition machinery needed: report_t already reports equilibrium s_t/h_t/Γ_{s,t} at every
        grid node, so sPolicy/ΓsPolicy walk that data forward directly.

        sols: policy.py's own {t: report dict}. s0: the state entering the first period (docs' s_0).

        Returns {'τ': pd.Series over db['t'], 'Γs','h','s': (T-1,) ndarrays over db['txE'],
        'multiplicity': multiplicitySummary(sols)}. τ is model.py's solvePEE_CRRA's input to
        EE_CRRA_solve; Γs/h/s let that caller build a CRRA-consistent x0. Nothing here is an equilibrium
        guarantee -- s_t is only as accurate as sGrid's interpolation, which is why solvePEE_CRRA
        re-solves EE_CRRA_solve exactly given this τ rather than reporting these Γs/h/s directly. """
        tIdx = self.db['t']
        l, u = self.GS['PEE']['gridSettings']['l'], self.GS['PEE']['gridSettings']['u']
        τ = np.empty(self.T)
        Γs, h, s = np.empty(self.T - 1), np.empty(self.T - 1), np.empty(self.T - 1)
        s_ = s0
        for pos, t in enumerate(tIdx):
            τ[pos] = np.clip(sols[t]['τPolicy'](s_), l, u)
            if pos < self.T - 1:
                Γs[pos], h[pos] = float(sols[t]['ΓsPolicy'](s_)), float(sols[t]['hPolicy'](s_))
                s_ = float(sols[t]['sPolicy'](s_))
                s[pos] = s_
        return {'τ': pd.Series(τ, index = tIdx), 'Γs': Γs, 'h': h, 's': s,
                'multiplicity': multiplicitySummary(sols)}

    def solveBackward(self, θ, ε, sGrid = None, sCandGrid = None, tol = 0.0, smooth = 1e-5):
        """ The full CRRA politico-economic equilibrium: τ_t(s_{t-1}), solved backwards from the terminal
        period (docs alg:CRRA:grid). Returns {t: solution dict}, one entry per db['t'], each carrying the
        per-state 'nCand'/'nEq'/'fallback'; their multiplicitySummary is left in self.lastMultiplicity.

        sGrid: the state grid 𝒮, shared by every period (adjacent periods' interpolants need a common
        grid) -- resolved once here and pinned, defaulting to self.GS['PEE']['stateGrids']['s_'] else
        defaultSGrid at the terminal period. sCandGrid: 𝒮', the candidate grid searched over; defaults to
        self.GS['PEE']['solGrids']['s'] else sGrid itself.

        Requires ρ != 1, checked up front (_requireCRRA) so it fails before doing the terminal period's
        work. The terminal solve alone *is* well-defined at ρ=1 -- call solveTerminal directly for that. """
        tIdx = self.db['t']
        posT = tIdx.get_loc(tIdx[-1])
        self._requireCRRA(tIdx[0])
        if sGrid is None:
            sGrid = self.GS['PEE']['stateGrids']['s_']
        if sGrid is None:
            sGrid = self.defaultSGrid(θ[posT], tIdx[-1])
        sGrid = np.asarray(sGrid)
        if sCandGrid is None:
            sCandGrid = self.GS['PEE']['solGrids']['s']
        sCandGrid = sGrid if sCandGrid is None else np.asarray(sCandGrid)

        sols = {tIdx[-1]: self.solveTerminal(θ[posT], ε[posT], t = tIdx[-1], tol = tol, sGrid = sGrid)}
        for t in tIdx[-2::-1]:
            pos = tIdx.get_loc(t)
            tLag = tIdx[pos - 1] if pos > 0 else self.B.tFirst
            t1 = tIdx[pos + 1]
            sols[t] = self.solveBackward_t(sols[t1], t, tLag, t1, θ[pos], θ[pos+1], ε[pos], ε[pos+1],
                                           sGrid, sCandGrid, tol = tol, smooth = smooth)
        self.lastMultiplicity = multiplicitySummary(sols)   # read by model.solvePEE_CRRA; per state in sols
        return sols
