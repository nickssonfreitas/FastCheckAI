#!/bin/bash

# FastCheckAI - Start Jupyter Notebook
# Starts Jupyter notebook without token on port 8894

PORT=${1:-8894}

echo "🚀 Starting Jupyter Notebook on port ${PORT}..."
echo "📝 Access at: http://localhost:${PORT}"
echo ""

uv run jupyter lab --no-browser --port=${PORT} --NotebookApp.token='' --NotebookApp.password=''
