# Windows 11에서 Lyrical 호환 MoveIt 2 설치

RoboStack의 `ros-lyrical-moveit` 메타패키지와 관련 패키지를 설치합니다. ROS 2 Lyrical도 함께 설치하므로 공식 ROS 배포본을 먼저 설치할 필요가 없습니다. 검증된 버전은 MoveIt 2.15.2입니다.

[MoveIt Windows 안내](https://moveit.ai/install-moveit2/binary-windows/)는 RoboStack 바이너리를 안내하지만 명령 예제는 Humble입니다. 이 저장소는 [RoboStack Lyrical 패키지](https://robostack.github.io/lyrical.html)와 고정된 lock 파일을 사용합니다.

## 자동 설치

저장소 루트의 새 PowerShell에서:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component MoveIt
```

이 명령은 프로젝트 전용 Pixi를 준비하고 두 환경을 `--locked`로 설치한 뒤 Panda 예제로 Planning을 검사합니다.

| 환경 | 주요 구성 |
| --- | --- |
| `moveit` | ROS desktop, MoveIt 메타패키지, moveit_py, Servo, Panda 설정, ros2_controllers, SQLite warehouse |
| `moveit-setup` | Setup Assistant 2.15.2, Qt 6.12 |

OMPL, CHOMP, STOMP, Pilz 등은 메타패키지 의존성으로 설치됩니다. `moveit/pixi.lock`과 `moveit-setup/pixi.lock`이 정확한 빌드를 결정합니다.

## 환경이 분리되는 이유

공식 ROS 배포본은 Python 3.12이고 이 RoboStack 구성은 Python 3.14입니다. 기존 공식 설치 위에 파일을 복사하거나 `local_setup`을 겹쳐 적용하지 않습니다. MoveIt 작업에는 `start_moveit.cmd`를 사용합니다. [RoboStack도 다른 ROS 환경과의 혼합을 피하도록 안내합니다.](https://robostack.github.io/GettingStarted.html)

현재 Setup Assistant 바이너리는 Qt 6.12 심볼을 필요로 하지만 본 환경의 PyQt는 Qt 6.11.2를 요구합니다. 따라서 Setup Assistant 전용 환경을 만들었습니다. 본 환경에서 직접 Setup Assistant를 실행하면 시작 오류가 발생할 수 있으므로 `start_moveit_setup.cmd`를 사용합니다.

## RViz에서 Planning

`start_moveit.cmd`를 열고 실행합니다.

```bat
ros2 launch moveit_resources_panda_moveit_config demo.launch.py ros2_control_hardware_type:=mock_components
```

RViz의 MotionPlanning 패널에서 `panda_arm` 그룹을 선택하고 목표 상태를 지정한 후 `Plan`을 누릅니다. `Plan & Execute`는 예제의 가상 컨트롤러를 이용합니다. 실제 로봇 컨트롤러가 없어도 이 예제의 Planning과 가상 Execution을 사용할 수 있습니다. 종료는 터미널에서 Ctrl+C입니다.

깨끗한 기존 터미널에서 활성화할 수도 있습니다.

```bat
call C:\python_ws\ros2\activate_moveit.cmd
```

```powershell
. C:\python_ws\ros2\activate_moveit.ps1
```

자신의 로봇 설정을 만들려면 `start_moveit_setup.cmd`를 실행하고 생성 패키지를 `C:\python_ws\ros2` 아래 워크스페이스에 저장합니다. 생성한 설정 패키지를 사용하는 빌드·로봇 드라이버 설정은 별도 작업입니다.

## 자동 Planning 검증

설치 명령의 기본 검증은 아래 명령과 같습니다. 활성화된 MoveIt 터미널에서:

```bat
python C:\python_ws\ros2\moveit\verify_runtime.py --planning-only
```

검사는 localhost, ROS_DOMAIN_ID 179에서 RViz 없이 Panda 예제를 시작하고, `/plan_kinematic_path` 서비스를 호출합니다. 계획 성공과 복수의 궤적 점을 확인한 뒤 자신이 시작한 프로세스를 종료합니다. 예제에는 관절 상태를 제공하는 mock 드라이버가 포함되어 있으며 실제 하드웨어는 연결하지 않습니다.

처음 실행하는 설치 경로에서는 Python 또는 ROS 노드에 대한 Windows 방화벽 알림이 나타날 수 있습니다. 허용 버튼이 비활성화된 경우의 설명은 [ROS 2 문제 해결](ros2-installation.md)을 참고하십시오. 설치기는 시스템 방화벽이나 알림 설정을 변경하지 않습니다.

가상 Execution까지 검사하려면:

```bat
python C:\python_ws\ros2\moveit\verify_runtime.py
```

또는 설치 시 `-VerifyExecution`을 지정합니다. 최종 검사 결과는 `logs/moveit-runtime-verification.json`, 예제 로그는 `logs/moveit-panda-demo.log`에 기록됩니다. 기존 환경에서는 OMPL RRTConnect로 14개 경유점의 경로 생성과 가상 Execution을 검증했습니다. 경유점 수는 재실행 시 달라질 수 있습니다.

## Ubuntu apt 설치와의 차이

주요 메타패키지와 의존성을 설치한다는 목적은 같지만 Windows 바이너리의 모든 동작이 Ubuntu와 동일하지는 않습니다.

- `moveit_py`는 경로 생성 후 객체 해제/프로세스 종료 시 접근 위반 `0xC0000005`가 재현됩니다. 기본 검증에서 사용하지 않습니다. Python에서는 `moveit/verify_runtime.py`처럼 `rclpy`로 `move_group` 서비스·액션을 호출하는 방식을 사용할 수 있습니다.
- Setup Assistant는 별도 Qt 환경으로 시작해야 합니다. 시작과 실행 유지까지 확인했으며, 모든 설정 생성 화면의 동작을 검증한 것은 아닙니다. Qt signal 경고가 남아 있습니다.
- RViz OpenGL 초기화와 MotionPlanning 플러그인 로딩은 확인했습니다. 환경에 따라 그래픽 드라이버 설정이 추가로 필요할 수 있습니다.
- OMPL Planning을 검증했습니다. 다른 플래너는 설치와 로딩을 확인했으며, 실제 하드웨어 제어와 사용자 C++ 패키지 빌드는 별도 검증이 필요합니다.

`moveit/verify_planning.py`는 `moveit_py` 종료 충돌을 재현하는 진단용입니다. 설치 성공 검사로 사용하지 마십시오. 선택적 GUI 진단 `moveit/verify_gui.ps1`은 `Start-Process -Environment`를 사용하므로 PowerShell 7.4 이상이 필요합니다. 설치 스크립트와 일반 실행기는 Windows PowerShell 5.1에서 실행됩니다.

## 고정 환경 재설치와 업데이트

동일한 설치 명령을 다시 실행하면 lock 파일 기준으로 환경을 재사용합니다. 패키지 변경을 의도한 경우에만 `pixi.toml`과 lock을 함께 갱신하고 Planning 검증을 다시 수행하십시오. 두 Qt 환경을 합치거나 본 환경에서 무조건 `pixi update`를 실행하면 검증된 조합이 바뀝니다.

다운로드, `.pixi`, 빌드 산출물과 로그는 Git에 포함하지 않습니다. 재현에 필요한 manifest와 lock은 반드시 함께 커밋합니다.
