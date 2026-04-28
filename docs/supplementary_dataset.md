# Supplementary dataset

These files provide utilities to work with the supplementary dataset published as part of  Rosario Dataset v2. The rosbag files of the supplementary dataset were recorded two years before the primary dataset was collected. Please note that the robot platform has changed since then, so sensor configurations, topics, or frame definitions may differ from those in the main dataset.

## ROS Transformations

A simple ROS module with the transformations between coordinate frames of the robot is provided in the [extrinsics/](extrinsics/) folder.
The ROS launch files spawn tf2_ros nodes that publish the relevant transformations between coordinate frames.

**IMPORTANT:** these transformations differ from those in the primary dataset.