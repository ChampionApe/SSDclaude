import numpy as np, pandas as pd
from scipy import interpolate
from gridsearch.InterpRoots import interpRootFromPandasGridOrNearestWithBoundary
from gridsearch.GlobalGrids import SolveGrid
from gridsearch.GlobalGrids import solveSingleRoot, solveLoopCartesianND, solveLoopND
from gridsearch.AdaptiveSearch import solveAdaptiveRoot

def noneInit(x, fallBackValue):
	return fallBackValue if x is None else x

def _linInterp(x, xp, fp, j):
    d = ((x-xp[j])/(xp[j+1]-xp[j])).reshape(j.shape+(1,)*(fp.ndim-1))
    return (1-d)*fp[j] + d*fp[j+1]

def polGrid(v0, vT, n, exp = 1):
	""" Create polynomial grid with exponent 'exp'. 
		If exp>1 there are more gridpoint in the lower end of the grid."""
	return v0+(vT-v0)*((np.arange(1,n+1)-1)/(n-1))**exp

def defaultGrid_(n, l, u, kl, ku):
	return np.insert(np.linspace(l,u,n-2), [0, n-2], [l-1/kl-1e-4, u+1/ku+1e-4])

def defaultGrid(k, db):
	return defaultGrid_(db[f'{k}_n'], db[f'{k}_l'], db[f'{k}_u'], db[f'k{k}_l'], db[f'k{k}_u'])

def refineGrid(grid, value, l, u):
	idx = np.searchsorted(grid, value)
	return refineGridIdx(grid, idx, l, u)

def refineGridIdx(grid, idx, l, u):
	return grid[max(idx-l,0):min(idx+u,len(grid))]

def checkOpt(sol, ftol = None):
	if (sol['success'] and (max(abs(sol['fun']))<noneInit(ftol,1e-5))):
		return True
	else:
		return False

class CustomLinInterp:
	""" xp = 1d array, fp = ndarray. 
		Linear interpolation with support extrapolate ∈ {'linear', 'Nearest'}"""
	def __init__(self, xp, fp, extrapolate = 'linear', **kwargs):
		self.extrapolate = extrapolate
		# self.xp = xp
		# self.fp = fp
		self.f = getattr(self, f'extrapolate_{self.extrapolate}')(xp, fp, **kwargs)

	def __call__(self, x, **kwargs):
		return self.f(x, **kwargs)

	def extrapolate_linear(self, xp, fp, **kwargs):
		def interpolator(x, **kwargs):
			xb = np.clip(x, min(xp)+np.finfo(float).eps, max(xp))
			j = np.searchsorted(xp, xb, side = 'left') - 1
			return _linInterp(x, xp, fp, j)
		return interpolator

	def extrapolate_nearest(self, xp, fp, **kwargs):
		def interpolator(x, **kwargs):
			xb = np.clip(x, min(xp)+np.finfo(float).eps, max(xp))
			j = np.searchsorted(xp, xb, side = 'left') - 1
			return _linInterp(xb, xp, fp, j)
		return interpolator

# class CalibrateV2:
# 	def __init__(self, m, fapprox = None, **kwargs):
# 		""" Small class used to help calibrate a model. """
# 		self.m = m
# 		self.fapprox = interpolate.PchipInterpolator if fapprox is None else fapprox
# 		[self.__setattr__(k, v) for k,v in (self.defaultKwargs | kwargs).items()];

# 	@property
# 	def defaultKwargs(self):
# 		return {'scipyMethod': self.m.pseudoCalib, 
# 		  		'updateMethod': self.m.pseudoCalibUpdateParameters,
# 				'objectiveMethod': self.m.pseudoCalib_objective,
# 				'PEE': self.m.PEE,
# 				'scipyKwargs': {}}
	
# 	def grid1DScipy(self, grid, parameter, cals = None, paths = None, sols = None, kt = 'x_unbounded', kT = 'τ_unbounded', breakIfFail = True, printProgress = True):
# 		""" 
# 		Calibrate the model on grid of parameters. Extrapolate guesses before recalibrating.
# 		"""
# 		if cals is None:
# 			cals, paths, sols = dict.fromkeys(grid), dict.fromkeys(grid), dict.fromkeys(grid)
# 		solved = (k for k,v in cals.items() if isinstance(v, np.ndarray))
# 		iterateThrough = [k for k in grid if k not in solved];

