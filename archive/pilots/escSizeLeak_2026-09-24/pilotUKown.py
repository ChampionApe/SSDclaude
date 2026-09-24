import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pilotQuadWedge as P          # installs the patched fWedge
import runESC as R
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
for spec, scale in (('quad', 1.0), ('quadSize', 0.1185714285714286/0.1442857142857143)):
    tic = time.time()
    m = R.buildEU('UK', {'spec': spec, 'phi': 0.5, 'p': 2.0}, commonX = True)
    m.db['wedgeScale'] = scale
    try:
        rec = m.calibrateWedge(spec = spec, phi = 0.5, bracket = (0.3, 20.0), nScan = 10, verbose = False)
        print(spec, 'UK own λ:', round(rec['p'], 4), 'residual', rec['residual'], rec['message'], f'({time.time()-tic:.0f}s)')
    except Exception as e:
        print(spec, 'FAILED', type(e).__name__, e)
