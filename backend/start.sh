#!/bin/bash
# Install Chromium for PDF generation, then start the app
apt-get update -qq && apt-get install -y -qq chromium 2>/dev/null || true
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
