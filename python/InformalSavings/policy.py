import numpy as np, pandas as pd
from scipy import optimize, interpolate
from gridsearch import (robustRoot, roots1d, CartesianGrid, griddedInterp1D, griddedInterp2D,
                        griddedSmooth1D, griddedGradient1D)


class LOG:
    """
    Identify Sequence of Policy Functions.
    Informal Savings, LOG model.

    The LOG model identifies a sequence of policy functions over the state
    ι_{t-1} = s_{t-1,0}/s_{t-1} when pension characteristics (θ,ϵ) are fixed.
    Unlike the analytical variant (no state under LOG), ι_t depends on τ_t
    through Θ_{s,t} (base.py's s0_s), so z_t = z_t(τ_t, τ_{t+1}, ι_{t-1}) and
    the tax path is no longer a triangular system in τ alone.
    """
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

    def initGS(self, grid = None):
        """ Named grid problems. 'PEE': solGrids={'τ': ...} built from this entry's own gridSettings
        (_gridSettings' defaults, overridable via `grid`), plus the state slot 'ι_' (= ι_{t-1}, docs' 𝒮_0)
        and the candidate slot solGrids['ι'] (docs' 𝒮_0'). The two are kept apart deliberately: 𝒮_0
        indexes the states solved *at*, 𝒮_0' is searched *over* to locate the equilibrium ι_t, and the
        accuracy of that search is governed by 𝒮_0' alone -- so it may warrant finer spacing.

        Both are settable *override slots*, not auto-populated caches: their bounds are data-dependent
        (they need θ/ε), and caching a computed default here would go stale silently on the next solve
        with a different policy. Left None -> the solve computes a fresh default per call. """
        settings = self._gridSettings | (grid or {})
        τGrid = np.linspace(settings['l'], settings['u'], settings['n'])
        self.GS = {'PEE': {'solGrids': {'τ': τGrid, 'ι': None}, 'stateGrids': {'ι_': None},
                           'gridSettings': settings}}

    @property
    def _gridSettings(self):
        """ Grid defaults. l/u: interior τ bounds -- u<1 strictly, since z_t carries a 1/(1-τ_t) factor and
        diverges at τ=1. n: nodes spanning [l,u]. Δl/Δu: nodes below/above the previous period's solution a
        refinement window spans (kept separate so a monotone-in-t path can be solved asymmetrically).
        nι/δι/padι/capι/spacingι: state-grid defaults -- see defaultIotaGrid.

        interpKind: the continuation interpolants' kind (gridsearch.interp). 'linear' is the piecewise-
        linear form everything below was measured against; its kinks are the documented error floor of the
        state approximation and of z_t. 'pchip' is the monotone C1 alternative -- smoother without the
        overshoot a plain 'cubic' introduces where a policy is flat at a bound. Changing it changes the
        solution, so it is recorded in the grid settings rather than set at the call sites.

    smoothKnots: how the policy smoother picks its knots (gridsearch.interp.griddedSmooth1D). An int m
        pins them at every m-th valid node, making the smoother a LINEAR MAP of its input and hence the
        outer residual continuous in the model parameters. None selects the adaptive-knot smoothing
        spline instead, whose knot COUNT is chosen from the data and therefore flips discontinuously as a
        parameter moves -- ~3.5e-6 jumps in the calibration's outer residual, which is what made ρ≈0.7
        uncalibratable (deviations note item 3).

        Defaulted to 4 on 2026-08-19, having previously defaulted to None so that pre-2026-08-19 results
        reproduced bitwise. Those results are all superseded, every calibration path was overriding it
        explicitly, and the configurations that still reached the adaptive branch by default were the ones
        that silently failed -- test_calibration.py §8 spent a session broken that way. None remains
        available and is what diagnoseRho07.py pins explicitly to reproduce its own measurements.

        NOTE the override trap this creates: initGS merges the caller's dict OVER these defaults, so
        passing smoothKnots=None explicitly now DISABLES pinned knots rather than requesting the default.
        A caller that threads an optional argument through must omit the key when it has nothing to say.
        Recorded here rather than set at the call sites for the same reason as interpKind. """
        return {'l': 1e-4, 'u': 1-1e-4, 'n': 101, 'Δl': 10, 'Δu': 10,
                'nι': 50, 'δι': 1e-4, 'padι': (0.45, 3.7), 'capι': 2.0, 'spacingι': 'log',
                'interpKind': 'linear', 'smoothKnots': 4}

    #######################################################################
    ##########   State grids over ι_{t-1} (docs §PEELOG, "Grids")      #####
    #######################################################################
    def defaultIotaGrid(self, θ, ε, t = None, n = None):
        """ Default grid of predetermined states ι_{t-1} (docs' 𝒮_0), taken from the steady state: under a
        constant policy τ, eq:auxiliary:s0_s evaluated at the steady-state Θ_s(τ) gives ι*(τ), and the grid
        spans BOTH bounds as multiples of min_τ ι*(τ): l_ι = max{δ_ι, padι[0]·min_τ ι*(τ)},
        u_ι = min{padι[1]·min_τ ι*(τ), capι}.

        Anchoring the upper bound on the MINIMUM is deliberate and is what retires the absolute cap as the
        operative bound (measureGrids.py, 2026-08-19). ι*(τ) diverges as τ→1 -- 25 484 at τ=0.9999 on the
        Argentina calibration -- so a rule anchored on max_τ ι*(τ) has no finite content and the grid's
        real upper bound was whatever capι happened to be set to, an absolute number that would not
        survive a change of data. Measured against the reachable set (policy.reachableBox), both bounds
        are stable multiples of the minimum instead: across ρ ∈ [0.5, 2.0] and under LOG, min_τ ι*(τ) is
        constant to 0.045%, and the reachable box sits at 0.539-0.557x and 2.89-3.07x it. The pads carry
        ~20% margin on those. capι survives as a backstop, inert on this calibration (3.7·0.3042 = 1.13).

        min/max run over the whole of 𝒯 rather than just its endpoints: ι*(τ) need not be monotone, and
        evaluating it is one vectorized closed-form pass (steadyState_LOG_solve takes the τ grid directly).

        l_ι > 0 strictly is not cosmetic. It puts dv20's pole at ι_{t-1}+A_tτ_t = 0 outside the evaluation
        region for every node of 𝒯, so z_t is bounded on the whole grid and no masking of the state
        dimension is needed. It also *assumes* the informal household is a net saver -- which is why a
        solved ι_t outside [l_ι,u_ι] is reported as an infeasibility and never clipped back onto the grid.

        Three departures from the doc's rule, all measured rather than assumed (see test_peeLOG.py and the
        README's open items):
        - u_ι is capped at 'capι' (default 2). ι*(τ) = s_0/s diverges as τ→1 -- not because informal
          savings explode, but because the *denominator*, formal savings, collapses -- so uncapped the
          rule gives ~10^4 on the Argentina calibration while solved paths live at ι ~ 0.1. The grid would
          then be spent almost entirely on states no path can reach. The cap places resolution; it is not
          an economic restriction, since a solved ι_t above it is still reported infeasible and never
          clipped, so too low a cap fails loudly.
        - The lower padding is 0.25, not the doc's 0.75. The steady-state range *understates* ι_t's
          dynamic range: at t=T-1 the solved ι_t(τ) falls to 0.031 against a steady-state minimum of
          0.094. With the doc's factor, 29 of 101 nodes of 𝒯 are infeasible purely because the implied ι_t
          sits below l_ι, and the political selection is then pinned to the feasibility edge at most
          states rather than determined by the first order condition (188 corner selections vs 71 here).
          The solved path is unaffected either way, which is what identifies this as a grid artefact.
        - Spacing is logarithmic ('spacingι'), which the doc does not specify. Well defined precisely
          because l_ι>0. """
        t = self.db['t'][-1] if t is None else t
        settings = self.GS['PEE']['gridSettings']
        τGrid = self.GS['PEE']['solGrids']['τ']
        Θs = self.m.steadyState_LOG_solve(τGrid, θ, t = t)['Θs']
        ι = self.B.s0_s(self.B.get('β0', t), Θs, τGrid, ε, t)   # B^0 = β_0 under LOG
        lo = max(settings['δι'], settings['padι'][0]*np.min(ι))
        hi = min(settings['padι'][1]*np.min(ι), settings['capι'])   # min, not max -- see docstring
        if not (0 < lo < hi):
            raise ValueError(f"defaultIotaGrid: degenerate state grid [{lo:.3e}, {hi:.3e}] from steady-state "
                             f"ι*(τ) ∈ [{np.min(ι):.3e}, {np.max(ι):.3e}] with cap {settings['capι']} -- "
                             "either the informal household is not a net saver over 𝒯 at this (θ,ε), so "
                             "ι_{t-1}>0 cannot be imposed, or 'capι' sits below l_ι and must be raised.")
        n = settings['nι'] if n is None else n
        return np.geomspace(lo, hi, n) if settings['spacingι'] == 'log' else np.linspace(lo, hi, n)

    def _ιGrid(self, ιGrid, θ, ε, t):
        """ Resolve the state grid 𝒮_0: explicit argument, else stateGrids['ι_'], else a fresh
        defaultIotaGrid (never cached back -- see initGS). """
        if ιGrid is None:
            ιGrid = self.GS['PEE']['stateGrids']['ι_']
        return self.defaultIotaGrid(θ, ε, t) if ιGrid is None else np.asarray(ιGrid)

    def _zState(self, zbar, τ, ε, ιGrid, t):
        """ Eq (zdecomposition): z_t(τ_t,ι_{t-1}) = z̄_t(τ_t) + ωγ_{t-1,0}p_{t-1,0}μ_{t-1,0}·A_t/(ι_{t-1}+A_tτ_t)
        -- the only channel through which the state reaches the first order condition. zbar: (M,), the pass
        over 𝒯 that every state shares. Returns (M, M_ι).

        This rank-one correction is what the design rests on: the (M,M_ι) matrix is *assembled*, never
        evaluated pointwise, so no CartesianGrid is built and refining 𝒮_0 is close to free. The weight is
        FOC's own γ_{t-1,0}·ω20, read off it rather than restated, so the two cannot drift apart. """
        BG = self.BG
        A = BG.auxInf1_(ε, t)
        w = BG.get('γ0[t-1]', t) * BG.ω20(t)
        return zbar[:, None] + w*A/(ιGrid[None, :] + A*τ[:, None])

    #######################################################################
    ##########   Grid placement diagnostics                            #####
    #######################################################################
    # Pure post-processing over what solveBackward already stored -- no solve, so these are free to record
    # on every calibration. They MEASURE where the state grids should sit; they never move them. Feeding a
    # measured box back into the grids automatically would make the solve depend on its own history, and a
    # calibration finite-differences that solve: the bounds would shift mid-search and put discontinuities
    # in the outer residual, which is exactly the failure this module spent a session removing from the
    # policy smoother (see gridsearch.interp's `knots`). Retuning the rule constants is an offline,
    # deliberate act; initGS' state slots stay override-only, per its own docstring.

    def _reachable_t(self, d):
        """ One period's (stateGrids, reachedArrays, okMask) for the box iteration, or None if the period
        records no transition (the terminal period has no continuation). LOG's single state: ι_t reached
        from each ι_{t-1}. """
        ι = d.get('ι')
        if ι is None:
            return None
        v = np.asarray(getattr(ι, 'values', ι), dtype = float)
        return {'ι': np.asarray(d['ι_'], dtype = float)}, {'ι': v}, np.isfinite(v)

    def reachableBox(self, sols, seed = None, iters = 4):
        """ The box of states the recursion actually maps into (docs eq:reachable), as {name: (lo, hi)}.

        seed: {name: (lo, hi)} to restrict the SOURCE states to, normally the solved path's own range
        widened a little. This is not optional in spirit -- the image of the whole grid is wide by
        construction (far-out states map far out) and answers nothing. Seeded, the map is iterated to a
        fixed point, so what comes back is the near-invariant region: states near the path stay near the
        path. seed=None returns the unrestricted image, which is only useful as a sanity bound.

        Cheap enough to call anywhere: every array it reads was computed by the solve. """
        box = None if seed is None else {k: (float(v[0]), float(v[1])) for k, v in seed.items()}
        for _ in range(max(1, iters)):
            acc = {}
            for t, d in sorted(sols.items()):
                r = self._reachable_t(d)
                if r is None:
                    continue
                grids, reached, ok = r
                dims = list(grids)
                sel = np.asarray(ok, dtype = bool)
                if box is not None:
                    for ax, name in enumerate(dims):
                        g, (lo, hi) = grids[name], box[name]
                        shape = [1]*len(dims)
                        shape[ax] = len(g)
                        sel = sel & ((g >= lo) & (g <= hi)).reshape(shape)
                if not sel.any():
                    continue
                for name in dims:
                    v = reached[name][sel]
                    v = v[np.isfinite(v)]
                    if v.size:
                        lo, hi = float(v.min()), float(v.max())
                        acc[name] = ((min(acc[name][0], lo), max(acc[name][1], hi))
                                     if name in acc else (lo, hi))
            if not acc:
                break
            new = acc if box is None else {k: (min(box[k][0], acc[k][0]), max(box[k][1], acc[k][1]))
                                           for k in acc}
            if box is not None and all(np.allclose(new[k], box[k]) for k in new):
                return new
            box = new
        return box

    def gridOccupancy(self, sols, box):
        """ How much of each state grid `box` occupies: the node count inside it is the resolution the
        dynamics actually get, and the fraction is the headline number to record per calibration.

        A LOW fraction is the dangerous case and the reason this is recorded rather than asserted: a grid
        that is too NARROW fails loudly (a state outside it is reported infeasible, never clipped), while
        one that is too WIDE fails silently, spending its nodes where no path goes. """
        for t, d in sorted(sols.items()):
            r = self._reachable_t(d)
            if r is None:
                continue
            grids = r[0]
            out = {}
            for name, g in grids.items():
                if name not in box:
                    continue
                lo, hi = box[name]
                inside = (g >= lo) & (g <= hi)
                cells = np.diff(g)
                idx = np.clip(np.searchsorted(g, np.clip([lo, hi], g[0], g[-1]))-1, 0, len(cells)-1)
                out[name] = {'nodes': int(inside.sum()), 'n': int(len(g)),
                             'frac': float(inside.sum()/len(g)),
                             'grid': (float(g[0]), float(g[-1])), 'box': (float(lo), float(hi)),
                             'cellAtBox': (float(cells[idx].min()), float(cells[idx].max())),
                             'cellMin': float(cells.min())}
            return out
        return {}

    #######################################################################
    ##########   Terminal period (docs alg:LOG:gridsearch)             #####
    #######################################################################
    # No continuation policy, hence no fixed point in ι_t to solve and no numerical differentiation: every
    # object entering z_T is closed form in (τ_T, ι_{T-1}) (docs eq:terminalPEELOG). The whole period is one
    # pass over 𝒯, _zState's broadcast, and one selection per state.

    def stateGrid_T(self, τ, θ, t, tLag):
        """ Terminal-period economic objects over the grid of candidate τ_T. Shapes: (M,), except si_s_
        which is (M,ni). Θ_{h,T}/dln(h_T) use T's own primitives; Γ_{s,T-1} and s_{T-1,i}/s_{T-1} -- the
        generation OLD at T -- are evaluated at the previous period's vintage, hence the explicit tLag
        (db['t'] need not be a literal integer range, so it is passed rather than computed as t-1). Neither
        ε nor ι_{T-1} appears here: both enter only through _zState. """
        BG = self.BG
        βi_ = BG.get('βi', tLag)
        Γs_ = BG.Γs(βi_, τ, θ, tLag)
        return {'τ': τ, 'Θh': BG.ΘhTerminal(τ, t), 'dlnh': BG.dlnΘhTerminal_dτ(τ, t),
                'Γs_': Γs_, 'si_s_': BG.si_s(βi_, τ, θ, Γs_, tLag)}

    def zbar_T(self, d, θ, t):
        """ Eq (zdecomposition)'s z̄_T on 𝒯, from a stateGrid_T dict: everything in z_T except the old
        informal generation's state term. dυ_{1,T}^0/dτ_T = 0 exactly (the informal young neither save nor
        face a future at T), and the dv20 slot carries only its (1-α)dln(h_T)/dτ_T part -- _zState adds the
        rest. Returns (M,). """
        BG, τ = self.BG, d['τ']
        dv1i = BG.dv1iTerminal_dτ_LOG(τ, t)
        dv2i = BG.dlnc2i_dτ(d['dlnh'], τ, θ, d['si_s_'], t)
        return BG.FOC(dv1i, np.zeros_like(τ), dv2i, (1-BG.get('α', t))*d['dlnh'], t)

    def solveTerminal(self, θ, ε, t = None, tol = 0.0, ιGrid = None):
        """ Terminal-period policy function τ_T(ι_{T-1}) over the state grid 𝒮_0, in one pass over 𝒯.
        θ, ε: scalars, period T's own pension characteristics.

        Corner/multiplicity handling is roots1d.selectMax's candidate-set criterion (docs eq:candidates):
        the maximiser of the interpolated political objective over {l,u} ∪ {downward crossings of ẑ_T},
        applied per state. z is handed over as the (M,M_ι) matrix selectMax already consumes column-wise.
        No feasibility mask at T: there is no fixed point to fail, and l_ι>0 keeps dv20's pole off the grid.

        Returns report_T's dict plus the z matrix and selectMax's 'nMax'/'atBound' diagnostics. """
        tIdx = self.db['t']
        t = tIdx[-1] if t is None else t
        pos = tIdx.get_loc(t)
        tLag = tIdx[pos - 1] if pos > 0 else self.B.tFirst
        τGrid = self.GS['PEE']['solGrids']['τ']
        ιGrid = self._ιGrid(ιGrid, θ, ε, t)
        with self.BG.cacheParams():
            d = self.stateGrid_T(τGrid, θ, t, tLag)
            z = self._zState(self.zbar_T(d, θ, t), τGrid, ε, ιGrid, t)
            sel = roots1d.selectMax(τGrid, z, tol = tol)
            report = self.report_T(ιGrid, sel['x'], θ, t, tLag)
        report['z'], report['nMax'], report['atBound'] = z, sel['nMax'], sel['atBound']
        return report

    def report_T(self, ιGrid, τ, θ, t, tLag):
        """ Expand a solved τ_T(ι_{T-1}) into the full terminal solution: stateGrid_T re-evaluated along
        the SOLVED path (it assumes nothing about where τ came from, only that its shape matches ιGrid's),
        plus the two interpolants period T-1 calls.

        τPolicy/ΘhPolicy are what the recursion carries -- Θ_{h,T}, not h_T, since the level also depends
        on s_{T-1} and so is not a function of the state (docs §PEELOG). griddedInterp1D extrapolates
        rather than clamps: t=T-1 evaluates these at whatever endogenous ι_T a candidate τ_{T-1} implies,
        which need not land on 𝒮_0's own nodes. There is no ιPolicy at T -- s_T = 0, so there is no ι_T. """
        d = self.stateGrid_T(τ, θ, t, tLag)
        kind = self.GS['PEE']['gridSettings']['interpKind']
        d['ι_'] = ιGrid
        d['τPolicy'] = griddedInterp1D(ιGrid, τ, kind)
        d['ΘhPolicy'] = griddedInterp1D(ιGrid, d['Θh'], kind)
        d['τ'] = pd.Series(τ, index = ιGrid)
        d['Θh'] = pd.Series(d['Θh'], index = ιGrid)
        return d

    #######################################################################
    ##########   t < T: backward recursion (docs alg:LOG:gridsearch)   #####
    #######################################################################
    # Two things change once there is a continuation policy τ^{t+1}(ι_t):
    #
    # (i) ι_t is no longer read off -- it is the root of eq:stateResidualLOG, since ι_t enters the
    #     right-hand side through τ^{t+1}(ι_t). It is a ROOT problem (any crossing solves it), so
    #     roots1d.allRoots is used and NOT the selectMax apparatus, which belongs to the political
    #     maximisation. Crucially the predetermined state does not appear in that fixed point at all
    #     (docs "The fixed point does not involve the state"): with B^i=β_i a primitive, Γ_{s,t} is a
    #     function of τ_{t+1} alone and Θ_{s,t} is a coefficient function with the level of past savings
    #     already divided out. So ι_t(τ_t) is solved ONCE over 𝒯×𝒮_0' and is not repeated per state --
    #     and its feasibility mask is one-dimensional for the same reason.
    #
    # (ii) The young generations' terms lose their closed form: both depend on τ_t through
    #      τ^{t+1}(ι_t(τ_t)), an interpolant with no closed-form derivative. Each profile of eq:v1LOG is
    #      assembled and differentiated numerically in one step, and dln(h_t)/dτ_t likewise comes from
    #      dln(Θ_{h,t})/dτ_t along 𝒯. The old generations' terms stay closed-form -- mandatorily so for
    #      dv2i (see base.py's dlnc2i_dτ), by choice for dv20.

    def stateApprox_t(self, τ, ι, t, θ1, solp):
        """ Forward pass of docs eq:stateApproxLOG at candidate pairs (τ_t, ι_t): a function of those two
        and the continuation policies only, never of ι_{t-1}. solp: the already-solved t+1 report, read
        only through its τPolicy/ΘhPolicy interpolants -- evaluated at candidate ι_t values that need not
        be grid nodes, which is why those interpolants extrapolate rather than clamp. """
        BG = self.BG
        τ1, Θh1 = solp['τPolicy'](ι), solp['ΘhPolicy'](ι)
        Γs = BG.Γs(BG.get('βi', t), τ1, θ1, t)          # B_{t+1}^i = β_{t,i} under LOG
        Θh = BG.Θh(τ, τ1, θ1, Γs, t)
        return {'τ1': τ1, 'Θh1': Θh1, 'Γs': Γs, 'Θh': Θh, 'Θs': BG.Θs(Θh, Γs, t)}

    def _residualIota(self, d, ι, t, ε1):
        """ Docs eq:stateResidualLOG: ι_t(β_{t,0}, Θ_{s,t}(τ_t,ι_t), τ^{t+1}(ι_t)) - ι_t, from a
        stateApprox_t dict evaluated at the same candidates ι. """
        return self.BG.s0_s(self.BG.get('β0', t), d['Θs'], d['τ1'], ε1, t) - ι

    def _rootIota(self, resid, ιCandGrid):
        """ Locate the root of eq:stateResidualLOG along 𝒮_0'. resid: (M_ι', N), one column per candidate
        τ_t. Returns ((N,) roots, (N,) root counts); NaN where no equilibrium ι_t lies inside 𝒮_0' -- the
        feasibility signal everything downstream keys off. A count >1 means genuinely multiple state
        equilibria; the lowest is taken and the count reported rather than one being silently picked. """
        r = roots1d.allRoots(ιCandGrid, resid, kind = 'any')
        if r.ndim == 1:
            r = r[:, None]
        n = (~np.isnan(r)).sum(axis = 0)
        return (r[0] if r.shape[0] else np.full(resid.shape[1], np.nan)), n

    def solveStateApprox_t(self, τGrid, ιCandGrid, t, θ1, ε1, solp):
        """ Step 1 of docs alg:LOG:gridsearch: ι_t(τ_t) on 𝒯, plus root counts. One pass over 𝒯×𝒮_0' --
        the only step that touches 𝒮_0' and the only one that calls the continuation interpolants. Both
        returns are (M,): there is no state axis here (see the §header). """
        g = CartesianGrid(τ = τGrid, ι = ιCandGrid)
        d = self.stateApprox_t(g.flat['τ'], g.flat['ι'], t, θ1, solp)
        resid = self._residualIota(d, g.flat['ι'], t, ε1)
        return self._rootIota(g.asColumns(resid, 'ι'), ιCandGrid)

    def stateGrid_t(self, τ, ι, t, tLag, θ, θ1, ε1, solp):
        """ Step 2: every object the t<T first order condition needs, given the already-resolved ι_t.
        Shapes (M,), except si_s_/v1i which are (M,ni). The t/tLag split is the terminal period's: only
        the generation OLD at t (Γ_{s,t-1}, s_{t-1,i}/s_{t-1}) uses tLag, everything else t's own vintage.
        The two young profiles are known only up to an additive constant along τ_t -- see base.py's
        v1iProfile_LOG/v10Profile_LOG, which is also why no s_{t-1} appears anywhere here. """
        BG = self.BG
        d = self.stateApprox_t(τ, ι, t, θ1, solp)
        d['τ'], d['ι'] = τ, ι
        d['v1i'] = BG.v1iProfile_LOG(d['Θh'], d['Θs'], d['Θh1'], BG.get('βi', t), d['τ1'], θ1, d['Γs'], t)
        d['v10'] = BG.v10Profile_LOG(d['Θs'], d['Θh1'], BG.get('β0', t), d['τ1'], ε1, t)
        βi_ = BG.get('βi', tLag)
        d['Γs_'] = BG.Γs(βi_, τ, θ, tLag)
        d['si_s_'] = BG.si_s(βi_, τ, θ, d['Γs_'], tLag)
        return d

    def _gradProfile(self, τGrid, y, s):
        """ dy/dτ along 𝒯, differentiated in the coordinate x = ln(1-τ_t) and chain-ruled back
        (dy/dτ = (dy/dx)·(-1/(1-τ_t))). Two deliberate departures from a bare griddedGradient1D call:

        1. The coordinate. Every profile here carries a ln(1-τ_t) term -- Θ_{h,t} ∝ ((1-α)(1-τ_t))^{ξ/(1+αξ)}
           -- so dy/dτ diverges like 1/(1-τ_t) as τ_t→u, and a spline through uniformly spaced τ nodes
           cannot represent that: measured against the closed form available when the continuation policy
           is held constant, a raw-τ fit is off by ~1e-2 relative near the top of 𝒯 (and ~1e-3 in the
           interior), while in x it is exact to ~1e-15. The singular part is affine in x, so the spline
           reproduces it; only the genuine curvature from τ^{t+1}(ι_t(τ_t)) is left to approximate.
        2. The scaling. griddedGradient1D's `s` is an absolute sum-of-squared-residuals bound, so a raw
           call would smooth a profile of magnitude 10^3 and one of magnitude 10^-3 completely
           differently. Each column is normalised by its own standard deviation and the derivative
           rescaled after, making `s` a budget in units of the profile's own variation -- so one default
           works for every profile.

        NaNs (infeasible nodes) are dropped from the fit and returned as NaN, by griddedGradient1D.

        On `s` itself: the callers default it to 0, i.e. an interpolating spline. Measured against the
        exact derivative (test_peeLOG.py §8), s=1e-6 in the units above is already 3-10x worse than s=0 --
        the profiles are smooth enough in x that there is nothing to denoise, and what remains is the
        kinks of the piecewise-linear continuation interpolant, which smoothing blurs rather than fixes.
        The doc's advice to smooth applies to τ_t(ι_{t-1}) before interpolation (solveBackward_t's
        `smooth`), not here. """
        y = np.asarray(y, dtype = float)
        flat = y.reshape(len(τGrid), -1)
        σ = np.nanstd(flat, axis = 0)
        σ = np.where(σ > 0, σ, 1.0)
        dydx = griddedGradient1D(np.log(1-τGrid), flat/σ, s = s) * σ
        return (dydx * (-1/(1-τGrid))[:, None]).reshape(y.shape)

    def zbar_t(self, d, θ, t, s = 0.0):
        """ Step 3: eq:zdecomposition's z̄_t on 𝒯, from a stateGrid_t dict. The two young profiles and
        dln(h_t)/dτ_t = dln(Θ_{h,t})/dτ_t (eq:logsep) are grid derivatives; dv2i and the dv20 stub are
        closed form. Infeasible nodes stay NaN throughout rather than being filled. Returns (M,).

        d['τ'] must be the full 𝒯 grid, not a subset: the derivatives run along it. s: the scale-free
        smoothing budget of _gradProfile. """
        BG, τ = self.BG, d['τ']
        dlnh = self._gradProfile(τ, np.log(d['Θh']), s)
        dv1i = self._gradProfile(τ, d['v1i'], s)
        dv10 = self._gradProfile(τ, d['v10'], s)
        dv2i = BG.dlnc2i_dτ(dlnh, τ, θ, d['si_s_'], t)
        return BG.FOC(dv1i, dv10, dv2i, (1-BG.get('α', t))*dlnh, t)

    def solveBackward_t(self, solp, t, tLag, θ, θ1, ε, ε1, ιGrid, ιCandGrid,
                        tol = 0.0, sGrad = 0.0, smooth = 1e-5, minFeasible = 2):
        """ One period of the backward recursion (steps 1-4 of docs alg:LOG:gridsearch), returning the same
        kind of dict as solveTerminal.

        minFeasible: the doc's requirement that at least two nodes of 𝒯 admit a state before a maximum is
        attempted -- selectMax enforces it per column anyway, but failing here gives the actual reason
        instead of a column of NaNs. smooth: griddedSmooth1D on the selected τ_t(ι_{t-1}) before
        interpolation (the profile inherits small kinks from the continuation interpolants, which the next
        period's numerical derivatives amplify); applied in log ι, since 𝒮_0 is geometrically spaced. Pass
        0 to disable. """
        settings = self.GS['PEE']['gridSettings']
        τGrid = self.GS['PEE']['solGrids']['τ']
        with self.BG.cacheParams():
            ι, nRoots = self.solveStateApprox_t(τGrid, ιCandGrid, t, θ1, ε1, solp)
            feasible = ~np.isnan(ι)
            if feasible.sum() < minFeasible:
                raise RuntimeError(f"t={t}: eq:stateResidualLOG has a root inside 𝒮_0' at only "
                                   f"{int(feasible.sum())} of {τGrid.size} nodes of 𝒯 (need {minFeasible}). "
                                   "Widen 𝒮_0' or narrow 𝒯 -- the implied ι_t leaves the grid, it is not "
                                   "clipped back onto it.")
            d = self.stateGrid_t(τGrid, ι, t, tLag, θ, θ1, ε1, solp)
            z = self._zState(self.zbar_t(d, θ, t, s = sGrad), τGrid, ε, ιGrid, t)
            sel = roots1d.selectMax(τGrid, z, tol = tol)
            τ = sel['x']
            if smooth:
                good = ~np.isnan(τ)
                τ = np.where(good, griddedSmooth1D(np.log(ιGrid), np.where(good, τ, np.nan), s = smooth,
                                                   knots = settings['smoothKnots']), np.nan)
                τ = np.clip(τ, settings['l'], settings['u'])   # a denoise must not leave the admissible set
            report = self.report_t(ιGrid, τ, ιCandGrid, t, tLag, θ, θ1, ε1, solp)
        report['z'], report['nMax'], report['atBound'] = z, sel['nMax'], sel['atBound']
        report['feasible'], report['nRoots'], report['ιOfτ'] = feasible, nRoots, ι
        return report

    def report_t(self, ιGrid, τ, ιCandGrid, t, tLag, θ, θ1, ε1, solp):
        """ Step 4, t<T counterpart of report_T: re-solve the state fixed point at the SELECTED τ_t(ι_{t-1})
        (which generally falls between nodes of 𝒯, so its ι_t must be re-solved rather than read off step
        1's grid -- cheap, one M_ι'×M_ι pass), expand into the full solution dict, and build the
        interpolants period t-1 calls.

        Three interpolants, not two: alongside τPolicy/ΘhPolicy this reports ιPolicy, the state transition
        ι_{t-1} ↦ ι_t along the equilibrium. That is what turns a sequence of policy functions into a path,
        and it costs nothing here since ι_t at every node is already the equilibrium value. """
        nS, nC = len(ιGrid), len(ιCandGrid)
        τ2 = np.broadcast_to(τ, (nC, nS)).reshape(-1)
        ι2 = np.broadcast_to(ιCandGrid[:, None], (nC, nS)).reshape(-1)
        dd = self.stateApprox_t(τ2, ι2, t, θ1, solp)
        ι, nRoots = self._rootIota(self._residualIota(dd, ι2, t, ε1).reshape(nC, nS), ιCandGrid)

        d = self.stateGrid_t(τ, ι, t, tLag, θ, θ1, ε1, solp)
        good = ~np.isnan(τ) & ~np.isnan(ι)
        d['ι_'], d['nRootsSol'], d['ιCand'] = ιGrid, nRoots, ιCandGrid  # 𝒮_0' recorded so the path
        # solve re-solves the transition on the grid this period used, rather than a re-resolved default
        d['outOfGrid'] = good & ((ι < ιGrid[0]) | (ι > ιGrid[-1]))  # never clipped -- docs §PEELOG
        kind = self.GS['PEE']['gridSettings']['interpKind']
        d['τPolicy'] = griddedInterp1D(ιGrid[good], τ[good], kind)
        d['ΘhPolicy'] = griddedInterp1D(ιGrid[good], d['Θh'][good], kind)
        d['ιPolicy'] = griddedInterp1D(ιGrid[good], ι[good], kind)
        d['τ'] = pd.Series(τ, index = ιGrid)
        d['Θh'] = pd.Series(d['Θh'], index = ιGrid)
        d['ι'] = pd.Series(ι, index = ιGrid)
        return d

    def solveBackward(self, θ, ε, ιGrid = None, ιCandGrid = None, tol = 0.0,
                      sGrad = 0.0, smooth = 1e-5, minFeasible = 2):
        """ The full LOG politico-economic equilibrium: the sequence of policy functions τ_t(ι_{t-1}),
        solved backwards from the terminal period (docs alg:LOG:gridsearch). Returns {t: solution dict},
        one entry per db['t']. θ, ε: full length-T paths. No initial guess for the path is needed --
        the recursion is self-starting from t=T.

        ιGrid: the state grid 𝒮_0, shared by every period (adjacent periods' interpolants must live on a
        common grid) -- resolved once here and pinned, defaulting to stateGrids['ι_'] else defaultIotaGrid
        at the terminal period's (θ,ε). ιCandGrid: 𝒮_0', the candidate grid searched over; defaults to
        solGrids['ι'] else 𝒮_0 itself.

        Cost is O(T·M·M_ι') closed-form evaluations: the state grid 𝒮_0 enters only through the selection
        step, not the evaluations, which is the practical content of eq:zdecomposition. """
        tIdx = self.db['t']
        posT = tIdx.get_loc(tIdx[-1])
        ιGrid = self._ιGrid(ιGrid, θ[posT], ε[posT], tIdx[-1])
        if ιCandGrid is None:
            ιCandGrid = self.GS['PEE']['solGrids']['ι']
        ιCandGrid = ιGrid if ιCandGrid is None else np.asarray(ιCandGrid)

        sols = {tIdx[-1]: self.solveTerminal(θ[posT], ε[posT], t = tIdx[-1], tol = tol, ιGrid = ιGrid)}
        for t in tIdx[-2::-1]:
            pos = tIdx.get_loc(t)
            tLag = tIdx[pos - 1] if pos > 0 else self.B.tFirst
            sols[t] = self.solveBackward_t(sols[tIdx[pos + 1]], t, tLag, θ[pos], θ[pos + 1],
                                           ε[pos], ε[pos + 1], ιGrid, ιCandGrid, tol = tol,
                                           sGrad = sGrad, smooth = smooth, minFeasible = minFeasible)
        return sols

    #######################################################################
    ##########   Forward simulation (docs eq:forwardSim)               #####
    #######################################################################
    def approximatePEE(self, sols, θ, ε, ι0, exact = True, strict = True):
        """ Walk the backward-solved policy functions forward from the initial state ι_0 (docs
        eq:forwardSim) -- what turns a sequence of policy functions into one path.

        sols: solveBackward's {t: report}. θ, ε: full length-T paths (needed by the re-solve below). ι0:
        the state entering db['t'][0] -- the docs' ι_0, i.e. the code's ι_{-1} (README's timing
        convention), normally model.py's initialStatePEE.

        exact: take the state transition as the docs write it, ι_t = ι_t(τ_t) -- re-solving
        eq:stateResidualLOG at the walked τ_t -- rather than reading it off the reported ιPolicy. The two
        agree at the nodes of 𝒮_0 and differ between them, so this removes 𝒮_0's interpolation error
        from the transition; it costs one root per PERIOD, against the one per NODE the recursion already
        paid. It also keeps the structural result the module is built on: ι_{t-1} does not enter that
        fixed point at all, which is exactly what interpolating ι_t over ι_{t-1} would discard. Pass
        exact=False to walk the interpolants instead -- the gap between the two is the state grid's own
        contribution to the path error.

        Returns {'τ': pd.Series over db['t'], 'ι': (T-1,) the states this path generates (docs' ι_t,
        t=1..T-1, the db['txE'] domain), 'ι_': (T,) the state ENTERING each period, 'inGrid'/'atBound':
        (T,) diagnostics}. Still not an equilibrium guarantee even at exact=True: τ_t itself comes off an
        interpolant, and the re-solve reaches t+1 through the continuation interpolants. Which is why
        model.py re-solves the economic equilibrium exactly at this τ.

        strict: raise if an entering state leaves 𝒮_0 (or anything is non-finite -- including a period
        whose transition has no root inside 𝒮_0') instead of returning it. Past the grid's ends
        griddedInterp1D extrapolates rather than clamps, so such a path is driven by a policy that was
        never solved for. Reported, never clipped -- docs §PEELOG. """
        tIdx = self.db['t']
        settings = self.GS['PEE']['gridSettings']
        l, u = settings['l'], settings['u']
        τ, ι_, ι = np.empty(self.T), np.empty(self.T), np.empty(self.T - 1)
        state = float(ι0)
        for pos, t in enumerate(tIdx):
            ι_[pos] = state
            τ[pos] = np.clip(float(sols[t]['τPolicy'](state)), l, u)
            if pos < self.T - 1:
                if exact:
                    r, _ = self.solveStateApprox_t(np.array([τ[pos]]), sols[t]['ιCand'], t,
                                                   θ[pos + 1], ε[pos + 1], sols[tIdx[pos + 1]])
                    state = float(r[0])
                else:
                    state = float(sols[t]['ιPolicy'](state))
                ι[pos] = state
        ιGrid = sols[tIdx[0]]['ι_']
        inGrid = (ι_ >= ιGrid[0]) & (ι_ <= ιGrid[-1]) & np.isfinite(ι_) & np.isfinite(τ)
        out = {'τ': pd.Series(τ, index = tIdx), 'ι': ι, 'ι_': ι_, 'inGrid': inGrid,
               'atBound': np.isclose(τ, l) | np.isclose(τ, u)}
        if strict and not inGrid.all():
            bad = np.flatnonzero(~inGrid)
            raise RuntimeError(f"approximatePEE: the state entering t={list(tIdx[bad])} lies outside "
                               f"𝒮_0=[{ιGrid[0]:.3e}, {ιGrid[-1]:.3e}] (ι_={np.array2string(ι_[bad], precision = 3)}). "
                               "The path would be driven by extrapolated policy: widen 𝒮_0, or check the "
                               "initial state. Pass strict=False to return it flagged instead.")
        return out


