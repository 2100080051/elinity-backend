#!/usr/bin/env bash

# .venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080 --reload

docker compose up  -d
docker logs -f elinity_common