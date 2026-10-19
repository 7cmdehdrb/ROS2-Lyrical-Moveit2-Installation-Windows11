@echo off
call "%~dp0activate_moveit_setup.cmd"
if errorlevel 1 exit /b 1
ros2 run moveit_setup_assistant moveit_setup_assistant
