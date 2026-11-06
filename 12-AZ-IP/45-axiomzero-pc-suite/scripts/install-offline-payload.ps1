# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 ThomasCory Walker-Pearson
param(
    [Parameter(Mandatory = $true)][string]$PayloadDirectory,
    [Parameter(Mandatory = $true)][string]$ManifestName,
    [Parameter(Mandatory = $true)][string]$ManifestSha256,
    [Parameter(Mandatory = $true)][string]$RuntimeManifest,
    [string]$DestinationDirectory,
    [switch]$ValidateOnly
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$modelFile = "Qwen3-4B-Instruct-2507-Q4_K_M.gguf"

function Assert-LocalPath([string]$FilePath, [bool]$Directory = $false) {
    if (-not [IO.Path]::IsPathRooted($FilePath) -or $FilePath.StartsWith("\\") -or $FilePath.StartsWith("//")) {
        throw "Offline payload paths must be absolute local paths."
    }
    $item = Get-Item -LiteralPath $FilePath -Force
    if (($item -is [IO.DirectoryInfo]) -ne $Directory) { throw "Unexpected payload path type." }
    while ($null -ne $item) {
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Reparse points are not permitted in offline payload paths."
        }
        if ($item -is [IO.DirectoryInfo]) { $item = $item.Parent } else { $item = $item.Directory }
    }
}

function Get-Hex([byte[]]$Bytes) {
    return [BitConverter]::ToString($Bytes).Replace("-", "").ToLowerInvariant()
}

function Read-TrustedJson([string]$FilePath, [string]$ExpectedHash) {
    Assert-LocalPath $FilePath
    $stream = [IO.File]::Open($FilePath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        if ($stream.Length -gt 16384 -or $stream.Length -eq 0) { throw "Oversized or empty manifest." }
        $bytes = New-Object byte[] ([int]$stream.Length)
        $offset = 0
        while ($offset -lt $bytes.Length) {
            $count = $stream.Read($bytes, $offset, $bytes.Length - $offset)
            if ($count -eq 0) { throw "Truncated manifest." }
            $offset += $count
        }
        $sha = [Security.Cryptography.SHA256]::Create()
        try { $hash = Get-Hex ($sha.ComputeHash($bytes)) } finally { $sha.Dispose() }
        if ($ExpectedHash -and $hash -cne $ExpectedHash) { throw "Installer-bound manifest SHA-256 mismatch." }
        return @{ Hash = $hash; Value = ([Text.Encoding]::UTF8.GetString($bytes) | ConvertFrom-Json) }
    } finally { $stream.Dispose() }
}

function Assert-Keys($Object, [string[]]$Keys) {
    $actual = @($Object.PSObject.Properties.Name | Sort-Object)
    $expected = @($Keys | Sort-Object)
    if (($actual -join ",") -cne ($expected -join ",")) { throw "Unexpected manifest fields." }
}

