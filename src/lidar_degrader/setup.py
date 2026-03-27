from setuptools import find_packages, setup
from glob import glob

package_name = 'lidar_degrader'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pratyush',
    maintainer_email='pratyush@example.com',
    description='Simple LiDAR degradation and mission runner tools',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'lidar_degrader_node = lidar_degrader.lidar_degrader_node:main',
            'mission_runner = lidar_degrader.mission_runner:main',
            'odom_to_path = lidar_degrader.odom_to_path:main',
        ],
    },
)
