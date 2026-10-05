r""" The first-order-condition layer for the CRRA leaded design (writing/US/num_esc.tex, alg esc:crra2Dfoc),
the documented alternative to LeadedCRRA2D's root layer (alg esc:crra2D, designRule = 'root'), and the
checks both layers are measured with:

  LeadedCRRA2DFOC    alg esc:crra2Dfoc. Candidates from the design condition eq:esc:designFOC (the
                     crossings of z^θ and the two corners), each tested and ranked on its own frozen
                     profile eq:esc:designProfile through roots1d.selectMaxFrozen. Overrides _choose only:
                     step 1 (_periodCore), the hand-back (_handBack) and the frozen tax pass
                     (policyESC.frozenTaxPass) are LeadedCRRA2D's; pinned periods and states with no
                     equilibrium (fallbackθ) take the legacy layer's answer (_chooseLegacy).
  consistentTax      the legacy layer's tax rule at every design.
  resolveAt          the state re-solved off the grid and W_t assembled at a given a: the check of a grid
                     reading of V.
  deviationCheck     the one-shot deviation check (eq:esc:stateEq:design) at a selected (θ̂', a*).
  designSlopeAt      the FOC layer's fixed-knot design derivative at an arbitrary θ'.

The inherited distribution (aOf, sharesFrom, eq:esc:aDef) and the frozen tax pass are policyESC's.
Shapes: the step-1 grid is CartesianGrid(τ, s_, θ1), flat in C-order; per θ_t the layers work on
(ns_, nθ1) arrays (state rows, design columns).
"""
import numpy as np
from scipy import interpolate
from gridsearch import roots1d, griddedGradient1D
from gridsearch.interp import _fixedKnots
from policyESC import LeadedCRRA2D, aOf, sharesFrom, frozenTaxPass, _alongτ, _interpRows


# ---------------------------------------------------------------------------------------------- the tax rule
def consistentTax(E, core, θ1Grid):
    """ The tax rule at every (θ_t, s_, θ1): LeadedCRRA2D._chooseLegacy's step 3 (the selection rule of
    num_robustroot.tex at frozen shares). Returns {'τStar', 'atBoundτ', 'nEqτ', 'nCandτ', 'fallbackτ'},
    each (nθ, ns_, nθ1). """
    g, d, parts, t, tLag = core['g'], core['d'], core['parts'], core['t'], core['tLag']
    shape = (E.nθ, len(core['sGrid']), len(θ1Grid))
    out = {'τStar': np.empty(shape), 'atBoundτ': np.zeros(shape, dtype = bool),
           'nEqτ': np.zeros(shape, dtype = int), 'nCandτ': np.zeros(shape, dtype = int),
           'fallbackτ': np.zeros(shape, dtype = bool)}
    with E.BG.cacheParams():
        for it, θt in enumerate(E.θGrid):
            frozen = lambda cand, θt = float(θt): E.objectiveFrozen(cand, g, d, parts, θt, t, tLag)
            sel = E._selectND(g, E._zAtθ(d, parts, θt, t, tLag), 'τ', frozen)
            out['τStar'][it], out['atBoundτ'][it] = sel['x'], sel['atBound']
            out['nEqτ'][it], out['nCandτ'][it], out['fallbackτ'][it] = sel['nEq'], sel['nCand'], sel['fallback']
    return out


