# ROS 2 환경에서 일반 Python 파일 실행

`import rclpy`를 사용하는 파일은 ROS 패키지의 executable로 등록하지 않아도 실행할 수 있습니다. **현재 설치에서는 해당 ROS 환경을 활성화한 뒤 `python 파일.py`로 실행합니다.**

Ubuntu에서 `/opt/ros/humble/setup.bash` 등을 source한 후 `python3`를 쓰는 것과 같은 원리입니다. 차이는 Windows에서 이 프로젝트의 Pixi Python과 DLL·패키지 검색 환경을 함께 선택한다는 점입니다. Python 코드에 `/opt/ros/...`나 Windows 설치 경로를 직접 추가할 필요가 없습니다.

## 어떤 Python을 사용해야 하는가

| 작업 | 활성화 스크립트 | 선택되는 Python |
| --- | --- | --- |
| 공식 ROS 2 Lyrical 사용 | `activate_ros2.cmd` / `.ps1` | `lyrical/.pixi/envs/default/python.exe`, 3.12.3 |
| MoveIt 메시지·서비스·액션, RoboStack ROS 사용 | `activate_moveit.cmd` / `.ps1` | `moveit/.pixi/envs/default/python.exe`, 3.14.8 |

예를 들어 CMD에서:

```bat
call C:\python_ws\ros2\activate_moveit.cmd
python -c "import sys, rclpy; print(sys.executable); print(rclpy.__file__)"
python C:\python_ws\ros2\examples\hello_ros.py
```

공식 ROS만 사용하려면 첫 줄을 `activate_ros2.cmd`로 바꿉니다. Python 파일은 동일하게 실행할 수 있습니다. 종료는 Ctrl+C입니다.

PowerShell에서는:

```powershell
. C:\python_ws\ros2\activate_moveit.ps1
python C:\python_ws\ros2\examples\hello_ros.py
```

활성화된 터미널에서 `python`이 전용 Python을 가리키는 것을 확인합니다. Windows의 `py`, 시스템 Python, 다른 venv의 Python은 별도 실행 파일을 선택할 수 있으므로 이 예제에서는 사용하지 않습니다. 환경 활성화 없이 전용 `python.exe` 경로만 직접 지정해도 DLL 검색 경로나 ROS 패키지 검색 경로가 빠질 수 있습니다.

## 실행 예제

[`examples/hello_ros.py`](../examples/hello_ros.py)는 패키지 등록 없이 실행되는 publisher입니다. `rclpy.init()`, `Node`, publisher와 timer를 만들고 `rclpy.spin_once()`로 콜백을 처리합니다. `import rclpy`만으로 노드가 생성되거나 통신이 시작되지는 않습니다.

첫 번째 터미널:

```bat
python C:/python_ws/ros2/examples/hello_ros.py
```

두 번째 터미널도 같은 ROS 환경을 활성화한 뒤:

```bat
ros2 node list
ros2 topic echo /hello
ros2 param get /hello_ros message
```

이 파일에는 `message`와 `max_messages` 파라미터가 선언되어 있습니다. 세 번 발행하고 종료하려면:

```bat
python C:/python_ws/ros2/examples/hello_ros.py --ros-args -p max_messages:=3 -p "message:=Hello from Windows"
```

노드와 토픽 이름도 바꿀 수 있습니다.

```bat
python C:/python_ws/ros2/examples/hello_ros.py --ros-args -r __node:=my_python_node -r hello:=my_hello
```

이 경우 노드는 `/my_python_node`, 토픽은 `/my_hello`입니다. 일반 Python 파일이어도 `rclpy.init()`가 ROS 인수를 읽으므로 동일한 ROS remapping과 파라미터 문법을 사용할 수 있습니다. 자체 `argparse`가 있다면 ROS 인수와 충돌하지 않도록 분리해서 처리해야 합니다.

## ROS 파라미터 YAML 사용

다음 파일은 ROS 노드용 파라미터 파일입니다.

