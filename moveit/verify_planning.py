"""Plan a collision-checked Panda motion with the installed MoveIt Python API."""
import json
import os
from pathlib import Path
import sys
import gc
import time
import xml.etree.ElementTree as ET

os.environ['ROS_DOMAIN_ID'] = '178'
os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
os.environ.setdefault('RMW_IMPLEMENTATION', 'rmw_fastrtps_cpp')

from ament_index_python.packages import get_package_share_directory, get_packages_with_prefixes
from moveit_configs_utils import MoveItConfigsBuilder
from moveit.planning import MoveItPy
from moveit.core.robot_state import RobotState

ROOT = Path(__file__).resolve().parent.parent
required = [
    'moveit', 'moveit_core', 'moveit_ros_move_group', 'moveit_py',
    'moveit_ros_visualization', 'moveit_setup_assistant', 'moveit_servo',
    'moveit_planners_ompl', 'moveit_planners_chomp', 'moveit_planners_stomp',
    'pilz_industrial_motion_planner', 'rviz2', 'controller_manager',
    'moveit_resources_panda_moveit_config', 'warehouse_ros_sqlite',
]
packages = get_packages_with_prefixes()
assert all(p in packages for p in required), [p for p in required if p not in packages]
versions = {}
for package in required:
    manifest = Path(get_package_share_directory(package)) / 'package.xml'
    versions[package] = ET.parse(manifest).findtext('version')

pipelines = ['ompl', 'chomp', 'stomp', 'pilz_industrial_motion_planner']
config = (
    MoveItConfigsBuilder('moveit_resources_panda', package_name='moveit_resources_panda_moveit_config')
    .robot_description(file_path='config/panda.urdf.xacro', mappings={'ros2_control_hardware_type': 'mock_components'})
    .robot_description_semantic(file_path='config/panda.srdf')
    .trajectory_execution(file_path='config/gripper_moveit_controllers.yaml')
    .planning_pipelines(pipelines=pipelines)
    .to_moveit_configs().to_dict()
)
config['planning_pipelines'] = {'pipeline_names': pipelines}
config['planning_scene_monitor_options'] = {
    'name': 'moveit_install_verification',
    'robot_description': 'robot_description',
    'joint_state_topic': '/joint_states',
    'attached_collision_object_topic': '/moveit_install/attached_collision_object',
    'publish_planning_scene_topic': '/moveit_install/publish_planning_scene',
    'monitored_planning_scene_topic': '/moveit_install/monitored_planning_scene',
    'wait_for_initial_state_timeout': 0.0,
}
config['plan_request_params'] = {
    'planning_attempts': 1,
    'planning_pipeline': 'ompl',
    'planner_id': 'RRTConnectkConfigDefault',
    'planning_time': 5.0,
    'max_velocity_scaling_factor': 0.2,
    'max_acceleration_scaling_factor': 0.2,
}
robot = MoveItPy(node_name='moveit_install_verification', config_dict=config)
try:
    arm = robot.get_planning_component('panda_arm')
    arm.set_start_state(configuration_name='ready')
    goal = RobotState(robot.get_robot_model())
    goal.set_to_default_values()
    goal.set_joint_group_positions('panda_arm', [0.3, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785])
    goal.update()
    arm.set_goal_state(robot_state=goal)
    result = arm.plan()
    assert result, 'OMPL failed to produce a motion plan'
    trajectory = result.trajectory
    report = {
        'planning_passed': len(trajectory) > 1,
        'ros_distro': os.environ.get('ROS_DISTRO'),
        'python': sys.version,
        'python_executable': sys.executable,
        'ros_package_count': len(packages),
        'versions': versions,
        'requested_pipelines': pipelines,
        'tested_planner': 'OMPL / RRTConnect',
        'robot': 'Panda (packaged model; no hardware connection)',
        'trajectory_waypoints': len(trajectory),
        'trajectory_duration_seconds': trajectory.duration,
    }
    (ROOT / 'logs' / 'moveit-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)
    assert report['planning_passed']
finally:
    # Release dependent pybind objects while Python and ROS are still running.
    arm = goal = result = trajectory = None
    # MoveItPy's deleter cancels its executor and shuts ROS down itself.
    robot = None
    gc.collect()
    time.sleep(1)
