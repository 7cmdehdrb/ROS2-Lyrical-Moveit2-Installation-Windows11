@echo off
if defined ROS_DISTRO if /I not "%CONDA_PREFIX%"=="%~dp0moveit\.pixi\envs\default" (
  echo Open a fresh terminal before activating MoveIt. Do not mix ROS installations.
  exit /b 1
)
call "%~dp0env-local.cmd"
cd /d "%~dp0moveit"
set "_MOVEIT_PIXI_HOOK=%~dp0tmp\moveit-activate-%RANDOM%-%RANDOM%.cmd"
pixi shell-hook --shell cmd --as-is > "%_MOVEIT_PIXI_HOOK%"
if errorlevel 1 exit /b 1
call "%_MOVEIT_PIXI_HOOK%"
if errorlevel 1 exit /b 1
del "%_MOVEIT_PIXI_HOOK%"
set "_MOVEIT_PIXI_HOOK="
echo MoveIt 2 / ROS 2 %ROS_DISTRO% is ready: %CONDA_PREFIX%
