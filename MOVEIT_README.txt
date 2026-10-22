MoveIt 2 / ROS 2 Lyrical / Windows 11 / UR Planning
개정일: 2026-10-23 (Asia/Seoul)
상세 안내: docs/moveit-installation.md, docs/moveit-usage.md

필수 사전 조건
- 설치 전 Windows x64 CPython 3.12.x (3.12.3 이상)를 먼저 설치합니다.
- https://www.python.org/downloads/release/python-3123/
  Windows installer (64-bit)를 선택합니다.
- MoveIt만 설치하거나 -SkipVerification을 사용해도 Python 검사는 필수입니다.
- 부적합하면 다운로드 전에 중단하고 Python 설치 안내를 출력합니다.
- 이 사전 조건은 저장소 정책이며, 실행 시에는 Pixi의 별도 Python 3.14.8을 씁니다.

설치 (저장소 루트의 새 PowerShell):
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component MoveIt

가장 먼저 할 일: 사용할 때마다 start_moveit.cmd를 실행하십시오.
1. <your-workspace>\start_moveit.cmd를 엽니다.
2. 열린 CMD에서 is ready 메시지를 확인합니다.
3. 그 CMD 안에서 실행합니다:
   ros2 launch "<your-workspace>/examples/ur_planning.launch.py" ur_type:=ur5e
4. RViz의 Planning Group을 ur_manipulator로 선택하고 목표 자세를 지정해 Plan을 누릅니다.
5. Ctrl+C로 종료합니다.

<your-workspace>는 저장소 폴더의 실제 절대 경로로 치환합니다.
꺾쇠를 그대로 실행하지 마십시오. 새 터미널마다 환경 활성화가 필요합니다.
공식 ROS용 start_ros2.cmd에는 이 MoveIt / UR 패키지가 없습니다.
기존 CMD: call "<your-workspace>\activate_moveit.cmd"
기존 PowerShell: . '<your-workspace>\activate_moveit.ps1'

기본 구성
- RoboStack Lyrical / MoveIt 2.15.2
- ur_moveit_config 6.1.0 및 ur_description 4.3.1
- ur_type: ur3, ur5, ur10, ur3e, ur5e, ur7e, ur10e, ur12e, ur16e,
  ur8long, ur15, ur18, ur20, ur30
- 모델 변경 예: 위 launch 명령 끝의 ur_type:=ur5e를 ur_type:=ur20으로 변경
- 고정 관절 상태만 발행하며 가상/실제 로봇 드라이버와 실행 컨트롤러를 띄우지 않습니다.
- Execution은 비활성화입니다. Plan 성공만 필요하며 Execute는 지원하지 않습니다.
- 기본 UR 모델과 설정은 패키지에서 읽습니다. YAML override는 상세 가이드를 참고합니다.
- Setup Assistant는 Qt 호환성을 위해 별도 환경이며 start_moveit_setup.cmd로 시작합니다.

Planning 검증 (활성화된 MoveIt 터미널):
   python "<your-workspace>\moveit\verify_runtime.py" --ur-type ur20
기본 모델은 ur5e, localhost / ROS_DOMAIN_ID=179를 사용합니다.
실행 요청 없이 OMPL 성공 코드와 복수의 궤적 점을 확인합니다.
결과: logs/moveit-runtime-verification.json
모델별 로그: logs/moveit-<ur_type>-planning.log
--planning-only는 호환 옵션입니다. 생략해도 Planning만 검사합니다.
기존 설치기의 -VerifyExecution 옵션은 제거했습니다.

기존 바이너리 환경에서 moveit_py 종료 충돌이 관찰되어 기본 검증은
rclpy를 통해 move_group 서비스를 호출합니다. 실제 하드웨어 제어는 별도 구성입니다.
패키지 버전과 체크섬은 moveit/pixi.lock에 고정하며 설치 시 --locked를 사용합니다.
