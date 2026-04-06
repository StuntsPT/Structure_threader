#
# Structure_threader Dockerfile
#

# Pull base image
FROM snakemake/snakemake:v9.19.0
WORKDIR /analysis

# Install necessary dependencies from main Debian repository and
# clean apt cache to reduce image size
#RUN apt-get update && apt-get upgrade -y && \
#  apt-get install -y xz-utils && \
#  apt-get clean && \
#  rm -rf /var/lib/apt/lists/*

# Install apptainer
RUN conda install apptainer xz -c conda-forge
