"""Check the packaged Panda demo using ROS services and mock controllers."""
import json
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import psutil

os.environ['ROS_DOMAIN_ID'] = '179'
os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
os.environ.setdefault('RMW_IMPLEMENTATION', 'rmw_fastrtps_cpp')
import rclpy
from rclpy.action import ActionClient
from moveit_msgs.srv import GetMotionPlan
from moveit_msgs.msg import Constraints, JointConstraint
from moveit_msgs.action import ExecuteTrajectory
from controller_manager_msgs.srv import ListControllers

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--planning-only', action='store_true', help='Validate planning without executing the trajectory.')
args = parser.parse_args()
report = {'passed': False, 'hardware': 'mock_components', 'ros_domain_id': 179,
          'execution_requested': not args.planning_only}
log_path = ROOT / 'logs' / 'moveit-panda-demo.log'
ros2 = shutil.which('ros2')
node = None
proc = None

def response(future, timeout=30):
    rclpy.spin_until_future_complete(node, future, timeout_sec=timeout)
    assert future.done(), 'ROS service/action timed out'
    return future.result()

try:
    with log_path.open('w', encoding='utf-8') as output:
        proc = subprocess.Popen(
            [ros2, 'launch', str(ROOT / 'moveit' / 'panda_headless.launch.py'), 'ros2_control_hardware_type:=mock_components'],
            stdout=output, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW,
        )
        rclpy.init()
        node = rclpy.create_node('moveit_binary_install_probe')
        planner = node.create_client(GetMotionPlan, '/plan_kinematic_path')
        assert planner.wait_for_service(timeout_sec=45), 'move_group planning service unavailable'
        controllers = node.create_client(ListControllers, '/controller_manager/list_controllers')
        assert controllers.wait_for_service(timeout_sec=30), 'mock controller manager unavailable'
        deadline = time.monotonic() + 35
        while True:
            controller_list = response(controllers.call_async(ListControllers.Request()))
            states = {c.name: c.state for c in controller_list.controller}
            if all(states.get(name) == 'active' for name in ['panda_arm_controller', 'panda_hand_controller', 'joint_state_broadcaster']):
                break
            assert time.monotonic() < deadline, states
            time.sleep(1)
        report['controllers'] = states

        req = GetMotionPlan.Request()
        req.motion_plan_request.group_name = 'panda_arm'
        req.motion_plan_request.pipeline_id = 'ompl'
        req.motion_plan_request.planner_id = 'RRTConnectkConfigDefault'
        req.motion_plan_request.num_planning_attempts = 1
        req.motion_plan_request.allowed_planning_time = 5.0
        req.motion_plan_request.max_velocity_scaling_factor = 0.2
        req.motion_plan_request.max_acceleration_scaling_factor = 0.2
        req.motion_plan_request.start_state.is_diff = True
        constraint = Constraints()
        constraint.name = 'safe_near_ready_pose'
        for i, value in enumerate([0.3, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785], 1):
            joint = JointConstraint()
            joint.joint_name = f'panda_joint{i}'
            joint.position = value
            joint.tolerance_above = joint.tolerance_below = 0.001
            joint.weight = 1.0
            constraint.joint_constraints.append(joint)
        req.motion_plan_request.goal_constraints = [constraint]
        plan = response(planner.call_async(req)).motion_plan_response
        report['planning_error_code'] = plan.error_code.val
        report['trajectory_points'] = len(plan.trajectory.joint_trajectory.points)
        assert plan.error_code.val == 1 and report['trajectory_points'] > 1, 'Native motion planning failed'

        if not args.planning_only:
            executor = ActionClient(node, ExecuteTrajectory, '/execute_trajectory')
            assert executor.wait_for_server(timeout_sec=15)
            goal = ExecuteTrajectory.Goal()
            goal.trajectory = plan.trajectory
            handle = response(executor.send_goal_async(goal))
            assert handle.accepted, 'Mock execution goal rejected'
            execution = response(handle.get_result_async(), timeout=40)
            report['execution_error_code'] = execution.result.error_code.val
            assert execution.result.error_code.val == 1, 'Mock trajectory execution failed'
        report['passed'] = True
finally:
    if node is not None:
        node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
    if proc is not None:
        try:
            children = psutil.Process(proc.pid).children(recursive=True)
        except psutil.NoSuchProcess:
            children = []
        for child in reversed(children):
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        if proc.poll() is None:
            proc.terminate()
        proc.wait(timeout=10)
        _, alive = psutil.wait_procs(children, timeout=10)
        for child in alive:
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass
    report['demo_log'] = str(log_path)
    (ROOT / 'logs' / 'moveit-runtime-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)
