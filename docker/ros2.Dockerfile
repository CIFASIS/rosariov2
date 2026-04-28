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

# We need shadow-utils for usermod/groupmod
RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*

RUN if [ ${USER_ID:-0} -ne 0 ] && [ ${GROUP_ID:-0} -ne 0 ]; then \
    # 1. Check if the UID is already taken (likely by the 'ubuntu' user)
    if getent passwd ${USER_ID} > /dev/null; then \
        EXISTING_USER=$(getent passwd ${USER_ID} | cut -d: -f1); \
        echo "UID ${USER_ID} taken by ${EXISTING_USER}, hijacking..."; \
        # Rename user and move home directory
        usermod -l ${USER_NAME} -m -d /home/${USER_NAME} ${EXISTING_USER}; \
        # Rename group if it exists
        groupmod -n ${USER_NAME} $(getent group ${USER_ID} | cut -d: -f1) || true; \
    else \
        # 2. Standard creation if UID is free
        groupadd -g ${GROUP_ID} ${USER_NAME} && \
        useradd -l -u ${USER_ID} -g ${USER_NAME} ${USER_NAME} && \
        install -d -m 0755 -o ${USER_NAME} -g ${USER_NAME} /home/${USER_NAME}; \
    fi; \
    # 3. Ensure permissions and sudo access
    usermod -aG sudo ${USER_NAME} && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers; \
fi

# Set up the environment for the user
USER ${USER_NAME}
WORKDIR /home/${USER_NAME}

# Automatically source ROS 2 in every new bash session
RUN echo "source /opt/ros/jazzy/setup.bash" >> /home/${USER_NAME}/.bashrc
