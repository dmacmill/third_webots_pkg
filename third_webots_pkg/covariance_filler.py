import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry

class CovarianceFiller(Node):
    def __init__(self):
        super().__init__('covariance_filler')
        
        # Declare parameters for topic names
        self.imu_input_topic = self.declare_parameter('imu_input_topic', '/imu')
        self.imu_output_topic = self.declare_parameter('imu_output_topic', '/imu_fixed')
        self.odom_input_topic = self.declare_parameter('odom_input_topic', '/diffdrive_controller/odom')
        self.odom_output_topic = self.declare_parameter('odom_output_topic', '/diffdrive_controller/odom_fixed')
        
        # Create subscriptions and publishers using parameters
        self.create_subscription(Imu, self.imu_input_topic.value, self.imu_cb, 10)
        self.create_subscription(Odometry, self.odom_input_topic.value, self.odom_cb, 10)
        self.imu_pub = self.create_publisher(Imu, self.imu_output_topic.value, 10)
        self.odom_pub = self.create_publisher(Odometry, self.odom_output_topic.value, 10)

    def imu_cb(self, msg: Imu):
        msg.orientation_covariance = [0.001,0.0,0.0, 0.0,0.001,0.0, 0.0,0.0,0.001]
        msg.angular_velocity_covariance = [0.1,0.0,0.0, 0.0,0.1,0.0, 0.0,0.0,0.1]
        msg.linear_acceleration_covariance = [0.1,0.0,0.0, 0.0,0.1,0.0, 0.0,0.0,0.1]
        self.imu_pub.publish(msg)

    def odom_cb(self, msg: Odometry):
        # Pose covariance diagonals:
        # x, y, z, rotation about x, rotation about y, rotation about z
        msg.pose.covariance = [0.05,0.0,0.0,0.0,0.0,0.0,
                                0.0,0.05,0.0,0.0,0.0,0.0,
                                0.0,0.0,0.0,0.0,0.0,0.0, 
                                0.0,0.0,0.0,0.0,0.0,0.0, 
                                0.0,0.0,0.0,0.0,0.0,0.0, 
                                0.0,0.0,0.0,0.0,0.0,0.1]
        # Twist covariance diagonals:
        # x, y, z, rotation about x, rotation about y, rotation about z
        msg.twist.covariance = [0.1,0.0,0.0,0.0,0.0,0.0,
                                0.0,0.0,0.0,0.0,0.0,0.0,
                                0.0,0.0,0.0,0.0,0.0,0.0, 
                                0.0,0.0,0.0,0.0,0.0,0.0, 
                                0.0,0.0,0.0,0.0,0.0,0.0, 
                                0.0,0.0,0.0,0.0,0.0,0.1]
        self.odom_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = CovarianceFiller()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()