#!/usr/bin/env sh
python3 -m app.provide_secrets "$ADMIN_EMAIL" "$ADMIN_PASSWORD" "$AUTH_SECRET"
uvicorn app.main:app --host 0.0.0.0 --port 8000

