# The Rosario Dataset v2 Accompanying Scripts

These files provide utilities to work with the dataset published in:
```text
@article{doi:10.1177/02783649251368909,
  author = {Nicolás Soncini and Javier Cremona and Erica Vidal and Maximiliano García and Gastón Castro and Taihú Pire},
  title ={The Rosario dataset v2: Multi-modal dataset for agricultural robotics},
  journal = {The International Journal of Robotics Research},
  year = {2025},
  pages = {02783649251368909},
  doi = {10.1177/02783649251368909},
  URL = {https://doi.org/10.1177/02783649251368909}
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

**IMPORTANT:** Transformations of the gps3 (Reach M1) antenna changed between the first (Dec 22) and second (Dec 26) day of recording.
We provided separate launch files for each of these days (`allTransformationsDay1` and `allTransformationsDay2`), or you can launch the `sensorBoxTransformations` with the appropiate argument (`day:=1` or `day:=2`).

To build the package it would suffice with including it on your ROS workspace and running:
```bash
catkin build extrinsics
source devel/setup.bash
```
then running it with
```
roslaunch extrinsics allTransformationsDayX.launch
```

Another way is to include the launch file in a different launch file of your project with a line similar to:
```xml
<include file="$(find extrinsics)/launch/allTransformationsDayX.launch"/>
```

## ROS Messages

Some messages recorded in the rosbags are custom made for specific sensor or log data, for this you will have to include the message definitions included in the [wheel_odometry/](wheel_odometry/) folder in your ROS workspace or at least have it built and sourced when running anything that would need them.
We have compiled them as a ROS package, so you can simply copy or link it to your ROS workspace to build the message interfaces.

To build the package it would suffice with including it on your ROS workspace and running:
```bash
catkin build wheel_odometry
source devel/setup.bash
```

## ROS2 Conversion

To convert the rosbags from ROS1 (Noetic) to ROS2 we recommend the following steps:

1. Install the rosbags python3 package ([Documentation](https://ternaris.gitlab.io/rosbags/) / [Repository](https://gitlab.com/ternaris/rosbags))
2. Follow the steps for converting a rosbag1 to a rosbag2 listed [here](https://ternaris.gitlab.io/rosbags/topics/convert.html), or by running the following command:  
```$ rosbags-convert --src [SOURCE_ROSBAG1] --src-typestore ros1_noetic --dst [DESTINATION_ROSBAG2_FOLDER] --dst-typestore ros2_humble```  
We also provide an automated script that converts all rosbags to ROS2 under [scripts/rosbags_conversion.sh](scripts/rosbags_conversion.sh).
3. Build and source the ROS2 packages found under [scripts/rosbags2_ws](scripts/rosbags2_ws/) to replay the custom message definitions:  
```$ cd scripts/rosbags2_ws && colcon build && source install/setup.bash```

After this you should be able to play the newly created rosbags with `ros2 bag play` without any problem. The packages will allow you to read and replay our custom messages.

## Experimental Evaluation

Configurations for the multi-modal SLAM systems ran in the experimental evaluation section of the paper can be found under the [evaluation/](evaluation/) folder.
We assume that you have the path to the rosbag under the environment value `$ROSARIOV2`, for example:

```bash
export ROSARIOV2=/home/$USER/rosariov2/sequences/2023-12-22-13-14-16.bag
```

### ORB-SLAM3
[Repository](https://github.com/CIFASIS/ORB_SLAM3)

After copying (evaluation/orb-slam3_rosariov2.launch)[evaluation/orb-slam3_rosariov2.launch] into the `ORB_SLAM3/Examples/ROS/ORB_SLAM3/launch/` folder, and copying (evaluation/orb-slam3_rosariov2.yaml)[evaluation/orb-slam3_rosariov2.yaml] into the newly created `ORB_SLAM3/Examples/ROS/ORB_SLAM3/config/` folder, run:

```bash
# Check additional parameters with: ./run.sh -h
./run.sh -l orb-slam3_rosariov2.launch &\
rosbag play -d 10 --clock $ROSARIOV2
```

Check the original repository for instructions on building, and running inside a Docker container.

### ORB-SLAM3+GNSS
[Repository](https://github.com/CIFASIS/gnss-stereo-inertial-fusion)

After copying (evaluation/orb-slam3-gnss_rosariov2.launch)[evaluation/orb-slam3-gnss_rosariov2.launch] into the `gnss-stereo-inertial-fusion/Examples/ROS/GNSS_SI/launch` folder, creating the folder `gnss-stereo-inertial-fusion/Examples/Stereo-Inertial/rosariov2`, and copying there the file (evaluation/orb-slam3-gnss_rosariov2.yaml)[evaluation/orb-slam3-gnss_rosariov2.yaml], run:

```bash
./run.sh -s Examples/Stereo-Inertial/rosariov2/orb-slam3-gnss_rosariov2.yaml -l Examples/ROS/GNSS_SI/launch/orb-slam3-gnss_rosariov2.launch $ROSARIOV2
```

Check the original repository for instructions on building, and running inside a Docker container.

### OpenVINS
[Repository](https://github.com/rpng/open_vins/)

After copying (evaluation/open-vins_rosariov2.launch)[evaluation/open-vins_rosariov2.launch] under `open_vins/ov_msckf/launch/`, creating the folder `open_vins/config/rosariov2`, and copying there the files (evaluation/open-vins_estimator_rosariov2.yaml)[evaluation/open-vins_estimator_rosariov2.yaml], (evaluation/open-vins_imuchain_rosariov2.yaml)[evaluation/open-vins_imuchain_rosariov2.yaml], and (evaluation/open-vins_imucam_rosariov2.yaml)[evaluation/open-vins_imucam_rosariov2.yaml], run:

```bash
# Check documentation on https://docs.openvins.com/
roslaunch ov_msckf evaluation/open-vins_rosariov2.launch bag:=$ROSARIOV2
```

Check the files to modify the resulting output paths. We opted to write all results into the `/tmp` folder.

## License

All data in the Rosario Dataset v2 is licensed under a [Creative Commons 4.0 Attribution License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) and the accompanying source code is licensed under a [BSD-2-Clause License](https://opensource.org/license/BSD-2-Clause).
Please make sure to check the license terms of use and attribution on the [LICENSE](LICENSE) file included in this repository.
