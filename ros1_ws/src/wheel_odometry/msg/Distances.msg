# This message indicates how many pulses have been counted since
# the robot was started. A pulse is equivalent to 1/46th of wheel turn.
# This is obtained directly from the microcontroller driving the robot.

std_msgs/Header header
uint32 pulses
float32 angle
int32 direction
string odometry_raw