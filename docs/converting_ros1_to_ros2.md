# ROS2 Conversion

To convert the rosbags from ROS1 (Noetic) to ROS2 we recommend the following steps:

1. Install the rosbags python3 package ([Documentation](https://ternaris.gitlab.io/rosbags/) / [Repository](https://gitlab.com/ternaris/rosbags))
2. Follow the steps for converting a rosbag1 to a rosbag2 listed [here](https://ternaris.gitlab.io/rosbags/topics/convert.html), or by running the following command:  
```$ rosbags-convert --src [SOURCE_ROSBAG1] --src-typestore ros1_noetic --dst [DESTINATION_ROSBAG2_FOLDER] --dst-typestore ros2_humble --dst-storage mcap```
We also provide an automated script that converts all rosbags to ROS2 under [scripts/rosbags_conversion.sh](scripts/rosbags_conversion.sh).
3. Build and source the ROS2 packages found under [scripts/rosbags2_ws](scripts/rosbags2_ws/) to replay the custom message definitions:  
```$ cd scripts/rosbags2_ws && colcon build && source install/setup.bash```

After this you should be able to play the newly created rosbags with `ros2 bag play` without any problem. The packages will allow you to read and replay our custom messages.
