# Windows 11에서 ROS 2 Lyrical과 MoveIt 2 설치

Windows 11 x64에서 검증한 ROS 2 Lyrical과 MoveIt 2.15.2 바이너리 설치를 재현하는 저장소입니다. 설치 스크립트는 필요한 파일을 프로젝트 내부로 다운로드하고, 고정된 의존성을 설치한 뒤 통신 또는 Planning을 검사합니다. 기존 바이너리 검증 기록은 2026-10-19 기준이며, UR 기본 구성과 Python 사전 조건은 2026-10-23에 개정했습니다.

## 0. 필수: Python부터 설치

> **설치 명령을 실행하기 전에 Windows x64 CPython 3.12.x(3.12.3 이상 패치 버전)를 반드시 설치하십시오.** Python이 없거나 3.11·3.13·3.14, 32비트 또는 ARM64 Python만 감지되면 설치를 거부합니다. 이 조건은 `ROS2`, `MoveIt`, `All`과 `-SkipVerification` 모두에 적용됩니다.

[Python 3.12.3 공식 다운로드](https://www.python.org/downloads/release/python-3123/)에서 **Windows installer (64-bit)**를 선택하고 Python Launcher도 설치합니다. 설치 후 **새 PowerShell**에서 확인합니다.

```powershell
py -3.12 -c "import sys, struct; print(sys.version); print(struct.calcsize('P') * 8)"
```

`3.12.x`와 `64`가 나와야 합니다. 설치기는 `py -3.12`, PATH의 `python.exe` / `python3.exe` 순서로 실제 버전·구현·아키텍처를 검사하며, Python을 대신 설치하지 않습니다. 자동 검색이 안 되면 설치 명령 끝에 `-PythonExecutable '<path-to-python312>\python.exe'`를 추가합니다. 명시한 Python이 부적합하면 다른 Python으로 대체하지 않습니다.

이 사전 조건은 **이 저장소의 설치 정책**입니다. 공식 ROS Windows 배포본의 런타임은 Python 3.12.3, RoboStack MoveIt의 런타임은 Python 3.14.8이며, 둘 다 Pixi가 별도로 설치합니다. 미리 설치한 Python을 MoveIt 환경에 덮어씌우거나 실행용으로 강제하지 마십시오.

## 1. 한 줄 설치

이 문서 전체에서 `<your-workspace>`는 **이 저장소를 clone한 폴더의 절대 경로**입니다. 꺾쇠까지 포함한 표기를 그대로 실행하지 말고 본인이 선택한 짧고 공백 없는 경로로 바꿉니다. `<path-to-python312>`도 실제 Python 설치 폴더로 바꿉니다.

Git과 위 Python을 설치한 새 PowerShell에서 준비합니다. 이미 저장소가 있다면 clone을 생략합니다.

```powershell
git clone https://github.com/7cmdehdrb/ROS2-Lyrical-Moveit2-Installation-Windows11.git '<your-workspace>'
cd '<your-workspace>'
```

설치 한 줄:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component All
```

각각 설치할 수도 있습니다.

```powershell
# 공식 ROS 2 Lyrical만 설치
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component ROS2

# MoveIt 2와 호환되는 RoboStack ROS 2 Lyrical을 함께 설치
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component MoveIt
```

## 2. 필수: 사용할 때마다 전용 터미널 먼저 열기

> **설치 완료만으로 일반 터미널에서 ROS를 사용할 수 있는 것은 아닙니다.** `ros2`, `rviz2`, `import rclpy`를 사용하는 Python 파일을 실행하기 **전에 반드시** 아래 실행기를 열고, **그 실행기가 연 터미널 안에서** 명령을 입력하십시오. 새 터미널을 추가하거나 PC를 재시작하면 다시 활성화해야 합니다.

1. 공식 ROS 작업: 탐색기에서 `<your-workspace>\start_ros2.cmd`를 실행합니다.
2. UR / MoveIt 작업: `<your-workspace>\start_moveit.cmd`를 실행합니다.
3. 열린 터미널에서 `is ready` 메시지를 확인한 뒤 `ros2 --help`를 실행합니다.

실행기는 Python, DLL, ROS 패키지 검색 경로를 **현재 터미널에만** 설정합니다. 시스템의 영구 PATH는 설정하지 않습니다. talker와 listener처럼 터미널이 두 개 필요하면 **각각** 실행기를 열어야 합니다. 기존 CMD의 `call activate_*.cmd`와 PowerShell의 dot-source 방식은 [환경 활성화 안내](docs/ros2-usage.md#터미널마다-환경-활성화)를 참고하십시오.

`MoveIt` 설치는 `ROS2` 설치를 먼저 실행할 필요가 없습니다. `All`은 목적이 다른 두 ROS 환경을 만듭니다. 설치 후에는 목적에 맞는 실행기를 사용합니다.

| 목적 | 설치 위치 | 실행기 |
| --- | --- | --- |
| 공식 ROS 2 Lyrical, Python 3.12.3 | `lyrical/` | `start_ros2.cmd` |
| MoveIt 2.15.2와 RoboStack Lyrical, Python 3.14.8 | `moveit/.pixi/` | `start_moveit.cmd` |
| Setup Assistant 2.15.2와 Qt 6.12 | `moveit-setup/.pixi/` | `start_moveit_setup.cmd` |

기존 공식 배포본과 RoboStack은 Python 및 바이너리 구성이 달라 같은 터미널에서 혼합하면 안 됩니다. Setup Assistant는 현재 패키지의 Qt 의존성 충돌 때문에 별도 환경을 사용합니다.

## 설치 조건과 동작

- Windows 11 x64, 64비트 Windows PowerShell 5.1 이상, 인터넷 연결이 필요합니다. 기본 제공 `curl.exe`와 `tar.exe`를 사용합니다.
- 공백·특수문자가 없는 짧은 쓰기 가능한 경로를 사용합니다. `<your-workspace>`를 실제 경로로 치환합니다.
- 기존 ROS, Conda, venv가 활성화되지 않은 새 터미널에서 설치합니다.
- 두 배포본과 다운로드 캐시를 보관하므로 여유 공간은 약 25 GB 이상을 권장합니다. 선택한 구성과 패키지 캐시에 따라 사용량이 달라집니다.
- 설치 스크립트는 시스템 Python이나 영구 PATH를 바꾸지 않습니다. 실행 정책 예외는 해당 PowerShell 프로세스에만 적용합니다.
- Visual Studio 설치와 사용자 C++ 패키지 빌드는 자동화 범위에 포함하지 않습니다. 빌드 도구 준비는 [ROS 2 가이드](docs/ros2-installation.md)를 확인합니다.

Pixi 및 공식 ROS ZIP의 URL과 SHA-256은 `config/sources.json`에 고정했습니다. MoveIt 환경의 정확한 패키지 URL·버전·해시는 두 `pixi.lock`에 기록되어 있으며, 설치 시 `--locked`를 사용합니다. 최신 버전을 자동으로 선택하지 않습니다.

설치 명령은 다시 실행할 수 있습니다. 검증된 캐시와 기존 환경을 재사용합니다. 기존 공식 ROS의 manifest/lock이 고정 배포본과 다르면 덮어쓰지 않고 중단합니다. 설치 위치는 이 스크립트가 있는 폴더입니다. 설치 후 폴더를 옮기면 절대 경로가 깨질 수 있으므로 새 위치에서 다시 설치하십시오.

## 검증과 알려진 제한

기본 설치 검증은 공식 ROS의 C++ talker → Python listener 송수신과 UR5e의 OMPL Planning입니다. MoveIt 기본 패키지는 `ur_moveit_config`와 `ur_description`입니다. `ur_type`으로 UR3부터 UR20 등 패키지가 제공하는 모델을 선택합니다. 가상·실제 로봇 드라이버, controller manager, 실행 컨트롤러는 시작하지 않습니다. 고정 관절 상태만 발행하며, **Plan 성공**이 검사 기준입니다. Execution은 비활성화되어 있습니다.

`start_moveit.cmd`로 연 터미널에서:

```bat
ros2 launch "<your-workspace>/examples/ur_planning.launch.py" ur_type:=ur20
```

RViz에서 `ur_manipulator` 그룹을 선택하고 **Plan**을 누릅니다. 모델 선택과 YAML 설정은 [MoveIt 사용법](docs/moveit-usage.md)을 참고합니다.

```powershell
# 패키지 설치만 수행
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component All -SkipVerification
```

검증에 실패하면 설치 명령도 실패 코드로 종료됩니다. 이 경우 이미 설치된 파일은 남습니다. 결과는 `logs/install-*.json`, `logs/verification.json`, `logs/moveit-runtime-verification.json`에서 확인합니다. `-SkipVerification` 결과는 런타임 정상 작동을 의미하지 않습니다.

새 경로에서 자동 통신 검증을 실행하면 Windows 방화벽 알림이 나타날 수 있습니다. 패키지 설치만 먼저 하려면 `-SkipVerification`을 사용하고, 실행 파일에 필요한 네트워크 규칙은 관리자와 확인하십시오. 허용 버튼 비활성화에 대한 설명은 [ROS 2 문제 해결](docs/ros2-installation.md)에 있습니다.

기존 환경에서는 `moveit_py`가 Planning 성공 후 종료 시 `0xC0000005` 충돌이 재현됩니다. 검증된 Python 사용 방식은 `rclpy`에서 `move_group` 서비스·액션을 호출하는 것입니다. `moveit/verify_runtime.py`가 해당 예제입니다. 상세 제한과 RViz 사용법은 [MoveIt 가이드](docs/moveit-installation.md)에 있습니다.

## Git에 포함하는 파일

소스 스크립트, 문서, 다운로드 명세, `pixi.toml`, `pixi.lock`을 포함합니다. `.gitignore`는 다운로드·설치 바이너리·캐시·빌드 산출물·로그를 제외합니다. lock 파일은 바이너리가 아닌 재현성 메타데이터이므로 추적합니다.

현재 LFS로 관리할 파일은 없습니다. 대용량 의존성은 공식 배포처에서 재다운로드할 수 있으므로 Git과 LFS 모두에 넣지 않습니다. 향후 외부에서 재확보하기 어려운 필수 원본 자산만 파일별로 검토하여 LFS에 추가합니다.

커밋 전에 다음 검사로 10 MiB 초과 파일과 이미 추적된 ignore 대상 파일을 확인합니다.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-git-files.ps1
git add .
git diff --cached --stat
git status --short
```

`.gitignore`는 이미 커밋한 대용량 파일을 기록에서 제거하지 않습니다. 이 저장소의 최초 점검 시 추적된 파일은 없었습니다. 다운로드 파일을 `git add -f`로 추가하지 마십시오.

## 상세 가이드

- [공식 ROS 2 Lyrical 설치](docs/ros2-installation.md)
- [MoveIt 2 설치와 Planning](docs/moveit-installation.md)
- [ROS 2 기본 사용: run, launch, topic, RViz](docs/ros2-usage.md)
- [일반 Python 파일을 ROS 2 환경에서 실행](docs/python-scripts.md)
- [MoveIt 실행과 kinematics·joint limits·OMPL YAML 변경](docs/moveit-usage.md)
- 텍스트 요약: `README.txt`, `MOVEIT_README.txt`

설치 방식은 [ROS 2 Windows 바이너리 안내](https://docs.ros.org/en/lyrical/Get-Started/Installation/Windows-Install-Binary.html), [MoveIt Windows 바이너리 안내](https://moveit.ai/install-moveit2/binary-windows/), [RoboStack 시작 안내](https://robostack.github.io/GettingStarted.html)를 참고했습니다.
