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

The official website for the dataset is: https://cifasis.github.io/rosariov2/
Any changes made to the scripts will be made explicit in the [CHANGELOG.md](CHANGELOG.md) file included in this repository.
Any changes made to the dataset will be made explicit in the [CHANGELOG.md](http://fs01.cifasis-conicet.gov.ar:90/~robot_desmalezador/rosariov2/CHANGELOG.md) file provided with the dataset.


## Usage

The dataset is provided in a combination of ROS rosbags and plain files.
To work with the ROS rosbags you should have a working ROS version installed.
Docker files have been provided to build and run the scripts without a local ROS1 or ROS2 installation, please refer to the documentation below.
The docker images have all the requirements ready for inspecting the rosbags, as well as running the provided scripts refered below.

These instructions have been tested on ROS Noetic (ROS1) and ROS Jazzy (ROS2).


## Documentation

- [Working With Docker](docs/docker.md): dockerfiles are provided to run in fully isolated ROS1 or ROS2 environments.
- [ROS1 to ROS2 Conversion](docs/converting_ros1_to_ros2.md): provides steps on how to convert our data provided in ROS1 rosbags, into ROS2 rosbags.
- [ROS Packages](docs/ros_packages.md): provides instructions on how to build and use our custom packages, such as custom message definitions and extrinsic transformations.
- [Scripts](docs/scripts.md): introduces the helping scripts we provide and how to run them.
- [Experimental Results](docs/experimental_results.md): explains how we obtained our experimental results for the different SLAM systems, and how to reproduce them.


## License

All data in the Rosario Dataset v2 is licensed under a [Creative Commons 4.0 Attribution License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) and the accompanying source code is licensed under a [BSD-2-Clause License](https://opensource.org/license/BSD-2-Clause).
Please make sure to check the license terms of use and attribution on the [LICENSE](LICENSE) file included in this repository.
