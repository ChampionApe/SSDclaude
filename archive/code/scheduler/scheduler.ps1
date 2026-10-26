# C6 reruns: start the jobs of jobs.tsv (gen_jobs.py) under a cap of 5 solver processes. Solvers are the python.exe
# processes on the machine whose parent is not a python.exe (the venv launcher and its interpreter count once); every
# job inherits OMP/MKL/OPENBLAS_NUM_THREADS = 1. A job starts, in file order, when every job it depends on has exited 0
# and passed its log checks (require: a case-sensitive regex the log must contain; fail: one it must not). A job whose
# dependency failed is skipped. HOLD in this directory pauses launching, STOP ends the scheduler (running jobs go on).
# jobs.tsv is re-read every loop. On restart, ok/failed come from scheduler.log ('reset NAME' lines clear one), and a
# job still running from the previous instance is adopted by its cmd.exe command line.
param([string]$dir = 'C:\Users\sxj477\Documents\GitHub\SSDclaude\logs\C6runs')
$ErrorActionPreference = 'Continue'
$repo = 'C:\Users\sxj477\Documents\GitHub\SSDclaude'
$jobsFile = Join-Path $dir 'jobs.tsv'
$log = Join-Path $dir 'scheduler.log'
$cap = 5
Set-Location $repo
$env:OMP_NUM_THREADS = '1'; $env:MKL_NUM_THREADS = '1'; $env:OPENBLAS_NUM_THREADS = '1'; $env:PYTHONUTF8 = '1'
$utf8 = New-Object System.Text.UTF8Encoding $false

function Now { Get-Date -Format 'MM-dd HH:mm:ss' }
function Log([string]$s) {
  for ($i = 0; $i -lt 20; $i++) {
    try { [System.IO.File]::AppendAllText($log, "$(Now) $s`r`n", $utf8); return } catch { Start-Sleep -Milliseconds 500 }
  }
}
function ReadJobs {
  $jobs = New-Object System.Collections.ArrayList
  foreach ($line in [System.IO.File]::ReadAllLines($jobsFile)) {
    if ($line.Trim() -eq '' -or $line.StartsWith('#')) { continue }
    $f = $line.Split("`t")
    if ($f.Count -lt 6) { continue }
    $deps = @(); if ($f[2] -ne '-') { $deps = @($f[2].Split(',')) }
    [void]$jobs.Add([pscustomobject]@{ name = $f[0]; cls = $f[1]; deps = $deps; require = $f[3]; fail = $f[4]; cmd = $f[5] })
  }
  return $jobs
}
function CountSolvers {
  $all = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'")
  $ids = @($all | ForEach-Object { $_.ProcessId })
  return @($all | Where-Object { $ids -notcontains $_.ParentProcessId }).Count
}
function CheckLog($job) {
  $lf = Join-Path $dir ($job.name + '.log')
  if (-not (Test-Path $lf)) { return 'no log' }
  $txt = [System.IO.File]::ReadAllText($lf)
  if ($job.fail -ne '-' -and $txt -cmatch $job.fail) { return "log matches /$($job.fail)/" }
  if ($job.require -ne '-' -and -not ($txt -cmatch $job.require)) { return "log lacks /$($job.require)/" }
  return ''
}

$state = @{}; $procs = @{}; $t0 = @{}
if (Test-Path $log) {
  foreach ($l in [System.IO.File]::ReadAllLines($log)) {
    if ($l -match '^\S+ \S+ (start|ok|failed|reset) (\S+)') {
      $ev = $Matches[1]; $nm = $Matches[2]
      if ($ev -eq 'reset') { $state.Remove($nm) } elseif ($ev -eq 'start') { $state[$nm] = 'orphan' } else { $state[$nm] = $ev }
    }
  }
}
Log "SCHEDULER pid $PID (cap $cap)"
foreach ($nm in @($state.Keys)) {
  if ($state[$nm] -ne 'orphan') { continue }
  $c = Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" | Where-Object { $_.CommandLine -like "*\$nm.log *" } | Select-Object -First 1
  if ($c) {
    $p = Get-Process -Id $c.ProcessId -ErrorAction SilentlyContinue
    if ($p) { $null = $p.Handle; $procs[$nm] = $p; $t0[$nm] = $p.StartTime; $state[$nm] = 'running'; Log "adopt $nm pid $($p.Id)"; continue }
  }
  $state[$nm] = 'failed'; Log "failed $nm (exited while no scheduler was watching; read its log, then 'reset' it)"
}

while ($true) {
  if (Test-Path (Join-Path $dir 'STOP')) { Log 'STOP requested; running jobs continue'; break }
  $jobs = ReadJobs
  foreach ($nm in @($procs.Keys)) {
    $p = $procs[$nm]
    if (-not $p.HasExited) { continue }
    $code = $p.ExitCode
    $el = '{0:N2} h' -f (((Get-Date) - $t0[$nm]).TotalHours)
    $why = ''
    if ($null -ne $code -and $code -ne 0) { $why = "exit $code" }
    else { $jb = $jobs | Where-Object { $_.name -eq $nm } | Select-Object -First 1; if ($jb) { $why = CheckLog $jb } }
    if ($why -eq '') { $state[$nm] = 'ok'; Log "ok $nm ($el)" } else { $state[$nm] = 'failed'; Log "failed $nm ($el): $why" }
    $procs.Remove($nm)
  }
  $changed = $true
  while ($changed) {
    $changed = $false
    foreach ($jb in $jobs) {
      if ($state.ContainsKey($jb.name)) { continue }
      $bad = @($jb.deps | Where-Object { $state[$_] -eq 'failed' -or $state[$_] -eq 'skipped' })
      if ($bad.Count -gt 0) { $state[$jb.name] = 'skipped'; Log "skipped $($jb.name): $($bad -join ',') did not succeed"; $changed = $true }
    }
  }
  if (-not (Test-Path (Join-Path $dir 'HOLD'))) {
    while ($true) {
      $n = [Math]::Max((CountSolvers), $procs.Count)
      if ($n -ge $cap) { break }
      $next = $null
      foreach ($jb in $jobs) {
        if ($state.ContainsKey($jb.name)) { continue }
        $unmet = @($jb.deps | Where-Object { $state[$_] -ne 'ok' })
        if ($unmet.Count -eq 0) { $next = $jb; break }
      }
      if ($null -eq $next) { break }
      $arg = "/c $($next.cmd) > $dir\$($next.name).log 2>&1"
      $p = Start-Process -FilePath 'cmd.exe' -ArgumentList $arg -WorkingDirectory $repo -WindowStyle Hidden -PassThru
      $null = $p.Handle
      $procs[$next.name] = $p; $t0[$next.name] = Get-Date; $state[$next.name] = 'running'
      Log "start $($next.name) [$($next.cls)] pid $($p.Id) (solvers before: $n)"
      Start-Sleep -Seconds 10
    }
  }
  $open = @($jobs | Where-Object { -not $state.ContainsKey($_.name) })
  if ($open.Count -eq 0 -and $procs.Count -eq 0) {
    $nf = @($state.Values | Where-Object { $_ -eq 'failed' }).Count
    $ns = @($state.Values | Where-Object { $_ -eq 'skipped' }).Count
    Log "DONE ($nf failed, $ns skipped)"
    break
  }
  Start-Sleep -Seconds 30
}
