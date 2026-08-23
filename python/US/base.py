import numpy as np, pandas as pd
from contextlib import contextmanager
def noneInit(x, fallBackValue):
    return fallBackValue if x is None else x


class Base:
    """ Economic equilibrium building blocks (writing/US/, model*.tex + num_ee.tex §auxiliary).

    Convention: parameters (α, ξ, ν, γ, η, X, β, p, κ, Γh, ...) are read from the database via
    self()/self.get(). Objects that may change during a solve or be chosen by policy -- taxes τ,
    pension characteristics θ/ε, aggregate states s, h and their lags/leads, discount factors B --
    are always explicit function arguments, never read from db, so this class stays agnostic to
    how those objects end up being solved for (fixed path, one-off choice, no-commitment policy, ...). """
    def __init__(self, m, t = None):
        self.m = m # associated Model class instance
        self.db = m.db # main database
        self.tFirst = self.db['t'][0] # model's first active/endogenous period (docs' t=1) -- NOT the
        # pre-determined state before it (docs' t=0, code's `s0`) and NOT db['t0'] (calibration baseline
        # year index). See README's "Timing convention".
        self.t = t # current year
        self._cache = None # parameter cache; None = disabled. See cacheParams().

    #######################################################################
    ##########   Parameter caching (cacheParams)                  #########
    #######################################################################
    # Opt-in and block-scoped, not always-on -- a cache surviving a db rewrite (model.py's calibration)
    # would return stale parameters silently. See README's "Base conventions" for the measurement/rationale.
    @contextmanager
    def cacheParams(self):
        """ Memoise db parameter reads for the duration of the block (see the §header comment above).

        Use around any loop that holds the year fixed while evaluating repeatedly -- a period of a policy
        grid search, say. Nests safely: an inner block reuses the outer block's cache rather than starting
        a second one, and only the outermost exit clears it. """
        if self._cache is not None:
            yield self # already inside a block -- reuse it, and let that block own the teardown
            return
        self._cache = {}
        try:
            yield self
        finally:
            self._cache = None

    def _year(self, t = None):
        """ The year a lookup actually resolves to -- the cache key's time component. Clamped at tFirst,
        matching __call__, so `t=None`, an explicit t, and any t before the horizon all share one entry. """
        return max(noneInit(t, self.t), self.tFirst)

    def _memo(self, key, fn):
        """ Return fn(), memoised under `key` while a cacheParams() block is active (otherwise just
        fn()). Keys must include the resolved year and any `lag` argument -- anything that changes the
        result. """
        c = self._cache
        if c is None:
            return fn()
        if key not in c:
            c[key] = fn()
        return c[key]

    def __call__(self, k, t = None):
        """ Return symbol 'k' from database. If t is not provided, rely on self.t attribute as backup. """
        return self._memo(('call', k, self._year(t)),
                          lambda: self.db[f'{k}'].xs(self._year(t)))

    def get(self, k, t = None):
        """ return numpy version of __call__ method """
        def _v():
            s = self(k, t = t)
            return s.values if isinstance(s, (pd.Series, pd.DataFrame)) else s
        return self._memo(('get', k, self._year(t)), _v)

    #######################################################################
    ##########                    0. Aux methods                ###########
    #######################################################################
    # Political weights:
    def ω2i(self, t = None):
        """ Political weight on types 2i. Uses μ_{t-1,i} (voting weight of the now-old generation as of
        when they were young), matching the FOC's timing (eq:PEELOG's restatement, tex line ~271) rather
        than the objective W_t's own (differently-timed) statement -- see README for the discrepancy. """
        return (self('pi[t-1]', t).mul(self('ω',t), axis = 0).mul(self('μi[t-1]',t), axis = 0)).values
    def ω20(self, t = None):
        """ Political weight on types 20. Uses μ_{t-1,0} -- see ω2i's docstring. """
        return self.get('p0[t-1]', t) * self.get('ω',t) * self.get('μ0[t-1]',t)
    def ω1i(self, t = None):
        """ Political weight on types 1i """
        return self.get('μi',t)
    def ω10(self, t = None):
        """ Political weight on types 10 """
        return self.get('μ0',t)

    # Power functions:
    def power_s(self, t = None):
        """ α(1+ξ)/(1+αξ) """
        return self.get('α',t)*(1+self.get('ξ',t))/(1+self.get('α',t)*self.get('ξ',t))
    def power_h(self, t = None):
        """ αξ/(1+αξ) """
        return self.get('α',t)*self.get('ξ',t)/(1+self.get('α',t)*self.get('ξ',t))
    def power_p(self, t = None):
        """ ( α(1+ξ)/(1+αξ) )^2 """
        return self.power_s(t)**2

    # Auxiliary parameters over household types:
    def auxProd(self, t = None, lag = ''):
        """ ηi^(1+ξ)/Xi^ξ. Pass lag = '[t-1]' or '[t+1]' to use a shifted vintage of η,X,ξ
        (needed e.g. in the pension benefit formula, which references last period's productivity distribution).
        Memoised inside cacheParams(). """
        return self._memo(('auxProd', lag, self._year(t)), lambda:
            (self(f'ηi{lag}', t).pow(1+self(f'ξ{lag}',t), axis = 0)/self(f'Xi{lag}',t).pow(self(f'ξ{lag}',t), axis = 0)).values)

    def Γh(self, t = None, lag = ''):
        """ ∑i γi * ηi^(1+ξ)/Xi^ξ. Memoised inside cacheParams(). Deliberately still *computed* rather
        than read from db['Γh'] (holds the same value via model.py's paramsFromFuncs): that's only
        refreshed by updateAuxPars, so it would go stale mid-calibration when ηi/Xi are being solved for. """
        return self._memo(('Γh', lag, self._year(t)), lambda:
            (self(f'γi{lag}', t) * self.auxProd(t, lag = lag)).sum())

    @staticmethod
    def _bcast(x):
        """ Reshape a (t,)-shaped array/scalar to (t,1) so it broadcasts against (t,i)-shaped arrays.
        No-op for true scalars / single-year values (Base, BaseGrid). """
        x = np.asarray(x)
        return x[:, None] if x.ndim else x

    # Two distinct ratios that differ by a factor η_{t,i} -- keep them apart:
    #   hRatio  = h_{t,i}/h_t          = (η_{t,i}/X_{t,i})^ξ / Γ_{h,t}     (eq EE:hi)
    #   hηRatio = h_{t,i}η_{t,i}/h_t   = (η_{t,i}^{1+ξ}/X_{t,i}^ξ) / Γ_{h,t}
    # hηRatio is what the doc's si_s/c2i/dv2i formulas carry (they all write η^{1+ξ}/X^ξ over Γh);
    # hRatio is what individual labour supply and the benefit formula need. Both are parameters only
    # (no solution state), so both memoise inside cacheParams() like their ingredients.
    def hRatio(self, t = None, lag = ''):
        """ Eq (EE:hi): h_{t,i}/h_t = (η_{t,i}/X_{t,i})^ξ/Γ_{h,t}. Satisfies ∑_i γ_{t,i}η_{t,i}·hRatio_i=1. """
        return self._memo(('hRatio', lag, self._year(t)), lambda:
            (self(f'ηi{lag}', t)/self(f'Xi{lag}', t)).pow(self(f'ξ{lag}', t), axis = 0).values
            / self._bcast(self.Γh(t, lag = lag)))

    def hηRatio(self, t = None, lag = ''):
        """ h_{t,i}η_{t,i}/h_t = (η_{t,i}^{1+ξ}/X_{t,i}^ξ)/Γ_{h,t}. Satisfies ∑_i γ_{t,i}·hηRatio_i = 1. """
        return self._memo(('hηRatio', lag, self._year(t)), lambda:
            self.auxProd(t, lag = lag) / self._bcast(self.Γh(t, lag = lag)))

    #######################################################################
    ##########      1. Factor prices (eq:factorPrices, eq:w0)     ##########
    #######################################################################
    def R(self, s_, h, t = None):
        """ Eq (factorPrices): R_t = α (s_{t-1}/(ν_t h_t))^(α-1). s_ = s_{t-1}, h = h_t (explicit -- solution objects). """
        α = self.get('α', t)
        return α * (s_/(self.get('ν', t)*h))**(α-1)

    def w(self, s_, h, t = None):
        """ Eq (factorPrices): w_t = (1-α)(s_{t-1}/(ν_t h_t))^α. TFP A_t normalized to 1. s_ = s_{t-1}, h = h_t. """
        α = self.get('α', t)
        return (1-α) * (s_/(self.get('ν', t)*h))**α

    def w0(self, s_, t = None):
        """ Eq (w0): informal wage w_t^0 = ((1-α)/Γh^α)^(1/(1+αξ)) (s_{t-1}/ν_t)^(α/(1+αξ)). s_ = s_{t-1}. """
        α, ξ = self.get('α', t), self.get('ξ', t)
        return ((1-α)/self.Γh(t)**α)**(1/(1+α*ξ)) * (s_/self.get('ν', t))**(α/(1+α*ξ))

    #######################################################################
    ##########   2. Individual labour supply (eq:EE:hi)           ##########
    #######################################################################
    def hi(self, h, t = None):
        """ h_{t,i} = h_t * (h_{t,i}/h_t). h = aggregate h_t (explicit -- solution object). """
        return self._bcast(h) * self.hRatio(t)

    #######################################################################
    ##########   2b. The pension-design wedge A(θ)/B(θ) (app:ESC)  #########
    #######################################################################
    # Benefits are b_t^i = [A(θ_t)·h_{t-1,i}η_{t-1,i} + B(θ_t)·h_{t-1}]·bbar_t. Without a wedge
    # (A,B) = (θ, 1-θ) and every formula below is the docs' own. With one, a share of contributions is
    # lost to the deadweight cost of redistributive transfers, f(θ) = φ+(1-φ)θ^p, f' > 0:
    #
    #   'scale'  A = f(θ)θ,  B = f(θ)(1-θ)   the appendix's live spec: bbar itself carries f(θ)
    #   'flat'   A = θ,      B = f(θ)(1-θ)   MGE's variant: only the FLAT component is costly
    #
    # THE ONE RULE THAT MAKES THIS SMALL: in every equilibrium object, θ_{t+1} appears only multiplying
    # (1-α)/α·τ_{t+1} (the discounted earnings-related return to an hour) and (1-θ_{t+1}) only multiplying
    # the same factor (the flat component). So the wedge is exactly the substitution θ->A(θ), (1-θ)->B(θ)
    # in Γs, Θh, si_s, c1i, tildec1i, c2i, dlnc2i_dτ, ΓsCap and BSteadyState -- and NOWHERE else. In
    # particular bbar is untouched: it stays GROSS revenue per unit h_{t-1}, with the lost share implicit
    # in A+B < 1. Verified against the appendix's own Γs/Θh/si_s in test_esc.py.
    #
    # Read from db (they are 0-D parameters, constant across t and j), not passed as arguments, unlike
    # θ/τ: they are primitives of the political environment, not objects any solver chooses.
    def fWedge(self, θ):
        """ f(θ) = φ + (1-φ)θ^p, the share of contributions that reaches beneficiaries. 1 with no wedge. """
        if self.db.get('wedgeSpec') is None:
            return 1.
        φ, p = self.db['wedgePhi'], self.db['wedgeP']
        return φ + (1-φ)*np.asarray(θ, dtype = float)**p

    def wedgeA(self, θ):
        """ The coefficient on own past earnings h_{t-1,i}η_{t-1,i} in the benefit formula. """
        return θ if self.db.get('wedgeSpec') in (None, 'flat') else self.fWedge(θ)*θ

    def wedgeB(self, θ):
        """ The coefficient on the flat component h_{t-1}. """
        return (1-θ) if self.db.get('wedgeSpec') is None else self.fWedge(θ)*(1-θ)

    #######################################################################
    ##########   3. Pension system / government budget (eq:governmentBudget)  ###
    ##########      τ, θ, ε are always explicit -- to be endogenized later     ###
    #######################################################################
    def κ(self, ε1, t = None):
        """ Eq (governmentBudget:bbar): κ_t(ε_{t+1}) = (p_t + ε_{t+1}γ_{t,0}p_t^0)(1+γ_{t,0})/(1+γ_{t+1,0}).
        ε1 = ε_{t+1} (explicit -- mirrors the b0/bi convention, since ε may be endogenized later;
        γ0/p/p0 are read from db as primitives, not solution objects). """
        p, p0, γ0, γ0_1 = self.get('p', t), self.get('p0', t), self.get('γ0', t), self.get('γ0[t+1]', t)
        return (p + ε1*γ0*p0) * (1+γ0)/(1+γ0_1)

    def bbar(self, τ, w, h, h_, t = None):
        """ Eq (governmentBudget:bbar): bbar_t = ν_t w_t h_t τ_t / (h_{t-1} κ_{t-1}).
        τ, w, h = period-t tax rate/wage/aggregate hours; h_ = h_{t-1} (aggregate, lagged). All explicit. """
        return self.get('ν', t)*w*h*τ / (h_*self.get('κ[t-1]', t))

    def bi(self, θ, bbar, h_, t = None):
        """ Eq (governmentBudget): b_t^i = [θ_t h_{t-1,i} η_{t-1,i} + (1-θ_t) h_{t-1}] bbar_t.
        θ, bbar = period-t contributive-incentive parameter / benefit level (explicit -- θ will be endogenized).
        h_ = h_{t-1} (aggregate, lagged). """
        hiη_ = self._bcast(h_) * self.hηRatio(t, lag = '[t-1]')
        bracket = self._bcast(self.wedgeA(θ))*hiη_ + self._bcast(self.wedgeB(θ)*h_)
        return bracket * self._bcast(bbar)

    def b0(self, ε, bbar, h_):
        """ Eq (governmentBudget): b_t^0 = ε_t h_{t-1} bbar_t.
        ε, bbar = period-t universal-pension parameter / benefit level (explicit -- ε will be endogenized).
        h_ = h_{t-1} (aggregate, lagged). """
        return ε * h_ * bbar

    #######################################################################
    ##########   4. Numerical auxiliary functions (eq:auxiliary)   #########
    ##########      -- the core building blocks used to solve the   #########
    ##########      economic equilibrium given a policy path        #########
    #######################################################################
    def Γs(self, B, τ1, θ1, t = None):
        """ Eq (auxiliary:Gammas): Γ_{s,t}(B_{t+1}, τ_{t+1}, θ_{t+1}).
        B = B_{t+1}^i (per type, explicit); τ1 = τ_{t+1}; θ1 = θ_{t+1} (explicit -- to be endogenized).
        Note: the doc's argument list for this equation omits θ_{t+1}, but the formula depends on it directly. """
        α, ξ, p, κ = self.get('α', t), self.get('ξ', t), self.get('p', t), self.get('κ', t)
        γi, auxProd = self.get('γi', t), self.auxProd(t)
        Bratio = B/(1+B)
        num = (γi*auxProd*Bratio).sum(axis = -1)/(1+ξ)
        denom = 1 + (1-α)/α * p*τ1/κ * (self.wedgeA(θ1) + self.wedgeB(θ1)*(γi/(1+B)).sum(axis = -1))
        return num/denom

    def Θh(self, τ, τ1, θ1, Γs, t = None):
        """ Eq (auxiliary:Thetah): Θ_{h,t}(τ_t, τ_{t+1}, θ_{t+1}, Γ_{s,t}). """
        α, ξ, p, κ, Γh = self.get('α', t), self.get('ξ', t), self.get('p', t), self.get('κ', t), self.Γh(t)
        return Γh**((1+ξ)/(1+α*ξ)) * ((1-α)*(1-τ)/(Γh - (1-α)/α*p*self.wedgeA(θ1)*τ1/κ*Γs))**(ξ/(1+α*ξ))

    def ΘhTerminal(self, τ, t = None):
        """ Eq (auxiliary:ThetahT): terminal-period Θ_{h,T}(τ_T). """
        α, ξ, Γh = self.get('α', t), self.get('ξ', t), self.Γh(t)
        return Γh**(1/(1+α*ξ)) * ((1-α)*(1-τ))**(ξ/(1+α*ξ))

    def Θs(self, Θh, Γs, t = None):
        """ Eq (auxiliary:Thetas): Θ_{s,t}(Θ_{h,t}, Γ_{s,t}). """
        ξ, Γh = self.get('ξ', t), self.Γh(t)
        return (Θh/Γh)**((1+ξ)/ξ) * Γs

    def s(self, Θs, s_, t = None):
        """ Eq (auxiliary:s): s_t(Θ_{s,t}, s_{t-1}). s_ = s_{t-1} (explicit). """
        return Θs * (s_/self.get('ν', t))**self.power_s(t)

    def h(self, Θh, s_, t = None):
        """ Eq (auxiliary:h): h_t(Θ_{h,t}, s_{t-1}). s_ = s_{t-1} (explicit). """
        return Θh * (s_/self.get('ν', t))**self.power_h(t)

    def ΘhFromH(self, h, s_, t = None):
        """ Eq (auxiliary:h), inverted: Θ_{h,t}(h_t, s_{t-1}). Recovers Θh from an already-solved
        equilibrium regardless of which formula (general/terminal) produced h -- used by §10. """
        return h / (s_/self.get('ν', t))**self.power_h(t)

    def sFromH(self, h, Γs, t = None):
        """ Eq (auxiliary:sFromH): alternative s_t(h_t, Γ_{s,t}), given h_t directly instead of s_{t-1}. """
        ξ = self.get('ξ', t)
        return (h/self.Γh(t))**((1+ξ)/ξ) * Γs

    def hFromS(self, s, Γs, t = None):
        """ Eq (auxiliary:sFromH), inverted: h_t(s_t, Γ_{s,t}) -- recovers aggregate hours from a *given*
        savings level and Γ_{s,t}, the reverse direction of sFromH. Used by model.py's initialState_solve
        to back out h_{-1} (docs' t=0's aggregate hours) from the actual given s0 and a Γ_{s,-1} computed
        from db['t'][0]'s own (τ,θ) -- see that method's docstring. Round-trips exactly with sFromH
        (verified numerically). """
        ξ = self.get('ξ', t)
        return self.Γh(t) * (s/Γs)**(ξ/(1+ξ))

    def Rlead(self, s, h1, t = None):
        """ Eq (auxiliary:R): R_{t+1}(s_t, h_{t+1}). s = s_t, h1 = h_{t+1} (both explicit). """
        α = self.get('α', t)
        return α * (s/(self.get('ν[t+1]', t)*h1))**(α-1)

    def B(self, s, h1, t = None):
        """ Eq (auxiliary:B): B_{t+1}^i(s_t, h_{t+1}) = (β_{t,i})^ρ [R_{t+1}(s_t,h_{t+1})/p_t]^(ρ-1). """
        ρc = self._bcast(self.get('ρ', t))
        Rp = self._bcast(self.Rlead(s, h1, t)/self.get('p', t))
        return self.get('βi', t)**ρc * Rp**(ρc-1)

    #######################################################################
    ##########   5. Individual savings ratio (eq:EE:si_s)          #########
    #######################################################################
    def si_s(self, B, τ1, θ1, Γs, t = None):
        """ Eq (EE:si_s): s_{t,i}/s_t(B_{t+1}, τ_{t+1}, θ_{t+1}, Γ_{s,t}).
        B = B_{t+1}^i (per type); τ1 = τ_{t+1}; θ1 = θ_{t+1}; Γs = Γ_{s,t} (all explicit -- solution objects).
        Rewritten in terms of Γ_{s,t}'s own numerator/denominator (Γs = num/denom, see eq:auxiliary:Gammas)
        so we avoid recomputing the aggregate sum ∑_j γ_j(η_j^{1+ξ}/X_j^ξ)B_{t+1}^j/(1+B_{t+1}^j) a second time. """
        α, p, κ = self.get('α', t), self.get('p', t), self.get('κ', t)
        auxProd, Bratio = self.auxProd(t), B/(1+B)
        term1 = Bratio*auxProd / self._bcast((1+self.get('ξ', t))*Γs)
        term2 = -(1/(1+B)) * self._bcast((1-α)/α * p*self.wedgeB(θ1)/κ*τ1)
        term3 = -self.hηRatio(t) * self._bcast((1-α)/α * p*self.wedgeA(θ1)/κ*τ1)
        return term1 + term2 + term3

    #######################################################################
    ##########   6. Closed-form consumption -- formal (eq:EE:ci)    ########
    #######################################################################
    def c1i(self, h, s, B, τ1, θ1, t = None):
        """ Eq (EE:ci): c_{1,t}^i(h_t, s_t, B_{t+1}, τ_{t+1}, θ_{t+1}). """
        ξ, α, p, κ = self.get('ξ', t), self.get('α', t), self.get('p', t), self.get('κ', t)
        auxProd, Bratio = self.auxProd(t), B/(1+B)
        smooth = auxProd * self._bcast((h/self.Γh(t))**((1+ξ)/ξ)) * (1 - Bratio/self._bcast(1+ξ))
        pension = self._bcast(s)/(1+B) * self._bcast((1-α)/α*p*τ1*self.wedgeB(θ1)/κ)
        return smooth + pension

    def tildec1i(self, h, B, τ1, θ1, Γs, t = None):
        """ Eq (EE:ci): tilde-c_{1,t}^i(h_t, B_{t+1}, τ_{t+1}, θ_{t+1}, Γ_{s,t}) -- s_t eliminated using Γ_{s,t}. """
        ξ, α, p, κ = self.get('ξ', t), self.get('α', t), self.get('p', t), self.get('κ', t)
        auxProd = self.auxProd(t)
        hΓh = self._bcast((h/self.Γh(t))**((1+ξ)/ξ))
        bracket = auxProd/self._bcast(1+ξ) + self._bcast(Γs*(1-α)/α*p*τ1*self.wedgeB(θ1)/κ)
        return hΓh/(1+B) * bracket

    # ĉ_{1,t}^i ≡ (1+B_{t+1}^i)^{1/(1-1/ρ)}·tilde-c_{1,t}^i (docs eq:hatc1i) folds B_{t+1}^i's own τ_t
    # -dependence (through s_t) into the consumption level, so υ_{1,t}^i = ĉ^{1-1/ρ}/(1-1/ρ) and one
    # numerical dln(ĉ)/dτ_t picks up both channels.
    #
    # ĉ itself is never computed -- only (ĉ)^{1-1/ρ} and ln(ĉ) are needed, and both avoid the
    # (1/(1-1/ρ))-power that the literal definition requires:
    #       (ĉ)^{1-1/ρ} = (1+B)·(tilde-c)^{1-1/ρ},        ln(ĉ) = ln(1+B)/(1-1/ρ) + ln(tilde-c).
    # DO NOT replace these with the literal form: it overflows float64 as ρ->1 (exponent 1001 at ρ=1.001,
    # overflowing once B>1.03), silently yielding inf. Neither form above overflows for any ρ≠1.
    #
    # ρ=1 itself is genuinely undefined (indirect utility is (1+B)ln(tilde-c), not a power of any level)
    # -- not a gap, since ρ=1 is exactly what policy.py's LOG class solves in closed form.
    def hatc1iPow(self, h, B, τ1, θ1, Γs, t = None):
        """ (ĉ_{1,t}^i)^{1-1/ρ} = (1+B_{t+1}^i)·(tilde-c_{1,t}^i)^{1-1/ρ} -- the level factor of
        dυ_{1,t}^i/dτ_t. See the §header comment above for why this form rather than the literal one. """
        p = 1 - 1/self.get('ρ', t)
        return (1+B) * self.tildec1i(h, B, τ1, θ1, Γs, t)**p

    def lnhatc1i(self, h, B, τ1, θ1, Γs, t = None):
        """ ln(ĉ_{1,t}^i) = ln(1+B_{t+1}^i)/(1-1/ρ) + ln(tilde-c_{1,t}^i) -- differentiate this along τ_t
        to get dln(ĉ_{1,t}^i)/dτ_t. See the §header comment above. """
        p = 1 - 1/self.get('ρ', t)
        return np.log1p(B)/p + np.log(self.tildec1i(h, B, τ1, θ1, Γs, t))

    def c2i(self, h, s_, τ, θ, siRatio_, t = None):
        """ Eq (EE:ci): c_{2,t}^i(h_t, s_{t-1}, τ_t, θ_t, s_{t-1,i}/s_{t-1}).
        siRatio_ = s_{t-1,i}/s_{t-1}, itself a solution object (si_s() evaluated at t-1) -- predetermined at t,
        explicit rather than read from db (mirrors θ/τ convention). """
        α, ν, p_, κ_ = self.get('α', t), self.get('ν', t), self.get('p[t-1]', t), self.get('κ[t-1]', t)
        A = (1-α)/α * p_*τ/κ_
        inner = siRatio_ + self._bcast(A) * (self._bcast(self.wedgeA(θ))*self.hηRatio(t, lag = '[t-1]')
                                             + self._bcast(self.wedgeB(θ)))
        outer = α * (ν/p_) * h**(1-α) * (s_/ν)**α
        return self._bcast(outer) * inner

    def tildec2i(self, h, s_, τ, θ, siRatio_, t = None):
        """ Eq (EE:ci): tilde-c_{2,t}^i = c_{2,t}^i -- formal retirees don't supply labour when old. """
        return self.c2i(h, s_, τ, θ, siRatio_, t = t)

    #######################################################################
    ##########   7. Closed-form consumption -- informal (eq:EE:c0)  ########
    #######################################################################
    def auxProd0(self, t = None, lag = ''):
        """ η0^(1+ξ)/X0^ξ -- informal analogue of auxProd (scalar type-0 productivity/disutility; note ξ
        is always current-period, see auxProd0χ). Memoised inside cacheParams(). """
        return self._memo(('auxProd0', lag, self._year(t)), lambda:
            self.get(f'η0{lag}', t)**(1+self.get('ξ', t)) / self.get(f'X0{lag}', t)**self.get('ξ', t))

    def auxProd0χ(self, t = None, lag = ''):
        """ (χ*η0)^(1+ξ)/X0^ξ, with χ/η0/X0 shifted by `lag` but ξ always current-period -- needed for
        c2^0/tildec2^0 (eq:EE:c0), which combine last period's informal productivity χ_{t-1}η_{t-1,0}/X_{t-1,0}
        with this period's Frisch elasticity/labour aggregates (ξ_t, Γ_{h,t}). Memoised inside cacheParams(). """
        return self._memo(('auxProd0χ', lag, self._year(t)), lambda:
            (self.get(f'χ{lag}', t)*self.get(f'η0{lag}', t))**(1+self.get('ξ', t)) / self.get(f'X0{lag}', t)**self.get('ξ', t))

    def c10(self, s_, t = None):
        """ Eq (EE:c0): c_{1,t}^0(s_{t-1}). s_ = s_{t-1}. """
        α, ξ = self.get('α', t), self.get('ξ', t)
        return self.auxProd0(t) * ((1-α)/self.Γh(t)**α)**((1+ξ)/(1+α*ξ)) * (s_/self.get('ν', t))**(α*(1+ξ)/(1+α*ξ))

    def tildec10(self, s_, t = None):
        """ Eq (EE:c0): tilde-c_{1,t}^0 = c_{1,t}^0/(1+ξ). """
        return self.c10(s_, t) / (1+self.get('ξ', t))

    def c20(self, h, s_, ε, τ, t = None):
        """ Eq (EE:c0): c_{2,t}^0(h_t, s_{t-1}, ε_t, τ_t). ε, τ explicit -- to be endogenized. """
        α, ξ, ν, κ_ = self.get('α', t), self.get('ξ', t), self.get('ν', t), self.get('κ[t-1]', t)
        smooth = self.auxProd0χ(t, lag = '[t-1]') * ((1-α)/self.Γh(t)**α)**((1+ξ)/(1+α*ξ)) * (s_/ν)**(α*(1+ξ)/(1+α*ξ))
        universal = (1-α)*ν*ε*τ/κ_ * (s_/ν)**α * h**(1-α)
        return smooth + universal

    def tildec20(self, h, s_, ε, τ, t = None):
        """ Eq (EE:c0): tilde-c_{2,t}^0 -- as c20, but the labour-smoothing term is divided by (1+ξ). """
        α, ξ, ν, κ_ = self.get('α', t), self.get('ξ', t), self.get('ν', t), self.get('κ[t-1]', t)
        smooth = self.auxProd0χ(t, lag = '[t-1]')/(1+ξ) * ((1-α)/self.Γh(t)**α)**((1+ξ)/(1+α*ξ)) * (s_/ν)**(α*(1+ξ)/(1+α*ξ))
        universal = (1-α)*ν*ε*τ/κ_ * (s_/ν)**α * h**(1-α)
        return smooth + universal


    #######################################################################
    ##########   8. Steady state (eq:steadystate_LOG, eq:steadystate_CRRA)  #
    #######################################################################
    # Fixed point s_t=s_{t-1}=s* under constant (τ,θ) at t=self.tFirst's parameters. See README's "Steady
    # state solve" / "Timing convention".
    def sSteadyState(self, Θs, t = None):
        """ Eq (steadystate_LOG:s), generalized: the steady-state savings level s* solving the fixed point
        s* = Θs*(s*/ν_t)^power_s -- i.e. s_t = s_{t-1} = s* under a constant Θs_t = Θs. Algebraically
        identical to eq (steadystate_LOG:s) once Θs is expanded via Θh/Θs (verified by hand), but written
        directly in terms of Θs so the same expression also serves the CRRA steady state (eq
        steadystate_CRRA), which only differs in *how* Γs (and hence Θh/Θs) was obtained. """
        ν, powerS = self.get('ν', t), self.power_s(t)
        return (Θs/ν**powerS)**(1/(1-powerS))

    def BSteadyState(self, Γs, τ, θ, t = None):
        """ Eq (steadystate_CRRA:Bi): steady-state B^i(Γ_s; τ, θ) -- the generalized discount factor
        consistent with a steady state at Γs, given constant policy τ, θ. Γs, τ, θ explicit (Γs is the
        candidate being root-found in steadyState_CRRA_residual; τ, θ are the constant steady-state policy).
        Used to close the Γs fixed point: a candidate Γs is a steady state iff
        self.Γs(self.BSteadyState(Γs, τ, θ), τ, θ) == Γs (see steadyState_CRRA_residual in model.py). At
        ρ=1 this collapses to the primitive βi regardless of Γs -- matching the LOG case's B^i=β_i, so
        BSteadyState is only actually needed for the CRRA (ρ≠1) solve. """
        α, ρ, p, κ, ν, Γh = self.get('α', t), self.get('ρ', t), self.get('p', t), self.get('κ', t), self.get('ν', t), self.Γh(t)
        ρc = self._bcast(ρ)
        inner = (α/p) * (Γh - (1-α)/α * p*self.wedgeA(θ)*τ/κ * Γs) / ((1-α)*(1-τ)) * (ν/Γs)
        return self.get('βi', t)**ρc * self._bcast(inner)**(ρc-1)

    def ΓsCap(self, τ, θ, t = None):
        """ The Γs at which Θ_{h,t}'s denominator (eq:auxiliary:Thetah) hits zero,

            Γs_cap = Γh·α·κ / ((1-α)·p·θ·τ),      = inf when θτ = 0.

        Above it Θh and BSteadyState's `inner` are negative, so a fractional power returns NaN and any
        bracketing root finder dies rather than reporting a bad bracket. It is a hard feasibility limit,
        not a numerical nicety: a steady state must have Θh real and positive, so the root is always
        strictly below the cap.

        This matters here in a way it does not in the Argentina models. The cap scales with α/(1-α), which
        is 0.43/0.57 = 0.75 there against 0.30/0.70 = 0.43 here, and with κ/p, which exceeds one there
        (a positive informal mass) but is exactly one here. At the US calibration the cap falls to ≈0.58
        as τ→1, i.e. BELOW the constant 0.75 upper bound those models hard-code -- so that constant is
        safe there by parameter values, not by construction. See steadyState_CRRA_bounds. """
        denom = (1-self.get('α', t))*self.get('p', t)*self.wedgeA(θ)*τ
        cap = self.Γh(t)*self.get('α', t)*self.get('κ', t)/np.where(denom == 0, np.nan, denom)
        return np.where(np.isnan(cap), np.inf, cap)[()]

    #######################################################################
    ##########   9. Political first-order condition (eq:fast, eq:PEELOG)  ##
    #######################################################################
    # FOC is the preference-agnostic combiner; `_LOG` methods below are LOG-specific closed forms (see
    # README's "Political first-order condition").
    def FOC(self, dv1i, dv10, dv2i, dv20, t = None):
        """ Eq (fast / the general FOC underlying eq:PEELOG, tex line ~269-273): z_t, the marginal
        political objective w.r.t. τ_t. Combines the young (dv1i,dv10) and old (dv2i,dv20) marginal
        indirect utilities via the political weights (ω1i/ω10/ω2i/ω20, §0) and population shares γ.
        Preference-agnostic: this combination is identical regardless of whether dv1i/dv10/dv2i/dv20 came
        from the LOG closed forms below or a future CRRA version -- only how the dv's themselves are
        computed differs by preference case. The old-generation term uses γ_{t-1,j} (their population share
        when they were young); the young-generation term uses current γ_{t,j} -- matches the doc's z_t
        definition exactly (not a typo). dv1i, dv2i: per-type, shape (...,ni). dv10, dv20: aggregate
        informal, shape (...,). """
        γi, γi_ = self.get('γi', t), self.get('γi[t-1]', t)
        γ0, γ0_ = self.get('γ0', t), self.get('γ0[t-1]', t)
        ω1i, ω10, ω2i, ω20 = self.ω1i(t), self.ω10(t), self.ω2i(t), self.ω20(t)
        ν = self.get('ν', t)
        old = (γi_*ω2i*dv2i).sum(axis = -1) + γ0_*ω20*dv20
        young = ν*((γi*ω1i*dv1i).sum(axis = -1) + γ0*ω10*dv10)
        return old + young

    # Young generations' closed-form terms (no Θh-derivative/si_s machinery needed). β/β0 explicit (not
    # db-read): lets FH_dv1i_LOG/FH_dv10_LOG (BaseTime §8) zero the terminal entry by passing a modified β,
    # no db-write needed.
    def dv1i_dτ_LOG(self, β, τ, t = None):
        """ Eq (PEELOG): dυ_{1,t}^i/dτ_t -- marginal indirect utility of the young formal type-i household
        w.r.t. the current tax τ_t. β = β_{t,i} (explicit, per type). """
        ξ, α = self.get('ξ', t), self.get('α', t)
        coef = -1/(1-τ) * (1+ξ)/(1+α*ξ)
        return self._bcast(coef) * (1 + β*self._bcast(self.power_s(t)))

    def dv10_dτ_LOG(self, β0, τ, t = None):
        """ Eq (PEELOG): dυ_{1,t}^0/dτ_t -- marginal indirect utility of the young informal household
        (works only through the future informal wage rate). β0 = β_{t,0} (explicit). """
        ξ, α = self.get('ξ', t), self.get('α', t)
        return -β0/(1-τ) * α*(1+ξ)**2/(1+α*ξ)**2

    def dlnΘh_dτ_LOG(self, τ, t = None):
        """ Eq (PEELOG): ∂ln(Θ_{h,t})/∂τ_t = -1/(1-τ_t)*ξ/(1+αξ). Same functional form at t<T-1 and t=T-1
        (the doc notes this explicitly for eq:terminalPEELOG) -- unlike dv1i_dτ_LOG/dv10_dτ_LOG,
        dv2i_dτ_LOG/dv20_dτ_LOG (which both use this) need no FH_* terminal-stacking wrapper as a result.
        Closed-form only because LOG's Θh has a closed form to begin with; a CRRA version would need to
        differentiate h_t numerically instead (see docs §PEE), so this is LOG-specific, not reusable. """
        ξ, α = self.get('ξ', t), self.get('α', t)
        return -1/(1-τ) * ξ/(1+α*ξ)

    # dlnc2i_dτ/dlnc20_dτ: old generations' dln(c)/dτ_t, preference-agnostic once dlnh_dτ is explicit --
    # LOG and CRRA share these exactly, differing only in how dln(h_t)/dτ_t is obtained (closed form here
    # vs. a numerical grid derivative for CRRA t<T, docs §PEE). dv2i_dτ_LOG/dv20_dτ_LOG below are thin LOG
    # wrappers.
    def dlnc2i_dτ(self, dlnh_dτ, τ, θ, siRatio_, t = None):
        """ Eq (PEE)/(PEELOG): dln(c_{2,t}^i)/dτ_t, given dln(h_t)/dτ_t. Preference-agnostic -- see the
        §(c) note above. siRatio_ = s_{t-1}^i/s_{t-1} (explicit -- predetermined at t, but itself a
        function of τ_t via si_s, see docs).

        This is also why the docs forbid taking this derivative numerically off a solution grid (docs §PEE,
        the c_{2,t}^i footnote): siRatio_ varies along such a grid, and the policy maker takes it as
        predetermined, so a grid derivative would fold in a channel that does not belong in the FOC. The
        closed form here holds siRatio_ fixed by construction. """
        α, p_, κ_ = self.get('α', t), self.get('p[t-1]', t), self.get('κ[t-1]', t)
        A0 = (1-α)/α * p_/κ_
        bracket = (self._bcast(self.wedgeA(θ))*self.hηRatio(t, lag = '[t-1]')
                   + self._bcast(self.wedgeB(θ)))
        num = self._bcast(A0) * bracket
        denom = siRatio_ + self._bcast(A0*τ)*bracket
        return self._bcast((1-α)*dlnh_dτ) + num/denom

    def dlnc20_dτ(self, dlnh_dτ, τ, ε, Θh, t = None):
        """ Eq (PEE)/(PEELOG): dln(tilde-c_{2,t}^0)/dτ_t, given dln(h_t)/dτ_t. Preference-agnostic -- see
        the §(c) note above. Θh: Θ_{h,t} (explicit) -- unlike dlnc2i_dτ this genuinely needs Θ_{h,t}'s
        *value*, not just its τ-derivative, so the caller passes the already-correctly-stacked
        general/terminal Θh. Unlike dlnc2i_dτ this one *could* legitimately be approximated on a grid
        instead (the docs note as much); we use the closed form for consistency with dlnc2i_dτ. """
        α, ξ, ν, κ_ = self.get('α', t), self.get('ξ', t), self.get('ν', t), self.get('κ[t-1]', t)
        Θh1mα = Θh**(1-α)
        coefSmooth = self.auxProd0χ(t, lag = '[t-1]')/(1+ξ) * ((1-α)/self.Γh(t)**α)**((1+ξ)/(1+α*ξ))
        coefUniversal = (1-α)*ν*ε/κ_ * Θh1mα
        num = coefUniversal * (1 + (1-α)*τ*dlnh_dτ)
        denom = coefSmooth + coefUniversal*τ
        return num/denom

    def dv2i_dτ_LOG(self, τ, θ, siRatio_, t = None):
        """ Eq (PEELOG): dυ_{2,t}^i/dτ_t -- marginal indirect utility of the old formal type-i household.
        The LOG case of dlnc2i_dτ: under log preferences dυ/dτ *is* dln(c)/dτ (the c^{1-1/ρ} weight is
        c^0=1), and dln(h_t)/dτ_t has the closed form dlnΘh_dτ_LOG. Literally the same formula at t<T-1
        and t=T-1 (the doc calls the terminal expression a "replica" of the general one) -- so, unlike
        dv1i_dτ_LOG, no FH_* wrapper is needed; the only t=T-1 vs. t<T-1 difference is which Θh went into
        dlnΘh_dτ_LOG upstream, and dlnΘh_dτ_LOG's own formula doesn't change either. """
        return self.dlnc2i_dτ(self.dlnΘh_dτ_LOG(τ, t), τ, θ, siRatio_, t)

    def dv20_dτ_LOG(self, τ, ε, Θh, t = None):
        """ Eq (PEELOG): dυ_{2,t}^0/dτ_t -- marginal indirect utility of the old informal household. The
        LOG case of dlnc20_dτ (see dv2i_dτ_LOG's docstring for why dυ/dτ = dln(c)/dτ here). Θh must be the
        already-correctly-stacked general/terminal Θ_{h,t} (e.g. as EE_LOG_solve/FH_h build it --
        ΘhTerminal at t=T-1, Θh elsewhere). """
        return self.dlnc20_dτ(self.dlnΘh_dτ_LOG(τ, t), τ, ε, Θh, t)

    #######################################################################
    ##########   10. Calibration targets (eq:calibration)          #########
    #######################################################################
    # Evaluated at the single baseline year db['t0'] -- pass that year as `t`, never rely on the default.
    # The US targets are R_{t0} and τ_{t0} (plus avgHours under commonX, see model.py §8). savingsRate is
    # kept because the savings rate is still *reported* here, it is just no longer a target; the informal
    # η0/X0 target helpers of the Argentina models are gone with the type that had a mass.
    def savingsRate(self, s, s_, h, t = None):
        """ Eq (calibration): s_t / ((s_{t-1}/ν_t)^α h_t^{1-α}). s, s_=s_{t-1}, h explicit. """
        α = self.get('α', t)
        return s / ((s_/self.get('ν', t))**α * h**(1-α))

    def avgHours(self, h, t = None):
        """ Eq (avgHours): the average workweek h̄_t = ∑_i γ_{t,i}h_{t,i} = h_t·∑_i γ_{t,i}·hRatio_i.

        NOT the aggregate h_t, which weights by productivity (∑_i γ_i η_i h_{t,i} = h_t) and is in
        efficiency units. Only h̄_t is comparable to an observed workweek, and -- see eq:hoursUnit -- only
        h̄_t and h_{t,i} respond to the hours unit that the commonX calibration pins down. h_t does not,
        which is exactly why h_t cannot serve as the target in its place. """
        return h * (self.get('γi', t) * self.hRatio(t)).sum(axis = -1)


