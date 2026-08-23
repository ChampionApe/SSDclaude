import numpy as np
import pandas as pd
from itertools import product
from numpy.lib.stride_tricks import sliding_window_view


def interpRootsFromNDGrid(X_samples, F_samples, tol=1e-6, method="multilinear", 
                          bracket="auto", newton_tol=1e-12, max_iter=50):
    """
    Approximate roots of F(X) = 0 using pre-computed grid samples via interpolation.
    
    Uses multilinear interpolation within grid cells and Newton's method on the
    interpolant for accurate root finding. Does not evaluate F(X) beyond samples.
    
    Parameters
    ----------
    X_samples : array_like, shape (M, N)
        Sample points in N-dimensional space where F has been evaluated.
        Must form a structured Cartesian grid.
    F_samples : array_like, shape (M, N)
        Function values at X_samples. Must be square system: N inputs → N outputs.
    tol : float, optional
        Tolerance for considering points near zero as roots. Default is 1e-6.
    method : {"multilinear", "edge"}, optional
        "multilinear": Use full multilinear interpolation + Newton (accurate).
        "edge": Use simple edge-based linear interpolation (fast, less accurate).
    bracket : {"auto", "corner", "pm"}, optional
        Cell bracketing strategy (for multilinear method):
        "auto": Try Poincaré-Miranda face test, then corner sign test.
        "corner": Each component has both signs among 2^N corners.
        "pm": Poincaré-Miranda weak face test.
    newton_tol : float, optional
        Tolerance for Newton's method on interpolant. Default is 1e-12.
    max_iter : int, optional
        Maximum Newton iterations. Default is 50.
    
    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'x': list of ndarray
            List of approximate root locations where F(X) ≈ 0.
            Each root is an N-dimensional array.
        - 'status': bool
            True if at least one root was found, False otherwise.
    
    Notes
    -----
    - Requires structured Cartesian grid (use meshgrid or similar)
    - For square systems only (N inputs, N outputs)
    - Multilinear method finds one root per bracketing cell
    - Edge method may find multiple roots per cell but less accurate
    
    Examples
    --------
    >>> # 2D example: find intersection of x^2 + y^2 = 1 and x = y
    >>> x = np.linspace(-2, 2, 30)
    >>> y = np.linspace(-2, 2, 30)
    >>> X, Y = np.meshgrid(x, y, indexing='ij')
    >>> X_samples = np.column_stack([X.ravel(), Y.ravel()])
    >>> 
    >>> def F(x): return np.array([x[0]**2 + x[1]**2 - 1, x[0] - x[1]])
    >>> F_samples = np.array([F(pt) for pt in X_samples])
    >>> 
    >>> roots = interpRootsFromNDGrid(X_samples, F_samples, method="multilinear")
    >>> # Should find roots near [±1/√2, ±1/√2]
    """
    X_samples = np.atleast_2d(X_samples)
    F_samples = np.atleast_2d(F_samples)
    
    M, N = X_samples.shape
    M_f, K = F_samples.shape
    
    if M != M_f:
        raise ValueError("X_samples and F_samples must have same number of points.")
    if N != K:
        raise ValueError("Must be square system: N inputs and N outputs.")
    
    # Extract grid structure
    if not _is_structured_grid(X_samples, N):
        raise ValueError("X_samples must form a structured Cartesian grid.")
    
    grids_1d = [np.unique(X_samples[:, i]) for i in range(N)]
    grid_shape = tuple(len(g) for g in grids_1d)
    
    # Reshape to N-D grid
    Y = F_samples.reshape(grid_shape + (N,))
    
    if method == "multilinear":
        roots = _find_roots_multilinear(grids_1d, Y, tol, bracket, newton_tol, max_iter)
    elif method == "edge":
        roots = _find_roots_edge_based(grids_1d, Y, tol)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return {'x': roots, 'status': len(roots) > 0}


def interpRootFromNDGrid(X_samples, F_samples, tol=1e-6, method="multilinear",
                         bracket="auto", newton_tol=1e-12, max_iter=50):
    """
    Approximate a single root of F(X) = 0 using pre-computed grid samples via interpolation.
    
    Similar to interpRootsFromNDGrid but stops after finding the first root.
    
    Parameters
    ----------
    X_samples : array_like, shape (M, N)
        Sample points in N-dimensional space where F has been evaluated.
        Must form a structured Cartesian grid.
    F_samples : array_like, shape (M, N)
        Function values at X_samples. Must be square system: N inputs → N outputs.
    tol : float, optional
        Tolerance for considering points near zero as roots. Default is 1e-6.
    method : {"multilinear", "edge"}, optional
        "multilinear": Use full multilinear interpolation + Newton (accurate).
        "edge": Use simple edge-based linear interpolation (fast, less accurate).
    bracket : {"auto", "corner", "pm"}, optional
        Cell bracketing strategy (for multilinear method).
    newton_tol : float, optional
        Tolerance for Newton's method on interpolant. Default is 1e-12.
    max_iter : int, optional
        Maximum Newton iterations. Default is 50.
    
    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'x': ndarray or None
            Approximate root location where F(X) ≈ 0, or None if no root found.
        - 'status': bool
            True if root was found, False otherwise.
    """
    X_samples = np.atleast_2d(X_samples)
    F_samples = np.atleast_2d(F_samples)
    
    M, N = X_samples.shape
    M_f, K = F_samples.shape
    
    if M != M_f:
        raise ValueError("X_samples and F_samples must have same number of points.")
    if N != K:
        raise ValueError("Must be square system: N inputs and N outputs.")
    
    # Extract grid structure
    if not _is_structured_grid(X_samples, N):
        raise ValueError("X_samples must form a structured Cartesian grid.")
    
    grids_1d = [np.unique(X_samples[:, i]) for i in range(N)]
    grid_shape = tuple(len(g) for g in grids_1d)
    
    # Reshape to N-D grid
    Y = F_samples.reshape(grid_shape + (N,))
    
    if method == "multilinear":
        root = _find_root_multilinear(grids_1d, Y, tol, bracket, newton_tol, max_iter)
    elif method == "edge":
        root = _find_root_edge_based(grids_1d, Y, tol)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return {'x': root, 'status': root is not None}


