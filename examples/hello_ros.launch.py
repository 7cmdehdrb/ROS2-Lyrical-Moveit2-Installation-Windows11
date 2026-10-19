"""Launch an unpackaged Python node using the activated ROS interpreter."""
from pathlib import Path
import sys
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('message', default_value='Hello from launch'),
        DeclareLaunchArgument('max_messages', default_value='0'),
        ExecuteProcess(
            cmd=[sys.executable, str(Path(__file__).with_name('hello_ros.py')),
                 '--ros-args', '-p', ['message:=', LaunchConfiguration('message')],
                 '-p', ['max_messages:=', LaunchConfiguration('max_messages')]],
            output='screen',
        ),
    ])
