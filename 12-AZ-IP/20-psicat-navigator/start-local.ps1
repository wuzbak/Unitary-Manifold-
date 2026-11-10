# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
# Local Navigator test without the Product 45 installer kit.
# Usage (from a repository checkout): powershell -NoProfile -File .\start-local.ps1 [-Port 8020]
param([int]$Port = 8020)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$venv = Join-Path $PSScriptRoot '.venv'
if (-not (Test-Path (Join-Path $venv 'Scripts\python.exe'))) {
    & py -3 -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.10+ (py launcher) is required.' }
}
$py = Join-Path $venv 'Scripts\python.exe'
& $py -m pip install --quiet -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
Write-Host "PsiCat Navigator: http://127.0.0.1:$Port/  (Ctrl+C to stop)"
& $py run.py --port $Port --no-open
