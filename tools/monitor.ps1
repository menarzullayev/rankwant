<#
RankWant - tunnel va origin monitori (Windows).

Sayt tashqaridan yiqilsa monitor sababni QATLAMLARGA ajratadi va faqat
o'sha qatlamni tiklaydi.

MUHIM: monitor handoff oqimini HURMAT QILADI. Hech narsa tiklanmaydi,
agar R2 dagi state.json owner='windows' bo'lmasa. Aks holda tizim live
emas (Linux live yoki topshirilgan) va tiklash ikki tomonni bir vaqtda
live qilib qo'yardi.

NEGA IKKITA MANZIL TEKSHIRILADI (2026-09-15 da o'lchangan avariya):

    https://rankwant.uz/                -> 200
    https://rankwant.uz/api/v1/health/  -> 503 (maintenance Worker)

Sahifalar normal ochilardi, lekin brauzerdagi HAR BIR API chaqiruvi
yiqilardi: kirish, yuborish, jadval. Eski monitor faqat saytning
ILDIZINI tekshirardi, shuning uchun u YASHIL qoldi va avariya
o'z-o'zidan tuzalmadi.

O'sha avariyaning ildizi ham alohida qatlam edi: `rankwant-api-1`
konteyneri Docker uchun `healthy`, ichkarida `/api/v1/health/` 200,
lekin host porti (127.0.0.1:8301) TCP ulanishni QABUL QILARDI va HTTP
000 qaytarardi. Ya'ni konteyner darajasidagi HAMMA signal yashil edi.
Yagona ishonchli farq: ichkarida 200, tashqarida 000.

QATLAMLAR (jurnalda shu nom bilan yoziladi):

    OK                  ikkala ommaviy manzil ham 200
    NOT LIVE            R2 owner boshqa tizimda - yiqilish KUTILGAN
    UNMEASURED          qatlamni o'qib bo'lmadi. "Sog'lom" DEGANI EMAS
    CONTAINER DOWN      konteyner ishlamayapti yoki yo'q
    DEAD BRIDGE         ichkarida 200, host portida 000 - port ko'prigi
                        o'lgan. Davo: FAQAT o'sha konteynerni restart
    CONTAINER UNHEALTHY docker healthcheck `unhealthy` deydi
    APP DOWN            konteyner ichida ham javob yo'q - ilova xatosi
    TUNNEL DOWN         origin 200, tunnel jarayoni yo'q
    EDGE                origin 200 va tunnel bor, lekin ommaviy URL yiqiq
                        (Cloudflare / Worker / DNS qatlami)

CHIQISH KODI (check_workers.sh va check_ci.sh bilan bir xil shartnoma):

    0 - hammasi sog'lom, yoki bu tizim live emas
    1 - muammo topildi
    2 - qatlamni o'lchab bo'lmadi, sayt holati haqida xulosa YO'Q

    powershell -ExecutionPolicy Bypass -File tools\monitor.ps1          # bir marta
    powershell -ExecutionPolicy Bypass -File tools\monitor.ps1 -Loop    # doimiy

SINOV ILMOQLARI (tools/check_negative.py ishlatadi, oddiy yurishda YO'Q):

    MONITOR_HTTP_STUB     qatorlar: <label>TAB<kod>TAB<open|closed>
                          Label: public-web, public-api, origin-web, origin-api
                          Uchinchi ustun - TCP ulanishi (host port ko'prigi).
    MONITOR_DOCKER_STUB   qatorlar: <nom>TAB<running|exited>TAB<health>TAB<ichki kod>
    MONITOR_OWNER_STUB    windows | linux | unknown
    MONITOR_TUNNEL_STUB   up | down
    MONITOR_FORCE_UNREADABLE  vergul bilan: docker, owner
    MONITOR_WORK_DIR      .handoff o'rniga (test haqiqiy jurnalni ifloslantirmasin)
    MONITOR_DRY_RUN       1 - hech narsa qayta ishga tushirilmaydi

    XAVFSIZLIK: har qanday STUB berilsa dry-run MAJBURIY yoqiladi (pastda
    $dryRun). Ya'ni salbiy test HECH QACHON haqiqiy konteynerni yoki
    tunnelni qayta ishga tushira olmaydi - bu taqiq kodda, testning
    ehtiyotkorligiga tashlab qo'yilmagan.

Fayl ataylab faqat ASCII: Windows PowerShell 5.1 BOM'siz UTF-8 ni ANSI
deb o'qiydi (handoff.ps1 bilan bir xil sabab).
#>
param(
  [switch]$Loop,
  [int]$IntervalSeconds = 60
)

$ErrorActionPreference = 'Continue'

$PSScriptRootValue = $PSScriptRoot
$root = Split-Path -Parent $PSScriptRootValue

# Ish katalogi. Test uni vaqtinchalik joyga buradi, aks holda salbiy
# testlar HAQIQIY .handoff/monitor.log va ogohlantirish faylini
# ifloslantirardi.
if ($env:MONITOR_WORK_DIR) { $work = $env:MONITOR_WORK_DIR }
else { $work = Join-Path $root '.handoff' }
New-Item -ItemType Directory -Force -Path $work | Out-Null

$cfConfig = Join-Path $env:USERPROFILE '.cloudflared\config.yml'
$cfPid = Join-Path $work 'cloudflared.pid'
$cfLog = Join-Path $work 'cloudflared.log'
$monitorLog = Join-Path $work 'monitor.log'
$alertFile = Join-Path $work 'monitor-alert.txt'

# R2 sozlamasi handoff.ps1 bilan bir xil manbadan o'qiladi.
$envFile = Join-Path $root '.env.handoff'

# ---------------------------------------------------------------------
# Tekshiriladigan servislar.
#
# Ikkalasi ham ALOHIDA tekshiriladi. Ilgari faqat birinchisi
# tekshirilardi va API-ning yolg'iz yiqilishi ko'rinmasdi.
#
# `Origin` manzillariga `Host: rankwant.uz` sarlavhasi YUBORILADI.
# Usiz Django ALLOWED_HOSTS bo'sh 400 qaytaradi va monitor buni
# "origin yiqilgan" deb o'qirdi (o'lchandi: 8301 ga sarlavhasiz so'rov
# 400, sarlavha bilan 200).
#
# `Inner` - konteyner ICHIDAGI probe. Obrazlarda nima borligi
# o'lchangan: api obrazida faqat `python`, web obrazida faqat `node`
# (na `curl`, na `wget`). Probe faqat bitta savolga javob beradi -
# "ichkarida 200 qaytyaptimi?". Har qanday boshqa natija (500, ulanish
# xatosi) `000` bo'lib ko'rinadi, chunki qatlam mantig'i uchun farqi
# yo'q: ichkarida ham sog'lom emas.
# ---------------------------------------------------------------------
$services = @(
  @{
    Name      = 'web'
    Container = 'rankwant-web-1'
    Public    = 'https://rankwant.uz/'
    Origin    = 'http://127.0.0.1:8300/'
    Port      = 8300
    Inner     = @('node', '-e',
      'require("http").get({host:"127.0.0.1",port:3000,path:"/",timeout:5000},function(r){process.stdout.write(String(r.statusCode));process.exit(0)}).on("error",function(){process.stdout.write("000");process.exit(0)})')
  },
  @{
    Name      = 'api'
    Container = 'rankwant-api-1'
    Public    = 'https://rankwant.uz/api/v1/health/'
    Origin    = 'http://127.0.0.1:8301/api/v1/health/'
    Port      = 8301
    Inner     = @('python', '-c',
      'import urllib.request,sys; sys.stdout.write(str(urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health/", timeout=5).status))')
  }
)

# ---------------------------------------------------------------------
# Sinov ilmoqlari
# ---------------------------------------------------------------------

function Read-StubTable([string]$raw) {
  # `$null` - stub berilmagan (haqiqiy o'lchov). Bo'sh jadval EMAS:
  # bo'sh jadval "hech narsa topilmadi" degani bo'lardi.
  if ([string]::IsNullOrEmpty($raw)) { return $null }
  $map = @{}
  foreach ($line in ($raw -split "`n")) {
    # `\r` OLIB TASHLANADI. Windows'da stub CRLF bilan kelishi mumkin va
    # `True\r` hech qachon `True` ga teng bo'lmaydi - check_workers.sh da
    # aynan shu xato o'lchangan edi (2026-09-14).
    $row = $line.TrimEnd("`r").Trim()
    if (-not $row) { continue }
    $cols = $row -split "`t"
    $vals = @()
    if ($cols.Length -gt 1) {
      for ($i = 1; $i -lt $cols.Length; $i++) { $vals += $cols[$i].Trim() }
    }
    $map[$cols[0].Trim()] = $vals
  }
  return $map
}

$httpStub = Read-StubTable $env:MONITOR_HTTP_STUB
$dockerStub = Read-StubTable $env:MONITOR_DOCKER_STUB
$ownerStub = $env:MONITOR_OWNER_STUB
$tunnelStub = $env:MONITOR_TUNNEL_STUB

$unreadable = @()
if ($env:MONITOR_FORCE_UNREADABLE) {
  $unreadable = @(($env:MONITOR_FORCE_UNREADABLE -split ',') |
    ForEach-Object { $_.Trim().ToLower() } | Where-Object { $_ })
}

$stubMode = ($null -ne $httpStub) -or ($null -ne $dockerStub) -or
            (-not [string]::IsNullOrEmpty($ownerStub)) -or
            (-not [string]::IsNullOrEmpty($tunnelStub)) -or
            ($unreadable.Count -gt 0)

# XAVFSIZLIK DARVOZASI. Stub rejimida hech qachon haqiqiy konteyner yoki
# tunnel qayta ishga tushirilmaydi - test buni o'zi eslab qolishi shart
# emas.
$dryRun = $stubMode -or (-not [string]::IsNullOrEmpty($env:MONITOR_DRY_RUN))

# ---------------------------------------------------------------------
# Jurnal
# ---------------------------------------------------------------------

function Now { (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') }

function Write-Log([string]$message) {
  # `Write-Output` ISHLATILMAYDI: u qiymatni funksiyaning chiqish
  # oqimiga qo'shadi va `$code = Test-Once` chiqish kodi o'rniga
  # jurnal qatorlari massivini olardi. `Write-Host` faqat konsolga
  # yozadi, ya'ni qaytarilgan qiymat toza qoladi.
  $line = "$(Now) $message"
  Add-Content -Path $monitorLog -Value $line
  Write-Host $line
}

function Write-Alert([string]$message) {
  Add-Content -Path $alertFile -Value "$(Now) $message"
  Write-Log $message
}

# ---------------------------------------------------------------------
# O'lchov qatlamlari
# ---------------------------------------------------------------------

function Get-Status([string]$label, [string]$url, [string]$hostHeader) {
  if ($null -ne $script:httpStub) {
    if ($script:httpStub.ContainsKey($label)) { return $script:httpStub[$label][0] }
    return '000'
  }
  # curl.exe ishlatiladi: PowerShell 5.1 da Invoke-WebRequest ba'zi TLS
  # sozlamalarida yiqiladi va xato matni status kodni ko'rsatmaydi.
  $curlArgs = @('--silent', '--output', 'NUL', '--write-out', '%{http_code}',
                '--max-time', '20', $url)
  if ($hostHeader) { $curlArgs = @('-H', "Host: $hostHeader") + $curlArgs }
  $code = & curl.exe @curlArgs 2>$null
  return "$code".Trim()
}

function Test-HostPort([string]$label, [int]$port) {
  # "TCP ochiq, lekin HTTP 000" - aynan shu juftlik o'lgan port
  # ko'prigini boshqa hamma narsadan ajratadi. Shuning uchun TCP
  # alohida o'lchanadi.
  if ($null -ne $script:httpStub) {
    if ($script:httpStub.ContainsKey($label) -and $script:httpStub[$label].Count -ge 2) {
      return ($script:httpStub[$label][1] -eq 'open')
    }
    return $false
  }
  $client = New-Object System.Net.Sockets.TcpClient
  try {
    $async = $client.BeginConnect('127.0.0.1', $port, $null, $null)
    if (-not $async.AsyncWaitHandle.WaitOne(3000, $false)) { return $false }
    $client.EndConnect($async)
    return $true
  } catch {
    return $false
  } finally {
    $client.Close()
  }
}

function Get-ContainerState([string]$name, [string[]]$innerCmd) {
  # `$null` - QATLAMNI O'QIB BO'LMADI (docker yo'q yoki javob bermayapti).
  # Bu "konteyner yiqilgan" DEGANI EMAS va "sog'lom" ham DEGANI EMAS.
  if ($script:unreadable -contains 'docker') { return $null }

  if ($script:stubMode) {
    if ($null -eq $script:dockerStub) { return $null }
    if (-not $script:dockerStub.ContainsKey($name)) { return $null }
    $row = $script:dockerStub[$name]
    if ($row.Count -lt 3) { return $null }
    return @{ Running = ($row[0] -eq 'running'); Health = $row[1]; Inner = $row[2] }
  }

  # docker'ning O'ZI javob beryaptimi? Bu tekshiruvsiz yo'q konteyner
  # ham, o'lik docker ham bir xil ko'rinadi - va ular butunlay boshqa
  # xulosaga olib keladi.
  & docker version --format '{{.Server.Version}}' 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { return $null }

  $fmt = '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}'
  $raw = & docker inspect -f $fmt $name 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $raw) {
    # docker tirik, lekin konteyner yo'q - bu O'LCHANGAN holat.
    return @{ Running = $false; Health = 'absent'; Inner = '000' }
  }
  $parts = ("$raw".Trim()) -split '\|'
  if ($parts.Count -lt 2) { return $null }
  $running = ($parts[0].Trim() -eq 'running')

  $inner = '000'
  if ($running) {
    $execArgs = @('exec', $name) + $innerCmd
    $out = & docker @execArgs 2>$null
    if ($LASTEXITCODE -eq 0 -and $out) { $inner = "$out".Trim() }
  }
  return @{ Running = $running; Health = $parts[1].Trim(); Inner = $inner }
}

function Get-TunnelProcess {
  if (-not [string]::IsNullOrEmpty($script:tunnelStub)) {
    if ($script:tunnelStub.Trim() -eq 'up') { return 'stub-tunnel' }
    return $null
  }
  # Stub rejimida tunnel haqida hech narsa aytilmasa, u TIRIK deb
  # hisoblanadi: test haqiqiy PID faylini o'qimasin.
  if ($script:stubMode) { return 'stub-tunnel' }
  if (-not (Test-Path $script:cfPid)) { return $null }
  $pidValue = 0
  if (-not [int]::TryParse((Get-Content $script:cfPid -Raw).Trim(), [ref]$pidValue)) { return $null }
  $p = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
  if ($p -and $p.ProcessName -eq 'cloudflared') { return $p }
  return $null
}

# Tizim live emasmi? R2 ga ulanib bo'lmasa XAVFSIZ javob: 'unknown'.
# 'yo''q' deb qabul qilinsa, Linux live paytida monitor tunnelni ko'tarib
# qo'yardi - bu handoff qoidasini buzadi.
function Get-RemoteOwner {
  if ($script:unreadable -contains 'owner') { return 'unknown' }
  if (-not [string]::IsNullOrEmpty($script:ownerStub)) { return $script:ownerStub.Trim() }
  # Stub rejimida egalik aytilmasa 'windows' deb hisoblanadi: test R2 ga
  # ham, docker'ga ham chiqmasin.
  if ($script:stubMode) { return 'windows' }

  if (-not (Test-Path $script:envFile)) { return 'unknown' }
  $cfg = @{}
  foreach ($line in Get-Content $script:envFile) {
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

# ---------------------------------------------------------------------
# Davolar
# ---------------------------------------------------------------------

function Restart-Container([string]$name) {
  # FAQAT bitta konteyner qayta ishga tushiriladi.
  #
  # KEYINGI ODAM UCHUN: repo qoidasi "api, worker va beat ni BIRGA qayta
  # quring" SHU YERGA TEGISHLI EMAS. O'sha qoida `--build` haqida -
  # faqat `api` qayta QURILSA, worker eski OBRAZDA qolib ketadi.
  # `docker restart` esa obrazni qayta qurmaydi va kodni umuman
  # o'zgartirmaydi: u mavjud konteynerni to'xtatib, o'sha obraz bilan
  # yana ishga tushiradi. Ya'ni worker bilan api bu yerda hech qachon
  # ajralib qolmaydi.
  #
  # Bu joyni "docker compose up --build" ga AYLANTIRMANG: u butun
  # stekni to'xtatadi, migratsiyani qayta yugurtiradi va bir necha
  # daqiqalik avariyani o'n daqiqalikka aylantiradi.
  if ($script:dryRun) { return "DRY RUN (hech narsa qilinmadi): docker restart $name" }
  & docker restart $name 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { return "docker restart $name YIQILDI" }
  return "docker restart $name bajarildi"
}

function Start-Tunnel {
  if ($script:dryRun) { return 'DRY RUN (hech narsa qilinmadi): tunnel' }
  if (-not (Test-Path $script:cfConfig)) { throw "cloudflared sozlamasi yo'q: $($script:cfConfig)" }
  $exe = (Get-Command cloudflared -ErrorAction SilentlyContinue).Source
  if (-not $exe) { $exe = 'C:\Program Files (x86)\cloudflared\cloudflared.exe' }
  if (-not (Test-Path $exe)) { throw 'cloudflared topilmadi' }
  $p = Start-Process -FilePath $exe `
    -ArgumentList @('tunnel', '--config', $script:cfConfig, '--logfile', $script:cfLog, 'run') `
    -WindowStyle Hidden -PassThru
  Set-Content -Path $script:cfPid -Value $p.Id
  return "newpid=$($p.Id)"
}

# ---------------------------------------------------------------------
# Qaror
# ---------------------------------------------------------------------

function Test-Once {
  # 1-qadam: IKKALA ommaviy manzil. Arzon yo'l - hech qanday docker,
  # hech qanday R2. Ilgari bu yerda faqat sayt ildizi turardi.
  $probe = @()
  foreach ($svc in $script:services) {
    $probe += @{
      Svc    = $svc
      Public = (Get-Status "public-$($svc.Name)" $svc.Public $null)
      Origin = '-'
    }
  }
  $detail = (($probe | ForEach-Object { "$($_.Svc.Name)=$($_.Public)" }) -join ' ')
  $bad = @($probe | Where-Object { $_.Public -ne '200' })

  if ($bad.Count -eq 0) {
    if (Test-Path $script:alertFile) { Remove-Item $script:alertFile -Force }
    # OK ham jurnalga yoziladi. Ilgari yozilmasdi va shu sabab avariya
    # QANCHA davom etganini jurnaldan aniqlab bo'lmasdi: api konteyneri
    # HTTP so'rovlarni umuman jurnalga yozmaydi (o'lchandi - har qanday
    # oynada 0 qator). Endi har 5 daqiqada bitta qator qoladi va bu
    # uzilish oralig'ining yagona haqiqiy manbai.
    Write-Log "OK ($detail)"
    return 0
  }

  # 2-qadam: egalik. Bu tizim umuman live bo'lishi kerakmi?
  $owner = Get-RemoteOwner

  if ($owner -eq 'unknown') {
    Write-Alert ("UNMEASURED ($detail) - R2 state.json o'qilmadi, egalik noma'lum. " +
      "Hech narsa tiklanmadi (handoff qoidasi). Sayt holati haqida xulosa YO'Q.")
    return 2
  }

  if ($owner -ne 'windows') {
    # Ogohlantirish fayli YOZILMAYDI: bu kutilgan holat, avariya emas.
    # Handoff `out` konteynerlarni to'xtatadi, ya'ni yiqilish TO'G'RI.
    Write-Log ("NOT LIVE ($detail) - R2 owner='$owner'. Bu tizim live emas, " +
      "ommaviy URL yiqiq bo'lishi KUTILGAN. Hech narsa qilinmadi.")
    return 0
  }

  # 3-qadam: har bir yiqilgan servis uchun qatlamni ajratamiz.
  $problems = 0
  $unmeasuredCount = 0
  $aboveOrigin = @()

  foreach ($p in $bad) {
    $svc = $p.Svc
    $originLabel = "origin-$($svc.Name)"
    $origin = Get-Status $originLabel $svc.Origin 'rankwant.uz'
    $p.Origin = $origin

    if ($origin -eq '200') {
      # Origin sog'lom - ayb undan YUQORIDA (tunnel yoki edge).
      $aboveOrigin += $svc.Name
      continue
    }

    $tcpOpen = Test-HostPort $originLabel $svc.Port
    if ($tcpOpen) { $tcpText = 'open' } else { $tcpText = 'closed' }
    $base = "$($svc.Name) public=$($p.Public) origin=$origin tcp=$tcpText"

    $state = Get-ContainerState $svc.Container $svc.Inner
    if ($null -eq $state) {
      Write-Alert ("UNMEASURED ($base) - docker holatini o'qib bo'lmadi. " +
        "Qatlamni ajratib bo'lmaydi, shuning uchun HECH NARSA qilinmadi.")
      $unmeasuredCount++
      continue
    }

    if ($state.Running) { $runText = 'running' } else { $runText = 'stopped' }
    $base = "$base container=$runText health=$($state.Health) inner=$($state.Inner)"

    if (-not $state.Running) {
      Write-Alert ("CONTAINER DOWN ($base) - konteyner ishlamayapti. " +
        "Tunnelni ko'tarish yordam bermaydi, konteyner aybdor.")
      $problems++
      continue
    }

    if ($state.Inner -eq '200') {
      # O'LCHANGAN AVARIYA (2026-09-15). Konteyner ichida /health 200,
      # Docker `healthy` deydi, host porti esa HTTP 000 qaytaradi.
      # TCP ulanish OCHILADI (com.docker.backend tinglaydi), ya'ni
      # "port band emas" degan tekshiruv ham yashil bo'lardi.
      # Shuning uchun qaror ichki 200 ga tayanadi, TCP ga emas.
      $act = Restart-Container $svc.Container
      Write-Alert ("DEAD BRIDGE ($base) - konteyner ICHIDA sog'lom, host port " +
        "ko'prigi o'lgan. Faqat shu konteyner qayta ishga tushiriladi: $act")
      $problems++
      continue
    }

    if ($state.Health -eq 'unhealthy') {
      Write-Alert ("CONTAINER UNHEALTHY ($base) - docker healthcheck yiqilgan va " +
        "ichkarida ham 200 yo'q. Qayta ishga tushirish DAVO EMAS, jurnalga qarang.")
    } else {
      Write-Alert ("APP DOWN ($base) - konteyner ishlayapti, lekin ichkarida ham " +
        "javob yo'q. Bu ilova xatosi, port ko'prigi emas.")
    }
    $problems++
  }

  # 4-qadam: origin sog'lom bo'lgan servislar - ayb tunnel yoki edge da.
  if ($aboveOrigin.Count -gt 0) {
    $who = ($aboveOrigin -join ',')
    $tunnel = Get-TunnelProcess
    if ($null -eq $tunnel) {
      $act = Start-Tunnel
      Start-Sleep -Seconds 10
      # Tiklanganini ANIQ taqqoslash bilan o'lchaymiz: har bir servis
      # 200 bo'lishi shart. Ilgari bu yerda matn ustidan regex turardi
      # va "web=200 api=503" ni ham "tiklandi" deb o'qishi mumkin edi.
      $afterCodes = @()
      $afterOk = $true
      foreach ($s in $script:services) {
        $c = Get-Status "public-$($s.Name)" $s.Public $null
        $afterCodes += "$($s.Name)=$c"
        if ($c -ne '200') { $afterOk = $false }
      }
      $after = ($afterCodes -join ' ')
      Write-Alert ("TUNNEL DOWN ($detail origin_ok=$who) - origin sog'lom, tunnel " +
        "jarayoni yo'q. Tunnel qayta ko'tarildi: $act after=($after)")
      if ($afterOk -and (Test-Path $script:alertFile)) { Remove-Item $script:alertFile -Force }
      $problems++
    } else {
      Write-Alert ("EDGE ($detail origin_ok=$who) - origin sog'lom va tunnel " +
        "ishlayapti, lekin ommaviy URL yiqiq. Ayb Cloudflare / Worker / DNS " +
        "qatlamida; bu yerdan tiklab bo'lmaydi.")
      $problems++
    }
  }

  if ($problems -gt 0) { return 1 }
  if ($unmeasuredCount -gt 0) { return 2 }
  return 0
}

if ($Loop) {
  Write-Log "Monitor boshlandi (har ${IntervalSeconds}s)."
  while ($true) {
    try { Test-Once | Out-Null } catch { Write-Log "XATO: $_" }
    Start-Sleep -Seconds $IntervalSeconds
  }
} else {
  $code = Test-Once
  exit $code
}
