import numpy as np
import pandas as pd
from itertools import product

from ..InterpRoots import interpRootFromPandasGrid, interpRootFromPandasGridOrNearestWithBoundary

def _refineGrid(grid, value, l, u):
    idx = np.searchsorted(grid, value)
    return grid[max(idx-l,0):min(idx+u,len(grid))]

def _refineGridWithIndices(grid, value, l, u):
    """Refine grid and return both values and their indices in the global grid.
    
    Returns
    -------
    refined_grid : ndarray
        Subset of grid values.
    refined_indices : ndarray
        Indices into the global grid for each refined grid point.
    """
    idx = np.searchsorted(grid, value)
    start_idx = max(idx - l, 0)
    end_idx = min(idx + u, len(grid))
    refined_indices = np.arange(start_idx, end_idx)
    return grid[refined_indices], refined_indices

def _createTraversalOrder(stateGrids: dict):
    """
    Create auxiliary array for N-dimensional traversal of state grid.
    
    Parameters
    ----------
    stateGrids : dict
        Keys = state variable names.
        Values = 1darray of states to solve for.
    
    Returns
    -------
    traversal : ndarray
        Array of shape (total_points, 2, n_states) where:
        - traversal[i, 0, :] contains the current state indices
        - traversal[i, 1, :] contains the reference state indices (for previous solution)
        First point has reference indices of (-1, -1, ...) to indicate no previous solution.
    """
    n_states = len(stateGrids)
    state_shapes = [len(v) for v in stateGrids.values()]
    total_points = np.prod(state_shapes)
    
    # Create array: (total_points, 2, n_states)
    # Column 0: current indices, Column 1: reference indices
    traversal = np.empty((total_points, 2, n_states), dtype=int)
    
    # Generate all combinations in C-order (last index varies fastest)
    all_indices = np.array(list(product(*[range(s) for s in state_shapes])))
    traversal[:, 0, :] = all_indices
    
    # For each point, determine which previous point to use as reference
    # Strategy: use the previous point in the last varying dimension
    # For first point in each "row", use previous in second-to-last dimension, etc.
    for idx in range(total_points):
        current = all_indices[idx]
        
        if idx == 0:
            # First point - no reference
            traversal[idx, 1, :] = -1
        else:
            # Find which dimension to step back in
            # Default: step back in last dimension (most frequently varying)
            reference = current.copy()
            
            # Try to step back in last dimension first, then second-to-last, etc.
            for dim in range(n_states - 1, -1, -1):
                if current[dim] > 0:
                    reference[dim] -= 1
                    break
            
            traversal[idx, 1, :] = reference
    
    return traversal


def _createTraversalOrderFromMultiIndex(stateGrids: pd.MultiIndex):
    """
    Create auxiliary array for traversal of MultiIndex state grid.
    Orders traversal to keep nearby state combinations together for better grid refinement.
    
    Parameters
    ----------
    stateGrids : pd.MultiIndex
        MultiIndex containing combinations of state variables to solve for.
        Each level represents a different state variable.
    
    Returns
    -------
    traversal : ndarray
        Array of shape (len(stateGrids), 3) where:
        - traversal[i, 0] contains the current position index in sorted order
        - traversal[i, 1] contains the reference position index (for previous solution)
        - traversal[i, 2] contains the number of state dimensions that changed from reference
        First point has reference index of -1 to indicate no previous solution.
    state_names : list
        Names of state variables from MultiIndex levels.
    sorted_indices : ndarray
        Indices that sort the original MultiIndex (for mapping back to original order if needed).
    """
    n_points = len(stateGrids)
    n_states = stateGrids.nlevels
    state_names = list(stateGrids.names)
    
    # Sort MultiIndex lexicographically to keep nearby states together
    # This ensures we traverse similar state combinations sequentially
    sorted_indices = np.lexsort([stateGrids.get_level_values(i) for i in range(n_states-1, -1, -1)])
    sorted_states = stateGrids[sorted_indices]
    
    # Create array: (n_points, 3)
    # Column 0: current index in sorted order
    # Column 1: reference index in sorted order
    # Column 2: number of dimensions that changed
    traversal = np.empty((n_points, 3), dtype=int)
    traversal[:, 0] = sorted_indices
    
    # For each point, determine which previous point to use as reference
    for idx in range(n_points):
        if idx == 0:
            # First point - no reference
            traversal[idx, 1] = -1
            traversal[idx, 2] = 0
        else:
            # Use previous point in sorted order as reference
            traversal[idx, 1] = sorted_indices[idx - 1]
            
            # Count how many dimensions changed
            current_state = sorted_states[idx]
            reference_state = sorted_states[idx - 1]
            n_changed = sum(current_state[dim] != reference_state[dim] for dim in range(n_states))
            traversal[idx, 2] = n_changed
    
    return traversal, state_names, sorted_indices


