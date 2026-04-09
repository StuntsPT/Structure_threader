FROM ubuntu:20.04

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y install wget python2 cython cmake gfortran-10 libblas-dev build-essential
RUN ln -s /usr/bin/gfortran-10 /usr/bin/gfortran
COPY install_faststructure.sh /app
#RUN pip2 install scipy
RUN bash install_faststructure.sh

# Final image
#FROM ubuntu:20.04
#RUN apt-get update && apt-get -y install python2
RUN mv /app/faststructure/fastStructure-1.0/* /usr/local/bin
RUN mv /app/faststructure/lib/libgsl* /usr/local/lib
#COPY --from=builder /usr/local/ /usr/local/
ENV LD_LIBRARY_PATH=/usr/local/lib
RUN sed -i '1i#!/usr/bin/python2' /usr/local/bin/structure.py
RUN chmod +x /usr/local/bin/structure.py


CMD ["python"]
