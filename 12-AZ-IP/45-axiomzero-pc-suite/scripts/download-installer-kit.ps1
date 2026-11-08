# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 ThomasCory Walker-Pearson
[CmdletBinding()]
param(
    [string]$Tag = 'pc-suite-v0.1.2',
    [string]$DestinationDirectory = '',
    [switch]$AcceptLargeDownload
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-KitUrl([string]$Url, [switch]$Redirect) {
    $uri = [Uri]$Url
    $hosts = @('github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com')
    if ($uri.Scheme -cne 'https' -or $uri.Port -ne 443 -or $uri.UserInfo -or $uri.Fragment -or
        ($Redirect -and $hosts -cnotcontains $uri.DnsSafeHost) -or
        (-not $Redirect -and @('api.github.com', 'github.com') -cnotcontains $uri.DnsSafeHost)) {
        throw 'Only approved GitHub HTTPS URLs are permitted.'
    }
}

function Receive-KitFile([string]$Url, [string]$Path, [long]$Limit, [long]$ExpectedSize = -1) {
    Assert-KitUrl $Url
    $created = $false
    $response = $null
    $inputStream = $null
    $outputStream = $null
    $clock = [Diagnostics.Stopwatch]::StartNew()
    try {
        for ($redirects = 0; ; $redirects++) {
            $request = [Net.HttpWebRequest]::Create($Url)
            $request.AllowAutoRedirect = $false
            $request.Timeout = 60000
            $request.ReadWriteTimeout = 60000
            $request.UserAgent = 'AxiomZero-PC-Suite-Installer-Kit/1'
            $request.Headers['Accept'] = 'application/vnd.github+json'
            $response = $request.GetResponse()
            $status = [int]$response.StatusCode
            if ($status -in @(301, 302, 303, 307, 308)) {
                if ($redirects -ge 5) { throw 'Too many download redirects.' }
                $next = [Uri]::new([Uri]$Url, $response.Headers['Location']).AbsoluteUri
                Assert-KitUrl $next -Redirect
                $response.Dispose()
                $response = $null
                $Url = $next
                continue
            }
            if ($status -ne 200) { throw "Download returned HTTP $status." }
            break
        }
        if ($response.ContentLength -gt $Limit -or
            ($ExpectedSize -ge 0 -and $response.ContentLength -ge 0 -and $response.ContentLength -ne $ExpectedSize)) {
            throw 'Download Content-Length exceeds bounds or differs from release metadata.'
        }
        $inputStream = $response.GetResponseStream()
        $outputStream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        $created = $true
        $buffer = New-Object byte[] 65536
        [long]$total = 0
        while (($read = $inputStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
            if ($clock.Elapsed.TotalMinutes -gt 30) { throw 'Download exceeded the thirty-minute file deadline.' }
            $total += $read
            if ($total -gt $Limit -or ($ExpectedSize -ge 0 -and $total -gt $ExpectedSize)) {
                throw 'Download exceeded its byte bound.'
            }
            $outputStream.Write($buffer, 0, $read)
        }
        if ($ExpectedSize -ge 0 -and $total -ne $ExpectedSize) { throw 'Download size mismatch.' }
    } catch {
        if ($outputStream) { $outputStream.Dispose(); $outputStream = $null }
        if ($created) { [IO.File]::Delete($Path) }
        throw
    } finally {
        if ($outputStream) { $outputStream.Dispose() }
        if ($inputStream) { $inputStream.Dispose() }
        if ($response) { $response.Dispose() }
    }
}

function Assert-KitDirectory([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force
    while ($item) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse points are not permitted.' }
        $item = $item.Parent
    }
}

function Get-KitPlan($Release, [string]$Checksums, [string]$Version, [string]$ReleaseTag) {
    if ($Release.tag_name -cne $ReleaseTag -or $Release.draft -ne $false) { throw 'Release tag mismatch or draft release.' }
    $prefix = "AxiomZero-PC-Suite-$Version"
    $assets = @{}
    foreach ($asset in $Release.assets) {
        if ($assets.ContainsKey($asset.name)) { throw 'Duplicate release asset.' }
        $assets[$asset.name] = $asset
    }
    $plan = @()
    $names = @{}
    foreach ($line in ($Checksums -split "`n")) {
        $line = $line.TrimEnd("`r")
        if ($line -eq '') { continue }
        if ($line -cnotmatch '^([a-f0-9]{64})  ([A-Za-z0-9.-]+)$') { throw 'Invalid checksum entry.' }
        $hash = $Matches[1]
        $name = $Matches[2]
        $allowed = @("$prefix-x64.exe", "$prefix-offline.json", "$prefix-download.ps1")
        if ($allowed -cnotcontains $name -and $name -cnotmatch ("^" + [regex]::Escape($prefix) + '-model\.part[0-9]{3}$')) {
            throw 'Unsafe or unexpected checksum asset name.'
        }
        if ($names.ContainsKey($name) -or -not $assets.ContainsKey($name)) { throw 'Duplicate or missing checksum asset.' }
        $names[$name] = $true
        $asset = $assets[$name]
        if ($asset.size -isnot [long] -and $asset.size -isnot [int]) { throw 'Invalid asset size.' }
        if ($asset.size -le 0 -or $asset.size -ge 2GB) { throw 'Asset size outside release bounds.' }
        if (($name -ceq "$prefix-offline.json" -and $asset.size -gt 64KB) -or
            ($name -ceq "$prefix-download.ps1" -and $asset.size -gt 256KB) -or
            ($name -match '-model\.part[0-9]{3}$' -and $asset.size -gt 1GB)) {
            throw 'Companion asset exceeds its type-specific size bound.'
        }
        $expectedUrl = "https://github.com/wuzbak/Unitary-Manifold-/releases/download/$ReleaseTag/$name"
        if ($asset.browser_download_url -cne $expectedUrl) { throw 'Unexpected release download URL.' }
        $plan += [pscustomobject]@{ Name = $name; Hash = $hash; Size = [long]$asset.size; Url = $expectedUrl }
        if ($plan.Count -gt 16) { throw 'Too many installer kit assets.' }
    }
    if (-not $names.ContainsKey("$prefix-x64.exe") -or -not $names.ContainsKey("$prefix-offline.json")) {
        throw 'Installer or offline manifest is missing.'
    }
    $parts = @($plan | Where-Object { $_.Name -match '-model\.part[0-9]{3}$' } | Sort-Object Name)
    if ($parts.Count -lt 1) { throw 'Model companion parts are missing.' }
    for ($i = 0; $i -lt $parts.Count; $i++) {
        if ($parts[$i].Name -cne ("$prefix-model.part{0:D3}" -f ($i + 1))) { throw 'Noncontiguous model parts.' }
    }
    if (($plan | Measure-Object Size -Sum).Sum -gt 8GB) { throw 'Installer kit exceeds total size limit.' }
    return $plan
}

# Direct .NET hashing avoids Get-FileHash module autoloading, which fails when
# Windows PowerShell 5.1 inherits PowerShell 7's PSModulePath.
function Get-KitSha256([string]$Path) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        try { $digest = $sha.ComputeHash($stream) } finally { $stream.Dispose() }
    } finally { $sha.Dispose() }
    return [BitConverter]::ToString($digest).Replace('-', '').ToLowerInvariant()
}

