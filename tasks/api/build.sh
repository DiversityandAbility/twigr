#!/bin/sh
set -e

docker build --build-arg BUILD_ENV=development --tag twigr/api:latest "$VG_APP_DIR/api"
