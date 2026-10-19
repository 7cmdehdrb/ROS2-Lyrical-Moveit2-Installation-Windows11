# Windows 11에서 ROS 2 Lyrical과 MoveIt 2 설치

Windows 11 x64에서 검증한 ROS 2 Lyrical과 MoveIt 2.15.2 바이너리 설치를 재현하는 저장소입니다. 설치 스크립트는 필요한 파일을 프로젝트 내부로 다운로드하고, 고정된 의존성을 설치한 뒤 통신 또는 Planning을 검사합니다. 검증 기준일은 2026-10-19입니다.

## 빠른 설치

Git이 설치된 새 PowerShell에서 저장소를 짧은 경로에 준비합니다. 이미 이 저장소가 있다면 clone을 생략합니다.

```powershell
git clone https://github.com/7cmdehdrb/ROS2-Lyrical-Moveit2-Installation-Windows11.git C:\python_ws\ros2
cd C:\python_ws\ros2
```

공식 ROS 2와 RoboStack MoveIt 환경을 모두 설치하는 명령 한 줄:

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

`MoveIt` 설치는 `ROS2` 설치를 먼저 실행할 필요가 없습니다. `All`은 목적이 다른 두 ROS 환경을 만듭니다. 설치 후에는 목적에 맞는 실행기를 사용합니다.

| 목적 | 설치 위치 | 실행기 |
| --- | --- | --- |
| 공식 ROS 2 Lyrical, Python 3.12.3 | `lyrical/` | `start_ros2.cmd` |
| MoveIt 2.15.2와 RoboStack Lyrical, Python 3.14.8 | `moveit/.pixi/` | `start_moveit.cmd` |
| Setup Assistant 2.15.2와 Qt 6.12 | `moveit-setup/.pixi/` | `start_moveit_setup.cmd` |

기존 공식 배포본과 RoboStack은 Python 및 바이너리 구성이 달라 같은 터미널에서 혼합하면 안 됩니다. Setup Assistant는 현재 패키지의 Qt 의존성 충돌 때문에 별도 환경을 사용합니다.

## 설치 조건과 동작

- Windows 11 x64, 64비트 Windows PowerShell 5.1 이상, 인터넷 연결이 필요합니다. 기본 제공 `curl.exe`와 `tar.exe`를 사용합니다.
- 공백·특수문자가 없는 짧은 쓰기 가능한 경로를 사용합니다. 예: `C:\python_ws\ros2`.
- 기존 ROS, Conda, venv가 활성화되지 않은 새 터미널에서 설치합니다.
- 두 배포본과 다운로드 캐시를 보관하므로 여유 공간은 약 25 GB 이상을 권장합니다. 선택한 구성과 패키지 캐시에 따라 사용량이 달라집니다.
- 설치 스크립트는 시스템 Python이나 영구 PATH를 바꾸지 않습니다. 실행 정책 예외는 해당 PowerShell 프로세스에만 적용합니다.
- Visual Studio 설치와 사용자 C++ 패키지 빌드는 자동화 범위에 포함하지 않습니다. 빌드 도구 준비는 [ROS 2 가이드](docs/ros2-installation.md)를 확인합니다.

Pixi 및 공식 ROS ZIP의 URL과 SHA-256은 `config/sources.json`에 고정했습니다. MoveIt 환경의 정확한 패키지 URL·버전·해시는 두 `pixi.lock`에 기록되어 있으며, 설치 시 `--locked`를 사용합니다. 최신 버전을 자동으로 선택하지 않습니다.

설치 명령은 다시 실행할 수 있습니다. 검증된 캐시와 기존 환경을 재사용합니다. 기존 공식 ROS의 manifest/lock이 고정 배포본과 다르면 덮어쓰지 않고 중단합니다. 설치 위치는 이 스크립트가 있는 폴더입니다. 설치 후 폴더를 옮기면 절대 경로가 깨질 수 있으므로 새 위치에서 다시 설치하십시오.

## 검증과 알려진 제한

기본 설치 검증은 공식 ROS의 C++ talker → Python listener 송수신과 MoveIt의 Panda OMPL Planning입니다. MoveIt 검증은 예제의 가상 드라이버를 띄우지만 기본적으로 궤적 실행을 요청하지 않습니다. 실제 로봇은 필요하지 않습니다.

```powershell
# Planning과 가상 Execution을 모두 검사
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component MoveIt -VerifyExecution

# 패키지 설치만 수행
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component All -SkipVerification
```

검증에 실패하면 설치 명령도 실패 코드로 종료됩니다. 이 경우 이미 설치된 파일은 남습니다. 결과는 `logs/install-*.json`, `logs/verification.json`, `logs/moveit-runtime-verification.json`에서 확인합니다. `-SkipVerification` 결과는 런타임 정상 작동을 의미하지 않습니다.

새 경로에서 자동 통신 검증을 실행하면 Windows 방화벽 알림이 나타날 수 있습니다. 패키지 설치만 먼저 하려면 `-SkipVerification`을 사용하고, 실행 파일에 필요한 네트워크 규칙은 관리자와 확인하십시오. 허용 버튼 비활성화에 대한 설명은 [ROS 2 문제 해결](docs/ros2-installation.md)에 있습니다.

현재 `moveit_py`는 Planning 성공 후 종료 시 `0xC0000005` 충돌이 재현됩니다. 검증된 Python 사용 방식은 `rclpy`에서 `move_group` 서비스·액션을 호출하는 것입니다. `moveit/verify_runtime.py`가 해당 예제입니다. 상세 제한과 RViz 사용법은 [MoveIt 가이드](docs/moveit-installation.md)에 있습니다.

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
- 기존 로컬 설치 기록: `README.txt`, `MOVEIT_README.txt` — 기록의 경로는 최초 설치 위치 기준입니다.

설치 방식은 [ROS 2 Windows 바이너리 안내](https://docs.ros.org/en/lyrical/Get-Started/Installation/Windows-Install-Binary.html), [MoveIt Windows 바이너리 안내](https://moveit.ai/install-moveit2/binary-windows/), [RoboStack 시작 안내](https://robostack.github.io/GettingStarted.html)를 참고했습니다.