def _avg_step_per_state_from_multiindex(stateGrids: pd.MultiIndex):
    """Compute average step size for each state dimension from a MultiIndex."""
    avg = {}
    for level, name in enumerate(stateGrids.names):
        vals = np.asarray(stateGrids.get_level_values(level), dtype=float)
        uniq = np.unique(vals)
        diffs = np.diff(uniq)
        avg[name] = float(np.mean(diffs)) if diffs.size else 1.0
    return avg


def _compute_norm_change(stateGrids: pd.MultiIndex, traversal: np.ndarray, state_names: list, avg_steps: dict):
    """Compute normalized state changes for each traversal step (vectorized).
    
    Returns
    -------
    norm_change : dict
        Keys = state names, Values = arrays of length n_points with |Δstate| / avg_step.
    """
    n_points = len(stateGrids)
    norm_change = {name: np.zeros(n_points, dtype=float) for name in state_names}
    
    # Extract all current and reference indices at once
    curr_indices = traversal[1:, 0]
    ref_indices = traversal[1:, 1]
    
    # Pre-compute reciprocals of average steps for faster division
    inv_avg = {name: 1.0 / (avg_steps.get(name, 1.0) or 1.0) for name in state_names}
    
    # Vectorized computation for each state dimension
    for dim, name in enumerate(state_names):
        curr_vals = np.array([float(stateGrids[idx][dim]) for idx in curr_indices])
        ref_vals = np.array([float(stateGrids[idx][dim]) for idx in ref_indices])
        norm_change[name][1:] = np.abs(curr_vals - ref_vals) * inv_avg[name]
    
    return norm_change


def _compute_grid_counts(norm_change: dict, sol_names: list, state_names: list, ΔL: dict, ΔU: dict):
    """Compute grid refinement counts for all points and solution variables (vectorized).
    
    Returns
    -------
    grid_counts_L : ndarray
        Array of shape (n_points, n_sol) with lower grid counts.
    grid_counts_U : ndarray
        Array of shape (n_points, n_sol) with upper grid counts.
    """
    n_points = len(next(iter(norm_change.values())))
    n_sol = len(sol_names)
    
    grid_counts_L = np.zeros((n_points, n_sol), dtype=int)
    grid_counts_U = np.zeros((n_points, n_sol), dtype=int)
    
    # For each solution variable, compute weighted sum over states
    for sol_idx, sol_name in enumerate(sol_names):
        l_sum = np.zeros(n_points, dtype=float)
        u_sum = np.zeros(n_points, dtype=float)
        
        for state_name in state_names:
            dL = ΔL[(sol_name, state_name)]
            dU = ΔU[(sol_name, state_name)]
            l_sum += norm_change[state_name] * dL
            u_sum += norm_change[state_name] * dU
        
        # Round and ensure minimum of 1
        grid_counts_L[:, sol_idx] = np.maximum(1, np.round(l_sum).astype(int))
        grid_counts_U[:, sol_idx] = np.maximum(1, np.round(u_sum).astype(int))
    
    return grid_counts_L, grid_counts_U


