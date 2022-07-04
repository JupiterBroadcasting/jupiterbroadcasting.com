FROM ubuntu:jammy AS builder
RUN apt-get update && apt-get install -y hugo
WORKDIR /build
COPY . .
RUN hugo -D

FROM nginx:1
COPY --from=builder /build/public /usr/share/nginx/html