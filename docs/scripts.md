# Running Scripts

To run the scripts inside the scripts folders [ros1_ws/ros1_scripts](ros1_ws/ros1_scripts) or [ros2_ws/ros2_scripts](ros2_ws/ros2_scripts) you are probably going to need to be inside the corresponding ROS1 or ROS2 environment, respectively.
You can check if this is the case for the script you want to run by verifying if any ros-related packages are being imported at the beginning (such as the `rosbag`, `rospy` or `rclpy` packages).

The scripts can be run inside the docker environments directly by installing the dependencies listed in the corresponding requirements.txt files in the folder:
```bash
pip3 install -r scripts/requirements.txt
```
You can also create a virtual environment to isolate dependencies. Useful if running it inside your own machine:
```bash
# install the virtual environment manager
sudo apt install python3-venv
# create virtual environment and activate it
python3 -m venv venv
source venv/bin/activate
# install requirements
pip3 install -r scripts/requirements.txt
```

All scripts can be run with the `--help` parameter to display the description and arguments they take in, such as:
```bash
python3 ros1_ws/src/ros1_scripts/extract_rosbag_data.py --help
```
we recommend reading this description to understand how the script works before running any commands.
