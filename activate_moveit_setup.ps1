$SetupPrefix = "$PSScriptRoot\moveit-setup\.pixi\envs\default"
if ($env:ROS_DISTRO -and $env:CONDA_PREFIX -ne $SetupPrefix) {
    throw 'Open a fresh terminal before activating the Setup Assistant environment.'
}
. "$PSScriptRoot\env-local.ps1"
Set-Location "$PSScriptRoot\moveit-setup"
$SetupEnvironment = & $env:ComSpec /d /c "call `"$PSScriptRoot\activate_moveit_setup.cmd`" >nul && python `"$PSScriptRoot\moveit\print_environment.py`""
if ($LASTEXITCODE -ne 0) { throw 'Setup Assistant activation failed.' }
$SetupVariables = ($SetupEnvironment -join "`n") | ConvertFrom-Json
foreach ($SetupVariable in $SetupVariables.PSObject.Properties) {
    [Environment]::SetEnvironmentVariable($SetupVariable.Name, [string]$SetupVariable.Value, 'Process')
}
Write-Host "MoveIt Setup Assistant / ROS 2 $env:ROS_DISTRO is ready: $env:CONDA_PREFIX"
