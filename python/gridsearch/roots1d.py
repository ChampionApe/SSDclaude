""" One-dimensional root and extremum detection on a grid (writing/*_docs.tex, alg:gridsearch).

Generic and model-agnostic. Given a sorted grid x (M,) and function values f (M,) or (M,N) -- N
independent functions sampled on the *same* grid -- locate where the piecewise-linear interpolant of f
crosses zero. Two families, differing only in which crossings count:

  kind='any'   f[i]*f[i+1] < 0          a genuine root (either direction)
  kind='down'  f[i] > 0 > f[i+1]        a downward crossing = interior *maximum* of ∫f
  kind='up'    f[i] < 0 < f[i+1]        an upward crossing  = interior *minimum* of ∫f

Use the 'any' family (allRoots/firstRoot) for genuine root problems, where any crossing is a solution.
Use the 'down' family (allMax/firstMax) when f is the derivative of an objective and only maxima are
admissible -- e.g. the political first-order condition z_t, where an upward crossing is a local *minimum*
of the political objective and must not be returned as a solution.

Exact zeros. `f[i]*f[i+1] < 0` cannot see a root that lands exactly *on* a grid node, and such nodes are
not the measure-zero curiosity they first appear to be: under the bounded-root reparameterization
(robustRoot, eq:root) a corner solution is encoded as an *identically* zero value at an outer node
(h = z + |z| = 0 whenever z < 0). Zeros are therefore always handled here, at any tol, via the sign-run
rule: nodes with |f| <= tol are skipped when pairing signs, so a zero (or a run of zeros) flanked by
opposite nonzero signs registers as one crossing, located at the midpoint of the run. tol defaults to 0
so that only genuinely exact zeros trigger it -- a nonzero default would report spurious roots wherever f
merely grazes zero without crossing, which for maximum-detection is a real error rather than a rounding
detail. Pass tol > 0 deliberately when near-zeros should count.

Selecting among several crossings. Solving f = 0 is only a *necessary* condition for a maximum: with
several downward crossings the first one located need not be the global one. objectiveProfile/selectMax
resolve this without any additional evaluations of f -- see selectMax's docstring.
"""
import numpy as np

_KINDS = ('any', 'down', 'up')


def _asMatrix(f):
    """ Promote (M,) -> (M,1) so every routine below can assume 2D. Returns (matrix, wasFlat) so the
    caller can squeeze the result back to the caller's own dimensionality. """
    f = np.asarray(f, dtype = float)
    if f.ndim == 1:
        return f[:, None], True
    elif f.ndim == 2:
        return f, False
    raise ValueError(f"f must be 1- or 2-dimensional, got shape {f.shape}.")


def _checkInputs(x, f, kind = 'any'):
    """ Shared validation: x sorted ascending (the sign-pairing and searchsorted logic below silently
    returns nonsense otherwise, so fail loudly instead), shapes conformable, kind recognised. """
    x = np.asarray(x, dtype = float)
    if x.ndim != 1:
        raise ValueError(f"x must be 1-dimensional, got shape {x.shape}.")
    if x.size < 2:
        raise ValueError(f"x must hold at least 2 nodes, got {x.size}.")
    if not np.all(np.diff(x) > 0):
        raise ValueError("x must be strictly increasing.")
    fm, wasFlat = _asMatrix(f)
    if fm.shape[0] != x.size:
        raise ValueError(f"f's first axis ({fm.shape[0]}) must match x ({x.size}).")
    if kind not in _KINDS:
        raise ValueError(f"kind must be one of {_KINDS}, got {kind!r}.")
    return x, fm, wasFlat


