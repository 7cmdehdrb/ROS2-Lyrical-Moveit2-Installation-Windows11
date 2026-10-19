MoveIt 2 / ROS 2 Lyrical / Windows 11
설치 및 검증일: 2026-10-19 (Asia/Seoul)

설치 결과
- RoboStack Windows 바이너리: MoveIt 2.15.2, ROS 2 Lyrical
- 본 환경: C:\python_ws\ros2\moveit\.pixi\envs\default
- Python 3.14.8, ROS 패키지 390개, 전체 conda 패키지 761개
- ros-lyrical-desktop 및 ros-lyrical-moveit 메타패키지와 의존성 설치
- moveit_py, Servo, OMPL/CHOMP/STOMP/Pilz, RViz, ros2_controllers,
  Panda 예제, SQLite warehouse 추가 설치
- Setup Assistant: moveit-setup의 별도 환경, MoveIt 2.15.2 / Qt 6.12
- 두 환경의 pixi.lock에 설치 버전 고정

시작 방법
1. C:\python_ws\ros2\start_moveit.cmd 실행
2. 열린 터미널에서 Panda 예제 실행:
   ros2 launch moveit_resources_panda_moveit_config demo.launch.py ros2_control_hardware_type:=mock_components
3. RViz의 MotionPlanning 패널에서 panda_arm 그룹과 목표 상태를 선택하고
   Plan을 누릅니다. Plan & Execute는 가상 컨트롤러로 실행됩니다.
4. Ctrl+C로 종료합니다.

기존의 깨끗한 명령 프롬프트에서 활성화:
   call C:\python_ws\ros2\activate_moveit.cmd

기존의 깨끗한 PowerShell에서 활성화 (점과 공백 포함):
   . C:\python_ws\ros2\activate_moveit.ps1

Setup Assistant 시작:
   C:\python_ws\ros2\start_moveit_setup.cmd
생성하는 로봇 설정 패키지의 저장 위치도 C:\python_ws\ros2 아래로 지정하십시오.
Setup Assistant 전용 터미널이 필요하면 새 터미널에서 다음을 사용합니다:
   call C:\python_ws\ros2\activate_moveit_setup.cmd
   또는 PowerShell: . C:\python_ws\ros2\activate_moveit_setup.ps1

환경을 나눈 이유
기존 공식 ROS 2 설치(lyrical 폴더, Python 3.12)는 그대로 유지했습니다.
RoboStack 바이너리는 Python 3.14용이므로 기존 설치 위에 덮어쓰지 않고,
ROS 2와 MoveIt 의존성이 함께 해결된 별도 환경으로 구성했습니다.
MoveIt 작업에는 start_moveit.cmd를 사용하십시오. 기존 start_ros2.cmd는
원래 공식 ROS 2 환경을 시작합니다. 같은 터미널에서 환경을 섞지 마십시오.

현재 RoboStack Setup Assistant 바이너리는 Qt 6.12의 심볼을 요구하지만,
본 환경의 PyQt 패키지는 Qt 6.11.2를 요구합니다. 이를 해결하기 위해
Setup Assistant만 Qt 6.12 환경으로 분리했습니다. 본 환경에서 직접
setup_assistant를 실행하는 대신 start_moveit_setup.cmd를 사용하십시오.

검증 결과
- move_group 서비스의 OMPL / RRTConnect Planning 성공: 14개 경유점
- Panda 가상 컨트롤러 3개 active, ExecuteTrajectory 성공
- 실제 로봇이나 하드웨어 드라이버 연결 없이 mock_components로 검증
- RViz: OpenGL 4.6 초기화 및 MoveIt MotionPlanning 플러그인 로딩 확인
- 별도 환경의 Setup Assistant: 시작 후 12초 동안 실행 유지 확인
  (전체 설정 생성 절차를 끝까지 검증한 것은 아닙니다.)
- 명령 프롬프트 및 PowerShell 환경 활성화 확인
- 검증 프로세스는 종료했습니다.

알려진 제한
moveit_py는 Planning에 성공하지만 MoveItCpp 객체 해제/프로세스 종료 시
Windows 접근 위반(0xC0000005)이 재현됩니다. 정상 종료까지 검증된
move_group의 ROS 서비스/액션을 Python rclpy에서 호출하는 방식을 권합니다.
moveit\verify_runtime.py가 해당 방식의 작동 예제입니다.
moveit\verify_planning.py는 이 종료 충돌이 재현되는 진단 스크립트입니다.

Ubuntu의 apt 설치처럼 주요 바이너리 패키지와 의존성을 설치했지만,
위 Qt 환경 분리와 Python 바인딩 종료 문제 때문에 완전히 동일한 상태는
아닙니다. OMPL 경로 계획은 검증했으며 다른 플래너는 설치/로딩만 확인했습니다.
실제 하드웨어 제어, 사용자 로봇 모델, 사용자 C++ 패키지 빌드는 미검증입니다.
Setup Assistant의 Qt signal 경고와 RViz의 플러그인 경고가 남아 있습니다.

검증 재실행 (활성화된 MoveIt 터미널)
   python C:\python_ws\ros2\moveit\verify_runtime.py
이 검사는 localhost / ROS_DOMAIN_ID=179에서 Panda 예제를 시작하고
Planning 및 가상 Execution 후 자신이 시작한 프로세스를 정리합니다.

파일 위치
- 설치 안내: C:\python_ws\ros2\MOVEIT_README.txt
- 종합 결과: C:\python_ws\ros2\logs\moveit-installation-report.json
- Planning / 가상 Execution: logs\moveit-runtime-verification.json
- Python Planning / 종료 문제: logs\moveit-verification.json,
  logs\moveit-python-shutdown.json, logs\moveit-planning.log
- GUI 시작 검사: logs\moveit-gui-rviz2-verification.json,
  logs\moveit-gui-setup-assistant-verification.json
- 설치 명세: moveit\pixi.toml, moveit\pixi.lock,
  moveit-setup\pixi.toml, moveit-setup\pixi.lock
- 다운로드/의존성 캐시/임시 파일: downloads, .cache, tmp
- ROS 실행 로그/상태: logs, .ros
GUI 도구가 사용하는 사용자 프로필 설정 경로까지 모두 재지정한 것은 아닙니다.
중간 진단 로그에는 이전 패키지 조합의 실패 기록도 남아 있으므로
현재 설치 상태는 종합 결과와 위 최종 검증 파일을 기준으로 확인하십시오.

고정된 설치 상태 복원 (새 PowerShell에서)
   . C:\python_ws\ros2\env-local.ps1
   Set-Location C:\python_ws\ros2\moveit
   pixi install --locked
   Set-Location C:\python_ws\ros2\moveit-setup
   pixi install --locked

참고 문서
https://moveit.ai/install-moveit2/binary-windows/
https://robostack.github.io/lyrical.html
https://robostack.github.io/GettingStarted.html
