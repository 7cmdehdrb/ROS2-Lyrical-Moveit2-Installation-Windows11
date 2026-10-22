"""UR model + MoveIt planning, without robot drivers or execution controllers."""
from pathlib import Path
import math
import xml.etree.ElementTree as ET

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder

# Models shipped in the pinned ur_description 4.3.1 package.
UR_TYPES = ('ur3', 'ur5', 'ur10', 'ur3e', 'ur5e', 'ur7e', 'ur10e',
            'ur12e', 'ur16e', 'ur8long', 'ur15', 'ur18', 'ur20', 'ur30')


def merge_mapping(base, overrides):
    """Merge mappings recursively; scalar and list values replace the original."""
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merge_mapping(base[key], value)
        else:
            base[key] = value


def apply_yaml(context, argument, target):
    filename = LaunchConfiguration(argument).perform(context).strip()
    if not filename:
        return
    path = Path(filename)
    if not path.is_absolute():
        raise ValueError(f'{argument} must be an absolute path: {filename}')
    with path.open(encoding='utf-8-sig') as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict) or 'ros__parameters' in data:
        raise ValueError(f'{argument} must contain a raw MoveIt YAML mapping.')
    merge_mapping(target, data)


def build_config(ur_type):
    if ur_type not in UR_TYPES:
        raise ValueError(f'Unsupported ur_type: {ur_type}')
    description = Path(get_package_share_directory('ur_description'))
    config = (
        MoveItConfigsBuilder('ur', package_name='ur_moveit_config')
        .robot_description(file_path=str(description / 'urdf' / 'ur.urdf.xacro'),
                           mappings={'name': ur_type, 'ur_type': ur_type})
        .robot_description_semantic(file_path='srdf/ur.srdf.xacro', mappings={'name': ur_type})
        .planning_pipelines(pipelines=['ompl'])
        .planning_scene_monitor(publish_robot_description=True,
                                publish_robot_description_semantic=True)
        .to_moveit_configs()
    )
    # The builder loads controller YAML by default; this launch is planning-only.
    config.trajectory_execution.clear()
    return config


def home_positions(config):
    """Use the package's named pose for a stationary planning start state."""
    srdf = ET.fromstring(config.robot_description_semantic['robot_description_semantic'])
    home = srdf.find("group_state[@name='home'][@group='ur_manipulator']")
    if home is None:
        raise ValueError('The UR SRDF must provide the ur_manipulator home pose.')
    return {joint.attrib['name']: float(joint.attrib['value']) for joint in home.findall('joint')}


def launch_nodes(context):
    ur_type = LaunchConfiguration('ur_type').perform(context)
    share = Path(get_package_share_directory('ur_moveit_config'))
    config = build_config(ur_type)
    kinematics = config.robot_description_kinematics['robot_description_kinematics']
    apply_yaml(context, 'kinematics_file', kinematics)
    apply_yaml(context, 'joint_limits_file', config.joint_limits['robot_description_planning'])
    apply_yaml(context, 'ompl_file', config.planning_pipelines['ompl'])
    timeout = LaunchConfiguration('ik_timeout').perform(context).strip()
    if timeout:
        value = float(timeout)
        if not math.isfinite(value) or value <= 0:
            raise ValueError('ik_timeout must be a positive, finite number of seconds.')
        kinematics['ur_manipulator']['kinematics_solver_timeout'] = value

    return [
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[config.robot_description]),
        # Publishes a fixed pose only. It does not accept or execute trajectories.
        Node(package='joint_state_publisher', executable='joint_state_publisher',
             parameters=[config.robot_description, {'rate': 30, 'zeros': home_positions(config)}]),
        Node(package='moveit_ros_move_group', executable='move_group', name='move_group',
             output='screen', parameters=[config.to_dict(), {'allow_trajectory_execution': False}]),
        Node(package='rviz2', executable='rviz2', name='rviz2', output='log',
             condition=IfCondition(LaunchConfiguration('rviz')),
             arguments=['-d', str(share / 'config' / 'moveit.rviz')],
             parameters=[config.robot_description, config.robot_description_semantic,
                         config.robot_description_kinematics, config.joint_limits,
                         config.planning_pipelines]),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('ur_type', default_value='ur5e', choices=list(UR_TYPES)),
        DeclareLaunchArgument('rviz', default_value='true', description='Start RViz'),
        DeclareLaunchArgument('kinematics_file', default_value='',
                              description='Optional absolute path to raw kinematics YAML'),
        DeclareLaunchArgument('joint_limits_file', default_value='',
                              description='Optional absolute path to raw joint limits YAML'),
        DeclareLaunchArgument('ompl_file', default_value='',
                              description='Optional absolute path to raw OMPL YAML'),
        DeclareLaunchArgument('ik_timeout', default_value='',
                              description='Optional ur_manipulator IK timeout in seconds; overrides YAML'),
        OpaqueFunction(function=launch_nodes),
    ])
