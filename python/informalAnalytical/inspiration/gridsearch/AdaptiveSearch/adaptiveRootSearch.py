"""
Adaptive root search with dynamic grid refinement and expansion.

This implementation focuses on:
- Minimizing calls to F (critical for expensive functions)
- Maintaining complete Cartesian grids to avoid re-evaluation
- Efficient code structure with clear expansion and refinement phases
"""

import numpy as np
import pandas as pd
from ..InterpRoots import interpRootFromPandasGridOrNearestWithBoundary


def _evaluate_grid(F, grids, state_vals=None, old_fGrid=None, **kwargs):
    """Evaluate F on complete Cartesian product of grids, reusing old evaluations.
    
    F must return an array of shape (M, N) where:
    - M is the number of gridpoints (total Cartesian product points)
    - N is the number of equations/outputs from the function
    
    Parameters
    ----------
    F : callable
        Function to evaluate.
    grids : dict
        Variable grids.
    state_vals : dict, optional
        State values passed to F.
    old_fGrid : pd.DataFrame, optional
        Previous evaluations. If provided, only new points are evaluated.
    **kwargs
        Additional arguments for F.
    
    Returns
    -------
    pd.DataFrame
        Function evaluations on full Cartesian grid.
    """
    gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
    
    # If no old grid, evaluate everything
    if old_fGrid is None:
        f_kwargs = {name: gridsND.get_level_values(name).values for name in grids.keys()}
        if state_vals is not None:
            f_kwargs['states'] = state_vals
        f_kwargs.update(kwargs)
        FSample = F(**f_kwargs)
        return pd.DataFrame(FSample, index=gridsND)
    
    # Identify new points not in old_fGrid
    old_index_set = set(old_fGrid.index)
    new_mask = np.array([idx not in old_index_set for idx in gridsND])
    
    if not np.any(new_mask):
        # No new points, return old grid (shouldn't happen but handle gracefully)
        return old_fGrid
    
    # Evaluate only new points
    new_gridsND = gridsND[new_mask]
    f_kwargs = {name: new_gridsND.get_level_values(name).values for name in grids.keys()}
    if state_vals is not None:
        f_kwargs['states'] = state_vals
    f_kwargs.update(kwargs)
    new_FSample = F(**f_kwargs)
    new_fGrid = pd.DataFrame(new_FSample, index=new_gridsND)
    
    # Merge old and new evaluations
    combined_fGrid = pd.concat([old_fGrid, new_fGrid])
    
    # Reindex to match full Cartesian product order
    return combined_fGrid.reindex(gridsND)


def _expand_grids(grids, boundary_directions, n_expand=1, stepsize=None, bounds=None):
    """Expand grids by adding N points in specified directions.

    Parameters
    ----------
    grids : dict
        Current grids by variable name. Grids can be in ascending or descending order.
    boundary_directions : array-like
        -1 to extend lower bound, 1 to extend upper bound, 0 to keep as-is (per variable).
    n_expand : int or dict, default 1
        Number of points to add per expansion. If dict, use per-variable values.
    stepsize : float or dict, optional
        Step size for new points. If None, uses average spacing in current grid.
        If dict, use per-variable values.
    bounds : dict, optional
        Optional per-variable (lower, upper) bounds. Points violating bounds are filtered out.
    """
    expanded = {}
    for idx, (name, grid) in enumerate(grids.items()):
        direction = boundary_directions[idx]
        if direction == 0:
            expanded[name] = grid
            continue

        # Get per-variable parameters
        n_val = int(n_expand.get(name, 1) if isinstance(n_expand, dict) else n_expand)
        if stepsize is None:
            step = np.abs(np.mean(np.diff(grid)))
        elif isinstance(stepsize, dict):
            step = float(stepsize.get(name, np.abs(np.mean(np.diff(grid)))))
        else:
            step = float(stepsize)

        # Detect grid order and get boundary value
        is_asc = grid[-1] > grid[0]
        min_val, max_val = (grid[0], grid[-1]) if is_asc else (grid[-1], grid[0])
        boundary = min_val if direction == -1 else max_val
        
        # Compute and filter new points
        new_points = boundary + direction * step * np.arange(1, n_val + 1)
        if bounds and name in bounds:
            lo, hi = bounds[name]
            if lo is not None:
                new_points = new_points[new_points >= lo]
            if hi is not None:
                new_points = new_points[new_points <= hi]

        # Combine grids (prepend if (asc & dir=-1) or (desc & dir=1))
        prepend = (is_asc and direction == -1) or (not is_asc and direction == 1)
        expanded[name] = np.concatenate([new_points[::-1], grid] if prepend 
                                        else [grid, new_points])

    return expanded


def _refine_hypercube(grids, fGrid, root, factor=2):
    """Extract and refine the hypercube containing root."""
    refined = {}
    mask = np.ones(len(fGrid), dtype=bool)
    
    for idx, (name, grid) in enumerate(grids.items()):
        # Find bracketing interval
        insert_idx = np.searchsorted(grid, root[idx])
        lower_idx = max(0, min(insert_idx - 1, len(grid) - 2))
        upper_idx = lower_idx + 1
        
        lower, upper = grid[lower_idx], grid[upper_idx]
        refined[name] = np.linspace(lower, upper, factor + 1)
        
        # Update mask for hypercube extraction
        level_values = fGrid.index.get_level_values(name)
        mask &= (level_values >= lower - 1e-10) & (level_values <= upper + 1e-10)
    
    return refined, fGrid[mask]