def interpRootFromNDGridOrNearest(X_samples, F_samples, tol=1e-6, method="multilinear",
                                   bracket="auto", newton_tol=1e-12, max_iter=50):
    """
    Find a single root of F(X) = 0, or return nearest sample point if no root found.
    
    First attempts to find a root using interpolation via interpRootFromNDGrid.
    If no root is found, returns the sample point with minimum |F(X)|.
    
    Parameters
    ----------
    X_samples : array_like, shape (M, N)
        Sample points in N-dimensional space where F has been evaluated.
        Must form a structured Cartesian grid.
    F_samples : array_like, shape (M, N)
        Function values at X_samples. Must be square system: N inputs → N outputs.
    tol : float, optional
        Tolerance for considering points near zero as roots. Default is 1e-6.
    method : {"multilinear", "edge"}, optional
        Root-finding method. Default is "multilinear".
    bracket : {"auto", "corner", "pm"}, optional
        Cell bracketing strategy. Default is "auto".
    newton_tol : float, optional
        Tolerance for Newton's method. Default is 1e-12.
    max_iter : int, optional
        Maximum Newton iterations. Default is 50.
    
    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'x': ndarray
            Either an interpolated root or the sample point with minimum |F(X)|.
        - 'status': bool
            Always True (a solution is always returned).
        - 'type': {'root', 'nn'}
            'root' if interpolated root was found, 'nn' if nearest neighbor.
    """
    # Try to find a root via interpolation
    result = interpRootFromNDGrid(X_samples, F_samples, tol=tol, method=method,
                                  bracket=bracket, newton_tol=newton_tol, max_iter=max_iter)
    
    if result['status']:
        return {'x': result['x'], 'status': True, 'type': 'root'}
    
    # No root found - return nearest neighbor (sample with minimum norm)
    F_samples = np.atleast_2d(F_samples)
    norms = np.linalg.norm(F_samples, axis=1)
    min_idx = np.argmin(norms)
    
    X_samples = np.atleast_2d(X_samples)
    return {'x': X_samples[min_idx], 'status': True, 'type': 'nn'}


def interpRootFromPandasGrid(fGrid, tol=1e-6, method="multilinear",
                             bracket="auto", newton_tol=1e-12, max_iter=50):
    """
    Find a single root of F(X) = 0 using samples provided as a pandas DataFrame with MultiIndex.
    
    Similar to interpRootsFromPandasGrid but stops after finding the first root.
    
    Parameters
    ----------
    fGrid : pd.DataFrame
        DataFrame with:
        - MultiIndex with N levels, each level representing one input variable (x_0, x_1, ..., x_{N-1})
        - N columns, each representing one output component (f_0, f_1, ..., f_{N-1})
        - Index must form a complete Cartesian product of the coordinate values
        - Values are the function evaluations F(X)
    tol : float, optional
        Tolerance for bracketing tests. Default is 1e-6.
    method : {"multilinear", "edge"}, optional
        Root-finding method. Default is "multilinear" (accurate).
    bracket : {"auto", "corner", "pm"}, optional
        Cell bracketing strategy. Default is "auto".
    newton_tol : float, optional
        Convergence tolerance for Newton's method. Default is 1e-12.
    max_iter : int, optional
        Maximum Newton iterations. Default is 50.
    
    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'x': ndarray or None
            Approximate root location where F(X) ≈ 0, or None if no root found.
        - 'status': bool
            True if root was found, False otherwise.
    
    Raises
    ------
    ValueError
        If fGrid is not a MultiIndex DataFrame or if it's not square (N inputs ≠ N outputs).
    """
    # Validate input
    if not isinstance(fGrid.index, pd.MultiIndex):
        raise ValueError("fGrid must have a MultiIndex index representing the N input dimensions.")
    
    N = fGrid.index.nlevels
    if fGrid.shape[1] != N:
        raise ValueError(
            f"fGrid must have exactly N columns to match N index levels (square system). "
            f"Found {N} index levels but {fGrid.shape[1]} columns."
        )
    
    # Extract grid structure and function values
    axes, Y = _grid_from_fgrid_nd(fGrid)
    
    if method == "multilinear":
        root = _find_root_multilinear(axes, Y, tol, bracket, newton_tol, max_iter)
    elif method == "edge":
        root = _find_root_edge_based(axes, Y, tol)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return {'x': root, 'status': root is not None}


def interpRootFromPandasGridOrNearest(fGrid, tol=1e-6, method="multilinear",
                                       bracket="auto", newton_tol=1e-12, max_iter=50):
    """
    Find a single root of F(X) = 0, or return nearest sample point if no root found.
    
    First attempts to find a root using interpolation via interpRootFromPandasGrid.
    If no root is found, returns the sample point with minimum |F(X)|.
    
    Parameters
    ----------
    fGrid : pd.DataFrame
        DataFrame with:
        - MultiIndex with N levels, each level representing one input variable
        - N columns, each representing one output component
        - Index must form a complete Cartesian product of the coordinate values
    tol : float, optional
        Tolerance for bracketing tests. Default is 1e-6.
    method : {"multilinear", "edge"}, optional
        Root-finding method. Default is "multilinear".
    bracket : {"auto", "corner", "pm"}, optional
        Cell bracketing strategy. Default is "auto".
    newton_tol : float, optional
        Tolerance for Newton's method. Default is 1e-12.
    max_iter : int, optional
        Maximum Newton iterations. Default is 50.
    
    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'x': ndarray
            Either an interpolated root or the sample point with minimum |F(X)|.
        - 'status': bool
            Always True (a solution is always returned).
        - 'type': {'root', 'nn'}
            'root' if interpolated root was found, 'nn' if nearest neighbor.
    
    Raises
    ------
    ValueError
        If fGrid is not a MultiIndex DataFrame or if it's not square.
    """
    # Try to find a root via interpolation
    result = interpRootFromPandasGrid(fGrid, tol=tol, method=method,
                                      bracket=bracket, newton_tol=newton_tol, max_iter=max_iter)
    
    if result['status']:
        return {'x': result['x'], 'status': True, 'type': 'root'}
    
    # No root found - return nearest neighbor (sample with minimum norm)
    F_samples = fGrid.to_numpy()
    norms = np.linalg.norm(F_samples, axis=1)
    min_idx = np.argmin(norms)
    
    # Extract the corresponding input coordinates
    N = fGrid.index.nlevels
    x_nearest = np.array([fGrid.index[min_idx][i] for i in range(N)])
    
    return {'x': x_nearest, 'status': True, 'type': 'nn'}


