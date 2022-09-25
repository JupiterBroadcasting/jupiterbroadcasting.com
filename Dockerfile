FROM registry.gitlab.com/pages/hugo/hugo_extended:0.101.0 as builder
WORKDIR /site
COPY . /site
RUN hugo

FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
COPY nginx.conf /etc/nginx/config.d/jb-404.conf
RUN echo "\ninclude /etc/nginx/config.d/*.conf;" > /etc/nginx/nginx.conf
COPY --from=builder /site/public /usr/share/nginx/html
