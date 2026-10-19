$RosProjectRoot = $PSScriptRoot
$env:PIXI_HOME = Join-Path $RosProjectRoot 'tools\pixi-home'
$env:PIXI_CACHE_DIR = Join-Path $RosProjectRoot '.cache\pixi'
$env:RATTLER_CACHE_DIR = $env:PIXI_CACHE_DIR
$env:UV_CACHE_DIR = Join-Path $RosProjectRoot '.cache\uv'
$env:PIP_CACHE_DIR = Join-Path $RosProjectRoot '.cache\pip'
$env:TEMP = Join-Path $RosProjectRoot 'tmp'
$env:TMP = $env:TEMP
$env:ROS_HOME = Join-Path $RosProjectRoot '.ros'
$env:ROS_LOG_DIR = Join-Path $RosProjectRoot 'logs\ros'
$env:COLCON_HOME = Join-Path $RosProjectRoot '.colcon'
# Avoid Fast DDS shared-memory files in the system ProgramData directory.
$env:FASTDDS_BUILTIN_TRANSPORTS = 'UDPv4'
$env:PYTHONNOUSERSITE = '1'
foreach ($RosDirectory in @($env:PIXI_HOME, $env:PIXI_CACHE_DIR, $env:UV_CACHE_DIR, $env:PIP_CACHE_DIR, $env:TEMP, $env:ROS_HOME, $env:ROS_LOG_DIR, $env:COLCON_HOME)) {
    New-Item -ItemType Directory -Force -Path $RosDirectory | Out-Null
}
$env:PATH = (Join-Path $RosProjectRoot 'tools\pixi') + ';' + $env:PATH
