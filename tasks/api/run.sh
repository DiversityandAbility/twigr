#!/bin/sh
# ---
# image:
#   tag: twigr/api:latest
#   rm: true
#   tty: true
#   interactive: true
#   network: twigr
#   volume:
#     - "$VG_APP_DIR/api:/app"
# ---
"${@:-bash}"
