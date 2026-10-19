@echo off
if defined ROS_DISTRO if /I not "%CONDA_PREFIX%"=="%~dp0moveit-setup\.pixi\envs\default" (
  echo Open a fresh terminal before activating the Setup Assistant environment.
  exit /b 1
)
call "%~dp0env-local.cmd"
cd /d "%~dp0moveit-setup"
set "_SETUP_PIXI_HOOK=%~dp0tmp\setup-activate-%RANDOM%-%RANDOM%.cmd"
pixi shell-hook --shell cmd --as-is > "%_SETUP_PIXI_HOOK%"
if errorlevel 1 exit /b 1
call "%_SETUP_PIXI_HOOK%"
if errorlevel 1 exit /b 1
del "%_SETUP_PIXI_HOOK%"
set "_SETUP_PIXI_HOOK="
echo MoveIt Setup Assistant / ROS 2 %ROS_DISTRO% is ready: %CONDA_PREFIX%