# ---------------------------------------------------------------------------------------------- checks
def resolveAt(E, core, τ, s_, θt, θ1, a):
    """ The state re-solved at arbitrary flat points (τ, s_, θ1) of the core's period (LeadedCRRA2D._econAt's
    fixed point) and W_t assembled there at the frozen distribution a (eq:esc:stateEq), not at the shares
    consistent with (τ, h_t): the check of a grid reading of V. All arguments broadcast to (N,). Returns
    {'W', 'Wy', 'Wo', 's', 'h', 'B', 'hatc1iPow', 'lnhatc1i', 'nRoots'}. """
    BG = E.BG
    t, tLag, t1, ε, ε1 = core['t'], core['tLag'], core['t1'], core['ε'], core['ε1']
    sCand, sol1 = core['sCand'], core['sol1']
    τF, s_F, θtF, θ1F, aF = (np.ascontiguousarray(v, dtype = float).reshape(-1)
                             for v in np.broadcast_arrays(τ, s_, θt, θ1, a))
    N, nsC = τF.size, len(sCand)
    with BG.cacheParams(), np.errstate(divide = 'ignore', invalid = 'ignore'):
        τR = np.ascontiguousarray(np.broadcast_to(τF, (nsC, N))).reshape(-1)
        θ1R = np.ascontiguousarray(np.broadcast_to(θ1F, (nsC, N))).reshape(-1)
        sR = np.ascontiguousarray(np.broadcast_to(sCand[:, None], (nsC, N))).reshape(-1)
        Θs = E.stateApprox_t(τR, sR, t, θ1R, sol1)['Θs'].reshape(nsC, N)
        sPt, nR = E._rootS(Θs, sCand, s_F, t)
        dd = E._econCore(τF, sPt, s_F, θ1F, t, tLag, t1, ε, ε1, sol1)
        q = float(1 - 1/BG.get('ρ', t))
        old, young = E.weights(t)
        c2 = BG.c2i(dd['h'], s_F, τF, θtF, sharesFrom(BG, aF, tLag), t)
        Wy = (young*dd['hatc1iPow']).sum(axis = -1)/q
        Wo = (old*c2**q).sum(axis = -1)/q
    return {'W': Wy + Wo, 'Wy': Wy, 'Wo': Wo, 's': sPt, 'h': dd['h'], 'B': dd['B'],
            'hatc1iPow': dd['hatc1iPow'], 'lnhatc1i': dd['lnhatc1i'], 'nRoots': nR}


def deviationCheck(E, core, θt, a, θSel):
    """ The one-shot deviation check at a state's selected (θ̂', a*) (eq:esc:stateEq:design): with a* held
    fixed, the largest gain V_t(θ'; a*) - V_t(θ̂'; a*) over the nodes of the core's θ1 grid, from one
    frozen pass. a, θSel: (ns_,). V_t(θ̂'; a*) is read by the quadratic through the three nodes nearest
    θ̂' (roots1d._quadAt). Returns {'gain', 'V', 'Vmax', 'rel' = gain/|V|, 'Vθ' (ns_, nθ1)}. """
    x = np.asarray(core['θ1Grid'], dtype = float)
    fp = frozenTaxPass(E, core, θt, np.where(np.isfinite(a), a, 1.))
    Vθ = np.where(np.isfinite(np.asarray(a))[:, None], fp['V'], np.nan)
    Vs = roots1d._quadAt(x, Vθ.T[None], np.asarray(θSel, dtype = float)[None])[0]
    with np.errstate(invalid = 'ignore'):
        Vmax = np.nanmax(np.where(np.isfinite(Vθ), Vθ, -np.inf), axis = 1)
        gain = Vmax - Vs
        return {'gain': gain, 'V': Vs, 'Vmax': Vmax, 'rel': gain/np.abs(Vs), 'Vθ': Vθ}


def designSlopeAt(E, core, iτ, js, θq, knots = None):
    """ The fixed-knot spline derivative along θ1 (LeadedCRRA2DFOC's, gridsearch.interp._fixedKnots every
    `knots` nodes, cubic) of ln hatc1i (ni,) and of ln h_t at the step-1 column (τ node iτ, s_ node js),
    evaluated at an arbitrary θq. Returns (dlnhatc1i (ni,), dlnh). knots None: the grid's smoothKnots. """
    g, d = core['g'], core['d']
    x = np.asarray(g.values('θ1'), dtype = float)
    knots = E.GS['PEE']['gridSettings']['smoothKnots'] if knots is None else knots

    def slope(col):
        ok = np.isfinite(col)
        sp = interpolate.LSQUnivariateSpline(x[ok], col[ok], _fixedKnots(x[ok], 3, knots), k = 3)
        return float(sp.derivative()(θq))
    lnc = g.reshape(d['lnhatc1i'])[iτ, js]                     # (nθ1, ni)
    with np.errstate(divide = 'ignore', invalid = 'ignore'):
        lnh = np.log(g.reshape(d['h'])[iτ, js])                # (nθ1,)
    return np.array([slope(lnc[:, i]) for i in range(lnc.shape[1])]), slope(lnh)


