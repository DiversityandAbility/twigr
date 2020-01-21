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
# ---
uvicorn app.main:app --reload --host 0.0.0.0
