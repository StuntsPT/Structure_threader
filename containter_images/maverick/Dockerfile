FROM alpine:3.23.3 AS builder

RUN apk add --update alpine-sdk wget bash

WORKDIR /app

RUN wget https://github.com/bobverity/MavericK/archive/v1.0.5.tar.gz -O maverick.tar.gz && \
    tar xvfz maverick.tar.gz && \
    cd  MavericK-1.0.5/ && \
    g++ -std=c++11 *.cpp -O3 -static -o MavericK && \
    mv MavericK /usr/local/bin/MavericK

#COPY install_maverick.sh /app
#RUN bash install_maverick.sh

# Final image
FROM alpine:3.23.3

RUN apk add --update bash
COPY --from=builder /usr/local/bin/MavericK /usr/local/bin/MavericK

CMD ["MavericK"]
