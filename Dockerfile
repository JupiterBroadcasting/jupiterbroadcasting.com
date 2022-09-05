FROM registry.gitlab.com/pages/hugo/hugo_extended:0.101.0 as builder
ARG BASE_URL
WORKDIR /site
COPY . /site
RUN [ -n "${BASE_URL}}" ] && hugo --gc --baseURL "${BASE_URL}" || hugo --gc

FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /site/public /usr/share/nginx/html