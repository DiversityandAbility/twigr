#!/bin/sh
set -e

docker network create twigr || true

vg pg new
vg pg ping
vg api migrate
