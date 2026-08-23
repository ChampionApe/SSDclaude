"""
AdaptiveSearch module for adaptive root finding with dynamic grid expansion.

Builds grids dynamically, expanding when no root is found and refining when 
roots are found but not sufficiently accurate. Optimized to minimize function 
evaluations for expensive computations.
"""

from .adaptiveRootSearch import solveAdaptiveRoot

__all__ = ['solveAdaptiveRoot']
