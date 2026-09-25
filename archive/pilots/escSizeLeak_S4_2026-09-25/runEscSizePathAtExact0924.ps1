$env:PYTHONUTF8 = '1'
$repo = 'C:\Users\sxj477\Documents\GitHub\SSDclaude'
$py = "$repo\.venv\Scripts\python.exe"
$log = "$repo\logs\escSizePathAtExact0924.log"
Set-Location $repo
# S4 diagnostic: the path-iteration method at rho = 2 under 'size' evaluated at the EXACT method's lambda
# (1.728, planted as a method = path row in the tagged calibration csv), so the method gap is measured at one
# lambda rather than at each method's own.
Add-Content -Encoding UTF8 $log ("START pathAtExact " + (Get-Date))
cmd /c "`"$py`" python\US\runESCcrra.py --rho 2.0 --spec size --phi 0.5 --commonX --stage shocks --scenarios baseline frVoting frBoth --ns 150 --tag _pathAtExact > `"$repo\logs\escSizePathAtExactRun0924.log`" 2>&1"
Add-Content -Encoding UTF8 $log ("pathAtExact exit $LASTEXITCODE " + (Get-Date))
Add-Content -Encoding UTF8 $log ('DONE ' + (Get-Date))
