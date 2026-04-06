FROM alpine:3.23.3 AS builder

RUN apk add --update alpine-sdk wget

WORKDIR /app

RUN wget http://web.stanford.edu/group/pritchardlab/structure_software/release_versions/v2.3.4/structure_kernel_source.tar.gz && tar xvfz structure_kernel_source.tar.gz
RUN cd structure_kernel_src && sed -i 's/OPT = -O3/OPT = -O3 -fcommon/' Makefile && sed -i 's/void CheckIfMissing();/void CheckIfMissing(int strat);/' params.c && make

# Final image
FROM alpine:3.23.3

COPY --from=builder /app/structure_kernel_src/structure /usr/local/bin

WORKDIR /workspace

CMD ["structure"]
