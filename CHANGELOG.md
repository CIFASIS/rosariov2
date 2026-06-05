# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Changed

- Fixed the ROS1 "Distances" message definition. 
- Added script and documentation about the Odometry fix.


## [1.2.0] - 2026-04-28

### Added

- Separated ROS1 and ROS2 files and workspaces
- Made a common representation for the robot extrinsic transformations
- Moved the documentation to separate files into a dedicated folder
- Separated the common data into its own folder
- Moved the dockerfiles into a custom folder and added a ROS2 Dockerfile


## [1.1.0] - 2025-09-05

### Added

- ROS2 conversion steps and script
- ROS2 version of the custom messages


## [1.0.0] - 2025-06-01

Initial Release of the tools

### Added

- This repository, to provide useful tools to work with "The Rosario Dataset v2"
- Scripts to work with the dataset
- Documentation to work with the scripts
- A Dockerfile to run the scripts even in incompatible local configurations
- A License file to protect contributors and users of the tools


[unreleased]: https://github.com/CIFASIS/rosariov2/tree/master