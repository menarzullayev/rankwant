<#
Ikki tizimli preview - Windows tomoni (Linux va Windows bitta mashinada, dual-boot).

Har tizimda preview'ning o'z bazasi va MinIO'si bor. Ma'lumot Cloudflare R2
dagi eksport orqali ko'chadi, R2 dagi state.json esa qaysi tizim live ekanini
saqlaydi. To'liq protokol: docs/10-operations/README.md, "Ikki tizimli preview".

  powershell -ExecutionPolicy Bypass -File tools\handoff.ps1 status
  powershell -ExecutionPolicy Bypass -File tools\handoff.ps1 init
  powershell -ExecutionPolicy Bypass -File tools\handoff.ps1 out
  powershell -ExecutionPolicy Bypass -File tools\handoff.ps1 in [-Force]

Asosiy qoida: toza topshirilmagan tizim live bo'lmaydi.

Windows'da tunnel xizmat emas, oddiy jarayon: Docker Desktop baribir
foydalanuvchi tizimga kirgandagina ishlaydi, jarayonni esa admin huquqisiz
boshqarsa bo'ladi.

Fayl ataylab faqat ASCII: Windows PowerShell 5.1 BOM'siz UTF-8 ni ANSI deb o'qiydi.
#>
param(
  [Parameter(Mandatory = $true, Position = 0)]
  [ValidateSet('status', 'init', 'out', 'in')]
  [string]$Command,
  [switch]$Force
)
# 'Stop' emas: PS 5.1 da native buyruq stderr'ga yozsa, u xato deb otiladi.
# Chiqish kodi har chaqiruvdan keyin Assert-Exit bilan tekshiriladi.
$ErrorActionPreference = 'Continue'
$me = 'windows'
$other = 'linux'
$root = Split-Path -Parent $PSScriptRoot
$work = Join-Path $root '.handoff'
$localIdFile = Join-Path $work 'local-export-id'
New-Item -ItemType Directory -Force -Path $work | Out-Null

$envFile = Join-Path $root '.env.handoff'
if (-not (Test-Path $envFile)) { throw ".env.handoff yo'q - .env.handoff.example dan nusxa olib to'ldiring" }
$cfg = @{}
foreach ($line in Get-Content $envFile) {
  if ($line -match '^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$') { $cfg[$Matches[1]] = $Matches[2].Trim('"') }
}
foreach ($k in 'R2_ACCOUNT_ID', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_BUCKET') {
  if (-not $cfg[$k]) { throw "$k .env.handoff da yo'q" }
}
$bucket = $cfg['R2_BUCKET']
# Kalit buyruq qatoriga chiqmasin: 'docker run -e MC_HOST_r2' qiymatni muhitdan oladi.
$env:MC_HOST_r2 = 'https://{0}:{1}@{2}.r2.cloudflarestorage.com' -f $cfg['R2_ACCESS_KEY_ID'], $cfg['R2_SECRET_ACCESS_KEY'], $cfg['R2_ACCOUNT_ID']

# Loyiha nomi qat'iy: katalogdan olinsa boshqa klon boshqa volume'larga tushardi.
$project = 'rankwant'
$composeBase = @('compose', '-p', $project, '--env-file', (Join-Path $root '.env.public'),
  '-f', (Join-Path $root 'docker-compose.yml'), '-f', (Join-Path $root 'docker-compose.public.yml'))
# Postgres va MinIO'dan boshqa hammasi bazaga yozadi yoki navbatdan oladi.
$writers = @('web', 'api', 'worker', 'beat', 'judge')

$cfConfig = Join-Path $env:USERPROFILE '.cloudflared\config.yml'
$cfPid = Join-Path $work 'cloudflared.pid'
$cfLog = Join-Path $work 'cloudflared.log'

