#!/bin/bash
set -e

echo "TASK_MODE: $TASK_MODE"

if $APP_ENV == "production"; then
    echo "Downloading production environment variables..."
    aws s3 cp s3://crypt-trader-bot/env/.env.production .env.production
fi

if [ "$TASK_MODE" == "api" ]; then
    echo "Starting FastAPI..."
    exec uvicorn main:app --host 0.0.0.0 --port 8000
elif [ "$TASK_MODE" == "auto_trade" ]; then
    echo "Running batch auto_trade..."
    export PYTHONPATH="/app"
    exec python tasks/auto_trade.py
else
    echo "TASK_MODE not set. Defaulting to API mode."
    exec uvicorn main:app --host 0.0.0.0 --port 8000
fi
