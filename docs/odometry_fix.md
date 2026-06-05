# Odometry Fix

When working with odometry data we found out there were two errors in the way in which the velocity component was recorded.

We have uploaded separate .bag files that contain the corrected odometry as a new topic appropiately named `/odom_fix`.
These rosbags can be found with the suffix "*_odom_fix.bag*", and can be combined with the original rosbags using our merge script.

The script that generated this new bags can be found under ROS1 scripts as: [fix_odom_vel.py](/ros1_ws/src/ros1_scripts/fix_odom_vel.py).
It requires the wheel_odometry package built and sourced in a ROS1 workspace, and the corresponding requirements installed.

## The Twist Issue

We record the [nav_msgs/Odometry](https://docs.ros.org/en/noetic/api/nav_msgs/html/msg/Odometry.html) message linear twist component in a global frame of reference, instead of the local robot coordinate frame of reference.

The Odometry message clearly specifies:

> [The Odometry message] represents an estimate of a position and velocity in free space. The pose in this message should be specified in the coordinate frame given by header.frame_id. The twist in this message should be specified in the coordinate frame given by the child_frame_id.

**How we fix it**

Our script re-computes the velocity of the robot by reading the raw wheels sensors output, computing the velocity, and writing it as the 'x' component of the linear twist on the new odometry topic. 


## The Direction Issue

We record the direction of movement by looking at the direction of the command sent by the (remote) control to the robot.
When trying to stop the movement of the robot we prevent the robot from continuing its movement due to inertia by sending the wheel motors a reverse command for a brief period of time.
This causes the Odometry to record the robot as moving backwards, instead of showing it as moving slower until stopping.

**How we fix it**

We recompute the sign of the linear twist of the new odometry topic.
We detect this "active breaking" by checking if we're slowing down when a change in direction is reversed.
If so, we keep the old direction until we start accelerating again.
This basically computes the sign of the 'x' component of the linear twist on our new odometry topic.