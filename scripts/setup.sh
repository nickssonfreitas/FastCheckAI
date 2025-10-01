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

# Check and install Tesseract OCR
echo ""
echo "🔍 Checking Tesseract OCR installation..."
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR is not installed"
    echo ""
    echo "Tesseract is required for OCR fallback when extracting text from corrupted PDFs."
    echo ""
    echo "To install Tesseract:"
    echo "  • Ubuntu/Debian/WSL2: sudo apt-get update && sudo apt-get install tesseract-ocr tesseract-ocr-eng"
    echo "  • macOS: brew install tesseract"
    echo "  • Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    echo ""
    read -p "Would you like to try installing Tesseract now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "📥 Installing Tesseract OCR..."
            sudo apt-get update && sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
            if command -v tesseract &> /dev/null; then
                echo "✅ Tesseract OCR installed successfully"
                tesseract --version | head -n 1
            else
                echo "❌ Tesseract installation failed. Please install manually."
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            if command -v brew &> /dev/null; then
                echo "📥 Installing Tesseract OCR via Homebrew..."
                brew install tesseract
                if command -v tesseract &> /dev/null; then
                    echo "✅ Tesseract OCR installed successfully"
                    tesseract --version | head -n 1
                else
                    echo "❌ Tesseract installation failed. Please install manually."
                fi
            else
                echo "❌ Homebrew not found. Please install Homebrew first: https://brew.sh"
            fi
        else
            echo "❌ Automatic installation not supported on this OS. Please install manually."
        fi
    else
        echo "⏭️  Skipping Tesseract installation. You can install it later."
        echo "   Note: OCR fallback will not work until Tesseract is installed."
    fi
else
    echo "✅ Tesseract OCR is already installed"
    tesseract --version | head -n 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Add your OpenAI API key to .env file:"
echo "     OPENAI_API_KEY=your_actual_key_here"
echo ""
echo "  3. Start Jupyter Lab:"
echo "     bash scripts/start_jupyter.sh"
echo ""
if ! command -v tesseract &> /dev/null; then
    echo "  ⚠️  Remember to install Tesseract OCR for full functionality!"
    echo ""
fi