def _columnCrossings(x, fj, kind, tol):
    """ All roots of a single column, ascending in x. Returns a 1d array of locations.

    Reference implementation. `_matrixCrossings` below does the same thing across every column at once and
    is what allRoots actually calls; this one is retained as the oracle the vectorized version is tested
    against (test_roots1d.py), since the two must agree exactly and the column-at-a-time form is the one
    that can be read as a plain statement of the rule.

    Sign pairing skips near-zero nodes (|f| <= tol) rather than testing adjacent nodes directly, which is
    what makes exact zeros and flat zero runs work: consecutive *nonzero* nodes with opposite signs bracket
    exactly one crossing, whether or not zeros sit between them. Where the two bracketing nodes are
    adjacent the crossing is located by linear interpolation (identical to a plain sign-change test); where
    they are not, everything between them is a zero run and the root is reported at its midpoint.

    Zeros at the grid's own first/last node are handled separately, since they have no neighbour on one
    side to bracket them and would otherwise be dropped. This is not an edge case worth skipping: under
    robustRoot's reparameterization a corner solution lands *exactly* on an outer node (h = z + |z| = 0),
    so dropping boundary zeros would silently lose precisely the solutions the extended grid exists to
    catch. Such a root is real regardless of direction; it is classified from the one sign available --
    a lower-boundary zero followed by negative values is a downward crossing, and so on. """
    s = np.sign(fj)
    if tol > 0:
        s = np.where(np.abs(fj) <= tol, 0.0, s)
    nz = np.flatnonzero(s)                              # nodes with a usable (nonzero) sign
    if nz.size == 0:
        return np.empty(0)                              # f vanishes across the whole grid: every node is
                                                        # a root and none is distinguished -- caller's problem

    roots, isDown = [], []

    if nz[0] > 0:                                       # leading zero run, nodes 0 .. nz[0]-1
        roots.append(0.5 * (x[0] + x[nz[0] - 1]))
        isDown.append(s[nz[0]] < 0)                     # 0 -> negative reads as + -> -

    if nz.size > 1:                                     # interior crossings between nonzero-sign nodes
        left, right = nz[:-1], nz[1:]
        sel = s[left] * s[right] < 0
        l, r = left[sel], right[sel]
        if l.size:
            interior = np.empty(l.size)
            adj = (r == l + 1)                          # nothing in between -> ordinary sign change
            la, ra = l[adj], r[adj]
            interior[adj] = x[la] - fj[la] * (x[ra] - x[la]) / (fj[ra] - fj[la])
            lz, rz = l[~adj], r[~adj]                   # zero run occupying nodes lz+1 .. rz-1
            interior[~adj] = 0.5 * (x[lz + 1] + x[rz - 1])
            roots.extend(interior)
            isDown.extend(s[l] > 0)                     # + -> - is a maximum of the antiderivative

    if nz[-1] < x.size - 1:                             # trailing zero run, nodes nz[-1]+1 .. M-1
        roots.append(0.5 * (x[nz[-1] + 1] + x[-1]))
        isDown.append(s[nz[-1]] > 0)                    # positive -> 0 reads as + -> -

    roots, isDown = np.array(roots), np.array(isDown, dtype = bool)
    if kind == 'down':
        roots = roots[isDown]
    elif kind == 'up':
        roots = roots[~isDown]
    return np.sort(roots)


