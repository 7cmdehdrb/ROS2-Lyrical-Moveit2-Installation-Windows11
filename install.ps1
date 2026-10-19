#Requires -Version 5.1
[CmdletBinding()]
param(
    [ValidateSet('ROS2', 'MoveIt', 'All')][string]$Component = 'All',
    [switch]$SkipVerification,
    [switch]$VerifyExecution
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ProjectRoot = $PSScriptRoot
$Summary = [ordered]@{
    component = $Component
    root = $ProjectRoot
    started_at = [DateTimeOffset]::Now.ToString('o')
    verification = $(if ($SkipVerification) { 'skipped' } else { 'requested' })
    success = $false
}

try {
    . "$ProjectRoot\scripts\install-common.ps1"
    Assert-InstallHost
    . "$ProjectRoot\env-local.ps1"
    $Sources = Get-Content -LiteralPath "$ProjectRoot\config\sources.json" -Raw | ConvertFrom-Json
    $PixiExe = Install-ProjectPixi $Sources.pixi
    if ($Component -in @('ROS2', 'All')) {
        Install-OfficialRos $Sources.ros2 $PixiExe
        if (!$SkipVerification) {
            Invoke-ActivatedPython 'activate_ros2.cmd' 'verify_install.py'
        }
    }
    if ($Component -in @('MoveIt', 'All')) {
        foreach ($Environment in @('moveit', 'moveit-setup')) {
            $Manifest = Join-Path $ProjectRoot "$Environment\pixi.toml"
            if (!(Test-Path -LiteralPath $Manifest) -or !(Test-Path -LiteralPath "$ProjectRoot\$Environment\pixi.lock")) {
                throw "Missing $Environment manifest/lock. Clone the complete repository."
            }
            Write-Host "Installing locked $Environment environment..."
            Invoke-Checked $PixiExe @('install', '--locked', '--manifest-path', $Manifest)
        }
        if (!$SkipVerification) {
            $CheckArgs = @('--planning-only')
            if ($VerifyExecution) { $CheckArgs = @() }
            Invoke-ActivatedPython 'activate_moveit.cmd' 'moveit\verify_runtime.py' $CheckArgs
        }
    }
    $Summary.success = $true
    $Summary.completed_at = [DateTimeOffset]::Now.ToString('o')
    if (!$SkipVerification) { $Summary.verification = 'passed' }
    $Summary | ConvertTo-Json | Set-Content -LiteralPath "$ProjectRoot\logs\install-$Component.json" -Encoding UTF8
    Write-Host "Installation complete: $Component ($ProjectRoot)"
    Write-Host 'ROS 2: start_ros2.cmd | MoveIt: start_moveit.cmd | Setup Assistant: start_moveit_setup.cmd'
} catch {
    $Summary.error = $_.Exception.Message
    $Summary.completed_at = [DateTimeOffset]::Now.ToString('o')
    if (Test-Path -LiteralPath "$ProjectRoot\logs") {
        $Summary | ConvertTo-Json | Set-Content -LiteralPath "$ProjectRoot\logs\install-$Component.json" -Encoding UTF8
    }
    [Console]::Error.WriteLine("Installation failed: $($_.Exception.Message)")
    exit 1
}
