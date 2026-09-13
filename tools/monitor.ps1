<#
RankWant - tunnel monitori (Windows).

Sayt tashqaridan 503 bo'lsa tunnelni qayta ko'taradi va holat faylini yozadi.

MUHIM: monitor handoff oqimini HURMAT QILADI. Tunnel faqat R2 dagi state.json
owner='windows' bo'lganda ko'tariladi. Aks holda tizim live emas (Linux live
yoki topshirilgan) va tunnelni ko'tarish ikki tomonni bir vaqtda live qilib
qo'yardi.

  powershell -ExecutionPolicy Bypass -File tools\monitor.ps1          # bir marta
  powershell -ExecutionPolicy Bypass -File tools\monitor.ps1 -Loop    # doimiy

Fayl ataylab faqat ASCII: Windows PowerShell 5.1 BOM'siz UTF-8 ni ANSI deb
o'qiydi (handoff.ps1 bilan bir xil sabab).
#>
param(
  [switch]$Loop,
  [int]$IntervalSeconds = 60
)

$ErrorActionPreference = 'Continue'

$PSScriptRootValue = $PSScriptRoot
$root = Split-Path -Parent $PSScriptRootValue
$work = Join-Path $root '.handoff'
New-Item -ItemType Directory -Force -Path $work | Out-Null

$cfConfig = Join-Path $env:USERPROFILE '.cloudflared\config.yml'
$cfPid = Join-Path $work 'cloudflared.pid'
$cfLog = Join-Path $work 'cloudflared.log'
$monitorLog = Join-Path $work 'monitor.log'
$alertFile = Join-Path $work 'monitor-alert.txt'

$siteUrl = 'https://rankwant.uz/'
$apiUrl = 'https://rankwant.uz/api/v1/stats/'
$originWeb = 'http://127.0.0.1:8300/'
$originApi = 'http://127.0.0.1:8301/api/v1/stats/'

# R2 sozlamasi handoff.ps1 bilan bir xil manbadan o'qiladi.
$envFile = Join-Path $root '.env.handoff'