class BaseGrid(Base):
    """ Assumes parameters from database are selected for a single year,
        but inputs/arguments are grids of the same length. """

class BaseTime(Base):
    """ Assume parameters from database are functions of time and
    so are inputs/arguments. """

    def _year(self, t = None):
        """ No year dimension here -- symbols are returned as whole time paths, so a lookup's result does
        not depend on t at all and every cache key collapses to the symbol (plus lag). """
        return None

    def __call__(self, k, t = None):
        """ Return the full time-indexed symbol 'k' (no year-slicing) -- parameters and inputs are vectors over t here. """
        return self._memo(('call', k, None), lambda: self.db[f'{k}'])

    def Γh(self, t = None, lag = ''):
        """ Matches Base.Γh's return type (plain ndarray, not a pandas Series) -- several formulas
        (Θh, ΘhTerminal, Θs, w0, c10/tildec10, c20/tildec20) use self.Γh(t) directly without going
        through self._bcast, so leaving this as a Series would silently break positional indexing
        (e.g. `result[-1]`) on their output whenever called via BaseTime. Memoised inside cacheParams()
        as in Base -- with its own key, since the value differs (a full path, not one year's scalar). """
        return self._memo(('Γh', lag, None), lambda:
            (self(f'γi{lag}', t) * self.auxProd(t, lag = lag)).sum(axis = 1).values)

    #######################################################################
    ##########   8. Finite-horizon terminal stacking (FH_*)         ########
    #######################################################################
    # Several quantities use a *different* formula at the terminal period (t=T-1) than for t<T-1 (e.g.
    # labour supply: Θh, needing Γs_t/τ_{t+1}/θ_{t+1}, vs. ΘhTerminal). These FH_* methods own that
    # stacking once rather than repeating it at every call site (EE_LOG_solve, EE_CRRA_*, EE_report).
    # Convention: Γs/B are length T-1 (genuinely undefined at T, no period T+1 to look into); h/s/τ/τ1/θ1
    # are length T. Where the terminal formula is a special case of the general one (c1i, tildec1i --
    # feeding B=0/Γs=0 alongside s_T=0 makes the smoothing/pension terms vanish, verified algebraically),
    # padding replaces branching; where it isn't (FH_h), the terminal entry is computed separately.
    def FH_h(self, τ, τ1, θ1, Γs, s_, t = None):
        """ Labour supply h_t, stacking Θh (eq:auxiliary:Thetah, t<T-1) with ΘhTerminal
        (eq:auxiliary:ThetahT, t=T-1). Γs: length T-1. τ, τ1, θ1, s_ (=s_{t-1} for every t): length T.
        Returns length-T array. """
        Γs_pad = np.append(Γs, 0) # dummy -- Θh's terminal-index output is overwritten below, never used
        Θh = self.Θh(τ, τ1, θ1, Γs_pad, t)
        Θh[-1] = self.ΘhTerminal(τ, t)[-1]
        return self.h(Θh, s_, t)

    def FH_c1i(self, h, s, B, τ1, θ1, t = None):
        """ Eq (EE:ci) stacked with the terminal formula (§Finite Horizon Terminal state) at t=T-1:
        c1_T^i = auxProd_i(h_T/Γh_T)^{(1+ξ)/ξ}, with no pension/smoothing term (no period T+1 to smooth
        into). Padding B with 0 and relying on the finite-horizon s[-1]=0 makes c1i's general formula
        collapse to exactly this. h, s, τ1, θ1: length T. B: length T-1. """
        B_pad = np.vstack([B, np.zeros((1, B.shape[1]))])
        return self.c1i(h, s, B_pad, τ1, θ1, t)

    def FH_tildec1i(self, h, B, τ1, θ1, Γs, t = None):
        """ As FH_c1i, for tildec1i (see FH_c1i's docstring for the terminal-collapse argument -- here
        driven by padding both B and Γs with 0). h, τ1, θ1: length T. B, Γs: length T-1. """
        B_pad = np.vstack([B, np.zeros((1, B.shape[1]))])
        Γs_pad = np.append(Γs, 0)
        return self.tildec1i(h, B_pad, τ1, θ1, Γs_pad, t)

    def FH_dv1i_LOG(self, β, τ, t = None):
        """ dυ_{1,t}^i/dτ_t (eq:PEELOG) stacked with the terminal formula (eq:terminalPEELOG) at t=T-1:
        the doc gets the terminal expressions by reusing the general ones with β_{t,j}=0 throughout, and
        zeroing dv1i_dτ_LOG's β argument at the terminal index reproduces that exactly (the β-term is the
        only place β enters). β, τ: length T (β already at its natural full-horizon length, unlike Γs/B --
        nothing to pad in length, just overwrite the terminal entry). """
        β_pad = β.copy()
        β_pad[-1] = 0
        return self.dv1i_dτ_LOG(β_pad, τ, t)

    def FH_dv10_LOG(self, β0, τ, t = None):
        """ As FH_dv1i_LOG, for the informal young (dυ_{1,t}^0/dτ_t) -- zeroing β0's terminal entry
        collapses dv10_dτ_LOG's general formula to the terminal one (=0) exactly, since β0 is
        dv10_dτ_LOG's only factor besides τ. β0, τ: length T. """
        β0_pad = β0.copy()
        β0_pad[-1] = 0
        return self.dv10_dτ_LOG(β0_pad, τ, t)