function Assert-Exit([string]$what) { if ($LASTEXITCODE -ne 0) { throw "$what (exit $LASTEXITCODE)" } }
function Compose { & docker @($composeBase + $args); Assert-Exit "docker compose $($args -join ' ')" }
function Mc { & docker @(@('run', '--rm', '-i', '-e', 'MC_HOST_r2', '-v', "${work}:/work", 'minio/mc', '--quiet') + $args); Assert-Exit "mc $($args -join ' ')" }
function Now { (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') }
function Get-LocalExport { if (Test-Path $localIdFile) { (Get-Content $localIdFile -Raw).Trim() } else { '' } }

# state.json yo'q bo'lsa $null.
function Get-State {
  $out = & docker run --rm -e MC_HOST_r2 minio/mc --quiet cat "r2/$bucket/state.json" 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $out) { return $null }
  return (($out -join "`n") | ConvertFrom-Json)
}

function Save-State($owner, $since, $exportId, $exportAt) {
  $json = [ordered]@{ owner = $owner; since = $since; export_id = $exportId; export_at = $exportAt } | ConvertTo-Json -Compress
  $json | & docker run --rm -i -e MC_HOST_r2 minio/mc --quiet pipe "r2/$bucket/state.json" | Out-Null
  Assert-Exit 'state.json yozilmadi'
}

function Get-RemoteSize([string]$key) {
  $j = & docker run --rm -e MC_HOST_r2 minio/mc --quiet stat --json "r2/$bucket/$key"
  Assert-Exit "mc stat $key"
  return [long](($j -join "`n") | ConvertFrom-Json).size
}

# Dump oxirigacha yozilganini va arxiv o'qilishini tekshiradi.
function Test-Archives([string]$dir) {
  & docker run --rm -v "${dir}:/in:ro" alpine sh -ec 'gzip -t /in/pg.sql.gz; tar tzf /in/minio.tar.gz >/dev/null'
  Assert-Exit "arxiv buzilgan: $dir"
}

function Get-Tunnel {
  if (-not (Test-Path $cfPid)) { return $null }
  $p = Get-Process -Id ([int](Get-Content $cfPid)) -ErrorAction SilentlyContinue
  if ($p -and $p.ProcessName -eq 'cloudflared') { return $p }
  return $null
}

function Start-Tunnel {
  if (Get-Tunnel) { return }
  if (-not (Test-Path $cfConfig)) { throw "cloudflared sozlamasi yo'q: $cfConfig" }
  $exe = (Get-Command cloudflared -ErrorAction SilentlyContinue).Source
  if (-not $exe) { throw 'cloudflared topilmadi: winget install --id Cloudflare.cloudflared' }
  $p = Start-Process -FilePath $exe -ArgumentList @('tunnel', '--config', $cfConfig, '--logfile', $cfLog, 'run') -WindowStyle Hidden -PassThru
  Set-Content -Path $cfPid -Value $p.Id
}

function Stop-Tunnel {
  $p = Get-Tunnel
  if ($p) { Stop-Process -Id $p.Id -Force }
  if (Test-Path $cfPid) { Remove-Item $cfPid -Force }
}

function Wait-Healthy {
  for ($i = 0; $i -lt 60; $i++) {
    & curl.exe -fsS -o NUL -H 'Host: rankwant.uz' http://127.0.0.1:8301/api/v1/health/ 2>$null
    if ($LASTEXITCODE -eq 0) { return }
    Start-Sleep -Seconds 2
  }
  throw "API sog'lom emas: http://127.0.0.1:8301/api/v1/health/"
}

# R2 da oxirgi ikkita eksport qoladi (bepul 10 GB), lokal nusxadan faqat joriysi.
function Remove-OldExports([string]$keep) {
  $names = @(& docker run --rm -e MC_HOST_r2 minio/mc --quiet ls "r2/$bucket/exports/" 2>$null |
    ForEach-Object { (($_ -split '\s+')[-1]).TrimEnd('/') } | Where-Object { $_ } | Sort-Object)
  foreach ($n in @($names | Select-Object -SkipLast 2)) { Mc rm --recursive --force "r2/$bucket/exports/$n/" | Out-Null }
  foreach ($sub in 'out', 'in') {
    Get-ChildItem (Join-Path $work $sub) -Directory -ErrorAction SilentlyContinue |
      Where-Object { $_.Name -ne $keep } | Remove-Item -Recurse -Force
  }
}

function Import-Export([string]$id) {
  $dir = Join-Path $work "in\$id"
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  "Eksport yuklab olinmoqda: $id"
  foreach ($f in 'pg.sql.gz', 'minio.tar.gz') { Mc cp "r2/$bucket/exports/$id/$f" "/work/in/$id/$f" | Out-Null }
  Test-Archives $dir

  'Baza tiklanmoqda'
  & docker @($composeBase + @('stop') + $writers) 2>$null | Out-Null
  Compose up -d --wait postgres minio
  # Bo'sh bazaga tiklanadi: --clean faqat dumpdagi obyektlarni tashlaydi,
  # bu tomonda qo'shimcha migratsiya bo'lsa undan qolgan jadvallar turib qolardi.
  Compose exec -T postgres psql -U rankwant -d postgres -q -v ON_ERROR_STOP=1 -c 'DROP DATABASE IF EXISTS rankwant WITH (FORCE);' -c 'CREATE DATABASE rankwant OWNER rankwant;'
  Compose cp (Join-Path $dir 'pg.sql.gz') postgres:/tmp/handoff-pg.sql.gz
  Compose exec -T postgres sh -ec 'gunzip -c /tmp/handoff-pg.sql.gz | psql -U rankwant -d rankwant -q -v ON_ERROR_STOP=1 >/dev/null'

  'MinIO tiklanmoqda'
  Compose stop minio
  & docker run --rm -v "${project}_miniodata:/data" -v "${dir}:/in:ro" alpine sh -ec 'find /data -mindepth 1 -delete; tar xzf /in/minio.tar.gz -C /data'
  Assert-Exit 'MinIO tiklanmadi'
  Set-Content -Path $localIdFile -Value $id
}

function Show-Status {
  $s = Get-State
  if (-not $s) { "R2 da state.json yo'q - birinchi marta: tools\handoff.ps1 init"; return }
  $tunnel = if (Get-Tunnel) { 'ishlayapti' } else { "to'xtagan" }
  "R2 holati:      owner=$($s.owner) since=$($s.since)"
  "Oxirgi eksport: $($s.export_id) ($($s.export_at))"
  "Bu tizim ($me): lokal eksport=$(Get-LocalExport) tunnel=$tunnel"
}

function Invoke-Init {
  if (Get-State) { throw "state.json allaqachon bor - init kerak emas (status ga qarang)" }
  Save-State $me (Now) $null $null
  "Boshlandi: $me live."
}

function Invoke-Out {
  $s = Get-State
  $owner = if ($s) { $s.owner } else { $null }
  if ($owner -ne $me) { throw "Live tizim: '$owner'. 'out' faqat live tizimda ishlaydi." }
  $id = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss') + "-$me"
  $dir = Join-Path $work "out\$id"
  New-Item -ItemType Directory -Force -Path $dir | Out-Null

  "1/6 Tunnel to'xtatilmoqda - sayt texnik ishlar sahifasiga o'tadi"
  Stop-Tunnel
  "2/6 Yozuvchi servislar to'xtatilmoqda"
  Compose stop @writers
  '3/6 Postgres dump'
  Compose exec -T postgres sh -ec "pg_dump -U rankwant --clean --if-exists rankwant | gzip -9 > /tmp/handoff-pg.sql.gz && gunzip -c /tmp/handoff-pg.sql.gz | tail -c 4096 | grep -q 'PostgreSQL database dump complete'"
  Compose cp postgres:/tmp/handoff-pg.sql.gz (Join-Path $dir 'pg.sql.gz')
  '4/6 MinIO arxivi'
  & docker run --rm -v "${project}_miniodata:/data:ro" -v "${dir}:/out" alpine tar czf /out/minio.tar.gz -C /data .
  Assert-Exit 'MinIO arxivi'
  Test-Archives $dir
  '5/6 R2 ga yuklanmoqda'
  foreach ($f in 'pg.sql.gz', 'minio.tar.gz') {
    Mc cp "/work/out/$id/$f" "r2/$bucket/exports/$id/$f" | Out-Null
    if ((Get-RemoteSize "exports/$id/$f") -ne (Get-Item (Join-Path $dir $f)).Length) {
      throw "R2 dagi $f hajmi mos emas - holat o'zgartirilmadi"
    }
  }
  '6/6 Holat yozilmoqda'
  Save-State $null $null $id (Now)
  Set-Content -Path $localIdFile -Value $id
  Remove-OldExports $id
  Compose stop
  "Topshirildi: $id. Endi Linux'ga o'tib 'tools/handoff.sh in' qiling."
}

function Invoke-In {
  $s = Get-State
  $owner = if ($s) { $s.owner } else { $null }
  $exportId = if ($s) { $s.export_id } else { $null }
  $exportAt = if ($s) { $s.export_at } else { $null }
  if ($owner -eq $other -and -not $Force) {
    "Linux hali live ($($s.since) dan beri) va topshirmagan."
    "Linux'ga kirib 'tools/handoff.sh out' qiling, keyin qaytib keling."
    "Linux'ga kira olmasangiz: tools\handoff.ps1 in -Force"
    "  (Linux'da oxirgi eksportdan keyin yozilgan ma'lumot yo'qoladi)."
    exit 1
  }
  if ($owner -ne $me -and $exportId -and $exportId -ne (Get-LocalExport)) {
    Import-Export $exportId
    Remove-OldExports $exportId
  }
  "Stek ko'tarilmoqda (birinchi marta build uzoq davom etadi)"
  Compose up -d --build --wait
  Wait-Healthy
  Start-Tunnel
  Save-State $me (Now) $exportId $exportAt
  "Live: $me. Sayt tunnel orqali ochiladi."
}

switch ($Command) {
  'status' { Show-Status }
  'init' { Invoke-Init }
  'out' { Invoke-Out }
  'in' { Invoke-In }
}
