"""
third_webots_driver - node

inverse kinematics
cmd_vel ->  left & right wheel velocities node for a webots robot using diff drive. 

"""

import rclpy
from geometry_msgs.msg import Twist

HALF_TRACK = 0.045
WHEEL_RADIUS = 0.025

class ThirdWebotsDriver:
	"""
	init()
	- get left and right motors named "left wheel motor" and "right wheel motor"
	- set their initial conditions, velocities to 0
	- subscribes to cmd_vel.
	"""
	def init(self, webots_node, properties):
		self.__robot = webots_node.robot
		
		self.__left_motor = self.__robot.getDevice('left wheel motor')
		self.__right_motor = self.__robot.getDevice('right wheel motor')
		
		self.__left_motor.setPosition(float('inf'))
		self.__left_motor.setVelocity(0)
		self.__right_motor.setPosition(float('inf'))
		self.__right_motor.setVelocity(0)
		
		self.__target_twist = Twist()
		
		rclpy.init(args=None)
		self.__node = rclpy.create_node('third_webots_driver_node')
		self.__node.create_subscription(Twist, 'cmd_vel', self.__cmd_vel_callback, 1)
		
	"""
	- store target twist velocities
	"""
	def __cmd_vel_callback(self, twist):
		self.__target_twist = twist
	
	"""
	step():
	- gets called in a loop somewhere
	- retrieve target forward / angular vels
	- set what the corresponding target left & right wheel vels should be based on 
	  a diff drive robot.
	"""
	def step(self):
		rclpy.spin_once(self.__node, timeout_sec=0)
		
		forward_speed = self.__target_twist.linear.x
		angular_speed = self.__target_twist.angular.z
		
		command_motor_left = (forward_speed - angular_speed * HALF_TRACK) / WHEEL_RADIUS
		command_motor_right = (forward_speed + angular_speed * HALF_TRACK) / WHEEL_RADIUS
		
		self.__left_motor.setVelocity(command_motor_left)
		self.__right_motor.setVelocity(command_motor_right)
