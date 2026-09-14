# Keeps the self-hosted GitHub Actions runner alive.
#
# Root cause: the runner lives inside the WSL distro `Ubuntu-24.04`. WSL
# stops the distro when no session holds it open, and a stopped distro
# means an OFFLINE runner - every workflow run then sits in `queued`
# forever. `vmIdleTimeout=-1` in .wslconfig was measured NOT to be enough:
# the distro was found stopped with that setting already in place.
#
# Fix: a systemd unit `rankwant-holder` inside the distro runs
# `/bin/sleep infinity`, so a process always holds the distro open. This
# script boots the distro, makes sure that unit is active, then makes sure
# the runner service is active.
#
# Why a unit and not `pgrep`: a pgrep-based probe matches its own command
# line and always reports the holder as running, so the holder is never
# actually started. `systemctl is-active` cannot lie that way.
#
# Idempotent - safe to run on a schedule.
#
# Usage (PowerShell):
#   powershell -File tools\runner_keepalive.ps1

$ErrorActionPreference = 'Continue'

$distro  = 'Ubuntu-24.04'
$runner  = 'actions.runner.menarzullayev-rankwant.nsn-pc-rankwant.service'
$holder  = 'rankwant-holder.service'

$logFile = Join-Path (Split-Path -Parent $PSScriptRoot) '.tmp\runner-keepalive.log'
New-Item -ItemType Directory -Force -Path (Split-Path $logFile) | Out-Null

function Log {
    param([string]$Text)
    $line = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + '  ' + $Text
    Write-Output $line
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

Log '--- keepalive ---'

# 1) Wake the distro. A trivial command is enough to boot it.
& wsl.exe -d $distro -u root -- bash -lc 'true' | Out-Null
Start-Sleep -Seconds 3

# 2) Holder unit - keeps a process alive so WSL will not stop the distro.
$h = (& wsl.exe -d $distro -u root -- bash -lc ('systemctl is-active ' + $holder)) | Out-String
if ($h.Trim() -ne 'active') {
    Log ('holder ' + $h.Trim() + ' - start')
    & wsl.exe -d $distro -u root -- bash -lc ('systemctl start ' + $holder) | Out-Null
    Start-Sleep -Seconds 3
    $h = (& wsl.exe -d $distro -u root -- bash -lc ('systemctl is-active ' + $holder)) | Out-String
}
Log ('holder: ' + $h.Trim())

# 3) Runner service must be active.
$r = (& wsl.exe -d $distro -u root -- bash -lc ('systemctl is-active ' + $runner)) | Out-String
if ($r.Trim() -ne 'active') {
    Log ('runner ' + $r.Trim() + ' - start')
    & wsl.exe -d $distro -u root -- bash -lc ('systemctl start ' + $runner) | Out-Null
    Start-Sleep -Seconds 8
    $r = (& wsl.exe -d $distro -u root -- bash -lc ('systemctl is-active ' + $runner)) | Out-String
}
Log ('runner: ' + $r.Trim())
