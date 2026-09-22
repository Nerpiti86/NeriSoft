param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
} catch {
    # PowerShell moderno ya negocia TLS correctamente.
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$assets = @(
    @{
        Name = "Geist Variable v1.7.2"
        Url = "https://raw.githubusercontent.com/vercel/geist-font/v1.7.2/packages/next/dist/fonts/geist-sans/Geist-Variable.woff2"
        Path = "app/static/vendor/geist/Geist-Variable.woff2"
        MinBytes = 60000
    },
    @{
        Name = "Geist OFL"
        Url = "https://raw.githubusercontent.com/vercel/geist-font/v1.7.2/OFL.txt"
        Path = "app/static/vendor/geist/OFL.txt"
        MinBytes = 3000
    },
    @{
        Name = "Tabler Icons CSS 3.35.0"
        Url = "https://cdnjs.cloudflare.com/ajax/libs/tabler-icons/3.35.0/tabler-icons.min.css"
        Path = "app/static/vendor/tabler/tabler-icons.min.css"
        MinBytes = 100000
    },
    @{
        Name = "Tabler Icons WOFF2 3.35.0"
        Url = "https://cdnjs.cloudflare.com/ajax/libs/tabler-icons/3.35.0/fonts/tabler-icons.woff2"
        Path = "app/static/vendor/tabler/fonts/tabler-icons.woff2"
        MinBytes = 100000
    },
    @{
        Name = "Tabler Icons MIT"
        Url = "https://raw.githubusercontent.com/tabler/tabler-icons/v3.35.0/LICENSE"
        Path = "app/static/vendor/tabler/LICENSE"
        MinBytes = 500
    },
    @{
        Name = "HTMX 2.0.7"
        Url = "https://cdnjs.cloudflare.com/ajax/libs/htmx/2.0.7/htmx.min.js"
        Path = "app/static/vendor/htmx/htmx.min.js"
        MinBytes = 30000
    },
    @{
        Name = "HTMX license"
        Url = "https://raw.githubusercontent.com/bigskysoftware/htmx/v2.0.7/LICENSE"
        Path = "app/static/vendor/htmx/LICENSE"
        MinBytes = 500
    }
)

function Get-VendoredAsset {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Asset
    )

    $destination = Join-Path $repoRoot $Asset.Path
    $directory = Split-Path -Parent $destination

    New-Item -ItemType Directory -Path $directory -Force | Out-Null

    if ((Test-Path $destination) -and -not $Force) {
        $existingSize = (Get-Item $destination).Length
        if ($existingSize -ge $Asset.MinBytes) {
            Write-Host "OK   $($Asset.Name) ya existe ($existingSize bytes)"
            return
        }
    }

    $temp = "$destination.download"
    Remove-Item $temp -Force -ErrorAction SilentlyContinue

    Write-Host "GET  $($Asset.Name)"
    Invoke-WebRequest -Uri $Asset.Url -OutFile $temp -UseBasicParsing

    $size = (Get-Item $temp).Length
    if ($size -lt $Asset.MinBytes) {
        Remove-Item $temp -Force -ErrorAction SilentlyContinue
        throw "Descarga inválida para $($Asset.Name): $size bytes."
    }

    Move-Item $temp $destination -Force
    Write-Host "OK   $($Asset.Name) ($size bytes)"
}

Write-Host "NERISOFT - instalando assets locales"
Write-Host "Repositorio: $repoRoot"
Write-Host ""

foreach ($asset in $assets) {
    Get-VendoredAsset -Asset $asset
}

$required = @(
    "app/static/vendor/geist/Geist-Variable.woff2",
    "app/static/vendor/tabler/tabler-icons.min.css",
    "app/static/vendor/tabler/fonts/tabler-icons.woff2",
    "app/static/vendor/htmx/htmx.min.js"
)

$missing = @()
foreach ($relativePath in $required) {
    if (-not (Test-Path (Join-Path $repoRoot $relativePath))) {
        $missing += $relativePath
    }
}

if ($missing.Count -gt 0) {
    throw "Faltan assets locales: $($missing -join ', ')"
}

Write-Host ""
Write-Host "Assets locales listos. NERISOFT ya puede servir tipografia, iconos y HTMX desde /static/vendor/."