def interpRootFromNDGridOrNearestWithBoundary(X_samples, F_samples, tol=1e-6, method="multilinear",
                                               bracket="auto", newton_tol=1e-12, max_iter=50):
    """
    Find a single root of F(X) = 0, or return nearest sample point with boundary information.
    
    First attempts to find a root using interpolation via interpRootFromNDGrid.
    If successful, returns (root, True).
    If no root is found, returns (nearest_neighbor, boundary_flags) where boundary_flags
    is an integer array indicating boundary direction for each dimension.
    
    Parameters
    ----------
    X_samples : array_like, shape (M, N)
        Sample points in N-dimensional space where F has been evaluated.
        Must form a structured Cartesian grid.
    F_samples : array_like, shape (M, N)
        Function values at X_samples. Must be square system: N inputs → N outputs.
    tol : float, optional
        Tolerance for considering points near zero as roots. Default is 1e-6.
    method : {"multilinear", "edge"}, optional
        Root-finding method. Default is "multilinear".
    bracket : {"auto", "corner", "pm"}, optional
        Cell bracketing strategy. Default is "auto".
    newton_tol : float, optional
        Tolerance for Newton's method. Default is 1e-12.
    max_iter : int, optional
        Maximum Newton iterations. Default is 50.
    
    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'x': ndarray
            Either an interpolated root or the sample point with minimum |F(X)|.
        - 'status': bool
            Always True (a solution is always returned).
        - 'type': {'root', 'nn'}
            'root' if interpolated root was found, 'nn' if nearest neighbor.
        - 'boundary': ndarray or None
            If type is 'nn': integer array of shape (N,) with values:
            -1 = at lower boundary, 0 = interior, +1 = at upper boundary.
            If type is 'root': None.
    """
    X_samples = np.atleast_2d(X_samples)
    F_samples = np.atleast_2d(F_samples)
    
    # Try to find a root via interpolation
    result = interpRootFromNDGrid(X_samples, F_samples, tol=tol, method=method,
                                  bracket=bracket, newton_tol=newton_tol, max_iter=max_iter)
    
    if result['status']:
        return {'x': result['x'], 'status': True, 'type': 'root', 'boundary': None}
    
    # No root found - find nearest neighbor
    norms = np.linalg.norm(F_samples, axis=1)
    min_idx = np.argmin(norms)
    x_nearest = X_samples[min_idx]
    
    N = X_samples.shape[1]
    boundary_flags = np.zeros(N, dtype=int)

    grids_1d = [np.unique(X_samples[:, i]) for i in range(N)]
    spans = [(g[0], g[-1], g[-1] - g[0] + 1e-14) for g in grids_1d]

    for i, (grid_min, grid_max, span) in enumerate(spans):
        scale = 1e-14 * span
        at_lower = np.abs(x_nearest[i] - grid_min) < scale
        at_upper = np.abs(x_nearest[i] - grid_max) < scale
        if at_lower:
            boundary_flags[i] = -1
        elif at_upper:
            boundary_flags[i] = 1
        # else: remains 0 (interior)

    return {'x': x_nearest, 'status': True, 'type': 'nn', 'boundary': boundary_flags}


def interpRootFromPandasGridOrNearestWithBoundary(fGrid, tol=1e-6, method="multilinear",
                                                   bracket="auto", newton_tol=1e-12, max_iter=50):
    """
    Find a single root of F(X) = 0, or return nearest sample point with boundary information.
    
    First attempts to find a root using interpolation via interpRootFromPandasGrid.
    If successful, returns (root, True).
    If no root is found, returns (nearest_neighbor, boundary_flags) where boundary_flags
    is an integer array indicating boundary direction for each dimension.
    
    Parameters
    ----------
    fGrid : pd.DataFrame
        DataFrame with:
        - MultiIndex with N levels, each level representing one input variable
        - N columns, each representing one output component
        - Index must form a complete Cartesian product of the coordinate values
    tol : float, optional
        Tolerance for bracketing tests. Default is 1e-6.
    method : {"multilinear", "edge"}, optional
        Root-finding method. Default is "multilinear".
    bracket : {"auto", "corner", "pm"}, optional
        Cell bracketing strategy. Default is "auto".
    newton_tol : float, optional
        Tolerance for Newton's method. Default is 1e-12.
    max_iter : int, optional
        Maximum Newton iterations. Default is 50.
    
    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'x': ndarray
            Either an interpolated root or the sample point with minimum |F(X)|.
        - 'status': bool
            Always True (a solution is always returned).
        - 'type': {'root', 'nn'}
            'root' if interpolated root was found, 'nn' if nearest neighbor.
        - 'boundary': ndarray or None
            If type is 'nn': integer array of shape (N,) with values:
            -1 = at lower boundary, 0 = interior, +1 = at upper boundary.
            If type is 'root': None.
    
    Raises
    ------
    ValueError
        If fGrid is not a MultiIndex DataFrame or if it's not square.
    """
    # Try to find a root via interpolation
    result = interpRootFromPandasGrid(fGrid, tol=tol, method=method,
                                      bracket=bracket, newton_tol=newton_tol, max_iter=max_iter)
    
    if result['status']:
        return {'x': result['x'], 'status': True, 'type': 'root', 'boundary': None}
    
    # No root found - find nearest neighbor
    F_samples = fGrid.to_numpy()
    norms = np.linalg.norm(F_samples, axis=1)
    min_idx = np.argmin(norms)
    
    # Extract the corresponding input coordinates
    N = fGrid.index.nlevels
    x_nearest = np.array([fGrid.index[min_idx][i] for i in range(N)])
    
    # Determine boundary status for each dimension
    boundary_flags = np.zeros(N, dtype=int)
    
    # Extract grid bounds for each dimension
    for dim in range(N):
        dim_values = fGrid.index.get_level_values(dim).unique()
        grid_min = float(dim_values.min())
        grid_max = float(dim_values.max())
        
        # Check if nearest neighbor is at boundary in this dimension
        x_dim = float(fGrid.index[min_idx][dim])
        # Consider at boundary if within numerical tolerance of min or max
        at_lower = np.abs(x_dim - grid_min) < 1e-14 * (grid_max - grid_min + 1e-14)
        at_upper = np.abs(x_dim - grid_max) < 1e-14 * (grid_max - grid_min + 1e-14)
        if at_lower:
            boundary_flags[dim] = -1
        elif at_upper:
            boundary_flags[dim] = 1
        # else: remains 0 (interior)
    
    return {'x': x_nearest, 'status': True, 'type': 'nn', 'boundary': boundary_flags}