def _expand_grids_by_one(grids: dict, solGrids: dict, boundary_directions: np.ndarray = None):
    """
    Expand refined grids by 1 gridpoint in the direction of boundaries.
    
    Parameters
    ----------
    grids : dict
        Current refined grids (keys = sol var names, values = 1d arrays).
    solGrids : dict
        Global solution grids with full extent.
    boundary_directions : ndarray, optional
        Integer array indicating expansion direction for each dimension:
        -1 = expand lower side only, 0 = no expansion, +1 = expand upper side only.
        If None, expand both sides for all dimensions.
    
    Returns
    -------
    expanded_grids : dict
        Expanded grids with additional boundary points (within solGrids bounds).
    """
    expanded_grids = {}
    sol_names = list(grids.keys())
    
    for idx, sol_name in enumerate(sol_names):
        grid = grids[sol_name]
        global_grid = solGrids[sol_name]
        
        # Determine expansion direction for this dimension
        if boundary_directions is not None:
            direction = boundary_directions[idx]
        else:
            direction = None  # Expand both sides
        
        # Find indices of current grid bounds in global grid
        min_idx = np.searchsorted(global_grid, grid[0])
        max_idx = np.searchsorted(global_grid, grid[-1])
        
        # Determine new bounds based on direction
        if direction is None:
            # Expand both sides (original behavior)
            new_min_idx = max(0, min_idx - 1)
            new_max_idx = min(len(global_grid) - 1, max_idx + 1)
        elif direction == -1:
            # Expand lower side only
            new_min_idx = max(0, min_idx - 1)
            new_max_idx = max_idx
        elif direction == 1:
            # Expand upper side only
            new_min_idx = min_idx
            new_max_idx = min(len(global_grid) - 1, max_idx + 1)
        else:  # direction == 0
            # No expansion
            new_min_idx = min_idx
            new_max_idx = max_idx
        
        expanded_grids[sol_name] = global_grid[new_min_idx:new_max_idx + 1]
    
    return expanded_grids


def _evaluate_F(F, gridsND, grids, state_vals, kwargs):
    """Helper to evaluate F with consistent keyword argument construction.
    
    Parameters
    ----------
    F : function
        Function to evaluate. Must return array of shape (M, N) where:
        - M is the number of gridpoints
        - N is the number of equations/outputs
    gridsND : pd.MultiIndex
        MultiIndex of grid points.
    grids : dict
        Solution grids dictionary.
    state_vals : dict
        State variable values.
    kwargs : dict
        Additional keyword arguments for F.
    
    Returns
    -------
    FSample : ndarray
        Function evaluations with shape (M, N).
    """
    f_kwargs = {name: gridsND.get_level_values(name).values for name in grids.keys()}
    if state_vals is not None:
        f_kwargs['states'] = state_vals
    f_kwargs.update(kwargs)
    return F(**f_kwargs)


def _evaluate_F_with_indices(F, gridsND, grid_indices, state_vals, kwargs):
    """Helper to evaluate F while passing grid indices via `idxs`.

    Parameters
    ----------
    F : function
        Function to evaluate. Receives solution variables as keyword arguments and
        a dict `idxs` with 1D index arrays into the global grids.
    gridsND : pd.MultiIndex
        MultiIndex of grid points.
    grid_indices : dict
        Dict mapping solution variable names to 1D arrays of indices in global grids.
    state_vals : dict
        State variable values.
    kwargs : dict
        Additional keyword arguments for F.

    Returns
    -------
    FSample : ndarray
        Function evaluations.
    """
    f_kwargs = {name: gridsND.get_level_values(name).values for name in gridsND.names}
    f_kwargs['idxs'] = grid_indices  # Pass 1D index arrays directly
    if state_vals is not None:
        f_kwargs['states'] = state_vals
    f_kwargs.update(kwargs)
    return F(**f_kwargs)

