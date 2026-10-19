ROS 2 Lyrical / Windows 11 설치 안내
설치 및 검증일: 2026-10-19 (Asia/Seoul)

MoveIt 2 추가 설치 안내: C:\python_ws\ros2\MOVEIT_README.txt
MoveIt 시작: C:\python_ws\ros2\start_moveit.cmd
Setup Assistant 시작: C:\python_ws\ros2\start_moveit_setup.cmd
아래 내용은 기존 공식 ROS 2 설치에 관한 안내입니다.

설치 결과
- 공식 Windows AMD64 배포본: release-lyrical-20260807
- ROS 2 경로: C:\python_ws\ros2\lyrical
- Pixi: 0.82.0 / C:\python_ws\ros2\tools\pixi\pixi.exe
- 전용 Python: 3.12.3 / lyrical\.pixi\envs\default\python.exe
- ROS 패키지: 353개
- 기본 미들웨어: Fast DDS (rmw_fastrtps_cpp), UDPv4
- 배포본의 pixi.lock을 사용해 의존성 설치 완료
- 공식 preinstall_setup_windows.py로 Python 경로 보정 완료
- ROS 2 및 Pixi 다운로드 SHA-256 검증 완료 (downloads\sources.json)

시작 방법
1. C:\python_ws\ros2\start_ros2.cmd를 실행합니다.
   ROS 2 환경이 활성화된 명령 프롬프트가 열립니다.
2. 다음과 같은 명령을 실행합니다.
   ros2 --help
   ros2 pkg list

이미 열려 있는 명령 프롬프트에서 활성화:
   call C:\python_ws\ros2\activate_ros2.cmd

이미 열려 있는 PowerShell에서 활성화 (앞의 점과 공백 필요):
   . C:\python_ws\ros2\activate_ros2.ps1

PowerShell 실행 정책이 스크립트를 차단하면 start_ros2.cmd를 사용합니다.
활성화 스크립트는 현재 터미널의 환경과 작업 디렉터리를 설정합니다.
시스템의 기존 Python과 영구 PATH는 변경하지 않았습니다.

예제
ROS 2 터미널을 두 개 열고 각각 다음을 실행합니다.
   ros2 run demo_nodes_cpp talker
   ros2 run demo_nodes_py listener
Ctrl+C로 종료합니다.

검증 결과
- ros2 --help: 성공
- ros2 pkg list: 성공 (353개)
- ros2 run demo_nodes_cpp talker: 3개 메시지 발행
- ros2 run demo_nodes_py listener: 3개 메시지 수신
- 명령 프롬프트 및 PowerShell 활성화: 성공
- 검증은 localhost, ROS_DOMAIN_ID=177에서 수행했습니다.
  이 테스트용 도메인/탐색 범위는 일반 시작 스크립트에는 적용하지 않습니다.
- 결과: logs\verification.json
- 송수신 로그: logs\talker.log, logs\listener.log

같은 검증을 다시 실행하려면 활성화된 ROS 2 터미널에서:
   python C:\python_ws\ros2\verify_install.py

파일 위치
- 다운로드와 출처/체크섬: downloads
- ROS 2 및 의존성: lyrical
- Pixi 실행 파일과 전용 데이터: tools
- 의존성 다운로드 캐시: .cache
- 임시 파일: tmp
- ROS 설정/상태: .ros
- colcon 설정/상태: .colcon
- 실행 및 설치 로그: logs

설정 및 범위
프로젝트 밖의 C:\ProgramData\eprosima에 공유 메모리 파일이 생성되지 않도록
시작 스크립트에서 FASTDDS_BUILTIN_TRANSPORTS=UDPv4를 설정했습니다.
큰 메시지의 로컬 전송 성능은 공유 메모리 사용 시와 다를 수 있습니다.
GUI 프로그램과 다른 PC/로봇 간 네트워크 통신은 검증 범위에 포함하지 않았습니다.

RTI Connext DDS 미설치 경고는 선택 미들웨어에 관한 것으로, 기본 Fast DDS
사용에는 문제가 없습니다. 공식 설치 문서에서도 이 경고를 안내합니다.

사용자 C++ 패키지를 직접 빌드하려면 문서의 선택 항목인 Visual Studio
Build Tools 2022 (Desktop development with C++)와 Windows SDK가 추가로 필요합니다.
이번에는 공식 사전 빌드 ROS 2와 Pixi 의존성을 설치했으며 Visual Studio
Build Tools는 설치하지 않았습니다. 배포본의 ABI에 맞춰 향후 C++ 패키지는
Release 또는 RelWithDebInfo로 빌드해야 합니다.

참고 문서
https://docs.ros.org/en/lyrical/Get-Started/Installation/Windows-Install-Binary.html
https://github.com/ros2/ros2/releases/tag/release-lyrical-20260807
https://fast-dds.docs.eprosima.com/en/2.14.x/fastdds/env_vars/env_vars.html
