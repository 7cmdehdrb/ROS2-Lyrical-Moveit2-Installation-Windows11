"""A ROS 2 publisher that runs directly with Python, without a ROS package."""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class HelloRos(Node):
    def __init__(self):
        super().__init__('hello_ros')
        self.declare_parameter('message', 'Hello from a standalone Python script')
        self.declare_parameter('max_messages', 0)  # 0: run until Ctrl+C
        self.count = 0
        self.publisher = self.create_publisher(String, 'hello', 10)
        self.timer = self.create_timer(1.0, self.publish_message)

    def publish_message(self):
        self.count += 1
        msg = String()
        msg.data = f'{self.get_parameter("message").value} ({self.count})'
        self.publisher.publish(msg)
        self.get_logger().info(msg.data)


def main():
    rclpy.init()
    node = None
    try:
        node = HelloRos()
        limit = node.get_parameter('max_messages').value
        while rclpy.ok() and (limit <= 0 or node.count < limit):
            rclpy.spin_once(node, timeout_sec=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
