"""
BSD 2-Clause License

This file is part of The Rosario Dataset v2 project.
https://github.com/CIFASIS/rosariov2

Copyright (c) 2025, Centro Internacional Franco-Argentino de Ciencias de la Información y Sistemas (CIFASIS)

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

"""
Tool to extract the rosbag (ROS1) data into standalone elements/files.
NOTE: will overwrite folders/files already created with the same names.
"""
import argparse
import csv
import cv2
import os
import rosbag
from cv_bridge import CvBridge
from pathlib import Path
from typing import List, Dict


SCRIPT_DESCRIPTION = \
    "This script allows the extraction of the rosbag data format to plain" \
    " files and directories for ease of working with it. The folders will be" \
    " created where the user specifies and any existing data with the exact" \
    " same file name as the data created will be overwritten." \
    "\nWe recommend extracting the files to an empty folder." \
    "\nThe script requires ROS1 to be installed. We recommend using the" \
    " dockerfile provided with the repository to avoid having to install" \
    " ROS1 permanently, and to avoid any clash of versions." \
    "\nThe files are extracted in the ASL Dataset Format, which is the" \
    " same format that the EuRoC MAV dataset uses." 

OUTPUT_STRUCTURE = \
    """
    data/
    ├── rosariov2/
    │   ├── 2023-12-22-13-14-16/
    │       |── realsense/
    │           |── color/ : folder with RealSense color camera data
    |           |── infra1/ : folder with RealSense left infra camera data
    │           |── infra2/ : folder with RealSense right infra camera data
    |           └── imu.csv: file with RealSense IMU data
    │       |── reach1/
    │           |── fix.csv : file with Reach M2 RTK-GPS data
    |           |── imu.csv : file with Reach M2 IMU data
    |           |── mag.csv : file with Reach M2 Magnetometer data
    |           |── vel.csv : file with Reach M2 RTK-GPS Velocity data
    |           |── spp.csv : file with Reach M2 SPP-GPS data
    |           |── spp_vel.csv : file with Reach M2 SPP-GPS Velocity data
    |           |── ppk.csv : file with Reach M2 PPK-GPS data
    |           └── ppk_vel.csv : file with Reach M2 PPK-GPS Velocity data
    │       |── reach2/ : same contents as reach1, for the second Reach M2
    │       |── reach3/ : same contentsas reach1, for the Reach M1
    |       └── odom/ : folder with wheel odometry data  (TODO)
    │   ├── 2023-12-22-14-29-43/
    │   ├── 2023-12-22-16-31-08/
    │   ├── 2023-12-26-13-39-43/
    │   ├── 2023-12-26-15-10-15/
    │   └── 2023-12-26-15-48-38/
    """


cv_bridge = CvBridge()


class MsgProcessor:

    def __init__(self):
        super().__init__()

    def process_message(self, msg, t):
        raise NotImplementedError()
    
    def destroy(self):
        pass
    

class Msg2CSVProcessor(MsgProcessor):
    header : List[str] = []

    def __init__(self, path = None, header = None, mode = 'w+'):
        if path:
            self.save_path = path
        os.makedirs(self.save_path.parent, exist_ok=True)
        if header:
            self.header = header
        self.f_csv = open(self.save_path, mode, newline='')
        if not self.f_csv:
            raise RuntimeError(
                f"Unable to create CSV file in {self.save_path}")
        self.writer = csv.writer(self.f_csv)
        self.writer.writerow(self.header)

    def destroy(self):
        self.f_csv.close()
    

class ImageProcessor(MsgProcessor):
    save_path: str = "images/"
    count: int = 0

    def __init__(self, path = None):
        if path:
            self.save_path = path
        os.makedirs(self.save_path, exist_ok=True)

    def process_message(self, msg, t):
        cv_img = cv_bridge.imgmsg_to_cv2(msg)
        if len(cv_img.shape) == 3:
            cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
        filename = self.save_path / self._filename_nsec(msg)
        cv2.imwrite(filename, cv_img)
        self.count += 1

    @staticmethod
    def _filename_nsec(msg):
        """ Returns a filename from the timestamp in nanoseconds """
        return f'{msg.header.stamp.to_nsec()}.png'
    
    @staticmethod
    def _filename_seq(msg):
        """ Returns a filename from the sequence id (uint32) """
        return f'{msg.header.seq}.png'
    
    def _filename_count(self, msg):
        """ Returns a filename from an internally increasing count """
        return f'{self.count}.png'


class NavSatFixProcessor(Msg2CSVProcessor):
    save_path: str = "navsatfix.csv"
    header: List[str] = [
        "nsec", "status", "service",
        "latitude", "longitude", "altitude",]
        # "position_covariance", "position_covariance_type"]

    def process_message(self, msg, t):
        row = [
            msg.header.stamp.to_nsec(), 
            msg.status.status, msg.status.service
            ] + [getattr(msg, e) for e in self.header[3:]]
        self.writer.writerow(row)


class IMUProcessor(Msg2CSVProcessor):
    save_path: str = "imu.csv"
    header: List[str] = [
        "nsec",
        "orientation", "orientation_covariance",
        "angular_velocity", "angular_velocity_covariance",
        "linear_acceleration", "linear_acceleration_covariance"]

    def process_message(self, msg, t):
        orientation = [
            msg.orientation.x, 
            msg.orientation.y, 
            msg.orientation.z,
            msg.orientation.w
        ]
        angular_velocity = [
            msg.angular_velocity.x, 
            msg.angular_velocity.y, 
            msg.angular_velocity.z
        ]
        linear_acceleration = [
            msg.linear_acceleration.x, 
            msg.linear_acceleration.y, 
            msg.linear_acceleration.z
        ]

        row = [
            msg.header.stamp.to_nsec(),
            orientation,
            msg.orientation_covariance,
            angular_velocity,
            msg.orientation_covariance,
            linear_acceleration,
            msg.orientation_covariance,
        ]
        self.writer.writerow(row)


class OdometryProcessor(Msg2CSVProcessor):
    save_path: str = "odometry.csv"

    def process_message(self, msg, t):
        pass


class MagneticFieldProcessor(Msg2CSVProcessor):
    save_path: str = "magnetic_field.csv"
    header: List[str] = [
        "nsec",
        "magnetic_field", "magnetic_field_covariance"]

    def process_message(self, msg, t):
        magnetic_field = [
            msg.magnetic_field.x,
            msg.magnetic_field.y,
            msg.magnetic_field.z
        ]

        row = [
            msg.header.stamp.to_nsec(), 
            magnetic_field,
            msg.magnetic_field_covariance
        ]
        self.writer.writerow(row)


class TwistStampedProcessor(Msg2CSVProcessor):
    save_path: str = "twist_stamped.csv"
    header: List[str] = [
        "nsec",
        "linear", "angular"]

    def process_message(self, msg, t):
        linear = [
            msg.twist.linear.x,
            msg.twist.linear.y,
            msg.twist.linear.z,
        ]
        angular = [
            msg.twist.angular.x,
            msg.twist.angular.y,
            msg.twist.angular.z,
        ]

        row = [
            msg.header.stamp.to_nsec(), 
            linear,
            angular
        ]
        self.writer.writerow(row)


class PoseWithCovarianceStampedProcessor(Msg2CSVProcessor):
    save_path: str = "posewcovar_stamped.csv"
    header: List[str] = [
        "nsec",
        "position", "orientation", "covariance"]

    def process_message(self, msg, t):
        position = [
            msg.pose.pose.position.x, 
            msg.pose.pose.position.y, 
            msg.pose.pose.position.z,
            msg.pose.pose.position.w
        ]
        orientation = [
            msg.pose.pose.orientation.x, 
            msg.pose.pose.orientation.y, 
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w
        ]

        row = [
            msg.header.stamp.to_nsec(),
            position,
            orientation,
            msg.pose.covariance,
        ]
        self.writer.writerow(row)


def extraxct_rosbag_data(
        bag_file: rosbag.Bag, processors: Dict[str, MsgProcessor]):
    for topic, msg, t in bag_file.read_messages(topics=processors.keys()):
        if topic not in processors.keys():
            continue
        try:
            processors[topic].process_message(msg, t)
        except Exception as e:
            print(e)
            continue
    for _,proc in processors.items():
        proc.destroy()


if __name__ == '__main__':

    # Parse CLI options
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument(
        '-b', '--bag-path', type=Path, required=True,
        help='Path to rosbag file to read and extract info from.'
    )
    parser.add_argument(
        '-t', '--topics', type=str, nargs='+', default=[],
        help='Topics to read from the rosbag (all if unspecified).'
    )
    parser.add_argument(
        '-s', '--skip', type=str, nargs='+', default=[],
        help='Topics to skip extraction (none if unspecified).'
    )
    parser.add_argument(
        '--start', type=int, required=False,
        help='Time (nsec) from which to start the processing the bag messages.'
    )
    parser.add_argument(
        '--end', type=int, required=False,
        help='Time (nsec) up to which to process the bag messages.'
    )
    parser.add_argument(
        '-o', '--output-folder', type=Path, default='.',
        help='Output folder where to extract all data, if unset will use the' \
             ' current directory.'
    )

    args = parser.parse_args()

    # check output folder
    assert(args.output_folder.is_dir()), \
        f"Path to output {args.output_folder} is not a valid folder."
    output_folder = args.output_folder

    TOPIC_TO_PROCESSOR = {
        '/realsense/color/image_raw': ImageProcessor(
            path=output_folder/'realsense'/'color'),
        '/realsense/infra1/image_rect_raw': ImageProcessor(
            path=output_folder/'realsense'/'infra1'),
        '/realsense/infra2/image_rect_raw': ImageProcessor(
            path=output_folder/'realsense'/'infra2'),
        '/realsense/imu': IMUProcessor(
            path=output_folder/'realsense'/'imu.csv'),
        '/reach_1/fix': NavSatFixProcessor(
            path=output_folder/'reach1'/'fix.csv'),
        '/reach_1/imu': IMUProcessor(
            path=output_folder/'reach1'/'imu.csv'),
        '/reach_1/mag': MagneticFieldProcessor(
            path=output_folder/'reach1'/'mag.csv'),
        '/reach_1/vel': TwistStampedProcessor(
            path=output_folder/'reach1'/'vel.csv'),
        '/reach_2/fix': NavSatFixProcessor(
            path=output_folder/'reach2'/'fix.csv'),
        '/reach_2/imu': IMUProcessor(
            path=output_folder/'reach2'/'imu.csv'),
        '/reach_2/mag': MagneticFieldProcessor(
            path=output_folder/'reach2'/'mag.csv'),
        '/reach_2/vel': TwistStampedProcessor(
            path=output_folder/'reach2'/'vel.csv'),
        '/reach_3/fix': NavSatFixProcessor(
            path=output_folder/'reach3'/'fix.csv'),
        '/reach_3/imu': IMUProcessor(
            path=output_folder/'reach3'/'imu.csv'),
        '/reach_3/mag': MagneticFieldProcessor(
            path=output_folder/'reach3'/'mag.csv'),
        '/reach_3/vel': TwistStampedProcessor(
            path=output_folder/'reach3'/'vel.csv'),
        # TODO
        # '/distance': DistancesProcessor(
        #     path=output_folder/'odom'/'distance.csv'),
        # '/odom': OdometryProcessor(
        #     path=output_folder/'odom'/'odom.csv'),

        # Topics available in separate rosbags

        '/reach_1/gps/fix': NavSatFixProcessor(
            path=output_folder/'reach1'/'spp.csv'),
        '/reach_1/gps/vel': TwistStampedProcessor(
            path=output_folder/'reach1'/'spp_vel.csv'),
        '/reach_2/gps/fix': NavSatFixProcessor(
            path=output_folder/'reach2'/'spp.csv'),
        '/reach_2/gps/vel': TwistStampedProcessor(
            path=output_folder/'reach2'/'spp_vel.csv'),
        '/reach_3/gps/fix': NavSatFixProcessor(
            path=output_folder/'reach3'/'spp.csv'),
        '/reach_3/gps/vel': TwistStampedProcessor(
            path=output_folder/'reach3'/'spp_vel.csv'),

        '/reach_1/ppk/fix': NavSatFixProcessor(
            path=output_folder/'reach1'/'ppk.csv'),
        '/reach_1/ppk/vel': TwistStampedProcessor(
            path=output_folder/'reach1'/'ppk_vel.csv'),
        '/reach_2/ppk/fix': NavSatFixProcessor(
            path=output_folder/'reach2'/'ppk.csv'),
        '/reach_2/ppk/vel': TwistStampedProcessor(
            path=output_folder/'reach2'/'ppk_vel.csv'),
        '/reach_3/ppk/fix': NavSatFixProcessor(
            path=output_folder/'reach3'/'ppk.csv'),
        '/reach_3/ppk/vel': TwistStampedProcessor(
            path=output_folder/'reach3'/'ppk_vel.csv'),

        '/mins/imu/pose': PoseWithCovarianceStampedProcessor(
            path=output_folder/'mins'/'imu_pose.csv'
        ),
    }

    # check input path and open rosbag file
    print(f'Opening rosbag located at {args.bag_path}...')
    assert(args.bag_path.is_file()), \
        f"Path to rosbag {args.bag_path} is not a valid path."
    bag_file = rosbag.Bag(args.bag_path)
    
    # filter topics with provided options
    bag_topics = [topic for topic in bag_file.get_type_and_topic_info().topics]
    topics_not_found = list(set(args.topics) - set(bag_topics))
    skip_not_found = list(set(args.skip) - set(bag_topics))
    not_found = topics_not_found + skip_not_found
    if not_found:
        print(f"The following topics were not found in the topic list:"
              f"\n{not_found}\nRemove them from the filter options.")
        exit(1)
    if args.topics:
        filtered_bag_topics = list(set(args.topics) - set(args.skip))
    else:
        filtered_bag_topics = bag_topics
    filtered_topic_to_processor = \
        {topic: TOPIC_TO_PROCESSOR[topic] for topic in filtered_bag_topics 
         if topic in TOPIC_TO_PROCESSOR.keys()}

    # check option timestamps
    def floatsec_to_intnsec(float_sec):
        int_sec = int(float_sec)
        rem_sec = float_sec - int_sec
        rem_nsec = int(rem_sec * int(1e9))
        return (int_sec * int(1e9)) + rem_nsec
    start_nsec = floatsec_to_intnsec(bag_file.get_start_time())
    end_nsec = floatsec_to_intnsec(bag_file.get_end_time())
    if args.start is not None and args.start < start_nsec:
        print(f"Provided start time is lower than rosbag start time")
        exit(1)
    if args.end is not None and args.end < end_nsec:
        print(f"Provided start time is higher than rosbag end time")
        exit(1)

    # execute data extraction
    print(f'Starting data extraction for {args.bag_path}')

    extraxct_rosbag_data(bag_file, processors=filtered_topic_to_processor)

    print(f'Finished extracting data for {args.bag_path}')
