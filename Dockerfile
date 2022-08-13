FROM registry.gitlab.com/pages/hugo/hugo_extended:0.101.0 as builder
RUN mkdir -p /site
WORKDIR /site
COPY . /site
RUN hugo

FROM nginx
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /site/public /usr/share/nginx/html