$partial = $null
$output = $null
$fullHash = $null
try {
    Assert-LocalPath $PayloadDirectory $true
    if ($ManifestName -cnotmatch '^AxiomZero-PC-Suite-\d+\.\d+\.\d+-offline\.json$' -or
        $ManifestSha256 -cnotmatch '^[a-f0-9]{64}$') { throw "Unsafe installer manifest parameters." }
    $payload = (Read-TrustedJson (Join-Path $PayloadDirectory $ManifestName) $ManifestSha256).Value
    Assert-Keys $payload @("formatVersion", "version", "runtimeManifestSha256", "model", "parts")
    Assert-Keys $payload.model @("file", "sizeBytes", "sha256")
    if ($payload.formatVersion -ne 1 -or $payload.version -cnotmatch '^\d+\.\d+\.\d+$' -or
        $ManifestName -cne "AxiomZero-PC-Suite-$($payload.version)-offline.json" -or
        $payload.runtimeManifestSha256 -cnotmatch '^[a-f0-9]{64}$') { throw "Unsupported offline payload manifest." }
    $runtime = (Read-TrustedJson $RuntimeManifest $payload.runtimeManifestSha256).Value
    if ($payload.model.file -cne $modelFile -or $runtime.model.file -cne $modelFile -or
        $payload.model.sha256 -cnotmatch '^[a-f0-9]{64}$' -or
        $payload.model.sha256 -cne $runtime.model.sha256 -or
        $payload.model.sizeBytes -ne $runtime.model.sizeBytes -or
        $payload.model.sizeBytes -lt 8 -or $payload.model.sizeBytes -gt 3000000000 -or
        $payload.model.sizeBytes -ne [Math]::Floor($payload.model.sizeBytes)) { throw "Model differs from the runtime manifest." }
    $parts = @($payload.parts)
    if ($parts.Count -lt 1 -or $parts.Count -gt 3) { throw "Unsupported offline part count." }
    [long]$expectedTotal = 0
    for ($index = 0; $index -lt $parts.Count; $index++) {
        $part = $parts[$index]
        Assert-Keys $part @("file", "sizeBytes", "sha256")
        $expectedName = "AxiomZero-PC-Suite-$($payload.version)-model.part{0:D3}" -f ($index + 1)
        if ($part.file -cne $expectedName -or $part.sha256 -cnotmatch '^[a-f0-9]{64}$' -or
            $part.sizeBytes -lt 1 -or $part.sizeBytes -gt 1073741824 -or
            $part.sizeBytes -ne [Math]::Floor($part.sizeBytes)) { throw "Unsafe offline part metadata." }
        $expectedTotal += $part.sizeBytes
        Assert-LocalPath (Join-Path $PayloadDirectory $part.file)
    }
    if ($expectedTotal -ne $payload.model.sizeBytes) { throw "Part total differs from the approved model size." }
    if (-not $ValidateOnly) {
        Assert-LocalPath $DestinationDirectory $true
        $destination = Join-Path $DestinationDirectory $modelFile
        if (Test-Path -LiteralPath $destination) { throw "Refusing to overwrite an existing model; reinstall into a clean destination." }
        $partial = Join-Path $DestinationDirectory (".p45-model-" + [Guid]::NewGuid().ToString("N") + ".partial")
        $output = [IO.File]::Open($partial, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    }
    $buffer = New-Object byte[] (1024 * 1024)
    $fullHash = [Security.Cryptography.SHA256]::Create()
    [long]$total = 0
    foreach ($part in $parts) {
        $file = Join-Path $PayloadDirectory $part.file
        Assert-LocalPath $file
        $inputStream = [IO.File]::Open($file, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        $partHash = [Security.Cryptography.SHA256]::Create()
        try {
            if ($inputStream.Length -ne $part.sizeBytes) { throw "Offline part length mismatch." }
            [long]$partTotal = 0
            while (($count = $inputStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
                $null = $partHash.TransformBlock($buffer, 0, $count, $buffer, 0)
                $null = $fullHash.TransformBlock($buffer, 0, $count, $buffer, 0)
                if ($output) { $output.Write($buffer, 0, $count) }
                $partTotal += $count
            }
            $null = $partHash.TransformFinalBlock([byte[]]@(), 0, 0)
            if ($partTotal -ne $part.sizeBytes -or (Get-Hex $partHash.Hash) -cne $part.sha256) {
                throw "Offline part SHA-256 mismatch."
            }
            $total += $partTotal
        } finally { $partHash.Dispose(); $inputStream.Dispose() }
    }
    $null = $fullHash.TransformFinalBlock([byte[]]@(), 0, 0)
    if ($total -ne $payload.model.sizeBytes -or (Get-Hex $fullHash.Hash) -cne $payload.model.sha256) {
        throw "Approved full-model SHA-256 mismatch."
    }
    if ($output) {
        $output.Flush($true)
        $output.Dispose()
        $output = $null
        Assert-LocalPath $DestinationDirectory $true
        [IO.File]::Move($partial, $destination)
        $partial = $null
    }
    Write-Host "VERIFIED OFFLINE payload: all part hashes and the full runtime model hash matched."
    exit 0
} catch {
    [Console]::Error.WriteLine("Offline payload FAILED: " + $_.Exception.Message)
    exit 1
} finally {
    if ($output) { $output.Dispose() }
    if ($fullHash) { $fullHash.Dispose() }
    if ($partial -and (Test-Path -LiteralPath $partial)) { Remove-Item -LiteralPath $partial -Force }
}