def _solveWithGridExpansion(F, grids: dict, solGrids: dict, fGrid: pd.DataFrame, 
                            state_vals: dict = None, maxExpand: int = 5, **kwargs):
    """
    Robust root finding with boundary-aware grid expansion.
    
    Attempts to find a root using the current grid. If unsuccessful, uses boundary
    detection to intelligently expand only the dimensions where the nearest neighbor
    is at a grid boundary. Iterates up to maxExpand times.
    
    Parameters
    ----------
    F : function
        Function to evaluate. Receives solution and state variables as keyword arguments, and **kwargs.
    grids : dict
        Current refined grids (keys = sol var names, values = 1d arrays).
    solGrids : dict
        Global solution grids (for boundary constraint).
    fGrid : pd.DataFrame
        Current DataFrame with function samples (MultiIndex on inputs, columns on outputs).
    state_vals : dict, optional
        State variable values for current state combination (keys = state names, values = scalar).
    maxExpand : int
        Maximum number of grid expansion iterations. Default is 5.
    kwargs : dict
        Additional arguments to pass to F.
    
    Returns
    -------
    root : ndarray
        Approximate root location.
    success : bool
        True if a root was found, False if returning nearest neighbor.
    """
    # Try to find root with current grid using boundary detection
    result_dict = interpRootFromPandasGridOrNearestWithBoundary(fGrid)
    
    # If root found, return immediately
    if result_dict['type'] == 'root':
        return result_dict['x'], True
    
    # Otherwise we have a nearest neighbor with boundary information
    nearest_neighbor = result_dict['x']
    boundary_directions = result_dict['boundary']
    
    # Check if any dimensions are at boundary
    if not np.any(boundary_directions != 0):
        # No dimensions at boundary - cannot expand meaningfully
        return nearest_neighbor, False
    
    # Iteratively expand grid at boundary dimensions and retry
    for expand_iter in range(maxExpand):
        # Expand only in directions indicated by boundary_directions
        grids = _expand_grids_by_one(grids, solGrids, boundary_directions=boundary_directions)
        
        # Create the new expanded grid (full Cartesian product)
        expanded_gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
        
        # Identify which points are new (not already in fGrid)
        new_points = expanded_gridsND.difference(fGrid.index)
        
        if len(new_points) == 0:
            # No more points to add (hit global boundaries)
            break
        
        # Evaluate F at new points only, including state values
        f_kwargs = {name: new_points.get_level_values(name).values for name in new_points.names}
        if state_vals is not None:
            f_kwargs['states'] = state_vals
        f_kwargs.update(kwargs)
        new_FSample = F(**f_kwargs)
        
        # Add new samples to DataFrame
        new_df = pd.DataFrame(new_FSample, index=new_points)
        fGrid = pd.concat([fGrid, new_df])
        
        # Try again with boundary detection
        result_dict = interpRootFromPandasGridOrNearestWithBoundary(fGrid)
        
        if result_dict['type'] == 'root':
            # Root found
            return result_dict['x'], True
        
        # Update nearest neighbor and boundary directions for next iteration
        nearest_neighbor = result_dict['x']
        boundary_directions = result_dict['boundary']
        
        # If no dimensions at boundary anymore, stop expanding
        if not np.any(boundary_directions != 0):
            break
    
    # Return nearest neighbor after maxExpand iterations
    return nearest_neighbor, False


def _solveWithGridExpansionWithIndices(F, grids: dict, grid_indices: dict, solGrids: dict, 
                                       fGrid: pd.DataFrame, state_vals: dict = None, 
                                       maxExpand: int = 5, **kwargs):
    """
    Boundary-aware grid expansion with `idxs` passed to F.
    """
    result_dict = interpRootFromPandasGridOrNearestWithBoundary(fGrid)

    if result_dict['type'] == 'root':
        return result_dict['x'], True

    nearest_neighbor = result_dict['x']
    boundary_directions = result_dict['boundary']

    if not np.any(boundary_directions != 0):
        return nearest_neighbor, False

    for _ in range(maxExpand):
        grids = _expand_grids_by_one(grids, solGrids, boundary_directions=boundary_directions)
        grid_indices = {name: np.searchsorted(solGrids[name], grids[name]) for name in grids.keys()}
        
        expanded_gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
        new_points = expanded_gridsND.difference(fGrid.index)

        if len(new_points) == 0:
            break

        new_FSample = _evaluate_F_with_indices(F, new_points, grid_indices, state_vals, kwargs)
        new_df = pd.DataFrame(new_FSample, index=new_points)
        fGrid = pd.concat([fGrid, new_df])

        result_dict = interpRootFromPandasGridOrNearestWithBoundary(fGrid)

        if result_dict['type'] == 'root':
            return result_dict['x'], True

        nearest_neighbor = result_dict['x']
        boundary_directions = result_dict['boundary']

        if not np.any(boundary_directions != 0):
            break

    return nearest_neighbor, False