def _matrixCrossings(x, fm, kind, tol):
    """ _columnCrossings applied to every column of fm at once, with no Python-level loop over columns.
    Returns the NaN-padded (Kmax, N) array allRoots documents. Identical results to the per-column
    reference by construction, and checked against it on randomized inputs in test_roots1d.py.

    The one part of the rule that looks inherently sequential is "pair each node with the last *nonzero*
    node before it", since how far back that reaches varies by column and by position. It vectorizes with
    a running maximum: writing each node's own row index where the sign is nonzero and -1 where it is not,
    np.maximum.accumulate along the grid axis carries forward the index of the most recent nonzero node.
    Everything else -- interpolating within a bracketing cell, taking the midpoint of a zero run,
    classifying direction -- is then elementwise.

    Cost. Roughly 4-8x faster than looping _columnCrossings in the range this is built for (M ~ 10^2
    nodes, N ~ 10^2 state combinations). The advantage narrows as M*N grows, because the loop keeps one
    column in cache at a time while this holds several (M,N) temporaries, and the two cross over around
    ~5*10^6 elements. Well past anything a policy grid search here produces, but worth knowing before
    reusing this on a much larger problem. """
    M, N = fm.shape
    s = np.sign(fm)
    if tol > 0:
        s = np.where(np.abs(fm) <= tol, 0.0, s)
    nz = s != 0
    rows = np.broadcast_to(np.arange(M)[:, None], (M, N))

    # prev[k] = index of the last nonzero-sign node at or before row k (-1 before the first one).
    prev = np.maximum.accumulate(np.where(nz, rows, -1), axis = 0)

    # Interior crossings, indexed by their *right* node r: the left bracket l is the last nonzero node
    # strictly before r, and the pair brackets a crossing iff their signs differ.
    l = np.full((M, N), -1)
    l[1:] = prev[:-1]
    sl = np.take_along_axis(s, np.maximum(l, 0), axis = 0)   # gather kept in range; validity is `ok`
    ok = nz & (l >= 0) & (sl * s < 0)
    if kind == 'down':
        ok &= sl > 0                                 # + -> - is a maximum of the antiderivative
    elif kind == 'up':
        ok &= sl < 0

    # Everything from here on runs only where a crossing actually is. Crossings are sparse -- a handful
    # per column against M nodes -- so locating them first and doing the gathers/interpolation on the
    # resulting 1d index set keeps the (M,N)-sized temporaries down to the few needed to build `ok`
    # itself. Computing loc over the full matrix instead is what makes this slower than looping columns
    # once N is large: the arithmetic is elementwise either way, but the memory traffic is not.
    r, c = np.nonzero(ok)
    lr = l[r, c]
    xl, fl = x[lr], fm[lr, c]
    adj = lr == r - 1                                # nothing in between -> ordinary sign change
    with np.errstate(divide = 'ignore', invalid = 'ignore'):
        interp = xl - fl * (x[r] - xl) / (fm[r, c] - fl)
    loc = np.where(adj, interp, 0.5 * (x[np.minimum(lr + 1, M - 1)] + x[np.maximum(r - 1, 0)]))

    # Zero runs at the grid's own first/last node: no neighbour on one side to bracket them, so they are
    # handled separately and classified from the single sign available (see _columnCrossings).
    cols = np.arange(N)
    anyNz = nz.any(axis = 0)
    first, last = np.argmax(nz, axis = 0), M - 1 - np.argmax(nz[::-1], axis = 0)
    leadOk, trailOk = anyNz & (first > 0), anyNz & (last < M - 1)
    leadDown, trailDown = s[first, cols] < 0, s[last, cols] > 0
    if kind == 'down':
        leadOk, trailOk = leadOk & leadDown, trailOk & trailDown
    elif kind == 'up':
        leadOk, trailOk = leadOk & ~leadDown, trailOk & ~trailDown
    lc, tc = np.flatnonzero(leadOk), np.flatnonzero(trailOk)

    # Compact into the documented (Kmax, N) layout. A leading-run root always sits below every interior
    # crossing of its column and a trailing-run root above every one, so sorting on (column, row) with
    # sentinel rows -1 and M puts each column in ascending x; the rank within a column then follows from
    # the per-column counts. The sort is over the crossings alone, never over the full grid height.
    allCol = np.concatenate([lc, c, tc]).astype(np.intp)
    allKey = np.concatenate([np.full(lc.size, -1), r, np.full(tc.size, M)]).astype(np.intp)
    allLoc = np.concatenate([0.5 * (x[0] + x[np.maximum(first[lc] - 1, 0)]),
                             loc,
                             0.5 * (x[np.minimum(last[tc] + 1, M - 1)] + x[-1])])
    order = np.lexsort((allKey, allCol))
    allCol, allLoc = allCol[order], allLoc[order]
    counts = np.bincount(allCol, minlength = N)
    starts = np.concatenate([[0], np.cumsum(counts)[:-1]])
    out = np.full((int(counts.max(initial = 0)), N), np.nan)
    out[np.arange(allCol.size) - starts[allCol], allCol] = allLoc
    return out


def allRoots(x, f, kind = 'any', tol = 0.0):
    """ Every crossing of the requested kind, for each column of f.

    Returns a (Kmax, N) array, ascending in x within each column and NaN-padded where a column has fewer
    than Kmax crossings (Kmax = the most found in any single column; the result is (0, N) if there are
    none anywhere). The padded-array form is deliberate: it keeps the genuinely ragged result usable in
    vectorized downstream code (selectMax below) instead of forcing a list of variable-length arrays.
    Squeezed back to 1d when f was passed as 1d. """
    x, fm, wasFlat = _checkInputs(x, f, kind)
    out = _matrixCrossings(x, fm, kind, tol)
    return out[:, 0] if wasFlat else out


