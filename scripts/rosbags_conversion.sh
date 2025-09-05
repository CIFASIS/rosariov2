#!/bin/bash
set -x  # print all that's happening to stdout

if [ -z "$1" ]; then
  echo "Usage: $0 <rosariov2_base_dir>"
  exit 1
fi

declare -a rosariov2seqs=(
    "2023-12-22-13-14-16" 
    "2023-12-22-14-29-43" 
    "2023-12-22-16-31-08" 
    "2023-12-26-13-39-43" 
    "2023-12-26-15-10-15" 
    "2023-12-26-15-48-38"
)

# Install rosbags on python3
pip3 install rosbags || python3 -m pip install rosbags

# Create a folder to generate output rosbags
mkdir $1/rosbags2/

# Run rosbags conversion
echo "Starting rosbag conversion..."
for seq in "${rosariov2seqs[@]}" 
do
    echo "Converting" ${bag}
    rosbags-convert --src "$1/$seq.compressed.bag" --src-typestore ros1_noetic --dst "$1/rosbags2/$seq" --dst-typestore ros2_humble
done

echo "Done!"
