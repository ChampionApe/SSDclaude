# AdaptiveSearch Module

## Overview

The `AdaptiveSearch` subpackage provides adaptive root-finding methods that differ from `GlobalGrids` in two key ways:

1. **No Pre-specified Global Grid**: Unlike `GlobalGrids` which requires a complete `solGrids` parameter defining the entire search space, `AdaptiveSearch` starts with an initial grid and dynamically expands it as needed.

2. **Two-Phase Refinement Strategy**:
   - **Expansion Phase**: When no root is detected, expands the grid in boundary dimensions
   - **Refinement Phase**: When a root is found, evaluates `F(root)` and if `||F(root)||` is not within tolerance, refines the grid within the hypercube containing the root

## Main Function

### `solveAdaptiveRoot(F, initial_grids, state_vals=None, tol=1e-6, maxExpand=5, maxRefine=3, expansion_factor=1.5, refinement_factor=2, **kwargs)`

Adaptively searches for a root `F(X) = 0` with dynamic grid expansion and refinement.

#### Parameters

- **F** (function): Function to evaluate. Receives solution variables as keyword arguments and returns column-stacked outputs.
- **initial_grids** (dict): Keys = choice variable names, Values = 1d arrays defining initial search grid.
- **state_vals** (dict, optional): State values to pass through to F under the key 'states'.
- **tol** (float, optional): Tolerance for root convergence `||F(root)||`. Default is 1e-6.
- **maxExpand** (int, optional): Maximum grid expansion iterations when no root found. Default is 5.
- **maxRefine** (int, optional): Maximum grid refinement iterations when root not accurate. Default is 3.
- **expansion_factor** (float, optional): Factor to expand grid range when no root found. Default is 1.5.
- **refinement_factor** (int, optional): Number of subdivisions per dimension during refinement. Default is 2.
- **kwargs** (dict): Additional keyword arguments forwarded to F.

#### Returns

Dictionary with keys:
- **'x'**: ndarray of the solution
- **'status'**: bool, True if converged root found, False otherwise
- **'type'**: 'root' or 'nn' (nearest neighbor)
- **'residual'**: float, `||F(x)||` at the returned solution
- **'iterations'**: dict with 'expansions' and 'refinements' counts

#### Algorithm

1. **Initial Evaluation**: Evaluate F on initial_grids using interpolation-based root finding
2. **Expansion Phase** (if no root found):
   - Identify dimensions where nearest neighbor is at grid boundary
   - Expand grid range in those dimensions by `expansion_factor`
   - Re-evaluate and search for root
   - Repeat up to `maxExpand` times
3. **Refinement Phase** (if root found):
   - Evaluate `F(root)` directly
   - If `||F(root)|| < tol`: return converged root
   - Otherwise: refine grid within the hypercube containing the root
   - Re-evaluate on refined grid and search for improved root
   - Repeat up to `maxRefine` times

## Key Differences from GlobalGrids

| Feature | GlobalGrids | AdaptiveSearch |
|---------|-------------|----------------|
| Grid Definition | Requires complete `solGrids` | Only requires `initial_grids` |
| Expansion | Constrained to `solGrids` boundaries | Unbounded expansion |
| Refinement Strategy | Single refinement per state | Iterative refinement until `tol` met |
| Residual Checking | Not performed | Evaluates `||F(root)||` |
| Use Case | Known solution domain | Unknown or large solution domain |

## Examples

### Simple Linear Function
```python
from gridsearch.AdaptiveSearch import solveAdaptiveRoot
import numpy as np

initial_grids = {"x": np.linspace(0.0, 5.0, 11)}

def F(x, states=None):
    return np.column_stack([x - 2.5])

result = solveAdaptiveRoot(F, initial_grids, tol=1e-6)
# result['x'] ≈ [2.5], result['status'] = True, result['residual'] < 1e-6
```

### Root Outside Initial Grid (Triggers Expansion)
```python
initial_grids = {"x": np.linspace(0.0, 2.0, 9)}

def F(x, states=None):
    return np.column_stack([x - 8.0])

result = solveAdaptiveRoot(F, initial_grids, tol=1e-6, maxExpand=10)
# Expands grid to find root at x ≈ 8.0
# result['iterations']['expansions'] > 0
```

### Nonlinear Function (Triggers Refinement)
```python
initial_grids = {"x": np.linspace(0.0, 5.0, 6)}  # Coarse grid

def F(x, states=None):
    return np.column_stack([x**2 - 4.0])

result = solveAdaptiveRoot(F, initial_grids, tol=1e-6, maxRefine=5)
# Finds root at x ≈ 2.0 with refinement
# result['iterations']['refinements'] > 0
```

### With State Values
```python
initial_grids = {"x": np.linspace(0.0, 5.0, 11)}
state_vals = {"s": 1.5}

def F(x, states):
    return np.column_stack([x - 2 * states['s']])

result = solveAdaptiveRoot(F, initial_grids, state_vals=state_vals, tol=1e-6)
# result['x'] ≈ [3.0]
```

## Implementation Details

### Helper Functions

- **`_expand_grids_unbounded`**: Expands grid range by `expansion_factor` in specified dimensions, extending equally on both sides.

- **`_refine_grid_around_root`**: Creates a finer grid within the hypercube containing the root by subdividing each dimension by `refinement_factor`.

- **`_evaluate_F`**: Constructs keyword arguments and evaluates F, handling state_vals and additional kwargs consistently.

## Testing

Comprehensive test suite in `tests/test_adaptive_root_search.py`:

- Linear convergence
- Expansion triggered by root outside grid
- Refinement triggered by coarse initial grid
- 2D systems
- No-root scenarios (returns nearest neighbor)
- State value propagation
- Tight tolerance requirements

All tests pass: `pytest tests/test_adaptive_root_search.py -v`

## Integration

The module integrates with the existing `InterpRoots` infrastructure by using `interpRootFromPandasGridOrNearestWithBoundary` for the core interpolation-based root finding on each grid configuration.