# 		# Loop through and calibrate, extrapolate initial guesses along the way:
# 		for x in iterateThrough:
# 			nSolved = sum((isinstance(j, np.ndarray) for j in cals.values()))
# 			if nSolved>1:
# 				_, cals_x0, sols_x0 = self.extrapolateInitials1D(cals, sols, kt = kt, kT = kT)
# 			else:
# 				cals_x0, sols_x0 = None, None
# 			cals[x], paths[x], sols[x] = self.scipyIte(parameter, x, cals_x0 = cals_x0, sols_x0 = sols_x0)
# 			if breakIfFail and (not isinstance(cals[x], np.ndarray)):
# 				break
# 			if printProgress:
# 				print(x)
			
# 		return cals, paths, sols
	
# 	def adaptiveSearchIte(self, k, v):
# 		return None

# 	def scipyIte(self, k, v, cals_x0 = None, sols_x0 = None):
# 		self.m.db.update(self.m.adjPar(k,v))
# 		try:
# 			if cals_x0:
# 				self.updateMethod(cals_x0[v])
# 			if sols_x0:
# 				self.PEE.x0 = sols_x0[v]
# 			cal = self.scipyMethod(**self.scipyKwargs)
# 			path, sol = self.m.solvePEE() # this automatically relates to either PEE or LOG.
# 		except AssertionError:
# 			cal = "Failed to calibrate"
# 			path, sol = None, None
# 		return cal, path, sol

# 	def extrapolateInitials1D(self, cals, sols, kt = 'x_unbounded', kT = 'τ_unbounded'):
# 		cals_x0 = self.extrapolateCals1D(cals)
# 		x, sols_x0 = self.extrapolateSols1D(sols, kt = kt, kT = kT)
# 		return x, cals_x0, sols_x0

# 	def extrapolateCals1D(self, cals):
# 		""" 
# 		Extrapolate calibration parameters in 'cals' using self.fapprox as 
# 		the extrapolation function. If 0/1 solutions already in cals,
# 		return without extrapolation.

# 		Assumes that cals only contains variation in one parameter (1D), and
# 		not an attempt to vary multiple parameters at once. 

# 		Parameters
# 		-------
# 		cals : dictionary
# 			Keys: parameter sample values with solutions + the values we 
# 				want to extrapolate over.
# 			Values: ndarrays of sample solutions for given parameter values. 
# 				For unsolved parameter values, the values are None. 

# 		Returns
# 		-------
# 		dict
# 			Keys: Identical to cals.
# 			Values: ndarrays of sample solutions and extrapolated values.
			
# 			If cals contains no or only 1 solution, return ValueError. 
# 		"""
# 		fp = np.vstack([v for k,v in cals.items() if isinstance(v, np.ndarray)])
# 		xp = np.array([k for k,v in cals.items() if isinstance(v, np.ndarray)])
# 		x = np.array([k for k,v in cals.items() if not isinstance(v, np.ndarray)])
# 		if len(fp)<2:
# 			raise ValueError("Cannot extrapolate with less than 2 solutions.")

# 		cals2d = self.fapprox(np.sort(xp), fp[np.argsort(xp)], extrapolate = True)(x)
# 		return {x[i]: cals2d[i,:] for i in range(len(x))}

# 	def extrapolateSols1D(self, sols, kt = 'x_unbounded', kT = 'τ_unbounded'):
# 		""" 
# 		Extrapolate sequences of policy functions using self.approx as the 
# 		extrapolation function. If 0/1 solutions already in sols, return 
# 		without extrapolation. 

# 		Assumes that sols only contains variation in one parameter (1D), and
# 		not an attempt to vary multiple parameters at once. 

# 		Policy functions are may be defined over different variables in the 
# 		terminal and non-terminal years.

# 		Parameters
# 		-------
# 		sols : dictionary
# 			Keys: parameter sample values with solutions + the values we 
# 				want to extrapolate over.
# 			Values: dictionary over time, with values also being dictionaries
# 				that contains the solution grids for policy functions 
# 				(the solution grids are outcomes from the policy.py, 'solve' 
# 				methods).
		
