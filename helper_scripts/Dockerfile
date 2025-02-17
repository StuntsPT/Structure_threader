#
# Structure_threader Dockerfile
#

# Pull base image
FROM python:3.11-slim
SHELL ["bash", "-l" ,"-c"]
WORKDIR /analysis

# Install necessary dependencies from main Debian repository and
# clean apt cache to reduce image size
RUN apt-get update && apt-get upgrade -y && \
  apt-get install xz-utils && \
  apt-get install -y r-base r-cran-devtools r-cran-biocmanager && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Install Python modules and remove pip cache to reduce image size
COPY . /st_setup
RUN pip install --upgrade pip --no-cache-dir --root-user-action ignore && \
  pip install /st_setup --no-cache-dir --root-user-action ignore && \
  rm -rf /st_setup
