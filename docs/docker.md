# Working With Docker

We provide files to build docker images for both ROS1 and ROS2 environments.

## Build

To build the ROS1 docker image from our dockerfile run:
```bash
docker build -f docker/ros1.Dockerfile -t "rosariov2:ros_noetic" .
```
or to build the ROS2 docker image:
```bash
docker build -f docker/ros2.Dockerfile -t "rosariov2:ros_jazzy" .
```

To build with a user having the same linux userid and groupid that you have on your local machine (recommended, as documents created in mounted volumes will be easily modifiable by the local user) for ROS1:
```bash
docker build --build-arg USER_ID=$(id -u ${USER}) --build-arg GROUP_ID=$(id -g ${USER}) --build-arg USER_NAME=${USER} -f docker/ros1.Dockerfile -t "rosariov2:ros_noetic" .
```
or for ROS2:
```bash
docker build --build-arg USER_ID=$(id -u ${USER}) --build-arg GROUP_ID=$(id -g ${USER}) --build-arg USER_NAME=${USER} -f docker/ros2.Dockerfile -t "rosariov2:ros_jazzy" .
```
then you should be able to run any scripts by running the image in interactive mode.

## Run

We assume that you have the directory with the dataset set in the `$ROSARIOV2` environment variable, otherwise set it or replace the variable with the path to the dataset on your local machine, then for ROS1:
```bash
xhost +local:root &&\
docker run -it --rm --env DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v${ROSARIOV2}:/rosariov2/dataset/ -v$(pwd):/rosariov2/scripts/ rosariov2:ros_noetic bash &&\
xhost -local:root
```
and for ROS2:
```bash
xhost +local:root &&\
docker run -it --rm --env DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v${ROSARIOV2}:/rosariov2/dataset/ -v$(pwd):/rosariov2/scripts/ rosariov2:ros_jazzy bash &&\
xhost -local:root
```

These commands will run the docker image, with access to the display (so it can open graphical displays if you run any), and mounting the `$ROSARIOV2` local path into the `/rosariov2/dataset` virtual path, as well as the current directory into the `/rosariov2/scripts` virtual folder.
The xhost commands allow for graphical interfaces inside docker to display on your local display.

You can mount any number of local volumes as you see fit to generate additional output, save images or read in additional information.