# 		kt : string 
# 			Indicates the symbol that we extract from solution grids (see sols)
# 			in non-terminal years (t<T). 
# 		kT : string
# 			Indicates the symbol that we extract from solution grids (see sols)
# 			in terminal years (T). 
		
# 		Returns
# 		-------
# 		x : ndarray (vector) of parameter values that are unsolved/extrapolation
# 			occurs on.
# 		sols_x0: dict
# 			Keys: Identical to sols.
# 			Values: Dictionary of extrapolated sequences of policy functions.
# 				The keys indicate years, values contain ndarrays with suitable
# 				dimensions to be used as initial guesses when calling
# 				self.m.solvePEE.
				
# 			If cals contains no or only 1 solution, return ValueError. 
# 		"""
# 		# Split into solved/unsolved sample points:
# 		xp = np.array([k for k,v in sols.items() if v is not None])
# 		x = np.array([k for k,v in sols.items() if v is None])
# 		if len(xp)<2:
# 			raise ValueError("Cannot extrapolate with less than 2 solutions.")

# 		# Create solution structure for unsolved part:
# 		sols_x0 = dict.fromkeys(x)
# 		[sols_x0.__setitem__(xi, {}) for xi in x]; # solutions are dict of dicts

# 		# Approximate solution for non-terminal states:
# 		for t in self.m.db['txE']:
# 			fp = np.vstack([sols[xi][t][kt] for xi in xp]) # sample points for non-terminal states
# 			x0 = self.fapprox(np.sort(xp), fp[np.argsort(xp)], extrapolate = True)(x) # extrapolate
# 			[sols_x0[x[i]].__setitem__(t, x0[i,:]) for i in range(len(x))]; # add to solution structure again
		
# 		# Approximate for terminal state (if kt != kT we cannot collect in one vectorized extrapolation):
# 		t = self.m.db['t'][-1]
# 		fp = np.vstack([sols[xi][t][kT] for xi in xp])
# 		x0 = self.fapprox(np.sort(xp), fp[np.argsort(xp)], extrapolate = True)(x)
# 		[sols_x0[x[i]].__setitem__(t, x0[i,:]) for i in range(len(x))];
# 		return x, sols_x0


# ## A few methods used for calibration purposes:
# class Calibrate:
# 	def __init__(self, m, root = True, fapprox = None, **kwargs):
# 		self.m = m
# 		self.root = root
# 		self.fapprox = interpolate.PchipInterpolator if fapprox is None else fapprox
# 		self.kwargs = self.defaultKwargs
# 		[self.kwargs.__setitem__(k,v) for k,v in kwargs.items()];

# 	@property
# 	def defaultKwargs(self):
# 		return {'method': 'lm', 'options': {'ftol': 1e-5}}

# 	def onGridFromDicts(self, cals, paths, sols, parameter, kt = 'x_unbounded', kT = 'τ_unbounded', maxIter = 10):
# 		count = sum((isinstance(j, np.ndarray) for j in cals.values()))
# 		if count == 0:
# 			cals, paths, sols = self.onGrid_simpleIte(cals.keys(), parameter)
# 		for i in range(maxIter):
# 			x, cals_x0, sols_x0 = self.approxInitials(cals, sols, kt = kt, kT = kT)
# 			cals_i, paths_i, sols_i = self.onGrid_simpleIte(x, parameter, cals_x0 = cals_x0, sols_x0 = sols_x0)
# 			cals.update(cals_i), paths.update(paths_i), sols.update(sols_i)
# 			print(i)
# 			countTemp = sum((isinstance(j, np.ndarray) for j in cals.values()))
# 			if countTemp in (count, len(cals)):
# 				break
# 			else:
# 				count = countTemp
# 		return cals, paths, sols

# 	def onGrid(self, grid, parameter, kt = 'x_unbounded', kT = 'τ_unbounded', maxIter = 10):
# 		""" Start with a simple iteration that breaks if it does not calibrate. 
# 			Then, extrapolate from existing solutions and re-try """
# 		cals, paths, sols = self.onGrid_simpleIte(grid, parameter)
# 		self.onGridFromDicts(cals, paths, sols, parameter, kt = kt, kT = kT, maxIter = maxIter)
# 		return cals, paths, sols