# ---------------------------------------------------------------------------------------------- layer B
class LeadedCRRA2DFOC(LeadedCRRA2D):
    """ alg esc:crra2Dfoc: the design located from its first order condition at a frozen state.

    Once per period: ∂_θ' ln h_t and ∂_θ' ln hatc1i on the step-1 grid by fixed-knot splines along θ1
    (griddedGradient1D, knots = smoothKnotsθ, default the grid's smoothKnots), dv1i_dθ = hatc1iPow·∂ ln
    hatc1i. Per θ_t: the tax rule at every design (consistentTax, the earlier layer's step 3) and the
    consistent a(θ') there; z^θ(θ') of eq:esc:designFOC = Σ young·dv1i_dθ + Σ old·c_2^q·(1-α)·∂ ln h, read
    along τ at τ*(θ'), c_2 at D(a(θ')); roots1d.selectMaxFrozen on θ1 with, per candidate, a_c = a(θ') at
    the candidate (np.interp along θ1), frozenTaxPass at a_c and the profile eq:esc:designProfile = the
    trapezoid integral of the frozen derivative eq:esc:designEnvelope plus V(first feasible θ'; a_c). The
    tax at the selected design: τ̂(·; a_c*) of that candidate's pass, np.interp along θ1.

    Period-dict entries (nθ, ns_): nCandθ, nEqθ, fallbackθ (none passed: _chooseLegacy's answer), aStar
    (= a_c*), Vstar (its profile value), τChosen (unsmoothed); Vθ (nθ, ns_, nθ1) = V(θ'; a_c*); nPass;
    and the tax rule's entries (τStar3, nEqτ, ...), which this layer runs everywhere. """

    def __init__(self, m, nθ = 13, nθCand = 21, smoothKnotsθ = None, rtol = 1e-9, **kwargs):
        super().__init__(m, nθ = nθ, nθCand = nθCand, **kwargs)
        self.smoothKnotsθ, self.rtol = smoothKnotsθ, float(rtol)

    def _designDerivatives(self, core):
        """ Step 1's extra derivatives along θ1, flat over the grid: {'dlnh' (N,), 'dv1i_dθ' (N, ni),
        'dWy' (N,) = Σ young·dv1i_dθ}. Cached on core per knot setting. """
        knots = (self.GS['PEE']['gridSettings']['smoothKnots'] if self.smoothKnotsθ is None
                 else self.smoothKnotsθ)
        key = ('_dθ', knots)
        if key in core:
            return core[key]
        g, d = core['g'], core['d']
        x = np.asarray(g.values('θ1'), dtype = float)

        def dθ(Y):
            A = np.moveaxis(g.reshape(Y), 2, 0)
            return np.moveaxis(griddedGradient1D(x, A, knots = knots), 0, 2).reshape(np.shape(Y))
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            dlnh = dθ(np.log(d['h']))
            dv1i = d['hatc1iPow']*dθ(d['lnhatc1i'])
        young = self.weights(core['t'])[1]
        core[key] = {'dlnh': dlnh, 'dv1i_dθ': dv1i, 'dWy': (young*dv1i).sum(axis = -1)}
        return core[key]

    def _choose(self, core, θ1Grid, choose):
        if not choose or len(θ1Grid) < 4:
            return self._chooseLegacy(core, θ1Grid, choose)
        BG, d, g = self.BG, core['d'], core['g']
        t, tLag = core['t'], core['tLag']
        τGrid = g.values('τ')
        x = np.asarray(θ1Grid, dtype = float)
        nτ, ns_, nθ1 = g.shape
        nθ, C = self.nθ, ns_*nθ1
        s_C = np.repeat(core['sGrid'], nθ1)
        q = float(1 - 1/BG.get('ρ', t))
        α = float(BG.get('α', t))
        old = self.weights(t)[0]
        tax = consistentTax(self, core, θ1Grid)
        der = self._designDerivatives(core)
        dWyG, dlnhG = der['dWy'].reshape(nτ, C), der['dlnh'].reshape(nτ, C)
        θNext, τSel, aStar, Vstar = (np.full((nθ, ns_), np.nan) for _ in range(4))
        atBoundθ = np.zeros((nθ, ns_), dtype = bool)
        nCand, nEq = np.zeros((nθ, ns_), dtype = int), np.zeros((nθ, ns_), dtype = int)
        fallback = np.zeros((nθ, ns_), dtype = bool)
        Vθ = np.full((nθ, ns_, nθ1), np.nan)
        nPass = 0
        for it, θt in enumerate(self.θGrid):
            θt = float(θt)
            τs = tax['τStar'][it].reshape(C)
            with BG.cacheParams(), np.errstate(divide = 'ignore', invalid = 'ignore'):
                hs = _alongτ(τGrid, d['h'].reshape(nτ, C), τs)
                aθ = aOf(BG, BG.B(s_C, hs, tLag), τs, θt, tLag)                      # (C,)
                c2 = BG.c2i(hs, s_C, τs, θt, sharesFrom(BG, aθ, tLag), t)
                zθ = (_alongτ(τGrid, dWyG, τs)
                      + (old*c2**q).sum(axis = -1)*(1 - α)*_alongτ(τGrid, dlnhG, τs))
            aθ, zθ = aθ.reshape(ns_, nθ1), zθ.reshape(ns_, nθ1)
            store = {}

            def frozen(cand, θt = θt, aθ = aθ, store = store):
                nonlocal nPass
                K = cand.shape[0]
                store['cand'] = cand.copy()
                W = np.full((K, nθ1, ns_), np.nan)
                for k in range(K):
                    ac = _interpRows(x, aθ, cand[k])
                    ok = np.isfinite(ac)
                    if not ok.any():
                        continue
                    acF = np.where(ok, ac, ac[ok].mean())
                    fp = frozenTaxPass(self, core, θt, acF, fields = {'dWy': der['dWy'], 'dlnh': der['dlnh']})
                    nPass += 1
                    with BG.cacheParams(), np.errstate(divide = 'ignore', invalid = 'ignore'):
                        c2k = BG.c2i(fp['h'].reshape(C), s_C, fp['τ'].reshape(C), θt,
                                     sharesFrom(BG, np.repeat(acF, nθ1), tLag), t)
                        integ = (fp['dWy'] + ((old*c2k**q).sum(axis = -1)*(1 - α)).reshape(ns_, nθ1)
                                 * fp['dlnh']).T                                      # (nθ1, ns_)
                    fin = np.isfinite(integ)
                    first = np.where(fin.any(axis = 0), fin.argmax(axis = 0), 0)
                    level = fp['V'][np.arange(ns_), first]
                    Wk = roots1d.cumtrapzColumns(x, integ) + level[None, :]
                    Wk[:, ~ok] = np.nan
                    W[k] = Wk
                    store[k] = (fp, ac)
                return W

            sel = roots1d.selectMaxFrozen(x, zθ.T, frozen, rtol = self.rtol)
            nCand[it], nEq[it], fallback[it] = sel['nCand'], sel['nEq'], sel['fallback']
            atBoundθ[it], Vstar[it] = sel['atBound'], sel['W']
            cand = store.get('cand')
            for j in np.flatnonzero(sel['nEq'] > 0):
                k = int(np.flatnonzero(cand[:, j] == sel['x'][j])[0])
                fp, ac = store[k]
                θNext[it, j] = sel['x'][j]
                τSel[it, j] = np.interp(sel['x'][j], x, fp['τ'][j])
                aStar[it, j], Vθ[it, j] = ac[j], fp['V'][j]
        legacy = None
        if fallback.any():
            legacy = self._chooseLegacy(core, θ1Grid, choose)
            θNext[fallback], τSel[fallback] = legacy['θNext'][fallback], legacy['τSel'][fallback]
            atBoundθ[fallback] = legacy['atBoundθ'][fallback]
        return tax | {'W': legacy['W'] if legacy is not None else np.full((nθ, ns_, nθ1), np.nan),
                      'θNext': θNext, 'atBoundθ': atBoundθ, 'τSel': τSel, 'τChosen': τSel.copy(),
                      'nCandθ': nCand, 'nEqθ': nEq, 'fallbackθ': fallback, 'aStar': aStar,
                      'Vstar': Vstar, 'Vθ': Vθ, 'nPass': nPass}