def solveSingleRoot(F, solGrids: dict, solGrid0: dict = None, state_vals: dict = None, maxExpand: int = 5, **kwargs):
    """
    Solve F(X) = 0 for a single state (no state grid traversal).

    Parameters
    ----------
    F : function
        Function to evaluate. Receives solution variables as keyword arguments and
        returns column-stacked outputs matching the number of solution variables.
    solGrids : dict
        Keys = choice variable names. Values = 1d arrays of the global grid.
    solGrid0 : dict, optional
        Optional refined subset of ``solGrids`` to use for the initial iteration.
    state_vals : dict, optional
        Optional state values to pass through to ``F`` under the key ``states``.
    maxExpand : int, optional
        Maximum number of grid expansion iterations. Default is 5.
    kwargs : dict
        Additional keyword arguments forwarded to ``F``.

    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'x': ndarray of the solution for the choice variables.
        - 'status': bool, always True for this solver.
        - 'type': ndarray of strings ('root' or 'nn') with one element (single root).
        - 'interior': True if all entries in 'type' are 'root' else False.
    """

    # Use provided initial grid subset or the full global grid
    grids = solGrid0 if solGrid0 is not None else solGrids

    # Build initial MultiIndex grid and evaluate F
    gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
    FSample = _evaluate_F(F, gridsND, grids, state_vals, kwargs)
    fGrid = pd.DataFrame(FSample, index=gridsND)

    # Solve with boundary-aware grid expansion
    root, success = _solveWithGridExpansion(
        F, grids, solGrids, fGrid, state_vals=state_vals, maxExpand=maxExpand, **kwargs
    )

    return {
        'x': root,
        'status': True,
        'type': np.array(['root' if success else 'nn']),
        'interior': success
    }


def solveLoopND(F, solGrids: dict, stateGrids: pd.MultiIndex, ΔL: dict, ΔU: dict, solGrid0 = None, maxExpand: int = 5, **kwargs):
    """
    Approximate roots F(X) = 0 using pre-computed grid samples via interpolation.
    This identifies solutions for combinations of states in stateGrids MultiIndex.

    Parameters
    ----------
    F: Function.
        Defined over refined solution grids, state grids, and **kwargs. 
        Assumes that function accepts solution variables in their order in solGrids
        and as 1d vectors of similar length.
    solGrids : dict.
        Keys = choice variable names.
        Values = 1darray of global intervals to search over.
    stateGrids : pd.MultiIndex
        MultiIndex containing combinations of state variables to solve for.
        Each level represents a different state variable.
    ΔL : dict.
        Keys = cartesian grid of keys from solGrids + names in stateGrids.
        Values = Number of gridpoints to include below previous solution.
    ΔU: dict.
        Keys follow same structure as ΔL.
        Values = Number of gridpoints to include above previous solution.
    solGrid0: None or refined version of solGrids (see refineGrid method below).
        Identifies a subset of the global grid solGrids to apply in the very first iteration.                
    maxExpand : int, optional
        Maximum number of grid expansion iterations before using nearest neighbor fallback.
        Default is 5.
    kwargs: Passed to evaluations of F.

    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'x': ndarray of roots with shape (len(stateGrids), len(solGrids)).
        - 'status': bool, always True for this solver.
        - 'type': ndarray of same shape as 'x', entries 'root' or 'nn'.
        - 'interior': bool, True when all entries in 'type' are 'root'.
    """
    n_points = len(stateGrids)
    n_sol = len(solGrids)
    roots = np.empty((n_points, n_sol), dtype=float)
    root_types = np.empty((n_points, n_sol), dtype=object)
    sol_names = list(solGrids.keys())
    avg_steps = _avg_step_per_state_from_multiindex(stateGrids)
    
    # Create traversal order
    traversal, state_names, sorted_indices = _createTraversalOrderFromMultiIndex(stateGrids)

    # norm_change is a dict: state_name -> array of |Δstate| / avg_step for each point
    norm_change = _compute_norm_change(stateGrids, traversal, state_names, avg_steps)
    
    # Precompute grid refinement counts for all points and solution variables
    grid_counts_L, grid_counts_U = _compute_grid_counts(norm_change, sol_names, state_names, ΔL, ΔU)
    
    # Loop through all state combinations in sorted order
    for point_idx in range(n_points):
        current_idx = traversal[point_idx, 0]
        reference_idx = traversal[point_idx, 1]
        
        # Extract state values for current state combination as dict
        state_vals = dict(zip(state_names, stateGrids[current_idx]))

        # Determine which grids to use
        if point_idx == 0:
            # First element: use solGrid0 or full solGrids
            grids = solGrids if solGrid0 is None else solGrid0
        else:
            # Refine grids based on previous solution using precomputed counts
            grids = {}
            for sol_idx, sol_name in enumerate(sol_names):
                grids[sol_name] = _refineGrid(
                    solGrids[sol_name], 
                    roots[reference_idx, sol_idx],
                    grid_counts_L[point_idx, sol_idx],
                    grid_counts_U[point_idx, sol_idx]
                )
        
        # Evaluate F on refined grid (includes state values)
        gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
        FSample = _evaluate_F(F, gridsND, grids, state_vals, kwargs)
        fGrid = pd.DataFrame(FSample.reshape(len(grids), gridsND.shape[0]).T, index=gridsND)
        
        # Find root with robust grid expansion fallback
        root, success = _solveWithGridExpansion(F, grids, solGrids, fGrid, state_vals=state_vals, maxExpand=maxExpand, **kwargs)
        roots[current_idx] = root
        root_types[current_idx] = 'root' if success else 'nn'
    
    interior = bool(np.all(root_types == 'root'))
    return {
        'x': roots,
        'status': True,
        'type': root_types,
        'interior': interior,
    }