def firstRoot(x, f, kind = 'any', tol = 0.0):
    """ The lowest-x crossing of the requested kind per column; NaN where a column has none. Returns
    shape (N,), or a scalar-like 0d-indexable value when f was passed as 1d. """
    roots = allRoots(x, f, kind = kind, tol = tol)
    if roots.ndim == 1:                                  # f was 1d
        return roots[0] if roots.size else np.nan
    return roots[0, :] if roots.shape[0] else np.full(roots.shape[1], np.nan)


# Named wrappers. The detection logic is shared and preference-agnostic (above); these only fix `kind`,
# so that call sites read as what they mean -- "the maxima of the objective" rather than "the downward
# crossings of its derivative" -- without a second implementation to keep in sync.
def allMax(x, f, tol = 0.0):
    """ Every interior maximum of ∫f, i.e. every downward crossing of f. """
    return allRoots(x, f, kind = 'down', tol = tol)

def firstMax(x, f, tol = 0.0):
    """ The lowest-x interior maximum of ∫f. """
    return firstRoot(x, f, kind = 'down', tol = tol)

def allMin(x, f, tol = 0.0):
    """ Every interior minimum of ∫f, i.e. every upward crossing of f. """
    return allRoots(x, f, kind = 'up', tol = tol)

def firstMin(x, f, tol = 0.0):
    """ The lowest-x interior minimum of ∫f. """
    return firstRoot(x, f, kind = 'up', tol = tol)


def objectiveProfile(x, f):
    """ V(x) = ∫_{x[0]}^{x} f, evaluated at the grid nodes (eq:objectiveProfile).

    Cumulative trapezoid, normalised to V(x[0]) = 0. Note this is not an approximation of the integral of
    the piecewise-linear interpolant of f -- it is that integral, *exactly*, since the trapezoid rule
    integrates a piecewise-linear function without error. So V is the exact antiderivative of the same
    interpolant whose zeros allRoots locates, which is what makes the two consistent with each other in
    selectMax below. Returns (M,N), or (M,) for 1d f. """
    x, fm, wasFlat = _checkInputs(x, f)
    cells = 0.5 * (fm[:-1, :] + fm[1:, :]) * np.diff(x)[:, None]
    V = np.vstack([np.zeros((1, fm.shape[1])), np.cumsum(cells, axis = 0)])
    return V[:, 0] if wasFlat else V


