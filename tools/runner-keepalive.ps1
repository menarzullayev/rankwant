<#
Keeps the WSL2 distro (and therefore the GitHub Actions runner) alive.

Why this exists
---------------
The runner runs as a systemd service inside WSL2. WSL2 tears the whole
distro down once the last session exits, and systemd -- with the runner
in it -- dies with it. GitHub then reports the runner as `offline` and
every queued job sits there until someone happens to open a WSL shell.
GitHub surfaces this as `Runner will be shutdown for UserCancelled` and
`completed with result: Canceled`, which points at the runner and hides
the real cause.

Measured 2026-09-14: the distro went `Stopped` within 30 s of the last
`wsl.exe` call returning. `vmIdleTimeout=-1` in .wslconfig did NOT help
(WSL 2.6.3), and neither did a systemd keepalive unit inside the distro
-- when the distro shuts down, the unit goes down with it. The only
thing that holds a distro open is a process on the Windows side.

What this does
--------------
Starts `wsl.exe ... exec sleep infinity` and keeps it running. WSL sees
a live session, so the distro stays up and the systemd runner along with
it. If the holder dies (WSL restart, Windows reboot), the loop respawns
it after $RetrySeconds.

Usage
-----
  powershell -ExecutionPolicy Bypass -File tools\runner-keepalive.ps1
  powershell -ExecutionPolicy Bypass -File tools\runner-keepalive.ps1 -Status

Run it detached so it survives the terminal:

  Start-Process powershell -ArgumentList '-NoProfile','-WindowStyle','Hidden',
    '-ExecutionPolicy','Bypass','-File','tools\runner-keepalive.ps1' -WindowStyle Hidden

To make that automatic at logon, register a Scheduled Task -- see
docs/10-operations/ci-runner.md.

ASCII only: Windows PowerShell 5.1 reads BOM-less UTF-8 as ANSI.
#>
param(
  [string]$Distro = 'Ubuntu-24.04',
  [int]$RetrySeconds = 15,
  [switch]$Status,
  [switch]$Stop
)

$ErrorActionPreference = 'Continue'

function Get-Holder {
  # The holder is the wsl.exe process running `exec sleep infinity` for
  # our distro. Matching on the command line is the only reliable way:
  # several wsl.exe processes can be alive at once (one per shell), and
  # only ours keeps the distro open deliberately.
  Get-CimInstance Win32_Process -Filter "Name = 'wsl.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like "*$Distro*" -and $_.CommandLine -like '*sleep infinity*' }
}

function Get-DistroState {
  # `wsl --list --verbose` writes UTF-16, which reads as spaced-out text
  # in some consoles. Strip NULs and parse the row for our distro.
  $raw = (& wsl.exe --list --verbose) -join "`n"
  $clean = $raw -replace "`0", ''
  foreach ($line in ($clean -split "`r?`n")) {
    if ($line -match [regex]::Escape($Distro)) {
      if ($line -match 'Running')  { return 'Running' }
      if ($line -match 'Stopped')  { return 'Stopped' }
      return 'Unknown'
    }
  }
  return 'Missing'
}

if ($Status) {
  $holders = @(Get-Holder)
  Write-Output "distro   : $Distro"
  Write-Output "state    : $(Get-DistroState)"
  Write-Output "holders  : $($holders.Count)"
  foreach ($h in $holders) { Write-Output "           pid=$($h.ProcessId)" }
  if ($holders.Count -eq 0) { Write-Output "verdict  : NOT HELD - the distro will shut down when idle" }
  exit 0
}

if ($Stop) {
  # Only stop our own holder. Killing every wsl.exe would take down the
  # user's interactive shells and Docker Desktop's distro as well.
  $holders = @(Get-Holder)
  if ($holders.Count -eq 0) { Write-Output 'No keepalive holder was running.'; exit 0 }
  foreach ($h in $holders) {
    Write-Output "stopping pid=$($h.ProcessId)"
    Stop-Process -Id $h.ProcessId -Force -ErrorAction SilentlyContinue
  }
  exit 0
}

# Single-instance guard. Two holders would be harmless but would make
# `-Status` misleading and leak a process per invocation.
$existing = @(Get-Holder)
if ($existing.Count -gt 0) {
  Write-Output "Keepalive already running (pid=$($existing[0].ProcessId)). Nothing to do."
  exit 0
}

Write-Output "Holding $Distro open. Ctrl+C (or -Stop) to release."
while ($true) {
  if (@(Get-Holder).Count -eq 0) {
    Write-Output "$(Get-Date -Format 'HH:mm:ss') starting holder"
    # `exec` so the bash wrapper is replaced and `sleep infinity` is the
    # process WSL tracks -- one process, and its command line is stable
    # enough for Get-Holder to find it again.
    & wsl.exe -d $Distro -u root -- bash -lc 'exec sleep infinity'
  }
  Start-Sleep -Seconds $RetrySeconds
}
