import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # Path to your xacro file
    pkg_share = get_package_share_directory('extrinsics')
    xacro_file = os.path.join(pkg_share, 'urdf', 'rosario_v2.urdf.xacro')

    # Declare the 'day' argument
    day_arg = DeclareLaunchArgument(
        'day', default_value='1',
        description='Day of recording (1 for Dec 22, 2 for Dec 26)')

    # Use Command to run xacro transparently
    robot_description_content = Command([
        'xacro ', xacro_file, ' day:=', LaunchConfiguration('day')
    ])

    return LaunchDescription([
        day_arg,
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{
                'robot_description': 
                    ParameterValue(robot_description_content, value_type=str)
            }]
        ),
    ])