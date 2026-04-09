import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry

class ImuCovarianceFiller(Node):
    def __init__(self):
        super().__init__('covariance_filler')
        
        # Declare parameters for topic names
        self.imu_input_topic = self.declare_parameter('imu_input_topic', '/imu')
        self.imu_output_topic = self.declare_parameter('imu_output_topic', '/imu_fixed')
        
        # Create subscriptions and publishers using parameters
        self.create_subscription(Imu, self.imu_input_topic.value, self.imu_cb, 10)
        self.imu_pub = self.create_publisher(Imu, self.imu_output_topic.value, 10)

    def imu_cb(self, msg: Imu):
        msg.orientation_covariance = [0.0001,0.0,0.0, 0.0,0.0001,0.0, 0.0,0.0,0.0001]
        msg.angular_velocity_covariance = [0.05,0.0,0.0, 0.0,0.05,0.0, 0.0,0.0,0.05]
        msg.linear_acceleration_covariance = [0.05,0.0,0.0, 0.0,0.05,0.0, 0.0,0.0,0.05]
        self.imu_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ImuCovarianceFiller()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()