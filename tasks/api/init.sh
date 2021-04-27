#!/bin/sh
set -e

vg pg new
vg pg ping
vg api migrate
