FROM registry.gitlab.com/pages/hugo/hugo_extended:0.105.0 AS builder
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

# Generate llms.txt, llms-full.txt, and per-show llms.txt indexes from the
# build's public/llmsdump.json (see layouts/index.llmsdump.json), then drop
# the intermediate dump. Regenerated on every deploy, so indexes always match
# content -- including scraper auto-commits. Separate stage because the pinned
# hugo image's apk repos resolve to current Alpine (incompatible python3).
FROM python:3.12-alpine AS llms
WORKDIR /site
COPY --from=builder /site /site
RUN python3 scripts/gen_llms.py && rm -f public/llmsdump.json

FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
RUN sed -i 's/#error_page/error_page/' /etc/nginx/conf.d/default.conf
# nginx:alpine ships no text/markdown mime type; llms.txt spec wants it on .md twins.
# (root is repeated: the stock conf declares it inside `location /`, and these
# location blocks replace it for matching paths.)
RUN sed -i '/listen  /i\    location ~ \\.md$ { root /usr/share/nginx/html; default_type text/markdown; }\n    location = /llms.txt { root /usr/share/nginx/html; default_type text/markdown; }\n    location = /llms-full.txt { root /usr/share/nginx/html; default_type text/markdown; }' /etc/nginx/conf.d/default.conf
COPY --from=llms /site/public /usr/share/nginx/html
