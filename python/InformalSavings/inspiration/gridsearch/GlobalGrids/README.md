# GlobalGrids

Grid-based root solving with precomputed global grids and efficient parameter management.

## What it does
- Samples F on full Cartesian grids and interpolates roots
- Supports single-state and multi-state traversals with grid refinement
- Precomputes global grids and index mappings for efficiency
- Can expand grids directionally when boundary hits occur
- Provides both functional API (`solveSingleRoot`, `solveLoopCartesianND`) and class-based API (`SolveGrid`)

## Recommended: SolveGrid Class

The `SolveGrid` class provides an efficient interface for repeated solves with parameter variations:

```python
import numpy as np
from gridsearch.GlobalGrids import SolveGrid

# Define objective function
def F(x, y, states=None, **kwargs):
    a = states['a']
    b = states['b']
    F1 = x**2 - a
    F2 = y**2 - b
    return np.column_stack([F1, F2])

# Setup solver with refinement parameters
# ΔL and ΔU use tuple keys (sol_var, state_var) to specify refinement
# based on which state dimension is being traversed
solver = SolveGrid(
    F=F,
    solGrids={'x': np.linspace(-5, 5, 100), 'y': np.linspace(-5, 5, 80)},
    stateGrids={'a': np.array([5.0, 10.0]), 'b': np.array([2.0, 3.0])},
    ΔL={('x', 'a'): 2, ('x', 'b'): 2, ('y', 'a'): 2, ('y', 'b'): 2},
    ΔU={('x', 'a'): 2, ('x', 'b'): 2, ('y', 'a'): 2, ('y', 'b'): 2},
    maxExpand=5
)

# Solve - automatically selects best method
result = solver.solve()
print(result['x'])  # shape: (2, 2, 2) for states grid
print(result['y'])  # shape: (2, 2, 2)
```

### Available Methods

```python
# Simple evaluation on full global grid (no refinement)
result = solver.solveLoopSimple()

# Adaptive refinement (recommended)
result = solver.solveLoopCartesianND()

# With index tracking for precomputed parameters
result = solver.solveLoopCartesianNDIdx()

# Single state point
result = solver.solveSingleRoot(states={'a': 7.0, 'b': 2.5})
```

### Advantages of SolveGrid Class

- **Precomputation**: Global grids and traversal computed once at initialization
- **Reusability**: Update parameters and re-solve without recomputation
- **Result caching**: Repeated solves reuse allocated arrays
- **Index utilities**: Built-in methods for parameter subsetting

## Grid Refinement Parameters (ΔL and ΔU)

For methods with adaptive refinement, ΔL and ΔU control how many gridpoints to include around the previous solution when refining grids.

**Key Format**: Use tuple keys `(sol_var, state_var)` to specify different refinement amounts based on which state dimension is being traversed.

```python
# Example: 2 solution variables (x, y) and 2 state variables (a, b)
ΔL = {
    ('x', 'a'): 3,  # When 'a' changes, use 3 gridpoints below x
    ('x', 'b'): 2,  # When 'b' changes, use 2 gridpoints below x
    ('y', 'a'): 2,  # When 'a' changes, use 2 gridpoints below y
    ('y', 'b'): 3,  # When 'b' changes, use 3 gridpoints below y
}

ΔU = {
    ('x', 'a'): 3,  # When 'a' changes, use 3 gridpoints above x
    ('x', 'b'): 2,  # When 'b' changes, use 2 gridpoints above x
    ('y', 'a'): 2,  # When 'a' changes, use 2 gridpoints above y
    ('y', 'b'): 3,  # When 'b' changes, use 3 gridpoints above y
}
```

**Why tuple keys?** When traversing a state grid, solutions change differently depending on which state variable varies. Using `(sol_var, state_var)` keys allows finer control over refinement strategy.

## F Signature Requirements

Your function `F` must:
- Accept solution variables as keyword arguments
- Return array shaped (M, N) where:
  - M = number of gridpoints in the Cartesian product
  - N = number of equations/outputs (must equal number of solution variables)
- Optionally accept `states` dict with current state values
- For index-based methods: accept `idxs` dict with 1D index arrays

```python
def F(x, y, states=None, **kwargs):
    # Extract state values
    a = states['a'] if states is not None else 0
    b = states['b'] if states is not None else 0
    
    # Compute equations
    F1 = x**2 - a
    F2 = y**2 - b
    
    # Return (M, N) array
    return np.column_stack([F1, F2])
```

## Using Index-Based Methods with Precomputed Parameters

When you have expensive-to-compute parameters precomputed on the full global grid, use `solveLoopCartesianNDIdx` to avoid recomputation during grid refinement.

### Example 1: 2D Precomputed Parameters