def solveLoopCartesianND(F, solGrids: dict, stateGrids: dict, ΔL: dict, ΔU: dict, solGrid0 = None, maxExpand: int = 5, **kwargs):
    """
    Approximate roots F(X) = 0 using pre-computed grid samples via interpolation.
    This identifies solutions on cartesian grid of states in stateGrids.

    Parameters
    ----------
    F: Function.
        Defined over refined solution grids, state grids, and **kwargs. 
        Assumes that function accepts solution variables in their order in solGrids
        and as 1d vectors of similar length.
    solGrids : dict.
        Keys = choice variable names.
        Values = 1darray of global intervals to search over.
    stateGrids : dict.
        Keys = state variable names. 
        Values = 1darray of states to solve for.
    ΔL : dict.
        Keys = cartesian grid of keys from solGrids + stateGrids.
        Values = Number of gridpoints to include below previous solution for variable, state combination.
    ΔU: dict.
        Keys = cartesian grid of keys from solGrids + stateGrids.
        Values = Number of gridpoints to include above previous solution for variable, state combination.
    solGrid0: None or refined version of solGrids (see refineGrid method below).
        Identifies a subset of the global grid solGrids to apply in the very first iteration.                
    maxExpand : int, optional
        Maximum number of grid expansion iterations before using nearest neighbor fallback.
        Default is 5.
    kwargs: Passed to evaluations of F.

    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'x': ndarray of roots with shape [len(v) for v in stateGrids.values()] + [len(solGrids)].
        - 'status': bool, always True for this solver.
        - 'type': ndarray of same shape as 'x', entries 'root' or 'nn'.
        - 'interior': bool, True when all entries in 'type' are 'root'.
    """
    roots = np.empty([len(v) for v in stateGrids.values()] + [len(solGrids)], dtype = float)
    root_types = np.empty_like(roots, dtype=object)
    sol_names = list(solGrids.keys())
    state_names = list(stateGrids.keys())
    n_states = len(state_names)
    
    # Create traversal order
    traversal = _createTraversalOrder(stateGrids)
    
    # Loop through all state combinations
    for point_idx in range(traversal.shape[0]):
        current_indices = tuple(traversal[point_idx, 0, :])
        reference_indices = tuple(traversal[point_idx, 1, :])
        
        # Extract state values for current state combination as dict
        state_vals = {state_names[i]: stateGrids[state_names[i]][current_indices[i]] for i in range(n_states)}
        
        # Determine which grids to use
        if point_idx == 0:
            # First element: use solGrid0 or full solGrids
            grids = solGrids if solGrid0 is None else solGrid0
        else:
            # Refine grids based on previous solution
            # Determine which state dimension changed to select appropriate ΔL/ΔU
            changed_dim = -1
            for dim in range(n_states):
                if current_indices[dim] != reference_indices[dim]:
                    changed_dim = dim
                    break
            
            # Get reference solution
            ref_solution = roots[reference_indices + (slice(None),)]
            
            # Refine grids for each solution variable
            grids = {}
            for sol_idx, sol_name in enumerate(sol_names):
                state_key = state_names[changed_dim] if changed_dim >= 0 else state_names[-1]
                grids[sol_name] = _refineGrid(
                    solGrids[sol_name], 
                    ref_solution[sol_idx],
                    ΔL[(sol_name, state_key)], 
                    ΔU[(sol_name, state_key)]
                )
        
        gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
        FSample = _evaluate_F(F, gridsND, grids, state_vals, kwargs)
        fGrid = pd.DataFrame(FSample, index=gridsND)
        
        root, success = _solveWithGridExpansion(F, grids, solGrids, fGrid, state_vals=state_vals, maxExpand=maxExpand, **kwargs)
        roots[current_indices + (slice(None),)] = root
        root_types[current_indices + (slice(None),)] = 'root' if success else 'nn'
    
    interior = bool(np.all(root_types == 'root'))
    return {
        'x': roots,
        'status': True,
        'type': root_types,
        'interior': interior,
    }


