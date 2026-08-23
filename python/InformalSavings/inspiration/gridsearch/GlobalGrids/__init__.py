"""
GlobalGrids module for solving systems using adaptive grid refinement.

Provides main functions for finding roots via interpolation on adaptively refined grids
with state-dependent refinement policies.
"""

from .solveGrids import (
    solveLoopND,
    solveLoopCartesianND,
    solveLoopCartesianNDIdx,
    solveLoopSimple,
    solveSingleRoot,
)
from .solveGridsTest import SolveGrid

__all__ = [
    'solveLoopND',
    'solveLoopCartesianND',
    'solveLoopCartesianNDIdx',
    'solveLoopSimple',
    'solveSingleRoot',
    'SolveGrid',
]
