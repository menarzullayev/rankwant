# RankWant — daily local dev: Docker backend only + Next.js on the host.
#
# Skips rebuilding the `web` image. UI hot-reloads via Turbopack.
#
#   powershell -File tools/dev-local.ps1          # backend + foreground UI
#   powershell -File tools/dev-local.ps1 -BackendOnly
#   powershell -File tools/dev-local.ps1 -WebOnly # backend already up

param(
    [switch]$BackendOnly,
    [switch]$WebOnly,
    [int]$WebPort = $(if ($env:RANKWANT_DEV_WEB_PORT) { [int]$env:RANKWANT_DEV_WEB_PORT } else { 8310 })
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$EnvFile = if ($env:RANKWANT_ENV_FILE) { $env:RANKWANT_ENV_FILE } else { Join-Path $RepoRoot ".env.public" }
if (-not (Test-Path $EnvFile)) {
    Write-Error "Env file missing: $EnvFile (copy .env.example to .env.public)"
}

$Compose = @(
    "compose", "-p", "rankwant",
    "--env-file", $EnvFile,
    "-f", "docker-compose.yml",
    "-f", "docker-compose.public.yml",
    "-f", "docker-compose.dev-local.yml"
)

$BackendServices = @(
    "postgres", "redis", "minio", "judge-queue",
    "migrate", "api", "worker", "beat", "judge", "realtime"
)

function Ensure-EnvLocal {
    $local = Join-Path $RepoRoot "apps/web/.env.local"
    $sample = Join-Path $RepoRoot "apps/web/env.local.example"
    if (-not (Test-Path $local) -and (Test-Path $sample)) {
        Copy-Item $sample $local
        Write-Host "Created apps/web/.env.local from example"
    }
}

if (-not $WebOnly) {
    $env:RANKWANT_DEV_WEB_PORT = "$WebPort"
    Write-Host "Docker backend (no-build, web container disabled)..."
    $prevEa = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & docker @Compose stop web | Out-Null
    $ErrorActionPreference = $prevEa
    & docker @Compose up -d --no-build --wait @BackendServices
    if ($LASTEXITCODE -ne 0) {
        Write-Host "First run may need images; building backend once..."
        & docker @Compose up -d --build --wait @BackendServices
    }
    Write-Host "API: http://127.0.0.1:8301/api/v1/health/"
}

if ($BackendOnly) { exit 0 }

Ensure-EnvLocal
Write-Host "Next.js dev: http://127.0.0.1:$WebPort/ (Ctrl+C stops UI only)"
Set-Location (Join-Path $RepoRoot "apps/web")
$env:NEXT_PUBLIC_API_BASE = "http://127.0.0.1:8301/api/v1"
$env:API_BASE_INTERNAL = "http://127.0.0.1:8301/api/v1"
& npx next dev -p $WebPort -H 127.0.0.1