function Test-KitFile([string]$Path, [long]$Size, [string]$Hash) {
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
        $item.Length -ne $Size -or (Get-KitSha256 $Path) -cne $Hash) {
        throw 'Downloaded file failed size/SHA-256 verification.'
    }
}

function Test-KitManifest($Plan, [string[]]$Files, [string]$Version) {
    $manifestIndex = -1
    for ($i = 0; $i -lt $Plan.Count; $i++) {
        if ($Plan[$i].Name -ceq "AxiomZero-PC-Suite-$Version-offline.json") { $manifestIndex = $i }
    }
    $manifest = Get-Content -LiteralPath $Files[$manifestIndex] -Raw | ConvertFrom-Json
    if ($manifest.formatVersion -ne 1 -or $manifest.version -cne $Version -or
        $manifest.runtimeManifestSha256 -cnotmatch '^[a-f0-9]{64}$' -or
        $manifest.model.file -cne 'Qwen3-4B-Instruct-2507-Q4_K_M.gguf' -or
        $manifest.model.sha256 -cnotmatch '^[a-f0-9]{64}$' -or
        $manifest.model.sizeBytes -lt 8 -or $manifest.model.sizeBytes -gt 3000000000) {
        throw 'Invalid offline manifest contract.'
    }
    $parts = @($Plan | Where-Object { $_.Name -match '-model\.part[0-9]{3}$' } | Sort-Object Name)
    if (@($manifest.parts).Count -ne $parts.Count) { throw 'Offline manifest/checksum part count mismatch.' }
    $hash = [Security.Cryptography.SHA256]::Create()
    [long]$total = 0
    try {
        for ($i = 0; $i -lt $parts.Count; $i++) {
            $part = $manifest.parts[$i]
            if ($part.file -cne $parts[$i].Name -or $part.sha256 -cne $parts[$i].Hash -or $part.sizeBytes -ne $parts[$i].Size) {
                throw 'Offline manifest/checksum part mismatch.'
            }
            $index = [Array]::IndexOf($Plan, $parts[$i])
            $stream = [IO.File]::OpenRead($Files[$index])
            try {
                $buffer = New-Object byte[] 65536
                while (($read = $stream.Read($buffer, 0, $buffer.Length)) -gt 0) {
                    $null = $hash.TransformBlock($buffer, 0, $read, $buffer, 0)
                    $total += $read
                }
            } finally { $stream.Dispose() }
        }
        $null = $hash.TransformFinalBlock((New-Object byte[] 0), 0, 0)
        $digest = [BitConverter]::ToString($hash.Hash).Replace('-', '').ToLowerInvariant()
        if ($total -ne $manifest.model.sizeBytes -or $digest -cne $manifest.model.sha256) {
            throw 'Full model size/SHA-256 mismatch.'
        }
    } finally { $hash.Dispose() }
}