def _check_convergence(F, root, grids, state_vals, tol, kwargs):
    """Evaluate F at root and check convergence."""
    f_kwargs = {name: np.array([root[i]]) for i, name in enumerate(grids.keys())}
    if state_vals is not None:
        f_kwargs['states'] = state_vals
    f_kwargs.update(kwargs)
    residual = float(np.linalg.norm(F(**f_kwargs)))
    return residual < tol, residual


def solveAdaptiveRoot(F, initial_grids, state_vals=None, tol=1e-6, 
                      maxExpand=5, maxRefine=3, expansion_n=1, expansion_stepsize=None,
                      refinement_factor=1, expansion_bounds=None, **kwargs):
    """
    Adaptively find root F(X) = 0 with minimal function evaluations.
    
    Strategy:
    1. Expansion: Add points directionally until root found or limit reached
    2. Refinement: Zoom into hypercube containing root for accuracy
    
    Parameters
    ----------
    F : callable
        Function to minimize. Receives solution variables as keyword arguments.
    initial_grids : dict
        Variable names -> 1D arrays defining initial search grid. 
    state_vals : dict, optional
        State values passed to F under 'states' key.
    tol : float, default 1e-6
        Convergence tolerance for ||F(root)||.
    maxExpand : int, default 5
        Maximum expansion iterations.
    maxRefine : int, default 3
        Maximum refinement iterations.
    expansion_n : int or dict, default 1
        Number of points to add per expansion. Dict allows per-variable values.
    expansion_stepsize : float or dict, optional
        Step size for expansion. If None, uses average grid spacing. Dict allows per-variable values.
    refinement_factor : int, default 1
        Subdivisions per dimension in refinement.
    expansion_bounds : dict, optional
        Per-variable (lower, upper) bounds to prevent grids from exceeding limits.
    **kwargs
        Additional arguments for F.
    
    Returns
    -------
    dict
        Keys: 'x' (solution), 'status' (converged), 'type' ('root'/'nn'),
        'residual' (||F(x)||), 'iterations' (expansion/refinement counts).
    """
    grids = {k: np.array(v, dtype=float) for k, v in initial_grids.items()}
    expand_count = refine_count = 0
    
    # Phase 1: Expansion - find a root
    fGrid = _evaluate_grid(F, grids, state_vals, **kwargs)
    
    for _ in range(maxExpand + 1):
        result = interpRootFromPandasGridOrNearestWithBoundary(fGrid)
        
        if result['type'] == 'root':
            root = result['x']
            break
        
        # No root found
        if expand_count >= maxExpand or not np.any(result['boundary'] != 0):
            # Expansion limit reached or NN is interior - return NN
            converged, residual = _check_convergence(
                F, result['x'], grids, state_vals, tol, kwargs
            )
            return {
                'x': result['x'],
                'status': converged,
                'type': 'nn',
                'residual': residual,
                'iterations': {'expansions': expand_count, 'refinements': 0}
            }
        
        # Expand and re-evaluate (only new points)
        grids = _expand_grids(grids, result['boundary'], expansion_n, expansion_stepsize, expansion_bounds)
        fGrid = _evaluate_grid(F, grids, state_vals, old_fGrid=fGrid, **kwargs)
        expand_count += 1
    
    # Phase 2: Refinement - improve accuracy
    for _ in range(maxRefine + 1):
        converged, residual = _check_convergence(F, root, grids, state_vals, tol, kwargs)
        
        if converged:
            return {
                'x': root,
                'status': True,
                'type': 'root',
                'residual': residual,
                'iterations': {'expansions': expand_count, 'refinements': refine_count}
            }
        
        if refine_count >= maxRefine:
            # Refinement limit reached
            return {
                'x': root,
                'status': False,
                'type': 'nn',
                'residual': residual,
                'iterations': {'expansions': expand_count, 'refinements': refine_count}
            }
        
        # Refine hypercube
        grids, fGrid = _refine_hypercube(grids, fGrid, root, refinement_factor)
        fGrid = _evaluate_grid(F, grids, state_vals, old_fGrid=fGrid, **kwargs)
        refine_count += 1
        
        result = interpRootFromPandasGridOrNearestWithBoundary(fGrid)
        if result['type'] != 'root':
            # Lost root in refinement - return best available
            converged, residual = _check_convergence(
                F, result['x'], grids, state_vals, tol, kwargs
            )
            return {
                'x': result['x'],
                'status': converged,
                'type': 'nn',
                'residual': residual,
                'iterations': {'expansions': expand_count, 'refinements': refine_count}
            }
        root = result['x']
    
    # Should not reach here, but handle gracefully
    converged, residual = _check_convergence(F, root, grids, state_vals, tol, kwargs)
    return {
        'x': root,
        'status': converged,
        'type': 'root' if converged else 'nn',
        'residual': residual,
        'iterations': {'expansions': expand_count, 'refinements': refine_count}
    }
