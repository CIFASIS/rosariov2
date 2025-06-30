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
Merge one or more bag files and filter for specific topics.
"""
import argparse
from fnmatch import fnmatchcase
from pathlib import Path
from rosbag import Bag
from tqdm import tqdm
from typing import List


SCRIPT_DESCRIPTION = \
    "This script merges a set of rosbag files into a single rosbag file" \
    " while filtering for specific topics. Can also be used to filter a" \
    " single rosbag for specific topics." \
    "\nThe script requires ROS1 to be installed. We recommend using the" \
    " dockerfile provided with the repository to avoid having to install" \
    " ROS1 permanently, and to avoid any clash of versions."


def stream(input_file: Bag, output_file: Bag, topics: List[str]):
    """
    Stream data from an input bag to an output bag.

    Arguments:
        input_file: the input bag to stream from
        output_file: the output bag to write data to
        topics: a list of the topics to include
    """
    included = 0
    skipped = 0
    # create a progress bar for iterating over the messages in the bag
    with tqdm(total=input_file.get_message_count(), unit='message') as prog:
        # iterate over the messages in this input bag
        for topic, msg, time in input_file:
            # check for matches between the topics filter and this topic
            if any(fnmatchcase(topic, pattern) for pattern in topics):
                # write this message to the output bag
                output_file.write(topic, msg, time)
                # increment the counter of included messages
                included += 1
            else:
                # increment the counter of excluded messages
                skipped += 1
            # update the progress bar with a single iteration
            prog.update(1)
            # update the progress bar post fix text with statistics
            prog.set_postfix(included=included, skipped=skipped)


# ensure this script is running as the main entry point
if __name__ == '__main__':
    
    # create an argument parser to read arguments from the command line
    PARSER = argparse.ArgumentParser(description=__doc__)
    # add an argument for the sequence of input bags
    PARSER.add_argument(
        '--input-bags', '-i', type=Path, nargs='+', required=True,
        help='A list of input bag files',
    )
    # add an argument for the output bag to create
    PARSER.add_argument(
        '--output-bag', '-o', type=Path, required=True,
        help='The output bag file to write to',
    )
    # add an argument for the topics to filter
    PARSER.add_argument(
        '--topics', '-t', type=str, nargs='*', default=['*'], required=False,
        help='A sequence of topics to include from the input bags.'
    )

    # get the arguments from the argument parser
    args = PARSER.parse_args()
    # open the output bag in an automatically closing context
    with Bag(args.output_bag.as_posix(), 'w') as output_bag:
        # iterate over the input files
        for filename in tqdm(args.input_bags, unit='bag'):
            # open the input bag with an automatically closing context
            with Bag(filename.as_posix(), 'r') as input_bag:
                # stream the input bag to the output bag
                stream(input_bag, output_bag, args.topics)
