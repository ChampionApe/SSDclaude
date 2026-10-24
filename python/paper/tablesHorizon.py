r""" Appendix D's tables (app:T): the horizon and the terminal condition (NUM_Horizon), and the first order
condition's residuals off the policy functions' grids (NUM_Residuals). The candidate counts are
tablesOA.numSelection (NUM_Selection), which appendix D and the online appendix share.

Inputs: results/numerical/{US_horizon,US_horizonDesign,US_residuals,US_derivativeScheme}.csv
(python/US/runHorizon.py) and ARG_horizon_commonX.csv, ARG_residuals_commonX.csv
(python/InformalSavings/runHorizon.py), read through datasets.horizon/residuals/derivativeScheme. Layout as
tablesOA: tablesUS._xwrap, a note in the house form, every body row ending in ` % row: <key>`. Rates in
percent to two decimals, their changes across horizons in p.p. to three, the design theta to three.
"""
import numpy as np

import config as C
import datasets as D
from tablesUS import _xwrap
from tablesOA import _row, _body, _signed, _rhoKey

BASE_TSS = 3                                     # the paper's horizon: three periods after the last projection
ALTERNATIVES = (('finite', 1), ('finite', 6), ('steadyState', None))
RHOS = (0.5, 1.0, 2.0)


def _label(name):
    return 'table:T:' + name


def _pick(df, block, ρ, terminal, tss):
    """ The rows of one (block, rho, horizon), indexed by date; tss None takes the steady-state rows. """
    sub = df[(df['block'] == block) & np.isclose(df['ρ'], ρ) & (df['terminal'] == terminal)]
    if tss is not None:
        sub = sub[sub['tss'] == tss]
    if sub['tss'].nunique() != 1:
        raise ValueError('NUM_Horizon: {} rows for ({}, rho = {}, {}, {})'.format(
            'no' if sub.empty else 'several horizons of', block, ρ, terminal, tss))
    return sub.set_index('date')


def _horizonPanel(df, title, years, outcomes):
    """ One panel: a title row with the two dates under every horizon, then a row per (outcome, rho): the
    level at the paper's horizon, and each alternative's change against it at the same date. """
    t0, t1 = years
    lines = [r'\multicolumn{2}{l}{\textit{' + title + r'}} & ' + ' & '.join([str(t0), str(t1)]*4) + r' \\',
             r'\cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}\cmidrule(lr){9-10}']
    for label, block, col, level, change, key in outcomes:
        for k, ρ in enumerate(RHOS):
            base = _pick(df, block, ρ, 'finite', BASE_TSS)
            cells = [label if k == 0 else '', C.num(ρ, 1)] + [level(base.loc[t, col]) for t in years]
            for terminal, tss in ALTERNATIVES:
                alt = _pick(df, block, ρ, terminal, tss)
                cells += [change(alt.loc[t, col] - base.loc[t, col]) for t in years]
            lines.append(_row(cells, key + '@' + _rhoKey(ρ)))
        lines[-1] = lines[-1].replace(r' \\ % row:', r' \\[.4em] % row:')
    return lines


