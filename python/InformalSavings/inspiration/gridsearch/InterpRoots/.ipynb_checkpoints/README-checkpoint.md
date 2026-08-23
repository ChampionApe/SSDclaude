# InterpRoots

Interpolation utilities for locating roots on precomputed grids.

## Core functions
- `interpRootFromPandasGrid(df)`: finds roots via interpolation on a full Cartesian grid stored as a MultiIndex DataFrame.
- `interpRootFromPandasGridOrNearestWithBoundary(df)`: as above, but returns nearest neighbor and boundary directions when no sign change is found.

## Expected input
- A pandas DataFrame indexed by a MultiIndex of grid coordinates.
- Columns correspond to equations; shape is (M, N) where M = gridpoints, N = equations.

## Minimal example
```python
import pandas as pd
import numpy as np
from gridsearch.InterpRoots import interpRootFromPandasGrid

x = np.linspace(0, 4, 5)
values = np.column_stack([x**2 - 4])
df = pd.DataFrame(values, index=pd.Index(x, name='x'))
result = interpRootFromPandasGrid(df)
print(result['x'])  # ~[2.0]
```
