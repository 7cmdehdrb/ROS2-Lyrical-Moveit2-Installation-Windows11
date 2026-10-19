# Windows 11에서 MoveIt 실행과 YAML 설정 변경

Windows에서도 `ros2 launch 패키지이름 파일.launch.py` 문법은 Ubuntu와 같습니다. 먼저 **MoveIt 환경**을 활성화하고, launch 파일이 어떤 설정 파일과 인수를 실제로 읽는지 확인하면 됩니다. 이 문서는 저장소에 설치된 RoboStack Lyrical과 Panda 예제를 기준으로 합니다.

## 기본 Panda 데모 실행

`start_moveit.cmd`를 열거나 새 CMD에서 활성화합니다.

```bat
call C:\python_ws\ros2\activate_moveit.cmd
ros2 launch moveit_resources_panda_moveit_config demo.launch.py
```

PowerShell에서는 활성화 명령만 다음으로 바꿉니다.

```powershell
. C:\python_ws\ros2\activate_moveit.ps1
```

이 데모는 `move_group`, RViz, 로봇 모델·TF, mock 하드웨어와 컨트롤러를 함께 시작합니다. 실제 로봇이 없어도 Planning을 사용할 수 있습니다. RViz의 MotionPlanning 패널에서 Planning Group을 `panda_arm`으로 선택하고, 시작 상태와 목표 상태를 정한 뒤 **Plan**을 누릅니다. 실행까지 필요하지 않다면 **Execute**나 **Plan & Execute**는 누르지 않아도 됩니다.

설치된 패키지 위치와 launch 인수는 다음으로 확인합니다.

```bat
ros2 pkg prefix --share moveit_resources_panda_moveit_config
ros2 launch moveit_resources_panda_moveit_config demo.launch.py --show-args
```

현재 배포본의 `demo.launch.py`는 `rviz_config`, `db`, `ros2_control_hardware_type` 인수를 제공합니다. 임의의 `kinematics_file:=...` 인수를 추가한다고 그 파일을 읽는 것은 아닙니다. launch가 해당 인수를 선언하고 설정 로딩에 연결해야 합니다.

## 수정 가능한 YAML을 별도로 전달하는 예제

설치 폴더 안의 파일을 직접 수정하지 않고 사용하도록 [`examples/panda_custom.launch.py`](../examples/panda_custom.launch.py)를 추가했습니다. **Panda 로봇, OMPL, mock 하드웨어**용 예제이며, 다른 로봇을 자동으로 설정하는 범용 launch는 아닙니다.

MoveIt 환경에서 다음 한 줄로 실행합니다.

```bat
ros2 launch C:/python_ws/ros2/examples/panda_custom.launch.py
```

기본적으로 [`examples/config/panda_kinematics.yaml`](../examples/config/panda_kinematics.yaml)을 읽고 RViz도 시작합니다. YAML을 수정한 뒤 launch를 다시 시작하면 적용됩니다. 이 방식은 launch 파일을 절대 경로로 실행하므로 `colcon build`가 필요하지 않습니다.

지원 인수:

| 인수 | 기본값 / 동작 |
| --- | --- |
| `rviz` | `true`. `false`이면 GUI 없이 시작 |
| `kinematics_file` | 예제 폴더의 `config/panda_kinematics.yaml` |
| `joint_limits_file` | 생략 시 설치된 기본 설정 유지 |
| `ompl_file` | 생략 시 설치된 기본 설정 유지 |
| `ik_timeout` | 생략 시 YAML 값 사용. 지정하면 Panda arm의 IK timeout을 마지막에 덮어씀 |

파일 인수에는 **절대 경로**를 전달합니다. 예를 들어 YAML 세 개와 명령행 override를 함께 적용하려면:

