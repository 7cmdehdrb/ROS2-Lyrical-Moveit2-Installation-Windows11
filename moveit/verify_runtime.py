"""Check UR planning through move_group without any robot driver or execution."""
import json
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import runpy
import psutil

os.environ['ROS_DOMAIN_ID'] = '179'
os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
os.environ.setdefault('RMW_IMPLEMENTATION', 'rmw_fastrtps_cpp')
import rclpy
from moveit_msgs.srv import GetMotionPlan
from moveit_msgs.msg import Constraints, JointConstraint
from sensor_msgs.msg import JointState

ROOT = Path(__file__).resolve().parent.parent
launch = runpy.run_path(str(ROOT / 'examples' / 'ur_planning.launch.py'))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ur-type', choices=launch['UR_TYPES'], default='ur5e')
parser.add_argument('--planning-only', action='store_true', help='Compatibility option; planning is always the only check.')
args = parser.parse_args()
report = {'passed': False, 'robot': args.ur_type, 'hardware': 'none', 'ros_domain_id': 179,
          'execution_requested': False}
(ROOT / 'logs').mkdir(exist_ok=True)
log_path = ROOT / 'logs' / f'moveit-{args.ur_type}-planning.log'
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
            [ros2, 'launch', str(ROOT / 'examples' / 'ur_planning.launch.py'),
             f'ur_type:={args.ur_type}', 'rviz:=false'],
            stdout=output, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW,
        )
        rclpy.init()
        node = rclpy.create_node('moveit_binary_install_probe')
        planner = node.create_client(GetMotionPlan, '/plan_kinematic_path')
        assert planner.wait_for_service(timeout_sec=45), 'move_group planning service unavailable'
        joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
                       'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
        current = {}

        def receive_state(msg):
            current.update(zip(msg.name, msg.position))

        subscription = node.create_subscription(JointState, '/joint_states', receive_state, 10)
        deadline = time.monotonic() + 30
        while not all(name in current for name in joint_names):
            assert proc.poll() is None, 'UR launch exited before publishing joint states'
            assert time.monotonic() < deadline, 'UR joint states unavailable'
            rclpy.spin_once(node, timeout_sec=0.5)
        report['joint_names'] = joint_names

        req = GetMotionPlan.Request()
        req.motion_plan_request.group_name = 'ur_manipulator'
        req.motion_plan_request.pipeline_id = 'ompl'
        req.motion_plan_request.planner_id = 'RRTConnectkConfigDefault'
        req.motion_plan_request.num_planning_attempts = 1
        req.motion_plan_request.allowed_planning_time = 5.0
        req.motion_plan_request.max_velocity_scaling_factor = 0.2
        req.motion_plan_request.max_acceleration_scaling_factor = 0.2
        req.motion_plan_request.start_state.is_diff = False
        req.motion_plan_request.start_state.joint_state.name = joint_names
        req.motion_plan_request.start_state.joint_state.position = [current[name] for name in joint_names]
        constraint = Constraints()
        constraint.name = 'near_home_pose'
        for name in joint_names:
            joint = JointConstraint()
            joint.joint_name = name
            joint.position = current[name] + (0.25 if name == 'shoulder_pan_joint' else 0.0)
            joint.tolerance_above = joint.tolerance_below = 0.001
            joint.weight = 1.0
            constraint.joint_constraints.append(joint)
        req.motion_plan_request.goal_constraints = [constraint]
        plan = response(planner.call_async(req)).motion_plan_response
        report['planning_error_code'] = plan.error_code.val
        report['trajectory_points'] = len(plan.trajectory.joint_trajectory.points)
        assert plan.error_code.val == 1 and report['trajectory_points'] > 1, 'Native motion planning failed'

        report['passed'] = True
except Exception as error:
    report['error'] = str(error)
    raise
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
