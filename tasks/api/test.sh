#!/bin/sh
# ---
# image:
#   tag: twigr/api:latest
#   rm: true
#   tty: true
#   interactive: true
#   publish: "8000:8000"
#   network: twigr
#   volume:
#     - "$VG_APP_DIR/api:/app"
# overrides:
#   TESTING: "on"
# ---
pytest tests "$@"
