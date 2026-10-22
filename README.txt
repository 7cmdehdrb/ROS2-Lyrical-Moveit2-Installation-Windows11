ROS 2 Lyrical / Windows 11 설치 및 실행 요약
개정일: 2026-10-23 (Asia/Seoul)
상세 안내: README.md, docs/ros2-installation.md, docs/ros2-usage.md

0. 반드시 Python을 먼저 설치하십시오.
   Windows x64 CPython 3.12.x (3.12.3 이상 패치 버전)가 필요합니다.
   Python 없음 / 3.11, 3.13, 3.14 / 32비트 / ARM64만 감지되면 설치를 거부합니다.
   다운로드: https://www.python.org/downloads/release/python-3123/
   Windows installer (64-bit)를 선택하고 Python Launcher도 설치합니다.
   새 PowerShell에서 확인:
   py -3.12 -c "import sys, struct; print(sys.version); print(struct.calcsize('P') * 8)"
   3.12.x와 64가 나와야 합니다.

1. Git으로 저장소를 준비하고 저장소 루트의 새 PowerShell에서 한 줄 설치:
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component All
   공식 ROS만 설치하려면 -Component ROS2, MoveIt만 설치하려면 -Component MoveIt.
   모든 구성과 -SkipVerification에서 Python 사전 검사는 필수입니다.
   자동 감지가 안 되면 -PythonExecutable '<path-to-python312>\python.exe'를 추가합니다.
   <path-to-python312>는 Python 설치 폴더로 바꿉니다.

2. 사용하기 전에 매번 전용 터미널을 먼저 여십시오. 가장 기본적인 필수 절차입니다.
   공식 ROS: <your-workspace>\start_ros2.cmd
   UR / MoveIt: <your-workspace>\start_moveit.cmd
   Setup Assistant: <your-workspace>\start_moveit_setup.cmd
   <your-workspace>는 이 저장소 폴더의 실제 절대 경로로 바꿉니다.
   꺾쇠가 포함된 표기를 그대로 명령에 입력하지 마십시오.

3. 실행기가 연 터미널 안에서만 ROS/Python 명령을 실행합니다.
   ros2 --help
   ros2 pkg list
   talker와 listener는 전용 터미널을 각각 열어서 실행:
   ros2 run demo_nodes_cpp talker
   ros2 run demo_nodes_py listener

새 창을 추가하거나 PC를 재시작하면 다시 활성화해야 합니다.
설치나 다른 창의 활성화가 일반 터미널에 전파되지 않습니다.
현재 CMD에서 활성화: call "<your-workspace>\activate_ros2.cmd"
현재 PowerShell에서 활성화: . '<your-workspace>\activate_ros2.ps1'
PowerShell에서 CMD 실행기를 열었다면 그 CMD 안에서 작업합니다.
두 ROS 환경을 같은 터미널에 겹쳐 적용하지 않습니다.

사전 Python 설치는 이 저장소의 정책입니다. 실행용 Python은 Pixi가 따로 설치합니다.
공식 ROS 런타임: lyrical/.pixi의 Python 3.12.3
RoboStack MoveIt 런타임: moveit/.pixi의 Python 3.14.8
시스템 Python과 영구 PATH는 변경하지 않습니다.

공식 ROS 자동 검증 재실행 (start_ros2.cmd로 연 터미널):
   python "<your-workspace>\verify_install.py"
결과: logs/verification.json, logs/install-*.json
다운로드/의존성/로그는 Git에 포함하지 않습니다.
