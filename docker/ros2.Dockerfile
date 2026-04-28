FROM osrf/ros:jazzy-desktop

ARG USER_ID
ARG GROUP_ID
ARG USER_NAME

# Install system and ROS 2 dependencies
RUN apt update && apt install -y \
        python3-venv \
        python3-pip \
        sudo \
    && apt install -y \
        ros-jazzy-tf2-ros \
        ros-jazzy-tf2-tools \
        ros-jazzy-cv-bridge \
        ros-jazzy-xacro \
        ros-jazzy-robot-state-publisher \
        ros-jazzy-rosbag2-storage-mcap \
    && rm -rf /var/lib/apt/lists/*

# Create user with same UID/GID as the host [cite: 34]
RUN if [ ${USER_ID:-0} -ne 0 ] && [ ${GROUP_ID:-0} -ne 0 ]; \
    then \
        groupadd -g ${GROUP_ID} ${USER_NAME} && \
        useradd -l -u ${USER_ID} -g ${USER_NAME} ${USER_NAME} && \
        install -d -m 0755 -o ${USER_NAME} -g ${USER_NAME} /home/${USER_NAME} && \
        usermod -aG sudo ${USER_NAME} && \
        echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    ;fi

# Set up the environment for the user
USER ${USER_NAME}
WORKDIR /home/${USER_NAME}

# Automatically source ROS 2 in every new bash session
RUN echo "source /opt/ros/jazzy/setup.bash" >> /home/${USER_NAME}/.bashrc
