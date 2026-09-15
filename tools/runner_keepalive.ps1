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
# Measured 2026-09-15 on this machine (read-only inspection):
#   - Scheduled task `RankWant-Runner-Keepalive` (Ready, last result 0)
#     runs THIS script: `-File ...\tools\runner_keepalive.ps1`.
#   - `systemctl is-active rankwant-holder.service` reports `active`, and
#     the unit is `enabled` in `systemctl list-unit-files`. The unit lives
#     on the machine only - there is no unit file in this repo, so a
#     rebuilt machine must recreate it before this script can start it.
#   - A separate task `RankWant-WSL-Holder` (Running) also holds the
#     distro from the Windows side, with no script involved:
#     `wsl.exe -d Ubuntu-24.04 -u root -- bash -lc "exec sleep 2147483647"`.
#     Both belts are live at once; this script owns the distro-side one.
#
# An older duplicate, `tools/runner-keepalive.ps1` (hyphen), was deleted
# on 2026-09-15. It argued the opposite - that an in-distro unit cannot
# work - but nothing invoked it, and its holder probe matched only
# `sleep infinity`, so it could not see the live `sleep 2147483647` holder
# and would have spawned a second one on every run.
#
# Runner background: docs/10-operations/README.md, section `Runner`.
#
# Idempotent - safe to run on a schedule.
#
# Usage (PowerShell):
#   powershell -File tools\runner_keepalive.ps1

$ErrorActionPreference = 'Continue'

$distro  = 'Ubuntu-24.04'
$runner  = 'actions.runner.menarzullayev-rankwant.nsn-pc-rankwant.service'
$holder  = 'rankwant-holder.service'

# Log name matches this script. It used to be `runner-keepalive.log`, the
# name of the deleted hyphen script, so the two wrote to one file and the
# log could not say which had run.
$logFile = Join-Path (Split-Path -Parent $PSScriptRoot) '.tmp\runner_keepalive.log'
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