```yaml
hello_ros:
  ros__parameters:
    message: Hello from a ROS parameter file
    max_messages: 3
```

저장소에 있는 파일을 그대로 사용할 수 있습니다.

```bat
python C:/python_ws/ros2/examples/hello_ros.py --ros-args --params-file C:/python_ws/ros2/examples/config/hello_ros.yaml
```

최상위 `hello_ros`는 실제 노드 이름과 맞아야 합니다. 노드 이름이나 namespace를 바꾸면 파일의 대상 이름도 맞추거나 목적에 맞는 ROS 파라미터 wildcard를 사용해야 합니다.

이 `노드명 → ros__parameters` 구조는 MoveIt의 원본 `kinematics.yaml` 구조와 다릅니다. `kinematics.yaml`을 그대로 일반 `--params-file`에 전달하는 방법은 [MoveIt 사용 가이드](moveit-usage.md)에서 설명하는 로딩 과정과 동일하지 않습니다.

## 일반 Python 파일을 launch에서 실행

[`examples/hello_ros.launch.py`](../examples/hello_ros.launch.py)는 활성화된 Python의 `sys.executable`을 이용해 `ExecuteProcess`로 스크립트를 시작합니다. 시스템 Python 이름을 하드코딩하지 않으므로 현재 선택한 ROS 환경을 따릅니다.

```bat
ros2 launch C:/python_ws/ros2/examples/hello_ros.launch.py max_messages:=3 "message:=Hello from launch"
```

`--show-args`로 지원 인수를 볼 수 있습니다. launch 파일을 일반 경로로 실행하는 이 방식에도 `colcon build`나 `setup.py` 등록이 필요하지 않습니다. `ExecuteProcess`가 ROS 파라미터를 자동으로 만들어 주는 것은 아니며, 예제에서 `--ros-args -p ...`를 명시적으로 전달합니다.

## 언제 ros2 run 등록이 필요한가

| 실행 방식 | 준비 |
| --- | --- |
| `python C:/.../node.py` | 환경 활성화와 Python 의존성 |
| `ros2 launch C:/.../file.launch.py` | launch 파일과 그 파일이 실행하는 코드 |
| `ros2 run my_package my_node` | ROS 패키지로 설치하고 실행 파일 또는 Python console entry point 등록 |
| `ros2 launch my_package file.launch.py` | 패키지의 share 디렉터리에 launch 파일 설치 |

여러 사람에게 배포하거나 다른 ROS 패키지가 이름으로 찾도록 하려면 `ament_python` 패키지의 `console_scripts` 등으로 등록하고 `colcon build`한 뒤 overlay를 활성화합니다. 단일 스크립트 실험을 위해 반드시 패키지부터 만들 필요는 없습니다.

VS Code에서도 표의 전용 Python을 interpreter로 선택해야 합니다. 통합 터미널의 ROS 활성화와 디버거 환경은 별개일 수 있습니다. 가장 먼저 활성화된 터미널에서 같은 명령이 성공하는지 확인한 뒤 IDE 환경을 맞추십시오.

## 오류 확인 순서

```bat
where.exe python
python -c "import sys, rclpy; print(sys.executable); print(rclpy.__file__)"
ros2 pkg prefix rclpy
```

`ModuleNotFoundError: rclpy`는 우선 interpreter와 활성화 상태를 확인합니다. DLL load 오류는 다른 Python 버전이나 다른 ROS 환경의 DLL이 섞였는지 확인합니다. 이를 해결하려고 일반 시스템 Python에 임의로 `pip install rclpy`하거나 두 ROS의 `Lib/site-packages`를 함께 추가하지 않습니다.

MoveIt Python 사용에는 별도 주의가 있습니다. `rclpy`로 `move_group` 서비스·액션을 사용하는 경로는 검증됐지만, 현재 `moveit_py`는 종료 시 충돌이 재현됩니다. 실행 예제는 [`moveit/verify_runtime.py`](../moveit/verify_runtime.py)를 참고합니다.
