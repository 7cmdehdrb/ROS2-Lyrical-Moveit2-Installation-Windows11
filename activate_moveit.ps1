$MoveItPrefix = "$PSScriptRoot\moveit\.pixi\envs\default"
if ($env:ROS_DISTRO -and $env:CONDA_PREFIX -ne $MoveItPrefix) {
    throw 'Open a fresh terminal before activating MoveIt. Do not mix ROS installations.'
}
. "$PSScriptRoot\env-local.ps1"
Set-Location "$PSScriptRoot\moveit"
# RoboStack's package includes local_setup.bat but not local_setup.ps1.
# Import the working CMD activation environment without touching user profiles.
$MoveItEnvironment = & $env:ComSpec /d /c "call `"$PSScriptRoot\activate_moveit.cmd`" >nul && python `"$PSScriptRoot\moveit\print_environment.py`""
if ($LASTEXITCODE -ne 0) { throw 'MoveIt CMD environment activation failed.' }
$MoveItVariables = ($MoveItEnvironment -join "`n") | ConvertFrom-Json
foreach ($MoveItVariable in $MoveItVariables.PSObject.Properties) {
    [Environment]::SetEnvironmentVariable($MoveItVariable.Name, [string]$MoveItVariable.Value, 'Process')
}
Write-Host "MoveIt 2 / ROS 2 $env:ROS_DISTRO is ready: $env:CONDA_PREFIX"
