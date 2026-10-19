#Requires -Version 5.1
# Audit all tracked and not-ignored files without staging or changing them.
[CmdletBinding()]
param([int]$MaxMiB = 10)
$ErrorActionPreference = 'Stop'
$Repository = Split-Path $PSScriptRoot -Parent
Push-Location $Repository
try {
    $Names = & git -c core.quotepath=false ls-files --cached --others --exclude-standard
    if ($LASTEXITCODE -ne 0) { throw 'git ls-files failed.' }
    $Files = @($Names | Sort-Object -Unique | ForEach-Object {
        if (Test-Path -LiteralPath $_ -PathType Leaf) { Get-Item -LiteralPath $_ }
    })
    $IgnoredTracked = @(& git ls-files --cached --ignored --exclude-standard)
    if ($LASTEXITCODE -ne 0) { throw 'git ignore audit failed.' }
    if ($IgnoredTracked.Count -gt 0) {
        throw "Already tracked files match .gitignore. Review git rm --cached for these paths: $($IgnoredTracked -join ', ')"
    }
    $Oversized = @($Files | Where-Object Length -GT ($MaxMiB * 1MB))
    $Files | Sort-Object Length -Descending | Select-Object -First 10 @{Name='Path';Expression={$_.FullName.Substring($Repository.Length + 1)}},Length | Format-Table
    if ($Oversized.Count -gt 0) {
        throw "Files over $MaxMiB MiB remain: $($Oversized.FullName -join ', ')"
    }
    $Total = ($Files | Measure-Object Length -Sum).Sum
    Write-Host ("PASS: {0} files, {1:N2} MiB total, no file over {2} MiB, no ignored files already tracked." -f $Files.Count, ($Total / 1MB), $MaxMiB)
} finally { Pop-Location }