def interpRootsFromPandasGrid(fGrid, tol=1e-6, method="multilinear", 
                               bracket="auto", newton_tol=1e-12, max_iter=50):
    """
    Find roots of F(X) = 0 using samples provided as a pandas DataFrame with MultiIndex.
    
    Parameters
    ----------
    fGrid : pd.DataFrame
        DataFrame with:
        - MultiIndex with N levels, each level representing one input variable (x_0, x_1, ..., x_{N-1})
        - N columns, each representing one output component (f_0, f_1, ..., f_{N-1})
        - Index must form a complete Cartesian product of the coordinate values
        - Values are the function evaluations F(X)
    tol : float, optional
        Tolerance for bracketing tests. Default is 1e-6.
    method : {"multilinear", "edge"}, optional
        Root-finding method. Default is "multilinear" (accurate).
    bracket : {"auto", "corner", "pm"}, optional
        Cell bracketing strategy. Default is "auto".
    newton_tol : float, optional
        Convergence tolerance for Newton's method. Default is 1e-12.
    max_iter : int, optional
        Maximum Newton iterations. Default is 50.
    
    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'x': list of ndarray
            List of approximate root locations (each is an N-dimensional array).
        - 'status': bool
            True if at least one root was found, False otherwise.
    
    Raises
    ------
    ValueError
        If fGrid is not a MultiIndex DataFrame or if it's not square (N inputs ≠ N outputs).
    
    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> 
    >>> # Create sample data for 2D system
    >>> x = np.linspace(-2, 2, 15)
    >>> y = np.linspace(-2, 2, 15)
    >>> index = pd.MultiIndex.from_product([x, y], names=['x', 'y'])
    >>> 
    >>> # Evaluate F(x,y) = [x^2 + y^2 - 1, x - y] at grid points
    >>> F_vals = np.array([
    ...     [pt[0]**2 + pt[1]**2 - 1, pt[0] - pt[1]] 
    ...     for pt in index
    ... ])
    >>> 
    >>> fGrid = pd.DataFrame(F_vals, index=index, columns=['f1', 'f2'])
    >>> roots = interpRootsFromPandasGrid(fGrid)
    """
    # Validate input
    if not isinstance(fGrid.index, pd.MultiIndex):
        raise ValueError("fGrid must have a MultiIndex index representing the N input dimensions.")
    
    N = fGrid.index.nlevels
    if fGrid.shape[1] != N:
        raise ValueError(
            f"fGrid must have exactly N columns to match N index levels (square system). "
            f"Found {N} index levels but {fGrid.shape[1]} columns."
        )
    
    # Extract grid structure and function values
    axes, Y = _grid_from_fgrid_nd(fGrid)
    
    # Reconstruct X_samples for compatibility (optional, mainly for reference)
    # The main work is done internally with axes and Y
    
    if method == "multilinear":
        roots = _find_roots_multilinear(axes, Y, tol, bracket, newton_tol, max_iter)
    elif method == "edge":
        roots = _find_roots_edge_based(axes, Y, tol)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return {'x': roots, 'status': len(roots) > 0}


def _grid_from_fgrid_nd(fGrid):
    """
    Extract grid structure from a pandas DataFrame with MultiIndex.
    
    Parameters
    ----------
    fGrid : pd.DataFrame
        MultiIndex DataFrame where each index level represents one input dimension
        and columns represent output components.
    
    Returns
    -------
    axes : list of ndarray
        List of N 1D sorted arrays of coordinates along each axis.
    Y : ndarray, shape (*grid_shape, N)
        N-dimensional grid of function values reshaped to match grid structure.
    """
    if not isinstance(fGrid.index, pd.MultiIndex):
        raise ValueError("fGrid must have a MultiIndex.")
    
    N = fGrid.index.nlevels
    if fGrid.shape[1] != N:
        raise ValueError(
            f"Square system required: number of columns must equal number of index levels. "
            f"Found {N} levels but {fGrid.shape[1]} columns."
        )
    
    # Sort by index
    fGrid_sorted = fGrid.sort_index()
    
    # Extract unique sorted coordinate values along each dimension
    axes = []
    for lvl in range(N):
        vals = fGrid_sorted.index.get_level_values(lvl).unique()
        axes.append(np.asarray(sorted(vals.astype(float))))
    
    # Build the full Cartesian product MultiIndex
    full_index = pd.MultiIndex.from_product(axes, names=fGrid_sorted.index.names)
    
    # Reindex to ensure we have all points in the correct order
    fGrid_full = fGrid_sorted.reindex(full_index)
    
    # Check for missing points
    if fGrid_full.isnull().values.any():
        raise ValueError(
            "fGrid is missing points from the full Cartesian product. "
            "All grid points must be present in the DataFrame."
        )
    
    # Reshape to N-dimensional grid
    grid_shape = tuple(len(a) for a in axes)
    F_values = fGrid_full.to_numpy()  # shape: (prod(grid_shape), N)
    Y = F_values.reshape(grid_shape + (N,))
    
    return axes, Y


def _is_structured_grid(X_samples, N):
    """Check if samples form a structured Cartesian grid."""
    try:
        unique_counts = [len(np.unique(X_samples[:, i])) for i in range(N)]
        return np.prod(unique_counts) == len(X_samples)
    except:
        return False


def _multilinear_value_and_jac(cell_vals, s):
    """
    Evaluate multilinear interpolant and Jacobian at local coords s ∈ [0,1]^N.
    
    Parameters
    ----------
    cell_vals : ndarray, shape (2,)*N + (N,)
        Function values at 2^N cell corners.
    s : ndarray, shape (N,)
        Local coordinates in [0,1]^N.
    
    Returns
    -------
    f : ndarray, shape (N,)
        Interpolated value at s.
    J : ndarray, shape (N, N)
        Jacobian ∂f/∂s at s.
    """
    N = cell_vals.shape[-1]
    
    # Interpolate value: iteratively blend along each dimension
    A = cell_vals
    for m in range(N):
        A = (1.0 - s[m]) * A[0, ...] + s[m] * A[1, ...]
    f = A
    
    # Jacobian: for each dimension d, take derivative along d, interpolate others
    J = np.empty((N, N), dtype=float)
    for d in range(N):
        G = cell_vals
        for m in range(N):
            if m == d:
                G = G[1, ...] - G[0, ...]  # derivative
            else:
                G = (1.0 - s[m]) * G[0, ...] + s[m] * G[1, ...]
        J[:, d] = G
    
    return f, J