```python
import numpy as np
from gridsearch.GlobalGrids import SolveGrid

# 1. Define global solution grids
solGrids = {
    'x': np.linspace(0, 10, 100),
    'y': np.linspace(0, 5, 50)
}

# 2. Precompute expensive parameters on full grid
# Shape: (100, 50) matching (len(solGrids['x']), len(solGrids['y']))
expensive_params = np.exp(solGrids['x'][:, None] + solGrids['y'][None, :])

# 3. Define objective function that uses indices
def F(x, y, idxs=None, states=None, precomputed_params=None):
    """
    Parameters
    ----------
    x, y : ndarray (1D)
        Solution variables on refined grid (raveled Cartesian product)
    idxs : dict
        {'x': array of indices into solGrids['x'], 
         'y': array of indices into solGrids['y']}
    states : dict
        Current state values
    precomputed_params : ndarray (2D)
        Full parameter array with shape (100, 50)
    """
    # Subset parameters using np.ix_ for efficient N-D indexing
    params_subset = precomputed_params[np.ix_(idxs['x'], idxs['y'])]
    # Ravel to match 1D structure of x, y
    params = params_subset.ravel()
    
    z = states['z']
    return np.column_stack([x**2 + y**2 + params - z])

# 4. Create solver and solve
solver = SolveGrid(
    F=F,
    solGrids=solGrids,
    stateGrids={'z': np.array([50.0, 100.0, 150.0])},
    ΔL={'x': 2, 'y': 2},
    ΔU={'x': 2, 'y': 2},
    maxExpand=5,
    precomputed_params=expensive_params  # Pass as kwarg
)

result = solver.solveLoopCartesianNDIdx()
print(result['x'])  # shape: (3,) for 3 states
print(result['y'])  # shape: (3,)
```

### Example 2: 1D Precomputed Parameters with Utility Method

Use the `get_linear_indices` helper for 1D precomputed arrays:

```python
import numpy as np
from gridsearch.GlobalGrids import SolveGrid

# 1. Define grids
solGrids = {
    'x': np.linspace(0, 10, 100),
    'y': np.linspace(0, 5, 50)
}

# 2. Precompute parameters as 1D array (raveled in Cartesian order)
# The SolveGrid class uses pd.MultiIndex.from_product ordering
X, Y = np.meshgrid(solGrids['x'], solGrids['y'], indexing='ij')
expensive_params_1d = (X**2 + Y**2).ravel()  # shape: (5000,)

# 3. Create solver instance
solver = SolveGrid(
    F=None,  # Will define F using solver instance
    solGrids=solGrids,
    stateGrids={'z': np.array([10.0, 50.0, 100.0])},
    ΔL={'x': 3, 'y': 3},
    ΔU={'x': 3, 'y': 3},
    maxExpand=5
)

# 4. Define F using solver's helper method
def F(x, y, idxs=None, states=None):
    # Use solver's get_linear_indices for proper conversion
    linear_indices = solver.get_linear_indices(idxs)
    params = expensive_params_1d[linear_indices]
    
    z = states['z']
    return np.column_stack([x + y + params - z])

solver.F = F

# 5. Solve with index tracking
result = solver.solveLoopCartesianNDIdx()
```

### Utility Methods for Parameter Subsetting

```python
# Get linear indices from dict of index arrays
grid_indices = {'x': np.array([10, 11, 12]), 'y': np.array([5, 6])}
linear_idx = solver.get_linear_indices(grid_indices)
# Returns: [505, 506, 555, 556, 605, 606] for Cartesian product

# Subset N-D parameter array
params_nd = np.random.rand(100, 50)  # Full grid
subset = solver.subset_nd_params(params_nd, grid_indices)
# Returns: params_nd[np.ix_([10,11,12], [5,6])].ravel()
```

## Key Points

- **`idxs` structure**: Dictionary with solution variable names as keys, 1D index arrays as values
- **2D parameters**: Use `np.ix_(idxs['x'], idxs['y'])` or `solver.subset_nd_params()`
- **1D parameters**: Use `solver.get_linear_indices(idxs)` for proper Cartesian ordering
- **Efficiency**: Direct integer indexing, no floating-point searches
- **Memory**: Uses views and fancy indexing; no need to copy full parameter arrays
- **Consistency**: All indexing uses `pd.MultiIndex.from_product` ordering

## Functional API (Legacy)

For one-off solves without reusability needs:

```python
from gridsearch.GlobalGrids import solveSingleRoot, solveLoopCartesianND

def F(x):
    return np.column_stack([x**2 - 4])

result = solveSingleRoot(F, grids={'x': np.linspace(0, 4, 9)})
print(result['x'])  # ~[2.0]
```