def selectMax(x, f, tol = 0.0):
    """ The global maximiser of ∫f over [x[0], x[-1]], per column (eq:candidates).

    Rationale. Locating a root of f only imposes a necessary condition; when f has several downward
    crossings, "the first root found" is not in general the maximum, and it may not even beat the
    endpoints. Since a grid search has already evaluated f everywhere on x, the maximisation can be
    restored for free. Let f̂ be the piecewise-linear interpolant of f and V̂ = ∫f̂ (objectiveProfile).
    V̂ is piecewise quadratic and C¹ with V̂' = f̂, so its interior local maxima are exactly f̂'s downward
    crossings, and its global maximiser over the grid's span lies in

        C = {x[0], x[-1]} ∪ {downward crossings of f̂}.

    This single criterion therefore subsumes the boundary check rather than supplementing it: the two
    endpoints compete with the interior maxima on the same footing, so a corner solution is selected when
    it genuinely is the best point, not merely when f happens not to change sign. Note the accuracy
    demanded of V̂ is only that it *rank* well-separated candidates correctly -- much weaker than the
    accuracy demanded of the crossing locations themselves, which come from the interpolant directly.

    x must be the interior grid over which f is a genuine derivative of the objective. In particular do
    not pass a robustRoot-extended grid: outside [l,u] the penalised residual h is an artificial
    construction, not dV/dτ, so integrating it would be meaningless.

    Infeasible nodes. f may contain NaN, marking nodes where the objective is genuinely undefined rather
    than merely small -- e.g. a (choice, state) pair admitting no economic equilibrium. Such nodes are
    *excluded*: each column is maximised over its own surviving sub-grid, so the reported 'atBound' refers
    to the ends of the feasible region, not of the full grid. A column with fewer than two feasible nodes
    yields NaN (nothing to choose between), matching the caller-side rule that a state needs at least two
    feasible choices before a maximum is meaningful. Note NaN cannot simply be zero-filled here: np.sign
    would treat it as a sign change and manufacture crossings that do not exist.

    Returns {'x': (N,) maximisers, 'nMax': (N,) number of interior maxima found -- >1 flags genuine
    multiplicity for the caller to report, 'atBound': (N,) bool, True where the selected point is one of
    the two endpoints}. Scalars instead of (N,) arrays when f was passed as 1d. """
    xg, fm, wasFlat = _checkInputs(x, f)
    n = fm.shape[1]

    # Ragged columns take a per-column path on their own feasible sub-grid; the rest stay fully
    # vectorized. Splitting rather than looping everything keeps the common all-feasible case at full
    # speed, and the loop only ever runs over states, never over grid nodes.
    nanCols = np.isnan(fm).any(axis = 0)
    if nanCols.any():
        out = {'x': np.full(n, np.nan), 'nMax': np.zeros(n, dtype = int),
               'atBound': np.zeros(n, dtype = bool)}
        clean = ~nanCols
        if clean.any():
            sub = selectMax(xg, fm[:, clean], tol = tol)
            for k in out:
                out[k][clean] = sub[k]
        for j in np.flatnonzero(nanCols):
            ok = ~np.isnan(fm[:, j])
            if ok.sum() < 2:
                continue                        # no feasible interval to maximise over
            sub = selectMax(xg[ok], fm[ok, j], tol = tol)
            out['x'][j], out['nMax'][j], out['atBound'][j] = sub['x'], sub['nMax'], sub['atBound']
        return {k: v[0] for k, v in out.items()} if wasFlat else out
    V = objectiveProfile(xg, fm)
    roots = allRoots(xg, fm, kind = 'down', tol = tol)   # (K,N), NaN-padded
    if roots.ndim == 1:
        roots = roots[:, None]

    # V̂ at each interior maximum: the profile at the node opening its cell, plus the triangle swept
    # between that node and the crossing. Exact, because f̂ falls linearly from f[k] to 0 across it.
    k = np.clip(np.searchsorted(xg, roots, side = 'right') - 1, 0, xg.size - 2)
    col = np.broadcast_to(np.arange(n), roots.shape)
    with np.errstate(invalid = 'ignore'):                # NaN padding propagates; masked out just below
        vRoots = V[k, col] + 0.5 * fm[k, col] * (roots - xg[k])
    vRoots = np.where(np.isnan(roots), -np.inf, vRoots)  # padding must never win the argmax

    candX = np.vstack([np.full((1, n), xg[0]), np.full((1, n), xg[-1]), roots])
    candV = np.vstack([np.zeros((1, n)), V[-1, :][None, :], vRoots])
    best = np.argmax(candV, axis = 0)
    out = {'x': candX[best, np.arange(n)],
           'nMax': np.sum(~np.isnan(roots), axis = 0),
           'atBound': best < 2}
    return {k: v[0] for k, v in out.items()} if wasFlat else out


def selectMaxND(grid, f, name, tol = 0.0):
    """ selectMax over a Cartesian grid: search along `name`, one solution per state combination.

    grid: a CartesianGrid (cartesian.py). f: the objective's derivative evaluated flat over the whole
    product, shape (grid.size,) -- i.e. exactly what `someEquation(**grid.flat)` returns. Returns
    selectMax's own dict with every entry reshaped to grid.stateShape(name), so 'x' is the chosen value of
    `name` at each state, laid out on the state grid rather than as an opaque flat vector.

    Deliberately duck-typed rather than importing CartesianGrid: all this needs is `.values`, `.asColumns`
    and `.stateShape`, and keeping the import out means roots1d stays a self-contained module about
    crossings on a grid, with no dependency on how the grid was built. """
    sel = selectMax(grid.values(name), grid.asColumns(f, name), tol = tol)
    shape = grid.stateShape(name)
    return {k: np.asarray(v).reshape(shape) for k, v in sel.items()}