def _newton_on_cell(cell_vals, tol=1e-12, max_iter=50, max_backtracks=8):
    """
    Newton's method on multilinear interpolant within cell.
    
    Solves for s ∈ [0,1]^N where interpolant equals zero.
    Uses line search with backtracking and projection onto [0,1]^N.
    
    Returns
    -------
    success : bool
    s : ndarray, shape (N,)
        Local coordinates if successful.
    info : dict
        Iteration details.
    """
    N = cell_vals.shape[-1]
    s = np.full(N, 0.5, dtype=float)  # Start at cell center
    
    f, J = _multilinear_value_and_jac(cell_vals, s)
    res = float(np.max(np.abs(f)))
    
    if res <= tol:
        return True, s, {"iterations": 0, "residual": res}
    
    for it in range(1, max_iter + 1):
        # Solve J·δ = -f (with Tikhonov regularization if singular)
        try:
            delta = np.linalg.solve(J, -f)
        except np.linalg.LinAlgError:
            JTJ = J.T @ J
            lam = 1e-14 * np.trace(JTJ) / N if np.isfinite(np.trace(JTJ)) else 1e-12
            delta = np.linalg.solve(JTJ + lam * np.eye(N), -J.T @ f)
        
        # Line search with backtracking
        step = 1.0
        s_best, res_best = None, np.inf
        
        for _ in range(max_backtracks + 1):
            s_try = np.clip(s + step * delta, 0.0, 1.0)
            f_try, _ = _multilinear_value_and_jac(cell_vals, s_try)
            r_try = float(np.max(np.abs(f_try)))
            
            if r_try < res_best:
                s_best, res_best = s_try, r_try
            if r_try <= 0.999 * res:  # Sufficient decrease
                break
            step *= 0.5
        
        if s_best is None:
            return False, s, {"iterations": it, "residual": res, "reason": "line_search_fail"}
        
        s, res = s_best, res_best
        if res <= tol:
            return True, s, {"iterations": it, "residual": res}
        
        f, J = _multilinear_value_and_jac(cell_vals, s)
    
    return False, s, {"iterations": max_iter, "residual": res, "reason": "max_iter"}


def _pm_face_test(cell_vals, eps=0.0):
    """
    Poincaré-Miranda weak face test: check if ranges on opposite faces straddle zero.
    
    For each component k and axis d, the values on opposite faces should have
    overlapping ranges that include zero.
    """
    N = cell_vals.shape[-1]
    for k in range(N):
        face0 = np.take(cell_vals[..., k], indices=0, axis=k)
        face1 = np.take(cell_vals[..., k], indices=1, axis=k)
        
        # Check if ranges straddle zero
        ok = (np.max(face0) >= -eps and np.min(face1) <= eps) and \
             (np.max(face1) >= -eps and np.min(face0) <= eps)
        if not ok:
            return False
    return True


def _corner_sign_test(cell_vals, eps=0.0):
    """Check if each component has both positive and negative values among corners."""
    N = cell_vals.shape[-1]
    corners = cell_vals.reshape(-1, N)  # (2^N, N)
    mn = corners.min(axis=0)
    mx = corners.max(axis=0)
    return bool(np.all(mn <= eps) and np.all(mx >= -eps))


def _get_cell_block(Y, idx):
    """Extract (2,)*N + (N,) block of values at cell corners."""
    slices = tuple(slice(i, i+2) for i in idx) + (slice(None),)
    return Y[slices]


def _find_root_multilinear(grids_1d, Y, tol, bracket, newton_tol, max_iter):
    """
    Find a single root using multilinear interpolation + Newton within bracketing cells.
    
    Returns the first successfully found root, or None if no root found.
    """
    N = len(grids_1d)
    
    # Special case: 1D optimization
    if N == 1:
        return _find_root_1d(grids_1d[0], Y.squeeze())
    
    grid_shape = Y.shape[:-1]
    
    # Select bracketing test based on strategy
    if bracket == "auto":
        tests = [("pm", _pm_face_test), ("corner", _corner_sign_test)]
    elif bracket == "corner":
        tests = [("corner", _corner_sign_test)]
    elif bracket == "pm":
        tests = [("pm", _pm_face_test)]
    else:
        raise ValueError(f"Unknown bracket strategy: {bracket}")

    grid_deltas = [np.diff(g) for g in grids_1d]
    
    for idx in product(*[range(n-1) for n in grid_shape]):
        cell_vals = _get_cell_block(Y, idx)
        if not any(test_fn(cell_vals, tol) for _, test_fn in tests):
            continue

        success, s, info = _newton_on_cell(cell_vals, tol=newton_tol, max_iter=max_iter)
        if success:
            x_root = np.array([
                grids_1d[d][idx[d]] + s[d] * grid_deltas[d][idx[d]]
                for d in range(N)
            ])
            return x_root

    return None


def _find_roots_multilinear(grids_1d, Y, tol, bracket, newton_tol, max_iter):
    """
    Find roots using multilinear interpolation + Newton within bracketing cells.
    
    This is the high-accuracy method inspired by ndlinearGridSearch.py.
    """
    N = len(grids_1d)
    
    # Special case: 1D optimization
    if N == 1:
        return _find_roots_1d(grids_1d[0], Y.squeeze(), tol=tol)
    
    grid_shape = Y.shape[:-1]
    roots = []
    
    # Select bracketing test based on strategy
    if bracket == "auto":
        tests = [("pm", _pm_face_test), ("corner", _corner_sign_test)]
    elif bracket == "corner":
        tests = [("corner", _corner_sign_test)]
    elif bracket == "pm":
        tests = [("pm", _pm_face_test)]
    else:
        raise ValueError(f"Unknown bracket strategy: {bracket}")

    grid_deltas = [np.diff(g) for g in grids_1d]

    bracketing_cells = []
    for idx in product(*[range(n-1) for n in grid_shape]):
        cell_vals = _get_cell_block(Y, idx)
        for _, test_fn in tests:
            if test_fn(cell_vals, tol):
                score = np.sum(np.abs(cell_vals))
                bracketing_cells.append((score, idx, cell_vals))
                break

    # Solve for root in each bracketing cell
    for score, idx, cell_vals in bracketing_cells:
        success, s, info = _newton_on_cell(cell_vals, tol=newton_tol, max_iter=max_iter)

        if success:
            x_root = np.array([
                grids_1d[d][idx[d]] + s[d] * grid_deltas[d][idx[d]]
                for d in range(N)
            ])
            roots.append(x_root)

    if roots:
        roots = _remove_duplicate_roots(roots, tol * 10)

    return roots


def _find_root_edge_based(grids_1d, Y, tol):
    """
    Find a single root using simple edge-based linear interpolation.
    
    Returns the first root found, or None if no root found.
    """
    N = len(grids_1d)
    
    # Special case: 1D optimization
    if N == 1:
        return _find_root_1d(grids_1d[0], Y.squeeze())
    
    grid_shape = Y.shape[:-1]

    vertex_offsets = list(product(*[[0, 1] for _ in range(N)]))
    edge_pairs = [
        (i, j)
        for i in range(len(vertex_offsets))
        for j in range(i + 1, len(vertex_offsets))
        if sum(a != b for a, b in zip(vertex_offsets[i], vertex_offsets[j])) == 1
    ]

    for k in range(N):
        F_k = Y[..., k]
        windows = sliding_window_view(F_k, window_shape=(2,) * N)

        for idx in product(*[range(n-1) for n in grid_shape]):
            block = windows[idx]
            base = np.array(idx)

            for i, j in edge_pairs:
                f1 = block[vertex_offsets[i]]
                f2 = block[vertex_offsets[j]]

                if f1 * f2 < 0:
                    x1 = np.array([grids_1d[d][base[d] + vertex_offsets[i][d]] for d in range(N)])
                    x2 = np.array([grids_1d[d][base[d] + vertex_offsets[j][d]] for d in range(N)])
                    alpha = -f1 / (f2 - f1)
                    return x1 + alpha * (x2 - x1)

                if abs(f1) < tol:
                    return np.array([grids_1d[d][base[d] + vertex_offsets[i][d]] for d in range(N)])

    return None


