# Windows 11에서 ROS 2 기본 사용

> **가장 먼저:** 설치 전에는 [필수 Python 3.12 x64 사전 설치](../README.md#0-필수-python부터-설치)를 완료하십시오. 설치 후에는 `start_ros2.cmd`(공식 ROS) 또는 `start_moveit.cmd`(MoveIt)를 **매번 먼저 실행**하고, 열린 전용 터미널 안에서 아래 ROS/Python 명령을 실행합니다. 새 터미널마다 활성화해야 합니다.

`<your-workspace>`는 저장소 폴더의 실제 절대 경로로 바꿉니다. 꺾쇠를 그대로 입력하지 마십시오.

이 저장소의 설치가 끝난 상태를 기준으로 설명합니다. ROS 명령의 구조는 Ubuntu와 같고, 먼저 실행하는 환경 활성화 명령이 다릅니다. 아래 `bat` 코드 블록은 CMD 기준입니다.

## 터미널마다 환경 활성화

공식 ROS만 사용할 때는 `start_ros2.cmd`, MoveIt과 함께 사용할 때는 `start_moveit.cmd`를 엽니다. 이미 열린 **새 CMD**에서는 하나만 선택합니다.

```bat
call "<your-workspace>\activate_ros2.cmd"
```

```bat
call "<your-workspace>\activate_moveit.cmd"
```

PowerShell에서는 다음 중 하나를 dot-source합니다.

```powershell
. "<your-workspace>\activate_ros2.ps1"
```

MoveIt 작업용 새 PowerShell에서는 위 명령 대신 다음을 사용합니다.

```powershell
. "<your-workspace>\activate_moveit.ps1"
```

**실행기를 한 번 열었다고 다른 터미널까지 활성화되는 것은 아닙니다.** `start_*.cmd`가 연 CMD에서 작업하거나, 현재 터미널에 맞는 `activate_*`를 실행하십시오. 두 환경을 한 터미널에 겹쳐 적용하지 않습니다. PowerShell에서 `.cmd`를 실행하는 것만으로는 자식 CMD의 환경이 현재 PowerShell로 전달되지 않으므로 `.ps1`을 사용합니다. 활성화 스크립트가 작업 디렉터리도 바꾸므로 아래 예제는 필요한 경우 절대 경로를 사용합니다.

```bat
echo %ROS_DISTRO%
where.exe ros2
where.exe python
ros2 --help
ros2 pkg list
```

PowerShell에서 환경변수 확인은 `$env:ROS_DISTRO`입니다. `where.exe`는 PowerShell에서도 그대로 사용할 수 있습니다.

## ros2 run으로 실행 파일 시작

```bat
ros2 run 패키지이름 실행파일이름
```

예를 들어 첫 번째 터미널에서 publisher를, 두 번째 터미널에서 subscriber를 실행합니다. 두 터미널 모두 같은 환경을 활성화합니다.

```bat
ros2 run demo_nodes_cpp talker
```

```bat
ros2 run demo_nodes_py listener
```

`Publishing`과 `I heard`가 반복되면 메시지가 전달되고 있습니다. Ctrl+C로 각각 종료합니다. `run`은 패키지에 등록된 실행 파일을 찾는 명령입니다. 임의의 `.py` 파일은 [일반 Python 스크립트 실행](python-scripts.md)을 참고합니다.

실행 가능한 이름과 실제 선택된 패키지 위치를 확인할 수 있습니다.

```bat
ros2 pkg executables demo_nodes_cpp
ros2 pkg prefix demo_nodes_cpp
ros2 node list
ros2 node info /talker
```

노드 이름이나 토픽 이름을 바꿔 실행하는 예:

```bat
ros2 run demo_nodes_cpp talker --ros-args -r __node:=my_talker -r chatter:=my_chatter
ros2 run demo_nodes_py listener --ros-args -r chatter:=my_chatter
```

위 두 명령은 별도 터미널에서 실행합니다. `--ros-args` 뒤의 `-r`은 이름 remapping이며, 실제 메시지는 `/my_chatter`에서 오갑니다.

## ros2 launch로 여러 프로세스 시작

설치된 패키지의 launch 파일은 Ubuntu와 같은 형식으로 실행합니다.

```bat
ros2 launch demo_nodes_cpp talker_listener_launch.py
```

이 배포본에는 해당 파일이 `demo_nodes_cpp` 패키지의 `launch/topics/` 아래에 설치되어 있습니다. 패키지 방식은 이름으로 찾으므로 설치 폴더의 절대 경로를 명령에 넣을 필요가 없습니다.

패키지로 설치하지 않은 launch 파일은 경로로 실행할 수도 있습니다.

```bat
ros2 launch "<your-workspace>/examples/hello_ros.launch.py" max_messages:=3
```

launch 인수 목록은 먼저 확인합니다.

```bat
ros2 launch "<your-workspace>/examples/hello_ros.launch.py" --show-args
ros2 launch "<your-workspace>/examples/ur_planning.launch.py" --show-args
```

`인수명:=값`은 launch 파일이 받아서 사용하도록 작성된 인수입니다. ROS 노드 파라미터와 자동으로 연결되는 것은 아닙니다. 예를 들어 `kinematics_solver_timeout:=0.2`를 아무 launch에 붙여도 MoveIt 설정이 바뀌지는 않습니다. [MoveIt 설정 가이드](moveit-usage.md)에서 연결 방법을 설명합니다.

launch는 Ctrl+C로 종료하며 자신이 띄운 프로세스들의 종료도 관리합니다. 로그는 이 프로젝트의 `logs/ros/` 아래에 저장됩니다. Windows의 `latest` 로그 링크 생성 권한 경고만 발생한 경우에는 날짜별 로그 폴더를 직접 확인하면 됩니다.

## ros2 topic으로 메시지 확인

talker를 실행한 상태에서 다른 활성화된 터미널을 사용합니다.

| 목적 | 명령 |
| --- | --- |
| 토픽 목록 | `ros2 topic list` |
| 이름과 메시지 타입 | `ros2 topic list -t` |
| 메시지 타입만 확인 | `ros2 topic type /chatter` |
| 발행·구독 수와 QoS | `ros2 topic info /chatter --verbose` |
| 메시지 계속 출력 | `ros2 topic echo /chatter` |
| 메시지 한 개만 출력 | `ros2 topic echo /chatter --once` |
| 수신 주기 측정 | `ros2 topic hz /chatter` |
| 수신 대역폭 측정 | `ros2 topic bw /chatter` |
| 메시지 필드 정의 | `ros2 interface show std_msgs/msg/String` |

listener를 실행한 상태에서 CLI로 메시지를 한 번 보낼 수도 있습니다.

```bat
ros2 topic pub --once /chatter std_msgs/msg/String "{data: 'hello from CLI'}"
```

`echo`, `hz`, `bw`처럼 계속 실행되는 명령은 Ctrl+C로 종료합니다. 수신 주기와 대역폭 측정값은 측정 노드와 시스템 부하의 영향을 받습니다.

토픽은 보이는데 데이터가 안 나오면 발행 측 QoS를 확인합니다. Best Effort 센서 토픽을 읽는 예:

```bat
ros2 topic echo /sensor_topic --qos-reliability best_effort
```

`/sensor_topic`은 실제 토픽 이름으로 바꿉니다. 토픽 타입, QoS, ROS_DOMAIN_ID가 서로 맞아야 합니다.

## RViz 실행

MoveIt 터미널에서 다음 중 하나를 실행합니다.

```bat
rviz2
```

```bat
ros2 run rviz2 rviz2
```

기존 `.rviz` 설정을 불러오는 형식은 다음과 같습니다. 경로는 실제 파일로 바꿉니다.

```bat
rviz2 -d "<your-workspace>/my_robot_ws/src/my_robot_moveit_config/config/my_robot.rviz"
```

RViz는 시각화 도구이므로 단독 실행만으로 로봇 모델이나 Planning 서버를 띄우지는 않습니다. 로봇 관련 노드가 이미 실행되어 있어야 하며, `Global Options → Fixed Frame`을 실제 TF 프레임으로 맞추고 필요한 Display를 추가합니다. UR 예제의 Fixed Frame은 `world`이며 Planning Group은 `ur_manipulator`입니다.

MoveIt의 MotionPlanning 패널까지 사용하려면 [MoveIt launch](moveit-usage.md)로 함께 시작하는 것이 편합니다. `.rviz` 파일은 화면 구성이고, `kinematics.yaml`이나 로봇 제어 설정을 대신하지 않습니다.

## 노드 파라미터와 서비스 확인

```bat
ros2 param list /노드이름
ros2 param get /노드이름 파라미터이름
ros2 service list -t
ros2 action list -t
```

`ros2 param set /노드이름 이름 값`은 해당 노드가 변경을 지원할 때만 사용합니다. 파라미터 저장값이 바뀌어도 이미 초기화된 플러그인이 자동으로 다시 만들어지는 것은 아닙니다. MoveIt의 IK나 플래너 구성은 YAML을 수정한 뒤 launch를 다시 시작하는 방식으로 적용합니다.

## 통신이 안 될 때

같은 PC에서 테스트할 터미널들의 도메인을 동일하게 맞출 수 있습니다. 노드를 실행하기 전에 설정합니다.

```bat
set ROS_DOMAIN_ID=42
set ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
```

PowerShell 형식:

```powershell
$env:ROS_DOMAIN_ID = '42'
$env:ROS_AUTOMATIC_DISCOVERY_RANGE = 'LOCALHOST'
```

`LOCALHOST`는 다른 PC의 로봇과 연결하려는 경우에는 맞지 않습니다. 외부 연결에는 탐색 범위, 네트워크, 방화벽을 별도로 설정해야 합니다. 도메인이나 미들웨어를 바꾼 뒤 CLI 목록이 오래된 상태라면 해당 터미널에서 `ros2 daemon stop` 후 다시 조회할 수 있습니다.

방화벽 허용 버튼 문제는 [설치 가이드의 문제 해결](ros2-installation.md)을 참고합니다. 공식 ROS와 MoveIt 환경을 번갈아 source하거나 전역 PATH/PYTHONPATH에 두 환경을 함께 넣어서 해결하지 않습니다.

참고: [ROS 2 Lyrical launch 안내 원문](https://github.com/ros2/ros2_documentation/blob/lyrical/source/ROS-Framework/nodes/Working-with-nodes/Launching-Multiple-Nodes/Launching-Multiple-Nodes.rst), [ROS 2 CLI 소스와 설명](https://github.com/ros2/ros2cli). 이 문서의 명령과 launch 이름은 현재 설치본을 기준으로 작성했습니다.
