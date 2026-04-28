cmake_minimum_required(VERSION 3.0.0)
project(extrinsics)

find_package(catkin REQUIRED)

catkin_package()

install(DIRECTORY launch urdf
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)