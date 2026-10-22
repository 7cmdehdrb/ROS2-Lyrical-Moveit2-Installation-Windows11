# Windows 11에서 Lyrical 호환 MoveIt 2 설치

RoboStack의 `ros-lyrical-moveit` 메타패키지와 관련 패키지를 설치합니다. ROS 2 Lyrical도 함께 설치하므로 공식 ROS 배포본을 먼저 설치할 필요가 없습니다. 검증된 버전은 MoveIt 2.15.2입니다.

[MoveIt Windows 안내](https://moveit.ai/install-moveit2/binary-windows/)는 RoboStack 바이너리를 안내하지만 명령 예제는 Humble입니다. 이 저장소는 [RoboStack Lyrical 패키지](https://robostack.github.io/lyrical.html)와 고정된 lock 파일을 사용합니다.

## 필수 사전 준비와 실행 순서

> **설치 전에 Windows x64 CPython 3.12.x(3.12.3 이상)를 반드시 설치하십시오.** MoveIt만 설치해도 이 저장소의 사전 검사를 통과해야 합니다. Python이 없거나 버전·아키텍처가 다르면 다운로드 전에 중단하고 설치 주소를 표시합니다. `-SkipVerification`으로 우회할 수 없습니다. [Python 설치와 감지 방법](../README.md#0-필수-python부터-설치)을 먼저 확인하십시오.

사전 설치한 Python과 MoveIt에서 사용할 Python은 구분합니다. 이 RoboStack lock은 Python 3.14.8을 별도로 공급합니다. 시스템 Python에 `pip install`하여 ROS 모듈을 맞추지 않습니다.

`<your-workspace>`는 저장소 폴더의 실제 절대 경로로 치환합니다.

## 자동 설치

저장소 루트의 새 PowerShell에서:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component MoveIt
```

이 명령은 프로젝트 전용 Pixi를 준비하고 두 환경을 `--locked`로 설치한 뒤 UR5e로 Planning을 검사합니다.

| 환경 | 주요 구성 |
| --- | --- |
| `moveit` | ROS desktop, MoveIt 메타패키지, moveit_py, Servo, ur_moveit_config 6.1.0, ur_description 4.3.1, joint_state_publisher, SQLite warehouse |
| `moveit-setup` | Setup Assistant 2.15.2, Qt 6.12 |

OMPL, CHOMP, STOMP, Pilz 등은 메타패키지 의존성으로 설치됩니다. `moveit/pixi.lock`과 `moveit-setup/pixi.lock`이 정확한 빌드를 결정합니다.

## 환경이 분리되는 이유

공식 ROS 배포본은 Python 3.12이고 이 RoboStack 구성은 Python 3.14입니다. 기존 공식 설치 위에 파일을 복사하거나 `local_setup`을 겹쳐 적용하지 않습니다. MoveIt 작업에는 `start_moveit.cmd`를 사용합니다. [RoboStack도 다른 ROS 환경과의 혼합을 피하도록 안내합니다.](https://robostack.github.io/GettingStarted.html)

현재 Setup Assistant 바이너리는 Qt 6.12 심볼을 필요로 하지만 본 환경의 PyQt는 Qt 6.11.2를 요구합니다. 따라서 Setup Assistant 전용 환경을 만들었습니다. 본 환경에서 직접 Setup Assistant를 실행하면 시작 오류가 발생할 수 있으므로 `start_moveit_setup.cmd`를 사용합니다.

## 필수: MoveIt 터미널 먼저 열기

**사용할 때마다 `<your-workspace>\start_moveit.cmd`를 먼저 실행하십시오.** `is ready`가 표시된 그 CMD 안에서만 아래 명령을 실행합니다. 다른 새 터미널에도 활성화가 필요합니다. 공식 ROS용 `start_ros2.cmd`는 이 MoveIt 패키지를 제공하지 않습니다.

```bat
ros2 launch "<your-workspace>/examples/ur_planning.launch.py" ur_type:=ur5e
```

RViz의 MotionPlanning에서 `ur_manipulator` 그룹과 목표 자세를 선택한 뒤 **Plan**을 누릅니다. `ur_type:=ur3` 또는 `ur_type:=ur20` 등으로 모델을 바꿉니다. [전체 모델과 설정 인수](moveit-usage.md)를 확인하십시오.

이 launch는 UR 패키지의 모델·설정을 로딩하고 고정 관절 상태를 발행합니다. 가상 로봇 드라이버와 실행 컨트롤러는 띄우지 않으며 **Execution은 비활성화**합니다. Execute 실패 여부는 설치 성공 기준에 포함하지 않습니다. 종료는 Ctrl+C입니다.

기존의 깨끗한 CMD에서는 다음으로 활성화할 수도 있습니다.

```bat
call "<your-workspace>\activate_moveit.cmd"
```

PowerShell에서는:

```powershell
. '<your-workspace>\activate_moveit.ps1'
```

환경 활성화는 Python·DLL·ROS 패키지 경로를 현재 터미널에 적용합니다. 일반 터미널에서 `ros2`가 없거나 `rclpy` import가 실패하면 먼저 활성화를 확인합니다.

자신의 로봇 설정을 만들 때는 `start_moveit_setup.cmd`를 사용합니다. UR 기본 Planning에는 Setup Assistant로 설정을 다시 생성할 필요가 없습니다.

## 자동 Planning 검증

활성화된 MoveIt 터미널에서:

```bat
python "<your-workspace>\moveit\verify_runtime.py"
python "<your-workspace>\moveit\verify_runtime.py" --ur-type ur20
```

기본값은 UR5e입니다. 검사는 localhost, ROS_DOMAIN_ID 179에서 RViz 없이 Planning 서버를 시작하고 6개 관절 상태를 기다린 뒤 `/plan_kinematic_path`를 호출합니다. OMPL 성공 코드 `1`과 복수의 궤적 점을 확인하고 자신이 시작한 프로세스를 종료합니다. 드라이버·컨트롤러 대기나 궤적 실행 요청은 없습니다.

`logs/moveit-runtime-verification.json`에 마지막 검사 결과를, `logs/moveit-<ur_type>-planning.log`에 모델별 실행 로그를 저장합니다. `--planning-only`는 기존 명령 호환용이며, 생략해도 항상 Planning만 검사합니다. 이전 `-VerifyExecution` 설치 옵션은 제거했습니다.

처음 실행하는 설치 경로에서는 Windows 방화벽 알림이 나타날 수 있습니다. [ROS 2 문제 해결](ros2-installation.md)을 참고하십시오. 설치기는 시스템 방화벽 정책을 변경하지 않습니다.

## Ubuntu apt 설치와의 차이

주요 메타패키지와 의존성을 설치한다는 목적은 같지만 Windows 바이너리의 모든 동작이 Ubuntu와 동일하지는 않습니다.

- 기존 바이너리 검증에서 `moveit_py`는 경로 생성 후 객체 해제/프로세스 종료 시 접근 위반 `0xC0000005`가 재현됩니다. 기본 검증에서 사용하지 않습니다. Python에서는 `moveit/verify_runtime.py`처럼 `rclpy`로 `move_group` 서비스·액션을 호출하는 방식을 사용할 수 있습니다.
- Setup Assistant는 별도 Qt 환경으로 시작해야 합니다. 기존 2026-10-19 환경에서 시작과 실행 유지까지 확인했으며, 모든 설정 생성 화면의 동작을 검증한 것은 아닙니다. Qt signal 경고가 남아 있습니다.
- 기존 2026-10-19 환경에서 RViz OpenGL 초기화와 MotionPlanning 플러그인 로딩을 확인했습니다. 환경에 따라 그래픽 드라이버 설정이 추가로 필요할 수 있습니다.
- 2026-10-23에 지원 UR 14개 모델 전체의 headless OMPL Planning을 검증했습니다. 다른 플래너는 기존 환경에서 설치와 로딩을 확인했으며, 실제 하드웨어 제어와 사용자 C++ 패키지 빌드는 별도 검증이 필요합니다.

`moveit/verify_planning.py`는 같은 UR Planning 검사를 실행하는 호환 진입점입니다. 선택적 GUI 진단 `moveit/verify_gui.ps1`은 `Start-Process -Environment`를 사용하므로 PowerShell 7.4 이상이 필요합니다. 설치 스크립트와 일반 실행기는 Windows PowerShell 5.1에서 실행됩니다.

## 고정 환경 재설치와 업데이트

동일한 설치 명령을 다시 실행하면 lock 파일 기준으로 환경을 재사용합니다. 패키지 변경을 의도한 경우에만 `pixi.toml`과 lock을 함께 갱신하고 Planning 검증을 다시 수행하십시오. 두 Qt 환경을 합치거나 본 환경에서 무조건 `pixi update`를 실행하면 검증된 조합이 바뀝니다.

다운로드, `.pixi`, 빌드 산출물과 로그는 Git에 포함하지 않습니다. 재현에 필요한 manifest와 lock은 반드시 함께 커밋합니다.
