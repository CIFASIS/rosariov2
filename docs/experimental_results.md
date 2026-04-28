# Experimental Evaluation

Configurations for the multi-modal SLAM systems ran in the experimental evaluation section of the paper can be found under the [evaluation/](evaluation/) folder.
We assume that you have the path to the rosbag under the environment value `$ROSARIOV2`, for example:

```bash
export ROSARIOV2=/home/$USER/rosariov2/sequences/2023-12-22-13-14-16.bag
```

## ORB-SLAM3
[Repository](https://github.com/CIFASIS/ORB_SLAM3)

After copying (evaluation/orb-slam3_rosariov2.launch)[evaluation/orb-slam3_rosariov2.launch] into the `ORB_SLAM3/Examples/ROS/ORB_SLAM3/launch/` folder, and copying (evaluation/orb-slam3_rosariov2.yaml)[evaluation/orb-slam3_rosariov2.yaml] into the newly created `ORB_SLAM3/Examples/ROS/ORB_SLAM3/config/` folder, run:

```bash
# Check additional parameters with: ./run.sh -h
./run.sh -l orb-slam3_rosariov2.launch &\
rosbag play -d 10 --clock $ROSARIOV2
```

Check the original repository for instructions on building, and running inside a Docker container.

## ORB-SLAM3+GNSS
[Repository](https://github.com/CIFASIS/gnss-stereo-inertial-fusion)

After copying (evaluation/orb-slam3-gnss_rosariov2.launch)[evaluation/orb-slam3-gnss_rosariov2.launch] into the `gnss-stereo-inertial-fusion/Examples/ROS/GNSS_SI/launch` folder, creating the folder `gnss-stereo-inertial-fusion/Examples/Stereo-Inertial/rosariov2`, and copying there the file (evaluation/orb-slam3-gnss_rosariov2.yaml)[evaluation/orb-slam3-gnss_rosariov2.yaml], run:

```bash
./run.sh -s Examples/Stereo-Inertial/rosariov2/orb-slam3-gnss_rosariov2.yaml -l Examples/ROS/GNSS_SI/launch/orb-slam3-gnss_rosariov2.launch $ROSARIOV2
```

Check the original repository for instructions on building, and running inside a Docker container.

## OpenVINS
[Repository](https://github.com/rpng/open_vins/)

After copying (evaluation/open-vins_rosariov2.launch)[evaluation/open-vins_rosariov2.launch] under `open_vins/ov_msckf/launch/`, creating the folder `open_vins/config/rosariov2`, and copying there the files (evaluation/open-vins_estimator_rosariov2.yaml)[evaluation/open-vins_estimator_rosariov2.yaml], (evaluation/open-vins_imuchain_rosariov2.yaml)[evaluation/open-vins_imuchain_rosariov2.yaml], and (evaluation/open-vins_imucam_rosariov2.yaml)[evaluation/open-vins_imucam_rosariov2.yaml], run:

```bash
# Check documentation on https://docs.openvins.com/
roslaunch ov_msckf evaluation/open-vins_rosariov2.launch bag:=$ROSARIOV2
```

Check the files to modify the resulting output paths. We opted to write all results into the `/tmp` folder.