function Now { (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') }

function Write-Log([string]$message) {
  $line = "$(Now) $message"
  Add-Content -Path $monitorLog -Value $line
  Write-Output $line
}

function Get-Status([string]$url, [string]$hostHeader) {
  # curl.exe ishlatiladi: PowerShell 5.1 da Invoke-WebRequest ba'zi TLS
  # sozlamalarida yiqiladi va xato matni status kodni ko'rsatmaydi.
  $args = @('--silent', '--output', 'NUL', '--write-out', '%{http_code}',
            '--max-time', '20', $url)
  if ($hostHeader) { $args = @('-H', "Host: $hostHeader") + $args }
  $code = & curl.exe @args 2>$null
  return "$code".Trim()
}

function Get-TunnelProcess {
  if (-not (Test-Path $cfPid)) { return $null }
  $pidValue = 0
  if (-not [int]::TryParse((Get-Content $cfPid -Raw).Trim(), [ref]$pidValue)) { return $null }
  $p = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
  if ($p -and $p.ProcessName -eq 'cloudflared') { return $p }
  return $null
}

# Tizim live emasmi? R2 ga ulanib bo'lmasa XAVFSIZ javob: 'unknown'.
# 'yo''q' deb qabul qilinsa, Linux live paytida monitor tunnelni ko'tarib
# qo'yardi - bu handoff qoidasini buzadi.
function Get-RemoteOwner {
  if (-not (Test-Path $envFile)) { return 'unknown' }
  $cfg = @{}
  foreach ($line in Get-Content $envFile) {
    if ($line -match '^([A-Z0-9_]+)=(.*)$') { $cfg[$Matches[1]] = $Matches[2].Trim().Trim('"') }
  }
  foreach ($k in 'R2_ACCOUNT_ID', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_BUCKET') {
    if (-not $cfg[$k]) { return 'unknown' }
  }
  $env:RCLONE_CONFIG_R2_TYPE = 's3'
  $env:RCLONE_CONFIG_R2_PROVIDER = 'Cloudflare'
  $env:RCLONE_CONFIG_R2_ACCESS_KEY_ID = $cfg['R2_ACCESS_KEY_ID']
  $env:RCLONE_CONFIG_R2_SECRET_ACCESS_KEY = $cfg['R2_SECRET_ACCESS_KEY']
  $env:RCLONE_CONFIG_R2_ENDPOINT = 'https://{0}.r2.cloudflarestorage.com' -f $cfg['R2_ACCOUNT_ID']
  $env:RCLONE_CONFIG_R2_NO_CHECK_BUCKET = 'true'
  $r2 = 'r2:' + $cfg['R2_BUCKET']

  $rcBase = @('run', '--rm', '-i',
    '-e', 'RCLONE_CONFIG_R2_TYPE', '-e', 'RCLONE_CONFIG_R2_PROVIDER',
    '-e', 'RCLONE_CONFIG_R2_ACCESS_KEY_ID', '-e', 'RCLONE_CONFIG_R2_SECRET_ACCESS_KEY',
    '-e', 'RCLONE_CONFIG_R2_ENDPOINT', '-e', 'RCLONE_CONFIG_R2_NO_CHECK_BUCKET',
    'rclone/rclone:1.75', '-q')

  $found = & docker @($rcBase + @('lsf', '--files-only', '--max-depth', '1', '--include', 'state.json', $r2)) 2>$null
  if ($LASTEXITCODE -ne 0) { return 'unknown' }
  if (-not $found) { return 'unknown' }
  $raw = & docker @($rcBase + @('cat', "$r2/state.json")) 2>$null
  if ($LASTEXITCODE -ne 0) { return 'unknown' }
  try {
    $state = (($raw -join "`n") | ConvertFrom-Json)
    if ($state.owner) { return "$($state.owner)" }
    return 'unknown'
  } catch {
    return 'unknown'
  }
}

function Start-Tunnel {
  if (-not (Test-Path $cfConfig)) { throw "cloudflared sozlamasi yo'q: $cfConfig" }
  $exe = (Get-Command cloudflared -ErrorAction SilentlyContinue).Source
  if (-not $exe) { $exe = 'C:\Program Files (x86)\cloudflared\cloudflared.exe' }
  if (-not (Test-Path $exe)) { throw 'cloudflared topilmadi' }
  $p = Start-Process -FilePath $exe `
    -ArgumentList @('tunnel', '--config', $cfConfig, '--logfile', $cfLog, 'run') `
    -WindowStyle Hidden -PassThru
  Set-Content -Path $cfPid -Value $p.Id
  return $p.Id
}

function Test-Once {
  $site = Get-Status $siteUrl $null

  if ($site -eq '200') {
    if (Test-Path $alertFile) { Remove-Item $alertFile -Force }
    return "OK site=200 tunnel=$((Get-TunnelProcess) -ne $null)"
  }

  # Sayt 200 emas. Sabab qaysi qatlamda?
  $origin = Get-Status $originWeb $null
  $owner = Get-RemoteOwner
  $tunnel = Get-TunnelProcess

  $detail = "site=$site origin=$origin owner=$owner tunnel=$($tunnel -ne $null)"

  if ($origin -ne '200') {
    $msg = "ORIGIN DOWN ($detail) - web konteyneri javob bermayapti. Tunnelni ko'tarish saytni tiklamaydi."
    Add-Content -Path $alertFile -Value "$(Now) $msg"
    Write-Log $msg
    return $msg
  }

  if ($owner -ne 'windows') {
    $msg = "TUNNEL DOWN, LEKIN LIVE EMAS ($detail) - R2 owner='$owner'. Tunnel ko'tarilmadi (handoff qoidasi)."
    Add-Content -Path $alertFile -Value "$(Now) $msg"
    Write-Log $msg
    return $msg
  }

  # Origin sog'lom va tizim live - demak tunnel yiqilgan. Tiklaymiz.
  if ($tunnel) {
    # Jarayon bor, lekin sayt 200 emas: eski PID yoki ulanish uzilgan.
    Stop-Process -Id $tunnel.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
  }
  $newPid = Start-Tunnel
  Start-Sleep -Seconds 10
  $after = Get-Status $siteUrl $null
  $msg = "TUNNEL QAYTA KO'TARILDI ($detail) newpid=$newPid after=$after"
  Add-Content -Path $alertFile -Value "$(Now) $msg"
  Write-Log $msg

  if ($after -eq '200') { Remove-Item $alertFile -Force }
  return $msg
}

if ($Loop) {
  Write-Log "Monitor boshlandi (har ${IntervalSeconds}s)."
  while ($true) {
    try { Test-Once | Out-Null } catch { Write-Log "XATO: $_" }
    Start-Sleep -Seconds $IntervalSeconds
  }
} else {
  Test-Once
  if (Test-Path $alertFile) { exit 1 } else { exit 0 }
}
