"""Panda mock demo with explicit, editable YAML overrides and an IK argument."""
from pathlib import Path
import math
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


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


def launch_nodes(context):
    share = Path(get_package_share_directory('moveit_resources_panda_moveit_config'))
    config = (
        MoveItConfigsBuilder('moveit_resources_panda', package_name='moveit_resources_panda_moveit_config')
        .robot_description(file_path='config/panda.urdf.xacro',
                           mappings={'ros2_control_hardware_type': 'mock_components'})
        .robot_description_semantic(file_path='config/panda.srdf')
        .trajectory_execution(file_path='config/gripper_moveit_controllers.yaml')
        .planning_scene_monitor(publish_robot_description=True,
                                publish_robot_description_semantic=True)
        .planning_pipelines(pipelines=['ompl'])
        .to_moveit_configs()
    )
    kinematics = config.robot_description_kinematics['robot_description_kinematics']
    apply_yaml(context, 'kinematics_file', kinematics)
    apply_yaml(context, 'joint_limits_file', config.joint_limits['robot_description_planning'])
    apply_yaml(context, 'ompl_file', config.planning_pipelines['ompl'])
    timeout = LaunchConfiguration('ik_timeout').perform(context).strip()
    if timeout:
        value = float(timeout)
        if not math.isfinite(value) or value <= 0:
            raise ValueError('ik_timeout must be a positive, finite number of seconds.')
        kinematics['panda_arm']['kinematics_solver_timeout'] = value

    controllers = str(share / 'config' / 'ros2_controllers.yaml')
    actions = [
        Node(package='moveit_ros_move_group', executable='move_group', name='move_group',
             output='screen', parameters=[config.to_dict()]),
        Node(package='rviz2', executable='rviz2', name='rviz2', output='log',
             condition=IfCondition(LaunchConfiguration('rviz')),
             arguments=['-d', str(share / 'launch' / 'moveit.rviz')],
             parameters=[config.robot_description, config.robot_description_semantic,
                         config.robot_description_kinematics, config.joint_limits,
                         config.planning_pipelines]),
        Node(package='tf2_ros', executable='static_transform_publisher',
             arguments=['--frame-id', 'world', '--child-frame-id', 'panda_link0']),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[config.robot_description]),
        Node(package='controller_manager', executable='ros2_control_node',
             parameters=[controllers],
             remappings=[('/controller_manager/robot_description', '/robot_description')]),
    ]
    for controller in ('joint_state_broadcaster', 'panda_arm_controller', 'panda_hand_controller'):
        actions.append(Node(package='controller_manager', executable='spawner',
                            arguments=[controller, '-c', '/controller_manager',
                                       '--param-file', controllers]))
    return actions


def generate_launch_description():
    default_ik = str(Path(__file__).parent / 'config' / 'panda_kinematics.yaml')
    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true', description='Start RViz'),
        DeclareLaunchArgument('kinematics_file', default_value=default_ik,
                              description='Absolute path to raw kinematics YAML'),
        DeclareLaunchArgument('joint_limits_file', default_value='',
                              description='Optional absolute path to raw joint limits YAML'),
        DeclareLaunchArgument('ompl_file', default_value='',
                              description='Optional absolute path to raw OMPL YAML'),
        DeclareLaunchArgument('ik_timeout', default_value='',
                              description='Optional Panda arm IK timeout in seconds; overrides YAML'),
        OpaqueFunction(function=launch_nodes),
    ])