def solveLoopSimple(F, solGrids: dict, stateGrids: dict, **kwargs):
    """
    Solve F(X) = 0 for each state combination using the full global solution grids only.

    This routine does not refine grids and does not expand grids. It loops through
    the cartesian product of ``stateGrids`` and applies ``solveSingleRoot`` with
    ``maxExpand=0`` so evaluation is always on the global grids.

    Parameters
    ----------
    F : function
        Function to evaluate. Receives solution variables and state variables as
        keyword arguments and returns column-stacked outputs.
    solGrids : dict
        Keys = choice variable names.
        Values = 1d arrays of the global grid.
    stateGrids : dict
        Keys = state variable names.
        Values = 1d arrays of states to solve for.
    kwargs : dict
        Additional keyword arguments forwarded to ``F``.

    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'x': ndarray of roots with shape [len(v) for v in stateGrids.values()] + [len(solGrids)].
        - 'status': bool, always True for this solver.
        - 'type': ndarray of same shape as 'x', entries 'root' or 'nn'.
        - 'interior': bool, True when all entries in 'type' are 'root'.
    """
    roots = np.empty([len(v) for v in stateGrids.values()] + [len(solGrids)], dtype=float)
    root_types = np.empty_like(roots, dtype=object)
    state_names = list(stateGrids.keys())
    n_states = len(state_names)

    traversal = _createTraversalOrder(stateGrids)

    for point_idx in range(traversal.shape[0]):
        current_indices = tuple(traversal[point_idx, 0, :])
        state_vals = {
            state_names[i]: stateGrids[state_names[i]][current_indices[i]]
            for i in range(n_states)
        }

        result = solveSingleRoot(
            F,
            solGrids,
            solGrid0=None,
            state_vals=state_vals,
            maxExpand=0,
            **kwargs
        )

        roots[current_indices + (slice(None),)] = result['x']
        root_types[current_indices + (slice(None),)] = result['type'][0]

    interior = bool(np.all(root_types == 'root'))
    return {
        'x': roots,
        'status': True,
        'type': root_types,
        'interior': interior,
    }


