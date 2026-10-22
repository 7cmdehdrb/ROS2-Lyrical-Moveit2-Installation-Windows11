param([ValidateSet('rviz2', 'setup-assistant')][string]$Component = 'rviz2')
$ErrorActionPreference = 'Stop'
$MoveItProject = Split-Path $PSScriptRoot -Parent
if ($Component -eq 'rviz2') {
    . "$MoveItProject\activate_moveit.ps1"
} else {
    . "$MoveItProject\activate_moveit_setup.ps1"
}
$env:ROS_DOMAIN_ID = '180'
$env:ROS_AUTOMATIC_DISCOVERY_RANGE = 'LOCALHOST'
$GuiProfile = Join-Path $MoveItProject '.gui-profile'
New-Item -ItemType Directory -Force $GuiProfile,"$GuiProfile\AppData\Roaming","$GuiProfile\AppData\Local" | Out-Null
$GuiEnvironment = @{
    USERPROFILE = $GuiProfile
    APPDATA = "$GuiProfile\AppData\Roaming"
    LOCALAPPDATA = "$GuiProfile\AppData\Local"
}
$GuiChecks = @{}
foreach ($GuiTarget in @(
    @{Name='rviz2'; Exe="$env:CONDA_PREFIX\Library\bin\rviz2.exe"; Args=@('-d', "$env:CONDA_PREFIX\Library\share\ur_moveit_config\config\moveit.rviz")},
    @{Name='setup-assistant'; Exe="$env:CONDA_PREFIX\Library\lib\moveit_setup_assistant\moveit_setup_assistant.exe"; Args=@('--ros-args', '--log-level', 'info')}
)) {
    if ($GuiTarget.Name -ne $Component) { continue }
    $GuiStdout = "$MoveItProject\logs\moveit-$($GuiTarget.Name)-stdout.log"
    $GuiStderr = "$MoveItProject\logs\moveit-$($GuiTarget.Name)-stderr.log"
    $GuiProcess = Start-Process -FilePath $GuiTarget.Exe -ArgumentList $GuiTarget.Args -WindowStyle Hidden -Environment $GuiEnvironment -PassThru -RedirectStandardOutput $GuiStdout -RedirectStandardError $GuiStderr
    try {
        Start-Sleep -Seconds 12
        $GuiProcess.Refresh()
        $GuiChecks[$GuiTarget.Name] = @{running_after_12_seconds = !$GuiProcess.HasExited; exit_code = $(if ($GuiProcess.HasExited) {$GuiProcess.ExitCode} else {$null})}
    } finally {
        if (!$GuiProcess.HasExited) { Stop-Process -Id $GuiProcess.Id }
    }
}
$GuiChecks | ConvertTo-Json -Depth 4 | Set-Content "$MoveItProject\logs\moveit-gui-$Component-verification.json"
$GuiChecks | ConvertTo-Json -Depth 4
Get-Content "$MoveItProject\logs\moveit-$Component-stderr.log" -Tail 12
