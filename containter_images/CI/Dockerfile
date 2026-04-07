#
# Structure_threader Dockerfile
#

# Pull base image
#FROM snakemake/snakemake:v9.14.5
FROM ubuntu:24.04
WORKDIR /analysis

# Install necessary dependencies from main Debian repository and
# clean apt cache to reduce image size
RUN apt-get update && \
    apt-get install -y wget xz-utils software-properties-common python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN add-apt-repository -y ppa:apptainer/ppa && apt-get update && apt install -y apptainer-suid