```bat
ros2 launch C:/python_ws/ros2/examples/panda_custom.launch.py kinematics_file:=C:/python_ws/ros2/examples/config/panda_kinematics.yaml joint_limits_file:=C:/python_ws/ros2/examples/config/panda_joint_limits.yaml ompl_file:=C:/python_ws/ros2/examples/config/panda_ompl.yaml ik_timeout:=0.2
```

GUI 없이 Planning 서버를 시작하려면 위 명령 끝에 `rviz:=false`를 붙입니다. 명령은 CMD와 PowerShell 모두 한 줄로 실행할 수 있습니다. 경로에 공백이 있다면 `"kinematics_file:=C:/path with spaces/kinematics.yaml"`처럼 인수 전체를 따옴표로 감쌉니다.

이 예제의 적용 순서는 **설치된 Panda 기본값 → YAML 파일 → `ik_timeout` 인수**입니다. YAML의 중첩 mapping은 재귀적으로 합치고, 같은 키의 scalar와 list는 교체합니다. 따라서 예제 joint limits 파일에 없는 관절과 OMPL planner 설정은 기본값을 유지합니다. 이 부분 병합은 **이번에 작성한 launch의 동작**이며, 모든 MoveIt launch가 같은 방식으로 동작하는 것은 아닙니다.

## kinematics.yaml의 값 변경

예제 파일의 내용입니다.

```yaml
panda_arm:
  kinematics_solver: kdl_kinematics_plugin/KDLKinematicsPlugin
  kinematics_solver_search_resolution: 0.01
  kinematics_solver_timeout: 0.1
```

- `panda_arm`은 SRDF에 정의된 planning group 이름입니다. 자신의 로봇에서는 실제 그룹 이름과 일치해야 합니다.
- `kinematics_solver`는 설치된 IK 플러그인의 클래스 이름입니다. 이름만 변경해 새 플러그인이 설치되지는 않습니다. Windows용 라이브러리와 플러그인 등록이 있어야 하며 로봇 구조도 지원해야 합니다.
- `kinematics_solver_search_resolution`은 IK solver가 사용하는 검색 간격입니다. 구체적인 의미와 사용 여부는 solver에 따릅니다.
- `kinematics_solver_timeout`은 IK 계산에 주는 시간(초)입니다. 전체 모션 플래닝의 허용 시간과는 별개입니다.

위 YAML의 timeout은 `0.1`이지만, `ik_timeout:=0.2`를 지정하면 최종 timeout은 `0.2`가 됩니다. 이 인수는 예제에서 `panda_arm`에 명시적으로 연결한 편의 기능입니다. 다른 파라미터를 명령행에서 바꾸려면 같은 방식으로 launch에 연결하거나 YAML을 수정합니다.

MoveIt 원본 설정 파일은 다음과 같이 서로 다른 파라미터 영역에 들어갑니다.

| 설정 파일 | 주요 내용 | 이 launch가 전달하는 ROS 파라미터 영역 |
| --- | --- | --- |
| `kinematics.yaml` | 그룹별 IK solver와 설정 | `robot_description_kinematics` |
| `joint_limits.yaml` | 관절 속도·가속도 제한 등 | `robot_description_planning` |
| `ompl_planning.yaml` | OMPL 알고리즘·planner 설정 | `ompl` |
| `moveit_controllers.yaml` 등 | MoveIt이 호출할 controller와 action 연결 | MoveIt trajectory execution 설정 |
| `ros2_controllers.yaml` | ros2_control controller 종류·관절 등 | controller manager 및 controller의 파라미터 |
| `.rviz` | 화면·Display 구성 | RViz 설정 파일로 로딩 |

이 예제의 joint limits 파일은 `panda_joint1`의 최대 속도와 가속도를 낮추는 예시이고, OMPL 파일은 `RRTConnectkConfigDefault`의 `range`를 바꾸는 예시입니다. IK timeout, 모션 플래닝 허용 시간, 관절의 물리적 제한, 요청별 속도·가속도 scaling은 각각 다른 설정입니다. RViz의 Planning Time이나 scaling 값을 바꾸는 것과 `kinematics.yaml` 수정은 같은 작업이 아닙니다. 실제 로봇의 제한은 제조사와 드라이버의 사양에 맞춰야 합니다.

