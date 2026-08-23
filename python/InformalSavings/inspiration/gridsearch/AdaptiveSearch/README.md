# AdaptiveSearch

Adaptive root solving with dynamic grid expansion (to find a root) and refinement (to zoom in once found). Optimized to minimize calls to your function F.

## What it does
- Expands grids directionally when the nearest neighbor lies on a boundary.
- Refines the hypercube that contains the candidate root.
- Keeps full Cartesian grids so F is never re-evaluated at already-sampled points.

## F signature
- F receives flattened grid arrays (one per variable) and must return shape (M, N):
  - M = number of gridpoints in the Cartesian product
  - N = number of equations/outputs
- No shape normalization is performed—return (M, N) directly.

## Minimal example
```python
import numpy as np
from gridsearch.AdaptiveSearch import solveAdaptiveRoot

def F(x, y):
    eq1 = x + y - 5
    eq2 = x - y - 1
    return np.column_stack((eq1, eq2))  # shape (M, 2)

result = solveAdaptiveRoot(
    F,
    initial_grids={'x': np.linspace(0, 6, 7), 'y': np.linspace(0, 4, 5)},
    maxExpand=5,
    maxRefine=3,
)
print(result['x'])  # ~[3.0, 2.0]
```

## Key parameters
- `initial_grids`: dict of variable → 1D grid (required)
- `state_vals`: optional dict passed to F under `states`
- `maxExpand`: expansion iterations before falling back
- `maxRefine`: refinement iterations
- `expansion_factor`: grid range multiplier per expansion
- `refinement_factor`: subdivisions per dimension in refinement

## Notes
- Provide reasonably coarse starting grids; the solver expands and refines as needed.
- If no sign change is found, nearest neighbor is returned with boundary directions.

## Limitations

## Troubleshooting

**"No root found, returning NN"**
- Increase `maxExpand` to search further
- Check if root actually exists in the expandable region
- Try different `initial_grids` placement

**"Residual still high after maxRefine"**
- Increase `maxRefine` for more refinement steps
- Check if `tol` is too tight for the problem
- Verify F is continuous and well-behaved

**"Solution jumps around"**
- F might be discontinuous or noisy
- Try smoother initial grid (more points)
- Check F implementation for numerical stability

## Advanced Usage

### Custom Expansion Strategy

```python
result = solveAdaptiveRoot(
    F,
    initial_grids={'x': np.linspace(0, 1, 5)},
    expansion_factor=3.0,  # Triple the range each expansion
    maxExpand=10
)
```

### Very Tight Tolerance

```python
result = solveAdaptiveRoot(
    F,
    initial_grids={'x': np.linspace(2, 4, 11)},
    tol=1e-10,  # Very tight
    maxRefine=15  # Allow many refinements
)
```

### Passing Additional Arguments

```python
def F(x, alpha, states):
    # Use alpha directly and states if needed
    return np.column_stack([x**alpha - 10.0])

result = solveAdaptiveRoot(
    F,
    initial_grids={'x': np.linspace(0, 5, 11)},
    alpha=2.0,  # Passed as kwarg
    state_vals={'param': 1.0}
)
```

## Testing

Run the test suite:

```bash
pytest tests/test_adaptive_search.py -v
```

## License

[Your license information here]
