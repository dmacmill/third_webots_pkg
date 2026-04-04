from setuptools import find_packages, setup

package_name = 'third_webots_pkg'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name + '/launch', ['launch/robot_launch.py']),              # remember these
        ('share/' + package_name + '/launch', ['launch/mapping_launch.py']),
	    ('share/' + package_name + '/worlds', ['worlds/my_world.wbt']),                 # in future 
	    ('share/' + package_name + '/resource', [
            'resource/third_webots_robot.urdf',
            'resource/robot_model.urdf'
        ]),
        ('share/' + package_name + '/config', [
            'config/ekf.yaml',
            'config/mapper_params_online_async.yaml',
            'config/ros2control.yml',
        ]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='daniel',
    maintainer_email='dmacmi.dm@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'third_webots_driver = third_webots_pkg.third_webots_driver:main'
        ],
    },
)