## 실제 적용된 값 확인

launch를 계속 실행한 상태에서 **다른 MoveIt 터미널**을 엽니다. 같은 ROS_DOMAIN_ID를 사용합니다.

```bat
ros2 param get /move_group robot_description_kinematics.panda_arm.kinematics_solver_timeout
ros2 param get /move_group robot_description_kinematics.panda_arm.kinematics_solver_search_resolution
ros2 param get /move_group robot_description_planning.joint_limits.panda_joint1.max_velocity
ros2 param get /move_group ompl.planner_configs.RRTConnectkConfigDefault.range
```

위의 세 YAML과 `ik_timeout:=0.2` 명령으로 시작했다면 각각 `0.2`, `0.01`, `1.0`, `0.15`가 나와야 합니다. RViz도 실행했다면 IK 설정을 별도로 확인할 수 있습니다.

```bat
ros2 param get /rviz2 robot_description_kinematics.panda_arm.kinematics_solver_timeout
```

예제 launch는 변경한 IK·관절 제한·플래너 설정을 `move_group`과 RViz에 함께 전달합니다. 자신이 작성한 launch에서도 양쪽이 서로 다른 로봇 설정을 받지 않도록 확인합니다.

전체 파라미터를 기록하려면:

```bat
ros2 param dump /move_group > C:/python_ws/ros2/logs/move_group-parameters.yaml
```

이 dump는 노드명과 `ros__parameters`로 감싼 **ROS 노드 파라미터 파일**입니다. 원본 `kinematics.yaml` 자리에 그대로 넣는 파일이 아닙니다. 마찬가지로 원본 `kinematics.yaml`을 `--ros-args --params-file`에 바로 넘기는 것만으로는 위 launch의 로딩 과정을 대신할 수 없습니다.

파일을 수정했다면 Ctrl+C로 launch를 종료하고 다시 시작합니다. `ros2 param set`으로 저장값이 바뀌었다고 이미 로딩한 IK 플러그인이나 planner가 새 설정으로 재초기화됐다고 판단하면 안 됩니다.

2026-10-19에 이 예제를 `rviz:=false`, `ik_timeout:=0.123`과 세 YAML로 실행하여 위 네 파라미터의 실제 값과 OMPL Planning 성공을 확인했습니다. `/plan_kinematic_path` 결과 코드는 성공(`1`)이었고 궤적은 26개 점을 포함했습니다. 궤적 점 수는 실행마다 달라질 수 있습니다. 이 검사는 Execution을 요청하지 않았습니다. 결과와 로그는 로컬 `logs/custom-panda-verification.json`, `logs/custom-panda-demo.log`에 있으며 Git에서는 제외됩니다.

## Ubuntu에서 사용하던 자신의 설정 패키지 실행

기존 명령이 다음과 같았다면 Windows에서도 명령 형식은 동일합니다.

```bat
ros2 launch my_robot_moveit_config demo.launch.py
```

다만 `my_robot_moveit_config`가 현재 Windows 환경에 설치되어 있어야 합니다. Ubuntu의 `build/`, `install/`을 복사해서 쓰는 대신 **패키지 소스**인 `package.xml`, `CMakeLists.txt`, launch, YAML, URDF/Xacro, SRDF와 필요한 mesh를 가져옵니다. Linux 전용 드라이버나 플러그인은 Windows 지원 여부를 별도로 확인합니다. launch 안의 `/opt/ros/...` 같은 하드코딩 경로와 Bash 실행도 점검합니다.

예를 들어 이 프로젝트 아래에 다음처럼 구성합니다.

