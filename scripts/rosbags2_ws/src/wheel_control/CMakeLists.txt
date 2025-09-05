cmake_minimum_required(VERSION 3.8)
project(wheel_control)

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

# Generate the message interfaces
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/WheelControl.msg"
  DEPENDENCIES std_msgs
)

# Export runtime deps so type support libs get installed
ament_export_dependencies(rosidl_default_runtime)

ament_package()