def _find_roots_edge_based(grids_1d, Y, tol):
    """
    Find roots using simple edge-based linear interpolation.
    
    This is the original fast method - checks all edges for sign changes.
    Less accurate but may find more candidate roots.
    """
    N = len(grids_1d)
    
    # Special case: 1D optimization
    if N == 1:
        return _find_roots_1d(grids_1d[0], Y.squeeze(), tol=tol)
    
    grid_shape = Y.shape[:-1]
    roots = []

    vertex_offsets = list(product(*[[0, 1] for _ in range(N)]))
    edge_pairs = [
        (i, j)
        for i in range(len(vertex_offsets))
        for j in range(i + 1, len(vertex_offsets))
        if sum(a != b for a, b in zip(vertex_offsets[i], vertex_offsets[j])) == 1
    ]

    for k in range(N):
        F_k = Y[..., k]
        windows = sliding_window_view(F_k, window_shape=(2,) * N)

        for idx in product(*[range(n-1) for n in grid_shape]):
            block = windows[idx]
            base = np.array(idx)

            for i, j in edge_pairs:
                f1 = block[vertex_offsets[i]]
                f2 = block[vertex_offsets[j]]

                if f1 * f2 < 0:
                    x1 = np.array([grids_1d[d][base[d] + vertex_offsets[i][d]] for d in range(N)])
                    x2 = np.array([grids_1d[d][base[d] + vertex_offsets[j][d]] for d in range(N)])
                    alpha = -f1 / (f2 - f1)
                    roots.append(x1 + alpha * (x2 - x1))
                elif abs(f1) < tol:
                    roots.append(np.array([grids_1d[d][base[d] + vertex_offsets[i][d]] for d in range(N)]))

    if roots:
        roots = _remove_duplicate_roots(roots, tol * 10)

    return roots


def _remove_duplicate_roots(roots, tol):
    """Remove duplicate roots within tolerance."""
    if len(roots) == 0:
        return roots
    
    unique_roots = [roots[0]]
    for root in roots[1:]:
        if not any(np.linalg.norm(root - ur) < tol for ur in unique_roots):
            unique_roots.append(root)
    
    return unique_roots


# ============================================================================
# SPECIALIZED 1D ROOT FINDING (N=1 optimization)
# ============================================================================

def _find_roots_1d(x_grid, f_vals, tol=1e-6, method="linear"):
    """
    Fast 1D root finding using vectorized sign change detection.
    
    Uses numpy vectorized operations (np.sign, np.diff) for efficient
    detection of sign changes without Python loops.
    
    Parameters
    ----------
    x_grid : ndarray, shape (M,)
        Sorted 1D grid of x values.
    f_vals : ndarray, shape (M,)
        Function values at x_grid.
    tol : float
        Tolerance for considering values near zero as roots.
    method : {"linear", "quadratic"}
        Interpolation method for root approximation.
    
    Returns
    -------
    roots : list of ndarray
        List of root locations (each is shape (1,) for consistency).
    """
    roots = []
    
    # Check for roots at grid points (vectorized)
    at_root = np.abs(f_vals) < tol
    if np.any(at_root):
        root_indices = np.where(at_root)[0]
        roots.extend([np.array([x_grid[i]]) for i in root_indices])
    
    # Find sign changes using vectorized operations
    signs = np.sign(f_vals)
    # Product of consecutive signs: negative means sign change
    sign_products = signs[:-1] * signs[1:]
    # Find indices where sign changes occur (and not at roots)
    change_indices = np.where(
        (sign_products < 0) & 
        (np.abs(f_vals[:-1]) >= tol) & 
        (np.abs(f_vals[1:]) >= tol)
    )[0]
    
    if len(change_indices) > 0:
        if method == "linear":
            # Vectorized linear interpolation
            f1 = f_vals[change_indices]
            f2 = f_vals[change_indices + 1]
            x1 = x_grid[change_indices]
            x2 = x_grid[change_indices + 1]
            
            alpha = -f1 / (f2 - f1)
            x_roots = x1 + alpha * (x2 - x1)
            roots.extend([np.array([x]) for x in x_roots])
        
        elif method == "quadratic":
            # Quadratic interpolation (partial vectorization)
            for i in change_indices:
                if i > 0:
                    x0, x1, x2 = x_grid[i-1], x_grid[i], x_grid[i+1]
                    f0, f1, f2 = f_vals[i-1], f_vals[i], f_vals[i+1]
                    
                    try:
                        # Inverse quadratic interpolation
                        L0 = ((x1 - x_grid[i]) * (x2 - x_grid[i])) / ((x0 - x1) * (x0 - x2))
                        L1 = ((x0 - x_grid[i]) * (x2 - x_grid[i])) / ((x1 - x0) * (x1 - x2))
                        L2 = ((x0 - x_grid[i]) * (x1 - x_grid[i])) / ((x2 - x0) * (x2 - x1))
                        
                        denom = L0/f0 + L1/f1 + L2/f2
                        if abs(denom) > 1e-14:
                            x_root = (L0*x0/f0 + L1*x1/f1 + L2*x2/f2) / denom
                            if x1 <= x_root <= x2:
                                roots.append(np.array([x_root]))
                            else:
                                # Fall back to linear
                                alpha = -f1 / (f2 - f1)
                                x_root = x1 + alpha * (x2 - x1)
                                roots.append(np.array([x_root]))
                        else:
                            # Fall back to linear
                            alpha = -f1 / (f2 - f1)
                            x_root = x1 + alpha * (x2 - x1)
                            roots.append(np.array([x_root]))
                    except:
                        # Fall back to linear on any error
                        alpha = -f1 / (f2 - f1)
                        x_root = x1 + alpha * (x2 - x1)
                        roots.append(np.array([x_root]))
                else:
                    # First interval, use linear
                    f1, f2 = f_vals[i], f_vals[i+1]
                    x1, x2 = x_grid[i], x_grid[i+1]
                    alpha = -f1 / (f2 - f1)
                    x_root = x1 + alpha * (x2 - x1)
                    roots.append(np.array([x_root]))
    
    # Remove duplicates
    if roots:
        roots = _remove_duplicate_roots(roots, tol * 10)
    
    return roots


