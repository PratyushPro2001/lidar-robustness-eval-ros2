#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    scan_topic = LaunchConfiguration('scan_topic')
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            'scan_topic',
            default_value='/scan',
            description='LaserScan topic to feed into slam_toolbox'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock'
        ),

        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time},
                {'odom_frame': 'odom'},
                {'map_frame': 'map'},
                {'base_frame': 'base_footprint'},
                {'scan_topic': '/scan'},
                {'resolution': 0.05},
                {'max_laser_range': 3.5},
                {'minimum_time_interval': 0.5},
                {'transform_publish_period': 0.05},
                {'map_update_interval': 2.0},
            ],
            remappings=[
                ('/scan', scan_topic),
            ]
        )
    ])
