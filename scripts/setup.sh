#!/bin/bash

# FastCheckAI - Setup Script
# This script creates a virtual environment with Python 3.12 and installs all dependencies

set -e  # Exit on error

echo "🚀 FastCheckAI Setup"
echo "===================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create virtual environment with Python 3.12
echo ""
echo "📦 Creating virtual environment with Python 3.12..."
uv venv --python 3.12.11

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies from pyproject.toml
echo ""
echo "📥 Installing dependencies from pyproject.toml..."
uv pip install -e .

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo ""
        echo "📝 Creating .env file from .env.example..."
        cp .env.example .env
        echo "⚠️  Don't forget to add your OPENAI_API_KEY to the .env file"
    else
        echo ""
        echo "📝 Creating .env file..."
        cat > .env << EOF
# OpenAI API Key
OPENAI_API_KEY=your_api_key_here

# Optional: Agno Configuration
AGNO_LOG_LEVEL=INFO
EOF
        echo "⚠️  Don't forget to add your OPENAI_API_KEY to the .env file"
    fi
fi

# Create required directories
echo ""
echo "📁 Creating project directories..."

mkdir -p src
mkdir -p tests/unit
mkdir -p data/inputs
mkdir -p data/outputs
mkdir -p logs
mkdir -p notebooks

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To start Jupyter Lab on port 8894, run:"
echo "  bash scripts/start_jupyter.sh"