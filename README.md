# The Rosario Dataset v2 Accompanying Scripts

These files provide utilities to work with the dataset published in:
```text
@unpublished{rosariodatasetv2,
  title  = {The Rosario Dataset v2: Multimodal Dataset for Agricultural Robotics},
  author = {Nicolás Soncini and Javier Cremona and Erica Vidal and Maximiliano García and Gastón Castro and Taihú Pire},
  note   = {Submitted to The International Journal of Robotics Research (IJRR)},
  month  = {},
  year   = {2025},
  annote = {}
}
```
please cite our work if you use these utilities and/or the dataset itself.

The dataset will be made available once the publication goes through.
Any changes made to the scripts, as well as the data included in the dataset, will be made explicit in the [CHANGELOG.md](CHANGELOG.md) file included in this repository.
A copy of this file should have also been provided along with the dataset itself.


## Usage

The dataset is provided in a combination of ROS rosbags and plain files.
To work with the ROS rosbags you should have a working ROS version installed.
A [Dockerfile](Dockerfile) has also been provided to build and run the scripts without a local ROS installation, please refer to the [Working with Docker](#working-with-docker) section.
The docker image has all the requirements ready for inspecting the rosbags, as well as running the provided scripts refered to in the [Running Scripts](#running-scripts)


## Running Scripts

To run the scripts inside the [scripts/](scripts/) folder you are probably going to need to be inside a ROS environment.
You can check if this is the case for the script you want to run by verifying if any ros-related packages are being imported at the beginning (such as the `rosbag` package).

To run the scripts we recommend creating a virtual environment and installing the dependencies presented in the [requirements.txt](scripts/requirements.txt) file with pip:
```bash
# create virtual environment and activate it
python3 -m venv venv
source venv/bin/activate
# install requirements
pip3 install -r scripts/requirements.txt
```

All scripts can be run with the `--help` parameter to display the description and arguments they take in, such as:
```bash
python3 scripts/extract_rosbag_data.py --help
```
we recommend reading this description to understand how the script works before running any commands.


## Working With Docker

To build the docker image from our dockerfile run:
```bash
docker build -t "rosariov2:ros_humble"
```
or to build with a user having the same linux userid and groupid that you have on your local machine (recommended, as documents created in mounted volumes will be easily modifiable by the local user):
```bash
docker build --build-arg USER_ID=$(id -u ${USER}) --build-arg GROUP_ID=$(id -g ${USER}) --build-arg USER_NAME=${USER} -t "rosariov2:ros_humble" .
```
then you should be able to run any scripts by running the image in interactive mode.

We assume that you have the directory with the dataset set in the `$ROSARIOV2` environment variable, otherwise set it or replace the variable with the path to the dataset on your local machine:
```bash
xhost +local:root &&\
docker run -it --rm --env DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v${ROSARIOV2}:/data/rosariov2 -v$(pwd):/scripts/rosariov2 rosariov2:ros_humble bash &&\
xhost -local:root
```
which will run the docker image, with access to the display (so it can open graphical displays if you run any), and mounting the `$ROSARIOV2` local path into the `/data/rosariov2` virtual path, as well as the current directory into the `/scripts/rosariov2` virtual folder.
The xhost commands allow for graphical interfaces inside docker to display on your local display.

You can mount any number of local volumes as you see fit to generate additional output, save images or read in additional information.


## ROS Transformations

A simple ROS module with the transformations between coordinate frames of the robot is provided in the [extrinsics/](extrinsics/) folder.
The ROS launch files spawn tf2_ros nodes that publish the relevant transformations between coordinate frames.

To build the package it would suffice with including it on your ROS workspace and running:
```bash
catkin build extrinsics
source devel/setup.bash
```
then running it with
```
roslaunch extrinsics allTransformations.launch
```

Another way is to include the launch file in a different launch file of your project with a line similar to:
```xml
<include file="$(find extrinsics)/launch/allTransformations.launch"/>
```

## ROS Messages

Some messages recorded in the rosbags are custom made for specific sensor or log data, for this you will have to include the message definitions included in the [wheel_odometry/](wheel_odometry/) folder in your ROS workspace or at least have it built and sourced when running anything that would need them.
We have compiled them as a ROS package, so you can simply copy or link it to your ROS workspace to build the message interfaces.

To build the package it would suffice with including it on your ROS workspace and running:
```bash
catkin build wheel_odometry
source devel/setup.bash
```


## License

All data in the Rosario Dataset v2 is licensed under a [Creative Commons 4.0 Attribution License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) and the accompanying source code is licensed under a [BSD-2-Clause License](https://opensource.org/license/BSD-2-Clause).
Please make sure to check the license terms of use and attribution on the [LICENSE](LICENSE) file included in this repository.