function Invoke-InstallerKitDownload {
    if ($Tag -cnotmatch '^pc-suite-v([0-9]+\.[0-9]+\.[0-9]+)$') { throw 'Use an explicit pc-suite-vMAJOR.MINOR.PATCH tag, never latest.' }
    $version = $Matches[1]
    if (-not $DestinationDirectory) { $DestinationDirectory = ".\AxiomZero-PC-Suite-$version-kit" }
    $destination = [IO.Path]::GetFullPath($DestinationDirectory)
    if ($destination.StartsWith('\\')) { throw 'Use a local destination, not a network path.' }
    if (-not (Test-Path -LiteralPath $destination -PathType Container)) {
        throw 'Create the destination folder yourself first. It must not contain existing kit files.'
    }
    Assert-KitDirectory $destination
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $scratch = @()
    try {
        $metadataPath = Join-Path $destination ("release-" + [Guid]::NewGuid().ToString('N') + '.partial')
        Receive-KitFile "https://api.github.com/repos/wuzbak/Unitary-Manifold-/releases/tags/$Tag" $metadataPath 1MB
        $scratch += $metadataPath
        $release = Get-Content -LiteralPath $metadataPath -Raw | ConvertFrom-Json
        if ($release.tag_name -cne $Tag -or $release.draft -ne $false) { throw 'Release tag mismatch or draft release.' }
        $sumAsset = @($release.assets | Where-Object { $_.name -ceq 'SHA256SUMS.txt' })
        if ($sumAsset.Count -ne 1 -or $sumAsset[0].size -le 0 -or $sumAsset[0].size -gt 64KB -or
            $sumAsset[0].browser_download_url -cne "https://github.com/wuzbak/Unitary-Manifold-/releases/download/$Tag/SHA256SUMS.txt") {
            throw 'Missing or invalid official checksum asset.'
        }
        $sumsPath = Join-Path $destination ("checksums-" + [Guid]::NewGuid().ToString('N') + '.partial')
        Receive-KitFile $sumAsset[0].browser_download_url $sumsPath 64KB $sumAsset[0].size
        $scratch += $sumsPath
        $plan = @(Get-KitPlan $release (Get-Content -LiteralPath $sumsPath -Raw) $version $Tag)
        foreach ($name in (@($plan.Name) + 'SHA256SUMS.txt')) {
            if (Test-Path -LiteralPath (Join-Path $destination $name)) { throw "Refusing to overwrite $name. Use a new empty folder." }
        }
        $total = ($plan | Measure-Object Size -Sum).Sum
        Write-Host ("This explicit download retrieves {0:N2} GiB for {1}. Setup needs additional space for the assembled model." -f ($total / 1GB), $Tag)
        if (-not $AcceptLargeDownload -and (Read-Host 'Type DOWNLOAD to consent (anything else stops)') -cne 'DOWNLOAD') {
            throw 'Download consent was not given.'
        }
        foreach ($entry in $plan) {
            Assert-KitDirectory $destination
            $partial = Join-Path $destination ($entry.Name + '.' + [Guid]::NewGuid().ToString('N') + '.partial')
            Write-Host "Downloading $($entry.Name)"
            Receive-KitFile $entry.Url $partial $entry.Size $entry.Size
            $scratch += $partial
            Test-KitFile $partial $entry.Size $entry.Hash
        }
        Test-KitManifest $plan @($scratch | Select-Object -Skip 2) $version
        # All assets are verified before exposing any final filenames.
        for ($i = 0; $i -lt $plan.Count; $i++) {
            [IO.File]::Move($scratch[$i + 2], (Join-Path $destination $plan[$i].Name))
        }
        [IO.File]::Move($sumsPath, (Join-Path $destination 'SHA256SUMS.txt'))
        Write-Host "VERIFIED INSTALLER KIT: $destination"
        Write-Host 'Nothing was installed or launched. Review the files, then manually run the EXE in this folder.'
    } catch {
        Write-Warning 'Stopped. Partial downloads are removed; there are no automatic retries. If final files exist, keep them and retry in a NEW empty folder. Never run an incomplete kit.'
        throw
    } finally {
        foreach ($file in $scratch) {
            if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file -Force -ErrorAction Stop }
        }
    }
}

if ($MyInvocation.InvocationName -ne '.') { Invoke-InstallerKitDownload }
