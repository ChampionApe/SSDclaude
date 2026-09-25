$env:PYTHONUTF8 = '1'
$repo = 'C:\Users\sxj477\Documents\GitHub\SSDclaude'
$py = "$repo\.venv\Scripts\python.exe"
$log = "$repo\logs\escSizeCand81_0924.log"
Set-Location $repo
# Stop condition S4 / check 11 of notes/plan_escSizeLeak.md: the exact 2-D choice at rho = 2 under 'size' with
# 81 candidates instead of 41, for the scenarios where the path iteration separated by more than 0.02.
Add-Content -Encoding UTF8 $log ("START cand81 " + (Get-Date))
cmd /c "`"$py`" python\US\runESCcrra.py --exact --rho 2.0 --spec size --phi 0.5 --commonX --stage shocks --scenarios baseline frVoting frBoth --ns 150 --nsScan 50 --nCand2D 81 --tag _cand81 > `"$repo\logs\escSizeCand81Run0924.log`" 2>&1"
Add-Content -Encoding UTF8 $log ("cand81 exit $LASTEXITCODE " + (Get-Date))
Add-Content -Encoding UTF8 $log ('DONE ' + (Get-Date))