class CRRA(LOG):
    """
    Identify Sequence of Policy Functions.
    Informal Savings, CRRA model (docs §PEE, alg:CRRA:grid).

    Two endogenous states. ι_{t-1} survives from the LOG case unchanged; the savings level s_{t-1} returns
    because eq:logsep no longer applies -- the marginal indirect utilities are (level)^{1-1/ρ}×(log-
    derivative), and while the log-derivatives are still independent of s_{t-1}, the levels are not.

    Three structural facts keep this from costing what a naive 5-dimensional reading would suggest, and
    each has a named method below:

    1. The forward pass (eq:stateApprox) sees NEITHER predetermined state, so it is evaluated once on
       𝒯×𝒮'×𝒮_0' -- 3-dimensional, not 5 (stateApprox_t).
    2. The two states unnest EXACTLY into two 1-D roots (eq:iotaOfTauS): ι_t(τ_t,s_t) first, since its
       residual involves neither predetermined state, then s_t given s_{t-1}. The ordering is forced --
       s_t cannot be resolved without s_{t-1} (_iotaOfTauS, then _rootS).
    3. ι_{t-1} still enters only the old informal generation's term, so extending 𝒯×𝒮 to 𝒯×𝒮×𝒮_0 is a
       broadcast (_zStateCRRA). It is no longer rank-one -- the (c_{2,t}^0)^{1-1/ρ} factor sees the state
       too -- but it still requires no re-entry into the forward pass.

    What LOG carried as Θ_{h,t+1}, this class carries as h_{t+1}: with s_t among the states the level IS a
    function of the state, and B_{t+1} needs it as a level.

    ρ=1 is refused outright (_requireCRRA) rather than approximated: the (·)^{1-1/ρ} powers and hatc1's
    exponent both divide by 1-1/ρ. It is not a gap -- ρ=1 is exactly what the LOG class solves in closed
    form, and the two agreeing in the limit is a test rather than a fallback.
    """

    @property
    def _gridSettings(self):
        """ LOG's, plus the savings-state grid (ns/δs/pads -- see defaultSGrid) and the refinement factor
        of its candidate grid (nsCandMult -- see defaultSCandGrid). nι is halved from LOG's default: with
        two states the product grid 𝒮×𝒮_0 is what costs, and the report step's re-solve scales with it. """
        return super()._gridSettings | {'nι': 30, 'ns': 30, 'δs': 1e-4, 'pads': (0.45, 3.65),
                                        'sAnchorτ': 0.3, 'nsCandMult': 4}

    def initGS(self, grid = None):
        """ Extends LOG's 'PEE' entry (not a separate name) with the second state: stateGrids['s_'] (docs'
        𝒮) and solGrids['s'] (docs' 𝒮'), the same state/candidate split as ι_/ι. Both start unset, for the
        reason given in LOG.initGS. """
        super().initGS(grid)
        self.GS['PEE']['stateGrids']['s_'] = None
        self.GS['PEE']['solGrids']['s'] = None

    def _requireCRRA(self, t):
        """ Guard every CRRA entry point against ρ=1 before anything evaluates a (·)^{1-1/ρ} power -- a
        directed error rather than a silently propagating inf/NaN. """
        ρ = self.BG.get('ρ', t)
        if np.isclose(ρ, 1):
            raise ValueError(f"CRRA requires ρ != 1 (got ρ={ρ}): every term of eq:PEEcrraTerms carries a "
                             "factor raised to 1-1/ρ, and hatc1's exponent 1/(1-1/ρ) diverges. Use the LOG "
                             "class, which solves ρ=1 in closed form.")

    #######################################################################
    ##########   Grids (docs §PEE, "Grids")                            #####
    #######################################################################
    def defaultSGrid(self, θ, t = None, n = None):
        """ Default grid of predetermined savings levels s_{t-1} (docs' 𝒮): both bounds as multiples
        (pads) of s*(sAnchorτ), the steady state at a fixed interior τ. Linearly spaced, unlike 𝒮_0: s*'s
        range is a single order of magnitude, so there is no resolution problem to fix.

        The anchor is NOT s*(0), and not the calibration's own τ_0 either -- both were measured and
        rejected (measureGrids.py, 2026-08-19). s*(τ) at low τ moves the wrong way: across ρ ∈ [0.5, 2.0]
        s*(0) falls by 83% while the reachable box's upper edge RISES by 20%, a correlation of -1.000, so
        no constant pad on it can track the box (occupancy ran 40% at ρ=0.5 against 80% at ρ=2.0). s*(τ_0)
        is better but still drifts 77%. At τ=0.3 the steady state is ρ-stable to 1.5% while remaining a
        solved function of the calibrated parameters, so it moves with the DATA without moving with ρ,
        which is what an anchor has to do. Pads of (0.45, 3.65) then contain the box at every ρ measured,
        with ~20% margin and occupancy 63-78%.

        δs remains a hard floor: s_{t-1}=0 makes Rlead/B/si_s undefined. """
        t = self.db['t'][-1] if t is None else t
        settings = self.GS['PEE']['gridSettings']
        anchor = self.m.steadyState_CRRA_solve(settings['sAnchorτ'], θ, t = t)['s']
        lo, hi = settings['pads'][0]*anchor, settings['pads'][1]*anchor
        return np.linspace(max(settings['δs'], lo), hi, settings['ns'] if n is None else n)

    def defaultIotaGrid(self, θ, ε, t = None, n = None, nτ = 21):
        """ LOG's rule (padded, capped range of the steady-state ι*(τ) -- see LOG.defaultIotaGrid for the
        three departures from the doc, all of which carry over), but off the CRRA steady state, where B^0
        is B0SteadyState rather than the primitive β_0.

        ι*(τ) is evaluated on a coarse subsample of 𝒯 (nτ nodes) rather than every node, since each is a
        brentq solve rather than a closed form. Nodes where that solve fails to bracket -- which happens as
        τ→1, where the steady state degenerates -- are skipped rather than propagated; only ValueError and
        RuntimeError are caught, the two the steady-state solve raises, so a genuine bug still surfaces. """
        t = self.db['t'][-1] if t is None else t
        settings = self.GS['PEE']['gridSettings']
        τGrid = self.GS['PEE']['solGrids']['τ']
        ι = []
        for τ in np.linspace(τGrid[0], τGrid[-1], nτ):
            try:
                ss = self.m.steadyState_CRRA_solve(τ, θ, t = t)
            except (ValueError, RuntimeError):
                continue
            ι.append(self.B.s0_s(self.B.B0SteadyState(ss['Γs'], τ, θ, t), ss['Θs'], τ, ε, t))
        if len(ι) < 2:
            raise RuntimeError(f"defaultIotaGrid: the CRRA steady state solved at only {len(ι)} of {nτ} "
                               "τ-nodes, too few to bracket ι*(τ). Pass an explicit state grid.")
        ι = np.asarray(ι)
        lo = max(settings['δι'], settings['padι'][0]*np.min(ι))
        hi = min(settings['padι'][1]*np.min(ι), settings['capι'])   # min, not max -- see docstring
        if not (0 < lo < hi):
            raise ValueError(f"defaultIotaGrid: degenerate state grid [{lo:.3e}, {hi:.3e}] from ι*(τ) ∈ "
                             f"[{np.min(ι):.3e}, {np.max(ι):.3e}] with cap {settings['capι']}.")
        n = settings['nι'] if n is None else n
        return np.geomspace(lo, hi, n) if settings['spacingι'] == 'log' else np.linspace(lo, hi, n)

    def _reachable_t(self, d):
        """ LOG's, over the state PAIR. report_t already records eq:reachable's (s_t,ι_t) and its own
        in-grid mask, so this is a lookup: both arrays are (nS, nι) over (s_{t-1}, ι_{t-1}), matching the
        order of the grids returned beside them. """
        r = d.get('reachable')
        if r is None:
            return None
        return ({'s': np.asarray(d['s_'], dtype = float), 'ι': np.asarray(d['ι_'], dtype = float)},
                {'s': np.asarray(r['s'], dtype = float), 'ι': np.asarray(r['ι'], dtype = float)},
                np.asarray(r['inGrid'], dtype = bool))

    def defaultSCandGrid(self, sGrid):
        """ Default 𝒮', the candidate grid the s_t root is searched over: spans 𝒮 but finer by
        'nsCandMult' AND geometrically spaced. The two candidate grids are deliberately chosen by
        different rules, because the two roots' errors have different sources (measured; docs §PEE
        "Grids"):

        - eq:stateResidual:iota reaches ι_t ONLY through the continuation interpolants, which are
          piecewise linear with breakpoints at 𝒮_0's nodes. The residual therefore has no intrinsic
          curvature of its own -- its kinks are the whole error -- and a cell of 𝒮_0' straddling a
          breakpoint is one the secant cannot represent. Aligning 𝒮_0' with 𝒮_0 removes every straddling
          cell: relative error 2.3e-7 at 𝒮_0'=𝒮_0, falling as O(h²) along refinements that CONTAIN 𝒮_0's
          nodes (5.4e-8, 1.4e-8, 3.5e-9 at k=2,4,8), while same-size grids that do not sit at ~2e-5 and do
          not converge cleanly. Hence 𝒮_0' = 𝒮_0 by default; refine it only as a superset.
        - eq:stateResidual:s is dominated instead by B_{t+1}(s_t,h_{t+1})'s genuine nonlinearity in s_t,
          which swamps the same kinks. Alignment buys nothing there (superset and non-aligned grids of
          equal size agree to within 20%), and refinement does. Relative error in the located s_t across
          the state grid: 2.3e-2 at 𝒮'=𝒮, 4.5e-4 at 4x uniform, 7.2e-5 at 4x geometric -- geometric
          because s_t spans a factor of ~20 while a uniform 𝒮' puts constant-width cells at the bottom of
          that range. """
        settings = self.GS['PEE']['gridSettings']
        return np.geomspace(sGrid[0], sGrid[-1], settings['nsCandMult']*len(sGrid))

    def _sGrid(self, sGrid, θ, t):
        """ Resolve 𝒮: explicit argument, else stateGrids['s_'], else a fresh defaultSGrid. """
        if sGrid is None:
            sGrid = self.GS['PEE']['stateGrids']['s_']
        return self.defaultSGrid(θ, t) if sGrid is None else np.asarray(sGrid)

    #######################################################################
    ##########   The state broadcast (docs eq:PEEcrraTerms + dv20)     #####
    #######################################################################
    def _zStateCRRA(self, zbar, d, ε, ιGrid, t, g):
        """ Extend z_t from 𝒯×𝒮 to 𝒯×𝒮×𝒮_0 (step 3 of alg:CRRA:grid). zbar and the entries of d are flat
        over g = CartesianGrid(τ, s_); returns (M, M_s, M_ι), matching the C-order flattening of
        CartesianGrid(τ, s_, ι_).

        LOG's counterpart (_zState) is a rank-one correction; this one is not, because the level factor
        (c_{2,t}^0)^{1-1/ρ} depends on the state as well as the log-derivative. It is still a pure
        broadcast: c_{2,t}^0 = outer(τ_t,s_{t-1})·(ι_{t-1}+A_tτ_t) and eq:dv20 both read off objects the
        (τ,s_) pass already produced, so no cell of 𝒯×𝒮×𝒮_0 re-enters eq:stateApprox. The weight is FOC's
        own γ_{t-1,0}·ω20, read off it rather than restated. """
        BG = self.BG
        p = 1 - 1/BG.get('ρ', t)
        r = lambda y: g.reshape(y)[..., None]                # (M, M_s, 1)
        τ3, h3, s_3, dlnh3 = r(d['τ']), r(d['h']), r(d['s_']), r(d['dlnh'])
        ι3 = ιGrid[None, None, :]
        dv20 = BG.c20(h3, s_3, ε, τ3, ι3, t)**p * BG.dlnc20_dτ(dlnh3, τ3, ε, ι3, t)
        return g.reshape(zbar)[..., None] + BG.get('γ0[t-1]', t)*BG.ω20(t)*dv20

    #######################################################################
    ##########   Terminal period (docs alg:CRRA:grid)                  #####
    #######################################################################
    # The one place the full three-dimensional grid is evaluated outright -- affordable precisely because
    # there is no state approximation to perform: every object is closed form in (τ_T, s_{T-1}, ι_{T-1}),
    # so it is one vectorized pass rather than a root-finding problem per cell.

    def stateGrid_T(self, τ, s_, θ, t, tLag):
        """ Terminal-period objects over flat (τ_T, s_{T-1}) points; (P,) except Bi/si_s_/tc1i, (P,ni).
        Only B_T^i (the generation OLD at T) and what depends on it (Γ_{s,T-1}, s_{T-1,i}/s_{T-1}) use
        tLag. Unlike the LOG case this genuinely needs h_T as a level: B_T^i = Base.B(s_{T-1}, h_T) is what
        makes s_{T-1} a state at all. c_{2,T}^0 is not built here -- it needs ι_{T-1}, so it belongs to the
        broadcast. """
        BG = self.BG
        Θh = BG.ΘhTerminal(τ, t)
        h = BG.h(Θh, s_, t)
        Bi = BG.B(s_, h, tLag)
        Γs_ = BG.Γs(Bi, τ, θ, tLag)
        si_s_ = BG.si_s(Bi, τ, θ, Γs_, tLag)
        zB, zΓs = np.zeros_like(Bi), np.zeros_like(Γs_)      # terminal collapse, as FH_tildec1i does
        return {'τ': τ, 's_': s_, 'Θh': Θh, 'h': h, 'dlnh': BG.dlnΘhTerminal_dτ(τ, t),
                'Bi': Bi, 'Γs_': Γs_, 'si_s_': si_s_,
                'tc1i': BG.tildec1i(h, zB, τ, θ, zΓs, t), 'c2i': BG.c2i(h, s_, τ, θ, si_s_, t)}

    def zbar_T(self, d, θ, t):
        """ The three (τ_T, s_{T-1}) terms of z_T (docs eq:terminalPEECRRA): each is a consumption level to
        the power 1-1/ρ times the log-derivative the LOG case already implements. dυ_{1,T}^0/dτ_T = 0
        regardless of ρ. The dv20 slot is left at zero -- _zStateCRRA supplies it. """
        BG, τ = self.BG, d['τ']
        p = 1 - 1/BG.get('ρ', t)
        dv1i = d['tc1i']**p * BG.dv1iTerminal_dτ_LOG(τ, t)
        dv2i = d['c2i']**p * BG.dlnc2i_dτ(d['dlnh'], τ, θ, d['si_s_'], t)
        return BG.FOC(dv1i, np.zeros_like(τ), dv2i, np.zeros_like(τ), t)

    def solveTerminal(self, θ, ε, t = None, tol = 0.0, ιGrid = None, sGrid = None):
        """ Terminal-period τ_T(s_{T-1}, ι_{T-1}) over the state grid 𝒮×𝒮_0, in one vectorized pass.
        Feasibility condition 3 (positive consumption levels) is the only one that can bite at T, and only
        through c_{2,T}^i; infeasible cells are NaN and selectMax maximises each state over its own
        surviving sub-grid. Returns report_T's dict plus z and selectMax's diagnostics.

        Deliberately NOT guarded by _requireCRRA. The terminal period never forms ĉ_1, so it stays
        well-defined at ρ=1, where every level factor collapses to c^0=1 and B_T^i to the primitive β_i --
        making this solve *exactly* LOG.solveTerminal at every state. That identity is the sharpest
        available test of this class, and refusing ρ=1 here would put it out of reach. """
        tIdx = self.db['t']
        t = tIdx[-1] if t is None else t
        pos = tIdx.get_loc(t)
        tLag = tIdx[pos - 1] if pos > 0 else self.B.tFirst
        τGrid = self.GS['PEE']['solGrids']['τ']
        ιGrid, sGrid = self._ιGrid(ιGrid, θ, ε, t), self._sGrid(sGrid, θ, t)
        g = CartesianGrid(τ = τGrid, s_ = sGrid)
        with self.BG.cacheParams():
            d = self.stateGrid_T(g.flat['τ'], g.flat['s_'], θ, t, tLag)
            zbar = np.where(self._positiveLevels(d), self.zbar_T(d, θ, t), np.nan)
            z = self._zStateCRRA(zbar, d, ε, ιGrid, t, g)
            g3 = CartesianGrid(τ = τGrid, s_ = sGrid, ι_ = ιGrid)
            sel = roots1d.selectMaxND(g3, z.reshape(-1), 'τ', tol = tol)
            report = self.report_T(sGrid, ιGrid, sel['x'], θ, t, tLag)
        report['z'], report['nMax'], report['atBound'] = z, sel['nMax'], sel['atBound']
        report['feasible'] = g.reshape(~np.isnan(zbar))
        return report

    def _positiveLevels(self, d):
        """ Feasibility condition 3 (docs §PEE): the (·)^{1-1/ρ} factors are undefined at a non-positive
        base. Of the four levels only c_{2,t}^i can turn negative -- its bracket
        s_{t-1,i}/s_{t-1}+A(1+θ_t[...]) can go negative for a low-productivity type when the savings share
        is small -- but c̃_1 is checked too, cheaply, rather than argued to be safe at every candidate.
        Returns a (P,) mask: a cell is feasible only if EVERY type's levels are positive, since z_t sums
        over types and one bad type poisons the sum. """
        levels = [v for k, v in d.items() if k in ('tc1i', 'c2i', 'hatc1iPow', 'hatc10Pow')]
        ok = np.ones(np.shape(d['τ']), dtype = bool)
        for v in levels:
            ok &= np.all(np.asarray(v) > 0, axis = -1) if np.ndim(v) > np.ndim(d['τ']) else (v > 0)
        return ok

    def report_T(self, sGrid, ιGrid, τ, θ, t, tLag):
        """ Expand a solved τ_T(s_{T-1},ι_{T-1}) into the full terminal solution, evaluated along the
        SOLVED path, plus the two 2-D interpolants period T-1 calls. h_T, not Θ_{h,T}: with s_{T-1} a
        state the level is a function of the state, and B_T needs it as a level (docs §PEE).

        τ arrives shaped (M_s, M_ι) from selectMaxND; stateGrid_T is called on the flattened pair, so the
        state grids are meshed here rather than crossed by CartesianGrid. """
        s2, ι2 = np.meshgrid(sGrid, ιGrid, indexing = 'ij')
        d = self.stateGrid_T(τ.reshape(-1), s2.reshape(-1), θ, t, tLag)
        shape = (len(sGrid), len(ιGrid))
        d = {k: (v.reshape(shape + v.shape[1:]) if np.ndim(v) else v) for k, v in d.items()}
        kind = self.GS['PEE']['gridSettings']['interpKind']
        d['s_'], d['ι_'] = sGrid, ιGrid
        d['τPolicy'] = griddedInterp2D(sGrid, ιGrid, τ, kind)
        d['hPolicy'] = griddedInterp2D(sGrid, ιGrid, d['h'], kind)
        d['τ'] = pd.DataFrame(τ, index = sGrid, columns = ιGrid)
        d['h'] = pd.DataFrame(d['h'], index = sGrid, columns = ιGrid)
        return d

    #######################################################################
    ##########   t < T: backward recursion (docs alg:CRRA:grid)        #####
    #######################################################################

    def _stateApproxSI(self, s, ι, t, θ1, solp):
        """ The τ_t-free part of docs eq:stateApprox: everything fixed by (s_t, ι_t) and the continuation
        policies alone. τ_t reaches eq:stateApprox only through Θ_{h,t}, so τ_{t+1}, h_{t+1}, B_{t+1},
        B_{t+1}^0 and Γ_{s,t} -- and the two interpolant calls behind them -- are constant along τ_t.

        Split out so _iotaOfTauS can evaluate this block once per distinct (s_t,ι_t) PAIR rather than once
        per (τ_t,s_t,ι_t) triple; see its docstring for the sizes involved. Exact, not an approximation:
        the argument lists are the authority -- none of Rlead/B/B0/Γs takes τ_t. """
        BG = self.BG
        τ1, h1 = solp['τPolicy'](s, ι), solp['hPolicy'](s, ι)
        B1, B01 = BG.B(s, h1, t), BG.B0(s, h1, t)
        return {'τ1': τ1, 'h1': h1, 'B1': B1, 'B01': B01, 'Γs': BG.Γs(B1, τ1, θ1, t)}

    def stateApprox_t(self, τ, s, ι, t, θ1, solp):
        """ Forward pass of docs eq:stateApprox at candidate triples (τ_t, s_t, ι_t), flat and mutually
        broadcastable. A function of those three and the continuation policies only -- NEITHER
        predetermined state appears, which is what makes the expensive part 3-dimensional rather than 5.
        solp is read only through τPolicy/hPolicy, evaluated at candidate pairs that need not be grid
        nodes (hence griddedInterp2D's extrapolation). """
        d = self._stateApproxSI(s, ι, t, θ1, solp)
        d['Θh'] = self.BG.Θh(τ, d['τ1'], θ1, d['Γs'], t)
        d['Θs'] = self.BG.Θs(d['Θh'], d['Γs'], t)
        return d

    def _iotaOfTauS(self, τ, s, t, θ1, ε1, solp, ιCandGrid, chunk = 200000):
        """ Docs eq:iotaOfTauS: the root of eq:stateResidual:iota along 𝒮_0', at arbitrary (τ_t, s_t)
        pairs. τ/s: flat, equal length P. Returns ((P,) roots, (P,) counts), NaN where no root lies inside
        𝒮_0' -- feasibility condition 1.

        Solved FIRST and without either predetermined state, which is what makes the nesting exact rather
        than an approximation. Evaluated in chunks of `chunk` (τ,s,ι) triples: the report step calls this
        with P = |𝒮|·|𝒮_0| pairs, so the full product against 𝒮_0' would otherwise be the one array in
        this class that scales with every grid at once.

        The τ-free block (_stateApproxSI) is evaluated once per distinct (s_t,ι_t) pair, not once per
        triple, and the chunk loop then only pays for Θ_h/Θ_s/s0_s. Both hot callers hand this method a
        (τ,s) CARTESIAN PRODUCT, so s repeats: report_t passes P=|𝒮|·|𝒮_0|·|𝒮'| = 108,000 pairs holding
        just |𝒮'| = 120 distinct s, i.e. 3,600 rows of the block against 3.2M triples. Two thirds of the
        recursion's runtime was that redundancy. np.unique groups on exact equality, which is what the
        callers produce (np.tile of one grid) -- an inexact grouping would be a silent approximation, so
        do not soften it to a tolerance. """
        P, M = len(τ), len(ιCandGrid)
        sU, inv = np.unique(s, return_inverse = True)
        blk = self._stateApproxSI(np.repeat(sU, M), np.tile(ιCandGrid, len(sU)), t, θ1, solp)
        base = inv.reshape(-1)*M                             # first row of each pair's ι-block
        roots, counts = np.empty(P), np.zeros(P, dtype = int)
        step = max(1, chunk // M)
        for a in range(0, P, step):
            b = min(a + step, P)
            τc = np.repeat(τ[a:b], M)
            ιc = np.tile(ιCandGrid, b - a)
            idx = (base[a:b, None] + np.arange(M)[None, :]).reshape(-1)
            τ1, Γs, B01 = blk['τ1'][idx], blk['Γs'][idx], blk['B01'][idx]
            Θs = self.BG.Θs(self.BG.Θh(τc, τ1, θ1, Γs, t), Γs, t)
            resid = (self.BG.s0_s(B01, Θs, τ1, ε1, t) - ιc).reshape(b - a, M).T
            r = roots1d.allRoots(ιCandGrid, resid, kind = 'any')
            r = r[:, None] if r.ndim == 1 else r
            roots[a:b] = r[0] if r.shape[0] else np.nan
            counts[a:b] = (~np.isnan(r)).sum(axis = 0)
        return roots, counts

    def _rootS(self, Θs, sCandGrid, s_, t):
        """ Docs eq:stateResidual:s, solved for s_t -- one column per (τ_t, s_{t-1}) pair. Θs: (M_s', N),
        Θ_{s,t} at each candidate s_t (rows) for each column's own τ_t; s_: (N,) the predetermined state of
        each column. s_{t-1} enters ONLY through the explicit factor here, which is why one Θ_s evaluation
        serves every state. Returns ((N,) roots, (N,) counts); NaN = feasibility condition 2. """
        ν, σ = self.BG.get('ν', t), self.BG.power_s(t)
        r = roots1d.allRoots(sCandGrid, Θs * ((s_/ν)**σ)[None, :] - sCandGrid[:, None], kind = 'any')
        r = r[:, None] if r.ndim == 1 else r
        n = (~np.isnan(r)).sum(axis = 0)
        return (r[0] if r.shape[0] else np.full(len(s_), np.nan)), n

    def solveStateApprox_t(self, τGrid, sGrid, sCandGrid, ιCandGrid, t, θ1, ε1, solp):
        """ Step 1 of docs alg:CRRA:grid, in the order the unnesting forces:
          (a) ι_t(τ_t,s_t) on 𝒯×𝒮' -- neither predetermined state involved;
          (b) Θ_{s,t}(τ_t,s_t) at that ι_t, then the s_t root along 𝒮' broadcast over every s_{t-1}∈𝒮;
          (c) ι_t(τ_t,s_{t-1}) by composition -- re-solved at the located s_t rather than interpolated off
              (a)'s grid, since s_t generally falls between nodes of 𝒮'.
        Returns (s_t, ι_t, nRootsS, nRootsι), each (M, M_s). This is the only step that touches 𝒮' or
        𝒮_0', and the only one that calls the continuation interpolants. """
        gc = CartesianGrid(τ = τGrid, s = sCandGrid)
        ιc, _ = self._iotaOfTauS(gc.flat['τ'], gc.flat['s'], t, θ1, ε1, solp, ιCandGrid)
        Θs = gc.reshape(self.stateApprox_t(gc.flat['τ'], gc.flat['s'], ιc, t, θ1, solp)['Θs'])  # (M, M_s')

        nT, nS, nC = len(τGrid), len(sGrid), len(sCandGrid)
        sSol, nS_ = self._rootS(np.repeat(Θs.T, nS, axis = 1), sCandGrid, np.tile(sGrid, nT), t)
        sSol = sSol.reshape(nT, nS)
        ιSol, nι = self._iotaOfTauS(np.repeat(τGrid, nS), sSol.reshape(-1), t, θ1, ε1, solp, ιCandGrid)
        return sSol, ιSol.reshape(nT, nS), nS_.reshape(nT, nS), nι.reshape(nT, nS)

    def stateGrid_t(self, τ, s, ι, s_, t, tLag, θ, θ1, ε1, solp):
        """ Step 2 of docs alg:CRRA:grid: every object the t<T first order condition needs, given the
        already-resolved (s_t, ι_t). Flat over (τ_t, s_{t-1}) points. The t/tLag split is the terminal
        period's. ĉ_1 is carried as its (1-1/ρ) power and its log, never as a level (base.py's
        hatc1iPow/lnhatc1i and their informal twins -- the literal level overflows as ρ→1). """
        BG = self.BG
        d = self.stateApprox_t(τ, s, ι, t, θ1, solp)
        d['τ'], d['s'], d['ι'], d['s_'] = τ, s, ι, s_
        d['h'] = BG.h(d['Θh'], s_, t)
        d['B'] = BG.B(s_, d['h'], tLag)                      # B_t^i, generation old at t
        d['Γs_'] = BG.Γs(d['B'], τ, θ, tLag)
        d['si_s_'] = BG.si_s(d['B'], τ, θ, d['Γs_'], tLag)
        d['hatc1iPow'] = BG.hatc1iPow(d['h'], d['B1'], d['τ1'], θ1, d['Γs'], t)
        d['lnhatc1i'] = BG.lnhatc1i(d['h'], d['B1'], d['τ1'], θ1, d['Γs'], t)
        d['hatc10Pow'] = BG.hatc10Pow(s_, s, d['B01'], d['τ1'], ε1, t)
        d['lnhatc10'] = BG.lnhatc10(s_, s, d['B01'], d['τ1'], ε1, t)
        d['c2i'] = BG.c2i(d['h'], s_, τ, θ, d['si_s_'], t)
        return d

    def zbar_t(self, d, g, θ, t, s = 0.0):
        """ Step 3 of docs alg:CRRA:grid: the three (τ_t, s_{t-1}) terms of z_t. g: the CartesianGrid the
        dict's flat arrays live on, with τ as its first axis -- the numerical derivatives run along τ
        *within each s_{t-1}*, so flat vectors are viewed as (M, M_s, ...) before differentiating and
        flattened back after.

        Three derivatives are numerical (dln h_t, dln ĉ_{1,t}^i, dln ĉ_{1,t}^0), each composing two
        interpolated surfaces; the two old-generation log-derivatives are closed form -- mandatorily for
        dv2i (base.py's dlnc2i_dτ), by choice for dv20, which _zStateCRRA supplies. Infeasible cells stay
        NaN throughout. """
        BG, τGrid = self.BG, g.values('τ')
        p = 1 - 1/BG.get('ρ', t)
        grad = lambda y: self._gradProfile(τGrid, g.reshape(y), s).reshape(np.shape(y))
        dlnh = grad(np.log(d['h']))
        d['dlnh'] = dlnh                                     # _zStateCRRA needs it too
        dv1i = d['hatc1iPow'] * grad(d['lnhatc1i'])          # already a log; differentiate it directly
        dv10 = d['hatc10Pow'] * grad(d['lnhatc10'])
        dv2i = d['c2i']**p * BG.dlnc2i_dτ(dlnh, d['τ'], θ, d['si_s_'], t)
        return BG.FOC(dv1i, dv10, dv2i, np.zeros_like(d['τ']), t)

    def solveBackward_t(self, solp, t, tLag, θ, θ1, ε, ε1, sGrid, ιGrid, sCandGrid, ιCandGrid,
                        tol = 0.0, sGrad = 0.0, smooth = 1e-5, minFeasible = 2):
        """ One period of the backward recursion (steps 1-4 of docs alg:CRRA:grid), returning the same kind
        of dict as solveTerminal. The feasibility mask is 2-dimensional -- conditions 1-3 all live on
        𝒯×𝒮 and none depends on ι_{t-1} -- so the selection step is not repeated per ι-node with a
        different feasible sub-grid each time. """
        self._requireCRRA(t)
        τGrid = self.GS['PEE']['solGrids']['τ']
        g = CartesianGrid(τ = τGrid, s_ = sGrid)
        with self.BG.cacheParams():
            sSol, ιSol, nRootsS, nRootsι = self.solveStateApprox_t(τGrid, sGrid, sCandGrid, ιCandGrid,
                                                                   t, θ1, ε1, solp)
            d = self.stateGrid_t(g.flat['τ'], sSol.reshape(-1), ιSol.reshape(-1), g.flat['s_'],
                                 t, tLag, θ, θ1, ε1, solp)
            feasible = g.reshape(self._positiveLevels(d)) & ~np.isnan(sSol) & ~np.isnan(ιSol)
            if feasible.sum(axis = 0).min() < minFeasible:
                raise RuntimeError(f"t={t}: only {int(feasible.sum(axis = 0).min())} of {τGrid.size} nodes "
                                   f"of 𝒯 are feasible at some s_{{t-1}} (need {minFeasible}). Widen 𝒮'/𝒮_0' "
                                   "or narrow 𝒯 -- states leaving the grid are reported, never clipped.")
            zbar = np.where(feasible.reshape(-1), self.zbar_t(d, g, θ, t, s = sGrad), np.nan)
            z = self._zStateCRRA(zbar, d, ε, ιGrid, t, g)
            g3 = CartesianGrid(τ = τGrid, s_ = sGrid, ι_ = ιGrid)
            sel = roots1d.selectMaxND(g3, z.reshape(-1), 'τ', tol = tol)
            τ = self._smooth2D(sel['x'], sGrid, ιGrid, smooth)
            report = self.report_t(sGrid, ιGrid, τ, sCandGrid, ιCandGrid, t, tLag, θ, θ1, ε1, solp)
        report['z'], report['nMax'], report['atBound'] = z, sel['nMax'], sel['atBound']
        report['feasible'], report['nRootsS'], report['nRootsι'] = feasible, nRootsS, nRootsι
        report['sOfτ'], report['ιOfτ'] = sSol, ιSol
        return report

    def _smooth2D(self, τ, sGrid, ιGrid, smooth):
        """ Docs §PEE "Numerical stability": a light smoothing of the selected τ_t(s_{t-1},ι_{t-1}) before
        interpolation, which matters more here than in the log case because each of the next period's
        numerical derivatives composes TWO interpolated surfaces. Applied separably, along s and then
        along ln ι -- log because 𝒮_0 is geometrically spaced while 𝒮 is not. NaNs are held out of the fit
        and restored after; pass smooth=0 to disable.

        The result is clipped back into [l,u]. Smoothing is a denoise, not a re-optimisation, and a spline
        through a profile that is flat at a corner over part of the grid undershoots it: without the clip
        the reported τ_t goes slightly negative wherever many states select the lower corner. """
        if not smooth:
            return τ
        out = np.array(τ, dtype = float)
        ok = ~np.isnan(out)
        settings = self.GS['PEE']['gridSettings']
        for axis, x in ((0, sGrid), (1, np.log(ιGrid))):
            y = np.moveaxis(out, axis, 0)
            sm = griddedSmooth1D(x, np.where(np.moveaxis(ok, axis, 0), y, np.nan), s = smooth,
                                 knots = settings['smoothKnots'])
            out = np.moveaxis(np.where(np.moveaxis(ok, axis, 0), sm, np.nan), 0, axis)
        return np.clip(out, settings['l'], settings['u'])

    def report_t(self, sGrid, ιGrid, τ, sCandGrid, ιCandGrid, t, tLag, θ, θ1, ε1, solp):
        """ Step 4 of docs alg:CRRA:grid: re-solve step 1 at the SELECTED τ_t(s_{t-1},ι_{t-1}) (which falls
        between nodes of 𝒯, so its (s_t,ι_t) must be re-solved rather than read off the grid), expand into
        the full solution dict, and build the interpolants period t-1 will call. ΓsPolicy is the one
        exception: t-1 never calls it, it exists so the path solve can warm-start the CRRA equilibrium
        system at the simulated (Γ_{s,t},h_t,s_t) (docs §PEEpath).

        Also records the reachable set (docs eq:reachable): the (s_t,ι_t) pairs this period can actually
        hand to t+1. 'inGrid' flags whether it stays inside 𝒮×𝒮_0. A pair outside means the grids are too
        narrow for the dynamics being asked of them and should be widened -- never clipped -- and the path
        solve is what has to check containment before trusting an interpolated policy. """
        shape = (len(sGrid), len(ιGrid))
        s_flat = np.repeat(sGrid, len(ιGrid))                # C-order over (s_, ι_), matching τ
        τflat = τ.reshape(-1)
        nC = len(sCandGrid)
        ιc, _ = self._iotaOfTauS(np.repeat(τflat, nC), np.tile(sCandGrid, len(τflat)),
                                 t, θ1, ε1, solp, ιCandGrid)
        Θs = self.stateApprox_t(np.repeat(τflat, nC), np.tile(sCandGrid, len(τflat)), ιc,
                                t, θ1, solp)['Θs'].reshape(-1, nC).T
        s, nRootsS = self._rootS(Θs, sCandGrid, s_flat, t)
        ι, nRootsι = self._iotaOfTauS(τflat, s, t, θ1, ε1, solp, ιCandGrid)

        d = self.stateGrid_t(τflat, s, ι, s_flat, t, tLag, θ, θ1, ε1, solp)
        d = {k: (v.reshape(shape + v.shape[1:]) if np.ndim(v) else v) for k, v in d.items()}
        ok = ~np.isnan(τ) & ~np.isnan(d['s']) & ~np.isnan(d['ι'])
        d['s_'], d['ι_'] = sGrid, ιGrid
        d['sCand'], d['ιCand'] = sCandGrid, ιCandGrid   # 𝒮'/𝒮_0', for the path solve's own re-solve
        d['reachable'] = {'s': d['s'], 'ι': d['ι'],
                          'inGrid': ok & (d['s'] >= sGrid[0]) & (d['s'] <= sGrid[-1])
                                       & (d['ι'] >= ιGrid[0]) & (d['ι'] <= ιGrid[-1])}
        d['outOfGrid'] = ok & ~d['reachable']['inGrid']
        d['nRootsSolS'], d['nRootsSolι'] = nRootsS.reshape(shape), nRootsι.reshape(shape)
        kind = self.GS['PEE']['gridSettings']['interpKind']
        for name, v in (('τPolicy', τ), ('hPolicy', d['h']), ('sPolicy', d['s']), ('ιPolicy', d['ι']),
                        ('ΓsPolicy', d['Γs'])):
            d[name] = griddedInterp2D(sGrid, ιGrid, v, kind)
        d['τ'] = pd.DataFrame(τ, index = sGrid, columns = ιGrid)
        d['h'] = pd.DataFrame(d['h'], index = sGrid, columns = ιGrid)
        d['s'] = pd.DataFrame(d['s'], index = sGrid, columns = ιGrid)
        d['ι'] = pd.DataFrame(d['ι'], index = sGrid, columns = ιGrid)
        return d

    def solveBackward(self, θ, ε, sGrid = None, ιGrid = None, sCandGrid = None, ιCandGrid = None,
                      tol = 0.0, sGrad = 0.0, smooth = 1e-5, minFeasible = 2):
        """ The full CRRA politico-economic equilibrium: the sequence of policy functions
        τ_t(s_{t-1}, ι_{t-1}), solved backwards from the terminal period (docs alg:CRRA:grid). Returns
        {t: solution dict}, one entry per db['t'].

        The four grids are resolved once here and pinned across periods (adjacent periods' interpolants
        must live on a common state grid): 𝒮/𝒮_0 default to the stateGrids slots else defaultSGrid/
        defaultIotaGrid at the terminal period's (θ,ε); 𝒮' defaults to the solGrids slot else
        defaultSCandGrid (finer than 𝒮), while 𝒮_0' defaults to 𝒮_0 itself -- see defaultSCandGrid for
        why the two candidate grids are treated asymmetrically. Requires ρ != 1, checked up front so it
        fails before doing the terminal period's work. """
        tIdx = self.db['t']
        posT = tIdx.get_loc(tIdx[-1])
        self._requireCRRA(tIdx[0])
        sGrid = self._sGrid(sGrid, θ[posT], tIdx[-1])
        ιGrid = self._ιGrid(ιGrid, θ[posT], ε[posT], tIdx[-1])
        sCandGrid = self.GS['PEE']['solGrids']['s'] if sCandGrid is None else sCandGrid
        ιCandGrid = self.GS['PEE']['solGrids']['ι'] if ιCandGrid is None else ιCandGrid
        sCandGrid = self.defaultSCandGrid(sGrid) if sCandGrid is None else np.asarray(sCandGrid)
        ιCandGrid = ιGrid if ιCandGrid is None else np.asarray(ιCandGrid)

        sols = {tIdx[-1]: self.solveTerminal(θ[posT], ε[posT], t = tIdx[-1], tol = tol,
                                             ιGrid = ιGrid, sGrid = sGrid)}
        for t in tIdx[-2::-1]:
            pos = tIdx.get_loc(t)
            tLag = tIdx[pos - 1] if pos > 0 else self.B.tFirst
            sols[t] = self.solveBackward_t(sols[tIdx[pos + 1]], t, tLag, θ[pos], θ[pos + 1],
                                           ε[pos], ε[pos + 1], sGrid, ιGrid, sCandGrid, ιCandGrid,
                                           tol = tol, sGrad = sGrad, smooth = smooth,
                                           minFeasible = minFeasible)
        return sols

    #######################################################################
    ##########   Forward simulation (docs eq:forwardSim)               #####
    #######################################################################
    def _reachBox(self, sol):
        """ The bounding box of the reachable set 𝒫_t (docs eq:reachable) recorded by report_t, over the
        nodes whose image stayed inside 𝒮×𝒮_0. Returns (sLo, sHi, ιLo, ιHi).

        A box rather than 𝒫_t itself, and the asymmetry is the point: 𝒫_t is recorded as the image of the
        state grid, a scatter of pairs, so the box CONTAINS it. A point outside the box is therefore
        genuinely outside 𝒫_t (never a false alarm); a point inside is inconclusive. That is the direction
        a containment check has to be conservative in. """
        R = sol['reachable']
        ok = R['inGrid']
        if not ok.any():
            return (np.nan,)*4
        return (R['s'][ok].min(), R['s'][ok].max(), R['ι'][ok].min(), R['ι'][ok].max())

    def approximatePEE(self, sols, θ, ε, s0, ι0, exact = True, strict = True):
        """ Walk the backward-solved policy functions forward from the initial state pair (s_0, ι_0)
        (docs eq:forwardSim), the CRRA counterpart of LOG.approximatePEE.

        exact: take the transitions as the docs write them -- s_t(τ_t,s_{t-1}) then ι_t(τ_t,s_t),
        re-solved at the walked τ_t in the order the unnesting forces -- rather than off the reported
        sPolicy/ιPolicy. See LOG.approximatePEE for why. Γ_{s,t}/h_t are then read off the same re-solve
        rather than their own interpolants, so the warm start is consistent with the states it accompanies.
        At exact=False both transitions are read at the ENTERING pair (s_{t-1},ι_{t-1}): sPolicy and
        ιPolicy are functions of the same state, so s_t must not be substituted into ιPolicy before ι_t is
        taken off it.

        sols: solveBackward's {t: report}. θ, ε: full length-T paths. s0/ι0: the states entering
        db['t'][0], normally model.py's initialStatePEE.

        Returns {'τ': pd.Series over db['t'], 'Γs','h','s','ι': (T-1,) over db['txE'], 's_','ι_': (T,)
        entering states, 'inGrid'/'inReach'/'atBound': (T,) diagnostics}. Γs/h/s are model.py's warm start
        for the exact CRRA equilibrium system, never a solution in themselves.

        strict: raise rather than return a path that (i) leaves 𝒮×𝒮_0, where the 2-D interpolants
        extrapolate, (ii) leaves the previous period's reachable set, or (iii) goes non-finite. The last
        is not hypothetical and has no counterpart in the log case: a policy surface carries NaN at its
        infeasible nodes, and griddedInterp2D cannot drop them the way the 1-D interpolants filter to
        their feasible nodes -- so a path can go non-finite without ever leaving the rectangle. """
        tIdx = self.db['t']
        settings = self.GS['PEE']['gridSettings']
        l, u = settings['l'], settings['u']
        τ = np.empty(self.T)
        s_, ι_ = np.empty(self.T), np.empty(self.T)
        Γs, h, s, ι = (np.empty(self.T - 1) for _ in range(4))
        sState, ιState = float(s0), float(ι0)
        for pos, t in enumerate(tIdx):
            d = sols[t]
            s_[pos], ι_[pos] = sState, ιState
            τ[pos] = np.clip(float(d['τPolicy'](sState, ιState)), l, u)
            if pos < self.T - 1:
                θ1, solp = θ[pos + 1], sols[tIdx[pos + 1]]
                if exact:
                    sSol, ιSol, _, _ = self.solveStateApprox_t(np.array([τ[pos]]), np.array([sState]),
                                                               d['sCand'], d['ιCand'], t, θ1,
                                                               ε[pos + 1], solp)
                    s[pos], ι[pos] = float(sSol[0, 0]), float(ιSol[0, 0])
                    dd = self.stateApprox_t(τ[pos], s[pos], ι[pos], t, θ1, solp)
                    Γs[pos], h[pos] = float(dd['Γs']), float(self.BG.h(dd['Θh'], sState, t))
                else:
                    Γs[pos] = float(d['ΓsPolicy'](sState, ιState))
                    h[pos] = float(d['hPolicy'](sState, ιState))
                    s[pos], ι[pos] = float(d['sPolicy'](sState, ιState)), float(d['ιPolicy'](sState, ιState))
                sState, ιState = s[pos], ι[pos]
        sGrid, ιGrid = sols[tIdx[0]]['s_'], sols[tIdx[0]]['ι_']
        inGrid = ((s_ >= sGrid[0]) & (s_ <= sGrid[-1]) & (ι_ >= ιGrid[0]) & (ι_ <= ιGrid[-1])
                  & np.isfinite(s_) & np.isfinite(ι_) & np.isfinite(τ))
        inReach = np.ones(self.T, dtype = bool)   # t=0's state comes from the steady-state assumption,
        for pos in range(1, self.T):              # not from any period's transition -- nothing to check
            lo_s, hi_s, lo_ι, hi_ι = self._reachBox(sols[tIdx[pos - 1]])
            inReach[pos] = (lo_s <= s_[pos] <= hi_s) and (lo_ι <= ι_[pos] <= hi_ι)
        out = {'τ': pd.Series(τ, index = tIdx), 'Γs': Γs, 'h': h, 's': s, 'ι': ι, 's_': s_, 'ι_': ι_,
               'inGrid': inGrid, 'inReach': inReach, 'atBound': np.isclose(τ, l) | np.isclose(τ, u)}
        if strict and not (inGrid & inReach).all():
            bad = np.flatnonzero(~(inGrid & inReach))
            raise RuntimeError(f"approximatePEE: the state entering t={list(tIdx[bad])} is outside "
                               f"{'𝒮×𝒮_0' if not inGrid.all() else 'the reachable set 𝒫_{t-1}'} "
                               f"(s_={np.array2string(s_[bad], precision = 3)}, "
                               f"ι_={np.array2string(ι_[bad], precision = 3)}; "
                               f"𝒮=[{sGrid[0]:.3e}, {sGrid[-1]:.3e}], 𝒮_0=[{ιGrid[0]:.3e}, {ιGrid[-1]:.3e}]). "
                               "The path would be driven by extrapolated policy: widen the grids, or check "
                               "the initial state. Pass strict=False to return it flagged instead.")
        return out