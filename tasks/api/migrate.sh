#!/bin/sh
# ---
# image:
#   tag: twigr/api:latest
#   rm: true
#   network: twigr
#   volume:
#     - "$VG_APP_DIR/api:/app"
# ---
alembic upgrade head
