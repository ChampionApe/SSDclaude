"""
Class-based interface for grid solving with improved efficiency and flexibility.

The SolveGrid class provides:
- Reusable configuration for repeated solves with parameter variations
- Automatic method selection based on problem structure
- Precomputed global index mappings for efficient parameter subsetting
"""

import numpy as np
import pandas as pd
from itertools import product
from ..InterpRoots import interpRootFromPandasGridOrNearestWithBoundary
from ..InterpRoots import interpRoot1DVectorized


# ============================================================================
# Helper Functions
# ============================================================================

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


# ============================================================================
# SolveGrid Class
# ============================================================================


class SolveGrid:
    """
    Class-based grid solver with efficient parameter management and index precomputation.
    
    Parameters
    ----------
    F : callable
        Objective function to solve F(x) = 0
    solGrids : dict
        Global solution grids {var_name: 1d_array}
    stateGrids : dict, optional
        State grids {state_name: 1d_array}. If None, single-root mode.
    ΔL : dict, optional
        Lower refinement counts {(sol_var, state_var): int}. If None, no refinement.
    ΔU : dict, optional
        Upper refinement counts {(sol_var, state_var): int}. If None, no refinement.
    solGrid0 : dict, optional
        Initial refined grids for first iteration
    maxExpand : int
        Maximum grid expansion iterations
    fallback_to_nn : bool, optional
        If True, use nearest neighbor as fallback when no root found. If False,
        return None/NaN for failed cases. Default is True. Note: methods using
        grid refinement or expansion always require nearest neighbor regardless
        of this setting.
    **kwargs
        Additional arguments passed to F
        
    Examples
    --------
    >>> solver = SolveGrid(F, solGrids, stateGrids, ΔL, ΔU)
    >>> result = solver.solve()  # Auto-selects method
    >>> 
    >>> # Update refinement and re-solve
    >>> solver.update(ΔL=new_ΔL)
    >>> result = solver.solve()
    >>>
    >>> # Solve with index tracking for precomputed parameters
    >>> result = solver.solveLoopCartesianNDIdx(precomputed_params=params)
    >>>
    >>> # Vectorized 1D without nearest neighbor fallback
    >>> solver = SolveGrid(F, solGrids, stateGrids, fallback_to_nn=False)
    >>> result = solver.solve()  # Returns NaN where no root found
    """
    
    def __init__(self, F, solGrids, stateGrids=None, ΔL=None, ΔU=None, 
                 solGrid0=None, maxExpand=5, fallback_to_nn=True, **kwargs):
        self.F = F
        self.solGrids = solGrids
        self.stateGrids = stateGrids
        self.ΔL = ΔL
        self.ΔU = ΔU
        self.solGrid0 = solGrid0
        self.maxExpand = maxExpand
        self.fallback_to_nn = fallback_to_nn
        self.kwargs = kwargs
        
        # Precompute metadata
        self.sol_names = list(solGrids.keys())
        self.n_sol = len(self.sol_names)
        
        # Precompute global gridsND for full grid evaluations
        self.global_gridsND = pd.MultiIndex.from_product(
            self.solGrids.values(), 
            names=self.sol_names
        )
        
        if stateGrids is not None:
            self.state_names = list(stateGrids.keys())
            self.n_states = len(self.state_names)
            self._precompute_mappings()
            self._precompute_traversal()
        else:
            self.state_names = []
            self.n_states = 0
            self.traversal = None
            
        # Cache for result arrays (reused if solving repeatedly with same structure)
        self._result_cache = None

    def __getstate__(self):
        """Return pickle-safe state by removing non-serializable callable F."""
        state = self.__dict__.copy()
        state['F'] = None
        return state

    def __setstate__(self, state):
        """Restore instance state from pickle payload."""
        self.__dict__.update(state)
            
    def _precompute_mappings(self):
        """Precompute global index mappings for efficient parameter subsetting."""
        # Create global MultiIndex from Cartesian product of solution grids
        # This matches how grids are created in solve methods
        global_idx_arrays = [np.arange(len(self.solGrids[name])) for name in self.sol_names]
        self.global_idx_multiindex = pd.MultiIndex.from_product(
            global_idx_arrays, 
            names=self.sol_names
        )
        
        # Extract index grids for each variable (1D arrays for np.ix_ usage)
        self.global_idx_grids = {
            name: np.unique(self.global_idx_multiindex.get_level_values(name).values)
            for name in self.sol_names
        }
        
        # Precompute shapes for Cartesian products
        self.global_shape = tuple(len(self.solGrids[name]) for name in self.sol_names)
        self.n_global_points = len(self.global_idx_multiindex)
        
        # Linear indices are just sequential (MultiIndex is already in correct order)
        self.global_linear_indices = np.arange(self.n_global_points).reshape(self.global_shape)

        # Precompute combined solution + state grids for vectorized 1D solver
        # This is used by solveVectorized1D for efficient evaluation
        if self._select_method() == 'vectorized1d':
            self.combined_gridsND = pd.MultiIndex.from_product(
                list(self.solGrids.values()) + list(self.stateGrids.values()),
                names = self.sol_names + self.state_names
            )

        # Combination of state grids:
        if self.n_states == 1:
            k, v = next(iter(self.stateGrids.items()))
            self.global_stateIdx = pd.Index(v, name = k)
        else:
            self.global_stateIdx = pd.MultiIndex.from_product(self.stateGrids.values(), names = self.stateGrids.keys())
    
    def _precompute_traversal(self):
        """Precompute traversal order for state grid iteration."""
        self.traversal = _createTraversalOrder(self.stateGrids)
        self.n_state_points = self.traversal.shape[0]
        
    def _allocate_result_arrays(self):
        """Allocate or reuse result arrays for storing solutions."""
        result_shape = list(self.state_shape) + [self.n_sol]
        
        if self._result_cache is None or self._result_cache['shape'] != tuple(result_shape):
            self._result_cache = {
                'shape': tuple(result_shape),
                'roots': np.empty(result_shape, dtype=float),
                'types': np.empty(result_shape, dtype=object)
            }
        return self._result_cache['roots'], self._result_cache['types']
        
    def _extract_state_vals(self, current_indices):
        """Extract state values dict for given indices."""
        return {
            self.state_names[i]: self.stateGrids[self.state_names[i]][current_indices[i]]
            for i in range(self.n_states)
        }
        
    def _get_initial_grids_and_indices(self):
        """Get grids and indices for first iteration."""
        if self.solGrid0 is None:
            grids = self.solGrids
            # Use precomputed global index grids
            grid_indices = self.global_idx_grids.copy()
        else:
            # solGrid0 contains array slices of solGrids
            grids = self.solGrid0
            # Compute indices for initial grid subset
            grid_indices = {
                name: np.searchsorted(self.solGrids[name], grids[name])
                for name in grids.keys()
            }
        return grids, grid_indices
        
    def _refine_grids_with_indices(self, ref_solution, changed_dim):
        """Refine grids based on reference solution and changed state dimension."""
        grids = {}
        grid_indices = {}
        
        # Determine which state variable changed
        state_key = self.state_names[changed_dim] if changed_dim >= 0 else self.state_names[-1]
        
        for sol_idx, sol_name in enumerate(self.sol_names):
            grids[sol_name], grid_indices[sol_name] = _refineGridWithIndices(
                self.solGrids[sol_name],
                ref_solution[sol_idx],
                self.ΔL[(sol_name, state_key)],
                self.ΔU[(sol_name, state_key)]
            )
        return grids, grid_indices
        
    def _package_result(self, roots, root_types):
        """Package solution arrays into result dict."""
        roots, root_types = self._apply_fallback_to_nn(roots, root_types)
        return {
            'x': roots,
            'status': True,
            'type': root_types,
            'interior': bool(np.all(root_types == 'root'))
        }

    def _apply_fallback_to_nn(self, roots, root_types):
        """Apply fallback_to_nn behavior to roots and root_types."""
        if self.fallback_to_nn:
            return roots, root_types

        roots_arr = np.array(roots, copy=True)
        root_types_arr = np.array(root_types, dtype=object, copy=True)

        if root_types_arr.size == 1:
            if root_types_arr.ravel()[0] == 'nn':
                roots_arr = np.full_like(roots_arr, np.nan, dtype=float)
                root_types_arr = np.array(['none'], dtype=object)
            return roots_arr, root_types_arr

        nn_mask = root_types_arr == 'nn'
        if np.any(nn_mask):
            roots_arr = roots_arr.astype(float, copy=False)
            roots_arr[nn_mask] = np.nan
            root_types_arr[nn_mask] = 'none'

        return roots_arr, root_types_arr

    def flatten_solution(self, roots, as_dataframe=False):
        """Flatten roots to align with global_stateIdx ordering."""
        if self.stateGrids is None:
            raise ValueError("stateGrids required to flatten solutions")

        roots_arr = np.asarray(roots)
        expected_shape = self.state_shape + (self.n_sol,)

        if roots_arr.shape != expected_shape:
            raise ValueError(
                f"Expected roots shape {expected_shape}, got {roots_arr.shape}"
            )

        roots_flat = roots_arr.reshape(self.n_state_points, self.n_sol)
        if as_dataframe:
            return pd.DataFrame(roots_flat, index=self.global_stateIdx, columns=self.sol_names)
        return roots_flat

    @property
    def state_shape(self):
        """Shape tuple of state grid lengths; use to reshape solution vectors into ND state arrays."""
        return tuple(len(v) for v in self.stateGrids.values())

    def get_levels(self, idx=None):
        """Return dict {state_name: array} of level values from idx (default: self.global_stateIdx)."""
        idx = self.global_stateIdx if idx is None else idx
        return {k: idx.get_level_values(k).to_numpy() for k in idx.names}

    def get_levels_stacked(self, idx=None):
        """Return column-stacked array of shape (n_points, n_states) from idx (default: self.global_stateIdx)."""
        idx = self.global_stateIdx if idx is None else idx
        return np.column_stack([idx.get_level_values(k).to_numpy() for k in idx.names])

    def estimate_refinement_from_full_solution(self, roots, percentile=95, margin=1, min_width=0):
        """
        Estimate ΔL and ΔU from a full solveLoopSimple solution.

        Returns
        -------
        ΔL : dict
            Lower refinement counts {(sol_var, state_var): int}
        ΔU : dict
            Upper refinement counts {(sol_var, state_var): int}
        """
        if self.stateGrids is None:
            raise ValueError("stateGrids required to estimate refinement")

        roots_arr = np.asarray(roots)
        expected_shape = self.state_shape + (self.n_sol,)
        if roots_arr.shape != expected_shape:
            raise ValueError(
                f"Expected roots shape {expected_shape}, got {roots_arr.shape}"
            )

        deltaL = {}
        deltaU = {}

        for sol_idx, sol_name in enumerate(self.sol_names):
            sol_grid = self.solGrids[sol_name]
            sol_vals = roots_arr[..., sol_idx]
            idx_grid = np.full(self.state_shape, np.nan, dtype=float)
            
            # Determine valid mask: only actual roots, not nearest neighbors or failed cases
            valid_mask = ~np.isnan(sol_vals)
            
            if np.any(valid_mask):
                idx_grid[valid_mask] = np.searchsorted(sol_grid, sol_vals[valid_mask])

            for state_dim, state_name in enumerate(self.state_names):
                delta = np.diff(idx_grid, axis=state_dim)

                pos = delta[(delta > 0) & ~np.isnan(delta)]
                neg = delta[(delta < 0) & ~np.isnan(delta)]

                if pos.size > 0:
                    q_pos = np.nanpercentile(pos, percentile)
                    u = int(np.ceil(q_pos)) + margin
                else:
                    u = 0

                if neg.size > 0:
                    q_neg = np.nanpercentile(-neg, percentile)
                    l = int(np.ceil(q_neg)) + margin
                else:
                    l = 0

                deltaU[(sol_name, state_name)] = max(u, min_width)
                deltaL[(sol_name, state_name)] = max(l, min_width)

        return {'ΔL': deltaL, 'ΔU': deltaU}
    
    def update(self, **kwargs):
        """Update solver parameters and recompute mappings if needed."""
        recompute = False
        
        for key, value in kwargs.items():
            if key in ['solGrids', 'stateGrids']:
                recompute = True
            setattr(self, key, value)
            
        if recompute:
            self.sol_names = list(self.solGrids.keys())
            self.n_sol = len(self.sol_names)
            self.global_gridsND = pd.MultiIndex.from_product(
                self.solGrids.values(), 
                names=self.sol_names
            )
            
            if self.stateGrids is not None:
                self.state_names = list(self.stateGrids.keys())
                self.n_states = len(self.state_names)
                self._precompute_mappings()
                self._precompute_traversal()
            
            # Invalidate result cache on structural changes
            self._result_cache = None
            
    def solve(self, method='auto', **kwargs):
        """
        Solve with automatic or explicit method selection.
        
        Parameters
        ----------
        method : str
            'auto': automatic selection based on parameters
            'single': use solveSingleRoot
            'vectorized1d': use solveVectorized1D (1D, no refinement)
            'vectorized1d_nd': use solveVectorized1D_ND (1D, no refinement, explicit combinations)
            'loop': use solveLoopCartesianND (with refinement)
            'simple': use solveLoopSimple (no refinement)
            'idx': use solveLoopCartesianNDIdx (with indices)
        **kwargs
            Override parameters for this solve call
            
        Returns
        -------
        result : dict
            Solution dictionary with keys 'x', 'status', 'type', 'interior'
        """
        # Merge kwargs with stored kwargs
        solve_kwargs = self.kwargs.copy()
        solve_kwargs.update(kwargs)
        
        if method == 'auto':
            method = self._select_method()
            
        if method == 'single':
            return self.solveSingleRoot(**solve_kwargs)
        elif method == 'vectorized1d':
            return self.solveVectorized1D(**solve_kwargs)
        elif method == 'vectorized1d_nd':
            return self.solveVectorized1D_ND(**solve_kwargs)
        elif method == 'loop':
            return self.solveLoopCartesianND(**solve_kwargs)
        elif method == 'simple':
            return self.solveLoopSimple(**solve_kwargs)
        elif method == 'idx':
            return self.solveLoopCartesianNDIdx(**solve_kwargs)
        else:
            raise ValueError(f"Unknown method: {method}")
            
    def _select_method(self):
        """Automatically select solving method based on parameters."""
        if self.stateGrids is None:
            return 'single'
        # Check for vectorized 1D case: single solution variable, no refinement
        elif (self.n_sol == 1 and 
              self.ΔL is None and self.ΔU is None and self.solGrid0 is None):
            return 'vectorized1d'
        elif self.ΔL is None or self.ΔU is None:
            return 'simple'
        else:
            return 'loop'
            
    def _solveSingleRoot1D(self, grids, state_vals, solve_kwargs):
        """Auxiliary method for solving single 1D root using sign-change detection.
        
        Parameters
        ----------
        grids : dict
            Solution grids (refined or full)
        state_vals : dict or None
            State variable values
        solve_kwargs : dict
            Additional kwargs for F
            
        Returns
        -------
        result : dict
            Solution dictionary with keys 'x', 'status', 'type', 'interior'
        """
        solName = self.sol_names[0]
        x_grid = grids[solName]
        
        # Evaluate F on grid
        gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
        FSample = _evaluate_F(self.F, gridsND, grids, state_vals, solve_kwargs)
        f_vals = FSample.ravel()
        
        # Use 1D root finding (expects shape (M, 1) for single state)
        root = interpRoot1DVectorized(x_grid, f_vals.reshape(-1, 1))
        
        # Handle failed case - mark as 'nn', let _package_result handle fallback logic
        if np.isnan(root[0]):
            # Find x_grid point with minimum |f_vals| as nearest neighbor
            min_idx = np.argmin(np.abs(f_vals))
            root = x_grid[min_idx]
            root_type = 'nn'
        else:
            root = root[0]
            root_type = 'root'
        
        return self._package_result(root, np.array([root_type]))
    
    def solveSingleRoot(self, **kwargs):
        """Solve F(x)=0 for single state (no state grid traversal).
        
        For 1D problems (n_sol == 1), uses fast vectorized sign-change detection.
        For N-D problems, uses general interpolation with boundary-aware expansion.
        """
        solve_kwargs = self.kwargs.copy()
        solve_kwargs.update(kwargs)
        
        state_vals = solve_kwargs.pop('states', None)
        
        # Use initial grid or precomputed global grid
        if self.solGrid0 is not None:
            # solGrid0 contains array slices of solGrids
            grids = self.solGrid0
        else:
            grids = self.solGrids
        
        # Fast path for 1D problems: use sign-change detection
        if self.n_sol == 1:
            return self._solveSingleRoot1D(grids, state_vals, solve_kwargs)
        
        # General N-D case: use interpolation with expansion
        gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
        FSample = _evaluate_F(self.F, gridsND, grids, state_vals, solve_kwargs)
        fGrid = pd.DataFrame(FSample, index=gridsND)
        root, success = self._solve_with_expansion(grids, fGrid, state_vals, solve_kwargs)

        root_type = np.array(['root' if success else 'nn'])
        return self._package_result(root, root_type)
        
    def solveLoopCartesianND(self, **kwargs):
        """Solve F(x)=0 over Cartesian state grid with refinement."""
        if self.stateGrids is None:
            raise ValueError("stateGrids required for looping methods")
        if self.ΔL is None or self.ΔU is None:
            raise ValueError("ΔL and ΔU required for refinement")
            
        solve_kwargs = self.kwargs.copy()
        solve_kwargs.update(kwargs)
        
        # Use precomputed traversal and cached arrays
        roots, root_types = self._allocate_result_arrays()
        
        for point_idx in range(self.n_state_points):
            current_indices = tuple(self.traversal[point_idx, 0, :])
            reference_indices = tuple(self.traversal[point_idx, 1, :])
            
            state_vals = self._extract_state_vals(current_indices)
            
            if point_idx == 0:
                # First iteration: use solGrid0 or full global grids
                if self.solGrid0 is not None:
                    # solGrid0 contains array slices of solGrids
                    grids = self.solGrid0
                    gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
                else:
                    grids = self.solGrids
                    gridsND = self.global_gridsND  # Use precomputed!
            else:
                # Refine grids based on previous solution
                changed_dim = self._find_changed_dimension(current_indices, reference_indices)
                ref_solution = roots[reference_indices + (slice(None),)]
                
                # Determine which state variable changed to select appropriate ΔL/ΔU
                state_key = self.state_names[changed_dim] if changed_dim >= 0 else self.state_names[-1]
                
                grids = {}
                for sol_idx, sol_name in enumerate(self.sol_names):
                    grids[sol_name], _ = _refineGridWithIndices(
                        self.solGrids[sol_name],
                        ref_solution[sol_idx],
                        self.ΔL[(sol_name, state_key)],
                        self.ΔU[(sol_name, state_key)]
                    )
                gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
            
            # Evaluate and solve
            FSample = _evaluate_F(self.F, gridsND, grids, state_vals, solve_kwargs)
            fGrid = pd.DataFrame(FSample, index=gridsND)
            
            root, success = self._solve_with_expansion(grids, fGrid, state_vals, solve_kwargs)
            roots[current_indices + (slice(None),)] = root
            root_types[current_indices + (slice(None),)] = 'root' if success else 'nn'
        
        return self._package_result(roots, root_types)
        
    def solveVectorized1D_ND(self, **kwargs):
        """
        Solve F(x)=0 over state grid using vectorized 1D root finding.
        
        Optimized for the special case where:
        - Only 1 solution variable (1D problem)
        - No refinement needed (ΔL=ΔU=solGrid0=None)
        
        For best performance, F should accept:
        - Solution variable: 1D array of shape (M,)
        - states: dict of 1D arrays, each of shape (N_states,)
        And return array of shape (M, N_states) via broadcasting.
                
        Failed root finding behavior:
        - If fallback_to_nn=True: returns nearest grid point (minimum |F|)
        - If fallback_to_nn=False: returns NaN and marks type as 'none'
        """
        solve_kwargs = self.kwargs.copy()
        solve_kwargs.update(kwargs)

        solName = self.sol_names[0]
        x_grid  = self.solGrids[solName]

        # add to kwargs:
        f_kwargs = {solName: x_grid}
        f_kwargs['states'] = self.get_levels()
        f_kwargs.update(solve_kwargs)

        M, N_states = len(x_grid), len(self.global_stateIdx) # 
        try:
            # Try vectorized evaluation first
            FSample = self.F(**f_kwargs)
        except (TypeError, ValueError, IndexError) as e:
            f_vals = np.empty((M, N_states))
            f_kwargs_scalar = {solName: x_grid}
            f_kwargs_scalar.update(solve_kwargs)
            for state_idx in range(N_states):
                f_kwargs_scalar['states'] = dict(zip(self.global_stateIdx.names, self.global_stateIdx[state_idx]))
                FSample = self.F(**f_kwargs_scalar)
                f_vals[:, state_idx] = FSample.ravel()
        
        roots_flat = interpRoot1DVectorized(x_grid, f_vals)
        
        # Handle failed cases - fill with nearest neighbor, mark as 'nn'
        # _package_result will convert 'nn' -> 'none'/NaN if fallback_to_nn=False
        failed_mask = np.isnan(roots_flat)
        if np.any(failed_mask):
            abs_f = np.abs(f_vals)
            min_indices = np.argmin(abs_f, axis=0)
            roots_flat[failed_mask] = x_grid[min_indices[failed_mask]]
        
        root_types = np.where(failed_mask, 'nn', 'root')
        return self._package_result(roots_flat, root_types)
    
    def solveVectorized1D(self, **kwargs):
        """
        Alternative vectorized 1D root finding with explicit solution+state grid combinations.
        
        This is an alternative to solveVectorized1D_ND that creates a combined Cartesian grid
        of solution and state variables, passes all combinations to F explicitly, and uses
        unstack to reshape the output.
        
        Optimized for the special case where:
        - Only 1 solution variable (1D problem)
        - No refinement needed (ΔL=ΔU=solGrid0=None)
        
        For best performance, F should accept:
        - Solution variable: 1D array with solution variable broadcasted to length of cartesian grid of solution+state variables.
        - states: dict of 1D arrays with states broadcasted to length of cartesian grid of solution+state variables.
        And return array of shape (M*N_states,) where M = len(x_grid), N_states = number of state combinations.
                
        The output is unstacked to shape (M, N_states) for interpRoot1DVectorized.
        
        Failed root finding behavior:
        - If fallback_to_nn=True: returns nearest grid point (minimum |F|)
        - If fallback_to_nn=False: returns NaN and marks type as 'none'
        """
        solve_kwargs = self.kwargs.copy()
        solve_kwargs.update(kwargs)

        solName = self.sol_names[0]
        x_grid = self.solGrids[solName]
        
        # Use precomputed combined grids (solution + state variables)
        gridsND = self.combined_gridsND
        
        # Prepare kwargs with solution variable and states dictionary
        f_kwargs = {solName: gridsND.get_level_values(solName).values}
        f_kwargs['states'] = {name: gridsND.get_level_values(name).values for name in self.state_names}
        f_kwargs.update(solve_kwargs)

        M = len(x_grid)
        N_states = len(gridsND) // M

        try:
            # Evaluate F on the combined grid (returns flattened output)
            FSample = self.F(**f_kwargs)
            
            # Ensure FSample is 1D for DataFrame creation
            FSample_flat = np.asarray(FSample).ravel()
            
            # Reshape from (M*N_states,) to (M, N_states) using unstack
            # Unstack by solution variable, which gives shape (N_states, M), then transpose
            temp_df = pd.DataFrame({'f': FSample_flat}, index=gridsND)
            f_vals = temp_df['f'].unstack(level=solName).values.T
            
        except (TypeError, ValueError, IndexError) as e:
            # Fallback: evaluate point-by-point using precomputed gridsND
            f_vals = np.empty((M, N_states))
            f_kwargs_scalar = {solName: x_grid}
            f_kwargs_scalar.update(solve_kwargs)
            
            # Extract unique state combinations from gridsND (skip solution level)
            state_combos = gridsND.droplevel(solName).unique()
            
            for state_idx, state_vals_tuple in enumerate(state_combos):
                # Handle both single-state and multi-state cases
                if self.n_states == 1:
                    f_kwargs_scalar['states'] = {self.state_names[0]: state_vals_tuple}
                else:
                    f_kwargs_scalar['states'] = dict(zip(self.state_names, state_vals_tuple))
                FSample = self.F(**f_kwargs_scalar)
                f_vals[:, state_idx] = FSample.ravel()
        
        roots_flat = interpRoot1DVectorized(x_grid, f_vals)
        
        # Handle failed cases - fill with nearest neighbor, mark as 'nn'
        # _package_result will convert 'nn' -> 'none'/NaN if fallback_to_nn=False
        failed_mask = np.isnan(roots_flat)
        if np.any(failed_mask):
            abs_f = np.abs(f_vals)
            min_indices = np.argmin(abs_f, axis=0)
            roots_flat[failed_mask] = x_grid[min_indices[failed_mask]]
        
        root_types = np.where(failed_mask, 'nn', 'root')
        return self._package_result(roots_flat, root_types)
    
    def solveLoopSimple(self, **kwargs):
        """Solve F(x)=0 over Cartesian state grid without refinement."""
        if self.stateGrids is None:
            raise ValueError("stateGrids required for looping methods")
            
        solve_kwargs = self.kwargs.copy()
        solve_kwargs.update(kwargs)
        
        # Use precomputed traversal, global_gridsND, and cached arrays
        roots, root_types = self._allocate_result_arrays()
        
        for point_idx in range(self.n_state_points):
            current_indices = tuple(self.traversal[point_idx, 0, :])
            state_vals = self._extract_state_vals(current_indices)
            
            # Evaluate on full global grid (precomputed!)
            FSample = _evaluate_F(self.F, self.global_gridsND, self.solGrids, 
                                 state_vals, solve_kwargs)
            fGrid = pd.DataFrame(FSample, index=self.global_gridsND)
            
            # Solve without expansion (maxExpand=0)
            root, success = self._solve_with_expansion(self.solGrids, fGrid, 
                                                       state_vals, solve_kwargs)
            
            roots[current_indices + (slice(None),)] = root
            root_types[current_indices + (slice(None),)] = 'root' if success else 'nn'
        
        return self._package_result(roots, root_types)
        
    def solveLoopCartesianNDIdx(self, **kwargs):
        """
        Solve F(x)=0 over Cartesian state grid with index tracking.
        
        This method tracks grid indices and passes them to F, enabling efficient
        access to precomputed parameters aligned with global grid structure.
        
        Additional kwargs are passed to F and can include precomputed parameter arrays.
        """
        if self.stateGrids is None:
            raise ValueError("stateGrids required for looping methods")
        if self.ΔL is None or self.ΔU is None:
            raise ValueError("ΔL and ΔU required for refinement")
            
        solve_kwargs = self.kwargs.copy()
        solve_kwargs.update(kwargs)
        
        return self._solve_loop_idx(**solve_kwargs)
        
    def _solve_loop_idx(self, **kwargs):
        """Internal implementation of index-tracking loop solver."""
        # Optimized: use precomputed traversal and result arrays
        roots, root_types = self._allocate_result_arrays()
        
        for point_idx in range(self.n_state_points):
            current_indices = tuple(self.traversal[point_idx, 0, :])
            reference_indices = tuple(self.traversal[point_idx, 1, :])
            
            state_vals = self._extract_state_vals(current_indices)
            
            if point_idx == 0:
                grids, grid_indices = self._get_initial_grids_and_indices()
            else:
                changed_dim = self._find_changed_dimension(current_indices, reference_indices)
                ref_solution = roots[reference_indices + (slice(None),)]
                grids, grid_indices = self._refine_grids_with_indices(ref_solution, changed_dim)
                    
            gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
            FSample = _evaluate_F_with_indices(self.F, gridsND, grid_indices, state_vals, kwargs)
            fGrid = pd.DataFrame(FSample, index=gridsND)
            
            root, success = self._solve_with_expansion_idx(grids, grid_indices, fGrid, 
                                                           state_vals, kwargs)
            roots[current_indices + (slice(None),)] = root
            root_types[current_indices + (slice(None),)] = 'root' if success else 'nn'
            
        return self._package_result(roots, root_types)
        
    def _find_changed_dimension(self, current_indices, reference_indices):
        """Find which state dimension changed between current and reference."""
        for dim in range(self.n_states):
            if current_indices[dim] != reference_indices[dim]:
                return dim
        return -1
    
    def _solve_with_expansion(self, grids, fGrid, state_vals, kwargs):
        """Robust root finding with boundary-aware grid expansion."""
        result_dict = interpRootFromPandasGridOrNearestWithBoundary(fGrid)
        
        if result_dict['type'] == 'root':
            return result_dict['x'], True
        
        nearest_neighbor = result_dict['x']
        boundary_directions = result_dict['boundary']
        
        if not np.any(boundary_directions != 0):
            # No expansion possible - return nearest neighbor
            # _package_result will handle fallback_to_nn conversion
            return nearest_neighbor, False
        
        # Iteratively expand grid at boundaries
        for _ in range(self.maxExpand):
            grids = _expand_grids_by_one(grids, self.solGrids, boundary_directions)
            expanded_gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
            new_points = expanded_gridsND.difference(fGrid.index)
            
            if len(new_points) == 0:
                break
            
            # Evaluate at new points
            f_kwargs = {name: new_points.get_level_values(name).values for name in new_points.names}
            if state_vals is not None:
                f_kwargs['states'] = state_vals
            f_kwargs.update(kwargs)
            new_FSample = self.F(**f_kwargs)
            
            new_df = pd.DataFrame(new_FSample, index=new_points)
            fGrid = pd.concat([fGrid, new_df])
            
            result_dict = interpRootFromPandasGridOrNearestWithBoundary(fGrid)
            
            if result_dict['type'] == 'root':
                return result_dict['x'], True
            
            nearest_neighbor = result_dict['x']
            boundary_directions = result_dict['boundary']
            
            if not np.any(boundary_directions != 0):
                break

        # Return nearest neighbor - _package_result handles fallback_to_nn
        return nearest_neighbor, False
    
    def _solve_with_expansion_idx(self, grids, grid_indices, fGrid, state_vals, kwargs):
        """Boundary-aware expansion with index tracking."""
        result_dict = interpRootFromPandasGridOrNearestWithBoundary(fGrid)
        
        if result_dict['type'] == 'root':
            return result_dict['x'], True
        
        nearest_neighbor = result_dict['x']
        boundary_directions = result_dict['boundary']
        
        if not np.any(boundary_directions != 0):
            # No expansion possible - return nearest neighbor
            return nearest_neighbor, False
        
        for _ in range(self.maxExpand):
            grids = _expand_grids_by_one(grids, self.solGrids, boundary_directions)
            grid_indices = {name: np.searchsorted(self.solGrids[name], grids[name]) 
                           for name in grids.keys()}
            
            expanded_gridsND = pd.MultiIndex.from_product(grids.values(), names=grids.keys())
            new_points = expanded_gridsND.difference(fGrid.index)
            
            if len(new_points) == 0:
                break
            
            new_FSample = _evaluate_F_with_indices(self.F, new_points, grid_indices, state_vals, kwargs)
            new_df = pd.DataFrame(new_FSample, index=new_points)
            fGrid = pd.concat([fGrid, new_df])
            
            result_dict = interpRootFromPandasGridOrNearestWithBoundary(fGrid)
            
            if result_dict['type'] == 'root':
                return result_dict['x'], True
            
            nearest_neighbor = result_dict['x']
            boundary_directions = result_dict['boundary']
            
            if not np.any(boundary_directions != 0):
                break

        # Return nearest neighbor - _package_result handles fallback_to_nn
        return nearest_neighbor, False
    
    def get_linear_indices(self, grid_indices):
        """
        Convert grid indices to linear indices in raveled global grid.
        
        Parameters
        ----------
        grid_indices : dict
            Dict of 1D index arrays {var_name: indices}
            
        Returns
        -------
        linear_indices : ndarray
            1D array of linear indices into raveled global parameter arrays
            
        Examples
        --------
        >>> # For 2D case with shapes (100, 50)
        >>> grid_indices = {'x': [10, 11, 12], 'y': [5, 6]}
        >>> linear_idx = solver.get_linear_indices(grid_indices)
        >>> # Use to subset 1D parameter array: params_1d[linear_idx]
        """
        if self.n_sol == 1:
            return grid_indices[self.sol_names[0]]
            
        # Use pd.MultiIndex.from_product to get natural Cartesian ordering
        idx_arrays = [grid_indices[name] for name in self.sol_names]
        idx_multiindex = pd.MultiIndex.from_product(idx_arrays, names=self.sol_names)
        
        # Get linear positions by looking up in global index mapping
        linear_indices = self.global_idx_multiindex.get_indexer(idx_multiindex)
        
        return linear_indices
    
    def subset_1d_params(self, params_1d, grid_indices):
        return params_1d[self.get_linear_indices(grid_indices)]
        
    def subset_nd_params(self, params_nd, grid_indices):
        """
        Subset N-D parameter array using grid indices.
        
        Parameters
        ----------
        params_nd : ndarray
            N-D array with shape matching global grid structure
        grid_indices : dict
            Dict of 1D index arrays {var_name: indices}
            
        Returns
        -------
        subset : ndarray
            Subset of params_nd, raveled to 1D
            
        Examples
        --------
        >>> # params_2d has shape (100, 50) matching solGrids
        >>> grid_indices = {'x': [10, 11, 12], 'y': [5, 6]}
        >>> subset = solver.subset_nd_params(params_2d, grid_indices)
        >>> # subset has shape (6,) = 3*2, ready for use in F
        """
        idx_arrays = [grid_indices[name] for name in self.sol_names]
        return params_nd[np.ix_(*idx_arrays)].ravel()
        
    def __repr__(self):
        return (f"SolveGrid(n_sol={self.n_sol}, n_states={self.n_states}, "
                f"refinement={'yes' if self.ΔL is not None else 'no'}, "
                f"fallback_to_nn={self.fallback_to_nn})")
