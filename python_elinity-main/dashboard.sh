#!/bin/bash

source .venv/bin/activate

uvicorn dashboard.app:app --host 0.0.0.0 --port 8082 --reload
