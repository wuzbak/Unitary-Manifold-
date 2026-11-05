$ErrorActionPreference = "Stop"

$suiteDirectory = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$distributionDirectory = Join-Path $suiteDirectory "dist"
$smokeScript = Join-Path $PSScriptRoot "electron-ui-smoke.cjs"
$package = Get-Content -LiteralPath (Join-Path $suiteDirectory "package.json") -Raw | ConvertFrom-Json
$installer = Join-Path $distributionDirectory "AxiomZero-PC-Suite-$($package.version)-x64.exe"
$portable = Join-Path $distributionDirectory "AxiomZero-PC-Suite-$($package.version)-portable-x64.exe"
$installDirectory = Join-Path $env:LOCALAPPDATA "Programs\AxiomZero PC Suite"
$installedApp = Join-Path $installDirectory "AxiomZero PC Suite.exe"
$uninstaller = Join-Path $installDirectory "Uninstall AxiomZero PC Suite.exe"

foreach ($artifact in @($installer, $portable)) {
    if (-not (Test-Path -LiteralPath $artifact -PathType Leaf)) {
        throw "Required Windows artifact is missing: $artifact"
    }
}

function Test-ProductWindow([string]$Executable, [string]$Label) {
    $port = Get-Random -Minimum 30000 -Maximum 50000
    $userData = Join-Path $env:TEMP "p45 smoke-$PID-$port"
    $env:P45_SMOKE_PORT = "$port"
    $appProcess = $null
    try {
        $arguments = @("--remote-debugging-port=$port", ('--user-data-dir="{0}"' -f $userData))
        $appProcess = Start-Process -FilePath $Executable -ArgumentList $arguments -PassThru
        & node $smokeScript
        if ($LASTEXITCODE -ne 0) {
            throw "$Label UI smoke test failed with exit code $LASTEXITCODE."
        }
        if (-not (Test-Path -LiteralPath $userData -PathType Container)) {
            throw "$Label application did not create its isolated user-data directory: $userData"
        }
        Write-Host "$Label application launch and UI smoke passed."
    } finally {
        if ($appProcess -and -not $appProcess.HasExited) {
            & taskkill.exe /PID $appProcess.Id /T /F | Out-Null
            $appProcess.WaitForExit(10000) | Out-Null
        }
        if (Test-Path -LiteralPath $userData) {
            Remove-Item -LiteralPath $userData -Recurse -Force
        }
        Remove-Item Env:P45_SMOKE_PORT -ErrorAction SilentlyContinue
    }
}

$installProcess = Start-Process -FilePath $installer -ArgumentList @("/S") -Wait -PassThru
if ($installProcess.ExitCode -ne 0) {
    throw "The NSIS installer exited with code $($installProcess.ExitCode)."
}
if (-not (Test-Path -LiteralPath $installedApp -PathType Leaf)) {
    throw "The installer completed but did not install the application at $installedApp."
}

try {
    & node (Join-Path $PSScriptRoot "instruction_smoke.cjs") (Join-Path $installDirectory "resources\psicat-instruction")
    if ($LASTEXITCODE -ne 0) {
        throw "Installed instruction-model inference failed."
    }
    & node (Join-Path $PSScriptRoot "platform_smoke.cjs") (Join-Path $installDirectory "resources\platform-targets")
    if ($LASTEXITCODE -ne 0) {
        throw "Installed platform-artifact integrity or structure verification failed."
    }
    & node (Join-Path $PSScriptRoot "native_smoke.cjs") (Join-Path $installDirectory "resources\psicat-native")
    if ($LASTEXITCODE -ne 0) {
        throw "Installed native model smoke failed."
    }
    & node (Join-Path $PSScriptRoot "portfolio_smoke.cjs") (Join-Path $installDirectory "resources\portfolio")
    if ($LASTEXITCODE -ne 0) {
        throw "Installed portfolio runtime smoke failed."
    }
    Test-ProductWindow $installedApp "Installed"
} finally {
    if (Test-Path -LiteralPath $uninstaller -PathType Leaf) {
        $uninstallProcess = Start-Process -FilePath $uninstaller -ArgumentList @("/S") -Wait -PassThru
        if ($uninstallProcess.ExitCode -ne 0) {
            throw "The NSIS uninstaller exited with code $($uninstallProcess.ExitCode)."
        }
    } else {
        throw "The installed application did not include its uninstaller."
    }
}

if (Test-Path -LiteralPath $installDirectory) {
    throw "The NSIS uninstaller left the application directory behind."
}

Test-ProductWindow $portable "Portable"
