"""
InterpRoots module for finding roots using interpolation on N-dimensional grids.

Provides main functions for root finding via multilinear interpolation and Newton's method.
"""

from .interpRootsFromNDGrid import (
    interpRootsFromNDGrid,
    interpRootFromNDGrid,
    interpRootFromNDGridOrNearest,
    interpRootFromNDGridOrNearestWithBoundary,
    interpRootFromPandasGrid,
    interpRootFromPandasGridOrNearest,
    interpRootFromPandasGridOrNearestWithBoundary,
    interpRootsFromPandasGrid,
    interpRoot1DVectorized,
    interpRootsFromNDGridBatch,
    interpRootFromNDGridBatch,
    interpRootsFromPandasGridBatch,
    interpRootFromPandasGridBatch,
    _find_root_1d
)

__all__ = [
    'interpRootsFromNDGrid',
    'interpRootFromNDGrid',
    'interpRootFromNDGridOrNearest',
    'interpRootFromNDGridOrNearestWithBoundary',
    'interpRootFromPandasGrid',
    'interpRootFromPandasGridOrNearest',
    'interpRootFromPandasGridOrNearestWithBoundary',
    'interpRootsFromPandasGrid',
    'interpRoot1DVectorized',
    'interpRootsFromNDGridBatch',
    'interpRootFromNDGridBatch',
    'interpRootsFromPandasGridBatch',
    'interpRootFromPandasGridBatch',
    '_find_root_1d'
]
