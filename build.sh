#!/usr/bin/env bash
# Hugo's Render guide installs both tools at build time: https://gohugo.io/host-and-deploy/host-on-render/
set -euo pipefail

# Pinned here, not in render.yaml envVars: a dashboard-configured Render service ignores those, and its own
# HUGO_VERSION may still name the old Hugo
DART_SASS_VERSION=1.79.3
HUGO_VERSION=0.169.0
PAGEFIND_VERSION=1.6.0
tools="${HOME}/.local"
mkdir -p "${tools}/hugo" "${tools}/pagefind"

curl -sSfL --retry 3 "https://github.com/sass/dart-sass/releases/download/${DART_SASS_VERSION}/dart-sass-${DART_SASS_VERSION}-linux-x64.tar.gz" | tar -xz -C "${tools}"
curl -sSfL --retry 3 "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz" | tar -xz -C "${tools}/hugo"
curl -sSfL --retry 3 "https://github.com/Pagefind/pagefind/releases/download/v${PAGEFIND_VERSION}/pagefind_extended-v${PAGEFIND_VERSION}-x86_64-unknown-linux-musl.tar.gz" | tar -xz -C "${tools}/pagefind"
export PATH="${tools}/hugo:${tools}/dart-sass:${tools}/pagefind:${PATH}"

sass --version
hugo version
pagefind_extended --version
hugo --minify --gc --baseURL '/'
pagefind_extended --site public
rm -rf public/search-index