# 	def approxInitials(self, cals, sols, kt = 'x_unbounded', kT = 'τ_unbounded'):
# 		cals_x0 = self.extrapolateParametersFromSols(cals, sols)
# 		x, sols_x0 = self.extrapolateInitialsFromSols(cals, sols, kt = kt, kT = kT)
# 		return x, cals_x0, sols_x0
	
# 	def extrapolateParametersFromSols(self, cals, sols):
# 		""" Return dictionary with extrapolated initial guesses for calibration parameters for 
# 			entries in cals/sols that are not yet inhabited by solutions (represented by np.ndarrays)"""
# 		fp = np.vstack([v for k,v in cals.items() if isinstance(v, np.ndarray)])
# 		xp = np.array([k for k,v in cals.items() if isinstance(v, np.ndarray)])
# 		x = np.array([k for k,v in cals.items() if not isinstance(v, np.ndarray)])
# 		cals2d = self.fapprox(np.sort(xp), fp[np.argsort(xp)], extrapolate = True)(x)
# 		return {x[i]: cals2d[i,:] for i in range(len(x))}
	
# 	def extrapolateInitialsFromSols(self, cals, sols, kt = 'x_unbounded', kT = 'τ_unbounded'):
# 		""" Return dictionary with extrapolated initial guesses for policy functions
# 			entries in cals/sols that are not yet inhabited by solutions (represented by np.ndarrays)"""
# 		xp = np.array([k for k,v in cals.items() if isinstance(v, np.ndarray)])	
# 		x = np.array([k for k,v in cals.items() if not isinstance(v, np.ndarray)])
# 		sols_x0 = dict.fromkeys(x)
# 		[sols_x0.__setitem__(xi, {}) for xi in x]; # dictionary with initial guesses 
# 		for t in self.m.db['txE']:
# 			fp = np.vstack([sols[xi][t][kt] for xi in xp])
# 			x0 = self.fapprox(np.sort(xp), fp[np.argsort(xp)], extrapolate = True)(x)
# 			[sols_x0[x[i]].__setitem__(t, x0[i,:]) for i in range(len(x))];
# 		t = self.m.db['t'][-1]
# 		fp = np.vstack([sols[xi][t][kT] for xi in xp])
# 		x0 = self.fapprox(np.sort(xp), fp[np.argsort(xp)], extrapolate = True)(x)
# 		[sols_x0[x[i]].__setitem__(t, x0[i,:]) for i in range(len(x))];
# 		return x, sols_x0
	
# 	def onGrid_simpleIte(self, grid, parameter, cals_x0 = None, sols_x0 = None):
# 		""" Calibrate model instance for grid of parameters with simple looping. """
# 		cals, sols, paths = dict.fromkeys(grid), dict.fromkeys(grid), dict.fromkeys(grid)
# 		for v in grid:
# 			try:
# 				cals[v], paths[v], sols[v] = self.basicIte(parameter, v, cals_x0 = cals_x0, sols_x0 = sols_x0)
# 			except:
# 				pass
# 			# print(v)
# 		return cals, paths, sols
	
# 	def onGrid_simpleBreak(self, grid, parameter, cals_x0 = None, sols_x0 = None):
# 		""" Calibrate model instance for grid of parameters with simple looping. """
# 		cals, sols, paths = dict.fromkeys(grid), dict.fromkeys(grid), dict.fromkeys(grid)
# 		for v in grid:
# 			cals[v], paths[v], sols[v] = self.basicIte(parameter, v, cals_x0 = cals_x0, sols_x0 = sols_x0)
# 			if not isinstance(cals[v], np.ndarray):
# 				break
# 			# print(v)
# 		return cals, paths, sols
	
# 	def basicIte(self, k, v, cals_x0 = None, sols_x0 = None):
# 		self.m.db.update(self.m.adjPar(k,v))
# 		try:
# 			if cals_x0:
# 				self.m.calibUpdateParameters(cals_x0[v])
# 			if sols_x0:
# 				self.m.PEE.x0 = sols_x0[v]
# 			if self.root:
# 				cal = self.m.calibPEE(**self.kwargs)
# 			else:
# 				cal = self.m.calibPEEmin(**self.kwargs)
# 			path, sol = self.m.solvePEE()
# 		except AssertionError:
# 			cal = """Failed to calibrate"""
# 			path, sol = None, None
# 		return cal, path, sol
	