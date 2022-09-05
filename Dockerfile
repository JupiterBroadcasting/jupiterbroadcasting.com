FROM registry.gitlab.com/pages/hugo/hugo_extended:0.101.0 as builder
ARG BASE_URL
WORKDIR /site
COPY . /site
RUN set -x && ( [ -z "${BASE_URL}" ] || [ "${BASE_URL}" == "PROD" ] ) && hugo --gc || hugo --gc --baseURL "${BASE_URL}"

FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /site/public /usr/share/nginx/html