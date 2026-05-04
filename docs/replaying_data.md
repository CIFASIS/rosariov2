# Replaying the data

To inspect all the sequences of the dataset there is some setup needed beforehand

## Requirements

- ROS1/ROS2 installation (ROS1: [installation page](https://wiki.ros.org/Installation) / ROS2: [installation page](https://docs.ros.org/en/jazzy/Installation.html))

We also provide docker images already setup: [Working with Docker](./docker.md)

## ROS Packages

The sequences have custom messages, and we also provide the extrinsic transformations.
Before being able to play the rosbags, follow the [ROS Packages docs](./ros_packages.md)

## Playing the rosbags

### ROS1

To play the rosbags, run `rosbag play [SEQUENCE.bag]`.

### ROS2

In ROS2 the rosbags format changed, so we need to convert them into 'mcap's before being able to play them.
Follow the [Convert from ROS1 to ROS2 docs](./converting_ros1_to_ros2.md).

Once this is done, play the rosbags by running `ros2 bag play [SEQUENCE.bag]`

## Extracting the data

If you don't have a ROS distribution available, you can use the 'extract_rosbag_data.py' python3 script in 'ros1_ws/src/ros1_scripts/' to extract the data from the rosbags and use them without ROS.
Before being able to run it, you should follow the [Scripts docs](./scripts.md)
