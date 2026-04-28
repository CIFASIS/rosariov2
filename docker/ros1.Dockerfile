FROM osrf/ros:noetic-desktop-full

ARG USER_ID
ARG GROUP_ID
ARG USER_NAME

RUN sudo apt update \
    && sudo apt install -y \
        python3-venv \
        python3-pip \
    && sudo apt install -y \
        ros-noetic-tf2 \
        ros-noetic-tf2-tools \
        ros-noetic-cv-bridge

RUN if [ ${USER_ID:-0} -ne 0 ] && [ ${GROUP_ID:-0} -ne 0 ]; then \
    groupadd -g ${GROUP_ID} ${USER_NAME} && \
    useradd -l -u ${USER_ID} -g ${USER_NAME} ${USER_NAME} && \
    install -d -m 0755 -o ${USER_NAME} -g ${USER_NAME} /home/${USER_NAME} && \
    usermod -aG sudo ${USER_NAME} && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers\
;fi

USER ${USER_NAME}
WORKDIR /home/${USER_NAME}

# Automatically source ROS 2 in every new bash session
RUN echo "source /opt/ros/noetic/setup.bash" >> /home/${USER_NAME}/.bashrc