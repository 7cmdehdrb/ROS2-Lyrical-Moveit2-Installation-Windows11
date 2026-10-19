# Dot-source this file to activate ROS 2 in the current PowerShell session.
if ($env:ROS_DISTRO -and $env:CONDA_PREFIX -ne "$PSScriptRoot\lyrical\.pixi\envs\default") {
    throw 'Open a fresh terminal before activating ROS 2. Do not mix ROS installations.'
}
. "$PSScriptRoot\env-local.ps1"
Set-Location "$PSScriptRoot\lyrical"
$RosPixiHook = & "$PSScriptRoot\tools\pixi\pixi.exe" shell-hook --shell powershell --as-is
if ($LASTEXITCODE -ne 0) { throw 'Pixi activation failed.' }
Invoke-Expression ($RosPixiHook -join "`n")
. "$PSScriptRoot\lyrical\local_setup.ps1"
$env:QT_QPA_PLATFORM_PLUGIN_PATH = "$PSScriptRoot\lyrical\.pixi\envs\default\Library\lib\qt6\plugins\platforms"
Write-Host "ROS 2 $env:ROS_DISTRO is ready. Python environment: $env:CONDA_PREFIX"