def numHorizon():
    r""" Table app:T's horizon check: the tax, the savings rate and (in the U.S.) the chosen design at the
    calibration year and one period later, at the paper's horizon (T = 2200 in the U.S., 2190 in Argentina)
    and the change against it at two periods shorter, three periods longer and under the steady-state terminal
    condition, every parameter at its calibrated value. Rows keyed `<arm>_<outcome>@<rho>`. """
    us, arg = D.horizon('US'), D.horizon('ARG')
    pct = lambda v: C.num(100*v, 2)
    dpp = lambda v: _signed(100*v, 3)
    th, dth = (lambda v: C.num(v, 3)), (lambda v: _signed(v, 3))
    yUS, yARG = C.usCalendar()['year0'], C.calendar()['year0']
    lines = _horizonPanel(us, 'United States', (yUS, yUS + 30), [
        ('Tax rate (\\%), design given', 'tax', 'τ', pct, dpp, 'us_tax'),
        ('Savings rate (\\% of GDP), design given', 'tax', 'srOverY', pct, dpp, 'us_savings'),
        (r'Design $\theta$, chosen', 'design', 'θ', th, dth, 'us_design'),
        ('Tax rate (\\%), design chosen', 'design', 'τ', pct, dpp, 'us_taxchosen'),
        ('Savings rate (\\% of GDP), design chosen', 'design', 'srOverY', pct, dpp, 'us_savingschosen')])
    lines += _horizonPanel(arg, 'Argentina', (yARG, yARG + 30), [
        ('Tax rate (\\%)', 'tax', 'τ', pct, dpp, 'arg_tax'),
        ('Savings rate (\\% of GDP)', 'tax', 'srGDP', pct, dpp, 'arg_savings'),
        ('Universal pension: change in the tax rate (p.p.)', 'tax', 'dτ', lambda v: _signed(100*v, 2), dpp,
         'arg_reform')])
    Tus = {k: int(_pick(us, 'tax', 0.5, *k)['T'].iloc[0]) for k in (('finite', BASE_TSS), ('finite', 1), ('finite', 6))}
    Targ = {k: int(_pick(arg, 'tax', 1.0, *k)['T'].iloc[0]) for k in (('finite', BASE_TSS), ('finite', 1), ('finite', 6))}
    gaps = [float(_pick(df, b, ρ, 'steadyState', None)['statGap'].max())
            for df, b in ((us, 'tax'), (arg, 'tax')) for ρ in RHOS if 'statGap' in df.columns
            and np.isfinite(_pick(df, b, ρ, 'steadyState', None)['statGap']).any()]
    kSS = int(_pick(us, 'tax', 0.5, 'steadyState', None)['tss'].iloc[0])
    note = (r'\textit{Note:} Every parameter at its calibrated value at the paper' + "'" + r's horizon, $T = '
            + str(Tus[('finite', BASE_TSS)]) + r'$ in the United States and $' + str(Targ[('finite', BASE_TSS)])
            + r'$ in Argentina; the first two columns are the levels there. The other columns are the change '
            r'against them at the same date: with the backward induction started two periods earlier ($T = '
            + str(Tus[('finite', 1)]) + r'$ and $' + str(Targ[('finite', 1)]) + r'$), three periods later ($T = '
            + str(Tus[('finite', 6)]) + r'$ and $' + str(Targ[('finite', 6)]) + r'$), and under the steady-state '
            r'terminal condition of appendix \ref{app:T}, population growth held at its last projected rate from '
            r'the last projection date on and the policy functions stationary from there, computed as the finite '
            r'horizon extended by ' + str(kSS) + r' periods (at the paper' + "'" + r's $T$ its tax policy '
            r'differs from that of the period after by at most ' + _sci(max(gaps)) + r' over the states the '
            r'path visits). Tax and savings rates in percent and their changes in percentage points, the '
            r'design in units of $\theta$. Under log preferences ($\rho = 1$) the U.S.\ tax at every date '
            r'and the design chosen at every date but $T - 1$ do not depend on the horizon. The design is '
            r'chosen one period ahead under the paper' + "'" + r's cost, at its calibrated $\lambda$; in '
            r'Argentina the universal pension is that of section \ref{sec:argentina}, its change against '
            r'the baseline of the same horizon.')
    head = (r'\textbf{Outcome} & $\bm{\rho}$ & \multicolumn{2}{c}{\textbf{Paper' + "'" + r's $\bm{T}$}} & '
            r'\multicolumn{2}{c}{\textbf{Two periods shorter}} & \multicolumn{2}{c}{\textbf{Three periods '
            r'longer}} & \multicolumn{2}{c}{\textbf{Steady state}}')
    return _xwrap('NUM_Horizon', 'results/numerical/{US_horizon,US_horizonDesign,ARG_horizon'
                  + C.argVariantTag(C.ARG['commonX']) + '}.csv',
                  'The horizon and the terminal condition', _label('Horizon'),
                  r'>{\raggedright\arraybackslash}p{3.4cm}c' + 'Y'*8, head, _body(lines), note,
                  width = r'\textwidth', size = r'\footnotesize')


def _sci(v):
    """ A small positive number as $a \times 10^{b}$ (one decimal); zero as $0$. """
    if not np.isfinite(v) or v == 0:
        return '$0$'
    e = int(np.floor(np.log10(abs(v))))
    return r'${:.1f} \times 10^{{{}}}$'.format(v/10**e, e)


def _pp2(v):
    """ |residual| in p.p. of the tax to two significant digits; '--' where there is none. """
    if v is None or not np.isfinite(v):
        return '--'
    x = 100*float(v)
    return '$0$' if x == 0 else '{:#.2g}'.format(x).rstrip('.') if x >= 1e-3 else _sci(x)


RESIDUALCOLS = (('path', 'visited', 'max'), ('cell', 'visited', 'max'), ('cell', 'visited', 'p99'),
                ('cell', 'all', 'max'))


def _residualCells(df, sel):
    """ The four statistics of RESIDUALCOLS for both references (the solver's condition, then the condition
    with converged tax derivatives) from the pooled rows (date 'all') of one (model, rho, ns). """
    pooled = df[sel & (df['date'] == 'all')].set_index(['set', 'region'])
    out = []
    for suffix in ('', 'Ref'):
        for s, r, stat in RESIDUALCOLS:
            out.append(_pp2(pooled.loc[(s, r), stat + suffix]) if (s, r) in pooled.index else '--')
    return out


