cmake_minimum_required(VERSION 2.8.3)
project(ri_packing)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  actionlib_msgs
  geometry_msgs
  shape_msgs
)

catkin_python_setup()

# catkin_install_python(PROGRAMS bin/packaging_action_srv.py DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})


## Generate actions in the 'action' folder
add_action_files(
  FILES
  Packing.action
)

## Generate added messages and services with any dependencies listed here
generate_messages(
  DEPENDENCIES
  actionlib_msgs
  geometry_msgs
  shape_msgs
  std_msgs
)

catkin_package(
  CATKIN_DEPENDS rospy std_msgs actionlib_msgs geometry_msgs shape_msgs
)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations
include_directories(
  ${catkin_INCLUDE_DIRS}
)

