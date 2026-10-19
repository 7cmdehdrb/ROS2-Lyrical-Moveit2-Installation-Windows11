"""Use the packaged mock Panda demo without starting RViz during automated checks."""
from pathlib import Path
import runpy
from ament_index_python.packages import get_package_share_directory
from launch import LaunchContext, LaunchDescription
from launch.utilities import normalize_to_list_of_substitutions, perform_substitutions
from launch_ros.actions import Node

def generate_launch_description():
    source = Path(get_package_share_directory('moveit_resources_panda_moveit_config')) / 'launch' / 'demo.launch.py'
    original = runpy.run_path(str(source))['generate_launch_description']()
    context = LaunchContext()
    actions = []
    for action in original.entities:
        if isinstance(action, Node):
            package = perform_substitutions(context, normalize_to_list_of_substitutions(action.node_package))
            if package == 'rviz2':
                continue
        actions.append(action)
    return LaunchDescription(actions)