def numResiduals():
    r""" Table app:T's accuracy check: |tau_FOC - tau_hat| in p.p. of the tax at states off the grids the
    policy functions were solved on, the 2200 (2190) horizon, pooled over periods: at the state the path
    enters each period with, at the centres of the grid's cells within the range the path visits (largest
    and 99th percentile) and anywhere on the grid (largest); against the first order condition as the solver
    evaluates it and against the condition with converged tax derivatives. The U.S. at both state grids the
    paper uses (150 nodes for every solve, 50 for the cost calibration's scan). Rows keyed
    `<arm>@<rho>[@<ns>]`. """
    us, arg = D.residuals('US'), D.residuals('ARG')
    lines = [r'\multicolumn{10}{l}{\textit{United States, CRRA preferences}} \\']
    for ns in sorted(us['ns'].dropna().unique(), reverse = True):
        for ρ in sorted(us['ρ'].unique()):
            sel = np.isclose(us['ρ'], ρ) & (us['ns'] == ns)
            lines.append(_row([C.num(ρ, 1), str(int(ns))] + _residualCells(us, sel),
                              'us@' + _rhoKey(ρ) + '@' + str(int(ns))))
    lines[-1] = lines[-1].replace(r' \\ % row:', r' \\[.4em] % row:')
    lines.append(r'\multicolumn{10}{l}{\textit{Argentina}} \\')
    for ρ in sorted(arg['ρ'].unique()):
        sub = arg[np.isclose(arg['ρ'], ρ)]
        grid = '45' + (r'$\times$45' if (sub['preferences'] == 'CRRA').all() else '')
        lines.append(_row([C.num(ρ, 1), grid] + _residualCells(arg, np.isclose(arg['ρ'], ρ)), 'arg@' + _rhoKey(ρ)))
    sch = D.derivativeScheme()
    gap = lambda s, ρ: (float(sch[(sch['scheme'] == s) & np.isclose(sch['ρ'], ρ) & (sch['scenario'] == 'theta0')
                                  & (sch['date'] == C.usCalendar()['year0'])]['τ'].iloc[0])
                        - float(sch[(sch['scheme'] == s) & np.isclose(sch['ρ'], ρ) & (sch['scenario'] == 'theta1')
                                    & (sch['date'] == C.usCalendar()['year0'])]['τ'].iloc[0]))
    base = lambda s, ρ, d: float(sch[(sch['scheme'] == s) & np.isclose(sch['ρ'], ρ) & (sch['scenario'] == 'baseline')
                                     & (sch['date'] == d)]['τ'].iloc[0])
    y0 = C.usCalendar()['year0']
    ρs = sorted(sch['ρ'].unique())
    nTau = lambda df: (int(df['nTau'].iloc[0]) - 1)*int(df['refine'].iloc[0]) + 1     # runHorizon.refined's nodes
    both = lambda f: ' and '.join(f(ρ) for ρ in ρs)
    note = (r'\textit{Note:} Each cell is the largest (or 99th percentile) absolute difference, in percentage '
            r'points of the tax rate, between the root of the first order condition at a state and the policy '
            r'function there, over the periods of the paper' + "'" + r's horizon: at the state the equilibrium '
            r'path enters each period with, at the centres of the state grid' + "'" + r's cells within the range '
            r'the path visits (padded by a fifth), and at the centres of all its cells. The grid column gives the '
            r'nodes of the state grid. The root is located by the selection of every period, without the smoothing '
            r'of the policy, against the solved continuation. The first four columns evaluate the condition as '
            r'the solver does; the last four with its derivatives in the tax converged, on a tax grid of '
            + str(nTau(us)) + r' nodes in the U.S.\ and ' + str(nTau(arg)) + r' in Argentina. The U.S.\ solver '
            r'differentiates along the tax with a smoothing spline, Argentina' + "'" + r's along $\ln(1-\tau)$ with '
            r'an interpolating one. Solved at every period with converged derivatives and the calibrated parameters, '
            r'the U.S.\ tax in ' + str(y0) + ' is ' + both(lambda ρ: C.num(100*base('reference', ρ, y0), 2) + r'\%')
            + ' at $\\rho = ' + both(lambda ρ: C.num(ρ, 1)).replace(' and ', '$ and $') + r'$ (the calibration'
            + "'" + r's ' + C.num(100*base('published', ρs[0], y0), 2) + r'\%), and the difference between '
            r'$\theta = 0$ and $\theta = 1$ is ' + both(lambda ρ: C.num(100*gap('reference', ρ), 2))
            + ' p.p. against ' + both(lambda ρ: C.num(100*gap('published', ρ), 2)) + r' p.p. Log preferences in '
            r'the U.S.\ have no state.')
    head = (r'$\bm{\rho}$ & \textbf{Grid} & \multicolumn{4}{c}{\textbf{As solved}} & \multicolumn{4}{c}{\textbf{'
            r'Converged derivatives}} \\' + '\n'
            r'\cmidrule(lr){3-6}\cmidrule(lr){7-10}' + '\n'
            r' & & Path & Visited, max & Visited, 99\% & All, max & Path & Visited, max & Visited, 99\% & '
            r'All, max')
    return _xwrap('NUM_Residuals', 'results/numerical/{US_residuals,US_derivativeScheme,ARG_residuals'
                  + C.argVariantTag(C.ARG['commonX']) + '}.csv',
                  'First order condition residuals off the grid', _label('Residuals'),
                  r'cc' + 'Y'*8, head, _body(lines), note, width = r'\textwidth', size = r'\footnotesize')
