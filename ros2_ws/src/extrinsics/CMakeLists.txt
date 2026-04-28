cmake_minimum_required(VERSION 3.8)
project(extrinsics)

find_package(ament_cmake REQUIRED)

# Install launch and urdf folders
install(DIRECTORY launch urdf
  DESTINATION share/${PROJECT_NAME}
)

ament_package()