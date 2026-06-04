# ROS Packages

We provide some custom ROS1/ROS2 packages to work with our dataset.


## Custom Message Definitions

Some messages recorded in the rosbags are custom made for specific sensor or log data, for this you will have to include the message definitions included in the wheel_odometry and wheel_control packages in your ROS workspace or at least have it built and sourced when running anything that would need them.
We have compiled them as ROS packages, so you can simply copy or link it to your ROS workspace to build the message interfaces.

To build the custom messages for ROS1 you can head to the `ros1_ws` folder and run:
```bash
catkin_make --only-pkg-with-deps wheel_odometry
source devel/setup.bash
```
and to build them for ROS2 you can head to the `ros2_ws` folder and run:
```bash
colcon build --packages-select wheel_odometry wheel_control
source install/setup.bash
```

If you're missing dependencies, you can install them with rosdep ([ROS1](http://wiki.ros.org/rosdep), [ROS2](https://docs.ros.org/en/foxy/Tutorials/Intermediate/Rosdep.html)).


## Extrinsic Transformations

We provide a unified URDF for the extrinsic transformations between coordinate frames of the robot.
This file, which can be found under "[data/config/rosariov2.urdf.xacro](data/config/rosariov2.urdf.xacro)", can be launched as a TF2 node that publishes the relevant transformation between coordinte frames.

**IMPORTANT:** Transformations of the gps3 (Reach M1) antenna changed between the first (Dec 22) and second (Dec 26) day of recording.
We provide a parameter to switch between these days.

To build the package with the launch file for ROS1 you can head to the `ros1_ws` folder and run:
```bash
catkin_make --only-pkg-with-deps extrinsics
source devel/setup.bash
```
then running it with
```bash
roslaunch extrinsics extrinsics.launch day:=1
# or for day 2:
roslaunch extrinsics extrinsics.launch day:=2
```

Another way is to include the launch file in a different launch file of your project with a line similar to:
```xml
<include file="$(find extrinsics)/launch/extrinsics.launch"/>
```

To build the package with the launch file for ROS2 you can head to the `ros2_ws` folder and run:
```bash
colcon build --symlink-install --packages-select extrinsics
source install/setup.bash
```
then running it with
```bash
ros2 launch extrinsics extrinsics.launch.py day:=1
# or for day 2:
ros2 launch extrinsics extrinsics.launch.py day:=2
```

You will see the topic `/tf_static` published with extrinsic transformations.
