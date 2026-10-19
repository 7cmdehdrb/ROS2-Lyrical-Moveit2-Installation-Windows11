# Windows 11에서 공식 ROS 2 Lyrical 설치

이 가이드는 ROS 2 공식 Windows AMD64 바이너리 `release-lyrical-20260807`을 설치합니다. 배포 ZIP에 포함된 Pixi manifest와 lock을 사용하여 Python 3.12.3 및 의존성을 구성합니다. MoveIt이 목적이라면 [MoveIt 가이드](moveit-installation.md)의 별도 RoboStack 설치만으로도 시작할 수 있습니다.

## 자동 설치

저장소를 `C:\python_ws\ros2`에 clone한 뒤 새 PowerShell에서 실행합니다.

```powershell
cd C:\python_ws\ros2
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component ROS2
```

스크립트는 다음 순서로 처리합니다.

1. Windows 11 x64와 깨끗한 터미널 환경을 확인합니다.
2. `downloads/`에 Pixi 0.82.0 ZIP을 내려받고 SHA-256 확인 후 `tools/pixi/`에 설치합니다.
3. 공식 ROS ZIP을 같은 폴더에 내려받고 SHA-256 확인 후 `lyrical/`에 풉니다.
4. `pixi install --locked`로 배포본의 의존성을 설치합니다.
5. 공식 `preinstall_setup_windows.py`로 Python 실행 경로를 보정합니다.
6. C++ talker와 Python listener 간 메시지 송수신을 검사합니다.

이 과정에 필요한 다운로드 URL과 체크섬은 [`config/sources.json`](../config/sources.json)에 있습니다. 캐시·임시 파일·ROS 로그는 프로젝트 아래에 저장합니다. 그래픽 도구의 모든 사용자 설정 경로까지 강제 재지정하는 것은 아닙니다.

## 실행과 통신 확인

`start_ros2.cmd`를 실행하면 환경이 활성화된 CMD가 열립니다. 이미 열린 깨끗한 CMD에서는 다음을 사용합니다.

```bat
call C:\python_ws\ros2\activate_ros2.cmd
ros2 --help
```

PowerShell에서는 dot-source합니다.

```powershell
. C:\python_ws\ros2\activate_ros2.ps1
```

터미널 두 개를 각각 활성화한 뒤 실행합니다.

```bat
rem 첫 번째 터미널
ros2 run demo_nodes_cpp talker
```

```bat
rem 두 번째 터미널
ros2 run demo_nodes_py listener
```

`Publishing`과 `I heard`가 반복되면 송수신이 정상입니다. 종료는 Ctrl+C입니다. 자동 검사를 다시 실행하려면 활성화된 터미널에서 다음을 사용합니다.

```bat
python C:\python_ws\ros2\verify_install.py
```

자동 검사는 localhost, ROS_DOMAIN_ID 177을 사용합니다. 일반 실행기에는 이 테스트 도메인을 적용하지 않습니다.

## 수동으로 의존성 재설치

이미 ZIP 압축 해제까지 끝난 경우 새 PowerShell에서 다음을 실행할 수 있습니다.

```powershell
cd C:\python_ws\ros2
. .\env-local.ps1
cd .\lyrical
pixi install --locked
pixi run --locked python preinstall_setup_windows.py
```

설치 명령을 다시 실행해도 됩니다. 변경된 기존 manifest나 lock을 자동으로 원상 복구하지는 않습니다.

## C++ 패키지를 빌드하는 경우

[공식 문서](https://docs.ros.org/en/lyrical/Get-Started/Installation/Windows-Install-Binary.html)는 사용자 C++ 패키지 빌드에 Visual Studio Build Tools 2022와 `Desktop development with C++` 워크로드, Windows SDK를 안내합니다. 빌드는 `x64 Native Tools Command Prompt for VS 2022`에서 수행합니다. 이 저장소의 설치기는 해당 시스템 도구를 설치하지 않습니다.

공식 ROS 바이너리와 연결되는 C++ 패키지는 `Release` 또는 `RelWithDebInfo`로 빌드해야 합니다. 예를 들어 별도로 준비한 워크스페이스에서:

```bat
colcon build --merge-install --cmake-args -DCMAKE_BUILD_TYPE=Release
```

생성되는 `build/`, `install/`, `log/`는 이 저장소의 `.gitignore`에서 제외됩니다.

## 문제 해결

| 증상 | 조치 |
| --- | --- |
| 다른 ROS 또는 Conda 환경이 활성화되었다는 오류 | 새 PowerShell을 열고 재실행합니다. |
| 다운로드 체크섬 오류 | 메시지에 표시된 파일만 삭제하고 재실행합니다. 해시 확인을 생략하지 않습니다. |
| 다운로드 또는 패키지 접근 실패 | GitHub 릴리스, conda-forge 접근과 프록시 설정을 확인한 뒤 재실행합니다. |
| 기존 manifest 또는 lock 불일치 | 기존 환경을 보존하고 새 프로젝트 위치에서 설치하거나 의도한 수정인지 먼저 확인합니다. |
| 경로 길이 오류 | 프로젝트를 더 짧은 경로에 새로 설치합니다. 설치된 환경 자체를 이동하지 않습니다. |
| RTI Connext DDS 없음 경고 | 선택 미들웨어 경고입니다. 기본 Fast DDS 사용에는 필요하지 않습니다. |
| Python 또는 ROS 프로그램의 네트워크 허용 알림 | 새 설치 경로는 별도 프로그램으로 인식됩니다. 허용 버튼을 사용할 수 없다면 관리자에게 해당 실행 파일의 규칙을 확인하도록 요청합니다. 설치기는 방화벽 정책을 자동으로 변경하지 않습니다. |

기본 실행기는 Fast DDS UDPv4를 사용하여 시스템 ProgramData의 공유 메모리 파일 생성을 피합니다. 다중 PC 및 실제 로봇 네트워크 설정은 별도로 구성해야 합니다.

[Microsoft의 방화벽 규칙 안내](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/rules)에 따르면 비관리자에게 허용 알림이 표시되면 선택과 관계없이 차단 규칙이 만들어질 수 있습니다. 같은 PC 안의 자동 검증과 외부 PC·로봇에서 들어오는 연결은 구분해야 합니다. 테스트가 끝난 임시 설치 경로에는 추가 네트워크 허용이 필요하지 않습니다.

공식 안내: [ROS 2 Windows 바이너리 설치](https://docs.ros.org/en/lyrical/Get-Started/Installation/Windows-Install-Binary.html), [해당 릴리스](https://github.com/ros2/ros2/releases/tag/release-lyrical-20260807).