def _find_root_1d(x_grid, f_vals, tol = 1e-12):
    """
    Fast 1D root finding - returns first root found.
    
    Uses vectorized sign change detection for efficiency.
    
    Parameters
    ----------
    x_grid : ndarray, shape (M,)
        Sorted 1D grid of x values.
    f_vals : ndarray, shape (M,)
        Function values at x_grid.
    tol : float
        Tolerance for considering values near zero as roots.
    method : {"linear", "quadratic"}
        Interpolation method for root approximation.
    
    Returns
    -------
    root : ndarray or None
        Root location (shape (1,)) or None if no root found.
    """    
    # Find sign changes using vectorized operations
    signs = np.sign(f_vals)
    sign_products = signs[:-1] * signs[1:]
    change_indices = np.where(sign_products < 0)[0]
    
    if len(change_indices) > 0:
        # Use first sign change
        i = change_indices[0]
        f1, f2 = f_vals[i], f_vals[i + 1]
        x1, x2 = x_grid[i], x_grid[i + 1]
        
        # Linear interpolation (fast)
        alpha = -f1 / (f2 - f1)
        x_root = x1 + alpha * (x2 - x1)
        return np.array([x_root])

    if any(abs(f_vals)<tol):
        return x_grid[abs(f_vals)<tol]

    return None


# ============================================================================
# VECTORIZED 1D ROOT FINDING (N functions on same grid)
# ============================================================================

def interpRoot1DVectorized(x_grid, f_vals):
    """
    Find N roots on the same 1D grid using fully vectorized operations.
    
    Identifies roots for N independent 1D functions evaluated on the same
    x_grid. All numpy operations are vectorized across all N functions
    simultaneously for maximum efficiency.
    
    Parameters
    ----------
    x_grid : ndarray, shape (M,)
        Sorted 1D grid of x values.
    f_vals : ndarray, shape (M, N)
        Function values for N functions at x_grid points.
        If 1D, treated as a single function.
    tol : float, optional
        Tolerance for considering values near zero as roots. Default is 1e-6.
    
    Returns
    -------
    roots : ndarray, shape (N,)
        Root location for each function. NaN if no root found.
    
    Notes
    -----
    - All N functions are evaluated on the same x_grid.
    - Returns first root found for each function.
    - Uses linear interpolation between grid points.
    
    Examples
    --------
    >>> x = np.linspace(-2, 2, 50)
    >>> f1 = x**2 - 1        # Roots near ±1
    >>> f2 = x**3 - 1        # Root near 1
    >>> f3 = np.sin(x)       # Roots near 0, ±π
    >>> f_vals = np.column_stack([f1, f2, f3])
    >>> roots = interpRoot1DVectorized(x, f_vals)
    >>> # roots array contains one root for each of the 3 functions
    """
    N = f_vals.shape[1]
    roots = np.full(N, np.nan)

    # Sign change:
    signs = np.sign(f_vals)  # shape (M, N)    
    sign_products = signs[:-1, :] * signs[1:, :]  # shape (M-1, N)
    has_sign_change = sign_products < 0  # shape (M-1, N), dtype bool

    # Find first sign change index for each column
    # argmax returns index of first True (1) in each column
    first_sign_change_idx = np.argmax(has_sign_change, axis=0)  # shape (N,)
    
    # Check which columns have any sign change
    has_any_change = np.any(has_sign_change, axis=0)  # shape (N,)
    
    # Extract and interpolate roots for columns with sign changes
    if np.any(has_any_change):
        valid_cols = np.where(has_any_change)[0]
        indices = first_sign_change_idx[valid_cols]
        
        # Use advanced indexing to extract values
        x1 = x_grid[indices]
        x2 = x_grid[indices + 1]
        f1 = f_vals[indices, valid_cols]
        f2 = f_vals[indices + 1, valid_cols]
        
        # Linear interpolation
        roots[valid_cols] = x1 + f1 * (x2 - x1) / (f1 - f2)
    
    return roots

# ============================================================================
# BATCH ROOT FINDING (multiple sample sets)
# ============================================================================

def interpRootsFromNDGridBatch(X_samples_list, F_samples_list, tol=1e-6, 
                               method="multilinear", bracket="auto", 
                               newton_tol=1e-12, max_iter=50, 
                               parallel=False, n_jobs=-1):
    """
    Batch version: find roots for multiple sample sets.
    
    Solves the root finding problem for multiple different sample sets,
    optionally in parallel for improved performance.
    
    Parameters
    ----------
    X_samples_list : list of array_like
        List of K sample point arrays, each shape (M_i, N).
    F_samples_list : list of array_like
        List of K function value arrays, each shape (M_i, N).
    tol : float, optional
        Tolerance for considering points near zero as roots. Default is 1e-6.
    method : {"multilinear", "edge"}, optional
        Root-finding method. Default is "multilinear".
    bracket : {"auto", "corner", "pm"}, optional
        Cell bracketing strategy. Default is "auto".
    newton_tol : float, optional
        Tolerance for Newton's method. Default is 1e-12.
    max_iter : int, optional
        Maximum Newton iterations. Default is 50.
    parallel : bool, optional
        If True, use parallel processing. Default is False.
    n_jobs : int, optional
        Number of parallel jobs. -1 uses all available cores. Default is -1.
    
    Returns
    -------
    results : list of dict
        List of K result dictionaries, each with keys:
        - 'x': list of ndarray (root locations)
        - 'status': bool (True if roots found)
    
    Examples
    --------
    >>> # Find roots for multiple different grids
    >>> X1, F1 = create_grid_1(...)
    >>> X2, F2 = create_grid_2(...)
    >>> results = interpRootsFromNDGridBatch([X1, X2], [F1, F2], parallel=True)
    """
    if len(X_samples_list) != len(F_samples_list):
        raise ValueError("X_samples_list and F_samples_list must have same length.")
    
    if not parallel:
        # Sequential processing
        results = []
        for X_samples, F_samples in zip(X_samples_list, F_samples_list):
            result = interpRootsFromNDGrid(
                X_samples, F_samples, tol=tol, method=method, 
                bracket=bracket, newton_tol=newton_tol, max_iter=max_iter
            )
            results.append(result)
        return results
    
    else:
        # Parallel processing
        try:
            from joblib import Parallel, delayed
        except ImportError:
            raise ImportError(
                "Parallel processing requires joblib. Install with: pip install joblib"
            )
        
        def solve_single(X_samples, F_samples):
            return interpRootsFromNDGrid(
                X_samples, F_samples, tol=tol, method=method,
                bracket=bracket, newton_tol=newton_tol, max_iter=max_iter
            )
        
        results = Parallel(n_jobs=n_jobs)(
            delayed(solve_single)(X, F) 
            for X, F in zip(X_samples_list, F_samples_list)
        )
        
        return results


