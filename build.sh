#!/usr/bin/env bash
# Hugo's Render guide installs both tools at build time: https://gohugo.io/host-and-deploy/host-on-render/
set -euo pipefail

tools="${HOME}/.local"
mkdir -p "${tools}/hugo"

curl -sSfL --retry 3 "https://github.com/sass/dart-sass/releases/download/${DART_SASS_VERSION}/dart-sass-${DART_SASS_VERSION}-linux-x64.tar.gz" | tar -xz -C "${tools}"
curl -sSfL --retry 3 "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz" | tar -xz -C "${tools}/hugo"
export PATH="${tools}/hugo:${tools}/dart-sass:${PATH}"

sass --version
hugo version
hugo --minify --gc --baseURL '/'
