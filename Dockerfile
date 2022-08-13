FROM registry.gitlab.com/pages/hugo/hugo_extended:0.101.0 as builder
RUN mkdir -p /app
WORKDIR /app
COPY . /app
RUN hugo

FROM nginx
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/public /usr/share/nginx/html