def solveLoopCartesianNDIdx(F, solGrids: dict, stateGrids: dict, ΔL: dict, ΔU: dict, solGrid0=None, maxExpand: int = 5, **kwargs):
    """
    Variant of solveLoopCartesianND where F receives grid indices for efficient parameter access.

    This method tracks grid indices during refinement and passes them to F via the `idxs` 
    keyword argument. This enables efficient access to precomputed parameters that are 
    arranged to match the global solution grid structure.

    Parameters
    ----------
    F : function
        Function to evaluate. Receives solution variables as keyword arguments and
        a dict `idxs` mapping each solution variable name to 1D arrays of indices in the 
        global grid. Use `np.ix_` to subset precomputed N-dimensional arrays.
        
        Example usage in F::
        
            def F(x, y, idxs=None, states=None, precomputed_params_2d=None):
                # precomputed_params_2d has shape (len(solGrids['x']), len(solGrids['y']))
                # Subset to match refined grid dimensions
                params_subset = precomputed_params_2d[np.ix_(idxs['x'], idxs['y'])]
                # Now params_subset has shape (len(x_refined), len(y_refined))
                # which matches the Cartesian product evaluation grid
                return equations_using(x, y, params_subset.ravel(), states)
    
    solGrids : dict
        Keys = choice variable names. Values = 1d arrays of the global grid.
    stateGrids : dict
        Keys = state variable names. Values = 1d arrays of states to solve for.
    ΔL, ΔU, solGrid0, maxExpand, kwargs :
        Same as solveLoopCartesianND.

    Returns
    -------
    result : dict
        Dictionary with keys 'x', 'status', 'type', and 'interior'.
        
    Notes
    -----
    The indices are 1D arrays for each solution variable, suitable for use with 
    `np.ix_()` for N-dimensional array subsetting. Indices are tracked throughout 
    grid refinement and expansion, eliminating repeated searchsorted operations.
    """
    roots = np.empty([len(v) for v in stateGrids.values()] + [len(solGrids)], dtype=float)
    root_types = np.empty_like(roots, dtype=object)
    sol_names = list(solGrids.keys())
    state_names = list(stateGrids.keys())
    n_states = len(state_names)

    traversal = _createTraversalOrder(stateGrids)

    for point_idx in range(traversal.shape[0]):
        current_indices = tuple(traversal[point_idx, 0, :])
        reference_indices = tuple(traversal[point_idx, 1, :])

        state_vals = {state_names[i]: stateGrids[state_names[i]][current_indices[i]] for i in range(n_states)}

        if point_idx == 0:
            grids = solGrids if solGrid0 is None else solGrid0
            # For first point, create grid_indices from grids
            grid_indices = {name: np.arange(len(grids[name])) if grids is solGrids 
                           else np.searchsorted(solGrids[name], grids[name]) 
                           for name in grids.keys()}
        else:
            changed_dim = -1
            for dim in range(n_states):
                if current_indices[dim] != reference_indices[dim]:
                    changed_dim = dim
                    break

            ref_solution = roots[reference_indices + (slice(None),)]

            grids = {}
            grid_indices = {}
            for sol_idx, sol_name in enumerate(sol_names):
                state_key = state_names[changed_dim] if changed_dim >= 0 else state_names[-1]
                grids[sol_name], grid_indices[sol_name] = _refineGridWithIndices(
                    solGrids[sol_name],
                    ref_solution[sol_idx],
                    ΔL[(sol_name, state_key)],
                    ΔU[(sol_name, state_key)]
                )

        gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
        FSample = _evaluate_F_with_indices(F, gridsND, grid_indices, state_vals, kwargs)
        fGrid = pd.DataFrame(FSample, index=gridsND)

        root, success = _solveWithGridExpansionWithIndices(
            F, grids, grid_indices, solGrids, fGrid, state_vals=state_vals, maxExpand=maxExpand, **kwargs
        )
        roots[current_indices + (slice(None),)] = root
        root_types[current_indices + (slice(None),)] = 'root' if success else 'nn'

    interior = bool(np.all(root_types == 'root'))
    return {
        'x': roots,
        'status': True,
        'type': root_types,
        'interior': interior,
    }
