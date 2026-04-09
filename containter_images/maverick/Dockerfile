FROM alpine:3.23.3 AS builder

RUN apk add --update alpine-sdk wget bash

WORKDIR /app

COPY install_maverick.sh /app
RUN bash install_maverick.sh

# Final image
FROM alpine:3.23.3

RUN apk add --update bash
COPY --from=builder /usr/local/bin/MavericK /usr/local/bin/MavericK

WORKDIR /workspace

CMD ["MavericK"]