```text
C:/python_ws/ros2/my_robot_ws/
  src/
    my_robot_moveit_config/
      package.xml
      CMakeLists.txt
      launch/
      config/
```

빌드 도구와 패키지 의존성이 준비된 **CMD**에서 사용하는 예입니다. 패키지 이름은 실제 이름으로 바꿉니다.

```bat
call C:\python_ws\ros2\activate_moveit.cmd
cd /d C:\python_ws\ros2\my_robot_ws
colcon build --merge-install --packages-select my_robot_moveit_config --cmake-args -DCMAKE_BUILD_TYPE=Release
call install\local_setup.bat
ros2 pkg prefix --share my_robot_moveit_config
ros2 launch my_robot_moveit_config demo.launch.py
```

이 명령은 해당 패키지의 의존성을 자동 다운로드하거나 빌드하지 않습니다. 소스 의존성까지 같은 워크스페이스에 있다면 빌드 범위도 조정해야 합니다. C++ 패키지는 Windows용 Visual Studio 빌드 환경 등이 필요하며 이 저장소의 바이너리 설치기는 이를 자동 설치하지 않습니다. 위 과정은 사용자 패키지마다 추가 검증이 필요합니다.

새 터미널에서는 MoveIt 기본 환경을 먼저 활성화하고 `my_robot_ws/install/local_setup.bat` overlay를 적용합니다. PowerShell용 overlay가 생성되어 있다면 `. C:\python_ws\ros2\my_robot_ws\install\local_setup.ps1`로 적용할 수 있습니다. `ros2 pkg prefix --share`가 기대한 자신의 `install` 경로를 가리키는지 확인하십시오.

일반 빌드에서는 소스의 YAML 수정이 설치된 복사본에 자동 반영되지 않습니다. 소스를 수정하고 다시 빌드하거나, 이번 예제처럼 외부 YAML의 절대 경로를 받아 로딩하도록 launch를 작성합니다. `build/`, `install/`, `log/`는 `.gitignore` 대상이고, 직접 작성한 설정·launch 소스는 Git에 포함합니다.

## 자신의 launch에 YAML 로딩 연결

`MoveItConfigsBuilder`를 쓰는 launch에서는 다음과 같이 설정 파일을 선택할 수 있습니다. 아래 코드는 설정 구성 부분만 보여 주며 로봇 bringup 전체를 대신하지 않습니다.

```python
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder

config = (
    MoveItConfigsBuilder('my_robot', package_name='my_robot_moveit_config')
    .robot_description_kinematics(file_path='config/kinematics.yaml')
    .joint_limits(file_path='config/joint_limits.yaml')
    .planning_pipelines(pipelines=['ompl'])
    .to_moveit_configs()
)

move_group_node = Node(
    package='moveit_ros_move_group',
    executable='move_group',
    parameters=[config.to_dict()],
)
```

이때 상대 `file_path`는 설정 패키지의 share 디렉터리를 기준으로 합니다. 외부 파일은 절대 경로로 지정할 수 있습니다. 명령행 `kinematics_file:=...`까지 지원하려면 `DeclareLaunchArgument`와 `LaunchConfiguration`을 연결해야 합니다. 완성된 예제에서는 `OpaqueFunction` 안에서 인수 값을 해석하고 YAML을 읽은 뒤 노드를 생성합니다. [`panda_custom.launch.py`](../examples/panda_custom.launch.py)를 참고하여 자신의 그룹·로봇 모델·controller 구성을 유지한 채 적용하십시오.

관련 문서: [MoveIt 설정 구성 안내](https://moveit.picknik.ai/main/doc/how_to_guides/moveit_configuration/moveit_configuration_tutorial.html), [Kinematics 설정 안내](https://moveit.picknik.ai/main/doc/examples/kinematics_configuration/kinematics_configuration_tutorial.html). 배포본별 launch 차이는 설치된 파일과 `--show-args`를 기준으로 확인합니다.
