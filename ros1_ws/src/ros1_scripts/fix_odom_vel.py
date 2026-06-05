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
Creates a new rosbag to fix an error with the odometry frame of reference where
the twist was expressed in global coordinates and not local to the robot. Also
fixes an issue with how the direction of the robot is calculated from the odometry.
Creates a rosbag with a single topic named '/odom_fix'.

We thank Dante Noguera for their contribution on finding the issue and creating
the original fix code. 
"""
import argparse
import math
import copy
import rosbag
from ast import literal_eval
from enum import Enum
from tqdm import tqdm

# Standard ROS 1 imports - requires the workspace to be sourced
from wheel_odometry.msg import Distances
from nav_msgs.msg import Odometry


class OdometryStates(Enum):
    CALIB = 0
    DUTY_REMOTE = 1
    RPM_REMOTE = 2
    DUTY_PC = 3
    RPM_PC = 4
    EMERGENCY = 5

class WheelOdometry(object):
    DIAMETER = 0.57
    VEL_MAX = 100
    VEL_MIN = 0

    def __init__(self):
        self.rpm_to_mps = math.pi * self.DIAMETER / 60

        # used to compensate for invalid read values
        self.prev_speed_rpm = 0
        self.prev_pulses = 0
        self.prev_forward = 0

        self.switch_direction_sensitivity = 3
        self.switch_direction_countdown = self.switch_direction_sensitivity

    @staticmethod
    def parse_odometry(line):
        try:
            state, data = line.split(":")
            state = literal_eval(state + ")")
            data, _ =  data.split(")")	
            data = literal_eval("(" + data + ")")

        except (ValueError, SyntaxError) as e:
            raise RuntimeError(f"Invalid motor message format: {e}")

        try:
            state = OdometryStates(state)
        except ValueError:
            raise RuntimeError('Invalid motor message - bad state')

        if len(data) != 22:
            raise RuntimeError('Invalid motor message - data too short')

        # data = [<motor nr>, <rpm>, <pulses>, <duty>, <current>, ..., <angle>, <direction>]
        wheels = {
            data[0]: tuple(data[1:5]),
            data[5]: tuple(data[6:10]),
            data[10]: tuple(data[11:15]),
            data[15]: tuple(data[16:20])
        }
        angle = data[20]*(-1)
        direction = 1 if data[21] == 0 else -1

        return state, wheels, angle, direction

    def velocity_from_distance_msg(self, line):
        state, wheels, _, direction = self.parse_odometry(line)

        if state == OdometryStates.EMERGENCY:
            rpms = [0.0]
        else:
            rpms = [v[0] for v in wheels.values() if self.VEL_MIN <= v[0] <= self.VEL_MAX]

        speed_rpm = self.prev_speed_rpm
        if rpms:
            speed_rpm = sum(rpms) / len(rpms)

        if direction != self.prev_forward:
            if self.prev_speed_rpm - speed_rpm > 0:
                direction = self.prev_forward
                self.switch_direction_countdown = self.switch_direction_sensitivity
            else:
                self.switch_direction_countdown -= 1
            
            if self.switch_direction_countdown != 0:
                direction = self.prev_forward
            else:
                self.switch_direction_countdown = self.switch_direction_sensitivity

        self.prev_speed_rpm = speed_rpm
        speed_mps = speed_rpm * self.rpm_to_mps
        velocity = speed_mps * direction
        self.prev_forward = direction

        return velocity

def main():
    parser = argparse.ArgumentParser(description='Inject fixed linear velocities into /odom messages.')
    parser.add_argument('-i', '--input_bag', required=True, help='Path to input rosbag.')
    parser.add_argument('-o', '--output_bag', required=True, help='Path to output rosbag.')
    args = parser.parse_args()

    wo = WheelOdometry()
    current_velocity = 0.0

    print("Opening rosbag...")

    topics_to_read = ['/distance', '/odom']
    with rosbag.Bag(args.input_bag, 'r') as inbag, rosbag.Bag(args.output_bag, 'w') as outbag:
        total_msgs = inbag.get_message_count(topic_filters=topics_to_read)
        
        for topic, msg, ts in tqdm(inbag.read_messages(topics=topics_to_read), total=total_msgs, desc="Parsing Bag"):
            
            if topic == "/distance":
                current_velocity = wo.velocity_from_distance_msg(msg.odometry_raw)
            
            if topic == "/odom":
                fixed_odom_msg = copy.deepcopy(msg)
                fixed_odom_msg.twist.twist.linear.x = current_velocity
                fixed_odom_msg.twist.twist.linear.y = 0.0
                fixed_odom_msg.twist.twist.linear.z = 0.0
                outbag.write("/odom_fix", fixed_odom_msg, ts)

    print("\nBag conversion complete.")


if __name__ == '__main__':
  main()
