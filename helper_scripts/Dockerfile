FROM ubuntu:20.04

# apt stuff
RUN apt update
RUN apt install -y python3-pip parallel zip

# Pypi stuff
RUN pip install structure_threader

RUN mkdir /analysis 
WORKDIR /analysis
