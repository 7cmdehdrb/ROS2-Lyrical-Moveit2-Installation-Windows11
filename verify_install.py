"""Verify the installed ROS CLI and C++ -> Python DDS communication."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil

# Preserve failure diagnostics on Windows consoles using a legacy code page.
sys.stdout.reconfigure(errors='backslashreplace')
sys.stderr.reconfigure(errors='backslashreplace')

ROOT = Path(__file__).resolve().parent
ROS = ROOT / 'lyrical'
LOGS = ROOT / 'logs'
LOGS.mkdir(exist_ok=True)
env = os.environ.copy()
env['ROS_DOMAIN_ID'] = '177'
env['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
env['PYTHONUNBUFFERED'] = '1'
env['RMW_IMPLEMENTATION'] = 'rmw_fastrtps_cpp'

import rclpy
from rclpy.utilities import get_rmw_implementation_identifier

cli = [str(ROS / 'Scripts' / 'ros2.exe')]
help_result = subprocess.run(cli + ['--help'], env=env, capture_output=True, text=True, timeout=30)
assert help_result.returncode == 0, help_result.stderr
(LOGS / 'ros2-help.txt').write_text(help_result.stdout, encoding='utf-8')
packages_result = subprocess.run(cli + ['pkg', 'list'], env=env, capture_output=True, text=True, timeout=30)
assert packages_result.returncode == 0, packages_result.stderr
(LOGS / 'ros2-packages.txt').write_text(packages_result.stdout, encoding='utf-8')
packages = packages_result.stdout.splitlines()
assert {'demo_nodes_cpp', 'demo_nodes_py', 'rclpy', 'rclcpp'}.issubset(packages)

processes = []
try:
    with (LOGS / 'listener.log').open('w', encoding='utf-8') as listener_log, (LOGS / 'talker.log').open('w', encoding='utf-8') as talker_log:
        listener = subprocess.Popen(
            cli + ['run', 'demo_nodes_py', 'listener'],
            env=env, stdout=listener_log, stderr=subprocess.STDOUT,
        )
        processes.append(listener)
        talker = subprocess.Popen(
            cli + ['run', 'demo_nodes_cpp', 'talker'],
            env=env, stdout=talker_log, stderr=subprocess.STDOUT,
        )
        processes.append(talker)
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            time.sleep(1)
            if listener.poll() is not None or talker.poll() is not None:
                break
            received = (LOGS / 'listener.log').read_text(encoding='utf-8', errors='replace')
            if received.count('I heard:') >= 3:
                break
finally:
    children = []
    for proc in processes:
        try:
            children.extend(psutil.Process(proc.pid).children(recursive=True))
        except psutil.NoSuchProcess:
            pass
    for child in reversed(children):
        try:
            child.terminate()
        except psutil.NoSuchProcess:
            pass
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
    for proc in processes:
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
    _, alive = psutil.wait_procs(children, timeout=10)
    for child in alive:
        try:
            child.kill()
        except psutil.NoSuchProcess:
            pass

sent = (LOGS / 'talker.log').read_text(encoding='utf-8', errors='replace')
received = (LOGS / 'listener.log').read_text(encoding='utf-8', errors='replace')
result = {
    'ros_distro': os.environ.get('ROS_DISTRO'),
    'python': sys.version,
    'python_executable': sys.executable,
    'rmw': get_rmw_implementation_identifier(),
    'package_count': len(packages),
    'cli_help_passed': help_result.returncode == 0,
    'launch_method': 'ros2 run demo_nodes_cpp talker / ros2 run demo_nodes_py listener',
    'cpp_published_messages': sent.count('Publishing:'),
    'python_received_messages': received.count('I heard:'),
    'test_domain_id': 177,
    'test_discovery_range': 'LOCALHOST',
    'builtin_transports': env.get('FASTDDS_BUILTIN_TRANSPORTS'),
}
result['passed'] = result['cpp_published_messages'] >= 3 and result['python_received_messages'] >= 3 and result['ros_distro'] == 'lyrical'
(LOGS / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
if not result['passed']:
    print('TALKER:', sent)
    print('LISTENER:', received)
    raise SystemExit(1)