def interpRootFromNDGridBatch(X_samples_list, F_samples_list, tol=1e-6,
                               method="multilinear", bracket="auto",
                               newton_tol=1e-12, max_iter=50,
                               parallel=False, n_jobs=-1):
    """
    Batch version: find single root for multiple sample sets.
    
    Solves the root finding problem for multiple different sample sets,
    stopping after finding the first root in each set. Optionally parallel.
    
    Parameters
    ----------
    X_samples_list : list of array_like
        List of K sample point arrays, each shape (M_i, N).
    F_samples_list : list of array_like
        List of K function value arrays, each shape (M_i, N).
    tol : float, optional
        Tolerance for considering points near zero as roots. Default is 1e-6.
    method : {"multilinear", "edge"}, optional
        Root-finding method. Default is "multilinear".
    bracket : {"auto", "corner", "pm"}, optional
        Cell bracketing strategy. Default is "auto".
    newton_tol : float, optional
        Tolerance for Newton's method. Default is 1e-12.
    max_iter : int, optional
        Maximum Newton iterations. Default is 50.
    parallel : bool, optional
        If True, use parallel processing. Default is False.
    n_jobs : int, optional
        Number of parallel jobs. -1 uses all available cores. Default is -1.
    
    Returns
    -------
    results : list of dict
        List of K result dictionaries, each with keys:
        - 'x': ndarray or None (root location)
        - 'status': bool (True if root found)
    """
    if len(X_samples_list) != len(F_samples_list):
        raise ValueError("X_samples_list and F_samples_list must have same length.")
    
    if not parallel:
        # Sequential processing
        results = []
        for X_samples, F_samples in zip(X_samples_list, F_samples_list):
            result = interpRootFromNDGrid(
                X_samples, F_samples, tol=tol, method=method,
                bracket=bracket, newton_tol=newton_tol, max_iter=max_iter
            )
            results.append(result)
        return results
    
    else:
        # Parallel processing
        try:
            from joblib import Parallel, delayed
        except ImportError:
            raise ImportError(
                "Parallel processing requires joblib. Install with: pip install joblib"
            )
        
        def solve_single(X_samples, F_samples):
            return interpRootFromNDGrid(
                X_samples, F_samples, tol=tol, method=method,
                bracket=bracket, newton_tol=newton_tol, max_iter=max_iter
            )
        
        results = Parallel(n_jobs=n_jobs)(
            delayed(solve_single)(X, F)
            for X, F in zip(X_samples_list, F_samples_list)
        )
        
        return results


def interpRootsFromPandasGridBatch(fGrid_list, tol=1e-6, method="multilinear",
                                   bracket="auto", newton_tol=1e-12, max_iter=50,
                                   parallel=False, n_jobs=-1):
    """
    Batch version: find roots for multiple pandas DataFrame grids.
    
    Parameters
    ----------
    fGrid_list : list of pd.DataFrame
        List of K DataFrames, each with MultiIndex and N columns.
    tol : float, optional
        Tolerance for bracketing tests. Default is 1e-6.
    method : {"multilinear", "edge"}, optional
        Root-finding method. Default is "multilinear".
    bracket : {"auto", "corner", "pm"}, optional
        Cell bracketing strategy. Default is "auto".
    newton_tol : float, optional
        Tolerance for Newton's method. Default is 1e-12.
    max_iter : int, optional
        Maximum Newton iterations. Default is 50.
    parallel : bool, optional
        If True, use parallel processing. Default is False.
    n_jobs : int, optional
        Number of parallel jobs. -1 uses all available cores. Default is -1.
    
    Returns
    -------
    results : list of dict
        List of K result dictionaries, each with keys:
        - 'x': list of ndarray (root locations)
        - 'status': bool (True if roots found)
    """
    if not parallel:
        # Sequential processing
        results = []
        for fGrid in fGrid_list:
            result = interpRootsFromPandasGrid(
                fGrid, tol=tol, method=method, bracket=bracket,
                newton_tol=newton_tol, max_iter=max_iter
            )
            results.append(result)
        return results
    
    else:
        # Parallel processing
        try:
            from joblib import Parallel, delayed
        except ImportError:
            raise ImportError(
                "Parallel processing requires joblib. Install with: pip install joblib"
            )
        
        def solve_single(fGrid):
            return interpRootsFromPandasGrid(
                fGrid, tol=tol, method=method, bracket=bracket,
                newton_tol=newton_tol, max_iter=max_iter
            )
        
        results = Parallel(n_jobs=n_jobs)(
            delayed(solve_single)(fGrid) for fGrid in fGrid_list
        )
        
        return results


def interpRootFromPandasGridBatch(fGrid_list, tol=1e-6, method="multilinear",
                                  bracket="auto", newton_tol=1e-12, max_iter=50,
                                  parallel=False, n_jobs=-1):
    """
    Batch version: find single root for multiple pandas DataFrame grids.
    
    Parameters
    ----------
    fGrid_list : list of pd.DataFrame
        List of K DataFrames, each with MultiIndex and N columns.
    tol : float, optional
        Tolerance for bracketing tests. Default is 1e-6.
    method : {"multilinear", "edge"}, optional
        Root-finding method. Default is "multilinear".
    bracket : {"auto", "corner", "pm"}, optional
        Cell bracketing strategy. Default is "auto".
    newton_tol : float, optional
        Tolerance for Newton's method. Default is 1e-12.
    max_iter : int, optional
        Maximum Newton iterations. Default is 50.
    parallel : bool, optional
        If True, use parallel processing. Default is False.
    n_jobs : int, optional
        Number of parallel jobs. -1 uses all available cores. Default is -1.
    
    Returns
    -------
    results : list of dict
        List of K result dictionaries, each with keys:
        - 'x': ndarray or None (root location)
        - 'status': bool (True if root found)
    """
    if not parallel:
        # Sequential processing
        results = []
        for fGrid in fGrid_list:
            result = interpRootFromPandasGrid(
                fGrid, tol=tol, method=method, bracket=bracket,
                newton_tol=newton_tol, max_iter=max_iter
            )
            results.append(result)
        return results
    
    else:
        # Parallel processing
        try:
            from joblib import Parallel, delayed
        except ImportError:
            raise ImportError(
                "Parallel processing requires joblib. Install with: pip install joblib"
            )
        
        def solve_single(fGrid):
            return interpRootFromPandasGrid(
                fGrid, tol=tol, method=method, bracket=bracket,
                newton_tol=newton_tol, max_iter=max_iter
            )
        
        results = Parallel(n_jobs=n_jobs)(
            delayed(solve_single)(fGrid) for fGrid in fGrid_list
        )
        
        return results
