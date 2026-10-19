@echo off
if defined ROS_DISTRO if /I not "%CONDA_PREFIX%"=="%~dp0lyrical\.pixi\envs\default" (
 echo Open a fresh terminal before activating ROS 2. Do not mix ROS installations.
 exit /b 1
)
call "%~dp0env-local.cmd"
cd /d "%~dp0lyrical"
set "_ROS_PIXI_HOOK=%~dp0tmp\pixi-activate-%RANDOM%-%RANDOM%.cmd"
pixi shell-hook --shell cmd --as-is > "%_ROS_PIXI_HOOK%"
if errorlevel 1 exit /b 1
call "%_ROS_PIXI_HOOK%"
if errorlevel 1 exit /b 1
del "%_ROS_PIXI_HOOK%"
set "_ROS_PIXI_HOOK="
call "%~dp0lyrical\local_setup.bat"
if errorlevel 1 exit /b 1
set "QT_QPA_PLATFORM_PLUGIN_PATH=%~dp0lyrical\.pixi\envs\default\Library\lib\qt6\plugins\platforms"
echo ROS 2 %ROS_DISTRO% is ready. Python environment: %CONDA_PREFIX%
