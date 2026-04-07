#
# Structure_threader Dockerfile
#

# Pull base image
FROM ubuntu:24.04
WORKDIR /analysis

# Allow pip to run amok
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Install necessary dependencies,
# Add apptainer PPA repository and install it,
# finally clean apt cache to reduce image size
RUN apt-get update && \
    apt-get install -y wget xz-utils software-properties-common python3-pip && \
    add-apt-repository -y ppa:apptainer/ppa && \
    apt-get update && apt install -y apptainer-suid && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/python3 /usr/bin/python
