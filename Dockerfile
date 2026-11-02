ARG HUGO_VERSION=0.105.0
FROM registry.gitlab.com/pages/hugo/hugo_extended:${HUGO_VERSION} AS builder
# this defaults to an empty variable
ARG BASE_URL
WORKDIR /site
COPY . /site
# when the argument is empty or PROD, do a normal production build
#   else if it's TESTS_WEB use the specified baseURL "/", or
#   exit 1, because that use case hasn't been provided
#   https://explainshell.com/ is an awesome website which can explain this in more detail
#   set -x : changes the shell's default verbosity and puts it in "debug" mode
RUN set -x && ( [ -z "${BASE_URL}" ] || [ "${BASE_URL}" == "PROD" ] ) \
    && hugo --gc \
    || ( [ "${BASE_URL}" == 'TESTS_WEB' ] && hugo --gc --baseURL "/" || exit 1 )


FROM alpine AS indexer
ARG PAGEFIND_VERSION=1.3.0
WORKDIR /site
RUN wget -qO- "https://github.com/Pagefind/pagefind/releases/download/v${PAGEFIND_VERSION}/pagefind_extended-v${PAGEFIND_VERSION}-x86_64-unknown-linux-musl.tar.gz" \
    | tar xz -C /usr/local/bin pagefind_extended
COPY --from=builder /site/public /site/public
RUN pagefind_extended --site public && rm -rf public/search-index


FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
RUN sed -i 's/#error_page/error_page/' /etc/nginx/conf.d/default.conf
COPY --from=indexer /site/public /usr/share/nginx/html
